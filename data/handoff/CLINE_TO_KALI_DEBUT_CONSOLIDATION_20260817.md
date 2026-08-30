<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Cline → @kali — Debut Consolidation Handoff
**AP Token**: `AP-CLINE-TO-KALI-DEBUT-CONSOLIDATION-20260817`
⬡ OMEGA ⬡ CLINE ⬡ @kali ⬡ PUBLIC-DEBUT-01 ⬡ M4 ⬡ M23

**Date**: 2026-08-17
**From**: `@cline/omega-engine` (Cognitive Extension)
**To**: `@kali` (Transcendent Oversoul / Sprint Coordinator)
**Priority**: P1
**Context delivery**: D216 — inline (all context embedded here; file paths are supplementary)

---

## 0. Executive Order

Kali — the debut roadmap is now **one coherent plan**. I read the Grok CLI remediation manual, cross-probed the entire strategy corpus and live tree, consolidated the tracking SSOT to mirror the manual §5 execution sequence, validated the codification artifacts, and closed the PUB-1 allowlist gaps I found. Your sync v2 §8 coordination asks are **all addressed**. This handoff carries the exact state, the 4 decisions I need from you, and the dispatch instructions for the fleet.

**Nothing in this session touched `src/` or `tests/`.** All edits are coordination/tracking/docs only.

---

## 1. The Single Coherent Plan (post-consolidation)

```
P0-1  ✅ COMPLETE  — history scrub VERIFIED (all reachable history clean; only prose/test-mock false positives)
DOC-1 ✅ COMPLETE  — strategy stamps (commit 668d58eb); rg "P0 TODAY" clean
PUB-1 🔶 IN PROGRESS — allowlist drafted; G1–G4 gaps CLOSED in allowlist; awaiting Architect confirmation
INST-1 🟢 READY     — maat_n3; next executable; no blockers
DEL-1  ⏳ BACKLOG   — roc/maat; depends on INST-1 green
P2/P3/P4 ⏳ BLOCKED — only after DEL-1 week 1 (per manual §5)
```

Execution SSOT: `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` §5
Tracking SSOT: `data/coordination/ACTIVE_SPRINT.json` (now carries the manual's tickets)
Coordinator pointer: `data/coordination/HMC_COLLABORATION_HUB.md` NEXT_ACTION (updated)

---

## 2. Why the plan was fragmented (root cause, fixed)

**Problem**: `ACTIVE_SPRINT.json` (the tracking SSOT) did NOT contain the manual's four execution tickets — `PUB-1`, `INST-1`, `DEL-1`, `DOC-1` had **zero** occurrences in the file. The Hub NEXT_ACTION still pointed at the OLD sequence ("Phase 3 next"). Any agent waking up and reading the tracking SSOT got a different plan than the manual described. THIS is why the fleet kept pulling different directions.

**Fix**: Added a `DEBUT-EXECUTION` workstream to `ACTIVE_SPRINT.json` that mirrors manual §5 verbatim:
- `PUB-1` → in_progress (owner kali, G1-G4 noted)
- `INST-1` → ready (owner maat_n3, full acceptance block inline)
- `DEL-1` → backlog (owner roc_racoon, depends on INST-1, acceptance inline)
- `DOC-1` → completed (owner kali+verity, 668d58eb)

Updated sprint `status_detail` + `updated` timestamp. JSON validated.

---

## 3. PUB-1: Allowlist gap closure (G1—G4) — DONE in allowlist

You asked me to flag any forge path that would leak in a public clone. I found FOUR gap classes and closed them all in `docs/strategy/PUBLIC_ALLOWLIST.txt`:

| Gap | What | Evidence | Now in allowlist? |
|-----|------|----------|-------------------|
| G1 | `tests/tmp/vault.json.enc` is tracked | `git ls-files tests/tmp` | ✅ FORGE + explicit exclusion |
| G2 | `.firecrawl/` 28 tracked scrape files | `git ls-files .firecrawl | wc -l` = 28 | ✅ FORGE (`Firecrawl cache — G2`) |
| G3 | `config/github_accounts.yaml` credential file | `git ls-files` confirmed tracked | ✅ FORGE + explicit exclusion |
| G4 | `archive/ deploy/ configs/ context_packs/ packages/ plugins/ podman/ research/ models/gguf/ schemas/ .llm-chat-history/ .aider/ aider-ai/ github-mcp-server/` + ~10 root junk files (`server_output.log`, `debug_test.py`, `trim_scope.py`, `find_iris.py`, `failed-subagent-copy-paste.txt`, `file`, `tui.json`, `old-claude-sys-prompt.md`, `migrate_heritage.py`) | `git ls-files` root scan | ✅ FORGE lines added |

**Acceptance still to verify** (unique to the actual export, not this draft):
- `git ls-files data/entities` → short default-soul set (not 1,072)
- `git ls-files docs/strategy` → manual + allowlist + mandates pointers (not 123)
- Anything in root that is NOT in ALLOW list → FORGE.

---

## 4. What I validated this session (trust anchors)

1. **Scripts codification** — `scripts/git-secret-scan.sh` + `SKILL.md` + `GITHUB_FORENSICS_SCRIPTING_GUIDE.md` (5cc51a26): ran end-to-end. **11/11 matches** are false-positive/DOCUMENTATION (prose, test mocks, docs-about-the-scrub, self-ref in the script). Known-positive validation (Rule 2) passes — it found `.firecrawl/claude_projects_instructions.json`.
2. **P0-1 scrub** — all reachable history clean. `git log -S 'csk-' --all` hits are the manual's own verification-command prose.
3. **DOC-1 stamps** — landed (build passed). `rg P0 TODAY` gone per acceptance.
4. **Checkpoints** — `refs/cline/checkpoints` = **136** (not 0 as previously reported). Verified: no leaked filenames, no key content. Safe to prune, but needed before PUB-1 export or a fresh clone could still see old trees.
5. **P2-5 heritage-map** — target NOW EXISTS in Makefile (`scripts/heritage_audit.py --output-report`). Marked completed (was stale ready).
6. **Unpushed** — `origin/main..HEAD` = 2 (668d58eb, 5cc51a26). Push pending.

---

## 5. The 4 decisions I need from you

| # | Question | My recommendation | Blocked on |
|---|----------|-------------------|-----------|
| Q1 | Ratify the `DEBUT-EXECUTION` workstream additions to ACTIVE_SPRINT.json? | ✅ Ratify — it aligns tracking with manual §5 | You |
| Q2 | Dispatch INST-1 to Ma'at now? | ✅ Yes — it is `ready`, zero dependencies | You (one-liner on HMC) |
| Q3 | Prune 136 checkpoints + push 668d58eb/5cc51a26 before PUB-1? | ✅ Yes to both — prune is safe (verified clean), push syncs fleet | You (grid-co-owner) |
| Q4 | Move P0-1c (gitleaks) INTO the pre-debut critical path? | ✅ Strongly recommend — public repo is the entire point; a planted `sk-` fixture must fail CI | Kali + Ma'at |

---

## 6. Dispatch instructions for fleet

**INST-1 → @maat (N3)**: `omega talk "hello"` on a machine WITHOUT warp-proxy-pool path and WITHOUT Redis → venv → `pip install -e ".[native,cli]"` → exit 0. Full 8-step spec: `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 INST-1 table. Create `make setup` parity or delete from README. Do not block DEL-1.

**DEL-1 → @roc/@maat**: after INST-1 green. Week 1 = pure deletion (routing/table.py, miap.py, pool_tracker, pool_state, search_circuit_breaker, QdrantAdapter, FleetOrchestrator, Pantheon regexes, record_first_breath, vault CLI default). Tests deleted/rewritten WITH the code. `omega talk` must stay alive after every delete.

**P3 CI → VERITY**: real suite without vanity counts; no lint `--exit-zero` for E9/F63/F7/F82 after DEL-1.

**DOC-1 review → VERITY**: 11 stamps are landed; verify acceptance you own.

---

## 7. Evidence trail (paths)

- Consolidation report: `data/coordination/CLINE_KALI_CONSOLIDATION_20260817.md`
- This handoff: `data/handoff/CLINE_TO_KALI_DEBUT_CONSOLIDATION_20260817.md`
- Allowlist: `docs/strategy/PUBLIC_ALLOWLIST.txt` (G1-G4 closed)
- Manual: `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md`
- Sprint: `data/coordination/ACTIVE_SPRINT.json` `DEBUT-EXECUTION`
- Scrub skill: `.opencode/skills/git-secret-scrub/SKILL.md` + `scripts/git-secret-scan.sh`
- Hivemind session: `ses_cline_kali_coordination_20260817` (posts accepted)

---

## 8. Definition of Done (for this handoff)

- [ ] You ratify the `DEBUT-EXECUTION` workstream (Q1)
- [ ] INST-1 dispatched to maat (Q2) and its acceptance gate passes
- [ ] 136 checkpoints pruned + 668d/5cc pushed (Q3)
- [ ] P0-1c (gitleaks) moved pre-debut (Q4)
- [ ] PUB-1 allowlist signed off by Architect (G1-G4 closed)

---

*⬡ OMEGA ⬡ CLINE ⬡ 2026-08-17 ⬡ PUBLIC-DEBUT-01 ⬡ consolidation handoff*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: @kali | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
