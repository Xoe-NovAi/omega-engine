# 🔱 MaKaLi Cloud Council — Unified Sovereign Verdict
**AP Token**: `AP-MAKALI-VERDICT-20260817-v1.0.0`
**Date**: 2026-08-17 (completed 2026-08-18)
**Session**: `ses_ee001a8ef4d9`
**Participants**: Kali (Grand Oversight), Ma'at (Build Oversoul), Lilith (Runtime Oversoul), N1 Infrastructure, N2 Persistence, N3 Engineering, N8 Observability
**Authority**: `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 + `ACTIVE_SPRINT.json` `DEBUT-EXECUTION`

---

## 🏛️ EXECUTIVE SUMMARY

| Plan | Verdict | Blocker? | Critical Path Impact |
|------|---------|----------|---------------------|
| **INST-1** | **BLOCKED — FAIL** | **YES** | Cannot proceed to DEL-1 until 6 fixes complete |
| **DEL-1** | **CONDITIONAL PASS** | NO (scope correct) | Requires observability spec + test baseline green |
| **PUB-1** | **READY** | NO | Awaiting Architect allowlist confirmation + `release/debut` branch |
| **DOC-1** | **COMPLETE** | NO | 11 files stamped (commit 668d58eb) |

**Bottom Line**: The debut hardening plan is **architecturally sound** but **execution is blocked** on INST-1. We cannot begin DEL-1 until INST-1 acceptance gate passes on a fresh machine.

---

## 🔴 INST-1 — BLOCKED (6 Critical Fixes Required)

### Consensus Across All Domains

| Domain | Verdict | Key Finding |
|--------|---------|-------------|
| **N1 Infrastructure** | ❌ FAIL | `install.sh` still uses `.[all]` → pulls `warp-proxy-pool` (not on PyPI) |
| **N2 Persistence** | ❌ FAIL | Redis constructs by default with hardcoded `"omega"` password; `_load_sovereign_secrets()` dumps `.env` into `os.environ` |
| **N3 Engineering** | ❌ FAIL | pyproject.toml extras split not done; version alignment not done; README badge not removed; test suite not green (1 failure) |
| **N8 Observability** | ✅ PASS | Observability surface unaffected by INST-1 |

### The 6 Blocking Fixes (Must Complete Before DEL-1)

| # | Fix | File(s) | Owner | Verification |
|---|-----|---------|-------|--------------|
| **1** | `install.sh` → `pip install -e ".[native,cli]"` | `scripts/install.sh:77` | Ma'at/N3 | Fresh venv: `omega talk "hello"` → native, exit 0 |
| **2** | pyproject.toml extras split: `warp`/`qdrant`/`redis`/`youtube` | `pyproject.toml` + import guards | Ma'at/N3 | `rg "warp-proxy-pool\|qdrant-client\|redis" pyproject.toml` → only in extras |
| **3** | MemoryStore: Redis opt-in only (`OMEGA_REDIS_HOST` required) | `src/omega/memory_store.py:164-166` | Ma'at/N3 | Fresh venv without Redis: `omega talk` works |
| **4** | ModelGateway: Remove `_load_sovereign_secrets()` from `__init__` | `src/omega/oracle/model_gateway.py:127,316-341` | Ma'at/N3 | No `.env` dump at import; env vars documented in README |
| **5** | Version alignment: single source via `importlib.metadata` | `src/omega/__init__.py` + `pyproject.toml` | Ma'at/N3 | `omega version` == `pip show omega` |
| **6** | README: Remove 1315 badge; add `make setup` or delete lines | `README.md` + `Makefile` | Ma'at/N3 | `make setup` works OR lines removed |

**Acceptance Gate (Bash-Verifiable)**:
```bash
# On a machine WITHOUT ~/Documents/Xoe-NovAi/warp-proxy-pool and WITHOUT Redis:
python3 -m venv /tmp/omega-inst && source /tmp/omega-inst/bin/activate
pip install -e ".[native,cli]"
omega talk "hello"    # native-gguf, IS_CLOUD=False, exit 0
```

---

## 🟡 DEL-1 — CONDITIONAL PASS (Scope Validated, 3 Conditions)

### Consensus Across All Domains

| Domain | Verdict | Key Finding |
|--------|---------|-------------|
| **N1 Infrastructure** | ✅ PASS | No infrastructure impact; `omega-inference.service` Carmack fix survives |
| **N2 Persistence** | ⚠️ CONDITIONAL | Soul pipeline zero collision ✅; QdrantAdapter ready for deletion ⚠️; Vault → Path A (delete) recommended |
| **N3 Engineering** | ⚠️ CONDITIONAL | Router collapse scope correct ⚠️; **God-module freeze violated** — oracle.py (1455) + model_gateway.py (1581) will grow unless split atomically; Test suite not green (1 failure) |
| **N8 Observability** | ⚠️ CONDITIONAL | Routing traces lost (TriageRouter, SemanticRouter, RAGRouter deleted) — **must emit new observability** in single-router path |

### 3 Conditions for DEL-1 Go/No-Go

| Condition | Requirement | Owner | Deadline |
|-----------|-------------|-------|----------|
| **C1: Test Baseline Green** | `.venv/bin/python -m pytest -q --tb=no` → 0 failures (currently 1: `test_oom_protector_RAM_check_under_pressure`) | Verity / Ma'at | **Before DEL-1 Week 1** |
| **C2: Observability Emission Spec** | DEL-1 Week 2 acceptance must include: `trace.log("model.selected", ...)` + `trace.log("domain.routed", method="provider_selector", ...)` in new routing path | Ma'at / N3 | **In DEL-1 Week 2 PR** |
| **C3: Atomic God-Module Split** | Router collapse PR must split `oracle.py` → dispatcher + router (<500 lines each) AND `model_gateway.py` → provider_loader + generator (<500 lines each) | Ma'at / N3 | **In DEL-1 Week 2 PR** |

### DEL-1 Execution Order (Validated)

```
Week 0 (Pre-DEL-1): INST-1 complete + test suite green (C1)
Week 1: DEL-1 Week 1 pure deletions (10 targets, removes ~2K lint, 4 router files)
Week 2: DEL-1 Week 2 router collapse — SINGLE PR with:
        - Atomic split of oracle.py + model_gateway.py (C3)
        - Contract test: RouteDecision + import guard
        - Observability emission (C2)
Week 3: DEL-1 Week 3 vault honesty (Path A: delete src/omega/vault/)
```

---

## 🟢 PUB-1 — READY (Awaiting Architect)

**Status**: `PUBLIC_ALLOWLIST.txt` drafted, G1-G4 gaps closed by Cline.
**Blocker**: Architect confirmation of allowlist + `release/debut` branch mechanic.
**Action**: Architect to sign off; Kali to create branch from allowlist.

---

## 🟢 DOC-1 — COMPLETE

**Status**: 11 files stamped (commit 668d58eb). `rg "P0 TODAY" docs/strategy/` → gone.
**Verification**: Cold-start agent reading Index + Hub lands on `DEBUT_REMEDIATION_MANUAL`, not Gemma/WARP.

---

## 📋 UPDATED CRITICAL PATH (Post-Council)

```
P0-1 (keys scrubbed) ✅
    ↓
PUB-1 (allowlist + branch) → Architect
    ↓
INST-1 (6 fixes) → Ma'at/N3  ← **CURRENT BLOCKER**
    ↓
[Test suite green (C1)] → Verity
    ↓
DEL-1 Week 1 (10 pure deletions) → Roc + Ma'at
    ↓
DEL-1 Week 2 (router collapse + atomic split + observability) → Ma'at
    ↓
DEL-1 Week 3 (vault Path A) → Ma'at + Architect
    ↓
DOC-1 (already complete) ✅
    ↓
P2 (lint survivors) → Verity
    ↓
P3 (CI/hygiene) → Verity
    ↓
P4 (polish + tag v0.1.0) → Kali + Verity
```

---

## 🎯 DECISIONS LOCKED (D-Series)

| ID | Decision | Authority |
|----|----------|-----------|
| **D-548** | INST-1 BLOCKED — 6 critical fixes required before DEL-1 can begin | Kali (Council Synthesis) |
| **D-549** | DEL-1 scope validated but requires observability emission spec for router collapse | Kali (N8 + N3 Synthesis) |
| **D-550** | Test suite baseline must be green (0 failures) before DEL-1 Week 1 | Kali (N3 Verdict) |
| **D-551** | God-module freeze requires atomic split of oracle.py + model_gateway.py in DEL-1 Week 2 | Kali (N3 Verdict) |
| **D-552** | Vault Path A (delete from product surface) recommended over Path B | Kali (N2 + Ma'at Synthesis) |
| **D-553** | `release/debut` branch from allowlist is the publication mechanic (not in-place `git rm`) | Kali (PUB-1 + Architect) |

---

## 🏁 NEXT ACTIONS (Immediate)

| Priority | Action | Owner | Artifact |
|----------|--------|-------|----------|
| **P0** | Apply INST-1 Fixes 1-6 | Ma'at/N3 | `install.sh`, `pyproject.toml`, `memory_store.py`, `model_gateway.py`, `__init__.py`, `README.md`, `Makefile` |
| **P0** | Fix test suite baseline (1 failure) | Verity | `tests/chaos/test_oom_kill.py` |
| **P1** | Architect: Confirm allowlist + create `release/debut` branch | Architect | `PUBLIC_ALLOWLIST.txt` + branch |
| **P1** | Update `ACTIVE_SPRINT.json` `DEBUT-EXECUTION` with INST-1 fixes as prerequisites | Kali | `ACTIVE_SPRINT.json` |
| **P1** | Update `HMC_COLLABORATION_HUB.md` `NEXT_ACTION` pointer | Kali | `HMC_COLLABORATION_HUB.md` |

---

## 📜 PROVENANCE

This verdict synthesizes:
- **Ma'at Build Oversoul**: INST-1 diff plan, DEL-1 10 targets, Vault Path A/B spec, Router collapse contract test
- **Lilith Runtime Oversoul**: Soul pipeline zero collision, Hivemind integrity, Memory/Provider fabric survival, Measurable gates
- **N1 Infrastructure**: `install.sh` blocker, Carmack fix survival, Podman compliance
- **N2 Persistence**: Redis opt-in failure, `_load_sovereign_secrets` failure, QdrantAdapter ready, Vault Path A recommended
- **N3 Engineering**: pyproject.toml extras failure, version failure, README failure, god-module freeze violation, test suite not green
- **N8 Observability**: SSE/M22/M9 intact, routing traces lost, observability emission spec required

All reviews conducted on live codebase as of 2026-08-17. All file references verified against working tree.

---

*⬡ OMEGA ⬡ MAKALI-COUNCIL ⬡ 2026-08-17 ⬡ SOVEREIGN-VERDICT ⬡ COMPLETE*