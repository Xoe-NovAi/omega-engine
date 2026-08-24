# 🔱 Sovereign Gate — Phase C: Cognitive Substrate
# ⬡ OMEGA ⬡ MA'AT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_sovereign_gate ⬡ VERIFICATION

**AP Token**: `AP-PHASE-C-GATES-v1.0.0`
**Status**: MANDATORY
**Scope**: Phase C (Cognitive Substrate) Implementation
**Updated**: 2026-06-15

This document defines the absolute quality bars (T-Gates) and the Definition of Done (DoD) for the Cognitive Substrate. No component of Phase C is considered complete until it passes these gates and is verified via `make temple-grade`.

---

## §1 T-Gates (Temple-Grade Verification)

### T12: Semantic Integrity Gate
**Goal**: Ensure consistency between persisted memory (SDR/Vector) and distilled gnosis (`soul.yaml`).

#### 1.1 Test Cases
| ID | Scenario | Expected Result | Detection Method |
|----|----------|-----------------|------------------|
| **T12-01** | **Direct Contradiction** | `ContradictionReport` generated; state locked until resolution. | NLI-based comparison of Memory vs Soul. |
| **T12-02** | **Temporal Conflict** | Recent memory overrides stale soul entry; update triggered. | Timestamp-based conflict detection. |
| **T12-03** | **Nuance Drift** | Flagged as "Refinement" (L2 $\rightarrow$ L3 evolution); no lock. | Semantic similarity threshold check. |

#### 1.2 Skeptical Verifier Output
The Skeptical Verifier must produce a `ContradictionReport` containing:
- **Source A (Memory)**: Verbatim excerpt and `trace_id`.
- **Source B (Soul)**: Verbatim excerpt and `soul_version`.
- **Conflict Type**: `DIRECT` | `TEMPORAL` | `NUANCE`.
- **Confidence Score**: 0.0-1.0.
- **Resolution Path**: Recommended override source.

---

### T-Gate: Somatic Caching (Zero-Copy State)
**Goal**: Verify $O(1)$ load times and zero-copy transitions for 1MB+ state pages using `mmap`.

#### 2.1 Requirements
- **Zero-Copy**: No `read()`, `memcpy()`, or `pickle.load()` calls in the hot path.
- **Complexity**: Load time must be $O(1)$ relative to page size.

#### 2.2 Benchmark Protocol
- **Tool**: `perf stat` + custom Python benchmark using `time.perf_counter_ns()`.
- **Metric**: Access latency for a random offset in a 1MB page vs a 10MB page.
- **Pass Criteria**: $\Delta \text{latency} < 5\%$ across page sizes.
- **Verification**: `strace` must show `mmap()` call but NO `read()` calls during state access.

---

### T-Gate: Symmetry-Break (Fast/Slow Toggle)
**Goal**: Verify the 'Fast/Slow' toggle and the triggering of `SymmetryBreakError`.

#### 3.1 Verification Process
1. **Fast Mode**: Set `SymmetryMode = FAST`. Execute 1,000 state transitions. Verify $\approx 0$ latency overhead.
2. **Slow Mode**: Set `SymmetryMode = SLOW`. Trigger a "Symmetry Audit" (forced verification).
3. **Trigger**: Inject a known contradiction into memory.
4. **Expectation**: System MUST raise `SymmetryBreakError` and halt the transition.
5. **Recovery**: Verify that the system recovers to `FAST` mode only after the contradiction is resolved.

---

## §2 Definition of Done (DoD)

A task is only 'Done' when it satisfies all checkboxes.

### 2.1 Somatic Caching
- [ ] **T-Gate Pass**: Zero-copy verified via `strace`/`perf`.
- [ ] **Complexity Pass**: $O(1)$ load verified for 1MB+ pages.
- [ ] **Temple-Grade**: `make temple-grade` Pass.
- [ ] **Sovereignty**: No cloud-dependency for state loading.

### 2.2 Dreaming Cycle (Cognitive Metabolism)
- [ ] **T-Gate Pass**: Strict Idle-Lock verified (CPU < 5% for 60s).
- [ ] **Priority Pass**: Process runs with `nice` value 19.
- [ ] **Temple-Grade**: `make temple-grade` Pass.
- [ ] **Integrity**: No orphan files created during metabolism.

### 2.3 Symmetry Audit
- [ ] **T-Gate Pass**: `SymmetryBreakError` triggered and caught.
- [ ] **Toggle Pass**: Fast/Slow state persistence verified in `cvar_table`.
- [ ] **Temple-Grade**: `make temple-grade` Pass.

### 2.4 SDR Indexing
- [ ] **T-Gate Pass**: Contiguous C-buffer verified via `ctypes` address check.
- [ ] **Alignment Pass**: Memory alignment verified for AVX2 optimization.
- [ ] **Temple-Grade**: `make temple-grade` Pass.

---

## §3 Sovereign Mandate Enforcement

### M17: Cognitive Integrity (Skeptical Verifier)
**Success Criteria**: A contradiction is considered 'resolved' if and only if:
1. **Weight-Based Override**: A higher-weight source (Soul $\rightarrow$ Memory $\rightarrow$ Cache) overrides the conflict.
2. **Temporal Override**: The most recent timestamped evidence is adopted.
3. **Human ACK**: An explicit user-provided resolution is recorded.
4. **Gnosis Distillation**: The resolution is distilled into a new L2 Insight in `soul.yaml`.

### Dreaming Cycle: Strict Idle-Lock
**Enforcement Mechanism**:
- **Resource Check**: The Dreaming process must poll `psutil.cpu_percent(interval=1)` and `psutil.virtual_memory().percent`.
- **Threshold**: CPU load $< 5\%$ AND RAM usage $< 80\%$ for 60 consecutive seconds.
- **Lock-Out**: If thresholds are exceeded, the Dreaming cycle must immediately `yield` or `sleep` for 300 seconds.
- **Priority**: Must be spawned as a separate process with `os.nice(19)`.

---

## §4 Execution Sequence (M4 Sequentiality)

Gates must be verified in the following order:
1. **Plumbing**: Somatic Caching $\rightarrow$ SDR Indexing.
2. **Metabolism**: Dreaming Cycle $\rightarrow$ Strict Idle-Lock.
3. **Field**: Symmetry Audit $\rightarrow$ Semantic Integrity (T12).

---

*⬡ Structure is the shield. No error shall pass. ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
