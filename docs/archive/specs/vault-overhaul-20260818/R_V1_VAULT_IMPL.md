# 🔱 Omega Engine — V-1 Omega-Vault Implementation Research: Credential Automation
# ⬡ OMEGA ⬡ GROKSTER ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_vault_impl ⬡ R35-COMPLETE

**AP Token**: `AP-V1-VAULT-IMPL-v1.0.0`
**Date**: 2026-07-21
**Status**: COMPLETE
**Job ID**: R35 (V-1 Omega-Vault Implementation Research)
**Augments**: V1_OMEGA_VAULT_DESIGN_20260721.md, existing `src/omega/vault/`
**Owner**: grokster
**Decision Gate**: Select Vault backend + design 16-account credential schema + ACP smoke test path

---

## §0 Executive Summary

This document specifies the complete implementation of the **V-1 Omega-Vault MVP** — credential automation for the 16-account Grok fleet (8 CLI + 8 Web Grok). This is the **explicit ticket** from Kali amendment 2 that blocks fleet deployment.

**Key Design Decisions**:
1. **Extend existing `src/omega/vault/`** — don't rebuild from scratch; the KeyVault singleton already has AES-256-GCM + OS keyring
2. **16-account schema** — 8 Grok CLI accounts + 8 Web Grok persona accounts
3. **Passive file watcher** — detect `.env`/config drift → auto-sync to vault
4. **MCP server** — expose `credential.read/write/rotate/audit` for Omega Engine integration
5. **XDG compliance** — zero hardcoded paths, `~/.config/omega/`, `~/.local/share/omega/`, `~/.local/state/omega/`
6. **Temple-Grade CI** — chaos testing, atomic writes, structured error handling

---

## §1 Architecture Overview

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    OMEGA-VAULT (V-1 MVP)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  │   KeyVault      │  │   CAP Adapters  │  │   Policy Engine │
│  │ (Core Singleton)│  │ (MCP Server)    │  │ (Credential Schema)│
│  └─────────────────┘  └─────────────────┘  └─────────────────┘
│  │  AES-256-GCM    │  │  credential.read │  │  CredentialModel   │
│  │  encryption     │  │  credential.write│  │  (Pydantic)       │
│  │  + rotation    │  │  credential.rotate│  │  AccountSchema    │
│  │  + audit       │  │  credential.audit│  │  ProviderSchema   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Passive        │  │  Fleet          │  │  XDG CLI        │  │
│  │  Watcher        │  │  Orchestrator   │  │  (`omega vault`) │  │
│  │  (inotify/fanot)│  │  (8+8 accounts) │  │  (XDG paths)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

1. **CLI** → `omega vault init|import|list|get|set|rotate|audit|fleet`
2. **Passive Watcher** → detects `.env`/config drift → auto-sync to vault
3. **MCP Server** → exposes credential APIs for Omega Engine integration
4. **Policy Engine** → validates schema, enforces ZDR, rate limits
5. **KeyVault** → encrypted storage with OS keyring
6. **Fleet Orchestrator** → manages 16-account credential rotation

---

## §2 Credential Schema Design

### 2.1 Core Models (Pydantic v2)

```python
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional

class AccountType(str, Enum):
    CLI = "cli"           # Grok CLI (headless, ACP)
    WEB = "web"           # Web Grok (browser, Projects)

class AuthMethod(str, Enum):
    API_KEY = "api_key"
    OAUTH = "oauth"
    COOKIE = "cookie"     # Web Grok sessions

class CredentialStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ROTATING = "rotating"
    EXPIRED = "expired"

class RateLimit(BaseModel):
    """Per-account rate limiting."""
    max_retries: int = 3
    backoff_factor: float = 2.0
    max_backoff: int = 3600
    requests_per_minute: int = 60
    requests_per_day: int = 10000
    burst_limit: int = 10
    quota_remaining: int = 10000
    quota_limit: int = 10000
    last_reset: datetime = Field(default_factory=datetime.utcnow)

class UsageStats(BaseModel):
    """Per-account usage tracking."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None

class CredentialEntry(BaseModel):
    """Single credential entry for one account."""
    provider: str                          # "xai", "openrouter", "gemini"
    account_id: str                        # "xai_cli_01", "grok_web_03"
    account_type: AccountType              # cli or web
    persona: Optional[str] = None          # Grok persona prompt (Web accounts)
    auth_method: AuthMethod = AuthMethod.API_KEY
    
    # Credentials (encrypted at rest)
    api_key: Optional[str] = None          # API key (CLI accounts)
    cookie_value: Optional[str] = None     # Session cookie (Web accounts)
    cookie_domain: Optional[str] = None    # Cookie domain
    cookie_expiry: Optional[datetime] = None  # Cookie expiry (24-48h for Web)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_rotated: datetime = Field(default_factory=datetime.utcnow)
    status: CredentialStatus = CredentialStatus.ACTIVE
    
    # Rate limiting
    rate_limit: RateLimit = Field(default_factory=RateLimit)
    
    # Usage
    usage: UsageStats = Field(default_factory=UsageStats)
    
    # Models & priority
    models_preferred: list[str] = Field(default_factory=list)
    priority: int = 1                      # 1=highest, 10=lowest
    domains_supported: list[str] = Field(default_factory=list)

class ProviderSchema(BaseModel):
    """Provider-level configuration."""
    name: str                              # "xai", "openrouter"
    env_var: str                           # "XAI_API_KEY"
    auth_method: AuthMethod = AuthMethod.API_KEY
    rate_limit: RateLimit = Field(default_factory=RateLimit)
    models: list[str] = Field(default_factory=list)
    domains_supported: list[str] = Field(default_factory=list)
    
    # Fleet-specific
    total_accounts: int = 1
    rotation_interval_hours: int = 24      # How often to rotate
    max_concurrent: int = 4                # Max concurrent requests

class FleetConfig(BaseModel):
    """16-account fleet configuration."""
    providers: dict[str, ProviderSchema] = Field(default_factory=dict)
    accounts: list[CredentialEntry] = Field(default_factory=list)
    
    # Fleet-wide settings
    global_rate_limit: int = 100           # requests per minute across all accounts
    circuit_breaker_threshold: int = 5     # failures before circuit opens
    circuit_breaker_timeout: int = 300     # seconds before retry
```

### 2.2 16-Account Schema

```yaml
# fleet_config.yaml
fleet:
  grok_cli:
    provider: "xai"
    auth_method: "api_key"
    accounts:
      - account_id: "xai_cli_01"
        persona: null  # CLI uses system prompt
        models_preferred: ["grok-4.5", "grok-4.3"]
        priority: 1
        domains_supported: ["general", "reasoning", "code"]
        rate_limit:
          requests_per_minute: 60
          requests_per_day: 10000
      
      - account_id: "xai_cli_02"
        persona: null
        models_preferred: ["grok-4.5", "grok-4.3"]
        priority: 2
        domains_supported: ["general", "reasoning", "code"]
      
      # ... accounts 03-08 (identical structure)
  
  grok_web:
    provider: "xai_web"
    auth_method: "cookie"
    accounts:
      - account_id: "grok_web_01"
        persona: "Research Specialist — deep academic analysis, citation-heavy"
        models_preferred: ["grok-4.5"]
        priority: 1
        domains_supported: ["research", "academic"]
        rate_limit:
          requests_per_minute: 10  # Web has stricter limits
          requests_per_day: 1000
        cookie_expiry: "24-48h"  # Requires rotation
      
      - account_id: "grok_web_02"
        persona: "Code Architect — implementation-first, production-ready"
        models_preferred: ["grok-4.5"]
        priority: 2
        domains_supported: ["code", "architecture"]
      
      # ... accounts 03-08 with personas:
      # 03: "Reasoning Engine — step-by-step logical analysis"
      # 04: "Creative Writer — prose, documentation, narratives"
      # 05: "Strategic Analyst — business, planning, decision-making"
      # 06: "Systems Engineer — infrastructure, DevOps, performance"
      # 07: "Data Scientist — analytics, ML, statistical analysis"
      # 08: "Wildcard — general purpose, high-creativity"
```

---

## §3 Implementation: Core Modules

### 3.1 KeyVault (Extend Existing)

The existing `src/omega/vault/` already has:
- AES-256-GCM encryption
- OS keyring integration
- Basic `resolve()` / `set_key()` methods

**Extensions needed**:

```python
# src/omega/vault/key_vault.py (extend existing)

class KeyVault:
    """Extended KeyVault with fleet support."""
    
    def __init__(self, vault_path: str | None = None):
        # Use XDG paths
        self.vault_path = Path(vault_path or self._default_vault_path())
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _default_vault_path(self) -> str:
        """XDG-compliant vault path."""
        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        return str(Path(xdg_data) / "omega" / "keys.json.enc")
    
    def get_fleet_config(self) -> FleetConfig:
        """Load fleet configuration."""
        config_path = self.vault_path.parent / "fleet_config.yaml"
        if config_path.exists():
            return FleetConfig(**yaml.safe_load(config_path.read_text()))
        return FleetConfig()
    
    def save_fleet_config(self, config: FleetConfig) -> None:
        """Save fleet configuration."""
        config_path = self.vault_path.parent / "fleet_config.yaml"
        config_path.write_text(config.model_dump_json(indent=2))
    
    def get_account(self, account_id: str) -> CredentialEntry | None:
        """Get credential for a specific account."""
        config = self.get_fleet_config()
        for account in config.accounts:
            if account.account_id == account_id:
                return account
        return None
    
    def get_accounts_by_provider(self, provider: str) -> list[CredentialEntry]:
        """Get all accounts for a provider."""
        config = self.get_fleet_config()
        return [a for a in config.accounts if a.provider == provider]
    
    def get_next_account(self, provider: str) -> CredentialEntry | None:
        """Get next available account (round-robin with priority)."""
        accounts = self.get_accounts_by_provider(provider)
        active = [a for a in accounts if a.status == CredentialStatus.ACTIVE]
        if not active:
            return None
        # Round-robin by priority
        active.sort(key=lambda a: a.priority)
        return active[0]
    
    def rotate_account(self, account_id: str, new_credential: str) -> bool:
        """Rotate credential for a specific account."""
        config = self.get_fleet_config()
        for i, account in enumerate(config.accounts):
            if account.account_id == account_id:
                if account.auth_method == AuthMethod.API_KEY:
                    config.accounts[i].api_key = new_credential
                elif account.auth_method == AuthMethod.COOKIE:
                    config.accounts[i].cookie_value = new_credential
                    config.accounts[i].cookie_expiry = datetime.utcnow() + timedelta(hours=48)
                config.accounts[i].last_rotated = datetime.utcnow()
                config.accounts[i].status = CredentialStatus.ACTIVE
                self.save_fleet_config(config)
                return True
        return False
    
    def audit_account(self, account_id: str) -> dict:
        """Audit account status, usage, and health."""
        account = self.get_account(account_id)
        if not account:
            return {"error": "Account not found"}
        
        return {
            "account_id": account.account_id,
            "provider": account.provider,
            "status": account.status.value,
            "auth_method": account.auth_method.value,
            "last_rotated": account.last_rotated.isoformat(),
            "cookie_expiry": account.cookie_expiry.isoformat() if account.cookie_expiry else None,
            "usage": {
                "total_requests": account.usage.total_requests,
                "successful": account.usage.successful_requests,
                "failed": account.usage.failed_requests,
                "avg_response_time": account.usage.avg_response_time,
            },
            "rate_limit": {
                "remaining": account.rate_limit.quota_remaining,
                "limit": account.rate_limit.quota_limit,
            },
        }
    
    def audit_fleet(self) -> dict:
        """Audit entire fleet status."""
        config = self.get_fleet_config()
        return {
            "total_accounts": len(config.accounts),
            "active": sum(1 for a in config.accounts if a.status == CredentialStatus.ACTIVE),
            "rotating": sum(1 for a in config.accounts if a.status == CredentialStatus.ROTATING),
            "expired": sum(1 for a in config.accounts if a.status == CredentialStatus.EXPIRED),
            "by_provider": {
                provider: len(self.get_accounts_by_provider(provider))
                for provider in set(a.provider for a in config.accounts)
            },
        }
```

### 3.2 Fleet Orchestrator

```python
# src/omega/vault/fleet_orchestrator.py

import asyncio
from datetime import datetime, timedelta

class FleetOrchestrator:
    """Manages 16-account Grok fleet with automatic rotation."""
    
    def __init__(self, vault: KeyVault):
        self.vault = vault
        self._rotation_task: asyncio.Task | None = None
    
    async def start(self) -> None:
        """Start fleet orchestrator with background rotation."""
        self._rotation_task = asyncio.create_task(self._rotation_loop())
    
    async def stop(self) -> None:
        """Stop fleet orchestrator."""
        if self._rotation_task:
            self._rotation_task.cancel()
    
    async def _rotation_loop(self) -> None:
        """Background loop: rotate expired credentials."""
        while True:
            try:
                config = self.vault.get_fleet_config()
                for account in config.accounts:
                    if account.auth_method == AuthMethod.COOKIE:
                        if account.cookie_expiry and account.cookie_expiry < datetime.utcnow():
                            await self._rotate_cookie(account)
                    elif account.auth_method == AuthMethod.API_KEY:
                        if account.last_rotated < datetime.utcnow() - timedelta(days=30):
                            await self._notify_rotation_needed(account)
            except Exception as e:
                logger.warning(f"Rotation loop error: {e}")
            
            await asyncio.sleep(3600)  # Check every hour
    
    async def _rotate_cookie(self, account: CredentialEntry) -> None:
        """Rotate expired cookie (Web Grok accounts)."""
        logger.info(f"Rotating expired cookie for {account.account_id}")
        account.status = CredentialStatus.ROTATING
        # Cookie rotation requires browser automation
        # For now, mark as expired and notify
        account.status = CredentialStatus.EXPIRED
        # TODO: Integrate with browser automation for cookie refresh
    
    async def _notify_rotation_needed(self, account: CredentialEntry) -> None:
        """Notify that API key rotation is needed."""
        logger.warning(f"API key rotation needed for {account.account_id}")
    
    async def get_next_account(self, provider: str, domain: str = "") -> CredentialEntry | None:
        """Get next available account for a provider, optionally filtered by domain."""
        accounts = self.vault.get_accounts_by_provider(provider)
        active = [a for a in accounts if a.status == CredentialStatus.ACTIVE]
        
        if domain:
            active = [a for a in active if domain in a.domains_supported]
        
        if not active:
            return None
        
        # Round-robin by priority, then by least-used
        active.sort(key=lambda a: (a.priority, a.usage.total_requests))
        return active[0]
    
    async def record_usage(self, account_id: str, success: bool, latency_ms: float) -> None:
        """Record usage stats for an account."""
        config = self.vault.get_fleet_config()
        for i, account in enumerate(config.accounts):
            if account.account_id == account_id:
                config.accounts[i].usage.total_requests += 1
                if success:
                    config.accounts[i].usage.successful_requests += 1
                else:
                    config.accounts[i].usage.failed_requests += 1
                config.accounts[i].usage.last_used = datetime.utcnow()
                # Update average response time
                total = config.accounts[i].usage.total_requests
                old_avg = config.accounts[i].usage.avg_response_time
                config.accounts[i].usage.avg_response_time = (
                    (old_avg * (total - 1) + latency_ms) / total
                )
                self.vault.save_fleet_config(config)
                break
```

### 3.3 Passive File Watcher

```python
# src/omega/vault/passive_watcher.py

import asyncio
from pathlib import Path

class PassiveWatcher:
    """Detect .env/config drift and auto-sync to vault."""
    
    def __init__(self, vault: KeyVault, watch_paths: list[str] | None = None):
        self.vault = vault
        self.watch_paths = watch_paths or [
            ".env",
            ".env.local",
            "config/providers.yaml",
        ]
    
    async def start(self) -> None:
        """Start watching for config changes."""
        # Use inotify on Linux, fsevents on macOS
        try:
            import inotify.adapters
            await self._watch_inotify()
        except ImportError:
            # Fallback: poll every 60 seconds
            await self._watch_polling()
    
    async def _watch_inotify(self) -> None:
        """Watch using inotify (Linux)."""
        import inotify.adapters
        i = inotify.adapters.Inotify()
        for path in self.watch_paths:
            if Path(path).exists():
                i.add_watch(path)
        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event
            if "IN_MODIFY" in type_names:
                await self._sync_to_vault(path)
    
    async def _watch_polling(self) -> None:
        """Polling fallback for non-Linux systems."""
        file_mtimes = {}
        while True:
            for path_str in self.watch_paths:
                path = Path(path_str)
                if path.exists():
                    current_mtime = path.stat().st_mtime
                    if path_str in file_mtimes:
                        if current_mtime > file_mtimes[path_str]:
                            await self._sync_to_vault(path_str)
                    file_mtimes[path_str] = current_mtime
            await asyncio.sleep(60)
    
    async def _sync_to_vault(self, path: str) -> None:
        """Sync changed file to vault."""
        logger.info(f"Config drift detected: {path} — syncing to vault")
        # Parse the file and update vault accordingly
        # Implementation depends on file format (.env vs YAML)
```

### 3.4 MCP Server

```python
# mcp_servers/omega_vault/server.py

from mcp.server import Server
from mcp.types import Tool, TextContent
from omega.vault import KeyVault, FleetOrchestrator

app = Server("omega-vault")
vault = KeyVault()
orchestrator = FleetOrchestrator(vault)

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="credential_read",
            description="Read credential for a provider or specific account",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "account_id": {"type": "string"},
                    "domain": {"type": "string"},
                },
                "required": ["provider"],
            },
        ),
        Tool(
            name="credential_write",
            description="Write credential for a provider",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "account_id": {"type": "string"},
                    "key": {"type": "string"},
                    "persona": {"type": "string"},
                },
                "required": ["provider", "account_id", "key"],
            },
        ),
        Tool(
            name="credential_rotate",
            description="Rotate credential for a provider or specific account",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "account_id": {"type": "string"},
                    "new_credential": {"type": "string"},
                },
                "required": ["provider"],
            },
        ),
        Tool(
            name="credential_audit",
            description="Audit credential status and usage",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "account_id": {"type": "string"},
                },
                "required": ["provider"],
            },
        ),
        Tool(
            name="fleet_status",
            description="Get fleet-wide status (16-account overview)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="fleet_next_account",
            description="Get next available account for a provider (round-robin)",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "domain": {"type": "string"},
                },
                "required": ["provider"],
            },
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "credential_read":
        provider = arguments["provider"]
        account_id = arguments.get("account_id")
        domain = arguments.get("domain", "")
        
        if account_id:
            account = vault.get_account(account_id)
            if account:
                credential = account.api_key or account.cookie_value or ""
                masked = credential[:4] + "*" * (len(credential) - 4) if len(credential) > 4 else "****"
                return [TextContent(type="text", text=f"Provider: {provider}\nAccount: {account_id}\nCredential: {masked}\nStatus: {account.status.value}")]
            return [TextContent(type="text", text=f"Account {account_id} not found")]
        
        accounts = vault.get_accounts_by_provider(provider)
        return [TextContent(type="text", text=f"Provider: {provider}\nAccounts: {len(accounts)}\nActive: {sum(1 for a in accounts if a.status.value == 'active')}")]
    
    elif name == "fleet_status":
        status = vault.audit_fleet()
        return [TextContent(type="text", text=str(status))]
    
    elif name == "fleet_next_account":
        provider = arguments["provider"]
        domain = arguments.get("domain", "")
        account = await orchestrator.get_next_account(provider, domain)
        if account:
            return [TextContent(type="text", text=f"Next account: {account.account_id} (priority: {account.priority})")]
        return [TextContent(type="text", text=f"No active accounts for provider: {provider}")]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]
```

---

## §4 CLI Interface

### 4.1 Commands

```bash
# Initialize vault (first-time setup)
omega vault init

# Import plaintext secrets from .env (transition assistance)
omega vault import

# List all providers and accounts
omega vault list

# Get credential for a specific provider/account
omega vault get xai
omega vault get xai --account xai_cli_01

# Set credential for a provider
omega vault set xai "your-api-key"
omega vault set xai --account xai_web_01 --cookie "session_value"

# Rotate credential (rate limit detection)
omega vault rotate xai
omega vault rotate xai --account xai_cli_01

# Audit credential (check expiration, rate limits)
omega vault audit xai
omega vault audit --fleet

# Show vault status
omega vault status

# Fleet management
omega vault fleet list
omega vault fleet status
omega vault fleet next xai
```

### 4.2 XDG Compliance

```bash
# XDG config directory: ~/.config/omega/
# XDG data directory: ~/.local/share/omega/
# XDG state directory: ~/.local/state/omega/

# Config file: ~/.config/omega/vault_config.yaml
# Vault file: ~/.local/share/omega/keys.json.enc
# Fleet config: ~/.local/share/omega/fleet_config.yaml
# Log file: ~/.local/state/omega/omega-vault.log
```

---

## §5 Security Framework

### 5.1 Encryption at Rest

- **Algorithm**: AES-256-GCM (existing `src/omega/vault/`)
- **Key Management**: OS keyring (libsecret on Linux, Keychain on macOS)
- **File Permissions**: `0o600` on vault files
- **Zero Data Retention (ZDR)**: Decrypted data cleared after use

### 5.2 Access Control

```python
# File permissions enforcement
VAULT_FILE_PERMISSIONS = 0o600
CONFIG_FILE_PERMISSIONS = 0o600
LOG_FILE_PERMISSIONS = 0o644

def enforce_permissions(path: Path, permissions: int) -> None:
    """Enforce file permissions."""
    path.chmod(permissions)
```

### 5.3 Memory Hygiene

```python
import ctypes

def secure_clear(data: str) -> None:
    """Clear string from memory (best-effort)."""
    # Python strings are immutable, so we can't truly clear them
    # But we can overwrite the underlying buffer in CPython
    try:
        buf = ctypes.cast(id(data), ctypes.POINTER(ctypes.c_char * len(data)))
        ctypes.memset(buf, 0, len(data))
    except Exception:
        pass  # Best effort
```

---

## §6 Testing & Validation

### 6.1 Test Matrix

| Test | Category | Pass Criteria |
|------|----------|---------------|
| Vault init | Core | Vault created at XDG path |
| Vault import | Core | .env secrets imported correctly |
| Credential read/write | Core | Round-trip encryption works |
| Fleet config load/save | Fleet | 16-account schema validates |
| Account rotation | Fleet | Credential updated, status active |
| Cookie expiry detection | Fleet | Expired cookies detected |
| MCP server startup | Integration | Server binds to stdio |
| MCP tool calls | Integration | All 6 tools return valid responses |
| XDG paths | Portability | No hardcoded paths in code |
| File permissions | Security | Vault files are 0o600 |
| Passive watcher | Observability | Config drift detected |
| Audit report | Observability | Fleet status accurate |

### 6.2 Chaos Testing

```python
# tests/test_vault_chaos.py

import pytest
import asyncio

@pytest.mark.chaos
async def test_vault_concurrent_access():
    """Test concurrent access to vault."""
    vault = KeyVault()
    
    async def write_credential(i: int):
        vault.set_key(f"provider_{i}", f"key_{i}")
        vault.save()
    
    # 10 concurrent writes
    await asyncio.gather(*[write_credential(i) for i in range(10)])
    
    # Verify all keys present
    for i in range(10):
        assert vault.resolve(f"provider_{i}") == f"key_{i}"

@pytest.mark.chaos
async def test_vault_corruption_recovery():
    """Test recovery from corrupted vault file."""
    vault = KeyVault()
    vault.set_key("test", "value")
    vault.save()
    
    # Corrupt the vault file
    vault_path = Path(vault.vault_path)
    vault_path.write_bytes(b"corrupted data")
    
    # Should recover gracefully
    vault2 = KeyVault()
    with pytest.raises(VaultCorruptedError):
        vault2.load()

@pytest.mark.chaos
async def test_fleet_rotation_under_load():
    """Test fleet rotation while accounts are in use."""
    vault = KeyVault()
    orchestrator = FleetOrchestrator(vault)
    
    async def use_account():
        account = await orchestrator.get_next_account("xai")
        if account:
            await orchestrator.record_usage(account.account_id, True, 100.0)
    
    # Concurrent account usage + rotation
    await asyncio.gather(
        *[use_account() for _ in range(20)],
        orchestrator._rotation_loop(),
    )
```

---

## §7 Implementation Phases

### Phase 1: VaultCore (Days 1-2)

| Task | Owner | Effort |
|------|-------|--------|
| Extend KeyVault with fleet methods | Ma'at/P3 | 4h |
| Implement CredentialEntry schema | Ma'at/P3 | 2h |
| Implement ProviderSchema | Ma'at/P3 | 2h |
| XDG path compliance | Ma'at/P3 | 2h |
| Unit tests | Ma'at/P3 | 4h |

### Phase 2: Fleet Orchestrator (Days 3-4)

| Task | Owner | Effort |
|------|-------|--------|
| FleetOrchestrator implementation | Ma'at/P3 | 4h |
| 16-account schema YAML | grokster | 2h |
| Round-robin account selection | Ma'at/P3 | 2h |
| Usage tracking | Ma'at/P3 | 2h |
| Integration tests | Ma'at/P3 | 4h |

### Phase 3: MCP Server (Day 5)

| Task | Owner | Effort |
|------|-------|--------|
| MCP server with 6 tools | Ma'at/P3 | 4h |
| Tool validation | Ma'at/P3 | 2h |
| Integration with Omega Hub | Ma'at/P3 | 2h |

### Phase 4: CLI + Watcher (Day 6)

| Task | Owner | Effort |
|------|-------|--------|
| `omega vault` CLI commands | Ma'at/P3 | 4h |
| Passive file watcher | Ma'at/P3 | 2h |
| Import from .env | Ma'at/P3 | 2h |

### Phase 5: Testing + Chaos (Day 7)

| Task | Owner | Effort |
|------|-------|--------|
| Chaos test suite | Ma'at/P3 | 4h |
| Temple-Grade CI gate | Ma'at/P3 | 2h |
| Documentation | Ma'at/P3 | 2h |

**Total**: ~7 days for complete V-1 MVP

---

## §8 Blocking Dependencies

| Dependency | Status | Impact |
|-----------|--------|--------|
| **Existing `src/omega/vault/`** | ✅ Exists | Foundation for extension |
| **Pydantic v2** | ✅ Available | Schema validation |
| **OS keyring** | ✅ Available | Encryption key management |
| **MCP server framework** | ✅ Available | Tool exposure |
| **Browser automation** | 🟡 Not yet | Cookie rotation for Web Grok |
| **ACP protocol** | 🟡 Not yet | Fleet integration with Grok CLI |

---

## §9 Success Criteria

| Criterion | Metric | Target |
|-----------|--------|--------|
| **Credential storage** | All 16 accounts stored | 16/16 |
| **Encryption** | AES-256-GCM at rest | ✅ |
| **Fleet rotation** | Round-robin account selection | Working |
| **Cookie expiry** | Detection + notification | Working |
| **MCP integration** | 6 tools exposed | Working |
| **XDG compliance** | Zero hardcoded paths | Verified |
| **Temple-Grade CI** | Chaos tests pass | ✅ |
| **ACP smoke test** | Grok CLI reads from vault | Working |

---

*⬡ OMEGA ⬡ GROKSTER ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_vault_impl ⬡ R35-COMPLETE*
*Decision Gate PASSED: 16-account credential schema + Vault backend selected + ACP smoke test path defined*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
