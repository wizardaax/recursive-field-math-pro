"""
Tests for the recursive self-evolution engine.

Covers:
- EvolutionEngine initialisation and state management
- Observation accuracy and gap detection
- Proposal generation, safety, and SCE-88 validation
- Sandbox simulation isolation and coherence tracking
- Apply: provenance logging, rollback plans, human-gate flags
- Thread safety and determinism
- CLI evolve subcommand end-to-end
- Edge cases and error paths

81 deterministic tests, zero flakiness.
"""

import copy
import json
import os
import subprocess
import sys
import threading

from recursive_field_math.evolution.meta_engine import (
    COHERENCE_FLOOR,
    COVERAGE_FLOOR,
    FEDERATION_AGENTS,
    LATENCY_THRESHOLD_MS,
    LOW_RISK_CATEGORIES,
    MEMORY_DECAY_THRESHOLD,
    STRUCTURAL_CATEGORIES,
    EvolutionEngine,
    _build_spec_from_agents,
    _compute_agent_score,
    _deterministic_id,
    _lucas_weight,
)
from recursive_field_math.self_model import SelfModel


# ---------------------------------------------------------------------------
# Helper: run the CLI and return (stdout, stderr, returncode)
# ---------------------------------------------------------------------------
def _run(*args):
    result = subprocess.run(
        [sys.executable, "-m", "recursive_field_math.cli", *args],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__)),
    )
    return result.stdout, result.stderr, result.returncode


# ===========================================================================
# Initialisation
# ===========================================================================


class TestEngineInit:
    def test_default_agents(self):
        engine = EvolutionEngine()
        s = engine.state()
        assert s["agents"] == list(FEDERATION_AGENTS)
        assert len(s["agents"]) == 13  # noqa: PLR2004

    def test_custom_agents(self):
        agents = ["alpha", "beta", "gamma"]
        engine = EvolutionEngine(agents=agents)
        assert engine.state()["agents"] == agents

    def test_initial_phase_zero(self):
        engine = EvolutionEngine()
        assert engine.state()["phase"] == 0

    def test_initial_counts_zero(self):
        engine = EvolutionEngine()
        s = engine.state()
        assert s["observation_count"] == 0
        assert s["proposal_count"] == 0
        assert s["simulation_count"] == 0
        assert s["applied_count"] == 0

    def test_self_model_injected(self):
        sm = SelfModel()
        engine = EvolutionEngine(self_model=sm)
        # The engine should use the same self-model
        assert engine.state()["self_model"] == sm.state()

    def test_self_model_default(self):
        engine = EvolutionEngine()
        sm_state = engine.state()["self_model"]
        assert "phase" in sm_state
        assert "coherence_score" in sm_state


# ===========================================================================
# Observation
# ===========================================================================


class TestObserve:
    def test_observe_returns_ok(self):
        engine = EvolutionEngine()
        report = engine.observe()
        assert report["ok"] is True

    def test_observe_increments_phase(self):
        engine = EvolutionEngine()
        engine.observe()
        assert engine.state()["phase"] == 1
        engine.observe()
        assert engine.state()["phase"] == 2  # noqa: PLR2004

    def test_observe_all_agents_present(self):
        engine = EvolutionEngine()
        report = engine.observe()
        for agent in FEDERATION_AGENTS:
            assert agent in report["agents"]

    def test_observe_health_scores_in_range(self):
        engine = EvolutionEngine()
        report = engine.observe()
        for agent_data in report["agents"].values():
            assert 0.0 <= agent_data["health_score"] <= 1.0

    def test_observe_summary(self):
        engine = EvolutionEngine()
        report = engine.observe()
        s = report["summary"]
        assert s["total_agents"] == 13  # noqa: PLR2004
        assert "gaps_found" in s
        assert "mean_health" in s
        assert "coherence" in s

    def test_observe_custom_metrics(self):
        engine = EvolutionEngine()
        metrics = {
            "observer": {
                "latency_ms": 200.0,
                "error_rate": 0.1,
                "test_coverage": 0.5,
                "constraint_violations": 2,
                "memory_decay": 0.5,
            }
        }
        report = engine.observe(agent_metrics=metrics)
        # Should detect gaps for observer
        gap_agents = [g["agent"] for g in report["gaps"]]
        assert "observer" in gap_agents

    def test_observe_detects_high_latency(self):
        engine = EvolutionEngine()
        metrics = {"observer": {"latency_ms": 250.0}}
        report = engine.observe(agent_metrics=metrics)
        latency_gaps = [g for g in report["gaps"] if g["type"] == "high_latency"]
        assert len(latency_gaps) >= 1
        assert latency_gaps[0]["agent"] == "observer"

    def test_observe_detects_low_coverage(self):
        engine = EvolutionEngine()
        metrics = {"planner": {"test_coverage": 0.3}}
        report = engine.observe(agent_metrics=metrics)
        coverage_gaps = [g for g in report["gaps"] if g["type"] == "low_coverage"]
        assert len(coverage_gaps) >= 1

    def test_observe_detects_constraint_violations(self):
        engine = EvolutionEngine()
        metrics = {"executor": {"constraint_violations": 3}}
        report = engine.observe(agent_metrics=metrics)
        violation_gaps = [g for g in report["gaps"] if g["type"] == "constraint_violation"]
        assert len(violation_gaps) >= 1

    def test_observe_detects_memory_decay(self):
        engine = EvolutionEngine()
        metrics = {"memory": {"memory_decay": 0.8}}
        report = engine.observe(agent_metrics=metrics)
        decay_gaps = [g for g in report["gaps"] if g["type"] == "memory_decay"]
        assert len(decay_gaps) >= 1

    def test_observe_coherence_in_range(self):
        engine = EvolutionEngine()
        report = engine.observe()
        assert 0.0 <= report["coherence"] <= 1.0

    def test_observe_is_deterministic(self):
        e1 = EvolutionEngine()
        e2 = EvolutionEngine()
        r1 = e1.observe()
        r2 = e2.observe()
        assert r1["agents"] == r2["agents"]
        assert r1["gaps"] == r2["gaps"]

    def test_observe_records_in_history(self):
        engine = EvolutionEngine()
        engine.observe()
        assert engine.state()["observation_count"] == 1
        engine.observe()
        assert engine.state()["observation_count"] == 2  # noqa: PLR2004


# ===========================================================================
# Proposal generation
# ===========================================================================


class TestPropose:
    def test_propose_returns_list(self):
        engine = EvolutionEngine()
        proposals = engine.propose()
        assert isinstance(proposals, list)

    def test_propose_with_gaps(self):
        engine = EvolutionEngine()
        metrics = {
            "observer": {"latency_ms": 300.0},
            "planner": {"test_coverage": 0.2},
        }
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        assert len(proposals) >= 2  # noqa: PLR2004

    def test_proposal_has_required_fields(self):
        engine = EvolutionEngine()
        metrics = {"observer": {"latency_ms": 300.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        for p in proposals:
            assert "id" in p
            assert "category" in p
            assert "target" in p
            assert "description" in p
            assert "patch" in p
            assert "risk" in p
            assert "human_gate" in p
            assert "sce88_valid" in p

    def test_proposal_sce88_validation(self):
        engine = EvolutionEngine()
        metrics = {"observer": {"latency_ms": 300.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        # All proposals targeting existing agents should be SCE-88 valid
        for p in proposals:
            if p["target"] in FEDERATION_AGENTS:
                assert p["sce88_valid"] is True

    def test_proposal_ids_deterministic(self):
        e1 = EvolutionEngine()
        e2 = EvolutionEngine()
        m = {"observer": {"latency_ms": 300.0}}
        o1 = e1.observe(agent_metrics=m)
        o2 = e2.observe(agent_metrics=m)
        p1 = e1.propose(observation=o1)
        p2 = e2.propose(observation=o2)
        assert [x["id"] for x in p1] == [x["id"] for x in p2]

    def test_high_latency_proposal_is_config_tweak(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        latency_proposals = [p for p in proposals if p["target"] == "router"]
        assert any(p["category"] == "config_tweak" for p in latency_proposals)

    def test_low_coverage_proposal_is_code_patch(self):
        engine = EvolutionEngine()
        metrics = {"sentinel": {"test_coverage": 0.3}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        coverage_proposals = [p for p in proposals if p["target"] == "sentinel"]
        assert any(p["category"] == "code_patch" for p in coverage_proposals)

    def test_memory_decay_proposal_is_math_opt(self):
        engine = EvolutionEngine()
        metrics = {"memory": {"memory_decay": 0.8}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        decay_proposals = [p for p in proposals if p["target"] == "memory"]
        assert any(p["category"] == "math_optimisation" for p in decay_proposals)

    def test_structural_proposals_have_human_gate(self):
        engine = EvolutionEngine()
        metrics = {"validator": {"test_coverage": 0.2}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        for p in proposals:
            if p["category"] in STRUCTURAL_CATEGORIES:
                assert p["human_gate"] is True

    def test_low_risk_proposals_no_human_gate(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        for p in proposals:
            if p["category"] in LOW_RISK_CATEGORIES:
                assert p["human_gate"] is False

    def test_propose_without_observation(self):
        """propose() without explicit observation should auto-observe."""
        engine = EvolutionEngine()
        proposals = engine.propose()
        assert isinstance(proposals, list)
        assert engine.state()["observation_count"] >= 1

    def test_propose_returns_deep_copy(self):
        engine = EvolutionEngine()
        metrics = {"observer": {"latency_ms": 300.0}}
        obs = engine.observe(agent_metrics=metrics)
        p1 = engine.propose(observation=obs)
        engine.propose(observation=obs)
        # Modifying p1 should not affect p2
        if p1:
            p1[0]["id"] = "mutated"
            p3 = engine.propose(observation=obs)
            assert p3[0]["id"] != "mutated"


# ===========================================================================
# Simulation
# ===========================================================================


class TestSimulate:
    def test_simulate_empty_proposals(self):
        engine = EvolutionEngine()
        result = engine.simulate(proposals=[])
        assert result["ok"] is True
        assert result["pass_count"] == 0
        assert result["fail_count"] == 0

    def test_simulate_returns_coherence_delta(self):
        engine = EvolutionEngine()
        metrics = {"observer": {"latency_ms": 300.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        result = engine.simulate(proposals)
        assert "coherence_before" in result
        assert "coherence_after" in result
        assert "coherence_delta" in result

    def test_simulate_valid_proposals_pass(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        result = engine.simulate(proposals)
        assert result["pass_count"] >= 1

    def test_simulate_invalid_proposals_fail(self):
        engine = EvolutionEngine()
        # Manually create a proposal with invalid SCE-88
        bad_proposal = {
            "id": "bad-001",
            "category": "code_patch",
            "target": "nonexistent_agent",
            "description": "Invalid proposal",
            "patch": {},
            "risk": "high",
            "human_gate": True,
            "sce88_valid": False,
        }
        result = engine.simulate(proposals=[bad_proposal])
        assert result["fail_count"] == 1

    def test_simulate_records_in_history(self):
        engine = EvolutionEngine()
        engine.simulate(proposals=[])
        assert engine.state()["simulation_count"] == 1

    def test_simulate_sandbox_isolation(self):
        """Simulation should not alter engine spec."""
        engine = EvolutionEngine()
        spec_before = copy.deepcopy(engine._spec)
        metrics = {"observer": {"latency_ms": 300.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        assert engine._spec == spec_before

    def test_simulate_results_per_proposal(self):
        engine = EvolutionEngine()
        metrics = {
            "observer": {"latency_ms": 300.0},
            "planner": {"memory_decay": 0.8},
        }
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        result = engine.simulate(proposals)
        assert len(result["results"]) == len(proposals)

    def test_simulate_each_result_has_fields(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        result = engine.simulate(proposals)
        for r in result["results"]:
            assert "proposal_id" in r
            assert "passed" in r
            assert "coherence_before" in r
            assert "coherence_after" in r
            assert "coherence_delta" in r
            assert "req01_pass" in r
            assert "req02_pass" in r

    def test_simulate_without_proposals_uses_stored(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        engine.propose(observation=obs)
        result = engine.simulate()
        assert isinstance(result, dict)
        assert result["ok"] is True

    def test_simulate_coherence_within_bounds(self):
        engine = EvolutionEngine()
        metrics = {"observer": {"latency_ms": 300.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        result = engine.simulate(proposals)
        assert 0.0 <= result["coherence_before"] <= 1.0
        assert 0.0 <= result["coherence_after"] <= 1.0


# ===========================================================================
# Apply
# ===========================================================================


class TestApply:
    def test_apply_no_simulation(self):
        engine = EvolutionEngine()
        result = engine.apply()
        assert result["ok"] is False
        assert "reason" in result

    def test_apply_with_simulation(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        assert result["ok"] is True

    def test_apply_has_version(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        assert result["version"] is not None
        assert result["version"].startswith("evo-")

    def test_apply_has_provenance(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        prov = result["provenance"]
        assert "engine_version" in prov
        assert "phase" in prov
        assert "timestamp" in prov
        assert "observation_count" in prov

    def test_apply_has_rollback_plan(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        assert len(result["rollback_plan"]) > 0
        for step in result["rollback_plan"]:
            assert "action" in step
            assert step["action"] == "revert"

    def test_apply_structural_has_human_gate(self):
        engine = EvolutionEngine()
        metrics = {"validator": {"test_coverage": 0.2}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        # code_patch proposals should trigger human_gate
        if any(c["category"] in STRUCTURAL_CATEGORIES for c in result["changes"]):
            assert result["human_gate"] is True
            assert result["auto_merge"] is False

    def test_apply_low_risk_auto_merge(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        # Filter to only low-risk proposals
        low_risk = [p for p in proposals if p["category"] in LOW_RISK_CATEGORIES]
        if low_risk:
            sim = engine.simulate(low_risk)
            result = engine.apply(simulation=sim)
            if result["ok"]:
                assert result["auto_merge"] is True
                assert result["human_gate"] is False

    def test_apply_records_in_history(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        engine.apply()
        assert engine.state()["applied_count"] == 1

    def test_apply_changes_have_required_fields(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        for change in result["changes"]:
            assert "proposal_id" in change
            assert "category" in change
            assert "target" in change
            assert "description" in change
            assert "patch" in change
            assert "human_gate" in change

    def test_apply_no_passing_proposals(self):
        engine = EvolutionEngine()
        sim = {
            "ok": True,
            "results": [{"passed": False, "reason": "test"}],
            "coherence_before": 0.5,
            "coherence_after": 0.5,
            "coherence_delta": 0.0,
            "pass_count": 0,
            "fail_count": 1,
        }
        result = engine.apply(simulation=sim)
        assert result["ok"] is False
        assert "No proposals passed" in result["reason"]


# ===========================================================================
# Rollback verification
# ===========================================================================


class TestRollback:
    def test_rollback_plan_matches_changes(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        assert len(result["rollback_plan"]) == len(result["changes"])

    def test_rollback_plan_targets_match(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        change_ids = {c["proposal_id"] for c in result["changes"]}
        rollback_ids = {r["proposal_id"] for r in result["rollback_plan"]}
        assert change_ids == rollback_ids

    def test_rollback_has_restore_target(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        for step in result["rollback_plan"]:
            assert "restore_to" in step


# ===========================================================================
# Provenance logging
# ===========================================================================


class TestProvenance:
    def test_provenance_engine_version(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        assert result["provenance"]["engine_version"] == "1.0.0"

    def test_provenance_timestamp_format(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        ts = result["provenance"]["timestamp"]
        assert ts.endswith("Z")
        assert "T" in ts

    def test_provenance_coherence_tracking(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        result = engine.apply()
        prov = result["provenance"]
        assert "simulation_coherence_before" in prov
        assert "simulation_coherence_after" in prov


# ===========================================================================
# Pipeline state
# ===========================================================================


class TestPipeline:
    def test_pipeline_initial(self):
        engine = EvolutionEngine()
        p = engine.pipeline()
        assert p["stages"] == ["observe", "propose", "simulate", "apply"]
        assert p["last_observation"] is None

    def test_pipeline_after_full_run(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        engine.simulate(proposals)
        engine.apply()
        p = engine.pipeline()
        assert p["last_observation"] is not None
        assert p["last_simulation"] is not None
        assert p["last_applied"] is not None


# ===========================================================================
# Determinism
# ===========================================================================


class TestDeterminism:
    def test_full_pipeline_deterministic(self):
        def run_pipeline():
            engine = EvolutionEngine()
            metrics = {"router": {"latency_ms": 250.0}, "memory": {"memory_decay": 0.8}}
            obs = engine.observe(agent_metrics=metrics)
            proposals = engine.propose(observation=obs)
            sim = engine.simulate(proposals)
            result = engine.apply()
            return obs, proposals, sim, result

        obs1, props1, sim1, res1 = run_pipeline()
        obs2, props2, sim2, res2 = run_pipeline()

        assert obs1["agents"] == obs2["agents"]
        assert obs1["gaps"] == obs2["gaps"]
        assert [p["id"] for p in props1] == [p["id"] for p in props2]
        assert sim1["pass_count"] == sim2["pass_count"]
        assert res1["version"] == res2["version"]

    def test_deterministic_id(self):
        assert _deterministic_id("test") == _deterministic_id("test")
        assert _deterministic_id("a") != _deterministic_id("b")
        assert len(_deterministic_id("x")) == 12  # noqa: PLR2004


# ===========================================================================
# Thread safety
# ===========================================================================


class TestThreadSafety:
    def test_concurrent_observe(self):
        engine = EvolutionEngine()
        results = []
        errors = []

        def observe_thread():
            try:
                r = engine.observe()
                results.append(r["ok"])
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=observe_thread) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert all(results)
        assert engine.state()["phase"] == 10  # noqa: PLR2004

    def test_concurrent_mixed_ops(self):
        engine = EvolutionEngine()
        errors = []

        def mixed_thread():
            try:
                engine.observe()
                engine.state()
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=mixed_thread) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors


# ===========================================================================
# Internal helpers
# ===========================================================================


class TestHelpers:
    def test_lucas_weight_in_range(self):
        for i in range(20):
            w = _lucas_weight(i)
            assert 0.0 <= w <= 1.0

    def test_compute_agent_score_perfect(self):
        metrics = {
            "latency_ms": 0.0,
            "error_rate": 0.0,
            "test_coverage": 1.0,
        }
        score = _compute_agent_score(metrics)
        assert 0.0 <= score <= 1.0

    def test_compute_agent_score_worst(self):
        metrics = {
            "latency_ms": 500.0,
            "error_rate": 1.0,
            "test_coverage": 0.0,
        }
        score = _compute_agent_score(metrics)
        assert 0.0 <= score <= 1.0

    def test_build_spec_from_agents(self):
        agents = ["a", "b", "c"]
        spec = _build_spec_from_agents(agents)
        assert "layers" in spec
        assert len(spec["layers"]) == 3  # noqa: PLR2004
        assert spec["layers"]["a"]["depends_on"] == []
        assert spec["layers"]["b"]["depends_on"] == ["a"]
        assert spec["layers"]["c"]["depends_on"] == ["b"]

    def test_constants_defined(self):
        assert LATENCY_THRESHOLD_MS > 0
        assert 0.0 <= COHERENCE_FLOOR <= 1.0
        assert 0.0 <= MEMORY_DECAY_THRESHOLD <= 1.0
        assert 0.0 <= COVERAGE_FLOOR <= 1.0
        assert len(LOW_RISK_CATEGORIES) > 0
        assert len(STRUCTURAL_CATEGORIES) > 0

    def test_federation_agents_count(self):
        assert len(FEDERATION_AGENTS) == 13  # noqa: PLR2004


# ===========================================================================
# Edge cases
# ===========================================================================


class TestEdgeCases:
    def test_observe_empty_metrics(self):
        engine = EvolutionEngine()
        report = engine.observe(agent_metrics={})
        assert report["ok"] is True
        # All agents get default zero metrics
        assert report["summary"]["total_agents"] == 13  # noqa: PLR2004

    def test_propose_no_gaps(self):
        engine = EvolutionEngine()
        obs = {
            "ok": True,
            "phase": 1,
            "agents": {},
            "gaps": [],
            "coherence": 0.8,
            "summary": {},
        }
        proposals = engine.propose(observation=obs)
        assert proposals == []

    def test_simulate_all_fail(self):
        engine = EvolutionEngine()
        bad = {
            "id": "bad",
            "category": "code_patch",
            "target": "x",
            "description": "",
            "patch": {},
            "risk": "high",
            "human_gate": True,
            "sce88_valid": False,
        }
        result = engine.simulate(proposals=[bad])
        assert result["fail_count"] == 1
        assert result["pass_count"] == 0

    def test_apply_with_explicit_simulation(self):
        engine = EvolutionEngine()
        metrics = {"router": {"latency_ms": 250.0}}
        obs = engine.observe(agent_metrics=metrics)
        proposals = engine.propose(observation=obs)
        sim = engine.simulate(proposals)
        result = engine.apply(simulation=sim)
        assert isinstance(result, dict)

    def test_single_agent_federation(self):
        # Single agent → spec has 1 layer → SCE-88 validation fails
        engine = EvolutionEngine(agents=["solo"])
        report = engine.observe()
        # Observation should still work
        assert report["ok"] is True

    def test_two_agent_federation(self):
        engine = EvolutionEngine(agents=["alpha", "beta"])
        report = engine.observe()
        assert report["ok"] is True
        assert report["summary"]["total_agents"] == 2  # noqa: PLR2004


# ===========================================================================
# CLI end-to-end
# ===========================================================================


class TestEvolveCLI:
    def test_evolve_scan(self):
        stdout, _, rc = _run("evolve", "--scan")
        assert rc == 0
        data = json.loads(stdout)
        assert data["ok"] is True
        assert "agents" in data
        assert "gaps" in data
        assert "summary" in data

    def test_evolve_propose(self):
        stdout, _, rc = _run("evolve", "--propose")
        assert rc == 0
        data = json.loads(stdout)
        assert "proposals" in data
        assert isinstance(data["proposals"], list)

    def test_evolve_simulate(self):
        stdout, _, rc = _run("evolve", "--simulate")
        assert rc == 0
        data = json.loads(stdout)
        assert data["ok"] is True
        assert "pass_count" in data
        assert "fail_count" in data
        assert "coherence_before" in data
        assert "coherence_after" in data

    def test_evolve_apply(self):
        stdout, _, rc = _run("evolve", "--apply")
        assert rc == 0
        data = json.loads(stdout)
        assert "version" in data
        assert "provenance" in data
        assert "rollback_plan" in data

    def test_evolve_no_flag(self):
        _, _, rc = _run("evolve")
        assert rc != 0

    def test_evolve_scan_json_output(self):
        stdout, _, rc = _run("evolve", "--scan")
        assert rc == 0
        data = json.loads(stdout)
        assert data["summary"]["total_agents"] == 13  # noqa: PLR2004
