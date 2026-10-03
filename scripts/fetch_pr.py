# -*- coding: utf-8 -*-
"""取上游 PR 的真实改动（含 patch），供移植评估与落地使用。

为什么需要它：Tempora 是**复制式 fork**（拷贝上游代码 + 重写壳），不是 GitHub fork，
`git fetch upstream` 拿不到东西；而 `reference/DeepSeek-Reasonix` 副本容易过期。
要判断"上游这个补丁要不要移植、改动面多大"，最快的路径就是直接取 PR 的 files+patch。

用法：
  python scripts/fetch_pr.py 11479              # 概览 + 改动文件清单
  python scripts/fetch_pr.py 11479 --patch      # 打印完整 patch
  python scripts/fetch_pr.py 11479 --out p.diff # patch 存盘
  python scripts/fetch_pr.py 11479 --grep boot  # 只列路径含关键字的文件

token 来源同 upstream_watch.py：--token > TEMPORA_GH_TOKEN > ~/.tempora/token
"""
import argparse, base64, json, os, sys, time, urllib.request

UPSTREAM = "esengine/DeepSeek-Reasonix"
API = "https://api.github.com"
TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".tempora", "token")


def load_token(cli=None):
    tok = cli or os.environ.get("TEMPORA_GH_TOKEN", "").strip()
    if not tok and os.path.exists(TOKEN_FILE):
        tok = open(TOKEN_FILE, encoding="utf-8").read().strip()
    return tok


def gh(token, url, tries=4):
    """GitHub API 在本机不稳定（同一脚本内前一请求成功、后一请求 timeout 是常态），
    所以这里带退避重试，别让一次抖动把整轮移植评估打断。"""
    creds = base64.b64encode(f"madajiann:{token}".encode()).decode()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "Authorization": "Basic " + creds,
                "User-Agent": "tempora-fetch-pr",
                "Accept": "application/vnd.github+json",
            })
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:  # noqa: BLE001 - 网络抖动种类多，一律退避重试
            last = e
            if i < tries - 1:
                print(f"  (第 {i + 1} 次请求失败：{e.__class__.__name__}，2 秒后重试)",
                      file=sys.stderr)
                time.sleep(2)
    raise last


def fetch_files(token, num):
    files, page = [], 1
    while True:
        batch = gh(token, f"{API}/repos/{UPSTREAM}/pulls/{num}/files"
                          f"?per_page=100&page={page}")
        files.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pr", help="上游 PR 号，如 11479")
    ap.add_argument("--token", default=None)
    ap.add_argument("--patch", action="store_true", help="打印完整 patch")
    ap.add_argument("--out", default=None, help="patch 存盘路径")
    ap.add_argument("--grep", default=None, help="只列路径含该关键字的文件")
    args = ap.parse_args()

    tok = load_token(args.token)
    if not tok:
        sys.exit("没有 token：传 --token 或写入 ~/.tempora/token")

    meta = gh(tok, f"{API}/repos/{UPSTREAM}/pulls/{args.pr}")
    print(f"#{args.pr}  {meta['title']}")
    print(f"  状态={meta['state']}  合并={meta.get('merged')}"
          f"  base={meta['base']['ref']}  +{meta['additions']}/-{meta['deletions']}"
          f"  文件={meta['changed_files']}")
    print("  " + (meta.get("body") or "").strip().splitlines()[0][:200]
          if meta.get("body") else "")

    files = fetch_files(tok, args.pr)
    if args.grep:
        files = [f for f in files if args.grep.lower() in f["filename"].lower()]

    print(f"\n改动文件（{len(files)}）：")
    for f in files:
        print(f"  {f['status']:8} +{f['additions']:<5}-{f['deletions']:<5} {f['filename']}")

    if args.patch or args.out:
        buf = []
        for f in files:
            buf.append(f"### {f['status']}  {f['filename']}\n{f.get('patch') or '(无 patch)'}\n")
        text = "\n".join(buf)
        if args.out:
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
            open(args.out, "w", encoding="utf-8").write(text)
            print(f"\npatch 已存盘：{args.out}（{len(text)} 字节）")
        if args.patch:
            print("\n" + text)


if __name__ == "__main__":
    main()
