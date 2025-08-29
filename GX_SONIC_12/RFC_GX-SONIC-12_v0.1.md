# GX-SONIC-12 Protocol Specification (v0.1 Draft)

Spec ID: GX-SONIC-12  
Version: 0.1 (Draft)  
Status: Internal Draft / Experimental  
Author: wizardaax  
License: Apache-2.0  

## 1. Overview

GX-SONIC-12 defines a deterministic, cryptographically-verifiable stream (“glyphstream”) of audio glyphs derived from:

- Inverse fine-structure constant α⁻¹ ≈ 137.036 (so α ≈ 1/137.036)
- Golden ratio φ ≈ 1.6180339887…
- Six orthogonal 2D planes (12 dimensions total)

Each glyph `n`:
1. Geometry → 12D vector
2. Synthesis → Audio frame (windowed multi-plane carriers)
3. Integrity → Canonical JSON descriptor + hashes (BLAKE2b-256 v0.1; upgrade path to BLAKE3)
4. Chain → `prev_glyph_hash` linking descriptors
5. Aggregate → Optional Merkle root over combined (audio ∥ descriptor) hashes stored in a session manifest
6. (Implemented in reference code) **ed25519 signing** of descriptors & manifest (signatures excluded from chain/hash bases)

## 2. Geometry

For integer n ≥ 1:

- Radius: r(n) = φ * √n  
- Angles (plane k = 0..5):

```
θ_k(n) = 2π * n * α⁻¹ * φ^k
```

That is: multiply by α⁻¹ (≈137.036); equivalently `n / α`.  
The exponent is φ^k (power), **not** (φ * k).

- Plane components:
  - x_k = r(n) cos θ_k
  - y_k = r(n) sin θ_k
- Vector v(n) = (x_0, y_0, x_1, y_1, ..., x_5, y_5)
- Norm: ‖v(n)‖ = r(n) * √6 (since each plane radius identical in v0.1)

### 2.1 Optional Plane Radius Variant (Future)
To embed timbral stratification:
```
r_k(n) = φ * √n * φ^{k / q}
```
for configurable q (default: no per-plane radius scaling in v0.1). MUST record variant metadata if enabled.

## 3. Frequency Mapping

Base frequency f_base(n) from norm (∝ √n):

```
norm(n) = φ * √n * √6
Let sqrt_n = √n
Linear strategy (v0.1):
  f_base(n) = f_min + (f_max - f_min) * (sqrt_n - sqrt_n_min)/(sqrt_n_max - sqrt_n_min)
```

Session parameters:
- f_min, f_max
- n_min, n_max (planned glyph range for mapping)

Per-plane carrier frequencies:

```
f_k = f_base * φ^{k / p}
```

`p ≥ 1` is the *spread compression factor* (default p = 3) to curb aliasing.

Aliasing strategies (negotiated):
- `saturate`: f' = (Nyquist * f)/(Nyquist + f)
- `clip`: discard plane if f > Nyquist
- `resample`: (future) oversample then low-pass.

## 4. Amplitude & Waveform

Per-plane normalized amplitudes:
```
A_sin_k = x_k / ‖v(n)‖
A_cos_k = y_k / ‖v(n)‖
Σ_k (A_sin_k² + A_cos_k²) = 1
```

Time-domain frame (duration T):
```
frame(t) = Σ_k [ A_sin_k sin(2π f_k t) + A_cos_k cos(2π f_k t) ], t ∈ [0, T)
```

Window: Hann (default; record in descriptor)  
Normalization: Peak-based (v0.1) — policy may evolve.

## 5. Descriptor

Canonical JSON (lexicographically sorted keys; compact separators `,` and `:`).  
Core fields:

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Unique session |
| spec_version | string | "GX-SONIC-12:0.1" |
| n | integer | Glyph index |
| alpha_inv | number | α⁻¹ used |
| phi | number | φ used |
| planes | integer | Usually 6 |
| radius | number | r(n) |
| angles | number[] | [θ_0,…,θ_5] modulo 2π |
| revolution_counts | integer[] (optional) | Full revolution counts (θ_full / 2π) |
| vector_components | number[] | [x_0,y_0,…,x_5,y_5] |
| norm | number | ‖v(n)‖ |
| fundamental_freq | number | f_base(n) |
| plane_freqs | number[] | [f_0,…,f_5] |
| amp_pairs | number[][] | [[A_sin_0,A_cos_0],…] |
| window | string | e.g. "hann" |
| scaling | object | { f_min, f_max, spread_p } |
| alias_strategy | string | "saturate"/"clip"/"resample" |
| audio_chunk_hash | hex | Hash(audio bytes) |
| prev_glyph_hash | hex | Hash(previous descriptor) |
| param_commit | hex | Hash of canonical final OFFER |
| timestamp | number (optional) | Seconds since epoch |
| signature | object (optional) | ed25519 block |

### 5.1 Signature Extension (Implemented v0.1 Reference)
If signing is enabled, a `signature` object is appended AFTER computing the descriptor hash (hash excludes the signature field):
```
"signature": {
  "scheme": "ed25519",
  "pub": "<base64 public key>",
  "sig": "<base64 signature over canonical unsigned descriptor>"
}
```
Descriptor hash and chain linkage are computed over the unsigned descriptor body. Verification:
1. Remove `signature`.
2. Canonicalize & hash (for chain comparison).
3. Verify ed25519 signature with `pub`.

### 5.2 Sample Glyph Descriptor (Illustrative)
```
{
  "alpha_inv":137.036,
  "alias_strategy":"saturate",
  "amp_pairs":[[0.18294,-0.30112],[-0.51277,0.07355],[0.05120,0.21649],[-0.09341,-0.03466],[0.04255,0.18402],[-0.00931,-0.05077]],
  "angles":[5.4120192749,3.1076621222,2.1680840017,0.9486173205,4.3993522702,1.1700306679],
  "audio_chunk_hash":"9c7b7d2d3ce2f5b4b0d4a5f3d5ad2b6e0b3e8c9bfa3de587b4f6c0e3ad9a4cc1",
  "fundamental_freq":57.8321549712,
  "n":1,
  "norm":3.9999998712,
  "param_commit":"a5d216b6e486cddfa4b4a048e1a035630d7f5b40318e1bf5f7f7a2bb4c2b9dc1",
  "phi":1.6180339887498948,
  "plane_freqs":[57.83215,75.81750,99.38378,130.22304,170.56987,223.35755],
  "planes":6,
  "prev_glyph_hash":"0000000000000000000000000000000000000000000000000000000000000000",
  "radius":1.6180339887498948,
  "revolution_counts":[118,959,7820,63762,519656,4233959],
  "scaling":{"f_min":40.0,"f_max":1600.0,"spread_p":3.0},
  "session_id":"demo",
  "spec_version":"GX-SONIC-12:0.1",
  "vector_components":[1.0891,-1.2132,-0.5128,1.4208,0.0832,0.3501,-0.1409,-0.0563,0.0689,0.2974,-0.0151,-0.0820],
  "window":"hann"
}
```
(Values illustrative.)

## 6. Cryptographic Primitives (v0.1)
- Hash: BLAKE2b-256 (digest size 32 bytes)
- Signature (implemented): ed25519 (descriptor & manifest, excluded from hash inputs)
- Merkle Tree: Binary; leaf = hash( audio_chunk_hash ∥ descriptor_hash )

## 7. Session Handshake
States:
```
INIT → OFFER ↔ COUNTER → ACCEPT → START → STREAM_CHUNK* → CLOSE
```
### 7.1 Message Types
All messages include:
```
{
  "type": "...",
  "session_id": "...",
  "spec_version": "GX-SONIC-12:0.1"
}
```
(OFFER, COUNTER, ACCEPT, START, STREAM_CHUNK, STATE, ACK, CLOSE — unchanged from previous polished draft; COUNTER uses full echo for deterministic `param_commit`.)

## 8. Parameter Commitment
```
param_commit = HASH( canonical_final_OFFER_JSON )
```
Embedded in every descriptor.

## 9. Manifest
Unsigned core hashed → `manifest_hash`. Signatures appended (do not affect hash):
```
{
  ... core fields ...,  
  "manifest_hash":"<hex>",
  "signatures":[
    {"scheme":"ed25519","pub":"<base64>","sig":"<base64>"}
  ]
}
```
Multiple signatures allowed.

## 10. Continuous Mode (Future)
Fractional n(t) with θ_k = 2π α⁻¹ φ^k n, derivative dθ_k/dt = 2π α⁻¹ φ^k dn/dt. Deferred to v0.2.

## 11. JSON-LD & Semantics
Context maps fields (see jsonld_context.py).

## 12. Security Considerations
- Integrity: Hash chain + Merkle root
- Authenticity: ed25519 signatures (optional per descriptor & manifest)
- Replay: Unique session_id
- Upgrade: Dual-hash transition planned

## 13. Upgrade Paths
- Add BLAKE3 (dual-hash)
- Modulation layers (mod_layers object)
- Continuous mode spec block

## 14. Registry (Future)
Window names, alias strategies, modulation layer IDs.

## 15. Reference Implementation
Repo: https://github.com/wizardaax/recursive-field-math-pro/tree/main/GX_SONIC_12/python/gxsonic  
Implements ed25519 signing (crypto.py, archive.py, cli.py --sign).

## 16. Open Issues
1. Continuous fractional-n spec
2. Dual-hash migration details
3. Deterministic dither seed
4. Psychoacoustic indexing standardization
5. Multi-party interleave semantics
6. Key distribution & revocation doc

## 17. License & Attribution
Apache-2.0  
Author: wizardaax

---
END OF SPEC (v0.1 Draft, with signing)