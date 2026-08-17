"""
Headless Subagent Pool — Profile Manager (CAO Pattern)

AP Token: AP-HEADLESS-POOL-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_headless_pool ⬡ PROFILE_MANAGER

CAO Pattern Reference: https://github.com/awslabs/cli-agent-orchestrator
- Agent profiles in markdown + YAML frontmatter
- Provider field for cross-provider support
- Role-based tool restrictions
- Memory scopes with auto-injection
"""

from __future__ import annotations

import anyio
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from .models import Account, PoolType

logger = logging.getLogger(__name__)


@dataclass
class AgentProfile:
    """CAO-compatible agent profile."""

    name: str
    description: str
    provider: str  # grok_cli, copilot_cli, cline_cli, claude_code, codex, etc.
    role: str  # supervisor, developer, reviewer, researcher
    allowed_tools: list[str]  # Tool restrictions (CAO pattern)
    model: str
    env_vars: dict[str, str] = field(default_factory=dict)
    memory_scopes: list[str] = field(default_factory=list)  # CAO memory scopes
    system_prompt: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Serialize to markdown with YAML frontmatter (CAO format)."""
        frontmatter = {
            "name": self.name,
            "description": self.description,
            "provider": self.provider,
            "role": self.role,
            "allowedTools": self.allowed_tools,
            "model": self.model,
            "envVars": self.env_vars,
            "memoryScopes": self.memory_scopes,
            "systemPrompt": self.system_prompt,
            "metadata": self.metadata,
        }
        yaml_str = yaml.dump(frontmatter, sort_keys=False, default_flow_style=False)
        return f"---\n{yaml_str}---\n\n{self.system_prompt}"

    @classmethod
    def from_markdown(cls, content: str) -> AgentProfile:
        """Parse from markdown with YAML frontmatter."""
        match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        if not match:
            raise ValueError("Invalid profile format: missing frontmatter")

        frontmatter = yaml.safe_load(match.group(1))
        system_prompt = match.group(2).strip()

        return cls(
            name=frontmatter.get("name", ""),
            description=frontmatter.get("description", ""),
            provider=frontmatter.get("provider", ""),
            role=frontmatter.get("role", "developer"),
            allowed_tools=frontmatter.get("allowedTools", ["@builtin"]),
            model=frontmatter.get("model", ""),
            env_vars=frontmatter.get("envVars", {}),
            memory_scopes=frontmatter.get("memoryScopes", []),
            system_prompt=system_prompt,
            metadata=frontmatter.get("metadata", {}),
        )


# CAO Role Definitions
CAO_ROLES = {
    "supervisor": {
        "description": "Orchestrates other agents, delegates tasks",
        "allowed_tools": ["@builtin", "@cao-mcp-server", "fs_read", "fs_list", "execute_bash"],
        "memory_scopes": ["global", "project", "session"],
    },
    "developer": {
        "description": "Implements code, writes files, runs tests",
        "allowed_tools": ["@builtin", "@cao-mcp-server", "fs_*", "execute_bash", "web_fetch"],
        "memory_scopes": ["project", "session"],
    },
    "reviewer": {
        "description": "Reviews code, audits security, checks quality",
        "allowed_tools": ["@builtin", "@cao-mcp-server", "fs_read", "fs_list", "web_fetch"],
        "memory_scopes": ["project", "session"],
    },
    "researcher": {
        "description": "Deep research, web search, synthesis",
        "allowed_tools": ["@builtin", "@cao-mcp-server", "web_fetch", "fs_read", "fs_list"],
        "memory_scopes": ["global", "project", "session"],
    },
}


# Provider-specific configurations
PROVIDER_CONFIGS = {
    "grok_cli": {
        "binary": "grok",
        "default_model": "grok-3",
        "supports_web_search": True,
        "supports_reasoning": True,
        "context_windows": {
            "grok-3": 1_000_000,
            "grok-2": 128_000,
            "grok-1.5": 128_000,
        },
    },
    "copilot_cli": {
        "binary": "github-copilot-cli",
        "default_model": "gpt-4o",
        "supports_web_search": False,
        "supports_reasoning": True,  # o1
        "context_windows": {
            "gpt-4o": 128_000,
            "gpt-4o-mini": 128_000,
            "o1": 128_000,
        },
    },
    "cline_cli": {
        "binary": "cline",
        "default_model": "deepseek-v4-flash",
        "supports_web_search": False,
        "supports_reasoning": True,
        "context_windows": {
            "deepseek-v4-flash": 1_000_000,
            "mimo-v2.5": 512_000,
            "claude-3.5-sonnet": 200_000,
            "gpt-4o": 128_000,
        },
    },
    "claude_code": {
        "binary": "claude",
        "default_model": "claude-3.5-sonnet",
        "supports_web_search": False,
        "supports_reasoning": True,
        "context_windows": {
            "claude-3.5-sonnet": 200_000,
            "claude-3-opus": 200_000,
        },
    },
    "codex": {
        "binary": "codex",
        "default_model": "gpt-4o",
        "supports_web_search": False,
        "supports_reasoning": True,
        "context_windows": {
            "gpt-4o": 128_000,
            "gpt-4o-mini": 128_000,
        },
    },
}


@dataclass
class LaunchConfig:
    """Launch configuration for an agent."""

    command: str
    args: list[str]
    env: dict[str, str]
    working_dir: str
    tmux_session_name: str


class ProfileManager:
    """
    Manages cross-provider agent profiles (CAO pattern).

    Generates profiles from account configurations, handles
    provider-specific settings, and manages profile persistence.
    """

    def __init__(
        self,
        profiles_dir: Optional[Path] = None,
        templates_dir: Optional[Path] = None,
    ):
        self.profiles_dir = profiles_dir or Path("data/state/subagent_pool/profiles")
        self.templates_dir = templates_dir or Path("config/subagent_pool/templates")
        self._profile_cache: dict[str, AgentProfile] = {}
        self._lock = anyio.Lock()

    async def initialize(self) -> None:
        """Initialize profile manager."""
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        await self._ensure_templates()

    async def _ensure_templates(self) -> None:
        """Ensure default profile templates exist."""
        templates = {
            "supervisor.md": self._create_template("supervisor"),
            "developer.md": self._create_template("developer"),
            "reviewer.md": self._create_template("reviewer"),
            "researcher.md": self._create_template("researcher"),
        }

        for name, content in templates.items():
            path = self.templates_dir / name
            if not path.exists():
                await anyio.to_thread.run_sync(path.write_text, content)

    def _create_template(self, role: str) -> str:
        """Create a profile template for a role."""
        role_config = CAO_ROLES.get(role, CAO_ROLES["developer"])

        frontmatter = {
            "name": "{{account_id}}-{role}",
            "description": "{{pool}} {role} agent",
            "provider": "{{provider}}",
            "role": role,
            "allowedTools": role_config["allowed_tools"],
            "model": "{{model}}",
            "envVars": {},
            "memoryScopes": role_config["memory_scopes"],
            "systemPrompt": f"You are a {role} agent in the Omega Engine Headless Subagent Pool.\n\n{role_config['description']}\n\nFollow the Sovereign Mandates and Omega Engine protocols.",
            "metadata": {
                "pool": "{{pool}}",
                "account_id": "{{account_id}}",
                "created_by": "ProfileManager",
            },
        }

        yaml_str = yaml.dump(frontmatter, sort_keys=False, default_flow_style=False)
        return f"---\n{yaml_str}---\n\n{frontmatter['systemPrompt']}"

    def _get_provider(self, pool: PoolType) -> str:
        """Map pool type to provider string."""
        mapping = {
            PoolType.GROK: "grok_cli",
            PoolType.COPILOT: "copilot_cli",
            PoolType.CLINE: "cline_cli",
        }
        return mapping.get(pool, "unknown")

    def _get_role(self, account: Account) -> str:
        """Determine CAO role from account capabilities."""
        caps = account.capabilities

        if "orchestrate" in caps or "delegate" in caps:
            return "supervisor"
        elif "code_review" in caps or "audit" in caps:
            return "reviewer"
        elif "deep_research" in caps or "web_search" in caps:
            return "researcher"
        else:
            return "developer"

    def _get_allowed_tools(self, account: Account, role: str) -> list[str]:
        """Map capabilities to CAO tool vocabulary."""
        base_tools = CAO_ROLES.get(role, CAO_ROLES["developer"])["allowed_tools"]
        tools = list(base_tools)

        # Add capability-specific tools
        if "code_gen" in account.capabilities or "code_impl" in account.capabilities:
            if "fs_*" not in tools:
                tools.append("fs_*")
            if "execute_bash" not in tools:
                tools.append("execute_bash")

        if "web_search" in account.capabilities:
            if "web_fetch" not in tools:
                tools.append("web_fetch")

        if "read_only" in account.capabilities:
            # Restrict to read-only
            tools = ["@builtin", "@cao-mcp-server", "fs_read", "fs_list", "web_fetch"]

        return tools

    def _get_env_vars(self, account: Account) -> dict[str, str]:
        """Get environment variables for account (credentials from Omega-Vault)."""
        # These would be populated from Omega-Vault at runtime
        pool = account.pool
        env = {}

        if pool == PoolType.GROK:
            env["GROK_API_KEY"] = f"${{VAULT:{account.credentials_ref}:api_key}}"
        elif pool == PoolType.COPILOT:
            env["GITHUB_TOKEN"] = f"${{VAULT:{account.credentials_ref}:token}}"
        elif pool == PoolType.CLINE:
            if "deepseek" in account.model.lower():
                env["DEEPSEEK_API_KEY"] = f"${{VAULT:{account.credentials_ref}:api_key}}"
            elif "mimo" in account.model.lower():
                env["MIMO_API_KEY"] = f"${{VAULT:{account.credentials_ref}:api_key}}"

        return env

    async def create_profile(self, account: Account) -> AgentProfile:
        """Generate profile for a specific account."""
        cache_key = f"{account.id}:{account.model}"

        async with self._lock:
            if cache_key in self._profile_cache:
                return self._profile_cache[cache_key]

        provider = self._get_provider(account.pool)
        role = self._get_role(account)
        allowed_tools = self._get_allowed_tools(account, role)
        env_vars = self._get_env_vars(account)

        # Get provider config
        provider_config = PROVIDER_CONFIGS.get(provider, {})

        # Build system prompt
        role_config = CAO_ROLES.get(role, CAO_ROLES["developer"])
        system_prompt = (
            f"You are a {role} agent in the Omega Engine Headless Subagent Pool.\n\n"
            f"{role_config['description']}\n\n"
            f"Account: {account.id}\n"
            f"Pool: {account.pool.value}\n"
            f"Model: {account.model}\n"
            f"Context Window: {account.context_window:,} tokens\n\n"
            f"Follow the Sovereign Mandates and Omega Engine protocols."
        )

        profile = AgentProfile(
            name=f"{account.id}-{role}",
            description=f"{account.pool.value} {role} agent ({account.model})",
            provider=provider,
            role=role,
            allowed_tools=allowed_tools,
            model=account.model,
            env_vars=env_vars,
            memory_scopes=role_config["memory_scopes"],
            system_prompt=system_prompt,
            metadata={
                "pool": account.pool.value,
                "account_id": account.id,
                "context_window": account.context_window,
                "capabilities": list(account.capabilities),
                "created_by": "ProfileManager",
            },
        )

        async with self._lock:
            self._profile_cache[cache_key] = profile

        # Persist profile
        await self._persist_profile(account.id, profile)

        return profile

    async def _persist_profile(self, account_id: str, profile: AgentProfile) -> None:
        """Persist profile to disk."""
        path = self.profiles_dir / f"{account_id}.md"
        await anyio.to_thread.run_sync(path.write_text, profile.to_markdown())

    async def get_profile(self, account_id: str) -> Optional[AgentProfile]:
        """Load profile from disk."""
        path = self.profiles_dir / f"{account_id}.md"
        if not path.exists():
            return None

        content = await anyio.to_thread.run_sync(path.read_text)
        return AgentProfile.from_markdown(content)

    async def get_launch_config(self, account: Account) -> LaunchConfig:
        """Get launch configuration for an account."""
        provider = self._get_provider(account.pool)
        provider_config = PROVIDER_CONFIGS.get(provider, {})
        binary = provider_config.get("binary", provider)

        # Build command based on provider
        if provider == "grok_cli":
            command = binary
            args = ["--model", account.model]
        elif provider == "copilot_cli":
            command = binary
            args = ["--model", account.model]
        elif provider == "cline_cli":
            command = binary
            args = ["--model", account.model]
        else:
            command = binary
            args = ["--model", account.model]

        # Get profile for env vars
        profile = await self.create_profile(account)

        return LaunchConfig(
            command=command,
            args=args,
            env=profile.env_vars,
            working_dir=os.getcwd(),
            tmux_session_name=f"omega-pool-{account.id}",
        )

    async def list_profiles(self) -> list[AgentProfile]:
        """List all persisted profiles."""
        profiles = []
        for path in self.profiles_dir.glob("*.md"):
            try:
                content = await anyio.to_thread.run_sync(path.read_text)
                profiles.append(AgentProfile.from_markdown(content))
            except Exception as e:
                logger.warning(f"Failed to load profile {path}: {e}")
        return profiles

    async def delete_profile(self, account_id: str) -> bool:
        """Delete a profile."""
        path = self.profiles_dir / f"{account_id}.md"
        if path.exists():
            await anyio.to_thread.run_sync(path.unlink)
            async with self._lock:
                # Remove from cache
                keys_to_remove = [k for k in self._profile_cache if k.startswith(account_id)]
                for k in keys_to_remove:
                    self._profile_cache.pop(k, None)
            return True
        return False

    async def update_profile_metadata(
        self,
        account_id: str,
        metadata: dict[str, Any],
    ) -> Optional[AgentProfile]:
        """Update profile metadata."""
        profile = await self.get_profile(account_id)
        if not profile:
            return None

        profile.metadata.update(metadata)
        await self._persist_profile(account_id, profile)

        async with self._lock:
            cache_key = f"{account_id}:{profile.model}"
            self._profile_cache[cache_key] = profile

        return profile


# --- Convenience Functions ---


async def create_profile_manager(
    profiles_dir: Optional[Path] = None,
    templates_dir: Optional[Path] = None,
) -> ProfileManager:
    """Create and initialize profile manager."""
    manager = ProfileManager(profiles_dir=profiles_dir, templates_dir=templates_dir)
    await manager.initialize()
    return manager


async def generate_all_profiles(
    manager: ProfileManager,
    accounts: list[Account],
) -> dict[str, AgentProfile]:
    """Generate profiles for all accounts."""
    profiles = {}
    for account in accounts:
        profiles[account.id] = await manager.create_profile(account)
    return profiles
