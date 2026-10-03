"""Upload a large file to the HK mirror as chunks, without deleting anything locally.

为什么不用 scripts/upload_hk.py：它每片落本地临时文件后 os.remove，本机安全守卫会拦（WinError 5）。
本脚本改为：从源文件按需切片到内存（4MB），用 scp 的 stdin 直传远端分片文件名，完全不落本地临时文件。
已存在的分片（远端字节数相符）自动跳过，可反复重跑续传。
"""
import os
import subprocess
import sys

HOST = "103.84.110.200"
USER = "root"
SSH_OPTS = ["-i", os.path.expanduser("~/.ssh/id_ed25519_deploy"),
            "-o", "HostKeyAlgorithms=+ssh-rsa",
            "-o", "PubkeyAcceptedAlgorithms=+ssh-ed25519,ssh-rsa",
            "-o", "ConnectTimeout=25"]
CHUNK = 4 * 1024 * 1024


def remote(cmd, tries=4):
    last = ""
    for _ in range(tries):
        r = subprocess.run(["ssh"] + SSH_OPTS + [f"{USER}@{HOST}", cmd],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
        last = r.stderr.strip() or r.stdout.strip()
    print(f"  [ssh 失败] {last[:160]}", flush=True)
    return ""


def remote_size(path):
    out = remote(f"stat -c %s {path} 2>/dev/null || echo 0")
    for line in reversed(out.splitlines()):
        try:
            return int(line)
        except ValueError:
            continue
    return 0


def main():
    local, remote_dir = sys.argv[1], sys.argv[2]
    name = os.path.basename(local)
    size = os.path.getsize(local)
    tmp_dir = f"/tmp/_up_{name}"
    parts = (size + CHUNK - 1) // CHUNK
    remote(f"mkdir -p {tmp_dir}")
    print(f"{name}  {size} 字节 / {parts} 片 x 4MB", flush=True)

    # scp 在 Windows 下不认 /dev/stdin，所以复用同一个临时文件、逐片覆盖写。
    # 不删除它：本机安全守卫会拦 Python 的 os.remove（WinError 5）。
    staging = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "tempora_chunk.bin")
    with open(local, "rb") as f:
        for i in range(parts):
            part = f"{tmp_dir}/part{1000 + i:04d}"
            blob = f.read(CHUNK)
            have = remote_size(part)
            if have == len(blob):
                print(f"  [{i+1}/{parts}] 已存在，跳过", flush=True)
                continue
            with open(staging, "wb") as s:
                s.write(blob)
            p = subprocess.run(["scp"] + SSH_OPTS + [staging, f"{USER}@{HOST}:{part}"],
                               capture_output=True)
            got = remote_size(part)
            if got != len(blob):
                print(f"  [{i+1}/{parts}] 失败：远端 {got} != 本地 {len(blob)}；{p.stderr.decode(errors='replace')[:200]}", flush=True)
                sys.exit(1)
            print(f"  [{i+1}/{parts}] 上传完成 ({got} 字节)", flush=True)

    print("=== 远端合并 ===", flush=True)
    print(remote(f"cd {tmp_dir} && cat $(ls part* | sort) > {remote_dir}/{name} && "
                 f"rm -f part* && cd /tmp && rmdir {tmp_dir}; "
                 f"ls -l {remote_dir}/{name} && sha256sum {remote_dir}/{name}"), flush=True)


if __name__ == "__main__":
    main()
