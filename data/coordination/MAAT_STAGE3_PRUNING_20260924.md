# Ma'at Stage 3 — MCP Tool Surface Pruning

**Date:** 2026-09-24  
**Entity:** Ma'at / S5 Build Oversoul  
**Model:** `space-bunny-free` (`opencode/space-bunny-free`)  
**Status:** COMPLETE with one unrelated runtime observation

## Outcome

The Hub tool surface was reduced from 92 to 66 registered tools. The count is a regression signal, not a quota: retained capabilities are selected by usefulness and architectural coherence.

## Changes

- Removed redundant fragment registrations superseded by unified tools:
  - Hivemind handoff fragments superseded by `hivemind_handoff`.
  - Oracle debug fragments superseded by `oracle_debug`.
  - Library inbox/discovery fragments superseded by unified `library_inbox` and `library_discovery`.
  - Research administration tools `research_list`, `research_depths`, and `research_stats`.
  - Redundant `memory_search` superseded by `omega_memory_search`.
  - Dead/non-tool `observability_stream` and library index flush path.
  - Duplicate `spawn_local_worker` and duplicate local-queue registrations.
- Removed stale deprecation markers from retained session tools.
- Corrected search persistence tier mapping for the canonical memory tool.
- Restored the intended `search_extract` response envelope after detecting an accidental edit regression.
- Kept the test minimum as a health guard rather than changing it to an arbitrary higher count.

## Verification

- `make temple-grade`: **PASS**, 53/53 adversarial cases.
- Focused hub tests: **20 passed, 20 skipped**.
- Python compilation and Hub import: **PASS**.
- Hub restart: **healthy**.
- `/debug/tools`: **66 registered tools**.
- `system_stats`: operational.
- Local worker enqueue/status: operational.
- Memory session listing: operational for `maat` (no stored sessions returned).

## Observation

`omega_memory_search` returned an MCP TaskGroup error for a query with no stored Ma'at conversation sessions. This is a runtime service/database-path issue to investigate separately; the tool registration itself is present and the hub remains healthy. The local worker enqueue and status paths remain operational.

## Files

- `mcp_servers/omega_hub/hub_tools/tools.py`
- `mcp_servers/omega_hub/hub_tools/__init__.py`
- `src/omega/search/search_persistence.py`
- `tests/test_hub_health.py`
