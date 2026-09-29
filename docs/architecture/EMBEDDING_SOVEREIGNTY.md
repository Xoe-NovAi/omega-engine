# 🔱 Embedding Sovereignty — One Canonical Space
**AP Token**: `AP-EMBEDDING-SOVEREIGNTY-v1.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode/space-bunny-free ⬡ trc_doc_sync ⬡ STANDARD

**Date**: 2026-09-28 · **Ruling**: `D-1024-DIM-NATIVE-20260926`
**Purpose**: Why there is exactly one embedding space, why width alone cannot enforce it, and what was removed on 2026-09-28.

---

# Omega Engine — Embedding Sovereignty
# AP: AP-EMBEDDING-SOVEREIGNTY-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: ENGINE | CONTEXT: EMBEDDING-SPACE]

## Answer first

Qwen3-Embedding-0.6B at **1024-D native** is the single canonical embedding space on both nodes. The default provider chain is `Qwen3GGUFEmbeddingProvider` → `SovereignFallbackEmbeddingProvider(dimension=1024)`. Nothing else.

If a canonical-capable provider is unavailable, the engine **raises**. It does not substitute another model, because a vector from a different model is not a smaller vector — it is a point in a different space that will silently corrupt every distance computed against it.

## The distinction that must not be collapsed

| | Status | Example |
|---|---|---|
| 1024-D canonical vector truncated by MRL to 768/512/256/128/64 | **LEGAL** — same model, same space, declared width | `mrl_dimensions: [1024, 768, 512, 256, 128, 64]` |
| A natively-768 vector produced by a *different model* | **ILLEGAL** — different space | nomic, gemma, minilm, potion standing in for canonical |

The discriminator is an explicit MRL declaration (`_target_dim`): same-model truncation is accepted; a narrow vector with no declared target is cross-model and is refused. Removing the MRL ladder to "fix" this would be an overcorrection — the ladder is what makes dimensionality flexible while keeping one space.

## Why a width check could never have caught it

The declared guard in `config/embedding_strategy.yaml` looked like enforcement and was not:

- The `vec0_lock` block is asserted by exactly one test and read by no `src/` code. The "All providers MUST output 1024-dim" text is never surfaced to any caller. It is documentation wearing a lock's clothing.
- The real runtime guard, `sqlite_vec_adapter_optimized._ensure_collection_vec_table`, compared the provider's width against **the target collection's declared width**. That is *self-consistency*, not canonical conformance. A 768-D nomic vector answering into `omega_vec_nomic_768` (declared 768) was a **perfect match**. The check passed.

A 768-D nomic vector and an MRL-truncated 768-D Qwen3 vector are indistinguishable by width. That is the whole reason removal was the only correct fix and why a width-based patch could not have worked.

The guard now in place is `EmbeddingManager._assert_canonical_width`, which compares against **canonical 1024** and runs *before* the value is returned, so a wrong-width answer is treated as a failure rather than a success. The circuit breaker refuses wrong-width answers as well.

## What was removed on 2026-09-28

| Removed | Why |
|---|---|
| `nomic_fallback` provider (priority 1, `native_dim: 768`) | A live silent cross-model substitution path. If Qwen3 was unavailable the chain dropped to 768 and reported success. |
| `GemmaGGUFEmbeddingProvider` + `omega_vec_gemma_768` collection, aliases, and adapter registrations | Officially deprecated. |
| `omega_vec_omega_vec_gemma_768` table (1009 rows) + 4 shadow tables | Contents were never semantically valid — see forensics below. |
| `omega_memory_vec` (float[256], 584 rows) in `data/memory/omega_memory.db` | Same finding. Also invisible to `COLLECTIONS`, to the alias table, and to `_scan_legacy_vec_tables`. |

`OllamaEmbeddingProvider` now requires an explicit `model=`. A no-arg construction cannot silently produce a nomic vector.

## The forensics that changed the migration plan

The gemma table was scheduled for re-embedding as a migration of meaningful vectors. It was not one.

- `1009 × 3072` bytes (`768 × float32`) `= 3,099,648` — an **exact match** for `sum(length(embedding))`. The count is 1009, not the 39 that vec0's internal storage pages suggest.
- **568 of 1009 rows are entirely zero.** The rest carry only 4–25 nonzero dimensions of 768.
- L2 norm is **exactly 1.0** as a single distinct value across all rows; only **103 distinct magnitudes**; ratios **exactly 3.0000 and 2.0000**. Values are integer token counts times one scale constant, then L2-normalised — reproduced locally as `md5(token) % dim` bucket increment followed by normalisation.

A neural embedding model emits dense vectors. These were **deterministic feature-hash output**. The table was named `gemma_768` and never held gemma.

**Consequence:** Step 19 is a **rebuild**, not a migration. There is no semantic data to preserve, so it is cheap, low-risk, and needs no rollback complexity beyond copying the `.db` first.

**No provenance record exists** — no `_meta` table, no version registry, no write-side log. The rows are unattributable, and the forensic answer is stronger than the bookkeeping one would have been. Any future write path must record model identity in-band, or this question recurs.

## Step 19 / Step 20 ordering

Order matters: 19 before 20. Removing aliases first would strand any caller still naming a legacy collection, and the canonical table must exist before legacy names are dropped.

1. Inventory with `get_status()`; record `legacy_vec_tables` / `legacy_vec_rows` before touching anything.
2. Copy `data/omega_memory.db` and record its sha256.
3. Re-embed the corpus with the canonical provider into `omega_vec_qwen_1024`.
4. Verify the canonical table exists at `float[1024]`, row count matches source documents, `_scan_legacy_vec_tables` is empty.
5. *Rollback:* restore the `.db` from step 2. Nothing outside that one file is touched.
6. Drop remaining legacy tables and the four `LEGACY_COLLECTION_ALIASES` entries — **only after** grepping `src/` and `mcp_servers/` for the old names.
7. Add a test asserting the retired names raise rather than silently aliasing.
8. *Rollback:* revert steps 6–7.

## Related

- `config/embedding_strategy.yaml` — canonical dimension, providers, collections, MRL ladder
- `src/omega/memory/sqlite_vec_adapter.py` — legacy aliases and dimension enforcement
- `SOVEREIGN_MANDATES.md` §M7 (Local-First), §M23 (Failure Integrity)
<!-- PROVENANCE-CORRECTED 2026-09-29T04:11:01Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/space-bunny-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

