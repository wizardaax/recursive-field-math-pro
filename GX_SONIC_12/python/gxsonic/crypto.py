"""
ed25519 keygen/sign/verify + tiny CLI
Requires: PyNaCl
"""
from __future__ import annotations
import argparse, base64, sys
from typing import Tuple
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError

# -------- Core helpers --------
def gen_keypair() -> Tuple[bytes, bytes]:
    sk = SigningKey.generate()
    pk = sk.verify_key
    return bytes(sk), bytes(pk)

def save(path: str, data: bytes) -> None:
    with open(path, "wb") as f:
        f.write(data)

def load_priv(path: str) -> SigningKey:
    with open(path, "rb") as f:
        raw = f.read().strip()
    return SigningKey(raw)

def load_pub(path: str) -> VerifyKey:
    with open(path, "rb") as f:
        raw = f.read().strip()
    return VerifyKey(raw)

def sign_bytes(priv_raw: bytes, data: bytes) -> Tuple[str, str]:
    sk = SigningKey(priv_raw)
    sig = sk.sign(data).signature
    pub_b64 = base64.b64encode(bytes(sk.verify_key)).decode("ascii")
    sig_b64 = base64.b64encode(sig).decode("ascii")
    return pub_b64, sig_b64

def verify_bytes(pub_b64: str, data: bytes, sig_b64: str) -> bool:
    try:
        vk = VerifyKey(base64.b64decode(pub_b64))
        vk.verify(data, base64.b64decode(sig_b64))
        return True
    except BadSignatureError:
        return False

# -------- Tiny CLI --------
def _cmd_gen(args):
    priv, pub = gen_keypair()
    if not args.out_priv or not args.out_pub:
        print("Specify --out-priv and --out-pub", file=sys.stderr); sys.exit(2)
    save(args.out_priv, priv)
    save(args.out_pub, pub)
    print("Wrote:", args.out_priv, args.out_pub)

def _cmd_sign(args):
    from .protocol import canonical_json_bytes
    sk = load_priv(args.priv_key)
    data = sys.stdin.buffer.read()
    pub_b64, sig_b64 = sign_bytes(bytes(sk), data)
    print(pub_b64, sig_b64)

def _cmd_verify(args):
    from .protocol import canonical_json_bytes
    vk = load_pub(args.pub_key)
    data = sys.stdin.buffer.read()
    pub_b64 = base64.b64encode(bytes(vk)).decode("ascii")
    sig_b64 = args.signature
    ok = verify_bytes(pub_b64, data, sig_b64)
    print("OK" if ok else "BAD")

def main():
    ap = argparse.ArgumentParser(prog="gxsonic.crypto")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_gen = sub.add_parser("gen", help="generate ed25519 keypair")
    ap_gen.add_argument("--out-priv", required=True)
    ap_gen.add_argument("--out-pub", required=True)
    ap_gen.set_defaults(func=_cmd_gen)

    ap_sign = sub.add_parser("sign", help="sign stdin bytes, output pub+sig (base64)")
    ap_sign.add_argument("--priv-key", required=True)
    ap_sign.set_defaults(func=_cmd_sign)

    ap_ver = sub.add_parser("verify", help="verify stdin bytes against --pub-key and --signature")
    ap_ver.add_argument("--pub-key", required=True)
    ap_ver.add_argument("--signature", required=True)
    ap_ver.set_defaults(func=_cmd_verify)

    args = ap.parse_args(); args.func(args)

if __name__ == "__main__":
    main()