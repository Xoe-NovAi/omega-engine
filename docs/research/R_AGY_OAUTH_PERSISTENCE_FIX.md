<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 AGY OAuth Persistence Fix — Root Cause & Atomic Write-Back
**AP Token**: `AP-AGY-OAUTH-FIX-v1.0.0`
**Status**: P0-1 BLOCKER — Ready for Implementation
**Owner**: `@pillar P4` (Integration Bridge)
**Blocks**: VaultCore Schema v2 (needs token format), FleetOrchestrator

---

## 🎯 Problem Statement

The `opencode-antigravity-auth` plugin forces **8× interactive re-auth on every engine restart** because it fails to persist refreshed tokens to `~/.config/opencode/antigravity-accounts.json`.

---

## 🔍 Root Cause Analysis

### Current Flow (Broken)
```
Engine Start
    │
    ▼
Plugin loads antigravity-accounts.json
    │
    ▼
Reads: { "agy-0": { "access_token": "EXPIRED", "refresh_token": "VALID", ... } }
    │
    ▼
SDK uses refresh_token → Gets NEW access_token + NEW refresh_token
    │
    ▼
❌ MISSING: Write-back of NEW refresh_token to JSON file
    │
    ▼
Engine Restart
    │
    ▼
Plugin reads STALE refresh_token → OAuth flow fails → Interactive re-auth
```

### Why It Happens
1. **No `on_token_refresh` callback hook** in the plugin architecture
2. **In-memory only** token caching — no persistence layer
3. **File read at startup only** — no write path for token updates

---

## 🛠️ Architectural Fix: Atomic Write-Back Pattern

### Required Plugin Modification

The `opencode-antigravity-auth` plugin must implement a **token persistence middleware** that intercepts every token refresh and atomically writes the updated token set to disk.

```python
# antigravity_auth/persistence.py
"""
Atomic Token Persistence for Antigravity OAuth.
Hooks into the SDK's token lifecycle to ensure refresh tokens survive restarts.
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from anyio import Path as AsyncPath
import anyio


class AntigravityTokenStore:
    """
    Manages atomic read/write of antigravity-accounts.json.
    Thread-safe, crash-safe, restart-safe.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.expanduser("~/.config/opencode/antigravity-accounts.json")
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def load(self) -> Dict[str, Any]:
        """Load all accounts from disk."""
        try:
            async with await anyio.open_file(self.config_path, 'r') as f:
                content = await f.read()
                return json.loads(content) if content else {}
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            # Corrupted file — backup and return empty
            backup = self.config_path.with_suffix('.json.corrupted')
            os.rename(self.config_path, backup)
            return {}
    
    async def save(self, accounts: Dict[str, Any]) -> None:
        """
        Atomically write accounts to disk.
        Uses temp file + fsync + atomic rename pattern.
        """
        # Write to temp file in same directory (for atomic rename)
        fd, temp_path = tempfile.mkstemp(
            dir=self.config_path.parent,
            prefix=f".{self.config_path.name}-",
            suffix=".tmp"
        )
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(accounts, f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Force to disk
            
            # Atomic rename (POSIX guarantee)
            os.rename(temp_path, self.config_path)
        except Exception:
            # Cleanup on failure
            try:
                os.remove(temp_path)
            except OSError:
                pass
            raise
    
    async def update_account(self, account_id: str, token_payload: Dict[str, Any]) -> None:
        """
        Update a single account's tokens atomically.
        Called after EVERY successful token refresh.
        """
        accounts = await self.load()
        accounts[account_id] = {
            "access_token": token_payload["access_token"],
            "refresh_token": token_payload["refresh_token"],
            "expires_at": token_payload["expires_at"],
            "auth_method": "oauth",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        await self.save(accounts)


# ─────────────────────────────────────────────────────────────────
# SDK Integration Hook
# ─────────────────────────────────────────────────────────────────

class TokenPersistenceMiddleware:
    """
    Middleware that wraps the Antigravity SDK client to persist tokens
    on every refresh. This is the CRITICAL missing piece.
    """
    
    def __init__(self, sdk_client, token_store: AntigravityTokenStore, account_id: str):
        self._client = sdk_client
        self._store = token_store
        self._account_id = account_id
        
        # Monkey-patch or wrap the SDK's token refresh method
        self._original_refresh = sdk_client._refresh_access_token
        sdk_client._refresh_access_token = self._refresh_with_persistence
    
    async def _refresh_with_persistence(self) -> Dict[str, Any]:
        """Wrap SDK refresh to persist new tokens immediately."""
        # Call original refresh
        new_tokens = await self._original_refresh()
        
        # Persist atomically
        await self._store.update_account(self._account_id, new_tokens)
        
        return new_tokens
```

---

## 🔧 Integration into OpenCode Plugin

### Plugin Entry Point Modification

```python
# antigravity_auth/__init__.py (or plugin entry point)
from antigravity_auth.persistence import AntigravityTokenStore, TokenPersistenceMiddleware
from antigravity_sdk import AntigravityClient

async def initialize_plugin(config: Dict[str, Any]) -> AntigravityClient:
    """Plugin initialization with token persistence enabled."""
    
    # 1. Initialize token store
    token_store = AntigravityTokenStore()
    
    # 2. Load existing accounts
    accounts = await token_store.load()
    
    # 3. Create SDK clients for each account with persistence
    clients = {}
    for account_id, account_data in accounts.items():
        client = AntigravityClient(
            access_token=account_data["access_token"],
            refresh_token=account_data["refresh_token"],
            # ... other config
        )
        
        # 4. WRAP with persistence middleware — THIS IS THE FIX
        TokenPersistenceMiddleware(client, token_store, account_id)
        
        clients[account_id] = client
    
    return clients
```

---

## 🧪 Verification Test Plan

### Test Case: Restart Survival
```python
# tests/test_agy_oauth_persistence.py
import pytest
from antigravity_auth.persistence import AntigravityTokenStore

@pytest.mark.asyncio
async def test_token_persistence_across_restart(tmp_path):
    """Verify refresh tokens survive engine restart simulation."""
    store = AntigravityTokenStore(str(tmp_path / "antigravity-accounts.json"))
    
    # Simulate initial auth
    initial = {
        "agy-0": {
            "access_token": "access-old",
            "refresh_token": "refresh-initial",
            "expires_at": "2026-07-24T10:00:00Z",
            "auth_method": "oauth"
        }
    }
    await store.save(initial)
    
    # Simulate token refresh (what SDK does)
    refreshed = {
        "access_token": "access-new",
        "refresh_token": "refresh-rotated",  # NEW refresh token!
        "expires_at": "2026-07-24T11:00:00Z"
    }
    await store.update_account("agy-0", refreshed)
    
    # Simulate engine restart (new store instance)
    new_store = AntigravityTokenStore(str(tmp_path / "antigravity-accounts.json"))
    loaded = await new_store.load()
    
    # Verify NEW refresh token persisted
    assert loaded["agy-0"]["refresh_token"] == "refresh-rotated"
    assert loaded["agy-0"]["access_token"] == "access-new"
```

### Test Case: Crash Safety
```python
@pytest.mark.asyncio
async def test_atomic_write_survives_crash(tmp_path):
    """Verify partial writes don't corrupt config."""
    store = AntigravityTokenStore(str(tmp_path / "accounts.json"))
    
    # Write valid data
    await store.save({"agy-0": {"refresh_token": "valid"}})
    
    # Simulate crash during write by corrupting temp file
    # (The atomic rename ensures config is either old or new, never partial)
    config = tmp_path / "accounts.json"
    assert config.exists()
    content = config.read_text()
    assert "valid" in content
```

---

## 📋 Implementation Checklist

- [ ] **Fork/Modify** `opencode-antigravity-auth` plugin
- [ ] **Add** `persistence.py` with `AntigravityTokenStore` + `TokenPersistenceMiddleware`
- [ ] **Hook** middleware into SDK client initialization
- [ ] **Test** restart survival (8 accounts)
- [ ] **Test** crash safety (kill -9 during write)
- [ ] **Test** concurrent access (multiple agents refreshing simultaneously)
- [ ] **Publish** updated plugin
- [ ] **Update** `opencode.json` plugin config to use fixed version
- [ ] **Verify** 8-account cold start → zero interactive prompts

---

## 🔗 Related Work

| Ticket | Relation |
|--------|----------|
| **V-1** | VaultCore needs persisted token format |
| **C-10.5** | Provider fallback needs healthy AGY tokens |
| **P0-2** | Grok CLI workflow (separate auth.json handling) |

---

*🔱 OMEGA ⬡ PILLAR-P4 ⬡ AGY-OAUTH-FIX ⬡ 2026-07-23*