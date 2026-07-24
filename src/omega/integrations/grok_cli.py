"""
Grok CLI Integration for Omega Engine

Provides subprocess management for `grok agent stdio` (ACP stdio transport)
and `grok -p` (quick prompt) via AnyIO open_process.

This is the Carmack Mode P0-2 implementation: minimal, working scaffold
for immediate dev leverage. Full ACP multiplexer deferred (D-435).

Architecture:
- Each Grok account = isolated process via `GROK_HOME=~/.grok-fleet/acct-{N}/`
- JSON-RPC 2.0 framing on stdin/stdout for ACP stdio
- Quota polling via gRPC-web `GetGrokCreditsConfig` (stubbed)
- No mid-stream 402 recovery yet — that's the multiplexer's job (deferred)
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Optional

import anyio
from anyio import open_process
from anyio.streams.text import TextReceiveStream, TextSendStream


@dataclass
class QuotaInfo:
    """Grok quota information from gRPC-web GetGrokCreditsConfig."""
    credits_remaining: float
    credits_total: float
    reset_time_unix: Optional[int] = None
    model: str = "grok-3"
    exhausted: bool = False

    @property
    def percent_remaining(self) -> float:
        if self.credits_total <= 0:
            return 0.0
        return max(0.0, min(1.0, self.credits_remaining / self.credits_total))


@dataclass
class GrokAccountConfig:
    """Configuration for a single Grok CLI account."""
    account_id: int  # 1-8
    grok_home: Path
    model: str = "grok-3"
    timeout_seconds: float = 60.0

    @property
    def env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["GROK_HOME"] = str(self.grok_home)
        return env


class GrokCLIError(Exception):
    """Base exception for Grok CLI errors."""
    pass


class GrokCLITimeoutError(GrokCLIError):
    """Raised when Grok CLI request times out."""
    pass


class GrokCLIQuotaExhaustedError(GrokCLIError):
    """Raised when Grok quota is exhausted (402 equivalent)."""
    def __init__(self, message: str, quota_info: Optional[QuotaInfo] = None):
        super().__init__(message)
        self.quota_info = quota_info


class GrokProcessError(GrokCLIError):
    """Raised when Grok subprocess fails."""
    def __init__(self, message: str, exit_code: Optional[int] = None, stderr: str = ""):
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


class GrokCLIClient:
    """
    Async client for Grok CLI via ACP stdio transport.
    
    Uses AnyIO open_process for proper async subprocess management.
    Each instance manages one Grok account's persistent `grok agent stdio` process.
    """
    
    def __init__(self, config: GrokAccountConfig):
        self.config = config
        self._process: Optional[anyio.Process] = None
        self._stdin: Optional[TextSendStream] = None
        self._stdout: Optional[TextReceiveStream] = None
        self._request_id = 0
        self._pending: dict[int, anyio.Event] = {}
        self._responses: dict[int, dict[str, Any]] = {}
        self._reader_task: Optional[anyio.Task] = None
        self._started = False
    
    async def start(self) -> None:
        """Start the persistent `grok agent stdio` process."""
        if self._started:
            return
        
        # Ensure GROK_HOME directory exists
        self.config.grok_home.mkdir(parents=True, exist_ok=True)
        
        # Start the process
        self._process = await open_process(
            ["grok", "agent", "stdio"],
            env=self.config.env,
        )
        
        # Wrap streams for text I/O
        self._stdin = TextSendStream(self._process.stdout)
        self._stdout = TextReceiveStream(self._process.stderr)
        
        # Start background reader for JSON-RPC responses
        self._reader_task = anyio.create_task_group()
        self._reader_task.start_soon(self._read_responses)
        
        # Initialize ACP session
        await self._initialize_acp()
        self._started = True
    
    async def _initialize_acp(self) -> None:
        """Send ACP initialize request."""
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "omega-engine",
                    "version": "0.1.0"
                }
            }
        }
        await self._send_request(init_request)
        response = await self._wait_for_response(init_request["id"])
        if "error" in response:
            raise GrokProcessError(f"ACP initialize failed: {response['error']}")
    
    async def _read_responses(self) -> None:
        """Background task to read JSON-RPC responses from stdout."""
        if not self._stdout:
            return
        
        async for line in self._stdout:
            line = line.strip()
            if not line:
                continue
            try:
                response = json.loads(line)
                req_id = response.get("id")
                if req_id is not None and req_id in self._pending:
                    self._responses[req_id] = response
                    self._pending[req_id].set()
            except json.JSONDecodeError:
                # Non-JSON output (logs, etc.) - ignore
                pass
    
    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id
    
    async def _send_request(self, request: dict[str, Any]) -> None:
        """Send a JSON-RPC request to the Grok process."""
        if not self._stdin:
            raise GrokProcessError("Process not started")
        line = json.dumps(request) + "\n"
        await self._stdin.send(line)
    
    async def _wait_for_response(self, req_id: int, timeout: float = 30.0) -> dict[str, Any]:
        """Wait for a response to a specific request ID."""
        event = anyio.Event()
        self._pending[req_id] = event
        try:
            with anyio.move_on_after(timeout) as scope:
                await event.wait()
            if scope.cancelled_caught:
                raise GrokCLITimeoutError(f"Request {req_id} timed out after {timeout}s")
            return self._responses.pop(req_id, {"error": {"message": "No response received"}})
        finally:
            self._pending.pop(req_id, None)
    
    async def prompt(self, text: str, model: Optional[str] = None) -> str:
        """
        Send a prompt to Grok via ACP stdio and return the response.
        
        Args:
            text: The prompt text
            model: Optional model override (default: config.model)
            
        Returns:
            The model's response text
            
        Raises:
            GrokCLIQuotaExhaustedError: If quota exhausted (check error message)
            GrokCLITimeoutError: If request times out
            GrokProcessError: If process fails
        """
        if not self._started:
            await self.start()
        
        req_id = self._next_id()
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "prompt",
            "params": {
                "text": text,
                "model": model or self.config.model
            }
        }
        
        await self._send_request(request)
        response = await self._wait_for_response(req_id, timeout=self.config.timeout_seconds)
        
        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            # Check for quota exhaustion (402 equivalent)
            if "exhausted" in error_msg.lower() or "quota" in error_msg.lower() or "balance" in error_msg.lower():
                raise GrokCLIQuotaExhaustedError(error_msg)
            raise GrokProcessError(f"Grok error: {error_msg}")
        
        # Extract text from ACP response
        result = response.get("result", {})
        if isinstance(result, dict):
            return result.get("text", str(result))
        return str(result)
    
    async def check_quota(self) -> QuotaInfo:
        """
        Check quota for this account via gRPC-web GetGrokCreditsConfig.
        
        NOTE: This is a STUB. Real implementation requires:
        - gRPC-web client (connectrpc/connect-web or similar)
        - Proper authentication headers
        - Endpoint: https://api.x.ai/credits/v1/GetGrokCreditsConfig
        
        For now, returns a mock QuotaInfo. The real quota check
        will be implemented when the ACP multiplexer is built (deferred).
        """
        # TODO: Implement real gRPC-web quota check
        # For now, return mock data
        return QuotaInfo(
            credits_remaining=100.0,
            credits_total=100.0,
            model=self.config.model,
            exhausted=False
        )
    
    async def close(self) -> None:
        """Cleanly shut down the Grok process."""
        if self._reader_task:
            self._reader_task.cancel_scope.cancel()
        if self._process:
            self._process.terminate()
            await self._process.wait()
        self._started = False


class GrokQuickPrompt:
    """
    Lightweight wrapper for `grok -p "prompt"` one-shot prompts.
    
    Does not maintain persistent process — spawns new process each call.
    Useful for quick checks, not for conversation continuity.
    """
    
    def __init__(self, config: GrokAccountConfig):
        self.config = config
    
    async def prompt(self, text: str, model: Optional[str] = None) -> str:
        """Run `grok -p "text"` and return stdout."""
        cmd = ["grok", "-p", text]
        if model:
            cmd.extend(["-m", model])
        
        process = await open_process(cmd, env=self.config.env)
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise GrokProcessError(
                f"grok -p failed with exit code {process.returncode}",
                exit_code=process.returncode,
                stderr=stderr.decode() if stderr else ""
            )
        
        return stdout.decode().strip()


class GrokFleetManager:
    """
    Manages a fleet of 8 Grok CLI accounts.
    
    Carmack Mode: Simple account isolation via GROK_HOME directories.
    Full ACP multiplexer with mid-stream 402 recovery deferred (D-435).
    """
    
    def __init__(
        self,
        base_grok_home: Path = Path.home() / ".grok-fleet",
        model: str = "grok-3",
        timeout_seconds: float = 60.0
    ):
        self.base_grok_home = base_grok_home
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._clients: dict[int, GrokCLIClient] = {}
        self._quick_prompts: dict[int, GrokQuickPrompt] = {}
    
    def _get_config(self, account_id: int) -> GrokAccountConfig:
        if not 1 <= account_id <= 8:
            raise ValueError(f"account_id must be 1-8, got {account_id}")
        return GrokAccountConfig(
            account_id=account_id,
            grok_home=self.base_grok_home / f"acct-{account_id}",
            model=self.model,
            timeout_seconds=self.timeout_seconds
        )
    
    def get_client(self, account_id: int) -> GrokCLIClient:
        """Get or create persistent ACP client for an account."""
        if account_id not in self._clients:
            self._clients[account_id] = GrokCLIClient(self._get_config(account_id))
        return self._clients[account_id]
    
    def get_quick_prompt(self, account_id: int) -> GrokQuickPrompt:
        """Get or create quick prompt wrapper for an account."""
        if account_id not in self._quick_prompts:
            self._quick_prompts[account_id] = GrokQuickPrompt(self._get_config(account_id))
        return self._quick_prompts[account_id]
    
    async def prompt(self, account_id: int, text: str, model: Optional[str] = None) -> str:
        """Send prompt to specific account via persistent ACP connection."""
        client = self.get_client(account_id)
        return await client.prompt(text, model)
    
    async def quick_prompt(self, account_id: int, text: str, model: Optional[str] = None) -> str:
        """Send prompt via one-shot `grok -p` (no conversation continuity)."""
        quick = self.get_quick_prompt(account_id)
        return await quick.prompt(text, model)
    
    async def check_quota(self, account_id: int) -> QuotaInfo:
        """Check quota for specific account."""
        client = self.get_client(account_id)
        return await client.check_quota()
    
    async def check_all_quotas(self) -> dict[int, QuotaInfo]:
        """Check quota for all 8 accounts."""
        results = {}
        for account_id in range(1, 9):
            try:
                results[account_id] = await self.check_quota(account_id)
            except Exception as e:
                results[account_id] = QuotaInfo(
                    credits_remaining=0.0,
                    credits_total=0.0,
                    model=self.model,
                    exhausted=True
                )
        return results
    
    async def find_available_account(self) -> Optional[int]:
        """Find first account with quota remaining."""
        quotas = await self.check_all_quotas()
        for account_id, quota in quotas.items():
            if not quota.exhausted and quota.credits_remaining > 0:
                return account_id
        return None
    
    async def close_all(self) -> None:
        """Close all persistent connections."""
        for client in self._clients.values():
            await client.close()
        self._clients.clear()


# Convenience function for quick one-liner usage
async def grok_prompt(
    text: str,
    account_id: int = 1,
    base_grok_home: Optional[Path] = None,
    model: str = "grok-3"
) -> str:
    """
    Quick one-liner: `await grok_prompt("refactor this function")`
    
    Uses persistent ACP connection for conversation continuity.
    """
    base = base_grok_home or Path.home() / ".grok-fleet"
    fleet = GrokFleetManager(base_grok_home=base, model=model)
    try:
        return await fleet.prompt(account_id, text)
    finally:
        await fleet.close_all()


# Module exports
__all__ = [
    "GrokCLIClient",
    "GrokQuickPrompt", 
    "GrokFleetManager",
    "GrokAccountConfig",
    "QuotaInfo",
    "GrokCLIError",
    "GrokCLITimeoutError",
    "GrokCLIQuotaExhaustedError",
    "GrokProcessError",
    "grok_prompt",
]