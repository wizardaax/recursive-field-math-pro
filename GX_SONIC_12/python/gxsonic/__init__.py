from .synth import geometry, synth_glyph, SynthesisParams
from .archive import build_descriptor, build_manifest, write_wav, merkle_root
from .protocol import canonical_json_bytes, hash_bytes, param_commit_from_offer
from .crypto import gen_keypair, sign_bytes, verify_bytes  # assuming your crypto.py exposes these

__all__ = [
    "geometry",
    "synth_glyph",
    "SynthesisParams",
    "build_descriptor",
    "build_manifest",
    "write_wav",
    "merkle_root",
    "canonical_json_bytes",
    "hash_bytes",
    "param_commit_from_offer",
    "gen_keypair",
    "sign_bytes",
    "verify_bytes",
]