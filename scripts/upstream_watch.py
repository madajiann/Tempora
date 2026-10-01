# -*- coding: utf-8 -*-
"""上游更新追踪 —— Tempora「自己更新」的弹药来源。

Tempora 是**复制式 fork**（拷贝上游代码 + 重写壳），不是 GitHub fork，
所以 `git fetch upstream` 拿不到东西。更新内容只能靠本脚本抓：
  上游 releases (release notes) + commits (实际改了哪些文件)

用法：
  python scripts/upstream_watch.py                     # 默认看最近 30 天
  python scripts/upstream_watch.py --since 2026-08-01  # 指定起点
  python scripts/upstream_watch.py --since 2026-08-01 --record v2.8.0   # 标记已吸收

产物：docs/upstream-brief.md（人工过一遍，决定哪些移植进 Tempora）
token 来源同 release_updater.py：--token > TEMPORA_GH_TOKEN > ~/.tempora/token
"""
import argparse, base64, json, os, re, sys, urllib.request

UPSTREAM = "esengine/DeepSeek-Reasonix"
API = "https://api.github.com"
TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".tempora", "token")
BRIEF = "docs/upstream-brief.md"
LOG = "docs/UPSTREAM_LOG.md"

# 关键词判定：哪些上游变更 Tempora 已经落地 / 值得移植 / 与轻便版无关
ALREADY = ["tauri", "托盘", "自动更新", "updater", "桌面图标", "启动动画", "安装器",
           "nsis", "chinese", "simplified"]
PORT = ["性能", "启动", "内存", "体积", "cache", "缓存", "sse", "stream", "会话",
        "session", "插件", "plugin", "终端", "terminal", "mcp", "provider",
        "model", "diff", "edit", "tool", "agent", "上下文", "context", "compact"]
SKIP = ["electron", "benchmark", "docker", "yomm", "workflow", "release pipeline",
        "homebrew", "brew", "docs/", "readme", "chore", "ci", "lint", "format"]


def load_token(cli=None):
    tok = cli or os.environ.get("TEMPORA_GH_TOKEN", "").strip()
    if not tok and os.path.exists(TOKEN_FILE):
        tok = open(TOKEN_FILE, encoding="utf-8").read().strip()
    return tok


def gh(token, url):
    creds = base64.b64encode(f"madajiann:{token}".encode()).decode()
    req = urllib.request.Request(url, headers={
        "Authorization": "Basic " + creds,
        "User-Agent": "tempora-upstream-watch",
        "Accept": "application/vnd.github+json",
    })
    return json.load(urllib.request.urlopen(req, timeout=60))


def hit(text, words):
    """词边界匹配，避免 'ci' 命中 'service' 这类假阳性"""
    return [w for w in words if re.search(r"\b" + re.escape(w) + r"\b", text)]


def classify(text):
    low = text.lower()
    a, p, s = hit(low, ALREADY), hit(low, PORT), hit(low, SKIP)
    if a:
        return "已落地", "Tempora 已自行实现（壳/图标/更新链）· 命中 " + "/".join(a)
    if len(s) > len(p):
        return "跳过", "与轻便版无关 · 命中 " + "/".join(s)
    if p:
        return "待评估", "可能值得移植 · 命中 " + "/".join(p) + "，需按 CUTLIST 红线复核"
    return "观察", "无关键词命中，扫一眼"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None, help="起点日期 YYYY-MM-DD，默认 30 天前")
    ap.add_argument("--token", default=None)
    ap.add_argument("--record", default=None, metavar="TAG", help="把某个上游 tag 记入已吸收日志")
    ap.add_argument("--out", default=BRIEF)
    args = ap.parse_args()

    token = load_token(args.token)
    if not token:
        sys.exit("缺少 GitHub token，请写 " + TOKEN_FILE)
    since = args.since
    if not since:
        import datetime
        since = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()

    seen = set()
    if os.path.exists(LOG):
        seen = set(re.findall(r"\|\s*`?(v?[\w.\-+]+)`?\s*\|", open(LOG, encoding="utf-8").read()))

    print(f"== 上游 {UPSTREAM} 自 {since} 起的变更 ==")

    print("== 拉取 releases ==")
    releases = [r for r in gh(token, f"{API}/repos/{UPSTREAM}/releases?per_page=40")
                if (r.get("published_at") or "")[:10] >= since]

    print("== 拉取 commits ==")
    commits = gh(token, f"{API}/repos/{UPSTREAM}/commits?per_page=60&since={since}T00:00:00Z")
    print(f"  releases={len(releases)}  commits={len(commits)}")

    lines = []
    lines.append(f"# 上游变更简报（自 {since} 起）\n")
    lines.append(f"- 上游：`{UPSTREAM}`（MIT © Reasonix Contributors）")
    lines.append("- 移植要求：**保留 MIT 版权声明**，改动的源文件头部补 `Ported from DeepSeek-Reasonix (MIT)。`")
    lines.append("- 红线复核：`docs/CUTLIST.md` 第 0 节（UI 1:1 / CodeMirror / 字体分片 / Go 内核 / yomm）\n")

    if args.record:
        flag = "已吸收" if args.record in seen else "新增"
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"\n| `{args.record}` | {flags_now()} | 已移植进 Tempora |\n")
        print(f"  已记录 {args.record}（{flag}）-> {LOG}")

    lines.append("## 一、上游 Release 变更\n")
    if not releases:
        lines.append("（该区间无 release）\n")
    dedup, last_note = set(), {}
    for r in releases:  # 上游同时发 vX 与 desktop-vX 两个 tag，notes 相同需去重
        key = (r.get("body") or "")[:200]
        if key in dedup:
            continue
        dedup.add(key)
        last_note[r["tag_name"]] = key
    for r in releases:
        if last_note.get(r["tag_name"]) != (r.get("body") or "")[:200]:
            continue
        verdict, why = classify(r.get("body", "") or r.get("name", ""))
        tag = r["tag_name"]
        if tag in seen:
            verdict = "已吸收"
        lines.append(f"### {tag} — {r.get('name','')}  ({r['published_at'][:10]})")
        lines.append(f"**判定：{verdict}** — {why}\n")
        body = (r.get("body") or "").strip()[:900]
        lines.append("```")
        lines.append(body or "（无 notes）")
        lines.append("```\n")

    lines.append("## 二、上游 Commits（按改动域归类）\n")
    groups = {}
    for c in commits:
        files = [f["filename"] for f in c.get("files", [])] or ["(源码外)"]
        dom = "frontend" if any("/src/" in x or x.endswith((".ts", ".tsx")) for x in files) else \
              "kernel" if any(x.startswith(("internal/", "cmd/", "go.mod")) for x in files) else "其他"
        groups.setdefault(dom, []).append(c)
    for dom, cs in groups.items():
        lines.append(f"### {dom}（{len(cs)} 条）\n")
        for c in cs[:20]:
            msg = (c["commit"]["message"].split("\n")[0])[:110]
            v, why = classify(msg + " " + " ".join(f["filename"] for f in c.get("files", [])))
            lines.append(f"- `{c['sha'][:7]}` {msg} — **{v}**")
        lines.append("")
    if not commits:
        lines.append("（该区间无 commit）\n")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"简报已写入 {args.out}")


def flags_now():
    import datetime
    return datetime.date.today().isoformat()


if __name__ == "__main__":
    main()
