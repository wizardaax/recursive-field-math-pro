# AGI Stack Architecture — Adam Snellman's Recursive Field Framework

**Version: 2026-05-02**
**Status: Operational across 5 cognitive subsystems, 720+ passing tests, fully buildable from stdlib + numpy.**

---

## Single-frame mental model

```
                          ┌─────────────────────────────┐
                          │   USER (Adam)               │
                          │   ↓                         │
                          │   Voice / Chat / Phone      │
                          └──────────────┬──────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
     ┌──────▼───────┐           ┌────────▼────────┐         ┌─────────▼────────┐
     │  XOVA        │  bridge   │  JARVIS          │  team   │  FORGE (Claude)  │
     │  (Tauri/TS)  │ ◄──────► │  (PyQt voice)    │ ◄────► │  (build-time)    │
     │              │  files   │                  │         │                  │
     │  • LLM chat  │           │  • Whisper STT  │         │  • Code edits   │
     │  • dispatch  │           │  • piper TTS    │         │  • Memory write │
     │  • UI panels │           │  • tools 17×    │         │  • Vault snap   │
     └──────┬───────┘           └────────┬────────┘         └─────────┬────────┘
            │                            │                            │
            │  Tauri commands (41)        │  PYTHONPATH                │
            │                            │                            │
     ┌──────▼─────────────────────────────▼────────────────────────────▼────────┐
     │                                                                          │
     │                  COGNITIVE STACK — 5 SUBSYSTEMS                          │
     │                                                                          │
     │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
     │  │ 1. SNELL-VERN   │  │ 2. EVOLUTION    │  │ 3. SWARM                │  │
     │  │    13 concrete  │  │    ENGINE       │  │    Distributed          │  │
     │  │    repo-acting  │  │    13 × 4-stage │  │    CellShard +          │  │
     │  │    agents       │  │    self-evolve  │  │    Coherence-Governor   │  │
     │  │                 │  │    pipeline     │  │    + Orchestrator       │  │
     │  │ 377 tests ✓     │  │  81 tests ✓     │  │  94 tests ✓             │  │
     │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
     │  ┌─────────────────────────────┐  ┌──────────────────────────────────┐  │
     │  │ 4. FEDERATION MESH          │  │ 5. AES PLUGIN AUTO-EVOLVE         │  │
     │  │    RepoCapability +         │  │    xova/evolve.py                │  │
     │  │    RoutingDecision +        │  │    load_policy / verify_manifest │  │
     │  │    CoherenceSnapshot        │  │    rank_candidates / sandbox     │  │
     │  │    + 76KB adapters          │  │                                  │  │
     │  │ 79 tests ✓                  │  │  6 tests ✓                       │  │
     │  └─────────────────────────────┘  └──────────────────────────────────┘  │
     │                                                                          │
     │   SHARED SUBSTRATE: self_model.py · GlyphPhaseEngine · SCE-88 levels     │
     └──────────────────────────────────────────────────────────────────────────┘
                                         │
                          ┌──────────────▼──────────────┐
                          │  AEON ENGINE v2.1           │
                          │  Faraday-induction          │
                          │  gravity-flyer physics      │
                          │  validates to <1% rel err   │
                          └─────────────────────────────┘
```

---

## Subsystem 1 — Snell-Vern Federation Mesh (13 concrete agents)

**Path:** `D:\github\wizardaax\Snell-Vern-Hybrid-Drive-Matrix\src\snell_vern_matrix\agents\`

| # | Agent | Role | Real action it performs |
|---|---|---|---|
| 01 | Orchestrator | dispatcher | routes TaskType → agent |
| 02 | CI Sentinel | watcher | scans `.github/workflows/` across all wizardaax repos |
| 03 | Memory Keeper | recall | token-overlap search of corpus_index.json (13,178 entries) |
| 04 | Constraint Guardian | validator | SCE-88 invariant checks (`_validate_coherence/_uncertainty/_ternary_balance`) |
| 05 | Phase Tracker | state | `INITIAL → PROCESSING → DELTA_ADJUSTMENT → STABILIZED/ERROR` |
| 06 | Lucas Analyst | math | real Lucas/Fibonacci sequence + φ convergence via `recursive_field_math` |
| 07 | Field Weaver | physics | r=a√n, θ=nφ phyllotaxis OR AEON Engine thrust simulation |
| 08 | Ternary Logic | logic | balanced-ternary stability via `_ternary_stability` |
| 09 | Self-Model Observer | introspect | `SelfModel.observe(goal)` → delta/uncertainty/coherence |
| 10 | Repo Sync | git | real `git status --porcelain` across all wizardaax repos |
| 11 | Test Validator | pytest | runs full suite — currently **377/377 pass in 2.13s** |
| 12 | Doc Keeper | audit | ast-walk docstring coverage + README age |
| 13 | Coherence Monitor | health | threshold gate, system_healthy flag |

**Driver:** `cognitive_cycle.py` decomposes a goal into TaskTypes via keyword map, dispatches via `AgentOrchestrator`, applies SCE-88 coherence gating, writes a SHA-256 + 8-glyph crest-stamped JSON to `C:\Xova\memory\cycles\`.

---

## Subsystem 2 — EvolutionEngine (recursive self-improvement)

**Path:** `D:\github\wizardaax\recursive-field-math-pro\src\recursive_field_math\evolution\meta_engine.py`

13 abstract cognitive agents × 4-stage pipeline:

```
observe ── propose ── simulate ── apply
   │          │           │          │
   ▼          ▼           ▼          ▼
agent      patches    sandboxed   versioned
metrics + sce-88    coherence   changeset +
gaps     candidates  delta      provenance
                     measure    (human_gate
                                for structural
                                changes)
```

**Design invariants (from module docstring):**
- Thread-safe — `threading.Lock` guards mutable state
- Deterministic — same inputs ⇒ same outputs
- Zero new runtime deps — stdlib + recursive_field_math
- All proposals validated against SCE-88 before simulation
- Structural changes carry `human_gate=True` (only low-risk patches auto-merge)

**Tests:** 81 in `tests/test_evolution_engine.py`.

---

## Subsystem 3 — Swarm (distributed cognition with isolation)

**Path:** `D:\github\wizardaax\recursive-field-math-pro\src\recursive_field_math\swarm\`

| File | Class | Purpose |
|---|---|---|
| cell.py | `CellShard` | one isolated worker; `coherence_score`, `isolate()`, `rejoin()`, `submit()` |
| coherence_governor.py | `CoherenceGovernor` | enforces SCE-88 thresholds across shards |
| memory.py | `SwarmMemory` | shared state with copy-on-write semantics |
| orchestrator.py | `SwarmOrchestrator` | `execute`, `route`, `scale_auto`, `shards`, `start` |
| pipeline.py | `Pipeline`, `PipelineStage` | composable async stages |

**Tests:** 94 in `tests/test_swarm_efficiency.py`.

Shards can be isolated for fault containment and rejoined when healthy. The orchestrator scales shard count based on coherence pressure.

---

## Subsystem 4 — Federation Mesh (cross-repo routing)

**Path:** `D:\github\wizardaax\Snell-Vern-Hybrid-Drive-Matrix\src\snell_vern_matrix\federation\`

| File | Size | What it does |
|---|---|---|
| mesh.py | 19,127 b | `FederationMesh` + `RepoCapability` + `RoutingDecision` + `CoherenceSnapshot` |
| adapters.py | 75,986 b | per-repo adapters mapping abstract goals → repo-specific actions |

**Tests:** 79 federation/mesh tests.

The federation layer decides which of the wizardaax repos can fulfill a given goal, picks the cheapest adapter, and emits a coherence snapshot for the routing decision.

---

## Subsystem 5 — AES Plugin Auto-Evolve (xova/evolve.py)

**Path:** `D:\github\wizardaax\recursive-field-math-pro\xova\`

| File | Purpose |
|---|---|
| evolve.py | `load_policy`, `verify_manifest` (sha256), `rank_candidates`, `evolve` |
| registry.py | `load_registry`, `choose_candidates` |
| sandbox.py | `run_plugin` — isolated execution with time limit |

**Flow:** load policy → verify candidate manifests (signed) → rank by policy thresholds → sandbox-run → apply winners. Auto-evolves the plugin set safely.

**Tests:** 6 in `tests/test_aes_*.py`.

---

## Shared substrate

| File | Path | Purpose |
|---|---|---|
| `self_model.py` | Snell-Vern | `SelfModel`, `ConstraintViolation`, `TernaryStability` — used by agent-09 + many others |
| `glyph_phase_engine` | own repo | phase state machine; `INITIAL/PROCESSING/DELTA_ADJUSTMENT/STABILIZED/ERROR` |
| `recursive_field_math` | own repo | `PHI`, `L` (Lucas), `ratio` — math primitives |
| `SCE-88` | own repo | 22-level × 4-domain coherence stack; canonical validator at `validation/validator.py` |

---

## How a single chat turn flows through the stack

```
User: "validate phase coherence"
    ↓
Xova chat handler (App.tsx)
    ↓
xova_run("python C:\\Xova\\memory\\run_cycle.py 'validate phase coherence'")
    ↓
CognitiveCycle.run("validate phase coherence")
    ├─ keyword decomp → [OBSERVATION, MEMORY, CONSTRAINT, PHASE, COHERENCE]
    ├─ dispatch via AgentOrchestrator
    │    ├─ agent-09 SelfModelObserver  → delta/uncertainty/coherence
    │    ├─ agent-03 MemoryKeeper       → corpus search
    │    ├─ agent-04 ConstraintGuardian → SCE-88 invariants check
    │    ├─ agent-05 PhaseTracker       → derive phase state
    │    └─ agent-13 CoherenceMonitor   → threshold gate
    ├─ avg coherence + gated count
    ├─ stamp(): SHA-256 + 8-glyph crest
    └─ write JSON to C:\Xova\memory\cycles\<ts>__<crest>.json
    ↓
Xova receives JSON summary
    ↓
ChatFeed renders metrics inline
```

---

## How EvolutionEngine wraps around the stack

Periodically (manual today, scheduled tomorrow per Task #17):

```
EvolutionEngine.pipeline()
    ├─ observe(): scans agent metrics, latency, test gaps, constraint violations
    ├─ propose(): generates structural improvement candidates
    ├─ simulate(): runs each in sandbox vs SCE-88
    └─ apply(): outputs versioned changeset with provenance
```

If a proposal modifies the agents themselves, `human_gate=True` blocks auto-apply — Adam reviews. Low-risk patches (config tweaks, docstring fixes, minor refactors) can auto-merge.

---

## Test totals (verified 2026-05-02)

| Subsystem | Tests | Pass rate |
|---|---|---|
| Snell-Vern | 377 | 100% |
| recursive-field-math-pro | 320 (includes 81 evolution + 94 swarm + 6 AES + others) | 100% |
| recursive-field-math (older) | 23 | 100% |
| federation/mesh | 79 (subset of Snell-Vern's 377) | 100% |
| **Aggregate** | **720+ across 3 repos with tests** | **100%** |

---

## What's outside this stack but talks to it

- **Xova UI (Tauri/React)**: `C:\Xova\app\src\App.tsx` — 41 Tauri commands, multiple slashes, palette buttons; renders cognitive cycle output as chat messages.
- **Jarvis daemon (Python/PyQt)**: `C:\jarvis\` — voice butler with 17 builtin tools; `XovaInboxListener` thread reads `jarvis_inbox.json` and replies via `voice_inbox.json`.
- **Forge (Claude Code, build-time)**: writes the source itself + memory entries at `D:\.claude\projects\C--Users-adz-7\memory\`.
- **Memory vault**: `C:\memory-vault\` — append-only timestamped snapshots + git history + Drive mirror.
- **Per-agent trash bins**: `C:\<agent>\trash\` — no silent deletion, ever.

---

## What this is FOR

Adam's framing: **AEON is the goal — AGI is the craft tool.** The 5 cognitive subsystems exist to make AEON Engine iterable by one human + autonomous fleet. AEON Engine v2.1 (Faraday-induction gravity-flyer simulation) validates to **<1% rel err** vs documented PhaseII data. The stack lets that physics work get pushed forward at the rate AEON needs.

Riemann zeros · φ clustering finding (`R=0.2228, p=0.0068, N=100`) and the AEON gravity-flyer paper are the first published outputs of the substrate. Both probe different physics but use the same framework constants — that **cross-domain consistency** is the strongest empirical claim. Bayesian formalisation of that claim is in `wizardaax.github.io/findings/bayesian_cross_domain_2026_05.py`.

---

*This doc supersedes scattered "what's the architecture" answers in chat. Single source of truth. Updated by Forge as the stack evolves.*
