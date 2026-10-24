# -*- coding: utf-8 -*-
"""用 GitHub Git Data API 推送本地 commit（保留原 sha，不重建 commit）。

背景：git push 走的 https 通道在本机被代理截断（502 / TLS EOF），但
api.github.com 稳定可达。`push_via_api.py` 会按断点重建 blob/tree/commit，
每次生成与本地不同的新 commit，导致本地与远端历史分叉。本脚本不同：
它把**本地已有的对象原样上传**，commit 的 tree/parent/message/author
全部取自本地，最终远端 commit sha 与本地完全一致。

用法:
    python scripts/push_git_api.py <local_sha> [--ref refs/heads/main] [--tag v0.1.28]
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
        if not os.path.exists(TOKEN_FILE):
            sys.exit("找不到 GitHub token：请设 TEMPORA_GH_TOKEN 或写 " + TOKEN_FILE)
        tok = open(TOKEN_FILE, encoding="utf-8").read().strip()
    return tok


def api(method, path, payload=None, raw=None, content_type="application/json", soft=False):
    """发一次 API 请求。payload 是要 JSON 化的对象，raw 是要原样上传的字节。

    soft=True 时不抛错，返回 {"_error": ...}，用于「存在性检查」这类
    404 属于正常答案的调用。
    """
    tok = load_token()
    url = path if path.startswith("http") else f"{API}{path}"
    if raw is not None:
        body = raw
    elif payload is None:
        body = None
    else:
        body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "tempora-push")
    if body is not None:
        req.add_header("Content-Type", content_type)
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
            if e.code == 404 and soft:
                return {"_error": f"HTTP 404"}
            last = f"HTTP {e.code}\n{detail[:600]}"
            if e.code in (404, 422):
                break  # 这类错误重试也没用
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


def object_types(shas):
    """一次性拿到一批对象的类型，避免逐个起进程。"""
    if not shas:
        return {}
    proc = subprocess.run(["git", "cat-file", "--batch-check"], input="\n".join(shas),
                          capture_output=True, text=True, cwd=REPO_DIR)
    types = {}
    for line in proc.stdout.strip().split("\n"):
        p = line.split()
        if len(p) >= 2:
            types[p[0]] = p[1]
    return types


def cat_blob(sha):
    proc = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True, cwd=REPO_DIR)
    return proc.stdout


def cat_tree(sha):
    """解析原始 tree 对象，返回条目列表。"""
    raw = subprocess.run(["git", "cat-file", "tree", sha], capture_output=True, cwd=REPO_DIR).stdout
    out = []
    i = 0
    while i < len(raw):
        sp = raw.index(b" ", i)
        mode = raw[i:sp].decode()
        nul = raw.index(b"\x00", sp)
        name = raw[sp + 1:nul].decode("utf-8", "surrogateescape")
        child = raw[nul + 1:nul + 21].hex()
        i = nul + 21
        out.append((name, mode, child))
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    target = sys.argv[1].strip()
    ref = "refs/heads/main"
    if "--ref" in sys.argv:
        ref = sys.argv[sys.argv.index("--ref") + 1]
    tag_name = ""
    if "--tag" in sys.argv:
        tag_name = sys.argv[sys.argv.index("--tag") + 1].strip()

    commit_sha = git("rev-parse", target).strip()
    tree_sha = git("rev-parse", f"{commit_sha}^{{tree}}").strip()
    parents = git("rev-list", "--parents", "-n", "1", commit_sha).strip().split()[1:]
    print(f"== 目标 commit {commit_sha} -> {ref} ==")

    remote = api("GET", f"/repos/{REPO}/git/ref/{ref.replace('refs/', '')}")
    base_sha = remote.get("object", {}).get("sha", "")
    print(f"   远端 {ref} = {base_sha[:12] or '(无)'}")

    rng = f"{base_sha}..{commit_sha}" if base_sha else commit_sha
    obj_lines = [l.split(" ", 1)[0] for l in git("rev-list", "--objects", rng).strip().split("\n") if l]
    types = object_types(obj_lines)
    blobs = [s for s in obj_lines if types.get(s) == "blob"]
    trees = [s for s in obj_lines if types.get(s) == "tree"]

    print(f"== 1/4 上传 blob（{len(blobs)} 个，并发 6）==")
    from concurrent.futures import ThreadPoolExecutor

    def blob_exists(sha):
        r = api("GET", f"/repos/{REPO}/git/blobs/{sha}", soft=True)
        return "_error" not in r

    # 先查远端已有哪些，避免重复上传（重跑时几乎全部命中）。
    with ThreadPoolExecutor(max_workers=8) as pool:
        exists_flags = list(pool.map(blob_exists, blobs))
    missing = [s for s, e in zip(blobs, exists_flags) if not e]
    print(f"   远端已有 {len(blobs) - len(missing)}，需上传 {len(missing)}")

    def put_blob(sha):
        data = cat_blob(sha)
        return api("POST", f"/repos/{REPO}/git/blobs",
                   payload={"content": base64.b64encode(data).decode(), "encoding": "base64"})

    blob_count = 0
    done = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        for r in pool.map(put_blob, missing):
            done += 1
            if not r.get("_exists"):
                blob_count += 1
            if done % 25 == 0:
                print(f"   {done}/{len(missing)}（新增 {blob_count}）")
    print(f"   新增 blob: {blob_count}/{len(missing)}")

    print(f"== 2/4 上传 tree（{len(trees)} 个）==")
    # tree 之间有引用顺序：创建父 tree 时它引用的子树必须已在远端存在。
    # 深度只是提示（路径 'app/frontend/src' 比 'app' 深），真正的保证是
    # 拓扑重试：这一轮建不成的留到下一轮，直到不再有进展。
    paths = {}
    for line in git("rev-list", "--objects", rng).strip().split("\n"):
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1]:
            paths[parts[0]] = parts[1]

    def depth(sha):
        p = paths.get(sha, "")
        return p.count("/") + 1 if p else 0

    trees.sort(key=depth, reverse=True)
    pending = []
    for tsha in trees:
        items = cat_tree(tsha)
        if not items:
            continue
        entries_out = []
        for name, mode, child in items:
            ctype = types.get(child) or object_types([child]).get(child, "blob")
            # git 原始 tree 里目录写 40000（5 位无前导零），GitHub API 要 040000。
            if mode == "40000":
                mode = "040000"
            entries_out.append({"path": name, "mode": mode, "type": ctype, "sha": child})
        pending.append((tsha, entries_out))

    tree_count = 0
    round_no = 0
    while pending:
        round_no += 1
        nxt = []
        failed_msgs = []
        for tsha, entries_out in pending:
            r = api("POST", f"/repos/{REPO}/git/trees", payload={"tree": entries_out}, soft=True)
            if r.get("_exists"):
                continue
            if "_error" in r:
                failed_msgs.append((tsha, r["_error"]))
                nxt.append((tsha, entries_out))
            else:
                tree_count += 1
        print(f"   第 {round_no} 轮：建成 {len(pending) - len(nxt)}/{len(pending)}，待建 {len(nxt)}")
        if len(nxt) == len(pending):
            # 一轮下来一个都没建成：报第一个错误，别死循环。
            tsha, msg = failed_msgs[0]
            sys.exit(f"tree {tsha[:12]} 无法创建：{msg[:300]}")
        pending = nxt
    print(f"   新增 tree: {tree_count}")

    print("== 3/4 创建 commit（复用本地内容）==")
    msg = git("show", "-s", "--format=%B", commit_sha)
    au = git("show", "-s", "--format=%an%n%ae%n%aI", commit_sha).strip().split("\n")
    co = git("show", "-s", "--format=%cn%n%ce%n%cI", commit_sha).strip().split("\n")
    payload = {
        "message": msg,
        "tree": tree_sha,
        "parents": parents,
        "author": {"name": au[0], "email": au[1], "date": au[2]},
        "committer": {"name": co[0], "email": co[1], "date": co[2]},
    }
    r = api("POST", f"/repos/{REPO}/git/commits", payload=payload)
    got = r.get("sha", "")
    print(f"   远端 commit = {got}")
    if got != commit_sha:
        print(f"   [!] sha 与本地不同（本地 {commit_sha}），继续用远端 sha")

    print("== 4/4 更新 ref ==")
    api("PATCH", f"/repos/{REPO}/git/refs/{ref.replace('refs/', '')}",
        payload={"sha": got, "force": False})
    print(f"   {ref} -> {got}")

    if tag_name:
        print(f"== 5/5 打 tag {tag_name} ==")
        tag_raw = git("cat-file", "-p", tag_name)
        obj_sha, tagger_name, tagger_email, tagger_date = got, "madajiann", "751262@qq.com", None
        for line in tag_raw.split("\n"):
            if line.startswith("object "):
                obj_sha = line.split(" ", 1)[1].strip()
            elif line.startswith("tagger "):
                rest = line[len("tagger "):]
                tagger_name = rest.split(" <")[0]
                if "<" in rest and ">" in rest:
                    tagger_email = rest.split("<")[1].split(">")[0]
                if "> " in rest:
                    tagger_date = rest.split("> ", 1)[1].strip()
        tag_msg = git("for-each-ref", "--format=%(contents)", f"refs/tags/{tag_name}").strip()
        tag_payload = {
            "tag": tag_name,
            "message": tag_msg,
            "object": obj_sha,
            "type": "commit",
            "tagger": {"name": tagger_name, "email": tagger_email,
                       "date": tagger_date or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
        }
        r = api("POST", f"/repos/{REPO}/git/tags", payload=tag_payload)
        tag_sha = r.get("sha", "")
        print(f"   tag object = {tag_sha}")
        if tag_sha:
            api("PATCH", f"/repos/{REPO}/git/refs/tags/{tag_name}",
                payload={"sha": tag_sha, "force": True})
            print(f"   refs/tags/{tag_name} -> {tag_sha}")

    print("\n完成。远端 main =", got)


if __name__ == "__main__":
    main()
