# -*- coding: utf-8 -*-
"""Tempora 更新发布脚本。

用法：
  python release_updater.py --version 0.1.7 --notes "更新说明"

token 来源优先级：--token > 环境变量 TEMPORA_GH_TOKEN > ~/.tempora/token（默认）

功能：
  1. 创建/复用 GitHub Release（tag: v<version>）
  2. 上传 安装包 / .sig，拿到安装包的 asset id
  3. 生成 latest.json（url 指向 api.github.com 资产端点），上传到 Release
  4. 把 latest.json 同步提交到仓库 updates/latest.json，供国内端点直接取

## 为什么要绕开 github.com（2026-09-28 实测）
国内网络下 `github.com` 常被定点阻断（DNS 污染 / SNI 干扰），
实测沙箱外直连：github.com = 连接超时，而
  api.github.com                     = 200
  raw.githubusercontent.com          = 通
  cdn.jsdelivr.net                   = 通
  release-assets.githubusercontent.com = 通（安装包真实下载域名）
所以：
  - 「取 latest.json」走 raw.githubusercontent.com / jsDelivr（仓库里的 updates/latest.json）
  - 「下安装包」走 https://api.github.com/repos/O/R/releases/assets/<id>
    —— 该端点会 302 到 release-assets.githubusercontent.com；
    tauri 的 download() 默认自带 `Accept: application/octet-stream`，无需额外配置头。
  - github.com 原地址保留为最后兜底，方便海外网络。

## endpoint 顺序（tauri.conf.json plugins.updater.endpoints）
  raw.githubusercontent.com -> cdn.jsdelivr.net -> github.com（兜底）
"""
import argparse, base64, json, os, subprocess, sys, time, urllib.request

REPO = "madajiann/Tempora"
API = "https://api.github.com"
UPLOAD = "https://uploads.github.com"
NSIS_DIR = "shell/src-tauri/target/release/bundle/nsis"
TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".tempora", "token")
# latest.json 在仓库里的落点：客户端用 raw / jsDelivr 取它
REPO_LATEST_PATH = "updates/latest.json"
BRANCH = "main"


def load_token(cli_token=None):
    tok = cli_token or os.environ.get("TEMPORA_GH_TOKEN", "").strip()
    if not tok and os.path.exists(TOKEN_FILE):
        tok = open(TOKEN_FILE, encoding="utf-8").read().strip()
    if not tok:
        sys.exit("找不到 GitHub token：请传 --token，或写入 " + TOKEN_FILE)
    return tok


def gh(creds, method, url, data=None, content_type="application/json"):
    req = urllib.request.Request(url, method=method, data=data, headers={
        "Authorization": "Basic " + creds,
        "User-Agent": "tempora-release",
        "Accept": "application/vnd.github+json",
        "Content-Type": content_type,
    })
    return urllib.request.urlopen(req, timeout=180)


def asset_api_url(asset_id):
    """安装包下载地址：匿名可访问，302 到 release-assets.githubusercontent.com。"""
    return f"{API}/repos/{REPO}/releases/assets/{asset_id}"


def push_repo_latest(creds, content_bytes, version):
    """把 latest.json 提交到仓库，供 raw / jsDelivr 端点读取。"""
    url = f"{API}/repos/{REPO}/contents/{REPO_LATEST_PATH}"
    sha = None
    try:
        with gh(creds, "GET", f"{url}?ref={BRANCH}") as r:
            sha = json.load(r).get("sha")
    except Exception:
        pass  # 首次创建时文件还不存在
    payload = {
        "message": f"chore(updates): latest.json -> v{version}",
        "content": base64.b64encode(content_bytes).decode(),
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha
    gh(creds, "PUT", url, json.dumps(payload).encode())
    return REPO_LATEST_PATH


def purge_jsdelivr():
    """jsDelivr 对分支文件有 12 小时缓存，发版后主动刷新。
    否则作为兜底端点的它可能返回上一个版本的 latest.json，
    客户端就会以为「已是最新」。失败不影响发版主流程。"""
    url = f"https://purge.jsdelivr.net/gh/{REPO}@{BRANCH}/{REPO_LATEST_PATH}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "tempora-release"})
        with urllib.request.urlopen(req, timeout=60) as r:
            json.load(r)
        return True
    except Exception:
        return False


def curl_upload(token, url, path, content_type, out_json):
    """上传资产走 curl。

    为什么不用 urllib：38MB 安装包经本地代理上传时，
    urllib 会报 `urlopen error The write operation timed out`（实测 2026-09-28），
    curl 同样的链路能稳定传完（约 100KB/s）。
    """
    p = subprocess.run(
        ["curl", "-sS", "--max-time", "5400", "-X", "POST",
         "-H", f"Authorization: token {token}",
         "-H", "Accept: application/vnd.github+json",
         "-H", f"Content-Type: {content_type}",
         "--data-binary", f"@{path}",
         "-o", out_json, "-w", "%{http_code}", url],
        capture_output=True, text=True)
    code = (p.stdout or "").strip()
    if p.returncode != 0 or not code.startswith("2"):
        err = (p.stderr or "").strip()[:300]
        raise RuntimeError(f"curl 上传失败 rc={p.returncode} http={code} {err}")
    with open(out_json, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--notes", default="")
    ap.add_argument("--token", default=None, help="GitHub PAT（repo 权限），缺省读 ~/.tempora/token")
    ap.add_argument("--user", default="madajiann")
    ap.add_argument("--dry-run", action="store_true", help="只生成 latest.json 不上传")
    ap.add_argument("--asset-id", default=None,
                    help="dry-run 时用：指定安装包的 asset id，让 url 与真发版一致")
    args = ap.parse_args()

    token = load_token(args.token)
    creds = base64.b64encode(f"{args.user}:{token}".encode()).decode()
    v = args.version.lstrip("v")
    tag = f"v{v}"
    exe = f"Tempora_{v}_x64-setup.exe"
    sig = exe + ".sig"

    print("== 1/5 读取签名 ==")
    sig_path = f"{NSIS_DIR}/{sig}"
    signature = ""
    if not os.path.exists(sig_path):
        print(f"  未找到 {sig_path}，本次以无签名模式发布（不写 signature）")
    else:
        with open(sig_path, "rb") as f:
            signature = f.read().decode("utf-8").strip()

    def build_latest(asset_id):
        return {
            "version": v,
            "notes": args.notes,
            "pub_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "platforms": {
                "windows-x86_64": {
                    **({"signature": signature} if signature else {}),
                    # 优先用 api 端点（国内可达）；asset_id 未知时退回 github.com
                    "url": asset_api_url(asset_id) if asset_id
                    else f"https://github.com/{REPO}/releases/download/{tag}/{exe}",
                }
            },
        }

    if args.dry_run:
        latest_bytes = json.dumps(build_latest(args.asset_id), ensure_ascii=False, indent=2).encode("utf-8")
        open(f"latest.v{v}.json", "wb").write(latest_bytes)
        print("== [dry-run] 生成 latest.v" + v + ".json ==")
        print(json.dumps(json.loads(latest_bytes), ensure_ascii=False, indent=2))
        return

    print("== 2/5 创建 Release ==")
    body = json.dumps({
        "tag_name": tag,
        "target_commitish": BRANCH,
        "name": f"Tempora {v}",
        "body": args.notes or f"Tempora v{v}",
        "draft": False,
        "prerelease": False,
    }).encode("utf-8")
    try:
        rel = json.load(gh(creds, "POST", f"{API}/repos/{REPO}/releases", body))
        print("  已创建", tag)
    except Exception as e:
        rels = json.load(gh(creds, "GET", f"{API}/repos/{REPO}/releases?per_page=50"))
        rel = next((r for r in rels if r["tag_name"] == tag), None)
        if not rel:
            print("创建失败且无同名 release:", e)
            sys.exit(1)
        print("  复用已有", tag)
    rid = rel["id"]
    existing = {a["name"]: a["id"] for a in rel.get("assets", [])}

    print("== 3/5 上传安装包与签名 ==")
    exe_asset_id = None
    tmp_out = "asset_upload_result.json"
    for path, ctype, name in [(f"{NSIS_DIR}/{exe}", "application/octet-stream", exe),
                              (f"{NSIS_DIR}/{sig}", "text/plain", sig)]:
        if not os.path.exists(path):
            print(f"  跳过（不存在）{name}")
            continue
        if name in existing:
            gh(creds, "DELETE", f"{API}/repos/{REPO}/releases/assets/{existing[name]}")
            print(f"  删除旧资产 {name}")
        print(f"  上传 {name} ({os.path.getsize(path)} bytes) …")
        up = curl_upload(token, f"{UPLOAD}/repos/{REPO}/releases/{rid}/assets?name={name}",
                         path, ctype, tmp_out)
        print(f"    完成 asset_id={up['id']}")
        if name == exe:
            exe_asset_id = up["id"]
    if os.path.exists(tmp_out):
        os.remove(tmp_out)

    if not exe_asset_id:
        sys.exit("安装包未上传成功，无法生成 latest.json")

    print("== 4/5 生成并上传 latest.json ==")
    latest_bytes = json.dumps(build_latest(exe_asset_id), ensure_ascii=False, indent=2).encode("utf-8")
    print("  下载地址:", json.loads(latest_bytes)["platforms"]["windows-x86_64"]["url"])
    if "latest.json" in existing:
        gh(creds, "DELETE", f"{API}/repos/{REPO}/releases/assets/{existing['latest.json']}")
    gh(creds, "POST",
       f"{UPLOAD}/repos/{REPO}/releases/{rid}/assets?name=latest.json",
       latest_bytes, "application/json")
    print("  上传 latest.json (%d bytes)" % len(latest_bytes))

    print("== 5/5 同步 latest.json 到仓库 ==")
    p = push_repo_latest(creds, latest_bytes, v)
    print(f"  已提交 {p}（客户端端点 raw.githubusercontent.com / jsDelivr 从这里取）")
    print("  刷新 jsDelivr 缓存:", "OK" if purge_jsdelivr() else "失败（不影响，raw 端点不受缓存影响）")
    print("完成。客户端将在下次检查时收到", tag)


if __name__ == "__main__":
    main()
