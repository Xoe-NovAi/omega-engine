<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# node2 WORKING NOTES — Council 2 Build Arm (specb)
⬡ OMEGA ⬡ MAAT/node2 ⬡ trc_c2_specb ⬡ RAW NOTES
Session: 20260825-094633-first-light-c2 | Date: 2026-08-25 | Mode: PREP-ONLY (draft spec + these notes)

## Deliverables
1. `docs/specs/team_infra/SPEC_B_P1_MECHANISM_HONESTY.md` (NEW — only production-tree file created)
2. This notes file.

## Reading order executed
SOVEREIGN_DECREE.md (full) → SYNTHESIS_ARM_REPORT.md §6+GAP-5 row → RESEARCHER_EMPIRICAL_GAPS_1_4.md → JEM_DEEP_DIVE_GAPS_5_7.md → P1/P3/P6/P10 reports → BUILD_SIDE_REPORT.md → self-verification bash pass.

## Self-verification commands run (all reproduced upstream claims)
```
ls -d .opencode/plugin                      # No such file or directory ✓
ls .opencode/plugins/                       # awareness.ts error-capture.ts silent-stall-sensor.ts test-event.js.DISABLED ✓
jq -r '.plugin[]' opencode.json             # 2 dead file:// singular-dir paths ✓
jq '.agent|to_entries[]|select(.value.instructions)|.key'   # exactly the 12 named agents ✓
sed -n '25,35p' opencode.json               # root instructions[] @ ~27 incl docs/archive/MASTER_SYNTHESIS ✓
sed -n '125,145p' mcp_servers/omega_hub/hub_tools/task_registry.py   # bug verbatim at :134-135 ✓
sed -n '95,105p' …task_registry.py          # Literal w/o 'all' at :100 ✓
sed -n '105,112p' .gitignore                # data/coordination/* at :109 ✓
grep -c strict scripts/validate_llm_docs.py # 0; argparse surface read (:201-209) — no --strict ✓
python3 yaml dump providers.yaml fallback_chain  # openrouter(5) BEFORE opencode-zen(6); google-compat dup priority 4 ✓
grep -n 'native-gguf(0)' SOVEREIGN_MANDATES.md   # :55 stale chain ✓
registration_payloads.json                  # keys canonical/tasks/gated_on; gated_on cites GAP-5 fix ✓
ls .opencode/agents/plan.md grok_cli.md     # both MISSING; grok_cli.md in archive/ ✓
```

## Mismatches / flags
- NONE factual. One calibration delta documented in spec WI-2(a): researcher rated GAP-4 migration "LOW effort, MED priority"; decree Art. VIII.4 sets HIGH urgency (data-exposure). Decree governs (fusion re-scales by impact).
- JEM cited task_registry.py:134-135; mission brief said "~line 134 region" — exact locant verified :134-135. No drift.
- LSP diagnostics observed during write are PRE-EXISTING in other files: lilith/proposed_lessons.yaml:374-377 (X-9 / Art. IX corrupt YAML) and config/omega.yaml:73 duplicate map key (P10 addendum). Independent live corroboration of decree findings; NOT touched by this node (bright line held).

## Design decisions recorded in spec (for reviewer attention)
1. WI-1 default = CORRECT paths (not drop entries) — registration list should tell truth even where discovery is redundant.
2. WI-2 makali target = makali.md (plan.md never existed); grok_cli default = delete JSON def (double-registration cleanup, P6 F-03) — flagged as owner decision with unblocking default.
3. CREDITS.md entries dropped from doom_guy/john_carmack agent defs — redundant with root instructions[] global injection (verified line 27 block).
4. G4 honesty caveat: gate will FAIL until keys provisioned/disabled; spec forbids fake-passing; `--allow-unkeyed` WARN mode specified for validator interim.
5. G5 archived-roadmap removal folded into WI-3 commit (same file, pairwise-bound).
6. WI-5 Step 3 flagged quiescence requirement due to known non-atomic writer (G6/SPEC-A territory — not duplicated).
7. Validator module name `validate_config_honesty.py` collision-checked against scripts/ inventory — clean.
8. Effort total ~16.5h across 5 WIs incl. shared validator slices; anti-big-bang: all ≤6h independent landings.

## Bright-line compliance
Zero edits to existing production files. Two new files only, exactly at mandated paths. No agents spawned. Recon reads only otherwise.
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_c2_specb | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

