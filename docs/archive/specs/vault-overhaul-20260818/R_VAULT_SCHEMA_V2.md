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
6. **BlindVault Resolver Integration**: `{{secret:NAME}}` pattern injection at last moment, output scrubbing
7. **Bury PID-Bound Fallback**: Session dies with process tree (PID reuse detected via start time)
5. **R19 Privacy Tiers**: PUBLIC/BONDED/PRIVATE split with CPE (Cumulative PII Exposure) scoring

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
    
    # R19 Privacy Tier (for credential metadata)
    visibility: Literal["public", "bonded", "private"] = "private"
    
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
import os
import age
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
        # Argon2id hash includes salt; we extract the raw key
        hash_str = self._ph.hash(self._master_key + salt.decode())
        # Use first 32 bytes of hash as key
        return hash_str.encode()[:32]
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext JSON to age-armored ciphertext."""
        salt = os.urandom(16)
        key = self._derive_key(salt)
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

## 🛡️ BlindVault Resolver Integration (Selected Backend)

### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                     BLINDVAULT RESOLVER                         │
├─────────────────────────────────────────────────────────────────┤
│  Agent Config:                                                  │
│    provider: "antigravity"                                      │
│    api_key: "{{secret:AGY_API_KEY_0}}"                         │
│                                                                 │
│  Runtime:                                                       │
│    1. Agent reads config → sees placeholder                     │
│    2. Provider fabric calls VaultCore.get_decrypted()           │
│    3. VaultCore → BlindVault resolver (bv run / proxy)         │
│    4. BlindVault decrypts, injects at LAST MOMENT              │
│    5. Response scrubbed before returning to agent              │
└─────────────────────────────────────────────────────────────────┘
```

### BlindVault Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| `{{secret:NAME}}` | Inline secret injection | `api_key: "{{secret:OPENROUTER_KEY}}"` |
| `bv run -- <cmd>` | Process injection | `bv run -- python agent.py` |
| `bv serve` | Resolver proxy (HTTP) | Local proxy for MCP tools |

### Security Properties (from BlindVault SECURITY.md)
- **Agent never holds plaintext** — resolver injects at syscall boundary
- **Output scrubbing** — responses scanned for leaked secrets
- **Host/command allowlists** — per-secret usage policies
- **Master password + Fernet** — Argon2id KDF, encrypted vault at rest
- **OS user isolation** — separate UID for vault broker (optional but recommended)

### Integration with VaultCore

```python
# src/omega/vault/blindvault_resolver.py
class BlindVaultResolver:
    """Bridge between VaultCore and BlindVault resolver."""
    
    def __init__(self, vault_path: Path, master_key: str):
        self.vault_path = vault_path
        self.master_key = master_key
    
    async def resolve(self, secret_ref: str) -> str:
        """Resolve {{secret:NAME}} to plaintext value."""
        # Extract secret name
        if not secret_ref.startswith("{{secret:") or not secret_ref.endswith("}}"):
            raise ValueError(f"Invalid secret reference: {secret_ref}")
        secret_name = secret_ref[9:-2]  # Remove {{secret: and }}
        
        # Call BlindVault resolver (via bv CLI or proxy)
        # bv get <secret_name> --vault <path> --master-key <key>
        proc = await anyio.open_process(
            ["bv", "get", secret_name, "--vault", str(self.vault_path)],
            env={"BLINDVAULT_MASTER_KEY": self.master_key}
        )
        stdout, _ = await proc.communicate()
        if proc.returncode != 0:
            raise VaultError(f"BlindVault resolver failed: {stdout}")
        return stdout.decode().strip()
    
    async def inject_into_config(self, config: dict) -> dict:
        """Recursively resolve all {{secret:NAME}} placeholders in config."""
        async def resolve_value(v):
            if isinstance(v, str) and v.startswith("{{secret:") and v.endswith("}}"):
                return await self.resolve(v)
            elif isinstance(v, dict):
                return {k: await resolve_value(vv) for k, vv in v.items()}
            elif isinstance(v, list):
                return [await resolve_value(vv) for vv in v]
            return v
        
        return await resolve_value(config)
```

---

## 🔁 Bury Fallback — PID-Bound Session Model

### When to Use Bury Over BlindVault

| Requirement | Backend |
|-------------|---------|
| Process-tree-scoped sessions (agent dies = session dies) | **Bury** |
| Real-time audit visibility during agent run | **Bury** |
| OS-enforced boundary (separate user, kernel-enforced) | **BlindVault** |
| PostgreSQL connector (passwordless DB access) | **BlindVault** |
| Windows support (named pipe + SID auth) | **BlindVault** |
| MCP server for Claude Code / OpenCode | **BlindVault** (planned) / **Keyblind** (ready) |

### Bury Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        BURY VAULT                               │
├─────────────────────────────────────────────────────────────────┤
│  Credential Format: [CRED:path/to/secret]                       │
│  Session Binding: PID + process start time (detects PID reuse) │
│  Audit Log: Real-time access.log (JSONL)                       │
│  Access Control: Path glob allow/deny lists                    │
└─────────────────────────────────────────────────────────────────┘
```

### Bury Session Lifecycle
```python
# src/omega/vault/bury_backend.py
class BuryBackend:
    """Bury vault backend with PID-bound sessions."""
    
    def __init__(self, vault_path: Path, master_key: str):
        self.vault_path = vault_path
        self.master_key = master_key
        self._session_pid: Optional[int] = None
        self._session_start_time: Optional[float] = None
    
    def start_session(self, agent_pid: int) -> str:
        """Start PID-bound session. Returns session token."""
        self._session_pid = agent_pid
        self._session_start_time = self._get_process_start_time(agent_pid)
        # bury session start --pid <pid> --start-time <ts>
        return self._generate_session_token()
    
    def _verify_session_alive(self) -> bool:
        """Verify PID still exists AND start time matches (detects PID reuse)."""
        if self._session_pid is None:
            return False
        try:
            current_start = self._get_process_start_time(self._session_pid)
            return abs(current_start - self._session_start_time) < 1.0
        except ProcessLookupError:
            return False
    
    def get_credential(self, path: str) -> str:
        """Get credential if session alive."""
        if not self._verify_session_alive():
            raise VaultError("Session dead — PID not found or reused")
        # bury get <path> --session <token>
        ...
    
    def end_session(self) -> None:
        """End session immediately (agent crash/exit)."""
        # bury session end --session <token>
        self._session_pid = None
        self._session_start_time = None
```

---

## 🔒 R19 Integration: PUBLIC/BONDED/PRIVATE Split with CPE Scoring

### Visibility Tiers for Credential Metadata

| Tier | Scope | Stored In | Git | Restic | Cloud Fallback |
|------|-------|-----------|-----|--------|----------------|
| **PUBLIC** | Provider names, key IDs, tier, rotation schedule | `vault.public.yaml` | ✅ Tracked | ✅ Full backup | ✅ Allowed |
| **BONDED** | Bonded-entity lease history, shared quota pools | `vault.private/bonds/` | ❌ Ignored | ✅ Encrypted | ❌ Never |
| **PRIVATE** | Encrypted blobs, actual secrets, usage details, errors | `vault.private/` | ❌ Ignored | ✅ Encrypted + age envelope | ❌ Never |

### Credential Visibility Field
```python
# Added to VaultCredential model
visibility: Literal["public", "bonded", "private"] = "private"
```

### Recall Engine Privacy Filtering
```python
# src/omega/vault/recall.py
async def recall_credentials(
    entity: str, 
    requester: str, 
    bond_strength: int,
    provider: Optional[str] = None
) -> List[VaultCredential]:
    """Privacy-filtered credential recall based on R19 visibility tiers."""
    all_creds = await load_all_credentials(entity)
    
    filtered = []
    for cred in all_creds:
        vis = cred.visibility
        if vis == "public":
            filtered.append(cred)
        elif vis == "bonded" and bond_strength >= 50:  # Configurable threshold
            filtered.append(cred)
        elif vis == "private" and requester == entity:
            filtered.append(cred)
        # Else: silently filtered out
    
    if provider:
        filtered = [c for c in filtered if c.provider == provider]
    
    return filtered
```

### CPE (Cumulative PII Exposure) Scoring for Credential Operations

Adapted from CAMP (Panjwani et al. 2026, arXiv:2604.16521):

```python
# src/omega/vault/cpe_scorer.py
class CredentialCPESession:
    """Tracks cumulative PII exposure during credential operations."""
    
    # Entity weights for credential-related PII
    ENTITY_WEIGHTS = {
        "API_KEY": 0.8,       # Direct credential exposure
        "OAUTH_TOKEN": 0.7,   # Access token
        "REFRESH_TOKEN": 0.9, # Long-lived, high value
        "PRIVATE_KEY": 1.0,   # GCP SA private key — critical
        "PROJECT_ID": 0.2,    # Metadata
        "EMAIL": 0.3,         # Service account email
        "ENDPOINT": 0.1,      # API endpoint URL
    }
    
    COOCCURRENCE_BOOST = {
        ("PRIVATE_KEY", "PROJECT_ID"): 0.5,
        ("REFRESH_TOKEN", "API_KEY"): 0.4,
        ("OAUTH_TOKEN", "EMAIL"): 0.3,
    }
    
    THRESHOLDS = {
        "LOW": 1.0,      # Pass — log but allow
        "MODERATE": 2.0, # Warn — log, require acknowledgment
        "HIGH": 3.0,     # Pseudonymize — mask in logs/audit
        "CRITICAL": 4.0, # Block — hard stop operation
    }
    
    def __init__(self, threshold: float = 2.0, alpha: float = 0.3):
        self.threshold = threshold
        self.alpha = alpha  # Graph amplifier
        self.registry: Dict[str, List[PIIEntity]] = defaultdict(list)
        self.cooccurrence_graph: nx.Graph = nx.Graph()
    
    def process_credential_access(self, credential: VaultCredential, operation: str) -> CPEAction:
        """Process a credential access event, compute CPE, decide action."""
        # Extract PII entities from credential payload (decrypted)
        entities = self._extract_credential_pii(credential)
        
        # Update registry
        for ent in entities:
            self.registry[ent.type].append(PIIEntity(
                value=ent.value, type=ent.type, 
                turn=len(self.registry[ent.type]), 
                span=(0, len(ent.value))
            ))
            self.cooccurrence_graph.add_node(ent.type)
        
        # Add co-occurrence edges
        types_in_op = {e.type for e in entities}
        for t1 in types_in_op:
            for t2 in types_in_op:
                if t1 != t2:
                    self.cooccurrence_graph.add_edge(t1, t2, weight=1)
        
        # Compute CPE
        cpe = self._compute_cpe()
        
        # Decide action
        if cpe >= self.THRESHOLDS["CRITICAL"]:
            return CPEAction.BLOCK
        elif cpe >= self.THRESHOLDS["HIGH"]:
            return CPEAction.PSEUDONYMIZE
        elif cpe >= self.THRESHOLDS["MODERATE"]:
            return CPEAction.WARN
        return CPEAction.PASS
    
    def _compute_cpe(self) -> float:
        """CPE = Σ(entity_weight * count) + α * Σ(edge_weight * cooccurrence_boost)"""
        base = sum(
            self.ENTITY_WEIGHTS.get(t, 0.1) * len(ents) 
            for t, ents in self.registry.items()
        )
        graph_boost = sum(
            self.COOCCURRENCE_BOOST.get((u, v), 0) * d.get("weight", 1)
            for u, v, d in self.cooccurrence_graph.edges(data=True)
        )
        return base + self.alpha * graph_boost
    
    def pseudonymize_audit_entry(self, entry: VaultAuditEntry) -> VaultAuditEntry:
        """Retroactive pseudonymization for HIGH/Critical CPE audit entries."""
        fake = Faker()
        pseudonym_map = {}
        
        for ent_type, entities in self.registry.items():
            for ent in entities:
                if ent.value not in pseudonym_map:
                    if ent_type == "PRIVATE_KEY":
                        pseudonym_map[ent.value] = "<<PRIVATE_KEY_REDACTED>>"
                    elif ent_type == "REFRESH_TOKEN":
                        pseudonym_map[ent.value] = f"<<REFRESH_TOKEN_{len(pseudonym_map)}>>"
                    elif ent_type == "API_KEY":
                        pseudonym_map[ent.value] = f"<<API_KEY_{len(pseudonym_map)}>>"
                    else:
                        pseudonym_map[ent.value] = f"<<{ent_type}_{len(pseudonym_map)}>>"
        
        # Rewrite entry details
        new_details = json.dumps(entry.details)
        for real, fake_val in pseudonym_map.items():
            new_details = new_details.replace(real, fake_val)
        
        return VaultAuditEntry(
            **entry.model_dump(),
            details=json.loads(new_details)
        )
```

---

## 🛠️ Implementation Checklist

- [ ] `src/omega/vault/models.py` — Pydantic models (VaultCredential, VaultLease, VaultAuditEntry, CPE types)
- [ ] `src/omega/vault/crypto.py` — Argon2id + age encryption
- [ ] `src/omega/vault/vault_core.py` — Core CRUD + lease manager + quota logic
- [ ] `src/omega/vault/blindvault_resolver.py` — BlindVault `{{secret:NAME}}` resolver bridge
- [ ] `src/omega/vault/bury_backend.py` — Bury PID-bound session fallback
- [ ] `src/omega/vault/cpe_scorer.py` — Cumulative PII Exposure scoring
- [ ] `src/omega/vault/recall.py` — R19 privacy-filtered recall (PUBLIC/BONDED/PRIVATE)
- [ ] `src/omega/vault/audit.py` — Append-only audit log (JSONL) with CPE pseudonymization
- [ ] `src/omega/vault/quota.py` — Daily reset, cooldown logic, tier enforcement
- [ ] `tests/test_vault_schema.py` — Property tests for lease lifecycle
- [ ] `tests/test_vault_crypto.py` — Round-trip encryption tests
- [ ] `tests/test_vault_cpe.py` — CPE scoring property tests
- [ ] `tests/test_vault_privacy.py` — PUBLIC/BONDED/PRIVATE filter tests
- [ ] Migration script: `scripts/migrate_vault_v1_to_v2.py`
- [ ] BlindVault integration test: `tests/integration/test_blindvault_resolver.py`
- [ ] Bury fallback test: `tests/integration/test_bury_pid_bound.py`

---

## 🔗 Integration Points

| Component | Integration |
|-----------|-------------|
| **FleetOrchestrator** | `vault.lease(provider="antigravity", ttl=300)` |
| **Provider Fabric** | `vault.get_decrypted(credential_ref)` for API calls |
| **Scribe Hub Master** | Audit log entries → Hub decisions/blockers |
| **Health Monitor** | Lease expiration alerts, quota exhaustion warnings |
| **BlindVault** | `bv run` / resolver proxy for secret injection |
| **Bury** | `vault agent --backend bury --allow "work/*" -- claude` |
| **R19 Soul Privacy** | Shared visibility tier logic, CPE scorer reuse |

---

## 📋 Decision Gates

| Gate | Criteria | Decision |
|------|----------|----------|
| **G1: Schema Complete** | All models defined, encryption round-trips, lease lifecycle tests pass | Go/No-Go |
| **G2: BlindVault Integrated** | `{{secret:NAME}}` resolution works; output scrubbing verified | Go/No-Go |
| **G3: Bury Fallback Works** | PID-bound session dies with process tree; audit log emits JSONL | Go/No-Go |
| **G4: R19 Privacy Tiers** | PUBLIC/BONDED/PRIVATE filters work; CPE scorer blocks/pseudonymizes correctly | Go/No-Go |
| **G5: Backup Verified** | Restic multi-repo (public/bonded/private) backup + restore successful | Go/No-Go |

---

## 🔑 Key References

| Source | Key Insight Applied |
|--------|---------------------|
| **BlindVault (psypilot/blindvault)** | `{{secret:NAME}}` resolver pattern; output scrubbing; host/command allowlists; master-pw + Fernet |
| **Bury (hammerhoundai/bury)** | PID-bound sessions (PID + start time); real-time `access.log`; `[CRED:path]` format; `vault-proxy` |
| **R19 Soul Privacy Model** | PUBLIC/BONDED/PRIVATE visibility tiers; CPE scoring; gitignored private dirs; restic selective backup |
| **CAMP (Panjwani 2026)** | Cumulative PII Exposure scoring; co-occurrence graph; retroactive pseudonymization |
| **CloakBot** | Local privacy kernel; session vault; streaming placeholder restoration |

---

*🔱 OMEGA ⬡ MAAT ⬡ VAULT-SCHEMA-v2 ⬡ 2026-07-24*