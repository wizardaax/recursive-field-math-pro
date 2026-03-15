"""
Tests for the Cross-Domain Bridge (xdomain_bridge.py).

Uses fixed-seed / deterministic sequences for reproducibility.
"""

import pytest

from recursive_field_math.xdomain_bridge import (
    BRIDGE_PROFILE,
    N_LATENT,
    BridgeError,
    bridge,
    decode,
    encode,
    register_adapter,
)

# ---------------------------------------------------------------------------
# Golden sequences
# ---------------------------------------------------------------------------
FIBONACCI = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
TOKENS = [10, 20, 30, 20, 10, 40, 50, 40, 30, 20]
ACTIONS = [0, 1, 2, 1, 0, 3, 2, 1, 0, 3]


# ---------------------------------------------------------------------------
# encode() tests
# ---------------------------------------------------------------------------


def test_encode_numeric_ok():
    lv = encode(FIBONACCI, domain="numeric")
    assert lv["profile"] == BRIDGE_PROFILE
    assert lv["domain"] == "numeric"
    assert lv["n_input"] == len(FIBONACCI)
    assert len(lv["values"]) == N_LATENT
    assert lv["norm"] > 0


def test_encode_tokens_ok():
    lv = encode(TOKENS, domain="tokens")
    assert lv["domain"] == "tokens"
    assert lv["n_input"] == len(TOKENS)


def test_encode_actions_ok():
    lv = encode(ACTIONS, domain="actions")
    assert lv["domain"] == "actions"


def test_encode_latent_values_bounded():
    """Normalised latent coefficients should be in [-1, 1]."""
    lv = encode(FIBONACCI, domain="numeric")
    for v in lv["values"]:
        assert -1.0 <= v <= 1.0


def test_encode_too_short_raises():
    with pytest.raises(BridgeError, match="too short"):
        encode([1, 2, 3], domain="numeric")  # len < MIN_INPUT_LENGTH (4)


def test_encode_unknown_domain_raises():
    with pytest.raises(BridgeError, match="Unknown domain"):
        encode(FIBONACCI, domain="not_a_domain")


def test_encode_is_deterministic():
    lv1 = encode(FIBONACCI, domain="numeric")
    lv2 = encode(FIBONACCI, domain="numeric")
    assert lv1["values"] == lv2["values"]
    assert lv1["norm"] == lv2["norm"]


# ---------------------------------------------------------------------------
# decode() tests
# ---------------------------------------------------------------------------


def test_decode_returns_correct_length():
    lv = encode(FIBONACCI, domain="numeric")
    rec = decode(lv)
    assert len(rec) == len(FIBONACCI)


def test_decode_all_floats():
    lv = encode(TOKENS, domain="tokens")
    rec = decode(lv)
    for v in rec:
        assert isinstance(v, float)


def test_decode_missing_key_raises():
    with pytest.raises(BridgeError, match="missing keys"):
        decode({"values": [], "norm": 1.0})  # n_input missing


def test_decode_no_error_check_passes():
    """With check_error_bound=False and no original, should never raise."""
    lv = encode(FIBONACCI, domain="numeric")
    rec = decode(lv, check_error_bound=False)
    assert len(rec) == len(FIBONACCI)


def test_decode_is_deterministic():
    lv = encode(FIBONACCI, domain="numeric")
    r1 = decode(lv)
    r2 = decode(lv)
    assert r1 == r2


# ---------------------------------------------------------------------------
# bridge() tests
# ---------------------------------------------------------------------------


def test_bridge_same_domain_ok():
    result = bridge(FIBONACCI, "numeric", "numeric")
    assert result["src_domain"] == "numeric"
    assert result["dst_domain"] == "numeric"
    assert result["profile"] == BRIDGE_PROFILE
    assert len(result["reconstructed"]) == len(FIBONACCI)
    assert "latent_vector" in result


def test_bridge_cross_domain_ok():
    result = bridge(FIBONACCI, "numeric", "tokens")
    assert result["src_domain"] == "numeric"
    assert result["dst_domain"] == "tokens"


def test_bridge_unknown_src_raises():
    with pytest.raises(BridgeError, match="Unknown src_domain"):
        bridge(FIBONACCI, "nope", "numeric")


def test_bridge_unknown_dst_raises():
    with pytest.raises(BridgeError, match="Unknown dst_domain"):
        bridge(FIBONACCI, "numeric", "nope")


def test_bridge_is_deterministic():
    r1 = bridge(FIBONACCI, "numeric", "numeric")
    r2 = bridge(FIBONACCI, "numeric", "numeric")
    assert r1["reconstructed"] == r2["reconstructed"]


# ---------------------------------------------------------------------------
# register_adapter() tests
# ---------------------------------------------------------------------------


def test_register_custom_adapter():
    """A custom adapter should become available for encoding."""
    register_adapter("custom_test", lambda seq: [float(x) * 2 for x in seq])
    lv = encode([1, 2, 3, 4, 5, 6, 7, 8], domain="custom_test")
    assert lv["domain"] == "custom_test"
    assert lv["n_input"] == 8  # noqa: PLR2004


# ---------------------------------------------------------------------------
# n_latent parameter
# ---------------------------------------------------------------------------


def test_encode_custom_n_latent():
    lv = encode(FIBONACCI, domain="numeric", n_latent=8)
    assert len(lv["values"]) == 8  # noqa: PLR2004


def test_decode_uses_latent_dimensionality():
    lv = encode(FIBONACCI, domain="numeric", n_latent=8)
    rec = decode(lv)
    assert len(rec) == len(FIBONACCI)
