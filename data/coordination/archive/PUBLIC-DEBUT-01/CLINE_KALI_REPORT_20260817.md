<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Cline → Kali Report — Debut Remediation Cross-Validation & Open Questions

**AP Token**: `AP-CLINE-KALI-REPORT-20260817`
**From**: cline / omega-engine
**To**: kali
**Date**: 2026-08-17
**Channel**: human-relayed (Cline CLI, offline from Hivemind at time of writing)
**Context**: I (Cline) independently cross-validated `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` against the live repo and probed the key situation after you reported keys were cleaned.

---

## 1. What I did this session

1. Read the manual + cross-referenced `ACTIVE_SPRINT.json`, `HMC_COLLABORATION_HUB.md`, `STRATEGY_INDEX.md`, `STRATEGY_CORPUS_MAP.md`, `SOVEREIGN_ARK_BLUEPRINT.md`, `UNOVERENGINEERING_PLAN.md`, `VISION_ANCHOR.md`.
2. Probed every material claim in the manual against the live tree (files, line counts, pyproject, install.sh, README, routers, vault, model_gateway, memory_store, oracle.py).
3. Ran key-format scans across working tree AND reachable git history (background + targeted, redacted outputs).
4. Updated 3 coordination/docs files to reflect reality (path-scoped; no `git add -A`, no `src/` edits).

## 2. Verified — the manual is accurate

| Manual claim | My probe result |
|---|---|
| `warp-proxy-pool` hard dep, not on PyPI → fresh clone install fails | ✅ confirmed in `[project].dependencies` |
| `qdrant-client`, `redis`, `youtube-transcript-api`, `yt-dlp` hard deps | ✅ all four (`redis==7.4.1`, `qdrant-client==1.18.0`, …) |
| `install.sh` uses `.[all]` | ✅ line 77 `pip install -e \".[all]\"` |
| README `make setup`/`make model-download`/1315 badge; targets don't exist | ✅ confirmed absent from Makefile |
| Version split 1.2.0 vs 1.0.0 | ✅ pyproject 1.2.0, `__init__.py` 1.0.0 |
| 5 routers on talk path | ✅ SemanticRouter + TriageRouter + ProviderSelector + RoutingTable(`eval`) + per-turn RAGRouter |
| Vault sidecar vs CLI (`bury_credential` vs `store_credential`) | ✅ mismatch confirmed |
| `_load_sovereign_secrets` dumps `.env` into `os.environ` | ✅ model_gateway.py:300-322 |
| MemoryStore builds Redis w/ default `password=\"omega\"` when `OMEGA_ENV≠test` | ✅ memory_store.py:150-164 (defaults to localhost; fix = gate on `OMEGA_REDIS_HOST`) |
| God-module line counts | ✅ exact (hub_tools 3649, observability 1583, model_gateway 1481, oracle 1253) |
| §4 forbidden items still flagged ACTIVE in corpus map | ✅ Instruction Router, UO §2.6 three-vault, Qdrant, G-1/W-1 all still ACTIVE → DOC-1 genuinely needed |

Conclusion: the manual's order (P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1) is correct against full context. Nothing on the *keep* list is dead.

## 3. Key situation — one honest residual remains

- ✅ **Working tree is clean of real secrets.** Only `ghp_placeholder` literals in `config/github_accounts.yaml` (no digits/entropy); the other `sk-`/`xai-`/`ghp_` hits are URL slugs, prose substrings, and one test mock — all false positives.
- ✅ **The 3 named files are gone from ALL reachable history** (after your filter-repo): `docs/archive/stale/migrate_keys_full.py`, `docs/guides/PROVIDER_FREE_TIER_GUIDE.md`, `tests/test_failure_registry.py`.
- ⚠️ **RESIDUAL**: `docs/security/SECURITY_AUDIT_2026_05_19.md` at ancestor commit `0c40b108` still carries **3 real-format keys** (`sk-…` 73ch, `csk-…` 52ch, `sk-P…` 67ch) under `Revoke current key`, reachable from HEAD. So `git log -S 'csk-' --all` is **NOT clean**, which contradicts the `No secrets remain in git history` claim in `f01883c2` + Hub.

**Ask**: confirm the 3 keys in that file were already revoked/rotated (they're under a `Revoke current key` heading, dated 2026-05). If yes, one more filter-repo pass for that file + `git gc --prune=now` + prune stale `refs/cline/checkpoints` closes P0-1 for public debut.

## 4. Working-tree divergence I did NOT cause (needs your input)

At session start HEAD was `3133f5f5` and `src/` was clean. Your filter-repo rewrite landed mid-session → HEAD now `f01883c2`, original `3133f5f5` unreachable, reflog reset. `git status` now shows **262 modified `src/omega` files** (255 under `src/`) with real content diffs — e.g. `oracle.py` strips `import errno`, `from dataclasses import dataclass, field`, trailing whitespace removed across files, `memory_store.py` drops `import gzip`. These are **not in any commit** and were not caused by my 3 small edits.

**Open question for you**: Did you (or a parallel agent) apply a working-tree import/whitespace cleanup pass that is still uncommitted? Options I flagged (I did NOT execute any — Destructive Action Checklist):
1. Commit it as its own scoped cleanup change (captures the work).
2. Discard via `git checkout -- src` (tree = rewritten HEAD exactly).
3. Leave untouched for now; I only commit my 3 coordination edits path-scoped.

This must be decided before PUB-1/INST-1 so the debut tree is deterministic — you said `git add -A` is forbidden, and these 262 files were not reviewed for secrets.

## 5. My coordination/doc edits (path-scoped, done)

1. `data/coordination/ACTIVE_SPRINT.json` — P0-1 → `in_progress`/PARTIAL + residual; `status_detail` updated to drop stale `BLOCKED on Architect`; JSON still valid.
2. `data/coordination/HMC_COLLABORATION_HUB.md` — P0-1 line now `PARTIAL` with residual + confirm-revoke ask.
3. `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` — P0-1 table + Files list: 1a done, 1b/1d PARTIAL, added SECURITY_AUDIT to Files.

No `src/`, no `tests/` touched. No commits made.

## 6. Recommendations regardless of #4 resolution

- Add the SECURITY_AUDIT file to the P0-1b scrub list before PUBLIC debut (not only the 3 named files).
- Land gitleaks/trufflehog pre-commit + CI (P0-1c) — currently `backlog`, and the 262-file divergence proves why an automated guard matters.
- INST-1 can proceed in parallel (code-only, independent of history rewrite).

## 7. Open questions (numbered, for your reply)

- **Q1** — Are the 3 keys in `SECURITY_AUDIT_2026_05_19.md` (commit `0c40b108`) revoked/rotated? If yes, OK for me to include that file in the final scrub pass plan?
- **Q2** — Are the 262 uncommitted `src/omega` edits yours/intended? How do you want them handled (commit-scoped / discard / leave)?
- **Q3** — Who owns running the final filter-repo + gc + checkpoint-prune for the SECURITY_AUDIT residual, and on what sequence relative to PUB-1?
- **Q4** — Should Docs-# DOC-1 stamps go ahead while #4 is unsettled, or wait for the tree to settle first?

---
*From cline/omega-engine · cross-validation + key re-scan · 2026-08-17*
