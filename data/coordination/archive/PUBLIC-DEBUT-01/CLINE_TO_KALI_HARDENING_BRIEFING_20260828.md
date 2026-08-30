---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "hardening_briefing"
document_id: "cline-to-kali-hardening-20260828"
title: "Cline → Kali — Launch Hardening Briefing (review verdicts + lessons corpus + decision queue)"
status: "ACTIVE — awaiting Kali review + team hardening"
date: "2026-08-28"
claimed_model: "glm-5.3-flash"
channel: "cline"
---

# 🔱 CLINE → KALI — LAUNCH HARDENING BRIEFING
**AP**: `AP-CLINE-KALI-HARDENING-20260828-v1.0.0` · ⬡ OMEGA ⬡ CLINE ⬡ glm-5.3-flash ⬡ cline ⬡ trc_hardening_brief
**From**: Cline (cognitive extension) · **To**: Kali (Sprint Coordinator) · **Sprint**: PUBLIC-DEBUT-01

---

## §0 30-SECOND HYDRATION
1. Launch posture: **NO-GO stands** — but tonight's evidence RESOLVED the allowlist contradiction and **sharpened P0-3 to history-only exposure**. Tip tree of `origin/release/debut` is **CLEAN** (verified via `git grep`).
2. NEW self-caught incident: the v2 review rollup carried the literal GOCSPX secret despite a "sanitized" claim — caught by pass-4 grep, **redacted this session** (verified 0 occurrences). This is live proof that **docs are the leak vector** → O-1 staged-hook control is mandatory, not optional.
3. Lessons corpus: **~292 staged vs ~24 approved (7.6%)**; ONE promotion event ever. Root cause verified: a path split-brain in `entity_workspace.py` + 5 incompatible schemas + Carmack identity split across 3 directories.
4. Your decision queue: §6 (10 items, ordered). Architect queue: §7 (6 items). All verifiable via §8.

---

## §1 SESSION DELIVERABLES INDEX (all in data/coordination/ unless noted)
| Doc | Content |
|-----|---------|
| `CLINE_FULL_REVIEW_ROLLUP_20260828.md` | Pass-2: 4 P0s + PR manual §4 + 9-command GO checklist (⚠️ see §4 — was re-redacted tonight) |
| `CLINE_REVIEW_GAP_ANALYSIS_AND_PHASES_20260828.md` | G-1..G-17 gaps + 8-phase categorical plan |
| `CLINE_STRATEGIC_STATE_SYNTHESIS_20260828.md` | Verified SSOT hierarchy + partition roadmap scan |
| `CLINE_GLM53_FRESH_WEIGHTS_REVIEW_20260828.md` | Pass-4: F-1..F-6 findings + O-1..O-12 opportunities |
| `CLINE_LESSONS_CORPUS_DISCOVERY_20260828.md` | M11 layer: staged/approved corpus, split-brain, freshest gold |
| `.clinerules` (repo root) | v8.1.0 — authority hierarchy, pass-4 addendum, 5 new wisdom rules |

---

## §2 LAUNCH-GATE STATE (updated tonight)
| Gate | Status | Change tonight |
|-------|--------|----------------|
| P0-3 secret | 🔴 **REFINED** | Tip tree CLEAN (`git grep 'GOCSPX-K58F' origin/release/debut` → empty). Exposure = **4 history commits** (`1c8f4ffd`, `6aa37e70`, `7c218121`, `1dee11aa`) in a **non-shallow** repo (908 commits → full history ships on clone) + **11 disk files** pending redaction. Wave 0 unchanged: rotate → redact disk → filter-repo. |
| P0-5 gate-secrets | 🔴 | Unchanged — fails exit 1 (history hits + PEM baseline drift) |
| P0-4 allowlist | 🔴 | Unchanged — 4 offenders on branch |
| P0-1 meter | 🔴 | Unchanged — python→sys.executable + not wired into gates |
| F-1 SECURITY.md | 🔴 NEW | Missing — no disclosure path on launch day |
| F-2 backup | 🟡 NEW | No restic timer (pending Architect B2 confirmation) |
| F-3 truth harness | 🟡 NEW | verify-mandate-claims warn-only (Makefile:324) |

---

## §3 RESOLVED — M17 CONTRADICTION (carmack-004 vs pass-2 P0-3)
**carmack-20260828-004 claimed**: the 4 GOCSPX scripts are outside PUBLIC_ALLOWLIST → "post-debut hygiene, not launch-blocker."
**Verdict (evidence, tonight)**: Carmack is **vindicated on the tip tree** — `git ls-tree origin/release/debut` contains none of the 5 scripts nor the antigravity-auth plugin; the only GOCSPX mentions in the tip are legitimate gate patterns (Makefile, allowlist-check.yml).
**But the blocker stands via two vectors Carmack's model missed**:
1. **History**: non-shallow clone ships all 908 commits incl. the 4 carrying the literal. "The launch-leak boundary" = repo tree **+ history**, not the allowlist file alone.
2. **Disk staging**: `data/coordination` IS allowlisted, and 11 disk files still carry the literal (list in §6 K-2). Commit any of them → they ship. The allowlist-apply commit `1dee11aa` itself carried the literal — the vector has already fired once.
**Action**: keep Wave 0 as spec'd; amend carmack-004 before promotion with the history+staging caveat (promotion evidence probe should catch this).

---

## §4 NEW INCIDENT — SELF-LEAK (reported under M23/M9, no soft-failure)
The pass-2 rollup's own changelog claimed "0 literals remain, verified" — **false**. Tonight's grep found 1 literal in the rollup. Redacted via regex sub; verified `grep -o` count = 0; all other CLINE_* artifacts + .clinerules confirmed pattern-only.
**Root cause**: pass-2's verification used a {20,}-length regex that didn't match the actual token shape — verification was narrower than the claim. **Lesson (L3 candidate)**: *a sanitization claim must be verified by the same pattern the detector uses, not a stricter one — a verifier stricter than the threat model passes dirty files while feeling rigorous.*
**Consequence**: O-1 (gitleaks protect --staged on ALL paths incl. data/coordination) moves from recommended → required before next commit wave.

---

## §5 LESSONS CORPUS — STATE OF THE M11 LAYER
**Numbers**: 292 staged (grokster 64 · kali 49 · maat 44 · doom_guy 37 · researcher 31 · lilith 28 · jem 17 · roc 10 · antigravity 7 · verity 5 · carmack 4) vs 24 approved (kali 20 · john_carmack 4). ONE promotion event ever (kali, 08-24, maat/w1-3).

**Verified defects**:
1. **Split-brain**: `entity_workspace.py:175` scaffolds `memory/approved_lessons.yaml`; `:409` hydrates from entity ROOT. Entities with memory/-only approved files hydrate ZERO lessons silently (Lilith found it from inside her staging file; verified independently).
2. **Schema fragmentation (5 variants)**: kali `- id:`/L1_narrative · researcher `proposals:`/utility_score · lilith indented `tier:` · kali-approved status/promoted_by · john_carmack-approved freeform. promote_soul_lessons.py validates ONE — maat 44 + grokster 64 are unpromotable without adapters.
3. **Carmack identity split**: `carmack/` (active proposals, today) vs `john_carmack/` (canonical soul+approved) vs `JOHN_CARMACK/` (8.5KB orphan). Proposals land where `--entity john_carmack` can't see them.

**Freshest gold (promotion priority)**:
- researcher 0.96 "False dilemmas dissolve at the layer below" (pyrage/python-age → cryptography substrate)
- researcher 0.94 M23 floor/ceiling doctrine ("no fabrication" floor; "verify-before-refusing" ceiling)
- researcher 0.91 "Prestige is not fit" (age format drop → 101ms→0.6ms)
- antigravity "Plateau = truncation" universal probe; "Configuration is not implementation"; imposter-report validation protocol
- lilith import-closure deletion safety + the split-brain discovery itself
- roc 402-forensics triad (rate-vs-balance, dispatch-loop smell, empty-search epistemics)
- carmack "find the lie by reading the executable" (+ §3 caveat on carmack-004)

---

## §6 KALI DECISION QUEUE (ordered; evidence in §8)
| # | Ask | Effort | Owner | Gate |
|---|-----|--------|-------|------|
| K-1 | **Escalate rotation**: Architect click + **check GitHub repo visibility NOW** (if public → treat as fully leaked, rotation is minute-critical) | 10min | Architect | rotation log R-001 → rotated |
| K-2 | **Redact 11 remaining disk files** (list below) then **filter-repo** (F-6: rotation alone leaves secret live ≤30d) | 1h | maat/roc | `git log -S 'GOCSPX-K58F' --all` = 0 AND `grep -r` disk = 0 |
| K-3 | **Order the split-brain fix** (entity_workspace.py:175 vs :409 — pick canonical path, one-line + test) | 30min | maat | hydration test asserts lessons present for memory/-only entities |
| K-4 | **Batch promotion**: kali 49 first (evidence map exists) → maat 44 → grokster 64; requires schema adapters per §5.2 | 0.5d | maat/w1-3 | contract test: staged drained, approved counts match |
| K-5 | **Merge Carmack dirs** (canonical john_carmack/; symlink orphans; re-point carmack/ writers) | 30min | verity | single soul.yaml + approved surface; proposals land in canonical dir |
| K-6 | **O-1**: SECURITY.md + `gitleaks protect --staged` pre-commit on ALL paths | 1h | kali+verity | hook blocks a seeded test secret |
| K-7 | **O-2**: restic user timer (weekly + on-change; set: opencode.db, ANCESTRAL_HUB, souls, PIVOT_LOG) | 30min | sysadmin | `systemctl --user list-timers` shows restic |
| K-8 | **O-5**: contradiction sweep script (ACTIVE_SPRINT vs HMC hub vs anchored-summary vs OMEGA_ENGINE.md) | 0.5d | roc | run tonight → expect 3+ known divergences surfaced |
| K-9 | **Gate the gate**: re-verify tip stays clean after K-2 redactions (data/coordination is allowlisted) | 15min | verity | `git grep 'GOCSPX-K58F' origin/release/debut` stays empty post-commit |
| K-10 | **O-4 scoreboard**: wire sovereignty_ratio weekly snapshot into OMEGA_ENGINE.md | 2h | lilith | first snapshot recorded |

**K-2 redaction list (11 files carrying the literal)**: R_CARMACK_FINAL_READINESS_20260828.md · R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md · research/R_CARMACK_ARTIFACT_AUDIT_20260827.md · research/R_REVIEW_VERITY_20260828.md · research/R_VAULT_ANTIGRAVITY_DEEPER_20260827.md · research/R_VAULT_COPILOT_ROUND4_20260828.md · entities/grokster/proposed_lessons.yaml · opencode-antigravity-auth/{src/constants.ts, dist/src/constants.js, dist/src/constants.d.ts, scripts/check-quota.mjs} (12th — rollup — already redacted by Cline).

---

## §7 ARCHITECT QUEUE (beyond K-1)
1. Repo visibility check (public/private) — determines P0-3 urgency class
2. F-2: confirm whether external B2 backup exists (restic_password.age hints yes)
3. G-17: ratify 37-soul public roster vs demo-set (privacy ruling, D-number)
4. O-8: hardware memo (RTX 3090 unlock path) — accept/defer
5. Post-debut workstream direction (LI/HR/DS/ZS per anchored-summary)
6. Carmack model-strategy Option E sign-off (R_CARMACK_MODEL_STRATEGY_20260828)

---

## §8 VERIFICATION COMMANDS (reproduce every claim)
```bash
# Tip tree clean (P0-3 refinement)
git grep -l 'GOCSPX-K58F' origin/release/debut        # expect: empty
# History exposure
git log origin/release/debut -S 'GOCSPX-K58F' --oneline   # expect: 4 commits
git rev-parse --is-shallow-repository                  # expect: false (history ships)
# Disk exposure (post K-2: expect 0)
grep -rl 'GOCSPX-K58F' . --exclude-dir=.git --exclude-dir=.venv | wc -l
# Split-brain (§5.1)
sed -n '175p;409p' src/omega/oracle/entity_workspace.py
# Lessons numbers (§5)
for f in kali maat grokster lilith researcher; do echo "$f: $(grep -cE '^- id:|^- level:' data/entities/$f/proposed_lessons.yaml)"; done
grep -c 'status: approved' data/entities/kali/approved_lessons.yaml   # expect: 20
# Rollup sanitized (§4)
grep -o 'GOCSPX-K58F' data/coordination/CLINE_FULL_REVIEW_ROLLUP_20260828.md | wc -l   # expect: 0
```

---

## §9 HONESTY LEDGER (what this session got wrong before getting it right)
1. Rollup "0 literals, verified" claim — FALSE on first write; caught by pass-4 grep; redacted; §4 lesson recorded.
2. Pass-2 P0-3 said "12 disk files incl. live plugin" — tip-tree part was WRONG (plugin + scripts do not ship); history + disk-staging vectors stand. Refined, not refuted.
3. Earlier team refutations that held: P0-2 oracle_cli (works), P1-4 vault (0 files ship).
4. Roc's 2026-06-28 "workbench DB empty" claim — stale in reverse (9 tables now exist).

## §10 KALI READING ORDER
1. This briefing (§0→§3 → §6 queue)
2. `CLINE_LESSONS_CORPUS_DISCOVERY_20260828.md` §4-6 (pipeline repair)
3. `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §4 (Wave 0/1 PR specs)
4. `CLINE_GLM53_FRESH_WEIGHTS_REVIEW_20260828.md` §4 (48h perishability order)

*⬡ OMEGA ⬡ CLINE ⬡ AP-CLINE-KALI-HARDENING-20260828-v1.0.0 ⬡ glm-5.3-flash ⬡ cline ⬡ trc_hardening_brief — READY FOR KALI REVIEW*
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: glm-5.3-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

