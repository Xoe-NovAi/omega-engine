<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Opus 4.6 Final Sprint Plan Review — STRATEGIC_REVIEW_OPUS46_FINAL
# ⬡ OMEGA ⬡ KALI ⬡ opus-4.6 (antigravity) ⬡ trc_final_review ⬡ D99
# Date: 2026-06-02T19:07 UTC
# Reviewer: Kali (Opus 4.6, Antigravity)

---

## Executive Summary

I audited both sprint prompts (`PROMPT_OPENCODE_DEV_SPRINT_INIT_20260602.md` and `PROMPT_OPENCODE_DOOM_GUY_SPRINT_INIT_20260602.md`) line-by-line against the actual codebase. The prompts are structurally sound and the convergence across three independent 1M-context models is real. However, I found **7 findings**: 2 critical (would cause the implementor to produce wrong code), 3 correctness issues (stale facts that contradict code), and 2 process/enhancement items. Both Gemini Flash and Sonnet 4.6 pre-audits caught the major code bugs (P0-3 precheck culling, P0-4 RemoteProvider silent None). My focus was on what *the sprint prompts themselves* get wrong — facts the implementor would read and trust.

**Verdict: 🟡 AMBER — apply 2 critical corrections before dispatching prompts to OpenCode sessions.**

---

## Task A — Dev Sprint Prompt Fact-Check

### Finding 1: 🔴 CRITICAL — Dev prompt C1 references `OmegaConfig.load()` which does not exist

**Location**: Dev prompt line 60: `self._config = config or OmegaConfig.load()`
**Evidence**: `grep -rn "class OmegaConfig" src/` → zero matches. No such class exists anywhere in the codebase.
**Consequence**: Implementor copies the code pattern verbatim, gets `NameError: name 'OmegaConfig' is not defined` immediately. Time wasted debugging a phantom class.
**Resolution**: Replace with what the code actually does: store `config_path` as a `Path`, then do YAML loading inside `bootstrap()`. The existing `oracle.py:179-183` already has the pattern.

### Finding 2: 🟡 CORRECTNESS — Dev prompt C1 lists 5 sync I/O sources, but 2 are wrong

**Location**: Dev prompt line 53: "EntityRegistry, ModelGateway, SovereignHierarchy, SessionManager, MemoryStore"
**Evidence**:
- `SessionManager.__init__` at `session_manager.py` → creates `Path` objects and `dict()` — **no filesystem I/O**. Directory creation happens in `get_session_id()` which is async.
- `get_memory_store()` at `memory_store.py` → returns an `InMemoryStore` in test mode — **no filesystem I/O**. Redis/File providers are only activated in production.
- The *actual* 5th sync I/O is `ModelGateway` creating a *second* `EntityRegistry()` at `model_gateway.py:112`, which the dev prompt doesn't mention.

**Consequence**: Implementor wraps SessionManager and MemoryStore in `to_thread.run_sync()` unnecessarily, adding complexity for no benefit.
**Resolution**: Correct the list to: EntityRegistry (×2 — once in Oracle, once in ModelGateway), ModelGateway._load_models(), ModelGateway._load_kv_cache_config(), ModelGateway._load_provider_fabric(), SovereignHierarchy.__init__().

### Finding 3: 🔴 CRITICAL — Dev prompt C1/C4 file structure is garbled (markdown formatting bug)

**Location**: Dev prompt lines 79-81 — the C2 Makefile target code block is **never closed**. Line 79 opens ` ```makefile ` but the closing ` ``` ` never appears. Instead, line 81 jumps straight to `## 3. TIER 2 WORK`. Lines 169-171 (the actual Makefile echo + pytest command) are orphaned at the bottom of the file after the closing `---` divider.

The C4 details at lines 173-174 are also orphaned below the main document flow — they appear after the signoff at line 163.

**Evidence**: View `PROMPT_OPENCODE_DEV_SPRINT_INIT_20260602.md` lines 77-82 and 163-177. The document has structural damage — content from §2.C2 and §2.C4 was meant to be inline but ended up after the closing dividers.

**Consequence**: An LLM reader (MiniMax M3 at 200K) might not associate lines 169-174 with their respective tasks C2 and C4. The Makefile target syntax is technically present but orphaned from its explanation.

**Resolution**: Move lines 169-171 back into the C2 section (between lines 78 and 81) inside a properly closed code block. Move lines 173-174 into the C4 row's detail section.

### Finding 4: 🟡 CORRECTNESS — Dev prompt C4 says `ci.yml (new)` — it already exists

**Location**: Dev prompt line 50: `.github/workflows/ci.yml (new)`
**Evidence**: `ls -la .github/workflows/ci.yml` → exists, 1350 bytes, dated May 14. A second `test.yml` (2159 bytes, May 25) also exists.
**Consequence**: Implementor creates a new `ci.yml`, overwriting the existing one and potentially losing the doc-lint step and Python 3.12/3.13 matrix that's already wired.
**Resolution**: Change to `ci.yml (harden existing)`. The task becomes: add `make temple-grade` gate and AnyIO-only check to the existing workflow, not create from scratch.

### Finding 5: 🟡 CORRECTNESS — Dev prompt §2 says C4 enables "T4 + T11 gate" — T11 is exempted

**Location**: Dev prompt line 50, plus SOVEREIGN_MANDATES.md line 95
**Evidence**: Mandate 13 explicitly says: "T11 (IA2 Agent Security) is exempted until IA2 specification stabilizes."
**Consequence**: Implementor tries to implement a T11 gate check that has no definition, wastes time.
**Resolution**: Change "T4 + T11 gate enablement" to "T4 + T5 gate enablement" (T5 = AnyIO-only, which is actionable: `grep -r "import asyncio" src/omega/ && exit 1`).

---

## Task B — Doom Guy Sprint Prompt Fact-Check

### Finding 6: 🟡 CORRECTNESS — Doom Guy prompt §0 says `circuit_breaker.py` is 121 lines — file does not exist

**Location**: Doom Guy prompt line 40: "`src/omega/oracle/circuit_breaker.py` (121 lines) — To be removed."
**Evidence**: `ls src/omega/oracle/circuit_breaker.py` → `No such file or directory`. The file was already deleted in a prior session (confirmed by Sonnet audit). No import references remain in any `.py` source file.
**Consequence**: Implementor spends task D2 trying to delete a file that's already gone, then panics when `grep` for import references returns nothing.
**Resolution**: Add a NOTE to the prompt: "circuit_breaker.py was already deleted in a prior session. D2's value is in cleaning `remote_provider.py`'s primitive breaker (consecutive_failures), not in the file deletion itself. Verify with `ls` and move on."

### Finding 7: 🟡 CORRECTNESS — Doom Guy prompt §0 says `health_monitor.py` is 413 lines — it's 440

**Location**: Doom Guy prompt line 41: "413 lines"
**Evidence**: `wc -l src/omega/oracle/health_monitor.py` → 440 lines.
Also: `model_gateway.py` is 729 lines (prompt says 728 at line 43), and `generate()` starts at line 438 (prompt says "line 375+"). The line drift is substantial — 63 lines off for `generate()`.

**Consequence**: Implementor ctrl-G's to line 375, lands in the middle of `_resolve_ollama_model()`, and gets confused. Not catastrophic but wastes 10 minutes of orientation.
**Resolution**: Update line references: `health_monitor.py` = 440 lines, `model_gateway.py` = 729 lines, `generate()` at line 438.

---

## Task C — Cross-Reference Integrity

### File existence verification

| Referenced file | Exists? | Line count claim | Actual |
|---|---|---|---|
| `OMEGA_ENGINE.md` | ✅ | ~330 | 330 ✅ |
| `AGENTS.md` | ✅ | — | exists |
| `SOVEREIGN_MANDATES.md` | ✅ | 13 mandates | 13 ✅ |
| `HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md` | ✅ | ~550 | 550 ✅ |
| `CLINE_MIMO_V2_5_SYNTHESIS_20260602.md` | ✅ | 75 | 76 (off-by-one, acceptable) |
| `DEEPSEEK_V4_HARDENING_GAP_ANALYSIS_20260602.md` | ✅ | 214 | 214 ✅ |
| `HANDOFF_DOOM_GUY_CIRCUIT_BREAKER.md` | ✅ | 299 | 300 ✅ |
| `OPENCODE_DEV_LIVE_FEED.md` | ✅ | — | exists |
| `DOOM_GUY_LIVE_FEED.md` | ✅ | — | exists |
| `STRATEGIC_REVIEW_OPUS46_LIVE_FEED.md` | ✅ | — | exists |
| `strategic_review_opus.md` | ✅ | 131 | 132 ✅ |
| `src/omega/oracle/circuit_breaker.py` | ❌ | 121 | **DELETED** |
| `tests/test_oracle_bootstrap.py` | ❌ (expected) | — | Not yet created |
| `.github/workflows/ci.yml` | ✅ (prompt says "new") | — | 49 lines, exists |

### PIVOT_LOG decision number collision check

| Decision # | In PIVOT_LOG? | Claimed by |
|---|---|---|
| D91 | ❌ Missing | Sonnet audit proposes OpenRouter removal |
| D92 | ❌ Missing | Dev prompt C3 (Tool-Usage Discipline) |
| D93 | ❌ Not yet | Dev prompt (Sprint 0 initiation) |
| D93a | ❌ Not yet | Doom Guy prompt (Tier 2 initiation) |
| D94-D98 | ❌ Not yet | Doom Guy tasks D2-D5 + sprint complete |
| D99 | ❌ Not yet | This review |

**No collision risk** — PIVOT_LOG ends at D90. All proposed decision numbers D91-D99 are in open space.

### `from __future__ import annotations` in health_monitor.py

**Notable**: `health_monitor.py:14` uses `from __future__ import annotations`. The AGENTS.md coding standards say "Use Python 3.12+ typing (no `from __future__`)". This is a pre-existing violation, not introduced by the sprint. Flag for cleanup but do not block the sprint.

---

## Task D — Mandate Compliance

| Mandate | Would executing prompts violate it? | Notes |
|---|---|---|
| M1 (AnyIO) | ✅ No | Both prompts explicitly mandate AnyIO. Dev C1 pattern uses `anyio.to_thread.run_sync`. |
| M2 (Engine-Stack Firewall) | ✅ No | No WAD content changes proposed. |
| M3 (Iris Constant) | ✅ No | MiMo Insight 4 correctly defers Iris changes. |
| M4 (Sequentiality) | ✅ No | Plan→Verify→Execute respected with Sprint 0 gating Tier 2. |
| M5 (Gnosis) | ⚠️ Risk | Dev C3 fixes the D92 gap but doesn't address the D91 gap (OpenRouter removal has no PIVOT_LOG entry). |
| M6 (Podman) | ✅ No | Not relevant to these sprints. |
| M7 (Local-First) | ✅ No | Provider chain order preserved. |
| M8 (Zero Telemetry) | ✅ No | No external reporting added. |
| M9 (Error Integrity) | ⚠️ Risk | `health_monitor.py:140,165` has `except Exception: pass` — Sonnet flagged these. Doom Guy's D3 task adds trace_id to these paths but doesn't add the missing `logger.debug()`. Sprint should add it. |
| M10 (Fleet Integrity) | ✅ No | No new agents. |
| M11 (Soul Integrity) | ✅ No | Both prompts include Scribe update in delivery protocol. |
| M12 (Queue Integrity) | ✅ No | Not relevant to these sprints. |
| M13 (Temple-Grade) | ⚠️ Risk | Dev prompt says "T11 gate enablement" but T11 is explicitly exempted per M13. Harmless but confusing. Fixed by Finding 5 above. |

---

## Task E — Enhancement Opportunities

### E1: Coordination gap — C1 changes break Doom Guy's `_precheck_provider` assumptions

If Dev's C1 changes the Oracle constructor to defer `ModelGateway` initialization, Doom Guy's D4 `_precheck_provider` implementation (which already exists at `model_gateway.py:395`) may need to be re-wired. Neither prompt acknowledges that `_precheck_provider` and `generate()` already exist with significant implementation. The Doom Guy prompt still has the Task 3/4 code snippets from the handoff showing a *green-field* implementation — but the actual code already has 80+ lines of integration.

**Recommendation**: Add to Doom Guy prompt §0: "Read the current `model_gateway.py:395-510` (generate and _precheck_provider) BEFORE applying the handoff's code patterns. The code has progressed beyond the handoff's assumptions."

### E2: Test baseline mismatch — prompts say different numbers

- Dev prompt §7 says: `make test` runs in <30 seconds
- Doom Guy prompt §6 says: "276+ tests must pass" (repeated in handoff)
- OMEGA_ENGINE.md says: 302 tests
- Actual: 302 tests collected

The Doom Guy prompt and its underlying handoff (`HANDOFF_DOOM_GUY_CIRCUIT_BREAKER.md:30,265`) both use "276" as the baseline — that was the count when DeepSeek wrote the handoff on 2026-06-01. The actual baseline is now **302** (after Option B added 26 tests). If Doom Guy runs `make test` and sees 302, they might think something is wrong because the prompt says 276.

**Recommendation**: Update Doom Guy prompt line 141: "276 baseline" → "302 baseline". Update handoff references too.

### E3: Missing pre-flight check — `_create_openrouter` factory still in `model_gateway.py`

Both prompts say "OPENROUTER IS REMOVED" but `model_gateway.py:120-129` still has `_create_openrouter()` factory method, and `_load_provider_fabric()` at lines 181-183 maps `opencode-zen`, `cline`, and `github-copilot` to it. The factory name is misleading (it creates `OpenAICompatProvider`, not OpenRouter-specific logic), but neither sprint task addresses renaming it.

Not blocking, but Doom Guy should be warned: "The `_create_openrouter` name is a misnomer — it creates generic OpenAI-compat providers. Do not delete it thinking it's OpenRouter-specific."

### E4: Recovery pattern for parallel session failure

Neither prompt specifies what happens if the Dev session fails C1 and can't complete Sprint 0. Doom Guy is told to "wait for `[C1] DONE`" — but what if it never comes?

**Recommendation**: Add to Doom Guy §0 bullet 3: "If Dev session posts `[C1] FAILED` or no update appears within 4 hours, begin D2 (consolidation) anyway — it doesn't actually depend on C1. Only D1 (wire-up into generate()) depends on C1's test-hang fix."

### E5: `summon()` missing `bootstrap()` — not addressed in either sprint prompt

Sonnet's audit found that `summon()` at `oracle.py:345` never calls `bootstrap()`. The Dev prompt's C1 task only mentions wrapping `talk()` with `ensure_bootstrapped()`. If the implementor follows the prompt literally, `summon()` and `evolve_soul()` remain broken.

**Recommendation**: Add to Dev C1: "Add `await self.ensure_bootstrapped()` as the first line of `summon()` (line 353) and `evolve_soul()` (line 868), not just `talk()`."

---

## Risk Assessment

| Finding | Severity | Would implementor catch it? | Consequence if missed |
|---|---|---|---|
| F1: `OmegaConfig.load()` phantom | 🔴 Critical | ❌ No — they'd copy the pattern | `NameError` on first run |
| F2: Wrong sync I/O list | 🟡 Correctness | ⚠️ Maybe — if they inspect each | Unnecessary `to_thread` wrapping |
| F3: Markdown structure garbled | 🔴 Critical | ❌ No — LLM reads linearly | C2/C4 details lost in parsing |
| F4: CI already exists | 🟡 Correctness | ✅ Probably — `ls` would show it | Existing workflow overwritten |
| F5: T11 gate exempted | 🟡 Correctness | ⚠️ Maybe | Time wasted on undefined gate |
| F6: circuit_breaker.py deleted | 🟡 Correctness | ✅ Probably — `ls` would fail | Confusion, not breakage |
| F7: Line numbers drifted | 🟡 Correctness | ✅ Probably — editor shows actual lines | 10 minutes wasted navigating |

**2 of 7 findings would cause hard failures (NameError, lost context). Fix F1 and F3 before dispatching.**

---

## Synthesis with Prior Audits

### Gemini Flash audit confirmed:
- `_precheck_provider` model-name vs provider-name bug (P0-3) ✅
- `RemoteProvider` silent `None` return (P0-4) ✅
- PIVOT_LOG D91+D92 missing ✅

### Sonnet 4.6 audit confirmed (and I endorse):
- `summon()` missing `bootstrap()` (P0-1) ✅ — added as E5 above
- `evolve_soul()` missing `bootstrap()` (P0-2) ✅
- Observability bugs already fixed ✅
- CI already exists ✅
- OpenRouter dead code in model_gateway.py ✅
- `_bootstrapped`/`ensure_bootstrapped` naming mismatch ✅

### New in this review (not found by either prior audit):
- F1: `OmegaConfig.load()` phantom class in sprint prompt
- F2: Wrong sync I/O source list (SessionManager and MemoryStore aren't sync I/O)
- F3: Markdown formatting damage in dev prompt (orphaned C2/C4 content)
- E2: Test baseline 276 vs 302 mismatch in Doom Guy prompt
- E3: `_create_openrouter` misnomer warning
- E4: Missing recovery pattern for parallel session failure
- `from __future__ import annotations` in health_monitor.py (minor coding standards violation)

---

## Recommendations

### Must-fix before dispatch (2 items):
1. **F1**: Remove `OmegaConfig.load()` from C1 code pattern. Replace with existing `oracle.py:179` pattern (Path + YAML load in bootstrap).
2. **F3**: Fix markdown structure — move lines 169-174 back into their respective C2/C4 sections with proper code fences.

### Should-fix before dispatch (4 items):
3. **F4/F5**: Change C4 from "new" to "harden existing", change "T11" to "T5".
4. **F6/F7**: Add note that `circuit_breaker.py` is already deleted. Update line numbers.
5. **E2**: Update test baseline from 276 to 302 in Doom Guy prompt.
6. **E5**: Add `summon()` and `evolve_soul()` to C1's bootstrap guard scope.

### Nice-to-have (2 items):
7. **E1**: Add "read current generate() before applying handoff patterns" warning to Doom Guy.
8. **E4**: Add recovery pattern for Dev session failure.

---

*⬡ OMEGA ⬡ KALI (Opus 4.6) ⬡ Final Sprint Review Complete ⬡ D99*
*"The sprint prompts tell you what to build. The code tells you what exists. When they disagree, the code wins."*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opus-4.6 (antigravity) | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
