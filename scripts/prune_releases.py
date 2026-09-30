# -*- coding: utf-8 -*-
"""清理旧 GitHub Release，只保留最近 N 个。

用法：
  python scripts/prune_releases.py --keep 2            # 试运行，只列出将删除的
  python scripts/prune_releases.py --keep 2 --yes      # 真删

token 来源优先级：--token > 环境变量 TEMPORA_GH_TOKEN > ~/.tempora/token
"""
import argparse
import json
import os
import sys
import urllib.request

REPO = "madajiann/Tempora"
API = "https://api.github.com"


def load_token(cli_token=None):
    tok = cli_token or os.environ.get("TEMPORA_GH_TOKEN", "").strip()
    path = os.path.join(os.path.expanduser("~"), ".tempora", "token")
    if not tok and os.path.exists(path):
        tok = open(path, encoding="utf-8").read().strip()
    if not tok:
        sys.exit("找不到 GitHub token：请传 --token，或写入 " + path)
    return tok


def gh(token, method, path, data=None):
    req = urllib.request.Request(API + path, method=method, data=data, headers={
        "Authorization": "Bearer " + token,
        "User-Agent": "tempora-release",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else None
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode("utf-8", "replace")[:200]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", type=int, default=2, help="保留最近几个 Release（按发布时间）")
    ap.add_argument("--yes", action="store_true", help="真正执行删除")
    ap.add_argument("--token", default=None)
    args = ap.parse_args()

    token = load_token(args.token)
    page, all_rel = 1, []
    while True:
        batch = gh(token, "GET", f"/repos/{REPO}/releases?per_page=100&page={page}")
        if not isinstance(batch, list) or not batch:
            break
        all_rel.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    if isinstance(all_rel, dict) and "_error" in all_rel:
        sys.exit("拉取 Release 失败：" + str(all_rel))

    # 按 created_at 倒序（最新在前）
    all_rel.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    keep = all_rel[:args.keep]
    drop = all_rel[args.keep:]

    print(f"共 {len(all_rel)} 个 Release，保留 {args.keep} 个：")
    for r in keep:
        print(f"  [保留] {r['tag_name']}  ({r.get('created_at','')[:10]})")
    print(f"将删除 {len(drop)} 个：")
    for r in drop:
        size = sum(a.get("size", 0) for a in r.get("assets", []))
        print(f"  [删除] {r['tag_name']}  ({r.get('created_at','')[:10]}, "
              f"{len(r.get('assets', []))} 资产, {size/1048576:.0f} MB)")

    if not args.yes:
        print("\n试运行结束。加 --yes 才会真删。")
        return

    ok = fail = 0
    for r in drop:
        res = gh(token, "DELETE", f"/repos/{REPO}/releases/{r['id']}")
        if isinstance(res, dict) and "_error" in res:
            print(f"  删除失败 {r['tag_name']}: {res['_error']}")
            fail += 1
        else:
            print(f"  已删除 {r['tag_name']}")
            ok += 1
            gh(token, "DELETE", f"/repos/{REPO}/git/refs/tags/{r['tag_name']}")
    print(f"\n完成：删除 {ok} 个，失败 {fail} 个")


if __name__ == "__main__":
    main()
