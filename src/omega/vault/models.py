"""
VaultCore Models — Unified Credential Schema for FleetOrchestrator
AP: AP-VAULT-MODELS-v2.0.0
⬡ OMEGA ⬡ P3 ⬡ vault_models ⬡ FLEET-ORCHESTRATOR

Implements R_VAULT_SCHEMA_V2.md:
- VaultCredential, VaultLease, VaultAuditEntry
- CredentialType, CredentialTier, CredentialStatus
- CPE types for credential operations
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from dataclasses import dataclass

from pydantic import BaseModel, Field, field_validator, computed_field


class CredentialType(str, Enum):
    OAUTH = "oauth"  # AGY: access_token + refresh_token
    API_KEY = "api_key"  # OpenRouter, Exa, Firecrawl
    GCP_SA = "gcp_sa"  # Google Service Account JSON
    GROK_AUTH = "grok_auth"  # Grok CLI auth.json blob


class CredentialTier(str, Enum):
    FREE = "free"
    PAID = "paid"
    BYOK = "byok"  # Bring Your Own Key (OpenRouter BYOK)


class CredentialStatus(str, Enum):
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    COOLING = "cooling"
    LOCKED = "locked"
    EXPIRED = "expired"


class VisibilityTier(str, Enum):
    PUBLIC = "public"
    BONDED = "bonded"
    PRIVATE = "private"


class ProviderName(str, Enum):
    """Known provider names for credential storage."""

    GOOGLE = "google"
    ANTIGRAVITY = "antigravity"
    OPENROUTER = "openrouter"
    EXA = "exa"
    FIRECRAWL = "firecrawl"
    GROK = "grok"
    XAI = "xai"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LMSTUDIO = "lmstudio"
    OLLAMA = "ollama"
    NATIVE_GGUF = "native-gguf"
    SEARXNG = "searxng"
    PARALLEL = "parallel"
    HUGGINGFACE = "huggingface"
    CEREBRAS = "cerebras"
    SAMBANOVA = "sambanova"
    TOGETHER = "together"
    DEEPINFRA = "deepinfra"
    REPLICATE = "replicate"
    PERPLEXITY = "perplexity"
    MISTRAL = "mistral"
    COHERE = "cohere"
    VOYAGE = "voyage"
    JINA = "jina"
    CUSTOM = "custom"


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
    cooldown_until: Optional[datetime] = Field(
        default=None, description="ISO timestamp when cooldown ends"
    )
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
    visibility: VisibilityTier = VisibilityTier.PRIVATE

    # Metadata
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("encrypted_blob")
    @classmethod
    def validate_age_armor(cls, v: str) -> str:
        """Ensure blob is age-armored (starts with 'age-encryption.org/v1' or '-----BEGIN AGE ENCRYPTED FILE-----')."""
        if not (
            v.startswith("age-encryption.org/v1")
            or v.startswith("-----BEGIN AGE ENCRYPTED FILE-----")
        ):
            raise ValueError("encrypted_blob must be age-armored ciphertext")
        return v

    @computed_field(return_type=str)
    @property
    def credential_ref(self) -> str:
        """Unique reference: provider:key_id"""
        return f"{self.provider}:{self.key_id}"

    def is_available(self) -> bool:
        """Check if credential is available for use."""
        if self.status != CredentialStatus.ACTIVE:
            return False
        if self.daily_limit > 0 and self.used_today >= self.daily_limit:
            return False
        if self.cooldown_until and datetime.utcnow() < self.cooldown_until:
            return False
        return True

    def is_leased(self) -> bool:
        """Check if credential is currently leased."""
        if not self.current_lease_agent or not self.lease_expires_at:
            return False
        return datetime.utcnow() < self.lease_expires_at


class VaultLeaseRequest(BaseModel):
    """Request to lease a credential for a time-bounded operation."""

    agent_id: str = Field(description="Requesting agent identifier")
    provider: str = Field(description="Target provider")
    key_id: Optional[str] = Field(
        default=None, description="Specific key, or None for any available"
    )
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

    def is_valid(self) -> bool:
        """Check if lease is still valid."""
        return datetime.utcnow() < self.expires_at

    def needs_heartbeat(self) -> bool:
        """Check if heartbeat is due."""
        if not self.last_heartbeat:
            return True
        elapsed = (datetime.utcnow() - self.last_heartbeat).total_seconds()
        return elapsed >= self.heartbeat_interval_seconds


class VaultAuditEntry(BaseModel):
    """Immutable audit log entry."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    action: Literal[
        "lease_granted",
        "lease_released",
        "lease_expired",
        "credential_used",
        "credential_rotated",
        "credential_locked",
        "credential_created",
        "credential_deleted",
        "credential_retrieved",
        "credential_updated",
    ]
    credential_ref: str
    details: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None

    # CPE pseudonymization metadata
    cpe_score: Optional[float] = None
    cpe_action: Optional[str] = None
    pseudonymized: bool = False


# =============================================================================
# CPE Types for Credential Operations
# =============================================================================


class CPEAction(str, Enum):
    PASS = "pass"
    WARN = "warn"
    PSEUDONYMIZE = "pseudonymize"
    BLOCK = "block"


@dataclass
class CredentialPIIEntity:
    """PII entity extracted from credential."""

    value: str
    type: str
    turn: int
    span: tuple[int, int]


class CredentialCPESession:
    """Tracks cumulative PII exposure during credential operations."""

    # Entity weights for credential-related PII
    ENTITY_WEIGHTS = {
        "API_KEY": 0.8,  # Direct credential exposure
        "OAUTH_TOKEN": 0.7,  # Access token
        "REFRESH_TOKEN": 0.9,  # Long-lived, high value
        "PRIVATE_KEY": 1.0,  # GCP SA private key — critical
        "PROJECT_ID": 0.2,  # Metadata
        "EMAIL": 0.3,  # Service account email
        "ENDPOINT": 0.1,  # API endpoint URL
    }

    COOCCURRENCE_BOOST = {
        ("PRIVATE_KEY", "PROJECT_ID"): 0.5,
        ("REFRESH_TOKEN", "API_KEY"): 0.4,
        ("OAUTH_TOKEN", "EMAIL"): 0.3,
    }

    THRESHOLDS = {
        "LOW": 1.0,  # Pass — log but allow
        "MODERATE": 2.0,  # Warn — log, require acknowledgment
        "HIGH": 3.0,  # Pseudonymize — mask in logs/audit
        "CRITICAL": 4.0,  # Block — hard stop operation
    }

    def __init__(self, threshold: float = 2.0, alpha: float = 0.3):
        self.threshold = threshold
        self.alpha = alpha  # Graph amplifier
        self.registry: Dict[str, List[CredentialPIIEntity]] = {}
        self.cooccurrence_graph: Dict[tuple, int] = {}
        self.pseudonym_map: Dict[str, str] = {}

    def process_credential_access(self, credential: VaultCredential, operation: str) -> CPEAction:
        """Process a credential access event, compute CPE, decide action."""
        entities = self._extract_credential_pii(credential)

        # Update registry
        for ent in entities:
            if ent.type not in self.registry:
                self.registry[ent.type] = []
            self.registry[ent.type].append(ent)

            # Add node to co-occurrence graph
            if (ent.type, ent.type) not in self.cooccurrence_graph:
                self.cooccurrence_graph[(ent.type, ent.type)] = 0
            self.cooccurrence_graph[(ent.type, ent.type)] += 1

        # Add co-occurrence edges
        types_in_op = {e.type for e in entities}
        for t1 in types_in_op:
            for t2 in types_in_op:
                if t1 != t2:
                    edge = tuple(sorted([t1, t2]))
                    self.cooccurrence_graph[edge] = self.cooccurrence_graph.get(edge, 0) + 1

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

    def _extract_credential_pii(self, credential: VaultCredential) -> List[CredentialPIIEntity]:
        """Extract PII entities from credential payload (decrypted)."""
        # In production, this would decrypt the blob and extract PII
        # For now, return metadata-based entities
        entities = []

        # Provider-specific PII types
        if credential.cred_type == CredentialType.GCP_SA:
            entities.append(
                CredentialPIIEntity(
                    value=credential.metadata.get("project_id", ""),
                    type="PROJECT_ID",
                    turn=len(self.registry.get("PROJECT_ID", [])),
                    span=(0, 0),
                )
            )
            entities.append(
                CredentialPIIEntity(
                    value=credential.metadata.get("client_email", ""),
                    type="EMAIL",
                    turn=len(self.registry.get("EMAIL", [])),
                    span=(0, 0),
                )
            )
            entities.append(
                CredentialPIIEntity(
                    value=credential.metadata.get("private_key", ""),
                    type="PRIVATE_KEY",
                    turn=len(self.registry.get("PRIVATE_KEY", [])),
                    span=(0, 0),
                )
            )
        elif credential.cred_type == CredentialType.OAUTH:
            entities.append(
                CredentialPIIEntity(
                    value=credential.metadata.get("access_token", ""),
                    type="OAUTH_TOKEN",
                    turn=len(self.registry.get("OAUTH_TOKEN", [])),
                    span=(0, 0),
                )
            )
            entities.append(
                CredentialPIIEntity(
                    value=credential.metadata.get("refresh_token", ""),
                    type="REFRESH_TOKEN",
                    turn=len(self.registry.get("REFRESH_TOKEN", [])),
                    span=(0, 0),
                )
            )
        elif credential.cred_type == CredentialType.API_KEY:
            entities.append(
                CredentialPIIEntity(
                    value=credential.metadata.get("api_key", ""),
                    type="API_KEY",
                    turn=len(self.registry.get("API_KEY", [])),
                    span=(0, 0),
                )
            )

        return [e for e in entities if e.value]

    def _compute_cpe(self) -> float:
        """CPE = Σ(entity_weight * count) + α * Σ(edge_weight * cooccurrence_boost)"""
        base = sum(self.ENTITY_WEIGHTS.get(t, 0.1) * len(ents) for t, ents in self.registry.items())
        graph_boost = sum(
            self.COOCCURRENCE_BOOST.get(edge, 0) * weight
            for edge, weight in self.cooccurrence_graph.items()
            if edge[0] != edge[1]  # Skip self-loops
        )
        return base + self.alpha * graph_boost

    def pseudonymize_audit_entry(self, entry: VaultAuditEntry) -> VaultAuditEntry:
        """Retroactive pseudonymization for HIGH/Critical CPE audit entries."""
        from faker import Faker

        fake = Faker()

        new_details = entry.details.copy()

        for ent_type, entities in self.registry.items():
            for ent in entities:
                if ent.value not in self.pseudonym_map:
                    if ent_type == "PRIVATE_KEY":
                        self.pseudonym_map[ent.value] = "<<PRIVATE_KEY_REDACTED>>"
                    elif ent_type == "REFRESH_TOKEN":
                        self.pseudonym_map[ent.value] = (
                            f"<<REFRESH_TOKEN_{len(self.pseudonym_map)}>>"
                        )
                    elif ent_type == "API_KEY":
                        self.pseudonym_map[ent.value] = f"<<API_KEY_{len(self.pseudonym_map)}>>"
                    elif ent_type == "OAUTH_TOKEN":
                        self.pseudonym_map[ent.value] = f"<<OAUTH_TOKEN_{len(self.pseudonym_map)}>>"
                    else:
                        self.pseudonym_map[ent.value] = f"<<{ent_type}_{len(self.pseudonym_map)}>>"

        # Rewrite entry details
        import json

        details_str = json.dumps(new_details)
        for real, fake_val in self.pseudonym_map.items():
            details_str = details_str.replace(real, fake_val)

        return VaultAuditEntry(
            **entry.model_dump(),
            details=json.loads(details_str),
            pseudonymized=True,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CredentialType",
    "CredentialTier",
    "CredentialStatus",
    "VisibilityTier",
    "VaultCredential",
    "VaultLeaseRequest",
    "VaultLease",
    "VaultAuditEntry",
    "CPEAction",
    "CredentialPIIEntity",
    "CredentialCPESession",
]
