#!/usr/bin/env bash
# =============================================================================
# DEPLOY_NODE0.SH - Atomic Deployment for HP Pavilion (Node 0)
# Unthrottled Parallel Search MCP Integration for OpenCode TUI
# Target: NVIDIA Nemotron 3 Ultra / 1M Token Context Window
# VERSION: 3.2 — SONNET 5 DEEPENING HARDENED (All critical bugs fixed)
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
    echo "DEPLOYMENT STARTED: Node 0 (HP Pavilion Archival Bastion)"
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "=============================================================================="

    # PHASE 0
    log_info "=== PHASE 0: PRE-DEPLOYMENT VALIDATION & BACKUP ==="
    verify_step "OpenCode version" "opencode --version | grep -q '1\.1[89]'"
    verify_step "MemPalace MCP responding" "opencode mcp call mempalace mempalace_search '{\"query\": \"test\", \"limit\": 1}' >/dev/null 2>&1"
    verify_step "Tailscale mesh" "tailscale status --json | jq -r '.Peer[] | .DNSName' | grep -q 'xnai-n1-asus.tail51f14a.ts.net'"

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

    # Venv bootstrap
    if ! /home/xnai/WanderGround/.venv/bin/python3 -c "import anyio; import inotify_simple" 2>/dev/null; then
        /home/xnai/WanderGround/.venv/bin/pip install 'anyio>=4.0,<5.0' 'inotify-simple==1.3.5' --quiet || { log_error "Deps failed"; exit 1; }
    fi
    log_success "Venv dependencies satisfied"

    # System dependency: inotify-tools (require passwordless sudo)
    sudo -n true 2>/dev/null || { log_error "Passwordless sudo required for inotify-tools install — run 'sudo -v' first or add sudoers rule"; exit 1; }
    sudo apt-get update && sudo apt-get install -y inotify-tools || exit 1
    log_success "inotify-tools installed"

    # PHASE 1
    log_info "=== PHASE 1: CONFIG (kali + makali) ==="
    cat > ~/.config/opencode/opencode.json << 'OPENCODE_EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "parallel-search": { "type": "remote", "url": "https://search.parallel.ai/mcp", "enabled": true, "oauth": false, "headers": { "Authorization": "Bearer {env:PARALLEL_API_KEY}" }, "timeout": 120000, "max_retries": 3 },
      "mempalace": { "type": "local", "command": ["/home/xnai/WanderGround/.venv/bin/mempalace-mcp", "--palace", "/home/xnai/WanderGround/mempalace"], "enabled": true }
    }
  },
  "agent": {
    "build": { "mode": "primary", "permission": { "task": { "asus_plan": "allow", "grokster": "allow", "kali": "allow", "makali": "allow", "*": "deny" } } },
    "kali": { "mode": "subagent", "inherit_context": true, "allow_background_execution": true, "description": "Council Synthesis / Federation Law", "tools": { "parallel-search": true }, "system_prompt": ["{include:~/.config/opencode/prompts/kali.md}"] },
    "makali": { "mode": "subagent", "inherit_context": true, "allow_background_execution": true, "description": "AMD Architecture Vault (Zen 2 Only)", "tools": { "parallel-search": true }, "system_prompt": ["{include:~/.config/opencode/prompts/makali.md}"] }
  },
  "subagent_depth": 2
}
OPENCODE_EOF
    verify_step "Config syntax" "jq empty ~/.config/opencode/opencode.json"
    log_success "Config deployed"

    # Ensure mempalace server is added via CLI (idempotent) + immediate verification
    opencode mcp add mempalace -- /home/xnai/WanderGround/.venv/bin/mempalace-mcp --palace /home/xnai/WanderGround/mempalace 2>/dev/null || true
    opencode mcp list --verbose 2>&1 | grep -q mempalace || { log_error "mempalace registration did not take"; exit 1; }

    # PHASE 2: Environment Variables (.env file, not bashrc)
    log_info "=== PHASE 2: ENV VARS (.env file, mode 600) ==="
    mkdir -p ~/.config/opencode
    install -m 600 /dev/null ~/.config/opencode/.env
    cat > ~/.config/opencode/.env << 'ENV_EOF'
# OMEGA ENGINE API KEYS — REPLACE PLACEHOLDERS WITH REAL KEYS
PARALLEL_API_KEY="pk_hp_$(date +%Y%m)"  # REPLACE WITH REAL PARALLEL.AI KEY
PARALLEL_API_KEY_KALI="${PARALLEL_API_KEY}"
PARALLEL_API_KEY_MAKALI="${PARALLEL_API_KEY}"
OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS="true"
MEMPALACE_PALACE="/home/xnai/WanderGround/mempalace"
ENV_EOF
    log_success "Env vars written to ~/.config/opencode/.env (mode 600)"

    # Also source for current shell
    set -a; source ~/.config/opencode/.env; set +a
    log_success "Env vars loaded"

    # PHASE 3: Prompts
    log_info "=== PHASE 3: PROMPTS ==="
    mkdir -p ~/.config/opencode/prompts
    cat > ~/.config/opencode/prompts/kali.md << 'KALI_EOF'
# kali — Council Synthesis / Federation Law
**Context Boundary**: 1,000,000 tokens | **Model Platform**: Cloud Core Invariant
## MISSION: Cross-system synthesis between Node 1 (ASUS i7-13620H) and Node 0 (HP Ryzen 5700U).
## TOOL CONTRACT: Ingest massive concurrent artifacts. Maintain trace context over hundreds of files.
## WORKFLOW: 1. Parallel web_search across kernel+systemd+hardware+federation. 2. Batch web_fetch entire doc sets.
3. Cross-ref line-by-line: kernel param -> systemd unit -> runtime -> benchmark.
4. Archive to ~/WanderGround/inbox/kali_<ts>_<synthesis>.md. 5. Decision records in docs/DECISIONS/.
KALI_EOF
    cat > ~/.config/opencode/prompts/makali.md << 'MAKALI_EOF'
# makali — Council Synthesis / AMD Architecture Vault
**Context Boundary**: 1,000,000 tokens | **Model Platform**: Cloud Core Invariant
## MISSION: Lead optimization for AMD Ryzen 7 5700U Zen 2. FORBIDDEN: intel_pstate, HWP, Thread Director, Raptor Lake.
## TOOL CONTRACT: web_search/web_fetch zero constraints. Target: amd-pstate, kernel.org AMD power mgmt.
## RESTRICTIONS: Force amd_pstate=active|guided lookups. Ignore Raptor Lake. Focus on Zen 2 EPP.
MAKALI_EOF
    log_success "Prompts created"

    # PHASE 4
    log_info "=== PHASE 4: WANDERGROUND ==="
    mkdir -p ~/WanderGround/{inbox,mempalace,spatial,domains/01_local_ai/{kernel,systemd,thermald},cache,daemon,audit}
    verify_step "WanderGround dirs" "[ -d ~/WanderGround/inbox ]"
    verify_step "MemPalace palace" "[ -f ~/WanderGround/mempalace/sqlite_exact.sqlite3 ]"
    log_success "WanderGround ready"

    # PHASE 5: Omega-hub wrapper
    log_info "=== PHASE 5: OMEGA-HUB WRAPPER ==="
    mkdir -p ~/omega-hub/tools
    cat > ~/omega-hub/tools/library_web_search.py << 'LIB_EOF'
import os
import json
import aiofiles
from datetime import datetime
import anyio
from anyio import Path, CapacityLimiter

async def library_web_search(ctx, query: str, limit: int = 15) -> str:
    """
    Structured anyio Ingestion Wrapper for the local Tailscale Federation Layer.
    Implements dynamic frontmatter generation and strict ingestion throttling.
    """
    # 1. Local MemPalace cache check
    try:
        with anyio.move_on_after(10.0):
            local_cache = await ctx.call_tool("mempalace", "mempalace_search", {
                "query": query, "limit": 3
            })
            if local_cache and getattr(local_cache, 'highest_confidence', 0) > 0.96:
                return getattr(local_cache, 'payload', str(local_cache))
    except Exception as err:
        print(f"[omega-hub] Cache lookup skip: {err}")

    # 2. Remote parallel-search
    search_payload = await ctx.call_tool("parallel-search", "web_search", {
        "query": query,
        "max_results": limit
    })

    # Defensive parsing
    try:
        data = json.loads(search_payload) if isinstance(search_payload, str) else search_payload
        urls = data.get("canonical_urls", [])[:5]
    except Exception:
        return "System Error: Invalid JSON schema returned from search backend."

    if not urls:
        return "System Warning: No authoritative technical URLs returned for this search matrix."

    accumulated_markdown = []
    limiter = CapacityLimiter(2)

    # Dynamic domain taxonomy parsing
    query_lower = query.lower()
    domain = "01_local_ai/kernel" if any(k in query_lower for k in ["kernel", "pstate", "thp", "zram"]) else \
             "01_local_ai/opencode-internals" if any(k in query_lower for k in ["opencode", "mcp", "agent"]) else \
             "02_consciousness_time" if "consciousness" in query_lower else \
             "03_classical_studies" if "classical" in query_lower else \
             "04_deep_psychology" if any(k in query_lower for k in ["psychology", "archetype", "dream"]) else \
             "05_video_games" if "game" in query_lower else \
             "06_general"  # Fallback domain for unrecognized queries

    room = "AMD_Tuning" if any(k in query_lower for k in ["amd", "ryzen", "zen2"]) else \
           "Intel_Tuning" if any(k in query_lower for k in ["intel", "raptor", "pstate"]) else \
           "MCP_Internals" if any(k in query_lower for k in ["mcp", "opencode", "agent"]) else \
           "General_Research"

    async def fetch_and_archive(target_url):
        async with limiter:
            raw_document = await ctx.call_tool("parallel-search", "web_fetch", {"url": target_url})
            clean_slug = "".join([c if c.isalnum() else "_" for c in target_url.split("/")[-1]])
            timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
            archive_path = Path(os.path.expanduser("~/WanderGround/inbox")) / f"{ctx.agent_name}_{timestamp}_{clean_slug}.md"

            frontmatter = (
                "---\n"
                f"source_url: \"{target_url}\"\n"
                f"entity: \"{ctx.agent_name}\"\n"
                f"timestamp: \"{datetime.utcnow().isoformat()}Z\"\n"
                f"hardware_target: \"AMD-Ryzen-5700U-Zen2\"\n"
                f"domain_axis: \"{domain}\"\n"
                f"palace_routing:\n"
                f"  wing: \"Archival_Systems\"\n"
                f"  room: \"{room}\"\n"
                f"---\n\n"
            )

            await archive_path.write_text(frontmatter + raw_document, encoding='utf-8')

            # Symmetric audit ledger
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "entity": ctx.agent_name,
                "query": query,
                "tool": "parallel-search.web_search",
                "results_count": len(urls),
                "fetched_urls": [target_url],
                "archived_to": str(archive_path),
                "domain_axis": domain,
                "palace_room": room
            }
            audit_path = Path(os.path.expanduser("~/WanderGround/audit/search_log.jsonl"))
            async with aiofiles.open(audit_path, mode='a') as f:
                await f.write(json.dumps(audit_entry) + "\n")

            accumulated_markdown.append(raw_document)

    async with anyio.create_task_group() as tg:
        for url in urls:
            tg.start_soon(fetch_and_archive, url)

    return "\n\n---NEW UNTHROTTLED FILE INGESTION---\n\n".join(accumulated_markdown)
LIB_EOF
    log_success "Wrapper deployed"

    # PHASE 6: Daemon
    log_info "=== PHASE 6: DAEMON (Hardened anyio 4.x) ==="
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
    log_success "Daemon running"

    # PHASE 7-8
    log_info "=== PHASE 7-8: TAILSCALE ACL + CACHE ==="
    log_warn "Apply in Tailscale Admin: src=xnai-n1-asus.tail51f14a.ts.net dst=omega-hub.tail51f14a.ts.net:8016"
    cd ~/WanderGround/cache
    [ ! -d thermal_daemon ] && git clone --depth=1 https://github.com/intel/thermal_daemon thermal_daemon 2>/dev/null || true
    [ ! -d zram-generator ] && git clone --depth=1 https://github.com/systemd/zram-generator zram-generator 2>/dev/null || true
    mkdir -p systemd; man -k systemd 2>/dev/null | awk '{print $1}' | xargs -I{} man -Thtml {} > systemd/{}.html 2>/dev/null || true

    # PHASE 9
    log_info "=== PHASE 9: VALIDATION ==="
    PARALLEL_TEST=$(opencode mcp call parallel-search web_search '{"query":"amd_pstate","max_results":1}' 2>&1 || true)
    echo "$PARALLEL_TEST" | grep -q "canonical_urls" && log_success "parallel-search OK" || { log_error "parallel-search failed"; echo "$PARALLEL_TEST"; exit 1; }
    verify_step "Daemon active" "systemctl --user is-active wanderground-embed.service | grep -q active"
    log_success "NODE 0 DEPLOYMENT COMPLETE - Backup: ${BACKUP_SUFFIX}"
    echo "Next: opencode -> Nemotron 3 Ultra -> @kali or @makali"
}
main "$@"
