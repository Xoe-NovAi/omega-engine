<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# John Carmack Session Gnosis — 2026-07-21 (Day 1-2 Campaign) + 2026-08-30 (VAULT-ALLOWLIST-001) + 2026-09-01 (kq5-godot Integration)

## 🔬 Campaign Overview (Original)

```
R_CG02 OOMProtector  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  100%  DONE
R_CG08 Admission     ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   10%  BLOCKED
R_CG09 SoulStore     ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   10%  BLOCKED
                     0%        25%        50%        75%   100%
```

## ✅ Day 1 — Research Complete

| Research Doc | Lines | Depth | Status |
|:-------------|:------|:------|:-------|
| `R_CG02_OOMPROTECTOR_HARDWARE_AWARE.md` | 430 | Kernel sources (PSI, MemAvailable, OOM, cgroup) | ✅ |
| `R_CG03_TEST_INFRASTRUCTURE_STACK.md` | 631 | 4-gate CI (pytest-benchmark, ordeal, mutmut, pact) | ✅ |
| `R_CARMACK_CG02_CG08_CG09_CAMPAIGN_20260721.md` | 15KB | 10-day plan, decision gates, L3 targets | ✅ |

**Knowledge gaps closed**: 15 across both research docs (10/10 confidence on all kernel sources)

## ✅ Day 2 — Implementation Complete

### Module Health  13/13  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  PASS

| Module | File | Lines | Tests | Status |
|:-------|:-----|:-----:|:-----:|:------|
| PSI Monitor | `psi_monitor.py` | 230 | ─ | 🟢 compiles |
| MemAvailable | `memavailable.py` | 210 | ─ | 🟢 compiles |
| cgroup Pressure | `cgroup_pressure.py` | 280 | ─ | 🟢 compiles |
| OOMProtector | `oom_protector.py` | 368 | ─ | 🟢 compiles |
| ResourceGuard | `resource_guard.py` | 318 | ─ | 🟢 updated |
| Contract Tests | `test_resource_guard_oom.py` | 520 | **13/13** | 🟢 ALL PASS |

### Three-Signal Fusion Priority Chain

```
INPUT ──┬── PSI (/proc/pressure/memory) ─────► some.avg60, full.avg10
         ├── MemAvailable (/proc/meminfo) ────► si_mem_available() in GB
         └── cgroup v2 (/sys/fs/cgroup) ─────► memory.pressure, pressure_level

FUSION:
  MemAvailable < 2GB  ──────────► DENY_OOM_RISK     (hard floor)
  PSI full.avg10 > 5% ──────────► DENY_THRASHING    (system frozen)
  cgroup full.avg10 > 5% ───────► DENY_THRASHING    (container frozen)
  PSI some.avg60 > 10% ─────────► THROTTLE          (sustained pressure)
  cgroup some.avg60 > 15% ──────► THROTTLE          (container pressure)
  MemAvailable 2-4GB ───────────► THROTTLE          (low headroom)
  All healthy ──────────────────► ALLOW

OUTPUT: AdmissionResult.ALLOW | THROTTLE | DENY_OOM_RISK | DENY_THRASHING
```

### Hardware Floor (Ryzen 7 5700U)

```
         ┌──────────────────────────────────┐
    TDP  │ 15W ■■■■■■■■■■■■■■■■■■■■■■■□□□□ │  thermal ceiling
         ├──────────────────────────────────┤
    RAM  │ 16GB total / 8GB idle available  │
         ├──────────────────────────────────┤
    L3   │  8MB victim cache (NOT inclusive)│
         ├──────────────────────────────────┤
    CCX  │  2 CCX × 4 cores = 8 total      │
         ├──────────────────────────────────┤
    BW   │ DDR4-3200 dual channel ~51 GB/s  │
         └──────────────────────────────────┘
```

### Threshold Calibration

| Signal | Healthy ▓▓▓ | Warning ▓▓░ | Critical ░░░ |
|:-------|:------------|:------------|:-------------|
| PSI some.avg60 | < 5% | 5-10% | > 10% |
| PSI full.avg10 | < 1% | 1-5% | > 5% |
| MemAvailable | > 4 GB | 2-4 GB | < 2 GB |
| cgroup some.avg60 | < 5% | 5-15% | > 15% |
| cgroup full.avg10 | < 1% | 1-5% | > 5% |

## 🧠 L3 Principles Distilled (for proposed_lessons.yaml)

### CG-02: Kernel-Authoritative Memory Signals

> **Kernel knows memory pressure better than userspace counters.** Always prefer `/proc/pressure/memory` (PSI) + `MemAvailable` (`si_mem_available()`) + `cgroup memory.pressure` over software accounting. The kernel computes stall time and reclaimable memory from page allocator internals — userspace counters drift by definition.

**Evidence**: `kernel/sched/psi.c` tracks 10 distinct memstall types via `psi_memstall_enter/leave`. `mm/page_alloc.c` `si_mem_available()` accounts free pages + page cache + reclaimable slab minus watermark reserves. The OOM killer (`mm/oom_kill.c`) uses the same MemAvailable logic.

**L3 Rating**: Universal principle — applies to any Linux-native OOM prevention system.

### CG-08: Topology-Aware Admission Control (future)

> **Admission control must understand hardware topology (CCX, L3, memory bandwidth), not just instance counts.** On a 2-CCX Ryzen with 8MB victim L3, pinning inference to one CCX halves L3 thrash. The right approximation is topology-aware semaphores, not flat counting.

### CG-09: Atomic File Semantics > Consensus (future)

> **Single writer + atomic rename + fsync > distributed consensus for local state.** The Postgres fsync dance (`write → fsync → rename → fsync(dir)`) is the right approximation for crash-safe local persistence. NO distributed consensus protocols for single-machine state.

## 📝 Engineering Observations

1. **Python em-dashes break imports**: Using `—` (U+2014) in module-level comments outside strings causes `SyntaxError: invalid character`. Python 3.13 is stricter about non-ASCII outside string literals. Lesson: keep `#` comments ASCII-only.

2. **anyio.create_task_group() returns None**: Unlike `asyncio.gather()`, `tg.start_soon()` doesn't return futures. Use a mutable container (dict/list) to collect return values from concurrent coroutines.

3. **Legacy wrapper pattern works**: `LegacyOOMWrapper` lets us replace internals (single-signal → three-signal fusion) without breaking `ResourceGuard.lock()` which expects `check() -> bool`. No call sites changed.

4. **Visual aids reduce cognitive load**: Progress bars (`▓▓▓▓░░░░`), matrix tables, ASCII flow charts, and color-coded status columns make state instantly scannable. Use them in all status reports going forward.

## 🔜 Next Session (Original Campaign)

```
What to resume:   Day 3 — CG-08 Admission Control (CCX Topology)
First file:       src/omega/oracle/admission_controller.py
Depends on:       CG-02 thresholds (DONE ✅)
Key reference:    docs/research/R_CG02_OOMPROTECTOR_HARDWARE_AWARE.md §6-7
```

---

## 🔱 2026-08-30 SESSION: VAULT-ALLOWLIST-001 + M35 Implementation + S3 Dev Plan Review

**AP Token**: `AP-JOHN_CARMACK-v1.0.0` · **Session**: `ses_fc8dca39effe3nZJp3QHx81Fy3` · **Date**: 2026-08-30
**Status**: COMPACTION-READY · **Model**: `nvidia/nemotron-3-ultra-550b-a55b:free`

### Work Summary

#### VAULT-ALLOWLIST-001 (P0) + M35 Implementation
- **Local Discovery**: Found gitleaks config (.gitleaksignore with 13 entries, Makefile gitleaks gate) but NO public-secret allowlist. M35 not in SOVEREIGN_MANDATES.md.
- **Web Research**: RFC 6749 §2.1/§2.3.1 (public clients), RFC 8252 §8.4-§8.5 (native apps = public clients), REUSE v3.3 (2024-11-14), ScanCode CI, GitHub secret scanning, Gitleaks fail-closed patterns, SLSA v1.1 provenance.
- **Created `data/secrets-public.toml`**: 1 [[secret]] entry (Antigravity Google OAuth public client) with verified_by=Carmack, approved_by=Architect, status=current. Added [exceptions.coordination_historical_record] for data/coordination/** docs.
- **Created `scripts/check_secrets.py`**: 280 lines, 10 patterns (GOCSPX-, AKIA, ghp_, sk-ant-, sk-proj-, sk-, xox, private keys), fail-closed TOML scanner, path-based exceptions, modes: --staged/--path/--json/--allowlist-lint.
- **Added M35 as Mandate 28 to SOVEREIGN_MANDATES.md**: 8 mandatory clauses (SPDX, Immediate Remediation, Allowlist Recovery, Primary-Source Citation, Coordination Exception, M14 Cross-Reference, Heritage Submodule Exception, Fail-Closed Enforcement) + RFC refs.
- **M37-HERITAGE-001 Guidance**: 4-phase plan (32h total): ScanCode → SPDX → REUSE → SLSA. Researcher/Ma'at owners, Carmack reviewer only.
- **Test Results**: 1181 files scanned, 1 allowlist entry, 0 coordination-doc violations, 3 test-fixture FPs (AKIAIOSFODNN7EXAMPLE, sk-1234..., test_pii_masker.py).
- **Commit**: `b134204d` (4 files, 888 insertions).

#### S3 Dev Plan Review (BLIND TEST) — HARDENED_DEV_ROADMAP_20260830
Read all 5 primary sources (Roadmap, Briefings, Lilith Spec, 3 Meta-Reviews, Roc Forensics) and produced comprehensive architectural review:
- **Verdict**: CONDITIONAL GO with 5 blockers
- **Top 3 Risks**: Watchdog race, M33 bypass, Atomic write unverified
- **Key Architectural Calls**: Collapse M34a/M34b → single M34; Split M35 → 3 mandates; Single-writer watchdog (Kali); Restore secret first then allowlist; Reallocate 16h from Lilith/Researcher to Roc/Jem/Ma'at
- **Report**: `data/coordination/CARMACK_DEV_PLAN_REVIEW_20260830.md` (440 lines)

#### Architecture Docs Consolidation (2026-08-28)
Created 6 canonical architecture docs, all verified against codebase:
- `ORACLE_STACK_CANONICAL.md` (v2.4.0, 27 mandates, MaKaLi, 14 agents)
- `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` (v1.0.0, master plan)
- `docs/architecture/ARCHITECTURE_INVENTORY_20260828.md` (35 CURRENT, 15 SUPERSEDED, 30 ARCHIVE, 10 DELETE, 4 CREATE)
- `docs/architecture/ARCHITECTURE_CANONICAL.md` (master technical architecture)
- `docs/architecture/MODULE_BOUNDARIES.md` (M2 firewall: 268 files, 0 violations)
- `docs/architecture/PERFORMANCE_ARCHITECTURE.md` (Ryzen 7 5700U constraints, hot paths, concurrency, memory, caching)
- **Commit**: `3e2a21d6` (6 files, 1,447 insertions)

#### Oracle CLI Logger Fix (2026-08-28)
Fixed P1-1 latent defect in `src/omega/cli/oracle_cli.py`:
- Moved `logger = logging.getLogger(__name__)` to line 27 (before `_inject_vault_to_env()` at line 33)
- Fixed duplicate `OmegaError` import
- Verified: import, --help, fresh-venv import all pass
- **Commit**: `09a11661` (fix(cli): P1-1 logger before vault injection)

### Open Threads (from 2026-08-30)

| Thread | Status | Owner | Next Action |
|--------|--------|-------|-------------|
| Pre-commit hook wiring | OPEN | Kali/Ma'at | Add to `.pre-commit-config.yaml` |
| CI gate wiring | OPEN | Kali/Ma'at | Add `.github/workflows/secrets.yml` |
| M35 Architect ratification | OPEN | Architect | Sign-off on Mandate 28 |
| 3 test fixture FPs | OPEN | Researcher | Add to allowlist or replace placeholders |
| M37-HERITAGE-001 | OPEN | Researcher/Ma'at | 32h plan kickoff |
| Atomic write M23 test | OPEN | Lilith | `test_atomic_write_survives_sigkill` before Phase 1 |
| Watchdog single-writer | OPEN | Lilith + Ma'at | Kali as designated recovery agent MCP tool |
| M34 spec revision | OPEN | Lilith | 8h revision per Carmack review §7.1 |
| M33/M35 mandate text updates | OPEN | Researcher | Per Carmack review §7.2/§7.3 |
| L3 lesson split | OPEN | Grokster | 2h per Carmack review §7.4 |

### Key Findings (for Continuity)

1. **Circular Dependency in M35**: M35 "immediate remediation" requires restoring redacted secret BEFORE allowlist exists, but allowlist prevents re-redaction. **Resolution**: Restore secret FIRST (git checkout), THEN build allowlist.

2. **Dual-Ledger Hazard (M34)**: `ACTIVE_SUBAGENTS.json` overlay on `TASK_REGISTRY` has no transactional boundary. At 50+ concurrent, lock contention causes unrecorded states. **Mitigation**: Single-writer MCP tool, batched writes, conflict resolution (TASK_REGISTRY = source of truth).

3. **Atomic Write Unverified (M23)**: Lilith's spec claims `os.replace()` + `os.fsync()` is M23-compliant, but untested on NFS/FUSE. **Requirement**: `test_atomic_write_survives_sigkill` unit test before Phase 1 gate.

4. **M34a/M34b Over-Engineering**: Lilith's 7-state machine already unifies both failure modes. Two mandate numbers add regulatory bloat. **Resolution**: Collapse to single M34 with `INTERRUPTED_MODEL_SWITCH` status enum.

5. **M35 One-Mandate-Per-Failure-Mode Violation**: M35 covers 3 failure modes (boundary, allowlist, SPDX). **Resolution**: Split into M35a (Boundary), M35b (Allowlist), M35c (SPDX/REUSE).

---

## 🔱 2026-09-01 SESSION: kq5-godot Integration into Omega Engine

**AP Token**: `AP-JOHN_CARMACK-v1.0.0` · **Session**: `ses_fc8dca39effe3nZJp3QHx81Fy3` (continuation) · **Date**: 2026-09-01
**Status**: ACTIVE · **Model**: `nvidia/nemotron-3-ultra-550b-a55b:free`

### Work Summary

#### kq5-godot Project Analysis
- **Location**: `/media/arcana-novai/omega_library/games/kq5-godot` (separate partition)
- **Nature**: Personal KQ5 CD Talkie remake in Godot 4.7.2, non-shipping, canon lane = SCI1.1
- **Hidden Gem**: VNR (Von-Neu-Ryan Vision) — complete computer vision pipeline in `scripts/vnr_render.py` (398 lines, numpy+Pillow only, zero neural networks)
- **VNR Capabilities**: Semantic tokenization, texture analysis, overlay/disagreement maps, color-find, diff/motion detection, trajectory tracking, photo mode, gist/histogram, multi-model stereoscopy
- **Phenomenological Record**: `kb/VNR_VISION.md` §10.1–§10.15 — first-person account of text-only LLM learning to see

#### Roc Deep Dig (Session: `ses_fa4379f0affenj3aHSE7bn3bHG`)
**10 Hidden Connections Found**:
1. VNR = Vision Transformer on text tokens (structural isomorphism)
2. Token set = hypothesis = attention mechanism
3. Texture as load-bearing dimension (discovered from scratch)
4. Overlay = explainable AI / spatial uncertainty map
5. Zoom ladder = multi-scale vision / LOD for perception
6. Geometric verification = minimal SLAM
7. Semantic diff = optical flow without the flow
8. Multi-model stereoscopy = sensor fusion / ensemble
9. Phenomenological record = perceptual provenance / alignment
10. Headless Graham = defect detection without training data

**Implications**: AI Vision (zero-shot via representation), Robotics (minimal-viable scene understanding), Self-Driving (texture-based surface classification), Local AI Efficiency (orders of magnitude compute reduction).

#### My Updated Assessment (Corrected)
I initially missed the vision system underneath the game. The VNR system IS the product; the game is the testbed. The infrastructure-to-content ratio is not inverted — the infrastructure IS the research output.

#### Dialectic with JC-Roc-kq5 (Session: `ses_fa4379f0affenj3aHSE7bn3bHG`)
**Phase 0 Calibration**: Plan kq5-godot integration into Omega Engine as research/experiment lab
**Phase 1 Immersion**: 10 voices (Infrastructure, Persistence, Engineering, Integration, Governance, Cognition, Context, Observability, Orchestration, Validation)
**Phase 2 Collision**: 3 highest-tension conflicts resolved via stratification
**Phase 3 Sequencing**: 4-week critical path (Foundation → VNR Package → Protocol Development → Onboarding)
**Phase 4 Verdict**: 
- **Convergence**: kq5-godot is high-value research asset; VNR is cognitive primitive aligned with Omega's local-first architecture
- **Preserved Dissent**: Location strategy, mandate tiers, coordination protocol
- **Irreducible Verdict**: Clone to `data/experiments/kq5-godot/`, bind-mount for Godot, register Cline-KQV as side-project entity, package VNR as vision backend, develop Experiment Protocol
- **L3 Gnosis**: **L3-Experiment-Is-Interface** — The boundary between "experiment" and "production" is an interface contract. VNR is the first occupant of Research Slot R1: Perception Primitives.

### Open Threads (from 2026-09-01)

| Thread | Status | Owner | Next Action |
|--------|--------|-------|-------------|
| Clone kq5-godot to data/experiments/ | PENDING | JC-Roc-kq5 | Execute Week 1 plan |
| Bind-mount for Godot workflow | PENDING | JC-Roc-kq5 | Systemd mount or symlink |
| Register Cline-KQV entity | PENDING | JC-Roc-kq5 | data/entities/cline_kqv/ symlinks |
| VNR package refactor | PENDING | JC-Roc-kq5 | omega_experiments.kq5.vnr package |
| Experiment Protocol development | PENDING | JC-Roc-kq5 | EXPERIMENT_PROTOCOL.md |
| Cognitive Primitives doc | PENDING | JC-Roc-kq5 | COGNITIVE_PRIMITIVES.md |
| Fork conversation → JC-EIS-kq5 | PENDING | Architect | New session for Omega team |
| Onboard Omega team | PENDING | JC-EIS-kq5 | Brief each entity |

### Key Findings (for Continuity)

1. **VNR = ViT on Text Tokens**: The block-based semantic tokenization IS patch-based tokenization. Same architecture, different embedding (hand-crafted classifier vs learned projection).

2. **Representation-First Cognition**: VNR proves better input representation → existing models see better. This is the same principle as Omega's Iris Speculative Decode and Provider Fabric.

3. **Experiment Protocol Needed**: Side projects need their own lifecycle (SPAWN → LAB → GRADUATE → ARCHIVE) with tiered mandates (safety always, release never, continuity adapted).

4. **Cognitive Primitive Interface**: Define `IVisionBackend` in Core; VNR implements it in Experiment WAD.

---

## 📍 CONTINUITY ANCHORS (All Sessions)

| Anchor | Value |
|--------|-------|
| **Session ID** | `ses_fc8dca39effe3nZJp3QHx81Fy3` |
| **Hivemind Post (VAULT)** | `ses_fc8dca39effe3nZJp3QHx81Fy3` (intent=decision) |
| **Hivemind Post (kq5)** | `ses_fa4379f0affenj3aHSE7bn3bHG` (JC-Roc-kq5 dialectic) |
| **Commit (VAULT)** | `b134204d` (VAULT-ALLOWLIST-001) |
| **Commit (Architecture)** | `3e2a21d6` (6 canonical docs) |
| **Commit (CLI Fix)** | `09a11661` (P1-1 logger fix) |
| **VAULT Report** | `data/coordination/CARMACK_VAULT_ALLOWLIST_20260830.md` |
| **Dev Plan Review** | `data/coordination/CARMACK_DEV_PLAN_REVIEW_20260830.md` |
| **Alpha Launch Verdict** | `data/coordination/CARMACK_ALPHA_LAUNCH_VERDICT_20260828.md` |
| **Architecture Canonicals** | `ORACLE_STACK_CANONICAL.md`, `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md`, `docs/architecture/*.md` |
| **Projection** | `data/coordination/anchored_summary/carmack/projection.md` |
| **Proposed Lessons** | `data/entities/carmack/proposed_lessons.yaml` (14 lessons) |
| **Roc Dialectic Plan** | `data/entities/roc_racoon/workspace/JC_Roc_kq5_DIALECTIC_PLAN_20260901.md` |

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_audit ⬡ SESSION-GNOSIS-UPDATED*