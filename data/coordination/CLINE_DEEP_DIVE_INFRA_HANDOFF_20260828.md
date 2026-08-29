---
schema_version: "2.0"
document_type: "deep_dive_handoff"
document_id: "cline-enhanced-deep-dive-infra-20260828"
title: "Cline CLI — Enhanced Deep Dive: Infrastructure & Process Lifecycle (What Cline Round 1 Missed)"
status: "ACTIVE — PRIORITY 0"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
---

# 🔱 Cline CLI — Enhanced Deep Dive: Infrastructure & Process Lifecycle
**AP Token**: `AP-CLINE-DEEP-DIVE-INFRA-20260828-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_alpha_launch �️ DEEP-EXECUTED

**Date**: 2026-08-28
**From**: Kali (Sprint Coordinator) + Grokster (Cross-Platform Specialist)
**To**: Cline CLI (interactive session, your terminal)
**Context**: Cline Round 1 (`CLINE_FULL_REVIEW_ROLLUP_20260828.md`) found 4 P0s, 10 P1s, 12 P2s. **All 26 findings are CODE-level.** During the Architect's pre-compaction review, we discovered a **5th class of P0 that Round 1 missed: infrastructure & process lifecycle**. This is the enhanced deep dive.

---

## §0 — WHY THIS DEEP DIVE EXISTS

### The Incident (2026-08-28, ~22:45 UTC)

The Architect requested 3 expert sessions to verify Round 1's findings. I (Grokster) dispatched Carmack, Roc, and Researcher in parallel. The Architect interrupted Carmack mid-execution (which terminated a `gitleaks` scan over 904 commits). After OpenCode exited, **CPU stayed at 100% on all 16 cores for many minutes**. A `ps` audit revealed:

- **46 leaked Python processes** (24× `check_mandate_compliance.py`, 8× `verify_mandate_claims.py`, 5× `firewall_checker.py`, 5× `m23_gate.py`, 3× `validate_llm_docs.py`, 1× `ruff`)
- **System load average: 23-27** on a 16-core machine (load > core count = thrashing)
- **Memory: 7.2GB used / 14GB total** (within budget, but pressure was real)
- **gitleaks**: NOT running (Architect killed it), but its child processes were

### The Root Cause

When subagent sessions are **cancelled** (not gracefully shut down), the Python child processes they spawned are **orphaned to PID 1**. The OpenCode process exits, but the children don't. There is **no process supervision, no process registry, no cleanup hook, and no resource cap** for subagent tool execution.

### Why Round 1 Missed This

Cline's review used the **8-account partition (ARC/QUAL/SEC/PERF/TEST/DOCS/MAND/DEBR)**. None of these dimensions naturally cover:
- **Process lifecycle** (belongs in INFRA, not in the 8 dimensions)
- **Resource management** (CPU/memory/IO caps)
- **Concurrency control** (max parallel subagents)
- **Observability** (metrics, alerting, dashboards)
- **Clean shutdown** (atexit, signal handlers, process groups)

The Round 1 checklist's 86 items are all **static** (file:line checks). None measure **dynamic** behavior (what happens when 3 subagents run in parallel, each spawning 5+ Python processes).

---

## §1 — THE GAPS ROUND 1 MISSED (10 P0 Infrastructure Findings)

### INFRA-1 [P0] Process Leak on Subagent Cancellation
**Evidence (live, 2026-08-28 22:45)**:
```
$ ps aux | grep python | grep -v mcp | grep -v opencode | wc -l
46
$ ps -eo comm,args | grep python | sort | uniq -c | sort -rn | head
24 scripts/check_mandate_compliance.py
 8 scripts/verify_mandate_claims.py
 5 scripts/m23_gate.py
 3 src/omega/audit/firewall_checker.py
 3 scripts/validate_llm_docs.py
 1 .venv/bin/ruff check src/omega
```
**Root cause**: When `task()` is cancelled, OpenCode sends SIGTERM to the subagent process but NOT to its child processes. The children become orphans reparented to PID 1.
**Impact**: System resource exhaustion, OOM risk, battery drain on laptops.
**Owner**: Cline (infra fix)
**Action**: Implement process group cleanup (setpgid + killpg on cancel).

### INFRA-2 [P0] No Concurrency Limit on Subagent Tools
**Evidence**: Round 1's "8-account partition" assumed parallelism. In practice, when 3+ subagents dispatch `bash` or `task` tools simultaneously, each spawns multiple Python processes. No semaphore, no rate limit.
**Existing code**: `src/omega/oracle/admission_controller.py` and `src/omega/oracle/resource_guard.py` implement `Semaphore(1)` for **local inference**. But this is **not applied to subagent tool dispatch**.
**Impact**: 3 subagents × 5 tools each = 15 concurrent processes minimum. With gitleaks-style long-running tools, 16-core saturation in <30 seconds.
**Owner**: Cline (infra fix)
**Action**: Apply admission controller to subagent tool dispatch, with `Semaphore(N)` where N = floor(cores / 2).

### INFRA-3 [P0] No Process Registry (Can't Track Orphans)
**Evidence**: When processes leak, we can't tell which subagent session they belong to. `ps` shows the command but not the parent session.
**Existing code**: `src/omega/observability/__init__.py` has signal handlers for death markers, but no **birth registry**.
**Impact**: When the Architect asks "what's eating my CPU?", the answer requires manual correlation.
**Owner**: Cline (infra fix)
**Action**: Create `scripts/process_registry.py` that tracks (pid, ppid, session_id, start_time, command) for every process spawned by a subagent.

### INFRA-4 [P0] MCP Watchdog Doesn't Monitor Subagent Tools
**Evidence**: `scripts/mcp_watchdog.py` exists and monitors MCP server health. It does NOT monitor:
- Subagent tool processes (`bash`, `read`, `write`, `task`, `webfetch`, etc.)
- Python processes spawned by `bash` tool
- Long-running tools like `gitleaks` or `find`
**Impact**: A subagent can spawn 100+ processes and the watchdog is blind to it.
**Owner**: Cline (infra fix)
**Action**: Extend `mcp_watchdog.py` to poll `ps` for child processes and enforce limits.

### INFRA-5 [P0] No Resource Caps on Tool Execution
**Evidence**: `gitleaks` scanned 904 commits across 16 cores with no rate limit. A single `bash` tool invocation with `find /` would do the same.
**Existing code**: `src/omega/oracle/oom_protector.py` exists for local inference OOM protection. Not applied to tools.
**Impact**: One subagent can DoS the entire system.
**Owner**: Cline (infra fix)
**Action**: Add per-tool resource caps: max CPU%, max memory MB, max wall-clock seconds, max child processes.

### INFRA-6 [P0] No Clean Shutdown for OpenCode on Resource Exhaustion
**Evidence**: When the system was at load 27, OpenCode kept running. There was no watchdog that says "if load > 20 for >60s, gracefully shutdown OpenCode to prevent data loss".
**Impact**: Potential data loss, corrupted state files, half-written commits.
**Owner**: Cline (infra fix)
**Action**: Add `scripts/system_resource_guard.py` that monitors load/memory and triggers graceful shutdown.

### INFRA-7 [P0] No Metrics/Alerting for Subagent Resource Usage
**Evidence**: `src/omega/observability/` has `metrics_db.py`, `latency_tracker.py`, `otel_exporter.py`. None of these track per-subagent CPU/memory/process count.
**Impact**: We can only detect resource exhaustion AFTER it happens, not before.
**Owner**: Cline (infra fix)
**Action**: Add per-subagent metrics: cpu_seconds, peak_memory_mb, child_process_count, tool_invocation_count.

### INFRA-8 [P0] No Retry/Backoff for Failed Tool Invocations
**Evidence**: When `python3 scripts/check_mandate_compliance.py` fails, the subagent retries immediately. No exponential backoff. If 3 subagents all retry, that's 9 concurrent invocations.
**Impact**: Cascading failures amplify into resource exhaustion.
**Owner**: Cline (infra fix)
**Action**: Add per-tool retry policy: max_retries, backoff_factor, jitter.

### INFRA-9 [P0] No Session-to-Process Mapping for Forensics
**Evidence**: When a process leaks, we can't answer "which subagent session spawned this?". The `data/knowledge/HALL_OF_RECORDS/` tracks sessions but not their child processes.
**Impact**: Post-incident forensics is impossible.
**Owner**: Cline (infra fix)
**Action**: Add `pid` field to session metadata at process spawn time.

### INFRA-10 [P0] No CPU Affinity / NUMA Awareness
**Evidence**: Ryzen 7 5700U is 2 CCX × 4 cores with separate L3 caches. Running gitleaks on all 16 threads means cross-CCX cache thrashing. Optimal: bind to one CCX (4 threads).
**Impact**: 2-3× slowdown on cache-sensitive workloads, plus higher power draw.
**Owner**: Cline (infra fix)
**Action**: Add `taskset` affinity to long-running tools, or document the optimal invocation pattern.

---

## §2 — THE ENHANCED 8-ACCOUNT PARTITION (Infra-Aware)

Cline, for this enhanced deep dive, use the **same 8-account partition** but add a **9th dimension: INFRA**. If you only have 8 accounts, fold INFRA into DEBR (they both deal with "what's wrong with the system").

| Acct | Dimension | What's NEW vs Round 1 | Owns | Symbol |
|------|-----------|----------------------|------|--------|
| 1 | Architecture & Design | + Process lifecycle architecture | ARC-01..10, INFRA-1, INFRA-3 | `ARC` |
| 2 | Code Quality (M1/M23/M7/types) | + Cleanup hook code | QUAL-01..11, INFRA-8, INFRA-9 | `QUAL` |
| 3 | Security & Secrets | (unchanged) | SEC-01..10 | `SEC` |
| 4 | Performance & Concurrency | + Process limits, CPU affinity | PERF-01..10, INFRA-2, INFRA-5, INFRA-10 | `PERF` |
| 5 | Testing & M13 Temple-Grade | + Load tests | TEST-01..10 | `TEST` |
| 6 | Docs, Heritage (M14), M26, M27 | + Infra docs | DOCS-01..10 | `DOCS` |
| 7 | Sovereign Mandates (27-row) | + INFRA mandate proposal | MAND-01..10, INFRA-7 | `MAND` |
| 8 | Debris/Tech Debt + API/CLI + Build/Release | + Process registry | DEBR-01..17, INFRA-4, INFRA-6 | `DEBR` |

---

## §3 — EXECUTION PROTOCOL (Critical — Read Before Starting)

### 3.1 Pre-Flight: Workspace Lock
Before dispatching any infra-related work, acquire a workspace lock:
```bash
# Check if locked
ls data/coordination/locks/infra.lock 2>/dev/null
# If not, claim it
touch data/coordination/locks/infra.lock
echo "$(date -u) - Cline CLI" > data/coordination/locks/infra.lock
```

### 3.2 Use Primed Sessions (Not New Ones)
Per L3-ResumeEstablishesSessionsTransientsDoNot, RESUME existing sessions:
- Carmack: `ses_6eeead51dd20` (last run 2026-08-28 18:06)
- Researcher: `ses_researcher_glm53_flash_20260828` (last run 2026-08-28 16:55)
- Roc: `ses_20260828_roc_racoon_knowledge_integration` (last run 2026-08-28 18:08)

### 3.3 Resource Caps on YOUR Investigation
When you run tools, set limits:
```bash
# Limit to 4 cores (one CCX on Ryzen 5700U)
taskset -c 0-3 gitleaks detect --no-git -s . -f json --max-target-mb 100

# Limit wall-clock to 5 minutes per investigation
timeout 300 gitleaks detect ...

# Limit memory
ulimit -v 2097152  # 2GB
```

### 3.4 After Each Investigation
Kill any child processes YOU spawned:
```bash
# List your children
ps -eo pid,ppid,comm | awk -v me=$$ '$2 == me'
# Kill them
pkill -P $$
```

---

## §4 — EXECUTION ORDER (~45-60 min wall-clock)

### Wave 0: Setup (2 min)
1. Acquire workspace lock
2. Read this document fully
3. Read `CLINE_FULL_REVIEW_ROLLUP_20260828.md` for context

### Wave 1: Parallel Investigations (30 min, all 8 accounts start)
Each account runs their checks, produces output in the spec'd format:
```
[DIM-NN] PASS|FAIL|SKIP  file:line  evidence  remediation_hint
```

#### ARC Account (Architecture)
- ARC-01..10 (unchanged from Round 1)
- **NEW INFRA-1**: Trace process lifecycle: where are children spawned? Where should they be cleaned?
- **NEW INFRA-3**: Design process registry schema (pid, ppid, session_id, start_time, command, status)

#### QUAL Account (Code Quality)
- QUAL-01..11 (unchanged)
- **NEW INFRA-8**: Find all `except` blocks in `src/omega/` that could hide retry storms
- **NEW INFRA-9**: Find all `subprocess.run`/`Popen` calls and check for missing timeout/capture

#### PERF Account (Performance)
- PERF-01..10 (unchanged)
- **NEW INFRA-2**: Verify admission controller is NOT applied to subagent tools (it should be)
- **NEW INFRA-5**: Find all tools that could DoS (long-running, high-CPU, no limits)
- **NEW INFRA-10**: Test gitleaks with `taskset -c 0-3` vs default — measure speedup

#### DEBR Account (Tech Debt)
- DEBR-01..17 (unchanged)
- **NEW INFRA-4**: Audit `scripts/mcp_watchdog.py` for subagent coverage gaps
- **NEW INFRA-6**: Design graceful shutdown triggers (load > 20 for 60s → shutdown)

#### MAND Account (Mandates)
- MAND-01..10 (unchanged)
- **NEW INFRA-7**: Propose new mandate: M28 Process Lifecycle Integrity

#### TEST/DOCS/SEC Accounts
- Unchanged from Round 1, but add **stress test** for 5 parallel subagents and verify no resource exhaustion

### Wave 2: Synthesis (15 min)
1. Collect all 8 outputs
2. Write `data/coordination/CLINE_DEEP_DIVE_INFRA_ROLLUP_20260828.md`
3. Append INFRA-1..10 to the original P0/P1/P2 lists
4. Update the 9-item GO checklist to include INFRA items

### Wave 3: Commit (3 min)
```bash
git add data/coordination/CLINE_DEEP_DIVE_INFRA_ROLLUP_20260828.md
git commit -m "infra(audit): enhanced deep dive — 10 P0 process-lifecycle findings, INFRA-1..10 spec'd"
git push origin release/debut
```

---

## §5 — OUTPUT FORMAT (strict)

Every check, every account:
```
[DIM-NN] PASS|FAIL|SKIP  file:line  evidence  remediation_hint
```

Append per-account summary:
```
ACCT X: P0=… P1=… P2=… INFRA-P0=… INFRA-P1=… INFRA-P2=…  TOTAL=…
```

---

## §6 — ANTI-PATTERNS TO REJECT (Round 1 + New)

### From Round 1 (still apply)
- "This could be more Pythonic." (aesthetic)
- "Why not use library X?" (without measuring)
- "I would have designed this differently." (not a defect)
- Any item not backed by `file:line` or command output

### New for INFRA
- "We can fix this later." (P0 process leak = data loss risk = launch blocker)
- "Just kill the processes manually." (doesn't scale, doesn't prevent)
- "OpenCode should handle this." (it's OUR harness, OUR responsibility)
- "This is a Linux problem, not an Omega problem." (it happened IN our session)

---

## §7 — THE 9-ITEM GO CHECKLIST (Updated)

Round 1's checklist + 2 new INFRA items:
1. Secret history scrubbed (`git log -S GOCSPX- --all | wc -l` → 0)
2. Engine's own secret gate green (`make gate-secrets` → exit 0)
3. Compliance meter green AND gating (`make check-mandates` → exit 0)
4. Allowlist conformant (`bash scripts/apply_public_allowlist.sh --summary` → Removed: 0)
5. Lint clean (`make lint` → exit 0)
6. Contract suite green (`pytest tests/contract -q` → 0 failures)
7. Temple-grade real (`make temple-grade` → exit 0, ≥8 real gates)
8. Fresh-venv import (D-539/CP-3) → exit 0
9. Focused runtime smoke (`omega --help && omega list-entities` → exit 0)
10. **NEW: Process leak test** — dispatch 3 parallel subagents, cancel all, verify 0 orphan Python processes
11. **NEW: Resource cap test** — dispatch a `gitleaks` scan, verify it respects `--max-cpu 50` and `--max-mem 2GB`

---

## §8 — FILES TO READ FIRST

1. `data/coordination/CLINE_FULL_REVIEW_ROLLUP_20260828.md` — Round 1 deliverable
2. `data/coordination/CLINE_FULL_REPO_REVIEW_HANDOFF_20260828.md` — Round 1 handoff
3. `data/coordination/CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md` — 86-check baseline
4. `data/entities/grokster/session_gnosis.md` — continuity anchor
5. `src/omega/oracle/admission_controller.py` — existing Semaphore(1) for local inference
6. `src/omega/oracle/resource_guard.py` — existing concurrency protection
7. `scripts/mcp_watchdog.py` — existing watchdog to extend
8. `src/omega/observability/__init__.py` — existing signal handlers

---

## §9 — THE GIFT IS THE DEMAND (Round 2)

Cline — Round 1 gave us the Cathedral's code. Round 2 gives us the Cathedral's **operational integrity**.

The code is 74% compliant. The infrastructure is 0% supervised. A Cathedral without process supervision is a Cathedral that DoS's itself.

**You have DeepSeek 1M context. You have the 8-account partition. You have the INFRA-1..10 spec. You have 45-60 minutes.**

**Execute the enhanced deep dive. Catch what Round 1 missed. Roll up the findings. Cut the alpha launch.**

**The community is waiting. The Cathedral needs its infrastructure.**

⬡ OMEGA ⬡ KALI ⬡ CLINE-DEEP-DIVE-INFRA-READY ⬡ 2026-08-28
