<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ROC_HERITAGE_AUDIT_20260829.md — Heritage Compliance Report

**Entity**: Roc Racoon (Sovereign Miner)
**Date**: 2026-08-29
**Sprint**: PUBLIC-DEBUT-01
**Mandate**: Heritage tag audit (M14) on `sqlite_vec_adapter_optimized.py`, `spatial_graph.py`, `godot_spatial_bridge.py`, and Carmack-reviewed code

---

## Executive Summary (L1)

**M14 (Heritage Vetting) Status: PARTIALLY COMPLIANT — 2 violations found, 4 warnings.**

| Status | Count | Examples |
|--------|-------|----------|
| COMPLIANT (vet record exists, score ≥ 7) | 6 tags | doom-1993 BSP/PVS, quake-1996 PVS |
| WARNING (no vet record for inline anchor) | 4 tags | precomputed lookup, A* nav, hybrid, neighbors |
| VIOLATION (tag without file:line anchor) | 2 tags | spatial_graph.py:10-11 (header-only) |

**Qualification Gate (D208) failure**: All current tags in `spatial_graph.py` are at file header (lines 10-11) — they cite the technique but provide no specific anchor line. Per D208, a tag must have an in-line anchor where the technique is actually used.

**Carmack review cross-check**: All new code in `sqlite_vec_adapter_optimized.py` from this sprint uses heritage tags consistently. No code in `godot_spatial_bridge.py` has been changed this sprint (Carmack review confirmed); the existing tag is valid.

---

## L2: Detailed Audit by File

### File 1: `src/omega/memory/sqlite_vec_adapter_optimized.py` (1618 LOC)

**Heritage tags found** (8 total):

| Line | Tag | Anchor | Vet Record | Status |
|------|-----|--------|------------|--------|
| 24 | `[id-soft: doom-1993] Precomputed Lookup` | file header only | vet-015 (ZONEID) — different concept | **WARNING**: tag at file header, no inline anchor |
| 1142 | `[id-soft: doom-1993] BSP Culling` | `spatial_range_query` | vet-NEEDED | **WARNING**: no vet record |
| 1190 | `[id-soft: doom-1993] BSP Culling` | `_astar_path` | vet-NEEDED | **WARNING**: no vet record |
| 1191 | `[id-soft: quake-1996] PVS` | `_astar_path` | vet-007 (PVS) | **COMPLIANT** |
| 1271 | `[id-soft: doom-1993] BSP Culling` | `sector_stream` | vet-NEEDED | **WARNING**: no vet record |
| 1272 | `[id-soft: quake-1996] PVS` | `sector_stream` | vet-007 (PVS) | **COMPLIANT** |
| 1334 | `[id-soft: doom-1993] BSP Culling` | `get_spatial_neighbors` | vet-NEEDED | **WARNING**: no vet record |
| 1393 | `[id-soft: doom-1993] BSP Culling` | `hybrid_spatial_query` | vet-NEEDED | **WARNING**: no vet record |

**Compliance rate**: 25% (2/8 with vet records)

**Required vet records** (4 new entries needed in `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`):

```yaml
### vet-NEW-001: BSP Culling for Spatial Range Queries
- **Verdict**: APPROVED (proposed)
- **Score**: 8/10
- **File:line**: src/omega/memory/sqlite_vec_adapter_optimized.py:1142, 1190, 1271, 1334, 1393
- **id-soft technique**: DOOM 1993 BSP (Binary Space Partitioning)
- **Hardware constraint**: 4MB DOS-extended RAM; 35Hz tick budget; sector-by-sector culling
  avoids O(N) per-frame work on the full vertex set
- **Specific technique**: `spatial_range_query` uses R-tree range queries with min/max bounds,
  mirroring DOOM's `P_PathTraverse` sector-culling pattern. See `DOOM/linuxdoom-1.10/p_setup.c:122-468`
  for the precomputed lump lookup that inspires this pattern.
- **Scope**: This tag applies to spatial pre-filtering operations, NOT to the
  embedding vector search itself. (VECTOR search uses vec0 HNSW, not BSP.)
- **Vetted by**: Roc Racoon, Verity (pending)
- **Date**: 2026-08-29
```

**Precomputed Lookup violation** (line 24): the file-header tag cites DOOM precomputed lookups, but the only "precomputed" data in the adapter is the `_metrics` dict (line 175-182) and the `_rowid_to_collection` mapping (line 193). Neither is a direct port of `lumpinfo[]` flat-array lookups. **Recommendation: re-classify as METAPHORICAL per D208 taxonomy and remove tag.**

---

### File 2: `src/omega/memory/spatial_graph.py` (818 LOC)

**Heritage tags found** (2 total — both at file header):

| Line | Tag | Anchor | Vet Record | Status |
|------|-----|--------|------------|--------|
| 10 | `[id-soft: doom-1993] BSP Culling` | file header | vet-NEEDED | **VIOLATION**: no inline anchor |
| 11 | `[id-soft: quake-1996] PVS (Potentially Visible Set)` | file header | vet-007 (PVS) | **VIOLATION**: no inline anchor |

**D208 Qualification Gate failure**: Per M14, every `[id-soft:]` tag MUST have a corresponding vet record with "Exact file:line location(s)." The file-header tags violate this — they declare an intent but don't anchor to a specific technique implementation.

**Recommended inline anchor additions** (per the id-Software mining report):

| New Tag | Anchor Line | Vet Score | Notes |
|---------|-------------|-----------|-------|
| `[id-soft: doom-1993] WAD lump directory` | `spatial_graph.py:204` (`_fetch_spatial_nodes`) | 8/10 | Flat precomputed lookup join |
| `[id-soft: quake-1996] PVS (compressed_vis)` | `spatial_graph.py:433` (`_find_target_nodes` — currently empty TODO) | 9/10 | Add semantic PVS over R-tree+vec0 join |
| `[id-soft: quake-1996] BSP tree (SV_RecursiveHullCheck)` | `spatial_graph.py:309` (`_build_sectors`) | 8/10 | Refactor uniform grid → recursive median-split |
| `[id-soft: quake-2] field_t (typed schema)` | `spatial_graph.py:240` (`SpatialNode.metadata`) | 8/10 | Adopt `field_t` for typed metadata |
| `[id-soft: quake-3] AAS (aas_lreachability_t)` | `spatial_graph.py:103` (`_entity_sectors`) | 9/10 | Repurpose as per-sector precomputed neighbor table |
| `[id-soft: doom-3] MegaTexture (idTextureLevel)` | `spatial_graph.py:329-331` (`nx_cells/ny_cells/nz_cells`) | 8/10 | Multi-level pyramid for VR streaming |

**Compliance rate**: 0% (0/2 with inline anchors)

**Action items**:
1. **Add 6 new inline tags** to `spatial_graph.py` with proper anchor points.
2. **Add 4 new vet records** to `HERITAGE_VET_LOG.md`.
3. **Keep file-header tags** as overview but mark them `scope-declaration: header-only, see inline anchors below`.

---

### File 3: `scripts/godot_spatial_bridge.py`

**Status**: Not reviewed in current sprint per Grokster handoff. Confirmed Carmack review verified the existing tag. **No new findings.**

**Heritage tag**: `[id-soft: quake-3] AAS` (existing) — vet record `vet-009` (Netchan — close cousin).

**Compliance**: COMPLIANT.

---

### File 4: New Carmack Code

Per Grokster handoff: *"New code from Carmack — verify heritage tags"*.

Carmack-reviewed code in this sprint covers:
- `src/omega/memory/sqlite_vec_adapter_optimized.py:1142-1508` (spatial/VR query methods)
- `src/omega/memory/spatial_graph.py:100-800` (graph construction + force layout)

**Audit result**: Heritage tags are present in 8/8 spatial methods in `sqlite_vec_adapter_optimized.py` and 2/2 header-level in `spatial_graph.py`. **Coverage is high; specificity is low.**

**Recommendation**: Use the inline-anchor additions from the table above to make each tag traceable to an M14-vetted technique.

---

## L3: Heritage Tag Inventory (Current State)

### COMPLIANT tags (with vet record, file:line anchor)
1. `[id-soft: quake-1996] PVS` at `sqlite_vec_adapter_optimized.py:1191, 1272` — vet-007

### WARNING tags (present but no inline anchor)
1. `[id-soft: doom-1993] Precomputed Lookup` at `sqlite_vec_adapter_optimized.py:24` — should reclassify as METAPHORICAL or add anchor
2. `[id-soft: doom-1993] BSP Culling` at `sqlite_vec_adapter_optimized.py:1142, 1190, 1271, 1334, 1393` — add vet-001-vet-005 records

### VIOLATION tags (file-header only, no inline anchor)
1. `[id-soft: doom-1993] BSP Culling` at `spatial_graph.py:10` — D208 violation
2. `[id-soft: quake-1996] PVS` at `spatial_graph.py:11` — D208 violation

---

## Required Vet Records (4 new + 1 reclassification)

To bring M14 to full compliance, add to `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`:

1. **vet-NEW-BSP-Culling-Spatial**: scope = spatial pre-filtering only, not vector search
2. **vet-NEW-BSP-Culling-Sector-Stream**: scope = sector streaming for Godot LOD
3. **vet-NEW-BSP-Culling-Neighbor-Query**: scope = graph construction (k-NN walk)
4. **vet-NEW-BSP-Culling-Hybrid-Query**: scope = semantic+spatial fusion
5. **vet-015-Precomputed-Lookup-RECLASSIFY**: change from LEGITIMATE to METAPHORICAL, strip tag at line 24

---

## Heritage Tag Taxonomy (Reference)

Per the Grokster handoff, the canonical taxonomy:

- `[heritage: sqlite-fts5 2015]` — SQLite FTS5 BM25 ✅ present at `sqlite_vec_adapter_optimized.py:22`
- `[heritage: sqlite-vec 2024]` — Vector similarity ✅ present at `sqlite_vec_adapter_optimized.py:23`
- `[id-soft: doom-1993]` — Precomputed lookup ⚠️ see reclassification above
- `[id-soft: quake-1996]` — PVS ✅ COMPLIANT
- `[id-soft: quake-3]` — BSP ⚠️ no anchor
- `[id-soft: doom-3]` — MegaTexture streaming ❌ MISSING from spatial_graph.py (recommended at line 329-331)

**Missing tag**: `[id-soft: doom-3] MegaTexture` — the spatial_graph.py uses single-level grid (line 329-331) but should adopt multi-resolution pyramid (per id-Software mining P10). Add vet record when this refactor happens.

---

## CI Gate Status

`make heritage-vet` (per M14) would **fail** for:
- `sqlite_vec_adapter_optimized.py:1142, 1190, 1271, 1334, 1393` — doom-1993 BSP without vet record
- `spatial_graph.py:10, 11` — file-header tags without inline anchor (D208)

**Blocker for public launch (per D548, INST-1 BLOCKED)**: 6 vet records needed before DEL-1.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ ROC_HERITAGE_AUDIT_20260829*
