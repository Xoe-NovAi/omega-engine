# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Headless Subagent Pool — MCP Coordinator (CAO Pattern)

AP Token: AP-HEADLESS-POOL-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_headless_pool ⬡ MCP_COORDINATOR

CAO Pattern Reference: https://github.com/awslabs/cli-agent-orchestrator
- MCP-based agent-to-agent coordination
- Primitives: handoff, assign, send_message, get_state
- Each agent exposes MCP server on unique port
"""

from __future__ import annotations

import anyio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .models import Account, PoolTask, PoolType

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an agent's MCP server."""

    account_id: str
    port: int
    host: str = "127.0.0.1"
    transport: str = "stdio"  # stdio, sse, streamable-http
    capabilities: list[str] = field(default_factory=list)
    pid: Optional[int] = None
    started_at: Optional[datetime] = None


@dataclass
class HandoffPacket:
    """MCP handoff packet (CAO pattern)."""

    id: str
    source_account: str
    target_account: str
    task: PoolTask
    context: dict[str, Any]
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Agent state retrieved via MCP."""

    account_id: str
    status: str  # idle, busy, error
    current_task: Optional[str] = None
    context_usage: float = 0.0
    last_activity: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class MockMCPClient:
    """Mock MCP client for development/testing."""

    def __init__(self, account_id: str):
        self.account_id = account_id
        self._state = AgentState(account_id=account_id, status="idle")

    async def call_tool(self, tool: str, args: dict[str, Any]) -> Any:
        """Mock tool call."""
        logger.debug(f"Mock MCP call: {tool} for {self.account_id}")

        if tool == "handoff":
            self._state.status = "busy"
            self._state.current_task = args.get("packet", {}).get("task", {}).get("id")
            return {"success": True, "packet_id": args.get("packet", {}).get("id")}

        elif tool == "assign":
            self._state.status = "busy"
            self._state.current_task = args.get("task", {}).get("id")
            return {"success": True, "assigned": True}

        elif tool == "send_message":
            return {"success": True, "delivered": True}

        elif tool == "get_state":
            return self._state.__dict__

        elif tool == "get_capabilities":
            return {"capabilities": ["code_gen", "reasoning"]}

        return {"success": False, "error": f"Unknown tool: {tool}"}

    async def close(self):
        pass


class MCPCoordinator:
    """
    MCP-based coordination for headless agent pool (CAO pattern).

    Each agent runs an MCP server exposing:
    - handoff: Transfer task to another agent
    - assign: Assign new task to agent
    - send_message: Send message to agent
    - get_state: Get agent state
    - get_capabilities: Get agent capabilities
    """

    def __init__(
        self,
        base_port: int = 9800,
        config_dir: Optional[Path] = None,
    ):
        self.base_port = base_port
        self.config_dir = config_dir or Path("data/state/subagent_pool/mcp")
        self._servers: dict[str, MCPServerConfig] = {}
        self._clients: dict[str, Any] = {}  # MCP client connections
        self._lock = anyio.Lock()

    def _get_port(self, account_id: str) -> int:
        """Get deterministic port for account."""
        # Hash account_id to port offset
        offset = hash(account_id) % 1000
        return self.base_port + offset

    def _get_config_path(self, account_id: str) -> Path:
        """Get MCP config file path for account."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        return self.config_dir / f"{account_id}.json"

    async def register_agent(
        self,
        account: Account,
        capabilities: Optional[list[str]] = None,
    ) -> MCPServerConfig:
        """Register an agent's MCP server."""
        port = self._get_port(account.id)

        config = MCPServerConfig(
            account_id=account.id,
            port=port,
            capabilities=capabilities or list(account.capabilities),
        )

        async with self._lock:
            self._servers[account.id] = config
            await self._persist_config(config)

        logger.info(f"Registered MCP server for {account.id} on port {port}")
        return config

    async def _persist_config(self, config: MCPServerConfig) -> None:
        """Persist MCP server config to disk."""
        path = self._get_config_path(config.account_id)
        data = {
            "account_id": config.account_id,
            "port": config.port,
            "host": config.host,
            "transport": config.transport,
            "capabilities": config.capabilities,
        }
        await anyio.to_thread.run_sync(
            path.write_text,
            json.dumps(data, indent=2),
        )

    async def unregister_agent(self, account_id: str) -> None:
        """Unregister an agent's MCP server."""
        async with self._lock:
            self._servers.pop(account_id, None)
            self._clients.pop(account_id, None)
            path = self._get_config_path(account_id)
            if path.exists():
                await anyio.to_thread.run_sync(path.unlink)
            logger.info(f"Unregistered MCP server for {account_id}")

    async def get_server_config(self, account_id: str) -> Optional[MCPServerConfig]:
        """Get MCP server config for account."""
        async with self._lock:
            return self._servers.get(account_id)

    async def get_all_configs(self) -> list[MCPServerConfig]:
        """Get all registered MCP server configs."""
        async with self._lock:
            return list(self._servers.values())

    async def start_agent_server(self, account: Account) -> MCPServerConfig:
        """Start MCP server for an agent (spawns process)."""
        config = await self.register_agent(account)

        # In production, this would spawn the agent with MCP server
        # For now, mark as started
        config.started_at = datetime.now()
        config.pid = 0  # Would be actual PID

        await self._persist_config(config)
        logger.info(f"Started MCP server for {account.id} on port {config.port}")
        return config

    async def stop_agent_server(self, account_id: str) -> bool:
        """Stop MCP server for an agent."""
        config = await self.get_server_config(account_id)
        if not config:
            return False

        # In production, would kill the process
        if config.pid:
            try:
                import os

                os.kill(config.pid, 15)  # SIGTERM
            except ProcessLookupError:
                pass

        config.pid = None
        config.started_at = None
        await self._persist_config(config)
        logger.info(f"Stopped MCP server for {account_id}")
        return True

    # --- MCP Client Operations (CAO Primitives) ---

    async def _get_client(self, account_id: str) -> Any:
        """Get or create MCP client for account."""
        if account_id in self._clients:
            return self._clients[account_id]

        config = await self.get_server_config(account_id)
        if not config:
            raise ValueError(f"No MCP server registered for {account_id}")

        # Create MCP client based on transport
        if config.transport == "stdio":
            client = await self._create_stdio_client(config)
        elif config.transport in ("sse", "streamable-http"):
            client = await self._create_http_client(config)
        else:
            raise ValueError(f"Unknown transport: {config.transport}")

        self._clients[account_id] = client
        return client

    async def _create_stdio_client(self, config: MCPServerConfig) -> Any:
        """Create stdio MCP client (spawns agent process)."""
        # This would spawn the actual CLI agent with MCP stdio transport
        # For now, return mock client
        return MockMCPClient(config.account_id)

    async def _create_http_client(self, config: MCPServerConfig) -> Any:
        """Create HTTP/SSE MCP client."""
        # Would connect to running agent's MCP endpoint
        return MockMCPClient(config.account_id)

    async def handoff(
        self,
        source_account: str,
        target_account: str,
        task: PoolTask,
        context: Optional[dict[str, Any]] = None,
        priority: int = 0,
    ) -> HandoffPacket:
        """
        Handoff task from one agent to another (CAO handoff primitive).

        This is the primary coordination mechanism - agents hand off
        tasks to each other via MCP.
        """
        packet = HandoffPacket(
            id=f"handoff-{source_account}-{target_account}-{datetime.now().timestamp()}",
            source_account=source_account,
            target_account=target_account,
            task=task,
            context=context or {},
            priority=priority,
        )

        # Send handoff to target agent via MCP
        client = await self._get_client(target_account)
        result = await client.call_tool(
            "handoff",
            {
                "packet": {
                    "id": packet.id,
                    "source_account": packet.source_account,
                    "target_account": packet.target_account,
                    "task": packet.task.to_dict(),
                    "context": packet.context,
                    "priority": packet.priority,
                    "created_at": packet.created_at.isoformat(),
                    "metadata": packet.metadata,
                }
            },
        )

        if not result.get("success"):
            raise RuntimeError(f"Handoff failed: {result.get('error')}")

        logger.info(f"Handoff {packet.id}: {source_account} -> {target_account}")
        return packet

    async def assign_task(
        self,
        account_id: str,
        task: PoolTask,
        context: Optional[dict[str, Any]] = None,
        callback: Optional[str] = None,
    ) -> bool:
        """
        Assign task to agent (CAO assign primitive).

        Async fire-and-forget with optional callback.
        """
        client = await self._get_client(account_id)
        result = await client.call_tool(
            "assign",
            {
                "task": task.to_dict(),
                "context": context or {},
                "callback": callback,
            },
        )

        if not result.get("success"):
            logger.error(f"Assign failed for {account_id}: {result.get('error')}")
            return False

        logger.info(f"Assigned task {task.id} to {account_id}")
        return True

    async def send_message(
        self,
        account_id: str,
        message: str,
        message_type: str = "user",
    ) -> bool:
        """
        Send message to agent (CAO send_message primitive).

        Communicates with existing agent session.
        """
        client = await self._get_client(account_id)
        result = await client.call_tool(
            "send_message",
            {
                "message": message,
                "type": message_type,
            },
        )

        if not result.get("success"):
            logger.error(f"Send message failed for {account_id}: {result.get('error')}")
            return False

        logger.debug(f"Sent message to {account_id}: {message[:50]}...")
        return True

    async def get_agent_state(self, account_id: str) -> Optional[AgentState]:
        """Get agent state via MCP (CAO get_state primitive)."""
        try:
            client = await self._get_client(account_id)
            result = await client.call_tool("get_state", {})

            if result.get("success") is not False:
                return AgentState(
                    account_id=account_id,
                    status=result.get("status", "unknown"),
                    current_task=result.get("current_task"),
                    context_usage=result.get("context_usage", 0.0),
                    last_activity=datetime.fromisoformat(result["last_activity"])
                    if result.get("last_activity")
                    else None,
                    metadata=result.get("metadata", {}),
                )
        except Exception as e:
            logger.error(f"Failed to get state for {account_id}: {e}")

        return None

    async def get_agent_capabilities(self, account_id: str) -> list[str]:
        """Get agent capabilities via MCP."""
        try:
            client = await self._get_client(account_id)
            result = await client.call_tool("get_capabilities", {})
            return result.get("capabilities", [])
        except Exception as e:
            logger.error(f"Failed to get capabilities for {account_id}: {e}")
            return []

    async def broadcast_message(
        self,
        message: str,
        pool: Optional[PoolType] = None,
        exclude: Optional[list[str]] = None,
    ) -> dict[str, bool]:
        """Broadcast message to all agents in pool."""
        exclude = exclude or []
        results = {}

        for account_id, config in self._servers.items():
            if account_id in exclude:
                continue
            if pool and not account_id.startswith(pool.value):
                continue

            results[account_id] = await self.send_message(account_id, message)

        return results

    async def health_check_all(self) -> dict[str, bool]:
        """Health check all registered agents."""
        results = {}
        for account_id in self._servers:
            state = await self.get_agent_state(account_id)
            results[account_id] = state is not None and state.status != "error"
        return results

    async def close_all_clients(self) -> None:
        """Close all MCP client connections."""
        for account_id, client in self._clients.items():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing client for {account_id}: {e}")
        self._clients.clear()

    async def cleanup(self) -> None:
        """Cleanup all resources."""
        await self.close_all_clients()
        for account_id in list(self._servers.keys()):
            await self.stop_agent_server(account_id)
        logger.info("MCP Coordinator cleaned up")


# --- CAO Fleet Coordination (Multi-Node) ---


@dataclass
class FleetNode:
    """Fleet node configuration (CAO fleet pattern)."""

    name: str
    host: str
    port: int = 9889
    role: str = "pool-node"  # grok-pool, copilot-pool, cline-pool
    capabilities: list[str] = field(default_factory=list)


class FleetCoordinator:
    """
    Multi-node fleet coordination (CAO fleet pattern).

    Coordinates pool across multiple machines:
    - fleet.json registry (git-ignored)
    - Concurrent health checks with per-node isolation
    - Proxy launch to specific fleet node
    """

    def __init__(self, fleet_config_path: Optional[Path] = None):
        self.fleet_config_path = fleet_config_path or Path("data/state/subagent_pool/fleet.json")
        self._nodes: dict[str, FleetNode] = {}
        self._lock = anyio.Lock()

    async def load_fleet_config(self) -> list[FleetNode]:
        """Load fleet configuration from file."""
        if not self.fleet_config_path.exists():
            return []

        content = await anyio.to_thread.run_sync(self.fleet_config_path.read_text)
        data = json.loads(content)

        nodes = []
        for node_data in data.get("machines", []):
            nodes.append(FleetNode(**node_data))

        async with self._lock:
            self._nodes = {n.name: n for n in nodes}

        return nodes

    async def save_fleet_config(self, nodes: list[FleetNode]) -> None:
        """Save fleet configuration to file."""
        self.fleet_config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "port": 9889,
            "machines": [
                {
                    "name": n.name,
                    "host": n.host,
                    "port": n.port,
                    "role": n.role,
                    "capabilities": n.capabilities,
                }
                for n in nodes
            ],
        }

        await anyio.to_thread.run_sync(
            self.fleet_config_path.write_text,
            json.dumps(data, indent=2),
        )

        async with self._lock:
            self._nodes = {n.name: n for n in nodes}

    async def fan_out_health_check(self) -> dict[str, bool]:
        """Concurrent health checks with per-node isolation."""
        # Would connect to each node's MCP coordinator
        # For now, return mock results
        return {name: True for name in self._nodes}

    async def launch_on_node(self, node_name: str, task: PoolTask) -> str:
        """Proxy launch to specific fleet node."""
        node = self._nodes.get(node_name)
        if not node:
            raise ValueError(f"Unknown fleet node: {node_name}")

        # Would proxy to node's MCP coordinator
        return f"launched-on-{node_name}"


# --- Convenience Functions ---


async def create_coordinator(
    base_port: int = 9800,
    config_dir: Optional[Path] = None,
) -> MCPCoordinator:
    """Create and initialize MCP coordinator."""
    coordinator = MCPCoordinator(base_port=base_port, config_dir=config_dir)
    return coordinator


async def register_pool_accounts(
    coordinator: MCPCoordinator,
    accounts: list[Account],
) -> dict[str, MCPServerConfig]:
    """Register all accounts in pool with MCP coordinator."""
    configs = {}
    for account in accounts:
        configs[account.id] = await coordinator.register_agent(account)
    return configs
