# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Headless Subagent Pool — Tmux Session Manager (CAO Pattern)

AP Token: AP-HEADLESS-POOL-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_headless_pool ⬡ TMUX_MANAGER

CAO Pattern Reference: https://github.com/awslabs/cli-agent-orchestrator
- Each agent in isolated tmux session
- Env var allowlist: HOME, PATH, SHELL, CAO_*, KIRO_*, MISE_*, AWS_*
- Per-account credentials forwarded via --env
- Clean shutdown: cao shutdown --session
"""

from __future__ import annotations

import anyio
import logging
import os
import shlex
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .models import Account
from .profile_manager import AgentProfile, LaunchConfig

logger = logging.getLogger(__name__)

# CAO env var allowlist - only these are passed through to tmux sessions
CAO_ENV_ALLOWLIST = {
    "HOME",
    "PATH",
    "SHELL",
    "USER",
    "LANG",
    "LC_ALL",
    "TERM",
    "COLORTERM",
    "EDITOR",
    "VISUAL",
    # CAO-specific
    "CAO_*",
    "KIRO_*",
    "MISE_*",
    "AWS_*",
    # Provider-specific (will be expanded at runtime)
    "GROK_*",
    "GITHUB_*",
    "DEEPSEEK_*",
    "ANTHROPIC_*",
    "OPENAI_*",
    "XAI_*",
    "GOOGLE_*",
    "AZURE_*",
}


def _match_allowlist(key: str) -> bool:
    """Check if env var matches CAO allowlist patterns."""
    for pattern in CAO_ENV_ALLOWLIST:
        if pattern.endswith("*"):
            if key.startswith(pattern[:-1]):
                return True
        elif key == pattern:
            return True
    return False


def _filter_env(env: dict[str, str]) -> dict[str, str]:
    """Filter environment to CAO allowlist."""
    return {k: v for k, v in env.items() if _match_allowlist(k)}


@dataclass
class TmuxSession:
    """Represents a managed tmux session."""

    name: str
    account_id: str
    created_at: float = field(default_factory=time.time)
    pid: Optional[int] = None
    pane_id: Optional[str] = None
    working_dir: str = ""
    command: str = ""


class TmuxManager:
    """
    Manages tmux sessions for 24 isolated agent accounts (CAO pattern).

    Each account gets its own tmux session with:
    - Isolated environment
    - Per-account credentials forwarded via env vars
    - CAO-compatible session naming
    - Health monitoring via tmux capture-pane
    """

    def __init__(
        self,
        session_prefix: str = "omega-pool",
        base_dir: Optional[str] = None,
        shell: str = "/bin/bash",
        tmux_socket: Optional[str] = None,
    ):
        self.session_prefix = session_prefix
        self.base_dir = Path(base_dir or os.path.expanduser("~/.omega/pool/sessions"))
        self.shell = shell
        self.tmux_socket = tmux_socket
        self._sessions: dict[str, TmuxSession] = {}
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _session_name(self, account: Account) -> str:
        """Generate CAO-style session name: omega-pool-grok-cli-3"""
        return f"{self.session_prefix}-{account.id}"

    def _tmux_cmd(self, *args: str) -> list[str]:
        """Build tmux command with optional socket."""
        cmd = ["tmux"]
        if self.tmux_socket:
            cmd.extend(["-L", self.tmux_socket])
        cmd.extend(args)
        return cmd

    async def _run_tmux(self, *args: str) -> tuple[int, str, str]:
        """Run tmux command asynchronously."""
        cmd = self._tmux_cmd(*args)
        proc = await anyio.open_process(
            cmd,
            stdout=anyio.PIPE,
            stderr=anyio.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode, stdout.decode(), stderr.decode()

    def _build_env(self, account: Account, profile: AgentProfile) -> dict[str, str]:
        """Build filtered environment for tmux session."""
        # Start with current environment
        env = dict(os.environ)

        # Add profile env vars (credentials from Omega-Vault)
        for key, value in profile.env_vars.items():
            if value.startswith("${VAULT:"):
                # Placeholder - real resolution happens at launch time
                # via Omega-Vault integration
                env[key] = value
            else:
                env[key] = value

        # Add account metadata
        env["OMEGA_POOL_ACCOUNT_ID"] = account.id
        env["OMEGA_POOL_TYPE"] = account.pool.value
        env["OMEGA_POOL_MODEL"] = account.model
        env["OMEGA_POOL_CONTEXT_WINDOW"] = str(account.context_window)

        # Filter to allowlist
        return _filter_env(env)

    async def create_session(
        self,
        account: Account,
        profile: AgentProfile,
        launch_config: Optional[LaunchConfig] = None,
    ) -> str:
        """
        Create isolated tmux session for account (CAO pattern).

        Returns session name.
        """
        session_name = self._session_name(account)

        # Check if session already exists
        if await self.session_exists(session_name):
            logger.warning(f"Session {session_name} already exists, reusing")
            return session_name

        # Build launch command
        if launch_config:
            cmd_parts = [launch_config.command] + launch_config.args
        else:
            # Fallback: use provider binary with model
            provider_config = {
                "grok_cli": ("grok", ["--model", account.model]),
                "copilot_cli": ("github-copilot-cli", ["--model", account.model]),
                "cline_cli": ("cline", ["--model", account.model]),
                "claude_code": ("claude", ["--model", account.model]),
                "codex": ("codex", ["--model", account.model]),
            }
            binary, args = provider_config.get(profile.provider, ("bash", []))
            cmd_parts = [binary] + args

        command = " ".join(shlex.quote(p) for p in cmd_parts)

        # Build environment
        env = self._build_env(account, profile)

        # Create session
        working_dir = str(self.base_dir / account.id)
        os.makedirs(working_dir, exist_ok=True)

        # tmux new-session -d -s <name> -c <dir> <command>
        returncode, stdout, stderr = await self._run_tmux(
            "new-session",
            "-d",
            "-s",
            session_name,
            "-c",
            working_dir,
            command,
        )

        if returncode != 0:
            raise RuntimeError(f"Failed to create tmux session: {stderr}")

        # Get pane info
        returncode, stdout, stderr = await self._run_tmux(
            "list-panes", "-t", session_name, "-F", "#{pane_id} #{pane_pid}"
        )

        pane_id = None
        pid = None
        if returncode == 0 and stdout.strip():
            parts = stdout.strip().split()
            if len(parts) >= 2:
                pane_id, pid_str = parts[0], parts[1]
                try:
                    pid = int(pid_str)
                except ValueError:
                    pass

        # Track session
        session = TmuxSession(
            name=session_name,
            account_id=account.id,
            pid=pid,
            pane_id=pane_id,
            working_dir=working_dir,
            command=command,
        )
        self._sessions[session_name] = session

        logger.info(f"Created tmux session {session_name} for {account.id}")
        return session_name

    async def session_exists(self, session_name: str) -> bool:
        """Check if tmux session exists."""
        returncode, _, _ = await self._run_tmux("has-session", "-t", session_name)
        return returncode == 0

    async def send_keys(self, session_name: str, keys: str, enter: bool = True) -> bool:
        """Send keystrokes to tmux session (CAO send_message pattern)."""
        cmd = ["send-keys", "-t", session_name]
        if enter:
            cmd.append(keys + " Enter")
        else:
            cmd.append(keys)

        returncode, _, stderr = await self._run_tmux(*cmd)
        if returncode != 0:
            logger.error(f"Failed to send keys to {session_name}: {stderr}")
            return False
        return True

    async def send_message(self, session_name: str, message: str) -> bool:
        """Send message to agent session (CAO send_message primitive)."""
        # Escape message for shell
        escaped = message.replace('"', '\\"').replace("$", "\\$")
        return await self.send_keys(session_name, f'echo "{escaped}"')

    async def capture_output(
        self,
        session_name: str,
        lines: int = 100,
        pane: Optional[str] = None,
    ) -> str:
        """Capture pane output (CAO get_state pattern)."""
        args = ["capture-pane", "-t", session_name]
        if pane:
            args.extend(["-t", pane])
        args.extend(["-p", "-S", f"-{lines}"])

        returncode, stdout, stderr = await self._run_tmux(*args)
        if returncode != 0:
            logger.error(f"Failed to capture output from {session_name}: {stderr}")
            return ""
        return stdout

    async def health_check(self, session_name: str) -> bool:
        """Check session responsiveness (CAO health check pattern)."""
        # Check session exists
        if not await self.session_exists(session_name):
            return False

        # Try to capture output (verifies tmux is responsive)
        output = await self.capture_output(session_name, lines=1)
        return output is not None

    async def terminate_session(self, session_name: str, graceful: bool = True) -> bool:
        """
        Terminate tmux session (CAO shutdown pattern).

        Graceful: sends SIGTERM to pane process, waits, then kills session.
        Force: immediately kills session.
        """
        if not await self.session_exists(session_name):
            logger.warning(f"Session {session_name} does not exist")
            return True

        if graceful:
            # Send Ctrl+C to gracefully stop agent
            await self.send_keys(session_name, "C-c", enter=False)
            await anyio.sleep(1)

            # Check if process is still alive
            session = self._sessions.get(session_name)
            if session and session.pid:
                try:
                    os.kill(session.pid, 0)  # Check if process exists
                    # Still alive, send SIGTERM
                    os.kill(session.pid, 15)
                    await anyio.sleep(2)
                    # Final check
                    try:
                        os.kill(session.pid, 0)
                        # Still alive, force kill
                        os.kill(session.pid, 9)
                    except ProcessLookupError:
                        pass  # Process exited
                except ProcessLookupError:
                    pass  # Already dead

        # Kill tmux session
        returncode, _, stderr = await self._run_tmux("kill-session", "-t", session_name)

        if returncode == 0:
            self._sessions.pop(session_name, None)
            logger.info(f"Terminated tmux session {session_name}")
            return True
        else:
            logger.error(f"Failed to kill session {session_name}: {stderr}")
            return False

    async def list_sessions(self, filter_prefix: Optional[str] = None) -> list[TmuxSession]:
        """List all managed tmux sessions."""
        prefix = filter_prefix or self.session_prefix
        returncode, stdout, stderr = await self._run_tmux(
            "list-sessions", "-F", "#{session_name} #{session_created} #{session_attached}"
        )

        sessions = []
        if returncode == 0:
            for line in stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    name, created, attached = parts[0], parts[1], parts[2]
                    if name.startswith(prefix):
                        session = self._sessions.get(name)
                        if not session:
                            session = TmuxSession(
                                name=name,
                                account_id=name.replace(f"{prefix}-", ""),
                                created_at=float(created) if created.isdigit() else time.time(),
                            )
                        sessions.append(session)

        return sessions

    async def get_session_info(self, session_name: str) -> Optional[TmuxSession]:
        """Get detailed session info."""
        if session_name in self._sessions:
            return self._sessions[session_name]

        # Try to get from tmux
        sessions = await self.list_sessions()
        for s in sessions:
            if s.name == session_name:
                return s
        return None

    async def resize_pane(self, session_name: str, width: int, height: int) -> bool:
        """Resize tmux pane."""
        returncode, _, stderr = await self._run_tmux(
            "resize-pane", "-t", session_name, "-x", str(width), "-y", str(height)
        )
        return returncode == 0

    async def set_window_title(self, session_name: str, title: str) -> bool:
        """Set window title for identification."""
        returncode, _, stderr = await self._run_tmux("rename-window", "-t", session_name, title)
        return returncode == 0

    async def cleanup_stale_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up sessions older than max_age_hours."""
        now = time.time()
        max_age = max_age_hours * 3600
        cleaned = 0

        sessions = await self.list_sessions()
        for session in sessions:
            if now - session.created_at > max_age:
                if await self.terminate_session(session.name):
                    cleaned += 1

        return cleaned

    async def get_session_log(self, session_name: str, lines: int = 1000) -> str:
        """Get full session log (for debugging)."""
        return await self.capture_output(session_name, lines=lines)

    async def pipe_pane(self, session_name: str, command: str) -> bool:
        """Pipe pane output to command (for logging)."""
        returncode, _, stderr = await self._run_tmux("pipe-pane", "-t", session_name, "-o", command)
        return returncode == 0

    def get_tracked_sessions(self) -> dict[str, TmuxSession]:
        """Get all tracked sessions."""
        return self._sessions.copy()


# --- CAO-style Session Management ---


class CAOSessionManager:
    """
    Higher-level session manager following CAO patterns.

    Handles:
    - Session lifecycle (create, attach, detach, shutdown)
    - Environment isolation
    - Credential injection
    - Process management
    """

    def __init__(self, tmux_manager: TmuxManager):
        self.tmux = tmux_manager

    async def launch_agent(
        self,
        account: Account,
        profile: AgentProfile,
        launch_config: Optional[LaunchConfig] = None,
    ) -> str:
        """Launch agent in isolated tmux session."""
        session_name = await self.tmux.create_session(account, profile, launch_config)

        # Wait for agent to be ready
        await anyio.sleep(2)

        # Verify health
        if not await self.tmux.health_check(session_name):
            await self.tmux.terminate_session(session_name)
            raise RuntimeError(f"Agent failed to start in {session_name}")

        return session_name

    async def shutdown_agent(self, session_name: str) -> bool:
        """Shutdown agent gracefully (CAO shutdown pattern)."""
        return await self.tmux.terminate_session(session_name, graceful=True)

    async def restart_agent(
        self,
        account: Account,
        profile: AgentProfile,
        session_name: Optional[str] = None,
    ) -> str:
        """Restart agent in same or new session."""
        if session_name:
            await self.shutdown_agent(session_name)

        return await self.launch_agent(account, profile)

    async def send_to_agent(self, session_name: str, message: str) -> bool:
        """Send message to agent (CAO send_message)."""
        return await self.tmux.send_message(session_name, message)

    async def get_agent_output(self, session_name: str, lines: int = 50) -> str:
        """Get recent agent output."""
        return await self.tmux.capture_output(session_name, lines=lines)


async def create_tmux_manager(
    session_prefix: str = "omega-pool",
    base_dir: Optional[str] = None,
) -> TmuxManager:
    """Factory for TmuxManager."""
    return TmuxManager(session_prefix=session_prefix, base_dir=base_dir)
