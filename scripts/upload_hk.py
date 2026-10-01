#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分片上传大文件到香港镜像（103.84.110.200）。

背景：本机 scp 直传 40MB 会在传输中途 "Connection closed"（中间链路会掐断
长连接）。切成小片逐片传 + 失败重传，再在远端 cat 合并，稳定得多。

用法:
    python scripts/upload_hk.py <本地文件> <远端目录> [--chunk MB]

例:
    python scripts/upload_hk.py \
      shell/src-tauri/target/release/bundle/nsis/Tempora_0.1.16_x64-setup.exe \
      /opt/tempora-site/dl
"""
import hashlib
import os
import subprocess
import sys
import time

HOST = "103.84.110.200"
USER = "root"
KEY = os.path.expanduser("~/.ssh/id_ed25519_deploy")
# 本机 OpenSSH 10.3 默认禁用 ssh-rsa hostkey，不加这两条会在 KEXINIT 后
# 被服务端直接 reset（表现为 ssh 无任何输出、退出码 255）。
SSH_ALG = [
    "-o", "HostKeyAlgorithms=+ssh-rsa",
    "-o", "PubkeyAcceptedAlgorithms=+ssh-ed25519,ssh-rsa",
]
SSH_BASE = [
    "ssh", "-i", KEY, "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
    "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
] + SSH_ALG
SCP_BASE = [
    "scp", "-i", KEY, "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
    "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
] + SSH_ALG


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()


def run(cmd, retries=3, desc=""):
    for i in range(retries):
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 0:
            return True
        print(f"    重试 {i + 1}/{retries} ({desc}): rc={p.returncode} "
              f"{p.stderr.strip()[:120]}", flush=True)
        time.sleep(2)
    return False


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    local = os.path.abspath(sys.argv[1])
    remote_dir = sys.argv[2].rstrip("/")
    chunk_mb = 4
    if "--chunk" in sys.argv:
        chunk_mb = int(sys.argv[sys.argv.index("--chunk") + 1])

    name = os.path.basename(local)
    size = os.path.getsize(local)
    local_hash = sha256(local)
    chunk = chunk_mb * 1024 * 1024
    n = (size + chunk - 1) // chunk
    print(f"{name}  {size} 字节 / {n} 片 x {chunk_mb}MB")
    print(f"本地 SHA256 {local_hash}", flush=True)

    tmp_dir = f"/tmp/_up_{name}"
    subprocess.run(SSH_BASE + [f"{USER}@{HOST}", f"mkdir -p {tmp_dir}"],
                   capture_output=True)

    # 1) 分片上传（支持断点：远端已存在且大小一致则跳过）
    ok = True
    with open(local, "rb") as f:
        for i in range(n):
            data = f.read(chunk)
            part = f"{tmp_dir}/part{1000 + i:04d}"
            p = subprocess.run(
                SSH_BASE + [f"{USER}@{HOST}",
                            f"stat -c %s {part} 2>/dev/null || echo 0"],
                capture_output=True, text=True)
            if p.stdout.strip() == str(len(data)):
                print(f"  [{i + 1}/{n}] 已存在，跳过", flush=True)
                continue
            tmp = f"{local}.part{1000 + i:04d}"
            with open(tmp, "wb") as pf:
                pf.write(data)
            if not run(SCP_BASE + [tmp, f"{USER}@{HOST}:{part}"],
                       retries=4, desc=f"片 {i + 1}"):
                ok = False
                break
            os.remove(tmp)
            print(f"  [{i + 1}/{n}] 上传完成 ({len(data)} 字节)", flush=True)
    if not ok:
        print("分片上传失败，远端保留分片，重跑本脚本可续传")
        sys.exit(1)

    # 2) 远端合并 + 校验
    print("远端合并 + 校验 ...", flush=True)
    merge = (
        f"cd {tmp_dir} && cat $(ls part* | sort) > {remote_dir}/{name} && "
        f"rm -f part* && rmdir {tmp_dir} && sha256sum {remote_dir}/{name}"
    )
    p = subprocess.run(SSH_BASE + [f"{USER}@{HOST}", merge],
                       capture_output=True, text=True)
    print(p.stdout.strip(), flush=True)
    if p.returncode != 0:
        print("合并失败:", p.stderr.strip()[:300])
        sys.exit(1)

    remote_hash = p.stdout.split()[0]
    if remote_hash != local_hash:
        print(f"!! SHA256 不一致 本地={local_hash} 远端={remote_hash}")
        sys.exit(1)
    print("OK SHA256 一致，上传完成", flush=True)


if __name__ == "__main__":
    main()
