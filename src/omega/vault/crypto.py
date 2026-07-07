# 🔱 Sovereign Key Vault — AES-256-GCM Encryption Layer
# AP: AP-KEY-VAULT-CRYPTO-v1.0.0
# ⬡ OMEGA ⬡ P3 ⬡ vault ⬡ crypto ⬡ KEY-VAULT
#
# Authenticated encryption for the vault file at rest.
# Uses AES-256-GCM via Python's cryptography library.
#
# [id-soft: quake-1996] Zone Memory — encrypted vault mirrors the tagged
# allocation approach: every block carries its own authentication tag.


# DocRef: docs/architecture/Sovereign_Sieve_Sovereign_Sieve.md
import os
import base64

from omega.errors import OmegaError


class VaultCryptoError(OmegaError):
    """Raised on encryption/decryption failures."""
    pass


def generate_master_key() -> bytes:
    """Generate a new 256-bit master key.
    
    Returns:
        32 random bytes suitable for AES-256-GCM.
    """
    return os.urandom(32)


def master_key_from_hex(hex_str: str) -> bytes:
    """Convert a hex-encoded master key to bytes.
    
    Args:
        hex_str: 64-character hex string (32 bytes encoded).
        
    Returns:
        32 bytes suitable for AES-256-GCM.
        
    Raises:
        VaultCryptoError: If the hex string is not exactly 64 characters.
    """
    try:
        key = bytes.fromhex(hex_str)
        if len(key) != 32:
            raise VaultCryptoError(
                f"Master key must be 32 bytes (64 hex chars), got {len(key)} bytes"
            )
        return key
    except ValueError as e:
        raise VaultCryptoError(f"Invalid master key hex: {e}")


def encrypt(plaintext: str, master_key: bytes) -> str:
    """Encrypt a string with AES-256-GCM.
    
    Uses a random 12-byte nonce per encryption. Returns a base64-encoded
    string containing nonce + ciphertext + GCM tag.
    
    Args:
        plaintext: The string to encrypt.
        master_key: 32-byte AES-256 key.
        
    Returns:
        Base64-encoded string: base64(nonce + ciphertext + tag).
        
    Raises:
        VaultCryptoError: If encryption fails.
    """
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        plain_bytes = plaintext.encode("utf-8")
        nonce = os.urandom(12)
        aesgcm = AESGCM(master_key)
        ciphertext = aesgcm.encrypt(nonce, plain_bytes, None)
        del plain_bytes  # Memory hygiene: clear plaintext bytes (P5 F-3)
        # ciphertext already contains the GCM tag (appended by AESGCM)
        payload = nonce + ciphertext
        return base64.b64encode(payload).decode("ascii")
    except ImportError:
        raise VaultCryptoError(
            "cryptography package not installed. "
            "Install with: pip install cryptography"
        )
    except (RuntimeError, OSError) as e:
        raise VaultCryptoError(f"Encryption failed: {e}")


def decrypt(ciphertext_b64: str, master_key: bytes) -> str:
    """Decrypt a base64-encoded AES-256-GCM ciphertext.
    
    Args:
        ciphertext_b64: Base64 string from encrypt().
        master_key: 32-byte AES-256 key (must match encryption key).
        
    Returns:
        Original plaintext string.
        
    Raises:
        VaultCryptoError: If decryption fails (wrong key, tampered data, etc.).
    """
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        payload = base64.b64decode(ciphertext_b64)
        if len(payload) < 12:
            raise VaultCryptoError("Ciphertext too short — missing nonce or data")
        
        nonce = payload[:12]
        ciphertext = payload[12:]
        del payload  # Memory hygiene: clear raw payload (P5 F-3)

        aesgcm = AESGCM(master_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        result = plaintext.decode("utf-8")
        del plaintext  # Memory hygiene: clear decrypted bytes (P5 F-3)
        return result
    except ImportError:
        raise VaultCryptoError(
            "cryptography package not installed. "
            "Install with: pip install cryptography"
        )
    except (RuntimeError, OSError) as e:
        raise VaultCryptoError(f"Decryption failed: {e}")
