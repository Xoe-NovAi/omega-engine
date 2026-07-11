# 🔱 Heritage Audit Remediation Report
**Generated**: 2026-07-10T20:27:59.314534
**Total Tags Analyzed**: 50

## Summary

- **LEGITIMATE**: 0
- **METAPHORICAL**: 0
- **OVER-ATTRIBUTED**: 50

## OVER-ATTRIBUTED (50)

### [id-soft: doom-1993] BSP Culling
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/context_builder.py:272` — `# [id-soft: doom-1993] BSP Culling — top-K principles only`
  - `src/omega/oracle/model_gateway.py:756` — `# [id-soft: doom-1993] BSP Culling — O(1) pre-check skips broken providers`
  - `src/omega/oracle/selective_hydration.py:8` — `# [id-soft: doom-1993] BSP Culling — O(1) culling of irrelevant principles`
  - `src/omega/oracle/semantic_router.py:8` — `# [id-soft: doom-1993] BSP Culling — O(1) culling of irrelevant entities`
  - `src/omega/oracle/semantic_router.py:110` — `# [id-soft: doom-1993] BSP Culling — only process active entities`
  - `src/omega/oracle/spatial_resolver.py:12` — `# [id-soft: doom-1993] BSP Culling — Spatial partitioning for efficiency`

### [id-soft: doom-1993] Fixed-Size Active Set
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/model_gateway.py:148` — `# [id-soft: doom-1993] Fixed-Size Active Set — 32-entry clip range for O(1) culling`

### [id-soft: doom-1993] High-Bit Trick
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:130` — `# [id-soft: doom-1993] High-Bit Trick — flags as bitfield, high bit = system`
  - `src/omega/oracle/entity_registry.py:220` — `# [id-soft: doom-1993] High-Bit Trick — flag encoding using high bit`
  - `src/omega/oracle/entity_registry.py:559` — `# [id-soft: doom-1993] High-Bit Trick — set FLAG_WAD if WAD-loaded`

### [id-soft: doom-1993] Lazy Deletion
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/cvar_table.py:132` — `# [id-soft: doom-1993] Lazy Deletion — sentinel value for tombstoned entities`
  - `src/omega/memory_store.py:116` — `# [id-soft: doom-1993] Lazy Deletion — tombstone registry`
  - `src/omega/memory_store.py:209` — `# [id-soft: doom-1993] Lazy Deletion — tombstoned sessions raise typed error`
  - `src/omega/memory_store.py:424` — `# [id-soft: doom-1993] Lazy Deletion — tombstoned sessions reject new exchanges`
  - `src/omega/memory_store.py:512` — `# [id-soft: doom-1993] Lazy Deletion — reap tombstoned before slot reuse`
  - `src/omega/memory_store.py:690` — `# [id-soft: doom-1993] Lazy Deletion — tombstone marker`
  - `src/omega/oracle/entity_registry.py:267` — `# [id-soft: doom-1993] Lazy Deletion — tombstoned entity tracking`
  - `src/omega/oracle/entity_registry.py:617` — `# [id-soft: doom-1993] Lazy Deletion — set sentinel, keep in dict`
  - `src/omega/oracle/soul_edit_history.py:5` — `# [id-soft: doom-1993] Lazy Deletion — tombstone-centric approach to history`

### [id-soft: doom-1993] Multi-Index Entity
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/capability_registry.py:9` — `# [id-soft: doom-1993] Multi-Index Entity — dual-index lookup`
  - `src/omega/oracle/entity_registry.py:264` — `# [id-soft: doom-1993] Multi-Index Entity — dual-index lookup`
  - `src/omega/oracle/entity_registry.py:366` — `# [id-soft: doom-1993] Multi-Index Entity — populate capability index`
  - `src/omega/oracle/entity_registry.py:573` — `# [id-soft: doom-1993] Multi-Index Entity — populate capability index`

### [id-soft: doom-1993] Oracle Summoning Pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/oracle.py:9` — `# [id-soft: doom-1993] Oracle Summoning Pattern — Direct entity dispatch via _summon()`

### [id-soft: doom-1993] Precomputed Lookup
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-023 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/cvar_table.py:126` — `# [id-soft: doom-1993] Precomputed Lookup — embedding cache integrity marker`
  - `src/omega/oracle/backends/remote_provider.py:350` — `# [id-soft: doom-1993] Precomputed Lookup — fixed-size window scan`
  - `src/omega/oracle/selective_hydration.py:13` — `# [id-soft: doom-1993] Precomputed Lookup — embeddings precomputed at store time`
  - `src/omega/oracle/semantic_router.py:9` — `# [id-soft: doom-1993] Precomputed Lookup — entity embeddings precomputed at boot`
  - `src/omega/oracle/semantic_router.py:76` — `# [id-soft: doom-1993] Precomputed Lookup — boot-time entity vectors`
- **Vet Record**: vet-023 (UNKNOWN, 0/10)

### [id-soft: doom-1993] SSRF Gate ──
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/extractor.py:134` — `# ── [id-soft: doom-1993] SSRF Gate ──`

### [id-soft: doom-1993] SSRF Guard ──────────────────────────────────────────
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/security.py:29` — `# ── [id-soft: doom-1993] SSRF Guard ──────────────────────────────────────────`

### [id-soft: doom-1993] WAD System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/api_clients.py:128` — `# BASE CLIENT [id-soft: doom-1993] WAD System — swapable data sources`
  - `src/omega/library/api_clients.py:470` — `# ORCHESTRATOR [id-soft: doom-1993] WAD System — multi-source coordination`
  - `src/omega/oracle/__init__.py:5` — `# [id-soft: doom-1993] WAD System — module facade as WAD directory entry`
  - `src/omega/oracle/entity_registry.py:86` — `# [id-soft: doom-1993] WAD System — base IWAD identifier`
  - `src/omega/oracle/headroom.py:9` — `# [id-soft: doom-1993] WAD System — Data-driven separation of engine and content`
  - `src/omega/oracle/soul_distiller.py:12` — `# [id-soft: doom-1993] WAD System — soul.yaml is data-driven, not hardcoded.`
  - `src/omega/oracle/wad_loader.py:12` — `# [id-soft: doom-1993] WAD System — IWAD/PWAD separation with backward scan`
  - `src/omega/workers/background_researcher/searxng_client.py:114` — `# [id-soft: doom-1993] WAD System — graceful degradation on search failure`

### [id-soft: doom-1993] ZONEID
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/wad_loader.py:36` — `# [id-soft: doom-1993] ZONEID — size sentinel for file validation`

### [id-soft: doom-1993] ZONEID Pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/cvar_table.py:11` — `#   [id-soft: doom-1993] ZONEID Pattern — magic constant + validate_zoneid()`
  - `src/omega/cvar_table.py:80` — `# [id-soft: doom-1993] ZONEID Pattern — MemoryStore entry validation`
  - `src/omega/cvar_table.py:83` — `# [id-soft: doom-1993] ZONEID Pattern — EntityRegistry entity validation`
  - `src/omega/cvar_table.py:86` — `# [id-soft: doom-1993] ZONEID Pattern — circuit breaker state marker`
  - `src/omega/cvar_table.py:89` — `# [id-soft: doom-1993] ZONEID Pattern — trace/session lineage marker`
  - `src/omega/cvar_table.py:92` — `# [id-soft: doom-1993] ZONEID Pattern — ResourceGuard critical section guard`
  - `src/omega/cvar_table.py:95` — `# [id-soft: doom-1993] ZONEID Pattern — Subagent HandoffPacket integrity marker`
  - `src/omega/cvar_table.py:100` — `# [id-soft: doom-1993] ZONEID Pattern — Agent Presence dataclass integrity marker`
  - `src/omega/cvar_table.py:105` — `# [id-soft: doom-1993] ZONEID Pattern — Knowledge Signal integrity marker`
  - `src/omega/cvar_table.py:110` — `# [id-soft: doom-1993] ZONEID Pattern — Demand Signal integrity marker`
  - `src/omega/cvar_table.py:115` — `# [id-soft: doom-1993] ZONEID Pattern — Verification audit trail integrity marker`
  - `src/omega/cvar_table.py:118` — `# [id-soft: doom-1993] ZONEID Pattern — critical section atomic lock marker`
  - `src/omega/cvar_table.py:121` — `# [id-soft: doom-1993] ZONEID Pattern — Somatic snapshot integrity marker`
  - `src/omega/memory_store.py:433` — `# [id-soft: doom-1993] ZONEID Pattern — integrity marker`
  - `src/omega/oracle/entity_registry.py:128` — `# [id-soft: doom-1993] ZONEID Pattern — runtime marker, not serialized`
  - `src/omega/oracle/entity_registry.py:355` — `# [id-soft: doom-1993] ZONEID Pattern — set at load, not serialized`
  - `src/omega/oracle/entity_registry.py:581` — `# [id-soft: doom-1993] ZONEID Pattern — set runtime marker`
  - `src/omega/oracle/entity_registry.py:615` — `# [id-soft: doom-1993] ZONEID Pattern — pre-tombstone check`
  - `src/omega/oracle/feed_utils.py:9` — `# [id-soft: doom-1993] ZONEID Pattern — knowledge and demand signal validation`
  - `src/omega/oracle/health_monitor.py:100` — `# [id-soft: doom-1993] ZONEID Pattern — circuit breaker state marker`
  - `src/omega/oracle/health_monitor.py:161` — `# [id-soft: doom-1993] ZONEID Pattern — pre-transition integrity check`
  - `src/omega/oracle/health_monitor.py:215` — `# [id-soft: doom-1993] ZONEID Pattern — pre-transition integrity check`
  - `src/omega/oracle/link_p9_runtime.py:11` — `# [id-soft: doom-1993] ZONEID Pattern — used for presence integrity.`
  - `src/omega/oracle/link_p9_runtime.py:48` — `# [id-soft: doom-1993] ZONEID Pattern — presence integrity constant`
  - `src/omega/oracle/resource_guard.py:86` — `# [id-soft: doom-1993] ZONEID Pattern — runtime state marker`
  - `src/omega/oracle/skeptical_verifier.py:4` — `# [id-soft: doom-1993] ZONEID Pattern — verification of claim integrity`
  - `src/omega/oracle/soul_validator.py:9` — `# [id-soft: doom-1993] ZONEID Pattern — validated via soul_power and session counts.`
  - `src/omega/oracle/subagent_dispatcher.py:8` — `# [id-soft: doom-1993] ZONEID Pattern — used for packet integrity constant`
  - `src/omega/oracle/subagent_dispatcher.py:33` — `# [id-soft: doom-1993] ZONEID Pattern — handoff packet integrity constant`

### [id-soft: doom3-2004] Event System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/observability/__init__.py:753` — `# [id-soft: doom3-2004] Event System — structured event logging for observability.`
  - `src/omega/observability/regression_watcher.py:9` — `# [id-soft: doom3-2004] Event System — structured event logging for observability.`

### [id-soft: doom3-2004] Event-Driven State Machine
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/gnosis_proxy.py:5` — `# [id-soft: doom3-2004] Event-Driven State Machine — idEventDef pattern`

### [id-soft: doom3-2004] idEntity event system
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/link_p9_runtime.py:9` — `# [id-soft: doom3-2004] idEntity event system — agents emit typed events,`

### [id-soft: doom3-2004] idHeap
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/monitoring/__init__.py:15` — `# [id-soft: doom3-2004] idHeap — know your memory topology before allocating.`

### [id-soft: doom3bfg-2012] Job-Worker Queue
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-020 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/coordinator.py:5` — `# [id-soft: doom3bfg-2012] Job-Worker Queue`
- **Vet Record**: vet-020 (UNKNOWN, 0/10)

### [id-soft: quake-1996] 0.5s Realloc Grace
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/soul_edit_history.py:11` — `# [id-soft: quake-1996] 0.5s Realloc Grace — atomic write pattern`

### [id-soft: quake-1996] 4-Tier Memory
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/selective_hydration.py:18` — `# [id-soft: quake-1996] 4-Tier Memory — L3 principles live in the Cache tier`

### [id-soft: quake-1996] Atomic Swap
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/providers.py:869` — `# [id-soft: quake-1996] Atomic Swap — save old state before mutation`

### [id-soft: quake-1996] Download Size Guard ────────────────────────────────
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/security.py:130` — `# ── [id-soft: quake-1996] Download Size Guard ────────────────────────────────`

### [id-soft: quake-1996] Flat-Field Entity
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/gnosis_proxy.py:9` — `# [id-soft: quake-1996] Flat-Field Entity — all fields are data-driven`

### [id-soft: quake-1996] Grace Period
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-011 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/coordinator.py:90` — `# [id-soft: quake-1996] Grace Period — 0.5s for entity morphing,`
  - `src/omega/memory_store.py:76` — `# [id-soft: quake-1996] Grace Period — 0.5s delay before fully removing a`
  - `src/omega/memory_store.py:691` — `# [id-soft: quake-1996] Grace Period — wait TOMBSTONE_GRACE_SECONDS`
  - `src/omega/oracle/entity_registry.py:217` — `# [id-soft: quake-1996] Grace Period — 0.5s realloc delay`
  - `src/omega/oracle/selective_hydration.py:48` — `# [id-soft: quake-1996] Grace Period — 0.5s realloc grace for tombstoned slots`
- **Vet Record**: vet-011 (APPROVED (via vet-005/vet-006), 0/10)

### [id-soft: quake-1996] Hard-Boundary
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/api_clients.py:117` — `# TYPED ERRORS [id-soft: quake-1996] Hard-Boundary`

### [id-soft: quake-1996] Memory Zone
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/oracle.py:10` — `# [id-soft: quake-1996] Memory Zone — Long-term learning via soul.yaml`

### [id-soft: quake-1996] Path Scope Gate ──
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/extractor.py:282` — `# ── [id-soft: quake-1996] Path Scope Gate ──`

### [id-soft: quake-1996] Path Scope Guard ───────────────────────────────────
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/security.py:93` — `# ── [id-soft: quake-1996] Path Scope Guard ───────────────────────────────────`

### [id-soft: quake-1996] Right Approximation
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/observability/bleg.py:14` — `# [id-soft: quake-1996] Right Approximation — a simple JSON-keyword`

### [id-soft: quake-1996] Rollback
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/providers.py:880` — `# [id-soft: quake-1996] Rollback — restore old state on failure`

### [id-soft: quake-1996] Save-game pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/soul_distiller.py:9` — `# [id-soft: quake-1996] Save-game pattern — auto-save → summary → lesson.`

### [id-soft: quake-1996] Size Gate ──
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/extractor.py:144` — `# ── [id-soft: quake-1996] Size Gate ──`

### [id-soft: quake-1996] Surface Cache
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/monitoring/__init__.py:13` — `# [id-soft: quake-1996] Surface Cache — understand the physical fetch path`

### [id-soft: quake-1996] Temp Tier
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/memory_store.py:119` — `# [id-soft: quake-1996] Temp Tier — transient scratchpad memory`

### [id-soft: quake-1996] Thinker Chain
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/observability/regression_watcher.py:8` — `# [id-soft: quake-1996] Thinker Chain — periodic background task for health monitoring.`

### [id-soft: quake-1996] Thinker chain
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/link_p9_runtime.py:12` — `# [id-soft: quake-1996] Thinker chain — spawn → execute → reap lifecycle.`

### [id-soft: quake-1996] WAL journal mode
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/memory/fts_index.py:32` — `# [id-soft: quake-1996] WAL journal mode — allows concurrent reads`

### [id-soft: quake-1996] Zone Memory
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-008 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/mcp_runtime.py:104` — `# [id-soft: quake-1996] Zone Memory — TaskGroup auto-cancels`
  - `src/omega/mcp_runtime.py:115` — `# [id-soft: quake-1996] Zone Memory — free allocated resources on exit`
  - `src/omega/observability/__init__.py:577` — `# [id-soft: quake-1996] Zone Memory — resource guard with budget enforcement.`
  - `src/omega/observability/ufl.py:12` — `# [id-soft: quake-1996] Zone Memory — memory tagging pattern: each ledger`
  - `src/omega/oracle/context_builder.py:18` — `# [id-soft: quake-1996] Zone Memory — Cache (LRU) tier pattern`
  - `src/omega/vault/crypto.py:8` — `# [id-soft: quake-1996] Zone Memory — encrypted vault mirrors the tagged`
  - `src/omega/vault/key_vault.py:7` — `# [id-soft: quake-1996] Zone Memory — memory tagging pattern applied to key`
- **Vet Record**: vet-008 (APPROVED, 0/10)

### [id-soft: quake-1996] cvar pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_affinity.py:17` — `# [id-soft: quake-1996] cvar pattern — YAML-backed config, hot-reloadable`
  - `src/omega/oracle/model_gateway.py:625` — `# [id-soft: quake-1996] cvar pattern — YAML-backed config, hot-reloadable`
  - `src/omega/oracle/oracle.py:777` — `# [id-soft: quake-1996] cvar pattern — YAML-backed affinity DB, hot-reloadable`

### [id-soft: quake-1996] netchan
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-009 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/cli/oracle_cli.py:450` — `# [id-soft: quake-1996] netchan — ICS-S header via ics.py (single source of truth)`
- **Vet Record**: vet-009 (APPROVED, 0/10)

### [id-soft: quake3-1999] 4-Path VFS
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/backends/__init__.py:3` — `# [id-soft: quake3-1999] 4-Path VFS — provider chain is a search path`
  - `src/omega/oracle/wad_loader.py:16` — `# [id-soft: quake3-1999] 4-Path VFS — search order: active stack → _omega_default`

### [id-soft: quake3-1999] Cvar System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/cvar_table.py:12` — `#   [id-soft: quake3-1999] Cvar System — typed, queryable, auditable cvars`
  - `src/omega/observability/token_ledger.py:9` — `# [id-soft: quake3-1999] Cvar System — ledger persistence settings from cvar_table`
  - `src/omega/oracle/budget_gate.py:9` — `# [id-soft: quake3-1999] Cvar System — budget limits read from cvar_table`
  - `src/omega/oracle/providers.py:140` — `# [id-soft: quake3-1999] Cvar System — stop tokens from cvar table`
  - `src/omega/oracle/providers.py:203` — `# [id-soft: quake3-1999] Cvar System — stop tokens from cvar table`
  - `src/omega/oracle/providers.py:307` — `# [id-soft: quake3-1999] Cvar System — read from cvar_table for hot-reload`
  - `src/omega/oracle/providers.py:345` — `# [id-soft: quake3-1999] Cvar System — n_gpu_layers from cvar table`
  - `src/omega/oracle/providers.py:820` — `# [id-soft: quake3-1999] Cvar System — trace_id propagated`

### [id-soft: quake3-1999] Hard-Boundary
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_affinity.py:18` — `# [id-soft: quake3-1999] Hard-Boundary — affinity is separate routing layer above Entity`
  - `src/omega/oracle/entity_registry.py:133` — `# [id-soft: quake3-1999] Hard-Boundary — engine zone sentinel`
  - `src/omega/oracle/entity_registry.py:306` — `# [id-soft: quake3-1999] Hard-Boundary — metadata is a core field,`

### [id-soft: quake3-1999] Hard-Boundary Struct
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/api_clients.py:6` — `# [id-soft: quake3-1999] Hard-Boundary Struct — each client is a sealed`
  - `src/omega/oracle/entity_registry.py:225` — `# [id-soft: quake3-1999] Hard-Boundary Struct — engine zone vs game zone`

### [id-soft: quake3-1999] Response format difference:
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/providers.py:807` — `# [id-soft: quake3-1999] Response format difference:`

### [id-soft: quake3-1999] Right Approximation
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/providers.py:578` — `# [id-soft: quake3-1999] Right Approximation — use create_chat_completion()`
  - `src/omega/oracle/providers.py:765` — `# [id-soft: quake3-1999] Right Approximation — send system_prompt and user_query`
  - `src/omega/oracle/search_providers.py:2` — `# [id-soft: quake3-1999] Right Approximation — optimized search provider chain`
  - `src/omega/oracle/search_providers.py:210` — `# [id-soft: quake3-1999] Right Approximation — Neural Zoom pattern`

### [id-soft: quake3-1999] Triage Routing
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/oracle.py:11` — `# [id-soft: quake3-1999] Triage Routing — Intent classification and entity selection`

### [id-soft: quake3-1999] VM System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/capability_registry.py:5` — `# [id-soft: quake3-1999] VM System — capability-based dispatch`

### [id-soft: quake3-1999] cvar
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/observability/sovereignty.py:8` — `# [id-soft: quake3-1999] cvar — sovereignty ratio as a cvar-table metric`

### [id-soft: quake3-1999] netchan Rate Limiting
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/rate_limiter.py:5` — `# [id-soft: quake3-1999] netchan Rate Limiting — legacy of qport pacing,`

### [id-soft: quake3-1999] vvar pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:237` — `# [id-soft: quake3-1999] vvar pattern — dynamic set, not hardcoded`
