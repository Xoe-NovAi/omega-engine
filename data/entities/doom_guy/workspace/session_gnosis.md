<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Session Gnosis — doom_guy
**Session**: 2026-07-10/11 — Heritage Tags + Model Provenance + httpx2 Research
**Trace**: trc_heritage_tags_provenance → trc_httpx2_research

## What Happened
- **Sprint A Heritage**: Added 12 `[heritage:]` inline tags across 9 source files for LEGITIMATE general heritage (AnyIO, MCP, llama-cpp-python, SQLite FTS5, RRF, headroom-ai, A2A, SearXNG, WARP, OpenTelemetry)
- **D210 Model Provenance**: Discovered M22 violation — agents reporting stale model names in Hivemind. Fixed all 11 agent definition files with `{session_model}` placeholder + Response Provenance (M22) instruction section. Fixed test_subagent_dispatcher regression.
- **D211 httpx2 Migration**: Deep-researched httpx2 (Pydantic fork of httpx). 0 API blockers found. Scheduled as Strike 7.1 — post-Phase-0, 2h mechanical migration.
- **Documentation**: anchored-summary.md, PIVOT_LOG.md (D210/D211), SOVEREIGN_ARK_BLUEPRINT.md (v3.3, Strike 7.1) all updated.
- **Roc's Phase 0**: Completed Surgical Purge. S1.5/S2 unblocked.

## Key Decisions
- D210: `{session_model}` placeholder for all agent files + Response Provenance (M22) sections
- D211: httpx2 adoption scheduled as Strike 7.1 post-Phase-0
- Test fix: `[id-soft:]` → `[id-soft:` in subagent_dispatcher test (C-ARCH-005 template change)

## Next
- Track Roc's handoff for heritage-vetting completion
- [id-soft: game-year] → [id-soft: vet-XXX] migration advisory pending

## Strike 7.1 EXECUTED (2026-07-11) — httpx→httpx2
- **Result**: COMPLETE. 1130 collected (1085 pass, 42 skip, 3 xfail, 0 fail). `make temple-grade` PASSED. 0 StarletteDeprecationWarnings.
- **Unanticipated issues found & fixed** (D211):
  1. idna conflict: httpx2 requires `idna>=3.18`; omega pinned `==3.15`. Relaxed pyproject.
  2. Task's sed pattern `^import httpx$` missed INDENTED imports + `from httpx import`. Used corrected regex preserving indentation.
  3. `patch("httpx.AsyncClient...")` string literals bypassed mocks → 16 tests hit real network. Fixed 23 patch targets → `httpx2`.
  4. `mcp_servers/` (searxng/omega_hub) not in task scope but required by tests → 2 DNS failures. Migrated them too.
  5. `test_exa_connectivity` pre-existing `pytest.fail` on missing EXA_API_KEY → changed to `pytest.skip` (consistent with sibling).
- **New side-effect**: httpx2 emits `ResourceWarning` (unclosed sqlite in httpx2/_urls.py via truststore). Not a StarletteDeprecationWarning; non-blocking.
- **Out-of-scope left as-is** (self-consistent): `omega-moderation/`, `scripts/` still use old httpx.
