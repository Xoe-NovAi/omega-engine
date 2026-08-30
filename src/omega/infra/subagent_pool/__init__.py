# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Headless Subagent Pool — 24-Account CLI Agent Compute Resource

AP Token: AP-HEADLESS-POOL-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_headless_pool ⬡ INIT

Transforms 24 unused CLI accounts (8 Grok + 8 Copilot + 8 Cline) into a unified
compute resource with intelligent task routing, credential integration, and
cognitive diversity weighting.

Architecture Reference: docs/strategy/HEADLESS_SUBAGENT_POOL_ARCHITECTURE_20260719.md
CAO Pattern: https://github.com/awslabs/cli-agent-orchestrator
"""

from .models import (
    # Enums
    PoolType,
    AccountHealth,
    TaskType,
    RoutingHint,
    # Data models
    Account,
    PoolTask,
    SubTask,
    RoutingPlan,
    AccountResult,
    AggregatedResult,
    PoolHealthReport,
    PoolStatus,
    RebalanceReport,
    create_default_accounts,
)

from .account_registry import AccountRegistry
from .tmux_manager import TmuxManager, TmuxSession, CAOSessionManager
from .mcp_coordinator import (
    MCPCoordinator,
    MCPServerConfig,
    HandoffPacket,
    AgentState,
    MockMCPClient,
    FleetNode,
    FleetCoordinator,
)
from .profile_manager import (
    ProfileManager,
    AgentProfile,
    LaunchConfig,
    CAO_ROLES,
    PROVIDER_CONFIGS,
    generate_all_profiles,
)
from .orchestrator import (
    PoolOrchestrator,
    PoolConfig,
    DispatchResult,
    create_orchestrator,
    create_full_pool,
)

__version__ = "1.0.0"
__all__ = [
    # Models
    "PoolType",
    "AccountHealth",
    "TaskType",
    "RoutingHint",
    "Account",
    "PoolTask",
    "SubTask",
    "RoutingPlan",
    "AccountResult",
    "AggregatedResult",
    "PoolHealthReport",
    "PoolStatus",
    "RebalanceReport",
    "create_default_accounts",
    # Account Registry
    "AccountRegistry",
    # Tmux Manager
    "TmuxManager",
    "TmuxSession",
    "CAOSessionManager",
    # MCP Coordinator
    "MCPCoordinator",
    "MCPServerConfig",
    "HandoffPacket",
    "AgentState",
    "MockMCPClient",
    "FleetNode",
    "FleetCoordinator",
    # Profile Manager
    "ProfileManager",
    "AgentProfile",
    "LaunchConfig",
    "CAO_ROLES",
    "PROVIDER_CONFIGS",
    "generate_all_profiles",
    # Orchestrator
    "PoolOrchestrator",
    "PoolConfig",
    "DispatchResult",
    "create_orchestrator",
    "create_full_pool",
]
