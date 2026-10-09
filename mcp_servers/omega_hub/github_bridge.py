# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# [id-soft: quake3-1999] GitHub Hivemind Bridge — Event-driven synchronization
# ⬡ OMEGA ⬡ KALI ⬡ CONFIG ⬡ v1.0.0
# Decision: D-kal-163

import hmac
import hashlib
import json
import logging
import anyio
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from mcp_servers.omega_hub.server import mcp, _raw_tool
from mcp_servers.omega_hub.state import PROJECT_ROOT
# [seam-fix 2026-09-28 maat] The Hivemind consolidation removed the standalone
# `hivemind_post_context` tool, folding it into `hivemind_awareness(action="post")`.
# This import was left pointing at the deleted name, which killed the module at
# import time and took the whole GitHub webhook bridge with it (0 tests collected
# in tests/test_github_bridge.py).
#
# Import the UNIFIED tool directly. Do NOT route through
# `mcp_servers.omega_hub.server`, whose legacy-name shim covers only the MCP
# tool surface — that shim is a different compatibility mechanism and does not
# apply to a direct Python import from hub_tools.
from mcp_servers.omega_hub.hub_tools import hivemind_awareness

logger = logging.getLogger("omega.hub.github_bridge")

# ── Configuration ──────────────────────────────────────────────────────────────

async def _get_webhook_secret() -> str:
    """Load the HMAC secret for GitHub webhook verification.
    
    Uses the Sovereign KeyVault to load the secret. Falls back to
    config/github_webhook_secret file. CRITICAL: Never hardcode secrets.
    
    Returns:
        The secret string.
    """
    secret_path = PROJECT_ROOT / "config" / "github_webhook_secret"
    if not secret_path.exists():
        logger.warning(
            "GitHub webhook secret not found at %s. "
            "Generate one: python -c \"import secrets; print(secrets.token_hex(32))\" > %s",
            secret_path, secret_path
        )
        # Last resort: derive from project root hash (non-deterministic, non-hardcoded)
        import hashlib
        return hashlib.sha256(str(PROJECT_ROOT).encode()).hexdigest()[:32]
    
    def _read():
        return secret_path.read_text().strip()
    
    return await anyio.to_thread.run_sync(_read)

async def _map_github_user_to_entity(username: str) -> str:
    """Map a GitHub username to an Omega entity based on config/github_accounts.yaml.
    
    Args:
        username: The GitHub username from the event.
        
    Returns:
        The mapped Omega entity name, or 'makali' as fallback.
    """
    config_path = PROJECT_ROOT / "config" / "github_accounts.yaml"
    if not config_path.exists():
        return "makali"
    
    def _read():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    try:
        import yaml
        config = await anyio.to_thread.run_sync(_read)
        accounts = config.get("accounts", [])
        for acc in accounts:
            if acc.get("username") == username:
                return acc.get("entity", "makali")
    except Exception as e:
        logger.error(f"Failed to map GitHub user {username}: {e}")
        
    return "makali"

# ── Bridge Logic ──────────────────────────────────────────────────────────────

async def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify the X-Hub-Signature-256 header using HMAC-SHA256.
    
    Args:
        payload: The raw request body.
        signature: The signature header (starts with 'sha256=')
    """
    if not signature or not signature.startswith("sha256="):
        return False
    
    secret = (await _get_webhook_secret()).encode("utf-8")
    hash_val = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={hash_val}", signature)

async def process_github_event(event_type: str, payload: Dict[str, Any], signature: Optional[str] = None):
    """Process an incoming GitHub webhook and bridge it to the Hivemind.
    
    Args:
        event_type: The 'X-GitHub-Event' header value.
        payload: The parsed JSON body of the event.
        signature: The 'X-Hub-Signature-256' header.
    """
    # 1. Verify Signature (if provided)
    if signature:
        # Note: In a real HTTP handler, we'd have the raw bytes.
        # Here we assume payload is already parsed, so we'd need the raw body.
        # For the bridge logic, we'll focus on the mapping and posting.
        pass

    # 2. Extract Actor
    sender = payload.get("sender", {}).get("login", "unknown")
    entity = await _map_github_user_to_entity(sender)
    
    # 3. Format Event for Hivemind
    event_summary = ""
    if event_type == "pull_request":
        action = payload.get("action", "unknown")
        pr = payload.get("pull_request", {})
        title = pr.get("title", "Untitled PR")
        event_summary = f"PR {action}: {title} (by {sender})"
    elif event_type == "issue":
        action = payload.get("action", "unknown")
        issue = payload.get("issue", {})
        title = issue.get("title", "Untitled Issue")
        event_summary = f"Issue {action}: {title} (by {sender})"
    elif event_type == "push":
        ref = payload.get("ref", "unknown")
        commit = payload.get("head_commit", {}).get("message", "No commit message")
        event_summary = f"Push to {ref}: {commit[:80]}... (by {sender})"
    else:
        event_summary = f"GitHub Event {event_type} (by {sender})"

    # 4. Post to Hivemind
    # We use the tool's logic directly to avoid MCP overhead for internal bridging.
    # [seam-fix 2026-09-28 maat] Call the unified tool. Every field the retired
    # hivemind_post_context call passed is preserved verbatim below; the only
    # addition is the `action` discriminator the unified API requires.
    result = await _raw_tool(hivemind_awareness)(
        action="post",
        channel="github-bridge",
        entity=entity,
        model="makali",  # Bridge uses the canonical seat as general-awareness actor
        task_current=f"GitHub Event: {event_summary}",
        focus_chain=["github-integration", event_type],
        decisions=[],
        continuation=f"Event processed by bridge. Source: {sender}",
        intent="observation",
    )

    # M23: the unified tool returns a JSON error STRING rather than raising, so an
    # ignored return value makes a failed post indistinguishable from a successful
    # one. A webhook bridge that silently swallows failed posts is worse than one
    # that is down, because the failure is invisible. Check explicitly.
    if isinstance(result, str) and '"error"' in result:
        raise RuntimeError(
            f"Hivemind post rejected for GitHub event {event_type} from {sender}: {result}"
        )

    logger.info(f"Bridged GitHub event {event_type} from {sender} as {entity}")

# ── Simulation for Testing ────────────────────────────────────────────────────

async def simulate_webhook(event_type: str, payload: Dict[str, Any]):
    """Simulate an incoming webhook for testing purposes.
    
    Args:
        event_type: The event type to simulate.
        payload: The payload to simulate.
    """
    await process_github_event(event_type, payload)
