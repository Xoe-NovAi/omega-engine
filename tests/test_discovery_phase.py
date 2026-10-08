# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""P0 regression: `DiscoveryOrchestrator._phase_discovery` did not exist.

`_research_subtopic` has always called `await self._phase_discovery(sub_query)`
(`src/omega/library/discovery.py`), but the method had NO definition anywhere in
the class:

    AttributeError: 'DiscoveryOrchestrator' object has no attribute '_phase_discovery'

Root cause (recovered from git, not guessed): commit 3418f854
"fix(discovery): library discovery tools no longer hardcode cloud-only model
names" extracted a new `_try_generate()` helper out of `_phase_synthesize`. The
extraction deleted the `async def _phase_discovery(self, query: str)` signature
line and left that method's BODY stranded underneath `_try_generate`'s new
`return`, where it became unreachable dead code. The call site survived; the
method did not. Any subtopic research therefore died on AttributeError.

These tests are deliberately structural as well as behavioural, because the
original defect was invisible to behavioural coverage:

  1. `_phase_discovery` is defined on the class (the direct guard).
  2. `discover()` runs the full pipeline end-to-end with NO AttributeError and
     populates `report.sources` with real dicts.
  3. `_research_subtopic` — the caller that owns the bug — works directly.
  4. `_phase_discovery` honours its `List[Dict[str, Any]]` return contract, which
     is what `report.sources.extend(...)` requires.
  5. 401/429 from Exa raise the specific provider errors (M23: no silent failure).
  6. STRUCTURAL: `_try_generate` has no unreachable statements after its
     unconditional `return` — the exact shape that hid this bug for ~3 months.
  7. STRUCTURAL: every `self._name(...)` call in the class resolves to a defined
     attribute, so the NEXT stranded method cannot hide the same way.

No network and no vault: the model gateway is a local fake (M7) and the vault is
forced absent (D-565), which is the real public-cut condition.
"""

import ast
import json
import os
import tempfile
from pathlib import Path

import pytest

# Isolate `data/` BEFORE importing omega.library.discovery — that module resolves
# DATA_DIR (and mkdir's its job queues) at import time, so the autouse
# OMEGA_DATA_DIR fixture in conftest.py arrives too late to help us here.
os.environ.setdefault("OMEGA_DATA_DIR", tempfile.mkdtemp(prefix="discovery-phase-"))

from omega.errors import ProviderAuthError, ProviderRateLimitError  # noqa: E402
from omega.library import discovery as d  # noqa: E402
from omega.library.discovery import DiscoveryOrchestrator, DiscoveryReport  # noqa: E402

MODULE_PATH = Path(d.__file__)


# --------------------------------------------------------------------------
# Local doubles — no network, no vault, no inference provider.
# --------------------------------------------------------------------------


class _FakeResult:
    def __init__(self, text: str):
        self.text = text


class _FakeGateway:
    """Stand-in for ModelGateway. Local-first, no cloud (M7)."""

    def __init__(self):
        self.calls = []

    async def generate(
        self,
        model_name=None,
        system_prompt="",
        user_query="",
        temperature=0.2,
        max_tokens=1024,
    ):
        self.calls.append({"system_prompt": system_prompt, "user_query": user_query})
        # `_phase_decompose` asks for a bare JSON list of sub-queries.
        if "research supervisor" in system_prompt:
            return _FakeResult(json.dumps(["alpha angle", "beta angle"]))
        return _FakeResult("stub synthesis text")


class _FakeResponse:
    def __init__(self, payload, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)
        self.url = "https://api.exa.ai/search"

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class _FakeAsyncClient:
    """Captures the request and replays a canned response."""

    last_request = {}

    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, json=None, headers=None):
        _FakeAsyncClient.last_request = {"url": url, "payload": json, "headers": headers}
        return self._response


@pytest.fixture
def orchestrator(monkeypatch):
    """A DiscoveryOrchestrator with no vault and no network."""
    monkeypatch.setattr(d, "VAULT_AVAILABLE", False)
    monkeypatch.setattr(d, "VaultCore", None)
    return DiscoveryOrchestrator(model_gateway=_FakeGateway())


# --------------------------------------------------------------------------
# 1. The direct guard.
# --------------------------------------------------------------------------


def test_phase_discovery_is_defined():
    """The P0 itself: the method must exist on the class."""
    assert hasattr(DiscoveryOrchestrator, "_phase_discovery"), (
        "DiscoveryOrchestrator._phase_discovery is missing — this is the P0 "
        "reintroduced. `_research_subtopic` calls it unconditionally."
    )
    assert callable(DiscoveryOrchestrator._phase_discovery)


# --------------------------------------------------------------------------
# 2. Full pipeline end-to-end.
# --------------------------------------------------------------------------


@pytest.mark.anyio
async def test_discover_runs_pipeline_without_attributeerror(orchestrator):
    """`discover()` must traverse the _phase_discovery call site (line ~341).

    This is the test that fails on the broken tree with the original
    AttributeError, rather than merely reporting a missing attribute.
    """
    report = await orchestrator.discover("what is sovereign retrieval?")

    assert isinstance(report, DiscoveryReport)
    assert report.status == "complete", f"pipeline failed: {report.final_synthesis!r}"
    # Two subtopics were decomposed; each must have completed (not raised).
    assert report.subtopics, "decomposition produced no subtopics"
    assert all(st["status"] == "complete" for st in report.subtopics), (
        f"subtopics did not complete: {report.subtopics}"
    )
    # `report.sources` is List[Dict] — populated via _phase_discovery.
    assert report.sources, "report.sources empty — _phase_discovery contributed nothing"
    assert all(isinstance(s, dict) for s in report.sources), (
        f"report.sources must hold dicts, got: {report.sources!r}"
    )


@pytest.mark.anyio
async def test_research_subtopic_calls_phase_discovery(orchestrator):
    """The caller that owned the bug, exercised directly."""
    report = DiscoveryReport(query="q")
    subtopic = {"query": "sub-query", "status": "pending"}

    await orchestrator._research_subtopic(report, subtopic)

    assert subtopic["status"] == "complete"
    assert report.sources, "no sources collected"
    assert all(isinstance(s, dict) for s in report.sources)


# --------------------------------------------------------------------------
# 3. The List[Dict] return contract + provider error taxonomy.
# --------------------------------------------------------------------------


@pytest.mark.anyio
async def test_phase_discovery_returns_exa_results_as_dicts(orchestrator, monkeypatch):
    """Exa's per-result dicts must survive intact.

    Guards against 'fixing' this by delegating to `ExaProvider.search()`,
    which returns Optional[str] and would silently fill `report.sources` with
    raw strings.
    """
    canned = {
        "results": [
            {"title": "Sovereign Retrieval", "url": "https://example.org/a", "score": 0.91},
            {"title": "Local-First Inference", "url": "https://example.org/b", "score": 0.77},
        ]
    }
    monkeypatch.setattr(
        d.httpx, "AsyncClient", lambda *a, **k: _FakeAsyncClient(_FakeResponse(canned))
    )
    orchestrator.exa_key = "test-key-not-a-real-secret"

    sources = await orchestrator._phase_discovery("sovereign retrieval")

    assert sources == canned["results"]
    assert all(isinstance(s, dict) for s in sources)
    # The sub-query must actually reach the provider.
    assert _FakeAsyncClient.last_request["payload"]["query"] == "sovereign retrieval"


@pytest.mark.anyio
async def test_phase_discovery_without_key_returns_labelled_mock(orchestrator):
    """D-565: vault absent on the public cut => degrade, do not crash."""
    assert orchestrator.exa_key is None

    sources = await orchestrator._phase_discovery("anything")

    assert sources and isinstance(sources[0], dict)
    assert sources[0]["url"] == "https://example.com"


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("status", "expected"),
    [(401, ProviderAuthError), (429, ProviderRateLimitError)],
)
async def test_phase_discovery_maps_provider_statuses(orchestrator, monkeypatch, status, expected):
    """M23: an auth/rate-limit failure must surface, never pass silently."""
    monkeypatch.setattr(
        d.httpx,
        "AsyncClient",
        lambda *a, **k: _FakeAsyncClient(_FakeResponse({"error": "nope"}, status_code=status)),
    )
    orchestrator.exa_key = "test-key-not-a-real-secret"

    with pytest.raises(expected):
        await orchestrator._phase_discovery("sovereign retrieval")


# --------------------------------------------------------------------------
# 4. Structural guards — the defect class, not just the instance.
# --------------------------------------------------------------------------


def _class_node():
    tree = ast.parse(MODULE_PATH.read_text())
    return next(
        n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "DiscoveryOrchestrator"
    )


def test_try_generate_has_no_unreachable_dead_code():
    """No statement may follow `_try_generate`'s unconditional return.

    The original bug was a method body parked after a `return`. That shape is
    syntactically valid, passes import, passes lint, and is invisible to every
    behavioural test — so assert on the AST directly.
    """
    fn = next(
        n
        for n in ast.walk(_class_node())
        if isinstance(n, ast.AsyncFunctionDef) and n.name == "_try_generate"
    )
    for i, stmt in enumerate(fn.body):
        if isinstance(stmt, ast.Return):
            trailing = fn.body[i + 1 :]
            assert not trailing, (
                f"{len(trailing)} unreachable statement(s) after the return in "
                f"_try_generate: {[type(s).__name__ for s in trailing]} — this is "
                "the exact shape that stranded _phase_discovery's body."
            )
            break
    else:
        pytest.fail("_try_generate has no unconditional return; shape changed — review")


def test_every_self_call_resolves_to_a_defined_attribute():
    """No `self._name(...)` call may reference an undefined method."""
    cls = _class_node()
    defined = set()
    for node in ast.walk(cls):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                ):
                    defined.add(target.attr)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Attribute):
            if isinstance(node.target.value, ast.Name) and node.target.value.id == "self":
                defined.add(node.target.attr)

    missing = {}
    for node in ast.walk(cls):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
            and node.func.attr not in defined
        ):
            missing.setdefault(node.func.attr, []).append(node.lineno)

    assert not missing, (
        f"called but never defined on DiscoveryOrchestrator: {missing} — "
        "each is a latent AttributeError (M23)"
    )
