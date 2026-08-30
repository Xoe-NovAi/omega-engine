# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Regression tests for SovereignSigner fail-closed secret handling.

D-590: M8/M22 security fix — provenance stamps must never fall back to a
hardcoded default secret. SovereignSigner raises OmegaError when neither
secret_key nor OMEGA_INGESTION_SECRET is provided.
"""
import os
import pytest

from omega.errors import OmegaError
from omega.oracle.ingestion import SovereignSigner


def test_raises_when_no_secret_and_env_unset(monkeypatch):
    """Fail-closed: no secret_key arg AND no env var → OmegaError."""
    monkeypatch.delenv("OMEGA_INGESTION_SECRET", raising=False)
    with pytest.raises(OmegaError):
        SovereignSigner()


def test_signs_when_secret_passed_directly():
    """Explicit secret_key is accepted (no env required)."""
    signer = SovereignSigner(secret_key="test-secret-value")
    stamp = signer.sign("content", {"k": "v"})
    assert isinstance(stamp, str) and len(stamp) == 64  # sha256 hex


def test_signs_when_env_set(monkeypatch):
    """Env var OMEGA_INGESTION_SECRET is accepted."""
    monkeypatch.setenv("OMEGA_INGESTION_SECRET", "env-provided-secret")
    signer = SovereignSigner()
    stamp = signer.sign("content", {"k": "v"})
    assert isinstance(stamp, str) and len(stamp) == 64


def test_verify_roundtrip(monkeypatch):
    """A stamp produced by sign() verifies true; tamper verifies false."""
    monkeypatch.setenv("OMEGA_INGESTION_SECRET", "roundtrip-secret")
    signer = SovereignSigner()
    content, meta = "payload", {"src": "web"}
    stamp = signer.sign(content, meta)
    assert signer.verify(content, meta, stamp) is True
    assert signer.verify("tampered", meta, stamp) is False
