# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Omega Vault Import Tool — Migrates plaintext secrets to encrypted storage.
AP: AP-VAULT-IMPORT-v1.0.0
Sovereign Mandate M7: Local-First, Zero Telemetry.
"""

import os
import json
import logging
import sys
from pathlib import Path
from typing import Dict

import keyring
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from omega.vault.crypto import encrypt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("vault_import")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VAULT_FILE = PROJECT_ROOT / "data" / "vault" / "keys.json.enc"
ENV_FILE = PROJECT_ROOT / ".env"
MASTER_KEY_FILE = Path.home() / ".config" / "omega" / "vault_master.key"

def get_or_create_master_key() -> bytes:
    """Retrieve master key from OS keyring or generate a new one."""
    service_id = "omega-engine"
    account_id = "vault-master"
    
    # 1. Try OS Keyring
    try:
        key_b64 = keyring.get_password(service_id, account_id)
        if key_b64:
            logger.info("Master key retrieved from OS keyring")
            return base64.b64decode(key_b64)
    except Exception as e:
        logger.warning(f"Keyring access failed: {e}")

    # 2. Try fallback file
    if MASTER_KEY_FILE.exists():
        try:
            key_b64 = MASTER_KEY_FILE.read_text().strip()
            logger.info("Master key retrieved from fallback file")
            return base64.b64decode(key_b64)
        except Exception as e:
            logger.error(f"Fallback key file corrupted: {e}")

    # 3. Generate new key
    logger.info("Generating new sovereign master key...")
    import os
    new_key = os.urandom(32)
    key_b64 = base64.b64encode(new_key).decode('utf-8')
    
    # Store in keyring
    try:
        keyring.set_password(service_id, account_id, key_b64)
    except Exception as e:
        logger.warning(f"Failed to store key in keyring: {e}")
    
    # Store in fallback file
    MASTER_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MASTER_KEY_FILE.write_text(key_b64)
    MASTER_KEY_FILE.chmod(0o600)
    
    return new_key

def parse_env_file(path: Path) -> Dict[str, str]:
    """Parse .env file into a dictionary."""
    secrets = {}
    if not path.exists():
        logger.warning(f"Env file not found: {path}")
        return secrets
    
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                secrets[k.strip()] = v.strip()
    return secrets

def encrypt_vault(secrets: Dict[str, str], master_key: bytes):
    """Encrypt secrets using AES-256-GCM via the Omega Crypto layer.
    
    Ensures the vault is stored as a base64-encoded string for compatibility
    with KeyVault._load().
    """
    data = json.dumps(secrets)
    encrypted_b64 = encrypt(data, master_key)
    
    VAULT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(VAULT_FILE, "w") as f:
        f.write(encrypted_b64)
    
    logger.info(f"Vault successfully encrypted to {VAULT_FILE}")

def main():
    logger.info("Starting Omega Vault Import...")
    
    # 1. Get master key
    from omega.vault.crypto import get_or_create_master_key
    master_key = get_or_create_master_key()
    
    # 2. Collect secrets
    secrets = parse_env_file(ENV_FILE)
    if not secrets:
        logger.error("No secrets found to import. Exiting.")
        sys.exit(1)
    
    logger.info(f"Collected {len(secrets)} secrets from .env")
    
    # 3. Encrypt and save
    encrypt_vault(secrets, master_key)
    
    logger.info("Vault import complete. You can now safely purge plaintext secrets from .env.")

if __name__ == "__main__":
    main()
