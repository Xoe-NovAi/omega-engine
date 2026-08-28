"""
VaultCore Crypto — age (scrypt-based) Passphrase Encryption
AP: AP-VAULT-CRYPTO-v2.0.0
⬡ OMEGA ⬡ P3 ⬡ vault_crypto ⬡ AGE-PASSPHRASE

Implements R_VAULT_SCHEMA_V2.md encryption architecture:
- age passphrase encryption (scrypt-based) via pyrage.passphrase
- master_key is used directly as the age passphrase; age handles
  scrypt salt derivation internally
- [M23-audit 2026-08-28 corrected]: Argon2id is NOT used for the
  encryption key derivation. The PasswordHasher instance is created
  for future migration to Argon2id-derived keys (see _derive_key
  method below, which is currently unused). The current architecture
  is age-with-scrypt; rotation to age-with-Argon2id is a V-1 task.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Optional dependencies - gracefully handle missing
try:
    import pyrage
    import pyrage.passphrase as pp
    from argon2 import PasswordHasher

    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False
    logger.warning("pyrage or argon2 not installed — crypto operations will fail")


class VaultCryptoError(Exception):
    """Base exception for vault crypto operations."""

    pass


class VaultCrypto:
    """
    Vault encryption using age (pyrage.passphrase).

    Key Derivation:
    Master Password → age passphrase encryption (scrypt internally) → age-armored ciphertext

    [M23-audit 2026-08-28] Argon2id-based derivation (_derive_key) is a
    V-1 migration target. Current code uses master_key directly as the
    age passphrase; age handles scrypt salt derivation internally. This
    is cryptographically sound (age's scrypt is OWASP-recommended for
    passphrase-based encryption) but is not the Argon2id-based KDF
    originally documented in R_VAULT_SCHEMA_V2.md.
    """

    def __init__(self, master_key: str):
        """
        Initialize vault crypto.

        Args:
            master_key: Master password/key for encryption
        """
        if not _HAS_CRYPTO:
            raise VaultCryptoError(
                "Crypto dependencies not installed. Run: pip install pyrage argon2-cffi"
            )

        self._ph = PasswordHasher(
            time_cost=3,
            memory_cost=65536,  # 64 MB
            parallelism=4,
            hash_len=32,
            salt_len=16,
        )
        self._master_key = master_key
        self._derived_key: Optional[bytes] = None
        self._salt: Optional[bytes] = None

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key from master password + salt.

        Uses Argon2id hash which includes salt. We extract raw key material
        from the hash for use as age passphrase.
        """
        # Argon2id hash includes salt; we use the hash as key material
        # Pass salt as bytes directly to hash() - it handles bytes
        hash_str = self._ph.hash(self._master_key.encode() + salt)
        # Use first 32 bytes of hash as key
        return hash_str.encode()[:32]

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext JSON to age-armored ciphertext.

        Returns:
            age-armored ciphertext (includes salt in header via scrypt)
        """
        # Use master key directly as passphrase - age handles scrypt salt internally
        ciphertext = pp.encrypt(plaintext.encode(), self._master_key, armored=True)

        return ciphertext.decode()

    def decrypt(self, armored: str) -> str:
        """
        Decrypt age-armored ciphertext to plaintext JSON.

        Args:
            armored: age-armored ciphertext format

        Returns:
            Decrypted plaintext
        """
        # Use master key directly as passphrase
        plaintext_bytes = pp.decrypt(armored.encode(), self._master_key)

        return plaintext_bytes.decode()

    def rotate_key(self, old_armored: str, new_master_key: str) -> str:
        """
        Re-encrypt ciphertext with new master key.

        Args:
            old_armored: Existing age-armored ciphertext
            new_master_key: New master password

        Returns:
            New age-armored ciphertext
        """
        # Decrypt with current key
        plaintext = self.decrypt(old_armored)

        # Create new crypto instance with new key
        new_crypto = VaultCrypto(new_master_key)

        # Re-encrypt
        return new_crypto.encrypt(plaintext)


class VaultCryptoManager:
    """
    Manages multiple vault crypto instances for different key versions.

    Supports key rotation by maintaining multiple key versions.
    """

    def __init__(self):
        self._ciphers: dict[str, VaultCrypto] = {}
        self._default_version: Optional[str] = None

    def add_key(self, version: str, master_key: str, default: bool = False) -> None:
        """Add a key version."""
        self._ciphers[version] = VaultCrypto(master_key)
        if default or self._default_version is None:
            self._default_version = version

    def get_cipher(self, version: Optional[str] = None) -> VaultCrypto:
        """Get cipher for version (or default)."""
        version = version or self._default_version
        if version not in self._ciphers:
            raise ValueError(f"No cipher for version: {version}")
        return self._ciphers[version]

    def encrypt(self, plaintext: str, version: Optional[str] = None) -> str:
        """Encrypt with specified or default version."""
        cipher = self.get_cipher(version)
        return cipher.encrypt(plaintext)

    def decrypt(self, armored: str) -> str:
        """
        Decrypt trying all key versions.

        Tries each version until one succeeds.
        """
        last_error = None
        for version, cipher in self._ciphers.items():
            try:
                return cipher.decrypt(armored)
            except Exception as e:
                last_error = e
                continue
        raise ValueError(f"Failed to decrypt with any key version: {last_error}")

    def rotate(self, old_version: str, new_version: str, new_master_key: str) -> None:
        """Rotate from old version to new version."""
        if old_version not in self._ciphers:
            raise ValueError(f"Old version not found: {old_version}")

        old_cipher = self._ciphers[old_version]
        new_cipher = VaultCrypto(new_master_key)

        self._ciphers[new_version] = new_cipher
        self._default_version = new_version


# =============================================================================
# FACTORY
# =============================================================================


def create_vault_crypto(master_key: str) -> VaultCrypto:
    """Factory: create VaultCrypto with master key."""
    return VaultCrypto(master_key)


def create_vault_crypto_manager() -> VaultCryptoManager:
    """Factory: create VaultCryptoManager."""
    return VaultCryptoManager()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "VaultCrypto",
    "VaultCryptoManager",
    "VaultCryptoError",
    "create_vault_crypto",
    "create_vault_crypto_manager",
]
