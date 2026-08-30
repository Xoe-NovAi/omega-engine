# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Hivemind Redis Event Bus
# AP: AP-HIVEMIND-REDIS-v1.0.0
# ⬡ OMEGA ⬡ LILITH ⬡ hivemind_redis ⬡ P1-3
#
# Ephemeral awareness bus (heartbeats, live-feed deltas) over Redis Pub/Sub.
#
# [heritage: redis-py 2010] Pub/Sub transport.
# [heritage: jem-2026-gap5] Redis Streams for task-critical; Pub/Sub for
#   ephemeral ONLY. This module is the ephemeral layer. File-based Hivemind
#   (data/coordination/) remains the durable source of truth for task-critical
#   coordination and is the fallback when Redis is unavailable (M23: no
#   soft-failure — degraded mode is explicit, not silent).
#
# [M1: AnyIO] redis.asyncio runs inside the anyio event loop; no `import asyncio`.

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_REDIS_URL = "redis://localhost:6379/0"
_CHANNEL_PREFIX = "omega:hivemind:"


class HivemindRedis:
    """Thin, resilient Pub/Sub wrapper for ephemeral Hivemind awareness."""

    def __init__(self, redis_url: str = DEFAULT_REDIS_URL, client=None):
        self.redis_url = redis_url
        self._client = client
        self._owns_client = client is None

    @property
    def client(self):
        if self._client is None:
            import redis.asyncio as aioredis

            self._client = aioredis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def publish(self, channel: str, message: str, ttl: Optional[int] = None) -> Dict[str, Any]:
        """Publish an ephemeral message. Returns delivery count or graceful error.

        ttl is advisory metadata only (Pub/Sub has no native TTL); it is echoed
        back so subscribers can expire locally.
        """
        full_channel = f"{_CHANNEL_PREFIX}{channel}"
        try:
            delivered = await self.client.publish(full_channel, message)
            return {
                "status": "ok",
                "channel": full_channel,
                "delivered": int(delivered),
                "ttl": ttl,
            }
        except (ConnectionError, OSError, RuntimeError) as e:
            logger.warning("HivemindRedis.publish failed (degraded → file fallback): %s", e)
            return {"status": "unavailable", "channel": full_channel, "error": str(e)}

    async def subscribe(
        self,
        channel: str,
        timeout: float = 2.0,
        max_messages: int = 50,
    ) -> Dict[str, Any]:
        """Subscribe and collect messages for up to ``timeout`` seconds.

        Bounded listen — never blocks indefinitely (M23 Failure Integrity).
        Returns collected messages or a graceful unavailable status.
        """
        full_channel = f"{_CHANNEL_PREFIX}{channel}"
        try:
            pubsub = self.client.pubsub()
            await pubsub.subscribe(full_channel)
            messages: List[Dict[str, Any]] = []
            try:
                while len(messages) < max_messages:
                    msg = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=timeout
                    )
                    if msg is None:
                        break
                    data = msg.get("data")
                    messages.append({"channel": msg.get("channel"), "data": data})
            finally:
                await pubsub.unsubscribe(full_channel)
                await pubsub.close()
            return {"status": "ok", "channel": full_channel, "messages": messages}
        except (ConnectionError, OSError, RuntimeError) as e:
            logger.warning("HivemindRedis.subscribe failed (degraded → file fallback): %s", e)
            return {"status": "unavailable", "channel": full_channel, "error": str(e), "messages": []}

    async def close(self) -> None:
        if self._client is not None and self._owns_client:
            try:
                await self._client.aclose()
            except (ConnectionError, OSError, RuntimeError):
                pass
            self._client = None


# ── Module-level singleton (lazy) ──────────────────────────────────────
_bus: Optional[HivemindRedis] = None


def get_hivemind_redis() -> HivemindRedis:
    """Get or create the global HivemindRedis bus."""
    global _bus
    if _bus is None:
        _bus = HivemindRedis()
    return _bus
