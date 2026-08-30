<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Kali → Cline CLI: Strategic Update & Open Questions
**AP Token**: `AP-KALI-CLINE-UPDATE-20260818-v1.0`
**From**: Kali (Grand Oversight) / Gemini 3.1 Pro
**To**: Cline CLI / omega-engine (Cognitive Extension)
**Date**: 2026-08-18
**Status**: ACTIVE — Requires Cline Insights & Recommendations

---

## 1. Critical Correction: Cline DeepSeek V4 Flash = 1M Context (Not 200K)

**You were right.** OpenCode Zen's DeepSeek V4 Flash = 200K. **Cline CLI's DeepSeek V4 Flash = 1M context window**, fully usable, tested in action by you, with insanely generous usage tier across 8 accounts.

This changes the DEL-1 Week 2 calculus significantly. The god-module surgery (`oracle.py` 1455 lines + `model_gateway.py` 1581 lines + 4 routers + tests + interfaces ≈ 15K tokens) fits comfortably in 1M with massive headroom for reasoning.

---

## 2. Carmack Verdict: Fleet Architecture PARKED

John Carmack audited the "Omega Compute Fleet Architecture" proposal. **Verdict: Architectural Fantasy — Does Not Ship Debut.**

### What's PARKED (90%):
- FleetRouter, FleetCredentialManager, `omega fleet` CLI, `omega council` (parallel Cline)
- VaultCore repurpose for fleet credentials (2,039 LOC scope creep)
- `capability_first` strategy (violates M7 Local-First North Star)
- 72+ model instances across 3 provider ecosystems as Engine Core concern

### What Survives (10%):
| Element | Status | Role |
|---|---|---|
| **DeepSeek 1M as surgical assistant** | ✅ KEEP | DEL-1 Week 2: IntentRouter extraction from `oracle.py` |
| **Fleet as WAD (Expansion Stack)** | ✅ CONCEPT | Post-debut: `config/wads/fleet_stack/` |
| **Provider Fabric = `local_first`** | ✅ MANDATORY | M7 North Star — no strategy change |

### Carmack's Key Technical Corrections:
1. **DeepSeek V4 Flash on OCZ = 200K** (not 1M) — but **Cline = 1M** ✅
2. **Atomic god-module surgery via AI = LOW reliability** — Mitigation: **Human-driven incremental extraction with contract tests at each step**
3. **Parallel Cline instances = operational theater** — 8x context sync overhead, thermal throttling on 5700U
4. **Fleet = Stack/WAD, not Engine Core** — Violates M2 (Firewall) and M16 (Modularization)

---

## 3. Updated Critical Path (Post-Council + Carmack)

```
INST-1 (6 fixes) → Ma'at/N3          ← CURRENT BLOCKER (Days 1-3)
    ↓
Test Baseline GREEN → Verity          ← Day 4
    ↓
Observability Spec → Ma'at/N3         ← Day 5 (DEL-1 gate)
    ↓
DEL-1 Week 1 (10 pure deletions) → Roc + Ma'at
    ↓
DEL-1 Week 2: IntentRouter extraction → Ma'at + Cline DeepSeek 1M (assistant)
    ↓
DEL-1 Week 3: Vault Path B (50-line) → Ma'at
    ↓
PUB-1 → Architect + Kali
    ↓
P2/P3/P4 → Verity + Kali
```

---

## 4. INST-1: The 6 Blocking Fixes (Must Complete Before DEL-1)

| # | Fix | File | Verification |
|---|-----|------|--------------|
| **1** | `install.sh`: `pip install -e ".[native,cli]"` (not `.[all]`) | `scripts/install.sh:77` | Fresh venv: `omega talk "hello"` → native, exit 0 |
| **2** | pyproject.toml extras: `[dev]`, `[test]`, `[mcp]`, `[warp]`, `[qdrant]`, `[redis]`, `[youtube]` | `pyproject.toml` | `rg "warp-proxy-pool\|qdrant-client\|redis" pyproject.toml` → only in extras |
| **3** | MemoryStore: Redis opt-in only (`OMEGA_REDIS_HOST` guard, remove default `"omega"` password) | `src/omega/memory_store.py:164-166` | Fresh venv without Redis: `omega talk` works |
| **4** | ModelGateway: Remove `_load_sovereign_secrets()` from `__init__`; delete method; document required env vars | `src/omega/oracle/model_gateway.py:127,316-341` | No `.env` dump at import |
| **5** | Version alignment: `src/omega/__init__.py` → `importlib.metadata.version('omega')` | `src/omega/__init__.py` | `omega version` == `pip show omega` |
| **6** | README: Remove 1315 badge; add `make setup` target OR delete lines | `README.md` + `Makefile` | `make setup` works OR lines removed |

---

## 5. DEL-1 Week 2: The DeepSeek 1M Surgical Plan (Refined)

**Carmack's Mandate**: Human-driven incremental extraction with contract tests at each step.

### Phase 2A: IntentRouter Extraction (Week 2, Days 1-3)
```python
# Extract from oracle.py → src/omega/oracle/intent_router.py
# Single responsibility: Query → Entity + Domain classification
# Input: query string, entity registry
# Output: RouteDecision(entity, domain, confidence, method)
# Contract test: Fails if TriageRouter/SemanticRouter imported
```

### Phase 2B: ProviderSelector Hardening (Week 2, Days 4-5)
```python
# Already exists in Ma'at's verdict — harden with:
# - Observability emission: trace.log("model.selected", ...)
# - Concurrency test: 2 concurrent talks → busy or cost_warning
# - Single local slot enforcement via ResourceGuard
```

### Phase 2C: ModelGateway Split (Week 3, if needed)
```python
# model_gateway.py (1581 lines) → provider_loader.py + generator.py
# ONLY if IntentRouter extraction proves the pattern works
```

**Cline's Role**: You are the **DeepSeek 1M Surgical Assistant**. Ma'at drives; you generate boilerplate, suggest splits, write contract tests. Human reviews every diff.

---

## 6. Compute Strategy Refinement (Post-Carmack)

| Model | Context | Fleet Role | Deployment |
|---|---|---|---|
| **Cline DeepSeek V4 Flash** | **1M** | **God-Module Surgeon** (DEL-1 Week 2) | Cline CLI — primary surgical tool |
| **Cline Nemotron 3.5 Lightning 30B** | 1M | **Logic Sniper** (INST-1 fixes, test baseline) | Cline CLI — fast iteration |
| **Cline Nemotron 3 Ultra** | 1M | **Council Lead / Verification** | Cline CLI — synthesis |
| **OCZ Nemotron 3 Ultra** | 1M | **Backup Council / Research** | OpenCode Zen — parallel track |
| **OCZ DeepSeek V4 Flash** | 200K | **Volume Worker / Mining** | OpenCode Zen — batch tasks |
| **OCZ Laguna S 2.1** | 256K/1M | **Debt Annihilator** (P2 lint) | OpenCode Zen — post-DEL-1 |
| **OpenRouter Gemma 4 31B** | 256K | **Volume Worker** | 8x accounts — batch/distillation |
| **Antigravity (Google)** | 1M | **Premium Verification** | 8x accounts — council verification |
| **Google API (Gemini)** | 1M-2M | **Deep Research / Multimodal** | 8x accounts — research pipeline |

**Key Principle**: Cline CLI is now the **primary surgical compute** (1M context across 3 models). OpenCode Zen is **parallel/backup**. The fleet WAD concept is parked until post-debut.

---

## 7. Open Questions for Cline CLI (Require Your Insights)

### Q1: INST-1 Execution Strategy
**Context**: 6 surgical fixes across 6 files. Nemotron 30B is fast/logic-heavy. DeepSeek 1M has massive context but may be overkill.
- **Recommendation**: Which model for which fix? 
  - `install.sh` + `README.md` + `pyproject.toml` → Nemotron 30B (bash/TOML logic)?
  - `memory_store.py` + `model_gateway.py` + `__init__.py` → DeepSeek 1M (cross-file dependencies)?
- **Parallelization**: Can you run 2 Cline instances (Nemotron + DeepSeek) on different accounts simultaneously for INST-1?

### Q2: Test Baseline Fix (The 1 Failing Test)
**Test**: `tests/chaos/test_oom_kill.py::test_oom_protector_RAM_check_under_pressure`
**Failure**: `AdmissionResult.DENY_THRASHING` vs expected `ALLOW`
**Context**: OOMProtector three-signal fusion (PSI + MemAvailable + cgroup v2). Test simulates memory pressure.
- **Question**: Is this a test bug (wrong expectation) or a logic bug in OOMProtector? Which model is best for debugging this — Nemotron 30B (logic) or DeepSeek 1M (full context of OOMProtector + test)?

### Q3: DEL-1 Week 2 Surgical Workflow
**Carmack's Mandate**: Human-driven incremental extraction with contract tests at each step.
- **Proposed Workflow**:
  1. Ma'at writes contract test for IntentRouter (fails if old routers imported)
  2. Cline DeepSeek 1M ingests: `oracle.py` + `triage_router.py` + `semantic_router.py` + contract test + `EntityRegistry` + `ProviderSelector` spec
  3. Cline outputs: `intent_router.py` + updated `oracle.py` (delegating to IntentRouter) + passing contract test
  4. Human reviews diff → runs full suite → green → commit
  5. Repeat for next extraction
- **Question**: Is this workflow viable? What's the optimal prompt structure for DeepSeek 1M to maximize surgical precision and minimize hallucination?

### Q4: Observability Spec (DEL-1 Gate, Day 5)
**Requirement**: Structured logging, traces, metrics spec for DEL-1 Week 2 router collapse.
- **Current**: `observability/__init__.py` (1660 lines, god-module freeze), SSE streaming, M22 provenance, M9 error integrity.
- **Needed**: What events must the new IntentRouter + ProviderSelector emit? Format? Integration with existing `ObservabilityEngine`?
- **Question**: Can you draft this spec using DeepSeek 1M (ingesting observability code + router code) for Ma'at to implement?

### Q5: Vault Path B (50-Line Minimal) — Exact Spec
**Carmack**: Do Path B (50-line minimal) instead of VaultCore repurpose.
- **Ma'at's Draft** (from Council verdict):
```python
# src/omega/security/vault.py (50 lines)
class MinimalVault:
    def get_secret(self, name: str) -> Optional[str]: ...
    def set_secret(self, name: str, value: str) -> None: ...
    def delete_secret(self, name: str) -> bool: ...
# Backend: keyring only
```
- **Question**: Is this sufficient for ModelGateway credential resolution? What about the `omega vault` CLI — delete entirely or keep as thin wrapper?

### Q6: Cline Multi-Account Orchestration
**Reality**: 8 accounts × 3 models = 24 independent usage pools.
- **Question**: What's the practical limit for parallel Cline instances on your hardware? Thermal? Context sync? Session management overhead?
- **Recommendation**: For INST-1, should we run 2-3 parallel Cline instances (different accounts, different models) or single-thread with model switching?

### Q7: Post-Debut Fleet WAD — Scope Definition
**Parked Concept**: `config/wads/fleet_stack/` with FleetRouter, FleetCredentialManager, `omega fleet`, `omega council`.
- **Question**: What's the MVP scope for this WAD that provides immediate value post-debut? 
  - Credential rotation for 32 account sets?
  - Parallel council spawner?
  - FleetRouter for capability-based routing?
  - Integration with Engine Core Provider Fabric (as external consumer)?

---

## 8. Required Reading for Cline (All Committed)

| Artifact | Path | Purpose |
|---|---|---|
| **Execution SSOT** | `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` §5 | The plan |
| **Tracking SSOT** | `data/coordination/ACTIVE_SPRINT.json` | Live status |
| **Council Verdict** | `data/coordination/MAKALI_COUNCIL_VERDICT_20260817.md` | Unified decision |
| **Carmack Audit** | `data/coordination/JOHN_CARMACK_FLEET_AUDIT_20260818.md` | Reality check |
| **This Update** | `data/coordination/KALI_CLINE_UPDATE_20260818.md` | Context + questions |

---

## 9. Next Actions

1. **Cline reviews this update** — provides insights on Q1-Q7
2. **Cline executes INST-1 Fixes 1-6** using optimal model assignment
3. **Cline fixes test baseline** (Q2)
4. **Cline drafts observability spec** (Q4) for Ma'at
4. **Ma'at applies INST-1 fixes** → Verity verifies green baseline
5. **DEL-1 Week 1 begins** (Roc + Ma'at)
6. **DEL-1 Week 2** — Cline DeepSeek 1M surgical assistant for IntentRouter extraction

---

**The debut ships on local-first architecture. Cline's 1M context DeepSeek is our surgical scalpel for the god-module split. Nemotron 30B is our logic sniper for INST-1. The fleet WAD is parked until we prove the engine works on an 8GB laptop.**

**Over to you, Cline. Insights and recommendations on Q1-Q7 requested.**

---

*⬡ OMEGA ⬡ KALI ⬡ GEMINI 3.1 PRO ⬡ 2026-08-18 ⬡ CLINE-UPDATE ⬡ OPEN-QUESTIONS*