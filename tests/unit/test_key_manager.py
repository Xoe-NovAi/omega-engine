"""Unit tests for KeyManager — M23 hard-stop on missing key.

AP: AP-SQLCIPHER-ENCRYPTION-v1.0.0
"""
import os
import stat
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.omega.memory.key_manager import (
    KeyManager,
    KeyManagerError,
    ENV_KEY,
    KEYRING_SERVICE,
)


# ── Test 1: key from OS keyring ──────────────────────────────────────────
def test_key_from_os_keyring(monkeypatch, tmp_path):
    """When keyring returns a value, get_key() should return it without
    touching the env var or key file."""
    fake_key = "x" * 32  # 32-char minimum
    fake_keyring = {"get": fake_key, "set": None}

    def fake_get_password(service, user):
        assert service == KEYRING_SERVICE
        return fake_keyring["get"]

    def fake_set_password(service, user, password):
        fake_keyring["set"] = password

    monkeypatch.delenv(ENV_KEY, raising=False)
    monkeypatch.setattr(
        "keyring.get_password", fake_get_password, raising=False
    )
    # Use a tmp_path key file to ensure it is NOT consulted.
    km = KeyManager(key_file=tmp_path / "nope.key")
    result = km.get_key()
    assert result == fake_key
    assert not (tmp_path / "nope.key").exists()  # never touched


# ── Test 2: key from env var (keyring absent) ────────────────────────────
def test_key_from_env_var_when_keyring_missing(monkeypatch, tmp_path):
    """If keyring is not importable, env var is the next source."""
    fake_key = "y" * 40
    monkeypatch.setenv(ENV_KEY, fake_key)

    # Make `import keyring` raise ImportError
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "keyring":
            raise ImportError("simulated absence")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    km = KeyManager(key_file=tmp_path / "nope.key")
    result = km.get_key()
    assert result == fake_key


# ── Test 3: key from file with 0600 perms ────────────────────────────────
def test_key_from_file_with_correct_perms(monkeypatch, tmp_path):
    """If keyring missing + env unset, key file with mode 0600 is used."""
    fake_key = "z" * 48
    key_file = tmp_path / "sqlcipher.key"
    key_file.write_text(fake_key)
    key_file.chmod(0o600)

    monkeypatch.delenv(ENV_KEY, raising=False)

    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "keyring":
            raise ImportError("simulated absence")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    km = KeyManager(key_file=key_file)
    result = km.get_key()
    assert result == fake_key


# ── Test 4: key file with wrong perms hard-stops (M23) ───────────────────
def test_key_file_wrong_perms_raises(monkeypatch, tmp_path):
    """If key file has mode other than 0600, M23 hard-stop — do not
    silently accept a world-readable key."""
    key_file = tmp_path / "sqlcipher.key"
    key_file.write_text("a" * 32)
    key_file.chmod(0o644)  # WRONG

    monkeypatch.delenv(ENV_KEY, raising=False)
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "keyring":
            raise ImportError("simulated absence")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    km = KeyManager(key_file=key_file)
    with pytest.raises(KeyManagerError, match="MUST be 0o600"):
        km.get_key()


# ── Test 5: missing key raises (M23) ─────────────────────────────────────
def test_no_key_anywhere_raises(monkeypatch, tmp_path):
    """If no key can be resolved from any source, KeyManagerError."""
    monkeypatch.delenv(ENV_KEY, raising=False)
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "keyring":
            raise ImportError("simulated absence")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    km = KeyManager(key_file=tmp_path / "nope.key")
    with pytest.raises(KeyManagerError, match="No SQLCipher key found"):
        km.get_key()


# ── Test 6: set_key rejects too-short keys ───────────────────────────────
def test_set_key_rejects_short_key(monkeypatch, tmp_path):
    """32-char minimum is enforced to ensure adequate entropy for AES-256."""
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "keyring":
            raise ImportError("simulated absence")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    km = KeyManager(key_file=tmp_path / "k.key")
    with pytest.raises(KeyManagerError, match="Key length"):
        km.set_key("too-short")
    # And a valid key writes the file
    km.set_key("a" * 40)
    assert (tmp_path / "k.key").exists()
    mode = (tmp_path / "k.key").stat().st_mode & 0o777
    assert mode == 0o600
