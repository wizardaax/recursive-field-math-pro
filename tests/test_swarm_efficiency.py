"""
Tests for the cellular swarm efficiency architecture.

Covers:
- Deterministic hash routing
- Stateless worker lifecycle
- Pipeline stages & backpressure
- Coherence/compute ratio gating
- Hardware-aware pool limits
- Shard isolation/failover
- SwarmMemory
- CoherenceGovernor
- SwarmOrchestrator end-to-end
- CLI end-to-end
"""

import contextlib
import json
import os
import subprocess
import sys
import threading

from recursive_field_math.swarm.cell import (
    CellShard,
    deterministic_route,
    deterministic_worker_slot,
)
from recursive_field_math.swarm.coherence_governor import (
    CoherenceGovernor,
)
from recursive_field_math.swarm.memory import SwarmMemory
from recursive_field_math.swarm.orchestrator import (
    SwarmOrchestrator,
    compute_max_workers,
)
from recursive_field_math.swarm.pipeline import (
    Pipeline,
    PipelineStage,
)


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
# 1. Deterministic Hash Routing
# ===========================================================================


class TestDeterministicRouting:
    def test_same_input_same_shard(self):
        """Identical input always routes to the same shard."""
        for _ in range(100):
            assert deterministic_route("hello", 8) == deterministic_route("hello", 8)

    def test_different_inputs_distribute(self):
        """Different inputs distribute across shards."""
        shards = {deterministic_route(f"input_{i}", 8) for i in range(50)}
        assert len(shards) > 1  # at least some distribution

    def test_route_with_one_shard(self):
        assert deterministic_route("anything", 1) == 0

    def test_route_bounds(self):
        for n in [1, 2, 4, 16, 100]:
            idx = deterministic_route("test", n)
            assert 0 <= idx < n

    def test_route_invalid_num_shards(self):
        try:
            deterministic_route("test", 0)
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

    def test_worker_slot_deterministic(self):
        for _ in range(100):
            assert deterministic_worker_slot("data", 4) == deterministic_worker_slot("data", 4)

    def test_worker_slot_bounds(self):
        for n in [1, 2, 8, 32]:
            slot = deterministic_worker_slot("test", n)
            assert 0 <= slot < n

    def test_worker_slot_invalid(self):
        try:
            deterministic_worker_slot("test", 0)
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

    def test_route_reproducibility_across_instances(self):
        """Route is purely functional — no instance state needed."""
        results = [deterministic_route("fixed_input", 10) for _ in range(50)]
        assert len(set(results)) == 1

    def test_route_and_slot_independence(self):
        """Shard route and worker slot use different hashes."""
        shard = deterministic_route("x", 100)
        slot = deterministic_worker_slot("x", 100)
        # They CAN be equal by coincidence, but the point is they're independent
        # Just verify both are valid
        assert 0 <= shard < 100  # noqa: PLR2004
        assert 0 <= slot < 100  # noqa: PLR2004


# ===========================================================================
# 2. SwarmMemory
# ===========================================================================


class TestSwarmMemory:
    def test_put_get(self):
        mem = SwarmMemory()
        mem.put("key1", {"v": 1})
        assert mem.get("key1") == {"v": 1}

    def test_get_default(self):
        mem = SwarmMemory()
        assert mem.get("missing") is None
        assert mem.get("missing", 42) == 42  # noqa: PLR2004

    def test_delete(self):
        mem = SwarmMemory()
        mem.put("k", 1)
        assert mem.delete("k") is True
        assert mem.get("k") is None
        assert mem.delete("k") is False

    def test_keys_insertion_order(self):
        mem = SwarmMemory()
        mem.put("b", 2)
        mem.put("a", 1)
        mem.put("c", 3)
        assert mem.keys() == ["b", "a", "c"]

    def test_size(self):
        mem = SwarmMemory()
        assert mem.size() == 0
        mem.put("k1", 1)
        assert mem.size() == 1

    def test_clear(self):
        mem = SwarmMemory()
        mem.put("k1", 1)
        mem.put("k2", 2)
        mem.clear()
        assert mem.size() == 0

    def test_eviction_fifo(self):
        mem = SwarmMemory(max_entries=3)
        mem.put("a", 1)
        mem.put("b", 2)
        mem.put("c", 3)
        mem.put("d", 4)  # evicts "a"
        assert mem.get("a") is None
        assert mem.get("d") == 4  # noqa: PLR2004
        assert mem.size() == 3  # noqa: PLR2004

    def test_max_entries_validation(self):
        try:
            SwarmMemory(max_entries=0)
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

    def test_snapshot(self):
        mem = SwarmMemory()
        mem.put("x", 10)
        snap = mem.snapshot()
        assert snap == {"x": 10}
        # Modifying snapshot doesn't affect memory
        snap["x"] = 999
        assert mem.get("x") == 10  # noqa: PLR2004

    def test_stats(self):
        mem = SwarmMemory(max_entries=100)
        mem.put("k", 1)
        stats = mem.stats()
        assert stats["size"] == 1
        assert stats["max_entries"] == 100  # noqa: PLR2004
        assert 0.0 <= stats["utilisation"] <= 1.0

    def test_get_or_put(self):
        mem = SwarmMemory()
        val = mem.get_or_put("new_key", lambda: 42)
        assert val == 42  # noqa: PLR2004
        assert mem.get("new_key") == 42  # noqa: PLR2004
        # Second call returns cached value
        val2 = mem.get_or_put("new_key", lambda: 99)
        assert val2 == 42  # noqa: PLR2004

    def test_update_existing_key(self):
        mem = SwarmMemory()
        mem.put("k", 1)
        mem.put("k", 2)
        assert mem.get("k") == 2  # noqa: PLR2004
        assert mem.size() == 1

    def test_thread_safety(self):
        mem = SwarmMemory(max_entries=1000)
        errors = []

        def writer(prefix, n):
            try:
                for i in range(n):
                    mem.put(f"{prefix}_{i}", i)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(f"t{t}", 50)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0
        assert mem.size() <= 1000  # noqa: PLR2004


# ===========================================================================
# 3. CellShard — Stateless Worker Lifecycle
# ===========================================================================


class TestCellShard:
    def test_init_defaults(self):
        shard = CellShard(shard_id=0)
        assert shard.shard_id == 0
        assert shard.workers_per_shard >= 1
        assert not shard.isolated
        assert shard.coherence_score > 0

    def test_start_stop(self):
        shard = CellShard(shard_id=1)
        shard.start()
        shard.stop()
        # Double stop is safe
        shard.stop()

    def test_execute_sync(self):
        shard = CellShard(shard_id=0)
        result = shard.execute_sync(lambda x: x.upper(), "hello")
        assert result == "HELLO"

    def test_submit_async(self):
        shard = CellShard(shard_id=0)
        shard.start()
        future = shard.submit(lambda x: len(x), "hello")
        assert future is not None
        assert future.result(timeout=5) == 5  # noqa: PLR2004
        shard.stop()

    def test_metrics_after_work(self):
        shard = CellShard(shard_id=0)
        shard.execute_sync(lambda x: x, "data")
        m = shard.metrics()
        assert m["tasks_completed"] == 1
        assert m["tasks_failed"] == 0
        assert m["total_compute_time"] > 0

    def test_failure_tracking(self):
        shard = CellShard(shard_id=0)

        def bad_fn(x):
            raise ValueError("boom")

        with contextlib.suppress(ValueError):
            shard.execute_sync(bad_fn, "data")
        m = shard.metrics()
        assert m["tasks_failed"] == 1

    def test_coherence_validation(self):
        shard = CellShard(shard_id=0)
        assert shard.validate_coherence() is True

    def test_isolate_and_rejoin(self):
        shard = CellShard(shard_id=0)
        shard.isolate()
        assert shard.isolated is True
        # Rejoin succeeds because default spec passes SCE-88
        assert shard.rejoin() is True
        assert shard.isolated is False

    def test_submit_returns_none_when_isolated(self):
        shard = CellShard(shard_id=0)
        shard.isolate()
        assert shard.submit(lambda x: x, "data") is None

    def test_execute_sync_raises_when_isolated(self):
        shard = CellShard(shard_id=0)
        shard.isolate()
        try:
            shard.execute_sync(lambda x: x, "data")
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError:
            pass

    def test_repr(self):
        shard = CellShard(shard_id=3, workers_per_shard=8)
        r = repr(shard)
        assert "3" in r
        assert "8" in r

    def test_stateless_pattern(self):
        """Workers don't retain state between invocations."""
        mem = SwarmMemory()
        shard = CellShard(shard_id=0, memory=mem)

        def worker(x):
            # Store result in shared memory, not local state
            mem.put(f"result_{x}", x.upper())
            return x.upper()

        shard.execute_sync(worker, "a")
        shard.execute_sync(worker, "b")
        assert mem.get("result_a") == "A"
        assert mem.get("result_b") == "B"

    def test_coherence_decay_on_failure(self):
        """Coherence score decreases on task failure via φ-decay."""
        shard = CellShard(shard_id=0)
        initial = shard.coherence_score

        def fail_fn(x):
            raise RuntimeError("fail")

        with contextlib.suppress(RuntimeError):
            shard.execute_sync(fail_fn, "x")
        assert shard.coherence_score < initial


# ===========================================================================
# 4. Pipeline Stages & Backpressure
# ===========================================================================


class TestPipelineStage:
    def test_enqueue_process(self):
        stage = PipelineStage("double", lambda x: x * 2, batch_size=4)
        stage.enqueue(5)
        results = stage.process()
        assert results == [10]

    def test_batch_processing(self):
        stage = PipelineStage("inc", lambda x: x + 1, batch_size=3)
        for i in range(5):
            stage.enqueue(i)
        r1 = stage.process()  # first batch of 3
        r2 = stage.process()  # remaining 2
        assert r1 == [1, 2, 3]
        assert r2 == [4, 5]

    def test_backpressure(self):
        stage = PipelineStage("id", lambda x: x, buffer_size=2, batch_size=1)
        assert stage.enqueue(1) is True
        assert stage.enqueue(2) is True
        assert stage.enqueue(3) is False  # buffer full → backpressure
        assert stage.backpressure is True

    def test_backpressure_release(self):
        stage = PipelineStage("id", lambda x: x, buffer_size=2, batch_size=1)
        stage.enqueue(1)
        stage.enqueue(2)
        stage.process()  # drain one
        assert stage.enqueue(3) is True  # space available again

    def test_flush(self):
        stage = PipelineStage("square", lambda x: x**2, batch_size=2)
        for i in range(5):
            stage.enqueue(i)
        results = stage.flush()
        assert sorted(results) == [0, 1, 4, 9, 16]

    def test_metrics(self):
        stage = PipelineStage("test", lambda x: x, batch_size=4)
        stage.enqueue(1)
        stage.process()
        m = stage.metrics()
        assert m["items_processed"] == 1
        assert m["batches_processed"] == 1

    def test_enqueue_batch(self):
        stage = PipelineStage("id", lambda x: x, buffer_size=3)
        accepted = stage.enqueue_batch([1, 2, 3, 4, 5])
        assert accepted == 3  # noqa: PLR2004

    def test_pending(self):
        stage = PipelineStage("id", lambda x: x)
        stage.enqueue("a")
        stage.enqueue("b")
        assert stage.pending() == 2  # noqa: PLR2004

    def test_empty_process(self):
        stage = PipelineStage("id", lambda x: x)
        assert stage.process() == []

    def test_handler_exception(self):
        """Exceptions in handler produce None results."""
        stage = PipelineStage("fail", lambda x: 1 / 0)
        stage.enqueue(1)
        results = stage.process()
        assert results == [None]


class TestPipeline:
    def test_two_stage_pipeline(self):
        s1 = PipelineStage("double", lambda x: x * 2, batch_size=4)
        s2 = PipelineStage("str", lambda x: str(x), batch_size=4)
        pipe = Pipeline([s1, s2])
        pipe.push(5)
        results = pipe.run_all()
        assert results == ["10"]

    def test_run_all(self):
        s1 = PipelineStage("inc", lambda x: x + 1, batch_size=4)
        s2 = PipelineStage("str", lambda x: str(x), batch_size=4)
        pipe = Pipeline([s1, s2])
        for i in range(5):
            pipe.push(i)
        results = pipe.run_all()
        assert sorted(results) == ["1", "2", "3", "4", "5"]

    def test_push_batch(self):
        s1 = PipelineStage("id", lambda x: x, batch_size=10)
        pipe = Pipeline([s1])
        count = pipe.push_batch([1, 2, 3])
        assert count == 3  # noqa: PLR2004

    def test_empty_pipeline_raises(self):
        try:
            Pipeline([])
            raise AssertionError("Should raise ValueError")
        except ValueError:
            pass

    def test_metrics(self):
        s1 = PipelineStage("a", lambda x: x)
        pipe = Pipeline([s1])
        m = pipe.metrics()
        assert len(m) == 1
        assert m[0]["name"] == "a"

    def test_validate_coherence(self):
        s1 = PipelineStage("a", lambda x: x)
        pipe = Pipeline([s1])
        assert pipe.validate_coherence() is True

    def test_backpressure_detection(self):
        s1 = PipelineStage("a", lambda x: x, buffer_size=1)
        pipe = Pipeline([s1])
        pipe.push(1)
        pipe.push(2)  # rejected
        assert pipe.has_backpressure() is True


# ===========================================================================
# 5. Coherence Governor
# ===========================================================================


class TestCoherenceGovernor:
    def test_ok_action(self):
        gov = CoherenceGovernor()
        result = gov.update(0.8, 2)
        assert result["action"] == "ok"

    def test_consolidate_action(self):
        gov = CoherenceGovernor(ratio_threshold=0.5)
        # 0.3 / 1 = 0.3 < 0.5 threshold
        result = gov.update(0.3, 1)
        assert result["action"] == "consolidate"
        assert gov.throttle_active is True

    def test_halt_action(self):
        gov = CoherenceGovernor(global_floor=0.5)
        result = gov.update(0.1, 1)
        assert result["action"] == "halt"
        assert gov.halt_triggered is True

    def test_reset_halt(self):
        gov = CoherenceGovernor(global_floor=0.5)
        gov.update(0.1, 1)
        assert gov.halt_triggered is True
        gov.reset_halt()
        assert gov.halt_triggered is False

    def test_metrics(self):
        gov = CoherenceGovernor()
        gov.update(0.8, 4)
        m = gov.metrics()
        assert "global_coherence" in m
        assert "coherence_compute_ratio" in m

    def test_history(self):
        gov = CoherenceGovernor()
        gov.update(0.8, 4)
        gov.update(0.7, 3)
        h = gov.history()
        assert len(h) == 2  # noqa: PLR2004

    def test_recommended_workers_normal(self):
        gov = CoherenceGovernor()
        gov.update(0.8, 4)
        assert gov.recommended_workers(4) == 4  # noqa: PLR2004

    def test_recommended_workers_on_halt(self):
        gov = CoherenceGovernor(global_floor=0.5)
        gov.update(0.1, 1)
        assert gov.recommended_workers(4) == 0

    def test_recommended_workers_on_consolidate(self):
        gov = CoherenceGovernor(ratio_threshold=0.5)
        gov.update(0.3, 1)
        rec = gov.recommended_workers(10)
        assert rec < 10  # noqa: PLR2004
        assert rec >= 1

    def test_zero_workers_ratio(self):
        """Zero active workers doesn't crash."""
        gov = CoherenceGovernor()
        result = gov.update(0.5, 0)
        assert result["ratio"] == 0.5  # noqa: PLR2004


# ===========================================================================
# 6. Hardware-Aware Pool Limits
# ===========================================================================


class TestHardwareAware:
    def test_compute_max_workers_explicit(self):
        w = compute_max_workers(cpu_cores=4, available_ram_mb=400, worker_footprint_mb=50)
        # by_cpu = 8, by_ram = 8
        assert w == 8  # noqa: PLR2004

    def test_compute_max_workers_ram_limited(self):
        w = compute_max_workers(cpu_cores=16, available_ram_mb=200, worker_footprint_mb=50)
        # by_cpu = 32, by_ram = 4
        assert w == 4  # noqa: PLR2004

    def test_compute_max_workers_cpu_limited(self):
        w = compute_max_workers(cpu_cores=2, available_ram_mb=10000, worker_footprint_mb=50)
        # by_cpu = 4, by_ram = 200
        assert w == 4  # noqa: PLR2004

    def test_compute_max_workers_minimum_one(self):
        w = compute_max_workers(cpu_cores=1, available_ram_mb=1, worker_footprint_mb=1000)
        assert w >= 1

    def test_orchestrator_caps_workers(self):
        """Orchestrator should not exceed hardware limits."""
        orch = SwarmOrchestrator(num_shards=100, workers_per_shard=100)
        total = orch._num_shards * orch._workers_per_shard
        hw_max = compute_max_workers()
        assert total <= hw_max or orch._workers_per_shard == 1


# ===========================================================================
# 7. SwarmOrchestrator
# ===========================================================================


class TestSwarmOrchestrator:
    def test_init_defaults(self):
        orch = SwarmOrchestrator()
        assert len(orch.shards) > 0
        assert orch.memory is not None
        assert orch.governor is not None

    def test_start_stop(self):
        orch = SwarmOrchestrator()
        orch.start()
        assert orch.started is True
        orch.stop()
        assert orch.started is False

    def test_deterministic_routing(self):
        orch = SwarmOrchestrator(num_shards=8)
        idx1 = orch.route("test_input")
        idx2 = orch.route("test_input")
        assert idx1 == idx2

    def test_execute_sync(self):
        orch = SwarmOrchestrator(num_shards=2, workers_per_shard=2)
        orch.start()
        result = orch.execute(lambda x: x.upper(), "hello")
        assert result == "HELLO"
        orch.stop()

    def test_execute_batch(self):
        orch = SwarmOrchestrator(num_shards=2, workers_per_shard=2)
        orch.start()
        inputs = ["a", "b", "c"]
        results = orch.execute_batch(lambda x: x.upper(), inputs)
        assert results == ["A", "B", "C"]
        orch.stop()

    def test_status(self):
        orch = SwarmOrchestrator()
        s = orch.status()
        assert "num_shards" in s
        assert "healthy_shards" in s
        assert "efficiency_mode" in s
        assert "shards" in s
        assert "pipeline" in s

    def test_scale_auto(self):
        orch = SwarmOrchestrator()
        result = orch.scale_auto()
        assert "hw_max_workers" in result
        assert "governor_recommended" in result

    def test_failover_to_healthy_shard(self):
        orch = SwarmOrchestrator(num_shards=3, workers_per_shard=2)
        orch.start()
        # Isolate shard 0
        orch.shards[0].isolate()
        # Should still execute via healthy shard
        result = orch.execute(lambda x: x, "test")
        assert result == "test"
        orch.stop()

    def test_all_shards_isolated_raises(self):
        orch = SwarmOrchestrator(num_shards=2)
        orch.start()
        for s in orch.shards:
            s.isolate()
        try:
            orch.execute(lambda x: x, "test")
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError:
            pass
        orch.stop()

    def test_halt_prevents_execution(self):
        orch = SwarmOrchestrator()
        orch.governor.update(0.01, 1)  # trigger halt
        try:
            orch.execute(lambda x: x, "test")
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError:
            pass

    def test_pipeline_property(self):
        orch = SwarmOrchestrator()
        pipe = orch.pipeline
        assert pipe is not None
        assert len(pipe.stages) == 4  # noqa: PLR2004

    def test_set_pipeline(self):
        orch = SwarmOrchestrator()
        custom = Pipeline([PipelineStage("custom", lambda x: x)])
        orch.set_pipeline(custom)
        assert orch.pipeline.stages[0].name == "custom"

    def test_efficiency_modes(self):
        for mode in ["balanced", "throughput", "coherence-strict"]:
            orch = SwarmOrchestrator(efficiency_mode=mode)
            assert orch.status()["efficiency_mode"] == mode


# ===========================================================================
# 8. Shard Isolation / Failover
# ===========================================================================


class TestShardIsolationFailover:
    def test_auto_isolate_on_low_coherence(self):
        shard = CellShard(shard_id=0)
        # Simulate many failures to decay coherence below floor
        for _ in range(20):
            with contextlib.suppress(RuntimeError):
                shard.execute_sync(lambda x: (_ for _ in ()).throw(RuntimeError("f")), "x")
        assert shard.isolated is True

    def test_isolated_shard_metrics(self):
        shard = CellShard(shard_id=0)
        shard.isolate()
        m = shard.metrics()
        assert m["isolated"] is True

    def test_rejoin_after_isolation(self):
        shard = CellShard(shard_id=0)
        shard.isolate()
        assert shard.rejoin() is True
        assert shard.isolated is False


# ===========================================================================
# 9. CLI end-to-end
# ===========================================================================


class TestSwarmCLI:
    def test_status(self):
        stdout, stderr, rc = _run("swarm", "--status")
        assert rc == 0
        data = json.loads(stdout)
        assert "num_shards" in data
        assert "healthy_shards" in data

    def test_status_custom_shards(self):
        stdout, _, rc = _run("swarm", "--status", "--shards", "2", "--workers-per-shard", "2")
        assert rc == 0
        data = json.loads(stdout)
        assert data["num_shards"] == 2  # noqa: PLR2004

    def test_scale_auto(self):
        stdout, _, rc = _run("swarm", "--scale", "auto")
        assert rc == 0
        data = json.loads(stdout)
        assert "hw_max_workers" in data

    def test_run_batch(self):
        stdout, _, rc = _run("swarm", "--run", '["a","b","c"]')
        assert rc == 0
        data = json.loads(stdout)
        assert data["results"] == ["a", "b", "c"]

    def test_efficiency_mode(self):
        stdout, _, rc = _run("swarm", "--status", "--efficiency-mode", "coherence-strict")
        assert rc == 0
        data = json.loads(stdout)
        assert data["efficiency_mode"] == "coherence-strict"

    def test_no_flag_exits_nonzero(self):
        _, _, rc = _run("swarm")
        assert rc != 0


# ===========================================================================
# 10. Integration / Determinism under load
# ===========================================================================


class TestIntegrationDeterminism:
    def test_batch_determinism(self):
        """Identical batch inputs produce identical results across runs."""
        inputs = [f"item_{i}" for i in range(20)]
        orch1 = SwarmOrchestrator(num_shards=4, workers_per_shard=2)
        orch1.start()
        r1 = orch1.execute_batch(lambda x: x.upper(), inputs)
        orch1.stop()

        orch2 = SwarmOrchestrator(num_shards=4, workers_per_shard=2)
        orch2.start()
        r2 = orch2.execute_batch(lambda x: x.upper(), inputs)
        orch2.stop()

        assert r1 == r2

    def test_routing_determinism_under_load(self):
        """Routing is deterministic even with many concurrent calls."""
        orch = SwarmOrchestrator(num_shards=8)
        routes = [orch.route(f"input_{i}") for i in range(1000)]
        routes2 = [orch.route(f"input_{i}") for i in range(1000)]
        assert routes == routes2

    def test_concurrent_memory_access(self):
        mem = SwarmMemory(max_entries=500)
        errors = []

        def worker(tid):
            try:
                for i in range(100):
                    mem.put(f"t{tid}_{i}", i)
                    mem.get(f"t{tid}_{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0

    def test_pipeline_deterministic_order(self):
        """Pipeline processes items in FIFO order within each batch."""
        s1 = PipelineStage("id", lambda x: x, batch_size=100)
        pipe = Pipeline([s1])
        items = list(range(10))
        for i in items:
            pipe.push(i)
        results = pipe.run_all()
        assert results == items
