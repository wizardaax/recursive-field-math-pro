from __future__ import annotations

"""
Hash helpers for GX-SONIC-12.

Always provides:
  - blake2b_256 (canonical)
Optionally provides (if 'blake3' module is installed):
  - blake3_256

dual_hash(data, want_blake3=True) returns a dict:
  {
    "blake2b": "<hex>",
    "blake3": "<hex>"   # only if want_blake3 and blake3 available
  }
"""

from hashlib import blake2b
from typing import Dict

try:
    import blake3  # type: ignore
    _HAS_BLAKE3 = True
except Exception:
    blake3 = None  # type: ignore
    _HAS_BLAKE3 = False

def blake2b_256(data: bytes) -> str:
    return blake2b(data, digest_size=32).hexdigest()

def blake3_256(data: bytes) -> str:
    if not _HAS_BLAKE3:
        raise RuntimeError("blake3 library not available")
    return blake3.blake3(data).hexdigest()  # type: ignore

def dual_hash(data: bytes, want_blake3: bool = True) -> Dict[str, str]:
    out = {"blake2b": blake2b_256(data)}
    if want_blake3 and _HAS_BLAKE3:
        out["blake3"] = blake3_256(data)
    return out

def has_blake3() -> bool:
    return _HAS_BLAKE3
