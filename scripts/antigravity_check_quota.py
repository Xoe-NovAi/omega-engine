#!/usr/bin/env python3
"""
Antigravity Quota Checker — Python port of the plugin's check-quota.mjs.

Queries Google's internal fetchAvailableModels endpoint per account
to return real-time remaining quota and reset times.

Usage:
    python3 scripts/antigravity_check_quota.py
    python3 scripts/antigravity_check_quota.py --account 2
    python3 scripts/antigravity_check_quota.py --json   # machine-readable output

⬡ OMEGA ⬡ QUOTACHECK ⬡ v1.0.0 ⬡ 2026-06-18
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import anyio
import httpx


# ── Constants ───────────────────────────────────────────────────────────────

# Default OAuth client credentials (public OAuth2 client — embedded in plugin)
# Can be overridden via environment variables for security hardening.
DEFAULT_CLIENT_ID = (
    "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
)
DEFAULT_CLIENT_SECRET = os.environ.get("ANTIGRAVITY_CLIENT_SECRET", "")

CLOUD_CODE_BASE = "https://cloudcode-pa.googleapis.com"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_AGENT = "antigravity/windows/amd64"
FALLBACK_PROJECT_ID = "bamboo-precept-lgxtn"

# Path to the accounts file
ACCOUNTS_FILE = (
    Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    / "opencode"
    / "antigravity-accounts.json"
)


# ── Data Types ──────────────────────────────────────────────────────────────


@dataclass
class AccountCredential:
    """An authenticated Google account from the accounts file."""

    email: Optional[str]
    refresh_token: str
    enabled: bool = True
    position: int = 0
    project_id: Optional[str] = None


@dataclass
class QuotaGroup:
    """Quota data for a model family (Claude, Gemini Flash, Gemini Pro)."""

    remaining: Optional[float] = None
    reset_time: Optional[str] = None
    model_count: int = 0


@dataclass
class AccountQuotaResult:
    """Full quota result for a single account."""

    position: int
    email: Optional[str]
    groups: Dict[str, QuotaGroup] = field(default_factory=dict)
    error: Optional[str] = None


# ── Credential Loading ──────────────────────────────────────────────────────


def load_accounts(path: Path = ACCOUNTS_FILE) -> List[AccountCredential]:
    """Load accounts from the local accounts file."""
    if not path.exists():
        print(f"ERROR: Accounts file not found at {path}", file=sys.stderr)
        print("Run 'opencode auth login' first to set up accounts.", file=sys.stderr)
        sys.exit(1)

    with open(path, "r") as f:
        data = json.load(f)

    accounts = []
    for i, entry in enumerate(data.get("accounts", [])):
        accounts.append(
            AccountCredential(
                email=entry.get("email"),
                refresh_token=entry.get("refreshToken", ""),
                enabled=entry.get("enabled", True),
                position=i,
                project_id=entry.get("projectId"),
            )
        )
    return accounts


# ── OAuth Token Refresh ────────────────────────────────────────────────────


async def refresh_access_token(
    client: httpx.AsyncClient,
    refresh_token: str,
) -> Optional[str]:
    """Refresh an OAuth access token from a refresh token."""
    client_id = os.environ.get(
        "ANTIGRAVITY_CLIENT_ID", DEFAULT_CLIENT_ID
    )
    client_secret = os.environ.get(
        "ANTIGRAVITY_CLIENT_SECRET", DEFAULT_CLIENT_SECRET
    )

    try:
        response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15.0,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("access_token")
    except Exception as exc:
        print(f"  Token refresh failed: {exc}", file=sys.stderr)
        return None


# ── Project ID Load ─────────────────────────────────────────────────────────


async def load_project_id(
    client: httpx.AsyncClient,
    access_token: str,
) -> str:
    """Load the Cloud Code project ID from the access token."""
    try:
        response = await client.post(
            f"{CLOUD_CODE_BASE}/v1internal:loadCodeAssist",
            json={"metadata": {"ideType": "ANTIGRAVITY"}},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            timeout=15.0,
        )
        if response.status_code != 200:
            return ""

        payload = response.json()
        if isinstance(payload.get("cloudaicompanionProject"), str):
            return payload["cloudaicompanionProject"]
        if isinstance(payload.get("cloudaicompanionProject"), dict):
            return payload["cloudaicompanionProject"].get("id", "")
        return ""
    except Exception:
        return ""


# ── Quota Query ─────────────────────────────────────────────────────────────


def classify_model_group(model_name: str) -> Optional[str]:
    """Classify a model name into a quota group."""
    lower = model_name.lower()
    if "claude" in lower:
        return "claude"
    if "gemini-3" not in lower:
        return None
    if "flash" in lower:
        return "gemini-flash"
    return "gemini-pro"


async def query_account_quota(
    client: httpx.AsyncClient,
    account: AccountCredential,
) -> AccountQuotaResult:
    """
    Query the fetchAvailableModels endpoint for a single account.

    Returns structured quota data for all model families.
    """
    result = AccountQuotaResult(
        position=account.position,
        email=account.email,
    )

    if not account.enabled:
        return result

    if not account.refresh_token:
        result.error = "No refresh token"
        return result

    # 1. Refresh access token
    access_token = await refresh_access_token(client, account.refresh_token)
    if not access_token:
        result.error = "Failed to refresh access token"
        return result

    # 2. Load project ID (needed for fetchAvailableModels)
    project_id = await load_project_id(client, access_token)
    if not project_id:
        project_id = account.project_id or FALLBACK_PROJECT_ID

    # 3. Fetch available models (which includes quota info)
    try:
        body = {"project": project_id} if project_id else {}
        response = await client.post(
            f"{CLOUD_CODE_BASE}/v1internal:fetchAvailableModels",
            json=body,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            timeout=15.0,
        )

        if response.status_code != 200:
            result.error = (
                f"fetchAvailableModels returned {response.status_code}: "
                f"{response.text[:200]}"
            )
            return result

        data = response.json()

        # 4. Extract quota per model family
        groups: Dict[str, QuotaGroup] = {}
        models: Dict[str, Any] = data.get("models", {})

        for model_name, info in models.items():
            group = classify_model_group(model_name)
            if not group:
                continue
            if not info or not info.get("quotaInfo"):
                continue

            quota = info["quotaInfo"]
            remaining = quota.get("remainingFraction")
            reset_time = quota.get("resetTime")

            if group not in groups:
                groups[group] = QuotaGroup(model_count=0)

            groups[group].model_count += 1

            # Take the minimum remaining fraction across models in the group
            current = groups[group].remaining
            if remaining is not None:
                if current is None or remaining < current:
                    groups[group].remaining = remaining

            # Take the earliest reset time
            if reset_time:
                current_reset = groups[group].reset_time
                if current_reset is None or reset_time < current_reset:
                    groups[group].reset_time = reset_time

        result.groups = groups

    except httpx.TimeoutException:
        result.error = "Request timed out"
    except Exception as exc:
        result.error = f"Query failed: {exc}"

    return result


# ── Quota Display ───────────────────────────────────────────────────────────


def format_duration(target_time_str: Optional[str]) -> str:
    """Format a duration from now to the target time."""
    if not target_time_str:
        return "unknown"
    try:
        # Parse ISO timestamp
        from datetime import datetime, timezone

        # Handle Z suffix
        ts = target_time_str.replace("Z", "+00:00")
        target = datetime.fromisoformat(ts)
        delta = target - datetime.now(timezone.utc)
        total_seconds = int(delta.total_seconds())
        if total_seconds <= 0:
            return "now"
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    except (ValueError, TypeError):
        return "unknown"


def print_account_result(result: AccountQuotaResult) -> None:
    """Print a human-readable quota result."""
    label = result.email or f"Account {result.position + 1}"
    print(f"\n{result.position + 1}. {label}")

    if result.error:
        print(f"   ERROR: {result.error}")
        return

    for group_name in ("claude", "gemini-pro", "gemini-flash"):
        group = result.groups.get(group_name)
        if not group or group.model_count == 0:
            continue

        remaining = group.remaining
        status = (
            "UNKNOWN"
            if remaining is None
            else "LIMITED"
            if remaining <= 0
            else "OK"
        )
        details = []
        if remaining is not None:
            details.append(f"remaining {remaining * 100:.0f}%")
        if group.reset_time:
            duration = format_duration(group.reset_time)
            details.append(f"resets in {duration}")

        suffix = f" ({', '.join(details)})" if details else ""
        print(f"   {group_name}: {status}{suffix}")


# ── Main ────────────────────────────────────────────────────────────────────


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check Antigravity account quotas"
    )
    parser.add_argument(
        "--account",
        type=int,
        help="Check only a specific account (1-based index)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=str(ACCOUNTS_FILE),
        help=f"Path to accounts file (default: {ACCOUNTS_FILE})",
    )
    args = parser.parse_args()

    accounts_file = Path(args.path)
    accounts = load_accounts(accounts_file)

    if not accounts:
        print("No accounts found.")
        sys.exit(1)

    # Filter by account index if specified
    if args.account is not None:
        idx = args.account - 1  # Convert to 0-based
        if idx < 0 or idx >= len(accounts):
            print(f"ERROR: Account {args.account} not found (have {len(accounts)} accounts)")
            sys.exit(1)
        accounts_to_check = [accounts[idx]]
    else:
        accounts_to_check = accounts

    # Query all accounts in parallel via anyio TaskGroup
    start = time.time()

    async with httpx.AsyncClient() as client:
        results = []
        async with anyio.create_task_group() as tg:
            for acct in accounts_to_check:
                results.append(None)  # placeholder

                async def _query(index: int, account=acct) -> None:
                    results[index] = await query_account_quota(client, account)

                tg.start_soon(_query, len(results) - 1)

    elapsed = time.time() - start

    # Output
    if args.json:
        # Machine-readable output
        json_results = []
        for result in results:
            result_dict = asdict(result)
            json_results.append(result_dict)
        print(json.dumps(json_results, indent=2, default=str))
    else:
        # Human-readable output
        for result in results:
            print_account_result(result)

        active = [r for r in results if not r.error]
        print(
            f"\n---\nChecked {len(results)} account(s) in {elapsed:.1f}s. "
            f"{len(active)} active, {len(results) - len(active)} errors."
        )


if __name__ == "__main__":
    anyio.run(main)
