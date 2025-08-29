import argparse, json, os, sys
from pathlib import Path
from typing import Optional, List
from .synth import SynthesisParams, synth_glyph
from .protocol import param_commit_from_offer
from .archive import build_descriptor, build_manifest, write_wav
from .crypto import load_priv  # If your crypto.py lacks this, replace with Path(...).read_bytes()

def parse_args():
    ap = argparse.ArgumentParser(
        prog="gxsonic.cli",
        description="Generate GX-SONIC-12 glyph audio, descriptors, and manifest."
    )
    ap.add_argument("--n-start", type=int, required=True)
    ap.add_argument("--n-end", type=int, required=True)
    ap.add_argument("--sr", type=int, default=48000, help="Sample rate")
    ap.add_argument("--planes", type=int, default=6)
    ap.add_argument("--alpha-inv", type=float, default=137.036)
    ap.add_argument("--phi", type=float, default=1.6180339887498948)
    ap.add_argument("--spread-p", type=float, default=3.0)
    ap.add_argument("--f-min", type=float, default=40.0)
    ap.add_argument("--f-max", type=float, default=1600.0)
    ap.add_argument("--frame-ms", type=float, default=120.0)
    ap.add_argument("--alias", type=str, default="saturate",
                    choices=["saturate", "clip", "resample"])
    ap.add_argument("--out", type=Path, required=True)

    # Signing
    ap.add_argument("--sign", action="store_true", help="Sign descriptors & manifest (ed25519)")
    ap.add_argument("--priv-key", type=Path, help="ed25519 private key file (required with --sign)")
    return ap.parse_args()

def main():
    args = parse_args()
    if args.sign and not args.priv_key:
        print("ERROR: --priv-key required when --sign", file=sys.stderr)
        sys.exit(2)

    priv_bytes = None
    if args.sign:
        priv_bytes = bytes(load_priv(str(args.priv_key)))

    outdir = args.out
    desc_dir = outdir / "descriptors"
    audio_dir = outdir / "audio"
    outdir.mkdir(parents=True, exist_ok=True)
    desc_dir.mkdir(exist_ok=True)
    audio_dir.mkdir(exist_ok=True)

    p = SynthesisParams(
        alpha_inv=args.alpha_inv,
        phi=args.phi,
        planes=args.planes,
        spread_p=args.spread_p,
        f_min=args.f_min,
        f_max=args.f_max,
        n_min=args.n_start,
        n_max=args.n_end,
        sample_rate=args.sr,
        frame_duration=args.frame_ms / 1000.0,
        window="hann",
        alias_strategy=args.alias
    )

    # Canonical OFFER → param_commit (binds the whole run)
    offer = {
        "type": "OFFER",
        "session_id": "demo",
        "spec_version": "GX-SONIC-12:0.1",
        "constants": {"alpha_inv": p.alpha_inv, "phi": p.phi},
        "planes": p.planes,
        "sequence": {"n_start": args.n_start, "n_end": args.n_end, "mode": "discrete"},
        "audio": {"sample_rate": p.sample_rate, "frame_duration_ms": args.frame_ms, "format": "PCM_FLOAT32"},
        "scaling": {"f_min": p.f_min, "f_max": p.f_max, "spread_p": p.spread_p},
        "aliasing": {"strategy": p.alias_strategy},
        "hashing": {"algo": "BLAKE2b-256", "merkle": True},
        "signature_scheme": "ed25519"
    }
    param_commit = param_commit_from_offer(offer)

    # Hash-chain start (64 hex zeros)
    prev_hash = "0" * 64

    descriptors = []
    descriptor_hashes = []
    audio_hashes = []

    for n in range(args.n_start, args.n_end + 1):
        # synth_glyph returns: samples, geometry, base_freq
        samples, geom, base = synth_glyph(n, p)

        # Persist audio
        wav_path = audio_dir / f"glyph_{n:06d}.wav"
        write_wav(str(wav_path), samples, p.sample_rate)

        # Build & (optionally) sign descriptor
        descriptor, dh, ah = build_descriptor(
            n=n,
            g=geom,
            base_freq=base,
            samples=samples,
            prev_hash=prev_hash,
            param_commit=param_commit,
            p=p,
            priv_key_bytes=priv_bytes
        )
        prev_hash = dh  # advance chain

        with open(desc_dir / f"glyph_{n:06d}.json", "w", encoding="utf-8") as f:
            json.dump(descriptor, f, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

        descriptors.append(descriptor)
        descriptor_hashes.append(dh)
        audio_hashes.append(ah)

        print(f"[n={{n}}] audio_hash={{ah[:12]}}… descriptor_hash={{dh[:12]}}… base={{base:.3f}} Hz")

    manifest = build_manifest(
        descriptors=descriptors,
        descriptor_hashes=descriptor_hashes,
        audio_hashes=audio_hashes,
        param_commit=param_commit,
        priv_key_bytes=priv_bytes
    )
    with open(outdir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

    print(f"Done. Glyphs: {{len(descriptors)}}")
    if args.sign:
        print("Signed manifest & descriptors with ed25519.")

if __name__ == "__main__":
    main()
