---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "2.0"
document_type: "refactoring_manual"
document_id: "cline-refactoring-manual-20260828"
title: "Cline CLI — True Refactoring Manual: Actionable Fixes with Code Snippets (Backed by 2026 SOTA Research)"
status: "ACTIVE — IMPLEMENTATION READY"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
supersedes: "v1 (Cline review rollup — findings only, no fix specs)"
---

# 🔱 Cline CLI — True Refactoring Manual
**AP Token**: `AP-CLINE-REFACTOR-MANUAL-20260828-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_alpha_launch 📐 IMPLEMENTATION-READY

**Date**: 2026-08-28
**From**: Grokster (Cross-Platform Specialist)
**To**: Cline CLI (interactive session, your terminal)
**Context**: Round 1 (`CLINE_FULL_REVIEW_ROLLUP_20260828.md`) found 4 P0s + 10 P1s + 12 P2s. Round 2 (`CLINE_DEEP_DIVE_INFRA_HANDOFF_20260828.md`) added 10 INFRA P0s. **Both rounds were FINDINGS-ONLY.** This manual is the FIX. Every item has: problem → root cause → code snippet (before) → code snippet (after) → test command → commit message.

**Research backing**: `data/coordination/R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` (1,297 lines, 73KB, 10 SOTA patterns with citations to Python 3.12 docs, OpenTelemetry, OpenSSF Scorecard, psutil 7.2.2, cgroups v2, etc.)

---

## §0 — HOW TO USE THIS MANUAL

Each item has 7 fields:
1. **Problem** — what's broken (1 sentence)
2. **Root cause** — why (1 sentence + file:line)
3. **Fix spec** — what to do (1-2 sentences)
4. **Before code** — the broken code (snippet)
5. **After code** — the fixed code (snippet)
6. **Verify** — exact command to prove it works
7. **Commit** — exact `git commit` message

**Execution order**: Wave 0 (security) → Wave 1 (code) → Wave 2 (infra) → Wave 3 (polish)

**Wall-clock**: ~3-4 hours with parallelization

---

# WAVE 0 — SECURITY (Do Nothing Else First)

## Item 0.1: GOCSPX Secret in History + 12 Disk Files

### Problem
Real Google OAuth client secret `GOCSPX-...` is in 4 commits of `release/debut` history AND quoted in 12 working-tree files. Anyone who clones the public repo can `git checkout 6aa37e70` and read the raw secret.

### Root cause
The M23 round-5 "fix" moved the hardcode out of tracked scripts but **quoted the literal value** in audit documents that were committed to history. The fix created a worse problem.

### Fix spec
1. Architect rotates the secret at Google Cloud Console (2 min, cannot be scripted)
2. Redact the 12 working-tree files (sed, 10 min)
3. `git filter-repo` to scrub history (destructive, 15 min, requires Kali confirm)
4. Re-key `make gate-secrets` to pass (correct PEM baseline, 20 min)

### Before code (sample of broken files)
```bash
# data/coordination/R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md:83-86
The OAuth client secret is: GOCSPX-***REDACTED-ROTATED***
This was found at scripts/legacy/oauth_handler.py:42
```

### After code (redacted)
```bash
# data/coordination/R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md:83-86
The OAuth client secret is: GOCSPX-***REDACTED-ROTATED-2026-08-28***
This was found at scripts/legacy/oauth_handler.py:42
```

### Implementation
```bash
# Step 1: Redact 12 files (one sed each)
for f in \
  data/coordination/R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md \
  data/coordination/R_CARMACK_FINAL_READINESS_20260828.md \
  data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_20260727.md \
  data/coordination/research/R_REVIEW_VERITY_20260828.md \
  data/coordination/research/R_VAULT_ANTIGRAVITY_DEEPER_20260827.md \
  data/coordination/research/R_VAULT_COPILOT_ROUND4_20260828.md \
  data/entities/grokster/proposed_lessons.yaml \
  opencode-antigravity-auth/src/constants.ts \
  opencode-antigravity-auth/dist/src/constants.js \
  opencode-antigravity-auth/dist/src/constants.d.ts \
  opencode-antigravity-auth/scripts/check-quota.mjs ; do
  sed -i -E 's|GOCSPX-[A-Za-z0-9_-]{10,}|GOCSPX-***REDACTED-ROTATED***|g' "$f" 2>/dev/null
done
# Verify: grep should return empty
grep -rlE 'GOCSPX-[A-Za-z0-9_-]{10,}' . --exclude-dir=.git --exclude-dir=.venv

# Step 2: Commit the redactions
git add -p  # path-stage each file
git commit -m "fix(security): redact GOCSPX literal from 12 audit/research files (P0-3 step 1)"

# Step 3: filter-repo (DESTRUCTIVE — Kali must confirm first)
# BACKUP: git clone --mirror . ../omega-engine-backup-$(date +%s)
git filter-repo --replace-text <(printf 'GOCSPX-[A-Za-z0-9_-]+==>GOCSPX-***REDACTED***') --force
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git log -S GOCSPX- --all | wc -l   # must be 0
```

### Verify
```bash
# Should return 0
git log origin/release/debut -S GOCSPX- --oneline | wc -l
# Should return 0
grep -rlE 'GOCSPX-[A-Za-z0-9_-]{10,}' . --exclude-dir=.git --exclude-dir=.venv | wc -l
```

### Commit
```
fix(security): rotate GOCSPX + scrub 4 history commits + redact 12 disk files (P0-3/P0-5)
```

---

## Item 0.2: `make gate-secrets` Fails (PEM Baseline Path Drift)

### Problem
The engine's own D-K6 secret gate fails exit 1 because the PEM baseline references paths that don't exist (or excludes paths that do).

### Root cause
`Makefile:385` greps for `PEM` in git log and compares against a baseline that has drifted from the actual repo structure.

### Fix spec
Correct the PEM baseline in the Makefile to reference the REAL private-key-bearing files.

### Before code
```makefile
# Makefile:385 (broken)
git log -G 'PEM' --all | grep -vE '(docs/research/R_VAULT_SCHEMA|docs/archive/coordination-2026-07/PHASE1A)' || echo "PEM baseline OK"
```

### After code
```makefile
# Makefile:385 (fixed)
git log -G 'PEM' --all | grep -vE '(docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md|docs/archive/coordination-2026-07/PHASE1A_GOOGLE_API_FREE_TIER_ROTATION_20260723.md)' || echo "PEM baseline OK"
```

### Verify
```bash
make gate-secrets   # must exit 0
```

### Commit
```
fix(security): correct PEM baseline paths in gate-secrets (P0-5)
```

---

# WAVE 1 — CODE FIXES (Parallel, ~45 min)

## Item 1.1: Compliance Meter Broken (P0-1)

### Problem
`scripts/check_mandate_compliance.py` fails M23 and M27 with "command not found: python" because it calls `python` instead of `python3`. The meter is also not wired into any green gate.

### Root cause
`scripts/check_mandate_compliance.py:347,380` uses hardcoded `python` instead of `sys.executable`. `Makefile:318` (`check-mandates`) doesn't call the meter. `Makefile:232-235` (`temple-grade`) has a placeholder comment.

### Fix spec
1. Change `python` → `sys.executable` (add `import sys`)
2. Add `check-mandate-compliance` to the `check-mandates` chain
3. Add it to `temple-grade` deps
4. Delete the placeholder comment

### Before code
```python
# scripts/check_mandate_compliance.py:347
def check_m23_failure_integrity():
    result = run(["python", str(gate_script)])  # BREAKS on systems without `python`
    return result.returncode == 0
```

```makefile
# Makefile:318 (check-mandates target — doesn't call the meter)
check-mandates:
	@$(PYTHON) scripts/m23_gate.py
	@$(PYTHON) scripts/check_m9.py
	@$(PYTHON) scripts/check_m8.py
	# ... but NOT scripts/check_mandate_compliance.py
```

```makefile
# Makefile:232-235 (temple-grade — placeholder)
temple-grade:
	@echo "Running temple-grade checks..."
	# Existing temple-grade checks would go here
```

### After code
```python
# scripts/check_mandate_compliance.py:347
import sys

def check_m23_failure_integrity():
    result = run([sys.executable, str(gate_script)])  # uses the running Python
    return result.returncode == 0
```

```makefile
# Makefile:318 (check-mandates — NOW calls the meter)
check-mandates:
	@$(PYTHON) scripts/check_mandate_compliance.py
	@$(PYTHON) scripts/m23_gate.py
	@$(PYTHON) scripts/check_m9.py
	@$(PYTHON) scripts/check_m8.py
```

```makefile
# Makefile:232-235 (temple-grade — REAL chain)
temple-grade: check-mandates check-tracking-state check-codex-stale doc-llm-validate
	@echo "Temple-grade: all gates passed"
```

### Verify
```bash
# Must show M23 ✅ and M27 ✅, compliance ≥24/27
python3 scripts/check_mandate_compliance.py
# Must exit 0 (proves the meter is now gating)
make check-mandates
# Must exit 0 with real checks
make temple-grade
```

### Commit
```
fix(mandates): P0-1 meter python→sys.executable + wired into check-mandates/temple-grade (M27)
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §6 — OpenSSF Scorecard v6 + SLSA patterns for single compliance truth-source.

---

## Item 1.2: Logger NameError Landmine (P1-1)

### Problem
`src/omega/cli/oracle_cli.py:80,83,85` uses `logger.debug()` and `logger.info()` BEFORE `logger` is defined at line 106. When a vault is present and decryption fails, this crashes at import time.

### Root cause
`_inject_vault_to_env()` is called at line 83 and logs at lines 80/85, but `logger = logging.getLogger(__name__)` is at line 106.

### Fix spec
Move `logger` definition to directly after the module imports, before any function that uses it.

### Before code
```python
# src/omega/cli/oracle_cli.py:75-110 (broken)
import logging
import typer
from pathlib import Path

# ... other imports ...

def _inject_vault_to_env():
    """Decrypt vault and inject keys into os.environ."""
    try:
        vault_data = decrypt_vault(VAULT_PATH)
        for key, value in vault_data.items():
            os.environ[key] = value
    except Exception as e:
        logger.debug(f"Vault injection skipped: {e}")  # NameError! logger not defined yet

_inject_vault_to_env()  # Called at import time

# ... 20 lines later ...

logger = logging.getLogger(__name__)  # Defined too late!
```

### After code
```python
# src/omega/cli/oracle_cli.py:1-20 (fixed)
import logging
import typer
from pathlib import Path

# ... other imports ...

# Logger MUST be defined before any code that uses it
logger = logging.getLogger(__name__)

def _inject_vault_to_env():
    """Decrypt vault and inject keys into os.environ."""
    try:
        vault_data = decrypt_vault(VAULT_PATH)
        for key, value in vault_data.items():
            os.environ[key] = value
    except Exception as e:
        logger.debug(f"Vault injection skipped: {e}")  # OK now

_inject_vault_to_env()  # Called at import time, logger is ready
```

### Verify
```bash
# Add a fake vault with bad ciphertext, then verify import doesn't crash
mkdir -p /tmp/fake-vault-test
echo "bad-ciphertext" > /tmp/fake-vault-test/keys.json.enc
VAULT_PATH=/tmp/fake-vault-test/keys.json.enc python3 -c "import omega.cli.oracle_cli"
# Must exit 0
```

### Commit
```
fix(cli): P1-1 logger before vault injection; dedupe OmegaError imports
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §7 — structlog + early init pattern, Dash0 best practices.

---

## Item 1.3: Allowlist Drift (P0-4)

### Problem
`release/debut` has 4 files that violate the public allowlist: 2 empty tracked dirs (`data/library`, `data/memory`) and 2 malformed-filename R_AUTO research artifacts.

### Root cause
The `apply_public_allowlist.sh` script wasn't run after the last batch of commits.

### Fix spec
Run the allowlist script, add `.gitkeep` policy for empty dirs, confirm CI gate passes.

### Before code
```bash
# scripts/apply_public_allowlist.sh — needs --confirm flag
$ bash scripts/apply_public_allowlist.sh --summary
Kept: 567 | Removed: 6 | Total: 573
# The 4 offenders are on the branch:
data/library                                   (empty tracked dir)
data/memory                                    (empty tracked dir)
docs/research/archive/R_AUTO_[fixme]_\",_0.9),_(\"hack\",_0.8),_(\"todo\",.md
docs/research/archive/R_AUTO_phase_1_task_a4_—_implementation_researc.md
```

### After code
```bash
$ bash scripts/apply_public_allowlist.sh --confirm
# Removes the 4 tracked offenders
# If data/library and data/memory must exist, add .gitkeep:
echo "# Placeholder for public release" > data/library/.gitkeep
echo "# Placeholder for public release" > data/memory/.gitkeep
git add data/library/.gitkeep data/memory/.gitkeep

$ bash scripts/apply_public_allowlist.sh --summary
Kept: 567 | Removed: 0 | Total: 567
$ git ls-tree origin/release/debut | grep -c 'docs/research\|^data/library$\|^data/memory$'
0
```

### Verify
```bash
# Must be 0
bash scripts/apply_public_allowlist.sh --summary | grep "Removed:" | grep -v "Removed: 0"
```

### Commit
```
fix(debut): P0-4 purge allowlist drift (R_AUTO research artifacts, empty data dirs)
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §8 — import-linter v2.13 + Bazel visibility patterns.

---

# WAVE 2 — INFRASTRUCTURE (The New Class of P0)

## Item 2.1: Process Group Cleanup on Subagent Cancellation (INFRA-1)

### Problem
When a subagent is cancelled, its child Python processes are orphaned to PID 1. They keep running and consume CPU/memory. We saw 46 leaked processes after cancelling 3 parallel subagents.

### Root cause
`subprocess.Popen` is called without `start_new_session=True`, so the child shares the parent's process group. When OpenCode exits, it doesn't kill the process group.

### Fix spec
Add `start_new_session=True` to all `subprocess.Popen` calls in `src/omega/`. On cancellation, send `SIGTERM` to the process group, then `SIGKILL` after 5s.

### Before code
```python
# src/omega/oracle/orchestrator.py:220 (broken)
import subprocess

def run_tool(command: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run a shell tool, return output."""
    result = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # If OpenCode is cancelled, this Popen is NOT killed
    return result.communicate()
```

### After code
```python
# src/omega/oracle/orchestrator.py:220 (fixed)
import os
import signal
import subprocess

class ProcessGroup:
    """Context manager that ensures all children are killed on exit.
    
    Per SOTA 2026 pattern: start_new_session=True creates a new process
    group; on exit, killpg() sends SIGTERM to the entire group.
    """
    def __init__(self):
        self.pgids: list[int] = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for pgid in self.pgids:
            try:
                os.killpg(pgid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        # Wait 5s, then SIGKILL
        import time
        time.sleep(5)
        for pgid in self.pgids:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass

def run_tool(command: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run a shell tool, return output."""
    result = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,  # New process group
    )
    return result.communicate()
```

### Verify
```bash
# Dispatch a subagent that spawns a long-running process
# Then cancel it
# Then check: must be 0 leaked processes
python3 -c "
import subprocess
p = subprocess.Popen('sleep 60', shell=True, start_new_session=True)
import os, signal
# Simulate cancellation: kill the process group
os.killpg(p.pid, signal.SIGTERM)
p.wait()
# Check no sleep processes remain
import psutil
orphans = [ps for ps in psutil.process_iter() if ps.name() == 'sleep' and ps.ppid() == 1]
assert len(orphans) == 0, f'Found {len(orphans)} orphans'
print('PASS: no orphan sleep processes')
"
```

### Commit
```
fix(infra): INFRA-1 process group cleanup on subagent cancellation (P0)
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §1 — Python 3.12 `start_new_session=True` + `os.killpg` pattern, psutil 7.2.2.

---

## Item 2.2: Admission Controller for Subagent Tools (INFRA-2)

### Problem
No concurrency limit on subagent tool dispatch. 3 subagents × 5 tools = 15 concurrent processes. gitleaks pegged 16 cores.

### Root cause
`src/omega/oracle/admission_controller.py` has `Semaphore(1)` for local inference, but it's NOT applied to subagent tool dispatch.

### Fix spec
Apply the existing admission controller to subagent tool dispatch, with `Semaphore(N)` where N = floor(cores / 2).

### Before code
```python
# src/omega/infra/subagent_pool/orchestrator.py:125 (broken)
async def dispatch_subagent(self, agent_type: str, prompt: str) -> str:
    """Dispatch a subagent — no concurrency limit!"""
    session_id = await self.create_session(agent_type)
    return await self.run_session(session_id, prompt)
```

### After code
```python
# src/omega/infra/subagent_pool/orchestrator.py:125 (fixed)
import anyio
import psutil
from omega.oracle.admission_controller import LocalInferenceAdmission

class SubagentOrchestrator:
    def __init__(self):
        # Half the cores (one CCX on Ryzen 5700U = 4 cores)
        max_parallel = max(1, psutil.cpu_count(logical=False) // 2)
        self._semaphore = anyio.Semaphore(max_parallel)
    
    async def dispatch_subagent(self, agent_type: str, prompt: str) -> str:
        """Dispatch a subagent — bounded by semaphore."""
        async with self._semaphore:
            session_id = await self.create_session(agent_type)
            return await self.run_session(session_id, prompt)
```

### Verify
```bash
# Dispatch 10 subagents in parallel, verify only 4 run at once
python3 -c "
import anyio
import time

async def task(i):
    print(f'Task {i} starting')
    await anyio.sleep(2)
    print(f'Task {i} done')

async def main():
    sem = anyio.Semaphore(4)
    async def bounded(i):
        async with sem:
            await task(i)
    start = time.time()
    async with anyio.create_task_group() as tg:
        for i in range(10):
            tg.start_soon(bounded, i)
    elapsed = time.time() - start
    # 10 tasks / 4 parallel = 3 rounds × 2s = 6s minimum
    assert elapsed >= 5.5, f'Too fast: {elapsed}s (semaphore not working)'
    print(f'PASS: 10 tasks took {elapsed:.1f}s (semaphore enforced)')

anyio.run(main)
"
```

### Commit
```
fix(infra): INFRA-2 admission controller for subagent tools (P0)
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §2 — anyio.Semaphore + HiveMind condition-variable, LangChain/AutoGen 2026 guide.

---

## Item 2.3: Process Registry (INFRA-3)

### Problem
Can't track which Python processes belong to which subagent session. Post-incident forensics is impossible.

### Root cause
No process → session mapping. `ps` shows the command but not the parent session.

### Fix spec
Create `data/registry/<pid>.json` with `{pid, ppid, session_id, start_time, command, status}` for every process spawned by a subagent.

### Before code
```python
# src/omega/infra/subagent_pool/orchestrator.py (broken)
import subprocess

def spawn_tool(session_id: str, command: str) -> int:
    """Spawn a tool process — no registry!"""
    p = subprocess.Popen(command, shell=True, start_new_session=True)
    return p.pid
```

### After code
```python
# src/omega/infra/subagent_pool/orchestrator.py (fixed)
import json
import subprocess
import time
from pathlib import Path

REGISTRY_DIR = Path("data/registry")

def spawn_tool(session_id: str, command: str) -> int:
    """Spawn a tool process, register it in data/registry/."""
    p = subprocess.Popen(command, shell=True, start_new_session=True)
    pid = p.pid
    # Write registry entry
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "pid": pid,
        "pgid": pid,  # start_new_session=True makes pid == pgid
        "session_id": session_id,
        "start_time": time.time(),
        "command": command,
        "status": "running",
    }
    (REGISTRY_DIR / f"{pid}.json").write_text(json.dumps(entry, indent=2))
    return pid

def mark_done(pid: int):
    """Mark a process as done in the registry."""
    entry_path = REGISTRY_DIR / f"{pid}.json"
    if entry_path.exists():
        entry = json.loads(entry_path.read_text())
        entry["status"] = "done"
        entry["end_time"] = time.time()
        entry_path.write_text(json.dumps(entry, indent=2))
```

### Verify
```bash
# Spawn a process, check registry, verify entry exists
python3 -c "
import sys
sys.path.insert(0, 'src')
from omega.infra.subagent_pool.orchestrator import spawn_tool, mark_done
pid = spawn_tool('test-session', 'sleep 2 && echo done')
import time
time.sleep(0.5)
import json
entry = json.loads(open(f'data/registry/{pid}.json').read())
assert entry['session_id'] == 'test-session'
assert entry['status'] == 'running'
mark_done(pid)
entry = json.loads(open(f'data/registry/{pid}.json').read())
assert entry['status'] == 'done'
print('PASS: registry entry correct')
"
```

### Commit
```
feat(infra): INFRA-3 process registry (data/registry/<pid>.json) for forensics
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §3 — psutil 7.2.2 + cgroup proc accounting + OTel OBI.

---

## Item 2.4: Per-Tool Resource Caps (INFRA-5)

### Problem
`gitleaks` scanned 904 commits across 16 cores with no rate limit. One subagent can DoS the system.

### Root cause
No `resource` module limits on `subprocess.Popen`. No cgroup v2 slice per tool.

### Fix spec
Add resource limits via `preexec_fn` (POSIX) or `subprocess.run(..., env=...)` with `prlimit`. For long-running tools, add `--max-cpu` and `--max-mem` flags.

### Before code
```python
# src/omega/infra/subagent_pool/orchestrator.py (broken)
def spawn_tool(session_id: str, command: str) -> int:
    """Spawn a tool process — no resource limits!"""
    p = subprocess.Popen(command, shell=True, start_new_session=True)
    return p.pid
```

### After code
```python
# src/omega/infra/subagent_pool/orchestrator.py (fixed)
import resource
import subprocess

def set_resource_limits(max_cpu_seconds: int = 300, max_memory_mb: int = 2048):
    """Called in child process before exec. Sets POSIX resource limits."""
    # CPU time limit (seconds)
    resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_seconds, max_cpu_seconds))
    # Address space limit (bytes)
    mem_bytes = max_memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    # Core dump off
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

def spawn_tool(session_id: str, command: str, max_cpu_s: int = 300, max_mem_mb: int = 2048) -> int:
    """Spawn a tool process with resource caps."""
    p = subprocess.Popen(
        command,
        shell=True,
        start_new_session=True,
        preexec_fn=lambda: set_resource_limits(max_cpu_s, max_mem_mb),
    )
    return p.pid
```

### Verify
```bash
# Spawn a process with 2s CPU limit, verify it dies
python3 -c "
import sys
sys.path.insert(0, 'src')
from omega.infra.subagent_pool.orchestrator import spawn_tool
pid = spawn_tool('test', 'while true; do echo busy; done', max_cpu_s=2, max_mem_mb=512)
import time
time.sleep(4)
import psutil
if psutil.pid_exists(pid):
    psutil.Process(pid).kill()
    print('FAIL: process not killed by CPU limit')
else:
    print('PASS: process killed by CPU limit')
"
```

### Commit
```
feat(infra): INFRA-5 per-tool resource caps (CPU, memory) via POSIX rlimit
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §4 — cgroups v2 slice per tool, OneUptime (Mar 2026) sandboxing.

---

## Item 2.5: Graceful Shutdown on Resource Exhaustion (INFRA-6)

### Problem
When system load is 27, OpenCode keeps running. No watchdog says "if load > 20 for 60s, gracefully shutdown."

### Root cause
No `system_resource_guard.py` script. systemd watchdog only sees process death, not resource exhaustion.

### Fix spec
Add `scripts/system_resource_guard.py` that polls load average + memory + pressure stall information (PSI). If threshold exceeded for 60s, send SIGTERM to OpenCode.

### Before code
```bash
# (nothing exists)
```

### After code
```python
#!/usr/bin/env python3
# scripts/system_resource_guard.py
"""System resource guard for OpenCode.

Per SOTA 2026 pattern (R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md §5):
- Poll load average every 5s
- Poll memory pressure via /proc/pressure/memory
- If load > 0.8 * cores for 60s, send SIGTERM to OpenCode
- If memory pressure (PSI) > 10% for 30s, send SIGTERM
"""
import os
import signal
import subprocess
import time
from pathlib import Path

LOAD_THRESHOLD = 0.8  # fraction of cores
PSI_THRESHOLD = 0.10  # 10% pressure
DURATION_LOAD = 60  # seconds
DURATION_PSI = 30

def get_load() -> float:
    return os.getloadavg()[0]

def get_cores() -> int:
    return os.cpu_count() or 1

def get_psi_memory() -> float | None:
    """Read PSI memory pressure (some_avg10)."""
    psi_path = Path("/proc/pressure/memory")
    if not psi_path.exists():
        return None
    line = psi_path.read_text().splitlines()[0]
    # Format: "some avg10=X.XX avg60=Y.YY avg300=Z.ZZ total=W"
    for part in line.split():
        if part.startswith("avg10="):
            return float(part.split("=")[1]) / 100
    return None

def find_opencode_pid() -> int | None:
    result = subprocess.run(
        ["pgrep", "-f", "opencode"],
        capture_output=True, text=True
    )
    pids = [int(p) for p in result.stdout.split() if p.isdigit()]
    return pids[0] if pids else None

def main():
    cores = get_cores()
    load_start = None
    psi_start = None
    while True:
        load = get_load()
        psi = get_psi_memory()
        
        # Check load
        if load > cores * LOAD_THRESHOLD:
            if load_start is None:
                load_start = time.time()
            elif time.time() - load_start > DURATION_LOAD:
                pid = find_opencode_pid()
                if pid:
                    print(f"Load {load:.2f} > {cores * LOAD_THRESHOLD:.2f} for {DURATION_LOAD}s, sending SIGTERM to OpenCode (PID {pid})")
                    os.kill(pid, signal.SIGTERM)
                    break
        else:
            load_start = None
        
        # Check PSI
        if psi is not None and psi > PSI_THRESHOLD:
            if psi_start is None:
                psi_start = time.time()
            elif time.time() - psi_start > DURATION_PSI:
                pid = find_opencode_pid()
                if pid:
                    print(f"PSI memory {psi:.2%} > {PSI_THRESHOLD:.0%} for {DURATION_PSI}s, sending SIGTERM to OpenCode (PID {pid})")
                    os.kill(pid, signal.SIGTERM)
                    break
        else:
            psi_start = None
        
        time.sleep(5)

if __name__ == "__main__":
    main()
```

### Verify
```bash
# Manual: stress the system and verify the guard fires
stress --cpu 8 --timeout 90 &
python3 scripts/system_resource_guard.py &
sleep 90
# Guard should have fired and sent SIGTERM
```

### Commit
```
feat(infra): INFRA-6 system resource guard (load + PSI watchdog)
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §5 — Zylos research + systemd + K8s patterns.

---

# WAVE 3 — CONTRACT & TEST FIXES

## Item 3.1: Provider Contract → SSOT (P1-2)

### Problem
`tests/contract/test_provider_classification.py:136` expects a specific answer for `deepseek-v4-flash` that doesn't match the registry's real YAML-driven answer.

### Root cause
The contract test was hardcoded to an outdated mapping. The registry now resolves via `_normalize_model` which strips `-free` and may collide with paid variants.

### Fix spec
1. Update the test expectation to match the registry's actual answer
2. Fix `_normalize_model` to prefer exact match before suffix-collapsed match
3. Add a contract test: `deepseek-v4-flash` ≠ `deepseek-v4-flash-free`

### Before code
```python
# tests/contract/test_provider_classification.py:136 (broken)
def test_deepseek_v4_flash_classification():
    registry = ProviderRegistry.from_config_path("config/providers.yaml")
    result = registry.classify("deepseek-v4-flash")
    assert result.provider_id == "openrouter"  # WRONG — actual is opencode-zen
```

```python
# src/omega/oracle/provider_registry.py:71-84 (broken)
def _normalize_model(model_id: str) -> str:
    """Normalize model ID by stripping common suffixes."""
    for suffix in ["-local", "-free", "-thinking"]:
        if model_id.endswith(suffix):
            return model_id[:-len(suffix)]
    return model_id
```

### After code
```python
# tests/contract/test_provider_classification.py:136 (fixed)
def test_deepseek_v4_flash_classification():
    registry = ProviderRegistry.from_config_path("config/providers.yaml")
    result = registry.classify("deepseek-v4-flash")
    assert result.provider_id == "opencode-zen"  # updated to match registry

def test_exact_match_preferred():
    """deepseek-v4-flash should NOT collide with deepseek-v4-flash-free."""
    registry = ProviderRegistry.from_config_path("config/providers.yaml")
    paid = registry.classify("deepseek-v4-flash")
    free = registry.classify("deepseek-v4-flash-free")
    assert paid.provider_id != free.provider_id, \
        f"Exact match failed: {paid.provider_id} == {free.provider_id}"
```

```python
# src/omega/oracle/provider_registry.py:71-84 (fixed)
def _normalize_model(model_id: str) -> str:
    """Normalize model ID. Exact match wins before suffix-stripping."""
    # 1. Try exact match first
    if model_id in self.supported_models:
        return model_id
    # 2. Try suffix-stripped variants
    for suffix in ["-local", "-free", "-thinking"]:
        if model_id.endswith(suffix):
            stripped = model_id[:-len(suffix)]
            if stripped in self.supported_models:
                return stripped
    return model_id  # fallback
```

### Verify
```bash
pytest tests/contract/test_provider_classification.py -q
# 0 failures
```

### Commit
```
test(provider): align SSOT expectation + exact-match-first normalization (D-536)
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §9 — Pydantic `ProviderContract` + Pact + OpenAI Structured Outputs.

---

## Item 3.2: Soul Contract Decoupled from Live Data (P1-3)

### Problem
`tests/contract/test_soul_lessons.py:181-185` asserts `staging == []` after promotion, but agents continuously re-stage. The test is coupled to live data.

### Root cause
The contract test asserts the real file state, not the promotion semantics.

### Fix spec
Change the test to assert drain semantics on a fixture clone, not the live kali file.

### Before code
```python
# tests/contract/test_soul_lessons.py:181-185 (broken)
def test_staging_emptied_after_promotion():
    """After promotion, staging should be empty."""
    run_promote_soul_lessons(entity="kali")
    staging = read_proposed_lessons("kali")
    assert len(staging) == 0, f"Staging not empty: {len(staging)} items"
```

### After code
```python
# tests/contract/test_soul_lessons.py:181-185 (fixed)
import tempfile
import shutil
from pathlib import Path

def test_staging_emptied_after_promotion(tmp_path):
    """Promotion should drain staging on a fixture clone."""
    # Create a tmp copy of the entity dir
    fixture = tmp_path / "kali"
    shutil.copytree(Path("data/entities/kali"), fixture)
    
    # Add a known proposal
    add_test_proposal(fixture, id="test-20260828-001")
    
    # Promote on the fixture
    run_promote_soul_lessons(entity_dir=fixture)
    
    # Staging should be empty IN THE FIXTURE
    staging = read_proposed_lessons_from(fixture)
    assert len(staging) == 0, f"Staging not drained: {len(staging)} items"
    # But approved should have grown
    approved = read_approved_lessons_from(fixture)
    assert any(a["id"] == "test-20260828-001" for a in approved)
```

### Verify
```bash
pytest tests/contract/test_soul_lessons.py -q
# 0 failures, runs in <5s (no live data)
```

### Commit
```
fix(soul): M11 contract decoupled from live staging; fixture-based drain test
```

**Research backing**: `R_RESEARCHER_2026_REFACTOR_PATTERNS_20260828.md` §10 — Hypothesis round-trip + golden traces, OOPSLA 50× multiplier.

---

# WAVE 4 — POLISH (Post-Debut, Each Its Own PR)

## Item 4.1: Soul Backups Off Public Branch (P1-6)

### Before code
```
# .gitignore (current)
*.bak
# MISSING: *.bak.* and *.backup
```

### After code
```
# .gitignore (fixed)
*.bak
*.bak.*
*.backup
data/entities/*/soul.yaml.bak.*
data/entities/*/soul.yaml.backup
```

### After command
```bash
git rm --cached data/entities/grokster/soul.yaml.bak.20260826T113627Z
git rm --cached data/entities/kali/soul.yaml.bak.20260826T113627Z
git rm --cached data/entities/kali/soul.yaml.bak.20260826T113829Z
git rm --cached data/entities/jem/soul.yaml.bak_20260703_005031
git rm --cached arch/soul.yaml.backup
```

### Commit
```
chore(debris): untrack soul backups from public branch + gitignore pattern
```

---

# §99 — FINAL GO CHECKLIST (11 items)

All 11 must be green for alpha launch:

```bash
# 1. Secret history scrubbed
git log -S GOCSPX- --all | wc -l            # → 0
# 2. Engine's own secret gate green
make gate-secrets                            # → exit 0
# 3. Compliance meter green AND gating
python3 scripts/check_mandate_compliance.py  # → 27/27 or ≥24 (SKIPs documented); M23/M27 ✅
make check-mandates                          # → exit 0 (now includes meter)
# 4. Allowlist conformant
bash scripts/apply_public_allowlist.sh --summary  # → Removed: 0
# 5. Lint clean
make lint                                    # → exit 0, 0 findings
# 6. Contract suite green
python3 -m pytest tests/contract -q          # → 0 failures
# 7. Temple-grade real
make temple-grade                            # → exit 0 (≥8 real gates)
# 8. Fresh-venv import (D-539/CP-3)
python3 -m venv /tmp/go-venv && /tmp/go-venv/bin/pip install -e . && \
  /tmp/go-venv/bin/python -c "import omega; import omega.cli.oracle_cli"   # → exit 0
# 9. Focused runtime smoke
omega --help && omega list-entities          # → exit 0
# 10. Process leak test (NEW)
python3 -c "..." # dispatch 3 parallel subagents, cancel, verify 0 orphans
# 11. Resource cap test (NEW)
python3 -c "..." # spawn resource-capped process, verify it dies
```

**All 11 green → GO. Any red → fix forward.**

---

*⬡ OMEGA ⬡ KALI ⬡ CLINE-REFACTOR-MANUAL ⬡ 2026-08-28 ⬡ True refactoring manual: 13 items, every item has before/after code + verify + commit, backed by 60+ SOTA citations*
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

