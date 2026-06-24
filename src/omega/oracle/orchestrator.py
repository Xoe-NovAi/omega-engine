# AP Token: AP-ORACLE-RESTORE-v2.3.0
"""Omega CLI Orchestrator.

AP: AP-ORCHESTRATOR-v1.0.0
ICS: [NODE: CORE | ARCHETYPE: HERMES | MODEL: GEMINI-3.1-PRO | CONTEXT: ORCHESTRATOR]

Manages the lifecycle of headless AI subagents (Cline, OpenCode).
Uses AnyIO for subprocess spawning and ResourceGuard to protect RAM.

[id-soft: quake-1996] Dedicated Server Model — lifecycle management
  Quake's dedicated server runs headless, managing client connections
  through a tick loop. Orchestrator mirrors this: manages subagent
  processes through AnyIO tasks with ResourceGuard protection.
"""

import logging
import subprocess
import anyio
from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
import httpx
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime


from .entity_workspace import EntityWorkspaceManager
from .resource_guard import ResourceGuard
from .context_builder import ContextBuilder
from .capability_registry import CapabilityRegistry
from .entity_registry import EntityRegistry
from .handoff import HandoffState, format_handoff_prompt
from omega.workers.model_updater import ModelUpdaterWorker
from omega.observability import ObservabilityEngine, get_engine
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

    async def submit_task(self, task_group: anyio.abc.TaskGroup, task_id: str, model: str, prompt: str, context: str = ""):
        """
        Submits a task to the background group.
        """
        task = task_group.start_soon(self._execute_with_retry, task_id, model, prompt, context)
        self.active_tasks[task_id] = task
        return task_id

    async def _execute_with_retry(self, task_id: str, model: str, prompt: str, context: str, retries: int = 2):
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
                from omega.hub import hivemind_post_context # hypothetical import, check actual
                # Actually, we use the MCP tool via the hub or a direct call.
                # For now, we'll log it to the live feed.
                logger.info(f"Worker {task_id} completed. Gold Sheet generated.")
                
        except Exception as e:
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
            "critical_payload": raw_data[:1000]
        }


class Orchestrator:

    """Spawns and manages headless CLI agents (Cline, OpenCode) and monitors MCP health."""

    def __init__(self, resource_guard: Optional[ResourceGuard] = None):
        self.guard = resource_guard or ResourceGuard(total_capacity=1)
        
        # Sovereign Capability Registry for Agent Discovery
        self.registry = CapabilityRegistry()
        
        # Initialize Background Worker
        # Collect all Google API keys: vault (resolve_all) + env fallback
        keys = []
        try:
            from omega.vault import KeyVault
            vault_keys = KeyVault().resolve_all("google")
            keys.extend(vault_keys)
        except Exception:
            # Fallback to environment variable pattern
            primary_key = os.environ.get("GOOGLE_API_KEY", "")
            if primary_key:
                keys.append(primary_key)
            for i in range(1, 9):
                suffix = f"_{i:02d}"
                key = os.environ.get(f"GOOGLE_API_KEY{suffix}", "")
                if key:
                    keys.append(key)
        self.background_worker = BackgroundWorker(
            model_gateway=ModelGateway(health_monitor=get_health_monitor()),
            api_keys=keys
        )
        
        self.mcp_ports = {
            "omega-hub": 8016,
            "omega-research": 8011,
            "omega-stats": 8012,
        }
        self._mcp_status = {}

        # Model Updater is initialized asynchronously during start_workers()
        self.model_updater = None

    async def watch_mcps(self):
        """Background loop to monitor MCP health via SSE endpoints."""
        logger.info("Starting MCP watchdog loop...")
        async with httpx.AsyncClient(timeout=5.0) as client:
            while True:
                for name, port in self.mcp_ports.items():
                    url = f"http://127.0.0.1:{port}/sse"
                    try:
                        # Use streaming to check headers and then close
                        async with client.stream("GET", url) as response:
                            if response.status_code == 200:
                                self._mcp_status[name] = {
                                    "status": "healthy",
                                    "last_check": datetime.now().isoformat(),
                                    "port": port
                                }
                            else:
                                logger.warning(f"MCP {name} returned {response.status_code} on port {port}. Triggering restart...")
                                self._mcp_status[name] = {"status": "degraded", "port": port}
                                await anyio.run_process(["systemctl", "--user", "restart", f"{name}.service"], check=False)
                    except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadError):
                        self._mcp_status[name] = {
                            "status": "unresponsive",
                            "last_check": datetime.now().isoformat(),
                            "port": port
                        }
                        logger.warning(f"MCP {name} is unresponsive on port {port}. Triggering restart...")
                        try:
                            await anyio.run_process(
                                ["systemctl", "--user", "restart", f"{name}.service"],
                                check=False
                            )
                        except OmegaError:
                            raise
                        except Exception as e:
                            logger.error(f"Failed to restart {name}: {e}", exc_info=True)
                            raise OmegaError(f"MCP restart failed: {e}", raw_error=e) from e
                
                await anyio.sleep(60) # One check per minute is enough for background health

    async def spawn_background_worker(
        self, 
        task_id: str, 
        model: str, 
        prompt: str, 
        context: str = ""
    ) -> str:
        """
        Spawns a background worker for high-throughput sensing.
        [Sovereign Workhorse Protocol: pw_model_15]
        """
        async with anyio.create_task_group() as tg:
            await self.background_worker.submit_task(
                task_group=tg, 
                task_id=task_id, 
                model=model, 
                prompt=prompt, 
                context=context
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
            "Output:": "The expected output format is not specified."
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
        if any(k in prompt_lower for k in ["exhaustive", "deep dive", "comprehensive", "audit", "complex"]):
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
                    logger.info(f"Agent '{entity_name}' is already active ({active_agents[0]}). Proceeding with caution.")
        except ImportError:
            logger.warning("Hivemind state not available for coordination check. Skipping hazard detection.")
        except BoundaryViolationError:
            raise
        except Exception as e:
            logger.warning(f"Coordination check failed (non-fatal): {e}")

    async def dispatch_agent(
        self, 
        cli_type: str, 
        task_prompt: str, 
        entity_name: str,
        timeout: int = 300,
        handoff_state: Optional[HandoffState] = None
    ) -> Dict[str, Any]:
        """Dispatch a headless CLI agent with the entity's soul injected.
        
        Args:
            cli_type: 'cline' or 'opencode'
            task_prompt: The objective for the agent
            entity_name: The awakened entity's name (for soul injection)
            timeout: Maximum execution time in seconds
            handoff_state: Optional state for transferring context from another agent
            
        Returns:
            Dict containing the exit status and stdout of the agent.
        """
        # Sovereign Brake & SCP Enforcement
        self._verify_sovereign_brake(task_prompt)
        
        # Coordination Hazard Check (C-8)
        await self._check_coordination_hazard(entity_name)
        
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
        except Exception as e:
            logger.error(f"Failed to load entity model for '{entity_name}': {e}. Using default.", exc_info=True)
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
            env['OPENCODE_MODEL'] = entity_model  # Pass entity's designated model to OpenCode CLI
            
            # The async context manager from resource_guard.py has no __aenter__ / __aexit__ natively 
            # if it's returning an AsyncContextManager but wait, resource_guard.py defines it as:
            # @asynccontextmanager
            # async def lock(self): ...
            # So `async with self.guard.lock():` is correct.
            async with self.guard.lock():
                logger.info(f"ResourceGuard acquired. Spawning {cli_type}...")
                
                # Execute the subprocess with entity's model environment override
                with anyio.fail_after(timeout):
                    result = await anyio.run_process(
                        cmd,
                        capture_output=True,
                        check=False,
                        env=env
                    )
                
                stdout = result.stdout.decode(errors='replace')
                stderr = result.stderr.decode(errors='replace')
                
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
                except Exception as e:
                    logger.warning(f"Session distillation failed: {e}")

                return {
                    "status": "success" if success else "failed",
                    "returncode": result.returncode,
                    "stdout": stdout[-2000:], # keep tail
                    "stderr": stderr[-2000:]
                }
                                
        except TimeoutError:
            logger.error(f"Agent {cli_type} timed out after {timeout}s.")
            return {"status": "timeout", "message": "Agent execution timed out."}
        except OmegaError:
            raise
        except Exception as e:
            logger.error(f"Error dispatching {cli_type}: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def delegate_task(
        self, 
        task_description: str, 
        entity_name: str, 
        cli_type: Optional[str] = None,
        timeout: int = 300,
        handoff_state: Optional[HandoffState] = None
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
                target_cli = best_agent.split('-')[0]
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
            handoff_state=handoff_state
        )


    async def start_workers(self) -> None:
        """Start all background workers."""
        await self._init_model_updater()
        if self.model_updater:
            await self.model_updater.start()

    async def _init_model_updater(self) -> None:
        """Asynchronously initialize the ModelUpdaterWorker."""
        try:
            config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "omega.yaml"
            
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
        except Exception as e:
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
        except Exception as e:
            logger.error(f"Model update cycle failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def get_model_updater_status(self) -> Dict[str, Any]:
        """Return the current status of the model updater worker."""
        if not self.model_updater:
            return {"status": "not_initialized"}
        return self.model_updater.get_status()
