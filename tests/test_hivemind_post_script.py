# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ MAAT ⬡ TEST ⬡ v1.0.0
"""Tests for scripts/hivemind_post.py — the sanctioned no-MCP-tool Hivemind post.

Network is NEVER touched here. The transport is stubbed so these tests run
offline and deterministically, and so the failure modes that matter (hub
rejecting a post, non-JSON-RPC garbage, unreachable hub) are covered without
needing the hub to be up.

The three behaviours worth pinning:
  1. A REJECTED post must raise and exit non-zero (M23). A caller that ignored
     the hub's error string would report success while nothing was delivered —
     the exact silent-degradation class that kept this fleet blind.
  2. Empty containers must be sent VERBATIM as []/"", never coerced to null.
     The ratified `post` contract treats `decisions=[]` as valid ("no
     decisions") and only rejects an explicit None; nulling them out would
     turn a legitimate post into a rejection.
  3. A transport failure must be distinguishable from a rejection by exit code.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import urllib.error
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "hivemind_post.py"
_spec = importlib.util.spec_from_file_location("hivemind_post", _SCRIPT)
hivemind_post = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hivemind_post)


class _FakeResp:
    def __init__(self, body: str):
        self._body = body

    def read(self) -> bytes:
        return self._body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _rpc_result(payload: dict) -> str:
    """Frame a payload the way the hub does: JSON-RPC tools/call result."""
    return json.dumps(
        {"jsonrpc": "2.0", "id": 2,
         "result": {"content": [{"type": "text", "text": json.dumps(payload)}]}}
    )


def _install(monkeypatch, responses: list[str]):
    """Serve `responses` in order to successive urlopen calls."""
    calls: list[dict] = []

    def fake_urlopen(req, timeout=None):
        calls.append(json.loads(req.data.decode("utf-8")))
        body = responses[min(len(calls) - 1, len(responses) - 1)]
        return _FakeResp(body)

    monkeypatch.setattr(hivemind_post.urllib.request, "urlopen", fake_urlopen)
    return calls


def test_post_sends_all_fields_verbatim(monkeypatch):
    """Every ratified post field reaches the hub unmodified."""
    calls = _install(monkeypatch, [
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}),   # initialize
        _rpc_result({"status": "accepted", "session_id": "ses_test1"}),
    ])

    got = hivemind_post.post(
        "http://hub/mcp", channel="opencode", entity="maat",
        model="opencode/space-bunny-free", task_current="COMPACT-PREP",
        focus_chain=["a", "b"], decisions=["d1"], continuation="next",
        intent="status",
    )

    assert got["status"] == "accepted"
    assert got["session_id"] == "ses_test1"

    args = calls[1]["params"]["arguments"]
    assert calls[1]["params"]["name"] == "hivemind_awareness"
    assert args["action"] == "post"
    assert args["channel"] == "opencode"
    assert args["entity"] == "maat"
    assert args["model"] == "opencode/space-bunny-free"
    assert args["task_current"] == "COMPACT-PREP"
    assert args["focus_chain"] == ["a", "b"]
    assert args["decisions"] == ["d1"]
    assert args["continuation"] == "next"
    assert args["intent"] == "status"


def test_empty_containers_sent_as_empty_not_null(monkeypatch):
    """REGRESSION: `decisions=[]` is VALID and must not be nulled out.

    The ratified contract distinguishes "absent" (None -> rejected) from
    "present but empty" ([]/"" -> accepted). Coercing [] to null would turn a
    legitimate "no decisions recorded" post into a rejection.
    """
    calls = _install(monkeypatch, [
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}),
        _rpc_result({"status": "accepted", "session_id": "ses_empty"}),
    ])

    hivemind_post.post(
        "http://hub/mcp", channel="opencode", entity="maat", model="m",
        task_current="t", focus_chain=[], decisions=[], continuation="",
    )
    args = calls[1]["params"]["arguments"]
    assert args["decisions"] == [] and args["decisions"] is not None
    assert args["focus_chain"] == [] and args["focus_chain"] is not None
    assert args["continuation"] == "" and args["continuation"] is not None
    # intent omitted entirely rather than sent as null
    assert "intent" not in args


def test_rejected_post_raises_and_names_the_field(monkeypatch):
    """M23: a hub rejection must raise, naming the missing field.

    If this returned normally, an agent would print "OK" while the post had
    been refused — indistinguishable from success.
    """
    _install(monkeypatch, [
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}),
        _rpc_result({"error": "post requires: decisions", "missing": ["decisions"]}),
    ])

    with pytest.raises(RuntimeError, match="REJECTED"):
        hivemind_post.post(
            "http://hub/mcp", channel="opencode", entity="maat", model="m",
            task_current="t", focus_chain=[], decisions=[], continuation="c",
        )


def test_exit_codes_distinguish_rejection_from_transport(monkeypatch):
    """Exit 1 = rejected by hub; exit 2 = transport failure. Never both 0."""
    _install(monkeypatch, [
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}),
        _rpc_result({"error": "post requires: decisions", "missing": ["decisions"]}),
    ])
    rc = hivemind_post.main(
        ["--url", "http://hub/mcp", "--entity", "maat", "--task-current", "t"]
    )
    assert rc == 1, "a rejected post must not exit 0"

    def boom(req, timeout=None):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(hivemind_post.urllib.request, "urlopen", boom)
    rc2 = hivemind_post.main(
        ["--url", "http://127.0.0.1:1/mcp", "--entity", "maat", "--task-current", "t"]
    )
    assert rc2 == 2, "an unreachable hub must not exit 0"


def test_non_jsonrpc_response_is_transport_failure(monkeypatch):
    """HTML or garbage from the endpoint must fail loud, not parse as success."""
    _install(monkeypatch, ["<html>502 Bad Gateway</html>"])
    with pytest.raises(RuntimeError, match="non-JSON-RPC"):
        hivemind_post.post(
            "http://hub/mcp", channel="opencode", entity="maat", model="m",
            task_current="t", focus_chain=[], decisions=[], continuation="c",
        )


def test_sse_framed_response_is_unwrapped(monkeypatch):
    """Streamable-HTTP may frame the JSON as an SSE `data:` line."""
    payload = _rpc_result({"status": "accepted", "session_id": "ses_sse"})
    _install(monkeypatch, [
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}),
        f"event: message\ndata: {payload}\n\n",
    ])
    got = hivemind_post.post(
        "http://hub/mcp", channel="opencode", entity="maat", model="m",
        task_current="t", focus_chain=[], decisions=[], continuation="c",
    )
    assert got["session_id"] == "ses_sse"


def test_read_back_returns_snapshot(monkeypatch):
    """--read-back proves a post actually landed, rather than assuming it."""
    _install(monkeypatch, [
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}}),
        _rpc_result({"entity": "maat", "task_current": "COMPACT-PREP"}),
    ])
    snap = hivemind_post.read_back("http://hub/mcp", "ses_abc")
    assert snap["entity"] == "maat"
    assert snap["task_current"] == "COMPACT-PREP"


def test_entity_required_for_post(monkeypatch):
    """Posting without --entity must fail on argument parsing, not guess."""
    with pytest.raises(SystemExit):
        hivemind_post.main(["--url", "http://hub/mcp", "--task-current", "t"])


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__]))
