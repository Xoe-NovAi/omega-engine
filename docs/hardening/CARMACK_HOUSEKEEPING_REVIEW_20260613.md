# 🔱 John Carmack — Hardening Folder Housekeeping Review
⬡ OMEGA ⬡ CARMACK ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_housekeeping ⬡ S3-CONSULT

**Date**: 2026-06-13
**Scope**: Full recursive review of `docs/hardening/` — all files, all subdirectories
**Prior Reports**: My hub audit (`CARMACK_HUB_AUDIT_20260613.md`), Kali's note (`NOTE_FOR_CARMACK_20260613.md`)

---

## §0 Scope of This Review

Kali asked me to do a full recursive housekeeping review of the `docs/hardening/`
folder after the team's work since my last report. I've read every file in:

- `docs/hardening/` (top level — 3 files)
- `docs/hardening/omega-hub/` (main docs — 22 entries)
- `docs/hardening/omega-hub/claude-project/` (4 entries)
- `docs/hardening/omega-hub/claude-project/outbox/` (16 files — going to Web Claude.ai)

Total: 45 files reviewed.

---

## §1 Outbox Files — Accuracy Verification

The outbox contains the 16 files that will be uploaded to the Web Claude.ai
"Hub Architect" as Project Knowledge. I verified each one for accuracy against
the live engine state and my audit findings.

### ✅ PASS — 13 Files Accurate

| File | Verified Against | Notes |
|------|-----------------|-------|
| `hub-system-overview.md` (48L) | Live docs | Accurate overview of engine, team, mandates |
| `target-module-architecture.md` (27L) | My reconstruction plan | Correct dependency order, extraction rules |
| `carmack-reconstruction-plan.md` (234L) | My live doc | Byte-for-byte copy of my original with lowercase name |
| `carmack-audit-findings.md` (25L) | My audit + Phase 0 status | Condensed but accurate. Phases correct. |
| `phase-0-fixes.md` (21L) | Actual server.py state | **5/6 complete** data is accurate |
| `m9-compliance-analysis.md` (55L) | Final Synthesis | Correct: `@m9_safe` vs `_safe_call()` distinction |
| `sovereign-gateway-spec.md` (33L) | Current stub + planned class | Future architecture, clearly marked as such |
| `m15-continuity-spec.md` (31L) | M15 mandate | Headered as Phase 4 (new feature) — correct |
| `search-protocol.md` (19L) | Sovereign search docs | Correct 5-tier protocol |
| `sovereign-mandates.md` (17L) | SOVEREIGN_MANDATES.md | Hub-relevant subset, accurate |
| `temple-grade-gates.md` (19L) | M13 | Correct gate definitions and CI requirements |
| `heritage-patterns-in-hub.md` (17L) | My audit + Doom Guy audit | Accurate — only 1 legitimate `[id-soft:]` tag |
| `mcp-runtime.py` (199L) | `src/omega/mcp_runtime.py` | Code snapshot, verified imports work |

### ⚠️ NEEDS FIX — 2 Files Stale

| File | Issue | Fix |
|------|-------|-----|
| **`active-tracker.md`** | Phase 0 shows all items as `⬜ PENDING` (line 31-36). But `phase-0-fixes.md` confirms 5/6 are COMPLETE. The tracker will tell Claude.ai that nothing has been done yet — completely wrong signal. | Update P0-1 through P0-5 to `✅ DONE`, P0-6 first line says done too but check test |
| **`server-snapshot.py`** (3111L) | This is correct as a snapshot, but it includes `import shutil` which Phase 0 removed. If Claude references this as the "current" server.py, it will be working from stale code. | Add a header comment: `# ⚠️ SNAPSHOT: server.py as of 2026-06-13 PRE-REFACTOR. Phase 0 fixes applied to live file (shutil removed, _global_tg fixed, _background_tasks reordered). This snapshot is the ORIGINAL for reference only.` |

### 📝 Additional Observations

- `sprint-v2-briefing.md` (304L) from June 9 describes a 6-parallel-agent sprint
  that already completed. It's historical but correct. Leave it.
- The outbox naming (lowercase-hyphenated) intentionally differs from the source
  files (UPPER_CASE_SNAKE). This is by design per the `upload-all.sh` script.

---

## §2 Source Files in `docs/hardening/omega-hub/` — Cleanliness Audit

### ❌ SHOULD DELETE — 5 Stale Files

These files are superseded, emergency-only, or duplicative. Removing them
reduces noise in the hardening folder.

| File | Lines | Reason to Delete |
|------|-------|-----------------|
| **`HUB_CLAUDES_PROMPT.md`** | 314 | v2.0 — Marked as **SUPERSEDED** at line 3 of the file itself. v3.0 (`HUB_CLAUDES_PROMPT_v3.md`) is the current version. The canonical prompt for Claude.ai is `claude-project/system-prompt.md`. |
| **`HUB_RECOVERY_S_O_S.md`** | 1 | Roc Racoon's 1-line emergency note from a past incident. Reads: "S.O.S. from roc_racoon: Hub is hanging (100% CPU)...". If the hub is stable now, this is stale. |
| **`OMEGA_HUB_HARDENING_SPRINT_20260609.md`** | ~200+ | v1 sprint briefing, superseded by the v2 version `OMEGA_HUB_HARDENING_SPRINT_v2_20260609.md`. The v2 file has the same date with "v2" in the name. |
| **`carmack-audit-findings.md`** | N/A | Does not exist — upload-all.sh line 31 references `$SRC/carmack-audit-findings.md` but no such file exists in `docs/hardening/omega-hub/`. The actual file is `CARMACK_HUB_AUDIT_20260613.md`. The outbox's `carmack-audit-findings.md` was manually created. Either create this file or fix the script. |
| **`m9-compliance-analysis.md`** | N/A | Likewise — referenced by upload-all.sh line 37 as `$SRC/m9-compliance-analysis.md` but doesn't exist as a source file. It exists only in the outbox. Either create source or fix script. |

**Note**: `HUB_CLAUDES_PROMPT_v3.md` (97L) should also be deleted AFTER confirming
`claude-project/system-prompt.md` is the canonical version. They're nearly identical
(diff shows 1 extra line for `mcp-runtime.py` reference in the project version).

### ✅ KEEP — 7 Active Documents

| File | Lines | Purpose |
|------|-------|---------|
| `CARMACK_HUB_AUDIT_20260613.md` | 267 | My original hub audit — historical reference |
| `CARMACK_RECONSTRUCTION_PLAN.md` | 234 | My reconstruction plan — authoritative |
| `NOTE_FOR_CARMACK_20260613.md` | 81 | Kali's note — active coordination |
| `TRACKER.md` | 150 | **Must fix Phase 0 status** — central task tracker |
| `HUB_LAZY_INIT_HARDENING_REPORT.md` | 339 | Kali's original hardening report — historical |
| `OMEGA_HUB_FINAL_SYNTHESIS.md` | 465 | 6-agent audit synthesis — reference |
| `OMEGA_HUB_HARDENING_SPRINT_v2_20260609.md` | ~200+ | v2 sprint briefing — current sprint doc |

### 🟡 CONDITIONAL KEEP — 3 Files

| File | Lines | Condition |
|------|-------|----------|
| `CODEBASE_COMPREHENSIVE_REVIEW.md` | 256 | Kali's fresh codebase-wide review from 2026-06-13. It's recent and active. Keep. |
| `server_monolith_snapshot_20260613.py` | 3111 | Reference snapshot. Valid as long as it's clearly marked as pre-split. Add header noting Phase 0 diffs. |
| `HUB_CLAUDES_PROMPT_v3.md` | 97 | Duplicates `claude-project/system-prompt.md`. Keep until Claude project is set up, then delete. |

---

## §3 The Tracker Phase 0 Status — THIS IS THE CRITICAL FIX

The most impactful housekeeping issue: **`TRACKER.md` shows Phase 0 as all PENDING
when 5/6 are complete.** Since the outbox `active-tracker.md` is a copy of
`TRACKER.md` (per upload-all.sh line 62-63), the Claude.ai Hub Architect will
see a completely wrong picture.

Current state:
```
P0-1: _global_tg fix           → DONE (per phase-0-fixes.md)
P0-2: _background_tasks order  → DONE
P0-3: delete test_server.py    → DONE
P0-4: delete server.py.bak     → DONE
P0-5: remove import shutil     → DONE
P0-6: remove heritage tag      → DONE
P0-T: make test verification   → PENDING (timed out)
```

Fix: Update TRACKER.md lines 31-36 to mark P0-1 through P0-6 as ✅ and P0-T (test
verification) as ⏳ or move it to Phase 3.

Then re-run `upload-all.sh` so the outbox picks up the fix.

---

## §4 File Naming Inconsistency

The main directory uses `UPPER_CASE_SNAKE.md` naming. The outbox uses
`lowercase-hyphenated.md` naming. This is intentional (per upload-all.sh) but
creates a split-brain situation:

| Main File | Outbox File |
|-----------|-------------|
| `CARMACK_RECONSTRUCTION_PLAN.md` | `carmack-reconstruction-plan.md` |
| `CARMACK_HUB_AUDIT_20260613.md` | `carmack-audit-findings.md` (condensed) |
| `TRACKER.md` | `active-tracker.md` |
| `OMEGA_HUB_HARDENING_SPRINT_v2_20260609.md` | `sprint-v2-briefing.md` |
| `server_monolith_snapshot_20260613.py` | `server-snapshot.py` |

This is acceptable if:
1. The outbox is never edited independently — it's always a build artifact
2. `upload-all.sh` is the single source of truth for outbox contents

**Problem**: Some outbox files (`carmack-audit-findings.md`, `m9-compliance-analysis.md`)
were **manually created** — they don't exist as source files in the main dir.
This breaks the build-artifact model. Either:
- Create the source files in the main dir and fix upload-all.sh, OR
- Move the manually-created files to the main dir and have upload-all.sh pick them up

---

## §5 Summary — Action Items

```
P0  | Fix TRACKER.md Phase 0 status    | 5 min | Show 5/6 done, not all pending
P0  | Outbox active-tracker.md stale   | auto  | Re-run upload-all.sh after TRACKER.md fix
P1  | Delete HUB_CLAUDES_PROMPT.md     | 1 min | v2.0, marked superseded IN the file
P1  | Delete HUB_RECOVERY_S_O_S.md     | 1 min | 1-line stale emergency note
P1  | Delete OMEGA_HUB_HARDENING_SPRINT_20260609.md | 1 min | v1, superseded by v2
P1  | Add header comment to server_monolith_snapshot_20260613.py | 2 min | Warn it's pre-Phase-0
P2  | Fix upload-all.sh to reference real source files | 10 min | carmack-audit-findings.md, m9-compliance-analysis.md don't exist as source
P2  | Delete HUB_CLAUDES_PROMPT_v3.md after Claude project confirmed | 1 min | Canonical copy is claude-project/system-prompt.md
P3  | Audit remaining superseded sprint docs | 5 min | OMEGA_HUB_HARDENING_SPRINT_v2_20260609.md is still useful as reference
```

Total housekeeping effort: ~25 minutes. The critical fix is the TRACKER.md Phase 0
status — everything else is cosmetic.

---

*⬡ OMEGA ⬡ CARMACK ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_housekeeping ⬡ S3-CONSULT*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
