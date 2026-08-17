"""
Headless Subagent Pool — Pool Orchestrator (Skeleton)

AP Token: AP-HEADLESS-POOL-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_headless_pool ⬡ ORCHESTRATOR

Main orchestration logic for the 24-account headless subagent pool.
"""

from __future__ import annotations

import anyio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .models import (
    AggregatedResult,
    PoolHealthReport,
    PoolStatus,
    PoolTask,
    PoolType,
    RebalanceReport,
    RoutingHint,
    RoutingPlan,
    SubTask,
)
from .account_registry import AccountRegistry
from .mcp_coordinator import MCPCoordinator
from .profile_manager import ProfileManager
from .tmux_manager import TmuxManager

logger = logging.getLogger(__name__)


@dataclass
class DispatchResult:
    """Result of task dispatch."""

    task_id: str
    success: bool
    routing_plan: Optional[RoutingPlan] = None
    results: list[Any] = field(default_factory=list)
    aggregated: Optional[AggregatedResult] = None
    error: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class PoolConfig:
    """Pool orchestrator configuration."""

    # Routing
    default_routing: dict[PoolType, list[PoolType]] = field(
        default_factory=lambda: {
            PoolType.CLINE: [PoolType.CLINE, PoolType.GROK, PoolType.COPILOT],
            PoolType.GROK: [PoolType.GROK, PoolType.CLINE, PoolType.COPILOT],
            PoolType.COPILOT: [PoolType.COPILOT, PoolType.CLINE, PoolType.GROK],
        }
    )

    # Task type -> primary pool mapping
    task_routing: dict[str, PoolType] = field(
        default_factory=lambda: {
            "deep_research": PoolType.CLINE,
            "code_impl": PoolType.COPILOT,
            "code_review": PoolType.COPILOT,
            "large_refactor": PoolType.CLINE,
            "parallel_verify": PoolType.CLINE,  # Will dispatch to all
            "web_search": PoolType.GROK,
            "synthesis": PoolType.CLINE,
        }
    )

    # Context thresholds
    min_context_for_deep_research: int = 500_000
    min_context_for_large_refactor: int = 500_000

    # Health
    health_check_interval: int = 60  # seconds
    rate_limit_threshold: float = 0.1  # 10% remaining triggers rebalance

    # Concurrency
    max_concurrent_tasks: int = 10
    max_subtasks_per_task: int = 8

    # Timeouts
    task_timeout_seconds: int = 300
    handoff_timeout_seconds: int = 30


class PoolOrchestrator:
    """
    Main orchestrator for the 24-account headless subagent pool.

    Coordinates:
    - AccountRegistry: Health, rate limits, credentials
    - TmuxManager: Session lifecycle (CAO pattern)
    - MCPCoordinator: Agent-to-agent communication (CAO pattern)
    - ProfileManager: Cross-provider profiles (CAO pattern)
    """

    def __init__(
        self,
        registry: AccountRegistry,
        tmux_manager: TmuxManager,
        mcp_coordinator: MCPCoordinator,
        profile_manager: ProfileManager,
        config: Optional[PoolConfig] = None,
    ):
        self.registry = registry
        self.tmux = tmux_manager
        self.mcp = mcp_coordinator
        self.profiles = profile_manager
        self.config = config or PoolConfig()

        self._running = False
        self._task_queue: anyio.Queue[PoolTask] = anyio.Queue()
        self._active_tasks: dict[str, DispatchResult] = {}
        self._health_task: Optional[anyio.Task] = None
        self._rebalance_task: Optional[anyio.Task] = None
        self._dispatch_semaphore = anyio.Semaphore(self.config.max_concurrent_tasks)

    async def start(self) -> None:
        """Start the orchestrator."""
        if self._running:
            return

        self._running = True

        # Start background tasks
        self._health_task = anyio.create_task(self._health_monitor())
        self._rebalance_task = anyio.create_task(self._rebalance_loop())

        logger.info("PoolOrchestrator started")

    async def stop(self) -> None:
        """Stop the orchestrator."""
        self._running = False

        if self._health_task:
            self._health_task.cancel()
        if self._rebalance_task:
            self._rebalance_task.cancel()

        # Wait for active tasks to complete (with timeout)
        if self._active_tasks:
            logger.info(f"Waiting for {len(self._active_tasks)} active tasks...")
            await anyio.sleep(5)

        logger.info("PoolOrchestrator stopped")

    # --- Task Dispatch ---

    async def dispatch(
        self,
        task: PoolTask,
        routing_hint: Optional[RoutingHint] = None,
    ) -> DispatchResult:
        """
        Dispatch a task to the pool.

        This is the main entry point for task execution.
        """
        logger.info(f"Dispatching task {task.id} (type: {task.type.value})")

        async with self._dispatch_semaphore:
            # Create routing plan
            routing_plan = await self._create_routing_plan(task, routing_hint)

            if not routing_plan.account and not routing_plan.subtasks:
                return DispatchResult(
                    task_id=task.id,
                    success=False,
                    error="No available accounts for task",
                )

            # Execute based on routing plan
            if routing_plan.parallel:
                result = await self._execute_parallel(task, routing_plan)
            else:
                result = await self._execute_single(task, routing_plan)

            return result

    async def _create_routing_plan(
        self,
        task: PoolTask,
        routing_hint: Optional[RoutingHint] = None,
    ) -> RoutingPlan:
        """Create routing plan for task."""
        plan = RoutingPlan()

        # Apply routing hint
        if routing_hint:
            plan.primary_pool = self._hint_to_pool(routing_hint)
        elif task.routing_hint:
            plan.primary_pool = self._hint_to_pool(task.routing_hint)
        else:
            plan.primary_pool = self.config.task_routing.get(task.type.value, PoolType.CLINE)

        # Determine if task should be parallel
        if task.type.value == "parallel_verify" or routing_hint == RoutingHint.COGNITIVE_DIVERSITY:
            plan.parallel = True
            plan.fallback_pools = [p for p in PoolType if p != plan.primary_pool]
        elif task.decomposable and task.context_size_estimate > 200_000:
            plan.parallel = True
            plan.fallback_pools = [plan.primary_pool]

        # Get available accounts
        if plan.parallel:
            # For parallel, get accounts from multiple pools
            for pool in [plan.primary_pool] + plan.fallback_pools:
                accounts = await self.registry.get_available(
                    pool=pool,
                    min_context=task.context_size_estimate,
                )
                if accounts:
                    for i, account in enumerate(accounts[:3]):  # Max 3 per pool
                        subtask = SubTask(
                            prompt=task.prompt,
                            context_size_estimate=task.context_size_estimate,
                            assigned_account_id=account.id,
                            routing_hint=routing_hint,
                        )
                        plan.subtasks.append(subtask)
        else:
            # Single account execution
            accounts = await self.registry.get_available(
                pool=plan.primary_pool,
                min_context=task.context_size_estimate,
            )
            if accounts:
                plan.account = accounts[0]
            else:
                # Try fallback pools
                for pool in self.config.default_routing.get(plan.primary_pool, []):
                    accounts = await self.registry.get_available(
                        pool=pool,
                        min_context=task.context_size_estimate,
                    )
                    if accounts:
                        plan.account = accounts[0]
                        break

        return plan

    def _hint_to_pool(self, hint: RoutingHint) -> PoolType:
        """Convert routing hint to pool type."""
        mapping = {
            RoutingHint.PREFER_GROK: PoolType.GROK,
            RoutingHint.PREFER_COPILOT: PoolType.COPILOT,
            RoutingHint.PREFER_CLINE: PoolType.CLINE,
            RoutingHint.REQUIRE_1M_CONTEXT: PoolType.CLINE,
            RoutingHint.REQUIRE_512K_CONTEXT: PoolType.CLINE,
            RoutingHint.PREFER_FREE_TIER: PoolType.GROK,
            RoutingHint.COGNITIVE_DIVERSITY: PoolType.CLINE,
        }
        return mapping.get(hint, PoolType.CLINE)

    async def _execute_single(
        self,
        task: PoolTask,
        plan: RoutingPlan,
    ) -> DispatchResult:
        """Execute task on single account."""
        if not plan.account:
            return DispatchResult(
                task_id=task.id,
                success=False,
                error="No available account",
            )

        account = plan.account

        # Record usage
        await self.registry.record_usage(account.id)

        # Get profile and launch config
        profile = await self.profiles.create_profile(account)
        launch_config = await self.profiles.get_launch_config(account)

        # Create tmux session
        session_name = await self.tmux.create_session(account, profile)
        await self.registry.update_tmux_session(account.id, session_name)

        # Send task to agent via tmux
        await self.tmux.send_message(session_name, task.prompt)

        # Wait for completion (simplified - in production would use MCP)
        await anyio.sleep(2)

        # Capture output
        output = await self.tmux.capture_output(session_name, lines=200)

        # Clean up session
        await self.tmux.terminate_session(session_name)
        await self.registry.update_tmux_session(account.id, None)

        # Create result
        result = DispatchResult(
            task_id=task.id,
            success=True,
            routing_plan=plan,
            results=[
                {
                    "account_id": account.id,
                    "output": output,
                    "success": True,
                }
            ],
            completed_at=datetime.now(),
        )

        return result

    async def _execute_parallel(
        self,
        task: PoolTask,
        plan: RoutingPlan,
    ) -> DispatchResult:
        """Execute task in parallel across multiple accounts."""
        if not plan.subtasks:
            return DispatchResult(
                task_id=task.id,
                success=False,
                error="No subtasks in parallel plan",
            )

        # Execute subtasks concurrently
        async def execute_subtask(subtask: SubTask) -> dict[str, Any]:
            account = await self.registry.get_account(subtask.assigned_account_id)
            if not account:
                return {"success": False, "error": "Account not found"}

            await self.registry.record_usage(account.id)

            profile = await self.profiles.create_profile(account)
            session_name = await self.tmux.create_session(account, profile)
            await self.registry.update_tmux_session(account.id, session_name)

            await self.tmux.send_message(session_name, subtask.prompt)
            await anyio.sleep(2)

            output = await self.tmux.capture_output(session_name, lines=200)

            await self.tmux.terminate_session(session_name)
            await self.registry.update_tmux_session(account.id, None)

            return {
                "account_id": account.id,
                "output": output,
                "success": True,
            }

        # Run all subtasks in parallel
        results = await anyio.gather(
            *[execute_subtask(st) for st in plan.subtasks],
            return_exceptions=True,
        )

        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {
                        "account_id": plan.subtasks[i].assigned_account_id,
                        "success": False,
                        "error": str(result),
                    }
                )
            else:
                processed_results.append(result)

        # Aggregate results (placeholder - would use ResultAggregator)
        aggregated = AggregatedResult(
            synthesis="\n\n".join(
                r.get("output", "") for r in processed_results if r.get("success")
            ),
            confidence=0.8,
            contributing_accounts=[r["account_id"] for r in processed_results if r.get("success")],
        )

        return DispatchResult(
            task_id=task.id,
            success=any(r.get("success") for r in processed_results),
            routing_plan=plan,
            results=processed_results,
            aggregated=aggregated,
            completed_at=datetime.now(),
        )

    # --- Health & Rebalance ---

    async def _health_monitor(self) -> None:
        """Background health monitoring."""
        while self._running:
            try:
                await self.health_check()
            except Exception as e:
                logger.error(f"Health check failed: {e}")

            await anyio.sleep(self.config.health_check_interval)

    async def _rebalance_loop(self) -> None:
        """Background rebalance loop."""
        while self._running:
            try:
                await self.rebalance()
            except Exception as e:
                logger.error(f"Rebalance failed: {e}")

            await anyio.sleep(300)  # Every 5 minutes

    async def health_check(self) -> PoolHealthReport:
        """Check health of all accounts."""
        # Check registry health
        report = await self.registry.get_health_report()

        # Check tmux sessions
        sessions = await self.tmux.list_sessions()
        for session in sessions:
            healthy = await self.tmux.health_check(session.name)
            if not healthy:
                logger.warning(f"Unhealthy tmux session: {session.name}")

        # Check MCP agents
        mcp_health = await self.mcp.health_check_all()
        for account_id, healthy in mcp_health.items():
            if not healthy:
                await self.registry.mark_offline(account_id)

        return report

    async def rebalance(self) -> RebalanceReport:
        """Rebalance pool: restore rate-limited accounts, redistribute load."""
        report = await self.registry.rebalance()

        # Also check for credential errors that might be resolved
        # (would integrate with Omega-Vault credential watcher)

        return report

    async def get_pool_status(self) -> PoolStatus:
        """Get real-time pool status."""
        return await self.registry.get_status()

    # --- Convenience Methods ---

    async def dispatch_research(
        self,
        query: str,
        context_estimate: int = 100_000,
        decomposable: bool = True,
    ) -> DispatchResult:
        """Convenience method for deep research tasks."""
        task = PoolTask(
            type=PoolTask.Type.DEEP_RESEARCH,
            prompt=query,
            context_size_estimate=context_estimate,
            decomposable=decomposable,
            routing_hint=RoutingHint.PREFER_CLINE,
        )
        return await self.dispatch(task)

    async def dispatch_code_impl(
        self,
        prompt: str,
        context_estimate: int = 50_000,
    ) -> DispatchResult:
        """Convenience method for code implementation."""
        task = PoolTask(
            type=PoolTask.Type.CODE_IMPL,
            prompt=prompt,
            context_size_estimate=context_estimate,
            routing_hint=RoutingHint.PREFER_COPILOT,
        )
        return await self.dispatch(task)

    async def dispatch_code_review(
        self,
        prompt: str,
        context_estimate: int = 50_000,
    ) -> DispatchResult:
        """Convenience method for code review."""
        task = PoolTask(
            type=PoolTask.Type.CODE_REVIEW,
            prompt=prompt,
            context_size_estimate=context_estimate,
            routing_hint=RoutingHint.PREFER_COPILOT,
        )
        return await self.dispatch(task)

    async def dispatch_parallel_verify(
        self,
        prompt: str,
        context_estimate: int = 100_000,
    ) -> DispatchResult:
        """Convenience method for parallel verification across all pools."""
        task = PoolTask(
            type=PoolTask.Type.PARALLEL_VERIFY,
            prompt=prompt,
            context_size_estimate=context_estimate,
            decomposable=True,
            routing_hint=RoutingHint.COGNITIVE_DIVERSITY,
        )
        return await self.dispatch(task)


# --- Factory Functions ---


async def create_orchestrator(
    registry: AccountRegistry,
    tmux_manager: TmuxManager,
    mcp_coordinator: MCPCoordinator,
    profile_manager: ProfileManager,
    config: Optional[PoolConfig] = None,
) -> PoolOrchestrator:
    """Create and start pool orchestrator."""
    orchestrator = PoolOrchestrator(
        registry=registry,
        tmux_manager=tmux_manager,
        mcp_coordinator=mcp_coordinator,
        profile_manager=profile_manager,
        config=config,
    )
    await orchestrator.start()
    return orchestrator


async def create_full_pool(
    registry_path: Optional[Path] = None,
    config: Optional[PoolConfig] = None,
) -> tuple[PoolOrchestrator, AccountRegistry, TmuxManager, MCPCoordinator, ProfileManager]:
    """Create complete pool with all components initialized."""

    # Create components
    registry = AccountRegistry(registry_path=registry_path)
    await registry.initialize(mock_data=True)

    tmux_manager = TmuxManager()

    mcp_coordinator = MCPCoordinator()

    profile_manager = ProfileManager()
    await profile_manager.initialize()

    # Create orchestrator
    orchestrator = await create_orchestrator(
        registry=registry,
        tmux_manager=tmux_manager,
        mcp_coordinator=mcp_coordinator,
        profile_manager=profile_manager,
        config=config,
    )

    # Register all accounts with MCP
    accounts = await registry.get_all_accounts()
    for account in accounts:
        await mcp_coordinator.register_agent(account)

    return orchestrator, registry, tmux_manager, mcp_coordinator, profile_manager
