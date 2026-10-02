#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tempora 旧版本与垃圾清理。

分三类：
  1) G:/Tempora 根目录的旧安装包（v0.1.0 ~ v0.1.15）——GitHub Release 上
     v0.1.12~v0.1.16 随时可下载，本地这份是冗余
  2) D:/Tempora 的 .bak-* / .old-* / *.bak 目录——部署目录的历次备份
  3) C:/Users/.../AppData/Local/Temp 的工作临时文件

用法:
    python scripts/cleanup_old_versions.py --dry-run   # 只列清单
    python scripts/cleanup_old_versions.py             # 执行删除
"""
from __future__ import annotations

import os
import sys
import time
import glob

DRY = "--dry-run" in sys.argv

USER = os.path.expanduser("~")
TMP = os.path.join(USER, "AppData", "Local", "Temp")

# 1) G 盘根目录旧安装包：0.1.0 ~ 0.1.15（0.1.16 在 target/ 下，不动）
G_OLD_VERSIONS = [
    "0.1.0", "0.1.1", "0.1.2", "0.1.3", "0.1.4", "0.1.5", "0.1.6", "0.1.7",
    "0.1.8", "0.1.9", "0.1.10", "0.1.11", "0.1.12", "0.1.13", "0.1.14", "0.1.15",
]

# G 盘根目录下划线前缀的临时/调试产物（保留 NSIS 离线包，重装环境要用）
G_KEEP_TEMP = {"_nsis311.zip", "_nsis_tauri_utils.dll"}

# 2) D 盘部署目录：只保留这些（当前运行所需）
D_KEEP = {
    "tempora-shell.exe", "tempora.exe", "uninstall.exe",
    "frontend-next", "Tempora-Fix-Restart.bat", "updater.log",
}

# 3) C 盘 Temp：只删这些明确的工作产物，其余（第三方软件目录）不动
TMP_PATTERNS = ["*.tmp", "probe.bin", "x.exe", "verify_*.exe", "wa.zip",
                "base_zip.zip", ".gitignore"]
TMP_DIR_PATTERNS = ["HeadlessChrome for Testing*", "_chromeprof*"]
TMP_SCREENSHOTS = "ScreenShot_*.png"


def sizeof(path: str) -> int:
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0
    total = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def collect() -> list[tuple[str, int, str]]:
    """返回 [(路径, 字节, 类别)]"""
    items: list[tuple[str, int, str]] = []

    # --- G 盘旧安装包 ---
    for v in G_OLD_VERSIONS:
        for pat in (f"Tempora_{v}_x64-setup.exe",
                    f"Tempora_{v}_x64-setup.exe.sig",
                    f"Tempora_{v}_x64-portable.zip",
                    f"SHA256SUMS-v{v}.txt",
                    f"update-to-{v}.bat"):
            p = os.path.join(r"G:\Tempora", pat)
            if os.path.exists(p):
                items.append((p, sizeof(p), "G-旧安装包"))

    # --- G 盘下划线临时文件 ---
    for p in glob.glob(os.path.join(r"G:\Tempora", "_*")):
        if os.path.basename(p) in G_KEEP_TEMP:
            continue
        if os.path.isfile(p):
            items.append((p, sizeof(p), "G-调试临时"))

    # --- D 盘备份 ---
    for p in glob.glob(os.path.join(r"D:\Tempora", "*")):
        name = os.path.basename(p)
        if name in D_KEEP:
            continue
        items.append((p, sizeof(p), "D-部署备份"))

    # --- C 盘 Temp ---
    for pat in TMP_PATTERNS:
        for p in glob.glob(os.path.join(TMP, pat)):
            if os.path.isfile(p):
                items.append((p, sizeof(p), "C-临时文件"))
    for pat in TMP_DIR_PATTERNS:
        for p in glob.glob(os.path.join(TMP, pat)):
            if os.path.isdir(p):
                items.append((p, sizeof(p), "C-临时目录"))
    for p in glob.glob(os.path.join(TMP, TMP_SCREENSHOTS)):
        if os.path.isfile(p):
            items.append((p, sizeof(p), "C-截图"))
    return items


def main() -> None:
    items = collect()
    if not items:
        print("没有需要清理的文件")
        return

    by_cat: dict[str, list[tuple[str, int, str]]] = {}
    for it in items:
        by_cat.setdefault(it[2], []).append(it)

    print("=" * 78)
    print(f"{'清理清单':^70}")
    print("=" * 78)
    grand = 0
    for cat in sorted(by_cat):
        sub = by_cat[cat]
        tot = sum(x[1] for x in sub)
        grand += tot
        print(f"\n【{cat}】 {len(sub)} 项  {tot / 1048576:.1f} MB")
        for p, sz, _ in sorted(sub, key=lambda x: -x[1])[:12]:
            print(f"    {sz / 1048576:9.2f} MB  {p}")
        if len(sub) > 12:
            print(f"    ... 还有 {len(sub) - 12} 项")
    print("\n" + "=" * 78)
    print(f"合计 {len(items)} 项，{grand / 1048576:.1f} MB")

    if DRY:
        print("\n[dry-run] 未执行删除。去掉 --dry-run 正式执行。")
        return

    # 保护：最近 2 小时内修改过的不删（防止误删正在写入的文件）
    now = time.time()
    done, skipped, freed = 0, 0, 0
    for p, sz, _ in items:
        try:
            if os.path.isfile(p) and now - os.path.getmtime(p) < 7200:
                skipped += 1
                continue
        except OSError:
            pass
        try:
            if os.path.isdir(p):
                import shutil
                shutil.rmtree(p, ignore_errors=True)
            else:
                os.remove(p)
            if not os.path.exists(p):
                done += 1
                freed += sz
            else:
                skipped += 1
        except Exception as e:  # noqa: BLE001
            print(f"  跳过 {p}: {e}")
            skipped += 1
    print(f"\n已删除 {done} 项，释放 {freed / 1048576:.1f} MB；跳过 {skipped} 项"
          f"（占用中或 2 小时内刚写入）")


if __name__ == "__main__":
    main()
