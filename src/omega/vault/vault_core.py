# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
VaultCore — Core CRUD + Lease Manager + Quota Logic
AP: AP-VAULT-CORE-v2.0.0
⬡ OMEGA ⬡ P3 ⬡ vault_core ⬡ CREDENTIAL-MANAGEMENT

Implements R_VAULT_SCHEMA_V2.md:
- VaultCredential CRUD
- M25 lease management
- Quota awareness
- BlindVault integration
- Bury fallback
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


from omega.soul_store import get_soul_store

from .models import (
    CredentialType,
    CredentialStatus,
    CredentialTier,
    VisibilityTier,
    VaultCredential,
    VaultLease,
    VaultLeaseRequest,
    VaultAuditEntry,
    CPEAction,
    CredentialCPESession,
)

logger = logging.getLogger(__name__)


class VaultError(Exception):
    """Base exception for vault operations."""

    pass


class CredentialNotFoundError(VaultError):
    """Raised when credential is not found."""

    pass


class LeaseError(VaultError):
    """Raised when lease operation fails."""

    pass


class QuotaExceededError(VaultError):
    """Raised when credential quota is exceeded."""

    pass


class VaultCore:
    """
    Core vault operations for FleetOrchestrator.

    Manages credentials, leases, quotas, and privacy tiers.
    Integrates with BlindVault resolver and Bury fallback.
    """

    def __init__(
        self,
        vault_path: Path = Path("data/vault"),
        master_key: Optional[str] = None,
        crypto_manager=None,
        blindvault_resolver=None,
        bury_backend=None,
    ):
        """
        Initialize vault core.

        Args:
            vault_path: Path to vault data directory
            master_key: Master key for encryption (if using crypto)
            crypto_manager: Crypto manager instance
            blindvault_resolver: BlindVault resolver instance
            bury_backend: Bury backend instance
        """
        self.vault_path = vault_path
        self.vault_path.mkdir(parents=True, exist_ok=True)

        self.master_key = master_key
        self.crypto_manager = crypto_manager
        self.blindvault_resolver = blindvault_resolver
        self.bury_backend = bury_backend

        # Load CPE scorer for privacy compliance
        self.cpe_scorer = CredentialCPESession()

        # File paths
        self.credentials_file = self.vault_path / "credentials.json"
        self.leases_file = self.vault_path / "leases.json"
        self.audit_file = self.vault_path / "audit.json"

        # Load existing data
        self._load_data()

    def _load_data(self) -> None:
        """Load vault data from files."""
        self.credentials: Dict[str, VaultCredential] = {}
        self.leases: Dict[str, VaultLease] = {}
        self.audit: List[VaultAuditEntry] = []

        # Load credentials
        if self.credentials_file.exists():
            try:
                content = self.credentials_file.read_text(encoding="utf-8")
                creds_data = json.loads(content)
                self.credentials = {
                    cred["credential_ref"]: VaultCredential(**cred) for cred in creds_data.values()
                }
            except Exception as e:
                logger.error(f"Failed to load credentials: {e}")
                self.credentials = {}

        # Load leases
        if self.leases_file.exists():
            try:
                content = self.leases_file.read_text(encoding="utf-8")
                leases_data = json.loads(content)
                self.leases = {
                    lease["lease_id"]: VaultLease(**lease) for lease in leases_data.values()
                }
            except Exception as e:
                logger.error(f"Failed to load leases: {e}")
                self.leases = {}

        # Load audit
        if self.audit_file.exists():
            try:
                content = self.audit_file.read_text(encoding="utf-8")
                # Handle both JSONL (new) and JSON array (old) formats
                content = content.strip()
                if content.startswith("["):
                    # Old JSON array format
                    audit_data = json.loads(content)
                else:
                    # New JSONL format (one JSON object per line)
                    audit_data = [json.loads(line) for line in content.split("\n") if line.strip()]
                self.audit = [VaultAuditEntry(**entry) for entry in audit_data]
            except Exception as e:
                logger.error(f"Failed to load audit: {e}")
                self.audit = []

        # Backward compatibility: _credentials was renamed to credentials (10+ callers)
        self._credentials = self.credentials

    # Backward compatibility: _load_sync renamed to _load_data (13+ callers)
    _load_sync = _load_data

    async def _save_data(self) -> None:
        """Save vault data to files atomically."""
        # Save credentials
        creds_data = {cred.key_id: cred.model_dump() for cred in self.credentials.values()}
        await self._atomic_write(
            self.credentials_file, json.dumps(creds_data, indent=2, default=str)
        )

        # Save leases
        leases_data = {lease.lease_id: lease.model_dump() for lease in self.leases.values()}
        await self._atomic_write(self.leases_file, json.dumps(leases_data, indent=2, default=str))

        # Save audit (only last 1000 entries to prevent unbounded growth)
        audit_data = self.audit[-1000:]
        audit_lines = [json.dumps(entry.model_dump(), default=str) for entry in audit_data]
        await self._atomic_write(self.audit_file, "\n".join(audit_lines) + "\n")

    async def _atomic_write(self, path: Path, content: str) -> None:
        """Atomic write using SoulStore."""
        store = get_soul_store()
        await store.write_atomic(path, content)

    # =============================================================================
    # Credential Operations
    # =============================================================================

    async def create_credential(
        self,
        provider: str,
        key_id: str,
        encrypted_blob: str,
        cred_type: CredentialType,
        tier: CredentialTier = CredentialTier.FREE,
        visibility: VisibilityTier = VisibilityTier.PRIVATE,
        metadata: Optional[Dict[str, Any]] = None,
        daily_limit: int = 0,
    ) -> VaultCredential:
        """
        Create a new credential.

        Args:
            provider: Provider name (antigravity, grok, google, openrouter, exa, firecrawl)
            key_id: Unique key within provider
            encrypted_blob: age-armored ciphertext
            cred_type: Type of credential
            tier: Tier for quota management
            visibility: Privacy visibility tier
            metadata: Additional metadata
            daily_limit: Daily request limit (0 = unlimited)

        Returns:
            Created credential

        Raises:
            VaultError: If credential already exists
        """
        if provider not in ("antigravity", "grok", "google", "openrouter", "exa", "firecrawl"):
            raise VaultError(f"Invalid provider: {provider}")

        credential_ref = f"{provider}:{key_id}"
        if credential_ref in self.credentials:
            raise VaultError(f"Credential already exists: {credential_ref}")

        credential = VaultCredential(
            provider=provider,
            key_id=key_id,
            cred_type=cred_type,
            encrypted_blob=encrypted_blob,
            tier=tier,
            visibility=visibility,
            metadata=metadata or {},
            daily_limit=daily_limit,
        )

        self.credentials[credential.credential_ref] = credential
        await self._log_audit(
            action="credential_created",
            credential_ref=credential.credential_ref,
            details={
                "provider": provider,
                "key_id": key_id,
                "cred_type": cred_type.value,
                "tier": tier.value,
                "visibility": visibility.value,
            },
            agent_id="system",
        )

        await self._save_data()
        return credential

    async def get_credential(self, provider: str, key_id: str) -> VaultCredential:
        """
        Get credential by provider and key_id.

        Args:
            provider: Provider name
            key_id: Key ID

        Returns:
            Credential

        Raises:
            CredentialNotFoundError: If credential not found
        """
        credential_key = f"{provider}:{key_id}"
        if credential_key not in self.credentials:
            raise CredentialNotFoundError(f"Credential not found: {provider}:{key_id}")

        credential = self.credentials[credential_key]

        # Log access
        await self._log_audit(
            action="credential_retrieved",
            credential_ref=credential.credential_ref,
            details={},
            agent_id="system",
        )

        return credential

    # Backward compatibility: retrieve_credential renamed to get_credential
    async def retrieve_credential(
        self, provider: str, key_id: str = "default"
    ) -> Optional[VaultCredential]:
        """Backward-compatible alias for get_credential that returns None instead of raising."""
        try:
            return await self.get_credential(provider=provider, key_id=key_id)
        except CredentialNotFoundError:
            return None

    async def update_credential(
        self,
        provider: str,
        key_id: str,
        **kwargs,
    ) -> VaultCredential:
        """
        Update credential fields.

        Args:
            provider: Provider name
            key_id: Key ID
            **kwargs: Fields to update

        Returns:
            Updated credential
        """
        credential = await self.get_credential(provider, key_id)

        # Update fields
        update_data = kwargs.copy()

        # Special handling for encrypted_blob
        if "encrypted_blob" in update_data:
            # Re-encrypt with new key if needed
            pass

        # Update credential with new data
        updated_data = credential.model_dump()
        updated_data.update(update_data)
        updated_credential = VaultCredential(**updated_data)

        self.credentials[credential.credential_ref] = updated_credential
        await self._log_audit(
            action="credential_updated",
            credential_ref=credential.credential_ref,
            details={"fields_updated": list(update_data.keys())},
            agent_id="system",
        )

        await self._save_data()
        return updated_credential

    async def delete_credential(self, provider: str, key_id: str) -> bool:
        """
        Delete credential.

        Args:
            provider: Provider name
            key_id: Key ID

        Returns:
            True if credential was deleted, False if it didn't exist
        """
        credential_key = f"{provider}:{key_id}"
        if credential_key not in self.credentials:
            return False

        credential = self.credentials.pop(credential_key)
        await self._log_audit(
            action="credential_deleted",
            credential_ref=credential.credential_ref,
            details={},
            agent_id="system",
        )

        await self._save_data()
        return True

    async def list_credentials(
        self,
        provider: Optional[str] = None,
        tier: Optional[CredentialTier] = None,
        visibility: Optional[VisibilityTier] = None,
    ) -> List[VaultCredential]:
        """
        List credentials with optional filtering.

        Args:
            provider: Filter by provider
            tier: Filter by tier
            visibility: Filter by visibility

        Returns:
            List of credentials
        """
        credentials = list(self.credentials.values())

        if provider:
            credentials = [c for c in credentials if c.provider == provider]

        if tier:
            credentials = [c for c in credentials if c.tier == tier]

        if visibility:
            credentials = [c for c in credentials if c.visibility == visibility]

        return credentials

    # =============================================================================
    # Lease Operations
    # =============================================================================

    async def lease_credential(
        self,
        request: VaultLeaseRequest,
    ) -> VaultLease:
        """
        Lease a credential to an agent.

        Args:
            request: Lease request

        Returns:
            Created lease

        Raises:
            LeaseError: If lease cannot be granted
        """
        # Check if credential exists
        try:
            credential = await self.get_credential(request.provider, request.key_id or "")
        except CredentialNotFoundError:
            raise LeaseError(f"Credential not found: {request.provider}:{request.key_id}")

        # Check if credential is available
        if not credential.is_available():
            raise LeaseError(f"Credential not available: {request.provider}:{request.key_id}")

        # Check if credential is already leased
        existing_lease = next(
            (
                l
                for l in self.leases.values()
                if l.credential_ref == f"{request.provider}:{request.key_id}"
            ),
            None,
        )
        if existing_lease and existing_lease.is_valid():
            raise LeaseError(f"Credential already leased to {existing_lease.agent_id}")

        # Create lease
        lease_id = f"lease_{request.provider}_{request.key_id}_{datetime.utcnow().timestamp()}"
        lease = VaultLease(
            lease_id=lease_id,
            credential_ref=f"{request.provider}:{request.key_id}",
            agent_id=request.agent_id,
            expires_at=datetime.utcnow() + timedelta(seconds=request.ttl_seconds),
            purpose=request.purpose,
        )

        self.leases[lease.lease_id] = lease

        # Update credential lease info
        credential.current_lease_agent = request.agent_id
        credential.lease_expires_at = lease.expires_at
        credential.used_today += 1  # Simple usage tracking

        await self._log_audit(
            action="lease_granted",
            credential_ref=lease.credential_ref,
            details={
                "lease_id": lease_id,
                "agent_id": request.agent_id,
                "ttl_seconds": request.ttl_seconds,
                "purpose": request.purpose,
            },
            agent_id=request.agent_id,
        )

        await self._save_data()
        return lease

    async def release_lease(self, lease_id: str) -> bool:
        """
        Release a lease.

        Args:
            lease_id: Lease ID

        Returns:
            True if lease was released, False if it didn't exist
        """
        if lease_id not in self.leases:
            return False

        lease = self.leases.pop(lease_id)

        # Update credential lease info
        credential_ref = lease.credential_ref
        if credential_ref in self.credentials:
            cred = self.credentials[credential_ref]
            if cred.current_lease_agent == lease.agent_id:
                cred.current_lease_agent = None
                cred.lease_expires_at = None

        await self._log_audit(
            action="lease_released",
            credential_ref=lease.credential_ref,
            details={"lease_id": lease_id, "agent_id": lease.agent_id},
            agent_id=lease.agent_id,
        )

        await self._save_data()
        return True

    async def heartbeat_lease(self, lease_id: str) -> bool:
        """
        Send heartbeat for a lease (M25 compliance).

        Args:
            lease_id: Lease ID

        Returns:
            True if heartbeat was sent, False if lease not found
        """
        if lease_id not in self.leases:
            return False

        lease = self.leases[lease_id]
        lease.last_heartbeat = datetime.utcnow()

        await self._save_data()
        return True

    async def cleanup_expired_leases(self) -> List[str]:
        """
        Clean up expired leases.

        Returns:
            List of lease IDs that were cleaned up
        """
        now = datetime.utcnow()
        expired_leases = [
            lease_id for lease_id, lease in self.leases.items() if lease.expires_at < now
        ]

        for lease_id in expired_leases:
            lease = self.leases.pop(lease_id)

            # Update credential lease info
            credential_ref = lease.credential_ref
            if credential_ref in self.credentials:
                cred = self.credentials[credential_ref]
                if cred.current_lease_agent == lease.agent_id:
                    cred.current_lease_agent = None
                    cred.lease_expires_at = None

            await self._log_audit(
                action="lease_expired",
                credential_ref=lease.credential_ref,
                details={"lease_id": lease_id, "agent_id": lease.agent_id},
                agent_id=lease.agent_id,
            )

        if expired_leases:
            await self._save_data()

        return expired_leases

    # =============================================================================
    # Quota & Usage Operations
    # =============================================================================

    async def increment_usage(self, provider: str, key_id: str) -> bool:
        """
        Increment usage counter for credential.

        Args:
            provider: Provider name
            key_id: Key ID

        Returns:
            True if usage was incremented, False if credential not found or quota exceeded
        """
        try:
            credential = await self.get_credential(provider, key_id)
        except CredentialNotFoundError:
            return False

        if not credential.is_available():
            return False

        credential.used_today += 1

        # Update status if quota exhausted
        if credential.daily_limit > 0 and credential.used_today >= credential.daily_limit:
            credential.status = CredentialStatus.EXHAUSTED

        await self._save_data()
        return True

    async def reset_daily_quota(self) -> None:
        """Reset daily usage counters for all credentials."""
        for credential in self.credentials.values():
            credential.used_today = 0
            # Reset status to ACTIVE if it was EXHAUSTED due to quota
            if credential.status == CredentialStatus.EXHAUSTED:
                credential.status = CredentialStatus.ACTIVE
        await self._save_data()

    async def cleanup_cooldown(self) -> None:
        """Remove expired cooldowns."""
        now = datetime.utcnow()
        for credential in self.credentials.values():
            if credential.cooldown_until and now >= credential.cooldown_until:
                credential.cooldown_until = None
        await self._save_data()

    # =============================================================================
    # Privacy Operations
    # =============================================================================

    async def filter_credentials_by_privacy(
        self,
        requester: str,
        bond_strength: int = 0,
        provider: Optional[str] = None,
    ) -> List[VaultCredential]:
        """
        Filter credentials based on privacy tiers (R19 compliance).

        Args:
            requester: Entity requesting credentials
            bond_strength: Bond strength with requester (for bonded tier)
            provider: Optional provider filter

        Returns:
            List of credentials accessible to requester
        """
        credentials = list(self.credentials.values())

        # Apply privacy filtering
        filtered = []
        for credential in credentials:
            if credential.visibility == VisibilityTier.PUBLIC:
                filtered.append(credential)
            elif credential.visibility == VisibilityTier.BONDED and bond_strength >= 50:
                filtered.append(credential)
            elif (
                credential.visibility == VisibilityTier.PRIVATE and requester == credential.provider
            ):
                filtered.append(credential)

        # Apply provider filter
        if provider:
            filtered = [c for c in filtered if c.provider == provider]

        return filtered

    # =============================================================================
    # BlindVault Integration
    # =============================================================================

    async def get_decrypted_credential(
        self,
        provider: str,
        key_id: str,
        agent_id: str,
    ) -> str:
        """
        Get decrypted credential using BlindVault resolver.

        Args:
            provider: Provider name
            key_id: Key ID
            agent_id: Agent requesting credential

        Returns:
            Decrypted credential payload

        Raises:
            VaultError: If credential cannot be decrypted
        """
        if not self.blindvault_resolver:
            raise VaultError("BlindVault resolver not configured")

        # Check if credential exists
        credential = await self.get_credential(provider, key_id)

        # Check if agent has lease
        lease = next(
            (
                l
                for l in self.leases.values()
                if l.credential_ref == f"{provider}:{key_id}" and l.agent_id == agent_id
            ),
            None,
        )

        if not lease or not lease.is_valid():
            raise VaultError(f"Agent {agent_id} does not have valid lease for {provider}:{key_id}")

        # Use BlindVault resolver to get decrypted credential
        secret_ref = f"{{secret:{provider}_{key_id}}}"
        try:
            decrypted = await self.blindvault_resolver.resolve(secret_ref)

            # Log access with CPE scoring
            await self._log_credential_access(credential, decrypted, agent_id)

            return decrypted
        except Exception as e:
            raise VaultError(f"Failed to decrypt credential: {e}")

    # =============================================================================
    # Bury Integration
    # =============================================================================

    async def bury_credential(
        self,
        provider: str,
        key_id: str,
        agent_id: str,
        bury_backend=None,
    ) -> str:
        """
        Bury credential using Bury backend (PID-bound session).

        Args:
            provider: Provider name
            key_id: Key ID
            agent_id: Agent requesting credential
            bury_backend: Bury backend instance

        Returns:
            Session token for buried credential
        """
        if not bury_backend:
            raise VaultError("Bury backend not configured")

        # Get credential
        credential = await self.get_credential(provider, key_id)

        # Start PID-bound session
        session_token = bury_backend.start_session(agent_id)

        # Bury credential
        bury_backend.bury_credential(session_token, credential)

        # Log access
        await self._log_audit(
            action="credential_buried",
            credential_ref=credential.credential_ref,
            details={
                "agent_id": agent_id,
                "session_token": session_token,
            },
            agent_id=agent_id,
        )

        return session_token

    # =============================================================================
    # Audit Logging
    # =============================================================================

    async def _log_audit(
        self,
        action: str,
        credential_ref: str,
        details: Dict[str, Any],
        success: bool = True,
        error: Optional[str] = None,
        agent_id: str = "system",
    ) -> None:
        """Log audit entry."""
        entry = VaultAuditEntry(
            action=action,
            credential_ref=credential_ref,
            details=details,
            success=success,
            error=error,
            agent_id=agent_id,
        )

        self.audit.append(entry)

        # Apply CPE scoring for sensitive operations
        if action in ["credential_created", "credential_updated", "credential_deleted"]:
            await self._process_credential_pii_cpe(entry)

        await self._save_data()

    async def _log_credential_access(
        self,
        credential: VaultCredential,
        decrypted: str,
        agent_id: str,
    ) -> None:
        """Log credential access with CPE scoring."""
        await self._log_audit(
            action="credential_used",
            credential_ref=credential.credential_ref,
            details={
                "agent_id": agent_id,
                "decrypted_length": len(decrypted),
            },
            success=True,
            agent_id=agent_id,
        )

        # Process CPE for this access
        await self._process_credential_pii_cpe(self.audit[-1])

    async def _process_credential_pii_cpe(self, entry: VaultAuditEntry) -> None:
        """Process CPE for credential-related PII exposure."""
        # Extract PII from credential and operation details
        # This is a simplified implementation
        cpe_action = self.cpe_scorer.process_credential_access(
            VaultCredential(
                provider="openrouter",
                key_id="temp",
                cred_type=CredentialType.API_KEY,
                encrypted_blob="age-encryption.org/v1->X25519->mock",
            ),
            entry.action,
        )

        entry.cpe_score = self.cpe_scorer._compute_cpe()
        entry.cpe_action = cpe_action.value

        # Apply pseudonymization if needed
        if cpe_action == CPEAction.PSEUDONYMIZE:
            entry = self.cpe_scorer.pseudonymize_audit_entry(entry)

        # Update audit entry
        index = len(self.audit) - 1
        self.audit[index] = entry

        await self._save_data()

    # =============================================================================
    # Utility Methods
    # =============================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get vault statistics."""
        now = datetime.utcnow()

        return {
            "total_credentials": len(self.credentials),
            "total_leases": len(self.leases),
            "active_leases": len([l for l in self.leases.values() if l.is_valid()]),
            "expired_leases": len([l for l in self.leases.values() if not l.is_valid()]),
            "credentials_by_tier": {
                tier.value: len([c for c in self.credentials.values() if c.tier == tier])
                for tier in CredentialTier
            },
            "credentials_by_visibility": {
                vis.value: len([c for c in self.credentials.values() if c.visibility == vis])
                for vis in VisibilityTier
            },
            "quota_usage": {
                cred.credential_ref: cred.used_today
                for cred in self.credentials.values()
                if cred.daily_limit > 0
            },
            "cpe_session_summary": self.cpe_scorer.get_session_summary(),
        }


# =============================================================================
# FACTORY
# =============================================================================


def create_vault_core(
    vault_path: Path = Path("data/vault"),
    master_key: Optional[str] = None,
    blindvault_resolver=None,
    bury_backend=None,
) -> VaultCore:
    """Factory: create VaultCore with default or custom dependencies."""
    return VaultCore(
        vault_path=vault_path,
        master_key=master_key,
        blindvault_resolver=blindvault_resolver,
        bury_backend=bury_backend,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "VaultCore",
    "VaultError",
    "CredentialNotFoundError",
    "LeaseError",
    "QuotaExceededError",
    "create_vault_core",
]
