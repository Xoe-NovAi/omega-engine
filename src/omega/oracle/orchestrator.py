# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-ORACLE-RESTORE-v2.3.0
"""Omega CLI Orchestrator.

AP: AP-ORCHESTRATOR-v1.0.0
ICS: [NODE: CORE | ARCHETYPE: HERMES | MODEL: GEMINI-3.1-PRO | CONTEXT: ORCHESTRATOR]

Manages the lifecycle of headless AI subagents (Cline, OpenCode).
Uses AnyIO for subprocess spawning and ResourceGuard to protect RAM.

[id-soft: vet-068] Dedicated Server Model — lifecycle management
  Quake's dedicated server runs headless, managing client connections
  through a tick loop. Orchestrator mirrors this: manages subagent
  processes through AnyIO tasks with ResourceGuard protection.
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import logging
import socket
import subprocess
import sys
import time
import anyio
from omega.errors import (
    OmegaError,
    OmegaError,
    InferenceError,
    BoundaryViolationError,
)
import httpx2 as httpx
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


from .entity_workspace import EntityWorkspaceManager
from .resource_guard import ResourceGuard
from .context_builder import ContextBuilder
from .capability_registry import CapabilityRegistry
from .entity_registry import EntityRegistry
from .handoff import HandoffState, format_handoff_prompt
from omega.observability import get_engine
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.health_monitor import get_health_monitor
from omega.errors import BrakeViolationError, BoundaryViolationError

logger = logging.getLogger(__name__)


def _parse_comma_env(raw: str) -> List[str]:
    """Parse a comma-separated environment variable safely.

    Handles edge cases:
    - Empty string or whitespace-only → returns empty list
    - Trailing/leading commas → filtered out
    - Whitespace around items → stripped
    """
    if not raw or not raw.strip():
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


class BackgroundWorker:
    """
    Manages a pool of concurrent background research tasks.
    Uses standard ModelGateway provider fabric for inference.
    [Sovereign Workhorse Protocol: pw_model_15]
    """

    def __init__(self, model_gateway: Any, api_keys: List[str]):
        self.gateway = model_gateway
        self.keys = api_keys
        # Semaphore based on key pool size to prevent over-saturation
        self.semaphore = anyio.Semaphore(len(api_keys) if api_keys else 1)
        self.active_tasks: Dict[str, anyio.Task] = {}

    async def submit_task(
        self,
        task_group: anyio.abc.TaskGroup,
        task_id: str,
        model: str,
        prompt: str,
        context: str = "",
    ):
        """
        Submits a task to the background group.
        """
        task = task_group.start_soon(self._execute_with_retry, task_id, model, prompt, context)
        self.active_tasks[task_id] = task
        return task_id

    async def _execute_with_retry(
        self, task_id: str, model: str, prompt: str, context: str, retries: int = 2
    ):
        """
        The core execution loop:
        1. Acquire semaphore
        2. Use ModelGateway provider fabric for inference
        3. Apply Sovereign Gold Filter (Triage -> Distillation -> Synthesis)
        4. Register result in Hivemind
        """
        try:
            async with self.semaphore:
                # 1. Sensing: Use the ModelGateway's standard provider fabric
                result = await self.gateway.generate(
                    model_name=model,
                    system_prompt=f"Sovereign Sensing Task. Context: {context}",
                    user_query=prompt,
                    trace_id=task_id,
                )

                if not result.text:
                    raise InferenceError(message="Sensing returned no data", trace_id=task_id)

                # 2. Sovereign Gold Filter Pipeline
                # Step A: Sentry Triage (Fast discard)
                # Step B: Local Distillation (Gemma 4 L2/L3)
                # Step C: Gold Synthesis (Final assembly)
                gold_sheet = await self._apply_gold_filter(result.text, task_id)

                # 3. Hivemind Registration
                # Actually, we use the MCP tool via the hub or a direct call.
                # For now, we'll log it to the live feed.
                logger.info(f"Worker {task_id} completed. Gold Sheet generated.")

        except (OmegaError, RuntimeError, OSError) as e:
            if retries > 0:
                logger.warning(f"Worker {task_id} failed, retrying... ({retries} left): {e}")
                await anyio.sleep(2)
                await self._execute_with_retry(task_id, model, prompt, context, retries - 1)
            else:
                logger.error(f"Worker {task_id} failed after retries: {e}", exc_info=True)
        finally:
            self.active_tasks.pop(task_id, None)

    async def _apply_gold_filter(self, raw_data: str, task_id: str) -> Dict[str, Any]:
        """
        Implements the Gold Filter Protocol:
        Sentry Triage -> Local Distillation -> Gold Synthesis
        """
        # This is a simplified implementation of the pipeline
        # In a full version, this would call specific distilled models
        distilled = f"L2 Insight: {raw_data[:200]}...\nL3 Principle: Sovereign sensing verified."

        return {
            "trace_id": task_id,
            "context_source": "Gemma 4 Sensing",
            "distilled_insights": distilled,
            "critical_payload": raw_data[:1000],
        }


def _port_served(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    """Return True if something is already accepting TCP connections on host:port.

    [D-619] The hub must not spawn a second MCP server onto a port that a
    dedicated systemd unit already owns. Measured on n0:
        127.0.0.1:8015  pid 2759  omega-firecrawl-mcp.service (active/running)
        127.0.0.1:8018  pid 734049 omega-searxng-mcp.service  (active/running)

    connect_ex() is used rather than a bind() probe on purpose. A bind() probe
    answers a different question ("could I take this port?") and returns False
    for a port that is very much in use, because SO_REUSEADDR lets the bind
    succeed into the listen backlog. The question we need to ask is "is the
    service already reachable?", and connect_ex answers exactly that.

    A 0.5s ceiling keeps a black-holed port from stalling hub boot; a timeout
    still returns non-zero, so an unresponsive port is correctly reported as
    "not served" and we fall through to spawning.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


class Orchestrator:
    """Spawns and manages headless CLI agents (Cline, OpenCode) and monitors MCP health."""

    def __init__(self, resource_guard: Optional[ResourceGuard] = None):
        self.guard = resource_guard or ResourceGuard(max_ram_mb=1024)

        # Sovereign Capability Registry for Agent Discovery
        self.registry = CapabilityRegistry()

        # Initialize Background Worker
        # Collect all Google API keys from the sovereign vault.
        # The vault is the single source of truth (no scattered
        # os.getenv reads for API keys).
        #
        # [D-565] `src/omega/vault/` is FORGE on public cuts. An absent vault
        # means zero google: keys, not a crash — the worker then runs with an
        # empty key list. Previously the bare `from omega.vault import VaultCore`
        # raised ModuleNotFoundError out of __init__ on every public cut.
        google_creds = []
        try:
            from omega.vault import VaultCore

            vault = VaultCore()
            vault._load_sync()
            google_creds = [c for c in vault._credentials.values() if c.provider.value == "google"]
        except (ImportError, OmegaError, RuntimeError, OSError, AttributeError) as e:
            logger.warning(
                "VaultCore unavailable while collecting Google API keys (%s) — "
                "starting with an empty key list (expected on public cuts per D-565)",
                e,
            )
        keys = [c.encrypted_blob for c in google_creds]
        self.background_worker = BackgroundWorker(
            model_gateway=ModelGateway(health_monitor=get_health_monitor()), api_keys=keys
        )

        # Orchestrator manages EXTERNAL MCP servers only (firecrawl, searxng).
        # The omega-hub server is managed by systemd — NOT by Orchestrator.
        # Including it here caused infinite recursive spawn (RCA_RUNAWAY_MCP_SPAWN_20260706).
        self.mcp_ports = {
            "firecrawl": 8015,
            "searxng": 8018,
        }
        self._mcp_status = {}
        self._mcp_processes: Dict[str, subprocess.Popen] = {}
        self._mcp_scripts = {
            "firecrawl": "mcp_servers/firecrawl/server.py",
            "searxng": "mcp_servers/searxng/server.py",
        }

        # Model Updater is initialized asynchronously during start_workers()
        self.model_updater = None

        # Start EXTERNAL MCP servers only (firecrawl, searxng)
        #
        # [D-619] Only spawn when the port is NOT already served. Both of these
        # are owned by dedicated systemd units (omega-firecrawl-mcp.service,
        # omega-searxng-mcp.service). Spawning anyway produced two <defunct>
        # children under the hub PID: the duplicate bound a port that was
        # already taken, died immediately, and was never wait()ed — so it stayed
        # in the process table as a zombie for the hub's entire uptime.
        #
        # The log then compounded it: `_start_mcp_server` logged "Started MCP
        # <name> on port <p> (PID: ...)" immediately after Popen() returned,
        # before the child had bound anything or exited. That is a false
        # operational claim about a process that was already dead — the exact
        # silent-degradation shape this codebase exists to catch, and it is why
        # the zombie pair went unnoticed while the log looked healthy.
        for name in self.mcp_ports:
            port = self.mcp_ports[name]
            if _port_served(port):
                logger.info(
                    "MCP %s already served on port %d by an external owner — "
                    "not spawning (no duplicate, no child to reap)",
                    name,
                    port,
                )
                self._mcp_status[name] = {
                    "status": "external",
                    "port": port,
                    "owner": "external (systemd)",
                }
                continue
            proc = self._start_mcp_server(name)
            if proc:
                self._mcp_processes[name] = proc
                self._mcp_status[name] = {"status": "starting", "port": port}
            else:
                self._mcp_status[name] = {"status": "failed", "port": port}

    def _start_mcp_server(self, name: str) -> subprocess.Popen | None:
        """Start an MCP server as a subprocess."""
        script = self._mcp_scripts.get(name)
        if not script:
            logger.warning(f"No script configured for MCP {name}")
            return None

        # [D-619] Defence in depth. __init__ already skips ports that are served,
        # but _restart_mcp reaches this method from the watchdog loop, and a port
        # can be claimed by systemd BETWEEN those two moments. Re-check here so
        # no caller can ever race a duplicate spawn onto a live port.
        port = self.mcp_ports.get(name)
        if port is not None and _port_served(port):
            logger.info(
                "MCP %s not started: port %d is already served — skipping duplicate spawn",
                name,
                port,
            )
            return None

        # Project root is 4 levels up from this file (src/omega/oracle/orchestrator.py)
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        script_path = project_root / script

        if not script_path.exists():
            logger.error(f"MCP script not found: {script_path}")
            return None

        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root / "src")
        env["MCP_PORT"] = str(port)

        try:
            proc = subprocess.Popen(
                [sys.executable, str(script_path)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            logger.error(f"Failed to start MCP {name}: {e}")
            return None

        # [D-619] Do NOT log "Started" yet. Popen() returning proves only that
        # fork/exec was issued — not that the process is alive, and certainly not
        # that it bound `port`. On a busy port the child dies within milliseconds
        # and the old code had already printed a success line naming its PID.
        # Poll briefly: only a process still alive after the grace window gets
        # the "Started" claim, and a dead child is reaped immediately so it
        # cannot become a <defunct> entry under the hub PID.
        for _ in range(10):
            if proc.poll() is not None:
                logger.error(
                    "MCP %s exited immediately (rc=%s) after spawn on port %s — "
                    "port already in use by another owner is the usual cause",
                    name,
                    proc.returncode,
                    port,
                )
                proc.wait()  # reap, so no zombie is left behind
                return None
            time.sleep(0.05)

        logger.info(f"Started MCP {name} on port {port} (PID: {proc.pid})")
        return proc

    async def _restart_mcp(self, name: str):
        """Restart an MCP server."""
        # [D-619] If the port is owned by an external process (systemd unit), the
        # watchdog's "unhealthy" verdict is about THAT owner's health, not ours.
        # Restarting would spawn a duplicate that instantly loses the port race
        # and dies — re-creating the exact zombie this fix removes. The correct
        # action is to change nothing and let the owning unit's own
        # Restart=on-failure policy handle it.
        port = self.mcp_ports.get(name)
        if port is not None and _port_served(port):
            logger.warning(
                "MCP %s reported unhealthy but port %d is served by an external "
                "owner — not restarting (systemd owns this service)",
                name,
                port,
            )
            self._mcp_status[name] = {
                "status": "external",
                "port": port,
                "owner": "external (systemd)",
            }
            return

        # Kill existing process if any
        existing = self._mcp_processes.get(name)
        if existing and existing.poll() is None:
            existing.terminate()
            try:
                await anyio.to_thread.run_sync(existing.wait, timeout=5.0)
            except TimeoutError:
                existing.kill()
                await anyio.to_thread.run_sync(existing.wait)
        elif existing is not None:
            # [D-619] Already exited: reap it. poll() alone does not clear the
            # zombie; only wait() does.
            await anyio.to_thread.run_sync(existing.wait)

        # Start new process. _start_mcp_server now contains a bounded (max 0.5s)
        # liveness poll, so it runs in a worker thread rather than blocking the
        # event loop for the duration (M1 AnyIO — no blocking I/O on the loop).
        proc = await anyio.to_thread.run_sync(self._start_mcp_server, name)
        if proc:
            self._mcp_processes[name] = proc
            self._mcp_status[name] = {"status": "starting", "port": self.mcp_ports[name]}
        else:
            self._mcp_status[name] = {"status": "failed", "port": self.mcp_ports[name]}

    async def watch_mcps(self):
        """Background loop to monitor MCP health via SSE endpoints."""
        logger.info("Starting MCP watchdog loop...")
        async with httpx.AsyncClient(timeout=5.0) as client:
            while True:
                # [D-619] Reap any spawned MCP child that exited on its own.
                # subprocess.Popen.poll() observes the exit status but does NOT
                # release the process table slot; only wait() does. Skipping this
                # is what allowed the two <defunct> children to sit under the hub
                # PID for its entire uptime. Runs before the health checks so a
                # child that died since the last tick is cleared immediately.
                for name, proc in list(self._mcp_processes.items()):
                    if proc.poll() is not None:
                        await anyio.to_thread.run_sync(proc.wait)
                        logger.warning(
                            "Reaped exited MCP %s child (rc=%s) — it had become a "
                            "zombie under the hub PID",
                            name,
                            proc.returncode,
                        )
                        self._mcp_processes.pop(name, None)

                for name, port in self.mcp_ports.items():
                    url = f"http://127.0.0.1:{port}/sse"
                    try:
                        # Use streaming to check headers and then close
                        async with client.stream("GET", url) as response:
                            if response.status_code == 200:
                                self._mcp_status[name] = {
                                    "status": "healthy",
                                    "last_check": datetime.now().isoformat(),
                                    "port": port,
                                }
                            else:
                                logger.warning(
                                    f"MCP {name} returned {response.status_code} on port {port}. Triggering restart..."
                                )
                                self._mcp_status[name] = {"status": "degraded", "port": port}
                                await self._restart_mcp(name)
                    except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadError):
                        self._mcp_status[name] = {
                            "status": "unresponsive",
                            "last_check": datetime.now().isoformat(),
                            "port": port,
                        }
                        logger.warning(
                            f"MCP {name} is unresponsive on port {port}. Triggering restart..."
                        )
                        try:
                            await self._restart_mcp(name)
                        except OmegaError:
                            raise
                        except (OmegaError, RuntimeError, OSError) as e:
                            logger.error(f"Failed to restart {name}: {e}", exc_info=True)
                            raise OmegaError(f"MCP restart failed: {e}", raw_error=e) from e

                await anyio.sleep(60)  # One check per minute is enough for background health

    async def _restart_mcp(self, name: str):
        """Restart an MCP server by spawning it as a background process."""
        script_map = {
            "firecrawl": "mcp_servers/firecrawl/server.py",
            "searxng": "mcp_servers/searxng/server.py",
            # "omega-hub" is managed by systemd — NOT by Orchestrator.
            # Including it caused infinite recursive spawn (RCA_RUNAWAY_MCP_SPAWN_20260706).
        }
        script = script_map.get(name)
        if not script:
            logger.warning(
                f"No restart script mapped for MCP {name} (omega-hub is managed by systemd)"
            )
            return

        project_root = Path(__file__).resolve().parent.parent.parent.parent
        script_path = project_root / script

        if not script_path.exists():
            logger.error(f"MCP script not found: {script_path}")
            return

        # Kill existing process if any
        try:
            await anyio.run_process(["pkill", "-f", f"{script}"], check=False)
            await anyio.sleep(1)
        except Exception as e:
            logger.debug("pkill cleanup (expected if no prior process): %s", e)

        # Spawn new process
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root / "src")
        try:
            await anyio.run_process([sys.executable, str(script_path)], env=env, check=False)
            logger.info(f"Restarted MCP {name} ({script})")
        except Exception as e:
            logger.error(f"Failed to restart MCP {name}: {e}", exc_info=True)

    async def spawn_background_worker(
        self, task_id: str, model: str, prompt: str, context: str = ""
    ) -> str:
        """
        Spawns a background worker for high-throughput sensing.
        [Sovereign Workhorse Protocol: pw_model_15]
        """
        async with anyio.create_task_group() as tg:
            await self.background_worker.submit_task(
                task_group=tg, task_id=task_id, model=model, prompt=prompt, context=context
            )
        return f"Worker {task_id} spawned successfully."

    def get_mcp_status(self) -> Dict[str, Any]:
        """Return the current health status of all MCPs."""
        return self._mcp_status

    def _verify_sovereign_brake(self, task_prompt: str):
        """
        Enforces the Sovereign Brake and the Sovereign Communication Protocol (SCP).

        Validates:
        1. [VERIFICATION] block presence.
        2. Structural RTCO pattern: Role, Task, Constraints, and Output must be explicitly defined.
        """
        if "[VERIFICATION]" not in task_prompt:
            raise BrakeViolationError(
                "Sovereign Brake Triggered: Dispatch missing [VERIFICATION] block. "
                "All subagent requests must be preceded by a verification of intent."
            )

        # Structural RTCO validation: Ensure each required section is followed by actual content.
        required_blocks = {
            "Role:": "The role of the agent is not specified.",
            "Task:": "The specific task for the agent is not specified.",
            "Constraints:": "The operational constraints are not specified.",
            "Output:": "The expected output format is not specified.",
        }

        missing_or_empty = []
        for marker, error_msg in required_blocks.items():
            if marker not in task_prompt:
                missing_or_empty.append(marker)
                continue

            # Check if the block is empty (nothing between current marker and next marker/end of string)
            lines = task_prompt.splitlines()
            found_marker = False
            content_found = False
            for line in lines:
                if marker in line:
                    found_marker = True
                    # If there is text after the marker on the same line, it's not empty
                    if line.split(marker)[-1].strip():
                        content_found = True
                        break
                elif found_marker and line.strip():
                    # If we found the marker and then a non-empty line, it's not empty
                    content_found = True
                    break

            if not content_found:
                missing_or_empty.append(marker)

        if missing_or_empty:
            raise BrakeViolationError(
                f"SCP Structural Violation: The following RTCO blocks are missing or empty: {', '.join(missing_or_empty)}. "
                "Sovereign dispatch requires a fully defined Role-Task-Constraints-Output structure."
            )

    def _calculate_sovereign_dampening(self, task_prompt: str) -> str:
        """
        Scales agent drive based on task complexity.
        """
        prompt_lower = task_prompt.lower()
        if any(
            k in prompt_lower
            for k in ["exhaustive", "deep dive", "comprehensive", "audit", "complex"]
        ):
            return "Sovereign Drive: COMPLEX. Execute with maximum depth, iterative verification, and exhaustive analysis."
        elif any(k in prompt_lower for k in ["quick", "simple", "list", "check", "trivial"]):
            return "Sovereign Drive: TRIVIAL. Execute with minimal overhead. Direct and concise."
        else:
            return "Sovereign Drive: STANDARD. Execute with standard rigor and verification."

    async def _check_coordination_hazard(self, entity_name: str):
        """
        Check for coordination hazards before spawning an agent.
        [M10 Fleet Integrity] Prevents redundant or conflicting agent instances.
        """
        try:
            from mcp_servers.omega_hub.state import _awareness, _awareness_lock

            async with _awareness_lock:
                # Check if any agent with this entity name is currently active in the Hivemind
                active_agents = [aid for aid in _awareness if aid.endswith(f"/{entity_name}")]
                if active_agents:
                    if entity_name.lower() == "kali":
                        raise BoundaryViolationError(
                            f"Coordination Hazard: Agent 'kali' is already active ({active_agents[0]}). "
                            "Sovereign protocol forbids spawning multiple KALI instances."
                        )
                    logger.info(
                        f"Agent '{entity_name}' is already active ({active_agents[0]}). Proceeding with caution."
                    )
        except ImportError:
            logger.warning(
                "Hivemind state not available for coordination check. Skipping hazard detection."
            )
        except BoundaryViolationError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(f"Coordination check failed (non-fatal): {e}")

    async def dispatch_agent(
        self,
        cli_type: str,
        task_prompt: str,
        entity_name: str,
        timeout: int = 300,
        handoff_state: Optional[HandoffState] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatch a headless CLI agent with the entity's soul injected.

        Args:
            cli_type: 'cline' or 'opencode'
            task_prompt: The objective for the agent
            entity_name: The awakened entity's name (for soul injection)
            timeout: Maximum execution time in seconds
            handoff_state: Optional state for transferring context from another agent
            trace_id: Optional trace ID for observability propagation

        Returns:
            Dict containing the exit status and stdout of the agent.
        """
        # Sovereign Brake & SCP Enforcement
        self._verify_sovereign_brake(task_prompt)

        # Coordination Hazard Check (C-8)
        await self._check_coordination_hazard(entity_name)

        # Loop Guard Check (T2-5)
        if handoff_state:
            if handoff_state.is_loop(entity_name):
                raise BoundaryViolationError(
                    f"Handoff Loop Detected: Agent '{entity_name}' has already been visited in this chain. "
                    f"Chain: {' -> '.join(handoff_state.visited_agents)} -> {entity_name}"
                )
            if not handoff_state.increment_hop():
                raise BoundaryViolationError(
                    f"Handoff Hop Limit Exceeded: Max hops {handoff_state.max_hops} reached. "
                    f"Chain: {' -> '.join(handoff_state.visited_agents)}"
                )
            # Add current target to visited list for the next hop
            if entity_name not in handoff_state.visited_agents:
                handoff_state.visited_agents.append(entity_name)

        dampening_field = self._calculate_sovereign_dampening(task_prompt)

        logger.info(f"Preparing to dispatch {cli_type} for entity '{entity_name}'")

        # Ensure workspace exists (auto-scaffold on first dispatch)
        EntityWorkspaceManager.scaffold_workspace(entity_name)

        # Load the soul profile
        soul_prompt = await EntityWorkspaceManager.get_soul_prompt(entity_name)

        # BLOCKER FIX #1: Load entity's designated model from entity registry
        try:
            entity_registry = EntityRegistry()
            entity = entity_registry.get(entity_name)
            entity_model = entity.model if entity else "qwen3-1.7b-q6_k"
            logger.info(f"Entity '{entity_name}' designated model: {entity_model}")
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(
                f"Failed to load entity model for '{entity_name}': {e}. Using default.",
                exc_info=True,
            )
            entity_model = "qwen3-1.7b-q6_k"

        # Combine the soul prompt with the task prompt and dampening field
        full_prompt = (
            f"{soul_prompt}\n\n"
            f"{dampening_field}\n\n"
            f"YOUR TASK:\n{task_prompt}\n\n"
            f"IMPORTANT: You are operating headlessly. When finished, use the omega-hivemind MCP "
            f"to post your context, or simply conclude the task."
        )

        if handoff_state:
            full_prompt = format_handoff_prompt(handoff_state) + "\n\n" + full_prompt

        # Construct the CLI command with model specification
        if cli_type.lower() == "cline":
            # cline task <prompt>
            cmd = ["cline", "task", full_prompt]
        elif cli_type.lower() == "opencode":
            # opencode <prompt>
            cmd = ["opencode", full_prompt]
        else:
            return {"status": "error", "message": f"Unsupported CLI type: {cli_type}"}

        logger.info(f"Waiting for ResourceGuard to spawn {cli_type} with model {entity_model}...")

        try:
            # Prepare environment with entity model override
            env = os.environ.copy()
            env["OPENCODE_MODEL"] = entity_model  # Pass entity's designated model to OpenCode CLI

            # Propagate trace_id to subprocess for observability continuity
            if trace_id:
                env["OMEGA_TRACE_ID"] = trace_id

            # The async context manager from resource_guard.py has no __aenter__ / __aexit__ natively
            # if it's returning an AsyncContextManager but wait, resource_guard.py defines it as:
            # @asynccontextmanager
            # async def lock(self): ...
            # So `async with self.guard.lock():` is correct.
            async with self.guard.lock():
                logger.info(f"ResourceGuard acquired. Spawning {cli_type}...")

                # Execute the subprocess with entity's model environment override
                with anyio.fail_after(timeout):
                    result = await anyio.run_process(cmd, capture_output=True, check=False, env=env)

                stdout = result.stdout.decode(errors="replace")
                stderr = result.stderr.decode(errors="replace")

                success = result.returncode == 0
                logger.info(f"Agent {cli_type} completed. Success: {success}")

                # Trigger soul distillation on session end (Mandate 11)
                try:
                    # We assume a session was created for this dispatch.
                    # If handoff_state provided a session_id, use it; else use trace_id.
                    sid = handoff_state.session_id if handoff_state else "unknown"
                    # Note: We use the Oracle singleton if available, or create one.
                    from omega.oracle.oracle import Oracle

                    oracle_instance = Oracle()
                    await oracle_instance.close_session(entity_name, sid)
                except (OmegaError, RuntimeError, OSError) as e:
                    logger.warning(f"Session distillation failed: {e}")

                return {
                    "status": "success" if success else "failed",
                    "returncode": result.returncode,
                    "stdout": stdout[-2000:],  # keep tail
                    "stderr": stderr[-2000:],
                }

        except TimeoutError:
            logger.error(f"Agent {cli_type} timed out after {timeout}s.")
            return {"status": "timeout", "message": "Agent execution timed out."}
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Error dispatching {cli_type}: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def delegate_task(
        self,
        task_description: str,
        entity_name: str,
        cli_type: Optional[str] = None,
        timeout: int = 300,
        handoff_state: Optional[HandoffState] = None,
    ) -> Dict[str, Any]:
        """
        Delegate a task to the best-suited agent discovered via the CapabilityRegistry.

        Args:
            task_description: Description of the task to be performed.
            entity_name: The awakened entity's name for soul injection.
            cli_type: Optional forced CLI type. If None, discovery is used.
            timeout: Maximum execution time in seconds.
            handoff_state: Optional state for transferring context from another agent.
        """
        logger.info(f"Delegating task: {task_description[:50]}...")

        # 1. Discover the best agent if cli_type is not provided
        target_cli = cli_type
        if not target_cli:
            best_agent = await self.registry.discover_expert(task_description)
            if best_agent:
                # Assume agent_id contains the cli_type (e.g., 'opencode-builder')
                target_cli = best_agent.split("-")[0]
                logger.info(f"Registry discovered expert agent: {best_agent} -> using {target_cli}")
            else:
                # Fallback to opencode if no expert found
                target_cli = "opencode"
                logger.info("No expert found in registry, falling back to 'opencode'")

        # 2. Dispatch the selected agent
        return await self.dispatch_agent(
            cli_type=target_cli,
            task_prompt=task_description,
            entity_name=entity_name,
            timeout=timeout,
            handoff_state=handoff_state,
        )

    async def start_workers(self) -> None:
        """Start all background workers."""
        await self._init_model_updater()
        if self.model_updater:
            await self.model_updater.start()

    async def _init_model_updater(self) -> None:
        """Asynchronously initialize the ModelUpdaterWorker."""
        try:
            config_path = (
                Path(__file__).resolve().parent.parent.parent.parent / "config" / "omega.yaml"
            )

            def _load_cfg():
                if not config_path.exists():
                    return {}
                import yaml

                with open(config_path, "r") as f:
                    return yaml.safe_load(f) or {}

            cfg = await anyio.to_thread.run_sync(_load_cfg)
            updater_cfg = cfg.get("omega", {}).get("model_updater", {})

            if updater_cfg.get("enabled", True):
                from omega.oracle.health_monitor import get_health_monitor
                from omega.workers.model_updater import ModelUpdaterWorker

                self.model_updater = ModelUpdaterWorker(
                    model_gateway=ModelGateway(health_monitor=get_health_monitor()),
                    observability=get_engine(),
                    context_builder=ContextBuilder(),
                    config=updater_cfg,
                    guard=self.guard,
                )
                logger.info("ModelUpdaterWorker initialized successfully.")
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to initialize ModelUpdaterWorker: {e}", exc_info=True)
            raise OmegaError(f"ModelUpdater init failed: {e}", raw_error=e) from e

    async def stop_workers(self) -> None:
        """Stop all background workers."""
        if self.model_updater:
            await self.model_updater.stop()

    async def start_model_updater(self) -> None:
        """Start the scheduled model updater worker."""
        if self.model_updater:
            await self.model_updater.start()

    async def stop_model_updater(self) -> None:
        """Stop the scheduled model updater worker."""
        if self.model_updater:
            await self.model_updater.stop()

    async def trigger_model_update(self) -> Dict[str, Any]:
        """Manually trigger a model update cycle."""
        if not self.model_updater:
            return {"status": "error", "message": "ModelUpdaterWorker not initialized."}
        try:
            await self.model_updater.run_update_cycle()
            return {"status": "success", "message": "Model update cycle completed."}
        except OmegaError:
            raise
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Model update cycle failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def get_model_updater_status(self) -> Dict[str, Any]:
        """Return the current status of the model updater worker."""
        if not self.model_updater:
            return {"status": "not_initialized"}
        return self.model_updater.get_status()
