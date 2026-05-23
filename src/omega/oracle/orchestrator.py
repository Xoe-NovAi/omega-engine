"""Omega CLI Orchestrator.

AP: AP-ORCHESTRATOR-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | MODEL: GEMINI-3.1-PRO | CONTEXT: ORCHESTRATOR]

Manages the lifecycle of headless AI subagents (Cline, OpenCode).
Uses AnyIO for subprocess spawning and ResourceGuard to protect RAM.
"""

import logging
import subprocess
import anyio
import httpx
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime


from .entity_workspace import EntityWorkspaceManager
from .resource_guard import ResourceGuard
from .context_builder import ContextBuilder
from omega.workers.model_updater import ModelUpdaterWorker
from omega.observability import ObservabilityEngine, get_engine
from omega.oracle.model_gateway import ModelGateway

logger = logging.getLogger(__name__)

class BackgroundWorker:
    """
    Manages a pool of concurrent background research tasks.
    Ensures rate-limit compliance via a key-rotating semaphore.
    """
    def __init__(self, api_keys: List[str]):
        self.keys = api_keys
        self.semaphore = anyio.Semaphore(len(api_keys))
        self.key_index = 0
        self.active_tasks: Dict[str, anyio.Task] = {}

    async def _get_next_key(self) -> str:
        """Round-robin key rotation."""
        key = self.keys[self.key_index]
        self.key_index = (self.key_index + 1) % len(self.keys)
        return key

    async def submit_task(self, task_id: str, role: str, prompt: str, context: str = ""):
        """
        Submits a task to the background group.
        """
        # This would be called within an existing TaskGroup
        # The actual execution logic is handled in _execute_with_retry
        pass

    async def _execute_with_retry(self, role: str, prompt: str, context: str, provider_fabric: Any, retries: int = 2):
        """
        The core execution loop:
        1. Acquire semaphore
        2. Get rotated key
        3. Call ProviderFabric with the model assigned to 'role'
        """
        async with self.semaphore:
            key = await self._get_next_key()
            # Logic to map role -> model and call provider_fabric.generate
            # This will be further refined in the Resilience Layer (Phase B, Step 6)
            pass

class Orchestrator:

    """Spawns and manages headless CLI agents (Cline, OpenCode) and monitors MCP health."""

    def __init__(self, resource_guard: Optional[ResourceGuard] = None):
        self.guard = resource_guard or ResourceGuard(limit=1)
        
        # Initialize Background Worker
        keys = os.environ.get("OPENROUTER_KEYS", "").split(",")
        self.background_worker = BackgroundWorker(api_keys=keys)
        
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
                        except Exception as e:
                            logger.error(f"Failed to restart {name}: {e}")
                
                await anyio.sleep(60) # One check per minute is enough for background health

    def get_mcp_status(self) -> Dict[str, Any]:
        """Return the current health status of all MCPs."""
        return self._mcp_status

    async def dispatch_agent(
        self, 
        cli_type: str, 
        task_prompt: str, 
        entity_name: str,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """Dispatch a headless CLI agent with the entity's soul injected.
        
        Args:
            cli_type: 'cline' or 'opencode'
            task_prompt: The objective for the agent
            entity_name: The awakened entity's name (for soul injection)
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict containing the exit status and stdout of the agent.
        """
        logger.info(f"Preparing to dispatch {cli_type} for entity '{entity_name}'")
        
        # Ensure workspace exists (auto-scaffold on first dispatch)
        EntityWorkspaceManager.scaffold_workspace(entity_name)
        
        # Load the soul profile
        soul_prompt = await EntityWorkspaceManager.get_soul_prompt(entity_name)
        
        # Combine the soul prompt with the task prompt
        full_prompt = (
            f"{soul_prompt}\n\n"
            f"YOUR TASK:\n{task_prompt}\n\n"
            f"IMPORTANT: You are operating headlessly. When finished, use the omega-hivemind MCP "
            f"to post your context, or simply conclude the task."
        )

        # Construct the CLI command
        if cli_type.lower() == "cline":
            # cline task <prompt>
            cmd = ["cline", "task", full_prompt]
        elif cli_type.lower() == "opencode":
            # opencode <prompt>
            cmd = ["opencode", full_prompt]
        else:
            return {"status": "error", "message": f"Unsupported CLI type: {cli_type}"}

        logger.info(f"Waiting for ResourceGuard to spawn {cli_type}...")
        
        try:
            # The async context manager from resource_guard.py has no __aenter__ / __aexit__ natively 
            # if it's returning an AsyncContextManager but wait, resource_guard.py defines it as:
            # @asynccontextmanager
            # async def lock(self): ...
            # So `async with self.guard.lock():` is correct.
            async with self.guard.lock():
                logger.info(f"ResourceGuard acquired. Spawning {cli_type}...")
                
                # Execute the subprocess
                with anyio.fail_after(timeout):
                    result = await anyio.run_process(
                        cmd,
                        capture_output=True,
                        check=False
                    )
                
                stdout = result.stdout.decode(errors='replace')
                stderr = result.stderr.decode(errors='replace')
                
                success = result.returncode == 0
                logger.info(f"Agent {cli_type} completed. Success: {success}")
                
                return {
                    "status": "success" if success else "failed",
                    "returncode": result.returncode,
                    "stdout": stdout[-2000:], # keep tail
                    "stderr": stderr[-2000:]
                }
                
        except TimeoutError:
            logger.error(f"Agent {cli_type} timed out after {timeout}s.")
            return {"status": "timeout", "message": "Agent execution timed out."}
        except Exception as e:
            logger.error(f"Error dispatching {cli_type}: {e}")
            return {"status": "error", "message": str(e)}

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
                self.model_updater = ModelUpdaterWorker(
                    model_gateway=ModelGateway(),
                    observability=get_engine(),
                    context_builder=ContextBuilder(),
                    config=updater_cfg,
                    guard=self.guard,
                )
                logger.info("ModelUpdaterWorker initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize ModelUpdaterWorker: {e}")

    async def stop_workers(self) -> None:
        """Stop all background workers."""
        if self.model_updater:
            await self.model_updater.stop()

    async def trigger_model_update(self) -> Dict[str, Any]:
        """Manually trigger a model update cycle."""
        if not self.model_updater:
            return {"status": "error", "message": "ModelUpdaterWorker not initialized."}
        try:
            await self.model_updater.run_update_cycle()
            return {"status": "success", "message": "Model update cycle completed."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_model_updater_status(self) -> Dict[str, Any]:
        """Return the current status of the model updater worker."""
        if not self.model_updater:
            return {"status": "not_initialized"}
        return self.model_updater.get_status()

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
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_model_updater_status(self) -> Dict[str, Any]:
        """Return the current status of the model updater worker."""
        if not self.model_updater:
            return {"status": "not_initialized"}
        return self.model_updater.get_status()
