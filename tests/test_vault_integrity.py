import pytest
import anyio
import os
import base64
from pathlib import Path
from datetime import datetime, timezone
from src.omega.vault.vault_core import (
    VaultCore, VaultCredential, ProviderName, CredentialType, 
    CredentialTier, CredentialStatus, AgeEncryption
)
from src.omega.vault.crypto import encrypt, decrypt, generate_master_key

@pytest.mark.anyio
async def test_vault_encryption_decryption():
    """Verify that secrets can be encrypted and decrypted correctly."""
    master_key = generate_master_key()
    plaintext = "sovereign-secret-123"
    
    ciphertext = encrypt(plaintext, master_key)
    decrypted = decrypt(ciphertext, master_key)
    
    assert decrypted == plaintext

@pytest.mark.anyio
async def test_vault_wrong_key_fails():
    """Verify that decryption with the wrong key fails."""
    master_key_1 = generate_master_key()
    master_key_2 = generate_master_key()
    plaintext = "sovereign-secret-123"
    
    ciphertext = encrypt(plaintext, master_key_1)
    
    with pytest.raises(Exception): # Should raise VaultCryptoError or InvalidTag
        decrypt(ciphertext, master_key_2)

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
            self.age = AgeEncryption(self.master_password)
            self._credentials = {}
            self._leases = {}
            self._loaded = False
    
    # Create a test credential
    master_password = "test-master-password-123"
    vault = TestVaultCore(vault_path, master_password)
    
    # Manually create a credential
    cred = VaultCredential(
        provider=ProviderName.GOOGLE,
        key_id="api_key",
        cred_type=CredentialType.API_KEY,
        encrypted_blob="test-key-123",  # In real use, this would be age-encrypted
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
    assert loaded_cred.encrypted_blob == "test-key-123"