# 🔱 Omega Engine — YouTube Research Module (P0)
# AP: AP-YOUTUBE-RESEARCH-MODULE-v1.0.0
# ⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_youtube_research ⬡ P0-STRUCTURAL
#
# SovereignSigner — Sieve-and-Sign attestation (HMAC-SHA256) + JWT attribution envelope.
#
# Heritage:
#   [heritage: cryptography 2023] HMAC-SHA256 via cryptography.hazmat.primitives.hmac
#   [heritage: pyjwt 2024] JWT HS256 envelope for portable attribution

"""SovereignSigner — tamper-evident provenance attestation (Sieve-and-Sign).

The Signer binds cleaned content to its source so that any later tampering with the
transcript is detectable. It produces a ``SourceChainAttestation`` (the ``sca.json``
document from the spec) and can also encode that attestation as a JWT for portable
attribution across engine boundaries (the sprint directive's "JWT attribution").
"""

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import jwt
from cryptography.hazmat.primitives import hashes, hmac as chmac
from pydantic import BaseModel, Field

from .config import SignerConfig
from .errors import SigningError

ATTESTATION_VERSION = "1.0"


class SourceChainAttestation(BaseModel):
    """Source Chain Attestation (``sca.json``) — the signed provenance record.

    Every extracted/cleaned artifact is bound to its source via this record. The
    ``provenance_hash`` is an HMAC-SHA256 over the cleaned text + sieve metadata,
    keyed by the module signing key, so it cannot be forged without the key.
    """

    version: str = ATTESTATION_VERSION
    source_id: str
    source_type: str
    source_url: str
    cleaned_text_hash: str
    provenance_hash: str
    sieve_metadata: Dict[str, Any] = Field(default_factory=dict)
    signed_at: str
    signer: str
    key_id: str

    def to_jwt_payload(self) -> Dict[str, Any]:
        """Return a JSON-serialisable payload for JWT encoding."""
        return self.model_dump()


class SovereignSigner:
    """HMAC-SHA256 attestation engine with optional JWT envelope.

    Args:
        key: Raw signing key bytes (>= 16 bytes recommended).
        key_id: Stable identifier for the key (embedded in attestations).
        signer: Human-readable signer label (embedded in attestations).
    """

    def __init__(
        self,
        key: bytes,
        key_id: str = "omega-youtube-research-key-2026",
        signer: str = "omega-youtube-research/v1.0",
    ):
        if not isinstance(key, bytes) or len(key) < 16:
            raise SigningError("Signing key must be bytes of length >= 16")
        self._key = key
        self._key_id = key_id
        self._signer = signer

    # ── Key management ───────────────────────────────────────────────────────
    @classmethod
    def load_or_create_key(cls, path: Path) -> bytes:
        """Load a signing key from ``path`` or generate + persist a new one.

        Args:
            path: Filesystem path for the key. Created with ``0o600`` if missing.

        Returns:
            The raw key bytes.
        """
        if path.exists():
            return path.read_bytes()
        key = secrets.token_bytes(32)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Write atomically; restrictive perms so the key is never world-readable.
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(key)
        import os

        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
        os.chmod(path, 0o600)
        return key

    @classmethod
    def from_config(cls, config: SignerConfig) -> "SovereignSigner":
        """Build a signer from ``SignerConfig``, loading/creating its key file."""
        key = cls.load_or_create_key(Path(config.key_path))
        return cls(key=key, key_id=config.key_id, signer=config.signer)

    # ── Signing ──────────────────────────────────────────────────────────────
    def sign(
        self,
        cleaned_text: str,
        sieve_metadata: Dict[str, Any],
        source_id: str,
        source_type: str,
        source_url: str,
    ) -> SourceChainAttestation:
        """Produce a signed ``SourceChainAttestation`` for cleaned content.

        Args:
            cleaned_text: The sieve-cleaned transcript text.
            sieve_metadata: Cleaning statistics (from ``SieveResult.metadata``).
            source_id: Stable source identifier (e.g. ``yt_<video_id>_<ts>``).
            source_type: Type label, typically ``"youtube_transcript"``.
            source_url: Canonical source URL.

        Returns:
            A ``SourceChainAttestation`` carrying the HMAC-SHA256 provenance hash.
        """
        cleaned_hash = "sha256:" + hashlib.sha256(
            cleaned_text.encode("utf-8")
        ).hexdigest()
        meta_json = json.dumps(sieve_metadata, sort_keys=True, ensure_ascii=False)
        mac = chmac.HMAC(self._key, hashes.SHA256())
        mac.update((cleaned_text + meta_json).encode("utf-8"))
        provenance_hash = "hmac_sha256:" + mac.finalize().hex()
        return SourceChainAttestation(
            source_id=source_id,
            source_type=source_type,
            source_url=source_url,
            cleaned_text_hash=cleaned_hash,
            provenance_hash=provenance_hash,
            sieve_metadata=sieve_metadata,
            signed_at=datetime.now(timezone.utc).isoformat(),
            signer=self._signer,
            key_id=self._key_id,
        )

    # ── Verification ─────────────────────────────────────────────────────────
    def verify(self, attestation: SourceChainAttestation, cleaned_text: str) -> bool:
        """Verify an attestation's HMAC against the supplied cleaned text.

        Args:
            attestation: The attestation to verify.
            cleaned_text: The cleaned text it should bind to.

        Returns:
            ``True`` if the HMAC + cleaned-text hash both match; ``False`` otherwise
            (i.e. the transcript was tampered with or the wrong key is in use).
        """
        try:
            expected = self.sign(
                cleaned_text=cleaned_text,
                sieve_metadata=attestation.sieve_metadata,
                source_id=attestation.source_id,
                source_type=attestation.source_type,
                source_url=attestation.source_url,
            )
        except Exception:  # pragma: no cover - defensive
            return False
        return (
            expected.provenance_hash == attestation.provenance_hash
            and expected.cleaned_text_hash == attestation.cleaned_text_hash
        )

    # ── JWT attribution envelope ─────────────────────────────────────────────
    def to_jwt(self, attestation: SourceChainAttestation) -> str:
        """Encode an attestation as a JWT (HS256) for portable attribution.

        Args:
            attestation: The attestation to encode.

        Returns:
            A signed JWT string.
        """
        return jwt.encode(
            attestation.to_jwt_payload(), key=self._key, algorithm="HS256"
        )

    def verify_jwt(self, token: str) -> SourceChainAttestation:
        """Decode + verify a JWT back into a ``SourceChainAttestation``.

        Args:
            token: The JWT string produced by :meth:`to_jwt`.

        Returns:
            The decoded ``SourceChainAttestation``.

        Raises:
            SigningError: If the JWT is invalid or its signature does not verify.
        """
        try:
            payload = jwt.decode(token, key=self._key, algorithms=["HS256"])
        except jwt.PyJWTError as exc:
            raise SigningError(f"JWT attestation failed verification: {exc}") from exc
        return SourceChainAttestation(**payload)
