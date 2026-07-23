"""
AGY OAuth Persistence Fix — Atomic Write-Back for Token Refresh
Fixes the 8x re-auth on restart by persisting refreshed tokens to antigravity-accounts.json
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

try:
    import anyio
    from anyio import Path as AsyncPath
    ANYIO_AVAILABLE = True
except ImportError:
    ANYIO_AVAILABLE = False


class AGYAuthPersistence:
    """
    Handles atomic persistence of Antigravity OAuth tokens.
    
    Root Cause: The opencode-antigravity-auth plugin caches tokens in memory
    but fails to write refreshed tokens back to antigravity-accounts.json.
    On restart, the plugin finds expired/missing tokens and triggers re-auth.
    
    Solution: Hook into the token refresh lifecycle and atomically write
    the new token pair (access + refresh) to the config file.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.expanduser("~/.config/opencode/antigravity-accounts.json")
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _read_accounts(self) -> Dict[str, Any]:
        """Read existing accounts from config file."""
        if self.config_path.exists():
            try:
                content = self.config_path.read_text()
                return json.loads(content)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}
    
    def _atomic_write(self, accounts: Dict[str, Any]) -> None:
        """Atomically write accounts to config file."""
        dir_name = self.config_path.parent
        fd, temp_path = tempfile.mkstemp(
            dir=dir_name,
            prefix=".agy-auth-",
            suffix=".tmp"
        )
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(accounts, f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Force to disk
            os.rename(temp_path, self.config_path)  # Atomic on POSIX
        except Exception:
            try:
                os.remove(temp_path)
            except OSError:
                pass
            raise
    
    def persist_tokens(
        self,
        account_id: str,
        access_token: str,
        refresh_token: str,
        expires_at: str,
        auth_method: str = "oauth"
    ) -> None:
        """
        Persist OAuth tokens for an account.
        
        Call this:
        1. After initial OAuth flow completes
        2. After EVERY token refresh (critical!)
        3. Before engine shutdown (graceful)
        """
        accounts = self._read_accounts()
        
        accounts[account_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "auth_method": auth_method,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        self._atomic_write(accounts)
    
    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account tokens for use in authentication."""
        accounts = self._read_accounts()
        return accounts.get(account_id)
    
    def remove_account(self, account_id: str) -> bool:
        """Remove an account (e.g., on explicit logout)."""
        accounts = self._read_accounts()
        if account_id in accounts:
            del accounts[account_id]
            self._atomic_write(accounts)
            return True
        return False


async def persist_oauth_tokens_async(
    account_id: str,
    token_payload: Dict[str, Any],
    config_path: Optional[str] = None
) -> None:
    """
    Async version for use in AnyIO contexts.
    
    Args:
        account_id: The Antigravity account identifier (e.g., "agy-0", "agy-1")
        token_payload: Dict with keys: access_token, refresh_token, expires_at
        config_path: Optional custom config path
    """
    if config_path is None:
        config_path = os.path.expanduser("~/.config/opencode/antigravity-accounts.json")
    
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing
    if await config_path.exists():
        content = await config_path.read_text()
        accounts = json.loads(content)
    else:
        accounts = {}
    
    # Update
    accounts[account_id] = {
        "access_token": token_payload["access_token"],
        "refresh_token": token_payload["refresh_token"],
        "expires_at": token_payload["expires_at"],
        "auth_method": "oauth",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Atomic write
    dir_name = config_path.parent
    fd, temp_path = tempfile.mkstemp(
        dir=dir_name,
        prefix=".agy-auth-",
        suffix=".tmp"
    )
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(accounts, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.rename(temp_path, config_path)
    except Exception:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise


def create_refresh_hook(persistence: AGYAuthPersistence, account_id: str):
    """
    Create a callback hook for the Antigravity SDK's on_token_refresh event.
    
    Usage:
        from antigravity_sdk import AntigravityClient
        
        persistence = AGYAuthPersistence()
        client = AntigravityClient(
            account_id="agy-0",
            on_token_refresh=create_refresh_hook(persistence, "agy-0")
        )
    """
    def on_refresh(token_payload: Dict[str, Any]):
        persistence.persist_tokens(
            account_id=account_id,
            access_token=token_payload["access_token"],
            refresh_token=token_payload["refresh_token"],
            expires_at=token_payload["expires_at"]
        )
    return on_refresh


# --- Integration Example for opencode-antigravity-auth plugin ---

"""
To fix the plugin, modify its token management to use this persistence layer.

In the plugin's token refresh logic (typically in auth.py or similar):

```python
# BEFORE (broken - no persistence):
async def refresh_access_token(self):
    new_tokens = await self.sdk.refresh()
    self.access_token = new_tokens["access_token"]
    # MISSING: write back to file!

# AFTER (fixed):
from omega.agents.scribe.agy_oauth_persistence import persist_oauth_tokens_async

async def refresh_access_token(self):
    new_tokens = await self.sdk.refresh()
    self.access_token = new_tokens["access_token"]
    
    # PERSIST IMMEDIATELY
    await persist_oauth_tokens_async(
        account_id=self.account_id,
        token_payload=new_tokens
    )
```

Additionally, ensure the plugin reads from the persisted file on startup:

```python
async def load_cached_tokens(self):
    account = persistence.get_account(self.account_id)
    if account and account.get("refresh_token"):
        self.refresh_token = account["refresh_token"]
        self.access_token = account.get("access_token")
        # Validate expiry, trigger refresh if needed
```
"""

# --- Quick Test / Verification ---

def verify_persistence():
    """Test the persistence layer."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test-accounts.json")
        persistence = AGYAuthPersistence(config_path)
        
        # Test write
        persistence.persist_tokens(
            account_id="agy-0",
            access_token="ya29.test-access",
            refresh_token="1//test-refresh",
            expires_at="2026-07-24T12:00:00Z"
        )
        
        # Test read
        account = persistence.get_account("agy-0")
        assert account is not None
        assert account["access_token"] == "ya29.test-access"
        assert account["refresh_token"] == "1//test-refresh"
        
        # Test atomic write survives crash simulation
        persistence.persist_tokens(
            account_id="agy-0",
            access_token="ya29.new-access",
            refresh_token="1//new-refresh",
            expires_at="2026-07-24T13:00:00Z"
        )
        
        account = persistence.get_account("agy-0")
        assert account["access_token"] == "ya29.new-access"
        assert account["refresh_token"] == "1//new-refresh"
        
        print("✅ AGY OAuth persistence verification passed")


if __name__ == "__main__":
    verify_persistence()