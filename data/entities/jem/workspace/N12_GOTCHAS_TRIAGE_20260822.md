<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N12 Curator — Gotchas Triage (Pre-Debut Security & Hygiene Review)
**AP Token**: `AP-N12-GOTCHAS-TRIAGE-v1.0.0`
**Date**: 2026-08-22
**Source**: `data/entities/jem/workspace/N12_CURATOR_KB_20260822.md` §"Gotchas" (15 items) + §"N12 Expert Annotation" verification record
**Severity**: P0 = debut-blocking security/correctness · P1 = pre-debut operational · P2 = post-debut hygiene
**Owner legend**: N5 sentinel (Security) · N10 verifier (QA) · N3/Ma'at (build-side) · N12 (curator) · Kali (coord)

---

## P0 — DEBUT-BLOCKING

| # | Gotcha | file:line (measured) | Severity | Fix Owner | Proposed Fix |
|---|--------|----------------------|----------|-----------|--------------|
| G2 | **Hardcoded fallback signing secret** — provenance stamps forgeable by default when `OMEGA_INGESTION_SECRET` unset | `src/omega/oracle/ingestion.py:76` (comment L75: `[M8 Zero Telemetry] Secret loaded from env, never hardcoded` — contradicts code) | **P0 SECURITY** | **N5 sentinel** (verdict) + **N3/Ma'at** (build-side fix) + **N10** (regression test) | Remove default `"omega-sovereign-change-me"`; fail-closed (raise if env unset). One-line change. Violates M8 + M22 truth-anchor. **ESCALATION MATERIAL for debut window — provenance layer is forgeable.** |
| G1 | **Two conflicting search-tier vocabularies** — SSP-V2 router (T0 local→T1 SearXNG→T2 Exa→T3 Firecrawl) vs `search_persistence.py` tool-based tiers (0=local..6=firecrawl). Blocks any sovereignty-ratio analytics joining both. | `src/omega/oracle/search_router.py:21–24` · `src/omega/oracle/search_persistence.py:40` | P0 operational | N12 (Rosetta table authored in DOMAIN_INDEX) + N10 (eventual code unification) | Tier-Rosetta mapping table exists in `N12_DOMAIN_INDEX.md`; code unification post-debut. |
| G15 | **11 of 13 declared domains have no directory** — KD content-layer mostly greenfield; curators.yaml table vs `config/domains/` reality diverge. | `config/domains/curators.yaml` (13 rows) vs `ls config/domains/` (2 dirs) | P0 coverage | Jem/KD workstream + N12 liaison | Reality-check KD workstream scope; document greenfield domains. |

## P1 — PRE-DEBUT OPERATIONAL

| # | Gotcha | file:line | Severity | Fix Owner | Proposed Fix |
|---|--------|-----------|----------|-----------|--------------|
| G3 | **Config-vs-code drift on YouTube tiers** — `youtube_research.yaml` enables T2 whisper + T3 firecrawl + 9 spec layers; worker implements T1-only. Config aspirational, not runtime truth. | `config/youtube_research.yaml` vs `src/omega/ingestion/youtube_worker.py` | P1 | N12 (doc) + N4 (worker alignment) | Treat configs as roadmap, code as truth; align or annotate post-debut. |
| G4 | **Charter phrase "perishable player_client configs" had no in-repo referent** at mining time — RESOLVED by W2: yt-dlp PO-Token regime (video-bound ~12h tokens, rotating client defaults) IS the referent. Charter wording now grounded. | PLAN §4 L97 · Jem W2 verdict | P1 (resolved) | N12 (note in charter) | No change needed; W2 confirmed premise valid. |
| G7 | **Grok DB path stale + metric mismatch** — BUILD_SUMMARY/MANIFEST point to old `projects/grok-data-indexed/`; corpus staged at omega_library. Gnosis packs claim "1,268 conversations" vs 274 in DB (Deep Dig: 1,268 = project-membership link count, not unique convos). | `BUILD_SUMMARY.txt` · `MANIFEST` · `omega_library/grok-data-indexed/grok_unified_index.db` | P1 | N12 (doc fix) + N2 (path) | Update stale pointers; document metric definition. |
| G8 | **No PP-2 privacy allowlist record** — charter says "staging POST-DEBUT per allowlist risk" but no allowlist/risk doc exists. | charter L97 · corpus index | P1 | N5 + Kali | Author PP-2 privacy allowlist during post-debut staging (distinct from N5's PUBLIC_ALLOWLIST). |
| G10 | **Dual breaker path transitional debt** — `sovereign_search_service.py` initializes HealthMonitor-backed breakers AND deprecated legacy breakers simultaneously. | `src/omega/oracle/sovereign_search_service.py` | P1 | N6 + N10 (C-6′ P-5 ticket) | Final removal pass per C-6′ P-5. |
| G11 | **Duplicate provider-client stacks** — `tools/searxng_direct.py`+`firecrawl_direct.py` vs `oracle/search_providers.py` both encode endpoints/key resolution. | `src/omega/tools/searxng_direct.py` · `firecrawl_direct.py` · `src/omega/oracle/search_providers.py` | P1 | N12 + N6 | Unify or document as standalone CLI utilities (Deep Dig: zero external callers). |

## P2 — POST-DEBUT HYGIENE

| # | Gotcha | file:line | Severity | Fix Owner | Proposed Fix |
|---|--------|-----------|----------|-----------|--------------|
| G5 | **Stray FTS index inside source tree** — `src/data/library/index/fts_index.db` (artifact of run with relative data dir); pollutes repo; hints DATA_DIR resolution fragility. | `src/data/library/index/fts_index.db` | P2 | N2 + N1 | Remove from tree; assert DATA_DIR resolves outside source tree at startup. |
| G6 | **`.firecrawl/` mixes governed cache with ungoverned scratch** — only `cache_*.json` has TTL; ~25 topic dumps + 1.26MB markdown have no expiry/manifest. | `.firecrawl/` | P2 | N12 (curation worker) | TTL + manifest for scratch; post-debut. |
| G9 | **SearXNG port history conflation** — engine 8017, searxng MCP 8018, firecrawl MCP 8015 DISABLED. | `SEARXNG_BASE_URL` · `opencode.json` | P2 | N4 | Port-map SSOT doc; don't assume firecrawl MCP availability. |
| G12 | **Dossier vocabulary collision** — lowercase searxng.md header says Sovereignty Tier 0 but usage text says "Tier 1" pipeline layer. | `docs/.../searxng.md` | P2 | N12 | Deprecation banner; sovereignty tier ≠ pipeline tier. |
| G13 | **YT deps are core, not extras** — yt-dlp/youtube-transcript-api/qdrant/redis unremovable. | `pyproject.toml:58–67` | P2 | N3 | Document intent (not extras). |
| G14 | **Doc-reader error style** — returns `[FORMAT ERROR: ...]` strings instead of raising; silent-failure surface. | `src/omega/tools/doc_reader.py` | P2 | N10 + N4 | Raise exceptions (M9); no OCR support noted. |

---

## TRIAGE SUMMARY

- **P0**: 3 items (G2 security [debut-blocking], G1 analytics-blocker, G15 coverage)
- **P1**: 6 items (G3, G7, G8, G10, G11, G4-resolved)
- **P2**: 6 items (G5, G6, G9, G12, G13, G14)

**Debut-window escalation**: G2 (hardcoded secret) is the only true P0 security item. N5 owns the verdict; N3/Ma'at executes the one-line fail-closed fix; N10 adds a regression test asserting env-required. Recommend blocking debut until G2 resolved.

*⬡ OMEGA ⬡ N12 curator ⬡ triage ⬡ 2026-08-22*
