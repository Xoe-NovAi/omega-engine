---
schema_version: "1.0"
document_type: "ticket_page"
document_id: "v-1-vaultcore-mvp"
title: "V-1: VaultCore MVP — Secure Credential Storage"
status: "PLANNED"
version: "1.0.0"
date: "2026-07-22"
owner: "maat/P1"
tags: ["sprint-plan", "phase-c", "p0-tickets", "llm-friendly", "guard-and-distill", "vault", "credentials", "encryption"]
priority: "P0"
depends_on: ["C-0", "C-1'"]
blocks: ["C-3", "C-0.5", "Phase D"]
acceptance_gates:
  - "VaultCore class with encrypt/decrypt using age (RFC 8610) or libsodium"
  - "Credentials stored in data/vault/ with .age encryption"
  - "Master key derived from passphrase + salt (Argon2id, 3 iterations)"
  - "CLI: omega vault set/get/list/rotate"
  - "B2 Application Key + Restic password + Provider API keys supported"
  - "Append-only audit log in data/vault/audit.log"
  - "Unit tests: 5+ scenarios (set, get, rotate, corrupt, missing)"
  - "Integration: C-3 restic script reads B2 keys from VaultCore"
cross_references:
  - "SOVEREIGN_ARK_BLUEPRINT.md"
  - "FLEET_TEAM_PLAYBOOK.md"
  - "LLM_FRIENDLY_DOCS_BP.md"
llm_metadata:
  token_budget: 3000
  chunk_strategy: "section_per_ticket"
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 V-1: VaultCore MVP — Secure Credential Storage
**AP Token**: `AP-TICKET-V1-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ticket_p0 ⬡ ACTIVE

**Date**: 2026-07-22
**Ticket ID**: `V-1`
**Sprint**: `guard-and-distill-2026-07-22`
**Priority**: P0 (Elevated by Kali Amendment 3)
**Owner**: maat/P1
**Status**: PLANNED
**Depends On**: ["C-0", "C-1'"]
**Blocks**: ["C-3", "C-0.5", "Phase D"]
**Estimated Hours**: 3

---

## What

Implement **VaultCore** — a minimal, sovereign credential vault for the Omega Engine. Stores B2 Application Keys, Restic repository passwords, and Provider API keys using age encryption (RFC 8610) with Argon2id key derivation.

## Why

**C-3 Restic backup cannot proceed without VaultCore** (Kali Amendment 3). The restic script needs B2 keys and repository passwords. Storing these in plaintext `config/providers.yaml` or environment files violates sovereignty. VaultCore provides encrypted storage with audit trail.

---

## Acceptance Criteria (Copy-Paste Verifiable)

- [ ] `VaultCore` class with `encrypt()`, `decrypt()`, `store()`, `retrieve()`, `rotate()`, `list()` methods
- [ ] Uses `age` (RFC 8610) via `rage` Python binding or `subprocess` to `age` CLI
- [ ] Master key: Argon2id(passphrase, salt, iterations=3, memory=64MB, parallelism=4)
- [ ] Credentials stored as individual `.age` files in `data/vault/`
- [ ] CLI: `omega vault set <key> <value>`, `omega vault get <key>`, `omega vault list`, `omega vault rotate <key>`
- [ ] Audit log: `data/vault/audit.log` (append-only, JSON Lines: timestamp, operation, key, success)
- [ ] Supported credential types: `b2_key_id`, `b2_app_key`, `restic_password`, `provider:<name>:api_key`
- [ ] Unit tests: 5+ scenarios (set/get, rotate, corrupt file, missing key, wrong passphrase)
- [ ] Integration: `scripts/backup_restic.sh` reads B2 keys via `VaultCore.retrieve("b2_key_id")`

---

## Implementation Sketch (Self-Contained)

```python
# File: src/omega/vault/vault_core.py
# Purpose: Sovereign credential vault using age encryption
# Dependencies: argon2-cffi, age (via subprocess or rage), anyio

import anyio
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

@dataclass
class AuditEntry:
    timestamp: str
    operation: str  # set, get, rotate, list, delete
    key: str
    success: bool
    error: Optional[str] = None

class VaultCore:
    """Sovereign credential vault using age encryption."""
    
    def __init__(self, vault_dir: Path, passphrase: str):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log = self.vault_dir / "audit.log"
        self._passphrase = passphrase
        self._salt = self.vault_dir / "salt.bin"
        self._master_key = self.vault_dir / "master.age"
        
    async def _derive_key(self) -> bytes:
        """Derive master key using Argon2id."""
        import argon2
        if not self._salt.exists():
            salt = os.urandom(16)
            self._salt.write_bytes(salt)
        else:
            salt = self._salt.read_bytes()
        
        ph = argon2.PasswordHasher(
            time_cost=3,
            memory_cost=65536,  # 64 MB
            parallelism=4,
            hash_len=32,
            type=argon2.Type.ID
        )
        # Argon2id derives key from passphrase + salt
        hash_bytes = ph.hash(self._passphrase.encode() + salt)
        # Extract raw key from hash (last 32 bytes of decoded hash)
        return hash_bytes[-32:]
    
    async def _age_encrypt(self, plaintext: str, recipient: str) -> str:
        """Encrypt using age with recipient (public key)."""
        proc = await anyio.run_process(
            ["age", "-r", recipient, "-e"],
            input=plaintext.encode(),
            capture=True
        )
        if proc.returncode != 0:
            raise VaultError(f"age encrypt failed: {proc.stderr.decode()}")
        return proc.stdout.decode()
    
    async def _age_decrypt(self, ciphertext: str) -> str:
        """Decrypt using age with master key (private key from passphrase)."""
        # Use master key file as identity
        proc = await anyio.run_process(
            ["age", "-d", "-i", str(self._master_key)],
            input=ciphertext.encode(),
            capture=True
        )
        if proc.returncode != 0:
            raise VaultError(f"age decrypt failed: {proc.stderr.decode()}")
        return proc.stdout.decode()
    
    async def _ensure_master_key(self):
        """Generate or load master age key pair."""
        if not self._master_key.exists():
            # Generate key pair from passphrase-derived seed
            key_bytes = await self._derive_key()
            # age-keygen from seed
            proc = await anyio.run_process(
                ["age-keygen", "-y"],
                input=key_bytes.hex().encode(),
                capture=True
            )
            if proc.returncode != 0:
                raise VaultError(f"age-keygen failed: {proc.stderr.decode()}")
            # Output format: "AGE-SECRET-KEY-... # public key: age1..."
            lines = proc.stdout.decode().strip().split('\n')
            private_key = lines[0].split()[0]
            public_key = lines[1].split(': ')[1] if len(lines) > 1 else None
            self._master_key.write_text(private_key)
            # Store public key for reference
            (self.vault_dir / "master.pub").write_text(public_key or "")
        return (self.vault_dir / "master.pub").read_text().strip()
    
    async def store(self, key: str, value: str) -> bool:
        """Store a credential."""
        try:
            recipient = await self._ensure_master_key()
            ciphertext = await self._age_encrypt(value, recipient)
            credential_file = self.vault_dir / f"{key}.age"
            credential_file.write_text(ciphertext)
            await self._audit("set", key, True)
            return True
        except Exception as e:
            await self._audit("set", key, False, str(e))
            raise VaultError(f"Failed to store {key}: {e}")
    
    async def retrieve(self, key: str) -> Optional[str]:
        """Retrieve a credential."""
        credential_file = self.vault_dir / f"{key}.age"
        if not credential_file.exists():
            await self._audit("get", key, False, "Key not found")
            return None
        try:
            ciphertext = credential_file.read_text()
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
        keys = [f.stem for f in self.vault_dir.glob("*.age")]
        await self._audit("list", "all", True)
        return keys
    
    async def delete(self, key: str) -> bool:
        """Delete a credential."""
        credential_file = self.vault_dir / f"{key}.age"
        if credential_file.exists():
            credential_file.unlink()
            await self._audit("delete", key, True)
            return True
        await self._audit("delete", key, False, "Key not found")
        return False
    
    async def _audit(self, operation: str, key: str, success: bool, error: Optional[str] = None):
        """Append to audit log."""
        entry = AuditEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            operation=operation,
            key=key,
            success=success,
            error=error
        )
        async with await anyio.open_file(self.audit_log, "a") as f:
            await f.write(json.dumps(asdict(entry)) + "\n")

class VaultError(Exception):
    pass
```

```python
# File: src/omega/cli/vault.py
# Purpose: CLI commands for vault operations

import anyio
import click
from pathlib import Path
from src.omega.vault.vault_core import VaultCore, VaultError

@click.group()
def vault():
    """Sovereign credential vault operations."""
    pass

@vault.command()
@click.argument("key")
@click.argument("value")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path))
def set(key: str, value: str, passphrase: str, vault_dir: Path):
    """Store a credential."""
    async def _set():
        vault = VaultCore(vault_dir, passphrase)
        await vault.store(key, value)
        click.echo(f"Stored: {key}")
    anyio.run(_set)

@vault.command()
@click.argument("key")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path))
def get(key: str, passphrase: str, vault_dir: Path):
    """Retrieve a credential."""
    async def _get():
        vault = VaultCore(vault_dir, passphrase)
        value = await vault.retrieve(key)
        if value is None:
            click.echo(f"Key not found: {key}", err=True)
            raise click.Abort()
        click.echo(value)
    anyio.run(_get)

@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path))
def list(passphrase: str, vault_dir: Path):
    """List all credential keys."""
    async def _list():
        vault = VaultCore(vault_dir, passphrase)
        keys = await vault.list_keys()
        for k in keys:
            click.echo(k)
    anyio.run(_list)

@vault.command()
@click.argument("key")
@click.argument("new_value")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path))
def rotate(key: str, new_value: str, passphrase: str, vault_dir: Path):
    """Rotate a credential."""
    async def _rotate():
        vault = VaultCore(vault_dir, passphrase)
        await vault.rotate(key, new_value)
        click.echo(f"Rotated: {key}")
    anyio.run(_rotate)

@vault.command()
@click.argument("key")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path))
def delete(key: str, passphrase: str, vault_dir: Path):
    """Delete a credential."""
    async def _delete():
        vault = VaultCore(vault_dir, passphrase)
        await vault.delete(key)
        click.echo(f"Deleted: {key}")
    anyio.run(_delete)
```

---

## Research-Backed Patterns (Structured)

```yaml
research_patterns:
  - pattern: "age Encryption (RFC 8610)"
    source: "FiloSottile/age, rage bindings, 2026-07"
    key_insights:
      - "Modern, simple, UNIX-y encryption tool"
      - "Supports passphrase-derived keys via scrypt (but we use Argon2id separately)"
      - "age-keygen can derive from seed; we use passphrase → Argon2id → seed"
      - "CLI and library (rage) available; subprocess to CLI is simpler for audit"
  
  - pattern: "Argon2id Key Derivation"
    source: "RFC 9106, argon2-cffi 2026-06"
    key_insights:
      - "Winner of Password Hashing Competition"
      - "Memory-hard: 64MB, 3 iterations, 4 threads = ~200ms on modern CPU"
      - "Resistant to GPU/ASIC cracking"
      - "Use Type.ID (Argon2id) for side-channel resistance"
  
  - pattern: "Append-Only Audit Log"
    source: "AWS CloudTrail pattern, restic audit"
    key_insights:
      - "JSON Lines format for streaming parsing"
      - "Never modify — only append"
      - "Include: timestamp, operation, key, success, error"
      - "Rotate annually; keep 7 years for sovereignty"
```

---

## Commands to Verify

```bash
# Install dependencies
pip install argon2-cffi
# age CLI: install via package manager or download from FiloSottile/age releases

# Test vault operations
OMEGA_VAULT_PASSPHRASE="test-passphrase" python -m src.omega.cli.vault set b2_key_id "my-key-id"
OMEGA_VAULT_PASSPHRASE="test-passphrase" python -m src.omega.cli.vault set b2_app_key "my-app-key"
OMEGA_VAULT_PASSPHRASE="test-passphrase" python -m src.omega.cli.vault set restic_password "strong-random-password"
OMEGA_VAULT_PASSPHRASE="test-passphrase" python -m src.omega.cli.vault list

# Verify encryption
cat data/vault/b2_key_id.age  # Should be age ciphertext

# Run unit tests
pytest tests/unit/test_vault_core.py -v

# Integration test: restic script reads from vault
OMEGA_VAULT_PASSPHRASE="test-passphrase" python -c "
from src.omega.vault.vault_core import VaultCore
import anyio
async def test():
    v = VaultCore(Path('data/vault'), 'test-passphrase')
    print(await v.retrieve('b2_key_id'))
anyio.run(test)
"
```

---

## Kali Amendments Applied

| Amendment | Original Scope | Amended Scope |
|-----------|----------------|---------------|
| **Amendment 3** | "V-1 credential rotation" | **V-1 Elevated to P0-1** — Must ship FIRST. Blocks C-3 restic backup. Secure storage for B2 keys, restic passwords, provider API keys. |

---

*⬡ OMEGA ⬡ MAAT ⬡ TICKET-V1 ⬡ v1.0.0 ⬡ 2026-07-22*