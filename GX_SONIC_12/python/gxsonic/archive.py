import json, wave, os, base64
from typing import Dict, Any, List, Optional, Tuple
from hashlib import blake2b
from .protocol import canonical_json_bytes, hash_bytes
from .synth import SynthesisParams

# ---------- WAV I/O ----------
def write_wav(path: str, samples, sr: int):
    import numpy as np
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sr)
        ints = (samples * 32767.0).clip(-32768, 32767).astype("int16")
        wf.writeframes(ints.tobytes())

# ---------- Descriptors & Manifest ----------
def _signature_block(priv_key_bytes: Optional[bytes], payload: bytes) -> Optional[Dict[str, str]]:
    if not priv_key_bytes:
        return None
    # Local import to avoid hard dep if unsigned
    from .crypto import sign_bytes
    pub_b64, sig_b64 = sign_bytes(priv_key_bytes, payload)
    return {"scheme": "ed25519", "pub": pub_b64, "sig": sig_b64}

def build_descriptor(n: int,
                     g: Dict[str, Any],
                     base_freq: float,
                     samples,
                     prev_hash: str,
                     param_commit: str,
                     p: SynthesisParams,
                     *,
                     priv_key_bytes: Optional[bytes] = None) -> Tuple[Dict[str, Any], str, str]:
    comps = g["components"]
    norm = g["norm"]
    amp_pairs = []
    for k in range(p.planes):
        amp_pairs.append([comps[2*k] / norm, comps[2*k+1] / norm])

    plane_freqs = [base_freq * (p.phi ** (k / p.spread_p)) for k in range(p.planes)]
    audio_hash = hash_bytes(samples.tobytes())

    descriptor = {
        "session_id": "demo",
        "spec_version": "GX-SONIC-12:0.1",
        "n": n,
        "alpha_inv": p.alpha_inv,
        "phi": p.phi,
        "planes": p.planes,
        "radius": g["r"],
        "angles": g["angles"],
        "revolution_counts": g["rev_counts"],
        "vector_components": comps,
        "norm": norm,
        "fundamental_freq": base_freq,
        "plane_freqs": plane_freqs,
        "amp_pairs": amp_pairs,
        "window": p.window,
        "scaling": {"f_min": p.f_min, "f_max": p.f_max, "spread_p": p.spread_p},
        "alias_strategy": p.alias_strategy,
        "audio_chunk_hash": audio_hash,
        "prev_glyph_hash": prev_hash,
        "param_commit": param_commit
    }

    # Hash & optional sign
    desc_bytes = canonical_json_bytes(descriptor)
    descriptor_hash = hash_bytes(desc_bytes)

    sigblk = _signature_block(priv_key_bytes, desc_bytes)
    if sigblk:
        descriptor["signature"] = sigblk

    return descriptor, descriptor_hash, audio_hash

def merkle_root(leaves: List[str]) -> str:
    if not leaves:
        return ""
    nodes = [bytes.fromhex(x) for x in leaves]
    while len(nodes) > 1:
        nxt = []
        for i in range(0, len(nodes), 2):
            a = nodes[i]; b = nodes[i+1] if i+1 < len(nodes) else nodes[i]
            nxt.append(blake2b(a + b, digest_size=32).digest())
        nodes = nxt
    return nodes[0].hex()

def build_manifest(descriptors: List[Dict[str, Any]],
                   descriptor_hashes: List[str],
                   audio_hashes: List[str],
                   param_commit: str,
                   *,
                   priv_key_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    first_h = descriptor_hashes[0] if descriptor_hashes else ""
    last_h = descriptor_hashes[-1] if descriptor_hashes else ""
    leaves = []
    for ah, dh in zip(audio_hashes, descriptor_hashes):
        pair = bytes.fromhex(ah) + bytes.fromhex(dh)
        leaves.append(blake2b(pair, digest_size=32).hexdigest())
    root = merkle_root(leaves)

    manifest = {
        "session_id": "demo",
        "spec_version": "GX-SONIC-12:0.1",
        "param_commit": param_commit,
        "hash_algo": "BLAKE2b-256",
        "glyph_count": len(descriptors),
        "first_descriptor_hash": first_h,
        "last_descriptor_hash": last_h,
        "audio_merkle_root": root
    }
    man_bytes = canonical_json_bytes(manifest)
    sigblk = _signature_block(priv_key_bytes, man_bytes)
    if sigblk:
        manifest["signatures"] = [sigblk]
    return manifest
