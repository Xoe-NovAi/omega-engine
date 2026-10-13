# DEBUT-ALLOWLIST-GAP.md

**Document ID:** `DEBUT-ALLOWLIST-GAP`
**Date:** 2026-09-21
**Status:** ACTIVE
**Spec:** `docs/specs/P1_TASK_SPECIFICATION.md` §P1-4

---

## 1. The Gap

`ACCOUNT_MAP.yaml` was tracked in git despite the explicit file inclusion allowlist (`docs/strategy/PUBLIC_ALLOWLIST.txt`). The allowlist defines which files are permitted in the public debut repository; `ACCOUNT_MAP.yaml` (a credential-adjacent mapping of provider accounts) was present in the index at HEAD, violating the allowlist contract and creating a debut-track credential leak risk.

## 2. Root Cause

The debut filter validates blobs at specific commits, not directory contents. The allowlist is enforced at release time by scanning the tree at release commits — but files can be tracked (and staged) between those validation points without triggering the filter. The filter's commit-scoped validation missed the working-tree/index presence of `ACCOUNT_MAP.yaml` until the forensic review (Antigravity three-model review, 2026-09-20) flagged it.

## 3. Immediate Fix (P0-2 COMPLETE)

- `git rm --cached data/entities/antigravity/knowledge/ACCOUNT_MAP.yaml` — removed from index (file retained on disk)
- Added `.gitignore` entry to prevent re-tracking
- Created `data/entities/antigravity/knowledge/ACCOUNT_MAP.yaml.example` as the sanitized template
- Verified: `git ls-files | grep ACCOUNT_MAP` returns empty

## 4. Phase 2 Fix (DEFERRED)

Restructure the allowlist with explicit deny patterns or explicit file allows:

- **Option A**: Convert `PUBLIC_ALLOWLIST.txt` to a deny-list model — allow everything except explicit patterns (e.g., `data/entities/*/knowledge/*.yaml`, `data/metrics/*`)
- **Option B**: Keep allow-list model but add a pre-commit hook / CI gate that fails if any tracked file is not in the allowlist (index-scoped validation, not commit-scoped)
- **Deferred per dialectic agreement** (2026-09-20): not required for debut; the immediate fix closes the leak; Phase 2 hardening scheduled post-debut

## 5. Status

- **P0**: COMPLETE — file de-tracked, sanitized template in place, no tracked credential-adjacent artifacts
- **Phase 2**: DEFERRED — allowlist restructure scheduled post-debut per dialectic agreement

## 6. References

- Dialectic: `DIALECTIC_ANTIGRAVITY_TO_MAKALI_20260920_2340.md` (data/coordination)
- P0 execution log: `data/coordination/PR_READINESS_LIVE_FEED.md` (P0-2 entries)
- Allowlist: `docs/strategy/PUBLIC_ALLOWLIST.txt`
- PR Readiness plan: `docs/federation/OMEGA ENGINE PR READINESS.md`

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ NEMOTRON-3.5-LIGHTNING ⬡ P1-4 ⬡ 2026-09-21*