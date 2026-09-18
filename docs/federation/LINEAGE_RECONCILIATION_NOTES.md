# Lineage Reconciliation Notes — `node1/all-5-mcp-green` vs `main`

**Date**: 2026-09-18 · **Status**: DECIDED 2026-09-18 — Option A (wait for Node 0).
Branch stays pushed as reviewable lineage; no merge until the Node 0 window.

## Facts

- Local lineage: 88 commits (Node 1 harness session work). Remote `main`: 1085 commits
  (sovereign-runtime lineage). `git merge-base --all` (full history both sides): **empty —
  no common ancestor**. GitHub refuses PR creation ("no history in common").
- Branch `node1/all-5-mcp-green` is pushed (591 KB payload, full-history secret scan clean).
- Trial `git merge --allow-unrelated-histories --no-commit origin/main` (aborted after
  mapping): **9 conflicted files + 5,765 staged additions** from their side, including
  `src/omega/` (278 files), `data/entities/` (1,737 files), `data/handoff/`,
  `data/coordination/`, `docs/strategy/`, `config/wads/`.

## The 9 conflicts (all add/add — same paths, independent content)

| File | Ours (node1) | Theirs (main) | Suggested resolution if merging |
|---|---|---|---|
| `.gitignore` | full harness ignore (+`logs/thermal/`) | small (TBD) | union; keep our `data/` quarantine |
| `.opencode/opencode.json` | npm `opencode-antigravity-auth@latest` (portable) | `file:///home/arcana-novai/...` absolute path (Node 0 machine leak) | keep ours; their path is machine-specific |
| `AGENTS.md` | Node 1 harness landing (HARDWARE/pin-trap) | Sovereign-runtime landing (src/omega, mandates) | **different scopes sharing a filename — needs human call; do not auto-pick** |
| `CONTRIBUTING.md` | harness contributing | sovereign contributing | same scope problem as AGENTS.md |
| `LICENSE` | **MIT** (Xoe-NovAi/Omega Engine Alpha 2026) | **Apache-2.0** | legal decision — human only |
| `Makefile` | harness targets (bench/lint/test/gnosis) | sovereign targets | scope-dependent; likely union with namespacing |
| `README.md` | honest-alpha harness README | sovereign README | scope-dependent |
| `docs/ROADMAP.md` | P0–P3 harness roadmap (+P3.4) | (their roadmap — unexamined) | compare + unify or split |
| `scripts/validate_model_cards.py` | OMER M1 Pydantic validator (lint-wired) | theirs (unexamined) | diff + keep superset |

## Flags (do not merge blindly)

1. **License change MIT→Apache**: legal, human-only.
2. **`data/` tracked upstream** (entities/handoff/coordination) while our `.gitignore`
   quarantines `data/` as unversioned — merging stages live databases into git.
   `data/entities/` (1,737 files) must be scanned for secrets/PII before any merge.
3. **AGENTS.md/CONTRIBUTING.md are different projects' landings**, not two versions of
   one file. A tree merge produces a franken-repo unless scopes are deliberately unified.
4. **Stale repo URLs in docs**: README badge + GETTING_STARTED point at
   `xnai/omega-engine-alpha` (404); FIRST_RUN points at `xnai/omega-engine` (404);
   real repo is `Xoe-NovAi/omega-engine`. Fix when docs are next touched.

## Options

- **A (recommended)**: leave lineages separate; reconcile in the Node 0 window
  (they own `main`'s lineage). This branch stays reviewable as-is.
- **B**: merge `--allow-unrelated-histories` with per-file calls above; requires
  human rulings on license + AGENTS.md scope + `data/` policy first.
- **C**: split — harness moves to its own repo (or subdirectory), sovereign keeps `main`.
