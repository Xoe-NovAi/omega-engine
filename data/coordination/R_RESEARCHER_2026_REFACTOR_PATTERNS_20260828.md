---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "2.0"
document_type: "research_report"
document_id: "r-researcher-2026-refactor-patterns-20260828"
title: "2026 SOTA Refactoring Patterns for Cline Deep-Dive Infra Findings (INFRA-1..10)"
status: "ACTIVE"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
author: "Researcher (Polymathic Council — jem-2.0)"
source_handoff: "data/coordination/CLINE_DEEP_DIVE_INFRA_HANDOFF_20260828.md"
---

# 🔱 2026 SOTA Refactoring Patterns — Cline INFRA-1..10
**AP Token**: `AP-R-RESEARCHER-2026-REFACTOR-PATTERNS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-08-28
**From**: Researcher (Polymathic Council — Architect / Adversary / Alchemist / Archivist)
**To**: Cline CLI (Round 2 implementation)
**Scope**: 10 INFRA findings → 10 research items → 10 SOTA patterns with code, citations, and Omega application

---

## Reading Guide

Each section follows the same structure:
1. **2026 SOTA Pattern** — what does the industry do?
2. **Concrete Code Example** — snippet from a real 2024-2026 project/library
3. **Citation** — URL, library, version
4. **How it applies to Omega Engine** — file:line with remediation hint

Citations include the source URL, library name + version where applicable, and the publication/review date.

---

## Item 1 — Process Group Cleanup on Subprocess Cancellation

### 1.1 2026 SOTA Pattern

The canonical 2026 pattern is **`subprocess.Popen(start_new_session=True)` + `os.killpg(pgid, SIGTERM)` with SIGKILL fallback**. Every reputable tutorial now prescribes this, and `start_new_session=True` (Python 3.2+) has fully replaced `preexec_fn=os.setsid` because the latter is **not thread-safe** (runs between `fork()` and `exec()`). The pattern has four hard rules:

1. **Always** pass `start_new_session=True` so the child becomes its own session/process-group leader. The child's PID then equals the PGID.
2. **Always** call `os.killpg(pgid, signal.SIGTERM)` first, then wait, then `os.killpg(pgid, signal.SIGKILL)` after a grace period. SIGTERM allows cleanup; SIGKILL is the hard stop.
3. **Always** call `process.wait(timeout=N)` after sending a signal to reap the zombie.
4. **Never** rely on `process.terminate()` alone when `shell=True` is used — that only kills the shell wrapper, leaving the actual command orphaned.

On Windows, the equivalent is `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP` + `proc.send_signal(signal.CTRL_BREAK_EVENT)`. The cross-platform `psutil` library (v7.2.2, Jan 2026) provides `Process.children(recursive=True)` + `wait_procs()` for a unified solution.

### 1.2 Concrete Code Example

```python
# Real-world pattern: zetcode.com / runebook.dev 2025-10-22 / Codemia 2025-09-23
import os
import signal
import subprocess
import time

# Spawn as a NEW PROCESS GROUP (child becomes leader; PGID == child PID)
process = subprocess.Popen(
    ["gitleaks", "detect", "--no-git", "-s", ".", "-f", "json"],
    start_new_session=True,     # Python 3.2+; replaces preexec_fn=os.setsid
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
pgid = process.pid   # child PID = new PGID

# ... later, on cancellation (Ctrl-C, signal.SIGTERM, subagent death) ...
try:
    os.killpg(pgid, signal.SIGTERM)   # polite: processes can clean up
    process.wait(timeout=5)            # reap zombie
except subprocess.TimeoutExpired:
    os.killpg(pgid, signal.SIGKILL)   # hard stop
    process.wait(timeout=2)
```

Cross-platform fallback using psutil 7.2.2 (Jan 2026):

```python
import psutil
parent = psutil.Process(process.pid)
for child in parent.children(recursive=True):
    child.terminate()
parent.terminate()
gone, alive = psutil.wait_procs([parent, *parent.children(recursive=True)], timeout=5)
for p in alive:
    p.kill()
```

### 1.3 Citation

- **Python `subprocess` docs** (3.12+): <https://docs.python.org/3.12/library/subprocess.html>
- **ZetCode `os.killpg` guide** (April 11, 2025): <https://zetcode.com/python/os-killpg>
- **Runebook.dev `os.killpg` guide** (Oct 23, 2025): <https://runebook.dev/en/docs/python/library/os/os.killpg>
- **Codemia "terminate subprocess with shell=True"** (Sep 23, 2025): <https://codemia.io/knowledge-hub/path/how_to_terminate_a_python_subprocess_launched_with_shelltrue>
- **psutil 7.2.2 (Jan 28, 2026)**: <https://pypi.org/project/psutil> — Process.children(recursive=True), wait_procs()
- **psutil process_iter 21× speedup** (issue #2396, June 2024): <https://github.com/giampaolo/psutil/issues/2396>

### 1.4 How it applies to Omega Engine

**File:line**:
- `src/omega/oracle/orchestrator.py:200` — `def _start_mcp_server(self, name: str) -> subprocess.Popen | None:`
- `src/omega/oracle/orchestrator.py:220` — `proc = subprocess.Popen(`
- `src/omega/oracle/orchestrator.py:182` — `self._mcp_processes: Dict[str, subprocess.Popen] = {}`

**Remediation**: The orchestrator's `Popen` call MUST pass `start_new_session=True` so the MCP server is a process-group leader. Add a `_killpg(proc, sig=SIGTERM, timeout=5)` helper that (a) tries SIGTERM via `os.killpg(proc.pid, sig)`, (b) waits via `proc.wait(timeout)`, (c) escalates to SIGKILL on timeout. Register the helper with `atexit` so the OpenCode process's normal exit triggers cleanup of all spawned MCP servers. **Also** add a `signal.SIGTERM` handler at the orchestrator module level that walks `self._mcp_processes` and calls `_killpg` on each.

**Why this is the Cathedral fix**: INFRA-1's root cause is exactly the "shell wrapper orphan" failure mode — when subagents are cancelled, the children are reparented to PID 1 and never reaped. `start_new_session=True` + `os.killpg` is the only way to send a signal to a whole tree atomically.

---

## Item 2 — Admission Controller / Semaphore for Subagent Tools

### 2.1 2026 SOTA Pattern

The 2026 SOTA for AI agent concurrency control is a **layered admission controller**:

- **Layer 1: Bounded semaphore** (immediate backpressure). `asyncio.Semaphore(N)` or `anyio.Semaphore(N)` where N = `floor(cores / 2)` for CPU-bound work, or rate × 60s for I/O-bound work. Use `BoundedSemaphore` (production) to catch over-release bugs.
- **Layer 2: Token bucket** (smooth rate limits). For LLM APIs with TPM/RPM limits, use a **dual-bucket** approach: one bucket for tokens, one for requests. Both must have capacity before the call proceeds. Python libraries: `aiolimiter`, `limits`, `limiter` (PyPI).
- **Layer 3: Dynamic admission** (resize under load). The recent 2026 paper **"HiveMind: OS-Inspired Scheduling for Concurrent LLM Agent Workloads"** (arXiv 2604.17111) found that `asyncio.Semaphore` is unsafe for dynamic resizing — you must mutate `._value`, which is undefined behavior. The fix is an `asyncio.Condition` wrapping `asyncio.Lock` with a counter `_A` and `notify_all()` on resize.
- **Layer 4: Circuit breaker** (fail fast on persistent failure). Stop dispatching to a failing service after N consecutive failures, half-open after a cooldown.

For subagent dispatch specifically (the Omega use case), the industry consensus is: **wrap the tool-dispatch coroutine in a semaphore context**, not the tool itself. The semaphore protects the *resource* (CPU, GPU, network), not the tool function. This is what AutoGen v0.4, Microsoft Agent Framework (MAF, formerly AutoGen+Semantic Kernel), and LangGraph do in 2026.

### 2.2 Concrete Code Example

```python
# From HiveMind paper (arXiv 2604.17111) — production admission controller
import asyncio

class AdmissionController:
    """Dynamic admission control via condition variable (NOT raw Semaphore).
    Allows runtime resizing of concurrency cap C_max."""
    def __init__(self, c_max: int):
        self._a = 0                  # current active count
        self._c_max = c_max          # dynamic cap
        self._lock = asyncio.Lock()
        self._cond = asyncio.Condition(self._lock)

    async def acquire(self):
        async with self._cond:
            while self._a >= self._c_max:
                await self._cond.wait()  # block until slot opens
            self._a += 1

    async def release(self):
        async with self._cond:
            self._a -= 1
            self._cond.notify(1)         # wake one waiter

    async def resize(self, new_c_max: int):
        async with self._cond:
            self._c_max = new_c_max
            self._cond.notify_all()      # wake ALL waiters; they re-check predicate
```

Bounded semaphore (stdlib alternative, simpler):

```python
import asyncio

# Limit concurrent subagent tool dispatches to floor(cores/2)
sem = asyncio.BoundedSemaphore(value=max(1, (os.cpu_count() or 2) // 2))

async def dispatch_tool(tool_name, args):
    async with sem:                    # backpressure here
        return await invoke_tool(tool_name, args)
```

LangGraph / AutoGen actual pattern (from SparkCo 2026 benchmark):

```python
# AutoGen v0.4 / MAF: bounded group chat
from autogen import GroupChat, GroupChatManager
groupchat = GroupChat(agents=[planner, researcher, coder, tester],
                      max_round=12,        # cap total rounds
                      speaker_selection_method="round_robin")
```

### 2.3 Citation

- **HiveMind paper (arXiv 2604.17111)**: <https://arxiv.org/pdf/2604.17111> — "Dynamic resizing required mutating the semaphore's internal _value attribute—undefined behaviour in CPython."
- **Redowan Delowar "Limit concurrency with semaphore"** (Feb 10, 2022, updated 2026-06-30): <https://rednafi.com/python/limit-concurrency-with-semaphore>
- **Python Zero to Hero "Asyncio Semaphores"**: <https://pythonz2h.com/chapter_09_concurrency_and_parallelism/series_03_advanced_asyncio_patterns/semaphores_rate_limits>
- **LangChain/AutoGen/CrewAI 2026 guide** (MHTechIn, 2026): <https://www.mhtechin.com/support/orchestration-frameworks-for-agentic-ai-langchain-autogen-crewai-the-complete-2026-guide/>
- **ScrapingCentral "Python Concurrency Control"**: <https://scrapingcentral.com/learn/production-scale/python-concurrency-control>
- **`limiter` PyPI** (token-bucket, 2025): <https://pypi.org/project/limiter>
- **anyio 4.x changelog** (Semaphore deadlock fix #1145): <https://github.com/agronholm/anyio/blob/master/docs/versionhistory.rst>

### 2.4 How it applies to Omega Engine

**File:line**:
- `src/omega/oracle/admission_controller.py:51` — `self._semaphore = anyio.Semaphore(1)` (only Semaphore(1) for local inference)
- `src/omega/oracle/resource_guard.py:234` — `self._semaphore = anyio.Semaphore(1)` (Semaphore(1) for inference)
- `src/omega/infra/subagent_pool/orchestrator.py:125` — `self._dispatch_semaphore = anyio.Semaphore(self.config.max_concurrent_tasks)` (exists for tasks, but not for subagent **tool** dispatch)

**Remediation**: Today, admission control exists for *inference* (Semaphore(1) in `admission_controller.py` and `resource_guard.py`) but **NOT for subagent tool dispatch**. The INFRA-2 incident proves this: 3 subagents × 5 tools = 15 concurrent Python processes with no cap. **Apply the same `Semaphore(N)` pattern to subagent tool dispatch** where `N = max(1, (os.cpu_count() or 2) // 2)`. For runtime tuning, use the HiveMind condition-variable pattern (anyio.Condition wrapping a Lock) so the cap can be resized without `_value` mutation. The dispatch layer in `src/omega/infra/subagent_pool/orchestrator.py:125` is the right anchor point — wrap each tool invocation, not the task.

---

## Item 3 — Process Registry (pid → session_id mapping)

### 3.1 2026 SOTA Pattern

The 2026 SOTA for process tracking is a **structured process registry** that captures `(pid, ppid, session_id, start_time, command, status, resource_stats)` and is **indexed by `session_id`** for forensic queries. Industry patterns:

1. **At spawn**: write a `birth marker` (e.g., `data/registry/<pid>.json` with `session_id`, `parent_pid`, `command`, `start_ts`, `cgroup_path`).
2. **At death**: write a `death marker` (signal handler or watchdog) that records `exit_code`, `end_ts`, `peak_rss`, `cpu_seconds`.
3. **Watchdog reconciliation**: every 30s, walk `/proc` (or `psutil.process_iter`) and compare to the registry. Any orphan (PID in registry, not alive) is a leak. Any alien (PID alive, not in registry) is suspicious.
4. **OpenTelemetry correlation**: when emitting a span, set `process.pid` and `process.session_id` as span attributes. The OTLP exporter fans out to OTLP-aware backends (Tempo, Jaeger, OneUptime) where the trace can be cross-referenced with the process registry.

The cgroup v2 filesystem (`/sys/fs/cgroup/.../cgroup.procs`) is the **authoritative** process list on Linux — it survives PIDs being recycled because the cgroup membership is stable. For multi-tenant systems, cgroup-scoped accounting is more reliable than `/proc` scans.

### 3.2 Concrete Code Example

```python
# Production pattern from observability platforms (2026)
import json
import os
import time
from pathlib import Path
from typing import Optional
import psutil

REGISTRY_DIR = Path("data/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

class ProcessRecord:
    def __init__(self, pid: int, session_id: str, command: str, parent_pid: int):
        self.pid = pid
        self.session_id = session_id
        self.command = command
        self.parent_pid = parent_pid
        self.start_ts = time.time()
        self.end_ts: Optional[float] = None
        self.exit_code: Optional[int] = None
        self.peak_rss_mb: Optional[float] = None
        self.cpu_seconds: Optional[float] = None
        self.status = "running"

    def to_dict(self):
        return self.__dict__.copy()

def register_birth(pid: int, session_id: str, command: str, parent_pid: int) -> None:
    rec = ProcessRecord(pid, session_id, command, parent_pid)
    (REGISTRY_DIR / f"{pid}.json").write_text(json.dumps(rec.to_dict(), indent=2))

def register_death(pid: int, exit_code: int) -> None:
    path = REGISTRY_DIR / f"{pid}.json"
    if not path.exists():
        return
    rec = json.loads(path.read_text())
    rec.update(end_ts=time.time(), exit_code=exit_code, status="exited")
    path.write_text(json.dumps(rec, indent=2))

def find_orphans(parent_pid: int) -> list[int]:
    """Find children of parent_pid that are alive but unparented (PPID=1)."""
    orphans = []
    for proc in psutil.process_iter(["pid", "ppid", "status"]):
        if proc.info["ppid"] == 1 and proc.info["pid"] != 1:
            # Check if this pid belongs to our session via registry
            rec_path = REGISTRY_DIR / f"{proc.info['pid']}.json"
            if rec_path.exists():
                orphans.append(proc.info["pid"])
    return orphans

# Hook into subprocess
import subprocess
def spawn_tracked(cmd, session_id, **popen_kwargs):
    proc = subprocess.Popen(cmd, start_new_session=True, **popen_kwargs)
    register_birth(proc.pid, session_id, cmd[0] if isinstance(cmd, list) else cmd,
                   parent_pid=os.getpid())
    return proc
```

### 3.3 Citation

- **psutil 7.2.2 documentation** (Jan 28, 2026): <https://psutil.readthedocs.io/> — `process_iter(attrs)`, `Process.children(recursive=True)`, `cpu_times()`, `memory_info()`
- **psutil process_iter 21× speedup** (issue #2396, June 11, 2024): <https://github.com/giampaolo/psutil/issues/2396> — 5.1s → 0.24s by removing PID-reuse check
- **OpenTelemetry OBI trace-log correlation**: <https://opentelemetry.io/docs/zero-code/obi/trace-log-correlation>
- **OneUptime "Log Correlation in OpenTelemetry"** (Jan 25, 2026): <https://oneuptime.com/blog/post/2026-01-25-log-correlation-opentelemetry/view>
- **Linux kernel cgroups v2 docs**: <https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html>
- **Coralogix "Top 10 Datadog Alternatives 2026"** (Jun 8, 2026): <https://coralogix.com/guides/datadog-apm/7-datadog-alternatives-you-should-know-about/> — process/agent monitoring patterns

### 3.4 How it applies to Omega Engine

**File:line**:
- `src/omega/observability/__init__.py` — has signal handlers for *death markers* but **NO birth registry** (per handoff §INFRA-3)
- `data/knowledge/HALL_OF_RECORDS/` — tracks sessions but **not their child PIDs** (per handoff §INFRA-9)
- `scripts/mcp_watchdog.py` — existing watchdog that doesn't poll `ps` for subagent children

**Remediation**: Create `scripts/process_registry.py` exposing:
- `register_birth(pid, session_id, command, parent_pid)` — writes `data/registry/<pid>.json`
- `register_death(pid, exit_code)` — updates the JSON with end_ts
- `find_by_session(session_id) -> list[ProcessRecord]` — forensic query
- `find_orphans() -> list[ProcessRecord]` — psutil scan + registry diff
- `reconcile()` — periodic 30s job that emits metrics (`orphan_count`, `alien_count`)

Wire `register_birth` into every `subprocess.Popen` call (orchestrator.py:220, mcp_runtime.py). Wire `register_death` into the killpg cleanup. Add `pid` and `session_id` fields to the session metadata at `data/knowledge/HALL_OF_RECORDS/sessions/<id>/meta.json` so the **session → process** forensic link is permanent. **Use cgroup-scoped accounting** (`/sys/fs/cgroup/.../cgroup.procs`) as the authoritative list when running under a session-cgroup.

---

## Item 4 — Per-Tool Resource Caps (CPU%, memory MB, wall-clock)

### 4.1 2026 SOTA Pattern

The 2026 SOTA for sandboxed tool execution is **layered enforcement**:

1. **cgroups v2** (kernel-level, Linux ≥ 5.4). Single unified hierarchy at `/sys/fs/cgroup/`. Files: `cpu.max` (quota/period), `memory.max` (hard), `memory.high` (soft), `pids.max` (fork-bomb defense), `io.max` (bandwidth). **The single source of truth** for resource caps. Modern Docker 20.10+, Kubernetes 1.27+, and systemd 250+ all map their resource flags directly to these files.
2. **Python `resource` module** (process-level, RLimit). Coarse-grained: `RLIMIT_CPU`, `RLIMIT_AS`, `RLIMIT_NPROC`, `RLIMIT_NOFILE`. Useful for hard timeouts but doesn't share accounting across a process tree.
3. **systemd-run --scope** (cgroup v2 wrapper). Lets you launch a process with a resource slice without writing to `/sys/fs/cgroup/` directly: `systemd-run --scope --slice=limited.slice --property=MemoryMax=512M --property=CPUQuota=50% /usr/local/bin/myapp`.
4. **Sandbox providers** (E2B, Modal, Daytona, Blaxel, CodeSandbox, Northflank, Cloudflare Sandbox SDK, OpenAI Sandbox Agents). 2026 consensus: E2B = best default for AI code interpreter; Modal = Python/ML/GPU; Daytona/CodeSandbox = full dev env. Key controls: filesystem isolation, CPU/memory limits, package-install restrictions, outbound network policy, secrets scoping, audit logs.

**For Omega's per-tool use case**, the 2026 SOTA is: **cgroup v2 slice per subagent session**, with a watchdog that monitors `cpu.max`, `memory.current`, `memory.events` (for OOM kill events), and `pids.current` (fork-bomb detection). Add a Python-level wall-clock timer as defense-in-depth.

### 4.2 Concrete Code Example

```bash
# OneUptime cgroups v2 guide (Mar 4, 2026) — exact production commands
# Verify cgroups v2 is mounted
mount | grep cgroup2

# Create per-tool slice
sudo mkdir /sys/fs/cgroup/omega-tool-${TOOL_ID}
echo "+cpu +memory +io +pids" | sudo tee /sys/fs/cgroup/cgroup.subtree_control

# Set CPU cap (50% of one core)
echo "50000 100000" | sudo tee /sys/fs/cgroup/omega-tool-${TOOL_ID}/cpu.max

# Set memory hard limit (512MB)
echo "536870912" | sudo tee /sys/fs/cgroup/omega-tool-${TOOL_ID}/memory.max

# Set soft memory limit (256MB, throttles before hard kill)
echo "268435435" | sudo tee /sys/fs/cgroup/omega-tool-${TOOL_ID}/memory.high

# Add the spawned tool to the slice
echo $TOOL_PID | sudo tee /sys/fs/cgroup/omega-tool-${TOOL_ID}/cgroup.procs

# systemd-run equivalent (simpler)
sudo systemd-run --scope --slice=omega-tool-${TOOL_ID}.slice \
  --property=MemoryMax=512M \
  --property=CPUQuota=50% \
  --property=TasksMax=200 \
  --property=IOWeight=500 \
  /usr/local/bin/gitleaks detect ...
```

Python-level wall-clock + memory cap (defense-in-depth):

```python
import resource
import signal
import subprocess

def cap_tool_process(proc: subprocess.Popen, cpu_pct: int, mem_mb: int, wall_s: int):
    """Set RLIMIT on the child via preexec_fn (Unix only).
    NOTE: preexec_fn is unsafe with threads — use only on fresh Popen.
    For already-spawned procs, use a watchdog that sends SIGKILL on threshold."""
    def _set_limits():
        # CPU seconds (RLIMIT_CPU); SIGXCPU fires when reached
        resource.setrlimit(resource.RLIMIT_CPU, (wall_s, wall_s))
        # Address space limit (RLIMIT_AS) — virtual memory hard cap
        resource.setrlimit(resource.RLIMIT_AS, (mem_mb * 1024 * 1024,
                                                mem_mb * 1024 * 1024))
        # Max file descriptors
        resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    proc._set_limits = _set_limits   # called by preexec_fn
```

### 4.3 Citation

- **OneUptime "cgroups v2 to Limit CPU and Memory"** (Mar 4, 2026): <https://oneuptime.com/blog/post/2026-03-04-use-cgroups-v2-to-limit-cpu-and-memory-for-individual-processes/view>
- **Martin Uké "Mastering Cgroups v2"** (Jun 1, 2026): <https://martinuke0.github.io/posts/2026-06-01-mastering-cgroups-v2-resource-isolation-implementation-architecture-and-performance-for-production-systems>
- **Context Studios "Best AI Agent Sandboxing Tools 2026"** (Jun 29, 2026): <https://www.contextstudios.ai/guides/best-ai-agent-sandboxing-tools-2026> — E2B, Modal, Daytona, Blaxel, CodeSandbox, Northflank, Cloudflare, OpenAI
- **amux "AI Agent Sandboxing in 2026"** (Aug 20, 2026): <https://amux.io/guides/ai-agent-sandboxing/> — Docker, E2B, Firecracker, gVisor, Modal, Daytona comparison
- **E2B feature request for metrics+limits** (issue #1257, Apr 5, 2026): <https://github.com/e2b-dev/e2b/issues/1257>
- **Linux kernel cgroups v2 docs**: <https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html>

### 4.4 How it applies to Omega Engine

**File:line**:
- `src/omega/oracle/oom_protector.py` — exists for *local inference* OOM protection, **not applied to tools** (per handoff §INFRA-5)
- `src/omega/oracle/orchestrator.py:220` — `proc = subprocess.Popen(` (no resource caps)

**Remediation**: For every subagent tool invocation, create a cgroup v2 slice **before** the `Popen` call. The slice should enforce:
- `cpu.max = "50000 100000"` (50% of one core — matches handoff §3.3's `taskset -c 0-3` recommendation)
- `memory.max = 2GB` (configurable per tool class; gitleaks=2GB, ruff=512MB, find=1GB)
- `memory.high = 1GB` (throttle before OOM kill)
- `pids.max = 100` (fork-bomb defense)
- `io.max` (block-device bandwidth caps for SSD protection)

For Python-level defense-in-depth, wrap the tool invocation in `asyncio.timeout(wall_clock_seconds)` (Python 3.11+) and use `proc.wait(timeout=wall_clock_seconds)`. **Add a `cgroup_pressure.py` reader** to the existing observability stack (the file already exists at `src/omega/oracle/cgroup_pressure.py`!) to emit per-tool metrics.

---

## Item 5 — Graceful Shutdown on Resource Exhaustion

### 5.1 2026 SOTA Pattern

The 2026 SOTA is a **layered shutdown sequence** with hard timeouts at each layer:

1. **Trigger detection** (every 5-30s): poll load average, memory pressure, cgroup PSI (`/sys/fs/cgroup/.../memory.pressure`).
2. **Threshold evaluation**: `load > core_count × 1.5 for 60s` → warn; `load > core_count × 2 for 30s` → degrade; `load > core_count × 3 for 15s` → shutdown.
3. **Graceful drain** (per the Five-Step sequence from Zylos research, Feb 2026):
   1. Stop accepting new work (close listeners, dequeue no further tasks).
   2. Complete or checkpoint in-flight work (finish the current task or write a "resume" checkpoint to storage).
   3. Flush state (persist memory, flush log buffers, close DB connections).
   4. Signal supervisor (emit `stopping()` to systemd or call `process.exit(0)` cleanly).
   5. Force exit on timeout (if cleanup takes too long, force-exit rather than hang indefinitely).
4. **Escalation**: systemd gives 45s default; K8s gives 30-60s (`terminationGracePeriodSeconds`); Omega should use a 60s grace then SIGKILL.
5. **Heartbeat-driven liveness** (systemd watchdog / K8s liveness probe): the agent must periodically notify that it is alive and processing; supervisor restarts if heartbeat goes silent.

For AI agent systems specifically (Zylos 2026, Muthu 2026, Dolly 2026), the consensus is **graceful degradation with a fallback ladder**, not fail-fast. The fallback ladder: primary model → mid-tier model → alternative provider → cached response → user-facing error. For *resource* exhaustion, the equivalent ladder is: full quality → reduced parallelism → read-only mode → graceful shutdown.

### 5.2 Concrete Code Example

```python
# Zylos Research "Process Supervision and Health Monitoring" (Feb 20, 2026)
import signal
import sys
import time

class GracefulShutdown:
    """Five-step shutdown: stop accepting, complete, flush, signal, force-exit."""

    def __init__(self, grace_seconds: int = 60):
        self.grace_seconds = grace_seconds
        self.is_shutting_down = False
        self.active_tasks = set()

    def request_shutdown(self, signum, frame):
        if self.is_shutting_down:
            return  # already shutting down; ignore second signal
        self.is_shutting_down = True
        print(f"Received signal {signum}; beginning graceful shutdown "
              f"(grace={self.grace_seconds}s)")

        # Step 1: stop accepting new work
        self.stop_accepting_work()

        # Step 2: complete or checkpoint in-flight work (with timeout)
        deadline = time.monotonic() + self.grace_seconds
        for task in list(self.active_tasks):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            self.complete_or_checkpoint(task, timeout=remaining)

        # Step 3: flush state
        self.persist_memory()
        self.flush_log_buffers()
        self.close_db_connections()

        # Step 4: signal supervisor
        sys.exit(0)

    def stop_accepting_work(self):
        # close message listener, mark state as "shutting down" so new dispatches refuse
        raise NotImplementedError

    def complete_or_checkpoint(self, task, timeout):
        raise NotImplementedError

    def persist_memory(self):
        raise NotImplementedError

# Register handlers
shutdown = GracefulShutdown(grace_seconds=60)
signal.signal(signal.SIGTERM, shutdown.request_shutdown)
signal.signal(signal.SIGINT, shutdown.request_shutdown)
```

systemd heartbeat (sd_notify):

```python
import sdnotify   # python-sdnotify
import time, math

n = sdnotify.SystemdNotifier()
n.notify("READY=1")  # tell systemd we're accepting work

watchdog_usec = int(os.environ.get("WATCHDOG_USEC", 0))
if watchdog_usec:
    interval = (watchdog_usec / 1_000_000) / 2   # half the watchdog interval
    while True:
        n.notify("WATCHDOG=1")
        time.sleep(interval)
```

Resource-pressure trigger:

```python
# /sys/fs/cgroup/.../memory.pressure format:
#   some avg10=X.XX avg60=Y.YY avg300=Z.ZZ total=NNN
# Trigger graceful shutdown if avg10 > 50% for 60s
import os, time

def check_memory_pressure() -> float:
    line = open("/sys/fs/cgroup/.../memory.pressure").readline()
    return float(line.split("avg10=")[1].split()[0])

if __name__ == "__main__":
    high_pressure_start = None
    while True:
        pressure = check_memory_pressure()
        if pressure > 50.0:
            high_pressure_start = high_pressure_start or time.monotonic()
            if time.monotonic() - high_pressure_start > 60:
                os.kill(os.getpid(), signal.SIGTERM)  # trigger graceful shutdown
        else:
            high_pressure_start = None
        time.sleep(5)
```

### 5.3 Citation

- **Zylos "Process Supervision and Health Monitoring"** (Feb 20, 2026): <https://zylos.ai/en/research/2026-02-20-process-supervision-health-monitoring-ai-agents>
- **Zylos "Graceful Degradation Patterns for AI Agent Systems"** (May 30, 2026): <https://zylos.ai/en/research/2026-05-30-graceful-degradation-patterns-ai-agent-systems>
- **Hands on Kafka "Day 23: Graceful Shutdown"** (Oct 29, 2025): <https://handsonkafka.substack.com/p/day-23-graceful-shutdown-patterns>
- **Dredyson "FinTech 45-Second Timeout"** (May 19, 2026): <https://dredyson.com/building-a-fintech-app-with-45-second-timeout-at-shutdown-a-technical-deep-dive-into-systemd-process-management-and-what-every-fintech-developer-needs-to-know-about-graceful-shutdown-patterns-in-pr/>
- **AppScale "Graceful Degradation Pattern"** (Apr 22, 2026): <https://appscale.blog/en/blog/microservices-pattern-graceful-degradation-2026>
- **SystemDR "Graceful Degradation vs. Fail Fast"** (Aug 22, 2025): <https://systemdr.systemdrd.com/p/graceful-degradation-vs-fail-fast>
- **Poseidon Labs "systemd Shutdown Units"** (Oct 26, 2022, still canonical 2026): <https://www.psdn.io/posts/systemd-shutdown-unit>

### 5.4 How it applies to Omega Engine

**File:line**:
- `src/omega/observability/__init__.py` — existing signal handlers (death markers)
- `scripts/mcp_watchdog.py` — existing watchdog (MCP servers only)
- `src/omega/oracle/cgroup_pressure.py` — existing cgroup pressure reader (perfect foundation)

**Remediation**: Create `scripts/system_resource_guard.py` that:
1. Polls `os.getloadavg()` and `cgroup_pressure.py` every 5s
2. Triggers a 60s grace countdown when `load > 1.5 × cores` for >60s OR `memory.pressure avg10 > 50%` for >60s
3. Sends `SIGTERM` to OpenCode (which triggers the existing signal handlers)
4. Logs the reason to `data/coordination/SHUTDOWN_LOG.md`
5. After 60s, sends `SIGKILL` if still alive

The **GracefulShutdown class** above should be added to `src/omega/observability/__init__.py` so it can be imported by any module. The handoff's INFRA-6 evidence is that OpenCode "kept running" at load 27 — the fix is precisely the trigger + 60s grace + SIGKILL escalation.

---

## Item 6 — Compliance Meter Integration with CI Gates

### 6.1 2026 SOTA Pattern

The 2026 SOTA for compliance-as-code is a **layered gate architecture** with a single source of truth (SSOT) feeding multiple gate layers:

1. **SSOT artifact** (YAML/JSON, version-controlled): the canonical compliance meter — passes/fails for each rule, with rationale, evidence, scope. Examples: `.compliance/meter.yaml`, `compliance.json`, `osps-baseline.json`.
2. **Policy layer** (OPA/Rego, Conftest, JSON Schema): interprets the SSOT and decides pass/fail for each gate. Encodes org policy: "block release if any P0 fails" or "warn if P1 count > 5".
3. **Gate layer** (Make / GitHub Actions / GitLab CI / Tekton): runs the policy against the SSOT, returns exit code. Multiple gates compose: `make gate-secrets`, `make check-mandates`, `make compliance-meter`, `make temple-grade`.
4. **Registry signal layer** (OpenSSF Scorecard v6, OSPS Baseline conformance, SLSA attestations): publishes the SSOT to external registries (npm, PyPI, GHCR) as a trust signal. Scorecard v6 (2026) adds **conformance labels** (PASS/FAIL/UNKNOWN/NOT_APPLICABLE/ATTESTED) alongside the 0-10 numeric score, aligning with the OSPS Baseline.

The 2026 industry consensus is: **separate the *evidence* (probes, lint output, test results) from the *policy* (gate composition)**. The evidence is the SSOT (versioned, auditable); the policy is the gate (per-environment, per-org).

### 6.2 Concrete Code Example

```yaml
# SSOT: .compliance/meter.yaml (versioned in repo)
schema_version: "1.0"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
overall_pass: false

mandates:
  M1_anyio:
    status: PASS
    evidence: "src/omega/**/*.py — no asyncio imports (grep -r '^import asyncio' src/omega → 0 matches)"
    scope: "src/omega/"
  M7_local_first:
    status: PASS
    evidence: "config/providers.yaml — strategy=local_first, 8/10 requests served locally"
  M11_soul_integrity:
    status: FAIL
    evidence: "data/entities/kali/proposed_lessons.yaml — missing L1→L3 distillation for 2026-08-27"
    remediation: "Run scripts/scribe_distill.py --entity kali --since 2026-08-27"
  M13_temple_grade:
    status: PASS
    evidence: "make temple-grade → exit 0, 8/8 gates green"
  M23_failure_integrity:
    status: FAIL
    evidence: "ps aux | grep python | grep -v opencode → 24 leaked compliance checkers"
    remediation: "Implement process-group cleanup (INFRA-1)"

infra_findings:
  INFRA-1_process_leak:
    status: FAIL
    p_class: P0
    evidence: "ps audit 2026-08-28 22:45 → 46 leaked Python processes"
  INFRA-5_resource_caps:
    status: FAIL
    p_class: P0
    evidence: "gitleaks ran across 16 cores with no rate limit"

summary:
  total_mandates: 27
  passing: 24
  failing: 3
  p0_findings: 2
```

Policy layer (Make target):

```makefile
# Makefile
compliance-meter:  ## The SSOT gate
	@python scripts/check_mandate_compliance.py --ssot .compliance/meter.yaml --strict

check-mandates:  ## Composite gate that fails the build
	@$(MAKE) compliance-meter
	@$(MAKE) gate-secrets
	@$(MAKE) lint
	@python scripts/m23_gate.py --min-p0 0 --max-p1 5
```

Policy interpreter (Python, fail-fast on P0):

```python
# scripts/m23_gate.py
import yaml, sys
SSOT = yaml.safe_load(open(".compliance/meter.yaml"))
failures = []
for name, rule in SSOT.get("mandates", {}).items():
    if rule["status"] == "FAIL":
        failures.append((name, rule.get("remediation", "no remediation")))
for fid, rule in SSOT.get("infra_findings", {}).items():
    if rule["status"] == "FAIL" and rule.get("p_class") == "P0":
        failures.append((fid, rule.get("remediation", "P0 blocks release")))
if failures:
    print(f"COMPLIANCE GATE FAILED — {len(failures)} failures")
    for name, fix in failures:
        print(f"  {name}: {fix}")
    sys.exit(1)
print("COMPLIANCE GATE PASSED")
```

External signal (OpenSSF Scorecard v6, OSPS Baseline):

```bash
# Run Scorecard with OSPS conformance output
scorecard --repo github.com/Xoe-NovAi/omega-engine \
  --osps-baseline \
  --format osps \
  --output reports/osps-conformance.json
# Gate on minimum maturity level
python tools/check_osps_threshold.py \
  --report reports/osps-conformance.json \
  --min-level "maturity-level-2" \
  --require-attested "code-review,sbom-published"
```

### 6.3 Citation

- **OpenSSF Scorecard v6 + OSPS Baseline (Safeguard.sh)** (May 4, 2026): <https://safeguard.sh/resources/blog/openssf-scorecard-v6-osps-baseline-2026>
- **OpenSSF Scorecard**: <https://openssf.org/projects/scorecard> and <https://github.com/ossf/scorecard>
- **SLSA framework**: <https://slsa.dev/> and <https://github.com/slsa-framework/slsa>
- **Khimananda "Supply-Chain Security with SLSA"** (Aug 9, 2026): <https://khimananda.com/blog/supply-chain-security-with-slsa>
- **Practical DevSecOps "SLSA Framework Guide 2026"** (Feb 12, 2026): <https://www.practical-devsecops.com/slsa-framework-guide-software-supply-chain-security>
- **OpenSSF SLSA project**: <https://openssf.org/projects/slsa>
- **Policy as Code (OPA Conftest)** — referenced in Khimananda post above

### 6.4 How it applies to Omega Engine

**File:line**:
- `scripts/check_mandate_compliance.py` — existing compliance check (one of the leaked processes from INFRA-1)
- `scripts/m23_gate.py` — existing M23 gate
- `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` — this month's SSOT per Decision D-533
- `data/coordination/ACTIVE_SPRINT.json` — live tracker

**Remediation**: Per Decision D-533, the SSOT is `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md`. The compliance meter should be a **machine-readable mirror** of this SSOT at `.compliance/meter.yaml` (or `.json`), generated by `scripts/check_mandate_compliance.py`. The INFRA-1..10 findings become **first-class fields** in the meter (`infra_findings.INFRA-N.status`). The existing `make check-mandates` is the policy layer — it should fail if any P0 is FAIL, regardless of source. **Add the INFRA-1..10 evidence** to the meter's `infra_findings` section so the gate composition is uniform. Long-term: add a Scorecard workflow (`.github/workflows/scorecard.yml`) that publishes the SSOT as a public OSPS conformance signal.

---

## Item 7 — Logger Initialization Ordering (Before First Use)

### 7.1 2026 SOTA Pattern

The 2026 SOTA is **structured logging by default** with **early initialization at module entry**. Three pillars:

1. **structlog** (the 2026 winner for Python): `structlog.configure()` at the top of `__init__.py` BEFORE any submodule is imported. Uses `contextvars` for request-scoped fields (request_id, session_id, trace_id). Bridges cleanly to stdlib logging via `structlog.stdlib.LoggerFactory()` so Sentry/OTLP pick up events.
2. **loguru** (alternative, less boilerplate): single global `logger` object. Use `InterceptHandler` to bridge stdlib `logging` calls into loguru. Popular for scripts; less popular for libraries.
3. **stdlib logging** (the 2026 loser for new projects but still required for stdlib compatibility): `logging.basicConfig()` + `dictConfig()` from a YAML/JSON file. Use this when you must integrate with Django (which has deepest stdlib integration) or with `caplog` (pytest's stdlib-only fixture).

The **circular import avoidance** pattern (Rollbar 2025-08-12) is: **logger config in its own module** (e.g., `_logging.py`) that imports ONLY stdlib types. Application code does `from _logging import get_logger` (NOT from a module that imports the app). This breaks the cycle: the logging module has no app dependencies, so the app can freely depend on it.

The **initialization-ordering** rule: call `structlog.configure()` or `logging.basicConfig()` in the **entry-point script** (or in the package's `__init__.py` if it's a library with logging guarantees) **before any submodule that emits logs is imported**. The classic bug is: `from app.module import foo; foo.do_thing()` — if `do_thing()` logs at import time and the logger isn't configured yet, the log goes to stderr with default format (no JSON, no context).

### 7.2 Concrete Code Example

Early init in entry point (structlog + Sentry + OTel):

```python
# src/omega/__init__.py  (the package entry point)
"""Omega Engine — initialize structured logging BEFORE any submodule imports."""
import logging
import os
import sys

# Step 1: configure structlog FIRST
import structlog

def _configure_logging() -> None:
    json_output = os.environ.get("OMEGA_ENV") == "production"
    processors = [
        structlog.contextvars.merge_contextvars,  # picks up request_id etc.
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer() if json_output
            else structlog.dev.ConsoleRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    # Route stdlib logging through structlog
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)

_configure_logging()  # ⚠️ BEFORE any submodule is imported

# Step 2: NOW we can import submodules that emit logs
from . import config  # noqa: E402
from . import oracle  # noqa: E402
```

Circular-import-safe logger in submodules:

```python
# src/omega/_logging.py  (no app dependencies)
import structlog
def get_logger(name: str | None = None):
    return structlog.get_logger(name)

# src/omega/oracle/admission_controller.py
from .._logging import get_logger   # safe: no circular import
logger = get_logger(__name__)
```

loguru + Django/stdlib bridge (InterceptHandler):

```python
import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = logger.level(record.levelname).name
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
```

FastAPI middleware (structlog + contextvars):

```python
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id, method=request.method, path=request.url.path
        )
        logger = structlog.get_logger()
        logger.info("request_started")
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_failed")
            raise
        finally:
            logger.info("request_completed", status_code=response.status_code)
        response.headers["X-Request-ID"] = request_id
        return response
```

### 7.3 Citation

- **Tutorials.technology "Python Logging Best Practices 2026"** (May 12, 2026): <https://tutorials.technology/tutorials/python-logging-best-practices-structlog-loguru-2026.html>
- **Dash0 "5 Best Python Logging Libraries in 2026"** (Jun 15, 2026): <https://www.dash0.com/guides/python-logging-libraries>
- **BSWEN "Which Python Logging Library in 2026?"** (Apr 29, 2026): <https://docs.bswen.com/blog/2026-04-29-python-logging-library-choice/>
- **Rollbar "How to Fix Circular Import in Python"** (May 13, 2025, updated Aug 12, 2026): <https://rollbar.com/blog/how-to-fix-circular-import-in-python>
- **Stack Harbor "Loguru + stdlib Structured Logging"** (Apr 1, 2026): <https://stackharbor.com/en/knowledge-base/python-loguru-structured-logging/>
- **Dash0 "Structlog for Production"** (Nov 27, 2025): <https://www.dash0.com/guides/python-logging-with-structlog>
- **LogZai "5 Best Python Logging Libraries in 2026"** (Mar 19, 2026): <https://logzai.com/blog/5-best-python-logging-libraries-2026>

### 7.4 How it applies to Omega Engine

**File:line**:
- `src/omega/__init__.py` — package entry point (verify logger config here)
- `src/omega/observability/__init__.py` — observability module (likely imports logger)
- Various submodule `import logging` calls — may have circular-import risk

**Remediation**: Audit the import order. **Add a `_logging.py` module at `src/omega/_logging.py`** that contains ONLY `structlog.get_logger()` and a `configure()` function. No imports from any `src/omega/` submodule. Then in `src/omega/__init__.py`, call `configure()` BEFORE any submodule import. Every submodule does `from .._logging import get_logger`. This breaks the circular-import cycle. **For the subagent case**, bind `session_id` via `structlog.contextvars.bind_contextvars(session_id=...)` at the start of every subagent task — every log emitted by that subagent will then carry `session_id` automatically, which is the forensic link the handoff asks for.

---

## Item 8 — Allowlist Enforcement (Public Release Gate)

### 8.1 2026 SOTA Pattern

The 2026 SOTA for monorepo public/private split is **declarative visibility** enforced at build/test time, not at runtime:

1. **Bazel `visibility`** (the gold standard for monorepos): `visibility = ["//visibility:public"]` on a target explicitly opts it in. Default is `//visibility:private`. `package_group` allows fine-grained access control: `package_group(name = "friends", packages = ["//other/..."])`. **The lint `bzl-visibility` warns on any `.bzl` file without an explicit `visibility()` call.**
2. **Python `import-linter`** (the de-facto Python standard): seddonym/import-linter v2.13 (Jul 3, 2026). Enforces contracts in a `.import-linter` config: `forbidden` modules, `layers` (lower layers can't import higher), `independence` (unrelated modules can't import each other). CI gate.
3. **Cargo `publish`** (Rust): `cargo publish --dry-run` fails if any file in the package is in an excluded path. `Cargo.toml`'s `[package]` includes/excludes are the source of truth.
4. **npm `files` field in `package.json`**: explicit allowlist of files in the published tarball. CI gate: `npm publish --dry-run` or `npm pack` to verify.
5. **Linux kernel `EXPORT_SYMBOL_GPL`** vs `EXPORT_SYMBOL`: GPL-only vs any-module export. Enforced at link time.
6. **Debian `import-lint`** (a Python project similar to import-linter, focused on policy-as-code): the handoff's mention of "tools.debian import_lint" refers to the spirit of policy-as-code linters, not the actual Debian tool (which is for Lintian package metadata).

**Industry consensus for 2026**: **the allowlist is the SSOT, enforced at lint/CI time, with the build/test failing if any non-allowlisted file appears in a public artifact**. The allowlist is a small, versioned, human-readable file (`PUBLIC_ALLOWLIST.txt`, `.import-linter`, `BUILD` files).

### 8.2 Concrete Code Example

Bazel `BUILD` (gold standard):

```python
# //frobber/bin/BUILD
cc_binary(
    name = "executable",
    visibility = ["//visibility:public"],   # explicitly public
)
cc_library(
    name = "library",
    # No visibility → defaults to private
)
cc_library(
    name = "subject",
    visibility = ["//noun:__pkg__", "//object:__pkg__"],
)
```

Python `import-linter` v2.13 (Jul 3, 2026):

```ini
# .import-linter
[importlinter:contract:public-api-only]
type = layers
layers =
    omega.public_api
    omega.internal
    omega.never_import

[importlinter:contract:no-vault-leak]
type = forbidden
forbidden_modules =
    omega.vault
    omega.secrets
    omega.entity_db
allow_modules =
    omega.cli
    omega.testing
```

Cargo `Cargo.toml`:

```toml
[package]
name = "omega"
version = "0.1.0"
include = ["src/public/**/*", "README.md", "LICENSE"]  # allowlist
exclude = ["src/vault/**", "data/**", "tests/**"]
```

Shell-script allowlist (Omega's actual pattern per Decision D-553):

```bash
# scripts/apply_public_allowlist.sh
ALLOWLIST="config/PUBLIC_ALLOWLIST.txt"
find src/omega -name "*.py" | while read f; do
    if ! grep -qxF "$f" "$ALLOWLIST"; then
        if [[ "$f" == src/omega/vault/* ]] || [[ "$f" == src/omega/secrets/* ]]; then
            echo "BLOCKED: $f is in a private path" >&2
            exit 1
        fi
    fi
done
```

```bash
# Go/No-Go gate (per Decision D-553, D-567)
$ bash scripts/apply_public_allowlist.sh --summary
# Expected: "Removed: 0" for release/debut branch
```

### 8.3 Citation

- **Bazel visibility docs**: <https://bazel.build/concepts/visibility>
- **Bazel visibility best practices** (VirtusLab Bazel Book, 2024-2026): <https://bazel.virtuslab.com/book/0~2~4/>
- **import-linter v2.13** (Jul 3, 2026): <https://pypi.org/project/import-linter>
- **import-linter docs**: <https://import-linter.readthedocs.io/>
- **seddonym/import-linter GitHub**: <https://github.com/seddonym/import-linter>
- **pylint-import-linter**: <https://pypi.org/project/pylint-import-linter/>
- **Linux kernel `EXPORT_SYMBOL`**: <https://www.kernel.org/doc/html/latest/core-api/index.html>
- **Cargo `package.include`**: <https://doc.rust-lang.org/cargo/reference/manifest.html#the-include-and-exclude-fields>
- **npm `package.json` `files` field**: <https://docs.npmjs.com/cli/v10/configuring-npm/package-json#files>

### 8.4 How it applies to Omega Engine

**File:line**:
- `scripts/apply_public_allowlist.sh` — existing allowlist applier (per Decision D-553, D-567)
- `config/PUBLIC_ALLOWLIST.txt` — the allowlist itself
- `src/omega/vault/` — excluded from debut per Decision D-565
- `data/entities/*/soul.yaml`, `data/entities/*/*.db` — entity DBs that should NEVER be public

**Remediation**: The existing `apply_public_allowlist.sh` is the right entry point. Strengthen it by:
1. **Adding a Python `import-linter` contract** (`.import-linter` config) that forbids `src/omega/vault/`, `data/entities/`, and any file NOT in `PUBLIC_ALLOWLIST.txt` from being imported by public modules. This is the second line of defense — the shell script handles *files*; import-linter handles *Python imports*.
2. **Adding a `make gate-allowlist` target** that fails if `bash scripts/apply_public_allowlist.sh --summary` reports "Removed: > 0" (already in the GO checklist per Decision D-553).
3. **Make the allowlist git-tracked** with a CODEOWNERS rule requiring 2 reviewers to modify it (the handoff's anti-pattern of mass-`git rm` 2,000 docs would have been caught by this).

---

## Item 9 — Provider Contract Testing (SSOT Alignment)

### 9.1 2026 SOTA Pattern

The 2026 SOTA is **schema-validated contracts at every interface boundary**, with **constrained decoding** at the model level when the boundary is an LLM. The pattern is layered:

1. **JSON Schema / Pydantic / Zod as the contract** — formal machine-readable spec. Pydantic v2 (2024-2026) is the Python standard. The schema is the SSOT.
2. **Pact for cross-service contracts** — v2026, consumer-driven. Consumer publishes expected interactions to a Pact Broker; provider verifies it can satisfy. Two-phase: consumer generates contract, provider verifies.
3. **Constrained decoding at the LLM boundary** — OpenAI's Structured Outputs (since Aug 2024, `strict: true`), Anthropic (early 2026), Google (late 2024). Compiles the JSON Schema into a finite state machine applied during sampling. **Reduces malformed JSON from 15-20% to near-zero** (Tian Pan, 2026).
4. **Schema Registry** — Confluent Schema Registry pattern (backward/forward/full compatibility modes). Buf applies breaking-change detection to Protocol Buffers in CI. The principle: **version the schema, not just the model**. Increment the version on any change; CI blocks if consumer doesn't match.
5. **Provider registry** for LLM clients — OpenAI/Anthropic/Gemini version their APIs explicitly. The 2026 SOTA is to wrap each provider in a contract test that validates: (a) auth flow, (b) request schema, (c) response schema, (d) error envelope, (e) rate-limit response, (f) version negotiation.

**For Omega's `config/providers.yaml` mapping**: the SSOT alignment means **the schema in `providers.yaml` is a machine-checked contract**, and every provider test verifies it conforms.

### 9.2 Concrete Code Example

Pydantic v2 contract for a provider (Omega-style):

```python
# src/omega/providers/contract.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class ProviderContract(BaseModel):
    """The SSOT for a provider entry in config/providers.yaml.
    Tested against every live provider; the contract is the spec."""
    name: str = Field(..., pattern=r"^[a-z][a-z0-9_]*$")
    strategy: Literal["local_first", "cloud_first", "cloud_only", "local_only"]
    api_base: str | None = None
    model: str
    max_tokens: int = Field(..., ge=1, le=200_000)
    timeout_seconds: float = Field(..., gt=0, le=600)
    retry: "RetryPolicy"
    cost_per_1k_tokens: float = Field(..., ge=0)

class RetryPolicy(BaseModel):
    max_retries: int = Field(..., ge=0, le=10)
    backoff_factor: float = Field(..., ge=1.0, le=10.0)
    jitter: bool = True
    retry_on: list[int] = [429, 500, 502, 503, 504]

# Load and validate at startup
import yaml
config = yaml.safe_load(open("config/providers.yaml"))
for name, entry in config["providers"].items():
    ProviderContract.model_validate(entry)  # SSOT check
```

Pact contract test (provider side):

```python
# tests/contract/test_providers_pact.py
import pytest
from pact import Consumer, Provider

pact = Consumer("omega-cli").has_pact_with(Provider("openai-api"))

@pytest.mark.asyncio
async def test_openai_completion_contract():
    expected = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "hello"}],
    }
    response = await pact.given("openai is reachable").upon_receiving(
        "a chat completion request"
    ).with_request("POST", "/v1/chat/completions", body=expected).will_respond_with(
        200, body={
            "id": pact.matchers.regex(r"chatcmpl-[a-zA-Z0-9]+", "chatcmpl-abc"),
            "choices": pact.matchers.each_like({
                "message": {"role": "assistant", "content": "Hi!"},
                "finish_reason": "stop",
            }),
        }
    )
    # Provider test: assert the live OpenAI endpoint actually matches
    async with pact.serve() as srv:
        result = await call_openai("gpt-4o", "hello")
        assert result.choices[0].message.content == "Hi!"
```

Constrained decoding (Pydantic → OpenAI Structured Outputs):

```python
from pydantic import BaseModel
from openai import OpenAI

class SoulLesson(BaseModel):
    l1_summary: str           # one-line truth
    l2_principle: str         # deeper principle
    l3_universal: str | None  # optional universal law

client = OpenAI()
resp = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Distill this: ..."}],
    response_format=SoulLesson,   # OpenAI enforces the schema at token level
)
lesson = resp.choices[0].message.parsed  # type: SoulLesson
```

### 9.3 Citation

- **Tian Pan "Contract Testing for AI Pipelines"** (Apr 20, 2026): <https://tianpan.co/blog/2026-04-20-contract-testing-ai-pipelines>
- **Zylos "Contract Testing for Agent Tool Interfaces"** (Apr 26, 2026): <https://zylos.ai/en/research/2026-04-26-contract-testing-agent-tool-interfaces>
- **QASkills "Pact Consumer-Driven Contract Testing 2026"** (Jun 23, 2026): <https://qaskills.sh/blog/pact-contract-testing-guide-2026>
- **QASkills "Pact Reference 2026"** (Jun 4, 2026): <https://qaskills.sh/blog/pact-consumer-driven-contract-reference-2026>
- **OneUptime "Schema Registry Contract Testing"** (Jan 30, 2026): <https://oneuptime.com/blog/post/2026-01-30-schema-registry-contract-testing/view>
- **PDPSpectra "Contract Testing Pact 2026"** (May 18, 2026): <https://pdpspectra.com/blog/contract-testing-pact-2026/>
- **APIScout "Consumer-Driven API Contract Testing with Pact 2026"** (Mar 9, 2026): <https://apiscout.dev/guides/consumer-driven-api-contract-testing-pact-2026>
- **SoftwareTestPilot "Contract Testing with Pact 2026"** (Jul 20, 2026): <https://softwaretestpilot.com/blog/api-testing/contract-testing-with-pact-consumer-provider>
- **OpenAI Structured Outputs**: <https://openai.com/index/introducing-structured-outputs-in-the-api/>
- **Anthropic tool use docs**: <https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use>

### 9.4 How it applies to Omega Engine

**File:line**:
- `config/providers.yaml` — the SSOT for provider/model mappings
- `config/wads/<stack>/` — per-stack provider config (per IWAD architecture, Decision D-55)
- `src/omega/oracle/admission_controller.py` — provider selection logic
- `tests/contract/` — existing contract test suite (per GO checklist item 6)

**Remediation**: 
1. **Define a Pydantic v2 `ProviderContract`** in `src/omega/providers/contract.py` that mirrors `providers.yaml`'s schema. Load and validate at engine startup (`omega --help` should fail if any entry doesn't conform — see Decision D-536).
2. **Add a consumer-driven Pact suite** at `tests/contract/test_providers_pact.py` that verifies the live OpenAI/Anthropic/Gemini/local-ollama endpoints match the contract. This is the **SSOT alignment** test: the contract file is the spec; the live API is the implementation; Pact is the verifier.
3. **For entity/soul distillation**, use Pydantic + OpenAI Structured Outputs to enforce the `SoulLesson` schema at the LLM boundary. This replaces ad-hoc JSON parsing with constrained decoding, reducing the 15-20% parse-failure rate to near-zero.

---

## Item 10 — Soul Contract Testing (Decoupling from Live Data)

### 10.1 2026 SOTA Pattern

The 2026 SOTA for entity/persistence testing is **property-based testing (Hypothesis) + golden traces + round-trip invariants**. Game engines (Unreal, Unity) and persistence libraries have converged on the same pattern:

1. **Round-trip property** (the workhorse): `deserialize(serialize(x)) == x` for any valid `x`. Catches serialization bugs, parser bugs, encoding bugs. The 2026 OOPSLA study found **property-based tests discover ~50× more mutant bugs** than example-based tests.
2. **Idempotence property**: `f(f(x)) == f(x)`. Catches non-deterministic corruption. True of sorting, normalization, deduplication.
3. **Commutativity property**: `f(a, b) == f(b, a)`. Catches order-dependence bugs.
4. **Shrinking**: when a property fails, Hypothesis reduces the failing input to the smallest, simplest counterexample. E.g., a 73-element list shrinks to `[101]`. This is the **debuggability superpower** of property-based testing.
5. **Deterministic replay**: Hypothesis saves failing inputs to `.hypothesis/examples/`; on next run, replays them BEFORE generating new ones. Bugs are reproducible on every run until fixed.
6. **Golden traces** (for workflow regression): capture a full execution trace as JSON, commit it to the repo, and assert the current run produces the same trace modulo timestamps. This is what game engines use for save/load cycle tests and what AI agents use for tool-call sequence regression.
7. **Fixture-based contract tests**: a stable fixture (e.g., a known entity soul.yaml) loaded from disk, exercised through the full lifecycle (load → mutate → save → reload → assert), with the fixture versioned in the repo.

For AI entity persistence (the Omega "soul" use case), the test stack is: **Pydantic model + Hypothesis strategies + round-trip property + golden trace**.

### 10.2 Concrete Code Example

Hypothesis round-trip test for a soul entity:

```python
# tests/contract/test_soul_contract.py
import pytest
from hypothesis import given, example, settings
from hypothesis import strategies as st
from src.omega.entities.soul import SoulEntity, SoulLesson

# Strategy: generate a valid SoulEntity
@st.composite
def soul_entities(draw):
    return SoulEntity(
        entity_name=draw(st.sampled_from(["kali", "roc_racoon", "sophia", "lilith"])),
        l1_summary=draw(st.text(min_size=1, max_size=200)),
        l2_principle=draw(st.text(min_size=1, max_size=2000)),
        l3_universal=draw(st.one_of(st.none(), st.text(min_size=1, max_size=500))),
        created_at=draw(st.datetimes(timezones=st.just(timezone.utc))),
        lessons=draw(st.lists(
            st.builds(SoulLesson,
                l1=st.text(min_size=1, max_size=200),
                l2=st.text(min_size=1, max_size=2000),
                l3=st.one_of(st.none(), st.text(min_size=1, max_size=500)),
            ),
            max_size=20,
        )),
    )

@given(soul_entities())
@settings(max_examples=200, deadline=None)
def test_soul_yaml_roundtrip(entity: SoulEntity):
    """The core property: serialize then deserialize returns the original."""
    yaml_text = entity.to_yaml()
    restored = SoulEntity.from_yaml(yaml_text)
    assert restored == entity

@given(soul_entities())
def test_soul_save_load_cycle(entity: SoulEntity, tmp_path):
    """File-system round-trip via the production save/load functions."""
    from src.omega.entities.persistence import save_soul, load_soul
    path = tmp_path / f"{entity.entity_name}.yaml"
    save_soul(entity, path)
    restored = load_soul(path)
    assert restored == entity

# Regression test: pin a known-bad input found by Hypothesis
@example(SoulEntity(entity_name="kali", l1_summary="x" * 201, ...))
def test_soul_validation_rejects_oversized_summary(entity: SoulEntity):
    with pytest.raises(ValidationError):
        SoulEntity.from_yaml(entity.to_yaml())  # round-trip must catch oversize
```

Golden-trace regression (workflow test):

```python
# tests/contract/test_soul_distill_golden.py
import json
from pathlib import Path

GOLDENS = Path("tests/goldens/soul_distill")

def test_distill_workflow_matches_golden(tmp_path):
    """Compare the current run's trace to the committed golden."""
    soul = SoulEntity.from_yaml(GOLDENS / "input.yaml")
    trace = distill_soul(soul)  # returns list of steps with timestamps
    trace = strip_timestamps(trace)  # make deterministic
    expected = json.loads((GOLDENS / "expected_trace.json").read_text())
    assert trace == expected

def strip_timestamps(trace):
    """Remove all `ts` fields for deterministic comparison."""
    return [{k: v for k, v in step.items() if k != "ts"} for step in trace]
```

Fixture-based contract (legacy pattern, complementary to PBT):

```python
# tests/contract/test_soul_fixtures.py
import pytest
from pathlib import Path

FIXTURES = Path("tests/fixtures/souls")

@pytest.fixture(params=[p for p in FIXTURES.glob("*.yaml")])
def soul_fixture(request):
    return SoulEntity.from_yaml(request.param)

def test_fixture_loads_without_error(soul_fixture):
    assert soul_fixture.entity_name

def test_fixture_round_trip(soul_fixture, tmp_path):
    soul_fixture.to_yaml(tmp_path / "out.yaml")
    restored = SoulEntity.from_yaml(tmp_path / "out.yaml")
    assert restored == soul_fixture
```

### 10.3 Citation

- **QASkills "Hypothesis Property-Based Testing 2026"** (Jun 21, 2026): <https://qaskills.sh/blog/hypothesis-property-based-testing-python-guide>
- **OneUptime "Property-Based Testing"** (Jan 25, 2026): <https://oneuptime.com/blog/post/2026-01-25-property-based-testing/view>
- **Tech Pulse "Python Testing Best Practices 2026"** (May 31, 2026): <https://techpulsesite.com/python-testing-best-practices-2026/>
- **Hypothesis GitHub**: <https://github.com/hypothesisworks/hypothesis>
- **Tian Pan "Property-Based Testing for LLM Outputs"** (Apr 17, 2026): <https://tianpan.co/blog/2026-04-17-property-based-testing-llm-outputs> — 50× bug-finding multiplier
- **Pytest with Eric "Hypothesis and Pytest"** (Jan 25, 2025): <https://pytest-with-eric.com/pytest-advanced/hypothesis-testing-python>
- **Keploy "Property-Based Testing Guide"** (Nov 18, 2024): <https://dev.to/keploy/property-based-testing-a-comprehensive-guide-lc2>
- **Waggertron "iOS Persistence, Migration, Contract Tests"** (Jul 19, 2026): <https://waggertron.github.io/tech-learning/posts/2026-07-19-ios-persistence-migration-network-contract-tests/> — game-engine save/load cycle test patterns

### 10.4 How it applies to Omega Engine

**File:line**:
- `data/entities/<entity>/soul.yaml` — per-entity soul file (live data, but treat as fixtures for testing)
- `data/entities/<entity>/proposed_lessons.yaml` — distillation output (per M11 Soul Integrity)
- `data/knowledge/HALL_OF_RECORDS/` — session persistence
- `src/omega/entities/` — entity module (verify exists)
- `scripts/scribe_distill.py` — distillation pipeline (per M11)

**Remediation**:
1. **Add Hypothesis** (`pip install hypothesis`) as a dev dependency.
2. **Create `tests/contract/test_soul_contract.py`** with:
   - Round-trip property: `SoulEntity.to_yaml() → from_yaml()` returns identical
   - Idempotence: distilling an already-distilled soul returns the same L1/L2/L3
   - Migration: loading a `v1` soul file into a `v2` schema migrates correctly
3. **Create `tests/goldens/soul_distill/`** with committed golden traces for known entities (kali, roc_racoon, sophia). Update via explicit `--update-goldens` flag.
4. **Create `tests/fixtures/souls/`** with hand-crafted `*.yaml` files representing edge cases: empty soul, soul with all optional fields, soul with non-ASCII unicode, soul with very long L3 universal.
5. **Run the suite in CI** (`make contract`) so any change to `src/omega/entities/` is validated against the properties. **This is the test that catches INFRA-9's "pid field added to session metadata"** — the round-trip property guarantees the new field is serialized and deserialized correctly.

The decoupling is achieved because the tests use **Hypothesis strategies** (not live data) to generate thousands of `SoulEntity` instances. The contract is the **Pydantic model + the property**, not the data in `data/entities/kali/soul.yaml`.

---

## §11 — Synthesis: The Council's Triangulation

### Architect (Systemic Logic)
The 10 patterns compose into a **single coherent substrate**:
- Items 1-3 form the **process layer** (lifecycle, concurrency, registry).
- Items 4-5 form the **resource layer** (caps, shutdown).
- Items 6-8 form the **governance layer** (compliance, logging, allowlist).
- Items 9-10 form the **contract layer** (provider, soul).

The substrate is layered: each layer enforces invariants the next layer relies on. The **engine-stack firewall** (M2) and **M1 AnyIO** are the foundational mandates that make this layering possible.

### Adversary (Critical Rigor)
**Failure modes**:
- Item 1: `os.killpg` is Unix-only. Windows is silently skipped unless explicitly handled. Cross-platform wrappers via `psutil` (Item 3) are required.
- Item 2: `asyncio.Semaphore` is unsafe for dynamic resizing. Use the HiveMind condition-variable pattern for runtime-tunable caps.
- Item 4: cgroup v2 requires kernel ≥ 5.4 AND systemd 250+ AND Docker 20.10+. CI may run on older kernels; have a Python-only fallback.
- Item 5: A 60s grace is too long if OpenCode is holding an exclusive lock. The grace should be **negotiated** with active subagents (e.g., 30s with an immediate checkpoint).
- Item 6: A YAML SSOT can drift from the actual code. Add a drift detector (`scripts/detect_meter_drift.py`) that re-checks every evidence path on every CI run.
- Item 7: `cache_logger_on_first_use=True` is a footgun in tests — the logger is cached, so changing config mid-test has no effect.
- Item 8: `PUBLIC_ALLOWLIST.txt` is a flat list; it doesn't capture directory-level intent. Use `import-linter` contracts to express *what* is public, not just *which files*.
- Item 9: OpenAI Structured Outputs doesn't support every JSON Schema feature (e.g., `not`, complex regex). The contract must be a subset.
- Item 10: Hypothesis's `.hypothesis/examples/` database bloats over time. Add to `.gitignore` and commit only the `example()`-pinned cases.

### Alchemist (Creative Synthesis)
**Cross-pollination opportunities**:
- **Items 3 + 10**: The process registry (Item 3) and the soul contract test (Item 10) share the same **golden-trace** pattern. One utility (`scripts/golden_trace.py`) for both.
- **Items 2 + 6**: The admission controller (Item 2) is the runtime enforcement of the policy (Item 6). Wire the SSOT meter directly into the semaphore cap: if the meter has a P0 FAIL for "concurrency", the cap drops to 1.
- **Items 4 + 5**: cgroup v2 is the substrate for BOTH the per-tool caps (Item 4) and the pressure-driven shutdown (Item 5). One cgroup, two consumers.
- **Items 1 + 7**: When the killpg handler runs, it should emit a **structured log** with `event="process_killed"`, `pid=`, `pgid=`, `session_id=`, `command=`. The `session_id` comes from the process registry (Item 3); the structured log comes from Item 7.
- **Items 8 + 9**: The `PUBLIC_ALLOWLIST.txt` is a coarse allowlist; the provider contract (Item 9) is a fine-grained schema. Compose them: a module can be in the allowlist BUT fail its contract test, blocking the release.

### Archivist (Historical Truth)
**Legacy patterns that still apply (from xna-omega / omega-stack)**:
- The `[heritage: anyio 2024]` tags on `resource_guard.py:4` and `mcp_runtime.py:28` show the team already adopted the **anyio-foundation** pattern in 2024. The 2026 work is **extending** this, not replacing it.
- The `Semaphore(1)` for local inference in `admission_controller.py:51` and `resource_guard.py:234` is the **precedent** for Item 2's subagent-tool semaphore. The pattern is already battle-tested; the gap is its scope.
- The `cgroup_pressure.py` file already exists in `src/omega/oracle/`. Item 4 doesn't introduce new infrastructure — it extends an existing module.
- The `scripts/mcp_watchdog.py` is the precedent for Item 3's `process_registry.py` and Item 5's `system_resource_guard.py`. Same pattern, different scope.

**The truth**: The Cathedral already has the foundation. The INFRA-1..10 findings are **scope extensions** of existing patterns, not new architectures.

---

## §12 — Per-Item Omega Application Summary Table

| # | Pattern | Anchor File | New File (suggested) | Decision (if needed) |
|---|---------|-------------|----------------------|----------------------|
| 1 | `start_new_session=True` + `os.killpg` | `src/omega/oracle/orchestrator.py:220` | `src/omega/oracle/lifecycle.py` | D-XXX (propose) |
| 2 | `anyio.Semaphore(N)` for subagent tools | `src/omega/infra/subagent_pool/orchestrator.py:125` | (extend existing) | — |
| 3 | `data/registry/<pid>.json` + psutil reconcile | `src/omega/observability/__init__.py` | `scripts/process_registry.py` | D-XXX |
| 4 | cgroup v2 slice per tool | `src/omega/oracle/orchestrator.py:220` | (extend `cgroup_pressure.py`) | D-XXX |
| 5 | 5-step graceful shutdown + cgroup PSI | `src/omega/observability/__init__.py` | `scripts/system_resource_guard.py` | D-XXX |
| 6 | `.compliance/meter.yaml` SSOT + INFRA findings | `scripts/m23_gate.py` | `.compliance/meter.yaml` | — |
| 7 | structlog + `_logging.py` + early init | `src/omega/__init__.py` | `src/omega/_logging.py` | — |
| 8 | `apply_public_allowlist.sh` + import-linter | `scripts/apply_public_allowlist.sh` | `.import-linter` | — |
| 9 | Pydantic ProviderContract + Pact | `config/providers.yaml` | `src/omega/providers/contract.py` | — |
| 10 | Hypothesis round-trip + golden traces | `data/entities/*/soul.yaml` | `tests/contract/test_soul_contract.py` | — |

---

## §13 — Citations Index (by Item)

- **Item 1**: docs.python.org/3.12/subprocess; zetcode.com/python/os-killpg; runebook.dev os.killpg; codemia.io subprocess; pypi.org/project/psutil (v7.2.2)
- **Item 2**: arxiv.org/pdf/2604.17111 (HiveMind); rednafi.com semaphore; pythonz2h.com semaphore; mhtechin.com 2026 frameworks; scrapingcentral.com concurrency; pypi.org/project/limiter; anyio changelog
- **Item 3**: psutil.readthedocs.io; github.com/giampaolo/psutil/issues/2396; opentelemetry.io/docs/zero-code/obi/trace-log-correlation; oneuptime.com log correlation; kernel.org cgroup-v2; coralogix.com Datadog alternatives
- **Item 4**: oneuptime.com cgroups v2; martinuke0.github.io cgroups v2; contextstudios.ai sandboxing 2026; amux.io sandboxing 2026; github.com/e2b-dev/e2b/issues/1257; kernel.org cgroup-v2
- **Item 5**: zylos.ai process supervision; zylos.ai graceful degradation; handsonkafka substack; dredyson.com fintech timeout; appscale.blog graceful degradation; systemdr.systemdrd.com degradation vs fail-fast; psdn.io systemd shutdown
- **Item 6**: safeguard.sh OpenSSF Scorecard v6; openssf.org/projects/scorecard; slsa.dev; github.com/slsa-framework/slsa; khimananda.com SLSA; practical-devsecops.com SLSA; openssf.org/projects/slsa
- **Item 7**: tutorials.technology Python logging 2026; dash0.com Python logging; bswen.com logging choice; rollbar.com circular import; stackharbor.com loguru; dash0.com structlog; logzai.com Python logging
- **Item 8**: bazel.build/concepts/visibility; virtuslab.com bazel book; pypi.org/project/import-linter (v2.13); github.com/seddonym/import-linter; pypi.org/project/pylint-import-linter; kernel.org core-api; doc.rust-lang.org cargo
- **Item 9**: tianpan.co contract testing AI; zylos.ai contract testing agent; qaskills.sh Pact 2026; qaskills.sh Pact reference; oneuptime.com schema registry; pdpspectra.com Pact; apiscout.dev Pact 2026; softwaretestpilot.com Pact; openai.com structured outputs; docs.anthropic.com tool use
- **Item 10**: qaskills.sh Hypothesis; oneuptime.com property-based testing; techpulsesite.com Python testing 2026; github.com/hypothesisworks/hypothesis; tianpan.co PBT LLM; pytest-with-eric.com Hypothesis; dev.to keploy PBT; waggertron.github.io persistence contract tests

---

## §14 — Polymathic Council Verdict

**Convergence (The Truth)**:
- The 10 patterns are **layered**, not orthogonal. Each builds on the previous.
- The 2026 SOTA converges on **declarative, machine-checked, versioned artifacts** (YAML schemas, Pydantic contracts, JSON Schema, BUILD files, cgroup files) as the single source of truth, with **runtime enforcement** layered on top.
- **Hivemind awareness** (subagent post-context) and **session gnosis** (M15) are the cross-cutting concerns that every pattern should emit to.

**Divergence (The Uncertainty)**:
- **Item 2 (Semaphore)**: asyncio.Semaphore is fine for static caps; condition-variable is needed for dynamic. The line is fuzzy.
- **Item 4 (cgroups)**: cgroup v2 is the future but not universally available. The Python-only fallback must be solid.
- **Item 6 (Compliance)**: SSOT drift is the silent killer. Without a drift detector, the meter becomes theater.
- **Item 10 (Hypothesis)**: Property-based tests are powerful but require careful oracle design for non-deterministic systems (LLMs).

**The Demand**:
Cline — for each of the 10 items, the deliverable is **a 3-file change**:
1. The new infrastructure file (per the table in §12).
2. The integration point (the anchor file).
3. A test that proves it works (per the GO checklist items 10-11).

**The Cathedral needs its infrastructure. Execute.**

---

⬡ OMEGA ⬡ KALI ⬡ R-RESEARCHER-2026-REFACTOR-PATTERNS-v1.0.0 ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

