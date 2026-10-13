# Release & PyPI Mechanics (Cline, 2026-10-13)

**Internal-only rules. Do NOT cherry-pick to the public repo.**

## GitHub tag: `v1.6.0-alpha` is PERMANENTLY POISONED

- Publishing an immutable release writes a `release_immutable_tags` row that **permanently reserves the tag name — it follows the name across repo re-creation, and survives deleting the release AND the tag. Archiving does NOT clear it.** Only GitHub Support can.
- Evidence: probe tag `vprobe-delete-me` pushed fine to the fresh repo while `v1.6.0-alpha` was rejected (GH013 "creations being restricted") on push, refs API, and releases API — after the retired repo's release+tag were already deleted.
- **The release shipped as `v1.6.0a0`** (same SHA `355cbf1a`). Never reference `v1.6.0-alpha` as a GitHub ref again. Human-facing brand strings may still say "v1.6.0-alpha" where they're not links.
- **Never auto-delete a published release/tag**: cleanup-after-failure on an immutable release permanently reserves the name (community case: "unrecoverable without GitHub Support").

## The cut ships `release.yml` — stray tag pushes create bot releases

- `.github/workflows/release.yml` runs on tag push and auto-publishes a GitHub Release (authored `github-actions[bot]`) with build assets. My probe tag `v1.6.0a0` created one; it had to be deleted and replaced with the real audited draft.
- **Do not push probe/experimental tags to `origin`.** Tag only when you intend a release, and prefer creating via `gh release create --draft` with `--notes-file ANNOUNCEMENT…`, then verify assets before `--draft=false`.

## PyPI: `the-omega-engine` (three-name reality)

| Layer | Name | Notes |
|---|---|---|
| Distribution (PyPI) | **`the-omega-engine`** | wheel `the_omega_engine-1.6.0a0-…` |
| Python module | `omega` | unchanged |
| Console script | `omega` | unchanged |

- Why not the others (researched): `omega` = unrelated game-theory package; `omega-engine` = **similarity-rejected** vs the `omegaengine` SDK (omegaengine.ai, v2.6.0, different author — NOT the operator's). PyPI normalizes `-`/`_`/`.`: `omega-engine` ≡ `omega_engine` ≡ `omega.engine`, all gated by the same existing project.
- **Trusted publishing mechanics**: pending publisher has **no manual publish button** — activation is the first successful OIDC run of `.github/workflows/publish.yml`. The publisher must live on the page that will OWN the project (org Publishing page if an org owns it; a personal-account publisher would land the project in the personal namespace). Repo field must be the REAL repo (`Xoe-NovAi/omega-engine`) — project name and repo name are decoupled by design (OIDC checks owner/repo/workflow/env, not string equality).
- **Current state (2026-10-13): BLOCKED on GitHub org approval.** After approval: register pending publisher on the org page (project `the-omega-engine`, repo `omega-engine`, workflow `publish.yml`, env `pypi`) → dispatch Publish workflow → verify clean-venv `pip install the-omega-engine` → THEN flip doc lines from pending to primary (M29: claim only once true).

## M29 claim-audit habit (announcement + README audits)

Before any publish: measure every claim — counts via `git ls-tree <tag>`, test tallies from recorded gates (176 passed / 4 skipped, not "180"), tag SHA via `ls-remote`, installability via live PyPI probe (`curl …/pypi/<name>/json` 404 = not published), artifact hashes via sha256. "Coming soon" lines need a ticket or they violate the doc's own no-vaporware rule.
