# Redis Pub/Sub — Federation Heartbeat Config (2026-09-22)
**Document ID:** REDIS_FED_CONFIG_20260922
**Author:** Node 0 (MaKaLi Fusion)
**Status:** PROPOSED — requires Redis running on at least one node

---

## Purpose
Ephemeral Hivemind awareness over Redis Pub/Sub. Task-critical coordination stays file-based (M23 — never rely on Redis for durable state).

## Channels
| Channel | Purpose | TTL |
|---------|---------|-----|
| `heartbeat` | Node liveness signals | 20s |
| `live_feed` | Live-feed deltas | 20s |
| `awareness` | Ephemeral awareness broadcasts | 30s |

## Config (Node 0 — if Redis is local)
```bash
# /etc/redis/redis.conf (minimal)
bind 127.0.0.1 ::1
port 6379
protected-mode yes
maxmemory 64mb
maxmemory-policy allkeys-lru
```

## Config (Node 1 — client only)
No local Redis needed. Node 1's `hivemind_redis_publish`/`hivemind_redis_subscribe` tools connect to Node 0's Redis via Tailscale if `OMEGA_REDIS_HOST` is set:
```bash
# In Node 1's omega-hub service environment:
OMEGA_REDIS_HOST=100.123.51.67
OMEGA_REDIS_PORT=6379
```

## Degradation
If Redis is unavailable, tools return `{"status": "unavailable"}` — the file-based Hivemind remains the source of truth (M23 Failure Integrity).

## Verification
```bash
redis-cli ping  # → PONG
redis-cli publish heartbeat '{"node":"n0","ts":"..."}'
redis-cli subscribe heartbeat
```