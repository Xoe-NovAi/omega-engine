# Host & Data Conventions (Cline, 2026-10-13)

## Mounts, not homes

- Model/data mounts live at **`/media/<user>/omega_library/…`**, NOT `~/omega_library`. Code defaults must match the mount (env override still wins). Two live bugs came from `Path.home() / "omega_library"` defaults — fixed in `src/omega/memory/embeddings.py`; keep new defaults mount-correct and regression-checked.
- Disks: `/` (root, 109G — target ≥20% free), `/tmp` is **tmpfs 7.3G total** (an 8 GB gate on `/tmp` can NEVER pass — redirect scratch to `/media/arcana-novai/omega_library/staging/`, which has 37G+).
- Big staging roots in use: `…/staging/install-timing-20261013/`, `…/staging/public-main/` (worktree), `…/staging/pypi-verify-*`.

## install.sh invariants (scripts/install.sh — measured 2026-10-13)

- Cold install: **202s** (target <300s). Was 615s before fixes — regressions show up as timing, so re-time after touching it. Logs: `…/staging/install-timing-20261013/`.
- `MODELS_DIR="${OMEGA_MODELS_DIR:-/media/arcana-novai/omega_library/models/gguf}"` — it was used-but-unset (instant `set -u` death). Never introduce a use-before-default.
- `CMAKE_BUILD_PARALLEL_LEVEL` default **6**, exported **before** the aria2c pre-fetch block (build ordering trap). 16 jobs thrashed this hybrid-CPU box to ~13 GiB RSS.
- aria2c is MANDATORY for >1MB downloads (M23, `.opencode/rules/07-sovereign-fetch.md`): model + llama-cpp sdist pre-fetch into `.vendor/` (gitignored). Fallback chain: aria2c → hf → curl-with-warning.
- Talk probe MUST force `OMEGA_PROVIDER=mock` — bare `omega talk` probes real backends and hangs 60s to turn-layer timeout. (MockProvider's "setup mode" text IS the mock response — that's by design, not a failure.)

## opencode.db (the 26.6 GB lesson)

- **Never `cp`/`rsync`/`dd` it.** `VACUUM INTO` only. (`cp` OOM-killed OpenCode twice and produced a torn file.)
- Never run blob aggregates (`SUM(LENGTH(data))`, `GROUP BY` on data columns) — materializes the 20 GB `event.data`.
- Never delete `event_sequence` (parent of `event`; cascades events away).
- Reclaim executed 2026-10-13: 26.61 → 6.56 GB, 114,021 duplicated `message.updated.1` removed, counts asserted unchanged. Script `scripts/opencode_db_reclaim.sh` (hardened — read its exit-code table). Rollback: `/media/arcana-novai/8TB/opencode_backups/opencode.db.rollback-20261013014834`.

## Giant-file serialization (the OOM root cause)

**One giant-file reader/writer at a time on Node 0 (14 GiB).** The OOM that killed a CLI session came from `integrity_check` + `sha256sum` + reclaim all streaming 27 GB files concurrently while root was at 99%. Check `ps` for `sqlite3 … integrity|foreign_key`, `sha256sum`, `VACUUM`, `mv` across GB-size files before launching another. Use `ionice -c 3` for background bulk I/O.

## Disk gates

- Before any download/clone/venv: `df -h / /tmp <target>` and require real headroom (≥8 GB on `/` for reclaim-class ops; `/tmp` counts only what tmpfs can hold).
- Root was recovered 99% → 73% by the reclaim + rollback relocation; keep it there — pre-reclaim, every install gate failed on disk.

## Search & research

- Sovereign pipeline (`sovereign_search`) tiers returned empty today — per M23 escalate: local FTS → web_search → fetch docs directly. For GitHub/PyPI behavior questions, fetch the canonical docs page + a real-world issue/PR as evidence, then verify empirically with a probe (push a throwaway tag, hit `/pypi/<name>/json`) — probes beat speculation.
