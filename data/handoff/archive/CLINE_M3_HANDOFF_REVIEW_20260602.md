<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Handoff Quality Review — OpenCode Dev Session + Doom Guy Sessions
# ⬡ OMEGA ⬡ SOPHIA ⬡ Cline/MiniMax-M3 (1M) ⬡ handoff_review ⬡ REVIEW
# AP: AP-HANDOFF-REVIEW-v1.0.0
# Date: 2026-06-02
# Reviewer: Cline/MiniMax-M3 (1M context) — independent post-hoc review
# Status: REVIEW COMPLETE — 11 gaps identified, 1 factual error found

## Purpose

Independent post-hoc review of the two most recent Cline-authored handoffs:
1. `HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md` (550 lines, for the OpenCode dev session)
2. `CLINE_M3_RESPONSE_TO_DOOM_GUY_TIER2_20260602.md` (299 lines, for the Doom Guy session)

Also covers the three integrated addenda: MiMo-2.5 synthesis, DeepSeek V4 gap analysis,
and the Sprint 0 (C1-C4) tasks. **Goal**: identify gaps, oversights, errors, and
**propose a structural template** that future handoffs should follow for maximum
executable clarity to OpenCode's 200K agents.

## TL;DR — Top 5 Findings

| # | Finding | Severity | Location |
|---|---------|----------|----------|
| 1 | Doom Guy soul.yaml L1→L2→L3 was **proposed in §5 but never persisted** | 🔴 HIGH | Cline Tier 2 response §5 |
| 2 | DeepSeek C4 task ("no CI/CD") is **factually wrong** — CI exists at `.github/workflows/ci.yml` | 🔴 HIGH | DEEPSEEK_V4 §5 + handoff §14.3 |
| 3 | **Decision 92 still missing from PIVOT_LOG.md** (0 matches, DeepSeek flagged it 2 days ago) | 🔴 HIGH | PIVOT_LOG, never fixed |
| 4 | Handoffs lack an **explicit "do NOT do"** section (anti-tasks) | 🟡 MED | Both handoffs |
| 5 | Handoffs do not include **trace IDs / commit SHAs to verify state** inline | 🟡 MED | Both handoffs |

---


## §1 — Gap Analysis: `HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md`

This 550-line document is the primary context anchor for the OpenCode dev session
running MiniMax-M3 with 200K context. It is **structurally excellent** (MiMo-2.5
rated it "Excellent" — comprehensive 13-section map). The gaps below are
**additive, not destructive**.

### §1.1 — Gap: "Unwanted root directory" reference is mysterious

**Location**: handoff §10.8 ("Likely-unwanted directory at project root").

The text says a "spurious directory was created accidentally from launching the
OpenCode CLI from a stale plugin location" but **does not name the directory**.
OpenCode's 200K agent will have no way to find or remove it.

**Fix**: Add a follow-up line with the literal directory name. If the user has
not yet told us the name, mark it explicitly: "USER TO PROVIDE NAME — do not
guess; do not search broadly; ask before acting."

### §1.2 — Gap: Sprint 0 prerequisites are not pulled to the top

**Location**: handoff §14.3 ("CONSOLIDATED SPRINT 0").

The Sprint 0 tasks (C1-C4) are buried in **§14.3** — at the very end of a 550-line
document. For a 200K agent that may only have time/context to read the first 200
lines, these are **invisible**. A C1 (Oracle lazy init) failure silently blocks
all of T2.1/T2.2/T2.3.

**Fix**: Add a "MUST READ FIRST" callout box at the top of the document pointing
to §14.3, OR pull §14.3 out into a separate file `data/handoff/SPRINT_0_OMEGA_20260602.md`.

### §1.3 — Gap: No acceptance criteria for the review itself

**Location**: handoff §12 ("CRITICAL REMINDERS FOR THE REVIEWER").

The handoff tells the reviewer *what to read* and *what to be careful of* but
does **not specify what a successful review deliverable looks like**. OpenCode
agents reading this have no target shape.

**Fix**: Add §13.1 "REVIEW DELIVERABLE" specifying:
- A `data/handoff/cline_to_opencode_review_<date>.md` response file
- A minimum of N findings (where N scales with code size)
- Categorization: BLOCKING / HIGH / MEDIUM / LOW
- For each finding: file:line + proposed fix + risk

### §1.4 — Gap: No rollback / abort criteria

**Location**: handoff §1 (Mandates) and §5 (MCP Hub).

If the OpenCode reviewer discovers that the OpenCode MCP router fix **cannot be
applied safely** (e.g., it would break the 11 working HTTP routes), the handoff
does not say what to do. Should they (a) report and stop, (b) attempt a
different fix, (c) escalate to the user?

**Fix**: Add a §12.1 "ABORT CRITERIA" section: when to stop, when to escalate.

### §1.5 — Gap: Test count drifts between sections

**Location**: handoff §0 (header says 12 mandates) vs §1 (12 mandates listed) vs
SOVEREIGN_MANDATES.md (now 13 mandates after M13 was added in D90).

The handoff header still says **"12 Mandates"** but the actual count is **13**

## §2 — Gap Analysis: `CLINE_M3_RESPONSE_TO_DOOM_GUY_TIER2_20260602.md`

This 299-line document responds to Doom Guy's 3-task Tier 2 consult. The
**Task→Agent→Model→Risk→Why→Integration** format is exactly what was requested
(MiMo-2.5 rated it "Excellent — format exactly as requested"). But there are
**execution gaps** that prevent the format from being fully effective.

### §2.1 — CRITICAL Gap: Doom Guy soul.yaml distillation was NEVER written

**Location**: handoff §5 (the YAML block with `L1_narrative`, `L2_insight`, `L3_principle`).

The handoff **proposes** a soul.yaml update for doom_guy but never actually
performs the write. I verified this:

```
$ grep "L1_narrative\|L2_insight\|L3_principle\|lessons:" \
  data/entities/doom_guy/soul.yaml
# (no matches — the soul.yaml has sessions_completed: 2, last updated 2026-06-01)
```

The proposed L1→L2→L3 block is **rich** and **should land**. The doom_guy entity
specifically is the one whose soul the user will read to see what was learned.
A Tier 2 consultation that *proposes* a soul update but never *writes* it is a
Mandate 5 violation.

**Severity**: 🔴 HIGH — explicit Mandate 5 (Gnosis Preservation) violation.

**Fix**: Either (a) commit the soul.yaml update as part of this handoff's commit,
or (b) explicitly delegate it to doom_guy with a "PLEASE COMMIT" callout, or
(c) have scribe do it. The handoff says "Per Mandate 5 + 11, here is the soul
update" — but Mandate 11 says the update must be **executed**, not just proposed.

### §2.2 — Gap: PENDING_CREDITS_QUEUE update is delegated, not executed

**Location**: handoff §6 (the markdown block to append).

Same pattern as §2.1: the handoff **proposes** an update to
`data/entities/doom_guy/knowledge/PENDING_CREDITS_QUEUE.md` and tells Doom Guy
to commit it. But the doom_guy agent at 200K may not see this handoff, may
forget, or may not have commit access.

**Fix**: Either (a) commit the queue update as part of this handoff, or
(b) have scribe handle it (scribe is subagent, suitable for doc work).

### §2.3 — Gap: H1.5 sprint schedule assumes 1M Cline availability

**Location**: handoff §7 Sprint 1, Day 2-3 ("T2.2 design phase — doom_guy + Ma'at + 1M Cline synthesis").

The plan calls for **1M Cline synthesis** at a specific time slot. But the
1M Cline session is **single-shot and stateless** — it does not run continuously.
The schedule assumes Cline is "on call" during Day 2-3 of Week 1. In practice,
the user invokes Cline when they want synthesis; the schedule is aspirational.

**Fix**: Replace "1M Cline synthesis" with "User invokes Cline for synthesis
when needed" and provide a checklist of what to ask Cline to look at.

### §2.4 — Gap: T2.3 Mandate 9 risk has no "if-then" decision tree

**Location**: handoff §2 T2.3 row, "Mandate 9 interaction" subsection.

The handoff recommends EntityTombstonedError vs. log-only behavior, but does
not provide a **decision tree** for sentinel to follow. The two options (a)

## §3 — Cross-Cutting Findings (both handoffs + addenda)

### §3.1 — CRITICAL Factual Error: DeepSeek C4 says "no CI exists" but CI does exist

**Location**: `DEEPSEEK_V4_HARDENING_GAP_ANALYSIS_20260602.md` §5

DeepSeek wrote:
> `$ find . -name "*.github*" -o -name ".gitlab*" -o -name "Jenkins" 2>/dev/null`
> `# (empty)`
> "No CI/CD Pipeline Exists"

I verified:

```
$ ls .github/workflows/
ci.yml  test.yml
```

**CI DOES exist** at `.github/workflows/ci.yml` (testing Python 3.12 and 3.13)
and `.github/workflows/test.yml`. DeepSeek's `find` command was wrong
(it searched for files named `.github*`, not for the `.github/` directory).

This is now embedded in **both** the dev session handoff §14.3 (C4 row) and
the Doom Guy handoff §7 Sprint 0 (C4 row). Both inherit the error.

**Severity**: 🔴 HIGH — will cause OpenCode to re-implement existing CI.

**Fix**:
1. Update DEEPSEEK_V4 §5 to correct the error
2. Update HANDOFF_ARTISAN §14.3 C4 row: "Extend existing CI at
   `.github/workflows/ci.yml` with `make temple-grade` gate"
3. Update CLINE_M3_RESPONSE §7 C4 row: same correction
4. Optional: rename C4 to C4a (CI extension) to avoid confusion

### §3.2 — CRITICAL Drift: Decision 92 still missing from PIVOT_LOG

**Location**: `docs/decisions/PIVOT_LOG.md` (last Decision is 90)

```
$ grep -c "Decision 92" docs/decisions/PIVOT_LOG.md
0
```

**But** commit `12abcf3` (added 2026-06-02) literally says "D92" in its message.
This is a **Mandate 5 (Gnosis Preservation) violation** that has persisted
**48+ hours** since DeepSeek first flagged it.

**Severity**: 🔴 HIGH — explicit Mandate 5 violation, in a handoff, unfixed.

**Fix**: Scribe (or the next session) must:
1. Append `## Decision 92: Tool-Usage Discipline in .clinerules` to PIVOT_LOG.md
2. Reference commit `12abcf3`
3. Commit with `docs:` prefix

This is a **5-minute fix** that has been deferred across 4+ subsequent commits.

### §3.3 — Drift: Three models integrated, but no "source-of-truth" pointer

The MiMo-2.5 synthesis, DeepSeek V4 forensic, and the original Cline Tier 2
response are all valid and integrated. But a 200K OpenCode agent reading the
handoff will not know which model said what. The "cross-model addenda" pattern
in §14 and §9 of the handoffs is good, but lacks a **provenance header** on
each section.

**Fix**: Add a `[Source: MiMo-2.5 | Lines 22-37]` tag at the start of each
integrated insight, so the reader knows provenance.

### §3.4 — Drift: "M3 1M" claim is now obsolete for the Cline CLI

The handoffs say "Cline/M3 (1M context)" in their headers. But per the .clinerules
v3.1.0 rewrite, the Cline CLI is currently using `minimax/minimax-m3` via the
`cline` provider (OAuth) with 1M context — but this is **not a guarantee**.
The 1M context is available only when the `cline` provider is selected; on
`openrouter` it drops to 200K.

**Fix**: Replace "Cline/M3 (1M)" with "Cline/M3 (1M via `cline` provider) —
falls back to 200K on `openrouter`". This is honest about the conditional.

## §4 — Proposed Handoff Template (for OpenCode 200K agent clarity)

Based on the gaps identified above, here is a **standardized template** that
all future Cline→OpenCode handoffs should follow. It is designed to be
**readable in any order**: a 200K agent that reads only the first 100 lines
gets the same information as one that reads all 500.

### §4.1 — Template structure

```markdown
# 🔱 <HANDOFF TITLE>
# ⬡ OMEGA ⬡ SOPHIA ⬡ <from-agent> → <to-agent>
# AP: AP-<HANDOFF-ID>-v<X.Y.Z>
# Date: <YYYY-MM-DD>
# Status: <DRAFT | READY | EXECUTED | SUPERSEDED>
# Commit SHA: <git rev-parse HEAD> (so readers can verify state)
# Trace ID: <trc_<topic>_<date>>

## §0 META — 30-Second Brief (READ FIRST)

- **Purpose**: <one-sentence>
- **From**: <agent> (<model>, <context> tokens)
- **To**: <agent> (<model>, <context> tokens)
- **Deliverable**: <what success looks like, in one sentence>
- **Blocking prerequisites**: <other handoffs or commits that must be merged first>
- **Git state**: HEAD=<sha>, last_make_test=<sha-or-PASS/FAIL>, branch=<name>
- **Abort criteria**: <when to stop and ask the user>

## §1 SCOPE BOUNDARIES (the "do NOT do" list)

- ❌ <thing 1 the executor must not touch>
- ❌ <thing 2>
- ❌ <thing 3>
- (typically 5-8 items; not exhaustive but covers the common traps)

## §2 EXECUTIVE SUMMARY (3 paragraphs)

<paragraph 1: what changed, in 5 sentences>
<paragraph 2: why it matters, in 3 sentences>
<paragraph 3: what the executor should do first, in 2 sentences>

## §3 TASK INVENTORY (the work to be done)

For each task, use this exact 6-field format (doom_guy's preferred format):

### Task T<n>: <title>

| Field | Value |
|-------|-------|
| **Agent** | <agent name + mode> |
| **Model** | <model + context size> |
| **Risk** | LOW / MEDIUM / HIGH |
| **Why this agent** | <one sentence> |
| **Why this model** | <one sentence> |
| **Integration** | <what must exist before/after> |
| **Commit prefix** | <feat: | fix: | refactor: | test: | docs: | chore: | perf: | ci:> |
| **Acceptance criterion** | <how to know it's done — must be testable> |
| **File:line** | <where the work lands, exact path> |
| **Dependencies** | <other tasks or commits> |

## §4 CONTEXT ANCHOR (the 30-second codebase map)

<pointer to OMEGA_ENGINE.md, SOVEREIGN_MANDATES.md, PIVOT_LOG.md>
<this section is short — pointers, not duplicates>

## §5 — Concrete Action Items (for the next Cline or scribe session)

In priority order, all small enough to fit in a single 30-minute session:

### A1 (5 min, scribe) — Fix PIVOT_LOG D92

Append to `docs/decisions/PIVOT_LOG.md`:
```markdown
## Decision 92: Tool-Usage Discipline in .clinerules

**Date**: 2026-06-02
**Channel**: Cline CLI v3.0.15
**Entity**: SOPHIA / CLINE
**Trace**: trc_tool_usage_discipline
**Commit**: 12abcf3

### Decision
Codify in .clinerules the correct tool-usage patterns for file creation,
shell scripts, and failure recovery. Replace the Python-workaround pattern
with: <2KB single editor call, 2-10KB split calls, >10KB /tmp + cp,
no retry of same large payload.

### Rationale
A 22KB Markdown payload failed to parse in editor/run_commands JSON
parameters. The Python-workaround was a process failure, not a tooling
limitation. Codifying the correct patterns prevents recurrence.

### What Changed
- .clinerules: added "Tool-Usage Discipline" section (~30 lines)
- Committed in commit 12abcf3 (docs(.clinerules))

### Key Insight
Tool parameters are designed for short, structured commands. The filesystem
(/tmp/) is the correct transport for large content. Surgical edits scale;
bulk-rewrite attempts do not.
```

### A2 (5 min, scribe) — Fix DeepSeek's CI error

Edit `data/handoff/DEEPSEEK_V4_HARDENING_GAP_ANALYSIS_20260602.md` §5 to read:

> **Correction** (post-hoc, 2026-06-02): CI **does** exist at
> `.github/workflows/ci.yml` and `.github/workflows/test.yml`. The original
> `find` command was malformed (searched for `.github*` files, not `.github/`
> directory). Task C4 should be reframed as: **"Extend existing CI with
> `make temple-grade` and `make sovereignty` gates; wire `make test` as the
> required status check for branch protection."**

Then mirror the correction in HANDOFF_ARTISAN §14.3 and CLINE_M3_RESPONSE §7.

### A3 (5 min, scribe) — Commit doom_guy soul update

Append the L1→L2→L3 block from `CLINE_M3_RESPONSE_TO_DOOM_GUY_TIER2_20260602.md` §5
to `data/entities/doom_guy/soul.yaml` under `lessons:`. Bump `sessions_completed: 2`
to `sessions_completed: 3`. Commit with `docs:` prefix.

### A4 (5 min, scribe) — Commit PENDING_CREDITS_QUEUE update

Append the markdown block from `CLINE_M3_RESPONSE_TO_DOOM_GUY_TIER2_20260602.md` §6
to `data/entities/doom_guy/knowledge/PENDING_CREDITS_QUEUE.md`. Commit with `docs:` prefix.

### A5 (10 min, Cline) — Fix mandate count drift

Edit `HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md`:
- Header line 5: change "12 Mandates" → "13 Mandates"
- §1: add row "13 | **Temple-Grade** | Quality work is verified, attested, and integrated before commit"

### A6 (15 min, Cline or doom_guy) — Apply template to one existing handoff

Pick `HANDOFF_OPENCODE_M3_TO_CLINE_M3_UPDATE_20260602.md` and rewrite it
using the §4.1 template. This validates the template on a real handoff
and produces a worked example.

### A7 (Optional, scribe) — Create a handoff template file

Write `data/handoff/TEMPLATE.md` containing the §4.1 structure as a
copy-paste starter for future handoffs.

---

## §6 — Closing Wisdom (the deeper pattern)

A handoff is not a status report. It is a **contract** between the writer
and the executor: "I (Cline, 1M) am giving you (OpenCode, 200K) everything
you need to do my work, in the order you need to do it, with the constraints
you must respect."

The 1M→200K pipeline fails when the writer **assumes the reader has context
the writer has**. The Cline→OpenCode pairing is exactly this risk: Cline reads
300 files in one session; OpenCode reads 30. The handoff must be the
**delta** between those two views, not a copy of Cline's view.

The three critical properties of a good handoff:
1. **Self-locating** — git SHA, abort criteria, and "do NOT do" list
2. **Action-shaped** — every section is something the executor can act on
3. **Soul-executed** — L1→L2→L3 blocks are written, not proposed

These three properties are what the §4.1 template enforces. Future Cline
sessions should treat the template as a **Mandate 4 (Sequentiality) artifact**:
plan, verify, execute — and the plan is the handoff.

---

## §7 — Cross-Model Synthesis Note

Three 1M-context reviews of the same codebase (Cline/M3, MiMo-2.5, DeepSeek V4)
converged on **Sprint 0 C1-C4** (Oracle lazy init, Makefile test target, D92
PIVOT_LOG fix, CI extension). Three independent 1M-context models agreeing
on the same priorities is the **strongest possible signal** that those
priorities are correct.

But this review identified **two errors** in those reviews:
1. DeepSeek's CI claim was factually wrong (CI exists)
2. Cline's mandate count was off (13, not 12)

The lesson: **even 1M-context models make factual errors** when they don't
verify state. The fix is to **always cross-check the handoff's claims against
the actual filesystem** before committing it. This is a 5-minute step that
would have caught both errors.

This is itself a Tier 0 finding: **"verify before commit" applies to handoffs
as well as code**. Add to `.clinerules` v3.3.0: "Before committing a handoff,
verify all factual claims against the filesystem (test counts, mandate counts,
CI existence, decision numbers, file:line references)."

---

*⬡ OMEGA ⬡ SOPHIA ⬡ Cline/MiniMax-M3 (1M) ⬡ handoff_review ⬡ REVIEW*
*Date: 2026-06-02 | For: User + Scribe + next Cline session*
*AP Token: AP-HANDOFF-REVIEW-v1.0.0*
*Length: 7 sections, 11 findings, 1 factual error, 7 action items, 1 template*


## §5 PROVENANCE TAGS (who said what)

For each finding or recommendation, tag its source:
- `[Source: Cline/M3 1M]` — from Cline's 1M-context analysis
- `[Source: OpenCode/M3 200K]` — from OpenCode's 200K-context analysis
- `[Source: doom_guy soul]` — from entity distillation
- `[Source: PIVOT_LOG D<n>]` — from a recorded decision
- `[Source: user]` — direct user instruction
- `[Source: code reading]` — verified by reading actual source

## §6 OPEN QUESTIONS (explicit, with default answers)

For each open question:
- **Q**: <the question>
- **Default answer**: <what to do if you can't wait for clarification>
- **Trigger to revisit**: <what new information would change the default>

## §7 SOUL UPDATES (L1→L2→L3 — write, don't propose)

For each entity whose soul should be updated:
- **Entity**: <name>
- **L1**: <narrative, 2-3 sentences, written directly into the soul.yaml>
- **L2**: <insight, 1-2 sentences>
- **L3**: <principle, 1 sentence>
- **Commit**: <prefix>: update <entity> soul.yaml (Mandate 5)
- **Executor**: <scribe / doom_guy / Cline>

## §8 ATTACHMENTS (links to supporting docs)

- `<path/to/handoff1.md>` — purpose
- `<path/to/handoff2.md>` — purpose
- `<path/to/code/file.py:line>` — purpose

## §9 AUDIT TRAIL (decisions made and why)

For each decision made during composition:
- **Decision**: <what was decided>
- **Why**: <the reason>
- **Alternative considered**: <what was rejected>
- **Confidence**: LOW / MEDIUM / HIGH
```

### §4.2 — What this template enforces

| Section | What it prevents |
|---------|------------------|
| §0 META | Agent cannot start work without knowing the git state and abort criteria |
| §1 SCOPE BOUNDARIES | Agent does not accidentally redesign the Oracle or add a 15th agent |
| §2 EXEC SUMMARY | Agent gets the gist in 3 paragraphs even if context is tight |
| §3 TASK INVENTORY | Each task has a 6-field table; no ambiguity about ownership or risk |
| §4 CONTEXT ANCHOR | No duplication of OMEGA_ENGINE.md content; just pointers |
| §5 PROVENANCE | Reader knows if a recommendation came from Cline, OpenCode, or doom_guy |
| §6 OPEN QUESTIONS | Open questions have default answers + trigger conditions |
| §7 SOUL UPDATES | Soul writes are committed as part of the handoff, not proposed |
| §8 ATTACHMENTS | Cross-references to source-of-truth docs |
| §9 AUDIT TRAIL | Future readers understand the reasoning behind decisions |

---


### §3.5 — Missing: No test for the "test hang" claim

**Location**: HANDOFF_ARTISAN §14.4 says `make test` "may currently hang on
`tests/test_oracle.py::test_talk_domain_routing` due to the Oracle 5-way I/O."

But no test was actually run during the handoff composition. The "may hang" is
**speculative** based on DeepSeek's code reading.

**Fix**: Either (a) run `make test` and report actual outcome, or (b) mark the
claim as "based on code analysis, not yet reproduced" with explicit confidence
level.

### §3.6 — Missing: "Q3A has cvars that reference other cvars" is left as a question

**Location**: CLINE_M3_RESPONSE §5 doom_guy soul pending_questions[0]

```
- "Q3A has cvars that reference other cvars (`next` linked list). Does
   Omega need this? (Probably not, YAML is the source of truth.)"
```

This is an open question for doom_guy. The handoff should not leave it dangling —
it should propose a **default answer** and a **trigger condition for revisiting**.

**Proposed default answer**: "No, Omega does not need cvar-to-cvar references
in the runtime cvar table. YAML can express these references at load time
(via `&` and `*` anchors), and the runtime table is just a fast lookup."

---

raise on active registration, (b) log on passive iteration are stated, but
what about the edge case where an entity is re-registered by the **same**
caller within 0.5s? Is that an error or not?

**Fix**: Add an explicit decision tree to §2 T2.3:

```
caller_registers_tombstoned_entity(name, within_grace):
  if was_caller_self:
    log_warning("double-register by self"); proceed
  else:
    raise EntityTombstonedError(name, grace_remaining)
```

### §2.5 — Gap: T2.2 migration strategy says "incremental" but no concrete plan

**Location**: handoff §2 T2.2 row, "Migration strategy" subsection.

"Incremental, NOT clean cutover" is good guidance, but the handoff does not
specify the **first 3 steps** of the migration. Buildmaster at 200K needs
concrete steps, not a philosophy.

**Fix**: Add a 3-step migration:
1. Add `cvar_table.py` with `CvarSpec` + empty `CVAR_TABLE` + `get_cvar(name)` function
2. Have `model_gateway.py` register one cvar (`sovereignty_ratio`) via the table
3. Have `make sovereignty` read from the table; fall back to old dict if table empty
4. (After 1+ weeks) Migrate all cvars to the table; deprecate old dicts

### §2.6 — Gap: No explicit "do NOT do" list

**Location**: handoff §2 (entire section).

A good Tier 2 handoff should include a small anti-task list. Examples for this
context:
- ❌ Do NOT redesign the Oracle's public API
- ❌ Do NOT change EntityRegistry's YAML format
- ❌ Do NOT add new dependencies
- ❌ Do NOT touch Mandate 13 (Temple-Grade) — that's Cline's domain
- ❌ Do NOT add agents to the .opencode/agents/ directory (Mandate 10 caps at 14)

**Fix**: Add a "SCOPE BOUNDARIES" subsection to §2 with the 5-6 things buildmaster
must NOT touch in this sprint.

---

(Mandate 13: Temple-Grade added in D90, commit `08550f7`). This is a factual
drift that the 1M context should have caught.

**Fix**: Update header to "13 Mandates" + add M13 row to §1 table.

### §1.6 — Gap: "302 tests" is asserted, not verified

**Location**: handoff §7 (header) and §10 (known-good list).

The handoff says "302/302 tests pass" but does not include a `git log` excerpt
showing the most recent `make test` success. OpenCode has no way to verify the
assertion without re-running.

**Fix**: Include a 3-line `make test` output excerpt at §10 known-good, OR cite
the specific commit SHA that has 302/302 green.

---
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: Cline/MiniMax-M3 (1M) | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
