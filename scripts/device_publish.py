#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用 GitHub OAuth Device Flow 拿凭据，然后一键完成 v0.1.16 发布全流程。

为什么需要它：`~/.tempora/token` 在清理 C 盘时被误删，而 GitHub Release 上传
必须带凭据。Device Flow 只需人在浏览器里输入一次 8 位 user_code，不必手动
生成 PAT。

流程：
  1. 轮询 https://github.com/login/oauth/access_token 拿 access_token
  2. 写入 ~/.tempora/token
  3. git push main
  4. 创建 Release v0.1.16
  5. 上传资产：安装包 / .sig / latest.json（走 S3 直传）
  6. 逐个端点读回验证

注意（2026-10-01 实测）：Device Flow 用 gh CLI 的 OAuth App 拿到的是 `ghu_` 开头的
**GitHub App token，没有仓库写权限** —— push / 建 release / 写文件一律 403
"Resource not accessible by integration"（`GET /repos` 返回的 push=True 是误导）。
这条脚本的取凭据部分只能用于只读场景；要发版请直接放一个 classic PAT（`ghp_`）
到 ~/.tempora/token，然后从「创建 Release」那一步开始跑。

用法:
    # 已有 PAT（推荐，ghp_ 开头）放 ~/.tempora/token 后：
    python scripts/device_publish.py --use-token <version>

    # 或走 Device Flow（只能拿到只读 ghu_ token，发版别用）：
    python scripts/device_publish.py <device_code> <version>
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO = "madajiann/Tempora"
CLIENT_ID = "Iv1.b507a08c87ecfe98"  # GitHub CLI 公开的 OAuth App，Device Flow 可用
NSIS_DIR = os.path.join("shell", "src-tauri", "target", "release", "bundle", "nsis")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def no_proxy_opener():
    # api.github.com 直连才通，必须绕开沙箱代理
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def proxy_opener():
    # github.com 域名沙箱外连不上，只能走沙箱注入的代理（默认 opener）
    return urllib.request.build_opener()


def post(url, data, headers, timeout=60, via_proxy=False):
    body = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else data
    req = urllib.request.Request(url, data=body, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    op = proxy_opener() if via_proxy else no_proxy_opener()
    return op.open(req, timeout=timeout)


def poll_token(device_code: str, timeout_sec=870):
    deadline = time.time() + timeout_sec
    interval = 5
    print(f"等待浏览器授权（最长 {timeout_sec // 60} 分钟）...", flush=True)
    while time.time() < deadline:
        try:
            r = post(
                "https://github.com/login/oauth/access_token",
                {
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                {"Accept": "application/json"},
                via_proxy=True,  # github.com 只有走沙箱代理才通
            )
            d = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            d = json.loads(e.read().decode() or "{}")
        if "access_token" in d:
            return d["access_token"]
        err = d.get("error")
        if err == "authorization_pending":
            time.sleep(interval)
            continue
        if err == "slow_down":
            interval = int(d.get("interval", interval)) + 5
            time.sleep(interval)
            continue
        if err:
            print("授权失败:", err, d.get("error_description", ""))
            return None
        time.sleep(interval)
    print("等待超时")
    return None


def api(method, path, token, data=None, ctype="application/json"):
    req = urllib.request.Request(f"https://api.github.com{path}", method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "tempora-publish")
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode()
        req.add_header("Content-Type", ctype)
    try:
        r = no_proxy_opener().open(req, data=body, timeout=120)
        raw = r.read()
        return r.status, (json.loads(raw.decode()) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw.decode())
        except Exception:
            return e.code, {"raw": raw[:300].decode("utf-8", "replace")}


def git(*args, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                       text=True, env=e)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def upload_asset(release_id, path, token):
    """GitHub 大文件 S3 直传：POST 拿预签名地址，再 PUT。"""
    name = os.path.basename(path)
    size = os.path.getsize(path)
    url = (f"https://uploads.github.com/repos/{REPO}/releases/{release_id}"
           f"/assets?name={name}")
    req = urllib.request.Request(url, data=b"0", method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/octet-stream")
    try:
        info = json.loads(no_proxy_opener().open(req, timeout=60).read().decode())
    except urllib.error.HTTPError as e:
        # 同名资产已存在会 422，先删再重试
        print(f"  POST 失败 {e.code}，尝试删除同名资产后重试", flush=True)
        st, rel = api("GET", f"/repos/{REPO}/releases/{release_id}/assets", token)
        for a in rel if isinstance(rel, list) else []:
            if a["name"] == name:
                api("DELETE", f"/repos/{REPO}/releases/assets/{a['id']}", token)
        info = json.loads(no_proxy_opener().open(req, timeout=60).read().decode())

    s3_url = (info.get("storage") or {}).get("s3_url")
    if not s3_url:
        print("  未拿到 s3_url:", json.dumps(info)[:400])
        return False
    print(f"  直传 {size} 字节 ...", flush=True)
    with open(path, "rb") as f:
        req = urllib.request.Request(s3_url, data=f, method="PUT")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/octet-stream")
        req.add_header("Content-Length", str(size))
        try:
            no_proxy_opener().open(req, timeout=3600)
        except urllib.error.HTTPError as e:
            print("  PUT 失败:", e.code, e.read()[:200])
            return False
    print(f"  {name} 上传完成", flush=True)
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if len(args) < 1:
        print(__doc__)
        sys.exit(2)
    version = args[-1]
    tag = f"v{version}"

    tok_path = os.path.expanduser("~/.tempora/token")
    if "--use-token" in flags or len(args) < 2:
        # 已有 PAT：跳过 Device Flow，直接走发布
        if not os.path.exists(tok_path):
            print(f"缺凭据文件 {tok_path}")
            sys.exit(1)
        token = open(tok_path, encoding="utf-8").read().strip()
        print(f"使用 {tok_path} 中的凭据 {token[:4]}...", flush=True)
    else:
        token = poll_token(args[0])
        if not token:
            sys.exit(1)
        print(f"拿到凭据 {token[:8]}...", flush=True)
        os.makedirs(os.path.dirname(tok_path), exist_ok=True)
        with open(tok_path, "w", encoding="utf-8") as f:
            f.write(token)
        os.chmod(tok_path, 0o600)
        print(f"已写入 {tok_path}", flush=True)

    # 1) push
    creds = base64.b64encode(f"madajiann:{token}".encode()).decode()
    rc, out, err = git("-c", f"http.extraHeader=Authorization: Basic {creds}",
                       "push", "origin", "main")
    print(f"[push] rc={rc} {out[:200]} {err[:200]}", flush=True)

    # 2) 创建 release
    notes_path = os.path.join(ROOT, f"_release-notes-{version}.txt")
    notes = open(notes_path, encoding="utf-8").read().strip() if os.path.exists(notes_path) else ""
    st, rel = api("POST", f"/repos/{REPO}/releases", token, {
        "tag_name": tag, "name": f"Tempora {version}", "body": notes,
        "draft": False, "prerelease": False, "target_commitish": "main",
    })
    if st not in (200, 201):
        print(f"[release] 创建失败 {st}: {json.dumps(rel, ensure_ascii=False)[:400]}")
        sys.exit(1)
    release_id = rel["id"]
    print(f"[release] 创建成功 id={release_id} {rel['html_url']}", flush=True)

    # 3) 上传资产
    assets = [
        os.path.join(ROOT, NSIS_DIR, f"Tempora_{version}_x64-setup.exe"),
        os.path.join(ROOT, NSIS_DIR, f"Tempora_{version}_x64-setup.exe.sig"),
        os.path.join(ROOT, "updates", "latest.json"),
    ]
    for p in assets:
        if not os.path.exists(p):
            print(f"  跳过（不存在）{p}")
            continue
        print(f"[upload] {os.path.basename(p)}", flush=True)
        if not upload_asset(release_id, p, token):
            print(f"  !! {os.path.basename(p)} 上传失败")

    # 4) 验证
    print("=== 验证 ===", flush=True)
    for label, url in [
        ("raw", f"https://raw.githubusercontent.com/{REPO}/main/updates/latest.json"),
        ("jsdelivr", f"https://cdn.jsdelivr.net/gh/{REPO}@main/updates/latest.json"),
        ("release-asset", f"https://github.com/{REPO}/releases/latest/download/latest.json"),
    ]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "tempora-verify"})
            d = json.loads(no_proxy_opener().open(req, timeout=60).read().decode())
            print(f"  {label:14s} version={d.get('version')}", flush=True)
        except Exception as e:
            print(f"  {label:14s} 失败 {e}", flush=True)
    print("PUBLISH_DONE", flush=True)


if __name__ == "__main__":
    main()
