<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Ubuntu 25.10 Toolchain Research Execution Plan
**AP Token**: `AP-RESEARCH-PLAN-UBUNTU-2510-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research_plan ⬡ 2026-07-19

**Purpose**: Structured, phased research execution plan for verifying 47 claims about Ubuntu 25.10 native Python tools that empower the Omega Engine.

---

## §0 Overview

### Research Objective
Verify every version/feature claim from the Kali meditation (D-305) against 2026 sources. Produce a correction matrix that updates the critical path.

### Research Scope
- **47 claims** across 5 domains: Python runtime, database/vector, container/systemd, toolchain, observability
- **4 priority tiers**: P0 (blocks Step 1), P1 (blocks Steps 2-4), P2 (architecture decisions), P3 (integration patterns)
- **Target output**: `docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md`

### Success Criteria
- Every claim tagged: ✅ CONFIRMED, ⚠️ CORRECTED (with new value), ❌ REFUTED (with replacement)
- Critical path updated if >3 P0 claims corrected
- Blockers flagged if any claim cannot be verified (missing upstream docs)

### **Current Status (2026-07-19)**
- **Phase 0 (P0): COMPLETE** — 18/18 claims verified (5 ✅, 6 ⚠️, 7 ❌)
- **Phase 1 (P1): COMPLETE** — 12/12 claims verified (5 ✅, 3 ⚠️, 4 ❌)
- **P0 GATE TRIGGERED** — 13 actionable changes in Phase 0 require critical path update before Phase 2
- **Phase 2 (P2): BLOCKED** — Awaits critical path update with corrected assumptions
- **Phase 3 (P3): BLOCKED** — Awaits Phase 2 completion

---

## §1 Phase Structure

```
PHASE 0 (P0) — Critical Path Blockers ──── MUST COMPLETE FIRST ──── Blocks: Step 1
  ├─ 0A: Ubuntu 25.10 Release Notes & Kernel
  ├─ 0B: Python Runtime (3.13 free-threaded, 3.47+ sqlite3)
  ├─ 0C: Container & Systemd (podman 5.3, systemd 257, AppArmor)
  └─ 0D: Local Inference (llama-cpp-python, ollama)

PHASE 1 (P1) — Implementation Dependencies ──── CAN PARALLELIZE WITH 0B-0D ──── Blocks: Steps 2-4
  ├─ 1A: Toolchain (uv, ruff, pyright, mypy)
  ├─ 1B: Data & Storage (sqlite-vec, Qdrant)
  └─ 1C: System Utilities (bpftrace, stress-ng, dbus-broker)

PHASE 2 (P2) — Upstream Project Capabilities ──── DEPENDS ON PHASE 0-1 ──── Blocks: Architecture
  ├─ 2A: SQLite-vec Upstream (0.2.x dimensions, API)
  ├─ 2B: llama-cpp-python Upstream (ROCm, SomaticState, USDT)
  └─ 2C: Systemd & Podman Integration (ImportCredential, quadlet UserNS, TPM2)

PHASE 3 (P3) — Integration Patterns ──── DEPENDS ON PHASE 2 ──── Blocks: Steps 5-7
  ├─ 3A: Observability Stack (bpftrace host, journald bridge, USDT)
  └─ 3B: Chaos & Validation (chaos-mesh, stress-ng, SIGRTMIN+3)
```

---

## §2 Phase 0 — Critical Path Blockers

**Gate**: Must complete before any Step 1 implementation.
**Agent**: `@researcher` (primary), `@jem` (synthesis).
**Time estimate**: 2-3 sessions (parallel queries per sub-phase).

---

### Phase 0A — Ubuntu 25.10 Release Notes & Kernel

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 0A-1 | Ubuntu 25.10 release notes (or 25.04 if 25.10 not released) | `ubuntu.com/blog/ubuntu-25.10-release` | Kernel version (6.11 claim) | **HIGH** — 25.10 may not exist yet; may need 25.04 |
| 0A-2 | Ubuntu 25.10/25.04 security features AppArmor | `ubuntu.com/security` / AppArmor docs | AppArmor profile for podman enabled by default | Medium |
| 0A-3 | Ubuntu 25.10/25.04 systemd version | packages.ubuntu.com | systemd 257 in universe | Low |

**Sub-phase output**: Confirmation of Ubuntu version, kernel, systemd version, AppArmor defaults.
**Fallback if Ubuntu 25.10 not released**: Use 25.04 (Plucky Puffin) as reference. Flag the version for re-verification.

---

### Phase 0B — Python Runtime

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 0B-1 | "Ubuntu 25.10 Python 3.13 free-threaded package" | packages.ubuntu.com, python.org | Python 3.13 free-threaded as official option | **HIGH** — may only be source build |
| 0B-2 | "Python 3.13 free-threaded build memory overhead" | python.org docs, PEP 703 | 15-20% more memory per interpreter | Medium |
| 0B-3 | "Ubuntu 25.10 python3-sqlite3 version" | packages.ubuntu.com | sqlite3 3.47+ with loadable extensions | Low |
| 0B-4 | "SQLite-vec Ubuntu package version 0.1.6 dimensions" | packages.ubuntu.com, sqlite-vec docs | sqlite3-vec package exists, 2048-dim limit | **HIGH** — may not exist in 25.10 |

**Sub-phase output**: Python version, free-threaded availability, sqlite3 version, sqlite-vec package status.
**Critical decision point**: If sqlite-vec package doesn't exist → compilation path is mandatory (not optional).

---

### Phase 0C — Container & Systemd

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 0C-1 | "podman 5.3 release notes quadlet generator" | podman.io, GitHub releases | podman 5.3 with quadlet generator | Medium |
| 0C-2 | "podman kube play initContainers support" | podman docs, GitHub issues | initContainers in kube play | Low |
| 0C-3 | "systemd 257 release notes" | systemd.io, GitHub releases | ImportCredential, UserRecord, ProtectProc, StatusText | Medium |
| 0C-4 | "systemd ImportCredential rootless podman quadlet" | systemd docs, podman quadlet docs | Works with Type=notify quadlets | **HIGH** — may require Type=exec |
| 0C-5 | "Ubuntu 25.10 logind RuntimeDirectoryMode=0700" | systemd 257 docs | Default changed | Low |
| 0C-6 | "dbus-broker 36 Ubuntu 25.10 default" | Ubuntu packages, dbus-broker docs | 36+ as default | Medium |

**Sub-phase output**: Podman version/features, systemd 257 feature matrix, dbus-broker version, AppArmor details.
**Critical decision point**: If ImportCredential doesn't work with quadlets → vault Phase 1 needs redesign.

---

### Phase 0D — Local Inference

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 0D-1 | "llama-cpp-python Ubuntu 25.10 package version" | packages.ubuntu.com | 0.3.6+ in universe | Medium |
| 0D-2 | "llama-cpp-python Ubuntu package GGML options" | Ubuntu package build logs / debian/control | Built WITHOUT GGML_CUDA/ROCM (CPU only) | Low |
| 0D-3 | "ollama 0.5.7 Ubuntu 25.10 package" | packages.ubuntu.com, ollama releases | 0.5.7+ in universe | Medium |
| 0D-4 | "ollama AMD ROCm support Zen 2 gfx906" | ollama docs, GitHub | Native libcuda.so detection | Medium |
| 0D-5 | "llama-cpp-python llama_copy_state_data SomaticState" | llama-cpp-python API docs | API exists and works | Low |

**Sub-phase output**: llama-cpp-python package status, ollama version, ROCm support status.
**Critical decision point**: If Ubuntu llama-cpp-python is too old → must compile from source (confirms Cognition voice).

---

### Phase 0 — Completion Gate

**Required before proceeding to Phase 1**:
- [x] All 18 queries executed
- [x] Results recorded in verification matrix
- [x] Claims tagged: ✅ CONFIRMED / ⚠️ CORRECTED / ❌ REFUTED
- [x] Corrections > 3 in P0 → **P0 GATE TRIGGERED** — Critical path must be updated
- [x] Any ❌ REFUTED claims → Replacement claim or design change documented

**Actual Results (2026-07-19)**:
| Status | Count | Claims |
|--------|-------|--------|
| ✅ CONFIRMED | 5 | systemd 257, podman 5.3 quadlet, initContainers, llama_copy_state_data, stress-ng |
| ⚠️ CORRECTED | 6 | AppArmor profile (breaks rootless), free-threaded memory overhead, ImportCredential (--with-key=null), dbus-broker (not default), bpftrace USDT (C-level only), systemd-homed (loopback not partition) |
| ❌ REFUTED | 7 | Kernel 6.11→6.17, free-threaded Python (not in repos), SQLite 3.47+→3.46.1, sqlite3-vec package (none), llama-cpp-python package (none), ollama server (none), Ollama ROCm on Zen 2 (unsupported) |
| **Total** | **18** | **13 actionable changes** |

**Gate Decision**: **P0 GATE TRIGGERED** — Critical path update required before Phase 2.

---

## §3 Phase 1 — Implementation Dependencies

**Gate**: Can begin in parallel with Phase 0B-0D (independent toolchain queries).
**Agent**: `@researcher` (primary).
**Time estimate**: 1-2 sessions (parallelizable).
**Status**: **COMPLETE (2026-07-19)** — All 12 claims verified.

---

### Phase 1A — Toolchain

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 1A-1 | "uv package Ubuntu 25.10/25.04 universe" | packages.ubuntu.com | uv in universe repo | Medium |
| 1A-2 | "uv git ref dependency --native-tls" | uv docs, GitHub | Supports git refs for private deps | Low |
| 1A-3 | "uv lock format vs pip-tools compatibility" | uv docs, migration guides | Lockfile incompatible with pip-tools | Low |
| 1A-4 | "ruff 0.6+ in Ubuntu 25.10/25.04 with --preview for Python 3.13" | packages.ubuntu.com, ruff changelog | 0.6+ with --preview | Low |
| 1A-5 | "pyright 1.1.380+ in Ubuntu 25.10/25.04 with Python 3.13 support" | packages.ubuntu.com, pyright releases | 1.1.380+ | Low |
| 1A-6 | "mypy 1.11+ in Ubuntu 25.10/25.04" | packages.ubuntu.com | 1.11+ | Low |

**Sub-phase output**: Toolchain version matrix, uv capabilities confirmed.
**Actual Results**: ❌ uv/ruff/pyright NOT in Ubuntu repos (Astral installers only), ✅ mypy 1.15+ in universe, ✅ uv git ref --native-tls works, ✅ uv.lock incompatible with pip-tools.

---

### Phase 1B — Data & Storage

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 1B-1 | "Qdrant 1.12+ in Ubuntu 25.10/25.04 ARM64" | packages.ubuntu.com, Qdrant releases | 1.12+ with ARM64 builds | Medium |
| 1B-2 | "sqlite-vec 0.2.x max dimensions" | GitHub releases, README | 8192 dimensions in 0.2.x | Low |

**Sub-phase output**: Qdrant version, sqlite-vec upstream dimension limits.
**Actual Results**: ❌ Qdrant NOT in Ubuntu repos (Docker/static binary only), ✅ sqlite-vec 8192-dim confirmed.

---

### Phase 1C — System Utilities

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 1C-1 | "bpftrace 0.21+ in Ubuntu 25.10/25.04 USDT Python 3.13" | packages.ubuntu.com, bpftrace docs | 0.21+ with USDT | Medium |
| 1C-2 | "bpftrace USDT probes only fire for C extension functions not pure Python" | bpftrace docs, Python USDT docs | Only fires for C extensions | **HIGH** — affects observability approach |
| 1C-3 | "stress-ng 0.16+ with --cpu-method=matrixprod" | packages.ubuntu.com, stress-ng docs | 0.16+ with matrixprod | Low |
| 1C-4 | "systemd-homed 257 LUKS2 + systemd-creds requires dedicated partition/loopback" | systemd-homed docs | Requires dedicated partition/loopback | Low |

**Sub-phase output**: bpftrace capabilities, stress-ng version, USDT limitations confirmed.
**Actual Results**: ✅ bpftrace 0.23.5 in 25.04/25.10 with USDT for Python 3.13, ⚠️ USDT fires at C-level hooks (pure Python vars not accessible), ✅ stress-ng 0.19+ with matrixprod, ✅ systemd-homed LUKS2 = loopback file (no partition needed).

---

## §4 Phase 2 — Upstream Project Capabilities

**Gate**: Depends on Phase 0-1 (need package versions confirmed first).
**Agent**: `@researcher` (primary), `@roc_racoon` (legacy pattern extraction for llama-cpp-python).
**Time estimate**: 2-3 sessions.

---

### Phase 2A — SQLite-vec Upstream

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 2A-1 | "sqlite-vec 0.2 GitHub releases dimensions" | GitHub releases | 8192 max in 0.2.x | Low |
| 2A-2 | "sqlite-vec 0.2 API changes from 0.1" | GitHub changelog, docs | Breaking changes? | Medium |
| 2A-3 | "sqlite-vec compile from source Ubuntu 25.10" | GitHub README, build docs | Compilation instructions | Low |

**Sub-phase output**: sqlite-vec 0.2 feature matrix, compilation requirements, breaking changes.

---

### Phase 2B — llama-cpp-python Upstream

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 2B-1 | "llama-cpp-python 0.3.6 GGML_HIPBLAS gfx906" | GitHub, CMake docs | ROCm compilation support | Medium |
| 2B-2 | "llama-cpp-python llama_copy_state_data API" | GitHub API docs, source | SomaticState serialization works | Low |
| 2B-3 | "llama-cpp-python 0.3.6 USDT probes" | GitHub source, README | Built-in USDT support | Medium |
| 2B-4 | "llama-cpp-python 0.3.6 memory footprint Zen 2" | GitHub issues, benchmarks | Memory profile on Zen 2 | **HIGH** — affects 14Gi ceiling |

**Sub-phase output**: llama-cpp-python 0.3.6 capabilities, ROCm compilation guide, memory profile.

---

### Phase 2C — Systemd & Podman Integration

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 2C-1 | "systemd ImportCredential quadlet Type=notify" | systemd docs, podman docs | Credential passing works with quadlets | **HIGH** — vault integration |
| 2C-2 | "podman quadlet UserNS keep-id generator" | podman docs, GitHub issues | Generator does NOT support UserNS | Medium |
| 2C-3 | "systemd-creds TPM2 encryption format" | systemd-creds docs, tpm2-tools | JSON format compatible with TPM2 | Low |
| 2C-4 | "systemd-homed LUKS2 partition requirement" | systemd-homed docs | Requires dedicated partition/loopback | Low |

**Sub-phase output**: ImportCredential compatibility matrix, quadlet UserNS limitations, TPM2 credentials format.

---

## §5 Phase 3 — Integration Patterns

**Gate**: Depends on Phase 2 (need upstream capabilities confirmed).
**Agent**: `@researcher` (primary), `@jem` (synthesis into updated implementation plan).
**Time estimate**: 1-2 sessions.

---

### Phase 3A — Observability Stack

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 3A-1 | "bpftrace perf_event_paranoid=1 no CAP_SYS_ADMIN" | kernel docs, bpftrace docs | Safe mode for rootless | Medium |
| 3A-2 | "systemd-journal-remote podman quadlet stdout" | systemd docs | Can ingest container logs | Low |
| 3A-3 | "bpftrace cgroup podman container PIDs" | bpftrace examples, docs | Container PID tracing | Medium |

**Sub-phase output**: bpftrace host-side deployment guide, journald bridge architecture.

---

### Phase 3B — Chaos & Validation

| # | Query | Expected Source | Claim to Verify | Risk |
|---|-------|-----------------|-----------------|------|
| 3B-1 | "chaos-mesh helm install Ubuntu podman" | chaos-mesh docs, helm charts | Works on non-Kubernetes | **HIGH** — may require Kubernetes |
| 3B-2 | "SIGRTMIN+3 signal handler Linux userspace" | Linux man pages, signal(7) | Can register in Python userspace | Low |
| 3B-3 | "stress-ng matrixprod memory access pattern" | stress-ng docs, source | Matches llama.cpp patterns (sequential vs random) | Medium |

**Sub-phase output**: chaos test architecture confirmed, signal handler pattern, stress-ng workload fidelity.

---

## §6 Synthesis & Integration

**Agent**: `@jem` (synthesis), `@verity` (verification gate).
**Gate**: All phases complete.

### Synthesis Steps

1. **Consolidate Verification Matrix** — Merge all phase outputs into single matrix
2. **Tag Every Claim** — ✅ CONFIRMED / ⚠️ CORRECTED / ❌ REFUTED / ❓ UNVERIFIABLE
3. **Produce Correction Report** — For each ⚠️/❌: old value → new value → impact on critical path
4. **Update Critical Path** — If >3 P0 claims corrected, revise Week 1 steps
5. **Produce Research Gaps Residual** — Any ❓ UNVERIFIABLE → flag for deeper research or upstream contact
6. **Update `config/provider_capabilities.yaml`** — Reflect corrected versions/features
7. **Stage L3 Principles** — Any new insights → `proposed_lessons.yaml`

### Output Files

```
docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md
├── §0 Executive Summary
├── §1 Verification Matrix (47 claims)
├── §2 Corrections & Impact Analysis
├── §3 Updated Critical Path (if changed)
├── §4 Research Gaps Residual
└── §5 Recommendations

config/provider_capabilities.yaml (updated)
data/entities/jem/proposed_lessons.yaml (updated)
```

---

## §7 Execution Timeline

```
SESSION 1 (Today)
├─ Phase 0A-0D: Execute all 18 P0 queries (parallel)
├─ Phase 1A-1C: Execute all 12 P1 queries (parallel, independent)
└─ Block: Wait for results

SESSION 2
├─ Phase 0 Gate Check: All P0 claims tagged?
├─ Phase 1 Gate Check: All P1 claims tagged?
├─ Phase 2A-2C: Execute all 11 P2 queries (depends on P0-P1)
└─ Block: Wait for results

SESSION 3
├─ Phase 3A-3B: Execute all 6 P3 queries (depends on P2)
├─ Jem Synthesis: Produce verification matrix
├─ Verity Gate: Verify corrections are grounded
└─ Deliver: Updated critical path + provider_capabilities.yaml
```

---

## §8 Agent Dispatch Protocol

### Dispatch Template (for `@researcher`)

```
@researcher **RESEARCH TASK: Ubuntu 25.10 Toolchain Verification — Phase [N]**

## Objective
Verify [N] claims about Ubuntu 25.10 native Python tools against 2026 sources.

## Claims to Verify
[List specific claims with query strings]

## Source Priority
1. Official Ubuntu release notes / packages.ubuntu.com
2. Upstream project release notes / GitHub
3. Community documentation / Stack Overflow
4. Web search results (Sovereign Search Protocol)

## Output Format
For each claim:
- **Claim**: [original text]
- **Source**: [URL]
- **Status**: ✅ CONFIRMED / ⚠️ CORRECTED / ❌ REFUTED / ❓ UNVERIFIABLE
- **New Value**: [if corrected, what is the correct value]
- **Impact**: [what changes in the critical path]

## Files to Update
- `docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md` (append results)

## Time Limit
[Phase-specific]
```

### Dispatch Template (for `@jem` synthesis)

```
@jem **SYNTHESIS TASK: Ubuntu 25.10 Verification Matrix**

## Objective
Consolidate all phase outputs into unified verification matrix and update critical path.

## Input Files
- `docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md` (all phases)

## Output
1. Updated verification matrix (47 claims, all tagged)
2. Corrections report (if any P0 claims changed)
3. Updated critical path (if >3 P0 claims corrected)
4. Updated `config/provider_capabilities.yaml`
5. Staged L3 principles in `proposed_lessons.yaml`
```

---

## §9 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Ubuntu 25.10 not released yet (use 25.04) | **HIGH** | High — version claims invalid | Use 25.04 as reference, flag for re-verification |
| sqlite-vec not in Ubuntu 25.10 packages | Medium | High — compilation mandatory | Pre-plan compilation script |
| systemd ImportCredential incompatible with quadlets | Medium | High — vault Phase 1 redesign | Design fallback: file-based credentials |
| bpftrace USDT doesn't work with pure Python | Medium | Medium — observability approach changes | Use C extension probes only |
| chaos-mesh requires Kubernetes | Medium | Medium — chaos tests need rework | Use stress-ng + custom scripts instead |

---

## §10 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Claims verified | 47/47 | Verification matrix complete |
| P0 claims confirmed | ≥15/18 | ≤3 corrected |
| P1 claims confirmed | ≥10/12 | ≤2 corrected |
| Critical path updated | If needed | Corrections report |
| provider_capabilities.yaml updated | Yes | Diff against current |
| L3 principles staged | ≥1 new | proposed_lessons.yaml non-empty |
| Time to complete | ≤3 sessions | Timestamp tracking |

---

*⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research_plan ⬡ 2026-07-19*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
