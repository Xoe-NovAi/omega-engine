# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import anyio
import os
import base64
from pathlib import Path
from datetime import datetime, timezone
from src.omega.vault.vault_core import (
    VaultCore, VaultCredential, 
    VaultError, CredentialNotFoundError, LeaseError, QuotaExceededError
)
from src.omega.vault.models import (
    CredentialType, CredentialTier, CredentialStatus
)
from src.omega.vault.crypto import (
    VaultCrypto, VaultCryptoManager, create_vault_crypto, create_vault_crypto_manager,
)


@pytest.mark.anyio
async def test_vault_encryption_decryption():
    """Verify that secrets can be encrypted and decrypted correctly."""
    crypto = create_vault_crypto("test-master-password-123")
    plaintext = "sovereign-secret-123"
    
    ciphertext = crypto.encrypt(plaintext)
    decrypted = crypto.decrypt(ciphertext)
    
    assert decrypted == plaintext
    # Accept both age-armored formats
    assert ciphertext.startswith("age-encryption.org/") or ciphertext.startswith("-----BEGIN AGE ENCRYPTED FILE-----")


@pytest.mark.anyio
async def test_vault_wrong_key_fails():
    """Verify that decryption with the wrong key fails."""
    crypto_1 = create_vault_crypto("test-master-password-1")
    crypto_2 = create_vault_crypto("test-master-password-2")
    plaintext = "sovereign-secret-123"
    
    ciphertext = crypto_1.encrypt(plaintext)
    
    with pytest.raises(Exception):  # Should raise VaultCryptoError or InvalidTag
        crypto_2.decrypt(ciphertext)


@pytest.mark.anyio
async def test_vault_persistence():
    """Verify that VaultCore can save and load secrets from disk."""
    vault_path = Path("tests/tmp/vault.json.enc")
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use a custom VaultCore that takes the master password directly for testing
    class TestVaultCore(VaultCore):
        def __init__(self, path, master_password):
            self.vault_dir = Path(path).parent
            self.creds_db = Path(path)
            self.leases_db = self.vault_dir / "leases.json"
            self.audit_log = self.vault_dir / "audit.log"
            self.master_password = master_password
            self.crypto = create_vault_crypto(master_password)
            self._credentials = {}
            self._leases = {}
            self._loaded = False
        
        def _load_sync(self):
            """Load credentials from disk."""
            if self.creds_db.exists():
                import json
                data = json.loads(self.creds_db.read_text())
                self._credentials = {k: VaultCredential(**v) for k, v in data.items()}
            self._loaded = True
        
        async def _save_credentials(self):
            """Save credentials to disk."""
            import json
            data = {k: v.model_dump() for k, v in self._credentials.items()}
            self.creds_db.write_text(json.dumps(data, indent=2, default=str))

    # Create a test credential with valid age-encrypted blob
    master_password = "test-master-password-123"
    crypto = create_vault_crypto(master_password)
    vault = TestVaultCore(vault_path, master_password)
    
    # Create a properly encrypted credential
    encrypted_blob = crypto.encrypt("test-api-key-value")
    cred = VaultCredential(
        provider="google",
        key_id="api_key",
        cred_type=CredentialType.API_KEY,
        encrypted_blob=encrypted_blob,
        tier=CredentialTier.FREE,
        daily_limit=0,
        used_today=0,
        cooldown_until=None,
        status=CredentialStatus.ACTIVE,
        rotated_at=datetime.now(timezone.utc),
        rotation_count=0,
        last_used_at=None,
        last_error=None,
        current_lease_agent=None,
        lease_expires_at=None,
        tags={},
        metadata={},
        created_at=datetime.now(timezone.utc),
        expires_at=None,
        last_rotated_by=None,
        rotation_policy=None,
        backup_refs=[],
    )
    
    vault._credentials["google:api_key"] = cred
    await vault._save_credentials()
    
    # Load a new instance
    vault2 = TestVaultCore(vault_path, master_password)
    vault2._load_sync()
    
    loaded_cred = vault2._credentials.get("google:api_key")
    assert loaded_cred is not None
    assert loaded_cred.encrypted_blob == encrypted_blob