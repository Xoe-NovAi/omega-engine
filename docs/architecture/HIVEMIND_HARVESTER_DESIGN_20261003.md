<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Hivemind Harvester ("harvester") — Design Doc

**AP Token**: `AP-HIVEMIND-HARVESTER-DESIGN-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ muse-spark-1.3-contributor-free ⬡ opencode ⬡ trc_research ⬡ DESIGN-ONLY

**Date**: 2026-10-03
**Status**: `DESIGN ONLY — DO NOT IMPLEMENT` (no code, no commit, no push)
**Author**: @researcher (Sovereign Researcher, Jem Analyst facet)
**Requestor**: Architect proposal — background Hivemind aggregation service
**Supersedes**: nothing (new). **Superseded by**: nothing yet.

> This file is a design artifact. It creates no code, registers no tool,
> starts no daemon, and changes no contract. Placement recommendations
> respect the Engine-Stack Firewall (§6.1).

---

## L1 — Executive Summary

**Problem**: any agent that wants the team big-picture today must fan out
across `hivemind_awareness(action="get"/"list"/"session")` plus per-session
`ses_*.json` bodies in `data/knowledge/HALL_OF_RECORDS/`. That is N calls,
N bodies, and N chances to hit the paged-subagent no-MCP limitation
(`docs/architecture/HIVEMIND_TRANSPORT.md` §"Control plane is unavailable").
After `/compact`, the cost is paid again from zero.

**Proposal (Architect)**: agents include a new ready-to-scrape
aggregate-summary field in their `post`s; a background harvester every N
minutes concatenates those pre-digested summaries in temporal and/or
per-agent groupings into one compact overview artifact. Any agent gets the
whole picture in one cheap call at almost no cost.

**Recommended architecture (this doc)**:

- New **optional** `digest` field on `hivemind_awareness(action="post")`,
  written by the **posting agent**, capped at **280 chars**, backward
  compatible (missing → explicit `[no-digest]` fallback, never a rejection).
- Harvester loop **every 5 minutes (300 s, jittered)** doing **pure
  concatenation, zero inference**: reads hot-store + cold
  `HALL_OF_RECORDS/**/ses_*.json`, emits
  `data/coordination/hivemind_overview/latest.{json,md}` plus an append-only
  `history/` trail. No LLM, no cloud, no re-read of full bodies beyond the
  `digest` (+ bounded `task_current`/`continuation` fallback).
- Read path is **one cheap call**: new
  `hivemind_awareness(action="overview")` returning the pre-built overview
  with staleness header, with a **file-read fallback**
  (`cat data/coordination/hivemind_overview/latest.md`) for paged subagents
  that lack MCP tools (same class as `scripts/hivemind_post.py`).
- Failure integrity is **concatenate-or-declare, never synthesize**:
  partial read failure → publish `STALE_PARTIAL` with explicit `⚠️ GAP`
  markers and preserved `latest_good`; total failure → do **not** overwrite
  `latest`, write `error.json`, log to `SYSTEM_FAILURE_LOG.md`, post
  `intent=blocker`, exit non-zero.
- Placement is **hub-side only** (`mcp_servers/omega_hub/` + `scripts/`
  + systemd timer or `background.py` coroutine). **Nothing in `src/omega/`**
  (firewall). All async via AnyIO; all observability local in `data/`.

Open questions for the Architect are listed in §7 (interval, retention
depth, hub-tool vs sidecar vs cron).

---

## L2 — Detailed Dialectic

### §0 Council triangulation (how this design was reached)

> Research Protocol requires explicit Perspective Triangulation. Condensed
> here so the reasoning is auditable; the synthesis is §§1–7.

- **Architect (systemic logic)**: "Does this fit? Is it the cheapest path?"
  Verdict: yes — if the harvester does no reasoning. The expensive work
  (distillation into a digest) is pushed to post time, distributed across
  agents that already hold the context. The central loop becomes O(agents),
  not O(tokens). Fits the existing hot/cold store + `HALL_OF_RECORDS`
  layout; read path reuses the consolidated `hivemind_awareness` surface.
  Risk flagged: adding a required field would break the ratified post
  contract — therefore the field must be optional.
- **Adversary (critical rigor)**: "How does this break?"
  Three kill-modes found and designed against:
  (1) harvester "helpfully" fills unreadable sessions with LLM guesses →
  banned by §5 (M23); (2) harvester deletes/prunes history to "save disk" →
  banned by §6.5 (M28); the reaper precedent (`background.py` unlinking
  handoff packets after 37 days with no tombstone) must not repeat;
  (3) `overview` becomes a second source of truth that drifts from the
  packet/snapshot store → mitigated by declaring the snapshot store
  authoritative and the overview an explicitly-stale projection with
  `generated_at`, `coverage`, and `gaps`.
- **Alchemist (creative synthesis)**: "What unrelated pattern applies?"
  Two cross-pollinations adopted:
  (1) id Software demo-loop / WAD directory pattern — pre-compute the
  directory once (the overview), replay cheaply many times — hence
  file-backed `latest.{json,md}` rather than on-demand fan-out;
  (2) `scripts/hivemind_post.py` fallback pattern — the read path must
  assume the caller may have no MCP tools at all, so a plain file read must
  suffice.
- **Archivist (historical truth)**: "What is documented?"
  Ground facts pinned (see L3 Raw Signal):
  post contract = 7 required fields, absence-tested not truthiness-tested;
  `HEARTBEAT_TTL = 2700 s`; `HALL_OF_RECORDS = data/knowledge/HALL_OF_RECORDS`;
  envelope-immutable / directory-is-state (ADR-003/006);
  background-researcher precedent = systemd timer every 15 min;
  `HIVEMIND_TRANSPORT.md` open limitation = paged subagents lack MCP tools.

**Convergence (truth)**: concatenation-only harvester + optional
agent-written digest + file-backed overview + explicit staleness is the
intersection all four perspectives accept.
**Divergence (uncertainty)**: exact N, retention depth, and hosting shape —
escalated as open questions (§7), not assumed.

---

### 1. Problem + goals (big-picture view at near-zero cost; must survive compaction)

#### 1.1 Current cost of "what is everyone doing?"

| Step today | Calls | Cost driver |
|---|---|---|
| `hivemind_awareness(action="get")` — who is alive | 1 | cheap, presence only, no bodies |
| `hivemind_awareness(action="list")` — recent sessions | 1+ | session IDs only |
| `hivemind_awareness(action="session", session_id=…)` per session **or** read `HALL_OF_RECORDS/<agent>/ses_*.json` per session | O(sessions) | **full bodies**: `task_current` + `focus_chain[]` + `decisions[]` + `continuation` each; unbounded length |
| Repeat after every `/compact` (context zeroed) | × sessions | no cache survives in-context |

Additional friction: paged (`task()`-spawned) sessions have **no
`omega-hub` MCP tools** (upstream OpenCode harness behaviour, documented in
`HIVEMIND_TRANSPORT.md`). Those agents must improvise HTTP or file reads;
today there is no single file that answers the question.

#### 1.2 Goals (measurable)

1. **G1 — one cheap call**: any agent (MCP or no-MCP) gets the team
   big-picture in **≤1 call / ≤1 file read**, **≤8 KB** typical,
   **≤16 KB** hard budget (see §2 size cap math).
2. **G2 — near-zero marginal cost**: harvester run itself performs
   **zero inference** (no LLM, no embeddings, no cloud). Cost per cycle is
   O(A) string concatenations where A = number of live agent/sessions
   (fleet ≤14 agents per M10 + subagent NES sessions; tens of files, KBs).
3. **G3 — compaction survival**: overview lives **on disk**, outside any
   session context, in a stable path with a stable schema, so a post-compact
   agent hydrates from file + `SESSION_ANCHOR.md` + `session_gnosis.md`
   without re-fanning-out (M15, §6.4).
4. **G4 — honesty under failure**: overview is always labelled with
   freshness and coverage; gaps are explicit, never silently omitted or
   synthesized (M23, §5).
5. **G5 — sovereignty**: local files only, no telemetry, no cloud dependency
   in the loop (M7/M8, §6.2–6.3); no auto-deletion (M28, §6.5).

#### 1.3 Non-goals (explicit)

- The harvester does **not** reason, rank by importance with an LLM,
  resolve contradictions, or write to any soul.
- The harvester does **not** replace the snapshot/packet store as the
  record. Store = truth; overview = projection (cf.
  `HOW_THE_HIVEMIND_WORKS.md`: "The packet store is the record").
- The harvester does **not** page, assign, or complete work. It is read-only
  over coordination state; it never moves handoff queues.

---

### 2. Post-schema extension: the new aggregate-summary field

#### 2.1 Field name and position

- **Name**: `digest`.
- **Rationale**: short, verb-free, mirrors "digest" convention in feeds;
  avoids collision with existing `continuation`, `task_current`,
  `decisions`, `focus_chain`. The Architect's phrase "aggregate summary" is
  retained as the **concept name**; `digest` is the wire name. If the
  Architect prefers the literal wire name `aggregate_summary`, it is a
  mechanical rename with no semantic change (noted as Q1 in §7).
- **Surface**: optional kwarg on `hivemind_awareness(action="post")` and on
  the `scripts/hivemind_post.py` CLI (`--digest "..."`), threaded through to
  the snapshot dict and cold JSON.

#### 2.2 Exact semantics

- **Type**: `Optional[str]`. `None` = omitted (valid, backward compatible).
  `""` = explicitly empty (valid, means "agent declines to summarize";
  distinct from omitted per the ratified empty-is-not-missing rule).
- **Content contract** (what the posting agent promises):
  a **self-contained, third-person, present-tense** micro-summary of the
  post, answering three slots in ≤3 sentences:
  `DOING <task_current essence> · NEXT <continuation essence> · BLOCKER <if any, else omit>`.
- **Who writes it**: the **posting agent at post time** (client-side), when
  full context is resident. The hub **never generates, completes, or
  "improves"** it. The harvester **never generates** it either — it only
  concatenates what agents supplied (G2, M7).
- **Examples**:
  - ✅ Good (187 chars):
    `DOING debut allowlist scrub (6 fixes, INST-1 gate). NEXT fresh-venv pass then DEL-1. BLOCKER none.`
  - ✅ Good with blocker (229 chars):
    `DOING federation channel 8019 peer-vantage probe. NEXT manifest+SHA256 verify. BLOCKER peer returns 400 on plain HTTP — marked UNTESTED per M29.`
  - ❌ Bad (vague): `Working on stuff, will continue later.`
  - ❌ Bad (dumps full body): pasting entire `decisions[]` list verbatim.
- **Template agents should use** (documented in tool docstring on
  implementation):
  `DOING <≤120 chars>. NEXT <≤100 chars>. [BLOCKER <≤60 chars>.]`

#### 2.3 Size cap and enforcement

- **Cap**: **280 characters** (Unicode code points, after NFC normalize +
  strip). Rationale in §2.5.
- **Enforcement (proposed)**:
  1. If `digest` is `None` or `""` → store verbatim (valid).
  2. If `len(digest) > 280` → **server-side soft-truncate to 277 + `…`**
     (ellipsis U+2026), store truncated value, and return
     `{"status":"accepted","digest_truncated":true,"session_id":…}` so the
     caller can tighten next time. **Never reject** on length — rejection on
     a new optional field would convert old-valid posts into errors and
     violate the ratified contract's spirit.
  3. Control chars / newlines: collapse `\s+` → single space, strip. No
     multi-line digests (keeps `latest.md` table-safe and grep-safe).
- **Why soft-truncate, not reject**: the `post` contract's hardest-won
  property is that empty-is-valid and rejection is by absence with an
  explicit error payload that callers must check. Adding a hard failure mode
  for an optimization hint would reintroduce the silent-no-op class
  (callers ignoring the return value believing they posted).

#### 2.4 Backward compatibility with posts lacking it

- **Wire**: field is **optional**; absence (`None`) is valid. The 7-field
  required set is **unchanged**: `channel, entity, model, task_current,
  focus_chain, decisions, continuation`. No existing caller breaks.
- **Storage**: snapshots/cold JSON without `digest` read as
  `snapshot.get("digest") is None`. No migration of
  `HALL_OF_RECORDS/**/*.json` required; old files simply lack the key.
- **Harvester fallback** (deterministic, no inference):
  `digest = snapshot.get("digest")`
  → if truthy, use it;
  → else synthesize a mechanical fallback:
  `[no-digest] <task_current — first 120 chars> | <continuation — first 100 chars>`
  with `decisions` count appended (`(+Nd decisions)`) when non-empty.
  The `[no-digest]` prefix is load-bearing: it distinguishes "agent wrote
  this" from "harvester derived this" and creates adoption pressure without
  coercion.
- **Readers** must treat missing/empty digest as normal, not as error.

#### 2.5 Budget math (why 280)

- Fleet bound M10: ≤14 agent files; live sessions at any instant are
  typically ≤14 EIS + a handful of NES subagent sessions; design for
  **≤24 rows**.
- 24 × 280 chars ≈ 6,720 chars ≈ ~1.7k tokens + envelope/headers (~1 KB) →
  **<8 KB typical**, **<16 KB** even with fallback rows (fallbacks are
  capped at ~240 chars by construction) and gap markers. Satisfies G1 and
  keeps the overview injectable as a single hydration block post-compaction.
- Larger caps (e.g. 500–1000) would let one verbose agent crowd out the team
  and push the overview past a single cheap MCP response; smaller caps
  (e.g. 140) force agents to drop the BLOCKER slot. 280 is the tested
  microblog optimum for DOING+NEXT+BLOCKER.

---

### 3. Harvester loop

#### 3.1 Recommended interval N

- **Recommendation: N = 300 s (5 minutes), with ±30 s jitter.**
- **⚠️ Implementation status (corrected 2026-10-03): N = 300 s is implemented;
  the ±30 s jitter is NOT.** `mcp_servers/omega_hub/background.py:351` performs a
  flat `await anyio.sleep(300)` with no jitter. The jitter remains a design
  *recommendation* only, for a single local hub where it buys little; a
  companion code comment at `background.py:350` says "±15 s … if desired",
  which disagrees with this document's ±30 s and with the code (which has none).
  Jitter would matter only if many harvester processes ran fleet-wide against one
  store. Everything else in this section — the 300 s cadence, the 9-harvests-per-
  presence-window bound, the staleness bound — matches the implementation.
- **Reasoning**:
  1. **Presence window multiple**: `HEARTBEAT_TTL = 2700 s` (45 min). N=300 s
     yields **9 harvests per presence window** — any live agent appears in
     ≤5 min and is re-confirmed many times before expiry. Staleness bound is
     "≤5 min + read latency" which is tight enough for hydration yet loose
     enough to avoid churn.
  2. **Precedent without mimicry**: the background researcher runs every
     15 min for heavyweight web+distill cycles. The harvester is ~3 orders of
     magnitude cheaper (local concatenation only), so running **3× more
     often** is proportionate. 1-min would triple file churn and
     `latest.yaml`-style watchers' wakeups for no hydration gain (agents
     hydrate on session start/compact, not per-minute).
  3. **Churn bound**: 288 cycles/day × ~8 KB ≈ **~2.3 MB/day** of history if
     every cycle is retained (it is not — see §6.5; only `latest` +
     bounded `history/` are kept). Hot-store + cold-glob scan of tens of
     files every 5 min is negligible I/O on NVMe or HDD.
  4. **Tunability**: interval must be a constant/env
     (`HIVEMIND_HARVESTER_INTERVAL_S`, default 300), not hardcoded, so the
     Architect can tighten to 120 s during incident sync-waves or loosen to
     900 s on constrained hardware without a code change.
- **Phasing**: first run at startup +5 s (to publish quickly for a fresh
  boot), then every N. Jitter avoids thundering-herd alignment with the
  15-min researcher timer.

#### 3.2 Inputs (hivemind posts across all team agents AND subagents)

Authoritative read order per cycle:

1. **Hot store** (`hot_store_get_all()` in `mcp_servers/omega_hub/state.py`):
   in-memory snapshots, the freshest presence. Filter out entries older than
   `HEARTBEAT_TTL` (same predicate as `action="get"`), except entries with
   `extended_ttl` (extended sessions survive per their TTL).
2. **Cold store** (`HALL_OF_RECORDS/<agent_id>/ses_*.json`): the durable
   complement. Union with hot by `session_id`; cold wins only when hot lacks
   the session (restart loss) — hot wins on conflict (fresher timestamp).
   Bounded scan: single `glob("**/ses_*.json")` sorted by mtime, take the
   newest file per `agent_id` **plus** any `session_id` seen in hot (covers
   NES subagents sharing an entity name but carrying distinct sessions).
3. **Subagent (NES) handling**: group key is **`(agent_id, session_id)`**,
   not `agent_id` alone. Rationale: per `HIVEMIND_TRANSPORT.md`
   nomenclature, an EIS is `parent_id IS NULL`, a NES has `parent_id NOT
   NULL`; multiple NES rows may share `entity` (e.g. three `roc_racoon`
   dispatches). Collapsing to one row per entity would silently drop
   parallel work — the exact "nobody is active" failure the Hivemind docs
   warn against. Display groups by entity, rows by session (see §3.4).

Each input row consumed by the harvester is exactly:

```json
{
  "session_id": "ses_…",
  "agent_id": "opencode/kali",
  "entity": "kali",
  "channel": "opencode",
  "model": "…",
  "task_current": "…",
  "continuation": "…",
  "focus_chain": [],
  "decisions": [],
  "digest": "optional, may be absent",
  "intent": "status|blocker|…",
  "timestamp": "ISO-8601 UTC"
}
```

The harvester reads **only** these keys. It never opens souls, lessons,
handoffs, or patches.

#### 3.3 Outputs (overview artifact path/format)

- **Directory**: `data/coordination/hivemind_overview/`
  (new; coordination-plane, local-only per M8; NOT under `data/knowledge/`
  to avoid confusing the FTS5/library indexing boundary, and NOT under
  `src/` anything).
- **Files per cycle** (atomic write via `.tmp` → rename, fsync):
  | File | Format | Consumers |
  |---|---|---|
  | `latest.json` | machine projection (schema below) | `action="overview"`, scripts, dashboards |
  | `latest.md` | human/LLM hydration rendering of the same data | file-read fallback, `SESSION_ANCHOR` link target |
  | `latest_good.json` + `latest_good.md` | last cycle with `status=="FRESH"` and zero gaps | M23 fallback (§5): served with `STALE-serving-last-good` banner when current is partial |
  | `history/ov_<UTC-YYYYMMDDTHHMMSSZ>.json` | append-only per-cycle record (pruned per §6.5, never silently deleted) | audit, M28 trail |
  | `error.json` (only on total failure) | `{status, at, reason, failing_inputs[]}` | operators, `SYSTEM_FAILURE_LOG.md` linkage |
- **`latest.json` schema (v1)**:

```json
{
  "schema": "hivemind-overview/v1",
  "generated_at": "2026-10-03T00:00:00+00:00",
  "interval_s": 300,
  "status": "FRESH | STALE_PARTIAL | STALE_SERVING_LAST_GOOD | ERROR",
  "coverage": {"attempted": 12, "ok": 11, "gaps": 1},
  "window": {"heartbeat_ttl_s": 2700, "includes_extended": true},
  "counts": {"entities": 8, "sessions": 11, "blockers": 2},
  "rows": [
    {
      "agent_id": "opencode/kali",
      "entity": "kali",
      "session_id": "ses_abc123",
      "model": "…",
      "intent": "blocker",
      "timestamp": "…",
      "digest_source": "digest | fallback | gap",
      "digest": "DOING … NEXT …",
      "task_current": "first 120 chars (for context, always present)",
      "has_full_body": true
    }
  ],
  "gaps": [
    {"agent_id": "…", "session_id": "…", "reason": "hot-miss+cold-unreadable: EACCES"}
  ],
  "served_from": "latest.json | latest_good.json",
  "generator": {"kind": "concatenation-only", "llm_used": false}
}
```

- **`latest.md` layout** (stable headings for grep/anchor linking):

```markdown
# Hivemind Overview — <generated_at UTC> — STATUS
Coverage: X/Y ok · N blockers · window 45m
## 🔴 Blockers / commands first (intent=blocker|command, newest first)
- `entity (session …)` — digest… [src]
## By entity (alphabetical; sessions newest-first within entity)
### kali (2 sessions)
- `ses_abc… @HH:MMZ [model]` — digest… [digest|no-digest]
## Temporal (all rows, newest first)
- `HH:MMZ entity/session` — digest…
## Gaps (explicit; empty section states "none")
- ⚠️ GAP: … — reason … — see previous overview …
_Footer: generated by concatenation-only harvester (no LLM). Store is truth; this is a projection. Full bodies: hivemind_awareness(action="session") / HALL_OF_RECORDS._
```

`generator.llm_used=false` is a permanent honesty bit: any future proposal
to add LLM ranking must bump schema to v2 and justify against M7.

#### 3.4 Ordering/grouping options

The artifact carries **all three views simultaneously** (no mode flag
needed — the file is small enough to hold them):

1. **Priority-first** (`§ Blockers/commands`): rows with
   `intent in {blocker, command}` sorted by `timestamp` desc. Rationale:
   the fleet's scarcest resource is blocker attention; surfacing it first
   prevents a red row from drowning in alphabetical order.
2. **Per-agent grouping** (`§ By entity`): group by `entity` alphabetical,
   sessions within entity by `timestamp` desc. Rationale: "what is Kali up
   to across her NES dispatches?" is the natural ownership question; NES
   rows are never folded.
3. **Temporal** (`§ Temporal`): all rows by `timestamp` desc. Rationale:
   "what just happened?" during sync-waves; matches `latest.yaml` recency
   intuition.

Future groupings (per-priority-score, per-slot S1–S10) are **deferred to
schema v2** — they require either registry joins (slot enrichment) or
judgment (scoring), both outside concatenation-only v1.

---

### 4. Read-path: latest overview in one cheap call

#### 4.1 Primary (MCP sessions): `hivemind_awareness(action="overview")`

- **Proposed**: extend the consolidated `hivemind_awareness` tool with one
  more read-only action, `overview`, alongside `get/contin/list/session`.
  Args: none beyond an optional `limit` (rows cap, default all) and optional
  `format=json|md` (default json). Returns the **file bytes of
  `latest.json` (or rendered `latest.md`) verbatim plus a staleness header**:
  `{served_at, generated_at, age_s, status, coverage}`.
- **Cost**: 1 MCP call, 0 fan-out, 0 inference, response ≤16 KB. No
  `session`-per-row loop, no glob, no soul reads.
- **Why extend `hivemind_awareness` rather than mint a fifth tool**:
  the 2026-09-28 consolidation deliberately collapsed 15 tools into 4;
  minting `hivemind_overview` re-fragments the surface the fleet just
  repaired. An `action=` keeps `_LEGACY_TOOL_ADAPTERS` discipline,
  import-smoke coverage, and the single permission story intact.

#### 4.2 Fallback (paged subagents without MCP tools): file read

- Any session — including a `task()`-paged NES with **zero** `omega-hub`
  tools — runs:
  `cat data/coordination/hivemind_overview/latest.md`
  (or the Read tool on the same path). This is the same fallback class as
  `scripts/hivemind_post.py` (audited direct-hub/file path for the
  no-MCP condition) and must be documented alongside it in
  `HIVEMIND_TRANSPORT.md` on implementation.
- A thin CLI wrapper (`scripts/hivemind_overview.py --format md|json`,
  exit 0 on serve / 1 on stale-partial-served / 2 on error) is recommended
  so fallback callers get the same staleness header semantics as MCP
  callers without parsing JSON themselves. (Design only — not implemented
  here.)

#### 4.3 Hydration wiring (M15)

- `data/coordination/SESSION_ANCHOR.md` gains one line pointing at
  `data/coordination/hivemind_overview/latest.md` as the **first**
  big-picture read on session start / post-compact hydration, before any
  per-session fan-out.
- Entity `session_gnosis.md` files may quote overview rows, but the overview
  is **input**, not replacement: gnosis remains per-agent working memory;
  the overview remains team projection. No agent writes to the overview
  except the harvester.

---

### 5. Failure integrity (M23): never synthesize across broken/missing reads

**Law restated**: per `SOVEREIGN_MANDATES.md` §23 and rule
`04-sovereign-search.md`, a broken mandatory read → STOP + report
`[TOOL-CHAIN-COLLAPSE]`-class signal. For the harvester the mandatory reads
are the hot-store snapshot set and the cold `HALL_OF_RECORDS` files it
attempted. Parametric completion of an unreadable row with an LLM guess is a
Sovereign Boundary Violation.

#### 5.1 Decision matrix (exact behavior)

| Condition | Harvester behavior |
|---|---|
| **All attempted reads ok** | Write `latest.{json,md}` with `status=FRESH`, `gaps=[]`. Copy to `latest_good.*`. Write `history/ov_*.json`. Exit 0. |
| **Partial failure** (≥1 row unreadable: hot-miss + cold EACCES/corrupt-JSON/mtime-race, or `hot_store_get_all()` throws for a shard) | **Publish with gaps, do not refuse**: write `latest.{json,md}` with `status=STALE_PARTIAL`, `coverage={attempted,ok,gaps}`, one `⚠️ GAP` marker per failed row in both json (`gaps[]`) and md (`## Gaps`), `digest_source=gap` rows excluded from counts. **Do NOT overwrite `latest_good.*`** (it stays the last fully-fresh projection). Append history record with `status` + per-gap `reason`. Log one line to `data/coordination/SYSTEM_FAILURE_LOG.md` + post Hivemind `intent=blocker` ("harvester partial: X/Y rows, gaps: …"). Exit 0 **only** because a degraded-but-honest projection was published; the gap section is the fail-loud signal. |
| **Total failure** (hot store unreachable AND cold glob raises, or overview dir unwritable) | **Refuse to publish**: do NOT touch `latest.*` (leave the previous projection with its honest timestamp). Write `error.json` (`{status:ERROR, at, reason, failing_inputs}`). Log to `SYSTEM_FAILURE_LOG.md` + Hivemind `intent=blocker`. Exit non-zero (2 = transport/store failure, mirroring `hivemind_post.py` exit-code discipline). Readers seeing `age_s` grow past `2×interval` treat the overview as expired (§5.2). |
| **Digest missing/corrupt on an otherwise-readable row** | Not a failure: use `[no-digest]` fallback (§2.4). Never a gap, never an error. |
| **Clock skew / future timestamps** | Clamp display to `generated_at`; flag row with `[clock-skew]` suffix rather than reordering silently. |

#### 5.2 Reader-side expiry rule

- `age_s = served_at − generated_at`. If `age_s > 2×interval_s` (default
  >600 s) **or** `status != FRESH`, readers must treat the projection as
  advisory and re-verify any row they intend to act on via
  `action="session"` / cold file before paging work. The `overview` action
  returns this rule in its header so no-MCP file readers see it in the md
  footer too.

#### 5.3 Worked gap-marker example

```json
{"agent_id": "opencode/grokster", "session_id": "ses_9f…",
 "reason": "hot-miss + cold JSON parse error (truncated write, mtime 12:04:31Z)"}
```

```markdown
- ⚠️ GAP: grokster/ses_9f… unreadable (cold JSON truncated) — last good row in latest_good.md @12:00Z; do NOT assume idle.
```

Note the final clause: a gap must never read as absence (cf.
`HOW_THE_HIVEMIND_WORKS.md`: empty view ≠ no work).

---

### 6. Mandate analysis

#### 6.1 M2 Engine-Stack Firewall — placement (no stack logic in `src/omega/`)

- **Allowed homes**: `mcp_servers/omega_hub/hub_tools/` (new `overview`
  read action + harvester helpers), `mcp_servers/omega_hub/background.py`
  (if hosted as a hub coroutine), `scripts/hivemind_harvest.py` +
  `scripts/hivemind_overview.py` (if hosted as cron/systemd),
  `data/coordination/hivemind_overview/` (artifacts),
  `config/` timer units. All are **control-plane / operations**, not Core.
- **Forbidden**: anything under `src/omega/` (universal runtime),
  `config/wads/*` (stack implementations), entity `soul.yaml` writes.
  The harvester reads snapshots; it never imports entity traits, slot
  logic, or stack config to decide content.
- **Firewall test on implementation**: `git status --porcelain` for the
  change must show zero paths under `src/omega/`; reviewer rejects
  otherwise.

#### 6.2 M1 AnyIO Absolute — async discipline

- All harvester I/O (hot-store locks, `anyio.Path` globs/reads/writes,
  atomic rename, fsync) uses **AnyIO**; blocking JSON/parse work wrapped in
  `anyio.to_thread.run_sync`. **No `import asyncio`** anywhere in the new
  surface (hub code or scripts' async paths). The existing
  `hot_store_*`/`_cold_path`/`_latest_path` helpers already follow this;
  the harvester reuses them rather than re-implementing store access.
- Import-smoke (`tests/test_hub_import_smoke.py`) and
  `make check-hub-imports` must cover any new module from day one (lesson of
  the 2026-09-28 outage: consolidation deleted a name nothing imported).

#### 6.3 M7 Local-First & Synergy — zero inference in the loop

- Harvester performs **concatenation only**: no LLM calls, no embeddings,
  no rerank, no cloud provider invocation, no `providers.yaml` routing.
  `generator.llm_used=false` is asserted in every output.
- Intelligence stays where it belongs: frontier/cloud models may help an
  **agent compose its own `digest` at post time** (build/synthesis ledger),
  while the **background loop stays local** (execution/privacy ledger).
  This is the synergy invariant (`SOVEREIGNTY_INVARIANT_SPEC.md`), not a
  forced air-gap.
- Unknown-provider default-cloud classification is unaffected (harvester
  calls no provider at all).

#### 6.4 M8 Zero Telemetry — local files only

- Inputs: local hot-store + local `HALL_OF_RECORDS`. Outputs: local
  `data/coordination/hivemind_overview/`. Observability: local
  `SYSTEM_FAILURE_LOG.md` + local Hivemind post. **No analytics, no
  phone-home, no external metrics endpoint.** A harvester that POSTs the
  overview anywhere off-host is an M8 violation by construction and must
  fail review.
- The `overview` action serves bytes already on disk; it introduces no new
  network path beyond the existing hub MCP transport (`:8016` loopback).

#### 6.5 M15 Sovereign Continuity — overview as gnosis input

- The overview is the **team complement** to per-agent `session_gnosis.md`:
  gnosis preserves *my* thread across compaction; the overview restores
  *everyone else's* thread in one read. Together with `SESSION_ANCHOR.md`
  they form the hydration triple: anchor (where am I) → overview (who is
  doing what) → gnosis (where was I).
- The overview must therefore be **stable-path, stable-schema, and
  human-greppable** (`latest.md` headings fixed; `latest.json` `schema`
  versioned). Any schema bump is additive with a version string, never a
  silent reshape that breaks post-compact parsers.

#### 6.6 M28 Sovereign Artifact Preservation — retention/pruning (explicit + auditable)

M28 (and the M29 reaper incident it memorializes: `background.py`
`f.unlink()` with no tombstone while temple-grade read 53/53) governs every
lifecycle transition of overview artifacts:

- **Default retention (proposed, Architect to ratify)**:
  `latest.*` + `latest_good.*` retained indefinitely (tiny);
  `history/` retains the last **288 cycles (24 h at N=300 s)** as hot
  files; older cycles are **moved** (atomic rename) to
  `data/coordination/hivemind_overview/archive/<YYYY-MM>/`, never unlinked.
  Archive is cold but online and greppable.
- **Allowed transitions**: `hot → archive` (move with manifest line in
  `archive/MANIFEST.jsonl`: `{ov_id, moved_at, sha256, reason: retention}`).
  The harvester/reaper may **only move**; it may not unlink, rewrite
  history files, change `status`, or fabricate terminal decisions.
- **Deep-archival / destruction**: moving `archive/` to cold storage
  requires a **signed manifest + operator authorization**; destruction of any
  overview artifact requires a **deliberate human act recorded in
  `PIVOT_LOG.md`** (M28 verbatim). Absence of a manifest blocks the move.
- **Enforcement hooks (on implementation)**: extend `make check-sahs`-class
  thinking — one authoritative overview surface (`hivemind_overview/`);
  a policy-constants check asserting a single retention constant (not two
  divergent thresholds); audit tests asserting no `unlink`/`rmtree` call
  exists in the harvester path (grep-gate, mirroring the
  `handoff.stale_threshold_days == handoff.hot_storage_max_days` lesson).
- **Recovery**: any archived `ov_*.json` replays into `latest_good` view by
  explicit operator copy; history files are content-addressable by
  `generated_at` + sha256 in the manifest.

---

### 7. Open questions for the Architect

1. **Interval N**: ratify **300 s ±30 s jitter** (§3.1), or direct an
   alternative (120 s incident mode / 900 s constrained mode)? Should N
   adapt to fleet size (e.g. N=600 s when sessions >40)?
2. **Retention depth**: ratify **288 hot cycles → monthly archive move**
   (§6.6)? Is 24 h hot sufficient, or is 7 d (2016 files, ~16 MB) preferred
   for post-incident forensics?
3. **Hosting shape** (three options, recommendation below):
   - **(a) Hub tool + `background.py` coroutine** (in-process, AnyIO-native,
     shares hot-store locks, no extra process). Recommended default:
     fewest moving parts, inherits hub health/watchdog story.
   - **(b) Sidecar daemon** (separate systemd unit polling hub JSON-RPC).
     Better fault isolation (harvester crash ≠ hub crash) at the cost of a
     second supervised process + auth surface.
   - **(c) Cron/systemd timer script** (`scripts/hivemind_harvest.py` every
     N, mirroring the background-researcher 15-min timer). Simplest to audit
     and most M28-friendly (each run is a discrete auditable invocation),
     but pays process-spawn + cold-import cost every 5 min.
   Which shape, and may the read-path `action="overview"` ship
   independently of the writer choice (recommended: yes)?
4. **Wire name**: `digest` (§2.1) or literal `aggregate_summary`? Mechanical
   rename — needs one decision before docstring freeze.
5. **Cap**: ratify **280 chars + soft-truncate** (§2.3)? Or hard-reject
   over-cap digests (Adversary warns this reintroduces silent-no-op risk)?
6. **Scope of inputs**: team agents + subagent NES sessions (§3.2) — should
   the harvester also include handoff-queue depth / lock table snapshot in
   v1, or stay strictly to awareness posts (recommended: posts only; queues
   are a v2 join)?
7. **Read-path independence**: may `scripts/hivemind_overview.py` file-read
   fallback ship even if MCP `action="overview"` is deferred (recommended:
   yes — paged subagents need it first)?

---

## L3 — Raw Signal (ground facts consumed; no synthesis beyond §§1–7)

- Post contract: `mcp_servers/omega_hub/hub_tools/tools.py:2357-2523`
  (`hivemind_awareness`, 7 required fields, absence-not-truthiness
  validation, JSON-error-string on rejection, caller must check return).
- Hot/cold store: `mcp_servers/omega_hub/state.py:309-310`
  (`HALL_OF_RECORDS = data/knowledge/HALL_OF_RECORDS`),
  `:315-373` (sharded hot store + `hot_store_{set,get,get_all,prune_stale}`),
  `:595-602` (`_cold_path(agent_id,sid)`, `_latest_path()`),
  `:381` (`HEARTBEAT_TTL = 2700`).
- Awareness read paths: `tools.py:2548-2649`
  (`get` with TTL expiry + cold backfill; `continuation` hot+cold;
  `session` hot-then-cold-scan; `list` per-agent or global).
- No-MCP fallback precedent: `scripts/hivemind_post.py:1-66` (exit
  0=accepted/read-back, 1=rejected, 2=transport failure) +
  `docs/architecture/HIVEMIND_TRANSPORT.md:105-192` (paged subagents lack
  `omega-hub` tools; sanctioned fallback; upstream limitation, not repo
  defect) + `tests/test_hivemind_post_script.py` (8 offline tests).
- Coordination-plane layout: `data/coordination/` (464 entries;
  `HMC_COLLABORATION_HUB.md`, `SESSION_ANCHOR.md`, `SYSTEM_FAILURE_LOG.md`,
  `TASK_REGISTRY.json`, `TRACKING_ARCHITECTURE.md` live here).
- Hivemind laws: `docs/architecture/HOW_THE_HIVEMIND_WORKS.md`
  (presence vs packets vs receipts vs discovery; "packet store is the
  record"; empty `inbox`/`get` ≠ absence).
- Background-loop precedent:
  `docs/architecture/R_BACKGROUND_RESEARCHER_ARCHITECTURE.md`
  (systemd timer every 15 min; triage→search→extract→distill→converge→update;
  local SearXNG + cloud fleet + Gemma distiller).
- Mandates: `SOVEREIGN_MANDATES.md` §§M1/M2/M7/M8/M15/M23/M28
  (+M29 reaper lesson referenced by M28); condensed map in
  `MANDATES_CONDENSED.md`; search protocol in
  `.opencode/rules/04-sovereign-search.md` (5 tiers + `[TOOL-CHAIN-COLLAPSE]`).
- Firewall: Core = `src/omega/` + `config/omega.yaml` + `opencode.json`;
  Stacks = `config/wads/<stack>/` (`SOVEREIGN_MANDATES.md` §2).
- Procedures consulted, not altered: `scripts/hivemind_post.py`,
  `mcp_servers/omega_hub/background.py`, `mcp_servers/omega_hub/server.py`
  (`_LEGACY_TOOL_ADAPTERS`), `tests/test_hub_import_smoke.py`.

**Tool calls performed (M23 active-call duty)**: filesystem reads of
`docs/architecture/HOW_THE_HIVEMIND_WORKS.md`,
`docs/architecture/HIVEMIND_TRANSPORT.md`,
`docs/architecture/R_BACKGROUND_RESEARCHER_ARCHITECTURE.md`,
`mcp_servers/omega_hub/hub_tools/tools.py` (post implementation),
`mcp_servers/omega_hub/state.py` (store paths/TTL),
`scripts/hivemind_post.py`, `.opencode/rules/04-sovereign-search.md`,
`SOVEREIGN_MANDATES.md`, `MANDATES_CONDENSED.md`, `data/coordination/`
listing. No parametric claims beyond these sources; no web fetch needed
(local-first tier sufficed — design is repo-grounded, not SOTA-dependent).

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ HIVEMIND-HARVESTER-DESIGN-v1.0.0 ⬡ 2026-10-03 ⬡ DESIGN-ONLY, UNCOMMITTED ⬡*
