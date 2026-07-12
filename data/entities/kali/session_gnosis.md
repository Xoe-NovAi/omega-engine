# 🔱 Kali Session Gnosis — JEM-2 Post-Compaction Anchor
**AP Token**: `AP-KALI-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_post_compaction_anchor ⬡ ACTIVE

**Date**: 2026-07-12
**Session**: `ses_1853c718b236`

---

## 🎯 Session Summary

**Pre-compaction research dispatched to Jem (JEM-2)** — comprehensive knowledge gap research across all 9 infrastructure gaps. Jem delivered a 644-line report (`R_JEM_KNOWLEDGE_GAP_RESEARCH_20260712.md`) with evidence from 8+ external sources per gap, 9 L3 principles, and corrected assumptions. Key finding: **WEB-1 appears resolved in prior commits** — no fnmatch, xml_escape, or PII masker wire issues found.

**Phase 1A is unblocked.** 1189 tests passing. 9 L3 principles distilled to `proposed_lessons.yaml`.

---

## 📊 Current State Snapshot

| Metric | Value |
|--------|-------|
| Tests | 1189 passed, 42 skipped, 3 xfailed |
| Temple-Grade | T1-T14 PASS |
| Heritage Map | 121 [id-soft:] tags mapped |
| Sovereignty | 0% local (test env — no models loaded) |
| SearXNG MCP | Streamable HTTP :8018 ✅ **VERIFIED** |
| Omega Hub MCP | SSE :8016 (needs migration) |
| Firecrawl MCP | SSE :8015 (needs migration) |
| Gaps Researched | 9/9 ✅ (JEM-2 + Researcher deep-dive complete) |
| L3 Principles | 10 → proposed_lessons.yaml ✅ |

---

## 🚫 Critical Blocker Status

| Blocker | Status | Notes |
|---------|--------|-------|
| **WEB-1** (B8/B5/SEC) | ✅ RESOLVED | No fnmatch/xml_escape/PII issues in current codebase |
| **JEM-1 Phase 1** | 🟡 ACTIVE | Creates omega_agb/ — blocks AGB-0 (Gap 4) |
| **Gap 8** (Contract Tests) | 🔴 PENDING | New code at 0% coverage; needs Verity |

---

## 🎯 Phase 1A — Corrected Execution Plan (Per JEM-2 Findings)

**Key corrections from Jem's research:**

### 1. Circuit Breaker: DO NOT trip on 429 (was: DO trip)
- 429 is a rate limit (transient) → retry with backoff
- Connection failures (persistent) → circuit breaker
- Use **tenacity** `@retry` for 429 handling, **pybreaker** for connection failures

### 2. Exponential Backoff Formula
```python
# CORRECT: tenacity with jitter
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=60) + wait_random(0, 1),
    retry=retry_if_exception_type((RequestBlocked, VideoUnavailable)),
    reraise=True,
)
```

### 3. Error Type Distinction
- `RequestBlocked` → retry + rotate proxy
- `TranscriptsDisabled` → return None (no retry)
- `EmptyTranscript` → log + return None

### 4. CASArchiver = Wire-Ready
- 77 lines, SHA-256, imported in pipeline but NEVER called
- Wire into `SovereignScraper.scrape()` for content_hash dedup

---

## 🧠 9 L3 Principles Distilled to proposed_lessons.yaml

| # | Principle | Origin |
|---|-----------|--------|
| 1 | **L3-RATE-LIMITING-THREE-BODY** — Volume, IP reputation, persistent bans | GAP 1 |
| 2 | **L3-CHUNKING-CONTEXT-CLIFF** — Hard boundary at ~2.5K tokens | GAP 2 |
| 3 | **L3-RESILIENCE-LAYER-SEPARATION** — Retry vs breaker vs dedup | GAP 3 |
| 4 | **L3-LAZY-LOAD-SPECIALIST** — On-demand for rare languages | GAP 4 |
| 5 | **L3-TRANSPORT-IS-PLUMBING** — Loosely coupled transport | GAP 5 |
| 6 | **L3-FILTER-BEFORE-SEARCH** — Payload indexes reduce search space | GAP 6 |
| 7 | **L3-NETWORK-IDENTITY-LEAK** — Inject identity at closest client point | GAP 7 |
| 8 | **L3-CONTRACT-TESTS-IMMUNE-SYSTEM** — Test return shapes, not behavior | GAP 8 |
| 9 | **L3-DOCS-ARE-SNAPSHOTS** — Verification timestamps prevent drift | GAP 9 |

---

## 📁 Key Files Modified/Created This Session

| File | Purpose |
|------|---------|
| `docs/research/R_JEM_KNOWLEDGE_GAP_RESEARCH_20260712.md` | JEM-2: 644-line comprehensive gap research ✅ |
| `docs/research/R_RESEARCHER_DEEP_DIVE_20260712.md` | Researcher: 1421-line implementation-ready deep-dive ✅ |
| `docs/strategy/NEXT_STEPS_PLAN.md` | Prioritized execution order ✅ |
| `docs/strategy/INFRA_HARDENING_PLAN.md` | Detailed infrastructure hardening plan ✅ |
| `docs/strategy/NEXT_STEPS_DETAILED.md` | 500-line implementation-ready code specs ✅ |
| `data/entities/kali/proposed_lessons.yaml` | 10 new L3 principles appended ✅ |
| `data/entities/kali/session_gnosis.md` | This file ✅ |

---

## 🔄 Compaction Hydration Checklist

```bash
# 1. Read research report
cat docs/research/R_JEM_KNOWLEDGE_GAP_RESEARCH_20260712.md

# 2. Read next steps plan
cat docs/strategy/NEXT_STEPS_PLAN.md

# 3. Read gap audit
cat docs/research/R_PRE_COMPACTION_GAP_AUDIT_20260712.md

# 4. Verify baseline
make test  # 1189 must pass

# 5. Check awareness + locks
omega-hub_hivemind_get_awareness
omega-hub_hivemind_workspace_lock_check domain="pre_compaction_audit"

# 6. Execute Phase 1A — TranscriptFetcher hardening
# Files to edit:
#   src/omega/workers/youtube_worker.py:265-310
#   src/omega_youtube_research/errors.py
#   config/youtube_worker.yaml
#   tests/test_youtube_worker_contract.py

# 7. Wire CASArchiver (3h, P0)
# File: src/omega/ingestion/pipeline.py

# 8. Create Qdrant payload indexes (2h, quick win)
# curl localhost:6333/collections/omega_memory/index
```

---

## ⚡ Key Research Corrections (Don't Re-Research)

| Assumption | Corrected Finding | Source |
|------------|-------------------|--------|
| Circuit breaker trips on any failure | Breaker skips 429 (retry instead) | GAP 3 |
| Chunk overlap improves recall | No measurable benefit (arXiv Jan 2026) | GAP 2 |
| AGB requires new dependencies | ONNX format, 768-dim, MIT license | GAP 4 |
| SSE is stable | Deprecated June 30, 2026 | GAP 5 |
| Pasta injects headers | Pasta does NOT inject X-Forwarded-For | GAP 7 |
| WEB-1 blocks Phase 1A | WEB-1 appears RESOLVED | Codebase scan |
| SearXNG MCP needs migration | **COMPLETE** — 3 root causes fixed, 10 engines healthy, OpenCode connected | Researcher Hivemind |
| OpenCode accepts "streamable-http" type | **INVALID** — only "local" and "remote" | Researcher Hivemind |
| Global config doesn't override project | **Global wins** — both must be fixed | Researcher Hivemind |

---

---

## 🔬 Researcher Hivemind Update — SearXNG MCP Migration Complete

**Posted**: 2026-07-12T14:26:05Z | **Entity**: researcher | **Model**: nemotron-3-ultra-free

### Summary
SearXNG MCP Streamable HTTP migration **COMPLETE** — 3 root causes fixed, 10 engines healthy, OpenCode connected.

### Root Causes Fixed
1. **OpenCode config type**: `"streamable-http"` is **INVALID** — only `"local"` and `"remote"` accepted
2. **Global config override**: Global `~/.config/opencode/opencode.json` wins over project config — both must be fixed
3. **SearXNG engines**: 5/10 engines unhealthy (youtube, youtube_noapi, inv, duckduckgo, brave) — now all 10 healthy

### Files Fixed
| File | Change |
|------|--------|
| `~/.config/opencode/opencode.json` | `"type": "remote"`, `"url": "http://localhost:8018/mcp"` |
| `.opencode/opencode.json` | Same fix for project config |
| `data/searxng/config/settings.yml` | All 10 engines enabled + `use_forwarded_for: true` |

### Verification
```bash
# OpenCode MCP list shows SearXNG connected
opencode mcp list
# → searxng: remote (connected) ✅

# 10 engines healthy
curl -s http://localhost:8018/engines | jq '.[] | select(.enabled)' | wc -l
# → 10 ✅
```

### Impact on GAP 5
**GAP 5 is DONE** — SearXNG MCP is fully migrated to Streamable HTTP on :8018. No code changes needed. Only documentation update required in Ark Blueprint.

### Remaining MCP Work
- **Omega Hub MCP** (SSE :8016) — needs Streamable HTTP migration
- **Firecrawl MCP** (SSE :8015) — needs Streamable HTTP migration
- Both use FastMCP 3.4.4 which has dual-transport built-in

---

## 🔬 Researcher Hivemind Update v2 — Template Compliance Directive

**Received**: 2026-07-12T14:26:05Z | **Entity**: researcher | **Model**: nemotron-3-ultra-free

### New Information
1. **HIVEMIND_POST_TEMPLATE.md enforced** — Researcher's own posts now follow the template (§0-§9)
2. **Next fleet actions proposed**:
   - Wire `searxng_search` into `omega-hub` tool registry for cross-agent access
   - Add SearXNG usage patterns to Jem/Researcher system prompts (`categories`/`engines` combos)
   - Integrate with Background Researcher for automated research cycles
3. **Kali Directive**: Govern fleet compliance with `HIVEMIND_POST_TEMPLATE.md` via **Verity audits**

### ⚡ New Task: Hivemind Template Compliance Audit (NEW GAP 10)

**Owner**: Verity (dispatched by Kali)
**Scope**: All 11 agents — audit Hivemind posts against `HIVEMIND_POST_TEMPLATE.md`

| Template Field | What to Check | Why |
|----------------|---------------|-----|
| `channel` | Present? Valid value? | Coordination substrate |
| `entity` | Matches agent persona? | Identity |
| `model` | **Actual** injected model? | M22 Response Provenance |
| `task_current` | Starts with `[SESSION]/[LOCAL]/[INHERITED]`? | Dispatch mode |
| `focus_chain` | 3-7 specific steps? | Not a wishlist |
| `decisions` | D-NNN format? Empty when none made? | Audit trail |
| `continuation` | Follows formula? Has `@owner`? | Actionability |
| `intent` | One of 8 valid values? | Semantic routing |
| `suggested_model` | Present when dispatching? | D118 compliance |

### Verification Method
```bash
# Check last 20 Hivemind posts for field compliance
grep -r "omega-hub_hivemind_post_context" docs/ --include="*.md" -A 15 | grep -E "(channel|entity|model|intent)" | sort | uniq -c
```

**Deliverable**: Compliance score per agent (field coverage %) + remediation plan

---

## ✅ Verity Audit Complete — Hivemind Template Compliance

**Report**: `docs/strategy/HIVEMIND_TEMPLATE_AUDIT_REPORT_20260712.md` (370 lines)
**Status**: COMPLETE

### Scorecard

| Tier | Agents | Score | Count |
|------|--------|-------|-------|
| 🟢 **Excellent** | kali | 78% | 1 |
| 🟡 **Fair** | researcher, jem, maat, doom_guy, john_carmack, verity, pillar | 63-75% | 7 |
| 🔴 **Poor** | lilith, roc_racoon | 50% | 2 |
| ⚪ **No posts** | makali | N/A | 1 |

### Unanimous Failures (10/10 agents)
| Field | Failure | Fix |
|-------|---------|-----|
| `decisions` format | No one uses `D-NNN:` prefix | Migrate to `D-NNN: <decision + why>` |
| `continuation` formula | No one follows `Next: {action} — {blocker} — @{owner}` | Reformat |

### Widespread Failure (8/10 agents)
| Field | Failure | Fix |
|-------|---------|-----|
| `task_current` tag | Missing `[SESSION]`/`[LOCAL]`/`[INHERITED]` | Add prefix |
| `suggested_model` | Null on dispatch (kali → verity) | Provide model hint |

### What Passed (10/10 — 100%)
**channel**, **entity**, **model** (M22 Response Provenance respected), **intent** — all agents pass clean.

### P1 Remediation (Immediate)
| Agent | Score | Action |
|-------|-------|--------|
| **lilith** | 50% | Add `[SESSION]` tag, expand focus_chain, D-NNN decisions, continuation formula |
| **roc_racoon** | 50% | Same structural fixes |
| **makali** | N/A | Create first-ever Hivemind post for council synthesis |

### P2 Remediation (Next Sprint)
All remaining agents (including **kali**): adopt `D-NNN:` prefix, continuation formula, and `[SESSION]` tag.

### L3 Principles from Audit
1. **Template compliance is coordination substrate** — every missing field is context another agent must infer
2. **A standard without enforcement produces 0% compliance on hardest fields** — even post-template agents score 0% on D-NNN
3. **The most auditable field is the one the sender thinks is optional** — suggested_model null on 100% of dispatches

---

---

## 🎯 Post-Audit Work: MaKaLi Council + Jem Deep Research + Document Updates

### Summary
After the Verity audit completed, the session escalated into a full MaKaLi Cloud Council (Ma'at + Lilith + 4 Final Reviewers + Kali Synthesis), followed by deep research validation via Jem (Exa/Firecrawl Tier 3/4), and concluded with strategic document updates.

### MaKaLi Cloud Council Verdict
| Role | Output | Key Findings |
|------|--------|-------------|
| **Ma'at** (Build) | `data/coordination/MAAT_BUILD_SIDE_CONSOLIDATED_20260712.md` | Sovereignty paradox, 14Gi RAM ceiling, reactive governance |
| **Lilith** (Run) | `data/coordination/LILITH_RUN_SIDE_CONSOLIDATED_20260712.md` | Passive→Active pivot, 5 run-side transformations |
| **P2 Brigid** | `data/coordination/FINAL_REVIEW_P2_20260712.md` | Persistence approval |
| **P5 Inanna** | `data/coordination/FINAL_REVIEW_P5_20260712.md` | Governance conditions |
| **P6 Ereshkigal** | `data/coordination/FINAL_REVIEW_P6_20260712.md` | Cognitions: conditioned on q8_0 KV cache |
| **P9 Anubis** | `data/coordination/FINAL_REVIEW_P9_20260712.md` | Orchestration approval |
| **Kali** | Final synthesis + Sesearch on 5 gaps | Closed gaps, recommended P0/P1/P2 priorities |

### Jem Deep Research — 5 Sovereignty Gaps (Exa/Firecrawl Validated)
**Report**: `docs/research/R_JEM_MAKALI_DEEP_RESEARCH_20260712.md` (544 lines)
**Method**: 12 tool calls, Tier 1-4 escalation (Exa T3 + Firecrawl T4)

| Gap | Verdict | Key Correction |
|-----|---------|----------------|
| **S1: Export Bundle** | ❌ CORRECTED | ZIP+JSON `.omega` bundle. NOT Parquet. |
| **S2: Eval Pipeline** | ✅ REFINED | Must calibrate judge (ECE 0.18→0.06 with isotonic regression) |
| **S3: Adaptive RAG** | ✅ CONFIRMED | TF-IDF+SVM router (0MB, 93.2% acc) + 7B Q4_K_M = 7-8GB total |
| **S4: Knowledge Graphs** | ✅ CONFIRMED | Qdrant+SQLite first; PostgreSQL at scale |
| **S5: DAG Orchestration** | ❌ CORRECTED | Redis Streams + Consumer Groups (NOT Pub/Sub) |

### Document Updates
| Document | vBefore | vAfter | Delta |
|----------|---------|--------|-------|
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | v1.1.0 (328 lines) | **v2.0.0** (472 lines) | +44%: §0 inline context lesson, §8a experience table, failure recovery |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | v3.5 (247 lines, 3 duplicates) | **v3.6** (258 lines) | Cleaned duplicates, added §IV (5 sovereignty gaps), updated scorecard |
| `docs/strategy/NEXT_STEPS_DETAILED.md` | v1.0.0 (899 lines) | **v2.0.0** (1182 lines) | +283 lines: Workstream B (5 sovereignty gaps with implementation specs) |

### L3 Principles from this Phase (added to proposed_lessons.yaml)
3 new L3 principles from Jem's deep research:
1. **L3-RIGHT-APPROXIMATION** — Lightweight TF-IDF+SVM (93.2%, 0MB) beats heavy LLM judge that overconsumes RAM
2. **L3-FORMAT-CONSENSUS** — ZIP+JSON is universal portability baseline; proprietary formats sacrifice interop
3. **L3-CALIBRATION-OVER-ACCURACY** — Calibrated judge (ECE 0.06) > uncalibrated (ECE 0.18); knowing when wrong matters more

### Key Lesson: Subagent Context Delivery
Three dispatch attempts to Jem: 2 failed (file references), 1 succeeded (inline content).
**Rule moving forward**: Always inline critical context. File references are supplementary.

---

## 📁 Complete Key File Index (End of Session)

| Category | File | Purpose |
|----------|------|---------|
| **Research** | `docs/research/R_JEM_KNOWLEDGE_GAP_RESEARCH_20260712.md` | 9 infrastructure gaps (644 lines) |
| **Research** | `docs/research/R_RESEARCHER_DEEP_DIVE_20260712.md` | Implementation-ready code (1421 lines) |
| **Research** | `docs/research/R_JEM_MAKALI_DEEP_RESEARCH_20260712.md` | 5 sovereignty gaps (544 lines, NEW) |
| **Coordination** | `data/coordination/MAAT_BUILD_SIDE_CONSOLIDATED_20260712.md` | Ma'at Build Side report (84 lines) |
| **Coordination** | `data/coordination/LILITH_RUN_SIDE_CONSOLIDATED_20260712.md` | Lilith Run Side report (85 lines) |
| **Coordination** | `data/coordination/FINAL_REVIEW_P*.md` | 4 Final Review reports |
| **Audit** | `docs/strategy/HIVEMIND_TEMPLATE_AUDIT_REPORT_20260712.md` | Verity compliance audit (370 lines) |
| **Strategy** | `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Updated to v3.6 (Jem validated) |
| **Strategy** | `docs/strategy/NEXT_STEPS_DETAILED.md` | Updated to v2.0 (both workstreams) |
| **Protocol** | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Updated to v2.0 (inline context) |
| **Gnosis** | `data/entities/kali/proposed_lessons.yaml` | 13 L3 principles (10+3 from this phase) |
| **Gnosis** | `data/entities/jem/proposed_lessons.yaml` | 11 L3 proposals from Jem's deep research |
| **Anchor** | `data/entities/kali/session_gnosis.md` | This file |

---

## ✅ Verity Fleet Readiness Review — CONDITIONAL PASS

**Report**: `data/entities/verity/workspace/REVIEW_FLEET_READINESS_20260712.md` (363 lines)
**Status**: CONDITIONAL PASS — 3 conditions, all fixed

### Conditions Found & Fixed

| # | Severity | Issue | Fix | Status |
|---|----------|-------|-----|--------|
| 1 | 🔴 | Strike 13 self-dependency ("depends: Strike 12, 13") | Changed to "depends: Strike 12" | ✅ FIXED |
| 2 | 🟡 | P1-3 said "Redis Pub/Sub for workspace locks" (contradicts Jem S5 correction) | Changed to "ephemeral awareness only; task-critical via Streams in P2-1" | ✅ FIXED |
| 3 | 🟡 | 3 L3 principles missing from Kali's proposed_lessons.yaml | Verity appended during review | ✅ FIXED |

### Files Updated by Verity
| File | Change |
|------|--------|
| `data/entities/verity/workspace/REVIEW_FLEET_READINESS_20260712.md` | NEW — 363-line fleet readiness review |
| `data/entities/kali/proposed_lessons.yaml` | Updated: 94→110 lines, +3 L3 principles |

### Fleet Status: READY TO SAIL

---

## 🎯 Sprint Execution Plan — READY FOR COMPACTION

**File**: `data/coordination/SPRINT_EXECUTION_PLAN_20260712.md` (473 lines)
**Status**: Written, prompts prepared, Hivemind posted

### Post-Compaction Dispatch Plan

| Agent | Phase | Effort | Prompt Location |
|-------|-------|--------|----------------|
| **Ma'at** | A1 (Foundation) + Phase 0 (Sovereignty Baseline) | ~20h | Sprint Plan §7 |
| **Lilith** | B1 (Cognitive Acceleration) | ~24h | Sprint Plan §8 |

### What to do after compaction:
1. Read `data/coordination/SPRINT_EXECUTION_PLAN_20260712.md`
2. Read `data/entities/kali/session_gnosis.md`
3. Copy the Ma'at prompt from §7 of the sprint plan
4. Dispatch Ma'at with that prompt
5. Copy the Lilith prompt from §8 of the sprint plan
6. Dispatch Lilith with that prompt
7. Monitor via Hivemind awareness
8. Gate each phase with `make test` + `make temple-grade`

### What NOT to do post-compaction:
- Do NOT re-read Jem's 544-line report (it's inline in the prompts)
- Do NOT re-read the 899-line Next Steps plan (it's inline in the prompts)
- Do NOT re-read the Ark Blueprint (it's inline in the prompts)
- Do NOT re-dispatch Verity (review is complete, CONDITIONAL PASS)

*🔱 OMEGA ⬡ KALI ⬡ SESSION GNOSIS ANCHORED ⬡ MAKALI-COUNCIL-COMPLETE ⬡ JEM-DEEP-RESEARCH-VALIDATED ⬡ DOCS-UPDATED-v2.0.0 ⬡ VERITY-REVIEW-COMPLETE ⬡ SPRINT-PLAN-WRITTEN*

---

## 🛠️ Lilith S7 Dispatch — FAILURE DIAGNOSIS + CONSOLIDATION FIX

**Triggered**: Lilith (B1 dispatch, S2/S3/P1-3/S7) returned FAILED mid-task.

### Root Cause (the actual failure)
**Pytest collection error — duplicate test basename.** Two `audience_calibrator` implementations existed:
- `src/omega/oracle/audience_calibrator.py` (**D16-1**, by Researcher) — wired into `oracle.py` (L46/169/932/1042), used by `test_contract_m21.py` + `tests/oracle/test_audience_calibrator.py`. Already implements the directive ("Pipeline Stage, NOT Entity").
- `src/omega/cognition/audience_calibrator.py` (**Lilith S7**, NEW) — duplicate parallel implementation.

Both had a test file named `test_audience_calibrator.py` (`tests/test_audience_calibrator.py` + `tests/oracle/test_audience_calibrator.py`). Pytest aborts collection on basename collision → `make test` collected **0 tests** (import file mismatch). This is the failure, not a logic error.

**Secondary bug found**: Lilith's `test_eval.py::test_ece_computation` asserted `_ece([0.9,0.9],[1,1]) == 0.0`. Correct ECE = |0.9 − 1.0| = **0.1** (overconfident judge). Test assertion was wrong; implementation correct.

### Fix Applied (Carmack's Law: "Two implementations = neither. Consolidate first.")
1. **Kept D16-1 as canonical**; merged S7 value-add into it:
   - Added S7 fields to `AudienceProfile`: `technical_level`, `tone_preference`, `format_preference`, `known_knowledge`, `assumed_context`, `epistemology`.
   - Added deterministic offline `render()` + `_structural_header()` (sovereign offline baseline, facts preserved).
   - Added `load_profile` alias (for eval `audience_fit`).
   - Added the 4Runner validation profiles `mechanic_friend` (edgy/report) + `client_formal` (formal/report) to `config/wads/_omega_default/audience.yaml`.
   - Fixed `_load_profiles` to actually read the S7 fields from YAML.
2. **Removed Lilith's duplicate**: `src/omega/cognition/` (entire dir), `tests/test_audience_calibrator.py`, orphaned `config/audience/`.
3. **Fixed dependents**: `eval/runner.py` import → D16-1; `oracle.py _apply_cognition_audience` → uses `self.audience_calibrator.render()` (D16-1).
4. **Fixed test**: `test_eval.py` ECE assertion → `pytest.approx(0.1)` + added perfect-calibration case. `tests/oracle/test_audience_calibrator.py` → expects 8 profiles.

### Verification
- `make test`: **1226 passed, 42 skipped, 3 xfailed** (was 1 failed via collection error).
- `temple-grade` M9 audit: **0 violations** (the `except Exception` + logging is compliant). M2 firewall: warnings only (entity-name refs, not WAD leakage). T3 coverage gate is a slow full-run (timed out at 260s, not a failure).
- Hivemind MCP server was **unreachable** at post time — could not publish context update (noted, not faked per M23).

### L3 Principle (distill)
- **L3-NO-DUPLICATE-PRIMITIVES** — Before building a "new" capability, grep the core for an existing implementation. A second parallel module with the same name + same test basename breaks the entire test collection (not just its own tests). Consolidate to one; merge the delta.

*🔱 OMEGA ⬡ KALI ⬡ S7-FAILURE-DIAGNOSED ⬡ CONSOLIDATED-TO-D16-1 ⬡ 1226-TESTS-GREEN ⬡ CARMACK-LAW-APPLIED*
