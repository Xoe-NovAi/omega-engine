# 🔱 Session Gnosis — Researcher

**⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_xdist_deadlock ⬡ GNOSIS-DISTILLATION**

**Date**: 2026-06-29
**Task**: `XDIST_ASYNC_DEADLOCK_DEEP_DIVE` — Comprehensive investigation of pytest-xdist + asyncio deadlock for Omega Engine Wave 5

---

## L1 (Narrative) — What Happened

Investigated the pytest-xdist + asyncio deadlock issue blocking Wave 5 of the test hardening plan. Performed 8 searches across 4 search tools (WebSearch, WebFetch, SearXNG), scraping GitHub issues, official docs, PyPI pages, and production case studies. Analyzed Omega's 53 test files (581 test functions, 270 async) and 4 async fixtures. Found that the deadlock is actually two separate issues, both fixed in current toolchain versions (pytest-xdist 3.6.0+, pytest-asyncio 1.2.0+). Omega already has pytest-asyncio 1.4.0 (latest). Recommended per-file subprocess runner over xdist as the primary parallel execution strategy — eliminates 100% of asyncio deadlock risk, provides maximum isolation, and is proven in production at NousResearch.

Key data points discovered:
- Root cause: `RuntimeError: There is no current event loop in thread 'Dummy-1'` from execnet dispatching to non-main threads
- Fixed in pytest-xdist 3.6.0 (#1027) — `main_thread_only` execmodel guarantees main-thread execution
- Second fix needed: pytest-asyncio 1.2.0 (#1177) — event loop not disrupted by `asyncio.run()` in tests
- Omega's 4 async fixtures are all function-scoped — no loop_scope mismatch risk
- Omega's conftest.py has ZERO async fixtures — major xdist compatibility advantage
- `asyncio_default_fixture_loop_scope` is unset in pyproject.toml — should be `"function"`
- Per-file subprocess runner (NousResearch Hermes PR #29016) proven at scale: 13+ min xdist → ~5 min subprocess

---

## L2 (Insight) — What This Means

1. **The "deadlock" is a historical artifact** — it was fixed in 2024-2025. The original issue (#620) was closed in 2021; the second issue (#1071) was closed in 2024. Modern pytest-xdist 3.6.0+ + pytest-asyncio 1.2.0+ are compatible.

2. **Omega is in a better position than most projects** — Zero async fixtures in conftest.py, all 4 async fixtures are function-scoped, and we already have pytest-asyncio 1.4.0. The only gap is the unset `asyncio_default_fixture_loop_scope`.

3. **xdist is not the only (or best) path to parallelism** — The per-file subprocess runner is simpler, safer, and already proven in a higher-stakes environment. It aligns with Omega's M12 (atomic contracts) and M19 (adversarial alchemy: turn parallelism risk into isolation strength).

4. **The "right approximation" principle applies** — xdist provides per-test granularity at the cost of complexity and edge cases. The subprocess runner provides per-file granularity at the cost of startup overhead. For Omega's 53 test files, the startup overhead is acceptable (~26-53s with overlapping workers).

---

## L3 (Universal Principles) — Proposed Lessons

The following L3 principles are proposed for `proposed_lessons.yaml`:

### Lesson 1: The Deadlock That Wasn't
- **Principle**: "When investigating a known blocker, always verify the current version state. The issue may have been fixed in the time between the research and the implementation."
- **Evidence**: The "xdist + asyncio deadlock" was widely cited as blocking but was actually fixed in 2024-2025. Omega already has the fixing versions. The real gap was cosmetic (unset config value).
- **Application**: Before blocking work on a version-dependent issue, run `pip list | grep` to verify current versions against the fix versions.

### Lesson 2: Isolation Over Complexity
- **Principle**: "The simplest isolation mechanism (fresh process per unit of work) is often more reliable than the most sophisticated shared-state scheduler."
- **Evidence**: NousResearch Hermes replaced xdist (sophisticated scheduler) with per-file subprocess runner (simple executor) and got 2.6x speedup + stronger guarantees.
- **Application**: For Wave 5, choose the per-file subprocess runner over xdist. Skip execnet entirely.

### Lesson 3: Configuration Debt Before Code Debt
- **Principle**: "A missing configuration value can trigger warnings and subtle behavior changes that appear to be bugs in completely unrelated systems."
- **Evidence**: The unset `asyncio_default_fixture_loop_scope` in pyproject.toml triggers a warning in pytest-asyncio 1.4.0 (#1298) and causes the fallback-to-fixture-scope behavior that was the root of issue #706/#868.
- **Application**: Set `asyncio_default_fixture_loop_scope = "function"` immediately. This is a zero-risk, high-value config change that future-proofs against the upcoming default change (PR #1444).
