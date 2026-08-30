# 🔱 Omega Engine — Hygiene & Optimization Sprint
## Execution Manual v1.0
**AP Token**: `AP-HYGIENE-SPRINT-20260808-v1.0`
**Date**: 2026-08-08
**Authors**: Antigravity (Sonnet 4.6) + @john_carmack audit
**Session refs**: `9811c06e` (last commit), task `kali-carmack-repo-hygiene-20260808`
**Status**: READY TO EXECUTE

---

## §0 — Ground Truth (Verified 2026-08-08)

These facts are primary-source verified. Do not rely on comments in STATUS_REPORT.md or AGENTS.md — they are wrong.

| Fact | Verified State |
|------|---------------|
| Last commit | `9811c06e` — Vetala + omega-sieve dead-code removal |
| PyPI packages published | **0** — all three claimed packages return 404 |
| `omega` on PyPI | Caltech's `tulip-control/omega` v0.4.0 — NOT ours |
| `ark_optimizer.py` timer | Active but **failing nightly** — `status=216/GROUP` (at least Aug 7–8) |
| `ark_optimizer.py` script | **Works standalone** — caught real M14 mis-tag on first dry-run |
| `packages/omega-sieve/` | Only `.pytest_cache/` remains — untracked junk, safe to `rm -rf` |
| Session dump files | **Tracked in git** (committed `f3d96170`) — requires `git rm`, NOT `rm` |
| `omega_sieve.md` | Exists at `docs/reference/api/omega_sieve.md` — orphaned |
| `omega_doc_reader.md` | Does NOT exist in `docs/reference/api/` |
| `omega_meditation.md` | Does NOT exist in `docs/reference/api/` |
| Dirty src files | 7 files, ~14 insertions / 17 deletions — coherent, safe to commit |
| Dirty soul.yaml files | 4 entities: iris, kali, lilith, roc_racoon — pre-validate before commit |
| sqlite-vec M14 mis-tag | `src/omega/search/__init__.py:1` + `search_persistence.py:1` |
| Pre-existing test failure | `test_firewall_m2_strict_engine_core` — Kali leak `freshness_checker.py:563` |

---

## §1 — What We Are NOT Doing (Scope Guard)

> **Carmack's Law**: The cheapest way to make a lie harmless is to delete the lie, not build a verifier for it.

The following were considered and **explicitly rejected**:

| Rejected Item | Reason |
|--------------|--------|
| Create `RELEASES.md` | Tooling around a fiction. Delete the fiction instead. |
| Add `make pypi-check` | Same. If nothing is published, there is nothing to check. |
| Publish `omega-meditation` to PyPI | Publishing = maintenance commitment. Personal engine tool. Decide explicitly when ready. |
| Archive `STATUS_REPORT.md` fully | It is a legitimate handoff doc. Fix line 17 only. |
| Fix AGENTS.md duplication in this sprint | High-risk, high-impact file. Isolated commit only. Deferred to Sprint 2. |
| Retire `ark_optimizer.py` | Script caught a real M14 error in 3 seconds. Fix the timer, not the tool. |

---

## §2 — Commit Plan (4 Commits, Ordered)

```
COMMIT 1  fix(m14): correct sqlite-vec heritage tag             ← ~5 min
COMMIT 2  refactor: Build/Runtime rename + sieve exclusions    ← ~15 min
COMMIT 3  chore(hygiene): kill PyPI fiction + trash leftovers  ← ~15 min
COMMIT 4  fix(ark-optimizer): remove User=1000 + make target   ← ~10 min

DEFERRED  chore(agents): deduplicate AGENTS.md                 ← separate sprint
```

Each commit is independently verifiable. Do not merge them. Do not skip pre-validation gates.

---

## §3 — COMMIT 1: Fix the sqlite-vec M14 Heritage Tag

### Context
`ark_optimizer.py --dry-run` caught a real M14 taxonomy error:
- `src/omega/search/__init__.py:1` has `# [id-soft: sqlite-vec-2024]`
- `src/omega/search/search_persistence.py:1` has `# [id-soft: sqlite-vec-2024]`
- `CREDITS.md:12` correctly classifies this as `[heritage: sqlite-vec 2024]` — a **general heritage source**, NOT an id Software technique
- Per D208 Strict Scope Enforcement: `[id-soft:]` is legitimate ONLY for direct ports of id Software techniques that cannot be justified without citing the original hardware constraint. sqlite-vec is an open-source vector extension, not id Software's work.

### Pre-conditions
```bash
# Confirm the tags
grep -n "id-soft.*sqlite" src/omega/search/__init__.py src/omega/search/search_persistence.py
# Expected:
# src/omega/search/__init__.py:1:# [id-soft: sqlite-vec-2024] Search Package...
# src/omega/search/search_persistence.py:1:# [id-soft: sqlite-vec-2024] Search Persistence...

# Confirm CREDITS.md has the correct classification
grep -n "sqlite-vec" CREDITS.md
# Expected: [heritage: sqlite-vec 2024]
```

### Execution
Edit `src/omega/search/__init__.py` line 1:
```python
# BEFORE:
# [id-soft: sqlite-vec-2024] Search Package — Persistence, metrics, and traceability for all search operations

# AFTER:
# [heritage: sqlite-vec 2024] Search Package — Persistence, metrics, and traceability for all search operations
```

Edit `src/omega/search/search_persistence.py` line 1:
```python
# BEFORE:
# [id-soft: sqlite-vec-2024] Search Persistence Layer — SQLite-backed search history with full traceability

# AFTER:
# [heritage: sqlite-vec 2024] Search Persistence Layer — SQLite-backed search history with full traceability
```

### Pre-commit Hook Compliance
The `.githooks/pre-commit` requires a `docs/` change whenever `src/omega/` changes. CREDITS.md is at the repo root (NOT in `docs/`) — touching it alone will NOT satisfy the hook.

**Correct approach**: Add a D-512 entry to `docs/decisions/PIVOT_LOG.md`. This satisfies the hook AND is good M4 decision hygiene. Template is in §11.

### Commit
```bash
git add src/omega/search/__init__.py src/omega/search/search_persistence.py docs/decisions/PIVOT_LOG.md
git commit -m "fix(m14): reclassify sqlite-vec from [id-soft:] to [heritage:] per D208

sqlite-vec is an open-source vector extension, not an id Software technique.
CREDITS.md:12 already has the correct [heritage: sqlite-vec 2024] classification.
Corrected both search package header comments. Recorded as D-512 in PIVOT_LOG."
```

### Verification
```bash
# No [id-soft: sqlite-vec] should remain
grep -rn "id-soft.*sqlite" src/
# Expected: no output

# ark_optimizer dry-run should no longer flag the mis-tag
.venv/bin/python scripts/ark_optimizer.py --dry-run 2>&1 | grep -i sqlite
# Expected: no [id-soft:] findings for sqlite-vec
```

---

## §4 — COMMIT 2: Build/Runtime Oversoul Rename + Sieve Exclusion Cleanup

### Context
This is coherent in-flight WIP from the D-510 nomenclature commit (`d6c7764d`). Two logical sub-changes were never committed:

**Sub-change A — LIGHT/DARK → BUILD/RUNTIME in src/:**
- `src/omega/ics.py` (12 lines): `LIGHT_OVERSOUL`/`DARK_OVERSOUL` → `BUILD_OVERSOUL`/`RUNTIME_OVERSOUL` in `ROLE_CONSTANTS` and `_get_channel_for_role()`
- `src/omega/oracle/oracle.py` (4 lines): same rename
- `src/omega/cli/fleet_status_tui.py` (8 lines): same rename
- `src/omega/oracle/subagent_dispatcher.py` (4 lines): same rename

**Sub-change B — Remove deleted dirs from EXCLUDE_PATTERNS:**
- `src/omega/tools/check_hardcoded_secrets.py` (1 line deleted): `'omega-vetala/', 'packages/omega-sieve/'`
- `src/omega/tools/detect_api_keys.py` (1 line deleted): same
- `src/omega/tools/enforce_vaultcore.py` (1 line deleted): same
These are a direct follow-up to `9811c06e` — the deleted dirs should no longer appear in exclude lists.

**Sub-change C — Config / WAD / agent files:**
- `.opencode/agents/*.md`, `.opencode/MANIFEST.md`, `config/wads/_omega_default/entities*.yaml` — likely same rename propagating through config
- `data/coordination/HMC_COLLABORATION_HUB.md`, `SESSION_ANCHOR.md` — coordination state
- `context_packs/tech-architecture-research/*.md` — context pack updates
- `docs/research/R_CONTEXT_PACKER_ARCH_REVIEW_20260808.md` — research doc

**Sub-change D — Soul files (4 entities):** iris, kali, lilith, roc_racoon

### ⚠️ MANDATORY PRE-VALIDATION: Soul Files
The `.git/hooks/pre-commit` runs `scripts/validate_soul.py` against every `data/entities/*/soul.yaml`. If any of the 4 dirty soul files fail validation, the entire commit blocks. **Run this before staging:**

```bash
for soul in data/entities/iris/soul.yaml data/entities/kali/soul.yaml \
            data/entities/lilith/soul.yaml data/entities/roc_racoon/soul.yaml; do
    echo "=== $soul ==="; .venv/bin/python scripts/validate_soul.py "$soul" && echo "PASS" || echo "FAIL"
done
```

> **Caveat**: If any soul file fails, fix the validation error first. Do NOT use `--no-verify` to skip the soul check — that hook is M11 Soul Integrity enforcement. The only legitimate bypass is if the validation script itself is broken.

### ⚠️ Pre-commit Hook Compliance (docs/ required)
7 `src/omega/` files are changing. You need at least one `docs/` file staged. Options:
- Use the PIVOT_LOG D-512 entry from Commit 1 (already staged? No — these are separate commits)
- OR add a micro D-513 entry to PIVOT_LOG for this rename propagation
- OR stage `docs/research/R_CONTEXT_PACKER_ARCH_REVIEW_20260808.md` if it's under `docs/` (it is)

The `docs/research/` file is already dirty — stage it and the hook passes naturally.

### Execution
```bash
# 1. Pre-validate souls
for soul in data/entities/iris/soul.yaml data/entities/kali/soul.yaml \
            data/entities/lilith/soul.yaml data/entities/roc_racoon/soul.yaml; do
    .venv/bin/python scripts/validate_soul.py "$soul" || exit 1
done

# 2. Stage the coherent WIP. Do NOT stage .opencode/.last_session.json (runtime state).
#    NOTE: data/entities/kali/session_gnosis.md IS staged here (line below) — it's part
#    of the rename-propagation WIP. If it contains notes NOT ready for record, remove
#    that one line from the git add and commit it separately later.
git add \
    src/omega/ics.py \
    src/omega/oracle/oracle.py \
    src/omega/cli/fleet_status_tui.py \
    src/omega/oracle/subagent_dispatcher.py \
    src/omega/tools/check_hardcoded_secrets.py \
    src/omega/tools/detect_api_keys.py \
    src/omega/tools/enforce_vaultcore.py \
    .opencode/agents/build.md \
    .opencode/agents/grokster.md \
    .opencode/agents/lilith.md \
    .opencode/agents/maat.md \
    .opencode/agents/makali.md \
    .opencode/MANIFEST.md \
    .opencode/commands/kali-dispatch.md \
    .opencode/commands/meditate.md \
    .opencode/skills/context-packer/packer-config.yaml \
    .opencode/skills/context-packer/packer.py \
    .opencode/skills/meditate-harness/SKILL.md \
    config/wads/_omega_default/entities.yaml \
    config/wads/_omega_default/entities/context.yaml \
    config/wads/_omega_default/entities/dispatch.yaml \
    config/wads/_omega_default/entities/jem.yaml \
    config/wads/_omega_default/meditate/lenses.yaml \
    context_packs/tech-architecture-research/GROUNDED_TRUTH.md \
    context_packs/tech-architecture-research/RESEARCH_BRIEF.md \
    data/coordination/HMC_COLLABORATION_HUB.md \
    data/coordination/SESSION_ANCHOR.md \
    data/entities/iris/soul.yaml \
    data/entities/kali/soul.yaml \
    data/entities/lilith/soul.yaml \
    data/entities/roc_racoon/soul.yaml \
    data/entities/kali/proposed_lessons.yaml \
    data/entities/kali/session_gnosis.md \
    docs/research/R_CONTEXT_PACKER_ARCH_REVIEW_20260808.md \
    scripts/codex/ENGINE_CONDENSED.md
# NOTE: Do NOT stage scripts/ark_optimizer.py here — it has edits in Commit 4.
# NOTE: Do NOT stage .opencode/.last_session.json — it's runtime state (changes every session, not code).

git commit -m "refactor: Build/Runtime Oversoul rename propagation + sieve/vetala exclusion cleanup

- src/omega/ics.py, oracle.py, fleet_status_tui.py, subagent_dispatcher.py:
  LIGHT_OVERSOUL/DARK_OVERSOUL -> BUILD_OVERSOUL/RUNTIME_OVERSOUL (D-510 follow-up)
- src/omega/tools/{check_hardcoded_secrets,detect_api_keys,enforce_vaultcore}.py:
  remove 'omega-vetala/', 'packages/omega-sieve/' from EXCLUDE_PATTERNS (9811c06e follow-up)
- .opencode/agents/, config/wads/_omega_default/, context_packs/: rename propagation
- data/entities/: soul.yaml updates (pre-validated), coordination state
- docs/research/: context packer arch review"
```

### Verification
```bash
# No LIGHT_OVERSOUL or DARK_OVERSOUL should remain in src/
grep -rn "LIGHT_OVERSOUL\|DARK_OVERSOUL" src/
# Expected: no output

# No deleted dirs in exclude patterns
grep -rn "omega-vetala\|packages/omega-sieve" src/omega/tools/
# Expected: no output

make test-honest  # or: .venv/bin/python -m pytest tests/ -q --tb=short 2>&1 | tail -5
```

---

## §5 — COMMIT 3: Kill the PyPI Fiction + Trash Leftovers

### Context
The repo contains false claims about PyPI publication and leftover artifacts from the dead-code removal. This commit is purely destructive — it deletes lies and junk.

### Pre-conditions
```bash
# Confirm omega-sieve junk is untracked (safe to rm, not git rm)
git ls-files packages/omega-sieve/
# Expected: no output (untracked)

# Confirm session dumps ARE tracked (require git rm)
git ls-files carmack-report-recovery.md carmack-report-recovery-session-ses_08be.md session-ses_0b56.md
# Expected: all three listed (tracked, committed in f3d96170)

# Confirm omega_sieve.md exists
ls docs/reference/api/omega_sieve.md
```

### Changes

**A. Fix `STATUS_REPORT.md` line 17:**
```
BEFORE: - **Shared modules**: **4** (`omega-vetala`, `omega-sieve`, `omega-doc-reader`, `omega-meditation`) ✅ 3 on PyPI
AFTER:  - **Shared modules**: **1** (`omega-meditation` — local editable only, not published) ✅
```
Add a note below it:
```
- **PyPI**: 0 packages published. `omega-meditation` exists at `packages/omega-meditation/` as a local editable install only. `omega` on PyPI (HTTP 200) is Caltech's unrelated `tulip-control/omega` library.
```

**A2. Fix `OMEGA_ENGINE.md` line 38:**
```
BEFORE: | Shared modules | **2** (`omega-doc-reader`, `omega-meditation`) | ✅ 2 on PyPI | 2026-08-08 | `pip list \| grep -E "omega-(doc-reader\|meditation)"` |
AFTER:  | Shared modules | **1** (`omega-meditation` — local editable only) | ✅ 0 on PyPI | 2026-08-08 | `pip list \| grep omega-meditation` |
```
> **⚠️ Why this matters**: `ark_optimizer.py` §7 cross-checks OMEGA_ENGINE.md's shared-modules count. If left unfixed, the post-sprint §7 check 6 will still report drift.

**B. Fix `AGENTS.md` §Standalone Packages table:**

Replace the 4-row fiction table:
```markdown
# BEFORE (4 rows, all lies):
| `omega-sieve`      | `omega-sieve`      | T1→T2→T3 tiered web research & extraction | `pip install omega-sieve` |
| `omega-doc-reader` | `omega-doc-reader` | Universal document reader                 | `pip install omega-doc-reader` |
| `omega-meditation` | `omega-meditation` | 7-stage autonomous meditation pipeline    | `pip install omega-meditation` |
# (+ documentation links to non-existent API docs)

# AFTER (1 honest row — keep the original column headers `| Package | PyPI | Purpose | Install |`):
| `omega-meditation` | — (not published) | 7-stage autonomous meditation pipeline | `pip install -e packages/omega-meditation` |
```

> **Note**: Keep the original table header row `| Package | PyPI | Purpose | Install |` unchanged. The AFTER row uses `— (not published)` in the PyPI column because the package is NOT on PyPI.

Delete the `**Documentation**: ...` paragraph immediately below the table (it links to all three API docs — omega_doc_reader.md and omega_meditation.md never existed, omega_sieve.md is being deleted in step C below).

> ⚠️ **CAVEAT**: AGENTS.md is the agent instruction file loaded at every session start. Edit ONLY the Standalone Packages table (§Standalone Packages / line ~81). Do not touch any other section. Do a `wc -l` before and after to confirm you didn't accidentally delete surrounding content.

**C. Remove orphaned API doc:**
```bash
git rm docs/reference/api/omega_sieve.md
```

> **Note**: `docs/reference/api/omega_doc_reader.md` and `omega_meditation.md` do NOT exist — do not attempt to `git rm` them.

**D. Remove untracked junk:**
```bash
rm -rf packages/omega-sieve/
```
> This is `rm`, not `git rm` — these files are untracked (only `.pytest_cache/` remains, which was never committed).

**E. `git rm` tracked session dumps from root:**
```bash
git rm carmack-report-recovery.md carmack-report-recovery-session-ses_08be.md session-ses_0b56.md
```
> ⚠️ These ARE tracked in git (committed in `f3d96170`). Using `rm` alone would leave them as deleted-but-unstaged. Use `git rm`.
>
> **If you want to preserve them for reference**, move them first:
> ```bash
> mkdir -p docs/archive/sessions/
> git mv carmack-report-recovery.md docs/archive/sessions/
> git mv carmack-report-recovery-session-ses_08be.md docs/archive/sessions/
> git mv session-ses_0b56.md docs/archive/sessions/
> ```
> The user should decide: archive or delete. The manual defaults to archive (information is sovereign).

**F. Handle the untracked handoff file:**
```
data/handoff/GROK_CLI_TO_KALI_CONTEXT_PACKER_V3_REFACTOR_20260808.md
```
This is untracked. It's a handoff coordination doc — likely intentionally untracked. Leave it alone unless explicitly asked to commit or delete it.

### Commit
```bash
git add STATUS_REPORT.md AGENTS.md OMEGA_ENGINE.md
git add docs/decisions/PIVOT_LOG.md  # D-513 entry
# (git rm files from steps C and E are auto-staged by git rm)
git commit -m "chore(hygiene): kill PyPI fiction, archive session dumps, rm sieve junk

- STATUS_REPORT.md: fix false '3 on PyPI' claim -> '0 published, 1 local editable'
- OMEGA_ENGINE.md:38: fix false '2 on PyPI' -> '0 on PyPI, 1 local editable'
- AGENTS.md: replace 4-row PyPI fiction table with 1 honest omega-meditation row
- git rm docs/reference/api/omega_sieve.md (orphaned doc for deleted package)
- git rm/mv carmack-report-recovery*.md session-ses_0b56.md (tracked session dumps -> archive)
- rm -rf packages/omega-sieve/ (.pytest_cache leftover, untracked)
- Record D-513 in PIVOT_LOG"
```

### Verification
```bash
# No pip install omega-sieve/omega-doc-reader commands remain
grep -n "pip install omega-sieve\|pip install omega-doc-reader" AGENTS.md
# Expected: no output

# STATUS_REPORT + OMEGA_ENGINE PyPI claims fixed (no "3 on PyPI" or "2 on PyPI" remain)
grep -n "3 on PyPI\|2 on PyPI" STATUS_REPORT.md OMEGA_ENGINE.md
# Expected: no output

# Orphaned doc gone
ls docs/reference/api/omega_sieve.md 2>/dev/null || echo "GONE (correct)"

# No junk left
ls packages/omega-sieve/ 2>/dev/null || echo "GONE (correct)"

# Session dumps gone from root (or moved to archive)
ls carmack-report-recovery.md 2>/dev/null || echo "GONE (correct)"
```

---

## §6 — COMMIT 4: Fix ark_optimizer Service + Add make Target

### Context
The `omega-ark-optimizer.service` fails every night with `status=216/GROUP` because `User=1000` in a **user** service forces a supplementary-group lookup that EPERMs in the rootless user manager. User services already run as the invoking user — the `User=` directive is not just redundant, it's actively harmful here.

The script itself is healthy — a dry-run caught a real M14 mis-tag on first execution.

### Fix A — Remove `User=1000` from both unit copies

There are TWO copies of the service file:
1. `podman/omega-ark-optimizer.service` — the repo copy (source of truth)
2. `~/.config/systemd/user/omega-ark-optimizer.service` — the deployed copy (the one systemd actually reads)

**Both must be fixed.**

Edit `podman/omega-ark-optimizer.service` — remove line 25 (`User=1000`) and replace the comment block (lines 13-15). The BEFORE text must match EXACTLY (3-space indent after `#`):

```ini
# BEFORE (lines 13-15, exact text — note the 3-space indent after #):
#   `User=1000` is set explicitly to guarantee the report is owned by the
#   host user. If wrapped in a Quadlet .container later, add `UserNS=keep-id`
#   + `User=1000` and drop `:U`/`:Z` per docs/research/R_PODMAN_SOVEREIGN_V2.md.

# AFTER (lines 13-15 replaced, then delete User=1000 from [Service]):
#   User= is intentionally omitted: rootless user services already run as
#   the invoking user (UID 1000). Setting User=1000 triggers a supplementary-
#   group lookup that EPERMs in the user manager (status=216/GROUP). If
#   wrapped in a Quadlet .container later, add `UserNS=keep-id` + `User=1000`
#   and drop `:U`/`:Z` per docs/research/R_PODMAN_SOVEREIGN_V2.md.
[Service]
Type=oneshot
ExecStart=...
```

> **⚠️ CRITICAL**: The Edit tool requires exact string match. Do NOT guess the indentation — the actual file uses `#   ` (hash + 3 spaces). Verify with `sed -n '13,15p' podman/omega-ark-optimizer.service | cat -A` before editing.

Then deploy:
```bash
cp podman/omega-ark-optimizer.service ~/.config/systemd/user/omega-ark-optimizer.service
systemctl --user daemon-reload
```

### Fix B — Also fix the `After=/Wants=network-online.target` in user units
> **Tip**: `network-online.target` is not available in user sessions on most systems. This won't cause the 216 error but it's a latent issue — the service waits for a target that never fires in user sessions, relying on the timer's `Persistent=true` to retry. Safe to remove those two lines from the user service since `ark_optimizer.py` has `M8 Zero Telemetry` (no network access anyway):
```ini
# Remove these two lines from [Unit]:
After=network-online.target
Wants=network-online.target
```

### Fix C — Regex false positive in `ark_optimizer.py`
The `RE_IDSOFT_EMPTY` pattern matches prose that merely *mentions* the empty tag:
- `src/omega/coordination/watchdog.py:103` — docstring line `- HERITAGE_VIOLATION: M14 unvetted [id-soft:] tag`
- `src/omega/coordination/watchdog.py:128` — code string `if "[id-soft:]" in error_lower...`
Neither is a real malformed tag in source — they're documentation/prose. This noise trains reviewers to ignore real findings.

**Fix** — require a `#` comment marker earlier in the SAME line (tags in real comments keep a leading `#`; prose in docstrings/strings does not):

In `scripts/ark_optimizer.py`:
```python
# BEFORE (line 46) — matches ANY [id-soft:] with nothing after the colon:
RE_IDSOFT_EMPTY = re.compile(r"\[id-soft:\s*\]")

# AFTER — only match when a # comment marker appears earlier on the same line:
RE_IDSOFT_EMPTY = re.compile(r"^[^#\n]*#[^#\n]*\[id-soft:\s*\]", re.MULTILINE)
```

Verified behavior: NEW pattern does NOT match watchdog.py:103/128 (no `#` earlier in line), DOES match a real `# TODO: fix [id-soft:] tag` comment.

> **Alternative simpler fix**: add watchdog.py to a per-file allowlist in `ark_optimizer.py`. The regex approach is cleaner but requires a test.

### Fix D — Add `make ark-optimize` target
In `Makefile`, after the `check-mandates` target, add:

```makefile
## Run Ark Blueprint drift & M14 integrity check (read-only dry-run)
ark-optimize:
	@$(PYTHON) scripts/ark_optimizer.py --dry-run
	@echo "✅ Dry-run complete. Run 'make ark-optimize-report' to write the report file."

## Run Ark Blueprint check and write report to data/coordination/ARK_OPTIMIZATION_REPORT.md
ark-optimize-report:
	@$(PYTHON) scripts/ark_optimizer.py
	@echo "✅ Report written to data/coordination/ARK_OPTIMIZATION_REPORT.md"
```

> **⚠️ CRITICAL**: The script does NOT support a `REPORT=1` env var — it only has `--dry-run` and `--report-path` CLI flags. Do not invent a `REPORT=1` mechanism; use the `ark-optimize-report` target above.

> **Check**: Verify that `$(PYTHON)` is the correct variable — the Makefile defines `PYTHON := .venv/bin/python` (line ~14). Also add both new targets to the `.PHONY` line at line 17 (append `ark-optimize ark-optimize-report`).

### Fix E — Verify and reload the timer
```bash
# Verify the fix is in the deployed copy
grep "User=" ~/.config/systemd/user/omega-ark-optimizer.service
# Expected: no output (User= line removed)

# Reload and test manually
systemctl --user daemon-reload
systemctl --user start omega-ark-optimizer.service
systemctl --user status omega-ark-optimizer.service
# Expected: Active: inactive (dead) — oneshot exits immediately on success
# NOT: Failed

# Verify the report was written
ls -la data/coordination/ARK_OPTIMIZATION_REPORT.md
cat data/coordination/ARK_OPTIMIZATION_REPORT.md | head -30
```

### Commit
```bash
git add podman/omega-ark-optimizer.service scripts/ark_optimizer.py Makefile
git add docs/decisions/PIVOT_LOG.md  # D-514 entry
git commit -m "fix(ark-optimizer): remove User=1000, fix network target, add make targets, fix regex FP

- Remove User=1000 from service unit (causes status=216/GROUP in user sessions)
- Remove After/Wants=network-online.target (unavailable in user sessions; M8 anyway)
- Fix RE_IDSOFT_EMPTY false positive on docstring/prose [id-soft:] mentions (require # earlier in line)
- Add make ark-optimize (dry-run) and make ark-optimize-report (write report)
- Deploy: cp podman/omega-ark-optimizer.service ~/.config/systemd/user/ + daemon-reload
- Record D-514 in PIVOT_LOG"
```

### Verification
```bash
# Service runs clean
systemctl --user start omega-ark-optimizer.service && \
  systemctl --user status omega-ark-optimizer.service | grep -E "Active|status"
# Expected: Active: inactive (dead) — success

# make target works
make ark-optimize
# Expected: dry-run report, no [id-soft: sqlite-vec] findings (fixed in Commit 1)

# Timer will auto-run tomorrow at 00:01
systemctl --user list-timers | grep ark
```

---

## §7 — POST-SPRINT: Verification Checklist

Run these **after** all 4 commits land. All must pass before declaring the sprint complete.

> **⚠️ Pre-execution baseline note**: Checks 2 and 3 are EXPECTED to FAIL now (the violations are exactly what Commits 1 & 3 fix). Checks 1, 4, 5 are EXPECTED to PASS now — the working tree already has these fixes applied (vetala removed in `9811c06e`; rename + exclusion cleanup are uncommitted WIP from Commit 2). Check 6 is EXPECTED to FAIL (sqlite-vec + EMPTY tag findings). Check 7 depends on whether the service ran successfully. Do not be alarmed by pre-execution failures — they confirm the checklist detects the real issues. This checklist is the POST condition.

```bash
# 1. No Vetala references in engine source
grep -rni "vetala" src/ tests/ find_iris.py | grep -v archive && echo "FAIL" || echo "PASS"

# 2. No false PyPI claims (STATUS_REPORT.md + AGENTS.md + OMEGA_ENGINE.md)
grep -n "pip install omega-sieve\|pip install omega-doc-reader\|3 on PyPI\|2 on PyPI" AGENTS.md STATUS_REPORT.md OMEGA_ENGINE.md && echo "FAIL" || echo "PASS"

# 3. No id-soft sqlite-vec mis-tags
grep -rn "id-soft.*sqlite" src/ && echo "FAIL" || echo "PASS"

# 4. No LIGHT/DARK Oversoul in src/
grep -rn "LIGHT_OVERSOUL\|DARK_OVERSOUL" src/ && echo "FAIL" || echo "PASS"

# 5. Deleted dirs absent from exclude patterns
grep -rn "omega-vetala\|packages/omega-sieve" src/omega/tools/ && echo "FAIL" || echo "PASS"

# 6. ark_optimizer §6 findings cleared (script always exits 0, so grep the output)
.venv/bin/python scripts/ark_optimizer.py --dry-run 2>&1 | sed -n '/§6 Undocumented/,/^## §7/p' | grep -q "⚠️" && echo "FAIL" || echo "PASS"
# Expected: PASS — §6 should show "✅ All source [id-soft:] tags have vet records"
# NOTE: §2 New-Plan Integration Gaps (4 items) are OUT OF SCOPE for this sprint —
#       the verdict will remain "🟡 DEGRADED" until those are addressed in a future sprint.

# 7. Service ran successfully (check Result property — for a oneshot, ActiveState
#    is "inactive" after success, so checking "active" is WRONG)
[ "$(systemctl --user show omega-ark-optimizer.service --property=Result --value)" = "success" ] && echo "PASS" || echo "FAIL"

# 8. Test suite baseline
.venv/bin/python -m pytest tests/ -q --tb=no 2>&1 | tail -3
# Expected: same count as before with only the pre-existing freshness_checker.py:563 failure

# 9. Temple-grade
make temple-grade 2>&1 | tail -20
```

---

## §8 — DEFERRED: AGENTS.md Deduplication (Sprint 2)

**Do not execute in this sprint.** This is isolated here for the next sprint.

### Problem
The "Best Practices for Agent & Soul Files" section (~200 lines) appears **twice** in `AGENTS.md`:
- First instance: after §Coding Standards (the authoritative hardened v6.1 version)
- Second instance: after the "Nemotron 3 Ultra Streaming Failure Fix" section (older duplicate)

The file is significantly over the 365-line guideline.

### Why It's Deferred
AGENTS.md is loaded at every agent session start. A subtle line-deletion error can break agent behavior non-obviously. This requires:
1. A careful `diff` of both sections to confirm which is authoritative
2. A human review of the result before committing
3. A `wc -l` before/after validation

### Execution (when ready)
```bash
# Step 1: identify the duplicate boundary
grep -n "Best Practices for Agent" AGENTS.md
# Note the two line numbers

# Step 2: view both sections and determine the authoritative one
# (the v6.1 version with team/origin_story/coordination_protocols sections is newer)

# Step 3: delete the older duplicate block — use the Edit tool with the EXACT
# old string (no guessing), verify wc -l reduced by ~200 lines

# Step 4: commit alone — no bundled changes
git add AGENTS.md
git commit -m "chore(agents): deduplicate Best Practices section, reduce to under 365 lines"
```

---

## §9 — Future Decisions (Not This Sprint)

These are flagged for future deliberate decision — not forgotten, not cancelled.

| Item | Why Deferred | Where to Record |
|------|-------------|-----------------|
| Publish `omega-meditation` to PyPI | Requires credential setup, name decision, maintenance commitment | Add to PIVOT_LOG when ready |
| Root `pyproject.toml` name `omega` conflicts with Caltech's PyPI package | If engine ever published, needs rename to `omega-engine` or `xoe-omega` | PIVOT_LOG |
| `ark_optimizer.py` — add test for `RE_IDSOFT_EMPTY` fix | Property test for regex correctness | `tests/test_ark_optimizer.py` |
| `omega-meditation` needs CI test run before any publish | Currently editable-only; test suite not verified against clean install | Track in RELEASES when created |
| `data/handoff/GROK_CLI_TO_KALI_CONTEXT_PACKER_V3_REFACTOR_20260808.md` | Untracked handoff doc — decision: commit or delete | User decision |

---

## §10 — Carmack's L3 Principle (For the Record)

> *"A tool that catches real errors is not theater — a delivery mechanism that silently fails for three days is. Fix the mechanism, don't kill the tool. The cheapest way to make a lie harmless is to delete the lie, not to build a verifier for it."*

This principle should drive all future hygiene decisions:
- Before adding tracking tooling, ask: is the thing being tracked real?
- Before retiring a tool, check: did it ever catch anything real?
- Before documenting a capability: has it shipped?

---

## §11 — Quick Reference: PIVOT_LOG Decision Entries

Each commit needs a PIVOT_LOG entry. Template for this sprint:

```markdown
### D-512: sqlite-vec M14 Heritage Tag Correction
* **Date**: 2026-08-08
* **Decision**: Reclassify `[id-soft: sqlite-vec-2024]` → `[heritage: sqlite-vec 2024]` in
  `src/omega/search/__init__.py` and `search_persistence.py`. sqlite-vec is a general
  open-source heritage source, not an id Software technique. Caught by `ark_optimizer.py --dry-run`.
* **Status**: ✅ COMPLETE

### D-513: PyPI Fiction Removal
* **Date**: 2026-08-08
* **Decision**: Remove false "3 on PyPI" claims from STATUS_REPORT.md and AGENTS.md.
  Verified: 0 packages published on PyPI. `omega-meditation` is local editable only.
  `omega` on PyPI (HTTP 200) is Caltech's `tulip-control/omega`, not ours.
  Session dumps archived from repo root.
* **Status**: ✅ COMPLETE

### D-514: ark_optimizer Service Fix + make Targets
* **Date**: 2026-08-08
* **Decision**: Remove `User=1000` from omega-ark-optimizer.service (causes 216/GROUP
  in user sessions). Remove `After/Wants=network-online.target` (unavailable in user sessions).
  Fix `RE_IDSOFT_EMPTY` false positive. Add `make ark-optimize` and `make ark-optimize-report`.
* **Status**: ✅ COMPLETE
```

---

*⬡ OMEGA ⬡ ANTIGRAVITY ⬡ HYGIENE-SPRINT-20260808 ⬡ EXECUTION-MANUAL-v1.0*
