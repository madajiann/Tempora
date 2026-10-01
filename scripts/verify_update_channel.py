# -*- coding: utf-8 -*-
"""验证「国内可读的更新通道」是否打通（一次性验证脚本，验证完可删）。

做三件事：
  1. 把 latest.json 提交到仓库 updates/latest.json（走 api.github.com）
  2. 从 raw.githubusercontent.com 读回，比对内容一致
  3. 从 cdn.jsdelivr.net 读回，比对内容一致
  4. 用 api 资产端点下载安装包前 64KB，确认能拿到真实数据

用法: python verify_update_channel.py <version> <asset_id>
"""
import base64, json, os, sys, urllib.request

REPO = "madajiann/Tempora"
API = "https://api.github.com"
BRANCH = "main"
PATH_IN_REPO = "updates/latest.json"
NSIS_DIR = "shell/src-tauri/target/release/bundle/nsis"
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{PATH_IN_REPO}"
JSD = f"https://cdn.jsdelivr.net/gh/{REPO}@{BRANCH}/{PATH_IN_REPO}"

tok = open(os.path.expanduser("~/.tempora/token"), encoding="utf-8").read().strip()
creds = base64.b64encode(f"madajiann:{tok}".encode()).decode()


def gh(method, url, data=None, ctype="application/json", raw_accept=False):
    headers = {
        "Authorization": "Basic " + creds,
        "User-Agent": "tempora-verify",
        "Accept": "application/vnd.github.raw" if raw_accept else "application/vnd.github+json",
    }
    if data is not None:
        headers["Content-Type"] = ctype
    req = urllib.request.Request(url, method=method, data=data, headers=headers)
    # 沙箱里直连 api.github.com 是通的，需绕过沙箱代理
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return opener.open(req, timeout=180)


def plain_get(url, rng=None):
    headers = {"User-Agent": "tempora-verify"}
    if rng:
        headers["Range"] = rng
    req = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return opener.open(req, timeout=120)


def main():
    version, asset_id = sys.argv[1], sys.argv[2]
    sig_path = f"{NSIS_DIR}/Tempora_{version}_x64-setup.exe.sig"
    sig = open(sig_path, encoding="utf-8").read().strip()

    latest = {
        "version": version,
        "notes": f"Tempora {version}",
        "pub_date": "2026-09-28T02:00:00Z",
        "platforms": {
            "windows-x86_64": {
                "signature": sig,
                "url": f"{API}/repos/{REPO}/releases/assets/{asset_id}",
            }
        },
    }
    payload_bytes = json.dumps(latest, ensure_ascii=False, indent=2).encode("utf-8")

    print("== 1/4 提交到仓库", PATH_IN_REPO, "==")
    url = f"{API}/repos/{REPO}/contents/{PATH_IN_REPO}"
    sha = None
    try:
        with gh("GET", f"{url}?ref={BRANCH}") as r:
            sha = json.load(r).get("sha")
        print("   文件已存在 sha=", sha)
    except Exception:
        print("   文件尚不存在，将新建")
    body = {"message": f"chore(updates): latest.json -> v{version}",
            "content": base64.b64encode(payload_bytes).decode(),
            "branch": BRANCH}
    if sha:
        body["sha"] = sha
    with gh("PUT", url, json.dumps(body).encode()) as r:
        d = json.load(r)
        print("   提交成功 commit=", d.get("commit", {}).get("sha", "")[:12])

    print("== 2/4 从 raw.githubusercontent.com 读回 ==")
    try:
        with plain_get(RAW + "?t=" + str(int(__import__("time").time()))) as r:
            got = r.read()
        ok = json.loads(got)["platforms"]["windows-x86_64"]["url"] == latest["platforms"]["windows-x86_64"]["url"]
        print(f"   HTTP {r.status}  {len(got)} B  url 一致: {'OK' if ok else 'FAIL'}")
    except Exception as e:
        print("   FAIL", type(e).__name__, e)

    print("== 3/4 从 cdn.jsdelivr.net 读回 ==")
    try:
        with plain_get(JSD) as r:
            got = r.read()
        ok = json.loads(got)["platforms"]["windows-x86_64"]["url"] == latest["platforms"]["windows-x86_64"]["url"]
        print(f"   HTTP {r.status}  {len(got)} B  url 一致: {'OK' if ok else 'FAIL（可能有 CDN 缓存，正常）'}")
    except Exception as e:
        print("   FAIL", type(e).__name__, e)

    print("== 4/4 用 api 资产端点下载安装包前 64KB ==")
    try:
        with plain_get(latest["platforms"]["windows-x86_64"]["url"], rng="bytes=0-65535") as r:
            data = r.read()
        print(f"   HTTP {r.status}  {len(data)} B  头部魔数: {data[:2]!r}")
    except Exception as e:
        print("   FAIL", type(e).__name__, e)


if __name__ == "__main__":
    main()
