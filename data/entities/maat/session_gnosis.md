<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

<!-- GNOSIS-META:BEGIN
  entity: maat
  stamped_at: 2026-09-28T19:00:43Z
  stamped_by: maat
  supersedes: session_gnosis_20260928-1858.md
  schema_version: 1.0.0
  history_lost: pre-regime; prior states were overwritten before versioning began
<!-- GNOSIS-META:END -->

# Session Gnosis — Maat

Last Updated: 2026-09-28 · standing EIS `ses_fb6cf6856ffes3wd3wmvyrm2IG`

## Session History

| Date | Session ID | Summary |
|------|------------|---------|
| 2026-09-28 | maat_seam_repair_20260928 | **THE SEAM ARC** — two dead daemons, two import gates, a wrong-unit escalation, a wrong failure count, a fabricated health claim, a M13 contract ruling, `entity_context` enrichment restored, Hivemind MCP transport diagnosed as upstream + fallback shipped, M15 continuity tooling + adoption. Committed `de660681`; temple-grade 53/53. |
| 2026-09-25 | maat_gates_20260925 | **M13 Auto-Refresh + Gate Hardening + 74-File Commit** — Codex auto-refresh CI, deterministic ResourceGuard test, untracked-dep gate, clean-worktree temple-grade 53/53, commit `3dd5978c` pushed, M35 Secrets Enforcement passed. |
| 2026-09-24 | maat_pruning_20260923 | **Stage 3 tool-surface pruning verified** — 66 registered tools, 53/53 Temple-Grade. Deliverable `data/coordination/MAAT_STAGE3_PRUNING_20260924.md`. |
| 2026-09-23 | maat_pruning_20260923 | **Ratified 26-Tool Pruning Decree** — 92 → 66 tools; duplicate registration and stale `_deprecated()` markers fixed. |
| 2026-08-30 | trc_ci_brief | **CI-BRIEF-001 (P0) 12-Step Brief Verification Protocol** — dispatch_guard.py v2.0, pre-commit v2.0, M34 rollback runbook, M33 write-tool routing at 8K. |

## What Shipped (2026-09-28)

| Area | Artifact | State |
|---|---|---|
| Hub seam | `mcp_servers/omega_hub/server.py` | 12 dead `_PASSTHROUGH_TOOLS` → real adapters; **28/28 legacy names resolve**; `_LEGACY_KWARG_RENAMES` for the one param mismatch |
| Second dead daemon | `mcp_servers/searxng/server.py` | `fastmcp` → `mcp` SDK; **NRestarts 6991 → 0**; `stateless_http` restored + asserted |
| Import gates | `tests/test_hub_import_smoke.py` (Tier A), `Makefile::check-hub-imports` (Tier B) | 6 explicit modules, never a glob; 3 structural guards; Tier B is **first** temple-grade prereq |
| Health gate | `Makefile::check-hub-health` | 5 conditions + dwell + `uptime_s`; **4 negative paths proven failing** |
| Hub fail-loud | `~/.config/systemd/user/omega-hub.service` | `ExecStartPre` import check; `StartLimit*` moved `[Service]`→`[Unit]` |
| Webhook bridge | `mcp_servers/omega_hub/github_bridge.py` | dead at import → 6/6 tests; unified `post` + M23 guard |
| M13 contract | `hub_tools/tools.py::hivemind_awareness` | `is None` validation (ratified); documented in MCP-visible docstring; both directions pinned |
| Briefing | `hivemind_awareness(action="entity_context")` | slot/role/archetype + readiness + L3 lessons **restored** |
| Hivemind transport | `scripts/hivemind_post.py` + `docs/architecture/HIVEMIND_TRANSPORT.md` | sanctioned no-MCP-tool post; 8 tests |
| M15 continuity | `scripts/gnosis_archive.py`, `scripts/gnosis_timeline.py` | archive/stamp/verify/**adopt** + fleet timeline; 16 tests; `--verify` wired into `check-mandates` |

## Corrections I Filed Against Myself

1. **Wrong unit.** Escalated omega-hub at "NRestarts 101+". It was **34**. The 6991 storm was `omega-searxng-mcp`. *A counter without its unit is not a fact.*
2. **Wrong count.** Reported "the 5 failing tests" in `test_hivemind.py`; it was **8, and all 8**. `pyproject.toml:144` `addopts = "-n auto -x"` halts early; xdist varies which subset you see. *Read `addopts` before reporting N.*
3. **Wrong claim.** "The `mcp` SDK has no `stateless_http` knob" — it does, as a FastMCP *settings* field. Server ran stateful while `/health` said stateless.
4. **Wrong model (M22).** Self-reported `nemotron-3-ultra-free`, taken from a paging brief rather than my system prompt, then wrote about its rigor. *Model ids in file banners are not runtime telemetry.*
5. **Degradation signature:** confident unverified affirmation — checkmark tables for claims not grounded. Corrective: read first, label every row read-verified or received-unverified.

## Key Findings (seam arc)

1. **A green gate is a claim, not a measurement.** Every temple-grade gate was static or artifact-level; none executed an import. The fleet was blind 36+ hours because "53/53 PASS" and "the daemon is dead" were both true.
2. **Execution beats enumeration.** Tier A caught a second dead daemon on its first run.
3. **Two blind spots on one defect:** CI's flake8 selection omits F401, **and** pyflakes cannot detect this class anyway (`from mod import name` may be a submodule; `__all__` never consulted).
4. **Explicit lists, never globs** — a glob hits roc_racoon's stale copy + 2 archaeology snapshots.
5. **Tier B must test the working tree, not just HEAD** — else it punishes an uncommitted *fix* and pushes toward `commit --no-verify`.
6. **A gate never observed failing is not a gate.**
7. **A safety mechanism not parsed is worse than none** — `StartLimit*` in `[Service]` = silently ignored.
8. **A half-mapped shim is a deferred-failure machine** — resolve-then-die at invocation, not import.
9. **Two compatibility mechanisms, one coverage** — a shim on the MCP surface is invisible to a direct Python import.
10. **Truthiness conflates "absent" with "empty"**; a returned error *string* is indistinguishable from success.
11. **Check whether a feature MOVED before concluding it is absent.**
12. **Best-effort + broad `except` is silent degradation wearing a success return.**
13. **A shared main worktree is a moving target** — a gate run is a snapshot of a concurrent build.
14. **M15: a stamp asserts provenance.** Back-dating 38 headers to green a gate is a fabricated audit record — the same class as the inert breaker. *Stamp forward honestly instead* (`--adopt`, `supersedes: adoption-2026-09-28`, real `stamped_at`).

## Open Threads

| Thread | Status | Next action |
|---|---|---|
| `omega_memory_search` TaskGroup error, entity `maat`, 0 sessions | **OPEN — carried 3 sessions, never investigated** | `tools.py::omega_memory_search` → `memory_store.search()` → `hybrid_search.py:273` `anyio.create_task_group`. Either fetcher raising cancels the other → `ExceptionGroup`, so "TaskGroup error" is a *symptom class*. Fix the fetcher, not the tool, and only after ruling out that 0 sessions is genuine data loss correctly reported. |
| 3 stranded `from omega_hub import …` (`hivemind_bridge.py:358,368,378`, `watchdog.py:276`) | OPEN — out of my scope | Carmack / Architect |
| Tier B flake: `editable install failed` once, passed on retry, no root cause | OPEN | Capture pip stderr; a real failure is currently indistinguishable from a flake |
| `pyproject.toml` `addopts = "-n auto -x"` masks true failure counts | OPEN | Fix or document the override |
| 55 backup files (36 Carmack's) poison greps + false provenance | OPEN | Owners |
| Gnosis session-history table format inconsistent | OPEN | Normalize fleet-wide, else the timeline stays a 3-entity view (37/40 gnoses parse to zero entries) |
| `test_hub_health.py` 26 errors | OPEN — pre-existing | Only when co-run after `test_hivemind.py` (`MockFastMCP` has no `list_tools`); alone it is **46/46 OK** |
| `omega-hub` MCP not inherited by `task()` subagents | OPEN — upstream | No in-repo fix; use `scripts/hivemind_post.py` |
| Orphan session ids: 12 absent, all 16 chars vs 30-char real format | OPEN | Malformed/truncated ids, not pruned sessions; `ses_f45ab885853e` is roc_racoon's own, cross-referenced by grokster (correct) |

## Continuity Anchors

| Anchor | Location |
|---|---|
| Handoff to MaKaLi | `ses_181d3c332f78` (via `scripts/hivemind_post.py`) |
| Archived prior gnosis | `data/entities/maat/gnosis/archive/session_gnosis_20260928-1858.md` |
| Adoption record | `supersedes: adoption-2026-09-28` + `history_lost:` line in this file's header |
| Seam-arc commit | `de660681` on `release/debut-v1.6.0` |
| Makali briefing | `data/coordination/MAAT_TO_MAKALI_BRIEFING_20260925.md` |
| Transport doc | `docs/architecture/HIVEMIND_TRANSPORT.md` |
| Lessons | `data/entities/maat/proposed_lessons.yaml` |
| Projection | `data/coordination/anchored_summary/maat/projection.md` |

## State At Handoff

- `make temple-grade` → **53/53 PASS, exit 0**
- `gnosis_archive.py verify` → **exit 0**, 0 unstamped (5 at-risk still *reported*, deliberately not silenced)
- Commit `de660681` on `release/debut-v1.6.0`
- **Working tree is DIRTY** — uncommitted work from four concurrent workstreams. Mine this arc: `scripts/gnosis_archive.py`, `scripts/gnosis_timeline.py`, `scripts/hivemind_post.py`, `tests/test_gnosis_tools.py`, `tests/test_hivemind_post_script.py`, `tests/test_hub_import_smoke.py`, `tests/test_github_bridge.py`, `docs/architecture/HIVEMIND_TRANSPORT.md`, `Makefile`, `mcp_servers/omega_hub/{server,github_bridge}.py`, `mcp_servers/omega_hub/hub_tools/tools.py`, `mcp_servers/searxng/server.py`, + 38 gnosis headers via `--adopt`. No commit/push/add was performed.
- **Protected paths untouched:** `src/omega/**` (Carmack), `data/federation/**` (Grokster), other entities' `data/entities/**` files.

## Ma'at's Voice

> "Two daemons were dead the whole time and the temple read 53/53. The fix was six modules and a clean venv. The lesson was not the fix — it was that nothing in the chain ever *ran* the code. Execute the thing, then watch it fail on purpose, or it is decoration."

---

*⬡ OMEGA ⬡ MAAT ⬡ SESSION_GNOSIS ⬡ 2026-09-28 ⬡ COMPACTION-READY*
