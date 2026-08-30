---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

name: "git-secret-scrub"
description: "GitHub/Git history secret detection and scrubbing — full workflow for finding key-format strings in ALL git history (not just working tree), classifying false positives, and removing them with filter-repo. Use when facing secret leaks, repo debut prep, or history audits."
---

# 🔱 Git Secret Scrub Skill (v1.0)

Codified 2026-08-17 from PUBLIC-DEBUT-01 P0-1 (omega-engine secret scrub).
This skill replaces the learning curve: **read this before touching any repo
that may contain secrets in history.**

## When to Use

- A secret (API key, token, credential) may exist in git history
- Preparing a repo for public debut / open-sourcing
- Post-incident audit ("was the key ever committed?")
- Verifying a scrub actually worked

## The Three-Layer Truth (Memorize)

| Layer | Command | What it sees |
|-------|---------|--------------|
| **Working tree** | `git grep -E 'pattern'` | Only checked-out files — **NOT history** |
| **History blobs** | `scripts/git-secret-scan.sh` | Every reachable blob in every ref |
| **Reachability** | `git rev-list --all --objects` | What `git log` can still show |

**Rule**: `git grep` clean ≠ history clean. Always scan history blobs.

## Decision Gate: Rotate vs Scrub

| Situation | Action |
|-----------|--------|
| **Public repo** (or may become public) | **ROTATE FIRST** (revoke key at provider), then scrub. Rotation is the only true fix — scrubbing only removes the copy. |
| **Private repo, never shared** | Scrub without rotation is acceptable (documented decision). |
| **Key already exposed externally** (CI logs, npm, forum) | **ROTATE. ALWAYS.** Scrub is cosmetic. |

## Workflow (10 Steps)

### 1. Detect in working tree
```bash
git grep -nE 'sk-[a-zA-Z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|ghp_[a-zA-Z0-9]{30,}|xai-[a-zA-Z0-9]{20,}'
```

### 2. Detect in ALL history (the real scan)
```bash
scripts/git-secret-scan.sh
```
Output: `<blob-sha> <path>` — machine-parseable, deduplicated.

### 3. Classify every match — DO NOT treat all as secrets
| Class | Example | Action |
|-------|---------|--------|
| **REAL KEY** | `sk-or-v1-9f8a...` (40+ chars, entropy) | Scrub/rotate |
| **PROSE** | "sk-questions-on-the-forum" | False positive — leave |
| **PLACEHOLDER** | "sk-dev-master-key-change-me" | False positive — leave |
| **TEST MOCK** | "sk-or-v1-test-key-1234567890" | False positive — leave |
| **DOCUMENTATION** | docs ABOUT the scrub itself | Expected — leave |

### 4. Find siblings & archives (the missed-file trap)
- `grep -rl "migrate_keys" .` — the scrub target had a **sibling** (`migrate_keys_full.py` vs `migrate_keys.py`) that was missed on first pass
- Check **archive paths**: `SECURITY_AUDIT_2026_05_19.md` existed at BOTH `docs/security/` AND `docs/archive/stale/security/`
- `git log --all --oneline -- <path>` to see every commit touching a file

### 5. Scrub with filter-repo
```bash
# Remove entire files from ALL history:
git filter-repo --path <file1> --path <file2> --invert-paths --force

# Redact a key embedded in a valuable doc (keeps the doc, blanks the key):
git filter-repo --replace-text <(echo 'sk-or-v1-9f8a...==>REDACTED') --force
```

### 6. GC — filter-repo does NOT remove objects
```bash
git gc --prune=now
# Run TWICE: once after filter-repo, once after checkpoint pruning
```

### 7. Prune stale refs (checkpoints carry history!)
```bash
# refs/cline/checkpoints/* and similar tool refs survive filter-repo and
# keep old commits reachable. Prune them (all were >24h old in P0-1):
git for-each-ref 'refs/cline/checkpoints/*' --format='%(refname) %(creatordate:iso8601)'
# delete stale ones:
git update-ref -d refs/cline/checkpoints/<name>
```

### 8. Force-push ALL branches
```bash
git push origin --all --force
git push origin --tags --force   # if tags exist
```

### 9. Verify — the final scan is the truth
```bash
scripts/git-secret-scan.sh
git log --all -p | grep -E 'sk-or-v1-'   # second verification layer
```
**Acceptance**: remaining matches are ONLY prose/placeholder/test-mock/documentation.

### 10. Document
- Record scrub scope, decisions (rotate vs scrub), and remaining false positives in the coordination report
- **Note**: new docs ABOUT the scrub will themselves match key patterns — classify as DOCUMENTATION

## Pitfalls (All Hit in P0-1)

1. **`grep -q` + `pipefail` + large blob = silent drop** — grep -q exits on first match, upstream writer gets SIGPIPE, pipefail reports 141, `if` evaluates false. Use `grep -E >/dev/null` instead.
2. **`${VAR:-default}` with braces in default** — bash parameter expansion ends at the FIRST `}`. Define the default separately: `DEFAULT='sk-...{20,}'; VAR="${VAR:-$DEFAULT}"`.
3. **bash `case` doesn't re-parse `|` from variables** — `case "$x" in $PATTERNS)` treats `|` literally. Write patterns literally in the case.
4. **Checkpoint refs survive filter-repo** — prune them or old commits stay reachable.
5. **filter-repo ≠ gc** — objects persist until `git gc --prune=now`.
6. **Sibling files** — always search for similar names (`migrate_keys*`, `*SECURITY_AUDIT*`).
7. **Never `git add -A`** — path-stage every commit (M27).
8. **Docs about the scrub self-match** — classify, don't panic.

## Scripts

- `scripts/git-secret-scan.sh` — history blob scanner (read-only, idempotent, machine-parseable output)

## Related

- `docs/strategy/GITHUB_FORENSICS_SCRIPTING_GUIDE.md` — how to write helpful scripts for complex git work
- `data/coordination/KALI_CLINE_SYNC_REPORT_20260817.md` — P0-1 execution record