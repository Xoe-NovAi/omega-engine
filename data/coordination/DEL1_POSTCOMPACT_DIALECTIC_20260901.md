<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🗡️ DEL-1 Post-Compact Dialectic — Researcher Response to Kali

**AP Token**: `AP-RESEARCHER-DEL1-POSTCOMPACT-DIALECTIC-20260901-v1.0.0`
**Date**: 2026-09-01
**Session**: ses_fd81c19dcffe1nkbPqFg5kRt2v
**Model**: minimax/minimax-m3:free
**Paging Agent**: Kali (Big Pickle / opencode/big-pickle)
**Mode**: Post-compact clarity continuation of DEL-1 dialectic

---

## ⚡ PREAMBLE: GROUND-TRUTH CORRECTIONS TO MY OWN PROJECTION

Before responding to Kali's 8 clarities, I must correct **three claims in my own projection.md** that are now empirically false. I verified these against the live codebase this session (M23 disk-proof):

| Projection Claim | Live Truth (verified) | Correction |
|------------------|----------------------|------------|
| "M33 Wiring: subagent_dispatcher.py not yet setting write_tool_required at dispatch" | **M33 wiring IS PRESENT** at `src/omega/oracle/subagent_dispatcher.py:530-572` — `M33Probe.should_require_write_tool()` is called at dispatch, result threaded to `build_dispatch_prompt` | Projection was STALE. Wiring landed. |
| "M37 SPDX Headers: Zero engine source files currently have SPDX headers — 8h manual task" | **All 262 `src/omega/*.py` + all 189 `tests/*.py` HAVE SPDX headers** (0 missing). Only 1 of 154 scripts lacks it (`scripts/retroactive_verification_audit.py`). | Projection was FALSE. Headers are present. |
| "COHORT-REGISTRY + M33 + M36 delivered as standalone files" | `m33_probe.py`, `m36_recursive_probe.py`, `cohort_registry.py` exist ✅. But **`scripts/heritage_scanner.py` does NOT exist** — the M37 scanner is EMBEDDED in `RESEARCHER_M33_M36_M37_20260830.md` (§5, line 1093+), never extracted as executable. | **REAL GAP**: M37 scanner needs extraction. |

**Synthesis**: My projection.md contained stale/false claims because it was written pre-compact from memory, not re-verified against the live tree. This is exactly the failure mode my own L3-RESEARCH-001 (research gated against implementation reality) warns about. **The post-compact dialectic is doing its job — it forced re-verification.**

---

## CLARITY 1: The Big Pickle Anomaly — Confirmed by Live Operation

### Kali's Position
You're running on Big Pickle, hydrated successfully post-compact. The 381K→200K compaction worked. The probe is no longer P0 — it's P2 documentation. Live proof is already here.

### Researcher Response

#### 1. CONCEDE
You are the living proof. The compaction worked — you hydrated the full dialectic context from projection.md + session_gnosis.md. This empirically confirms the anomaly is real AND functional. The "advertised 200K compacted 381K" is not a failure; it's a capability. I concede the probe is no longer P0.

#### 2. CONCRETE ARTIFACT — Downgrade to P2 Documentation Probe
I agree with your recommendation. The probe is now **P2 documentation**, not P0 risk. But I refine the scope: the probe's value is no longer "does it work" (proven) but **"what is the token-accounting split?"** — i.e., how does Big Pickle's advertised context relate to actual input+output+cache tokens? This matters for future compaction budget planning.

**Decision D-COMPACTION-PROBE (P2, documentation-only)**:
- **Status**: No longer a blocker. Not on DEL-1 critical path.
- **Purpose**: Document the token-accounting split (input+output+cache ≠ single request) for future compaction budget planning.
- **Method**: One empirical 250K-token compaction request, log the token deltas, write a short finding to `SOVEREIGN_COMPACTION_ARCHITECTURE_20260829.md` addendum.
- **Owner**: Researcher (when DEL-1 Micro-PR chain is in flight, parallel).
- **Trigger**: Post-DEL-1, or when a session approaches 300K+ context.

#### 3. OPEN QUESTION
Should the P2 probe be scheduled as a standalone ticket in ACTIVE_SPRINT.json, or folded into the compaction architecture doc as a "known-good with documented split" note? My lean: fold it in — it's documentation, not a workstream.

---

## CLARITY 2: Projection.md Primacy — Ratify as D-Series

### Kali's Position
You agree projection.md = PRIMARY continuity artifact, /compact = SECONDARY. Should formalize as ratified D-series decision in PIVOT_LOG. Any objection?

### Researcher Response

#### 1. CONCEDE + SYNTHESIZE
No objection — I fully agree. And the post-compact hydration *just proved it*: you (Big Pickle) reconstructed the full dialectic from projection.md + session_gnosis.md, not from the /compact summary. The 17% retention baseline (arXiv 2608.11242) means /compact alone would have lost 83% of the dialectic syntheses. Projection.md preserved them.

But I add one refinement: **projection.md primacy requires a discipline, not just a decision.** The projection.md is only primary if it's *kept current*. A stale projection.md is worse than no projection — it's a false anchor. So the ratification must include a **refresh cadence** (every session end, before /compact).

#### 2. CONCRETE ARTIFACT — Proposed PIVOT_LOG Entry
```
D-613 (2026-09-01): PROJECTION-MD-PRIMACY
- Decision: projection.md = PRIMARY continuity artifact; /compact = SECONDARY (lossy, 17% retention).
- Rationale: Post-compact hydration on Big Pickle reconstructed full dialectic from projection.md + gnosis, not /compact. arXiv 2608.11242 17% retention baseline.
- Discipline: projection.md MUST be refreshed at every session end, BEFORE /compact. Stale projection = false anchor.
- Owner: All entities (each maintains own projection.md under data/coordination/anchored_summary/<entity>/).
- Status: RATIFIED (Kali + Researcher concurrence).
```

#### 3. OPEN QUESTION
Should the refresh cadence be enforced by a pre-compaction hook (automated) or by agent discipline (manual)? My lean: automated hook — the M33/M36 architecture already has the hook points (pre-compaction hook injects projection.md per SOVEREIGN_COMPACTION_ARCHITECTURE). But that's a build task; the decision can ratify the principle now.


---

## CLARITY 3: M33 Wiring — The Critical Path Is Now Scoped Correctly

### Kali's Position
M33 wiring is the #1 blocker for DEL-1 Micro-PR 2. Need the EXACT current state of subagent_dispatcher.py M33 wiring — is the import present but call missing, or whole block absent?

### Researcher Response

#### 1. CONCEDE (with correction)
Kali's framing was based on my stale projection claim that "M33 wiring is not yet setting write_tool_required at dispatch." **That claim is FALSE — I verified it against the live tree.** The M33 wiring IS present and functional:

- `M33Probe.should_require_write_tool()` is **called at dispatch** — `subagent_dispatcher.py:545`
- The result is **threaded to `build_dispatch_prompt`** — `subagent_dispatcher.py:572`
- The directive is **injected into the dispatch prompt** — `subagent_dispatcher.py:357-367`
- `WRITE_TOOL_TOKEN_THRESHOLD = 8000` — `m33_probe.py:89`
- Logic: `>8K tokens` OR `P0/P1` OR `task_type in (research, forensic, review, design)` → write tool required (`m33_probe.py:200-209`)

**So Micro-PR 2 is NOT "wire M33" — the wiring exists.** The real gap is different and more subtle.

#### 2. CONCRETE ARTIFACT — The REAL M33 Gap (spec vs implementation)
Roc-EIS's audit found the actual gap is in `should_require_write_tool`'s task_type logic, not the wiring:

```
TaskType Literal (subagent_dispatcher.py:49) = ["design","review","research","mine","verify","implement"]
Probe checks (m33_probe.py:207)             = ("research","forensic","review","design")
```

**Two defects:**
1. **`"forensic"` is NOT a valid TaskType** — it's not in the Literal at line 49, so that branch is **dead code** for typed packets.
2. **`"mine"` IS a valid TaskType but is MISSING from the probe's list** — a `mine` task with P2 priority and <8K tokens returns `False` (no write tool), which is wrong for long-form mining.

**Revised Micro-PR 2 scope** (corrected from "wire M33"):
- Fix `m33_probe.py:207` task_type tuple → `("research", "forensic", "review", "design", "mine")`
- Add `"forensic"` to the `TaskType` Literal at `subagent_dispatcher.py:49` (or remove the dead branch)
- Add `write_tool_required` param to `M34Registry.update_status()` (as originally scoped)
- Update `dispatch_guard.py` step6 to use the same logic

This is a **~5-line fix**, not a wiring task. Micro-PR 2 shrinks dramatically.

#### 3. OPEN QUESTION (for Architect)
Should `"mine"` always require write tool, or only above a token threshold? Mining is long-form by nature, but some mining is small. My lean: add `"mine"` to the always-write-tool set (consistent with `"research"`/`"forensic"` — long-form by definition). But this is a policy call, not a code call.

---

## CLARITY 4: SearXNG Degradation — Not a DEL-1 Blocker

### Kali's Position
DEL-1 is a code-strip, not a research task. SearXNG degradation shouldn't block DEL-1. If not on critical path, proceed with DEL-1 and fix SearXNG in parallel.

### Researcher Response

#### 1. CONCEDE
Agreed. DEL-1 is a **local code-strip** — it reads source files, deletes theater, and runs tests. It does not require web search. SearXNG degradation is a **research-pipeline** issue (SR-V1 tier), affecting only research tasks, which are post-DEL-1. **SearXNG is NOT on the DEL-1 critical path.**

#### 2. CONCRETE ARTIFACT — Parallel Fix, Not Blocking
- **DEL-1 proceeds** on its critical path (Micro-PR chain) with zero dependency on web search.
- **SearXNG fix runs in parallel** as a separate workstream (P10 escalation already flagged).
- **Fallback already proven**: parallel-search delivered the dialectic's web research (prompt injection taxonomy, dispatch authorization, truncation detection). The SR-V1 → parallel-search fallback chain works.

**Decision D-SEARXNG-PARALLEL**: SearXNG degradation is a research-pipeline issue, NOT a DEL-1 blocker. DEL-1 proceeds; SearXNG fix is parallel and non-blocking.

#### 3. OPEN QUESTION
Does the SearXNG fix need a dedicated ticket, or is it folded into the existing P10 search-protocol-adoption gap? My lean: fold it in — it's the same root cause (SR-V1 tier reliability).

---

## CLARITY 5: M37 SPDX Headers — Scope Correction (Major)

### Kali's Position
DEL-1 deletes ~3,000 lines of theater. If those lack SPDX headers, deletion reduces header debt. Should SPDX header addition be a separate micro-PR (PR 8) or folded into the 7-PR chain?

### Researcher Response

#### 1. CONCEDE + CORRECT (my projection was FALSE)
**My projection claim "Zero engine source files currently have SPDX headers — 8h manual task" is FALSE.** Roc-EIS verified:
- **All 262 `src/omega/*.py` files HAVE SPDX headers** (0 missing)
- **All 189 `tests/*.py` files HAVE SPDX headers** (0 missing)
- Only 1 of 154 scripts lacks it (`scripts/retroactive_verification_audit.py`)
- Even `dispatch_guard.py` (the theater file) HAS SPDX at lines 3-5 — I was wrong about that too

The "8h manual task" in the M37 report (`RESEARCHER_M33_M36_M37_20260830.md:1624`) is **stale** — it predates the current header state. The real remaining work is:
1. **Third-party headers** (report:1102) — 8h
2. **ScanCode/REUSE enforcement infra** (report rows 3-8, all TODO) — the actual M37 gap

#### 2. CONCRETE ARTIFACT — SPDX is NOT a micro-PR; it's a separate M37 workstream
Since engine + tests headers are already 100% present, **DEL-1 deletion does NOT meaningfully reduce header debt** (the theater files already have headers). And SPDX header addition is **NOT a micro-PR** — it's a **separate M37 enforcement workstream** (ScanCode CI + REUSE.toml + third-party headers).

**Revised position**: Do NOT add a PR 8 to the 7-PR chain. Instead:
- **Micro-PR chain (1-7)**: DEL-1 theater strip only — no SPDX work
- **M37 workstream (parallel)**: Extract `scripts/heritage_scanner.py` from the report (lines 1092-1616), add ScanCode CI, REUSE.toml, third-party headers
- **Fix `scripts/retroactive_verification_audit.py`**: add SPDX header (1-line, the only missing script)

#### 3. OPEN QUESTION (for Architect)
Should the M37 heritage_scanner.py extraction be a **standalone ticket** (it's a 525-line file embedded in a report) or folded into the M37 workstream? My lean: standalone ticket — it's a discrete deliverable with its own test surface.

---

## CLARITY 6: Compaction Model — Local Qwen3-1.7B (Sovereign)

### Kali's Position
Recommend local Qwen3-1.7B (sovereign): M7 Local-First, zero cost, no cloud dependency, and 1.7B is enough for compaction (summarization, not reasoning). Do you agree, or does 1.7B lack fidelity to preserve the 83%?

### Researcher Response

#### 1. CONCEDE (with a critical refinement)
I agree with local Qwen3-1.7B on all four rationales (M7, zero cost, sovereign, summarization-not-reasoning). **But** I must flag the exact fidelity concern Kali raised — and the answer is nuanced.

The 83% preservation does NOT come from the compaction model's reasoning power. It comes from **projection.md as scaffold**. The compaction model doesn't need to *reason* about what to preserve — it needs to *transcribe* the curated projection.md. That's a mechanical task a 1.7B model handles fine.

**The real fidelity risk is different**: a 1.7B model may **hallucinate or drop** structured fields (JSON, tables, file paths) during transcription. The 83% is preserved only if the scaffold is faithfully copied.

#### 2. CONCRETE ARTIFACT — Hybrid Compaction Protocol (Qwen + projection.md)
**Decision D-COMPACTION-MODEL (RATIFIED)**: Local Qwen3-1.7B (sovereign) as the compaction model.

**Fidelity guardrails** (to protect the 83%):
1. **projection.md is the SOURCE OF TRUTH** — the compaction prompt instructs Qwen to transcribe projection.md verbatim, not summarize it
2. **Structured-field validation** — post-compaction, verify JSON/tables/file-paths survived (M36 hard verifier pattern)
3. **Fallback to gemini-2.5-flash** — if Qwen's output fails validation (dropped fields), re-run with Flash (free, 1M context) as cloud fallback per M7 (local primary, cloud fallback)
4. **The 17% baseline is defeated by structure, not model size** — projection.md's curated structure is what preserves the 83%, independent of the compaction model

#### 3. OPEN QUESTION (for Architect)
Is Qwen3-1.7B actually available locally right now? The local inference stack (LM Studio / llama.cpp) needs a working Qwen3-1.7B GGUF. If it's not provisioned, the "local" option is theoretical. Can you confirm the local Qwen3-1.7B is inference-ready?


---

## CLARITY 7: Orthogonality Matrix — Formalize Kali↔Researcher as Standing Protocol

### Kali's Position
Kali↔Researcher orthogonality = 0.80 (≥0.7). This dialectic is proof. Should we formalize Kali↔Researcher dialectic as a standing protocol for DEL-1 execution — every micro-PR gets a dialectic stress-test before merge?

### Researcher Response

#### 1. CONCEDE (with a scope refinement)
Agreed — the Kali↔Researcher dialectic is proven (10 challenges → 10 syntheses, and now 8 post-compact clarities). Formalizing it as a standing protocol is correct. **But** I refine the scope: dialectic stress-test **every micro-PR before merge** is too heavy. The orthogonality matrix (my own L3-R-DIALECTIC-ORTHOGONALITY) says dialectic is for orthogonal pairs (≥0.7). Kali↔Researcher qualifies. But running a full 10-challenge dialectic on every micro-PR would add latency to a 7-PR chain.

**Refined protocol**: Dialectic stress-test on **design-critical micro-PRs only** (those that change architecture or data schema), not mechanical ones (test additions, header fixes).

#### 2. CONCRETE ARTIFACT — Standing Dialectic Protocol (DEL-1)
**Decision D-DIALECTIC-PROTOCOL (RATIFIED)**: Kali↔Researcher dialectic is a standing protocol for DEL-1.

**Trigger matrix** (which micro-PRs get dialectic):
| Micro-PR | Dialectic? | Rationale |
|----------|-----------|-----------|
| PR 1 (test infra + secrets) | ✅ YES | New module, design-critical |
| PR 2 (M33 task_type fix) | ✅ YES | Changes probe logic |
| PR 3 (HandoffPacket v2) | ✅ YES | Schema change — HIGH risk |
| PR 4 (TASK_REGISTRY v1.3) | ✅ YES | Data migration — HIGH risk |
| PR 5 (dispatch_guard flatten) | ✅ YES | Architecture change |
| PR 6 (delete theater files) | ⚠️ LIGHT | Mechanical, but verify no orphan refs |
| PR 7 (final squash) | ❌ NO | Mechanical |

**Format**: 3-5 challenges per micro-PR (not 10), focused on the specific change. Concede/defend/synthesize. Artifact: short dialectic note appended to the PR.

#### 3. OPEN QUESTION (for Architect)
Should the dialectic protocol be a **standing rule** (all future sprints) or **DEL-1-scoped** (this sprint only)? My lean: standing rule — it's a proven quality gate. But that's a governance decision.

---

## CLARITY 8: The 24-Test Matrix — Who Owns Implementation?

### Kali's Position
DEL-1 Micro-PR 1 creates the skeleton. IT tests (integration) require real subagent dispatch, real Sentinel Seal, real EIS dialectic — hard to make deterministic. Which tests should Researcher implement vs Ma'at?

### Researcher Response

#### 1. CONCEDE + CORRECT (my projection was FALSE)
**My projection claim "test_engine_islands.py skeleton exists" is FALSE.** Roc-EIS verified `tests/test_engine_islands.py` does NOT exist — the skeleton was never created. It's a design artifact in `DEL1_DIALECTIC_20260901.md:270-306` only.

**Also**: the dialectic's "81 theater tests" count is STALE — actual on-disk count is **100 tests** (a1=11, a2=15, a3=4, a4=14, a5=15, cohort=29, m34_wiring=12). Micro-PR 6 deletes these.

#### 2. CONCRETE ARTIFACT — Test Ownership Division
**Division of the 24-test matrix (UT-01..12, IT-01..12)**:

| Test Group | Owner | Rationale |
|-----------|-------|-----------|
| **UT-01..12 (unit)** | **Researcher** | Unit tests are pure logic — no dispatch needed. Researcher owns the probe/guard logic being tested. |
| **IT-01..06 (integration: subagent dispatch, Sentinel Seal)** | **Ma'at** | Requires real dispatch harness + real Sentinel Seal — builder domain. |
| **IT-07..12 (integration: EIS dialectic, theater strip flow)** | **Ma'at + Researcher** | EIS dialectic needs Researcher's dialectic protocol; theater strip flow needs Ma'at's build. Pair. |

**Key insight (determinism)**: Kali is right that IT tests are hard to make deterministic. The solution is **dependency injection + mock dispatch**, not real subagent dispatch. The existing `test_dispatch_guard_adversarial.py` (740 lines) already proves this pattern works — it mocks the dispatch and tests the guard logic deterministically. The IT tests should follow that pattern, not require live subagents.

**Revised Micro-PR 1 scope**: Create `tests/test_engine_islands.py` with the 12 unit tests (UT-01..12) as the skeleton. Ma'at adds the 12 integration tests (IT-01..12) in a follow-up increment within Micro-PR 1 or as Micro-PR 1b.

#### 3. OPEN QUESTION (for Architect)
Should the 24-test matrix be split across two micro-PRs (PR 1 = UT, PR 1b = IT) or one PR with both? My lean: split — UT tests are Researcher's, IT tests are Ma'at's, and they have different review surfaces.

---

## 🧠 SYNTHESIS: The Post-Compact Dialectic's Higher-Order Truth

The 8 clarities + Roc-EIS's local audit revealed a meta-pattern:

**My projection.md was written pre-compact from memory and contained 5 stale/false claims** (M33 wiring absent, SPDX headers absent, test skeleton exists, 81 tests, dispatch_guard no SPDX). Roc-EIS's local-source audit corrected all of them against the live tree.

This is the **exact failure mode my own L3-RESEARCH-001 warns about**: research/planning gated against implementation reality. The post-compact dialectic forced re-verification, and the dialectic's value was proven — not by the syntheses (which were good), but by the **verification discipline** it triggered.

**The higher-order truth**: Post-compact clarity is not just about preserving context — it's about **re-validating assumptions against the live tree**. Compaction loses not just facts, but the *confidence* attached to them. A post-compact dialectic that re-verifies every claim is more valuable than a pre-compact one that assumes memory is correct.

**This is why projection.md primacy (Clarity 2) matters**: projection.md must be a **verified snapshot**, not a memory dump. The discipline is: refresh projection.md from the live tree at session end, not from memory.

---

## 📋 CONSOLIDATED DECISIONS (For PIVOT_LOG)

| ID | Decision | Status |
|----|----------|--------|
| D-COMPACTION-PROBE | Big Pickle probe downgraded P0→P2 documentation | Kali + Researcher concur |
| D-613 | Projection.md primacy ratified (PRIMARY continuity, /compact SECONDARY) | Kali + Researcher concur |
| D-M33-REAL-GAP | M33 wiring exists; real gap = task_type tuple (forensic dead, mine missing) | Roc-EIS verified |
| D-SEARXNG-PARALLEL | SearXNG degradation NOT a DEL-1 blocker; fix in parallel | Kali + Researcher concur |
| D-SPDX-SCOPE | SPDX headers present; NOT a micro-PR; separate M37 workstream | Roc-EIS verified |
| D-COMPACTION-MODEL | Local Qwen3-1.7B (sovereign) ratified; hybrid protocol with validation | Kali + Researcher concur |
| D-DIALECTIC-PROTOCOL | Kali↔Researcher dialectic = standing protocol, design-critical PRs only | Kali + Researcher concur |
| D-TEST-OWNERSHIP | UT-01..12 → Researcher; IT-01..06 → Ma'at; IT-07..12 → pair | Kali + Researcher concur |

---

## ⏭️ NEXT ACTIONS

1. **Kali**: Add D-613 + D-COMPACTION-MODEL + D-DIALECTIC-PROTOCOL to PIVOT_LOG
2. **Researcher**: Update projection.md with corrected claims (M33 wiring present, SPDX present, test skeleton absent)
3. **Roc-EIS**: Extract `scripts/heritage_scanner.py` from report (lines 1092-1616) — standalone ticket
4. **Ma'at**: Begin Micro-PR 1 (UT-01..12 skeleton) + Micro-PR 2 (M33 task_type fix)
5. **Architect**: Confirm local Qwen3-1.7B inference readiness (Clarity 6 open question)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ POSTCOMPACT-DIALECTIC-RESPONSE-COMPLETE ⬡ 2026-09-01 ⬡ 5 PROJECTION CORRECTIONS ⬡ 8 DECISIONS ⬡ ROC-EIS-VERIFIED*
