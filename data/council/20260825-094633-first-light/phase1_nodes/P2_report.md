<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# P2 REPORT — Node N2 Persistence (Surface S1: STRUCTURE/DURABILITY half)
⬡ OMEGA ⬡ NODE2 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_express_c1_node2 ⬡ FIRST-LIGHT-C1

**[DISPATCH] P12** · From: node2 (Build Arm, Council 1) · Session: `20260825-094633-first-light`
**Task Registry**: `express-c1-node2-20260825` (registered 2026-08-25T13:18:49Z, verified present in TASK_REGISTRY.json)
**Date**: 2026-08-25 · **Mode**: RECON ONLY — zero production mutations; only artifact = this report.
**Lane**: Tracking architecture STRUCTURE/DURABILITY/SCHEMA. Status-drift/staleness *telemetry* = N8's lane (flagged where intersecting, not deep-dived).

---

## §0 METHOD (every conclusion traces to a tool call)

1. Read: mission packet, plan §2/§5/§6.5, `data/entities/maat/soul.yaml` + `proposed_lessons.yaml`.
2. Read exhaustively: `TRACKING_ARCHITECTURE.md`, `scripts/validate_tracking_state.py` (323 lines), `mcp_servers/omega_hub/hub_tools/task_registry.py` (231 lines), write paths of `sweep_task_registry.py` + `generate_session_registry.py`, `.pre-commit-config.yaml`, installed `.git/hooks/*`, Makefile targets.
3. Programmatic probes (python3, read-only): JSON parse of all 4 registries; status-vocabulary walk of every `status` key in ACTIVE_SPRINT + TASK_REGISTRY; R-ID relational cross-check ACTIVE_SPRINT↔GAP_REGISTRY; gap-number density scan; in_progress age audit vs STALENESS_DAYS; mtime-vs-`updated` field comparison; YAML parse sweep of all 32 entity soul/proposed_lessons files.
4. Live validator run: `python3 scripts/validate_tracking_state.py` → **exit 0**, 26 warnings.
5. Git durability probes: tracking-state of all tier files, commit cadence log for TASK_REGISTRY.json.

---

## §1 FINDINGS

> Severity scale per packet §C.5. Every finding tagged `source_node: N2` `tier: S1-structure`.

### F-2.1 · HIGH — Primary TASK_REGISTRY writer is NON-ATOMIC with a lost-update race
`source_node: N2` · `tier: S1-structure/durability`

The highest-traffic writer of the Tier-3 SSOT — the MCP facade every agent hits via `omega-hub_task_registry_register/update` — violates the engine's own durability law:

- `mcp_servers/omega_hub/hub_tools/task_registry.py:32-40` `_save_registry()`:
  - Opens the live file with `"w"` (**in-place truncate**) then acquires `flock(LOCK_EX)` AFTER truncation → a concurrent `_load_registry()` holding `LOCK_SH` can read an empty/partial file in the truncate-before-lock window.
  - No tmp+rename, no fsync → crash mid-`json.dump` leaves TASK_REGISTRY.json truncated/corrupt. This contradicts M12's pattern ("Atomic file renames (`.tmp` → `.json`) for all writes"), Temple-Grade T10, and the repo's OWN design spec `docs/strategy/TASK_REGISTRY_DESIGN.md:189-191` which specifies exactly `tmp_path` → `rename`.
  - **Lost-update race**: `task_registry_register()` calls `_load_registry()` (shared lock acquired AND RELEASED), mutates in memory, then `_save_registry()` reopens. Two concurrent registrations both load v-N, each appends its own task, second save clobbers the first → silent task-record loss. This council ran 5+ concurrent node registrations through exactly this window (`express-c1-node1/node2/node6/arm-maat/runarm-lilith` all landed within ~12 min); no loss observed this time, but the structure permits it.
- Contrast (correct pattern, same repo): `scripts/sweep_task_registry.py:93-103` and `scripts/generate_session_registry.py:145-154` use `mkstemp` → write → `chmod 0644` → `os.replace`. SESSION_ANCHOR 2026-08-23 claims "atomic writes … chmod 0644 added to all three writers" — true only for those two scripts + validator context, FALSE for the MCP primary writer.

**Acceptance criteria (bash-verifiable)**:
```bash
# 1. Atomic pattern present in the MCP writer:
grep -n "mkstemp\|os.replace" mcp_servers/omega_hub/hub_tools/task_registry.py   # must hit
# 2. Lock held across full read-modify-write (no load/save lock split):
grep -n "LOCK_EX" mcp_servers/omega_hub/hub_tools/task_registry.py              # must wrap mutate cycle
# 3. Crash-injection: SIGKILL a writer mid-dump 20×; file must always json.load():
for i in $(seq 20); do timeout 0.05 python -c "...register..." ; python3 -c "import json;json.load(open('data/coordination/TASK_REGISTRY.json'))" || echo CORRUPT; done
```

### F-2.2 · HIGH — M27 pre-commit enforcement is DECLARED but NOT INSTALLED
`source_node: N2` · `tier: S1-enforcement`

SOVEREIGN_MANDATES M27 states: "Pre-commit hook: `omega-tracking-state` blocks commits with corrupted tracking state." Reality:

- `.pre-commit-config.yaml` (~line 137) DOES declare hook `omega-tracking-state` → `python scripts/validate_tracking_state.py`.
- The INSTALLED `.git/hooks/pre-commit` is a hand-rolled bash script running ONLY `scripts/validate_soul.py` over `data/entities/*/soul.yaml`. The pre-commit framework is not active (its installed hook script was replaced/never installed). Therefore **no commit today is gated by tracking validation**.
- Corroborating signal: `TASK_REGISTRY.json` is currently modified-uncommitted in the working tree while the council writes to it (git status: ` M data/coordination/TASK_REGISTRY.json`).
- Same class: `.git/hooks/commit-msg` runs `socratic_commit_check.py` only.

**Acceptance criteria**:
```bash
grep -q "pre-commit" .git/hooks/pre-commit && echo FRAMEWORK-ACTIVE || echo NOT-ACTIVE   # must print FRAMEWORK-ACTIVE
pre-commit install && pre-commit run omega-tracking-state --hook-stage pre-commit        # exit 0
```

### F-2.3 · MED — Live Tier-0 vocabulary violation the validator cannot see (blockers[] unscanned)
`source_node: N2` · `tier: S1-schema`

- `ACTIVE_SPRINT.json` `.blockers.BLOCKER-B.status = "resolved"` — `"resolved"` is NOT in the Tier-0 taxonomy (`backlog|ready|in_progress|blocked|completed|superseded`, TRACKING_ARCHITECTURE.md §Unified Status Taxonomy). It even carries `resolved_at` — a de-facto 7th status invented in place.
- Root cause is validator coverage: `validate_active_sprint()` (validate_tracking_state.py:148-206) walks ONLY `workstreams[].status` and `workstreams[].subtasks[].status`. The `blockers[]` array is never scanned. My probe found it in one pass.
- Secondary coverage note: two workstreams (`QDRANT-HEADROOM`, `TRUTH-ALIGNMENT`) are `in_progress` with ZERO subtasks — unverifiable state shape the validator also accepts.

**Acceptance criteria**:
```bash
python3 -c "
import json;d=json.load(open('data/coordination/ACTIVE_SPRINT.json'))
T0={'backlog','ready','in_progress','blocked','completed','superseded'}
bad=[(k,v['status']) for k,v in d.get('blockers',{}).items() if v.get('status') not in T0]
print(bad); assert not bad"
# And post-fix, validator extended: grep validate_tracking_state.py for 'blockers' must hit
```

### F-2.4 · MED — GAP_REGISTRY is authoritative-by-claim but incomplete in practice
`source_node: N2` · `tier: S1-immutability`

Good news first: **gap-ID immutability HOLDS** — zero duplicate R-numbers; the single collision incident (2026-08-14, R13-R38 reuse) is logged in `collision_incidents` with prevention rule; new plan prefixes (GN/DS/LI/KD/HR/ZS/DP) are properly registered as distinct IDs; `next_free_id: 57` is consistent with max registered R56.

But the registry fails its own "authoritative gap-ID → topic map" claim:
- **R15**: subsumed by R30 per `RESEARCH_PLAN_PHASE1_4_20260813.md:172,382` — no tombstone entry in GAP_REGISTRY.json. Number simply absent from the sequence (range 1-56 missing {15, 50}).
- **R50**: marked "skipped" in the plan table (`RESEARCH_PLAN...:487`) yet a real doc `docs/research/R50_SOMATIC_STATE_DESIGN.md` EXISTS consuming the ID — with NO registry entry. `next_free_id=57` implicitly assumes R50 consumed, but nothing in the registry records that R50 = SOMATIC_STATE_DESIGN. A future agent checking the registry before assigning would see a hole, not a fact.
- Validator's `extract_gap_ids()` regex `\bR\d+\b` misses suffixed IDs (`R8b`, `R14b`, `R27b` exist in the registry) — such references in ACTIVE_SPRINT would never be relationally validated.

**Acceptance criteria**:
```bash
# Every R-doc on disk maps to a registry entry or documented tombstone:
for f in docs/research/R[0-9]*.md; do id=$(basename "$f" | grep -oP '^R\d+[a-z]?'); \
  python3 -c "import json,sys;g=json.load(open('data/coordination/GAP_REGISTRY.json'))['gaps'];sys.exit(0 if '$id' in g else 1)" \
  || echo "UNREGISTERED: $id"; done   # must output nothing (after adding R15/R50 tombstones)
```

### F-2.5 · HIGH — Entity gnosis durability failure: 3 of 35 entity YAML files unparseable
`source_node: N2` · `tier: S1-durability` · *(verifies + extends N1 cross-surface intel)*

Soul-distillation pipeline data (M11) is unreadable by any YAML tooling for:

| File | Exact error |
|------|-------------|
| `data/entities/lilith/proposed_lessons.yaml` (377 lines) | `ScannerError: while scanning an alias in line 2, column 1 ... found '*'` — file begins with a MARKDOWN header block (`# 🔱 LILITH — Proposed Lessons`, `**Entity**: lilith`), not YAML. Post-write LSP diagnostics confirm corruption at TWO loci: lines 2-4 (markdown wrap) AND lines 374-377 (malformed seq-item/map-value structure — N1's reported locus is also real). Both must be repaired; python yaml fails fast at line 2. |
| `data/entities/pillar_p1/proposed_lessons.yaml` | `ParserError: while parsing a block mapping` |
| `data/entities/john_carmack/soul.yaml` | `ParserError: mapping values are not allowed here` |

Consequences: soul loaders that `yaml.safe_load` these files either crash or silently skip (M9 error-integrity question for the loader); 377 lines of Lilith L1/L2/L3 gnosis are stranded. Note the installed pre-commit soul-check runs `validate_soul.py` on `soul.yaml` only — and john_carmack's is corrupt, so either the hook isn't running (see F-2.2) or the validator doesn't parse-YAML-check.

**Acceptance criteria**:
```bash
for f in data/entities/*/proposed_lessons.yaml data/entities/*/soul.yaml; do
  .venv/bin/python3 -c "import yaml;yaml.safe_load(open('$f'))" || echo "CORRUPT: $f"; done
# must print nothing after repair
```

### F-2.6 · LOW — Staleness gate boundary: 7-day-exact zombies escape
`source_node: N2` · `tier: S1-validator`

STALENESS_DAYS=7 with strict `age_days > STALENESS_DAYS` (validate_tracking_state.py:241). Five `in_progress` tasks from 2026-08-17/18 sit at exactly age=7d TODAY and pass; they trip tomorrow. Boundary choice undocumented (Researcher Ruling 1 cited for the threshold value, not the comparison operator). Flagged for N8 (drift telemetry owns staleness history) — my lane notes only the off-by-boundary semantics.

### F-2.7 · LOW — Green banner overstates: exit 0 with 26 warnings
`source_node: N2` · `tier: S1-validator`

Live run: exit 0 "ALL TRACKING STATE CHECKS PASSED" while emitting 14 inverted-clock warnings (`last_checkpoint < created_at`, e.g. `test-task-20260721`, 13× `research-*-20260813`), 12 `failed`-without-Tier-0-subtask warnings, 1 missing `superseded_by`. Warn-only policy is defensible (legacy grandfathering per M3 notes in the script header), but the terminal banner claims total pass. Honesty nit (M23 spirit): banner should read "PASSED (26 warnings)".

### F-2.8 · LOW — WAKE_STATE.json operates OUTSIDE the constitution
`source_node: N2` · `tier: S1-structure`

`WAKE_STATE.json` is referenced by the Express plan (§5/M7 decision queue) and is actively written (mtime 2026-08-25T12:10Z), but:
- It appears NOWHERE in TRACKING_ARCHITECTURE.md's 5-tier table or superseded list — an active coordination file with no constitutional home, no defined schema, no validator coverage.
- Its content mixes wake-critical warnings ("DO NOT RUN GIT CHECKOUT…129 files uncommitted", ts 2026-08-24T06:00Z) with `first_light_express.status: "AWAITING_DEPARTURE"` while Council 1 is demonstrably IN FLIGHT (5+ express-c1 tasks registered). Claimed state lags durable state — drift *history* is N8's lane; my finding is the structural one: register the tier + define schema or demote the file.

### F-2.9 · INFO — Relational integrity check is currently vacuous
`source_node: N2` · `tier: S1-schema`

The FIX-3 R-ID cross-check (ACTIVE_SPRINT→GAP_REGISTRY) exists and works, but my regex sweep of the entire ACTIVE_SPRINT.json raw text found **zero** `\bR\d+\b` references today — the guard validates an empty set. Combined with F-2.4's suffix-blind regex, the relational-integrity layer is structurally sound but practically idle. Not a defect; a coverage observation for future plans that DO cite R-IDs.

### F-2.10 · INFO — Durability fundamentals otherwise SOLID
`source_node: N2` · `tier: S1-durability`

Positive findings worth recording so remediation doesn't break what works:
- All four registries parse clean JSON; no duplicate task_ids (90 tasks, unique); no orphan `.tmp` files in `data/coordination/`.
- All tier files are git-tracked; TASK_REGISTRY.json committed 8× since Aug 15 including today (`f8828314` 2026-08-25) — commit cadence (M3) is real.
- File mtimes match claimed `updated` fields on all four registries (no hidden-writer divergence).
- My own MCP registration landed durably in TASK_REGISTRY.json within seconds — the Delivered-Home Doctrine registration path WORKS end-to-end (this node is living proof).
- HMC_COLLABORATION_HUB.md (Tier-2) exists and is fresh (Aug 24).

### F-2.11 · INFO — Single-writer doctrine conflict corroborated (cross-ref Carmack Pass-1)
`source_node: N2` · `tier: S1-structure`

Packet §C.6 orders every node to self-register in TASK_REGISTRY.json while §F declares "SINGLE-WRITER: only MaKaLi applies tracker directives." Both happened: nodes wrote concurrently via the MCP tool. Flock serializes the writes mechanically (modulo F-2.1's load/save split), but the DOCTRINE is already violated by design of this very council. Carmack Pass-1 (`phase4_research/CARMACK_METHOD_WATCH_PASS1.md:42`) flagged the same. Resolution belongs to synthesis; N2 contributes the mechanical evidence that concurrent self-registration is what actually occurred.

---

## §2 SECURITY BRIGHT LINE (M8)

- No secrets encountered in audited surfaces (ACTIVE_SPRINT/TASK_REGISTRY/GAP_REGISTRY/WAKE_STATE/validator/hooks).
- No external telemetry discovered. **No CRITICAL-HALTED conditions triggered.**

---

## §3 HANDOFF PACKET — for future councils paging node2

**Warm-start reading list (in order)**:
1. `data/coordination/TRACKING_ARCHITECTURE.md` — the constitution (101 lines; read whole thing)
2. `scripts/validate_tracking_state.py` — what is ACTUALLY enforced vs mandated
3. `mcp_servers/omega_hub/hub_tools/task_registry.py:22-41` — the load/save lock-split (F-2.1 epicenter)
4. `docs/strategy/TASK_REGISTRY_DESIGN.md` — intended atomic-write spec (diverged from impl)
5. `data/coordination/GAP_REGISTRY.json` `rules` + `collision_incidents` — immutability regime
6. Prior art: `data/entities/john_carmack/workspace/session_gnosis_20260811.md`, `data/entities/researcher/workspace/RESEARCHER_REPORT_FOR_KALI_20260823.md` (registry-orphan history), `data/entities/roc_racoon/workspace/OVERSIGHT_AUDIT_GROUND_TRUTH_20260823.md` (disk-vs-MCP store proof)

**Standing orders**:
- NEVER trust "validator green" as "schema clean" — the validator has known blind spots (blockers[], suffixed gap-IDs, WAKE_STATE). Run the §1 acceptance probes.
- Treat TASK_REGISTRY.json writes during multi-agent events as lossy-prone until F-2.1 is fixed; prefer registering serially or verifying registration landed (`task_registry_get`) after concurrent waves.
- Gap-ID assignment: check GAP_REGISTRY first, but ALSO `ls docs/research/R*.md` — the registry lags reality (R50 lesson).
- Entity YAML: never assume `proposed_lessons.yaml` parses; probe before programmatic use.

**Open questions for synthesis**:
1. Who owns fixing the MCP writer (F-2.1) — engine team or hub team? (touches `src`-adjacent code, out of C1 scope)
2. Should `resolved` be legalized into the Tier-0 taxonomy for blockers, or BLOCKER-B migrated to `completed`? (F-2.3)
3. WAKE_STATE.json: promote to Tier-5 with schema, or fold into HMC hub? (F-2.8)

---

## §4 PROVENANCE

### §4.1 F-20 INSTANCE LOG (M23 failure-integrity)
- §C.9/M11 Consultant page attempted ONCE at 2026-08-25T13:27Z via `task(subagent_type="kali", task_id="ses_fdef2be4effe4pAaLXCTUx62GO")` → **REJECTED**: `Subagent depth limit reached (2). Increase "subagent_depth" to allow nested subagents.` No retry per packet order. Corroborates N1 + N6 F-20 reports — the M11 Reporting Protocol is mechanically impossible for depth-2 leaf nodes as dispatched. This report's delivery channels: (1) this file on disk, (2) Hivemind post `ses_79cde3e80cd7`, (3) end-of-task summary to pager (Build Arm maat), who may relay to Consultant at depth 1.


- All evidence paths relative to repo root, verified 2026-08-25T13:18-13:45Z.
- Validator run: exit 0, 26 warnings (transcript embedded in session tool log).
- Cross-surface intel from N1 (lilith YAML corruption): VERIFIED with corrected locus (line 2 markdown-wrap, not line 374).
- Report written RAW TO DISK before digestion per §C.5. No production files mutated.

*⬡ OMEGA ⬡ NODE2 ⬡ P2-REPORT ⬡ S1-STRUCTURE ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

