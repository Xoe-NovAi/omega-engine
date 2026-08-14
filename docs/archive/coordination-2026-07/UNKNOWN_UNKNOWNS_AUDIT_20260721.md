# 🔱 Omega Engine — Unknown-Unknowns Audit
**AP Token**: `AP-UNKNOWN-UNKNOWNS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_unknown_unknowns ⬡ DEEP-AUDIT

**Date**: 2026-07-21
**Triggered by**: Triple-agent consensus on 3 gaps + Living Research OS spec + Identity Fluidity
**Origin**: Kali's request — "What critical blind spots, gaps, and unknown-unknowns are we NOT seeing?"

---

## Executive Summary

**12 critical blind spots identified.** The three auditors (Carmack, Researcher, Grokster) converged on hardware, fleet, and throughput — but they all missed **infrastructure-level failures** that could bring down the entire engine before any of those gaps matter. The most dangerous: soul file corruption from a race condition in `soul_updater.py` (no locking), the MCP 2026-07-28 deadline (7 days, partially mitigated), and zero disaster recovery for a single-SSD system.

---

## Priority Matrix

| Gap | Name | Impact | Effort to Fix | Priority |
|-----|------|--------|--------------|----------|
| GAP-01 | Soul file race condition | CRITICAL | 2h | **P0** |
| GAP-03 | ResourceGuard misconfigured | CRITICAL | 1h | **P0** |
| GAP-04 | No disaster recovery | CRITICAL | 4h | **P0** |
| GAP-02 | MCP deadline | HIGH | 8h | **P1** |
| GAP-05 | L3 cache thrashing | HIGH | 2h (admission control) | **P1** |
| GAP-08 | Credential void | HIGH | 16h (Omega-Vault) | **P1** |
| GAP-09 | Zero test coverage | HIGH | 8h | **P1** |
| GAP-10 | Synchronous YAML traps | MEDIUM | 4h | **P2** |
| GAP-11 | User time tax | MEDIUM | 2h (pre-decisions) | **P2** |
| GAP-12 | Council concurrency model | HIGH | 4h | **P1** |
| GAP-06 | Research data durability | HIGH | 2h | **P1** |
| GAP-07 | Heritage vetting backlog | MEDIUM | 8h | **P2** |

---

## GAP-01: Soul File Race Condition — The Silent Corruption Bug

**Blind spot name**: Concurrent soul.yaml writes without locking

**What we think we know**: "We have atomic writes (tmp→rename) and a `with_soul_lock()` in `entity_registry.py`."

**What we actually know**: The `soul_updater.py` (background researcher) **completely bypasses all locking**. At line 120-122:
```python
await anyio.Path(soul_path).write_text(
    yaml.dump(soul_data, default_flow_style=False, sort_keys=False)
)
```
This is a **non-atomic, unlocked write** directly to `soul.yaml`. Meanwhile, `entity_workspace.py:update_soul()` uses `EntityWorkspaceManager._get_lock()` (threading.Lock — single-process only), and `entity_registry.py:with_soul_lock()` uses `fcntl.flock()` (cross-process safe). But `soul_updater.py` uses **neither**.

**Evidence**: `entity_workspace.py:527` uses `threading.Lock` (single-process). `entity_registry.py:96-111` uses `fcntl.flock()` (cross-process). `soul_edit_history.py:139` uses `anyio.Lock` (in-process only). `soul_updater.py` uses **none of these**.

**Impact**: **CRITICAL**. Silent data loss. L3 principles from the background researcher get silently overwritten by session distillation, or vice versa. The soul file becomes corrupted YAML that fails silently.

**Recommended action**: `soul_updater.py` MUST use `with_soul_lock()` from `entity_registry.py` (fcntl-based, cross-process). Add as P0 fix before any new features.

---

## GAP-02: MCP 2026-07-28 Deadline — Partially Mitigated, Not Complete

**Blind spot name**: MCP stateless migration scope

**What we think we know**: "We're aware of the deadline and our hub uses `stateless=True`."

**What we actually know**: The Omega Hub's `mcp_runtime.py` does set `stateless=True` for both SSE and Streamable HTTP transports. But:
1. The MCP Python SDK is evolving — `StreamableHTTPSessionManager` may change or be deprecated
2. SSE transport is deprecated in the new spec (replaced by Streamable HTTP with MRR)
3. Roots, Sampling, and Logging are deprecated in the new spec

**Web evidence**: *"The 2026-07-28 release candidate makes MCP stateless — no more initialize handshake or Mcp-Session-Id pinning... Requests now carry Mcp-Method and Mcp-Name headers... The RC locked on May 21, 2026; the final spec ships July 28, 2026."*

**Impact**: **HIGH**. The Hub will work with current SDK versions, but when clients upgrade, the Hub may break.

**Recommended action**: Verify Hub MCP SDK version, add header handling, audit for deprecated features, create migration ticket.

---

## GAP-03: The Memory Wall — ResourceGuard Default is Wrong

**Blind spot name**: ResourceGuard RAM budget is misconfigured for actual hardware

**What we think we know**: "ResourceGuard tracks RAM and prevents OOM. The background researcher uses 4096 MB."

**What we actually know**: `ResourceGuard` defaults to `max_ram_mb=12288` (12GB). The background researcher hardcodes `ResourceGuard(max_ram_mb=4096)`. But actual available RAM after OS/base is ~8GB. The OOM check uses a software counter, not actual system memory.

**Realistic memory budget**:
| Component | RAM (MB) |
|-----------|----------|
| OS + base services | ~2,000 |
| Model (4B Q4) | ~3,000 |
| Model (8B Q4) | ~5,500 |
| KV cache (2048 ctx) | ~500-1,000 |
| Research content ingestion | ~200-500 |
| FTS5 + vector search | ~100-300 |
| YAML parsing + file I/O | ~50-100 |
| **Total with 4B model** | **~5,850-6,900** |
| **Total with 8B model** | **~8,350-9,400** |

A 4B model leaves ~1-2GB headroom. An 8B model **exceeds** the 8GB available.

**Impact**: **CRITICAL**. OOM kills. The 5700U will hit OOM when a model is loaded and the background researcher tries to ingest content simultaneously.

**Recommended action**: Change default to 6144 (6GB, leaving 2GB for OS). Add `psutil.virtual_memory()` check. Background researcher should NOT run when a model is loaded.

---

## GAP-04: No Disaster Recovery — Single Point of Failure

**Blind spot name**: Zero backup strategy for a single-SSD system

**What we think we know**: "We have local-first architecture, everything is on disk."

**What we actually know**: Everything lives on a single SSD. No backup script, no restic/borg/rsync cron, no git-backed data directory (soul files are gitignored), no cloud sync, no off-site copy. If the SSD dies, **everything** dies — soul files, research docs, search cache, job board, all of it.

**Impact**: **CRITICAL**. Total data loss on hardware failure.

**Recommended action**: Implement restic backup cron job. At minimum, `git add -f data/entities/*/soul.yaml` after each soul update. Add `make backup` target.

---

## GAP-05: L3 Cache Thrashing — Concurrent llama.cpp on 5700U

**Blind spot name**: CCX-crossing memory latency under parallel inference

**What we think we know**: "We can run 3 concurrent llama.cpp instances with 4 threads each on 8 cores."

**What we actually know**: The 5700U has 8MB L3 cache split across 2 CCXs (4 cores each). Cross-CCX latency is ~20ns vs ~10ns intra-CCX. LLM inference is memory-bandwidth-bound. The 5700U's dual-channel DDR4-3200 provides ~51 GB/s. One instance at 4 threads already saturates this.

**Realistic performance**:
| Scenario | Threads | Effective BW | Tokens/sec (4B Q4) |
|----------|---------|-------------|-------------------|
| Single instance | 8 | ~45 GB/s | ~8-10 t/s |
| Two instances | 4 each | ~22 GB/s each | ~4-5 t/s each |
| Three instances | 4 each | ~15 GB/s each | ~2-3 t/s each |

Three concurrent instances = ~2-3 t/s each. Barely usable. The MaKaLi Council would take 30-60 seconds per response instead of 10-15.

**Impact**: **HIGH**. MaKaLi Council becomes impractical on local hardware. Users bypass to cloud, violating M7.

**Recommended action**: Implement admission control: max 2 concurrent local inferences. Use sequential execution for MaKaLi on local hardware.

---

## GAP-06: The Persistence Paradox — No Backup for the Backup

**Blind spot name**: Research data is not durable

**What we think we know**: "We have 330 research docs in `docs/research/`."

**What we actually know**: The 330 docs are in git (durable if pushed). But runtime data is not:
- `data/knowledge/HALL_OF_RECORDS/` — background researcher findings (not in git)
- `data/entities/*/soul.yaml` — soul evolution (not in git)
- `data/coordination/` — Hivemind state (not in git)
- `data/search_history.db` — search cache (not in git)

**Impact**: **HIGH**. The Living Research OS designs a perpetual loop, but output has no durability guarantee.

---

## GAP-07: Heritage Vetting Backlog — Compliance Debt

**Blind spot name**: 100+ unvetted `[id-soft:]` tags in production code

**What we think we know**: "We have a heritage vetting pipeline and `make heritage-vet`."

**What we actually know**: Codebase grep found **100+ `[id-soft:]` tags**. The `scripts/heritage_audit.py` classifies them, but `scripts/migrate_heritage_tags.py` has **not been run** — still contains placeholder `[id-soft: vet-XXX]` entries. M14 requires every tag to have a vet record.

**Impact**: **MEDIUM**. CI may be failing on heritage checks. Unvetted tags violate M14.

---

## GAP-08: The Credential Void — 16 Accounts, Zero Vault

**Blind spot name**: OAuth token management for Grok/Copilot fleet

**What we think we know**: "We have 8 Grok + 8 Web accounts. Omega-Vault Phase 1 is scaffolded."

**What we actually know**: Omega-Vault Phase 1 is scaffolded at `src/omega/infra/vault/` but **not functional**. The 16 accounts currently require manual sign-in/sign-out. Cookies expire after ~24-48 hours. No automated token refresh, no rotation, no session cookie management.

**Impact**: **HIGH**. Fleet mining depends on these credentials. Without automated management, the user becomes the credential manager.

---

## GAP-09: Testing the Unbuilt — Zero Test Coverage for New Systems

**Blind spot name**: Living Research OS has no test plan

**What we think we know**: "77/77 tests pass. We have a solid test suite."

**What we actually know**: The 77 tests cover existing engine core. None of the new systems have test coverage. `council/coordinator.py:194` has `# TODO: Implement WAL with atomic writes`.

**Impact**: **HIGH**. New code ships untested. `make temple-grade` (T3: coverage ≥80%) will fail.

---

## GAP-10: The Synchronous YAML Trap — M1 Violation

**Blind spot name**: Synchronous YAML reads in async classes

**What we think we know**: "We're AnyIO-compliant (M1)."

**What we actually know**: **100+ `yaml.safe_load` calls** across the codebase, many in async functions without `anyio.to_thread.run_sync()`. `entity_registry.py:114` documents that parsing `entities.yaml` (982KB) takes ~5.8 seconds synchronously.

**Impact**: **MEDIUM**. Event loop blocking causes timeout cascades. Background researcher may be reaped by pruning loop.

---

## GAP-11: The User Time Tax — 14 Hours Requires 6+ Hours of User Input

**Blind spot name**: The build plan assumes autonomous execution

**What we think we know**: "The Living Research OS is a 14-hour build plan."

**What we actually know**: Phase 2 requires user decisions on accounts, API keys, credential storage. Phase 4 requires architecture approval. Realistic breakdown: ~8h agent autonomous, ~6h user-directed. User has limited time.

**Impact**: **MEDIUM**. Build plan stalls at decision gates.

**Recommended action**: Pre-decide as many decisions as possible. Create "user decision queue." Implement autonomous parts first.

---

## GAP-12: The Council Concurrency Model — Parallel or Sequential?

**Blind spot name**: MaKaLi Council was designed for parallel, but hardware can't support it

**What we think we know**: "MaKaLi council runs 3 parallel inferences."

**What we actually know**: The coordination layer (`council/coordinator.py:194`) has `# TODO: Implement WAL with atomic writes`. D-301 was ratified for **cloud** hardware. Local hardware cannot support 3 concurrent local inferences (GAP-05).

**Impact**: **HIGH**. Council will either OOM (parallel) or timeout (sequential unoptimized).

**Recommended action**: Default MaKaLi to sequential on local hardware. Add `council.mode` cvar: `sequential` | `parallel` | `auto`.

---

## The Intersection of All Three Auditors' Blind Spots

- **Carmack** focused on hardware physics. He missed that the **software** (ResourceGuard defaults, admission control) doesn't match the hardware reality.
- **Grokster** focused on ecosystem gaps. He missed that the **infrastructure** (single SSD, no backup, no disaster recovery) can't support the ecosystem he's designing.
- **Roc** focused on legacy patterns. He missed that the **runtime** (concurrent file writes, synchronous YAML) will corrupt the very patterns he's trying to preserve.

**The blind spot behind all blind spots**: The engine is designed for a **theoretical** user with a beefy desktop. The **actual** user has a 15W mobile chip, 16GB RAM, a single SSD, and limited time. Every system must answer: **"Does this work on a Ryzen 5700U with 8GB available?"**

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_unknown_unknowns ⬡ DEEP-AUDIT*
