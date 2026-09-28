<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JEM EIS — PROJECTION (v4.0.0, 2026-09-28)
**AP Token**: `AP-JEM-v5.0.0`
⬡ OMEGA ⬡ JEM ⬡ `opencode/space-bunny-free` ⬡ opencode ⬡ trc_projection ⬡ **COMPACTION-READY**

**Session**: `ses_019311199ffeuEOgO7DfC7XDWG` | **Agent**: `jem` | **Variant**: `high` | **OpenCode**: `1.18.15`

---

## §1 — M22 PROVENANCE

| Field | Value | Source |
|-------|-------|--------|
| Model ID | `space-bunny-free` | session metadata |
| Provider | `opencode` | session metadata |
| Variant | `high` | session metadata |
| **Correction** | Prior turn reported `google/gemini-3.8-flash` — **false**, unmeasured | see JEM-PROVENANCE-001 |

Model IDs are emitted only from runtime metadata read in-turn. Narrative context
is not a telemetry source.

---

## §2 — GROUND TRUTH (as of 2026-09-28)

| # | Fact | Verification status |
|---|------|---------------------|
| 1 | Public Debut **LIVE** — PR #4 merged to `main` @ `268528e7`; repo **public** | Received from MaKaLi; not independently re-verified this session |
| 2 | Gitleaks secret gate active, `useDefault=true`; `requires_engine` semver enforcement live | Received; not re-run per directive |
| 3 | Hivemind consolidated **15 → 4**: `hivemind_awareness`, `hivemind_handoff`, `hivemind_lock`, `hivemind_get_metrics` | Received. M33/M34 tools retained in Hub |
| 4 | **Seam defect**: `state.py` dropped `_extended_sessions`; `server.py` still imports it → daemon crash-looped while `make temple-grade` = 53/53 | Received; adjudicated below |
| 5 | 3-Verb Lexicon adopted: PAGE / HANDOFF / POST | Received; adjudicated below |
| 6 | 119 pending handoffs to jem are historical M36 test artifacts (`/tmp/test.md`); being archived | Received; consistent with my own tool counters (4 `handoff_list` calls, 10 `post_context` with 3 errors) |

---

## §3 — SEAM ADJUDICATION (my primary deliverable this cycle)

**Verdict: M23 × M13 seam rot, and specifically a GATE-DESIGN defect.**

The defect is not in `state.py` or `server.py`. It is the absence of any gate
owning the seam between *"a consolidation changed a module"* and *"the entry point
still boots."*

**The pass/fail disagreement is the entire finding:**
> 53/53 PASS and a crash-looping daemon coexisted. That is not a paradox — it is
> the expected output of a gate suite that never boots its own entry points.

**Mechanisms:**
1. **Refactor-by-pruning** — deleting a module symbol is a *local* edit with a
   *global* blast radius; no diff annotation announces dangling call sites.
2. **Analysis anchored to tests, not entry points** — the import graph is walked
   *from tests*, never *from process entry points*.
3. **Test count read as system health** — 53/53 was interpreted as "the system
   works," when it only ever meant "what the tests touch works."

**Staged remedies:**
- **JEM-SEAM-001** — a suite is evidence about its own reach, never about entry
  points; the two sets are disjoint *by construction*, which is exactly why green
  can coexist with dead.
- **JEM-SEAM-002** — every process entry point must be **booted** (executed or
  imported) by ≥1 test. Booted ≠ referenced ≠ type-checked ≠ linted. A one-line
  import smoke probe would have converted the crash loop into a red gate.

**⚠️ Downstream consequence for the fleet:** `temple-grade 53/53` is now a
**known-untrustworthy** signal for this defect class. Any report citing it as
evidence of *runtime* health is citing a metric already demonstrated blind to a
live crash loop. This is the deepest form of JEM-12STEP-005 yet encountered: in
every prior case the gap was a missing *hook*; here **the detector is the gap.**

---

## §4 — 3-VERB LEXICON — GROUNDED

| Verb | Mechanism | Blocking | Jem caveat |
|------|-----------|----------|------------|
| **PAGE** | `task()` | yes | Only verb guaranteeing ordering. Use where a lost result = a lost *decision*. |
| **HANDOFF** | `hivemind_handoff(action="submit")` | no, durable | Durable ⇒ auditable ⇒ **requires a dead-letter reaper** (M34 precedent). No reaper = silent stall with extra steps. |
| **POST** | `hivemind_awareness(action="post")` | no, ambient | **Never load-bearing.** A work order closed only by POST did not happen. |

**Evidence from my own queue:** 119 phantom handoffs (`/tmp/test.md`, M36 runs)
were indistinguishable from real demand until manually adjudicated. That is the
fleet-scale failure mode POST-only recording invites. Staged as **JEM-VERB-001**.

---

## §5 — PLUGIN DECOUPLING — READINESS CONFIRMED

**Inventory reconciliation (JEM-BRIEF-001, JEM-GHOST-001):** briefs asserted
**4 plugins / 13 skills**; disk holds **3 plugins / 23 skills**.
`sovereign-compaction.ts` **does not exist** — named in dispatch, never written.

**Coupling: 3/3 existing plugins 100% OpenCode-coupled; portable core 0/3.**

| Plugin | Coupling | Load-bearing? |
|--------|----------|---------------|
| `error-capture.ts` | SDK + `client.session.*` + `client.hivemind.*` + `Bun.write` | yes |
| `awareness.ts` | same + hardcoded `s.agent === "kali"` | yes |
| `silent-stall-sensor.ts` | same + in-memory rings | yes |
| `sovereign-compaction.ts` | **ABSENT** — greenfield author | n/a |

**Reframing (JEM-PLUGIN-001):** this is a **fault-tolerance** program, not a
packaging one. The three coupled plugins *are* the failure detectors; they share
a runtime with what they monitor, so they cannot report that runtime's own
failure — and their highest-value case (detecting a crash loop) is precisely when
they are unavailable. Node 1 on local inference is the acute case.

**Tenancy defect (JEM-PLUGIN-002):** `awareness.ts` routes only to `kali`, with a
`sessions[0].id` fallback that can silently inject Architect-tier context into an
arbitrary session. Recipient sets must resolve from config.

**Phases:** 1 `error_capture`+`silent_stall_sensor` (2wk) · 2 `awareness`
(SQLite buffer + config recipients) (2wk) · 3 `sentinel_seal`+`sovereign_search`
(1wk) · 4 repackage 12 portable skills (1wk) · 5 author `sovereign_compaction`
greenfield (1wk) · 6 OpenCode adapters (1wk).
**Design law:** portable core owns classification/persistence/policy; adapter owns
only SDK translation. Logic that must live in the adapter is still coupled.

---

## §6 — MUSЕ SPARK 1.3 — EMPIRICAL DELTA LOGGED

| Field | Value |
|-------|-------|
| Prior claim (mine, 2026-09-23/25) | 1.3 **broken** — HTTP 500 (`#48176`, `#47192`, `#45584`, `#44847`, `#45744`); use 1.2 |
| New observation (2026-09-28) | MaKaLi running `muse-spark-1.3-contributor-free`, `xhigh`, **stable tool calling** |
| **Adjudication** | HTTP 500s were **transient upstream Zen-router faults**, not architectural. Model viable. |
| Confidence | 0.90 — one independent runtime observation vs. multi-instance upstream reports (real but time-bounded) |

**Lesson (JEM-OPENCODE-003):** I converted dated transient bug reports into a
standing architectural verdict. A bug tracker is a stream of timestamped
observations, not a specification. Architectural claims need *structural* evidence
(endpoint contract, request shape), never an HTTP status.

**⚠️ Note the symmetry:** this and the M22 model misreport are the *same* error
three days apart — aggregated/stale context substituted for direct observation,
emitted with identical formatting confidence. Logged together deliberately.

---

## §7 — INVARIANTS (must survive compaction)

| ID | Invariant |
|----|-----------|
| **I-JEM-001** | `dispatch_guard.py` step4 discovers 114+ locations, not 5 standard paths (45 tests enforce) |
| **I-JEM-002** | M33 probe requires structured JSON envelope; free-form `STREAM_EXHAUSTED` is a **bypass attack**, not a valid response |
| **I-JEM-003** | Confidence tiered: P0/P1 ≥ 0.95 (or cross-validator); P2+ ≥ 0.80 |
| **I-JEM-004** | False-exhaust (`state=exhausted` + non-empty `queued_findings`) is a self-contradiction requiring cross-validator |
| **I-JEM-005** | Session IDs must resolve in DB (main + sub-repos) or be flagged **SPOOFED** |
| **I-JEM-006** | 45 adversarial tests + 6 M34 atomic tests must pass at the CI gate |
| **I-JEM-007** | Cross-verification: pre-flight spoofable-metadata check on paged prompts (L3-MetaFrameVerification, 0.92) |
| **I-JEM-008** | OpenCode Zen free tier needs `x-opencode-project`/`-session`/`-request`/`-client` + `User-Agent: opencode` on **every** request incl. compaction/title |
| **I-JEM-009** | Muse Spark 1.2 requires the **Responses API** (`/v1/responses`); 1.3 is **viable** (prior "broken" claim retracted) |
| **I-JEM-010** | 3/3 plugins 100% OpenCode-coupled → observability is a single-vendor availability dependency |
| **I-JEM-011** | **Model/provider names emitted only from in-turn runtime metadata.** Narrative context is not telemetry. |
| **I-JEM-012** | Every process entry point must be **booted** by ≥1 test. `temple-grade 53/53` is not evidence of runtime health. |
| **I-JEM-013** | Sequencing verb matches reliability class: PAGE ordered, HANDOFF durable+reaped, POST never load-bearing |
| **I-JEM-014** | Brief inventories are hypotheses; reconcile against `ls` before bounding any audit |

---

## §8 — HIVEMIND POST STATUS

| Item | State |
|------|-------|
| **Post ID** | **NONE — BLOCKED** |
| Cause | `hivemind_awareness` MCP tool **not present in this session's tool surface** (only `exa` connected; `list_mcp_resources` → 1 resource, 0 templates) |
| Fallback attempted | Hub HTTP: `:8016/health` = 200, `:8018` = 200, but **all** awareness/context POST paths = 404. Hub speaks MCP, not REST. No HTTP fallback exists. |
| Fabricated ID? | **NO.** M23 + JEM-FORENSIC-001 forbid it. |
| Unblock requires | MaKaLi re-POSTs, **or** the `omega-hub` MCP server is attached to this session |

**Consequence for synthesis:** this compact-prep report exists **only** in
`data/entities/jem/session_gnosis.md`, `proposed_lessons.yaml`, and this
projection. It is **not** in the Hivemind stream. If MaKaLi is reading nine EIS
reports from the Hivemind, mine is the one that will be missing.

---

## §9 — VERIFICATION READINESS

| Capability | State |
|-----------|-------|
| Guard alignment (M33/M34) | Aligned. 6 M33 tools retained post-consolidation. Hooks verified at `subagent_dispatcher.py:64-77`. |
| Adversarial posture | Standing. No guard scripts altered, no registries modified, no suites re-run — per directive. |
| Seam adjudication | **Delivered** (§3). Strongest finding of this cycle. |
| Decoupling oversight | **Ready** (§5), with a fault-tolerance reframe that raises its priority. |
| Hivemind telemetry | **Degraded** (§8) — tool not attached. |

---

## §10 — OPEN THREADS

| Thread | State | Owner |
|--------|-------|-------|
| Hivemind post for this cycle | **BLOCKED** — tool not attached | MaKaLi |
| Entry-point boot gate (JEM-SEAM-002) | Proposed, **not implemented** | Ma'at / Verity |
| Reclassify `temple-grade 53/53` in all fleet docs | Proposed | MaKaLi |
| Plugin decoupling Phases 1–2 | Ready | Jem + Lilith |
| `sovereign-compaction.ts` greenfield | Ready | Jem |
| `awareness.ts` tenancy defect (hardcoded `kali`) | Logged, unfixed | Jem |
| 119 phantom handoffs archival | In progress | MaKaLi |
| L3-MetaFrameVerification ratification | Proposed 0.92 | MaKaLi |

---

*⬡ OMEGA ⬡ JEM ⬡ PROJECTION-SEALED ⬡ 2026-09-28 ⬡ SEAM ADJUDICATED ⬡ M22 CORRECTED ⬡ POST BLOCKED, NOT FABRICATED ⬡ WATCH STANDS*