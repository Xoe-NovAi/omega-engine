# P1-2 VaultCrypto() Callsite Audit Report

**Document ID:** `P1-2_VAULTCRYPTO_AUDIT`
**Date:** 2026-09-21
**Executor:** Nemotron 3.5 Lightning (via MaKaLi Fusion orchestration)
**Spec:** `docs/specs/P1_TASK_SPECIFICATION.md` §P1-2

## Summary
- Total callsites: 5
- DEBUT-TRACK: 1
- EXCLUDED: 4
- Action Required: 1

## DEBUT-TRACK Callsites

### File: src/omega/cli/oracle_cli.py:77

```python
try:
    from omega.vault.crypto import VaultCrypto, VaultCryptoError
    crypto = VaultCrypto(master_key)
    encrypted = vault_path.read_text().strip()
    decrypted = crypto.decrypt(encrypted)
    secrets = _json.loads(decrypted)
    for k, v in secrets.items():
        if k not in _os.environ:
            _os.environ[k] = v
    return len(secrets)
except (ValueError, OSError, _json.JSONDecodeError, VaultCryptoError) as e:
    logger.debug(f"Vault injection skipped: {e}")
    return 0
```

**Classification:** DEBUT-TRACK
**Action:** Add error handling — `VaultCryptoError` added to caught exception tuple (line 86)

**Justification:** `VaultCrypto.__init__` raises `VaultCryptoError` when `_HAS_CRYPTO` is False (pyrage/argon2 not installed — current state). `VaultCryptoError(Exception)` is NOT a subclass of `ValueError`/`OSError`/`JSONDecodeError`, so the original `except` tuple did not catch it — the CLI would crash on `omega talk`/`omega summon` when the vault master key exists but crypto deps are absent. Fix: import `VaultCryptoError` and add to the caught exceptions. Behavior preserved: returns 0 (skip injection) on any vault failure.

## EXCLUDED Callsites

### File: src/omega/vault/crypto.py:137

```python
new_crypto = VaultCrypto(new_master_key)
```

**Classification:** EXCLUDED
**Justification:** Internal to `VaultCryptoManager.rotate()` — the vault subsystem itself. Vault excluded from debut per D-565 (no code changes to Vault for debut). Callsite is guarded by `_HAS_CRYPTO` checks in the manager path.

### File: src/omega/vault/crypto.py:156

```python
self._ciphers[version] = VaultCrypto(master_key)
```

**Classification:** EXCLUDED
**Justification:** Internal to `VaultCryptoManager` cipher registry — vault subsystem internals. D-565 excludes Vault from debut scope.

### File: src/omega/vault/crypto.py:193

```python
new_cipher = VaultCrypto(new_master_key)
```

**Classification:** EXCLUDED
**Justification:** Internal to `VaultCryptoManager.rotate()` — vault subsystem internals. D-565 excludes Vault from debut scope.

### File: src/omega/vault/crypto.py:206

```python
return VaultCrypto(master_key)
```

**Classification:** EXCLUDED
**Justification:** Internal to `VaultCryptoManager.get_cipher()` factory — vault subsystem internals. D-565 excludes Vault from debut scope.

## References
- Dialectic: `DIALECTIC_ANTIGRAVITY_FINAL_PASS_20260921` (Antigravity brain dir)
- P0 execution: `data/coordination/PR_READINESS_LIVE_FEED.md` (P0-2 ACCOUNT_MAP.yaml de-track)
- Decision D-565: Vault excluded from debut (no code changes)

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ NEMOTRON-3.5-LIGHTNING ⬡ P1-2-AUDIT ⬡ 2026-09-21*