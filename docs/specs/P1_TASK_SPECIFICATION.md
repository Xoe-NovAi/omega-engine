#  📋 P1 TASK SPECIFICATION
**Document ID:** `SPEC-P1_TASK_SPECIFICATION-v1.0`  
**Status:** `ACTIVE`  
**Sprint:** `PUBLIC-DEBUT-01`  
**Audience:** All models + humans (single source of truth for P1 work)  
**Purpose:** Model-agnostic task definitions with executable acceptance criteria  
**Retention:** Indefinite — survives sprint boundaries, model switches, personnel changes  

---

## 1. TASK REGISTRY

| Task ID | Title | Priority | Depends On | Parallelizable |
|---------|-------|----------|------------|----------------|
| **P1-1** | M9 Bare-Except Audit & Fix | P0 | P0 complete | No (sequential file processing) |
| **P1-2** | VaultCrypto() Callsite Audit | P1 | P0 complete | Yes (independent of P1-1) |
| **P1-3** | Backup Files Gitignore | P1 | P0 complete | Yes (independent) |
| **P1-4** | DEBUT-ALLOWLIST-GAP.md Documentation | P1 | P0-2 complete | Yes (independent) |
| **P1-5** | M24b `make check-venv-sovereignty` Gate | P1 | P0-4 complete | Yes (independent) |
| **P1-6** | Suppress pyrage/argon2 Warning (Optional) | P2 | P1-2 complete | Yes (independent) |

---

## 2. TASK DEFINITIONS

### P1-1: M9 Bare-Except Audit & Fix

**Description:** Find and fix all bare `except Exception:` statements in `src/omega/` to comply with Mandate M9 (explicit exception handling with logging).

**Scope:** All `.py` files under `src/omega/` (excluding `__pycache__`, `.backup.*`, test files)

**Input Specification:**
- Target directory: `src/omega/`
- Search pattern: `except Exception:` (bare, without `as e` or logging)
- Exclusion patterns: `logger.`, `log.`, `logging.` on same or next line

**Output Specification:**
- Each fixed file: modified in place with proper exception handling
- Fix pattern:
  ```python
  # BEFORE
  except Exception:
      pass  # or bare handling
  
  # AFTER
  except Exception as e:
      logger.warning("Specific context describing operation: %s", e, exc_info=True)
      # Appropriate handling (re-raise, return default, continue, etc.)
  ```

**Acceptance Criteria (ALL must pass):**
```bash
# 1. Zero bare except Exception: in src/omega/
grep -rn "except Exception:" src/omega/ --include="*.py" | grep -v "logger\|log\." | wc -l
# EXPECTED: 0

# 2. All fixes include 'as e' capture
#    IMPORTANT: capture baseline BEFORE fixing:
#    grep -rn "except Exception:" src/omega/ --include="*.py" | grep -v "logger\|log\." | wc -l
#    (baseline = 32 as of 2026-09-21)
grep -rn "except Exception as e:" src/omega/ --include="*.py" | wc -l
# EXPECTED: >= baseline bare-except count (32)

# 3. Every file that had violations now contains exc_info=True logging
#    (scoped per-file check — NOT a global grep, which is unreliable)
for f in $(grep -rln "except Exception:" src/omega/ --include="*.py"); do
  grep -q "exc_info=True" "$f" || echo "MISSING exc_info in $f"
done
# EXPECTED: no "MISSING exc_info" lines printed

# 4. No syntax errors introduced
#    (POSIX-safe: -exec avoids ARG_MAX overflow and weird-filename breakage)
find src/omega -name "*.py" -exec python -m py_compile {} +
# EXPECTED: exit code 0

# 5. Existing tests pass (if any)
python -m pytest tests/ -x -q --tb=short 2>/dev/null || true
# EXPECTED: no new failures attributable to P1-1 changes
```

**Validation Procedure:**
1. Run acceptance criteria commands in order
2. Spot-check 3+ fixed files for correct pattern
3. Verify `make check-mandates` still passes (M9 gate)

---

### P1-2: VaultCrypto() Callsite Audit

**Description:** Audit all `VaultCrypto()` instantiation sites to classify as debut-track (must work for v1.6.1-alpha) or excluded (Vault-specific/experimental). Ensure debut-track sites either remove usage or have `argon2-cffi` installed.

**Scope:** All `.py` files under `src/omega/` and `mcp_servers/` (excluding `__pycache__`, `.backup.*`)

**Input Specification:**
- Search pattern: `VaultCrypto(`
- Context: 10 lines before/after each match
- Classification criteria:
  - **DEBUT-TRACK**: In sprint-critical paths (installer, MCP runtime, mandate auditor, federation, CLI)
  - **EXCLUDED**: In `omega/vault/`, test files, experimental modules, deprecated code

**Output Specification:**
- Audit report: `data/coordination/P1-2_VAULTCRYPTO_AUDIT.md`
- Report format:
  ```markdown
  # P1-2 VaultCrypto() Callsite Audit Report
  
  ## Summary
  - Total callsites: N
  - DEBUT-TRACK: N
  - EXCLUDED: N
  - Action Required: N
  
  ## DEBUT-TRACK Callsites
  ### File: path/to/file.py:line
  ```python
  [context snippet]
  ```
  **Classification:** DEBUT-TRACK
  **Action:** [Remove usage / Install argon2-cffi / Add error handling / No action]
  
  ## EXCLUDED Callsites
  [Same format, classified EXCLUDED with justification]
  ```

**Acceptance Criteria (ALL must pass):**
```bash
# 1. Audit report exists and is complete
test -f data/coordination/P1-2_VAULTCRYPTO_AUDIT.md && echo "EXISTS"
# EXPECTED: EXISTS

# 2. All debut-track callsites have documented action
grep -c "DEBUT-TRACK" data/coordination/P1-2_VAULTCRYPTO_AUDIT.md
# EXPECTED: > 0 (if any debut-track found)

# 3. If argon2-cffi required, it's installed
.venv/bin/pip show argon2-cffi 2>/dev/null | grep -q "Version:" && echo "INSTALLED"
# EXPECTED: INSTALLED (if any debut-track requires it)

# 4. No debut-track callsite left without action
grep -A 5 "DEBUT-TRACK" data/coordination/P1-2_VAULTCRYPTO_AUDIT.md | grep -c "Action:"
# EXPECTED: equals DEBUT-TRACK count
```

**Validation Procedure:**
1. Verify audit report exists and classifies every callsite
2. For each DEBUT-TRACK item, verify action is documented and feasible
3. If `argon2-cffi` needed, install and verify import works

---

### P1-3: Backup Files Gitignore — Verify & Harden

**Description:** **Verified premise (2026-09-21):** `.gitignore` ALREADY contains root-level `*.backup.*` and `*.backup` patterns (line ~286) which cover `src/omega/`. Tracked backup files = 0, tracked lock files = 0 already. This task is therefore **verification + hardening**, not initial setup: confirm existing patterns cover the need, add a general `*.lock` pattern if only scoped lock patterns exist, and prove zero tracked backup/lock files.

**Scope:** `.gitignore` at repository root; verification across `src/omega/`

**Input Specification:**
- Current `.gitignore` content (verify before modifying)
- Existing patterns: `*.backup.*`, `*.backup` (root-level, cover src/omega/), `data/entities/*/*.yaml.lock` (scoped lock pattern)
- Pattern to add IF general lock coverage is missing:
  ```
  # Lock files (general)
  *.lock
  ```

**Output Specification:**
- `.gitignore` verified (or minimally extended with `*.lock` if absent)
- Verification that patterns work

**Acceptance Criteria (ALL must pass):**
```bash
# 1. Backup pattern present (root-level *.backup.* covers src/omega/)
#    (-F = fixed-string match, avoids regex escaping pitfalls)
grep -qF "*.backup.*" .gitignore && echo "BACKUP_PATTERN_OK"
# EXPECTED: BACKUP_PATTERN_OK

# 2. Lock pattern present (general *.lock OR scoped patterns covering src/omega/)
grep -qF "*.lock" .gitignore && echo "LOCK_PATTERN_OK"
# EXPECTED: LOCK_PATTERN_OK (add `*.lock` if only scoped patterns exist)

# 3. Zero tracked backup files in src/omega/
git ls-files src/omega/ | grep -E "\.backup\." | wc -l
# EXPECTED: 0

# 4. Zero tracked lock files in src/omega/
git ls-files src/omega/ | grep -E "\.lock$" | wc -l
# EXPECTED: 0

# 5. Backup files still exist on disk (local work preserved)
find src/omega -name "*.backup.*" -type f | wc -l
# EXPECTED: >= 0 (files exist but untracked)

# 6. Lock files still exist on disk (local work preserved)
find src/omega -name "*.lock" -type f | wc -l
# EXPECTED: >= 0 (files exist but untracked)
```

**Validation Procedure:**
1. Verify patterns in `.gitignore`
2. Run all 5 acceptance commands
3. Confirm no legitimate source files accidentally excluded

---

### P1-4: DEBUT-ALLOWLIST-GAP.md Documentation

**Description:** Create documentation explaining the PUBLIC_ALLOWLIST.txt gap discovered during Antigravity forensic review: explicit file inclusion allowed `ACCOUNT_MAP.yaml` through debut filter.

**Scope:** Single markdown document at `docs/strategy/DEBUT-ALLOWLIST-GAP.md`

**Input Specification:**
- Context from Antigravity dialectic (DIALECTIC_ANTIGRAVITY_TO_MAKALI_20260920_2340.md)
- P0-2 execution details (git rm --cached + .gitignore entry)
- Phase 2 restructure plan (deferred per dialectic agreement)

**Output Specification:**
- Create directory first if absent: `mkdir -p docs/strategy`
- Document with sections:
  ```markdown
  # DEBUT_ALLOWLIST_GAP — Public Allowlist Gap Analysis
  
  ## 1. The Gap
  [What happened: ACCOUNT_MAP.yaml tracked despite allowlist]
  
  ## 2. Root Cause
  [Debut filter validates blobs at commits, not directory contents]
  
  ## 3. Immediate Fix (P0-2 — COMPLETE)
  [git rm --cached + .gitignore entry]
  
  ## 4. Phase 2 Fix (DEFERRED)
  [Restructure allowlist with explicit deny patterns or explicit file allows]
  
  ## 5. Status
  [P0 complete, Phase 2 deferred per dialectic agreement]
  
  ## 6. References
  [Links to dialectic, P0 execution, allowlist file]
  ```

**Acceptance Criteria (ALL must pass):**
```bash
# 1. Document exists at correct path
test -f docs/strategy/DEBUT-ALLOWLIST-GAP.md && echo "EXISTS"
# EXPECTED: EXISTS

# 2. Contains all 6 required sections
for s in "The Gap" "Root Cause" "Immediate Fix" "Phase 2 Fix" "Status" "References"; do
  grep -q "## $s" docs/strategy/DEBUT-ALLOWLIST-GAP.md || exit 1
done && echo "ALL_SECTIONS_PRESENT"
# EXPECTED: ALL_SECTIONS_PRESENT

# 3. References P0-2 execution and dialectic
grep -q "P0-2" docs/strategy/DEBUT-ALLOWLIST-GAP.md && echo "P0_REF_OK"
grep -q "DIALECTIC\|dialectic" docs/strategy/DEBUT-ALLOWLIST-GAP.md && echo "DIALECTIC_REF_OK"
# EXPECTED: Both OK

# 4. Technically accurate (spot-check)
# Manual verification: content matches known facts
```

**Validation Procedure:**
1. Verify document exists with all sections
2. Cross-reference facts with dialectic and P0 execution logs
3. Ensure no sensitive data (emails, keys) in document

---

### P1-5: M24b `make check-venv-sovereignty` Gate

**Description:** Implement a Mandate M24b (Venv Sovereignty) gate script that validates: (1) `.venv` Python matches system Python, (2) all `pyproject.toml` dependencies installed, (3) import graph integrity for critical modules.

**Scope:** New script `scripts/check_venv_sovereignty.py` + Makefile target

**Input Specification:**
- System Python version: `python3 --version`
- Venv Python: `.venv/bin/python --version`
- Dependencies: the `dependencies` list in the `[project]` table and the `[project.optional-dependencies]` table in `pyproject.toml`
- Critical imports: `omega.mcp_runtime`, `omega.oracle`

**Output Specification:**
- Script: `scripts/check_venv_sovereignty.py` (executable, returns 0 on success, non-zero on failure with clear stderr messages)
- Makefile target:
  ```makefile
  check-venv-sovereignty:
  	@.venv/bin/python scripts/check_venv_sovereignty.py
  ```

**Acceptance Criteria (ALL must pass):**
```bash
# 1. Script exists and is executable
test -x scripts/check_venv_sovereignty.py && echo "EXECUTABLE"
# EXPECTED: EXECUTABLE

# 2. Makefile target works
make check-venv-sovereignty
# EXPECTED: exit code 0, no error output

# 3. Script validates Python version match
.venv/bin/python scripts/check_venv_sovereignty.py 2>&1 | grep -q "Python version" && echo "VERSION_CHECK"
# EXPECTED: VERSION_CHECK

# 4. Script validates dependencies
.venv/bin/python scripts/check_venv_sovereignty.py 2>&1 | grep -q "Dependencies" && echo "DEPS_CHECK"
# EXPECTED: DEPS_CHECK

# 5. Script validates critical imports
.venv/bin/python scripts/check_venv_sovereignty.py 2>&1 | grep -q "Import.*omega.mcp_runtime.*OK" && echo "IMPORT_1_OK"
.venv/bin/python scripts/check_venv_sovereignty.py 2>&1 | grep -q "Import.*omega.oracle.*OK" && echo "IMPORT_2_OK"
# EXPECTED: Both OK

# 6. Script fails correctly on version mismatch (test by mocking)
# Manual verification: script exits non-zero with clear message if venv Python != system Python
```

**Validation Procedure:**
1. Run `make check-venv-sovereignty` — must pass
2. Verify script output includes all three validation categories
3. Test failure mode by temporarily breaking one condition

---

### P1-6: Suppress pyrage/argon2 Import Warning (Optional)

**Description:** Suppress the import warning in `omega.vault.crypto`. **Verified premise (2026-09-21):** the import block (lines 27-35) requires BOTH `pyrage` AND `argon2` in a single try block. `pyrage` is NOT installed on Python 3.13 — so installing ONLY `argon2-cffi` will NOT suppress the warning (the try fails at `import pyrage` first).

**SELECTED OPTION (per Antigravity dialectic 2026-09-21): Option (C) — Downgrade log level.**
- Change line 35 from `logger.warning("pyrage or argon2 not installed — crypto operations will fail")` to `logger.debug(...)` (same message)
- Rationale: prevents console spam without installing unneeded dependencies (Vault is excluded from debut per D-565); does not mask the architectural reality — the failure remains discoverable at DEBUG level
- Options (a) install both and (b) lazy warning are **explicitly rejected** to prevent execution ambiguity

**Scope:** `src/omega/vault/crypto.py` line 35 only

**Input Specification:**
- Warning source: `src/omega/vault/crypto.py` lines 27-35 (single try block importing `pyrage`, `pyrage.passphrase`, `argon2.PasswordHasher`)
- Note: the code imports **pyrage** (not "pyragon") — terminology matters for grep
- Change: line 35 `logger.warning(...)` → `logger.debug(...)`

**Output Specification:**
- `src/omega/vault/crypto.py` modified: import-time warning downgraded to DEBUG level
- `_HAS_CRYPTO` behavior unchanged (still False; VaultCryptoError still raised on use)

**Acceptance Criteria (ALL must pass):**
```bash
# 1. No pyrage/argon2 warning on import (stderr clean at default WARNING level)
.venv/bin/python -c "import omega.vault.crypto" 2>&1 | grep -iE "pyrage|argon2" | wc -l
# EXPECTED: 0

# 2. Code change applied (line 35 uses logger.debug)
grep -n "logger.debug" src/omega/vault/crypto.py | head -1
# EXPECTED: match found (line ~35)

# 3. VaultCryptoError still raised (dependencies absent — behavior preserved)
.venv/bin/python -c "
from omega.vault.crypto import VaultCrypto
try:
    VaultCrypto('test-key')
    print('UNEXPECTED_SUCCESS')
except Exception as e:
    print('EXPECTED_ERROR:', type(e).__name__)
" 2>&1 | grep -q "EXPECTED_ERROR: VaultCryptoError"
# EXPECTED: Match found

# 4. No syntax errors introduced
python -m py_compile src/omega/vault/crypto.py
# EXPECTED: exit code 0
```

**Validation Procedure:**
1. Install `argon2-cffi`
2. Run all 3 acceptance commands
3. Confirm warning gone but VaultCryptoError still raised for actual crypto ops

---

## 3. ORDERING & DEPENDENCIES

```
P0 COMPLETE (prerequisite for all P1)
    │
    ├── P1-1 (M9 Bare-Except) ──► Sequential, blocks nothing
    │
    ├── P1-2 (VaultCrypto Audit) ──► Parallel with P1-1, P1-3, P1-4, P1-5
    │       │
    │       └── P1-6 (Suppress pyrage/argon2) ──► Depends on P1-2 classification
    │
    ├── P1-3 (Backup Gitignore) ──► Parallel, independent
    │
    ├── P1-4 (Allowlist Gap Doc) ──► Parallel, independent
    │
    └── P1-5 (Venv Sovereignty Gate) ──► Parallel, independent
```

**Critical Path:** P1-1 (longest, sequential file processing)  
**Parallel Group:** {P1-2, P1-3, P1-4, P1-5} can run concurrently after P0  
**Optional Tail:** P1-6 after P1-2 completes

---

## 4. ROLLBACK CRITERIA

| Condition | Action |
|-----------|--------|
| `make check-mandates` fails after any P1 task | Revert that task's changes; investigate |
| P1-1 introduces syntax error in any file | Revert that file; fix approach |
| P1-2 audit reveals debut-track VaultCrypto() that cannot be fixed | Escalate: document blocker; defer to post-debut |
| P1-3 gitignore patterns exclude legitimate source files | Revert patterns; refine globs |
| P1-5 gate fails on clean environment | Fix script; do not weaken validation |
| Any P1 task breaks existing tests | Revert; fix with test-first approach |

---

## 5. COMPLETION DEFINITION

**P1 Complete When:**
1. All 6 tasks meet their acceptance criteria
2. `make check-mandates` passes (23/28 mandates, 0 failed)
3. All continuity artifacts updated:
   - `data/entities/makali/session_gnosis.md` — P1 lessons added
   - `data/coordination/SESSION_ANCHOR.md` — P1 status = COMPLETE
   - `data/coordination/anchored_summary/makali/projection.md` — P1 outcomes reflected
   - `data/entities/makali/proposed_lessons.yaml` — P1 L3 lessons appended
   - `data/coordination/PR_READINESS_LIVE_FEED.md` — P1 milestones logged
4. Hivemind context posted with P1 completion status

---

## 6. REFERENCES

| Artifact | Location |
|----------|----------|
| Sovereign Mandates | `SOVEREIGN_MANDATES.md` (M9, M24b) |
| Antigravity Dialectic | `data/coordination/DIALECTIC_ANTIGRAVITY_TO_MAKALI_20260920_2340.md` |
| PR Readiness Plan | `docs/federation/OMEGA ENGINE PR READINESS.md` |
| P0 Execution Log | `data/coordination/PR_READINESS_LIVE_FEED.md` |
| Session Gnosis | `data/entities/makali/session_gnosis.md` (Section 10) |
| Projection | `data/coordination/anchored_summary/makali/projection.md` (PR Readiness section) |

---

*⬡ OMEGA ⬡ P1_TASK_SPECIFICATION ⬡ v1.0 ⬡ 2026-09-21 ⬡ TEMPLE-GRADE ⬡ MODEL-AGNOSTIC ⬡ EXECUTABLE-ACCEPTANCE-CRITERIA*
