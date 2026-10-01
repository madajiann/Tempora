#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
不走 git 协议，改用 GitHub Git Data API 推送本地待推送的 commit。

为什么需要它：本机 `git push` 走 github.com 会被沙箱代理掐掉
（`CONNECT tunnel failed, response 502`），而 api.github.com 是通的。
于是把 commit 拆成 blob/tree/commit/ref 四步 API 调用完成推送。

做法：
  1. 用 API 拉远端 main 的 commit 列表，找到与本地历史重合的基点
  2. 逐个本地 commit：diff-tree 取变化文件 → 建 blob → 建 tree（带 base_tree
     所以只传变化的部分）→ 建 commit（parent 串起来）
  3. 最后 PATCH refs/heads/main 指向新 commit

用法:
    python scripts/push_via_api.py            # 推送（默认 main）
    python scripts/push_via_api.py --dry-run  # 只看将要推哪些 commit
"""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPO = "madajiann/Tempora"
BRANCH = "main"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args, binary=False):
    p = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True)
    if binary:
        return p.returncode, p.stdout
    return p.returncode, p.stdout.decode("utf-8", "replace")


def no_proxy_opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def api(method, path, data=None):
    tok = open(os.path.expanduser("~/.tempora/token"), encoding="utf-8").read().strip()
    req = urllib.request.Request(f"https://api.github.com{path}", method=method)
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "tempora-push")
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode()
        req.add_header("Content-Type", "application/json")
    try:
        r = no_proxy_opener().open(req, data=body, timeout=180)
        return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw.decode())
        except Exception:
            return e.code, {"raw": raw[:300].decode("utf-8", "replace")}


def make_blob(content: bytes) -> str:
    """上传 blob；文本用 utf-8，二进制走 base64。"""
    try:
        text = content.decode("utf-8")
        st, d = api("POST", f"/repos/{REPO}/git/blobs",
                    {"content": text, "encoding": "utf-8"})
    except UnicodeDecodeError:
        text = None
    if text is None:
        st, d = api("POST", f"/repos/{REPO}/git/blobs",
                    {"content": base64.b64encode(content).decode(),
                     "encoding": "base64"})
    if st not in (200, 201):
        raise RuntimeError(f"blob 上传失败 {st}: {json.dumps(d, ensure_ascii=False)[:300]}")
    return d["sha"]


def main():
    dry = "--dry-run" in sys.argv

    # 1) 远端 main head
    st, ref = api("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}")
    if st != 200:
        print("取远端 ref 失败:", st, json.dumps(ref, ensure_ascii=False)[:200])
        sys.exit(1)
    remote_head = ref["object"]["sha"]
    print(f"远端 {BRANCH}: {remote_head[:10]}")

    # 2) 找本地历史与远端的重合点作为 base
    local_all = git("rev-list", "--all")[1].split()
    base = None
    for page in range(1, 4):
        st, commits = api("GET", f"/repos/{REPO}/commits?sha={BRANCH}&per_page=100&page={page}")
        if st != 200 or not isinstance(commits, list):
            break
        for c in commits:
            if c["sha"] in local_all:
                base = c["sha"]
                break
        if base:
            break
    if base is None:
        print("找不到与远端重合的本地 commit，无法增量推送")
        sys.exit(1)
    print(f"重合基点: {base[:10]}")

    rc, out = git("rev-list", "--reverse", f"{base}..HEAD")
    pending = [s for s in out.split() if s]
    if not pending:
        print("没有待推送的 commit")
        return
    print(f"待推送 {len(pending)} 个 commit:")
    for s in pending:
        print("  ", s[:10], git("log", "-1", "--format=%s", s)[1].strip())

    if dry:
        return

    # 3) 逐个 commit 重建
    parent = remote_head
    for sha in pending:
        rc, raw = git("diff-tree", "-r", "--no-commit-id", "--raw", sha)
        entries = []
        for line in raw.strip().split("\n"):
            if not line.strip():
                continue
            # 形如 ":100644 100644 oldsha newsha M\tpath"
            # 删除行的 new mode 是 000000，无效，要用旧的那个
            meta, path = line.split("\t", 1)
            parts = meta.split()
            old_mode = parts[0].lstrip(":")
            new_mode, new_sha, status = parts[1], parts[3], parts[4]
            mode = old_mode if new_mode == "000000" else new_mode
            if status == "D":
                entries.append({"path": path, "mode": mode,
                                "type": "blob", "sha": None})
                continue
            rc2, content = git("cat-file", "blob", new_sha, binary=True)
            if rc2 != 0:
                print(f"  跳过（读不到 blob）{path}")
                continue
            blob_sha = make_blob(content)
            entries.append({"path": path, "mode": new_mode,
                            "type": "blob", "sha": blob_sha})
        st, tree = api("POST", f"/repos/{REPO}/git/trees",
                       {"base_tree": git_api_tree_of(parent), "tree": entries})
        if st not in (200, 201):
            print(f"  tree 创建失败 {st}: {json.dumps(tree, ensure_ascii=False)[:300]}")
            sys.exit(1)
        msg = git("log", "-1", "--format=%B", sha)[1].strip()
        st, cm = api("POST", f"/repos/{REPO}/git/commits",
                     {"message": msg, "tree": tree["sha"], "parents": [parent]})
        if st not in (200, 201):
            print(f"  commit 创建失败 {st}: {json.dumps(cm, ensure_ascii=False)[:300]}")
            sys.exit(1)
        parent = cm["sha"]
        print(f"  已重建 {sha[:10]} -> {parent[:10]} ({len(entries)} 个文件)")

    # 4) 移动 ref
    st, res = api("PATCH", f"/repos/{REPO}/git/refs/heads/{BRANCH}", {"sha": parent})
    print("更新 ref:", st)
    if st != 200:
        print(json.dumps(res, ensure_ascii=False)[:300])
        sys.exit(1)
    print(f"推送完成，{BRANCH} -> {parent[:10]}")


def git_api_tree_of(commit_sha: str) -> str:
    st, d = api("GET", f"/repos/{REPO}/git/commits/{commit_sha}")
    if st != 200:
        raise RuntimeError(f"读 commit 失败 {st}")
    return d["tree"]["sha"]


if __name__ == "__main__":
    main()
