# -*- coding: utf-8 -*-
"""Tempora 更新发布脚本。

用法：
  python release_updater.py --version 0.1.1 --notes "更新说明"

功能：
  1. 读取 NSIS 产物 + .sig 签名，生成 latest.json
  2. 在 GitHub 创建 Release（tag: v<version>，已存在则复用）
  3. 上传 安装包 / .sig / latest.json 三个资产
  4. 客户端 updater 端点即 releases/latest/download/latest.json，自动命中最新版

endpoint 顺序（tauri.conf.json plugins.updater.endpoints）：
  香港镜像（待用户提供服务器后插入第一行）-> GitHub Releases 兜底
"""
import argparse, base64, json, sys, time, urllib.request

REPO = "madajiann/Tempora"
API = "https://api.github.com"
UPLOAD = "https://uploads.github.com"
NSIS_DIR = "shell/src-tauri/target/release/bundle/nsis"


def gh(creds, method, url, data=None, content_type="application/json"):
    req = urllib.request.Request(url, method=method, data=data, headers={
        "Authorization": "Basic " + creds,
        "User-Agent": "tempora-release",
        "Accept": "application/vnd.github+json",
        "Content-Type": content_type,
    })
    return urllib.request.urlopen(req, timeout=120)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--notes", default="")
    ap.add_argument("--token", required=True, help="GitHub PAT（repo 权限）")
    ap.add_argument("--user", default="madajiann")
    args = ap.parse_args()

    creds = base64.b64encode(f"{args.user}:{args.token}".encode()).decode()
    v = args.version.lstrip("v")
    tag = f"v{v}"
    exe = f"Tempora_{v}_x64-setup.exe"
    sig = exe + ".sig"

    print("== 1/4 读取签名 ==")
    with open(f"{NSIS_DIR}/{sig}", "rb") as f:
        signature = f.read().decode("utf-8").strip()

    print("== 2/4 生成 latest.json ==")
    latest = {
        "version": v,
        "notes": args.notes,
        "pub_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platforms": {
            "windows-x86_64": {
                "signature": signature,
                "url": f"https://github.com/{REPO}/releases/download/{tag}/{exe}",
            }
        },
    }
    latest_bytes = json.dumps(latest, ensure_ascii=False, indent=2).encode("utf-8")
    print(json.dumps({k: ("..." if k == "platforms" else v2) for k, v2 in latest.items()}, ensure_ascii=False))

    print("== 3/4 创建 Release ==")
    body = json.dumps({
        "tag_name": tag,
        "target_commitish": "main",
        "name": f"Tempora {v}",
        "body": args.notes or f"Tempora v{v}",
        "draft": False,
        "prerelease": False,
    }).encode("utf-8")
    try:
        rel = json.load(gh(creds, "POST", f"{API}/repos/{REPO}/releases", body))
        print("  已创建", tag)
    except Exception as e:
        # 409/422 = tag 已存在，改用已有 release
        rels = json.load(gh(creds, "GET", f"{API}/repos/{REPO}/releases?per_page=50"))
        rel = next((r for r in rels if r["tag_name"] == tag), None)
        if not rel:
            print("创建失败且无同名 release:", e)
            sys.exit(1)
        print("  复用已有", tag)
    rid = rel["id"]

    print("== 4/4 上传资产 ==")
    assets = [
        (f"{NSIS_DIR}/{exe}", "application/octet-stream", exe),
        (f"{NSIS_DIR}/{sig}", "text/plain", sig),
        ("latest.json.tmp", "application/octet-stream", "latest.json"),
    ]
    with open("latest.json.tmp", "wb") as f:
        f.write(latest_bytes)
    for path, ctype, name in assets:
        # 已存在同名资产则先删
        for a in rel.get("assets", []):
            if a["name"] == name:
                gh(creds, "DELETE", f"{API}/repos/{REPO}/releases/assets/{a['id']}")
                print(f"  删除旧资产 {name}")
        with open(path, "rb") as f:
            data = f.read()
        gh(creds, "POST",
           f"{UPLOAD}/repos/{REPO}/releases/{rid}/assets?name={name}",
           data, ctype)
        print(f"  上传 {name} ({len(data)} bytes)")
    import os
    os.remove("latest.json.tmp")
    print("完成。客户端将在下次检查时收到", tag)


if __name__ == "__main__":
    main()
