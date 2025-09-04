from regen88_codex.flame_correct import phi_correct_drift
from regen88_codex.reseed_pure import clean_reseed
from regen88_codex.harmonic_balance import harmonic_balance
from regen88_codex.shard_isolate import shard_isolate

def test_phi_correction_range():
    phases = [1.0, 3.14, 0.5]
    result = phi_correct_drift(phases)
    assert all(0 <= r < 2 * 3.14159 for r in result)

def test_zpe_seed_is_valid():
    corrupt = b'\x00' * 32
    clean = clean_reseed(corrupt)
    assert len(clean) == 32 and clean != corrupt

def test_harmonic_balancing_returns_bytes():
    corrupted = [b'\x00\x00', b'\xFF\xFF']
    result = harmonic_balance(corrupted)
    assert all(isinstance(r, bytes) for r in result)

def test_shard_removes_corrupt():
    trace = [{'phase': 1.0}, {'phase': 2.0, 'corrupt': True}]
    clean = shard_isolate(trace)
    assert all('corrupt' not in step for step in clean)
