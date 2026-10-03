# -*- coding: utf-8 -*-
"""GitHub Release 资产一步式上传（修复 device_publish.py 的旧两阶段流程）。

坑：旧的「POST 1 字节占位 → 取 storage.s3_url → PUT」已失效，API 不再返回 s3_url，
只会造出 size=1 的废资产。正确做法是直接 POST 完整 body 到 uploads.github.com。

坑2：`state` 才是真判据。半吊子资产 size 正确而 state=starter，下载 404。
     上传后回读，只认 state == "uploaded"。

用法：
  python scripts/upload_assets.py --release-id 402378643 --version 0.1.19
"""
import argparse, json, os, sys, time, urllib.request

REPO = "madajiann/Tempora"
BASE = "G:/Tempora"


def req(method, url, data=None, headers=None, timeout=120):
    token = open(os.path.expanduser("~/.tempora/token"), encoding="utf-8").read().strip()
    h = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "tempora-asset-upload",
    }
    if headers:
        h.update(headers)
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    return urllib.request.urlopen(r, timeout=timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-id", required=True)
    ap.add_argument("--version", required=True)
    args = ap.parse_args()

    v = args.version.lstrip("v")
    nsis = f"{BASE}/shell/src-tauri/target/release/bundle/nsis"
    assets = [
        f"{nsis}/Tempora_{v}_x64-setup.exe.sig",
        f"{BASE}/updates/latest.json",
        f"{nsis}/Tempora_{v}_x64-setup.exe",
    ]
    for path in assets:
        if not os.path.exists(path):
            sys.exit(f"缺少文件：{path}")

    # 1) 清掉旧两阶段留下的废资产（size 极小 / state 非 uploaded）
    print("=== 清理废资产 ===", flush=True)
    for a in json.load(req("GET", f"https://api.github.com/repos/{REPO}/releases/{args.release_id}/assets?per_page=100")):
        if a["size"] < 4096 or a.get("state") == "starter":
            print(f"  删除 {a['name']} (size={a['size']} state={a.get('state')})", flush=True)
            try:
                req("DELETE", f"https://api.github.com/repos/{REPO}/releases/assets/{a['id']}")
                print("   已删除", flush=True)
            except Exception as e:
                print(f"   删除失败（可重试）：{e.__class__.__name__} {e}", flush=True)

    # 2) 一步式上传
    print("\n=== 上传 ===", flush=True)
    for path in assets:
        name = os.path.basename(path)
        size = os.path.getsize(path)
        print(f"  {name}  {size} 字节 ...", flush=True)
        body = open(path, "rb").read()
        for attempt in range(3):
            try:
                r = req(
                    "POST",
                    f"https://uploads.github.com/repos/{REPO}/releases/{args.release_id}/assets?name={name}",
                    data=body,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=1800,
                )
                got = json.load(r)
                print(f"   返回 size={got.get('size')} state={got.get('state')}", flush=True)
                break
            except Exception as e:
                print(f"   第 {attempt + 1} 次失败：{e.__class__.__name__} {e}", flush=True)
                if attempt == 2:
                    print(f"   !! {name} 放弃", flush=True)
                else:
                    time.sleep(5)

    print("\n=== 最终资产（只认 state=uploaded）===", flush=True)
    bad = 0
    for a in json.load(req("GET", f"https://api.github.com/repos/{REPO}/releases/{args.release_id}/assets?per_page=100")):
        state = a.get("state")
        if state != "uploaded":
            bad += 1
        print(f"  {a['name']:45} {a['size']:>10}  state={state}", flush=True)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
