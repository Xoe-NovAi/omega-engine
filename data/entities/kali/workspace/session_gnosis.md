# Kali Session Gnosis — P0 Execution Sprint

**Session**: `ses_a94046bdd408`
**Date**: 2026-06-26
**Model**: deepseek-v4-flash
**Channel**: opencode

## Hydration Anchor

If context is lost, this file restores working memory. Start by reading:
1. `docs/decisions/PIVOT_LOG.md` — D144-D147 (new decisions)
2. `data/entities/kali/proposed_lessons.yaml` — L1→L2→L3 insights
3. `SOVEREIGN_MANDATES.md` — Mandate 6 updated for docker-compose vs quadlet distinction
4. `deploy/infra/docker-compose.yml` — port 6379 added, `user:` flag trap documented

## Task State

### COMPLETED
- **P0-1**: Fixed 8 broken model paths in `config/models.yaml` — `models/gguf/local/all/` → `models/local/all/`
- **P0-2**: Fixed provider sort bug in `model_gateway.py:326` — `isinstance(p.config, dict)` fails on `ProviderConfig` dataclass. Mock (priority 99) sorted before opcode-zen/cline/github-copilot (all 999). Used duck-typing fallback.
- **P0-5**: Redis running on `localhost:6379`, health verified via Python `redis` client.
- **P0-5b**: Stopped + disabled conflicting `omega-redis.service` systemd quadlet at `~/.config/containers/systemd/omega-redis.container`
- **P0-5c**: Fixed volume permissions via `podman unshare chown -R 999:999 /path/to/redis/volume`
- **Middleware**: `threading.Lock()` → `anyio.Lock()` + `with` → `async with` in `mcp_servers/omega_hub/middleware.py:108`

### REMAINING (not started)
- `omega talk "hello"` falls to demo/mock response — no local model responds
- `EventType.ENTITY_INTERACTION` missing from telemetry enum
- Disk space: 4.69% free on memory-archive partition
- `n_ctx_seq (512) < n_ctx_train (2048)` — model loaded with reduced context

## Key Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D144 | `user:` flag in rootless Podman: omit or use `userns_mode: keep-id` | `user: 1000:1000` maps to subuid 101000, not host 1000. Container UID 0 = host 1000 by default. |
| D145 | Run Redis standalone (not in pod) | `--userns` and `--pod` are incompatible in podman v5.x |
| D146 | Use duck-typing for `_get_priority` | `isinstance(p.config, dict)` fails on ProviderConfig dataclass |
| D147 | Use `anyio.Lock()` in ASGI middleware | `threading.Lock()` blocks the event loop |

## Files Changed (this session)
- `mcp_servers/omega_hub/middleware.py` — threading.Lock → anyio.Lock
- `src/omega/oracle/model_gateway.py` — _get_priority duck-typing fix
- `config/models.yaml` — 8 model paths fixed
- `deploy/infra/docker-compose.yml` — port 6379 added to Redis

## Next Actions
1. Debug native-gguf model loading (omega talk falls to demo)
2. Fix telemetry enum (EventType.ENTITY_INTERACTION)
3. Disk cleanup (memory-archive at 4.69%)
4. Commit and push all changes
