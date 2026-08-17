"""
Vault Module — Credential Management, Encryption, and Privacy
AP: AP-VAULT-PKG-v2.0.0
⬡ OMEGA ⬡ P3 ⬡ vault ⬡ CREDENTIAL-MANAGEMENT

Implements R_VAULT_SCHEMA_V2.md:
- VaultCredential, VaultLease, VaultAuditEntry models
- VaultCore CRUD + lease management
- BlindVault resolver integration
- Bury fallback backend
- CPE scoring for PII exposure
"""

from .models import (
    CredentialType,
    CredentialTier,
    CredentialStatus,
    VisibilityTier,
    ProviderName,
    VaultCredential,
    VaultLeaseRequest,
    VaultLease,
    VaultAuditEntry,
    CPEAction,
    CredentialPIIEntity,
    CredentialCPESession,
)

from .crypto import (
    VaultCrypto,
    VaultCryptoManager,
    create_vault_crypto,
    create_vault_crypto_manager,
)

from .vault_core import (
    VaultCore,
    VaultError,
    CredentialNotFoundError,
    LeaseError,
    QuotaExceededError,
    create_vault_core,
)

__all__ = [
    # Models
    "CredentialType",
    "CredentialTier",
    "CredentialStatus",
    "VisibilityTier",
    "ProviderName",
    "VaultCredential",
    "VaultLeaseRequest",
    "VaultLease",
    "VaultAuditEntry",
    "CPEAction",
    "CredentialPIIEntity",
    "CredentialCPESession",
    # Crypto
    "VaultCrypto",
    "VaultCryptoManager",
    "create_vault_crypto",
    "create_vault_crypto_manager",
    # Core
    "VaultCore",
    "VaultError",
    "CredentialNotFoundError",
    "LeaseError",
    "QuotaExceededError",
    "create_vault_core",
]
