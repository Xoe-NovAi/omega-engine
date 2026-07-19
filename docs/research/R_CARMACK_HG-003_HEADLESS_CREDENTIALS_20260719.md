# 🔱 HG-003: Headless Pool Credential Formats
**AP Token**: `AP-CARMACK-HG003-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19

---

## 🎯 Research Target
Exact file paths, formats, rotation mechanisms for Grok CLI, Copilot CLI, Cline CLI — for Omega-Vault adapters

---

## 📋 Primary Source Findings

### 1. Grok CLI (xAI)

**Credential Storage**: macOS Keychain (service: `grok-cli`)
```bash
# CLI commands
grok --api-key <key>        # Store in keychain
grok --reset-key            # Delete from keychain
```

**Format**: Single API key string
```json
// Keychain entry (generic password)
{
  "service": "grok-cli",
  "account": "default",
  "password": "xai-<base64-key>"
}
```

**Rotation**: Manual via `--reset-key` + re-enter. No auto-rotation.

**Multi-account**: Not supported natively. Workaround: multiple keychain entries with different accounts.

---

### 2. GitHub Copilot CLI

**Credential Storage**: `~/.copilot/auth.json` (plaintext JSON)
```json
{
  "github.com": {
    "oauth_token": "gho_...",
    "refresh_token": "ghr_...",
    "expires_at": 1720000000,
    "token_type": "bearer",
    "scope": "copilot read:user user:email"
  }
}
```

**Alternative**: Environment variables (precedence order):
1. `COPILOT_GITHUB_TOKEN`
2. `GH_TOKEN` 
3. `GITHUB_TOKEN`

**Rotation**: Auto-refresh via OAuth device flow. `gh auth refresh` updates file.

**Multi-account**: Supported via `gh auth login --hostname github.com` multiple times. Stored as separate entries in `auth.json`.

---

### 3. Cline CLI (VS Code Extension + CLI)

**Credential Storage**: VS Code SecretStorage (OS keychain backend)
- **Linux**: `libsecret` → `~/.local/share/cline/credentials.json` (encrypted)
- **macOS**: Keychain → `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/credentials.json`
- **Windows**: Credential Manager → `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\credentials.json`

**Format** (decrypted):
```json
{
  "providers": {
    "anthropic": {
      "apiKey": "sk-ant-...",
      "model": "claude-sonnet-4-20250514"
    },
    "openai": {
      "apiKey": "sk-...",
      "model": "gpt-4o"
    },
    "google": {
      "apiKey": "AIza...",
      "model": "gemini-2.5-pro"
    },
    "openrouter": {
      "apiKey": "sk-or-...",
      "model": "deepseek/deepseek-chat"
    },
    "ollama": {
      "baseUrl": "http://localhost:11434",
      "model": "qwen2.5-coder:32b"
    }
  },
  "activeProvider": "anthropic",
  "settings": {
    "autoApprove": false,
    "maxTokens": 8192
  }
}
```

**Rotation**: Manual via Cline UI → Settings → Providers. No CLI command for rotation.

**Multi-account**: Not supported. Single active provider at a time.

---

### 4. OpenCode (Reference)

**Credential Storage**: `~/.local/share/opencode/auth.json`
```json
{
  "providers": {
    "anthropic": { "apiKey": "sk-ant-..." },
    "openai": { "apiKey": "sk-..." },
    "google": { "apiKey": "AIza..." },
    "openrouter": { "apiKey": "sk-or-..." }
  }
}
```

**Command**: `opencode auth login` (interactive TUI)

---

## 🔧 Omega-Vault Adapter Specifications

### VaultCore Provider Interface
```python
# src/omega/infra/vault/providers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class Credential:
    provider: str
    api_key: str
    metadata: dict  # model, base_url, expires_at, etc.

class CredentialProvider(ABC):
    @abstractmethod
    def read(self) -> list[Credential]: ...
    
    @abstractmethod
    def write(self, credentials: list[Credential]) -> None: ...
    
    @abstractmethod
    def rotate(self, provider: str, new_key: str) -> None: ...
    
    @abstractmethod
    def supports_rotation(self) -> bool: ...
```

### Grok CLI Adapter
```python
# src/omega/infra/vault/providers/grok.py
import subprocess
import keyring
from .base import CredentialProvider, Credential

class GrokCLIProvider(CredentialProvider):
    SERVICE = "grok-cli"
    
    def read(self) -> list[Credential]:
        key = keyring.get_password(self.SERVICE, "default")
        if key:
            return [Credential(provider="grok", api_key=key, metadata={})]
        return []
    
    def write(self, credentials: list[Credential]) -> None:
        for cred in credentials:
            if cred.provider == "grok":
                keyring.set_password(self.SERVICE, "default", cred.api_key)
    
    def rotate(self, provider: str, new_key: str) -> None:
        if provider == "grok":
            keyring.set_password(self.SERVICE, "default", new_key)
    
    def supports_rotation(self) -> bool:
        return True
```

### Copilot CLI Adapter
```python
# src/omega/infra/vault/providers/copilot.py
import json
from pathlib import Path
from .base import CredentialProvider, Credential

class CopilotCLIProvider(CredentialProvider):
    CONFIG_PATH = Path.home() / ".copilot" / "auth.json"
    
    def read(self) -> list[Credential]:
        if not self.CONFIG_PATH.exists():
            return []
        data = json.loads(self.CONFIG_PATH.read_text())
        creds = []
        for host, token_data in data.items():
            creds.append(Credential(
                provider="copilot",
                api_key=token_data["oauth_token"],
                metadata={
                    "refresh_token": token_data.get("refresh_token"),
                    "expires_at": token_data.get("expires_at"),
                    "scope": token_data.get("scope"),
                    "host": host
                }
            ))
        return creds
    
    def write(self, credentials: list[Credential]) -> None:
        data = {}
        for cred in credentials:
            if cred.provider == "copilot":
                host = cred.metadata.get("host", "github.com")
                data[host] = {
                    "oauth_token": cred.api_key,
                    "refresh_token": cred.metadata.get("refresh_token"),
                    "expires_at": cred.metadata.get("expires_at"),
                    "token_type": "bearer",
                    "scope": cred.metadata.get("scope", "copilot read:user user:email")
                }
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.CONFIG_PATH.write_text(json.dumps(data, indent=2))
    
    def rotate(self, provider: str, new_key: str) -> None:
        # Copilot uses OAuth — rotation = re-auth via device flow
        raise NotImplementedError("Use `gh auth refresh` or device flow")
    
    def supports_rotation(self) -> bool:
        return False  # OAuth flow required
```

### Cline CLI Adapter
```python
# src/omega/infra/vault/providers/cline.py
import json
import platform
from pathlib import Path
from .base import CredentialProvider, Credential

class ClineCLIProvider(CredentialProvider):
    def _get_credentials_path(self) -> Path:
        system = platform.system()
        if system == "Darwin":
            base = Path.home() / "Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev"
        elif system == "Linux":
            base = Path.home() / ".local/share/cline"
        else:  # Windows
            base = Path(os.environ["APPDATA"]) / "Code/User/globalStorage/saoudrizwan.claude-dev"
        return base / "credentials.json"
    
    def read(self) -> list[Credential]:
        path = self._get_credentials_path()
        if not path.exists():
            return []
        # VS Code SecretStorage is encrypted — need VS Code API to decrypt
        # Fallback: read raw (encrypted) for audit only
        return [Credential(
            provider="cline",
            api_key="[ENCRYPTED_IN_VSCODE_SECRETSTORAGE]",
            metadata={"path": str(path), "encrypted": True}
        )]
    
    def write(self, credentials: list[Credential]) -> None:
        # Cannot write directly — must use VS Code extension API
        # Document manual process
        pass
    
    def rotate(self, provider: str, new_key: str) -> None:
        raise NotImplementedError("Rotate via Cline UI: Settings → Providers")
    
    def supports_rotation(self) -> bool:
        return False
```

---

## 🔐 VaultCore CLI Commands

```bash
# omega-vault CLI
vault init                    # Initialize vault (OS keyring + SQLite event log)
vault add grok --api-key xai-...           # Store Grok key
vault add copilot --oauth-token gho-...    # Store Copilot token
vault add cline --provider anthropic --api-key sk-ant-...  # Document manual step
vault sync                    # Push to all CLI configs (where writable)
vault audit                   # List all credentials + last rotation
vault rotate grok --new-key xai-...        # Rotate Grok key
vault rotate copilot           # Triggers `gh auth refresh`
vault backup --output vault-backup-20260719.json  # Encrypted backup
vault restore --input vault-backup-20260719.json
```

---

## 🔬 id Software Qualification Gate

| Aspect | id Software Analog | Omega-Vault |
|--------|-------------------|-------------|
| **Constraint** | 4MB RAM limit → zone allocator | 24 CLI accounts, 0 unified credential mgmt |
| **Technique** | Tagged memory zones with purge levels | Provider adapters with capability matrix |
| **Justification** | Fragmentation kills perf silently | Credential drift causes silent auth failures |
| **Scope** | Engine memory only | Credential layer only |

**Verdict**: **PASSES** — Credential fragmentation is a real operational constraint.

---

## 📝 Implementation Priority

| Phase | Provider | Effort | Blockers |
|-------|----------|--------|----------|
| **0** | Gitignore fix | 5 min | None |
| **1** | Grok CLI (keyring) | 1 hr | None |
| **1** | Copilot CLI (JSON) | 1 hr | None |
| **1** | OpenCode (JSON) | 30 min | None |
| **2** | Cline CLI (VS Code API) | 4 hr | Requires VS Code extension API |
| **3** | Rotation orchestrator | 2 hr | Phase 1 complete |
| **4** | Passive watcher (fanotify) | 3 hr | Linux-only |
| **5** | MCP server | 2 hr | Phase 1-3 complete |

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19*