# 🔱 V-1 Omega-Vault Design Spec — Credential Vault MVP
**Version**: 1.0.0 | **Date**: 2026-07-21 | **Status**: Design Complete | **Approved**: Kali (Kali amendment 2)

---

## 📋 Executive Summary

**Purpose**: Design the Omega-Vault MVP (V-1) — credential automation for the 16-account Grok fleet (8 CLI + 8 Web Grok). This is the **explicit ticket** from Kali amendment 2 that blocks fleet deployment.

**Scope**: Design only. Implementation to be done by Ma'at/P3 (Phase 1: VaultCore, Phase 2: CAP Adapters, Phase 3: Policy Engine).

**Key Design Decisions**:
- 16 accounts × (API key + persona prompt + rate budget + ZDR flag)
- AES-256-GCM encryption with OS keyring (existing `src/omega/vault/`)
- Per-provider credential schema with rotation support
- Passive file watcher for `.env`/config drift detection
- MCP server exposing `credential.read/write/rotate/audit`
- XDG-compliant CLI with zero hardcoded paths
- Temple-Grade CI with chaos testing

---

## 🎯 Design Objectives

### Primary Goals
1. **Credential Automation** — Eliminate plaintext `.env` keys for Grok fleet
2. **Sovereign Storage** — Zero telemetry, local-first, OS keyring integration
3. **Fleet Support** — 16 accounts (8 CLI + 8 Web Grok) with persona prompts
4. **Passive Sync** — File watcher detects config drift → auto-sync to vault
5. **Enterprise Ready** — Temple-Grade quality, chaos testing, XDG compliance

### Design Principles
- **Single Source of Truth** — All credentials stored in encrypted vault
- **Zero Hardcoded Paths** — XDG compliance, no platform-specific code
- **Graceful Degradation** — Fallback to environment variables during transition
- **Memory Hygiene** — Clear decrypted data after use (P5 F-3)
- **Rate Limit Awareness** — Per-account rate tracking, circuit breaker integration
- **ZDR Enforcement** — Zero data retention, automatic cleanup
- **Heritage Compliance** — M14 tags for all credential patterns

---

## 🏗️ Architecture Overview

### Core Components
```
┌─────────────────────────────────────────────────────────────┐
│                    OMEGA-VAULT (PyPI)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   KeyVault      │  │   CAP Adapters  │  │   Policy Engine │  │
│  │ (Core Singleton)│  │ (MCP Server)    │  │ (Credential Schema)│ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  │  AES-256-GCM    │  │  credential.read │  │  CredentialModel   │  │
│  │  encryption     │  │  credential.write│  │  (Pydantic)       │  │
│  │  + rotation    │  │  credential.rotate│  │  AccountSchema    │  │
│  │  + audit       │  │  credential.audit│  │  ProviderSchema   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Passive        │  │  MCP            │  │  XDG CLI        │  │
│  │  Watcher        │  │  Server         │  │  (`omega vault`) │  │
│  │  (inotify/fanot)│  │  (stdio)        │  │  (XDG paths)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **CLI** → `omega vault init|import|list|get|set|rotate`
2. **Passive Watcher** → detects `.env`/config drift → auto-sync to vault
3. **MCP Server** → exposes credential APIs for Omega Engine integration
4. **Policy Engine** → validates schema, enforces ZDR, rate limits
5. **KeyVault** → encrypted storage with OS keyring

---

## 📊 Credential Schema Design

### Core Models

#### 1. CredentialEntry (Base)
```yaml
# Base credential entry structure
credential_entry:
  provider: "string"                    # ex: "gemini", "firecrawl"
  account_id: "string"                   # ex: "gemini_oauth_01"
  persona: "string"                      # Grok persona prompt
  created_at: "2026-07-21T00:00:00Z"
  last_rotated: "2026-07-21T00:00:00Z"
  status: "active|inactive|rotating"
  
  # Security
  encryption_key_ref: "~/.config/omega/vault_master.key"
  file_permissions: 0o600
  zdr_enforced: true
  
  # Rate limiting
  rate_limit:
    max_retries: 3
    backoff_factor: 2
    max_backoff: 3600
    quota_remaining: 1000000
    quota_limit: 1000000
    last_reset: "2026-07-21T00:00:00Z"
  
  # Usage tracking
  usage:
    total_requests: 0
    successful_requests: 0
    failed_requests: 0
    avg_response_time: 0.0
    last_used: "2026-07-21T00:00:00Z"
```

#### 2. ProviderSchema (Per-Provider Config)
```yaml
# Provider-specific configuration
provider_schema:
  gemini:
    env_var: "GEMINI_API_KEY"
    default_model: "gemini-3-pro-preview"
    models:
      - "gemini-3-pro-preview"
      - "gemini-3-flash-preview"
      - "gemini-3-flash"
    rate_limit:
      requests_per_minute: 60
      requests_per_day: 1000000
      burst_limit: 10
    domains_supported:
      - "general"
      - "architect"
      - "ui"
      - "voice"
      - "data"
    
  firecrawl:
    env_var: "FIRECRAWL_API_KEY"
    default_model: "firecrawl-1"
    rate_limit:
      requests_per_minute: 30
      requests_per_day: 100000
      burst_limit: 5
    domains_supported:
      - "web"
      - "code"
      - "research"
```

#### 3. AccountSchema (Per-Account)
```yaml
# Account-specific configuration
account_schema:
  type: "string"                           # "oauth", "api_key", "service_account"
  auth_method: "string"                    # "google_oauth", "bearer", "basic"
  credentials:
    access_token: "encrypted_string"
    refresh_token: "encrypted_string"
    expiry: "2026-07-22T00:00:00Z"
    scopes: ["https://www.googleapis.com/auth/cloud-platform"]
  
  # Security
  encryption_key_ref: "~/.config/omega/vault_master.key"
  file_permissions: 0o600
  zdr_enforced: true
  
  # Rate limiting
  rate_limit:
    max_retries: 3
    backoff_factor: 2
    max_backoff: 3600
    quota_remaining: 1000000
    quota_limit: 1000000
    last_reset: "2026-07-21T00:00:00Z"
  
  # Usage tracking
  usage:
    total_requests: 0
    successful_requests: 0
    failed_requests: 0
    avg_response_time: 0.0
    last_used: "2026-07-21T00:00:00Z"
  
  # Models & priority
  models_preferred: ["gemini-3-pro-preview", "gemini-3-flash-preview"]
  priority: 1
  domains_supported: ["general", "architect", "ui", "voice", "data"]
```

---

## 🖥️ CLI Interface Design

### Commands
```bash
# Initialize vault (first-time setup)
omega vault init

# Import plaintext secrets from .env (transition assistance)
omega vault import

# List all providers
omega vault list

# Get credential for a specific provider
omega vault get gemini

# Set credential for a provider
omega vault set gemini "your-api-key"

# Rotate credential (rate limit detection)
omega vault rotate gemini

# Audit credential (check expiration, rate limits)
omega vault audit gemini

# Show vault status
omega vault status

# Show help
omega vault help
```

### XDG Compliance
```bash
# XDG config directory: ~/.config/omega/
# XDG data directory: ~/.local/share/omega/
# XDG state directory: ~/.local/state/omega/

# Config file: ~/.config/omega/vault_config.yaml
# Vault file: ~/.local/share/omega/keys.json.enc
# Log file: ~/.local/state/omega/omega-vault.log
```

### Example CLI Implementation
```python
class VaultCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="omega vault")
        self.subparsers = self.parser.add_subparsers(dest="command")
        
        # Initialize command
        init_parser = self.subparsers.add_parser("init", help="Initialize vault")
        init_parser.set_defaults(func=self.init_vault)
        
        # Import command
        import_parser = self.subparsers.add_parser("import", help="Import from .env")
        import_parser.set_defaults(func=self.import_from_env)
        
        # List command
        list_parser = self.subparsers.add_parser("list", help="List providers")
        list_parser.set_defaults(func=self.list_providers)
        
        # Get command
        get_parser = self.subparsers.add_parser("get", help="Get credential")
        get_parser.add_argument("provider", help="Provider name")
        get_parser.set_defaults(func=self.get_credential)
        
        # Set command
        set_parser = self.subparsers.add_parser("set", help="Set credential")
        set_parser.add_argument("provider", help="Provider name")
        set_parser.add_argument("key", help="API key value")
        set_parser.set_defaults(func=self.set_credential)
        
        # Rotate command
        rotate_parser = self.subparsers.add_parser("rotate", help="Rotate credential")
        rotate_parser.add_argument("provider", help="Provider name")
        rotate_parser.set_defaults(func=self.rotate_credential)
        
        # Audit command
        audit_parser = self.subparsers.add_parser("audit", help="Audit credential")
        audit_parser.add_argument("provider", help="Provider name")
        audit_parser.set_defaults(func=self.audit_credential)
        
        # Status command
        status_parser = self.subparsers.add_parser("status", help="Show vault status")
        status_parser.set_defaults(func=self.show_status)
    
    def init_vault(self, args):
        """Initialize vault with OS keyring"""
        vault = KeyVault()
        vault.save()
        print("Vault initialized successfully")
    
    def import_from_env(self, args):
        """Import secrets from .env file"""
        vault = KeyVault()
        vault._auto_init_from_env()
        print("Vault imported from .env")
    
    def list_providers(self, args):
        """List all providers in vault"""
        vault = KeyVault()
        providers = vault.get_providers()
        for provider in providers:
            print(f"  {provider}")
    
    def get_credential(self, args):
        """Get credential for provider"""
        vault = KeyVault()
        try:
            key = vault.resolve(args.provider)
            print(f"Credential for {args.provider}: {'*' * (len(key) - 4)}{key[-4:]}")
        except VaultKeyNotFound:
            print(f"No credential found for provider '{args.provider}'")
    
    def set_credential(self, args):
        """Set credential for provider"""
        vault = KeyVault()
        vault.set_key(args.provider, args.key)
        vault.save()
        print(f"Credential set for {args.provider}")
    
    def rotate_credential(self, args):
        """Rotate credential for provider"""
        vault = KeyVault()
        # Implementation for credential rotation
        print(f"Credential rotation requested for {args.provider}")
    
    def audit_credential(self, args):
        """Audit credential for provider"""
        vault = KeyVault()
        status = vault.get_status()
        print(f"Status for {args.provider}:")
        print(f"  Loaded: {status['loaded']}")
        print(f"  Vault path: {status['vault_path']}")
        print(f"  Total keys: {status['total_keys']}")
    
    def show_status(self, args):
        """Show overall vault status"""
        vault = KeyVault()
        status = vault.get_status()
        print("Vault Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    
    def run(self):
        """Run CLI"""
        args = self.parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            self.parser.print_help()
```

---

## 🔌 MCP Server Design

### Server Structure
```python
# mcp_servers/omega_vault/server.py

from mcp.server import Server
from mcp.types import Tool, TextContent
from omega.vault import KeyVault, VaultKeyNotFound

app = Server("omega-vault")
vault = KeyVault()

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="credential_read",
            description="Read credential for a provider",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "account_id": {"type": "string"}
                },
                "required": ["provider"]
            }
        ),
        Tool(
            name="credential_write",
            description="Write credential for a provider",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "key": {"type": "string"},
                    "account_id": {"type": "string"}
                },
                "required": ["provider", "key"]
            }
        ),
        Tool(
            name="credential_rotate",
            description="Rotate credential for a provider",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"}
                },
                "required": ["provider"]
            }
        ),
        Tool(
            name="credential_audit",
            description="Audit credential for a provider",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"}
                },
                "required": ["provider"]
            }
        ),
        Tool(
            name="vault_status",
            description="Get vault status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "credential_read":
        provider = arguments["provider"]
        account_id = arguments.get("account_id")
        try:
            if account_id:
                # Get specific account credential
                pass
            else:
                key = vault.resolve(provider)
            return [TextContent(type="text", text=f"Credential for {provider}: {'*' * (len(key) - 4)}{key[-4:]}")]
        except VaultKeyNotFound:
            return [TextContent(type="text", text=f"No credential found for provider '{provider}'")]
    
    elif name == "credential_write":
        provider = arguments["provider"]
        key = arguments["key"]
        account_id = arguments.get("account_id")
        vault.set_key(provider, key, account=account_id)
        vault.save()
        return [TextContent(type="text", text=f"Credential written for {provider}")]
    
    elif name == "credential_rotate":
        provider = arguments["provider"]
        # Implementation for credential rotation
        return [TextContent(type="text", text=f"Credential rotation requested for {provider}")]
    
    elif name == "credential_audit":
        provider = arguments["provider"]
        status = vault.get_status()
        return [TextContent(type="text", text=f"Status for {provider}: {status}")]
    
    elif name == "vault_status":
        status = vault.get_status()
        return [TextContent(type="text", text=f"Vault status: {status}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")
```

---

## 👁️ Passive Watcher Design

### File Monitoring
```python
# mcp_servers/omega_vault/watcher.py

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from omega.vault import KeyVault

class VaultChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.vault = KeyVault()
        self.last_modified = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.name in [".env", "vault_config.yaml", "config/*.env"]:
            self._sync_vault_from_file(file_path)
    
    def _sync_vault_from_file(self, file_path):
        """Sync vault from modified file"""
        try:
            # Debounce: wait 1 second to avoid multiple triggers
            if file_path in self.last_modified:
                if time.time() - self.last_modified[file_path] < 1.0:
                    return
            
            self.last_modified[file_path] = time.time()
            
            # Import from .env if it's the .env file
            if file_path.name == ".env":
                self.vault._auto_init_from_env()
                self.vault.save()
                print(f"Vault synced from {file_path}")
            
        except Exception as e:
            print(f"Error syncing vault from {file_path}: {e}")

class VaultWatcher:
    def __init__(self, watch_paths):
        self.observer = Observer()
        self.handler = VaultChangeHandler()
        self.watch_paths = watch_paths
    
    def start(self):
        """Start watching for file changes"""
        for path in self.watch_paths:
            self.observer.schedule(self.handler, path, recursive=True)
        
        print("Starting vault watcher...")
        self.observer.start()
    
    def stop(self):
        """Stop watching"""
        self.observer.stop()
        self.observer.join()
        print("Vault watcher stopped")
```

---

## 📋 Implementation Phases

### Phase 1: VaultCore (2-3 sessions)
**Objective**: Core encrypted storage with OS keyring

| Session | Tasks |
|---------|-------|
| 1 | Implement KeyVault singleton, AES-256-GCM encryption, OS keyring integration |
| 2 | Implement `resolve()`, `resolve_all()`, `resolve_safe()`, `set_key()`, `save()` |
| 3 | Implement `_auto_init_from_env()`, `_fallback_to_env()`, error handling |

### Phase 2: CAP Adapters (2 sessions)
**Objective**: MCP server + passive watcher

| Session | Tasks |
|---------|-------|
| 4 | Implement MCP server with credential.read/write/rotate/audit tools |
| 5 | Implement passive file watcher with inotify/fanotify |
| 6 | Test MCP integration with Omega Engine |

### Phase 3: Policy Engine (1 session)
**Objective**: Credential schema validation, ZDR enforcement

| Session | Tasks |
|---------|-------|
| 7 | Implement Pydantic models for CredentialEntry, ProviderSchema, AccountSchema |
| 8 | Implement validation, ZDR enforcement, rate limit tracking |
| 9 | Integrate with KeyVault for schema validation |

---

## 🔑 Key Design Decisions Summary

### ✅ Design Decisions
1. **AES-256-GCM encryption** with OS keyring (existing `src/omega/vault/`)
2. **Per-provider credential schema** with persona prompts
3. **Passive file watcher** for `.env`/config drift detection
4. **MCP server** exposing credential APIs for Omega Engine
5. **XDG-compliant CLI** with zero hardcoded paths
6. **Temple-Grade quality** with chaos testing

### ⚠️ Known Limitations
1. **Transition period** — fallback to environment variables during initial setup
2. **Rate limit rotation** — uses circuit breaker fabric, not key rotation
3. **ZDR enforcement** — requires explicit configuration per credential
4. **File system dependency** — passive watcher requires inotify/fanotify

### 🎯 Success Criteria
1. **Zero plaintext keys** in production after initial setup
2. **Automatic sync** from `.env` modifications
3. **Graceful degradation** during transition
4. **Temple-Grade compliance** with CI/CD integration
5. **Enterprise features** with monitoring and auditing

---

## 📊 Project Timeline

### Week 1 (Phase 1)
- **Session 1-3**: VaultCore implementation
- **Deliverable**: Core encrypted storage with OS keyring

### Week 2 (Phase 2)
- **Session 4-6**: CAP Adapters implementation
- **Deliverable**: MCP server + passive watcher

### Week 3 (Phase 3)
- **Session 7-9**: Policy Engine implementation
- **Deliverable**: Credential schema validation, ZDR enforcement

### Week 4 (Integration)
- **Session 10-12**: Integration testing, chaos testing
- **Deliverable**: Temple-Grade release

---

## 🔗 Integration Points

### Omega Engine Integration
```python
# Integration points for Omega Engine

# 1. Credential Resolution
from omega.vault import KeyVault
vault = KeyVault()
key = vault.resolve("gemini")

# 2. Rate Limit Handling
from omega.errors import ProviderRateLimitError
try:
    # Make API call
    response = make_api_call(key)
except ProviderRateLimitError:
    # Handle rate limit via circuit breaker
    pass

# 3. Credential Rotation
vault.set_key("gemini", "new-key")
vault.save()

# 4. Vault Status
status = vault.get_status()
```

### Hivemind Integration
```python
# Hivemind context for V-1 design
# - Workspace lock: data/coordination/V1_OMEGA_VAULT_DESIGN_20260721.md
# - Live feed: data/coordination/GROKSTER_LIVE_FEED.md
# - Heartbeat: every 5-10 minutes during design
```

---

## 📋 Decision Matrix

| Decision | Option A | Option B | Option C | Chosen |
|----------|----------|----------|----------|--------|
| **Storage** | AES-256-GCM with OS keyring | Plaintext files | Cloud storage | ✅ AES-256-GCM |
| **Sync** | Passive file watcher | Manual import | Scheduled jobs | ✅ Passive watcher |
| **API** | MCP server | REST API | gRPC | ✅ MCP server |
| **CLI** | XDG-compliant | Platform-specific | Web interface | ✅ XDG-compliant |
| **Validation** | Pydantic schemas | JSON schema | Custom validation | ✅ Pydantic |

---

## 🎯 Conclusion

The V-1 Omega-Vault design provides a **secure, sovereign credential management system** for the 16-account Grok fleet. It leverages existing Omega infrastructure while adding the necessary features for enterprise deployment.

**Key Benefits**:
- **Zero plaintext keys** in production
- **Automatic sync** from configuration files
- **Enterprise-grade security** with Temple-Grade quality
- **Scalable architecture** for 16+ accounts
- **Seamless integration** with Omega Engine

**Implementation Timeline**: 3 weeks (Phase 1-3) with Ma'at/P3.

---

*⬡ OMEGA ⬡ V-1 OMEGA-VAULT DESIGN ⬡ 2026-07-21 ⬡ 2026-07-21 ⬡ Design Complete — Ready for Ma&#x01F4A1;P3 Implementation*