#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Release 大文件直传（S3 方式）。

GitHub 的 `POST /repos/{o}/{r}/releases/{id}/assets?name=...` 会先返回一个
`storage.s3_url` 预签名地址，之后只要对这个地址做一次 PUT 就能完成上传。
比直接把 39MB 塞进 API 请求体稳定得多（后者在本机 40 分钟没传完）。

用法:
    python upload_asset_s3.py <release_id> <本地文件路径>
"""
import json
import os
import ssl
import sys
import urllib.request
import urllib.error

REPO = "madajiann/Tempora"


def load_token() -> str:
    with open(os.path.expanduser("~/.tempora/token"), "r", encoding="utf-8") as f:
        return f.read().strip().strip('"').strip()


def post_asset(release_id: str, name: str, token: str) -> dict:
    url = (
        f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets"
        f"?name={name}"
    )
    # 注意：GitHub 现在要求 POST 的 size >= 1，传 0 字节会被 422 拒掉。
    # 这里塞 1 字节占位，随后由 PUT 覆盖为真实内容。
    req = urllib.request.Request(url, data=b"0", method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/octet-stream")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def put_s3(s3_url: str, path: str, token: str) -> None:
    size = os.path.getsize(path)
    print(f"  PUT {size} bytes ...", flush=True)
    with open(path, "rb") as f:
        req = urllib.request.Request(s3_url, data=f, method="PUT")
        req.add_header("Authorization", f"token {token}")
        req.add_header("Content-Type", "application/octet-stream")
        req.add_header("X-GitHub-Media-Type", "github.v3+json")
        req.add_header("Content-Length", str(size))
        try:
            with urllib.request.urlopen(req, timeout=3600) as r:
                print(f"  PUT -> HTTP {r.status}", flush=True)
        except urllib.error.HTTPError as e:
            body = e.read()[:500].decode("utf-8", "replace")
            print(f"  PUT -> HTTP {e.code}: {body}", flush=True)
            raise


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    release_id, path = sys.argv[1], sys.argv[2]
    name = os.path.basename(path)
    token = load_token()

    print(f"[1/2] 申请直传地址 {name}", flush=True)
    info = post_asset(release_id, name, token)
    s3_url = (info.get("storage") or {}).get("s3_url")
    if not s3_url:
        print("  未拿到 s3_url，返回:", json.dumps(info, ensure_ascii=False)[:800])
        sys.exit(1)
    print(f"  s3_url = {s3_url[:110]}...", flush=True)

    print(f"[2/2] 直传", flush=True)
    put_s3(s3_url, path, token)
    print("完成", flush=True)


if __name__ == "__main__":
    main()
