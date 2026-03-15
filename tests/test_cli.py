"""
Tests for the rfm CLI (src/recursive_field_math/cli.py).

Each sub-command is exercised via subprocess so that the argparse + main()
code path is fully covered.  The subprocess approach mirrors how users run
the CLI and avoids patching sys.argv.
"""

import json
import os
import subprocess
import sys
import tempfile

import pytest


# Helper: run the CLI and return (stdout, stderr, returncode)
def _run(*args: str) -> tuple[str, str, int]:
    result = subprocess.run(
        [sys.executable, "-m", "recursive_field_math.cli", *args],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__)),
    )
    return result.stdout, result.stderr, result.returncode


# ---------------------------------------------------------------------------
# lucas
# ---------------------------------------------------------------------------
class TestLucasCommand:
    def test_basic_range(self):
        stdout, _, rc = _run("lucas", "0", "5")
        assert rc == 0
        data = json.loads(stdout)
        assert data == {"0": 2, "1": 1, "2": 3, "3": 4, "4": 7, "5": 11}

    def test_single_value(self):
        stdout, _, rc = _run("lucas", "4", "4")
        assert rc == 0
        data = json.loads(stdout)
        assert data == {"4": 7}


# ---------------------------------------------------------------------------
# fib
# ---------------------------------------------------------------------------
class TestFibCommand:
    def test_basic_range(self):
        stdout, _, rc = _run("fib", "0", "6")
        assert rc == 0
        data = json.loads(stdout)
        assert data == {"0": 0, "1": 1, "2": 1, "3": 2, "4": 3, "5": 5, "6": 8}

    def test_single_value(self):
        stdout, _, rc = _run("fib", "10", "10")
        assert rc == 0
        data = json.loads(stdout)
        assert data == {"10": 55}  # noqa: PLR2004


# ---------------------------------------------------------------------------
# field
# ---------------------------------------------------------------------------
class TestFieldCommand:
    def test_basic_range(self):
        stdout, _, rc = _run("field", "1", "3")
        assert rc == 0
        data = json.loads(stdout)
        assert set(data.keys()) == {"1", "2", "3"}
        r1, th1 = data["1"]
        assert abs(r1 - 3.0) < 1e-9  # noqa: PLR2004

    def test_single_value(self):
        stdout, _, rc = _run("field", "4", "4")
        assert rc == 0
        data = json.loads(stdout)
        r4, _ = data["4"]
        assert abs(r4 - 6.0) < 1e-9  # noqa: PLR2004


# ---------------------------------------------------------------------------
# ratio
# ---------------------------------------------------------------------------
class TestRatioCommand:
    def test_ratio_n5(self):
        stdout, _, rc = _run("ratio", "5")
        assert rc == 0
        data = json.loads(stdout)
        assert data["n"] == 5  # noqa: PLR2004
        assert data["ratio"] > 1
        lo, hi = data["abs_error_bounds"]
        assert lo > 0 and hi > lo


# ---------------------------------------------------------------------------
# egypt
# ---------------------------------------------------------------------------
class TestEgyptCommand:
    def test_egypt(self):
        stdout, _, rc = _run("egypt")
        assert rc == 0
        data = json.loads(stdout)
        # 1/4 + 1/7 + 1/11 = 149/308
        assert data["sum_1_4_7_11"]["num"] == 149  # noqa: PLR2004
        assert data["sum_1_4_7_11"]["den"] == 308  # noqa: PLR2004


# ---------------------------------------------------------------------------
# sig
# ---------------------------------------------------------------------------
class TestSigCommand:
    def test_sig(self):
        stdout, _, rc = _run("sig")
        assert rc == 0
        data = json.loads(stdout)
        assert data["L3"] == 4  # noqa: PLR2004
        assert data["L4"] == 7  # noqa: PLR2004
        assert data["L5"] == 11  # noqa: PLR2004
        assert data["product"] == 308  # noqa: PLR2004


# ---------------------------------------------------------------------------
# cfrac
# ---------------------------------------------------------------------------
class TestCfracCommand:
    def test_cfrac_n3(self):
        stdout, _, rc = _run("cfrac", "3")
        assert rc == 0
        data = json.loads(stdout)
        assert data["n"] == 3  # noqa: PLR2004
        assert data["ratio"] == [7, 4]  # L(4)/L(3)
        assert data["cfrac_meta"] == {"head": 1, "ones": 1, "tail": 3}

    def test_cfrac_n1(self):
        stdout, _, rc = _run("cfrac", "1")
        assert rc == 0
        data = json.loads(stdout)
        assert data["ratio"] == [3, 1]  # L(2)/L(1) = 3/1
        # For n=1: ones = max(0, 1-2) = 0
        assert data["cfrac_meta"]["ones"] == 0


# ---------------------------------------------------------------------------
# eval (JSON output)
# ---------------------------------------------------------------------------
class TestEvalCommand:
    def _make_results_file(self, results: list, suffix: str = ".json") -> str:
        """Write results list to a temp JSON file, return path."""
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "w") as f:
            json.dump(results, f)
        return path

    def test_eval_pass(self):
        results = [
            {
                "ok": True,
                "tag": "game_a",
                "moves": 25,
                "variance_reduction_pct": 85.0,
                "mae_improvement_pct": 5.0,
                "theta_after_hist": ([0.6, 0.65, 0.67, 0.68, 0.7], [1, 2, 10, 2]),
            }
        ]
        path = self._make_results_file(results)
        try:
            stdout, _, rc = _run("eval", path)
            assert rc == 0
            data = json.loads(stdout)
            assert data["summary"]["total_games"] == 1
            assert data["summary"]["passes"] == 1
            assert data["evaluations"][0]["verdict"] == "PASS"
        finally:
            os.unlink(path)

    def test_eval_skip(self):
        results = [{"ok": False, "reason": "too short", "tag": "game_b", "moves": 3}]
        path = self._make_results_file(results)
        try:
            stdout, _, rc = _run("eval", path)
            assert rc == 0
            data = json.loads(stdout)
            assert data["summary"]["skips"] == 1
            assert data["evaluations"][0]["verdict"] == "SKIP"
        finally:
            os.unlink(path)

    def test_eval_missing_file(self):
        stdout, _, rc = _run("eval", "/nonexistent/path/results.json")
        assert rc == 0  # CLI prints error JSON, doesn't exit with error code
        data = json.loads(stdout)
        assert "error" in data

    def test_eval_markdown_flag(self):
        results = [
            {
                "ok": True,
                "tag": "game_md",
                "moves": 20,
                "variance_reduction_pct": 30.0,
                "mae_improvement_pct": 3.0,
                "theta_after_hist": ([0.6, 0.65, 0.67, 0.68, 0.7], [1, 2, 10, 2]),
            }
        ]
        path = self._make_results_file(results)
        try:
            stdout, _, rc = _run("eval", path, "--markdown")
            assert rc == 0
            # Markdown output must not be valid JSON
            with pytest.raises((json.JSONDecodeError, ValueError)):
                json.loads(stdout)
            assert "Codex Entropy-Pump Results" in stdout
            assert "game_md" in stdout
        finally:
            os.unlink(path)

    def test_eval_custom_lucas_weights(self):
        results = [
            {
                "ok": True,
                "tag": "game_c",
                "moves": 30,
                "variance_reduction_pct": 50.0,
                "mae_improvement_pct": 4.0,
                "theta_after_hist": ([0.6, 0.65, 0.67, 0.68, 0.7], [1, 2, 10, 2]),
            }
        ]
        path = self._make_results_file(results)
        try:
            stdout, _, rc = _run("eval", path, "--lucas-weights", "4", "7", "11")
            assert rc == 0
            data = json.loads(stdout)
            assert data["lucas_weights"] == [4, 7, 11]
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------
class TestCliErrors:
    def test_no_subcommand_exits_nonzero(self):
        _, _, rc = _run()
        assert rc != 0

    def test_unknown_subcommand_exits_nonzero(self):
        _, _, rc = _run("nonexistent")
        assert rc != 0
