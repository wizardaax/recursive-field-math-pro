import os, time, hashlib, random
from .utils import PHI

def clean_reseed(corrupted: bytes) -> bytes:
    t = time.time_ns()
    phi_noise = (t % 1000000) * (PHI ** random.random())
    merged = str(phi_noise).encode() + os.urandom(8)
    return hashlib.sha256(merged).digest()
