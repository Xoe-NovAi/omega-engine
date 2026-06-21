"""M21 Gate Integrity: Contract Tests for Core API Boundaries.

[M21: Gate Integrity Mandate] Every core API boundary returning a typed result
MUST be exercised by at least one test that validates the return type.
No mock-based tests that mask type mismatches.

These tests verify real isinstance() checks against the actual dataclasses
returned by the public API — not mock stubs that may drift from reality.

Test Plan:
  1. model_gateway.generate() returns GenerateResult (not a string or tuple)
  2. oracle.talk() returns OracleResponse (not a GenerateResult or string)
  3. GenerateResult instance from MockProvider has all required fields:
     text (str), provider_name (str), is_cloud (bool)
"""

import pytest
import os

from omega.oracle.model_gateway import ModelGateway, GenerateResult
from omega.oracle.oracle import Oracle, OracleResponse


# ── Helpers ──────────────────────────────────────────────────────────────

def _run(coro_fn):
    """Run an async test function (same pattern as test_oracle.py)."""
    import anyio
    return anyio.run(coro_fn)


# ── Test 1: ModelGateway.generate() returns GenerateResult ──────────────

def test_generate_returns_generateresult():
    """M21: Contract test — ModelGateway.generate() returns GenerateResult.

    In OMEGA_ENV=test, ModelGateway loads only MockProvider, which returns
    a deterministic string. The generate() method must wrap that string in
    a GenerateResult dataclass — not return the raw string or a tuple.
    """
    async def t():
        gateway = ModelGateway()
        result = await gateway.generate(
            model_name="test-model",
            system_prompt="You are a test entity.",
            user_query="Hello",
            temperature=0.7,
            max_tokens=100,
        )
        # M21 Gate Integrity: verify exact return type
        assert isinstance(result, GenerateResult), (
            f"Expected GenerateResult, got {type(result).__name__}: {result!r}"
        )
        # Sanity: the text field should contain a non-empty string
        assert isinstance(result.text, str)
        assert len(result.text) > 0
        return result

    result = _run(t)
    # Re-assert outside the coroutine for clarity in failure output
    assert isinstance(result, GenerateResult)


# ── Test 2: Oracle.talk() returns OracleResponse ───────────────────────

def test_talk_returns_oracleresponse():
    """M21: Contract test — Oracle.talk() returns OracleResponse.

    The talk() method must wrap all results (Iris direct, domain-routed,
    or summoned) in an OracleResponse dataclass. It must NEVER return a
    raw string, a GenerateResult, or a tuple — all of which would be
    invisible type errors caught only at runtime.
    """
    async def t():
        oracle = Oracle()
        result = await oracle.talk("hello")
        return result

    result = _run(t)

    # M21 Gate Integrity: verify exact return type
    assert isinstance(result, OracleResponse), (
        f"Expected OracleResponse, got {type(result).__name__}: {result!r}"
    )

    # The OracleResponse must have the minimum expected fields populated
    assert isinstance(result.text, str), f"text must be str, got {type(result.text)}"
    assert isinstance(result.entity, str), f"entity must be str, got {type(result.entity)}"
    assert isinstance(result.confidence, float), (
        f"confidence must be float, got {type(result.confidence)}"
    )

    # These are NOT GenerateResult fields — ensure we don't regress
    # to confusing the two dataclass types
    assert not hasattr(result, "provider_name"), (
        "OracleResponse should not have provider_name (that's GenerateResult's field)"
    )
    assert not hasattr(result, "is_cloud"), (
        "OracleResponse should not have is_cloud (that's GenerateResult's field)"
    )


# ── Test 3: GenerateResult has all required fields ─────────────────────

def test_generateresult_has_required_fields():
    """M21: Contract test — GenerateResult dataclass has required fields.

    The GenerateResult is the canonical return type for all model inference.
    Downstream consumers (Oracle._summon, observability, token ledger) rely
    on these fields being present with the correct types.
    
    Required fields per the dataclass definition in model_gateway.py:
      - text: str          — the generated response text
      - provider_name: str — the ACTUAL provider that served the response
      - is_cloud: bool     — sovereignty flag (local vs cloud provenance)
      - latency_ms: float  — generation latency (default 0.0)
      - model_used: Optional[str] — model identifier (default None)
    """
    async def t():
        gateway = ModelGateway()
        result = await gateway.generate(
            model_name="test-model",
            system_prompt="You are a test entity.",
            user_query="Hello",
            temperature=0.7,
            max_tokens=100,
        )
        return result

    result = _run(t)

    # 1. text: str — the actual response content
    assert isinstance(result.text, str), (
        f"GenerateResult.text must be str, got {type(result.text).__name__}"
    )
    assert len(result.text) > 0, "GenerateResult.text must be non-empty"

    # 2. provider_name: str — provenance tracking (M22 Response Provenance)
    assert isinstance(result.provider_name, str), (
        f"GenerateResult.provider_name must be str, "
        f"got {type(result.provider_name).__name__}"
    )
    # In test mode, the active provider should be "mock"
    assert result.provider_name == "mock", (
        f"Expected provider_name='mock', got '{result.provider_name}'"
    )

    # 3. is_cloud: bool — sovereignty tracking (Mandate 7)
    assert isinstance(result.is_cloud, bool), (
        f"GenerateResult.is_cloud must be bool, "
        f"got {type(result.is_cloud).__name__}"
    )
    # MockProvider is local (not in _cloud_providers set)
    assert result.is_cloud is False, (
        f"MockProvider should report is_cloud=False, got {result.is_cloud}"
    )

    # 4. latency_ms: float — timing metadata (default 0.0)
    assert isinstance(result.latency_ms, float), (
        f"GenerateResult.latency_ms must be float, "
        f"got {type(result.latency_ms).__name__}"
    )

    # 5. model_used: Optional[str] — model identifier (may be None)
    assert result.model_used is None or isinstance(result.model_used, str), (
        f"GenerateResult.model_used must be str or None, "
        f"got {type(result.model_used).__name__}"
    )


# ── Negative Test: talk() must NOT return GenerateResult ───────────────

def test_talk_does_not_return_generateresult():
    """M21: Negative contract — talk() must NOT return GenerateResult.

    This is a regression guard. If someone changes talk() to pass through
    GenerateResult directly instead of wrapping it in OracleResponse, this
    test catches the drift immediately.
    """
    async def t():
        oracle = Oracle()
        result = await oracle.talk("hello")
        return result

    result = _run(t)

    # The cardinal sin: returning the wrong type
    assert not isinstance(result, GenerateResult), (
        "Oracle.talk() returned GenerateResult instead of OracleResponse! "
        "This means the outer response wrapper is broken or bypassed."
    )

    # It must be an OracleResponse
    assert isinstance(result, OracleResponse), (
        f"Expected OracleResponse, got {type(result).__name__}"
    )
