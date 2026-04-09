# SCE-88 Hardware Sovereignty Integration Spec

**Path:** `docs/specs/sce-88-sgx-integration.md`
**Status:** Draft / Ready for Phase 1 Discovery
**Author:** wizardaax
**Date:** 2026-04-08

---

## 1. Overview

This spec defines how to integrate **hardware-enforced sovereignty** into the current AI stack by placing critical policy and memory-trust functions behind a **hardware-backed trust boundary**. The goal is to preserve the existing software architecture while ensuring that sensitive state, policy decisions, and integrity checks are protected from OS-level tampering.

The target platform is an **R740xd-class server** with support for:
- **Confidential-computing enclaves** such as Intel SGX or AMD SEV
- **IOMMU-backed device isolation**
- Optional **FPGA-assisted integrity or gating logic**
- Protected memory regions for high-trust state

This document is implementation-oriented and intended for commit to `docs/specs/`.

---

## 2. Terminology

### Hardware terms
- **SGX**: Intel Software Guard Extensions, a CPU feature for enclave-style protected execution.
- **SEV**: AMD Secure Encrypted Virtualization, a CPU feature for protected guest memory and isolation.
- **TEE**: Trusted Execution Environment, a general term for protected compute regions.
- **IOMMU**: Input-Output Memory Management Unit, used to isolate DMA-capable devices from protected memory.

### Project terms
- **SCE-88**: The project’s sovereignty and policy model.
- **MemPalace**: The memory organization pattern using Wings / Halls / Rooms / Closets.
- **AAAK**: The project’s compression dialect / compact memory representation.
- **Protected memory**: State that must be verified, sealed, or integrity-checked before use.
- **High-trust state**: Policy rules, signatures, summaries, and critical memory records.

### Interpretation note
In this document, **SGX**, **SEV**, and **TEE** are hardware concepts, not repositories, packages, or modules.

---

## 3. Goals

### Primary goals
- Keep the existing math and symbolic-processing code in software.
- Move **policy enforcement**, **critical state validation**, and **high-trust memory handling** into a hardware-backed boundary.
- Ensure that AI memory artifacts can be structured, compressed, retrieved, and audited without exposing the trust core to the host OS.
- Preserve the current repository structure while introducing a secure integration path.

### Secondary goals
- Support a MemPalace-style memory hierarchy:
  - Wings
  - Halls
  - Rooms
  - Closets
- Allow software layers to continue using familiar Python/JS interfaces.
- Make integrity failures explicit and detectable.

---

## 4. Non-Goals

This spec does **not** aim to:
- Replace the full application stack with enclave code.
- Make the system “unhackable” or eliminate all trust in firmware or supply chain.
- Force all computation into hardware.
- Redesign the math core itself.

The math and symbolic logic stay intact. The enforcement model changes.

---

## 5. Threat Model

### Assumed attacker capabilities
- OS-level compromise
- Root access on the host
- Malicious local process
- Tampering with files on disk
- Memory scraping outside protected regions
- Replay or substitution of stale artifacts

### Assumed protected assets
- SCE-88 policy rules
- Trusted memory metadata
- Integrity signatures
- High-value state summaries
- Access-control decisions
- Write authorization for persistent memory

### Security objective
The host OS may observe and request work, but it should not be able to silently alter:
- Policy decisions
- Critical state
- Protected memory records
- Attested identity of trusted code

---

## 6. Repo Roles & Responsibilities

### `recursive-field-math`
- **Role:** Math core and artifact store
- **Responsibilities:** Numerical formulas, recursive field structures, analysis outputs, CSV/Markdown artifacts, structured memory candidates

### `glyph_phase_engine`
- **Role:** Symbolic processing and phase logic
- **Responsibilities:** Symbolic input transformation, coherence/phase-state processing, preprocessing before persistence, normalization of data

### `recursive-field-math-pro`
- **Role:** Orchestration, policy, execution, and integration layer
- **Responsibilities:** Application entry points, policy management, docs/release structure, execution glue, future enclave IPC/adapter code, hardware-aware trust boundary management

### `xova/` and `my_recursive_ai.py`
- **Role:** Agent-facing execution surface
- **Responsibilities:** User-facing orchestration, task dispatch, invoking policy-aware operations, routing memory writes/reads through trusted interfaces

---

## 7. Data Flow Model

### Proposed sovereign flow
1. **Software layer prepares request**
   Input arrives from user or task.
2. **Request enters hardware-trust boundary**
   Request passes into a confidential-computing enclave or equivalent.
3. **Enclave verifies policy**
   SCE-88 rules are evaluated inside the trusted boundary.
4. **Integrity decision returned**
   The enclave returns allow, deny, or transform.
5. **Only approved state is persisted or released**
   Approved data moves to MemPalace-style memory or persistent storage.
6. **Software consumes result**
   The AI receives verified context or a rejection reason.

---

## 8. Trust Boundaries

### Boundary A: Application Layer
- **Trust level:** Low
- **Components:** `my_recursive_ai.py`, UI/CLI adapters, outer orchestration code
- **Risk:** Runs on the host OS and is exposed to normal process compromise

### Boundary B: Processing Layer
- **Trust level:** Medium
- **Components:** `glyph_phase_engine`, symbolic transforms, data normalization
- **Risk:** Useful and necessary, but not authoritative for safety

### Boundary C: Policy Layer
- **Trust level:** High
- **Components:** `policies/`, SCE-88 rules, validation logic
- **Risk:** Must be protected from modification

### Boundary D: Protected Memory
- **Trust level:** Highest
- **Components:** Enclave memory, IOMMU-isolated buffers, integrity-checked persistent records
- **Risk:** System of record, protected by hardware isolation

---

## 9. SCE-88 Enforcement Points

### 9.1 Write Authorization
Every persistent write passes through a trusted gate.

**Enforce:**
- Schema validation
- Policy validation
- State transition validation
- Integrity signature generation

**Result:**
- Approved writes are committed
- Rejected writes are dropped with a reason code

### 9.2 Read Authorization
Every high-value read is verified before release.

**Enforce:**
- Record integrity check
- Freshness/version validation
- Policy-based redaction

**Result:**
- Verified output to software
- Explicit failure on tampering

### 9.3 State Bootstrapping
On system start:
- Load trusted policy hash
- Verify sealed state
- Restore protected summaries
- Refuse startup if trust is broken

### 9.4 Memory Promotion
When raw data becomes important enough to keep:
- Software proposes promotion
- Enclave validates it
- Approved facts move into protected storage tier

---

## 10. Software vs Hardware Split

### Keep in Software
- Math routines
- Symbolic transformations
- Compression algorithms (AAAK, lossless compression dialect)
- Retrieval ranking
- UI/CLI/agent orchestration
- Reporting and docs
- Non-sensitive caching

### Move to Hardware-Backed Protection
- SCE-88 policy rules
- Access-control decisions
- Integrity signatures
- High-trust memory summaries
- Sealed state
- Write authorization for protected memory
- Any source of truth for safety-critical state

### Optional Hardware Acceleration
- FPGA-assisted filtering
- IOMMU-enforced DMA isolation
- Device-level integrity checks

---

## 11. MemPalace-Compatible Memory Structure

The **MemPalace** hierarchy is used as the organization model for protected memory:

- **Wing:** Major domain or project
- **Hall:** Functional sub-area
- **Room:** Topic cluster or state family
- **Closet:** Compact summary or compressed memory packet
- **Drawer:** Raw immutable evidence or original artifact

### Mapping
- `recursive-field-math` artifacts → Wing/Hall/Room entries
- CSV outputs → Drawer or Closet payloads
- Policy decisions → sealed metadata attached to the Room
- Execution traces → append-only audit records

---

## 12. Integration Architecture

### Proposed Components
1. **Policy Adapter**
   Converts software requests into enclave-verifiable policy queries
2. **Enclave Gatekeeper**
   Validates requests and returns allow/deny/transform results
3. **Memory Broker**
   Manages structured storage routes and writes only after approval
4. **Integrity Service**
   Signs or verifies records and checks versioning and replay resistance
5. **Agent Bridge**
   Exposes safe APIs to `my_recursive_ai.py` and any MCP-like layer

---

## 13. Implementation Phases

### Phase 1: Discovery
- Identify exact entry points in `my_recursive_ai.py`
- Enumerate policy files in `policies/`
- Map read/write paths to persistent storage
- Locate all persistent storage touchpoints

### Phase 2: Interface Design
- Define enclave request/response schema
- Define policy hash format
- Define trust-state serialization

### Phase 3: Adapter Layer
- Add a software wrapper around policy calls
- Route writes through the gatekeeper
- Route sensitive reads through verification

### Phase 4: Protected State
- Seal critical summaries
- Protect signatures and policy versions
- Introduce tamper detection

### Phase 5: Hardening
- Add audit logging
- Add replay protection
- Add fail-closed behavior
- Add tests for tampering and rollback

---

## 14. Risks and Limitations

- Confidential-computing support varies by platform and CPU generation
- Enclave memory is limited and expensive
- Hardware trust still depends on firmware and provisioning quality
- Debugging enclave code is harder than ordinary Python
- Over-architecting could hurt iteration speed

**Recommendation:** Keep the first enclave boundary narrow and focused on **policy + integrity**, not the entire application.

---

## 15. Open Questions

Before implementation, verify:
1. What are the actual entry points in `my_recursive_ai.py`?
2. Which files in `policies/` contain authoritative rules?
3. Which objects are truly safety-critical vs. merely useful?
4. What data must be sealed vs. merely logged?
5. What is the minimal enclave API needed?
6. Do we need read protection, write protection, or a split model?
7. Should FPGA logic act as a filter, verifier, or accelerator?
8. What is the rollback model for protected memory?
9. How are policy updates signed and rotated?
10. Which parts of the memory hierarchy are mutable vs. append-only?

---

## 16. Recommended Next Step

1. Commit this spec to `docs/specs/sce-88-sgx-integration.md`.
2. Execute **Phase 1: Discovery** by mapping actual code paths in `my_recursive_ai.py`, `pyproject.toml`, and `policies/`.
3. Draft the **Policy Adapter** interface contract based on discovery findings.
