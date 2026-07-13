# 🔱 Omega Engine — Hivemind Redis Tests (M21 Contract Tests)
# AP: AP-TEST-HIVEMIND-REDIS-v1.0.0
# ⬡ OMEGA ⬡ LILITH ⬡ test_hivemind_redis ⬡ P1-3
"""Contract tests for the Hivemind Redis ephemeral event bus.

Redis is not required — the client is mocked so tests run offline and verify
graceful degradation (M23: explicit unavailable status, never a silent crash).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from mcp_servers.omega_hub.hivemind_redis import HivemindRedis, get_hivemind_redis


def _make_mock_client(publish_return=1, messages=None):
    client = MagicMock()
    client.publish = AsyncMock(return_value=publish_return)
    pubsub = MagicMock()
    pubsub.subscribe = AsyncMock()
    pubsub.unsubscribe = AsyncMock()
    pubsub.close = AsyncMock()
    if messages is None:
        messages = []
    pubsub.get_message = AsyncMock(side_effect=[*messages, None])
    client.pubsub = MagicMock(return_value=pubsub)
    return client, pubsub


@pytest.mark.asyncio
async def test_publish_ok():
    client, _ = _make_mock_client(publish_return=2)
    bus = HivemindRedis(client=client)
    res = await bus.publish("heartbeat", '{"entity":"lilith"}')
    assert res["status"] == "ok"
    assert res["delivered"] == 2
    assert res["channel"].startswith("omega:hivemind:")


@pytest.mark.asyncio
async def test_publish_degrades_on_connection_error():
    client = MagicMock()
    client.publish = AsyncMock(side_effect=ConnectionError("redis down"))
    bus = HivemindRedis(client=client)
    res = await bus.publish("heartbeat", "x")
    assert res["status"] == "unavailable"
    assert "error" in res


@pytest.mark.asyncio
async def test_subscribe_collects_messages():
    msg_a = {"channel": "omega:hivemind:live", "data": "ping"}
    client, _ = _make_mock_client(messages=[msg_a])
    bus = HivemindRedis(client=client)
    res = await bus.subscribe("live", timeout=0.1)
    assert res["status"] == "ok"
    assert len(res["messages"]) == 1
    assert res["messages"][0]["data"] == "ping"


@pytest.mark.asyncio
async def test_subscribe_degrades_on_connection_error():
    client = MagicMock()
    client.pubsub = MagicMock(side_effect=ConnectionError("redis down"))
    bus = HivemindRedis(client=client)
    res = await bus.subscribe("live", timeout=0.1)
    assert res["status"] == "unavailable"
    assert res["messages"] == []


def test_singleton_getter():
    assert isinstance(get_hivemind_redis(), HivemindRedis)
