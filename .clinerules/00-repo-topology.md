# Repo Topology & Git Flows (Cline, 2026-10-13)

**Internal-only rules. Do NOT cherry-pick this file to the public repo.**

## Two remotes, two flows

| Remote | Repo | Contains | Push rule |
|---|---|---|---|
| `origin` | `Xoe-NovAi/omega-engine` (PUBLIC, fresh history) | cut lineage + public-safe commits ONLY | via `public/main` worktree |
| `internal` | `Xoe-NovAi/omega-engine-internal` (PRIVATE) | full tree: gnosis, federation, coordination | internal work goes here |

- **Internal work**: commit on `main`, `git push internal main`. NEVER push internal lineage to `origin` — `origin/main` is a curated lineage (cut + cherry-picks), not a mirror.
- **Public changes** (announcement/README/install.sh/src): develop on internal, cherry-pick onto the public worktree, push:
  ```bash
  cd /media/arcana-novai/omega_library/staging/public-main
  git cherry-pick <sha>   # resolve cut-tree conflicts (files may be absent on cut!)
  git push origin public/main:main
  ```
- Cut-tree cherry-pick conflicts are normal: the allowlist rewrites/removes files (README structure differs; announcement absent → `DU` conflict → take theirs).
- `internal` repo has **Actions disabled** (free-tier CI budget) — CI credit is spent on `origin` only.
- Branch protection on `origin/main`: `allow_force_pushes: false`. The documented toggle (PUT full protection body, push, PUT back with false) exists in `docs/operations/RELEASE_PR_PUBLIC_STANDARDS.md` recovery path — use only for lineage resets, restore immediately.
- Never `git add -A` (entity DBs, secrets, scratch). Stage explicit paths.
- `data/coordination/`, `data/entities/`, `data/handoff/` are INTERNAL documents — they exist on `internal` only. Makali/agents read the working clone.

## Worktrees

- Public worktree: `/media/arcana-novai/omega_library/staging/public-main` (branch `public/main`, cut `355cbf1a` as base).
- Never edit public docs in two places: pick ONE tree per file, or cherry-pick promptly. Drift was real today (README fixed separately on both trees).

## Retirement / archive mechanics (learned 2026-10-13)

- Renaming a repo leaves **redirect poisoning**: API calls and some pushes still resolve the OLD name's releases/tags. Free the name for a new repo by DELETING the retired one (`gh auth refresh -s delete_repo` needed; UI also works).
- Old repo `omega-engine-retired` (private) is fully backed up: 11 `retired/*` refs on internal + issue JSONs in `data/handoff/retired-repo-backup/`. Deletion pending operator.
