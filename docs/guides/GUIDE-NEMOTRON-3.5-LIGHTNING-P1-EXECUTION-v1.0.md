#  🤖 NEMOTRON 3.5 LIGHTNING — P1 EXECUTION GUIDE
**Document ID:** `GUIDE-NEMOTRON-3.5-LIGHTNING-P1-EXECUTION-v1.0`  
**Status:** `ACTIVE`  
**Target Model:** `nvidia/nemotron-3.5-lightning-30b-a3b` (NVFP4)  
**Audience:** Nemotron 3.5 Lightning (executing model)  
**Prerequisites:** 
- P0 queue complete (verified via `make check-mandates`)
- Continuity artifacts hydrated (session_gnosis.md, SESSION_ANCHOR.md, projection.md, proposed_lessons.yaml)
- Python 3.13 venv active with ruff installed

**This guide is self-contained.** All task instructions, verification commands, and output formats are inline. You do not need any other document to execute P1. (Server launch config, if needed, is in the Quick Reference Card.)

**Deployment Modes (pick the one that matches your runtime):**
- **Mode A — OpenCode/agent runtime (typical)**: You are already running as Nemotron 3.5 Lightning inside the agent harness. Skip the vLLM server check below; go straight to task execution. The verification commands (grep, py_compile, make) run in the workspace shell.
- **Mode B — vLLM server (self-hosted)**: If you are served via a local vLLM endpoint, verify server health first (step 3 below) using the launch config in the Quick Reference Card.

---

## ⚡ EXECUTION MODEL

**You are Nemotron 3.5 Lightning.** You execute the P1 tasks defined in this guide. Your strengths:
- Pattern recognition across codebases (bare-except detection, VaultCrypto classification)
- Structured output generation (audit reports, fixes, documentation)
- Tool calling for file operations, grep, verification
- 256K native context (1M extended) — process related files in batches

**Your Constraints:**
- Reasoning + output share `max_tokens` budget — disable thinking for structured output
- Use `enable_thinking: false` for JSON, code fixes, documentation
- Output format templates are mandatory — follow them exactly
- Verify each fix with linter/compile before marking complete

---

## 🔧 ENVIRONMENT SETUP (Verify Before Starting)

```bash
# 1. Verify venv active
which python
# EXPECTED: /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/python

# 2. Verify ruff available
.venv/bin/ruff --version
# EXPECTED: ruff 0.x.x

# 3. [Mode B ONLY — vLLM server] Verify server reachable
curl -s http://localhost:8000/v1/models | jq -r '.data[0].id'
# EXPECTED: nemotron-3.5-lightning
# NOTE: requires jq installed; if jq missing, use: curl -s http://localhost:8000/v1/models

# 4. Verify P0 complete
make check-mandates
# EXPECTED: 23/28 passed, 0 failed
```

---

## 📋 TASK P1-1: M9 BARE-EXCEPT AUDIT & FIX

### 1.1 Discovery Phase — Find All Bare Excepts

**Prompt:**
```
Find ALL bare `except Exception:` statements in src/omega/ (excluding __pycache__, .backup.* files).

Run this command and report the full output:
grep -rn "except Exception:" src/omega/ --include="*.py" | grep -v "logger\|log\."

Then for EACH match, show me:
- File path and line number
- 5 lines before and after the match
- Whether it has 'as e' capture
- Whether it has logging with exc_info=True
```

**Expected Output Format:**
```
## BARE EXCEPT INVENTORY
Total found: N

### File: src/omega/module.py:42
Context:
```python
# lines 37-47
try:
    do_something()
except Exception:
    pass
```
Has 'as e': NO
Has logging: NO
Classification: M9 VIOLATION - needs fix
```

### 1.2 Fix Phase — Process Files in Batches

**Batch Strategy:** Process 5-10 related files per turn. For each file:

**Prompt Template (use for each file with violations):**
```
Fix bare excepts in: src/omega/[file].py

Current violations in this file:
[List from inventory]

For EACH bare except, apply this EXACT pattern:

BEFORE:
```python
except Exception:
    [current handling]
```

AFTER:
```python
except Exception as e:
    logger.warning("Specific context describing what failed: %s", e, exc_info=True)
    [appropriate handling: re-raise / return default / continue / etc.]
```

Requirements:
1. ALWAYS add 'as e' capture
2. ALWAYS add logger.warning with exc_info=True
3. Context string must describe the OPERATION that failed (not generic "error occurred")
4. Preserve original control flow (re-raise if it did, return default if it did, etc.)
5. Import logging if not present: `import logging; logger = logging.getLogger(__name__)`

Output format for THIS file:
## File: src/omega/[file].py
### Fix 1 (line N):
**Before:**
```python
[exact lines]
```
**After:**
```python
[fixed lines]
```
**Justification:** [Why this fix is correct]

### Fix 2 (line M):
[Same format]

### Verification:
Run: python -m py_compile src/omega/[file].py
Result: [PASS/FAIL]
```

### 1.3 Verification Phase — After Each Batch

**Prompt:**
```
Verify the batch just fixed:

1. Run: find src/omega -name "*.py" -exec python -m py_compile {} +
   Report: PASS or FAIL with error details

2. Run: grep -rn "except Exception:" src/omega/ --include="*.py" | grep -v "logger\|log\." | wc -l
   Report: Remaining count

3. Run: grep -rn "except Exception as " src/omega/ --include="*.py" | wc -l
   Report: Fixed count

4. Spot-check 2 fixed files for correct pattern
```

### 1.4 Completion Criteria for P1-1

**All must be true:**
- [ ] `grep -rn "except Exception:" src/omega/ --include="*.py" | grep -v "logger\|log\." | wc -l` returns `0`
- [ ] `find src/omega -name "*.py" -exec python -m py_compile {} +` passes for all src/omega/*.py
- [ ] `make check-mandates` still passes (M9 gate)
- [ ] No existing tests broken

**When done, report:**
```
P1-1 COMPLETE
- Files fixed: N
- Bare excepts eliminated: N
- Verification: ALL PASS
- Next task: P1-2 (can run in parallel)
```

---

## 🔍 TASK P1-2: VAULTCRYPTO() CALLSITE AUDIT

### 2.1 Discovery Phase

**Prompt:**
```
Find ALL VaultCrypto() instantiation sites in src/omega/ and mcp_servers/:

Run:
grep -rn "VaultCrypto(" src/omega/ mcp_servers/ --include="*.py" | grep -v "backup\|__pycache__\|#"

For EACH match, show:
- File path and line number
- 10 lines before and after
- Module/package context (what subsystem)
```

### 2.2 Classification Phase

**Prompt:**
```
Classify EACH callsite as DEBUT-TRACK or EXCLUDED:

DEBUT-TRACK criteria (sprint-critical paths):
- Installer (scripts/install_omega.py)
- MCP Runtime (src/omega/mcp_runtime.py)
- Mandate Auditor (src/omega/audit/mandate_auditor.py)
- Federation (src/omega/governance/federation_*.py)
- CLI entry points
- Any code that MUST work for v1.6.1-alpha debut

EXCLUDED criteria:
- omega/vault/ module (Vault-specific)
- Test files
- Experimental/deprecated code
- Commented-out code

For EACH callsite, output:
## File: path/to/file.py:line
### Context:
```python
[10 lines before/after]
```
### Classification: [DEBUT-TRACK / EXCLUDED]
### Justification: [1-2 sentences]
### Action Required: [Remove usage / Install argon2-cffi / Add error handling / No action needed]
```

### 2.3 Report Generation

**Prompt:**
```
Generate the audit report at: data/coordination/P1-2_VAULTCRYPTO_AUDIT.md

Use EXACT format below:

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

Include:
- Summary counts
- All DEBUT-TRACK items with actions
- All EXCLUDED items with justifications
- References to dialectic/P0 execution
```

### 2.4 Action Execution (if needed)

**If any DEBUT-TRACK requires argon2-cffi:**
```
Prompt: Install argon2-cffi and verify
Run: .venv/bin/pip install argon2-cffi
Verify: .venv/bin/python -c "import omega.vault.crypto" 2>&1 | grep -iE "pyrage|argon2"
Expected: Empty output (no warning)
```

**If any DEBUT-TRACK requires usage removal:**
```
Prompt: Remove VaultCrypto() usage from [file] and replace with appropriate alternative
[Provide specific fix based on context]
Verify: python -m py_compile [file]
```

### 2.5 Completion Criteria for P1-2

- [ ] Audit report exists at `data/coordination/P1-2_VAULTCRYPTO_AUDIT.md`
- [ ] Every callsite classified
- [ ] All DEBUT-TRACK items have documented feasible actions
- [ ] If argon2-cffi needed: installed and warning suppressed
- [ ] Report references dialectic and P0 execution

**When done, report:**
```
P1-2 COMPLETE
- Total callsites: N
- DEBUT-TRACK: N (actions documented)
- EXCLUDED: N
- argon2-cffi: [INSTALLED/NOT_NEEDED]
- Next task: P1-6 (if argon2-cffi installed) or P1-3/P1-4/P1-5
```

---

## 🗂️ TASK P1-3: BACKUP FILES GITIGNORE — VERIFY & HARDEN

### 3.0 Verify Current State First (Verified Premise)

**IMPORTANT (verified 2026-09-21):** `.gitignore` ALREADY has root-level `*.backup.*` and `*.backup` patterns (line ~286). Tracked backup files = 0, tracked lock files = 0 already. This task is verification + hardening, NOT initial setup.

### 3.1 Pattern Verification & Hardening

**Prompt:**
```
Verify .gitignore backup/lock coverage:

1. grep -qF "*.backup.*" .gitignore && echo "BACKUP_PATTERN_OK"
2. grep -qF "*.lock" .gitignore && echo "LOCK_PATTERN_OK"

If LOCK_PATTERN_OK does NOT print (only scoped patterns like data/entities/*/*.yaml.lock exist),
add a general pattern to .gitignore:

# Lock files (general)
*.lock

Verify current .gitignore content first, then add only if missing.
```

### 3.2 Verification

**Prompt:**
```
Run ALL verification commands below:

1. grep -qF "*.backup.*" .gitignore && echo "BACKUP_PATTERN_OK"
2. grep -qF "*.lock" .gitignore && echo "LOCK_PATTERN_OK"
3. git ls-files src/omega/ | grep -E "\.backup\." | wc -l
4. git ls-files src/omega/ | grep -E "\.lock$" | wc -l
5. find src/omega -name "*.backup.*" -type f | wc -l
6. find src/omega -name "*.lock" -type f | wc -l

Report each result. All must match expected values.
```

### 3.3 Completion Criteria for P1-3

- [ ] Backup pattern present (root-level `*.backup.*`)
- [ ] Lock pattern present (general `*.lock` OR scoped patterns covering src/omega/)
- [ ] Zero tracked backup files in src/omega/
- [ ] Zero tracked lock files in src/omega/
- [ ] Backup/lock files still exist on disk (untracked)
- [ ] No legitimate source files accidentally excluded

**When done, report:**
```
P1-3 COMPLETE
- Backup pattern: PRESENT (verified)
- Lock pattern: [PRESENT / ADDED]
- Verification: ALL PASS
- Next task: P1-4 or P1-5
```

---

## 📝 TASK P1-4: DEBUT-ALLOWLIST-GAP.md DOCUMENTATION

### 4.1 Document Creation

**Prompt:**
```
Create docs/strategy/DEBUT-ALLOWLIST-GAP.md with EXACT structure below:

Content requirements:
1. The Gap: ACCOUNT_MAP.yaml tracked despite explicit file inclusion allowlist
2. Root Cause: Debut filter validates blobs at specific commits, not directory contents
3. Immediate Fix (P0-2 COMPLETE): git rm --cached + .gitignore entry
4. Phase 2 Fix (DEFERRED): Restructure allowlist with explicit deny patterns or explicit file allows
5. Status: P0 complete, Phase 2 deferred per dialectic agreement
6. References: Link to dialectic doc, P0 execution log, PUBLIC_ALLOWLIST.txt

Write technically accurate, audience-appropriate content. No sensitive data.
```

### 4.2 Verification

**Prompt:**
```
Verify document meets all acceptance criteria:

1. test -f docs/strategy/DEBUT-ALLOWLIST-GAP.md && echo "EXISTS"
2. Check all 6 sections present (grep for "## 1." through "## 6.")
3. grep -q "P0-2" docs/strategy/DEBUT-ALLOWLIST-GAP.md && echo "P0_REF_OK"
4. grep -q "DIALECTIC\|dialectic" docs/strategy/DEBUT-ALLOWLIST-GAP.md && echo "DIALECTIC_REF_OK"

Report each result.
```

### 4.3 Completion Criteria for P1-4

- [ ] Document exists at correct path
- [ ] All 6 required sections present
- [ ] References P0-2 and dialectic
- [ ] Technically accurate (no sensitive data)

**When done, report:**
```
P1-4 COMPLETE
- Document created: YES
- Sections: 6/6 present
- References: OK
- Next task: P1-5
```

---

## ⚙️ TASK P1-5: M24B VENV SOVEREIGNTY GATE

### 5.1 Script Creation

**Prompt:**
```
Create scripts/check_venv_sovereignty.py with these requirements:

1. Shebang: #!/usr/bin/env python3
2. Returns 0 on success, non-zero on failure
3. Prints clear messages to stderr for each failure
4. Validates THREE things:

   A. Python Version Match:
      - System: python3 --version
      - Venv: .venv/bin/python --version
      - Must match major.minor (e.g., both 3.13)

   B. Dependencies Installed:
      - Parse pyproject.toml [project.dependencies] and [project.optional-dependencies]
      - Verify each importable in .venv
      - Report missing with: pip show <package>

   C. Critical Imports:
      - import omega.mcp_runtime → OK
      - import omega.oracle → OK
      - Any ImportError → FAIL with module name

5. Output format:
   [OK] Python version match: 3.13.7 == 3.13.7
   [OK] Dependencies: 47/47 installed
   [OK] Import omega.mcp_runtime: OK
   [OK] Import omega.oracle: OK
   ALL CHECKS PASSED

   Or on failure:
   [FAIL] Python version mismatch: system=3.12.3, venv=3.13.7
   EXIT CODE: 1
```

### 5.2 Makefile Integration

**Prompt:**
```
Add to Makefile (check if target exists first):

check-venv-sovereignty:
	@.venv/bin/python scripts/check_venv_sovereignty.py

Make script executable: chmod +x scripts/check_venv_sovereignty.py
```

### 5.3 Verification

**Prompt:**
```
Run ALL verification commands below:

1. test -x scripts/check_venv_sovereignty.py && echo "EXECUTABLE"
2. make check-venv-sovereignty (report exit code and output)
3. Verify output contains "Python version", "Dependencies", "Import omega.mcp_runtime", "Import omega.oracle"

Report each result.
```

### 5.4 Completion Criteria for P1-5

- [ ] Script exists and executable
- [ ] Makefile target works
- [ ] `make check-venv-sovereignty` exits 0 with all checks passing
- [ ] Script validates all three categories
- [ ] Failure modes tested (manual verification)

**When done, report:**
```
P1-5 COMPLETE
- Script created: YES
- Makefile target: ADDED
- Gate passes: YES
- All validations: OK
- Next task: P1-6 (if needed) or P1 complete
```

---

## 🔇 TASK P1-6: SUPPRESS PYRAGE/ARGON2 WARNING (OPTIONAL)

### 6.0 Selected Option (per Antigravity dialectic 2026-09-21)

**IMPORTANT (verified 2026-09-21):** the import block in `src/omega/vault/crypto.py` (lines 27-35) requires BOTH `pyrage` AND `argon2` in one try block. `pyrage` is NOT installed on Python 3.13 — installing ONLY `argon2-cffi` will NOT suppress the warning.

**SELECTED OPTION: (C) Downgrade log level.** Change line 35 from `logger.warning(...)` to `logger.debug(...)` (same message). This prevents console spam without installing unneeded dependencies (Vault is excluded from debut per D-565). Options (a) and (b) are explicitly rejected.

### 6.1 Execution (Option C only)

```
Modify src/omega/vault/crypto.py line 35:
- Change: logger.warning("pyrage or argon2 not installed — crypto operations will fail")
- To:     logger.debug("pyrage or argon2 not installed — crypto operations will fail")

Verify: python -m py_compile src/omega/vault/crypto.py
```

### 6.2 Verification

**Prompt:**
```
Run ALL verification commands below:

1. .venv/bin/python -c "import omega.vault.crypto" 2>&1 | grep -iE "pyrage|argon2" | wc -l
   # MUST BE 0 (no warning at default WARNING level)

2. grep -n "logger.debug" src/omega/vault/crypto.py | head -1
   # MUST show the modified line (~35)

3. VaultCryptoError still raised:
   .venv/bin/python -c "
from omega.vault.crypto import VaultCrypto
try: VaultCrypto('test-key')
except Exception as e: print('EXPECTED_ERROR:', type(e).__name__)" 2>&1 | grep VaultCryptoError

4. python -m py_compile src/omega/vault/crypto.py
   # MUST exit 0

Report each result.
```

### 6.3 Completion Criteria for P1-6

- [ ] No pyrage/argon2 warning on import (stderr clean at WARNING level)
- [ ] Line 35 uses `logger.debug` (code change applied)
- [ ] VaultCryptoError still raised (behavior preserved)
- [ ] `python -m py_compile` passes

**When done, report:**
```
P1-6 COMPLETE
- Option: C (downgrade to logger.debug)
- Warning suppressed: YES
- VaultCryptoError behavior: PRESERVED
```

---

## 📊 CONTINUITY ARTIFACT UPDATES (After Each Task)

**After completing ANY P1 task, you MUST update these files:**

### session_gnosis.md (append to Section 10 or create Section 11)
```
### 11.x P1-[N] [Task Name] — COMPLETE (2026-09-21)
- Summary: [2-3 sentences]
- Key findings: [bullet points]
- Files modified: [list]
- Verification: [commands run, results]
- Lessons for proposed_lessons.yaml: [L1/L2/L3 drafts]
```

### SESSION_ANCHOR.md (update P1 status)
```
- P1-[N] [Task Name]: ✅ COMPLETE
```

### projection.md (update P1 section)
```
### 🟠 P1 — THIS SPRINT
- P1-1: ✅ M9 bare-except audit & fix
- P1-2: ✅ VaultCrypto() callsite audit
- P1-3: ✅ Backup files gitignore
- P1-4: ✅ DEBUT-ALLOWLIST-GAP.md documentation
- P1-5: ✅ M24b make check-venv-sovereignty gate
- P1-6: ✅ Suppress pyrage/argon2 warning (optional)
```

### proposed_lessons.yaml (append L3 lessons)
```yaml
- "L1: 2026-09-21 — [Concrete observation from P1-N]
  L2: [Pattern/insight]
  L3: [Generalizable principle for future work]"
```

### PR_READINESS_LIVE_FEED.md (append)
```
$(date -u +%FT%TZ) | P1-[N] | [Task name] COMPLETE - [key metric]
```

---

## 🐝 HIVEMIND COORDINATION (Every 30 Minutes)

**Post context snapshot:**
```bash
omega-hub_hivemind_post_context \
  --channel opencode \
  --entity makali_fusion \
  --model nemotron-3.5-lightning \
  --task_current "P1-[N] [Task Name]" \
  --focus_chain '["P1-[N]: [current focus]", "Next: P1-[N+1]"]' \
  --decisions '["Fixed bare except in X files", "Classified Y callsites"]' \
  --continuation "Continuing P1-[N]" \
  --intent status
```

---

## ✅ P1 OVERALL COMPLETION CHECKLIST

**P1 Complete When ALL Tasks Meet Acceptance Criteria AND:**

- [ ] `make check-mandates` passes (23/28, 0 failed)
- [ ] All 6 continuity artifacts updated
- [ ] Hivemind context posted with P1 completion
- [ ] No regressions in existing functionality
- [ ] Ready for P2 (federation verification when Node 1 reconnects)

**Final Report:**
```
P1 COMPLETE — ALL TASKS VERIFIED
- P1-1: M9 bare-except — 0 remaining, N fixed
- P1-2: VaultCrypto audit — N callsites, all classified
- P1-3: Backup gitignore — patterns active, 0 tracked
- P1-4: Allowlist gap doc — created, accurate
- P1-5: Venv sovereignty gate — implemented, passing
- P1-6: pyrage/argon2 warning — suppressed (optional)
- Mandate gate: PASSING
- Continuity: UPDATED
- Next phase: P2 (awaiting Node 1 reconnect)
```

---

## 🆘 TROUBLESHOOTING QUICK REF

| Issue | Command | Fix |
|-------|---------|-----|
| vLLM server down | `curl http://localhost:8000/health` | Restart with Quick Ref config |
| Context full | Degraded coherence | Reset: start new session, hydrate from artifacts |
| Fix breaks tests | `pytest tests/ -x` | Revert file, analyze pattern, re-fix |
| `make check-mandates` fails | `make check-mandates` | Check output; revert last change |
| Import error in venv | `.venv/bin/python -c "import X"` | `.venv/bin/pip install X` |

---

*⬡ OMEGA ⬡ NEMOTRON-3.5-LIGHTNING ⬡ P1-EXECUTION ⬡ v1.0 ⬡ 2026-09-21 ⬡ TASK-SPEC-COMPLIANT ⬡ READY-TO-EXECUTE*
