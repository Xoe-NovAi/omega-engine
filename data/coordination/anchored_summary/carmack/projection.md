<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JOHN_CARMACK PROJECTION — 2026-09-28 (POST-COMPACTION)

**EIS**: `ses_fc8dca39effe3nZJp3QHx81Fy3` · **Model**: `opencode/space-bunny-free`
**Branch**: `release/debut-v1.6.0` · **Committed**: `de660681` (MaKaLi)
**Temple-grade**: 53/53 · **M1/M23/M24/M27** observed throughout

## Status: GREEN — four mandates closed, one retraction pair banked

### ⭐ Two Self-Retractions (highest-value output)

| Claim I made | Truth | Proof |
|---|---|---|
| "39 real vectors" | **1009** | `1009 × 3072 = 3,099,648` = `sum(length(embedding))`. The 39 was vec0's **internal storage-page** count, not a census. Confidence in 39: **0/10** |
| "8/10 EmbeddingGemma-300M" | **0/10 — feature-hash** | 568/1009 all-zero · 4–25 nonzero of 768 · L2 **exactly** 1.0 · 103 distinct magnitudes · ratios **exactly** 3.0 and 2.0 · `0.1644 = 1/√37` · algorithm **reproduced locally** (md5 hash, `+=1`, L2) |

**Doctrine earned**: *never reason from a label — characterise the artifact. When a
number and byte arithmetic disagree, the bytes win.* Retraction 2 recast **Step 19 from
migration to rebuild**.

### Mandates Closed

**P0 — D-1024 sovereignty (M23 fail-loud).** Ticket premise corrected: `vec0_lock` at
`embedding_strategy.yaml:23` **enforces nothing at runtime** — one reader, a test. The
real guard compared width to the *target collection's* declared dim, so a nomic-768
answer into a 768 collection was a **perfect match**. Width cannot separate cross-model
from same-model-MRL; `_target_dim` is the only discriminator. Removed the priority-1
nomic fallback; added `EmbeddingProviderUnavailableError` + pre-return width assertion;
`OllamaEmbeddingProvider()` now requires an explicit model. **Found a second hole absent
from the ticket**: the `OMEGA_ENV=test` short-circuit emitted a *sub-canonical* zero
vector. Negative test **observed firing**. Contract tests 17 → **25**.

**P1 — stranded imports.** `import omega_hub` → `ModuleNotFoundError`; live surface is
54 tools with Hivemind = `awareness / get_metrics / handoff / lock`. Repointed publish,
watchdog alert, and the post script; reimplemented the dead Redis **subscribe as a poll**
returning `{"status":"empty"}` rather than a fake success. All adapters now raise
(`M23`). **Found a fifth site not in the brief** — `scorecard.py:452`.

**P1 — circular import lesson.** Hoisting a lazy import broke the engine
(`omega.research → hub_tools → task_registry → hub_tools.server → omega.oracle →
omega.governance → omega.research`). **The original lazy placement was deliberate and
correct** — only the module name was wrong. Also: FastMCP's `@mcp.tool()` wraps callables
(`TypeError: object of type 'CallToolResult' has no len()`) — a bridge whose *call shape*
no longer matched.

**P1 — the dead test.** `TestCriticalTools` **20 skips / 0 assertions** → **26 real
assertions / 0 skips** against the complete registry, with truncation-as-hard-failure and
a live-hub count cross-check. **Falsified by injection**: both guards failed with
actionable messages, then restored and re-verified green.

**Gemma removal.** Provider class, config collection, both adapters' `COLLECTIONS` +
`LEGACY_COLLECTION_ALIASES`, and 10 tables across 2 DBs. Qwen3 MRL ladder intact.

### Rulings Delivered

- **AVX-VNNI — DO NOT SPLIT THE EMBEDDER.** Both chips retire ~64 MAC/cycle; a split
  would introduce a cross-node quantisation boundary (the Nomic-vs-Qwen error, smaller);
  and at 20/60/120 items the corpus is **~480 KB — fits L2**. No distribution problem
  exists. **No ANN index** at these cardinalities.
- **Headroom D-582 — tool boundary, READ payloads only.** Before vector storage is
  double-lossy and *structurally unobservable*; inside transport envelopes couples layers
  and kills `diff`-ability + M9. Never compress writes or tool arguments.
- **Minisign/C6 — sound primitive, insufficient closure.** A signature proves *a* key
  signed *these bytes*, not that the authorised publisher did. Needs a pinned
  **out-of-band** trust root + written rotation policy. **Do not declare C6 closed on a
  signature alone.**

### Invariants Held

Doom Guy lineage-only · Flynn `continuation_of: null` · Build/Slot not agents · Scribe
separate · checkout `fa9c4edc` lineage / `1.6.0-alpha.1` · exact `/mcp` · integrity ≠
trust · C6/N0-04 **OPEN** · final authenticated transfer **NOT claimed** ·
`mcp_servers/**` and `data/federation/**` **untouched** throughout.

### Verification

`make temple-grade` **53/53** · contract tests **25** · touched-file sweep **118 PASS**.

### Open Threads

1. **`mcp_servers/omega_hub/github_bridge.py`** carries the same stranded-import class
   and is still unfixed — the whole webhook bridge is dead until Ma'at applies the
   lazy-import + `__wrapped__` pattern.
2. **Provenance must go in-band.** No `_meta`, no version registry, no write log existed;
   legacy tables are permanently unattributable.
3. **Step 20 scope** — nomic tiers are the only remaining legacy collections; gemma is
   fully gone. The 256-dim `omega_memory_vec` was invisible to `COLLECTIONS`, aliases,
   and `_scan_legacy_vec_tables`; now dropped.
4. **Microbenchmark** Zen 2 FMA vs Raptor Lake VNNI before treating throughput parity as
   settled (my 7/10 confidence on that specific claim).

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode/space-bunny-free ⬡ trc_p0_p1_gemma_arc ⬡ COMPACTION-READY ⬡ 53/53*
