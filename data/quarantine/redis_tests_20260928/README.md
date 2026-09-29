# redis_tests_20260928 — quarantined test file

Date: 2026-09-28 · Owner: doom_guy (S1)

## What was moved and why

`tests/test_hivemind_redis.py` → `test_hivemind_redis.py` (this directory).

The file was a contract test for `mcp_servers.omega_hub.hivemind_redis`, which
was **deleted in commit `2176e10d`** (pre-dating this session). The test module
did a hard top-level import of the deleted module:

```python
from mcp_servers.omega_hub.hivemind_redis import HivemindRedis, get_hivemind_redis
```

That raised `ModuleNotFoundError` during **collection**, which aborted the whole
pytest run before a single test executed — `Ran 0 tests`. One stale test file
was blinding the entire suite.

This is a test *for a module that no longer exists*. There is no code to fix;
the test itself is the obsolete artefact. It was moved rather than deleted per
standing order, and it can be restored if the Redis pub/sub surface is ever
reinstated.

## What was NOT moved, and why

`tests/test_hub_health.py` also references `hivemind_redis_publish` /
`hivemind_redis_subscribe` at lines 182-183, and it was left untouched because
those references are **correct**. They sit in a list named `RETIRED_HIVEMIND_TOOLS`
— an explicit *absence* assertion:

> "Kept as an explicit ABSENCE assertion: a name that was folded into another
> tool must not reappear, and its return to the surface would mean the shim and
> the real tool diverged."

Verified against the live MCP surface: `tools/list` on the hub at 127.0.0.1:8016
returns no redis/publish/subscribe tools, so the assertion holds and the test is
healthy. Editing it would have destroyed a useful regression guard.

## Verification

    .venv/bin/python -m pytest tests/ -q     # previously: ModuleNotFoundError, 0 tests

