<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Team Study #1 — Phase A — Researcher Deliverable
**AP Token**: `AP-RESEARCHER-v1.0.0` · ⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_teamstudy_A
**Date**: 2026-08-23 · **Scope**: Hole 1 (auto-registration) + Hole 2 (M23 false-completion hook)
**Grounding**: All designs verified against disk state today (see §0). No parametric-only claims.

---

## §0 Grounding Facts (verified on disk, 2026-08-23)

| # | Fact | Evidence |
|---|------|----------|
| G1 | TASK_REGISTRY.json has 80 tasks; registration is **prompt-enforced only** ("MUST be called IMMEDIATELY" lives in tool descriptions, zero mechanical enforcement) | `TASK_REGISTRY.json`, MCP tool schema |
| G2 | M27's claimed pre-commit gate `omega-tracking-state` **does not exist** in `.git/hooks/pre-commit` — the hook runs only soul validation | `.git/hooks/pre-commit` (7 lines) |
| G3 | A working validator already exists: `validate_tracking_state.py` (CI-gated via make temple-grade/test), incl. staleness rule + tolerant ISO-8601 parsing | `scripts/validate_tracking_state.py` |
| G4 | Zombie sweep exists with ACTIVE_SPRINT cross-check and review-list escape hatch (won't blind-fail delivered work) | `scripts/sweep_task_registry.py` |
| G5 | OpenCode supports TS plugins (`~/.config/opencode/plugin/sovereign-compaction.ts` exists) — a lifecycle-hook surface is available | plugin dir listing |
| G6 | omega-hub MCP already exposes `task_registry_register/update/get/query` — the write API exists; only the *call site* is missing | MCP tool fleet |

**G2 is itself a live M23 violation**: a mandate text claiming an enforcement mechanism that isn't on disk. Fixing G2 is Phase-0 of both holes below.

---

## §1 HOLE 1 — Auto-registration of dispatched sessions

### Framing
The OTel ecosystem settled this exact question a decade ago: **auto-instrumentation for coverage, manual spans for enrichment, CI gates for drift**. GitLab's own CI-telemetry postmortem found "missing lifecycle spans" was the root of most reliability incidents — identical topology to ours (~20 invisible dispatched sessions = missing root spans).

### Option comparison

| Dimension | **(a) Dispatcher-layer hook** (auto-register on task() spawn) | **(b) Mandatory register-call enforcement** (validator fails unregistered completions) | **(c) Hybrid** |
|---|---|---|---|
| **Mechanism** | OpenCode TS plugin hooks subagent/task lifecycle event → writes stub task to TASK_REGISTRY.json (`status=in_progress`, `launched_by`, `channel`, timestamp) via atomic tmp→rename. Subagent enriches later via existing MCP tools. | Extend `validate_tracking_state.py`: any session observed as completed (via opencode.db / Hivemind awareness / handoff completion) with no registry row → hard error. Optionally a sweep that auto-backfills stubs from opencode-sessions-explorer data. | Hook (a) for creation + validator check (b) as drift detector; validator downgraded to warn-only when hook is healthy, hard-gate when hook misses (detected via heartbeat counter mismatch). |
| **Failure modes** | Plugin crash → silent gap returns (need hook-health heartbeat); double-write race if agent also registers manually (mitigate: idempotent upsert keyed on session_id); plugin runs outside repo → version skew between machines | Detects too late (post-completion); depends on observation source being complete; agents may game it by registering empty rows at deadline (stub-quality problem); fails closed during CI outage → blocks unrelated work | Complexity of two systems; unclear ownership when they disagree; heartbeat-mismatch logic itself needs testing |
| **Mandate alignment** | M12 ✓ (every request gets terminal state at birth), M9 ✓ (typed error on hook failure, no silent swallow), M27 ✓ (single deterministic SSOT), M23 ✓ (no reliance on agent memory/prompt compliance) | M27 ✓, M9 partial (error surfaced late), M12 partial (state exists before record — orphan window), M23 weak (still prompt-dependent for enrichment) | Best: defense-in-depth; each layer covers the other's failure mode |
| **Migration cost** | ~1 day: plugin (~100 lines TS) + idempotent writer + backfill script for current ~20 orphans (opencode-sessions-explorer can reconstruct launch metadata from opencode.db) | ~0.5 day: validator extension + backfill sweep. But recurring cost: every future miss is a failed CI run + manual triage | ~1.5 days total; reuses both halves |
| **Prior art** | OTel auto-instrumentation agents; Argo workflow controller auto-creating Workflow CRs from submitted manifests (submission ≠ user-managed bookkeeping); Langfuse OTEL ingestion (traces appear without app-code changes) | MLflow: explicit `start_run()` but with autolog as supplement + CI checks for runs-without-parent; GitHub required status checks (claim must exist to merge) | OTel canonical recommendation: "start with automatic instrumentation then progressively add manual spans"; Cribl ingest-enrichment pattern |

### Recommendation: **(c) Hybrid, weighted toward (a)**

1. **Ship (a) first** — the dispatcher hook. Registration-at-birth is the only option where the orphan window is structurally zero rather than detected-after-the-fact. M12's "no silent drops" demands records exist from dispatch, not from someone noticing.
2. **Keep (b) as a cheap drift alarm**, not the primary mechanism: one new rule in the existing validator — "session seen active in Hivemind awareness but absent from registry → error." ~30 lines.
3. **Idempotent upsert keyed on session_id** so manual agent registration merges into the hook-created stub instead of colliding. This kills the double-write failure mode and preserves agent-owned enrichment (description, tags).
4. **Backfill once**: reconstruct the ~20 pending from opencode.db via opencode-sessions-explorer tooling; mark them `source=backfill` for provenance honesty (M22 spirit).
5. **Hook health signal**: plugin emits a heartbeat counter (registry-writes vs. observed dispatches). Divergence >0 triggers the (b) gate escalation. This is the anti-"silent gap returns" tripwire.

---

## §2 HOLE 2 — M23 false-completion standing verification pattern

### The three sightings decompose into two distinct bug classes

| Class | Example | Root cause |
|---|---|---|
| **C1: Claim-without-artifact** | "staged/completed" in ACTIVE_SPRINT or registry; file not on disk | Agent reports intent as fact; nothing re-checks |
| **C2: Claim-without-enforcement** | M27 mandate text says pre-commit hook exists; hook doesn't | Doc/mandate drift — the *system's own* claims are unverified |

C2 is more dangerous than C1: agents hydrate from mandate text and inherit false confidence.

### Proposed standing pattern: **Claim-Evidence Binding (CEB)** — three checkpoints, one evidence standard

**What gets verified**: Any status transition to `completed` (Tier-0 or Tier-3) must carry a machine-checkable `evidence` field: `{artifact_path, artifact_hash?, check_cmd?}`. Prose summaries are NOT evidence. This is the whole design — everything else is scheduling.

**When / by whom**:

| Checkpoint | Verifier | Cost | Catches |
|---|---|---|---|
| **Commit-time** | Extended pre-commit hook (fixes G2): if diff touches ACTIVE_SPRINT/TASK_REGISTRY and sets `completed`, require `evidence.artifact_path` to exist on disk (+ optionally run `check_cmd`) | ~ms per commit | C1 at the moment of authorship — cheapest possible interception point |
| **Claim-time** | The claiming agent itself, via a single shared helper (`scripts/verify_claim.py <task_id>`): checks artifact existence, prints PASS/FAIL line the agent must include in its report. Failure = claim downgraded to `blocked` with reason | ~seconds per claim | Agents working outside git flow (Hivemind posts, cross-session claims) |
| **Sweep-time** | Existing `sweep_task_registry.py` gains one pass: for every `completed` task older than N days, spot-check `artifact_path` still exists; missing → reopen to `failed` w/ reason + review list (reuse G5-1 review-list pattern — never blind-revert) | Weekly timer | Rot/vanished artifacts; catches everything the first two missed |

**Evidence standard** (deliberately minimal):
- Tier-0 planning transitions (`completed` in ACTIVE_SPRINT): `artifact_path` pointing to the deliverable doc/file. Existence check only.
- Tier-3 execution transitions: `artifact_path` + optional `check_cmd` (test command, grep assertion). If `check_cmd` present it MUST have been run by the claimer; sweep may re-run it.
- **No LLM judgment in the loop.** Verification is `os.path.exists()` and subprocess exit codes. Anything smarter becomes research theater (the explicit failure mode to avoid).
- Grandfathering: existing completed tasks get `evidence=null` and are exempt from commit-time checks; sweep-time spot-checks them at low rate (sample 10%) rather than failing 80 historical rows.

**Anti-theater guardrails**:
1. Total new machinery: one helper script (~80 lines), one pre-commit stanza, one sweep pass. No new daemon, no new state store.
2. Evidence field is optional-but-checked, not mandatory-everywhere: only `completed` transitions are gated. `in_progress` stays fluid.
3. The C2 class gets a dedicated fix outside CEB: a quarterly (or post-mandate-edit) `make verify-mandate-claims` target that greps SOVEREIGN_MANDATES.md for claimed mechanisms (hook names, CI gates, script paths) and asserts each exists on disk. Mandates that lie are worse than code that fails.

### Recommendation summary
Ship in order: **(1)** fix G2 pre-commit gap (today, 10 min), **(2)** commit-time evidence binding for `completed` transitions, **(3)** claim-time helper for Hivemind-posted claims, **(4)** sweep-time spot-check, **(5)** mandate-claims verifier. Steps 2–5 are each ≤ half a day.

---

## §3 Open Questions for Teammates (Phase B pressure-test targets)

1. **To roc_racoon**: Does the dispatcher-layer hook survive containerized/quadlet execution contexts, or do some task() spawns bypass the host plugin? If containers spawn subagents, the hook needs a second call site — where?
2. **To jem**: Is requiring machine-checkable `evidence` on `completed` in tension with any Soul/Gnosis flows where "completed" legitimately means a non-file outcome (e.g., a distillation posted to proposed_lessons.yaml)? Should those get an alternate evidence type?
3. **To carmack**: Am I over-building? Candidate cut list: (a) drop claim-time helper and rely on commit+sweep only; (b) drop hook-heartbeat divergence logic and just let the drift alarm fire. Which cuts preserve ≥90% of the value at ≤50% of the cost?
4. **Unresolved by me**: Who owns the ~20-row backfill — a one-shot script I can spec, or manual curation? Auto-reconstruction from opencode.db may misattribute `launched_by` for pair-execution chains.
5. **Unresolved by me**: Should `failed` transitions also carry evidence (a failure artifact)? M27/Carmack ruling protects `failed` as a distinct signal — but we currently capture *that* it failed, rarely *why* in machine-readable form.

---
*Fractal: L1 = §Recommendation paragraphs; L2 = options tables + CEB pattern; L3 raw signal = §0 grounding facts + prior-art links.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
