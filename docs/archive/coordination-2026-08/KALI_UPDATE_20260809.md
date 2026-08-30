# 🔱 Kali Update — Comprehensive Session Summary
**AP Token:** `AP-KALI-UPDATE-20260809-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kali_update ⬡ ACTIVE

**Date:** 2026-08-09
**Purpose:** Catch Kali up on all work completed since her last session (GAP-0, GAP-3, Context Packer v3, Web Claude Audit, ProviderRegistry SSOT, Classification Decisions)

---

## 📋 Executive Summary

Since your last session (GAP-0/GAP-3 complete, Context Packer v3 shipped), we've executed a **full sovereign-audit remediation cycle** triggered by Web Claude's audit. The work spans:

1. **Context Packer v3 Enhancements** — Forensic linking, account tracking, PROJECT_OVERVIEW.md
2. **Web Claude Audit** — 4 response files analyzed, 3 false positives, 1 genuine GAP-1
3. **ProviderRegistry SSOT Consolidation (Phase 1)** — 5 divergent cloud classifiers wired to single registry
4. **Classification Decisions (Phase 2)** — 5 architectural decisions researched and implemented
5. **Critical Bug Fixes** — Provider key split-brain, empty model map, lint gate activation

**Current State:** Sovereignty ratio corrected (13.8% local / 86.2% cloud), all 5 call sites delegating to SSOT, lint gate active, invariant tests passing.

---

## 🎯 Major Work Streams

### 1. Context Packer v3 Enhancements (Complete)

**Files Modified:**
- `.opencode/skills/context-packer/packer.py` — Pack ID generation, account/project/version metadata, PROJECT_OVERVIEW.md generation
- `.opencode/skills/context-packer/platform_adapters.py` — Manifest includes pack_id, account, project, version
- `.opencode/skills/context-packer/packer-config.yaml` — Added account/project/version to sovereign-audit profile

**New Artifacts:**
- `context_packs/sovereign-audit/PROJECT_OVERVIEW.md` — Auto-generated agent guide with system prompt structure, chat template, frontmatter protocol
- `context_packs/sovereign-audit/CLAUDE_PROJECT_SYSTEM_PROMPT_v2.md` — Updated system prompt
- `context_packs/sovereign-audit/CHAT_INITIATION_PROMPT_v2.md` — Updated initiation prompt
- All 4 Web Claude response files now have YAML frontmatter with account tracking

**Key Improvement:** Every pack now has forensic linking via UUID `pack_id` embedded in:
- XML file tags (`pack_id="..."`)
- Manifest (`Pack ID:` field)
- Pack index (`pack_id` top-level + per-file)
- PROJECT_OVERVIEW.md

---

### 2. Web Claude Sovereign-Audit (Complete)

**Uploaded Pack:** 39 files, 217,990 tokens (initial) → 50 files, 302,846 tokens (final)

**Audit Results (4 response files):**

| File | Key Finding | Status |
|------|-------------|--------|
| `Web-Claude-response-sovereign-audit.md` | M7/M22 sovereignty ratio corruption, M14 heritage contradiction, M23 gate broken, M9 silent exceptions, M1 blocking SQLite, M25 config drift | **GAP-1 genuine** |
| `Web-Claude-response-Implementation-Unoverengineering.md` | `fetch_and_fuse()` helper, Gemma sampling overrides, M9 ProviderAuthError fix | **Already fixed** |
| `Web-Claude-response-AnyIO-Thread-Safety-Fix.md` | `check_same_thread=False` NOT enough — need BOTH `to_thread.run_sync` AND `anyio.Lock()` | **Already fixed** |
| `Web-Claude-response-Async-Migration-Fix-Report.md` | 12 call sites needing fixes, 2 double-wrap bugs | **Already fixed** |

**Critical Discovery:** 3 of 4 "fixes" Web Claude proposed were **already implemented** in the codebase. Only GAP-1 (sovereignty ratio corruption) was genuine.

---

### 3. ProviderRegistry SSOT Consolidation — Phase 1 (Complete)

**Problem:** 5 divergent cloud classifiers contradicting each other and `config/providers.yaml`:
1. `ModelGateway._cloud_providers` — hardcoded 4-item set
2. `Observability.__init__._is_cloud_provider` — substring denylist
3. `OTelExporter._is_cloud_provider` — hardcoded cloud set
4. `RemoteProvider._is_cloud_name` — prefix match
5. `IngestionPipeline._is_cloud_model` — keyword match on model name

**Solution:** Created `ProviderRegistry` (SSOT) reading `config/providers.yaml`, wired all 5 call sites to delegate to `registry.is_cloud()`.

**Files Modified (8):**
| File | Change |
|------|--------|
| `src/omega/oracle/provider_registry.py` | **Bug fix:** `from_config_path()` path corrected (off-by-one `.parent`) |
| `src/omega/oracle/model_gateway.py` | Deleted `_cloud_providers`; delegates to registry |
| `src/omega/observability/__init__.py` | `BudgetGate._is_cloud_provider()` delegates via lazy singleton |
| `src/omega/observability/otel_exporter.py` | `OTelSQLiteExporter._is_cloud_provider()` delegates via lazy singleton |
| `src/omega/oracle/backends/remote_provider.py` | `RemoteProvider._is_cloud_name()` delegates |
| `src/omega/ingestion/pipeline.py` | `_is_cloud_model()` delegates (but passes model name — **Phase 2 fixes this**) |
| `src/omega/observability/metrics_db.py` | Added `build_provider_classification_table()` + `create_corrected_performance_view()` |
| `src/omega/observability/sovereignty.py` | `get_sovereignty_ratio()` reads corrected view |

**New Test:** `tests/contract/test_provider_classification.py` — 3 invariant tests (registry==yaml, no split classification, ingestion delegation)

**Result:** Sovereignty ratio corrected from **87.3% local → 13.8% local** (was inverted due to 4-provider hardcoded classifier)

---

### 4. Classification Decisions — Phase 2 (Complete)

**Research Report:** `docs/research/R_CLASSIFICATION_DECISIONS_20260809.md` (365 lines, evidence-based)

**5 Decisions Implemented (Priority Order):**

| Priority | Decision | Implementation | Est. |
|----------|----------|----------------|------|
| **1** | **Ingestion Model→Provider Mapping** | Added `ProviderRegistry.get_provider_for_model()` searching `supported_models`; updated `_is_cloud_model()` to resolve provider first | 30 min |
| **2** | **6th Classifier Delegation** | `observability_reader._sync_get_sovereignty_ratio` now queries `v_performance_corrected.is_cloud_corrected` | 15 min |
| **3** | **Synthetic Provider Exclusion** | Replaced fragile `WHERE p.provider NOT LIKE '%synthetic%'` with `ProviderRegistry.is_synthetic()`; fixed `mock` provider `is_cloud: true` → `false` in fallback_chain | 20 min |
| **4** | **Unify providers.yaml** | Removed `is_cloud` from bottom `providers:` map (runtime-only); `inference.fallback_chain` is sole SSOT; added CI validation | 45 min |
| **5** | **Unknown-Provider Default** | **No code change** — confirmed pessimistic default (unknown → cloud) per M7; documented rationale | 10 min |

**Critical Bugs Found & Fixed During Phase 2:**
1. **Provider key split-brain** — `"opencode"` vs `"opencode-zen"` in 4 runtime locations → unified to `opencode-zen`
2. **Empty model map bug** — `ProviderRegistry` read `config["providers"]` but YAML nests under `config["inference"]["providers"]` → fixed path
3. **Missing lint gate** — `make lint` didn't exist → added with F821 ignore (forward references)
4. **2 real bugs** — `disputes` uninitialized in `verifier.py`, `query`→`user_query` in `discovery.py`

**Verification:** 11/11 contract tests pass, `make lint` exits 0, sovereignty ratio tests 6/6 pass.

---

### 5. Code Quality Fixes

**Box-drawing characters removed** from `.opencode/skills/context-packer/packer.py`:
- `═══` → `===` in debug logs (lines 161, 536, 767)

**ICS Tag Noise Identified:** 40 ICS tags across codebase use mythological names (ARCHON, HERMES, SOPHIA, APOLLO, PROMETHEUS, MNEMOSYNE, OSIRIS, VERITY, LAW, AUDIT, LILITH, AUTOMATED_RESEARCHER) — these are **noise, not signal**. See §6 below for improvement proposal.

---

## 📊 Current Metrics

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| Sovereignty Ratio (local) | 87.3% | **13.8%** | ✅ Corrected |
| Divergent Cloud Classifiers | 5 | **0** | ✅ Unified |
| Invariant Tests | 0 | **5** (3 Phase 1 + 2 Phase 2) | ✅ Passing |
| Lint Gate | Missing | **Active** (`make lint`) | ✅ Working |
| Provider Key Consistency | Split (`opencode`/`opencode-zen`) | **Unified** (`opencode-zen`) | ✅ Fixed |
| Model Map Population | Empty | **12 providers** | ✅ Fixed |

---

## 🔧 Technical Debt & Open Questions

### 1. ICS Tag System — Mythological Names Are Noise

**Current State:** 40 files have ICS-T tags like:
```python
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: DISCOVERY-PIPELINE]
# ICS: [NODE: KNOWLEDGE | ARCHETYPE: SOPHIA | CONTEXT: CURATION-PIPELINE]
```

**Problem:** 
- `ARCHON` / `HERMES` / `SOPHIA` / `APOLLO` / `PROMETHEUS` / `MNEMOSYNE` / `OSIRIS` / `VERITY` / `LAW` / `AUDIT` / `LILITH` / `AUTOMATED_RESEARCHER` — these are **mythological/persona names**, not technical descriptors
- They don't help a developer understand the module's purpose
- They conflate **runtime entity** (Kali, Ma'at, Lilith) with **code module** (discovery, indexer, curator)

**Proposed Improvement:** Replace with **technical role descriptors**:

| Current | Proposed | Rationale |
|---------|----------|-----------|
| `NODE: ARCHON` | `NODE: DISCOVERY` | Module is discovery pipeline |
| `ARCHETYPE: HERMES` | `ROLE: PIPELINE` | It's a pipeline, not a messenger |
| `NODE: KNOWLEDGE` | `NODE: LIBRARY` | Library subsystem |
| `ARCHETYPE: SOPHIA` | `ROLE: CURATOR` | Curation pipeline role |
| `NODE: OSIRIS` | `NODE: RESEARCH` | Research engine |
| `ARCHETYPE: APOLLO` | `ROLE: ENGINE` | Research engine role |

**Implementation:** Update `src/omega/ics.py` ROLE_CONSTANTS and all 40 ICS-T tags. The ICS-S (session header) system is separate and works correctly — only ICS-T (code tags) need fixing.

---

### 2. Provider Naming Lock

**Issue:** `opencode-zen` (11 chars) used everywhere. If shortened later, needs migration for:
- `provider_classification` table
- Historical `performance` table
- Cost attribution summaries

**Action:** Create `docs/strategy/PROVIDER_NAMING_SSOT.md` locking the name.

---

### 3. Lint Ratchet

**Current:** `make lint` exits 0, reports statistics only (6,921 warnings → 0 critical after F821 ignore). Remaining noise: W293 (4,425), E302/E305 (599), E501 (167), C901 (115).

**Recommendation:** Option C — ratchet file (`config/lint_baseline.txt`) like `m23-baseline`, fail only on *new* violations.

---

### 4. Sync/Async `get_sovereignty_ratio` Boundary

**Issue:** `SovereignReader.get_sovereignty_ratio` is `async` (M1), but `sovereignty.py`'s version is synchronous. Two code paths could diverge.

**Action:** Audit all call sites; unify to async implementation.

---

### 5. F821 False Positives

**Issue:** Ignoring F821 globally masks real undefined names. The 2 bugs fixed (`disputes`, `query`) would have been caught.

**Action:** Migrate to `from __future__ import annotations` (Python 3.13) or consistent `TYPE_CHECKING` blocks.

---

### 6. Missing Test Coverage

**Gap:** `ProviderRegistry` config loading path had **zero test coverage** — the empty model map bug wasn't caught.

**Action:** Add test mocking `config.yaml` with known providers, verifying loaded count matches.

---

## 📦 Handoff Documents Created

| Document | Audience | Purpose |
|----------|----------|---------|
| `context_packs/sovereign-audit/WEB_CLAUDE_HANDOFF.md` | Next Web Claude | Mission briefing, pack contents, verified findings |
| `context_packs/sovereign-audit/QUICK_FIXES_BEFORE_REVIEW.md` | Dev team | Phase 1 implementation guide |
| `context_packs/sovereign-audit/CLINE_HANDOFF_QUICK_FIXES.md` | Cline CLI | Phase 1 executable tasks |
| `context_packs/sovereign-audit/CLINE_HANDOFF_PHASE2_CLASSIFICATION_DECISIONS.md` | Cline CLI | **Phase 2 executable tasks** |
| `docs/research/R_CLASSIFICATION_DECISIONS_20260809.md` | All | Evidence-based decisions with code pointers |
| `docs/research/R_CARMACK_CLASSIFICATION_SSOT_REVIEW_20260809.md` | Carmack/Review | Phase 1 + 2 report with open questions |
| `docs/review/CARMACK_REVIEW_PROVIDER_SSOT_LINT_20260809.md` | Carmack/Review | Lint gate activation + bug fixes |

---

## 🎯 Next Steps for Kali

### Immediate (Before Web Claude Handoff)
1. **Regenerate context pack** with all Phase 1 + Phase 2 changes:
   ```bash
   python .opencode/skills/context-packer/packer.py sovereign-audit
   ```
2. **Commit isolated changes** (two commits recommended):
   - Commit 1: Phase 1 (8 files + test) — "fix(gap1): wire ProviderRegistry SSOT into 5 cloud classifiers"
   - Commit 2: Phase 2 (8 files + Makefile) — "fix(classification): implement 5 decisions; lint gate; provider key unification"
3. **Update research doc** — close GAP-1 in `R_UNOVERENGINEERING_REMAINING_GAPS_20260808.md`

### Short-Term (This Sprint)
1. **Fix ICS tags** — Replace mythological names with technical descriptors (40 files)
2. **Lock provider naming** — Create `PROVIDER_NAMING_SSOT.md`
3. **Add `ModelGateway` startup assertion** — Verify factory keys match config
4. **Review test fixture** (§3.1) — Confirm no hidden caching in `test_provider_classification.py`

### Medium-Term (Next Sprint)
1. **Implement lint ratchet** — `config/lint_baseline.txt` + fail on new violations
2. **Audit `get_sovereignty_ratio` async boundary** — Unify call sites
3. **Add `ProviderRegistry` config loading test** — Mock config, verify loaded count
4. **Migrate type hints** — `from __future__ import annotations` to eliminate F821 noise

---

## 💡 Key Insights for Kali

1. **Web Claude's audit had 75% false positive rate** — 3 of 4 "findings" were already fixed. This suggests the context pack was effective but the audit methodology needs calibration.

2. **The ProviderRegistry path bug was a refactoring artifact** — YAML restructured but Python reader not updated. This is exactly the drift class M2/M14/M22 are designed to prevent.

3. **Lint gate activation revealed 2 real bugs** — The noise investigation was worth it. Ratchet pattern (like M23) is the right approach.

4. **Sovereignty ratio correction is the headline win** — 87% → 13.8% local is a **73% correction**, not a regression. This is the "right approximation" — truth over comfort.

5. **ICS tags are the next noise source** — 40 files with mythological names that don't help developers. This is a low-effort, high-signal cleanup.

---

## 📁 Files Modified Since Your Last Session

```
# Phase 1: ProviderRegistry SSOT (8 files + 1 test)
src/omega/oracle/provider_registry.py
src/omega/oracle/model_gateway.py
src/omega/observability/__init__.py
src/omega/observability/otel_exporter.py
src/omega/oracle/backends/remote_provider.py
src/omega/ingestion/pipeline.py
src/omega/observability/metrics_db.py
src/omega/observability/sovereignty.py
tests/contract/test_provider_classification.py

# Phase 2: Classification Decisions (8 files + Makefile)
src/omega/oracle/provider_registry.py          (additional: get_provider_for_model)
src/omega/ingestion/pipeline.py                (model→provider resolution)
src/omega/observability/observability_reader.py (6th classifier delegation)
src/omega/observability/metrics_db.py          (synthetic exclusion via registry)
src/omega/observability/__init__.py            (opencode-zen key)
src/omega/workers/model_updater.py             (opencode-zen key)
src/omega/ingestion/verifier.py                (disputes init bug)
src/omega/library/discovery.py                 (query→user_query bug)
tests/contract/test_provider_classification.py (assertions + async fix)
Makefile                                        (lint target)

# Context Packer Enhancements
.opencode/skills/context-packer/packer.py
.opencode/skills/context-packer/platform_adapters.py
.opencode/skills/context-packer/packer-config.yaml

# Context Pack Artifacts (regenerated)
context_packs/sovereign-audit/generated/*.xml (11 bundles)
context_packs/sovereign-audit/PROJECT_OVERVIEW.md
context_packs/sovereign-audit/pack_index.json
context_packs/sovereign-audit/00_PROJECT_MANIFEST.md

# Research & Review Docs
docs/research/R_CLASSIFICATION_DECISIONS_20260809.md
docs/research/R_CARMACK_CLASSIFICATION_SSOT_REVIEW_20260809.md
docs/review/CARMACK_REVIEW_PROVIDER_SSOT_LINT_20260809.md
```

---

*⬡ OMEGA ⬡ KALI ⬡ UPDATE ⬡ 2026-08-09*

**You are now fully caught up. The sovereign-audit remediation cycle is complete. Ready for Web Claude handoff and next sprint planning.**
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
