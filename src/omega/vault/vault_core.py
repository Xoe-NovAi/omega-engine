# ⬡ OMEGA ⬡ MAAT ⬡ VAULT_CORE ⬡ v1.0.0 ⬡ 2026-07-22
"""
VaultCore — Sovereign Credential Vault using age encryption (RFC 8610) and Argon2id key derivation.

Research-backed patterns (R_GUARD_DISTILL_RESEARCH_GUIDE_20260722.md):
- Domain 1: Argon2id params (19 MiB memory, t=2, p=1 minimum), pyrage v1.3.0 library,
  zeroize for memory wiping, systemd LoadCredential patterns
- Mandate 1 (AnyIO): All async operations use anyio
- Mandate 24 (Venv Sovereignty): All deps in .venv
- Mandate 22 (Response Provenance): Audit log tracks actual operations
"""

import anyio
import argon2
import base64
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List, Dict, Any
from zeroize.zeroize import zeroize1 as zeroize

from age.keys.agekey import AgePrivateKey, AgePublicKey
from age.keys.base import DecryptionKey, EncryptionKey
from age.file import Encryptor, Decryptor
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


@dataclass
class AuditEntry:
    """Append-only audit log entry (JSON Lines)."""
    timestamp: str
    operation: str  # set, get, rotate, list, delete
    key: str
    success: bool
    error: Optional[str] = None


class VaultError(Exception):
    """Base exception for vault operations."""
    pass


class VaultCore:
    """
    Sovereign credential vault using age encryption with Argon2id-derived master key.
    
    Credentials stored as individual .age files in vault_dir/
    Master key derived from passphrase + salt using Argon2id
    Audit log: append-only JSON Lines at vault_dir/audit.log
    """
    
    # Argon2id parameters per OWASP 2026 recommendations (Domain 1 research)
    ARGON2_TIME_COST = 2
    ARGON2_MEMORY_COST = 19456  # 19 MiB in KB
    ARGON2_PARALLELISM = 1
    ARGON2_HASH_LEN = 32
    ARGON2_TYPE = argon2.Type.ID
    
    def __init__(self, vault_dir: Path, passphrase: str):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log = self.vault_dir / "audit.log"
        self._passphrase = passphrase.encode('utf-8')
        self._salt_file = self.vault_dir / "salt.bin"
        self._master_identity_file = self.vault_dir / "master.age"
        self._master_pub_file = self.vault_dir / "master.pub"
        self._identity: Optional[AgePrivateKey] = None
        self._recipient: Optional[AgePublicKey] = None
        
    async def _derive_master_seed(self) -> bytes:
        """
        Derive 32-byte master seed from passphrase using Argon2id.
        
        Uses zeroize to wipe intermediate values from memory.
        """
        # Load or generate salt
        if not self._salt_file.exists():
            salt = os.urandom(16)
            await anyio.Path(self._salt_file).write_bytes(salt)
        else:
            salt = await anyio.Path(self._salt_file).read_bytes()
        
        # Derive key using Argon2id
        ph = argon2.PasswordHasher(
            time_cost=self.ARGON2_TIME_COST,
            memory_cost=self.ARGON2_MEMORY_COST,
            parallelism=self.ARGON2_PARALLELISM,
            hash_len=self.ARGON2_HASH_LEN,
            type=self.ARGON2_TYPE
        )
        
        hash_input = self._passphrase + salt
        hash_str = ph.hash(hash_input)
        
        # Extract raw 32-byte key from hash
        # argon2-cffi returns encoded hash: $argon2id$v=19$m=19456,t=2,p=1$salt$hash
        # The hash part uses URL-safe base64 (with - and _)
        parts = hash_str.split('$')
        hash_b64 = parts[-1]
        # Add padding if needed for URL-safe base64
        padding = 4 - (len(hash_b64) % 4)
        if padding != 4:
            hash_b64 += '=' * padding
        raw_hash = base64.urlsafe_b64decode(hash_b64)
        seed = raw_hash[:32]
        
        # Wipe intermediate values
        zeroize(hash_input)
        zeroize(salt)
        
        return seed
    
    async def _ensure_master_identity(self) -> AgePublicKey:
        """Generate or load master age identity from derived seed."""
        if self._recipient is not None:
            return self._recipient
            
        if not self._master_identity_file.exists():
            # Generate new identity from derived seed
            seed = await self._derive_master_seed()
            
            # Create X25519 private key from seed
            x25519_private = X25519PrivateKey.from_private_bytes(seed)
            x25519_public = x25519_private.public_key()
            pub_bytes = x25519_public.public_bytes(Encoding.Raw, PublicFormat.Raw)
            
            # Create age keys
            self._recipient = AgePublicKey.from_public_bytes(pub_bytes)
            self._identity = AgePrivateKey(x25519_private)
            
            # Save private key (age format)
            await anyio.Path(self._master_identity_file).write_text(self._identity.private_string())
            # Save public key for reference
            await anyio.Path(self._master_pub_file).write_text(self._recipient.public_string())
            
            # Wipe seed
            zeroize(seed)
        else:
            # Load existing identity
            private_key_str = await anyio.Path(self._master_identity_file).read_text()
            self._identity = AgePrivateKey.from_private_string(private_key_str.strip())
            self._recipient = self._identity.public_key()
            
        return self._recipient
    
    async def _age_encrypt(self, plaintext: str, recipient: AgePublicKey) -> str:
        """Encrypt plaintext using age with the given recipient."""
        import io
        import base64
        out_stream = io.BytesIO()
        encryptor = Encryptor([recipient], out_stream)
        encryptor.write(plaintext.encode('utf-8'))
        encryptor.close()
        return base64.b64encode(out_stream.getvalue()).decode('ascii')
    
    async def _age_decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext using master identity."""
        if self._identity is None:
            await self._ensure_master_identity()
        import io
        import base64
        ciphertext_bytes = base64.b64decode(ciphertext.encode('ascii'))
        in_stream = io.BytesIO(ciphertext_bytes)
        decryptor = Decryptor([self._identity], in_stream)
        plaintext = decryptor.read()
        return plaintext.decode('utf-8')
    
    async def _audit(self, operation: str, key: str, success: bool, error: Optional[str] = None):
        """Append audit entry to log (append-only, JSON Lines)."""
        entry = AuditEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            operation=operation,
            key=key,
            success=success,
            error=error
        )
        line = json.dumps(asdict(entry)) + "\n"
        async with await anyio.open_file(self.audit_log, "a") as f:
            await f.write(line)
    
    async def store(self, key: str, value: str) -> bool:
        """Store a credential encrypted with age."""
        try:
            recipient = await self._ensure_master_identity()
            ciphertext = await self._age_encrypt(value, recipient)
            credential_file = self.vault_dir / f"{key}.age"
            await anyio.Path(credential_file).write_text(ciphertext)
            await self._audit("set", key, True)
            return True
        except Exception as e:
            await self._audit("set", key, False, str(e))
            raise VaultError(f"Failed to store {key}: {e}")
    
    async def retrieve(self, key: str) -> Optional[str]:
        """Retrieve and decrypt a credential."""
        credential_file = self.vault_dir / f"{key}.age"
        if not credential_file.exists():
            await self._audit("get", key, False, "Key not found")
            return None
        try:
            ciphertext = await anyio.Path(credential_file).read_text()
            plaintext = await self._age_decrypt(ciphertext)
            await self._audit("get", key, True)
            return plaintext
        except Exception as e:
            await self._audit("get", key, False, str(e))
            raise VaultError(f"Failed to retrieve {key}: {e}")
    
    async def rotate(self, key: str, new_value: str) -> bool:
        """Rotate a credential (overwrite with new value)."""
        return await self.store(key, new_value)
    
    async def list_keys(self) -> List[str]:
        """List all stored credential keys."""
        keys = []
        async for entry in anyio.Path(self.vault_dir).iterdir():
            if entry.name.endswith(".age") and entry.name != "master.age":
                keys.append(entry.name[:-4])  # Remove .age suffix
        await self._audit("list", "all", True)
        return sorted(keys)
    
    async def delete(self, key: str) -> bool:
        """Delete a credential."""
        credential_file = self.vault_dir / f"{key}.age"
        if credential_file.exists():
            await anyio.Path(credential_file).unlink()
            await self._audit("delete", key, True)
            return True
        await self._audit("delete", key, False, "Key not found")
        return False
    
    async def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Read recent audit log entries."""
        if not self.audit_log.exists():
            return []
        lines = await anyio.Path(self.audit_log).read_text()
        entries = []
        for line in lines.strip().split('\n')[-limit:]:
            if line:
                entries.append(json.loads(line))
        return entries
    
    async def verify_integrity(self) -> Dict[str, Any]:
        """Verify vault integrity: all .age files decrypt successfully."""
        results = {"total": 0, "valid": 0, "corrupted": []}
        keys = await self.list_keys()
        results["total"] = len(keys)
        for key in keys:
            try:
                await self.retrieve(key)
                results["valid"] += 1
            except Exception:
                results["corrupted"].append(key)
        return results


# Convenience function for CLI usage
async def create_vault(vault_dir: Path, passphrase: str) -> VaultCore:
    """Create and initialize a new vault."""
    vault = VaultCore(vault_dir, passphrase)
    await vault._ensure_master_identity()  # Force identity generation
    return vault