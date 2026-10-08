# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ VERITY ⬡ TEST ⬡ v1.0.0
# Test suite for GitHub Hivemind Bridge
#
# [seam-fix 2026-09-28 maat] This file collected ZERO tests. The Hivemind
# consolidation deleted `hivemind_post_context`, but github_bridge.py still
# imported it directly from hub_tools, so the module raised ImportError at
# collection and pytest reported "Ran 0 tests" — a green-looking result that
# was actually total absence of coverage. It is now wired to the unified
# `hivemind_awareness(action="post")` surface.
#
# The post is mocked at the bridge boundary rather than initialising the whole
# hub service stack. Two reasons:
#   1. Speed and isolation — _init_services() loads the model gateway, Qdrant
#      and friends; a signature-mapping test should not pay for that.
#   2. It lets the test assert the FIELD MAPPING, which is precisely what the
#      consolidation could have broken. The previous test only asserted "did not
#      raise", so a caller that dropped `decisions` or `intent` would have
#      passed. This one pins every field.

import json

import anyio
import pytest

import mcp_servers.omega_hub.github_bridge as bridge
from mcp_servers.omega_hub.github_bridge import (
    process_github_event,
    verify_signature,
)


@pytest.fixture
def recorded_posts(monkeypatch):
    """Capture hivemind_awareness(action="post") calls made by the bridge.

    Returns the list of captured kwargs dicts. Patches the symbol the bridge
    module imported, which is the boundary the bridge actually calls through.
    """
    calls: list[dict] = []

    async def fake_awareness(**kwargs):
        calls.append(kwargs)
        return json.dumps({"status": "accepted", "session_id": "ses_test"})

    monkeypatch.setattr(bridge, "hivemind_awareness", fake_awareness)
    return calls


@pytest.fixture
def mapped_entity(monkeypatch):
    """Patch the REAL account-mapping function.

    The pre-existing tests set `bridge._get_github_account`, which does not
    exist in github_bridge.py. Assigning it created a brand-new module
    attribute that nothing ever called, so the account-mapping path was never
    actually mocked — the tests silently exercised the real lookup. The real
    function is `_map_github_user_to_entity` (github_bridge.py:61).

    Returns a setter so each test can choose the mapped entity.
    """
    box = {"entity": "SOPHIA"}

    async def _mapper(username: str) -> str:
        return box["entity"]

    monkeypatch.setattr(bridge, "_map_github_user_to_entity", _mapper)

    def _set(entity: str) -> None:
        box["entity"] = entity

    return _set


@pytest.mark.anyio
async def test_verify_signature_valid(monkeypatch):
    secret = "test_webhook_secret_for_verification"
    payload = b'{"action": "opened", "issue": {"number": 1}}'

    async def mock_get_secret():
        return secret

    monkeypatch.setattr(bridge, "_get_webhook_secret", mock_get_secret)

    import hashlib
    import hmac

    hash_val = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    signature = f"sha256={hash_val}"

    assert await verify_signature(payload, signature) is True


@pytest.mark.anyio
async def test_verify_signature_invalid():
    payload = b'{"action": "opened", "issue": {"number": 1}}'
    assert await verify_signature(payload, "sha256=wronghash") is False


@pytest.mark.anyio
async def test_process_github_event_mapping(recorded_posts, mapped_entity):
    """A PR event must reach the unified tool with every field preserved."""
    mapped_entity("kali")

    payload = {
        "sender": {"login": "test-user"},
        "action": "opened",
        "pull_request": {"title": "Test PR"},
    }

    await process_github_event("pull_request", payload)

    assert len(recorded_posts) == 1, "bridge did not post exactly one awareness snapshot"
    post = recorded_posts[0]

    # The action discriminator the unified API requires.
    assert post["action"] == "post"

    # Every field the retired hivemind_post_context call passed, preserved.
    # The regression this pins: the consolidation could silently drop any one
    # of these and the old "does not raise" assertion would still pass.
    assert post["channel"] == "github-bridge"
    assert post["entity"] == "kali"
    assert post["model"] == "SOPHIA"
    assert post["task_current"] == "GitHub Event: PR opened: Test PR (by test-user)"
    assert post["focus_chain"] == ["github-integration", "pull_request"]
    assert post["decisions"] == []
    assert post["continuation"] == "Event processed by bridge. Source: test-user"
    assert post["intent"] == "observation"


@pytest.mark.anyio
async def test_empty_decisions_list_is_preserved(recorded_posts, mapped_entity):
    """`decisions=[]` must survive the mapping.

    Regression pin for the validation bug fixed in hivemind_awareness: the post
    branch validated with `all([...])`, which treats an empty list as missing
    and returned an error STRING rather than raising. A caller that ignored the
    return value believed it had posted while nothing reached the Hivemind.
    """
    mapped_entity("kali")
    await process_github_event("push", {"sender": {"login": "test-user"}, "ref": "refs/heads/main"})

    assert recorded_posts[0]["decisions"] == [], (
        "decisions must be passed through as an empty list, not dropped or "
        "coerced to None"
    )


@pytest.mark.anyio
async def test_rejected_post_fails_loud(monkeypatch, mapped_entity):
    """M23: a rejected post must raise, not be silently swallowed.

    The unified tool returns a JSON error string instead of raising. If the
    bridge ignored that, a broken webhook bridge would be indistinguishable
    from a working one — it would log success and post nothing.
    """

    async def rejecting_awareness(**kwargs):
        return json.dumps({"error": "post requires: decisions", "missing": ["decisions"]})

    monkeypatch.setattr(bridge, "hivemind_awareness", rejecting_awareness)
    mapped_entity("kali")

    payload = {"sender": {"login": "test-user"}, "action": "opened", "issue": {"title": "X"}}

    with pytest.raises(RuntimeError, match="Hivemind post rejected"):
        await process_github_event("issue", payload)


@pytest.mark.anyio
async def test_process_github_event_fallback(recorded_posts, mapped_entity):
    """An unmappable GitHub user falls back rather than crashing.

    `_map_github_user_to_entity` returns "SOPHIA" when config/github_accounts.yaml
    is absent or the username is unknown (github_bridge.py:70-88). This pins
    that the bridge still posts under the fallback entity rather than raising.
    """
    mapped_entity("SOPHIA")

    payload = {
        "sender": {"login": "unknown-user"},
        "action": "opened",
        "issue": {"title": "Unknown Issue"},
    }

    await process_github_event("issue", payload)

    assert len(recorded_posts) == 1
    assert recorded_posts[0]["action"] == "post"
