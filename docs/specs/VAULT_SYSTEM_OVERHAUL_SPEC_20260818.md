# 🔱 Omega Engine — Vault System Overhaul Specification
**AP Token**: `AP-VAULT-OVERHAUL-SPEC-20260818-v1.0.0`
**Status**: DEFINITIVE — Implementation Ready
**Date**: 2026-08-18
**Authors**: Ma'at (Build), Lilith (Runtime), Researcher (Validation), Kali (Oversight)
**Supersedes**: `src/omega/vault/` (2,039 LOC — TO BE DELETED)

---

## 📋 Executive Summary

This specification defines the complete replacement of the custom `VaultCore` (2,039 LOC across 5 files) with a **platform-native, zero-dependency, pure-Python secret management system** that satisfies all Omega Engine constraints:

| Constraint | Solution |
|------------|----------|
| **M7 Local-First** | OS keyring (offline) + `pyrage`/`cryptography` fallback (offline) |
| **M16 Modularization** | Thin `credential_provider.py` wrapper; no engine logic in secret store |
| **M18 Token Efficiency** | Zero custom crypto; `flashtext` O(N) sanitization |
| **M24 Venv Sovereignty** | All deps in `.venv`; `pyrage` wheels + `cryptography` pure-Python |
| **30-Second Install** | No external binaries; systemd declarative hardening |
| **8 Accounts × 4 Providers** | Envelope encryption bypasses Windows 512B limit; bulk-edit via YAML bridge |
| **Agent Safety** | Zero-Knowledge `ProviderIdentity` + 4 egress sanitizers + RBAC |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HUMAN USER                                         │
│  omega secrets edit  →  $EDITOR (bundled micro) opens secrets.yaml.age      │
│  (SOPS-style decrypt → edit → auto-encrypt on save)                         │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CREDENTIAL PROVIDER (Process Edge)                     │
│  get_provider_credential("openrouter", "3") → "sk-or-..."                   │
│  • NEVER writes to os.environ                                               │
│  • Key lives ONLY in this scope                                             │
│  • Backend: OS keyring (primary) → pyrage/cryptography (fallback)           │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
      ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
      │  Provider   │     │  Provider   │     │  Provider   │
      │ (httpx)     │     │ (llama.cpp) │     │ (Search)    │
      │ Key in      │     │ Key in      │     │ Key in      │
      │ headers     │     │ context     │     │ params      │
      └─────────────┘     └─────────────┘     └─────────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EGRESS SANITIZATION LAYER                              │
│  SecretRegistry (flashtext) scans ALL outputs:                              │
│  • Logs → [REDACTED:openrouter_3]                                           │
│  • Hivemind/OpenCode DB → sanitized                                         │
│  • Crash dumps/Error capture → sanitized                                    │
│  • Observability SSE → sanitized                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Component 1: Encryption Backend (Auto-Select Chain)

### Backend Priority Chain

```python
# config/encryption_backend.py
BACKENDS = [
    ("pyrage", "pyrage", "Rust-backed age (fast, audited, wheels everywhere)"),
    ("cryptography", "crypto.aead_fallback.PurePythonAEAD", "Pure-Python AES-GCM (universal, no Rust)"),
]
```

### Wheel Coverage Matrix (Validated 2026-08-18)

| Platform | `pyrage` 1.3.0 | `cryptography` 42.0 |
|----------|----------------|---------------------|
| Windows x64 | ✅ `win_amd64` | ✅ |
| macOS Intel | ✅ `macosx_10_12_x86_64` | ✅ |
| macOS ARM64 | ✅ `macosx_11_0_arm64` | ✅ |
| macOS Universal2 | ✅ `macosx_10_12_universal2` | ✅ |
| Linux x86_64 (glibc) | ✅ `manylinux_2_17_x86_64` | ✅ |
| Linux ARM64 (glibc) | ✅ `manylinux_2_17_aarch64` | ✅ |
| **Alpine Linux (musl)** | ❌ **MISSING** | ✅ **Pure Python wheel** |
| **Raspberry Pi 32-bit (armv7)** | ❌ **MISSING** | ✅ **Pure Python wheel** |

### Implementation

```python
# config/encryption_backend.py
import sys, importlib
from pathlib import Path
from typing import Optional

class EncryptionBackend:
    """Auto-select best available encryption backend."""
    
    BACKENDS = [
        ("pyrage", "pyrage", "Rust-backed age"),
        ("cryptography", "crypto.aead_fallback.PurePythonAEAD", "Pure-Python AES-GCM"),
    ]
    
    def __init__(self):
        self._backend_name: Optional[str] = None
        self._impl = None
    
    def initialize(self) -> str:
        for name, import_path, desc in self.BACKENDS:
            try:
                if name == "pyrage":
                    import pyrage
                    self._impl = pyrage
                else:
                    mod_name, cls_name = import_path.rsplit(".", 1)
                    mod = importlib.import_module(mod_name)
                    self._impl = getattr(mod, cls_name)
                self._backend_name = name
                return name
            except ImportError:
                continue
        raise RuntimeError("No encryption backend available")
    
    def encrypt(self, data: bytes, recipient_pubkey: str = None, passphrase: str = None) -> bytes:
        if self._backend_name == "pyrage":
            if recipient_pubkey:
                from pyrage import encrypt, x25519
                recipient = x25519.Recipient.from_str(recipient_pubkey)
                return encrypt(data, [recipient])
            elif passphrase:
                from pyrage import passphrase
                return passphrase.encrypt(data, passphrase)
        else:
            if passphrase:
                key, salt = self._impl.derive_key(passphrase)
                aead = self._impl(key)
                return salt + aead.encrypt(data)
            raise NotImplementedError("Public-key encryption requires pyrage")
    
    def decrypt(self, data: bytes, identity: str = None, passphrase: str = None) -> bytes:
        if self._backend_name == "pyrage":
            if identity:
                from pyrage import decrypt, x25519
                ident = x25519.Identity.from_str(identity)
                return decrypt(data, [ident])
            elif passphrase:
                from pyrage import passphrase
                return passphrase.decrypt(data, passphrase)
        else:
            if passphrase:
                salt, ct = data[:16], data[16:]
                key, _ = self._impl.derive_key(passphrase, salt)
                aead = self._impl(key)
                return aead.decrypt(ct)
            raise NotImplementedError("Public-key decryption requires pyrage")

# Pure-Python AES-GCM Fallback (crypto/aead_fallback.py)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import os

class PurePythonAEAD:
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256-bit)")
        self._aead = AESGCM(key)
    
    def encrypt(self, plaintext: bytes, associated_data: bytes = b"") -> bytes:
        nonce = os.urandom(12)
        ct = self._aead.encrypt(nonce, plaintext, associated_data)
        return nonce + ct
    
    def decrypt(self, ciphertext: bytes, associated_data: bytes = b"") -> bytes:
        if len(ciphertext) < 12:
            raise ValueError("Ciphertext too short")
        nonce, ct = ciphertext[:12], ciphertext[12:]
        return self._aead.decrypt(nonce, ct, associated_data)

    @staticmethod
    def derive_key(passphrase: str, salt: bytes = None) -> tuple[bytes, bytes]:
        if salt is None:
            salt = os.urandom(16)
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"age-encryption.org/v1/passphrase",
        )
        return hkdf.derive(passphrase.encode()), salt
```