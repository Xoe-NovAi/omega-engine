# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Key management for SQLCipher encryption at rest.

AP: AP-SQLCIPHER-ENCRYPTION-v1.0.0

[heritage: zetetic-2026] SQLCipher 4.x PBKDF2-HMAC-SHA512 + AES-256.
[heritage: owasp-llm08-2025] Vector and Embedding Weaknesses mandate encryption.

M23: never fall through to plaintext. If no key is resolvable, raise
KeyManagerError immediately.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ENV_KEY = "OMEGA_SQLCIPHER_KEY"
KEY_FILE_DEFAULT = Path.home() / ".config" / "omega" / "sqlcipher.key"
KEYRING_SERVICE = "omega-engine-sqlcipher"
KEYRING_USER = "default"


class KeyManagerError(RuntimeError):
    """Raised when no valid encryption key can be obtained. M23 hard-stop."""


class KeyManager:
    """Resolves the SQLCipher encryption key from prioritized sources.

    Priority: OS keyring > env var > key file (mode 0600).
    NEVER hard-coded; never logged.
    """

    def __init__(self,
                 service_name: str = KEYRING_SERVICE,
                 key_file: Optional[Path] = None):
        self._service = service_name
        self._key_file = key_file or KEY_FILE_DEFAULT

    def get_key(self) -> str:
        """Returns the key string. Raises KeyManagerError if none found.

        M23: hard-stop if no key is available; do NOT fall through to plaintext.
        """
        # 1. OS keyring (preferred)
        try:
            import keyring  # type: ignore[import-untyped]
            k = keyring.get_password(self._service, KEYRING_USER)
            if k:
                logger.debug("Key resolved from OS keyring (service=%s)", self._service)
                return k
        except ImportError:
            logger.debug("keyring library not installed; skipping")
        except Exception as e:  # keyring backend errors — don't crash
            logger.warning("keyring backend error: %s", e)

        # 2. Environment variable
        k = os.environ.get(ENV_KEY)
        if k:
            logger.debug("Key resolved from %s env var", ENV_KEY)
            return k

        # 3. Key file (0600 perms enforced)
        if self._key_file.exists():
            mode = self._key_file.stat().st_mode & 0o777
            if mode != 0o600:
                raise KeyManagerError(
                    f"Key file {self._key_file} has mode {oct(mode)}; "
                    f"MUST be 0o600. Fix: chmod 600 {self._key_file}"
                )
            k = self._key_file.read_text().strip()
            if k:
                logger.debug("Key resolved from key file %s", self._key_file)
                return k

        raise KeyManagerError(
            f"No SQLCipher key found. Set {ENV_KEY} env var, store in OS "
            f"keyring (service='{self._service}'), or write to "
            f"{self._key_file} (mode 0600)."
        )

    def set_key(self, key: str) -> None:
        """Persist key to OS keyring (preferred) or key file (fallback).

        Validates that the key meets a minimum length (32 chars) to ensure
        adequate entropy for AES-256.
        """
        if len(key) < 32:
            raise KeyManagerError(
                f"Key length {len(key)} < 32 chars. Use a 32+ char "
                f"passphrase or `python -c 'import secrets; print(secrets.token_urlsafe(32))'`."
            )

        # 1. Try keyring first
        try:
            import keyring  # type: ignore[import-untyped]
            keyring.set_password(self._service, KEYRING_USER, key)
            logger.info("Key stored in OS keyring (service=%s)", self._service)
            return
        except ImportError:
            pass
        except Exception as e:
            logger.warning("keyring set failed: %s; falling back to key file", e)

        # 2. Fall back to key file
        self._key_file.parent.mkdir(parents=True, exist_ok=True)
        self._key_file.write_text(key)
        self._key_file.chmod(0o600)
        logger.info("Key stored in %s (mode 0600)", self._key_file)

    def clear_key(self) -> None:
        """Remove the key from keyring and/or key file. Use with caution."""
        try:
            import keyring  # type: ignore[import-untyped]
            keyring.delete_password(self._service, KEYRING_USER)
        except Exception:
            pass
        if self._key_file.exists():
            self._key_file.unlink()
        logger.warning("Key cleared from all sources (operator action)")
