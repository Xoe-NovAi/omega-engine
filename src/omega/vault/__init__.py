# 🔱 Sovereign Key Vault — Encrypted API Key Management
# AP: AP-KEY-VAULT-v1.0.0
# ⬡ OMEGA ⬡ P3 ⬡ vault ⬡ ENGINEERING ⬡ KEY-VAULT
#
# Sovereign encrypted storage for all API keys used by the Omega Engine.
# Replaces plaintext .env as the single source of truth for credentials.
# AES-256-GCM at rest, signed with Ed25519 for tamper detection.
#
# Usage:
#   from omega.vault import KeyVault
#   vault = KeyVault()
#   exa_key = vault.resolve("exa")
#   all_google_keys = vault.resolve_all("google")

from omega.vault.key_vault import KeyVault, VaultKeyNotFound, VaultLockedError
from omega.vault.crypto import encrypt, decrypt, generate_master_key, master_key_from_hex

__all__ = [
    "KeyVault",
    "VaultKeyNotFound",
    "VaultLockedError",
    "encrypt",
    "decrypt",
    "generate_master_key",
    "master_key_from_hex",
]
