# -*- coding: utf-8 -*-
"""把远端 main 对齐到本地 commit 对象，并创建 v0.1.28 tag。

背景：远端 main 已是本次发布的等价内容（tree sha 完全相同），但 commit
sha 与本地不同（早前用旧脚本 push_via_api.py 重建，committer 信息有别），
本地 git 对象库里不存在那个远端 sha，导致 push_git_api.py 的
`rev-list A..B` 直接失败。

本脚本绕开 git 本地对象库：
  1. 用本地 commit 的 tree/parent/message/author/committer 调 API 建 commit
  2. 回读校验 tree sha 与文件数与本地一致后，才动 ref
  3. 更新 refs/heads/main（force，因为远端那条是兄弟节点不是祖先）
  4. 建 annotated tag refs/tags/v0.1.28

用法:
    python scripts/align_release_ref.py <local_sha> <tag_name>
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
    req.add_header("User-Agent", "tempora-align")
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


def git(*args):
    out = subprocess.run(["git", *args], capture_output=True, cwd=REPO_DIR)
    if out.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {out.stderr.decode('utf-8','replace')[:400]}")
    return out.stdout.decode("utf-8", "replace")


def main():
    local_sha = git("rev-parse", sys.argv[1].strip()).strip()
    tag_name = sys.argv[2].strip()

    tree_sha = git("rev-parse", f"{local_sha}^{{tree}}").strip()
    parents = git("rev-list", "--parents", "-n", "1", local_sha).strip().split()[1:]
    msg = git("show", "-s", "--format=%B", local_sha)
    au = git("show", "-s", "--format=%an%n%ae%n%aI", local_sha).strip().split("\n")
    co = git("show", "-s", "--format=%cn%n%ce%n%cI", local_sha).strip().split("\n")
    local_files = len([x for x in git("diff-tree", "--no-commit-id", "--name-only", "-r",
                                     local_sha).strip().split("\n") if x])

    print(f"== 本地 commit {local_sha}")
    print(f"   tree    = {tree_sha}")
    print(f"   parents = {[p[:12] for p in parents]}")
    print(f"   files   = {local_files}")

    payload = {
        "message": msg,
        "tree": tree_sha,
        "parents": parents,
        "author": {"name": au[0], "email": au[1], "date": au[2]},
        "committer": {"name": co[0], "email": co[1], "date": co[2]},
    }
    print("== 1/4 建 commit 对象（不动 ref）==")
    r = api("POST", f"/repos/{REPO}/git/commits", payload=payload)
    got = r.get("sha", "")
    if not got:
        sys.exit(f"建 commit 失败：{r}")
    print(f"   远端 commit = {got}")
    print(f"   {'sha 与本地一致 ✓' if got == local_sha else 'sha 与本地不同（内容仍需校验）'}")

    print("== 2/4 回读校验内容 ==")
    chk = api("GET", f"/repos/{REPO}/git/commits/{got}")
    chk_tree = chk.get("tree", {}).get("sha", "")
    chk_files = len([f for f in chk.get("files", []) if f])
    if not chk_files:
        chk2 = api("GET", f"/repos/{REPO}/commits/{got}")
        chk_files = len(chk2.get("files", []))
    print(f"   tree = {chk_tree}  (本地 {tree_sha})")
    print(f"   files = {chk_files}  (本地 {local_files})")
    if chk_tree != tree_sha:
        sys.exit("tree 不一致，拒绝更新 ref")
    if chk_files != local_files:
        sys.exit(f"文件数不一致（远端 {chk_files} / 本地 {local_files}），拒绝更新 ref")

    print("== 3/4 更新 refs/heads/main ==")
    cur = api("GET", f"/repos/{REPO}/git/ref/heads/main").get("object", {}).get("sha", "")
    print(f"   当前 main = {cur[:12]}")
    if cur != got:
        api("PATCH", f"/repos/{REPO}/git/refs/heads/main",
            payload={"sha": got, "force": True})
        print(f"   main -> {got}")
    else:
        print("   main 已是目标，无需更新")

    print(f"== 4/4 创建 tag {tag_name} ==")
    tag_raw = git("cat-file", "-p", tag_name)
    obj_sha, tname, temail, tdate = got, "madajiann", "751262@qq.com", None
    for line in tag_raw.split("\n"):
        if line.startswith("object "):
            obj_sha = line.split(" ", 1)[1].strip()
        elif line.startswith("tagger "):
            rest = line[len("tagger "):]
            tname = rest.split(" <")[0]
            if "<" in rest and ">" in rest:
                temail = rest.split("<")[1].split(">")[0]
    # GitHub API 只认 ISO 8601，不能用 git 的 "unix +0800" 原始格式。
    tdate = git("for-each-ref", "--format=%(taggerdate:iso-strict)",
                f"refs/tags/{tag_name}").strip() or None
    tag_msg = git("for-each-ref", "--format=%(contents)", f"refs/tags/{tag_name}").strip()
    tag_payload = {
        "tag": tag_name,
        "message": tag_msg,
        # 必须指向远端存在的 commit：本地那个 sha（远端没有）不能用作 tag 目标，
        # 否则 GitHub 报 "Could not verify object"。两者 tree 完全一致，内容等价。
        "object": got,
        "type": "commit",
        "tagger": {"name": tname, "email": temail,
                   "date": tdate or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
    }
    tr = api("POST", f"/repos/{REPO}/git/tags", payload=tag_payload)
    tag_sha = tr.get("sha", "")
    if not tag_sha:
        # tag 对象已存在：直接读回
        t = api("GET", f"/repos/{REPO}/git/ref/tags/{tag_name}")
        tag_sha = t.get("object", {}).get("sha", "")
        print(f"   tag 对象已存在 = {tag_sha}")
    else:
        print(f"   tag object = {tag_sha}")
    if tag_sha:
        # ref 可能还不存在：先 POST 创建，已存在再 PATCH 更新。
        cr = api("POST", f"/repos/{REPO}/git/refs",
                 payload={"ref": f"refs/tags/{tag_name}", "sha": tag_sha}, soft=True)
        if "_error" in cr:
            api("PATCH", f"/repos/{REPO}/git/refs/tags/{tag_name}",
                payload={"sha": tag_sha, "force": True})
            print(f"   refs/tags/{tag_name} -> {tag_sha} (patch)")
        else:
            print(f"   refs/tags/{tag_name} -> {tag_sha} (created)")

    print("\n完成。main =", got, "| tag =", tag_name, "->", tag_sha)


if __name__ == "__main__":
    main()
