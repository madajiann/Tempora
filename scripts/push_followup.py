# -*- coding: utf-8 -*-
"""把本地 HEAD 的内容推到远端 main，parent 取远端当前 main。

背景：本地 commit 的 parent 是 `245400c`，而远端 main 是等价但 sha 不同的
`d9eaa03`（GitHub 把 author/committer date 归一到 UTC，本地提交时区是 +0800），
本地 git 对象库里没有远端那个 sha，所以 `rev-list <remote>..<local>` 直接
fatal: Invalid revision range。push_git_api.py 的断点算法在这里失效。

本脚本的做法：
  1. 取远端当前 main 作为新 commit 的 parent（保证快进）
  2. 只上传相对远端 tree 有变化的 blob
  3. 用 base_tree + 变化路径 POST /git/trees，得到新 tree
  4. POST /git/commits（parent = 远端 main），PATCH refs/heads/main

用法:
    python scripts/push_followup.py [local_sha]
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = "madajiann/Tempora"
API = "https://api.github.com"
REPO_DIR = "G:/Tempora"
TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".tempora", "token")


def load_token():
    tok = os.environ.get("TEMPORA_GH_TOKEN", "").strip()
    if not tok:
        tok = open(TOKEN_FILE, encoding="utf-8").read().strip()
    return tok


def api(method, path, payload=None, soft=False):
    tok = load_token()
    url = path if path.startswith("http") else f"{API}{path}"
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "tempora-followup")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    last = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = resp.read()
                return json.loads(data) if data else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")
            if e.code == 422 and "already exists" in detail:
                return {"_exists": True}
            last = f"HTTP {e.code}\n{detail[:800]}"
            if e.code in (404, 422):
                break
        except Exception as e:
            last = str(e)
        time.sleep(2 + attempt * 2)
    if soft:
        return {"_error": last}
    sys.exit(f"{method} {url} -> {last}")


def git(*args, binary=False):
    out = subprocess.run(["git", *args], capture_output=True, cwd=REPO_DIR)
    if out.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {out.stderr.decode('utf-8','replace')[:400]}")
    return out.stdout if binary else out.stdout.decode("utf-8", "replace")


def main():
    local_sha = git("rev-parse", (sys.argv[1] if len(sys.argv) > 1 else "HEAD").strip()).strip()
    local_tree = git("rev-parse", f"{local_sha}^{{tree}}").strip()

    remote = api("GET", "/repos/%s/git/ref/heads/main" % REPO)
    base_sha = remote.get("object", {}).get("sha", "")
    if not base_sha:
        sys.exit("拿不到远端 main")
    base = api("GET", "/repos/%s/git/commits/%s" % (REPO, base_sha))
    base_tree = base.get("tree", {}).get("sha", "")
    print(f"== 本地 {local_sha}  tree={local_tree}")
    print(f"   远端 main={base_sha[:12]}  tree={base_tree}")

    # 1) 找出本地相对远端 base_tree 变化的路径
    diff = git("diff", "--name-status", f"{base_tree}^{{tree}}", f"{local_tree}")
    changed = []
    for line in diff.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0][0]
        if status == "R":
            old, new = parts[1], parts[2]
            changed.append(("D", old))
            changed.append(("A", new))
        else:
            changed.append((status, parts[-1]))
    print(f"== 变化路径 {len(changed)} 个")
    for st, p in changed:
        print(f"   {st}  {p}")

    # 2) 上传新 blob
    entries = []
    for st, path in changed:
        if st == "D":
            entries.append({"path": path, "mode": "100644", "type": "commit", "sha": None})
            continue
        blob_sha = git("rev-parse", f"{local_tree}:{path}").strip()
        mode = "100755" if (st == "A" and git("ls-tree", local_tree, "--", path).startswith("100755")) else "100644"
        raw = git("cat-file", "blob", blob_sha, binary=True)
        api("POST", "/repos/%s/git/blobs" % REPO,
            payload={"content": base64.b64encode(raw).decode(), "encoding": "base64"})
        entries.append({"path": path, "mode": mode, "type": "blob", "sha": blob_sha})
        print(f"   blob 已上传 {path} ({len(raw)} 字节, {blob_sha[:12]}, {mode})")

    # 3) 建新 tree（以远端 tree 为 base，只覆盖变化路径）
    print("== 建 tree ==")
    r = api("POST", "/repos/%s/git/trees" % REPO,
            payload={"base_tree": base_tree, "tree": [e for e in entries if e["sha"]]})
    new_tree = r.get("sha", "")
    print(f"   新 tree = {new_tree}  (本地 {local_tree})")
    if new_tree != local_tree:
        print("   [!] tree sha 与本地不同，校验文件数")
        chk = api("GET", "/repos/%s/git/trees/%s?recursive=1" % (REPO, new_tree))
        if len(chk.get("tree", [])) != len(git("ls-tree", "-r", local_tree).strip().split("\n")):
            sys.exit("tree 内容不一致，拒绝提交")

    # 4) 建 commit（parent 用远端 main，保证快进）
    msg = git("show", "-s", "--format=%B", local_sha)
    au = git("show", "-s", "--format=%an%n%ae%n%aI", local_sha).strip().split("\n")
    co = git("show", "-s", "--format=%cn%n%ce%n%cI", local_sha).strip().split("\n")
    payload = {
        "message": msg,
        "tree": new_tree,
        "parents": [base_sha],
        "author": {"name": au[0], "email": au[1], "date": au[2]},
        "committer": {"name": co[0], "email": co[1], "date": co[2]},
    }
    r = api("POST", "/repos/%s/git/commits" % REPO, payload=payload)
    got = r.get("sha", "")
    print(f"== 远端 commit = {got}")
    if not got:
        sys.exit(f"建 commit 失败：{r}")

    print("== 更新 refs/heads/main ==")
    api("PATCH", "/repos/%s/git/refs/heads/main" % REPO,
        payload={"sha": got, "force": False})
    print(f"   main -> {got}")


if __name__ == "__main__":
    main()
