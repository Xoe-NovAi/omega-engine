---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "lessons_corpus_discovery"
document_id: "lessons-corpus-discovery-20260828"
title: "Cline — Deep Discovery: Proposed + Approved Lessons Corpus (M11 layer)"
status: "ACTIVE — reference for promotion pipeline repair"
date: "2026-08-28"
claimed_model: "glm-5.3-flash"
---

# 🔱 LESSONS CORPUS DISCOVERY — Proposed & Approved (2026-08-28)
**AP**: `AP-CLINE-LESSONS-DISCOVERY-20260828-v1.0.0` · ⬡ OMEGA ⬡ CLINE ⬡ glm-5.3-flash ⬡ cline ⬡ trc_m11_discovery

## §1 HEADLINE NUMBERS
- **~292 staged proposals** across 11 active entities vs **~24 approved** entries fleet-wide → **~7.6% approval rate**
- **Exactly ONE promotion event in engine history**: kali (20 lessons), 2026-08-24, by maat/w1-3 via promote_soul_lessons.py
- Per-entity staged: grokster 64 · kali 49 · maat 44 · doom_guy 37 · researcher 31 · lilith 28 · jem 17 · roc_racoon 10 · antigravity 7 · verity 5 · carmack 4
- Per-entity approved: kali 20 · john_carmack 4 · **everyone else: 0** (sophia approved = `[]`)
- 24/56 entities have substantive lesson files; 32 are stubs (70-byte scaffolds)

## §2 THE APPROVED CORPUS (what IS vetted)
- **kali (20, promoted 08-24)**: GitHub secret-scrub triplet (L1-L3, validated scanner + skill + guide); vault-overhaul synthesis (VaultCore caller verification, talk-path filter); context-packer/session-tracking approvals. Schema: `- level:` + status/evidence/promoted_by/promoted_at.
- **john_carmack (4, dated 2026-06-15+, richest prose)**: ctypes-CDLL-segfault = single catastrophic failure point (Phase C verdict); process isolation as structural requirement; "physics always trumps aesthetics." Schema: `- lesson:/context:/insight:/principle:` — NO status field.

## §3 FRESHEST PROPOSALS (today, 2026-08-28 — highest value)
1. **researcher** (16:48, minimax-m3:free, ses r-gpt53-cline): `utility 0.96` **"False dilemmas dissolve at the layer below"** (pyrage vs python-age → cryptography substrate; 4-0 Council); **"Prestige is not fit"** (age format chosen for reputation, 101ms→0.6ms when dropped); **"Sovereignty is honesty about state"** (vault forensics: 16/18 CLI commands broken at runtime, BlindVault returned fake data); **M23 floor/ceiling** ("no fabrication" floor, "verify before refusing" ceiling — premise disagreement ≠ M23 trigger); Cline provider taxonomy (GPT-5.3-Codex belongs in openrouter block, not cline priority-7).
2. **antigravity** (13:07): **"Plateau = truncation, linear = no truncation"** — universal probe pattern; **"Configuration is not implementation"** (8-key vault declarative, _create_google factory absent); **"An imposter report is a hypothesis"** (80% accurate triage, verify with live probes); minimum-viable-launch philosophy.
3. **carmack/ dir** (13:13): **"Find the lie by reading the executable, not the comment"** (crypto.py docstring vs :87); **"PUBLIC_ALLOWLIST.txt is the launch-leak boundary"** — ⚠️ CONTRADICTS pass-2 P0-3 (see §5).
4. **lilith** (14:28): import-graph closure for deletion safety; **split-brain discovery: scaffold writes memory/approved_lessons.yaml (entity_workspace.py:175) but hydration reads ROOT (entity_workspace.py:409)** — VERIFIED this pass; entities with memory/-only approved files hydrate ZERO lessons silently; "ImportError guards don't catch decorator TypeErrors at import time."
5. **roc_racoon** (08-27, PL-ROC-402-001..003): 402-on-free = rate cap mislabeled as balance; re-dispatch loop smell ("check the loop before checking the data"); empty search result is about the search, not the data.

## §4 STRUCTURAL FINDINGS — WHY THE PIPELINE IS STUCK
1. **Schema fragmentation (≥5 variants)**: kali `- id:`/L1_narrative; researcher `proposals:`/`- level:`/utility_score; lilith indented `- id:`/`tier:`; kali-approved status/evidence/promoted_by; john_carmack-approved lesson/context/insight. promote_soul_lessons.py validates ONE schema (omega.soul.lessons Lesson/EvidenceRef) — maat's 44 and grokster's 64 cannot promote without translation.
2. **Directory fragmentation**: Carmack identity split across `carmack/` (active proposals, today), `john_carmack/` (canonical soul + approved), `JOHN_CARMACK/` (8.5KB orphan). Proposals landing in carmack/ are invisible to `--entity john_carmack` promotion.
3. **Path split-brain (root cause)**: entity_workspace.py:175 writes memory/approved_lessons.yaml; :409 reads entity-root approved_lessons.yaml. Confirmed dual copies: kali memory/ 551B (stale) vs root 24.6KB (canonical); grokster memory/approved = 0 bytes. Silent zero-lesson hydration for affected entities.
4. **302-level mismatch**: M11 mandates distillation every session; nothing schedules promotion. Approval is a maat/w1-3 one-off, not an operating process.

## §5 CROSS-AGENT CONTRADICTION (M17 flag — do not silently resolve)
- **carmack-20260828-004**: 4 GOCSPX scripts are NOT in PUBLIC_ALLOWLIST → "post-debut hygiene, not launch-blocker."
- **Pass-2 rollup P0-3**: secret in 4 history COMMITS of release/debut + 12 disk files incl. live opencode-antigravity-auth/ + coordination docs → launch blocker until rotate+scrub.
- **Reconciliation**: Carmack is right about the TIP TREE; the blocker claim rests on (a) git HISTORY ships with the repo, (b) the allowlist gate itself currently FAILS (P0-4) so the boundary is not yet enforced, (c) non-script files (docs, plugin dir) may fall inside allowlist. Resolution requires one check: are the 12 GOCSPX disk files inside or outside the allowlist? Until then BOTH verdicts stay conditional.

## §6 RECOMMENDATIONS
1. Fix entity_workspace.py:175/:409 path split-brain (one-line convention decision) — P1, blocks trust in hydration.
2. Schema-normalize staging → single Lesson/EvidenceRef format (adapter per entity), then run promote in batch: kali 49 first (evidence map already built), then maat/grokster.
3. Merge Carmack dirs; symlink orphans; register canonical entity in registry.
4. Make promotion a standing ritual (weekly maat batch + evidence probes) — M11 closure.
5. Resolve §5 contradiction BEFORE the GO re-check (single grep decides).
6. Utility-score leaderboard: researcher's 0.96/0.94 lessons deserve fleet-wide L3 promotion priority.

*⬡ OMEGA ⬡ CLINE ⬡ AP-CLINE-LESSONS-DISCOVERY-20260828-v1.0.0 ⬡ glm-5.3-flash ⬡ trc_m11_discovery*
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: glm-5.3-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

