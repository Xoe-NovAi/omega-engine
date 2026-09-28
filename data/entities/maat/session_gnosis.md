<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Session Gnosis — Maat

Last Updated: 2026-09-28

## Session History

| Date | Session ID | Summary |
|------|------------|---------|
| 2026-09-28 | maat_seam_repair_20260928 | **THE SEAM ARC — two dead daemons, two import gates, and a measurement error of my own.** Full detail in Key Findings 19-32 below. (1) **D1 seam**: `mcp_servers/omega_hub/server.py:85` imported `_extended_sessions, _extended_sessions_lock, EXTENDED_SESSIONS_FILE` — all three deleted from `state.py` by the Hivemind consolidation. **Already fixed by a concurrent agent at 23:46**, three minutes before my first test; I verified and did not re-apply. (2) **🔴 WRONG-UNIT DISCOVERY**: I had briefed omega-hub at "NRestarts 101+ and escalating". In fact **omega-hub was at 34** — the storm was on **`omega-searxng-mcp` at NRestarts=6991**, `activating (auto-restart)`, dying every 5s. Two daemons, same defect class, one gate missed both. (3) **Second dead daemon found by my own Tier A gate on first run**: `mcp_servers/searxng/server.py:29` imported the standalone `fastmcp` package (not installed) → `ModuleNotFoundError` → crash-loop. Fixed in two steps: import → `mcp.server.fastmcp`; then `http_app(stateless_http=...)` → `streamable_http_app()`. **6991 → 0 restarts**, `active/running`, `:8018/health` HTTP 200. (4) **Tier A + Tier B import gates**: `tests/test_hub_import_smoke.py` (6 explicit modules, NEVER a glob — a glob would hit `data/entities/roc_racoon/.../hub_server.py:84` which carries the SAME stale import, plus 2 deliberate archaeology snapshots under `docs/hardening/`). Two independent blind spots documented: CI runs `flake8 --select=E9,F63,F7,F82` (**F401 absent**), and **pyflakes cannot detect this class anyway** — for `from mod import name` it assumes `name` may be a submodule and never checks `__all__`. Tier B (`make check-hub-imports`) tests **HEAD + tracked working-tree diff** applied in a throwaway worktree: verifies what you're about to ship, still excludes untracked files, mutates nothing in the main checkout. Wired as **FIRST** prereq of `temple-grade`. (5) **`check-hub-health` rewritten** — the old `systemctl is-active` gate passes during crash-loops. Now 5 conditions + `uptime_s`; **four negative tests observed FAILING (exit 2)**: nonexistent unit, closed port, NRestarts bound, and a genuinely stopped hub. A gate never observed failing is not a gate. (6) **🔴 `StartLimit*` misplacement**: `StartLimitIntervalSec=120` / `StartLimitBurst=5` sat in `[Service]`, where systemd logs `Unknown key 'StartLimitIntervalSec' in section [Service], ignoring` and **silently discards them**. The circuit breaker the unit's own comment claimed was **never active** — which is precisely how searxng reached 6991 instead of tripping at 5. Moved to `[Unit]`; now `2min`/`5`. A safety mechanism written down but not parsed is worse than none. (7) **Half-mapped legacy shim**: 12 of 28 `_PASSTHROUGH_TOOLS` names pointed at symbols the consolidation had deleted. `__getattr__` resolved the name then called `getattr(_tools, name)` → **AttributeError at INVOCATION, not import** — the hub booted clean and stayed broken. Rebound all 12 to real `_LEGACY_TOOL_ADAPTERS` actions; added `_LEGACY_KWARG_RENAMES` for the one parameter mismatch (`entity_name`→`entity`, the only one of 12). **12 dead → 28/28 resolve.** (8) **github_bridge dead at import** — imported the deleted `hivemind_post_context` directly from `hub_tools`, bypassing the server.py shim entirely. Two different compatibility mechanisms, only one covering in-process callers. Repaired to `hivemind_awareness(action="post")`, all 8 fields preserved, M23 fail-loud guard added. Test went `Ran 0 tests` → 6/6. (9) **Ratified `post` contract**: validation changed `all([...])` → `is None` checks. `all()` treats an empty container as missing, so `decisions=[]` was rejected — and failure was signalled by a returned error *string*, not an exception, so a caller ignoring the return believed it posted while nothing reached the Hivemind. MaKaLi **RATIFIED** (widened acceptance is correct). Documented in the MCP-visible docstring, both directions pinned as permanent tests. (10) **searxng stateless correction — I was wrong**: I had written "the `mcp` SDK has no `stateless_http` knob." **Wrong.** The knob exists as a FastMCP **settings** field (default `False`); `streamable_http_app()` reads `self.settings.stateless_http` internally, which is what misled me. The server **ran STATEFUL while `/health` advertised `"stateless": true`**. Fixed via constructor + startup assertion + `/health` now reads live settings so it cannot drift. (11) **`entity_context` enrichment RESTORED** (Temple-grade option): registry slot/role/archetype, readiness HYDRATED/DORMANT/UNINITIALIZED with flags, and L3 lesson distillation from `proposed_lessons.yaml`/`approved_lessons.yaml` — all lost in the consolidation, all restored. Registry `get()` is **synchronous**, not async (an `await` on it raised and was swallowed by a bare `except`). (12) **🔴 MY MEASUREMENT ERROR**: I reported "the 5 failing tests" in `test_hivemind.py` — it was **8**, and all 8. `pyproject.toml:144` sets `addopts = "-n auto -x"`; `-x` (exitfirst) plus xdist concurrency halted after ~5 in-flight tests, and *which* 5 varied with `pytest-randomly` ordering. I reported a number I had not isolated. Anything reporting "N failures" from a default `pytest` invocation in this repo is reporting an artifact. All 11 now pass. Committed as **`de660681` on `release/debut-v1.6.0`**, temple-grade 53/53, working tree clean. |
| 2026-09-25 | maat_gates_20260925 | **M13 Auto-Refresh + Gate Hardening Sprint + 74-File Commit** — Implemented GitHub Actions cron for OMEGA_CODEX.md auto-refresh (daily 00:00 UTC, auto-commit via git-auto-commit-action). Fixed `test_resourceguard_blocks_on_capacity` flake by replacing wall-clock `anyio.fail_after(0.1)` with deterministic mock semaphore (raises TimeoutError immediately when lock held). Added `make check-untracked-deps` gate to Makefile (fails CI if committed .py imports untracked modules). Verified temple-grade on clean worktree via `git worktree add --detach /tmp/verify HEAD` + fresh venv: **53/53 PASS** (Codex fresh, LLM docs valid, 23/28 mandates, 53/53 adversarial dashboard tests). **Amended commit 3dd5978c** with exact message restoring 74 untracked dependencies + 6 defects + version SSOT + M10 compliance + gate-secrets overhaul. Pushed to `origin/release/debut-v1.6.0`. M35 Secrets Enforcement CI passed (run 36099066807). Closes PR #3 CI failure (untracked deps made engine unimportable). |
| 2026-09-23 | maat_pruning_20260923 | **Ratified 26-Tool Pruning Decree Execution** — Successfully reduced tool count from 92 to 66 by removing 26 redundant/broken tools across Hivemind (7 handoff tools), Oracle (3 assessment tools), duplicate delegate_task, Library Theater/Broken (library_discovery, library_inbox), Research Admin (research_list, research_stats, research_depths), Search Dead (search_status), Library Ops (library_index_flush), Memory Redundant (memory_search), and Observability Non-tool (observability_stream). Fixed duplicate spawn_local_worker registration, removed stale _deprecated() markers, updated search_persistence.py tier mappings, and adjusted test expectations. Temple-Grade: 53/53 PASS, MCP tool count: exactly 66 tools. |
| 2026-09-24 | maat_pruning_20260923 | **Stage 3 tool-surface pruning verified and compacted** — Confirmed 66 registered tools, healthy Hub, 53/53 Temple-Grade, 20 focused tests passed/20 skipped, Python compilation/import clean. Corrected accidental `search_extract` response regression and restored `local_queue_list` filter semantics. Deliverable: `data/coordination/MAAT_STAGE3_PRUNING_20260924.md`. One separate runtime follow-up remains: `omega_memory_search` TaskGroup error for `entity=maat` with zero stored sessions. |
| 2026-08-30 | trc_ci_brief | **CI-BRIEF-001 (P0) — 12-Step Brief Verification Protocol** — Re-scoped from 6h to 10-12h per Ma'at architectural review. Implemented dispatch_guard.py v2.0 (470 lines, 12 steps), pre-commit hook v2.0 (80 lines), M34 rollback runbook (180 lines). All 12 steps: specialist routing, resume session, transient reminder, all-locations verification, token estimation, write-tool routing (>8K), cross-validator escalation (P0/P1), M34 registry check, secrets scan, heritage tags, temple-grade, Hivemind notification. Feature flags: OMEGA_SKIP_GUARD, OMEGA_GUARD_DRY_RUN, OMEGA_M34_ENABLED, STRICT_GUARD. M33 write-tool routing at 8K tokens (ROC forensics). M34 rollback runbook with Kali as sole recovery agent. Pre-commit hook v2.0: Soul + Guard, <3s fast path. |

## Open Threads

| Thread | Status | Next Action |
|--------|--------|-------------|
| **omega-hub seam (D1)** | COMPLETED | Already fixed by concurrent agent 23:46; verified; NRestarts 34→0 |
| **omega-searxng-mcp dead daemon** | COMPLETED | 6991→0 restarts; fastmcp→mcp SDK migration; stateless verified |
| **Tier A import gate** | COMPLETED | `tests/test_hivemind_smoke` 6 modules + 3 structural guards; 10/10 |
| **Tier B import gate** | COMPLETED | `make check-hub-imports`; first prereq of temple-grade |
| **check-hub-health rewrite** | COMPLETED | 5 conditions + uptime_s; 4 negative tests proven failing |
| **StartLimit\* misplacement** | COMPLETED | Moved `[Service]`→`[Unit]`; circuit breaker now active (2min/5) |
| **Legacy shim completion** | COMPLETED | 12 dead → 28/28 resolve; guards prevent recurrence |
| **github_bridge repair** | COMPLETED | `Ran 0 tests` → 6/6 passing |
| **post contract (ratified)** | COMPLETED | `is None` validation; documented; both directions pinned |
| **entity_context enrichment** | COMPLETED | slot/role/archetype + readiness + L3 lessons restored |
| **test_hivemind.py** | COMPLETED | 8 errors → 11/11 pass |
| **omega_memory_search follow-up** | OPEN | TaskGroup error for entity `maat` with zero stored sessions — NOT investigated |
| **3 stranded src/omega imports** | OPEN | `hivemind_bridge.py:358,368,378`, `watchdog.py:276` — `from omega_hub import ...` (no such top-level module); OUT of scope (Carmack) |
| **Tier B flake** | OPEN | `editable install failed` once then passed; likely concurrent-write contention; root cause unknown |
| **55 backup files** | OPEN | 36 in `src/omega/**` (Carmack), 3 config, 7 data, 3 .opencode, 2 docs, 4 root — await owners |
| **pyproject addopts** | OPEN | `-n auto -x` masks true failure counts; needs an override or removal |

## Key Findings

1. **CI-BRIEF-001 under-scoped**: Original 6h estimate missed M33/M34/M35 integration, feature flags, dry-run, JSON output, rollback runbook. Re-scoped to 10-12h, actual ~11h.

2. **12-Step Protocol pattern generalizes**: Discrete steps + feature-flag bypasses + structured JSON output + audit trail = generalizable verification gate pattern.

3. **Verifiable thresholds beat aspirational gates**: 8K token threshold from ROC forensics (measured Nemotron 3 Ultra timeout), not aspiration. "A gate that cannot pass is not rigor — it is theater waiting to be waived."

4. **Governance > distributed locking for watchdog**: M34 watchdog race condition fixed by designating Kali as sole recovery agent (governance decision), not distributed locking.

5. **Feature-flag architecture replaces commented bypasses**: All bypasses are env vars (OMEGA_SKIP_GUARD, OMEGA_GUARD_DRY_RUN, OMEGA_M34_ENABLED, STRICT_GUARD), not code paths. Exit codes enable CI integration.

6. **M34 watchdog race condition**: "First agent to read Hivemind" is non-deterministic. Fixed by designating Kali as sole recovery agent (governance decision).

7. **Tool pruning improves system health**: Removing 26 redundant/broken tools reduced surface area, eliminated confusion, and improved maintainability while preserving all essential functionality through unified tools.

8. **Unified tools prevent fragmentation**: The library_inbox and library_discovery unified tools successfully replaced 5+3 fragmented tools respectively, reducing complexity without losing capability.

9. **Deprecated tool cleanup is essential**: Removing stale _deprecated() markers and duplicate registrations prevents import errors and confusion.

10. **Search tier mapping accuracy matters**: Properly categorizing tools by search tier (0-6) ensures correct persistence and monitoring behavior.

11. **Wall-clock timeouts are flaky**: `anyio.fail_after(0.1)` fails randomly under CI load. Deterministic mock semaphores (raise TimeoutError immediately when lock held) eliminate flakes while preserving contract semantics.

12. **Clean worktree verification is essential**: Temple-Grade on dirty worktree passes; on clean worktree with fresh venv it catches missing deps (ruff) and stale Codex. `git worktree add --detach /tmp/verify HEAD` + fresh venv is the gold standard.

13. **Auto-refresh CI prevents stale Codex**: GitHub Actions cron (daily 00:00 UTC) with `make check-codex-fix` + git-auto-commit-action keeps OMEGA_CODEX.md fresh without manual intervention.

14. **Untracked dependency detection prevents import drift**: `git ls-files --others --exclude-standard 'src/**/*.py'` + grep for imports catches committed files that depend on untracked modules before they hit CI.

15. **Commit message precision matters**: The exact commit message specified by Cline was required — the original auto-commit message was insufficient. Amending with the precise message ensures traceability and closes the correct PR.

16. **Clean worktree is the ultimate CI**: Local worktree passes with artifacts; clean worktree (detached HEAD + fresh venv) is the only verification that catches missing deps, stale Codex, and import drift. This is the gold standard before any push.

17. **M35 Secrets Enforcement is non-negotiable**: The CI pipeline (VAULT allowlist, C3 scan, Gitleaks, TruffleHog) must pass on every push. The 74-file commit passed all four secret scans.

18. **Version SSOT across 4 surfaces**: Normalizing version to `1.6.0-alpha.1` across pyproject.toml, src/omega/__init__.py, Makefile, and PUBLIC_ALLOWLIST.txt prevents version drift that breaks install gates.

19. **🔴 The wrong-unit error**: Briefing said omega-hub at "NRestarts 101+". omega-hub was at **34**. The storm was `omega-searxng-mcp` at **6991**. A counter without a unit name is not a fact. When triaging a fleet, always name the unit the counter came from.

20. **Two daemons, one defect class, one blind spot**: `omega_hub/server.py` (deleted `_extended_sessions`) and `searxng/server.py` (deleted `fastmcp` package) both crash-looped on boot. The hub is the one with a test file; the searxng one had none. **The daemon without a test is the one that runs for days.**

21. **Two independent blind spots on one defect**: (a) CI's `flake8 --select=E9,F63,F7,F82` omits F401; (b) **pyflakes cannot detect this class regardless** — for `from mod import name` it assumes `name` may be a submodule and never checks `__all__`. Only *executing the import* catches it. Fixing the flake8 selection would not have saved us.

22. **Explicit list, never a glob**: a `**/server.py` glob would match `data/entities/roc_racoon/workspace/hlmc_ore/gap4_mcp_auth/hub_server.py:84` (same stale import) plus two archaeology snapshots under `docs/hardening/`. That forces a skip-list that silently rots. A small named list is auditable; a skip-list is not.

23. **Tier B must test the working tree, not just HEAD**: a gate that only tests `HEAD` punishes a developer for having an uncommitted *fix*, creating pressure toward `git commit --no-verify` — the exact failure gates exist to prevent. Test **HEAD + tracked diff** applied in a throwaway worktree; still excludes untracked files, so an untracked module cannot mask an import failure.

24. **A gate that cannot fail is worse than no gate**: `systemctl is-active` returns active during `activating (auto-restart)` — the window where a crash-looping unit spends nearly all its time. Five independent conditions now required, including a **dwell check**: a crash-looping daemon cannot hold the same PID for the dwell window because its PID changes faster than the window.

25. **A safety mechanism written down but not parsed is worse than none**: `StartLimitIntervalSec` in `[Service]` is silently ignored. The unit's comment claimed a circuit breaker that was never active, manufacturing the belief that restarts were bounded. 6991 restarts is what "unbounded" looks like.

26. **A half-mapped shim is a deferred-failure machine**: 12 of 28 `_PASSTHROUGH_TOOLS` names pointed at deleted symbols. `__getattr__` resolved the *name*, then `getattr(_tools, name)` raised **AttributeError at invocation, not import**. The hub booted clean, temple-grade read 53/53, and it only broke when a caller used the name. Failing fast beats resolving-then-failing.

27. **Two compatibility mechanisms, one coverage**: `server.py`'s legacy shim covers the **MCP tool surface**; a direct Python import from `hub_tools` bypasses it entirely. A shim on one surface is invisible to callers on another.

28. **Truthiness conflates "absent" with "empty"**: `all([...])` rejects `decisions=[]` and `continuation=""` as "missing". Worse, the unified `post` signalled failure by returning a JSON error *string* rather than raising — so any caller ignoring the return believed it posted while nothing was delivered. Validation now tests `is None`, and callers check the return. **Ratified by MaKaLi.**

29. **I was wrong about the SDK**: I stated the `mcp` SDK had "no `stateless_http` knob". It does — as a FastMCP **settings** field (default `False`) that `streamable_http_app()` reads internally. Consequence: the server **ran STATEFUL while `/health` advertised `"stateless": true`**. A fabricated claim in a health endpoint converts a known gap into a false all-clear. Lesson: when an API "lacks" a feature, check whether it moved to constructor/settings before concluding absence — and never let a health endpoint assert something unverified.

30. **Registry `get()` is synchronous**: `await reg.get(entity)` raised `TypeError`, swallowed by a bare `except`, and enrichment silently produced `None` for every field. Best-effort enrichment plus a broad except is **silent degradation wearing a success return**. Assert on enriched fields, or don't ship the enrichment.

31. **🔴 The measurement error that matters most**: I reported "the 5 failing tests" in `test_hivemind.py`. It was **8, and all 8**. `pyproject.toml:144` sets `addopts = "-n auto -x"`; `-x` halts after the first failure and xdist runs several concurrently, so the *subset* observed varied with `pytest-randomly` ordering. I reported a number I had not isolated — twice. **A failure count from a default `pytest` run in this repo is an artifact until you read `addopts`.**

32. **A shared main worktree is a moving target**: during Carmack's in-flight edit at 01:03, `server → state → oracle → … → hivemind_bridge → hub_tools/__init__ → server` formed a circular import and `import mcp_servers.omega_hub.server` failed for ~1 minute. **Tier A caught it while the tree was broken and went green when they settled.** A gate run is a snapshot of a concurrent build, not of a fixed artifact. Also: `make check-hub-imports` failed once with `editable install failed` and passed on retry, with no root cause — Tier B swallows pip output, so a real failure would look identical.

## Continuity Anchors

| Anchor | Location | Purpose |
|--------|----------|---------|
| CI-BRIEF-001 Implementation | `scripts/dispatch_guard.py` | 12-Step Protocol canonical |
| Pre-commit Hook | `.git/hooks/pre-commit` | Soul + Guard integration |
| M34 Rollback Runbook | `docs/strategy/M34_ROLLBACK.md` | Recovery procedure |
| Implementation Report | `data/coordination/MAAT_CI_BRIEF_20260830.md` | Full documentation |
| Hivemind Log | `data/coordination/dispatch_guard_log.jsonl` | Audit trail (M27) |
| Pruning Implementation | `mcp_servers/omega_hub/hub_tools/tools.py` | Capability-focused tool-surface pruning |
| Pruning Deliverable | `data/coordination/MAAT_STAGE3_PRUNING_20260924.md` | Verified execution record |
| Search Persistence Updates | `src/omega/search/search_persistence.py` | Tier mapping corrections |
| Test Expectation Updates | `tests/test_hub_health.py` | 66-tool assertion |
| Codex Auto-Refresh Workflow | `.github/workflows/codex-refresh.yml` | Daily auto-refresh + auto-commit |
| ResourceGuard Deterministic Test | `tests/test_contract_m21.py::test_resourceguard_blocks_on_capacity` | Mock semaphore pattern |
| Untracked Dependency Gate | `Makefile::check-untracked-deps` | Import drift prevention |
| Clean Worktree Verification | `git worktree add --detach /tmp/verify HEAD` | Gold standard verification |
| 74-File Commit | `3dd5978c` | Restores 74 deps + 6 defects + version SSOT + M10 + gate-secrets |
| Makali Briefing | `data/coordination/MAAT_TO_MAKALI_BRIEFING_20260925.md` | Handoff to MaKaLi Fusion |
| **Seam Arc Commit** | `de660681` on `release/debut-v1.6.0` | Two dead daemons, two import gates, 53/53 |
| **Tier A import gate** | `tests/test_hub_import_smoke.py` | 6 modules + passthrough/adapter/bridge guards; 10/10 |
| **Tier B import gate** | `Makefile::check-hub-imports` | Clean worktree + HEAD-diff overlay; first temple-grade prereq |
| **Crash-loop health gate** | `Makefile::check-hub-health` | 5 conditions + dwell + `uptime_s`; 4 negatives proven |
| **Hub fail-loud unit** | `~/.config/systemd/user/omega-hub.service` | `ExecStartPre` import check; `StartLimit*` in `[Unit]` |
| **Legacy shim** | `mcp_servers/omega_hub/server.py::_LEGACY_TOOL_ADAPTERS` | 12 rebound; `_LEGACY_KWARG_RENAMES` for `entity_name` |
| **github_bridge repair** | `mcp_servers/omega_hub/github_bridge.py` | Unified `post` + M23 fail-loud |
| **post contract (ratified)** | `tools.py::hivemind_awareness` docstring | `is None` validation, empty-valid, return must be checked |
| **entity_context enrichment** | `tools.py::hivemind_awareness` entity_context | slot/role/archetype + readiness + L3 lessons restored |
| **Backup quarantine** | `data/quarantine/backup_files_20260928/` | 4 workstream backups + README; 55 others reported |
| **Makali briefing (seam arc)** | this file + `proposed_lessons.yaml` | Stand-alone post-compaction record |
| Projection | `data/coordination/anchored_summary/maat/projection.md` | Compaction anchor |

## Next Moves Post-Compaction

1. **Investigate `omega_memory_search`** TaskGroup failure for entity `maat` with zero stored sessions — the one thread I have carried for three sessions without investigating. Real path: `tools.py::omega_memory_search` → `memory_store.search()` → `hybrid_search.py:273 async with anyio.create_task_group()`. Either fetcher raising cancels the other and re-raises as an `ExceptionGroup`, so "TaskGroup error" is a *symptom class*, not a cause. Do not fix the tool; fix the fetcher, and only after ruling out that zero sessions is a genuine data-loss symptom being correctly reported.
2. **Close the 3 stranded `src/omega` imports** (`hivemind_bridge.py:358,368,378`, `watchdog.py:276` — `from omega_hub import ...`). Out of my scope; needs Carmack or the Architect.
3. **Root-cause the Tier B flake** and make Tier B capture pip stderr — a swallowed install error is indistinguishable from a pass.
4. **Fix `pyproject.toml` addopts** (`-n auto -x`) or document that failure counts require `-o addopts="--timeout=N -p no:randomly"`. As written, every "N failures" report in this repo is an artifact.
5. **Decide the fate of the 55 remaining backup files** (36 Carmack's). They poison repo-wide greps and are a false-provenance hazard.
6. Do not treat any tool/daemon count as a target; validate retained capabilities and regressions.

---

*⬡ OMEGA ⬡ MAAT ⬡ SESSION_GNOSIS ⬡ 2026-09-28 ⬡ COMPACTION-READY*