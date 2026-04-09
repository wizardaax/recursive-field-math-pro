"""
Tests for the SelfModel sentience seed module.

Covers:
- State persistence across sequential calls
- Uncertainty decay on valid integration
- Constraint validation rejects out-of-bounds state
- CLI self-model subcommand end-to-end
"""

import json
import os
import subprocess
import sys

from recursive_field_math.constants import PHI
from recursive_field_math.self_model import (
    UNCERTAINTY_THRESHOLD,
    SelfModel,
    _hash_input,
    _lucas_delta,
)


# ---------------------------------------------------------------------------
# Helper: run the CLI and return (stdout, stderr, returncode)
# ---------------------------------------------------------------------------
def _run(*args: str) -> tuple[str, str, int]:
    result = subprocess.run(
        [sys.executable, "-m", "recursive_field_math.cli", *args],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__)),
    )
    return result.stdout, result.stderr, result.returncode


# ---------------------------------------------------------------------------
# SelfModel unit tests
# ---------------------------------------------------------------------------


class TestSelfModelInit:
    def test_initial_state(self):
        sm = SelfModel()
        s = sm.state()
        assert s["phase"] == 0
        assert s["uncertainty"] == 1.0
        assert s["last_input_hash"] == ""
        assert 0.0 <= s["coherence_score"] <= 1.0

    def test_custom_spec(self):
        spec = {
            "layers": {
                "a": {"depends_on": []},
                "b": {"depends_on": ["a"]},
            }
        }
        sm = SelfModel(spec=spec)
        s = sm.state()
        assert s["phase"] == 0
        assert s["coherence_score"] > 0


class TestObserve:
    def test_observe_increments_phase(self):
        sm = SelfModel()
        sm.observe("test input")
        assert sm.state()["phase"] == 1
        sm.observe("another input")
        assert sm.state()["phase"] == 2  # noqa: PLR2004

    def test_observe_returns_delta_in_range(self):
        sm = SelfModel()
        delta = sm.observe("pattern A")
        assert 0.0 <= delta <= 1.0

    def test_observe_updates_hash(self):
        sm = SelfModel()
        sm.observe("hello world")
        s = sm.state()
        assert s["last_input_hash"] == _hash_input("hello world")

    def test_observe_deterministic(self):
        sm1 = SelfModel()
        sm2 = SelfModel()
        d1 = sm1.observe("same input")
        d2 = sm2.observe("same input")
        assert d1 == d2
        assert sm1.state() == sm2.state()


class TestAsk:
    def test_ask_returns_query_at_high_uncertainty(self):
        sm = SelfModel()
        # Initial uncertainty is 1.0 > 0.3, so ask() should return a query
        q = sm.ask()
        assert q is not None
        assert "query" in q
        assert q["current_uncertainty"] > UNCERTAINTY_THRESHOLD

    def test_ask_returns_none_at_low_uncertainty(self):
        sm = SelfModel()
        # Integrate enough times to drive uncertainty below 0.3
        # Each integration multiplies by 1/φ ≈ 0.618
        # 1.0 * 0.618^3 ≈ 0.236 < 0.3
        for _ in range(3):
            sm.integrate("{}")
        q = sm.ask()
        assert q is None


class TestIntegrate:
    def test_integrate_reduces_uncertainty(self):
        sm = SelfModel()
        u_before = sm.state()["uncertainty"]
        result = sm.integrate("{}")
        assert result["ok"] is True
        u_after = sm.state()["uncertainty"]
        assert u_after < u_before

    def test_uncertainty_decay_factor(self):
        sm = SelfModel()
        u0 = sm.state()["uncertainty"]
        sm.integrate("{}")
        u1 = sm.state()["uncertainty"]
        # Uncertainty should decay by factor 1/φ
        expected = round(u0 * (1.0 / PHI), 6)
        assert u1 == expected

    def test_integrate_rejects_bad_spec(self):
        sm = SelfModel()
        # A spec with only one layer should fail containment validation
        bad_data = json.dumps({"layers": {"only_one": {"depends_on": []}}})
        result = sm.integrate(bad_data)
        assert result["ok"] is False
        assert "reason" in result

    def test_integrate_rejects_no_layers_key(self):
        sm = SelfModel()
        bad_data = json.dumps({"layers": {}})
        result = sm.integrate(bad_data)
        assert result["ok"] is False

    def test_integrate_accepts_non_json(self):
        sm = SelfModel()
        # Plain string should fall back to default spec validation
        result = sm.integrate("just a plain string")
        assert result["ok"] is True

    def test_integrate_persists_state(self):
        sm = SelfModel()
        sm.integrate("{}")
        s1 = sm.state()
        sm.integrate("{}")
        s2 = sm.state()
        # Phase doesn't change on integrate, but uncertainty keeps decaying
        assert s2["uncertainty"] < s1["uncertainty"]


class TestStatePersistence:
    def test_state_persists_across_calls(self):
        sm = SelfModel()
        sm.observe("input_1")
        s1 = sm.state()
        sm.observe("input_2")
        s2 = sm.state()
        # Phase should have incremented
        assert s2["phase"] == s1["phase"] + 1
        # Hash should have changed
        assert s2["last_input_hash"] != s1["last_input_hash"]

    def test_mixed_operations_persist(self):
        sm = SelfModel()
        sm.observe("x")
        sm.integrate("{}")
        q = sm.ask()
        s = sm.state()
        assert s["phase"] == 1
        # After one integration, uncertainty should have decayed
        assert s["uncertainty"] < 1.0
        # Uncertainty is 1.0/φ ≈ 0.618 > 0.3, so ask still returns query
        assert q is not None


class TestConstraintValidation:
    def test_rejects_single_layer(self):
        sm = SelfModel()
        data = json.dumps({"layers": {"solo": {"depends_on": []}}})
        result = sm.integrate(data)
        assert result["ok"] is False

    def test_accepts_valid_multi_layer(self):
        sm = SelfModel()
        data = json.dumps(
            {
                "layers": {
                    "core": {"depends_on": []},
                    "api": {"depends_on": ["core"]},
                }
            }
        )
        result = sm.integrate(data)
        assert result["ok"] is True


class TestHelpers:
    def test_hash_input_deterministic(self):
        assert _hash_input("foo") == _hash_input("foo")
        assert _hash_input("foo") != _hash_input("bar")

    def test_lucas_delta_in_range(self):
        for phase in range(20):
            d = _lucas_delta(phase)
            assert 0.0 <= d <= 1.0


# ---------------------------------------------------------------------------
# CLI end-to-end tests
# ---------------------------------------------------------------------------


class TestSelfModelCLI:
    def test_observe(self):
        stdout, _, rc = _run("self-model", "--observe", "test pattern")
        assert rc == 0
        data = json.loads(stdout)
        assert "delta" in data
        assert "state" in data
        assert data["state"]["phase"] == 1

    def test_ask(self):
        stdout, _, rc = _run("self-model", "--ask")
        assert rc == 0
        data = json.loads(stdout)
        # Fresh model has uncertainty=1.0 > 0.3, so query is returned
        assert "query" in data

    def test_integrate(self):
        stdout, _, rc = _run("self-model", "--integrate", "{}")
        assert rc == 0
        data = json.loads(stdout)
        assert data["ok"] is True
        assert "state" in data

    def test_state(self):
        stdout, _, rc = _run("self-model", "--state")
        assert rc == 0
        data = json.loads(stdout)
        assert "phase" in data
        assert "uncertainty" in data

    def test_integrate_bad_spec(self):
        bad = json.dumps({"layers": {"one": {"depends_on": []}}})
        stdout, _, rc = _run("self-model", "--integrate", bad)
        assert rc == 0
        data = json.loads(stdout)
        assert data["ok"] is False

    def test_no_flag_exits_nonzero(self):
        _, _, rc = _run("self-model")
        assert rc != 0
