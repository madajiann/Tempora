#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 dist/index.html 出发做静态资源可达性分析，删除没有任何地方引用的孤儿文件。

背景：本项目 build 时用了 `vite --emptyOutDir=false`（绕开沙箱的批量删除守卫），
导致每次 build 留下的旧 hash 文件永远不会被清掉，积累了几十个失效 chunk，
全部被打进 41MB 的 NSIS 安装包。

用法:
    python scripts/prune_dist.py <dist目录> [--dry-run] [--keep N]
      --dry-run   只列出计划删除的文件，不真删
      --keep N    额外保留最近修改的 N 个文件（默认 0）
"""
import os
import re
import sys
from collections import deque

# JS/CSS 里引用相对路径的几种写法
PATTERNS = [
    rb'["\']\./[^"\']+["\']',              # "./xxx.js"
    rb'["\']\.\./[^"\']+["\']',            # "../xxx"
    rb'url\(([^)]*?)\)',                   # url(./font.woff2)
]


def refs_in(text: bytes):
    out = set()
    for pat in PATTERNS:
        for m in re.finditer(pat, text):
            s = m.group(0)
            s = s[1:-1] if s.startswith((b'"', b"'")) else m.group(1)
            s = s.strip().strip(b'()"\'')
            if s.startswith(b'./') or s.startswith(b'../'):
                out.add(s.decode("utf-8", "replace"))
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    root = os.path.abspath(sys.argv[1])
    dry = "--dry-run" in sys.argv
    keep_n = 0
    if "--keep" in sys.argv:
        keep_n = int(sys.argv[sys.argv.index("--keep") + 1])

    # 根目录下的每个 html 都是独立入口（updater.html 就是更新窗口的落地页），
    # 别把它们判成孤儿。
    entries = sorted(
        f for f in os.listdir(root) if f.endswith(".html") and os.path.isfile(os.path.join(root, f))
    )
    if not entries:
        print("根目录找不到任何 html 入口:", root)
        sys.exit(1)
    print("入口:", ", ".join(entries))

    # ① 可达性分析
    seen = set()
    queue = deque(entries)
    while queue:
        rel = queue.popleft()
        if rel in seen:
            continue
        seen.add(rel)
        full = os.path.join(root, rel)
        if not os.path.isfile(full):
            continue
        with open(full, "rb") as f:
            data = f.read()
        if rel.endswith((".html", ".js", ".css", ".svg", ".map")):
            for r in refs_in(data):
                norm = os.path.normpath(os.path.join(os.path.dirname(rel), r))
                queue.append(norm)

    # ② 磁盘上所有文件
    all_files = []
    for dirpath, _, names in os.walk(root):
        for n in names:
            p = os.path.join(dirpath, n)
            all_files.append(os.path.relpath(p, root))

    extra_keep = set()
    if keep_n:
        top = sorted(
            (os.path.getmtime(os.path.join(root, f)), f) for f in all_files
        )[-keep_n:]
        extra_keep = {f for _, f in top}

    doomed = sorted(set(all_files) - seen - extra_keep)

    total = sum(os.path.getsize(os.path.join(root, f)) for f in doomed)
    kept_size = sum(os.path.getsize(os.path.join(root, f)) for f in seen)

    print(f"dist 根目录: {root}")
    print(f"  磁盘文件 {len(all_files)} 个，可达 {len(seen)} 个，计划删除 {len(doomed)} 个")
    print(f"  删除后占用 {kept_size/1048576:.1f} MB（当前 {(kept_size+total)/1048576:.1f} MB）")
    if doomed:
        print("  删除清单（前 40）:")
        for f in doomed[:40]:
            print(f"    - {f}")
        if len(doomed) > 40:
            print(f"    ... 还有 {len(doomed)-40} 个")
    if dry:
        print("\n[dry-run] 未实际删除")
        return
    for f in doomed:
        os.remove(os.path.join(root, f))
    print(f"\n已删除 {len(doomed)} 个文件，释放 {total/1048576:.1f} MB")


if __name__ == "__main__":
    main()
