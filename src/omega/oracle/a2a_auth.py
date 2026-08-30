# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-A2A-AUTH-v1.0.0
"""
A2A Authentication — SPIFFE/WIMSE Agent Identity.

[IETF draft-klrc-aiagent-auth-02]
Implements the Agent Identity Management System (AIMS) framework:
- Identifier: SPIFFE/WIMSE ID per agent
- Credentials: Short-lived X.509-SVID (~1h TTL)
- Authentication: mTLS with bound credentials
- Authorization: OAuth 2.0 Transaction Tokens

This module handles the identity primitives using Python's
standard library. Full X.509 certificate management is deferred
to the SPIFFE SDK integration (Phase 2).
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class SPIFFEID:
    """SPIFFE ID representing an agent's identity.

    Format: spiffe://<trust_domain>/<path>
    Example: spiffe://omega.local/entity/kali

    [draft-klrc-aiagent-auth-02 §4.1]
    """

    trust_domain: str
    path: str

    def __str__(self) -> str:
        return f"spiffe://{self.trust_domain}/{self.path}"

    @classmethod
    def parse(cls, spiffe_id: str) -> "SPIFFEID":
        """Parse a SPIFFE ID string into its components.

        Args:
            spiffe_id: The SPIFFE ID to parse (e.g., spiffe://omega.local/entity/kali)

        Returns:
            SPIFFEID instance with trust_domain and path extracted.
        """
        parts = spiffe_id.replace("spiffe://", "").split("/", 1)
        return cls(
            trust_domain=parts[0],
            path=parts[1] if len(parts) > 1 else "",
        )


@dataclass
class AgentCredential:
    """Short-lived credential for agent authentication.

    [draft-klrc-aiagent-auth-02 §5]
    Credentials must be bound to the agent's identity,
    short-lived (~1h), and dynamically rotated.
    """

    spiffe_id: SPIFFEID
    issued_at: datetime
    expires_at: datetime
    token: str  # JWT or X.509-SVID thumbprint

    @property
    def is_expired(self) -> bool:
        """Check if this credential has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def ttl_seconds(self) -> int:
        """Seconds remaining until this credential expires."""
        remaining = (self.expires_at - datetime.now(timezone.utc)).total_seconds()
        return max(0, int(remaining))

    def is_valid_for(self, expected_spiffe_id: SPIFFEID) -> bool:
        """Check if this credential is valid for a given SPIFFE ID.

        Args:
            expected_spiffe_id: The SPIFFE ID to validate against.

        Returns:
            True if the credential matches and is not expired.
        """
        if self.is_expired:
            logger.warning("Credential expired for %s", self.spiffe_id)
            return False
        if str(self.spiffe_id) != str(expected_spiffe_id):
            logger.warning("SPIFFE ID mismatch: %s != %s", self.spiffe_id, expected_spiffe_id)
            return False
        return True
