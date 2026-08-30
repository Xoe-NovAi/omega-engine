# 🔱 Heritage Audit Remediation Report
**Generated**: 2026-08-16T19:29:41.554786
**Total Tags Analyzed**: 65

## Summary

- **LEGITIMATE**: 0
- **METAPHORICAL**: 0
- **OVER-ATTRIBUTED**: 65

## OVER-ATTRIBUTED (65)

### [id-soft: doom-1993] BSP Culling
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-046 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/resource_guard.py:6` — `# [id-soft: doom-1993] BSP Culling — precompute hard parts, trade memory for compute`
- **Vet Record**: vet-046 (UNKNOWN, 0/10)

### [id-soft: doom-1993] Lazy Deletion
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:316` — `# [id-soft: doom-1993] Lazy Deletion — tombstone-based entity lifecycle (set sentinel, keep in dict)`
  - `src/omega/oracle/entity_registry.py:666` — `# [id-soft: doom-1993] Lazy Deletion — tombstone-based entity lifecycle (set sentinel, keep in dict)`

### [id-soft: doom-1993] Multi-Index Entity
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:313` — `# [id-soft: doom-1993] Multi-Index Entity — dual-index entity lookup (name + capability)`
  - `src/omega/oracle/entity_registry.py:415` — `# [id-soft: doom-1993] Multi-Index Entity — dual-index entity lookup (name + capability)`
  - `src/omega/oracle/entity_registry.py:622` — `# [id-soft: doom-1993] Multi-Index Entity — dual-index entity lookup (name + capability)`

### [id-soft: doom-1993] Precomputed Lookup
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-023 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/memory/sqlite_vec_adapter.py:22` — `# [id-soft: doom-1993] Precomputed Lookup — embedding cache integrity`
  - `src/omega/oracle/selective_hydration.py:13` — `# [id-soft: doom-1993] Precomputed Lookup — embeddings precomputed at store time`
- **Vet Record**: vet-023 (UNKNOWN, 0/10)

### [id-soft: doom-1993] ZONEID Pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:158` — `# [id-soft: doom-1993] ZONEID Pattern — magic constant for entity runtime integrity validation`
  - `src/omega/oracle/entity_registry.py:404` — `# [id-soft: doom-1993] ZONEID Pattern — magic constant for entity runtime integrity validation`
  - `src/omega/oracle/entity_registry.py:630` — `# [id-soft: doom-1993] ZONEID Pattern — magic constant for entity runtime integrity validation`

### [id-soft: doom3-2004] Event-Driven State Machine
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/gnosis_proxy.py:5` — `# [id-soft: doom3-2004] Event-Driven State Machine — idEventDef pattern`

### [id-soft: quake-1996] 4-Tier Memory
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/selective_hydration.py:18` — `# [id-soft: quake-1996] 4-Tier Memory — L3 principles live in the Cache tier`

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
  - `src/omega/oracle/entity_registry.py:269` — `# [id-soft: quake-1996] Grace Period — 0.5s realloc delay`
  - `src/omega/oracle/selective_hydration.py:48` — `# [id-soft: quake-1996] Grace Period — 0.5s realloc grace for tombstoned slots`
- **Vet Record**: vet-011 (APPROVED (via vet-005/vet-006), 0/10)

### [id-soft: quake-1996] WAL journal mode
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-036 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/memory/fts_index.py:68` — `# [id-soft: quake-1996] WAL journal mode — allows concurrent reads`
- **Vet Record**: vet-036 (UNKNOWN, 0/10)

### [id-soft: quake3-1999] Cvar System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/budget_gate.py:9` — `# [id-soft: quake3-1999] Cvar System — budget limits read from cvar_table`

### [id-soft: quake3-1999] vvar pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:289` — `# [id-soft: quake3-1999] vvar pattern — dynamic set, not hardcoded`

### [id-soft: vet-002] Right Approximation
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-042 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/providers.py:719` — `# [id-soft: vet-002] Right Approximation — fast heuristic over exact (create_chat_completion with template match)`
  - `src/omega/oracle/providers.py:908` — `# [id-soft: vet-002] Right Approximation — fast heuristic over exact (create_chat_completion with template match)`
  - `src/omega/oracle/search_providers.py:2` — `# [id-soft: vet-002] Right Approximation — fast heuristic search provider chain`
  - `src/omega/oracle/search_providers.py:218` — `# [id-soft: vet-002] Right Approximation — fast heuristic search provider chain`
- **Vet Record**: vet-042 (UNKNOWN, 0/10)

### [id-soft: vet-008] 0.5s Realloc Grace
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/soul_edit_history.py:11` — `# [id-soft: vet-008] 0.5s Realloc Grace — atomic write pattern`

### [id-soft: vet-008] Grace Period
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-011 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/coordinator.py:90` — `# [id-soft: vet-008] Grace Period — 0.5s for entity morphing,`
  - `src/omega/memory_store.py:84` — `# [id-soft: vet-008] Grace Period — wait TOMBSTONE_GRACE_SECONDS before full reclamation`
  - `src/omega/memory_store.py:666` — `# [id-soft: vet-008] Grace Period — wait TOMBSTONE_GRACE_SECONDS before full reclamation`
- **Vet Record**: vet-011 (APPROVED (via vet-005/vet-006), 0/10)

### [id-soft: vet-008] Lazy Deletion
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/cvar_table.py:101` — `# [id-soft: vet-008] Lazy Deletion — sentinel value for tombstoned entities`
  - `src/omega/memory_store.py:125` — `# [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle`
  - `src/omega/memory_store.py:227` — `# [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle`
  - `src/omega/memory_store.py:394` — `# [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle`
  - `src/omega/memory_store.py:487` — `# [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle`
  - `src/omega/memory_store.py:665` — `# [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle`
  - `src/omega/oracle/soul_edit_history.py:5` — `# [id-soft: vet-008] Lazy Deletion — tombstone-centric approach to history`

### [id-soft: vet-008] Zone Memory
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-008 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/mcp_runtime.py:200` — `# [id-soft: vet-008] Zone Memory — deterministic cleanup via zone-purge semantics`
  - `src/omega/mcp_runtime.py:211` — `# [id-soft: vet-008] Zone Memory — deterministic cleanup via zone-purge semantics`
  - `src/omega/memory/blocks.py:14` — `# [id-soft: vet-008] Zone Memory — Core blocks = Cache tier (always hot)`
  - `src/omega/observability/__init__.py:602` — `# [id-soft: vet-008] Zone Memory — resource guard with budget enforcement.`
  - `src/omega/observability/ufl.py:12` — `# [id-soft: vet-008] Zone Memory — memory tagging pattern: each ledger`
  - `src/omega/oracle/context_builder.py:17` — `# [id-soft: vet-008] Zone Memory — Cache (LRU) tier pattern`
- **Vet Record**: vet-008 (APPROVED, 0/10)

### [id-soft: vet-009] Memory Zone - Long-term learning via soul.yaml
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/oracle.py:10` — `# [id-soft: vet-009] Memory Zone - Long-term learning via soul.yaml`

### [id-soft: vet-009] netchan Rate Limiting
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/library/rate_limiter.py:5` — `# [id-soft: vet-009] netchan Rate Limiting — legacy of qport pacing,`

### [id-soft: vet-010] Multi-Index Entity
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/capability_registry.py:9` — `# [id-soft: vet-010] Multi-Index Entity — dual-index lookup`

### [id-soft: vet-011] Thinker Chain
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/observability/regression_watcher.py:8` — `# [id-soft: vet-011] Thinker Chain — periodic background task for health monitoring.`

### [id-soft: vet-011] Thinker chain
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/link_p9_runtime.py:12` — `# [id-soft: vet-011] Thinker chain — spawn → execute → reap lifecycle.`

### [id-soft: vet-015] ZONEID
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/wad_loader.py:36` — `# [id-soft: vet-015] ZONEID — size sentinel for file validation`

### [id-soft: vet-015] ZONEID Pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/cvar_table.py:11` — `#   [id-soft: vet-015] ZONEID Pattern — magic constants for runtime integrity.`
  - `src/omega/memory_store.py:403` — `# [id-soft: vet-015] ZONEID Pattern — integrity marker`
  - `src/omega/oracle/admission_controller.py:5` — `# [id-soft: vet-015] ZONEID Pattern — critical section markers`
  - `src/omega/oracle/feed_utils.py:9` — `# [id-soft: vet-015] ZONEID Pattern — knowledge and demand signal validation`
  - `src/omega/oracle/health_monitor.py:155` — `# [id-soft: vet-015] ZONEID Pattern — magic constant for circuit breaker state integrity`
  - `src/omega/oracle/health_monitor.py:236` — `# [id-soft: vet-015] ZONEID Pattern — magic constant for circuit breaker state integrity`
  - `src/omega/oracle/health_monitor.py:307` — `# [id-soft: vet-015] ZONEID Pattern — magic constant for circuit breaker state integrity`
  - `src/omega/oracle/link_p9_runtime.py:11` — `# [id-soft: vet-015] ZONEID Pattern — magic constant for agent presence integrity`
  - `src/omega/oracle/link_p9_runtime.py:48` — `# [id-soft: vet-015] ZONEID Pattern — magic constant for agent presence integrity`
  - `src/omega/oracle/resource_guard.py:5` — `# [id-soft: vet-015] ZONEID Pattern — critical sections guarded by ZONEID_PROBE marker`
  - `src/omega/oracle/resource_guard.py:218` — `# [id-soft: vet-015] ZONEID Pattern — runtime state marker`
  - `src/omega/oracle/skeptical_verifier.py:4` — `# [id-soft: vet-015] ZONEID Pattern — verification of claim integrity`
  - `src/omega/oracle/soul_validator.py:8` — `# [id-soft: vet-015] ZONEID Pattern — validated via soul_power and session counts.`
  - `src/omega/oracle/subagent_dispatcher.py:8` — `# [id-soft: vet-015] ZONEID Pattern — magic constant for handoff packet integrity`
  - `src/omega/oracle/subagent_dispatcher.py:40` — `# [id-soft: vet-015] ZONEID Pattern — magic constant for handoff packet integrity`

### [id-soft: vet-016] Cvar System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/cvar_table.py:15` — `#   [id-soft: vet-016] Cvar System — typed, queryable, auditable cvars`
  - `src/omega/observability/token_ledger.py:9` — `# [id-soft: vet-016] Cvar System — ledger persistence settings from cvar_table`
  - `src/omega/oracle/providers.py:221` — `# [id-soft: vet-016] Cvar System — typed config lookup from cvar_table`
  - `src/omega/oracle/providers.py:284` — `# [id-soft: vet-016] Cvar System — typed config lookup from cvar_table`
  - `src/omega/oracle/providers.py:388` — `# [id-soft: vet-016] Cvar System — typed config lookup from cvar_table`
  - `src/omega/oracle/providers.py:443` — `# [id-soft: vet-016] Cvar System — typed config lookup from cvar_table`
  - `src/omega/oracle/providers.py:969` — `# [id-soft: vet-016] Cvar System — typed config lookup from cvar_table`

### [id-soft: vet-016] cvar
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/observability/sovereignty.py:9` — `# [id-soft: vet-016] cvar — sovereignty ratio as a cvar-table metric`

### [id-soft: vet-016] cvar pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_affinity.py:17` — `# [id-soft: vet-016] cvar pattern — YAML-backed config, hot-reloadable`
  - `src/omega/oracle/model_gateway.py:763` — `# [id-soft: vet-016] cvar pattern — YAML-backed config, hot-reloadable`

### [id-soft: vet-016] cvar pattern - YAML-backed affinity DB, hot-reloadable
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/oracle.py:865` — `# [id-soft: vet-016] cvar pattern - YAML-backed affinity DB, hot-reloadable`

### [id-soft: vet-023] Precomputed Lookup
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-023 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/cvar_table.py:95` — `# [id-soft: vet-023] Precomputed Lookup — embedding cache integrity marker`
  - `src/omega/oracle/backends/remote_provider.py:377` — `# [id-soft: vet-023] Precomputed Lookup — fixed-size window scan`
  - `src/omega/oracle/semantic_router.py:9` — `# [id-soft: vet-023] Precomputed Lookup — entity embeddings precomputed at boot for O(1) routing`
  - `src/omega/oracle/semantic_router.py:76` — `# [id-soft: vet-023] Precomputed Lookup — entity embeddings precomputed at boot for O(1) routing`
- **Vet Record**: vet-023 (UNKNOWN, 0/10)

### [id-soft: vet-025] Hard-Boundary Struct
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-025 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/api_clients.py:6` — `# [id-soft: vet-025] Hard-Boundary Struct — each client is a sealed`
- **Vet Record**: vet-025 (UNKNOWN, 0/10)

### [id-soft: vet-026] Hard-Boundary
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-025 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/api_clients.py:117` — `# TYPED ERRORS [id-soft: vet-026] Hard-Boundary — typed error hierarchy as boundary layer`
- **Vet Record**: vet-025 (UNKNOWN, 0/10)

### [id-soft: vet-027] WAD System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-027 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/api_clients.py:128` — `# BASE CLIENT [id-soft: vet-027] WAD System — swapable, hot-pluggable data sources`
- **Vet Record**: vet-027 (UNKNOWN, 0/10)

### [id-soft: vet-028] WAD System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-027 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/api_clients.py:470` — `# ORCHESTRATOR [id-soft: vet-028] WAD System — swapable, hot-pluggable data sources`
- **Vet Record**: vet-027 (UNKNOWN, 0/10)

### [id-soft: vet-029] Job-Worker Queue
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-029 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/coordinator.py:5` — `# [id-soft: vet-029] Job-Worker Queue — atomic task decomposition with load coordination`
- **Vet Record**: vet-029 (UNKNOWN, 0/10)

### [id-soft: vet-030] SSRF Gate
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-030 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/extractor.py:135` — `# ── [id-soft: vet-030] SSRF Gate — O(1) cull of private IP ranges ──`
- **Vet Record**: vet-030 (UNKNOWN, 0/10)

### [id-soft: vet-031] Size Gate
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-031 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/extractor.py:145` — `# ── [id-soft: vet-031] Size Gate — fixed-timestep pre-check on download size ──`
- **Vet Record**: vet-031 (UNKNOWN, 0/10)

### [id-soft: vet-032] Path Scope Gate
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-032 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/extractor.py:283` — `# ── [id-soft: vet-032] Path Scope Gate — zone boundary enforcement for file paths ──`
- **Vet Record**: vet-032 (UNKNOWN, 0/10)

### [id-soft: vet-033] SSRF Guard
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-033 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/security.py:29` — `# ── [id-soft: vet-033] SSRF Guard — O(1) cull of forbidden IP ranges ──────────────────`
- **Vet Record**: vet-033 (UNKNOWN, 0/10)

### [id-soft: vet-034] Path Scope Guard
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-034 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/security.py:93` — `# ── [id-soft: vet-034] Path Scope Guard — zone boundary enforcement for file paths ──`
- **Vet Record**: vet-034 (UNKNOWN, 0/10)

### [id-soft: vet-035] Download Size Guard
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-035 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/library/security.py:130` — `# ── [id-soft: vet-035] Download Size Guard — fixed-timestep pre-check on download size ──`
- **Vet Record**: vet-035 (UNKNOWN, 0/10)

### [id-soft: vet-037] Temp Tier
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-037 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/memory_store.py:128` — `# [id-soft: vet-037] Temp Tier — transient scratchpad memory`
- **Vet Record**: vet-037 (UNKNOWN, 0/10)

### [id-soft: vet-038] Surface Cache
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-038 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/monitoring/__init__.py:13` — `# [id-soft: vet-038] Surface Cache — understand the physical fetch path`
- **Vet Record**: vet-038 (UNKNOWN, 0/10)

### [id-soft: vet-039] idHeap
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-039 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/monitoring/__init__.py:15` — `# [id-soft: vet-039] idHeap — know your memory topology before allocating.`
- **Vet Record**: vet-039 (UNKNOWN, 0/10)

### [id-soft: vet-040] Event System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-040 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/observability/__init__.py:763` — `# [id-soft: vet-040] Event System — structured event logging for observability.`
- **Vet Record**: vet-040 (UNKNOWN, 0/10)

### [id-soft: vet-041] Event System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-040 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/observability/regression_watcher.py:9` — `# [id-soft: vet-041] Event System — structured event logging for observability.`
- **Vet Record**: vet-040 (UNKNOWN, 0/10)

### [id-soft: vet-042] Right Approximation
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-042 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/observability/bleg.py:14` — `# [id-soft: vet-042] Right Approximation — a simple JSON-keyword`
- **Vet Record**: vet-042 (UNKNOWN, 0/10)

### [id-soft: vet-043] WAD System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-027 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/__init__.py:5` — `# [id-soft: vet-043] WAD System — module facade as WAD directory entry`
  - `src/omega/oracle/headroom.py:9` — `# [id-soft: vet-043] WAD System — Data-driven separation of engine and content`
  - `src/omega/oracle/wad_loader.py:11` — `# [id-soft: vet-043] WAD System — IWAD/PWAD separation with backward scan`
- **Vet Record**: vet-027 (UNKNOWN, 0/10)

### [id-soft: vet-044] 4-Path VFS
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-044 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/backends/__init__.py:3` — `# [id-soft: vet-044] 4-Path VFS — provider chain is a search path`
  - `src/omega/oracle/wad_loader.py:15` — `# [id-soft: vet-044] 4-Path VFS — search order: active stack → _omega_default`
- **Vet Record**: vet-044 (UNKNOWN, 0/10)

### [id-soft: vet-045] SEDA Ring-Bus
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/cli/fleet_status_tui.py:250` — `# [id-soft: vet-045] SEDA Ring-Bus — replaces polling with pub/sub.`
  - `src/omega/research/sediment.py:14` — `# [id-soft: vet-045] SEDA Ring-Bus — inspired by LMAX Disruptor ring buffer pattern.`

### [id-soft: vet-045] VM System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-045 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/capability_registry.py:5` — `# [id-soft: vet-045] VM System — capability-based dispatch`
- **Vet Record**: vet-045 (UNKNOWN, 0/10)

### [id-soft: vet-046] BSP Culling
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-046 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/memory/spatial.py:12` — `# [id-soft: vet-046] BSP Culling — Spatial partitioning for efficiency`
  - `src/omega/oracle/context_builder.py:282` — `# [id-soft: vet-046] BSP Culling — top-K principles only`
  - `src/omega/oracle/model_gateway.py:889` — `# [id-soft: vet-046] BSP Culling — O(1) pre-check skips broken providers`
  - `src/omega/oracle/selective_hydration.py:8` — `# [id-soft: vet-046] BSP Culling — O(1) culling of irrelevant principles`
  - `src/omega/oracle/semantic_router.py:8` — `# [id-soft: vet-046] BSP Culling — O(1) culling of irrelevant entities via precomputed routing structure`
  - `src/omega/oracle/semantic_router.py:110` — `# [id-soft: vet-046] BSP Culling — O(1) culling of irrelevant entities via precomputed routing structure`
  - `src/omega/oracle/spatial_resolver.py:11` — `# [id-soft: vet-046] BSP Culling — Spatial partitioning for efficiency`
- **Vet Record**: vet-046 (UNKNOWN, 0/10)

### [id-soft: vet-047] Hard-Boundary
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-025 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/entity_affinity.py:18` — `# [id-soft: vet-047] Hard-Boundary — affinity is separate routing layer above Entity`
- **Vet Record**: vet-025 (UNKNOWN, 0/10)

### [id-soft: vet-048] WAD System
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-027 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:116` — `# [id-soft: vet-048] WAD System — base IWAD identifier`
- **Vet Record**: vet-027 (UNKNOWN, 0/10)

### [id-soft: vet-052] Hard-Boundary Struct
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-025 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:277` — `# [id-soft: vet-052] Hard-Boundary Struct — engine zone vs game zone`
- **Vet Record**: vet-025 (UNKNOWN, 0/10)

### [id-soft: vet-053] Hard-Boundary
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-025 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:163` — `# [id-soft: vet-053] Hard-Boundary — engine-zone vs game-zone boundary enforcement`
  - `src/omega/oracle/entity_registry.py:355` — `# [id-soft: vet-053] Hard-Boundary — engine-zone vs game-zone boundary enforcement`
- **Vet Record**: vet-025 (UNKNOWN, 0/10)

### [id-soft: vet-054] High-Bit Trick
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-047 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:160` — `# [id-soft: vet-054] High-Bit Trick — bitfield flag encoding with high-bit markers`
  - `src/omega/oracle/entity_registry.py:272` — `# [id-soft: vet-054] High-Bit Trick — bitfield flag encoding with high-bit markers`
  - `src/omega/oracle/entity_registry.py:608` — `# [id-soft: vet-054] High-Bit Trick — bitfield flag encoding with high-bit markers`
- **Vet Record**: vet-047 (UNKNOWN, 0/10)

### [id-soft: vet-055] Fixed-Size Active Set
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-055 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/model_gateway.py:137` — `# [id-soft: vet-055] Fixed-Size Active Set — 32-entry clip range for O(1) culling`
- **Vet Record**: vet-055 (UNKNOWN, 0/10)

### [id-soft: vet-056] Oracle Summoning Pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/memory/blocks.py:13` — `# [id-soft: vet-056] Oracle Summoning Pattern — Blocks injected at summon time`

### [id-soft: vet-056] Oracle Summoning Pattern - Direct entity dispatch via _summon()
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/oracle.py:9` — `# [id-soft: vet-056] Oracle Summoning Pattern - Direct entity dispatch via _summon()`

### [id-soft: vet-056] Triage Routing - Intent classification and entity selection
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/oracle.py:11` — `# [id-soft: vet-056] Triage Routing - Intent classification and entity selection`

### [id-soft: vet-057] Atomic Swap
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-057 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/providers.py:1018` — `# [id-soft: vet-057] Atomic Swap — save old state before mutation`
- **Vet Record**: vet-057 (UNKNOWN, 0/10)

### [id-soft: vet-058] Rollback
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-058 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/oracle/providers.py:1029` — `# [id-soft: vet-058] Rollback — restore old state on failure`
- **Vet Record**: vet-058 (UNKNOWN, 0/10)

### [id-soft: vet-065] ZONEID Pattern
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/entity_registry.py:664` — `# [id-soft: vet-065] ZONEID Pattern — magic constant for entity runtime integrity validation`

### [id-soft: vet-066] idEntity event system
- **Classification**: OVER-ATTRIBUTED
- **Reason**: No vet record found for this pattern
- **Remediation**: Either create a vet record with score >= 7, or remove the tag
- **Occurrences**:
  - `src/omega/oracle/link_p9_runtime.py:9` — `# [id-soft: vet-066] idEntity event system — agents emit typed events,`

### [id-soft: vet-071] netchan
- **Classification**: OVER-ATTRIBUTED
- **Reason**: Vet record vet-009 score: 0/10 (minimum 7)
- **Remediation**: Remove tag or re-vet with stronger justification
- **Occurrences**:
  - `src/omega/cli/oracle_cli.py:484` — `# [id-soft: vet-071] netchan — ICS-S header via ics.py (single source of truth)`
- **Vet Record**: vet-009 (APPROVED, 0/10)
