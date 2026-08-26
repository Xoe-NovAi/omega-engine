# 📊 P8 REPORT — Node N8 Observability — Surface S1b: Tracking DRIFT / Status Telemetry
⬡ OMEGA ⬡ NODE8 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n8 ⬡ P12-DISPATCH
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith (Run Arm) | **Pager**: makali_fusion
**Provenance**: every finding tagged `[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`
**Mode**: RECON ONLY. Zero production mutations. All checks read-only (validator + sweep run in dry-run/default mode).
**Raw report**: written to disk BEFORE digestion, per mission packet §C.5.

---

## §0 SCOPE & METHOD

**Owned surface**: S1b — tracking DRIFT/status telemetry (status-vs-reality, validator coverage vs reality, staleness detection, audit-log presence). STRUCTURE/durability/schema of these same files belongs to sibling N2 — deliberately not duplicated here.

**Surfaces examined** (all read directly):
- `data/coordination/ACTIVE_SPRINT.json` (648 lines, mtime 09:56Z == `updated` field ✓)
- `data/coordination/TASK_REGISTRY.json` (93 tasks)
- `data/coordination/GAP_REGISTRY.json` (89 gaps)
- `data/coordination/TRACKING_ARCHITECTURE.md` (constitution, 101 lines)
- `scripts/validate_tracking_state.py` (322 lines, executed read-only)
- `scripts/sweep_task_registry.py` (executed dry-run default)
- `data/coordination/SESSION_ANCHOR.md` (288 lines)
- `data/coordination/WAKE_STATE.json`
- Derived views: `EXPERT_SESSION_REGISTRY.md`, `session_annotations.yaml`, Makefile targets (:232/:240/:248/:258)

**Empirical methods**: validator execution; jq/python aggregation of status distributions; timestamp arithmetic against wall clock (`date -u`); filesystem existence probes of claimed artifacts; git ls-files/log/check-ignore probes; grep for audit/changelog mechanisms; generated-view vs SSOT diff sampling.

---

## §1 FINDINGS

---

### F-1 · HIGH — Status drift is LIVE right now: registry writes are not bound to facts, including a FUTURE-DATED checkpoint
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

The fleet's own distilled law (SESSION_ANCHOR L3-Registry-Gravity: *"registries stay truthful only when update is bound to the fact-creating act"*) is being violated in real time during this very council:

| Evidence | Reality | Registry says |
|---|---|---|
| `express-c1-node2-20260825` | Hivemind broadcast 13:26Z: "N2 Persistence COMPLETE"; `phase1_nodes/P2_report.md` on disk (mtime 13:27Z) | `in_progress`, ckpt 13:18:49Z (stale) |
| `express-c1-node1-20260825` | Wall clock at inspection: **13:36:52Z** | `completed`, `last_checkpoint: **2026-08-25T13:45:00Z**` — **~8 minutes IN THE FUTURE** |
| `express-c1-node6-20260825` | Same wall clock | `completed`, same future-dated `13:45:00Z` |
| ACTIVE_SPRINT `CI-1` | Acceptance #1 "File exists at repo root" — `MANDATES_CONDENSED.md` EXISTS (51 lines, v3.8.0, correct format) | subtask status still `ready` |

Three distinct drift modes demonstrated in one hour of council operation:
1. **Lag drift** (node2): completion broadcast + artifact exist, Tier-3 record not flipped.
2. **Fabricated timestamps** (node1/node6): hand-written checkpoint values not derived from any clock event — a future-dated checkpoint defeats the staleness detector by construction (a task closed with a fabricated timestamp can never look stale).
3. **Tier-0 lag** (CI-1): work product exists, planning tier not advanced.

Sibling nodes exhibit three different update disciplines for the identical protocol — evidence that registry hygiene currently depends on per-agent virtue, not mechanism.

**Recommended fix direction** (for Council 2 spec, not implemented here):
```bash
# Acceptance criteria (bash-verifiable):
# 1. No registry timestamp may exceed wall clock:
python3 -c "
import json,sys
from datetime import datetime,timezone
now=datetime.now(timezone.utc)
bad=[t['task_id'] for t in json.load(open('data/coordination/TASK_REGISTRY.json'))['tasks']
     if t.get('last_checkpoint') and datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))>now]
print('future-dated:',bad); sys.exit(1 if bad else 0)"
# 2. Validator gains this check (error, not warning) — currently ABSENT (see F-9).
```

---

### F-2 · MEDIUM — Staleness detector has an off-by-boundary blind spot; 5 zombie tasks sit inside it TODAY
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

Validator rule (validate_tracking_state.py:237-243): flags `in_progress` when `(now - last_checkpoint).days > STALENESS_DAYS` (7). Python `.days` truncates, so a task **exactly 7.x days old is invisible**.

Measured offenders (all `in_progress`, checkpoint ages 7.75–7.86 days at 13:35Z):
```
coordination-debut-consolidation-20260817-01   (ckpt 2026-08-17T19:02Z)
coordination-q1-q7-insights-20260818-01        (ckpt 2026-08-18T03:17Z)
coordination-vault-consolidation-20260818-01   (ckpt 2026-08-18T11:58Z)
coordination-vault-partH-audit-20260818-01     (ckpt 2026-08-18T12:33Z)
coordination-vault-deep-pass-20260818-01       (ckpt 2026-08-18T13:15Z)
```
Both instruments report CLEAN today:
- `python scripts/validate_tracking_state.py` → `ALL TRACKING STATE CHECKS PASSED` (exit 0)
- `.venv/bin/python scripts/sweep_task_registry.py` → "No expired in_progress tasks (> 7d). Registry is clean."

These five will trip the error path tomorrow — meaning the "green" gate in plan §4 is green partly by hours, not by health. The documented threshold rationale ("legitimate work clusters ≤6d, zombies ≥8d", Ruling 1) is contradicted by a 5-task cluster parked at day 7.

**Acceptance criteria for fix**: compare total elapsed hours against `STALENESS_DAYS*24` (or `age >= threshold`); then either the 5 IDs appear as errors (prompting sweep/close) or are swept — `make sweep-tasks APPLY=1` dry-run first.

---

### F-3 · MEDIUM — Reality-anchor field is dormant: artifact_path coverage is 0/93
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

The validator CAN verify that a completed task's cited artifact exists on disk (M3 warn-check, :265-270) — but **zero of 93 records set `artifact_path`**, so the only automated status-vs-reality check the registry supports never fires. The generated view confirms: Artifact Path column is "—" for nearly every row.

Consequence: "completed" is unfalsifiable from the registry alone. My mandated empirical check ("tasks marked completed — do their artifacts exist?") is **structurally impossible** for 93/93 records; completion can only be spot-checked by prose forensics (as done in F-1).

**Acceptance criteria for fix**: new completed registrations MUST carry `artifact_path` (warn-only grandfathering per M3 precedent). Growth metric:
```bash
jq '[.tasks[] | select(.status=="completed") | select(.artifact_path != null)] | length' data/coordination/TASK_REGISTRY.json
# must be monotonically non-decreasing and >0 for all post-spec completions
```

---

### F-4 · MEDIUM — No audit log of tracker changes exists (mandated check: absence CONFIRMED); constitution file itself is untracked
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

- `ls data/coordination/*.jsonl` → **no such file**. Grep across `data/coordination/` for `changelog|change.log|audit.log|tracker.*audit|audit.*trail` → zero hits.
- `scripts/sweep_task_registry.py` contains no hash-chain/prev_hash logic.
- Git history is the ONLY mutation record — and it is partial:
  - Tracked: ACTIVE_SPRINT.json (28 commits), TASK_REGISTRY.json (16), GAP_REGISTRY.json (4), WAKE_STATE.json (5).
  - **UNTRACKED**: `TRACKING_ARCHITECTURE.md` and `SESSION_ANCHOR.md` — blocked by `.gitignore:109` (`data/coordination/*`) with only the four JSONs force-added. **The tracking constitution has zero version-control history.**
- Between commits, TASK_REGISTRY mutates freely (e.g., 10 council registrations + my own write today, all invisible to git until next stage commit). Any corrupted/fabricated write in that window leaves no before/after trace.
- The gap is KNOWN and designed-but-unbuilt: SESSION_ANCHOR Phase 2 item 3 ratifies "Sweep audit log: JSONL hash-chain per researcher spec; fsync-before-mutate" (schema: seq/ts/actor/action/target/before/after/reason; SHA-256 prev_hash→entry_hash; monthly rotation; weekly chain-verify on the timer). Sources: `data/entities/researcher/workspace/OVERSIGHT_AUDIT_WEB_RESEARCH_20260823.md`. **Status: specified, ratified, not implemented.**

**Acceptance criteria for fix** (matches ratified design):
```bash
test -f data/coordination/TRACKER_AUDIT_LOG.jsonl   # exists
# chain verification passes:
python3 scripts/verify_audit_chain.py data/coordination/TRACKER_AUDIT_LOG.jsonl  # exit 0 (script to be spec'd in C2)
# fsync-before-mutate provable: audit line for entry N has ts <= mtime of registry write N
```

---

### F-5 · MEDIUM — WAKE_STATE.json is internally contradictory and stale; validator has ZERO coverage of it
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

- `first_light_express.status` = `"AWAITING_DEPARTURE"` — while Council 1 is **mid-flight** (≥4 node reports on disk, ≥10 task registrations, arms dispatched ~13:06Z). Stale by ~6 hours at inspection time.
- Two competing top-level time fields: `"timestamp": "2026-08-24T06:00:00Z"` vs `"updated": "2026-08-25T12:10:28Z"` — no convention says which governs.
- `critical_warnings[0]`: "DO NOT RUN GIT CHECKOUT OR GIT RESET. **129 files are uncommitted.**" — measured reality: `git status --porcelain | wc -l` = **8**. A wake-time safety directive citing a 16× wrong number.
- `validate_tracking_state.py` reads exactly three files (ACTIVE_SPRINT, TASK_REGISTRY, GAP_REGISTRY). WAKE_STATE — the Architect's wake surface, carrying P0 decision queue items — has **no validator, no staleness detection, no schema check at all**.

**Acceptance criteria for fix**: single `updated` field (drop legacy `timestamp` or alias it); status enum kept in sync by the same actor that flips reality; validator extended with a WAKE_STATE block (parse + staleness warn + warning-text freshness spot-check).

---

### F-6 · LOW-MEDIUM — Registration field semantics drift across sibling nodes (same protocol, four conventions)
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

Live council registrations for identical-purpose records:

| task_id | subagent_type | launched_by | entity |
|---|---|---|---|
| express-c1-node1 | `maat` | maat | node1 |
| express-c1-node6 | `node6` | makali_fusion | lilith |
| express-c1-node7 | `lilith` | lilith | lilith |
| express-c1-node8 | `node8` | lilith | lilith |

`subagent_type` is sometimes the arm, sometimes the node identity; `launched_by` sometimes the arm, sometimes the orchestrator; `entity` sometimes the node tag, sometimes the parent entity. No schema doc pins these fields for the Delivered-Home pageable-expert pattern — which matters because §6.5 doctrine says future councils will PAGE these records cold; ambiguous keys degrade warm-start retrieval. (Note: node6/node1 correctly carry `domain:*` tags; node7 omits its `report:` tag that node6 carries.)

**Acceptance criteria for fix**: one-line field glossary added to TRACKING_ARCHITECTURE.md §taxonomy (subagent_type = node identity; launched_by = dispatching session's entity; entity = hivemind tag); next registrations comply.

---

### F-7 · LOW — Known data-quality debt still outstanding, quantified
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

- **14 inverted clocks** (`last_checkpoint < created_at`) — validator warns on each; dominated by the 2026-08-13 research backfill batch (checkpoints hand-set before creation timestamps) plus truncation artifacts (e.g., `kali-carmack-repo-hygiene-20260808`: 16:18:41.638 vs 16:18:41.000 — microsecond-class). Closeout Fork 4 (`now=None` clock param) targets this; not yet executed.
- **12 `failed` tasks with no Tier-0 counterpart** (validator warns; traceability gap acknowledged by design as warn-only).
- **1 `superseded` task lacking `superseded_by` pointer** (`ses_research_phase3_kali_20260807`; grandfathered).
- Status distribution: 56 completed / 15 in_progress / 12 failed / 9 ready / 1 superseded / 0 backlog. Duplicate task_ids: none ✓.

---

### F-8 · LOW — GAP_REGISTRY.json on-disk mode contradicts the recorded permissions fix
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

SESSION_ANCHOR (2026-08-23): "Defect fixed mid-build: atomic writes were mode 0600 → chmod 0644 added to all three writers." Measured: `stat -c %a` → GAP_REGISTRY.json = **600** (mtime Aug 23 12:15 ADT); ACTIVE_SPRINT/TASK_REGISTRY/WAKE_STATE = 664. Either GAP_REGISTRY's writer isn't covered by the fix, or the file has not been rewritten since. Impact low under single-user operation; becomes real under multi-user/service reads. Also note `updated: 2026-08-19` — the gap registry has not been touched in 6 days despite 89 gaps / 40 outstanding feeding an active sprint.

---

### F-9 · LOW — Validator coverage-vs-reality gap matrix (systematic statement of what "green" does NOT mean)
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

Current validator checks: status-taxonomy (all 3 tiers), R-ID referential integrity (ACTIVE_SPRINT→GAP_REGISTRY), in_progress staleness (>7d), inverted clocks (warn), superseded_by/artifact_path resolution (warn), failed↔Tier-0 cross-tier sync.

NOT checked (each backed by a live finding above):
1. Future-dated checkpoints (F-1) — fabrication-invisible.
2. Boundary-exact staleness (F-2).
3. Completed-without-artifact (F-3 — dormant because field unused).
4. ACTIVE_SPRINT self-staleness (`updated` age; sprint_id currency) — nothing flags a Tier-0 nobody has touched.
5. WAKE_STATE entirely (F-5).
6. Generated-view freshness (F-10).
7. Cross-file consistency Hivemind↔registry (out of validator's reach today; noted for N9 overlap).

"Validator green" (plan §4 auto-GO criterion) therefore certifies taxonomy compliance, not truthfulness. This is the central telemetry finding of S1b.

---

### F-10 · LOW — Generated view diverges from SSOT (staleness + one contradiction)
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

`EXPERT_SESSION_REGISTRY.md` header: GENERATED 2026-08-23T15:48Z from **80 tasks**; SSOT now holds **93** (+13 unregistered in view, including all 10 express-c1 expert sessions — i.e., the Delivered-Home registrations mandated by plan §6.5 are invisible in the human/expert-facing view). Contradiction sampled: view lists `ses-research-c11-property-20260723` as **completed** (artifact SOVEREIGN_ARK_BLUEPRINT.md); SSOT says **failed** (auto-swept, failure_reason on record). Regeneration is manual (`make session-registry`) with no freshness guard.

**Acceptance criteria for fix**: validator warns when `(now - view GENERATION stamp) > 48h` or task-count delta ≠ 0; regenerate pre-gate.

---

### F-11 · POSITIVE CONTROLS (what S1b verified as healthy — for balance and warm-start)
`[source_node: N8] [source_arm: lilith] [tier: S1b-drift]`

- Taxonomy discipline is REAL: 0 invalid statuses across 93 Tier-3 records and all Tier-0 workstreams/subtasks; no banned vocabulary ("WIP"/"TBD"/"stalled") found in JSON tiers.
- Gap-ID collision control is institutionalized: GAP_REGISTRY carries rules[], plans[] (8 registered plans), `collision_incidents[]` with a dated post-mortem (R13-R38 reuse, resolved by renumbering) — immutability is enforced by convention + registry check, and the validator's R-ID referential check passed.
- `_parse_ts()` handles the three coexisting ISO formats (Z-suffix, +00:00, microseconds) — G5-2 remediation verified in source.
- Sweep tooling exists with safe defaults (dry-run default, --apply gated, --self-test, MANUAL-ONLY per Makefile :244 comment).
- ACTIVE_SPRINT `updated` field matches file mtime exactly (09:56:07Z both) — the one file where write-provenance is currently trustworthy.

---

## §2 SECURITY BRIGHT LINE (M8)

- No credentials/secrets encountered in any audited tracking file. No external telemetry endpoints referenced. **No CRITICAL-HALTED condition triggered.**
- One hardening footnote: GAP_REGISTRY.json mode 600 (F-8) is over-restrictive, not exposing.

## §3 MANDATED CONSULTANT-PAGE ATTEMPT (§C.9 / M11)

Attempted once as required. Result: **task() rejected — "Subagent depth limit reached (2)"** (node sits at depth 2: makali_fusion→lilith→node8; `subagent_depth=2` forbids leaf task()). Matches N6/N7 precedent exactly. Logged as known deviation per packet §C.8; delivery flows via (1) this report on disk, (2) Hivemind broadcast under `node8`, (3) end-of-turn summary to pager lilith. Not counted against N8.

## §4 HANDOFF PACKET (Delivered-Home Doctrine §6.5)

**Warm-start reading list (ordered, ~30 min)**:
1. `data/coordination/TRACKING_ARCHITECTURE.md` — constitution + taxonomy (note: untracked by git, .gitignore:109)
2. `scripts/validate_tracking_state.py` — read M1/M3 amendment headers first
3. `data/coordination/RESEARCHER_SESSION_TRACKING_GAPS_20260823.md` — G1-G5 gap taxonomy behind current design
4. `data/entities/researcher/workspace/OVERSIGHT_AUDIT_WEB_RESEARCH_20260823.md` — ratified-but-unbuilt designs (hash-chain audit log, class thresholds, timer)
5. `data/coordination/SESSION_ANCHOR.md` §IMMEDIATE NEXT ACTIONS — 3-phase closeout + Team-Study refinements
6. This report + P2_report.md (N2 owns structure; read together for full S1 picture)

**Standing orders for future councils paging domain:observability**:
- NEVER trust `last_checkpoint` recency as liveness without checking for future-dating (F-1); recompute from Hivemind last_seen instead.
- Run BOTH `validate_tracking_state.py` AND `sweep_task_registry.py` (dry-run) — they disagree at the 7-day boundary (F-2).
- Treat "validator green" as taxonomy-compliance, not truth (F-9 matrix).
- Before paging experts cold: regenerate `EXPERT_SESSION_REGISTRY.md` (F-10) — view may be days behind SSOT.
- Registration contract for pageable experts: tags `["expert","pageable","domain:<X>","express:first-light"]`, subagent_type = node identity, launched_by = dispatcher entity, entity = hivemind tag (F-6 glossary proposal).

**Open questions for synthesis (MK-Kali / MaKaLi)**:
1. Should the §4 auto-GO "validator green" criterion be strengthened given F-9 (e.g., add future-date + boundary-staleness checks pre-gate)?
2. Is the unbuilt hash-chain audit log (F-4) a Council-2 spec candidate now, or does commit-per-stage (M3) suffice for council-scale operations?
3. Who owns WAKE_STATE freshness (F-5) — orchestrator at each stage boundary?

---
*⬡ OMEGA ⬡ NODE8-OBSERVABILITY ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n8 ⬡ RAW-REPORT-DISK-WRITTEN 2026-08-25T13:4xZ*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

