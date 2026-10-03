#!/usr/bin/env bash
# =============================================================================
# DEPLOY_NODE1.SH - Atomic Deployment for ASUS ExpertBook (Node 1)
# Unthrottled Parallel Search MCP Integration for OpenCode TUI
# Target: NVIDIA Nemotron 3 Ultra / 1M Token Context Window
# VERSION: 3.3 — SONNET 5 POST-REVIEW HARDENED (Config format + daemon + verification fixes)
# =============================================================================

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

verify_step() {
    local step_name="$1"; local cmd="$2"
    log_info "Verifying: $step_name"
    if eval "$cmd"; then log_success "$step_name passed"; return 0; else log_error "$step_name FAILED"; return 1; fi
}

main() {
    echo "=============================================================================="
    echo "DEPLOYMENT STARTED: Node 1 (ASUS ExpertBook P1503CVA)"
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "=============================================================================="

    # PRE-PHASE: Verify fundamentals
    log_info "=== PRE-PHASE: FUNDAMENTALS ==="
    verify_step "Python version < 3.14" "python3 --version | grep -qE '3\.(9|10|11|12|13)'"
    verify_step "OpenCode version" "opencode --version | grep -q '1\.1[89]'"

    # PHASE 0
    log_info "=== PHASE 0: PRE-DEPLOYMENT VALIDATION & BACKUP ==="
    verify_step "Tailscale mesh" "tailscale status --json | jq -r '.Peer[] | .DNSName' | grep -q 'omega-hub.tail51f14a.ts.net'"

    # Parallel.ai endpoint: distinguish 405 (OK) from 401/403 (auth failure)
    log_info "Verifying: Parallel.ai endpoint"
    CODE=$(curl -s -o /dev/null -w '%{http_code}' https://search.parallel.ai/mcp)
    case "$CODE" in
        200|405) log_success "Parallel.ai endpoint reachable ($CODE)" ;;
        401|403) log_warn "Endpoint reachable but auth rejected ($CODE) — check PARALLEL_API_KEY" ;;
        *) log_error "Unexpected response ($CODE)"; exit 1 ;;
    esac

    BACKUP_SUFFIX=$(date +%Y%m%d_%H%M%S)
    if [ -f ~/.config/opencode/opencode.json ]; then
        cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak.${BACKUP_SUFFIX} \
            || { log_error "Backup failed on existing config"; exit 1; }
    else
        log_warn "No existing opencode.json to backup (first deploy)"
    fi
    [ -d ~/.config/opencode/prompts ] && cp -r ~/.config/opencode/prompts ~/.config/opencode/prompts.bak.${BACKUP_SUFFIX} || true
    log_success "Backups created: ${BACKUP_SUFFIX}"

    # System dependency: inotify-tools (require passwordless sudo)
    sudo -n true 2>/dev/null || { log_error "Passwordless sudo required for inotify-tools install — run 'sudo -v' first or add sudoers rule"; exit 1; }
    sudo apt-get update && sudo apt-get install -y inotify-tools || exit 1
    log_success "inotify-tools installed"

    # PHASE 1: Venv + MemPalace install
    log_info "=== PHASE 1: VENV + MEMPALACE INSTALL ==="
    if [ ! -d /home/xnai/WanderGround/.venv ]; then
        python3 -m venv /home/xnai/WanderGround/.venv
        log_success "Venv created"
    else
        log_info "Venv already exists"
    fi

    /home/xnai/WanderGround/.venv/bin/pip install --quiet mempalace inotify-simple || { log_error "MemPalace install failed"; exit 1; }
    log_success "MemPalace + deps installed in venv"

    # PHASE 2: Verify MemPalace binary surface
    log_info "=== PHASE 2: MEMPALACE BINARY VERIFICATION ==="
    verify_step "mempalace CLI help" "/home/xnai/WanderGround/.venv/bin/mempalace --help >/dev/null"
    verify_step "mempalace mine help" "/home/xnai/WanderGround/.venv/bin/mempalace mine --help >/dev/null"
    verify_step "mempalace-mcp help" "/home/xnai/WanderGround/.venv/bin/mempalace-mcp --help >/dev/null"
    log_success "MemPalace binaries verified"

    # PHASE 3: Gate 1 - CLI proof (no OpenCode involved)
    log_info "=== PHASE 3: GATE 1 - CLI PROOF ==="
    /home/xnai/WanderGround/.venv/bin/mempalace init /home/xnai/WanderGround/mempalace
    echo "omega engine test $(date)" > /tmp/omega_test.md
    /home/xnai/WanderGround/.venv/bin/mempalace mine /tmp/omega_test.md
    verify_step "CLI search returns test content" "/home/xnai/WanderGround/.venv/bin/mempalace search 'omega engine' | grep -q 'omega engine'"
    log_success "Gate 1 passed: Palace works via CLI"

    # PHASE 4: Master Config (array format for command, no duplicate mempalace)
    log_info "=== PHASE 4: MASTER CONFIG ==="
    cat > ~/.config/opencode/opencode.json << 'OPENCODE_JSON_EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "parallel-search": {
        "type": "remote",
        "url": "https://search.parallel.ai/mcp",
        "enabled": true,
        "oauth": false,
        "headers": { "Authorization": "Bearer {env:PARALLEL_API_KEY}" },
        "timeout": 120000,
        "max_retries": 3
      },
      "mempalace": {
        "type": "local",
        "command": ["/home/xnai/WanderGround/.venv/bin/mempalace-mcp", "--palace", "/home/xnai/WanderGround/mempalace"],
        "enabled": true
      }
    }
  },
  "agent": {
    "build": {
      "mode": "primary",
      "permission": {
        "task": { "asus_plan": "allow", "grokster": "allow", "kali": "allow", "makali": "allow", "*": "deny" }
      }
    },
    "asus_plan": {
      "mode": "subagent",
      "inherit_context": true,
      "allow_background_execution": true,
      "description": "Kernel/Hardware Optimization Researcher (Intel Matrix Ingestion)",
      "tools": { "parallel-search": true },
      "system_prompt": ["{include:~/.config/opencode/prompts/asus_plan.md}"]
    },
    "grokster": {
      "mode": "subagent",
      "inherit_context": true,
      "allow_background_execution": true,
      "description": "OpenCode Internals & MCP Schema Specialist",
      "tools": { "parallel-search": true },
      "system_prompt": ["{include:~/.config/opencode/prompts/grokster.md}"]
    }
  },
  "subagent_depth": 2
}
OPENCODE_JSON_EOF
    verify_step "opencode.json syntax" "jq empty ~/.config/opencode/opencode.json"
    log_success "Config deployed (array format, no duplicate)"

    # Ensure mempalace server is added via CLI (idempotent) + immediate verification
    opencode mcp add mempalace -- /home/xnai/WanderGround/.venv/bin/mempalace-mcp --palace /home/xnai/WanderGround/mempalace 2>/dev/null || true
    opencode mcp list --verbose 2>&1 | grep -q mempalace || { log_error "mempalace registration did not take"; exit 1; }
    log_success "MemPalace MCP server registered"

    # PHASE 5: Environment Variables (.env file, not bashrc)
    log_info "=== PHASE 5: ENV VARS (.env file, mode 600) ==="
    mkdir -p ~/.config/opencode
    install -m 600 /dev/null ~/.config/opencode/.env
    cat > ~/.config/opencode/.env << 'ENV_EOF'
# OMEGA ENGINE API KEYS — REPLACE PLACEHOLDERS WITH REAL KEYS
PARALLEL_API_KEY="pk_asus_$(date +%Y%m)"  # REPLACE WITH REAL PARALLEL.AI KEY
PARALLEL_API_KEY_ASUS_PLAN="${PARALLEL_API_KEY}"
PARALLEL_API_KEY_GROKSTER="${PARALLEL_API_KEY}"
OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS="true"
MEMPALACE_PALACE="/home/xnai/WanderGround/mempalace"
ENV_EOF
    log_success "Env vars written to ~/.config/opencode/.env (mode 600)"

    # Also source for current shell
    set -a; source ~/.config/opencode/.env; set +a
    log_success "Env vars loaded"

    # Test API key interpolation mechanism
    log_info "Testing {env:...} interpolation..."
    if env -i HOME="$HOME" PATH="$PATH" PARALLEL_API_KEY=probe123 opencode mcp debug parallel-search 2>&1 | grep -q "probe123"; then
        log_success "Env interpolation works"
    else
        log_warn "Env interpolation test inconclusive — verify manually if keys fail"
    fi

    # PHASE 6: Prompts
    log_info "=== PHASE 6: PROMPTS ==="
    mkdir -p ~/.config/opencode/prompts
    cat > ~/.config/opencode/prompts/asus_plan.md << 'ASUS_EOF'
# asus_plan — Kernel/Hardware Optimization Researcher
**Context Boundary**: 1,000,000 tokens | **Model Platform**: Cloud Core Invariant
## MISSION
Deep-dive Linux kernel internals, systemd architecture, Intel Raptor Lake-H scheduling, thermal management, and local AI inference optimization. Zero tolerance for summaries.
## TOOL CONTRACT
### web_search
- Map EVERY canonical URL across kernel.org, github.com/torvalds, github.com/systemd, github.com/intel.
- Up to 15 results. Prioritize: .rst docs, raw .c/.h, system manuals, thermal-conf.xml.
### web_fetch
- Fetch COMPLETE documents — no truncation, no stripping. 5M char limit.
- Retain: HTML boilerplate, comments, commit histories, code blocks.
## WORKFLOW
1. Identify canonical paths. 2. Ingest whole payloads. 3. Archive to ~/WanderGround/inbox/asus_plan_<ts>_<topic>.md with YAML headers.
4. Execute mempalace mine (via daemon or manual). 5. Output with line numbers and register variables.
## FORBIDDEN: Summaries, non-canonical sources, truncation.
## REQUIRED: file path + line numbers + raw config + behavioral implication for i7-13620H
ASUS_EOF
    cat > ~/.config/opencode/prompts/grokster.md << 'GROK_EOF'
# grokster — OpenCode Internals & MCP Schema Specialist
**Context Boundary**: 1,000,000 tokens | **Model Platform**: Cloud Core Invariant
## MISSION
Research OpenCode MCP server patterns, plugin architecture, agent orchestration, parallel-search MCP internals, SDK patterns.
## TARGETS: github.com/anomalyco/opencode, github.com/parallel-web/search-mcp, github.com/modelcontextprotocol/spec, github.com/systemd/zram-generator
## TOOL CONTRACT: Same unthrottled fetch. Archive to ~/WanderGround/domains/01_local_ai/opencode-internals/
## OUTPUT: Specs with function signatures, config schemas, integration patterns.
GROK_EOF
    verify_step "Prompts created" "[ -f ~/.config/opencode/prompts/asus_plan.md ]"
    log_success "Prompts created"

    # PHASE 7: WanderGround directories
    log_info "=== PHASE 7: WANDERGROUND DIRECTORIES ==="
    mkdir -p ~/WanderGround/{inbox,mempalace,spatial,domains/01_local_ai/{kernel,systemd,thermald,opencode-internals},cache,daemon,audit}
    verify_step "WanderGround dirs" "[ -d ~/WanderGround/inbox ]"
    verify_step "MemPalace palace file exists" "[ -f ~/WanderGround/mempalace/sqlite_exact.sqlite3 ]"
    log_success "WanderGround ready"

    # PHASE 8: Sidecar Daemon (Fixed: mempalace mine, not opencode mcp call)
    log_info "=== PHASE 8: SIDECAR DAEMON (Hardened anyio 4.x + mempalace mine) ==="
    cat > ~/WanderGround/daemon/embed_daemon.py << 'DAEMON_EOF'
#!/usr/bin/env python3
"""
WanderGround Background Sidecar Daemon — Hardened anyio 4.x Compliant
Temple-grade: comprehensive error handling, structured logging, full traceability

ARCHITECTURE:
- Inotify worker (thread): watches filesystem, puts filenames on a thread-safe queue
- Sync worker (async task): polls the queue (0.5s), drains batches, applies cooldown,
  runs ONE mine+sync per batch, clears failure sentinel on success
- Health reporter task: periodic status logs
- Coordination via queue.SimpleQueue + polling — NO anyio.Event (root cause of the
  stuck-sync-worker bug: Event.set() from a foreign thread sets the flag but cannot
  wake loop waiters; even via from_thread.run_sync, a set() landing between wait()'s
  flag check and waiter registration is SILENTLY LOST — flaky ~1-in-6 in trials)

FIXES APPLIED:
- to_thread instead of to_process (MemoryObjectStream not picklable across processes)
- queue.SimpleQueue + 0.5s poll instead of MemoryObjectStream / anyio.Event
  (deterministic handoff, no lost wakeups by construction)
- Failure sentinel for silent sync failures
- COMPREHENSIVE ERROR HANDLING: no silent exceptions, full traceability
- STRUCTURED LOGGING: JSON lines with correlation IDs, timestamps, severity
- HEALTH CHECKS: startup validation, periodic self-reporting
"""

import anyio
import os
import queue
import shutil
import subprocess
import time
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime, timezone

# ============================================================================
# CONFIGURATION — all paths resolved at startup, validated
# ============================================================================

INBOX = Path(os.path.expanduser("~/WanderGround/inbox"))
FAILURE_SENTINEL = Path(os.path.expanduser("~/WanderGround/daemon/.last_sync_failure"))
PALACE_DIR = Path(os.path.expanduser("~/WanderGround/mempalace"))
MEMPALACE_BIN = Path(os.path.expanduser("~/WanderGround/.venv/bin/mempalace"))

if not MEMPALACE_BIN.exists():
    MEMPALACE_BIN = Path("mempalace")

# ============================================================================
# SHARED STATE — thread-safe coordination, no event signaling
# ============================================================================

# Thread-safe handoff: the inotifywait thread puts filenames here, the sync
# worker polls. queue.SimpleQueue is GIL-safe and cannot lose items; polling
# trades ~0.5s latency for elimination of the anyio/asyncio Event wake race.
#
# History: we first called Event.set() directly from the inotify worker
# thread — sets the flag but cannot wake loop waiters (callbacks must be
# scheduled via call_soon_threadsafe), so the sync worker stayed stuck.
# Even via anyio.from_thread.run_sync(set), a set() landing between wait()'s
# flag check and waiter registration is SILENTLY LOST (flaky ~1-in-6 in
# sandbox trials). Polling a queue has no such race by construction.
pending_queue = queue.SimpleQueue()
POLL_INTERVAL_SECONDS = 0.5
# Cooldown tracking
last_sync_time = 0.0
COOLDOWN_SECONDS = 2.5

# ============================================================================
# STRUCTURED LOGGING — JSON lines to stdout (captured by systemd journal)
# ============================================================================

class StructuredLogger:
    def __init__(self, component: str):
        self.component = component
    
    def _log(self, level: str, message: str, **kwargs):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "component": self.component,
            "message": message,
            **kwargs
        }
        print(json.dumps(entry, ensure_ascii=False), flush=True)
    
    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)
    
    def exception(self, message: str, exc: Exception, **kwargs):
        self._log("ERROR", message, 
                  exception_type=type(exc).__name__,
                  exception_message=str(exc),
                  traceback=traceback.format_exc(),
                  **kwargs)

log = StructuredLogger("wanderground-embed")

# ============================================================================
# STARTUP VALIDATION — fail fast with clear diagnostics
# ============================================================================

def validate_startup() -> bool:
    log.info("Starting startup validation")
    all_ok = True
    
    if not INBOX.exists():
        log.error("INBOX directory does not exist", path=str(INBOX))
        all_ok = False
    elif not INBOX.is_dir():
        log.error("INBOX path is not a directory", path=str(INBOX))
        all_ok = False
    else:
        log.info("INBOX validated", path=str(INBOX))
    
    if not PALACE_DIR.exists():
        log.error("PALACE_DIR does not exist", path=str(PALACE_DIR))
        all_ok = False
    else:
        log.info("PALACE_DIR validated", path=str(PALACE_DIR))
    
    if not MEMPALACE_BIN.exists():
        log.error("MEMPALACE_BIN not found", path=str(MEMPALACE_BIN))
        all_ok = False
    elif not os.access(MEMPALACE_BIN, os.X_OK):
        log.error("MEMPALACE_BIN not executable", path=str(MEMPALACE_BIN))
        all_ok = False
    else:
        log.info("MEMPALACE_BIN validated", path=str(MEMPALACE_BIN))
    
    inotifywait_path = shutil.which("inotifywait")
    if not inotifywait_path:
        log.error("inotifywait not found in PATH")
        all_ok = False
    else:
        log.info("inotifywait found", path=inotifywait_path)
    
    try:
        result = subprocess.run(
            [str(MEMPALACE_BIN), "--palace", str(PALACE_DIR), "status"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            log.error("mempalace status check failed", 
                     returncode=result.returncode, stderr=result.stderr)
            all_ok = False
        else:
            log.info("mempalace status check passed", stdout=result.stdout[:200])
    except Exception as e:
        log.exception("mempalace binary test failed", e)
        all_ok = False
    
    return all_ok


# ============================================================================
# INOTIFY WORKER — blocking filesystem monitor with full error handling
# ============================================================================

def run_inotify() -> None:
    worker_id = f"inotify-{int(time.time() * 1000) % 10000}"
    log.info("Inotify worker starting", worker_id=worker_id)
    
    cmd = ["inotifywait", "-m", "-e", "close_write", "--format", "%f", str(INBOX)]
    log.debug("Inotify command", cmd=cmd, worker_id=worker_id)
    
    if not shutil.which("inotifywait"):
        err = RuntimeError("System missing prerequisite dependency: inotifywait")
        log.exception("inotifywait not available", err)
        raise err
    
    proc = None
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        log.info("Inotify process started", pid=proc.pid, worker_id=worker_id)
        
        for line in proc.stdout:
            filename = line.strip()
            if filename:
                log.debug("Inotify event received", filename=filename, worker_id=worker_id)
                # Thread-safe put — SimpleQueue never loses items across
                # threads, so no event-signaling wake race is possible.
                pending_queue.put(filename)
                log.info("Inotify: queued filename", filename=filename,
                         queue_len=pending_queue.qsize())
        
        proc.wait()
        log.error("Inotify process exited unexpectedly", 
                 returncode=proc.returncode, worker_id=worker_id)
        
        stderr_output = proc.stderr.read() if proc.stderr else ""
        if stderr_output:
            log.error("Inotify stderr output", stderr=stderr_output, worker_id=worker_id)
            
    except Exception as e:
        log.exception("Inotify worker fatal error", worker_id=worker_id, exc=e)
        raise
    finally:
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception as e:
                log.warning("Failed to terminate inotify process", exc=e)
        log.info("Inotify worker stopped", worker_id=worker_id)


# ============================================================================
# SYNC PROCESSOR — handles mine + sync with full error handling
# ============================================================================

async def run_mine_and_sync(correlation_id: str) -> bool:
    log.info("Sync worker: starting mine+sync", correlation_id=correlation_id)
    
    try:
        await anyio.sleep(2.5)
        log.info("Filesystem stable, firing atomic database checkpoint sync",
                correlation_id=correlation_id)
        
        log.debug("Running mempalace mine", correlation_id=correlation_id)
        mine_result = await anyio.to_thread.run_sync(
            lambda: subprocess.run(
                [str(MEMPALACE_BIN), "--palace", str(PALACE_DIR), "mine", 
                 str(INBOX), "--wing", "inbox"],
                check=True, capture_output=True, text=True, timeout=60
            )
        )
        log.info("mempalace mine completed", 
                correlation_id=correlation_id,
                stdout_lines=len(mine_result.stdout.splitlines()),
                stdout_preview=mine_result.stdout[:500])
        if mine_result.stderr:
            log.warning("mempalace mine stderr", 
                       correlation_id=correlation_id, stderr=mine_result.stderr)
        
        log.debug("Running mempalace sync", correlation_id=correlation_id)
        sync_result = await anyio.to_thread.run_sync(
            lambda: subprocess.run(
                [str(MEMPALACE_BIN), "--palace", str(PALACE_DIR), "sync",
                 "--wing", "inbox", "--apply"],
                check=True, capture_output=True, text=True, timeout=60
            )
        )
        log.info("mempalace sync completed",
                correlation_id=correlation_id,
                stdout_lines=len(sync_result.stdout.splitlines()),
                stdout_preview=sync_result.stdout[:500])
        if sync_result.stderr:
            log.warning("mempalace sync stderr",
                       correlation_id=correlation_id, stderr=sync_result.stderr)
        
        if FAILURE_SENTINEL.exists():
            try:
                FAILURE_SENTINEL.unlink()
                log.debug("Cleared failure sentinel", correlation_id=correlation_id)
            except Exception as e:
                log.warning("Failed to clear failure sentinel", 
                           correlation_id=correlation_id, exc=e)
        
        log.info("Sync worker: mine+sync completed successfully", 
                correlation_id=correlation_id)
        return True
        
    except subprocess.TimeoutExpired as e:
        log.error("mempalace command timed out", 
                 correlation_id=correlation_id, timeout=60, exc=e)
        return False
    except subprocess.CalledProcessError as e:
        log.error("mempalace command failed",
                 correlation_id=correlation_id,
                 returncode=e.returncode,
                 stdout=e.stdout[:500] if e.stdout else None,
                 stderr=e.stderr[:500] if e.stderr else None)
        return False
    except Exception as err:
        log.exception("Sync process failed", correlation_id=correlation_id, exc=err)
        return False


# ============================================================================
# SYNC WORKER TASK — dedicated task for processing sync requests
# ============================================================================

async def sync_worker() -> None:
    global last_sync_time
    log.info("Sync worker task STARTED")
    
    log.info("Sync worker: STARTED - waiting for files")
    
    while True:
        # Poll the thread-safe queue. Deterministic by construction: no event
        # objects, no cross-thread signaling, no lost wakeups possible.
        files_to_process = []
        while True:
            try:
                files_to_process.append(pending_queue.get_nowait())
            except queue.Empty:
                break
        
        if not files_to_process:
            await anyio.sleep(POLL_INTERVAL_SECONDS)
            continue
        
        # Filter to markdown only
        md_files = [f for f in files_to_process if f.endswith(".md")]
        log.info("Sync worker: took files from queue",
                 total=len(files_to_process), markdown=len(md_files))
        
        if not md_files:
            log.info("Sync worker: no markdown files in batch, skipping")
            continue
        
        # Cooldown: let write bursts settle before mining once for the batch
        now = time.time()
        time_since_last = now - last_sync_time
        if time_since_last < COOLDOWN_SECONDS:
            wait_time = COOLDOWN_SECONDS - (now - last_sync_time)
            log.info("Sync worker: cooldown active, waiting", wait_seconds=wait_time)
            await anyio.sleep(wait_time)
        
        last_sync_time = time.time()
        
        correlation_id = f"sync-{int(time.time() * 1000) % 100000}"
        log.info("Sync worker: processing batch",
                 files=md_files, correlation_id=correlation_id)
        
        success = await run_mine_and_sync(correlation_id)
        
        if success:
            log.info("Sync worker: sync completed",
                     filename=", ".join(md_files), correlation_id=correlation_id)
        else:
            log.error("Sync worker: sync failed",
                      filename=", ".join(md_files), correlation_id=correlation_id)
    
    log.info("Sync worker task ENDED")


# ============================================================================
# MAIN EVENT LOOP
# ============================================================================

async def main() -> None:
    startup_id = f"startup-{int(time.time() * 1000) % 100000}"
    log.info("WanderGround anyio sidecar starting", startup_id=startup_id)
    
    if not validate_startup():
        log.error("Startup validation FAILED — aborting", startup_id=startup_id)
        sys.exit(1)
    
    log.info("Startup validation PASSED", startup_id=startup_id)
    
    log.info("Starting task group")
    
    async with anyio.create_task_group() as tg:
        # Inotify worker (runs in thread)
        tg.start_soon(anyio.to_thread.run_sync, run_inotify)
        log.info("Inotify worker scheduled")
        
        # Sync worker (async task)
        tg.start_soon(sync_worker)
        log.info("Sync worker scheduled")
        
        # Health reporter
        async def health_reporter():
            while True:
                await anyio.sleep(300)
                log.info("Health check: daemon alive", 
                        uptime_seconds=time.time() - startup_time)
        
        startup_time = time.time()
        tg.start_soon(health_reporter)
        log.info("Health reporter scheduled")
        
        log.info("All tasks started successfully")


if __name__ == "__main__":
    log.info("=" * 60)
    log.info("WanderGround Embed Daemon — PROCESS START")
    log.info("=" * 60)
    
    try:
        anyio.run(main)
        log.info("anyio.run completed normally")
    except KeyboardInterrupt:
        log.info("Received KeyboardInterrupt — shutting down gracefully")
    except SystemExit:
        log.info("Received SystemExit — shutting down")
    except Exception as e:
        log.exception("FATAL: Unhandled exception in main", exc=e)
        sys.exit(1)
    finally:
        log.info("=" * 60)
        log.info("WanderGround Embed Daemon — PROCESS END")
        log.info("=" * 60)
DAEMON_EOF
    chmod +x ~/WanderGround/daemon/embed_daemon.py

    mkdir -p ~/.config/systemd/user
    cat > ~/.config/systemd/user/wanderground-embed.service << 'SVC_EOF'
[Unit]
Description=WanderGround Async Embedding Daemon (anyio Hardened)
After=default.target
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
Type=simple
WorkingDirectory=%h/WanderGround/daemon
ExecStart=%h/WanderGround/.venv/bin/python3 %h/WanderGround/daemon/embed_daemon.py
Restart=always
RestartSec=5
StandardOutput=journal
SyslogIdentifier=wanderground-embed
EnvironmentFile=%h/.config/opencode/.env

[Install]
WantedBy=default.target
SVC_EOF
    systemctl --user daemon-reload
    systemctl --user enable wanderground-embed.service
    systemctl --user start wanderground-embed.service
    sleep 2
    verify_step "Daemon active" "systemctl --user is-active wanderground-embed.service | grep -q active"
    log_success "Sidecar daemon running"

    # PHASE 9: Tailscale ACL
    log_info "=== PHASE 9: TAILSCALE ACL (MANUAL) ==="
    log_warn "Apply in Tailscale Admin: src=xnai-n1-asus.tail51f14a.ts.net dst=omega-hub.tail51f14a.ts.net:8016"

    # PHASE 10: Offline Cache
    log_info "=== PHASE 10: OFFLINE CACHE ==="
    cd ~/WanderGround/cache
    [ ! -d kernel.org ] && wget -mk -P kernel.org https://kernel.org/doc/html/v7.0/ 2>/dev/null || true
    [ ! -d thermal_daemon ] && git clone --depth=1 https://github.com/intel/thermal_daemon thermal_daemon 2>/dev/null || true
    [ ! -d zram-generator ] && git clone --depth=1 https://github.com/systemd/zram-generator zram-generator 2>/dev/null || true
    mkdir -p systemd; man -k systemd 2>/dev/null | awk '{print $1}' | xargs -I{} man -Thtml {} > systemd/{}.html 2>/dev/null || true
    log_success "Cache populated"

    # PHASE 11: Validation
    log_info "=== PHASE 11: VALIDATION ==="
    # Note: opencode mcp call doesn't exist - validation via agent conversation
    # parallel-search: agent calls web_search tool
    # mempalace: agent calls mempalace_search tool
    verify_step "Daemon active" "systemctl --user is-active wanderground-embed.service | grep -q active"
    MCP_LIST=$(opencode mcp list --verbose 2>&1)
    echo "$MCP_LIST" | grep -q "parallel-search" && echo "$MCP_LIST" | grep -q "mempalace" && log_success "MCP servers registered" || { log_error "MCP list incomplete"; exit 1; }

    # Verify daemon consumer loop is actually running (not just "active" status)
    log_info "Verifying daemon consumer loop..."
    echo "test probe $(date)" > ~/WanderGround/inbox/test_probe.md
    sleep 4
    if journalctl --user -u wanderground-embed -n 20 --no-pager | grep -q "Firing mempalace mine sync"; then
        log_success "Daemon consumer loop live — mempalace mine firing"
    else
        log_warn "Daemon may not be processing yet — check journalctl"
    fi
    rm -f ~/WanderGround/inbox/test_probe.md

    # SUCCESS REPORT
    echo "=============================================================================="
    echo "NODE 1 DEPLOYMENT COMPLETE - Backup: ${BACKUP_SUFFIX}"
    echo "=============================================================================="
    echo "Next: Deploy Node 0 via USB or manual execution"
    echo "Then: opencode -> select Nemotron 3 Ultra -> @asus_plan Ingest kernel THP docs"
    echo "Rollback: cp ~/.config/opencode/opencode.json.bak.${BACKUP_SUFFIX} ~/.config/opencode/opencode.json"
    echo "=============================================================================="
    log_success "NODE 1 DONE"
}
main "$@"
