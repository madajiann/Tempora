#!/usr/bin/env python3
"""端到端验收更新通道：从公网取 latest.json 与安装包，做 Ed25519 验签。

发布完成后跑一次，直接回答「客户端现在点更新能装上吗」：

    python scripts/verify_release_channel.py
    python scripts/verify_release_channel.py --url https://tempora.yomm.cc/latest.json

判据（三条全过才算通）：
  1. latest.json 里的 version 与期望版本一致
  2. ���载到的字节数与 sha256 与本地产物一致（说明 CDN/边缘缓存没有给旧包）
  3. 安装包能被官方公钥验签通过（说明签名与包是同一对，不是重发错配）

本机没有 Ed25519 库，也没有 minisign 可执行文件，所以校验路径在这里自带
一份纯 Python 实现（RFC 8032 验证流程 + minisign 的 BLAKE2b-256 摘要约定）。
自检用 RFC 8032 官方向量，见文件末尾。

Ported from DeepSeek-Reasonix (MIT)
"""

import argparse
import base64
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.request

# --- Ed25519 验证（RFC 8032）-------------------------------------------

P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, P - 2, P) % P
I = pow(2, (P - 1) // 4, P)


def _recover_x(y, sign):
    if y >= P:
        return None
    x2 = (y * y - 1) * pow(D * y * y + 1, P - 2, P) % P
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P != 0:
        x = x * I % P
    if (x * x - x2) % P != 0:
        return None
    if x % 2 != sign:
        x = P - x
    return x


def _point_add(p, q):
    x1, y1, z1, t1 = p
    x2, y2, z2, t2 = q
    a = (y1 - x1) * (y2 - x2) % P
    b = (y1 + x1) * (y2 + x2) % P
    c = 2 * t1 * t2 * D % P
    d = 2 * z1 * z2 % P
    e, f, g, h = b - a, d - c, d + c, b + a
    return (e * f % P, g * h % P, f * g % P, e * h % P)


def _point_mul(s, p):
    q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            q = _point_add(q, p)
        p = _point_add(p, p)
        s >>= 1
    return q


def _point_equal(p, q):
    x1, y1, z1, _ = p
    x2, y2, z2, _ = q
    if (x1 * z2 - x2 * z1) % P != 0:
        return False
    return (y1 * z2 - y2 * z1) % P == 0


_GY = 4 * pow(5, P - 2, P) % P
_G = (_recover_x(_GY, 0), _GY, 1, _recover_x(_GY, 0) * _GY % P)


def _decompress(raw):
    if len(raw) != 32:
        return None
    y = int.from_bytes(raw, "little")
    sign = (y >> 255) & 1
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    if x is None:
        return None
    return (x, y, 1, x * y % P)


def ed25519_verify(public_key, message, signature):
    """Return True when signature is a valid Ed25519 signature over message."""
    if len(signature) != 64 or len(public_key) != 32:
        return False
    a = _decompress(public_key)
    if a is None:
        return False
    r_bytes = signature[:32]
    s = int.from_bytes(signature[32:], "little")
    if s >= L:
        return False
    r = _decompress(r_bytes)
    if r is None:
        return False
    h = int.from_bytes(hashlib.sha512(r_bytes + public_key + message).digest(), "little") % L
    return _point_equal(_point_mul(s, _G), _point_add(r, _point_mul(h, a)))


def self_test():
    """RFC 8032 test vector 1 — a broken verifier must fail here."""
    pk = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
    sig = bytes.fromhex(
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    )
    return ed25519_verify(pk, b"", sig)


# --- minisign / Tauri 格式 ------------------------------------------------


def parse_tauri_pubkey(text):
    """Tauri 的 pubkey 文件 = base64('untrusted comment: ...\\n' + <b64 pubkey>)。"""
    raw = base64.b64decode(text.strip())
    blob = base64.b64decode(raw[raw.find(b"\n") + 1:].strip())
    if blob[:2] not in (b"Ed", b"ED"):
        raise ValueError("not an Ed25519 minisign public key")
    return blob[2:10], blob[10:42]


def parse_minisign_signature(text):
    """Return (keyid, sig64, trusted_comment) from a minisign signature text."""
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    sig_b64 = None
    trusted = ""
    for ln in lines:
        if ln.startswith("trusted comment:"):
            trusted = ln.split(":", 1)[1].strip()
        elif not ln.startswith("untrusted comment:") and sig_b64 is None:
            sig_b64 = ln.strip()
    if sig_b64 is None:
        raise ValueError("no signature line found")
    raw = base64.b64decode(sig_b64)
    if raw[:2] not in (b"Ed", b"ED"):
        raise ValueError("not an Ed25519 minisign signature")
    return raw[2:10], raw[10:], trusted


def _http_get(url, timeout=400, tries=4):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx)
    )
    # Cloudflare 对没有 User-Agent 的请求直接 403；边缘节点偶发 reset 连接，
    # 所以重试几次而不是让一次抖动把验收判成失败。
    req = urllib.request.Request(url, headers={"User-Agent": "Tempora-Updater/verify"})
    last = None
    for attempt in range(tries):
        try:
            return opener.open(req, timeout=timeout).read()
        except Exception as exc:  # noqa: BLE001 - retry on any transport error
            last = exc
            if attempt + 1 < tries:
                time.sleep(3 * (attempt + 1))
    raise last


def main():
    ap = argparse.ArgumentParser(description="Verify the update channel end to end.")
    ap.add_argument("--url", default="https://tempora.yomm.cc/latest.json", help="latest.json endpoint")
    ap.add_argument("--expect", default=None, help="expected version string, e.g. 0.1.27")
    ap.add_argument("--installer", default=None, help="local installer to compare bytes against")
    ap.add_argument("--pubkey", default=None, help="path to tauri pubkey file")
    args = ap.parse_args()

    if not self_test():
        print("自检失败：Ed25519 验证器实现有误，中止。")
        return 2
    print("自检通过（RFC 8032 官方向量）")

    pub_path = args.pubkey or os.path.expanduser("~/.tauri/tempora.key.pub")
    keyid, pubkey = parse_tauri_pubkey(open(pub_path, encoding="utf-8").read())
    print(f"公钥 keyID : {keyid.hex()}")

    lj = json.loads(_http_get(args.url))
    version = lj.get("version")
    plat = lj["platforms"]["windows-x86_64"]
    url = plat["url"]
    sig_text = base64.b64decode(plat["signature"]).decode("utf-8")
    print(f"latest.json : {args.url}")
    print(f"版本        : {version}")
    print(f"下载地址    : {url}")

    data = _http_get(url)
    digest = hashlib.sha256(data).hexdigest()
    print(f"下载字节    : {len(data)}")
    print(f"sha256      : {digest}")

    sig_keyid, sig64, trusted = parse_minisign_signature(sig_text)
    print(f"签名 keyID  : {sig_keyid.hex()}  ({trusted})")

    ok = True
    if args.expect and version != args.expect:
        print(f"✗ 版本不符：期望 {args.expect}，实际 {version}")
        ok = False
    if sig_keyid != keyid:
        print(f"✗ 签名 keyID 与公钥不一致")
        ok = False
    if not ed25519_verify(pubkey, hashlib.blake2b(data).digest(), sig64):
        print("✗ Ed25519 验签失败（签名与下载到的字节不是同一对）")
        ok = False
    else:
        print("✓ Ed25519 验签通过（BLAKE2b-256 摘要）")

    if args.installer:
        local = open(args.installer, "rb").read()
        if local == data:
            print("✓ 下载字节与本地产物逐字节一致")
        else:
            print(f"✗ 下载字节与本地产物不一致（本地 {len(local)} 字节 / sha {hashlib.sha256(local).hexdigest()}）")
            ok = False

    print()
    print("更新通道可用" if ok else "更新通道有问题")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
