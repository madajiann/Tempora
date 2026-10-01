# -*- coding: utf-8 -*-
"""发版中断后补完 latest.json。

场景：release_updater.py 上传 38MB 安装包时中断（urllib write timeout / curl 断流），
但 Release 与安装包资产已经就位，只差 latest.json。本脚本从线上 Release
读回安装包的 asset id，生成 latest.json 并分发到两处：

  1. Release 资产（海外 / 直接下载用）
  2. 仓库 updates/latest.json（客户端端点 raw.githubusercontent.com / jsDelivr 用）

用法:
  python finalize_latest.py 0.1.7 --notes "更新说明"
"""
import argparse, base64, json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import release_updater as ru  # noqa: E402  复用 gh / push_repo_latest / purge_jsdelivr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version")
    ap.add_argument("--notes", default="")
    ap.add_argument("--token", default=None)
    args = ap.parse_args()

    token = ru.load_token(args.token)
    creds = base64.b64encode(f"madajiann:{token}".encode()).decode()
    v = args.version.lstrip("v")
    tag = f"v{v}"
    exe = f"Tempora_{v}_x64-setup.exe"

    print("== 1/4 从线上 Release 取安装包 asset id ==")
    rel = json.load(ru.gh(creds, "GET", f"{ru.API}/repos/{ru.REPO}/releases/tags/{tag}"))
    assets = {a["name"]: a["id"] for a in rel.get("assets", [])}
    exe_id = assets.get(exe)
    if not exe_id:
        sys.exit(f"{tag} 上找不到 {exe}，请先确认安装包已上传")
    print(f"   release id={rel['id']}  {exe} asset_id={exe_id}")

    print("== 2/4 生成 latest.json ==")
    sig_path = f"{ru.NSIS_DIR}/{exe}.sig"
    signature = open(sig_path, encoding="utf-8").read().strip() if os.path.exists(sig_path) else ""
    if not signature:
        print("   [!] 本地找不到 .sig，latest.json 将不带签名（客户端会拒绝安装）")
    latest = {
        "version": v,
        "notes": args.notes or f"Tempora {v}",
        "pub_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platforms": {
            "windows-x86_64": {
                **({"signature": signature} if signature else {}),
                "url": f"{ru.API}/repos/{ru.REPO}/releases/assets/{exe_id}",
            }
        },
    }
    latest_bytes = json.dumps(latest, ensure_ascii=False, indent=2).encode("utf-8")
    print("   下载地址:", latest["platforms"]["windows-x86_64"]["url"])
    open(f"latest.v{v}.json", "wb").write(latest_bytes)

    print("== 3/4 上传 latest.json 到 Release ==")
    if "latest.json" in assets:
        ru.gh(creds, "DELETE", f"{ru.API}/repos/{ru.REPO}/releases/assets/{assets['latest.json']}")
        print("   已删除旧 latest.json 资产")
    tmp = "latest.json.tmp"
    open(tmp, "wb").write(latest_bytes)
    up = ru.curl_upload(token,
                        f"{ru.UPLOAD}/repos/{ru.REPO}/releases/{rel['id']}/assets?name=latest.json",
                        tmp, "application/json", "latest_upload_result.json")
    os.remove(tmp)
    if os.path.exists("latest_upload_result.json"):
        os.remove("latest_upload_result.json")
    print("   asset_id=", up["id"])

    print("== 4/4 同步到仓库 updates/latest.json ==")
    p = ru.push_repo_latest(creds, latest_bytes, v)
    print("   已提交", p)
    print("   jsDelivr 缓存刷新:", "OK" if ru.purge_jsdelivr() else "失败（raw 端点不受缓存影响）")
    print("完成：客户端端点已可读到 v" + v)


if __name__ == "__main__":
    main()
