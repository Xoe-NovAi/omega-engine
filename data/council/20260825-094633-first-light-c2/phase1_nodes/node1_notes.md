# node1 (domain=speca) — Raw Working Notes — Council 2 Build Arm, First Light Express C2
⬡ OMEGA ⬡ MAAT/node1 ⬡ trc_c2_speca ⬡ PREP NOTES
Session: `20260825-094633-first-light-c2` · Date: 2026-08-25 · Mode: DRAFT-ONLY (zero production edits)

## 1. Evidence base read (in order)

| # | Artifact | Status |
|---|----------|--------|
| 1 | `data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md` (104 lines) | Read full. Art. II (II.1–II.5), Art. III, Art. X P0 list, Art. XII guards, §4 G29/G30 extracted. |
| 2 | `data/council/20260825-094633-first-light/phase3_synthesis/SYNTHESIS_ARM_REPORT.md` §6 | Read full. Gate commands G1–G28 copied verbatim where cited. |
| 3 | `phase1_nodes/P1_report.md`, `P2_report.md`, `P5_report.md`; `phase2_arms/BUILD_SIDE_REPORT.md` (via decree/synthesis corroboration) | P1/P2/P5 read in full. |

## 2. Anchor verification log (grep/sed run by node1, 2026-08-25)

| Anchor claimed in mission | Verified? | Actual finding |
|---|---|---|
| Makefile ~234 contains "would go here" | ✅ | `Makefile:234` — literal `# Existing temple-grade checks would go here` inside `temple-grade:` target (target at :232). G13 (`! grep -q "would go here" Makefile`) FAILS today. |
| task_registry.py registry writer lacks mkstemp/os.replace | ✅ | `mcp_servers/omega_hub/hub_tools/task_registry.py:32-40` `_save_registry()`: `open(REGISTRY_PATH,"w")` truncate → `flock(LOCK_EX)` AFTER truncation → `json.dump` → no fsync, no tmp+rename. grep for `mkstemp\|os.replace` = zero hits. Load/save lock-split confirmed (:24-31 SH load, :36 EX save). Matches P2 F-2.1 exactly. |
| M8 regex unanchored, false-positive on ics.py ~197 | ✅ with NUANCE | Live: `rg -n 'import (segment\|...)\|from (segment\|...)' src/omega/ --type py` hits **src/omega/ics.py:197** — but the matching line is a COMMENT: `# Build header from segments (F1 fix: robust node insertion, sanitized)`. Mission described it as "`from x import segments`" — it is actually the word "from segments" inside a comment. Same defect class (unanchored + no word boundary); same fix. Anchored regex from decree G29 returns exit=1 (no match) → gate green after fix. Current gate command lives at `Makefile:295` (`check-m8-zero-telemetry`). |
| pre-commit framework not installed; hook has zero tracking refs | ✅ | `.git/hooks/pre-commit` is 7-line hand-rolled bash running ONLY `scripts/validate_soul.py` over soul.yaml. No "pre-commit" invocation, no tracking references. `.pre-commit-config.yaml:137` declares `omega-tracking-state`. G7 fails today. Only hooks present: pre-commit, commit-msg. |
| lilith proposed_lessons.yaml L374+ YAML failure (live LSP evidence) | ⚠️ NUANCED — REAL DEFECT, DIFFERENT CLASS | **LSP diagnostics re-confirmed live during my session** (errors at 374:1+ "Unexpected seq-item-ind"). But `.venv/bin/python3 yaml.safe_load` returns exit=0 (type=list, 381 lines, mtime 12:00:50 -0300 today). Manual structural inspection of L374-380 reveals the actual defect: the final proposal record is **SPLIT ACROSS TWO SEQ ITEMS** — item A carries `{id, tier, category}` ("lilith-20260825-n6-del1-vetting"), item B carries `{narrative, insight, principle, tags}` with NO id. PyYAML accepts it; the record is semantically corrupt (orphaned half-record; the vetting entry has no content body). TWO parser verdicts disagree = live specimen of C-B6 "validator green ≠ truthfulness". Consequence for spec: WI-2 must pair the G8 parseability loop with a MINIMAL SCHEMA check (every proposals[] entry requires id+narrative+insight+principle), which catches split-record corruption that bare safe_load misses. Art. IX repair status: pillar_p1 + john_carmack now parse clean; lilith parses but remains schema-corrupt → repair still OPEN for MaKaLi Stage-6 (out of my scope; flagged). |
| ACTIVE_SPRINT blockers[] illegal status (P2 F-2.3) | ✅ re-verified live | `ACTIVE_SPRINT.json .blockers.BLOCKER-B.status = "resolved"` (+ `resolved_at`) — not in Tier-0 set {backlog,ready,in_progress,blocked,completed,superseded}. Validator `validate_active_sprint()` (validate_tracking_state.py:148-206) scans only workstreams[].status and subtasks[].status — blockers never scanned. Confirmed by reading code. |
| Staleness day-truncation boundary (G16 class) | ✅ | validate_tracking_state.py:237-238: `age_days = (now - ts).days` then `age_days > STALENESS_DAYS` (STALENESS_DAYS=7 at :43). Day-granularity truncation lets 7.x-day zombies pass until they hit 8d wall-clock. Hours-resolution fix required per Art. III. |
| Future-dated timestamps uncaught | ✅ structurally | `_parse_ts()` helper exists at :46 (shared, tz-aware, Z-tolerant) — good extension point. Inverted-clock check exists (warn-only, post-:245 "G5-2 drift item 2"). NO future-date check exists anywhere. G15 currently fails against any future-dated entry; validator green throughout Council 1's X-6 arc proves it. |
| make sovereignty refs (Art. II.3 adjacent) | ✅ | No `sovereignty:` target in Makefile; ≥5 references in `.opencode/skills/{meditate-research-pipeline,autonomous-meditation-pipeline}/SKILL.md`. Out of my 5-item scope proper; noted in spec §4 as adjacent evidence for the stamps item (G12 territory, flagged for Council 2 planner). |

## 3. Design decisions recorded

- **Validator extension shape**: all new ERROR-class checks go into `scripts/validate_tracking_state.py` reusing `_parse_ts()` (its own docstring forbids duplicating parsing logic). New functions: `check_future_timestamps()`, hours-resolution staleness rewrite inside `validate_task_registry()`, `check_blocker_statuses()`, `check_wake_state()`.
- **Atomicity fix pattern**: copy the repo's own proven pattern from `scripts/sweep_task_registry.py:93-103` / `generate_session_registry.py:145-154` (mkstemp → write → chmod 0644 → os.replace) + fsync before replace (T10/M12). Lock must wrap the whole read-modify-write cycle (fixes load/save split).
- **Stamps**: machine-derived generator script (`scripts/generate_enforcement_stamps.py`) reading Makefile targets + `.git/hooks/pre-commit` + `.pre-commit-config.yaml` → emits stamp table; SOVEREIGN_MANDATES.md gets a GENERATED block (single hand-edit to insert the include-marker, thereafter derived). Pairwise binding enforced as review rule + CI grep.
- **M8 fix**: adopt decree G29 anchored regex verbatim in Makefile:295.
- **Effort totals**: 16h across 5 items (2+6+3+4+1).

## 4. Deviations / flags for maat

1. **lilith YAML anchor stale** (see §2) — spec wording adjusted: parseability check framed as regression guard, not first-repair.
2. **ics.py:197 nuance** — false positive is on a comment line ("Build header from segments"), not an import statement as mission phrased. Fix identical; noted in spec evidence so nobody chases a phantom import.
3. Bright line held: only two new files written (this notes file + the spec). Zero production-tree edits. No agents spawned.

## 5. Gate commands lifted verbatim (for spec citations)

From SYNTHESIS_ARM_REPORT §6: G6 (:213-214), G7 (:216-219), G13 (:240-241), G15 (:247-254), G16 (:256-262).
From SOVEREIGN_DECREE §4 additions: G29 (:81-82), G30 (:83-84).
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_c2_speca | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

