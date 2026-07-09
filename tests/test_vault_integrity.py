import pytest
import anyio
import os
import base64
from pathlib import Path
from src.omega.vault.key_vault import KeyVault
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
async def test_key_vault_persistence():
    """Verify that KeyVault can save and load secrets from disk."""
    vault_path = Path("tests/tmp/vault.json.enc")
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    
    # We need to mock the master key to avoid keyring issues in tests
    master_key = generate_master_key()
    
    # Use a custom KeyVault that takes the master key directly for testing
    class TestKeyVault(KeyVault):
        def __init__(self, path, master_key):
            self._vault_path = Path(path)
            self._master_key = master_key
            # Bypass the super().__init__ call that triggers self._load()
            # because we want to set up the file first.
            self._loaded = False
            self._initialized = True


    vault = TestKeyVault(vault_path, master_key)
    
    # Manually create an encrypted vault file (must match KeyVault schema:
    # {"vault_version": int, "created_at": str, "keys": {provider: key}})
    import json
    from datetime import datetime, timezone
    secrets = {
        "vault_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "keys": {"google": "key-123", "firecrawl": "key-456"},
    }
    encrypted_data = encrypt(json.dumps(secrets), master_key)
    vault_path.write_text(encrypted_data)
    
    vault._load()
    
    assert vault.resolve("google") == "key-123"
    assert vault.resolve("firecrawl") == "key-456"
