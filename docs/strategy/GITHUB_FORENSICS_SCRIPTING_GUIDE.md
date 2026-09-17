# 🔱 GitHub Forensics Scripting Guide
**AP Token**: `AP-GITHUB-FORENSICS-SCRIPTING-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_github_forensics ⬡ 2026-08-17

**Purpose**: Codify how to write *helpful* scripts for complex GitHub/git work —
so agents don't re-derive the learning curve each time. Born from PUBLIC-DEBUT-01
P0-1 (secret scrub) where the first scan script silently missed 2 of 9 matches.

---

## §1 The Core Principle

> **A helpful script is one that fails loudly, verifies itself, and lives in the repo.**

Three failures in P0-1, all silent:
1. `grep -q` + `pipefail` + large blob → **dropped 2 matches, no error**
2. `${VAR:-default}` with `}` in the default → **corrupted regex, no error**
3. bash `case` with `|` from a variable → **filtered everything, no error**

None of these produced an error message. The only reason they were caught:
**the script was validated against known-positive samples.**

## §2 The 10 Rules

### 1. Live in `scripts/`, never `/tmp`
`/tmp` is ephemeral. The first scan script lived in `/tmp/opencode/` and was one
reboot from loss. Repo scripts accumulate wisdom; /tmp scripts evaporate it.

### 2. Validate against known-positive samples (MANDATORY)
Before trusting a scan script, run it against data you KNOW matches:
```bash
# P0-1 example: a tracked file with a known prose match
git cat-file -p HEAD:.firecrawl/claude_projects_instructions.json | grep -c 'sk-'
scripts/git-secret-scan.sh | grep -c 'claude_projects_instructions'  # must be ≥1
```
If the script misses a known match, the script is broken — not the data.

### 3. Be non-destructive by default
Read-only by default. Destructive operations (filter-repo, gc, push --force)
are separate steps, never hidden inside a scan script.

### 4. Machine-parseable output
`<sha> <path>` per line. One record per line, no prose interleaved (prose goes
to stderr). Pipes to `sort -u -k2` for dedup.

### 5. Scan ALL refs, not just branches
`git rev-list --all --objects` — not `git log HEAD`. Tool checkpoints
(`refs/cline/checkpoints/*`) carry history that branches don't.

### 6. Filter for speed, but verify the filter
Skip binary/large paths (png, db, min.js...) — but a filter bug silently
skips everything. The known-positive validation (Rule 2) catches this.

### 7. Avoid silent-failure constructs
| Construct | Failure mode | Fix |
|-----------|-------------|-----|
| `grep -q` in pipefail pipeline | SIGPIPE → 141 → false | `grep -E >/dev/null` |
| `${VAR:-...{20,}...}` | expansion ends at first `}` | separate `DEFAULT=` var |
| `case "$x" in $VAR)` | `|` treated literally | literal patterns in case |
| `set -e` without pipefail | pipeline status masked | `set -euo pipefail` + Rule 7 |
| `|| true` swallowing | hides real errors | log the error, then continue |

### 8. Document the WHY in the header
Every script carries: why it exists, lessons encoded, usage, output format.
The header IS the knowledge transfer — future agents read it instead of
re-deriving.

### 9. Idempotent and re-runnable
Safe to run twice. The final verification scan is the truth — re-run after
every destructive step (filter-repo → gc → prune → push).

### 10. Verify after action, not just before
After scrubbing: re-scan. After gc: re-scan. After push: re-scan. The last
scan is the acceptance criterion, not the first.

## §3 The P0-1 Case Study (What Actually Happened)

| Step | Command | Lesson |
|------|---------|--------|
| Working tree scan | `git grep -E 'sk-...'` | Only sees checked-out files |
| History scan v1 | `/tmp/opencode/find_key_blobs.sh` | Worked, but lived in /tmp |
| History scan v2 | `scripts/git-secret-scan.sh` | **Silently dropped 2/9 matches** (grep -q SIGPIPE) |
| Validation | known-positive grep | **Caught the drop** — script fixed |
| Scrub | `git filter-repo --path X --invert-paths --force` | Removes files from ALL history |
| Redact | `git filter-repo --replace-text` | Blanks key, keeps doc |
| GC | `git gc --prune=now` ×2 | filter-repo ≠ gc |
| Prune | `git update-ref -d refs/cline/checkpoints/*` | Checkpoints survive filter-repo |
| Push | `git push origin --all --force` | All branches, not just main |
| Verify | `scripts/git-secret-scan.sh` | 9 matches, ALL classified false-positive/documentation |

**Time saved by codification**: next agent skips the 3 silent-failure bugs, the
sibling-file trap, the archive-path trap, and the checkpoint trap.

## §4 When NOT to Write a Script

- One-off, never-repeated action → do it inline, document the command
- The action is destructive and interactive → prefer documented manual steps
- A tool already exists (`git filter-repo`, `gitleaks`, `trufflehog`) → use it,
  script only the glue

## §5 Related

- `.opencode/skills/git-secret-scrub/SKILL.md` — the full scrub procedure
- `scripts/git-secret-scan.sh` — the validated scanner
- `data/coordination/KALI_CLINE_SYNC_REPORT_20260817.md` — P0-1 execution record

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-17 ⬡ PUBLIC-DEBUT-01 ⬡ P0-1 codification*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
