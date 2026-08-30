<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Researcher Session Gnosis — 2026-07-21
**AP Token**: AP-RESEARCH-GNOSIS-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research

## Session Summary

Deployed as **Sovereign Researcher** to research the 5 most critical Phase C infrastructure gaps. Executed full Sovereign Search protocol (T0→T5) across all 5 domains, produced 5 research deliverables.

## L1 — Narrative

1. Read Sovereign Ark §3 (Phase C critical path) and job board specs for R20, R23, R25, R27, R28
2. Claimed all 5 jobs on `RESEARCH_JOB_BOARD.yaml` as `in_progress`
3. Read existing source code: `resource_guard.py`, `entity_registry.py`, `soul_updater.py`, `soul_update_manager.py`, `entity_workspace.py`, `Makefile`
4. Executed 10 parallel web searches covering: fcntl.flock, atomic write durability, psutil accuracy, OOM killer, llama.cpp RAM, pytest quarantine, MCP 2026-07-28 spec, Ryzen CCX optimization, concurrent llama.cpp, DDR4 bandwidth
5. Deep-fetched key MCP migration guide article from luismori.dev (15-min read, comprehensive migration spec)
6. Checked hardware topology via `omega-hub_get_system_stats`: 2 CCX, 8MB L3, 7637MB available/14793MB total
7. Wrote 5 research papers to `docs/research/R_*.md`
8. Updated all 5 jobs to `completed` with key_findings on the job board
9. Posted session completion to Hivemind

## L2 — Insights

### R25 — SoulStore Atomic Write Patterns
4 concurrent soul writers exist; **none** call os.fsync(). This is a data-loss vulnerability, not just a race condition. The fcntl.flock + atomic rename + fsync dance is the proven PostgreSQL pattern. Actor model (user vs system_agent) is partially implemented in `entity_registry.py` with `SOVEREIGN_USER_TOKEN` — this token scope can be extended rather than reinvented.

### R27 — ResourceGuard Single RAM Truth
The kernel knows more about available memory than any userspace counter. `MemAvailable` is the authoritative metric, accounting for page cache, reclaimable slab, and low-watermark reserves. The software counter (`_current_ram_mb`) creates a dangerous false ceiling (default `max_ram_mb=12288` on a system with 8000MB available). The OOMProtector path already reads `MemAvailable` — the fix is to elevate it and kill the counter.

### R28 — Test Suite Honesty
The Makefile lie is a cultural problem that trains everyone to ignore test output. The `test-badge` fallback hardcoded defaults (`PASSED=${PASSED:-705}`) means the badge is fabricating results whenever pytest fails or times out. The `@pytest.mark.quarantine` pattern is the canonical 2026 industry fix — it preserves test code (still runs) while not blocking CI.

### R20 — MCP Migration Audit (P1)
MCP 2026-07-28 is a **hard deadline 7 days from today**. The Hub's `stateless=True` flag is a head start, but SSE transport session state must be externalized before July 28. Three required headers (`Mcp-Method`, `Mcp-Name`, `traceparent`) are the new bar. File-based Hivemind is the sovereign contingency if SDK migration breaks.

### R23 — Local Admission Control (P1)
Ryzen 5700U is 2 CCX with 4MB L3 each, memory-bandwidth-bound. One concurrent llama.cpp instance is the hard optimum. Thread pinning to a single CCX (`taskset -c 0-3`) gives ~15% improvement over all-cores. Admission control via `asyncio.Semaphore(1)` with fail-fast to cloud is the right pattern.

## L3 — Universal Principles

1. **Single Writer Principle** — Every persisted state machine requires exactly one writer. Multiple concurrent writers guaranteed data loss regardless of locking protocol, because fsync semantics are process-scoped.
2. **Kernel Trust Principle** — The kernel's memory model includes page cache, slab, overcommit, and MMU behavior that no userspace counter can replicate. For admission control, trust the kernel's `MemAvailable` — it's the same signal the OOM killer uses.
3. **Honest Test Principle** — A test badge that lies is worse than no badge. Quarantine preserves test code and run visibility while enabling honest CI gating. The quarantine expiry prevents permanent acceptance of failure.
4. **Protocol Contingency Principle** — When an upstream protocol changes its wire format (MCP 2026-07-28), the sovereign fallback is to decouple coordination from that protocol entirely. File-based coordination has zero external dependencies and is the ultimate M23 safety net.
5. **Hardware Humbling Principle** — The Ryzen 5700U's 4MB per-CCX L3 cache and 51 GB/s memory bandwidth define hard inference limits. No amount of software optimization overcomes these physical constraints. The correct architectural response is admission control, not optimization heroics.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
