# 🔱 VaultCore Schema v2 — FleetOrchestrator Credential Architecture
**AP Token**: `AP-VAULT-SCHEMA-v2.0.0`
**Status**: DESIGN — Ready for Implementation
**Owner**: `@maat` / `@pillar P3`

---

## 🎯 Design Goals

1. **Unified Credential Store**: Single schema for 32 heterogeneous credentials (8 AGY OAuth, 8 Grok auth.json, 8 Google GCP SA, 8 OpenRouter/Exa/Firecrawl API keys)
2. **M25 Compliance**: Lease TTLs, heartbeat, graceful fallback on stream timeout
3. **Encryption at Rest**: Argon2id key derivation → age (Actually Good Encryption) ciphertext
4. **Quota Awareness**: Per-credential daily limits, cooldown tracking, tier awareness
5. **Audit Trail**: Rotation timestamps, lease history, access logging

---

## 📐 Data Models

### Core Credential Model

```python
# src/omega/vault/models.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CredentialType(str, Enum):
    OAUTH = "oauth"           # AGY: access_token + refresh_token
    API_KEY = "api_key"       # OpenRouter, Exa, Firecrawl
    GCP_SA = "gcp_sa"         # Google Service Account JSON
    GROK_AUTH = "grok_auth"   # Grok CLI auth.json blob

class CredentialTier(str, Enum):
    FREE = "free"
    PAID = "paid"
    BYOK = "byok"             # Bring Your Own Key (OpenRouter BYOK)

class CredentialStatus(str, Enum):
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    COOLING = "cooling"
    LOCKED = "locked"
    EXPIRED = "expired"

class VaultCredential(BaseModel):
    """Unified credential record for FleetOrchestrator."""
    
    # Identity
    provider: Literal["antigravity", "grok", "google", "openrouter", "exa", "firecrawl"]
    key_id: str = Field(description="Unique key within provider (e.g., 'agy-0', 'grok-3')")
    cred_type: CredentialType
    
    # Encrypted Payload
    # Encryption: Argon2id(master_password) -> age encrypt(plaintext_json)
    encrypted_blob: str = Field(description="age-armored ciphertext")
    
    # Quota & Tier Management
    tier: CredentialTier = CredentialTier.FREE
    daily_limit: int = Field(default=0, description="Requests per day (0 = unlimited)")
    used_today: int = Field(default=0, description="Counter reset at midnight UTC")
    cooldown_until: Optional[datetime] = Field(default=None, description="ISO timestamp when cooldown ends")
    status: CredentialStatus = CredentialStatus.ACTIVE
    
    # Rotation & Audit
    rotated_at: datetime = Field(default_factory=datetime.utcnow)
    rotation_count: int = Field(default=0)
    last_used_at: Optional[datetime] = None
    last_error: Optional[str] = None
    
    # M25 Lease Management
    current_lease_agent: Optional[str] = Field(default=None, description="Agent ID holding lease")
    lease_expires_at: Optional[datetime] = Field(default=None)
    
    # Metadata
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('encrypted_blob')
    def validate_age_armor(cls, v):
        """Ensure blob is age-armored (starts with 'age-encryption.org/v1')."""
        if not v.startswith("age-encryption.org/v1"):
            raise ValueError("encrypted_blob must be age-armored ciphertext")
        return v


class VaultLeaseRequest(BaseModel):
    """Request to lease a credential for a time-bounded operation."""
    agent_id: str = Field(description="Requesting agent identifier")
    provider: str = Field(description="Target provider")
    key_id: Optional[str] = Field(default=None, description="Specific key, or None for any available")
    ttl_seconds: int = Field(default=300, le=3600, description="Max lease duration (1 hour)")
    purpose: str = Field(default="inference", description="Operation purpose for audit")


class VaultLease(BaseModel):
    """Granted lease for a credential."""
    lease_id: str
    credential_ref: str = Field(description="provider:key_id")
    agent_id: str
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    purpose: str
    
    # Heartbeat for M25 streaming resilience
    last_heartbeat: Optional[datetime] = None
    heartbeat_interval_seconds: int = 30


class VaultAuditEntry(BaseModel):
    """Immutable audit log entry."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    action: Literal["lease_granted", "lease_released", "lease_expired", "credential_used", "credential_rotated", "credential_locked"]
    credential_ref: str
    details: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
```

---

## 🔐 Encryption Architecture

### Key Derivation
```
Master Password (user-provided or env: OMEGA_VAULT_MASTER_KEY)
    │
    ▼
Argon2id(memory=64MB, iterations=3, parallelism=4, salt=16 bytes)
    │
    ▼
32-byte encryption key
    │
    ▼
age.Encrypt(key) → age-armored ciphertext
```

### Implementation
```python
# src/omega/vault/crypto.py
import age
import argon2
from argon2 import PasswordHasher

class VaultCrypto:
    def __init__(self, master_key: str):
        self._ph = PasswordHasher(
            time_cost=3,
            memory_cost=65536,  # 64 MB
            parallelism=4,
            hash_len=32,
            salt_len=16
        )
        self._master_key = master_key
        self._derived_key: Optional[bytes] = None
    
    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from master password + salt."""
        return self._ph.hash(self._master_key + salt.decode()).encode()[:32]
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext JSON to age-armored ciphertext."""
        salt = os.urandom(16)
        key = self._derive_key(salt)
        # age uses X25519 + ChaCha20-Poly1305
        recipient = age.X25519Recipient(key)
        ciphertext = age.encrypt(recipient, plaintext.encode())
        # Prepend salt for key derivation on decrypt
        return salt.hex() + ":" + ciphertext
    
    def decrypt(self, armored: str) -> str:
        """Decrypt age-armored ciphertext to plaintext JSON."""
        salt_hex, ciphertext = armored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        key = self._derive_key(salt)
        identity = age.X25519Identity(key)
        return age.decrypt(identity, ciphertext).decode()
```

---

## 📋 Credential Payloads (Plaintext JSON before encryption)

### AGY OAuth (`cred_type: "oauth"`)
```json
{
  "access_token": "ya29.a0AfH6SMC...",
  "refresh_token": "1//0g...",
  "expires_at": "2026-07-24T10:30:00Z",
  "auth_method": "oauth",
  "scopes": ["https://www.googleapis.com/auth/generative-language"]
}
```

### Grok CLI (`cred_type: "grok_auth"`)
```json
{
  "auth_json": "{\"access_token\": \"...\", \"refresh_token\": \"...\", \"expires_at\": \"...\"}",
  "grok_home": "/home/user/.grok-accounts/account-3"
}
```

### Google GCP Service Account (`cred_type: "gcp_sa"`)
```json
{
  "type": "service_account",
  "project_id": "omega-gcp-3",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "omega-sa@omega-gcp-3.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

### OpenRouter / Exa / Firecrawl (`cred_type: "api_key"`)
```json
{
  "api_key": "sk-or-v1-...",
  "base_url": "https://openrouter.ai/api/v1",
  "model_allowlist": ["google/gemma-4-31b-it:free", "deepseek/deepseek-v4-flash:free"]
}
```

---

## 🔄 Lease Lifecycle (M25 Compliance)

```
┌─────────────┐     Request Lease      ┌─────────────┐
│   Agent     │ ─────────────────────► │ VaultCore   │
└─────────────┘   (provider, ttl)      └──────┬──────┘
                                              │
                    ┌─────────────────────────┘
                    ▼
            ┌───────────────┐
            │ Check Status  │
            │ • ACTIVE?     │
            │ • Not EXHAUSTED?     │
            │ • Not COOLING?       │
            │ • No active lease?   │
            └───────┬───────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
      GRANTED               DENIED
         │                     │
         ▼                     ▼
┌─────────────────┐    ┌─────────────────┐
│ Create Lease    │    │ Return Error:   │
│ • lease_id      │    │ EXHAUSTED /     │
│ • expires_at    │    │ COOLDOWN /      │
│ • heartbeat=30s │    │ LEASED          │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Agent Uses      │
│ Credential      │
│ (heartbeat      │
│ every 30s)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Release /       │
│ Expire          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update          │
│ • used_today++  │
│ • last_used_at  │
│ • status check  │
└─────────────────┘
```

---

## 📊 Quota & Tier Matrix

| Provider | Tier | Daily Limit | Cooldown | Rotation |
|----------|------|-------------|----------|----------|
| Antigravity (8) | PAID (OAuth) | 1000 req/day | 1h on 429 | 7 days |
| Grok CLI (8) | FREE (auth.json) | 50 req/day | 24h on 402 | 30 days |
| Google GCP (8) | FREE (per-project) | 60 req/min | 1h on 429 | 30 days |
| OpenRouter (4) | FREE / BYOK | 50-1000 req/day | 1h on 429 | 7 days |
| Exa (2) | FREE | 150 req/day | 1h on 429 | 30 days |
| Firecrawl (2) | FREE | 10 req/min | 1h on 429 | 30 days |

---

## 🛠️ Implementation Checklist

- [ ] `src/omega/vault/models.py` — Pydantic models above
- [ ] `src/omega/vault/crypto.py` — Argon2id + age encryption
- [ ] `src/omega/vault/vault_core.py` — Core CRUD + lease manager
- [ ] `src/omega/vault/audit.py` — Append-only audit log (JSONL)
- [ ] `src/omega/vault/quota.py` — Daily reset, cooldown logic
- [ ] `tests/test_vault_schema.py` — Property tests for lease lifecycle
- [ ] `tests/test_vault_crypto.py` — Round-trip encryption tests
- [ ] Migration script: `vault_core.py` v1 → v2

---

## 🔗 Integration Points

| Component | Integration |
|-----------|-------------|
| **FleetOrchestrator** | `vault.lease(provider="antigravity", ttl=300)` |
| **Provider Fabric** | `vault.get_decrypted(credential_ref)` for API calls |
| **Scribe Hub Master** | Audit log entries → Hub decisions/blockers |
| **Health Monitor** | Lease expiration alerts, quota exhaustion warnings |

---

*🔱 OMEGA ⬡ MAAT ⬡ VAULT-SCHEMA-v2 ⬡ 2026-07-23*