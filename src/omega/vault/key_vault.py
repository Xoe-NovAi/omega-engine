# 🔱 Sovereign Key Vault — Core Singleton
# AP: AP-KEY-VAULT-CORE-v1.0.0
# ⬡ OMEGA ⬡ P3 ⬡ vault ⬡ key_vault ⬡ KEY-VAULT
#
# Sovereign encrypted storage for all API keys used by the Omega Engine.
#
# [id-soft: quake-1996] Zone Memory — memory tagging pattern applied to key
# management: every vault access carries provenance metadata (which account,
# when resolved) for audit trails.
#
# Architecture:
#   - Singleton: one vault instance per process
#   - AES-256-GCM at rest (data/vault/keys.json.enc)
#   - Multi-account rotation per provider
#   - Automatic failover on rate limit detection
#   - Graceful fallback to os.getenv() during transition period


# DocRef: docs/architecture/Sovereign_Sieve_Sovereign_Sieve.md
import json
import logging
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

from omega.errors import OmegaError, ProviderRateLimitError
from omega.vault.crypto import encrypt, decrypt, VaultCryptoError

logger = logging.getLogger(__name__)


class VaultKeyNotFound(OmegaError):
    """Raised when a provider's key is not found in the vault."""
    pass


class VaultLockedError(OmegaError):
    """Raised when the vault cannot be decrypted (wrong key or corruption)."""
    pass


# NOTE: VaultRotationNotSupported was removed in IW-2 (2026-06-30).
# Round-robin key rotation is banned. Rate limits are handled by the
# circuit breaker fabric via ProviderRateLimitError.


class KeyVault:
    """Sovereign Key Vault — encrypted API key management.
    
    This is the single source of truth for all API keys used by the Omega
    Engine. It replaces the previous pattern of scattered os.getenv() calls.
    
    **Round-robin rotation was ERADICATED per IW-2 (2026-06-30).**
    Multi-account rotation violates M4 (Sequentiality) and M8 (Zero Telemetry)
    because Google and other providers ban rapid account switching.
    Rate limits are now handled by the circuit breaker fabric via
    ``ProviderRateLimitError`` — the vault is a simple O(1) key store.
    
    Usage:
        vault = KeyVault()
        exa_key = vault.resolve("exa")
        all_google = vault.resolve_all("google")
    
    The vault file is encrypted at rest with AES-256-GCM. The master key
    is read from the VAULT_MASTER_KEY environment variable (or auto-generated
    on first run).
    """
    
    _instance: Optional["KeyVault"] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        vault_path: Optional[Path] = None,
        master_key: Optional[bytes] = None,
        auto_init: bool = True,
    ):
        """Initialize the KeyVault singleton.
        
        Args:
            vault_path: Path to the encrypted vault file. Defaults to
                data/vault/keys.json.enc.
            master_key: 32-byte AES-256-GCM master key. If None, reads from
                VAULT_MASTER_KEY env var.
            auto_init: If True and no vault file exists, auto-initialize from
                existing .env file (transition assistance).
        """
        if hasattr(self, "_initialized") and self._initialized:
            return
        
        self._vault_path = vault_path or Path(
            os.environ.get(
                "OMEGA_VAULT_PATH",
                str(Path(__file__).resolve().parent.parent.parent.parent / "data" / "vault" / "keys.json.enc")
            )
        )
        self._data: Dict = {
            "vault_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "keys": {},
        }
        self._loaded = False
        
        # Resolve master key
        self._master_key = master_key
        if self._master_key is None:
            env_key = os.environ.get("VAULT_MASTER_KEY", "")
            if env_key:
                try:
                    from omega.vault.crypto import master_key_from_hex
                    self._master_key = master_key_from_hex(env_key)
                except VaultCryptoError as e:
                    logger.warning(f"Invalid VAULT_MASTER_KEY: {e}")
            else:
                from omega.vault.crypto import get_or_create_master_key
                self._master_key = get_or_create_master_key()

        
        # Try to load existing vault
        if self._vault_path.exists():
            self._load()
        elif auto_init:
            self._auto_init_from_env()
        
        # [M21 Gate Integrity] Only mark initialized AFTER all init code succeeds
        self._initialized = True
    
    # ── Public API ─────────────────────────────────────────────────────
    
    def resolve(self, provider: str) -> str:
        """Get the active API key for a provider.
        
        Supports rotation: returns the key for the active account.
        Falls back to os.getenv(provider_env_var) if vault not loaded.
        
        Args:
            provider: Provider name (e.g., "exa", "firecrawl", "google").
            
        Returns:
            The API key string.
            
        Raises:
            VaultKeyNotFound: If no key found for the provider.
        """
        # Fallback to env vars during transition
        if not self._loaded:
            env_key = self._fallback_to_env(provider)
            if env_key:
                return env_key
            # Try to load again (in case vault was populated by another instance)
            if self._vault_path.exists():
                self._load()
            if not self._loaded:
                raise VaultKeyNotFound(
                    f"No key for provider '{provider}' — vault not initialized. "
                    f"Run `omega vault init` or ensure VAULT_MASTER_KEY is set."
                )
        
        entry = self._data.get("keys", {}).get(provider)
        if not entry:
            # Fallback to env var before raising
            env_key = self._fallback_to_env(provider)
            if env_key:
                return env_key
            raise VaultKeyNotFound(
                f"No key for provider '{provider}' in vault"
            )
        
        if isinstance(entry, str):
            return entry  # Simple key (no rotation)
        
        # Multi-account key
        active = entry.get("active_account", "primary")
        accounts = entry.get("accounts", {})
        if active not in accounts:
            # Fallback to first account
            active = list(accounts.keys())[0] if accounts else "primary"
            if active not in accounts:
                raise VaultKeyNotFound(
                    f"No accounts configured for provider '{provider}'"
                )
        
        result = accounts[active]
        return result
    
    def resolve_all(self, provider: str) -> List[str]:
        """Get all API keys for a provider (for key pool rotation).
        
        Args:
            provider: Provider name (e.g., "google").
            
        Returns:
            List of all API key strings.
            
        Raises:
            VaultKeyNotFound: If no keys found for the provider.
        """
        if not self._loaded:
            if self._vault_path.exists():
                self._load()
        
        if not self._loaded:
            # Fallback: try env-based multi-key pattern
            return self._fallback_to_env_multi(provider)
        
        entry = self._data.get("keys", {}).get(provider)
        if not entry:
            return self._fallback_to_env_multi(provider)
        
        if isinstance(entry, str):
            return [entry]
        
        if "keys" in entry:
            # Array-based keys (e.g., google)
            return entry["keys"]
        
        if "accounts" in entry:
            # Dict-based accounts
            return list(entry["accounts"].values())
        
        return [str(entry)]
    
    def handle_rate_limit(self, provider: str) -> str:
        """Sovereign rate-limit handler — raises ProviderRateLimitError.

        Rate limits are handled by the circuit breaker fabric, NOT by
        rotating API keys. This method exists as an explicit replacement
        for the removed ``mark_rate_limited()`` + ``rotate()`` pattern.

        Args:
            provider: Provider name that returned a 429.

        Raises:
            ProviderRateLimitError: Always — the caller is responsible
                for retry/backoff via circuit breaker integration.

        Returns:
            This method does not return — it always raises.
        """
        logger.info(f"Rate limit detected for '{provider}' — delegating to circuit breaker")
        raise ProviderRateLimitError(
            provider,
            f"Provider '{provider}' is rate-limited. "
            f"The circuit breaker fabric will handle retry/backoff. "
            f"Key rotation is intentionally disabled (IW-2).",
        )
    
    # ── Vault Management ──────────────────────────────────────────────
    
    def set_key(self, provider: str, key: str, account: Optional[str] = None):
        """Set a key in the vault (in-memory, call save() to persist).
        
        Args:
            provider: Provider name.
            key: The API key value.
            account: Optional account name. If provider already has accounts,
                this adds to them. If not, sets as simple key.
        """
        if provider not in self._data["keys"]:
            if account:
                self._data["keys"][provider] = {
                    "primary": "",
                    "accounts": {account: key},
                    "active_account": account,
                }
            else:
                self._data["keys"][provider] = key
        else:
            entry = self._data["keys"][provider]
            if isinstance(entry, str):
                if account:
                    # Convert simple key to multi-account dict
                    self._data["keys"][provider] = {
                        "primary": entry,
                        "accounts": {account: key},
                        "active_account": account,
                    }
                else:
                    self._data["keys"][provider] = key
            elif isinstance(entry, dict):
                if account:
                    if "accounts" not in entry:
                        entry["accounts"] = {"primary": entry.get("primary", "")}
                    entry["accounts"][account] = key
                    if "active_account" not in entry:
                        entry["active_account"] = account
                else:
                    if "accounts" not in entry:
                        entry["accounts"] = {}
                    entry["accounts"]["primary"] = key
                    entry["active_account"] = "primary"
    
    def save(self):
        """Persist the vault to disk (encrypted)."""
        self._save()
    
    # ── Internal ──────────────────────────────────────────────────────
    
    def _load(self):
        """Load and decrypt the vault from disk."""
        try:
            if not self._vault_path.exists():
                logger.warning(f"Vault file not found: {self._vault_path}")
                self._loaded = False
                return
            
            encrypted = self._vault_path.read_bytes()
            if not encrypted:
                logger.warning("Vault file is empty")
                self._loaded = False
                return
            
            if self._master_key is None:
                logger.warning(
                    "No VAULT_MASTER_KEY set — vault is locked. "
                    "Falling back to environment variables."
                )
                self._loaded = False
                return
            
            try:
                plaintext = decrypt(encrypted, self._master_key)
                self._data = json.loads(plaintext)
                del plaintext  # Memory hygiene: clear decrypted data (P5 F-3)
                self._loaded = True
                key_count = sum(
                    len(v.get("accounts", {})) if isinstance(v, dict) and "accounts" in v
                    else 1 if isinstance(v, str) or "keys" in v
                    else 1
                    for v in self._data.get("keys", {}).values()
                )
                logger.info(
                    f"Vault loaded: {len(self._data.get('keys', {}))} providers, "
                    f"{key_count} keys total"
                )
            except VaultCryptoError as e:
                self._loaded = False
                raise VaultLockedError(
                    f"Failed to decrypt vault: {e}. "
                    f"Check VAULT_MASTER_KEY."
                )
        except VaultLockedError:
            raise
        except (VaultCryptoError, json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load vault: {e}", exc_info=True)
            self._loaded = False
    
    def _save(self):
        """Encrypt and write the vault to disk."""
        try:
            vault_dir = self._vault_path.parent
            vault_dir.mkdir(parents=True, exist_ok=True)
            
            if self._master_key is None:
                logger.warning("Cannot save vault: no master key set")
                return
            
            plaintext = json.dumps(self._data, indent=2, default=str)
            encrypted = encrypt(plaintext, self._master_key)
            
            # Atomic write: .tmp -> .json.enc
            tmp_path = self._vault_path.with_suffix(".tmp")
            tmp_path.write_text(encrypted)
            tmp_path.rename(self._vault_path)
            
            # Restrict permissions
            self._vault_path.chmod(0o600)
            self._loaded = True  # Mark loaded after successful save (P5 F-4)
            
            logger.info(f"Vault saved: {self._vault_path}")
        except (OSError, RuntimeError) as e:
            logger.error(f"Failed to save vault: {e}", exc_info=True)
    
    def _auto_init_from_env(self):
        """Auto-initialize vault from existing .env file.
        
        This runs once on first instantiation if no vault file exists.
        It reads keys from the environment (.env or shell) and creates
        an initial vault.
        """
        logger.info("No vault found — auto-initializing from environment variables")
        
        env_key_map = {
            "exa": ("EXA_API_KEY", None),
            "firecrawl": ("FIRECRAWL_API_KEY", None),
            "google": ("GOOGLE_API_KEY", "primary"),
            "openrouter": ("OPENROUTER_API_KEY", None),
            "opencode_zen": ("OPENCODE_ZEN_API_KEY", None),
        }
        
        found_any = False
        for provider, (env_var, account) in env_key_map.items():
            value = os.environ.get(env_var, "")
            if value:
                self.set_key(provider, value, account=account)
                found_any = True
        
        if found_any:
            if self._master_key is None:
                # Auto-generate master key on first initialization
                from omega.vault.crypto import generate_master_key
                self._master_key = generate_master_key()
                logger.warning(
                    "VAULT_MASTER_KEY auto-generated. "
                    "Add this to your .env for persistence:\n"
                    f"VAULT_MASTER_KEY={self._master_key.hex()}"
                )
            self._save()
            self._loaded = True
            logger.info("Vault auto-initialized from environment variables")
        else:
            logger.info("No API keys found in environment — vault remains empty")
    
    def _fallback_to_env(self, provider: str) -> Optional[str]:
        """Fallback to environment variable for a provider.
        
        Enables graceful transition: existing os.getenv() calls continue
        to work until all code is migrated to vault.
        """
        env_map = {
            "exa": "EXA_API_KEY",
            "firecrawl": "FIRECRAWL_API_KEY",
            "google": "GOOGLE_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "opencode_zen": "OPENCODE_ZEN_API_KEY",
            "antigravity_client_id": "ANTIGRAVITY_CLIENT_ID",
            "antigravity_client_secret": "ANTIGRAVITY_CLIENT_SECRET",
        }
        env_var = env_map.get(provider)
        if env_var:
            val = os.environ.get(env_var, "")
            if val:
                logger.debug(f"Fell back to env var {env_var} for provider '{provider}'")
                return val
        return None
    
    def _fallback_to_env_multi(self, provider: str) -> List[str]:
        """Fallback to environment-based multi-key pattern.
        
        Handles patterns like GOOGLE_API_KEY_01 through _08.
        """
        if provider == "google":
            keys = []
            primary = os.environ.get("GOOGLE_API_KEY", "")
            if primary:
                keys.append(primary)
            for i in range(1, 9):
                suffix = f"_{i:02d}"
                key = os.environ.get(f"GOOGLE_API_KEY{suffix}", "")
                if key:
                    keys.append(key)
            return keys
        return []
    
    def is_loaded(self) -> bool:
        """Check if the vault has been successfully loaded."""
        return self._loaded
    
    def get_providers(self) -> List[str]:
        """List all providers registered in the vault."""
        if self._loaded:
            return list(self._data.get("keys", {}).keys())
        return []
    
    def get_status(self) -> Dict:
        """Get vault status for diagnostics."""
        status = {
            "loaded": self._loaded,
            "vault_path": str(self._vault_path),
            "vault_exists": self._vault_path.exists(),
            "has_master_key": self._master_key is not None,
        }
        if self._loaded:
            status["providers"] = list(self._data.get("keys", {}).keys())
            status["rotation_policy"] = "sticky (round-robin ERADICATED per IW-2)"
            key_count = 0
            for provider, entry in self._data.get("keys", {}).items():
                if isinstance(entry, str):
                    key_count += 1
                elif isinstance(entry, dict):
                    key_count += len(entry.get("accounts", {}))
            status["total_keys"] = key_count
        return status
