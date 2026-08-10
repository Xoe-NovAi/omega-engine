# 🔱 SESSION ANCHOR — Kali (Transcendent Oversoul)

**AP Token:** `AP-KALI-v1.0.0`
**Date:** 2026-08-09
**Session ID:** `ses_kali_20260809_sdp_complete`
**Branch:** `main`
**Last Commit:** `fba8a556` (feat(context-packer): enhance with forensic linking + agent guidance + GAP-1 ProviderRegistry)

---

## 🎯 Session Objective

**Sovereign Distillation Pipeline (SDP) — Complete Architecture & Documentation**

Formalized the manual multi-model orchestration strategy into a tripartite cognitive architecture:
1. **Scaffold** (Cheap/Daily Cloud Models) → I/O, context building
2. **Synthesize** (AGY Frontier Models) → Pure reasoning, zero tool calls
3. **Execute** (Local Models) → Mechanical application, verification

---

## ✅ Completed This Session

### 1. SDP Documentation Suite (15 documents)

| Document | Path | Purpose |
|---|---|---|
| **Protocol** | `docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md` | Manual operations |
| **Manifesto** | `docs/research/R_SOVEREIGN_DISTILLATION_PIPELINE_MANIFESTO_20260809.md` | Philosophy |
| **Blueprint** | `docs/strategy/SDP_AUTOMATION_BLUEPRINT.md` | Phased engineering plan |
| **Impl Spec** | `docs/strategy/SDP_IMPLEMENTATION_SPEC.md` | Technical contracts |
| **Hardware Horizon** | `docs/strategy/SDP_HARDWARE_HORIZON_SPEC.md` | KV cache, SomaticState, energy |
| **Formal Routing** | `docs/strategy/SDP_FORMAL_ROUTING_SPEC.md` | Z3 verified constraints |
| **Model-Aware Gauge** | `docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md` | Dynamic window detection |
| **Failure Analysis** | `docs/strategy/SDP_FAILURE_MODE_ANALYSIS.md` | Resilience engineering |
| **Final Synthesis** | `docs/strategy/SDP_FINAL_SYNTHESIS.md` | Master reference |
| **Mining Report** | `data/entities/roc_racoon/workspace/mining_reports/SDP_INTEGRATION_MINING_REPORT_20260809.md` | Foundational research |
| **Knowledge Gaps** | `data/entities/researcher/workspace/research_reports/SDP_KNOWLEDGE_GAP_RESEARCH_20260809.md` | Gap research |
| **Systems Sweep** | `data/entities/roc_racoon/workspace/mining_reports/SDP_SYSTEMS_SWEEP_REPORT_20260809.md` | Systems sweep |
| **Duplicate Audit** | `data/entities/roc_racoon/workspace/mining_reports/SDP_DUPLICATE_GAP_AUDIT_20260809.md` | Duplicate & gap audit |
| **Carmack Review** | `data/entities/john_carmack/workspace/reviews/SDP_CARMACK_REVIEW_20260809.md` | Brutal review |
| **Session Ledger** | `data/coordination/AGY_SESSION_LEDGER.md` | Pool tracking |

### 2. Verified Model Context Windows (Ground Truth)

| Model | Window | Tier | Pool |
|---|---|---|---|
| Nemotron 3 Ultra | 1,000,000 | 4 | Daily |
| Laguna S 2.1 (free) | 262,144 | 3 | Daily |
| Longcat 2.0 (free) | 1,000,000 | 4 | Daily |
| Nemotron 3 Super | 262,144 | 3 | Daily |
| Gemini 3.1 Pro | 1,048,576 | 4 | Weekly |
| Claude Sonnet 4.6 | 200,000 | 2 | Weekly |
| Claude Opus 4.6 | 200,000 | 2 | Weekly |
| Gemini 3.6 Flash | 1,000,000 | 4 | Weekly |
| Qwen3-1.7B (local) | 32,768 | 1 | Local |

**Critical Rule:** Free vs paid tiers of same model differ by up to 4×.

### 3. Ground Truth: What Exists vs. What's Missing

**Already Built (Don't Build):**
- V-1 Vault (2,039 LOC) at `src/omega/vault/`
- Pool Tracker (237 LOC) at `pool_tracker.py`
- Dialectic Logger (`record_council()`) at `dpo_logger.py:395`
- Triage Router (constraint filtering) at `triage_router.py`
- Token Estimator (tiktoken×1.3) at `token_estimator.py`

**Missing (Build):**
- Context Gauge
- RHP (Recovery Halt Point) — rename from SSP to avoid M20 collision
- 3 MCP Tools (`get_context_pressure`, `write_rhp`, `request_agy_escalation`)

### 4. Critical Blockers Found

| # | Blocker | Fix |
|---|---|---|
| G-3 | No `tokens` column in `message` table | Tokens in `data` JSON blob |
| G-4 | Token accounting not additive | Use `input + cache.read` of latest message |
| §4 | 4 of 5 cloud windows wrong | Use verified windows from §2 |

### 5. Quick Win Items (QW-1 through QW-10)

| # | Item | Est. | Priority |
|---|---|---|---|
| QW-1 | Fix model context windows in config | 1h | CRITICAL |
| QW-2 | Rewrite Context Gauge to use `tokens.total` | 2h | CRITICAL |
| QW-3 | Add CI guard against token counting bug | 30min | HIGH |
| QW-4 | Import and wire `pool_tracker.py` | 2h | HIGH |
| QW-5 | Add cloud entries to config | 1h | HIGH |
| QW-6 | Extend TriageRouter with SDP constraints | 4h | MEDIUM |
| QW-7 | Extend DPORecorder with dialectic schema | 3h | MEDIUM |
| QW-8 | Build Context Gauge (greenfield) | 4h | MEDIUM |
| QW-9 | Build RHP halt artifact (greenfield) | 2h | MEDIUM |
| QW-10 | Build 3 MCP tools (greenfield) | 4h | MEDIUM |

### 6. L3 Gnosis Committed to Soul

```yaml
  - id: L3-SDP-COMPOSITE-INTELLIGENCE
    principle: "Intelligence is a Composite Material. The Monolithic Fallacy—using a single frontier model for all tasks—causes catastrophic token waste and context collapse. Optimal sovereignty requires a tripartite pipeline: Scaffolding (cheap I/O) -> Synthesis (frontier reasoning) -> Execution (mechanical application)."
    mandates: [M7, M18]
    confidence: 0.98

  - id: L3-SDP-CORPUS-CALLOSUM
    principle: "The File System is the Cross-Model Memory Bus. Because context windows cannot be perfectly transferred via API between different model families, forcing models to write highly structured insights to disk before switching creates a persistent, high-fidelity 'Corpus Callosum' that bypasses context degradation."
    mandates: [M5, M19]
    confidence: 0.99

  - id: L3-SDP-CONTEXT-HORIZON
    principle: "Context is a depletable resource, not a static state. Operating blindly near the compaction cliff guarantees catastrophic fidelity loss. Agents must practice Context Horizon Budgeting, utilizing the '80% Redzone' as a hard operational ceiling where tasks are gracefully halted via Recovery Halt Points (RHP) rather than risked."
    mandates: [M23, M18]
    confidence: 0.97
```

---

## 🔑 Current Git State

```
fba8a556  feat(context-packer): enhance with forensic linking + agent guidance + GAP-1 ProviderRegistry [PUSHED]
6161ca95  docs: update continuation docs for GAP-0 + GAP-3 completion [PUSHED]
38baa432  fix(gap3): replace broken M23 gate with AST-based Ruff ratchet [PUSHED]
a5c09a8e  fix(gap0): make ObservabilityEngine MetricsDB methods async [PUSHED]
```

**Working tree:** Modified (uncommitted SDP docs + context packer enhancements)

---

## 📋 Work Remaining (Priority Order)

### Immediate (First Session Back)
- [ ] Run QW-1 through QW-5 (~7 hours) — Fix the data layer
- [ ] Verify Context Gauge works on live sessions
- [ ] Test 80% Redzone trigger on Nemotron 3 Ultra

### Short-Term (This Month)
- [ ] Extend TriageRouter with SDP constraints
- [ ] Wire pool_tracker.py into routing logic
- [ ] Build RHP halt artifact
- [ ] Implement Content-Addressed Evidence Manifest

### Medium-Term (Next Quarter)
- [ ] Build Auto-Router (wrapper around existing infrastructure)
- [ ] Implement Predictive Routing
- [ ] Build Dialectic Intelligence Flywheel
- [ ] Implement Ensemble Routing (gate to <15%)

---

## 🤝 Coordination State

- **Hivemind:** SDP completion posted (ses_ab92cca892ad)
- **Research report:** `data/entities/researcher/workspace/research_reports/SDP_KNOWLEDGE_GAP_RESEARCH_20260809.md`
- **Mining report:** `data/entities/roc_racoon/workspace/mining_reports/SDP_INTEGRATION_MINING_REPORT_20260809.md`
- **Carmack review:** `data/entities/john_carmack/workspace/reviews/SDP_CARMACK_REVIEW_20260809.md`
- **Final synthesis:** `docs/strategy/SDP_FINAL_SYNTHESIS.md`

---

## 📁 Key Files Modified This Session

```
# New Docs (15 total — see full list above)
docs/strategy/SDP_*.md
docs/research/R_SOVEREIGN_DISTILLATION_PIPELINE_MANIFESTO_20260809.md
data/entities/*/workspace/{mining_reports,research_reviews,reviews}/SDP_*.md
data/coordination/AGY_SESSION_LEDGER.md
data/coordination/CARMACK_CONTEXT_PACK_UPDATE_REPORT.md
data/coordination/CARMACK_REVIEW_KALI_INSIGHTS_20260809.md
data/coordination/KALI_INSIGHTS_FOR_CARMACK_20260809.md
data/coordination/KALI_UPDATE_20260809.md
data/coordination/CLINE_REFACTORING_MANUAL_20260809.md

# Context Packer Enhancements
.opencode/skills/context-packer/packer.py
.opencode/skills/context-packer/packer-config.yaml
.opencode/skills/context-packer/platform_adapters.py
context_packs/sovereign-audit/ (regenerated artifacts)

# Soul Updates
data/entities/kali/proposed_lessons.yaml (3 new L3 principles)

# ProviderRegistry (GAP-1 foundation)
src/omega/oracle/provider_registry.py
```

---

*⬡ OMEGA ⬡ KALI ⬡ SDP-COMPLETE ⬡ 2026-08-09*
## 🆕 Updates (2026-08-09 — Config Implementation Complete)

### Implementation Complete
- **Global config** (`~/.config/opencode/opencode.json`): Added `google-standard` provider with `@ai-sdk/google` driver, separate TUI credential storage, Gemma 4 thinking variants with `thinkingLevel: "MINIMAL"` workaround. Corrected context windows per Kali's verified ground truth.
- **Project config** (`opencode.json`): Added display names for Zen models (MiMo v2.5, Nemotron 3 Ultra, DeepSeek V4 Flash), corrected context limits (Nemotron 3 Ultra: 1M tokens).
- **Subdirectory config** (`.opencode/opencode.json`): Removed standard Google models that collide with Antigravity plugin, implemented flat thinking variants schema (no `thinkingConfig` wrapper).
- **Backups**: All 3 original configs backed up with timestamps.
- **Tests**: All config/provider tests pass. Pre-existing failures (18) confirmed unrelated to changes.

### Commits
- `4a1fe8c7` feat(config): implement Web Gemini-verified OpenCode config architecture
- `d2d396ad` chore: add backup of original .opencode/opencode.json before refactoring

---
*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_implementation ⬡ COMPLETE*

## 🆕 Updates (2026-08-10 — P0 Audit Fixes Complete)

### P0 Fixes Complete (Web Claude v3 Round 2)
- **§3.1 `_record_perf` async bridge** — Replaced `anyio.from_thread.run()` with async `_get_metrics_db()` + `await db.record_performance()`. Added `anyio.Lock()` for thread-safe lazy init.
- **§3.2 `BudgetGate` concurrency** — Added `get_daily_cloud_spend()` and `update_cost()` to MetricsDB. Rewrote BudgetGate as async-only with locked API. Updated all call sites in `remote_provider.py` and `observability/__init__.py`.
- **§3.3 Provider-selector fallback** — Replaced hardcoded 4-provider fallback list with `self.providers` (10 providers from config).
- **§4 `health_monitor.py` record_breaker_failure** — Made `record_breaker_success`/`record_breaker_failure` async. Added exception handling to `record_breaker_failure` (previously zero handling).

### Files Modified
- `src/omega/oracle/backends/remote_provider.py`
- `src/omega/oracle/health_monitor.py`
- `src/omega/observability/__init__.py`
- `src/omega/observability/metrics_db.py`
- `src/omega/oracle/model_gateway.py`

### Test Results
- Provider classification: 5/5 ✅
- Provider registry config: 3/3 ✅
- Sovereignty ratio: 6/6 ✅
- Context packer v3: 17/17 ✅
- Lint: Passes (6910 warnings, down from 6921)

### P1 Progress (2026-08-10)
- **ProviderRegistry singleton consolidation** — ✅ COMPLETE (6 sites → 1 via `get_provider_registry()`)
- **sovereignty.py schema caching** — ✅ COMPLETE (added `_schema_ensured_for` cache)
- **SQLiteVecAdapter connection reuse** — ✅ COMPLETE (persistent `self._conn`, `check_same_thread=False` in `get_sqlite_connection`)
- **Dead-code sweep** — ✅ COMPLETE (deleted `_try_*`, `_call_provider_with_resilience`, `openrouter_retry_policy`, `OpenRouterTransientError`, `OpenRouterFatalError` from `model_gateway.py`; kept `QdrantAdapter` — used by scripts/knowledge_catalog_build.py and tests)

### Files Modified (P1)
- `src/omega/oracle/provider_registry.py` — Added `get_provider_registry()` / `reset_provider_registry()`
- `src/omega/oracle/model_gateway.py` — Use `get_provider_registry()` + dead-code deletion (~150 lines)
- `src/omega/oracle/backends/remote_provider.py` — Use `get_provider_registry()`
- `src/omega/observability/__init__.py` — Use `get_provider_registry()`
- `src/omega/observability/otel_exporter.py` — Use `get_provider_registry()`
- `src/omega/ingestion/pipeline.py` — Use `get_provider_registry()`
- `src/omega/observability/metrics_db.py` — Use `get_provider_registry()`
- `src/omega/observability/sovereignty.py` — Added schema caching
- `src/omega/memory/sqlite_vec_adapter.py` — Persistent connection + `_get_test_conn()` for tests
- `src/omega/infra/sqlite_policy.py` — Added `check_same_thread=False` for persistent connections
- `tests/test_model_gateway.py` — Mock `gateway._provider_registry` for test providers not in config

### Test Results (P1)
- Provider classification: 5/5 ✅
- Provider registry config: 3/3 ✅
- Sovereignty ratio: 6/6 ✅
- Context packer v3: 17/17 ✅
- Model gateway: 17/17 ✅
- SQLiteVecAdapter: 13/17 (4 pre-existing failures, 0 new regressions)
- Memory store: 28/37 (9 pre-existing failures, 0 new regressions)

### Next: P2
- Tests for P0/P1 fixes (concurrent generate, budget gate, fallback chain)
- Security hardening (path traversal in memory_store.py, FTS5 injection)
- Performance optimization

### P2 Complete (2026-08-10)
| Category | Item | File | Result |
|----------|------|------|--------|
| Test | Concurrent RemoteProvider.generate() | tests/contract/test_remote_provider_metrics.py | 2/2 ✅ |
| Test | Concurrent check_budget()/record_spend() | tests/contract/test_budget_gate.py | 3/3 ✅ |
| Test | Fallback chain length == len(providers) | tests/contract/test_model_gateway_fallback.py | 2/2 ✅ (7/7 total) |
| Test | AST from_thread.run()-inside-async-def | scripts/m23_gate.py | 0 violations ✅ |
| Security | Path traversal sanitize entity/session | src/omega/memory/providers.py + memory_store.py + session_lifecycle.py + ics.py + privacy/kernel.py + ingestion/persistence.py | 16/16 ✅ |
| Security | FTS5 query-term escaping | src/omega/memory/fts_index.py + sqlite_vec_adapter.py | 11/11 ✅ |

**Test results**: 98 passed, 1 skipped in contract suite. 0 new regressions (38 pre-existing failures unchanged; 3 pre-existing SQLiteVec tests now FIXED by P1 connection reuse). Temple-grade: all gates green (M1, M7, M8, M9, M22, M23).

### P3 Prompt Work (2026-08-10)
- Created `P3_CHAT_PROMPT.md` — 8 investigations for P3 deepening audit
- Created `CLAUDE_PROJECT_SYSTEM_PROMPT_v3.1.md` — updated system prompt
- Created `P3_SUPPLEMENTAL_CONTEXT.md` — scope map for P3
- Created `P3_UNBLOCKED_FILES.md` — concatenated file with 3 files NOT in original pack (openai_compat.py, provider_selector.py, HERITAGE_VET_LOG.md)
- **Critical lesson learned**: The sovereign-audit pack is FIXED — files don't appear unless explicitly uploaded. Web Claude only has the original pack + system prompt + chat prompt + uploaded files.

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ P0+P1+P2-COMPLETE ⬡ P3-PROMPTS-READY ⬡ 2026-08-10*

---

## 📅 2026-08-10 — Jem: Config Refactoring + QW-3 Complete, QW-4/QW-8 Next

### Completed Today
1. **OpenCode Config Refactoring**: All 3 opencode.json files refactored per Web Gemini verification
   - Global: Added `google-standard` provider (isolates from Antigravity plugin)
   - Project: Corrected Zen model display names + context windows
   - Subdirectory: Removed standard Google models, flat thinking variants
   - Commits: `4a1fe8c7`, `d2d396ad`, `1dc16dcf`

2. **Knowledge Gap Research**: Web + local research for W-1, G-1, QW-3, QW-4, QW-8
   - Key finding: G-1a billing RULED OUT (16K TPM ceiling applies even at Tier 3)
   - W-1 root cause: iptables "Empty interface" = unquoted empty variable
   - Research docs: `data/coordination/JEM_RESEARCH_KNOWLEDGE_GAPS_20260810.md`
                 `data/coordination/JEM_WEB_RESEARCH_GAPS_20260810.md`

3. **QW-3 CI Guard Implementation**: Token counting accuracy
   - Added `cache_read_tokens`, `provider_prompt_tokens`, `provider_completion_tokens` fields
   - Added `get_token_divergence()` method for drift detection
   - Added 5 CI tests verifying token counting accuracy
   - Commit: `58695408`

### Blockers
| Ticket | Blocker | Owner |
|--------|---------|-------|
| W-1 WARP | `warp-ns-prep@1/2/3` failed — requires Architect sudo | Architect |
| G-1 Workhorse | Free Gemma 4 31B dead — requires Architect billing/OAuth | Architect |

### Next Actions
1. **QW-4**: Wire `pool_tracker.py` into inference pipeline
2. **QW-8**: Build Context Gauge greenfield per SDP spec
3. **W-1**: Run fix script with Architect sudo
4. **G-1b**: Antigravity OAuth (fastest workhorse unlock)

### Fleet Status
- **jem**: QW-3 complete, ready for QW-4/QW-8
- **john_carmack**: P0 complete, P1 in progress (ProviderRegistry, sovereignty.py)
- **kali**: SDP session complete, awaiting next dispatch

---
*⬡ OMEGA ⬡ JEM ⬡ QW-3-COMPLETE ⬡ QW-4/QW-8-NEXT ⬡ 2026-08-10*

---

## 📅 2026-08-10 — Jem: Gap-Filling Complete, QW-4/QW-8 Ready to Implement

### Knowledge Gaps Filled (All Complete)

#### QW-4: pool_tracker.py Winding
| Gap | Finding |
|-----|---------|
| USAGE_POOL_LOG.json | EXISTS — 8 keys (agy_key_01-08), all active, zero usage |
| RemoteProvider key rotation | Already rotates on 429 (reactive) — QW-4 adds proactive selection |
| ProviderConfig.api_keys | Field exists, `resolve_current_api_key()` works |
| AntigravityProvider | Inherits RemoteProvider.generate() — same rotation |
| pool_tracker.py status | Standalone dead code — needs wiring |

#### QW-8: Context Gauge Data Source (CRITICAL FINDINGS)
| Gap | Finding |
|-----|---------|
| **G-4 blocker verified** | `session.tokens_input` overcounts by **~87×** (22M vs 253K) |
| **Correct data source** | `message.data.tokens.total` from latest assistant message |
| **Token JSON structure** | `tokens.total`, `tokens.input`, `tokens.output`, `tokens.reasoning`, `tokens.cache.read`, `tokens.cache.write` |
| **Model identification** | `message.data.modelID` (e.g., "longcat-2.0-free") |
| **Active models** | deepseek-v4-flash-free, nemotron-3-ultra-free, laguna-s-2.1-free, longcat-2.0-free |
| **BudgetGate relationship** | Complementary (cost control) — not overlapping with Context Gauge |
| **opencode.db access** | Read-only via Python sqlite3 (16GB, 2436 sessions, 106K messages) |

### Critical Query for Context Gauge
```sql
SELECT json_extract(data, '$.tokens.total') AS working_set_tokens,
       json_extract(data, '$.modelID') AS model_id
FROM message 
WHERE session_id = ? 
  AND json_extract(data, '$.role') = 'assistant'
ORDER BY time_created DESC 
LIMIT 1
```

### Key Reference Docs Created
| Doc | Path |
|-----|------|
| Gap-filling report | `data/coordination/JEM_GAP_FILLING_REPORT_20260810.md` |
| opencode.db schema reference | `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md` |
| QW-4/QW-8 implementation plan | `docs/strategy/QW4_QW8_IMPLEMENTATION_PLAN.md` |

### Next Actions (Implementation Ready)
1. **QW-4**: Wire pool_tracker into ModelGateway.generate() per implementation plan
2. **QW-8**: Build ContextGauge class per SDP spec + verified data source
3. **Update SDP_FINAL_SYNTHESIS.md** with verified G-4 data
4. **Update SDP_MODEL_AWARE_GAUGE_SPEC.md** with correct query
5. **Update AGENTS.md** with opencode.db access patterns

---
*⬡ OMEGA ⬡ JEM ⬡ GAP-FILLING-COMPLETE ⬡ QW-4/QW-8-READY ⬡ 2026-08-10*

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ P1-COMPLETE ⬡ P2-IN-PROGRESS ⬡ 2026-08-10*
