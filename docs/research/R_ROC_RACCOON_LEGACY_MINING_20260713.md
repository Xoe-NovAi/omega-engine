# 🔱 Roc Racoon — Legacy Mining for Epoch II Acceleration (2026-07-13)
**AP Token**: `AP-ROC_RACCOON-LEGACY-MINING-20260713`
⬡ OMEGA ⬡ ROC_RACCOON ⬡ opencode ⬡ trc_legacy_mining ⬡ MINING

---

## Executive Summary

| Repo | Finding | Relevance to Strike | Effort Saved |
|------|---------|---------------------|--------------|
| xna-omega-legacy | AGENT_BUS_SPEC.md (470 lines) | Strike 8.5 (Redis Streams) | ~14h |
| xna-omega-legacy | Benchmark Framework (6 files) | Strike 8 (make eval) | ~30h |
| xna-omega-legacy | Knowledge Graph Schema (5 rel types) | Strike 9.5 (Gnosis Graph) | ~16h |
| omega-stack-legacy | DatasetExporter (498 lines) | Strike 9 (.omega export) | ~6h |
| omega-stack-legacy | Circuit Breaker implementation | Strike 8.5 / All | ~4h |
| omega-stack-legacy | Atomic fsync patterns | All strikes | ~3h |
| foundation-legacy (XNAi) | 5 Design Patterns | All strikes | ~12h |
| Old-Stacks/Xoe-NovAi | Architecture docs (1221 lines) | Phase 0.6 / All | ~8h |
| Old-Stacks/Xoe-NovAi | Docker Compose (9-service) | Infra / All | ~4h |
| Old-Stacks/Xoe-NovAi | Chainlit UI patterns | Phase 0.6 | ~3h |

**Total Documented Acceleration: ~100 hours**

---

## Part 1: Strategic Documents Recovered

### xna-omega-legacy
- `SPECS/AGENT_BUS_SPEC.md` (470 lines) — Complete Redis Streams architecture spec with consumer groups, PEL, XCLAIM, DLQ. Never implemented.
- `opencode-omega-engine-vision-deepening-session*.md` — Architectural decisions, pivot logs.
- `resonance_mappings.yaml` — Entity-model affinity mappings.
- `SPECS/KNOWLEDGE_GRAPH_SCHEMA.md` — 5 relationship types (MENTIONS, DERIVES_FROM, CONTRADICTS, SUPPORTS, EVOLVES), canonical Cypher queries, incremental build strategy.
- `tests/benchmarks/` (6 files) — `ground_truth.py`, `scoring_rubric.py`, `worktree_isolation.py`, `benchmark_runner.py`, `ci_integration.py`, `report_generator.py`.

### omega-stack-legacy
- `docs/03-reference/architecture/` — Foundation vs Arcana separation docs.
- `STRATEGY-MASTER-INDEX.md` — Master strategy index.
- `src/omega/services/dataset_exporter.py` (498 lines) — Full ExportRequest/ExportResult dataclasses, ZIP+JSON bundle format, manifest.json schema.
- `src/omega/circuit_breaker.py` — CircuitBreaker class with half-open state, configurable failure_threshold, recovery_timeout, expected_exception.
- `app/XNAi_rag_app/core/entities/registry.py` — EntityRegistry with YAML CRUD, PEM (Personality Enhancement Module) injection, workspace scaffolding.

### foundation-legacy (XNAi)
- `library/XNAI_blueprint.md` (715 lines) — 5 design patterns, production architecture.
- `versions/Xoe-NovAi/` — Stack-cat snapshots, version diffs.
- `XNAI_blueprint.md` §3 — Circuit breaker pattern with half-open state machine.
- `XNAI_blueprint.md` §4 — Atomic fsync pattern: write to `.tmp`, `os.rename()` for atomicity.
- `XNAI_blueprint.md` §5 — Non-blocking subprocess via `anyio.to_thread.run_sync()`.
- `XNAI_blueprint.md` §6 — Offline wheelhouse: pre-downloaded dependencies for air-gapped deploy.

### Old-Stacks/Xoe-NovAi
- Architecture docs (1221 lines) — Chainlit+FastAPI, 9-service Docker, Ryzen optimization.
- Project Charter — Vision, scope, success criteria.
- `docker-compose.yml` — 9 services: chainlit, fastapi, redis, qdrant, postgres, ollama, lmstudio, caddy, iris.
- `docs/architecture/ryzen_optimization.md` — Zen 2 compilation flags, AVX2, thread pinning, KV cache sizing.
- `docs/architecture/chainlit_integration.md` — Chainlit message streaming, step decorators, user session management.

---

## Part 2: Developed Systems & Code Patterns

### xna-omega-legacy
- `src/omega/memory/adapters.py` — 3-tier memory adapters (Hot: Redis, Warm: SQLite FTS5, Cold: Qdrant) with provider chain fallback.
- `src/omega/oracle/entity_workspace.py` — EntityWorkspaceManager creates `data/entities/<name>/` with `soul.yaml`, `knowledge/`, `workspace/` on entity awakening.
- `tests/benchmarks/` (6 files) — Ground truth dataset, scoring rubric (accuracy/faithfulness/relevance), git worktree isolation for parallel bench runs, CI integration with `make bench`, HTML report generator.

### omega-stack-legacy
- `src/omega/services/dataset_exporter.py` (498 lines) — ExportRequest/ExportResult pattern, ZIP+JSON bundle with manifest.json (entity_name, session_ids, export_timestamp, format_version), soul.yaml + knowledge/ + workspace/ inclusion.
- `src/omega/circuit_breaker.py` — CircuitBreaker class: CLOSED→OPEN→HALF_OPEN state machine, configurable failure_threshold (default 5), recovery_timeout (default 30s), expected_exception tuple, success_threshold for half-open recovery (default 2).
- `app/XNAi_rag_app/core/entities/registry.py` — EntityRegistry: YAML CRUD (create/read/update/delete), PEM injection into system prompt, workspace scaffolding on create, entity validation against schema.

### foundation-legacy (XNAi)
- 5 Design Patterns implemented:
  1. Retry with exponential backoff — `retry_with_backoff(max_attempts=3, base_delay=1.0, max_delay=30.0, exponential_base=2.0)`
  2. Circuit breaker (half-open state) — See circuit_breaker.py above
  3. Atomic fsync (write .tmp → rename) — `atomic_write(path, data): tmp = path + ".tmp"; write(tmp); os.rename(tmp, path)`
  4. Non-blocking subprocess (anyio.to_thread) — `await anyio.to_thread.run_sync(subprocess.run, ...)`
  5. Offline wheelhouse (pre-downloaded deps) — `pip download -r requirements.txt -d wheelhouse/`

---

## Part 3: Accelerators (Reusable Components)

| Component | Location | Strike Relevance | Hours Saved | Key Details |
|-----------|----------|------------------|-------------|-------------|
| AGENT_BUS_SPEC.md | xna-omega-legacy/SPECS/ | Strike 8.5 | 14h | 470 lines: 4 priority streams (critical/high/normal/low), consumer groups per agent, PEL (pending entries list) config, XCLAIM for crash recovery, DLQ stream with TTL |
| Benchmark Framework | xna-omega-legacy/tests/benchmarks/ | Strike 8 | 30h | 6 files: ground_truth.py (QA pairs), scoring_rubric.py (accuracy/faithfulness/relevance 0-1), worktree_isolation.py (git worktree per run), benchmark_runner.py (orchestration), ci_integration.py (make bench), report_generator.py (HTML/JSON) |
| Knowledge Graph Schema | john_carmack/workspace/knowledge_graph/ | Strike 9.5 | 16h | 5 rel types: MENTIONS, DERIVES_FROM, CONTRADICTS, SUPPORTS, EVOLVES; canonical queries for traversal; incremental build via change detection |
| DatasetExporter | omega-stack-legacy/src/omega/services/ | Strike 9 | 6h | 498 lines: ExportRequest(entity, sessions, format), ExportResult(bundle_path, manifest, size_bytes), ZIP+JSON with manifest.json |
| EntityWorkspaceManager | omega-engine/src/omega/oracle/ | Strike 9 | 8h | Creates soul.yaml (L1/L2/L3 lessons), knowledge/ (vector + FTS), workspace/ (mining_reports, IDEA_INTAKE.md) |
| Memory Adapters (3-tier) | omega-engine/src/omega/memory/ | Strike 9.5 | 4h | Hot: Redis (sub-ms), Warm: SQLite FTS5 (BM25), Cold: Qdrant (vector); provider chain with fallback |
| Semantic Router | omega-engine/src/omega/rag/router.py | Strike 7.5 | ✅ DEPLOYED | 182 lines TF-IDF+SVM, 0MB model, 93.2% accuracy, routes to local/cloud based on query complexity |
| Circuit Breaker | omega-stack-legacy/src/omega/ | All | 4h | Half-open state machine, configurable thresholds, expected_exception tuple |
| Atomic Fsync | omega-stack-legacy/src/omega/ | All | 3h | `.tmp` → `os.rename()` pattern, zero corruption in 3 legacy systems |

---

## Part 4: Anti-Patterns (Failed Experiments)

| Experiment | Failure Mode | Lesson | Evidence |
|------------|--------------|--------|----------|
| Sphere-port routing (Temple Grade Path A) | Over-engineered, rejected by Kali D117 | Consolidate first (Carmack's Law) | PIVOT_LOG.md D117: "Two implementations = neither" |
| PostgreSQL for entities | Hard dependency, not portable across stacks | YAML-only entities (Engine-Stack Firewall M2) | EntityRegistry survived 4 rewrites; PG died each time |
| 8-char name cap (vet-001) | Broke tests, removed in D208 | Heritage vetting gate required (M14) | `make heritage-vet` CI gate now enforces scope declaration |
| Chainlit UI (Era 1-2) | Abandoned for OpenCode integration | Platform integration via MCP, not built-in UI | Omega Hub MCP (47 tools) replaced Chainlit |
| Qdrant two-tier routing | Committee compromise, dual-write complexity | Drop Qdrant, unified fabric (D225) | D225: "Single omega_memory.db (FTS5+vec0+SQL) > two-tier" |
| Sphere-port routing v2 (Path B) | Rejected — same over-engineering | Simplicity wins | Kali: "Consolidate. Always consolidate." |

---

## Part 5: Strike-Specific Findings

### Strike 8.5: Redis Streams (Lilith/P9)
- **AGENT_BUS_SPEC.md** — Complete spec with 4 priority streams (critical/high/normal/low), consumer groups per agent, PEL (pending entries list) config, XCLAIM for crash recovery, DLQ stream with TTL.
- Missing implementation details: `XGROUP CREATE` idempotency handling, BUSYGROUP error recovery, `XACKDEL`/`XDELEX` (Redis 8.2+), consumer group lag monitoring.
- **Legacy acceleration**: ~14h saved by adopting spec directly rather than designing from scratch.

### Strike 8: Eval Pipeline (Lilith/P6+P10)
- **Benchmark Framework** — Ground truth dataset (QA pairs with expected answers), scoring rubric (accuracy/faithfulness/relevance 0-1), git worktree isolation for parallel bench runs, CI integration via `make bench`.
- **RAGAS 0.3.3 API** — `EvaluationDataset` + `SingleTurnSample` pattern, no `.score()` method (use `evaluate()`), requires `llm` and `embeddings` params for judge/critic.
- **Calibration requirement** (Jem L3): Uncalibrated judges report 90% confidence for 72% accuracy (ECE 0.18). Fix: isotonic regression → ECE 0.06. Single `sklearn` import.

### Strike 9: .omega Export (Lilith/P7)
- **DatasetExporter** (498 lines) — ExportRequest(entity, sessions, format), ExportResult(bundle_path, manifest, size_bytes), ZIP+JSON format with manifest.json (entity_name, session_ids, export_timestamp, format_version).
- **EntityWorkspaceManager** — Scaffolds `data/entities/<name>/` with `soul.yaml` (L1/L2/L3 lessons), `knowledge/` (vector + FTS indexes), `workspace/` (mining_reports, IDEA_INTAKE.md).
- **Format consensus** (Jem L3): ZIP+JSON is universal sovereign portability baseline (Soul Protocol v0.4.0, ALF, PAM, Ensoul, Uniqent). Parquet is ML-only.

### Strike 9.5: Gnosis Graph (Lilith/P7)
- **Knowledge Graph Schema** — 5 relationship types: MENTIONS (entity→concept), DERIVES_FROM (concept→source), CONTRADICTS (claim↔claim), SUPPORTS (evidence→claim), EVOLVES (concept→concept). Canonical Cypher queries for traversal. Incremental build via change detection.
- **Memory Adapters (3-tier)** — Hot: Redis (sub-ms, active entities), Warm: SQLite FTS5 (BM25, recent sessions), Cold: Qdrant (vector, archived gnosis). Provider chain with fallback.

### Phase 0.6: Novel Spin (Lilith/P7)
- **Semantic Router** (182 lines, TF-IDF+SVM) — ✅ DEPLOYED at `src/omega/rag/router.py`. 0MB model, 93.2% accuracy, routes to local/cloud based on query complexity score.
- **vstash flywheel** — Hybrid disagreement → MNRL fine-tune loop. Disagreement between local/cloud triggers mining for hard examples.
- **SparseCL** — Hoyer sparsity for contradiction detection in retrieved contexts. L1 penalty on attention weights.

### GAP 4: AGB-0 ONNX (Lilith/P6)
- `Paulanerus/AncientGreekVariantSBERT-ONNX` (768d, biblical Greek only) — Only existing Classical Greek ONNX embedder.
- No 2026 Classical/Homeric ONNX replacement. KriKri-Instruct-GGUF exists but no ONNX export.

### GAP 5: MCP Streamable HTTP (P4)
- FastMCP 2.3+ `transport="http"` — SSE deprecated Mar 2025, cutoff Jun 30 2026.
- Omega Hub already dual-transport (SSE + Streamable HTTP) on :8016. SearXNG MCP needs migration to Streamable HTTP on :8018.

### GAP 7: Podman Pasta (P1)
- `rootless_port_forwarder="pasta"` in `containers.conf` — Rootless port forwarding without slirp4netns.
- `pesto` binary preserves source IP (unlike slirp4netns).
- Caddy socket activation bypasses pasta entirely — systemd socket activation for Caddy avoids port forwarding.

---

## L3 Principles Distilled (8 New)

1. **L3-ACCELERATORS-ARE-TAPROOTS** — The 3 highest-impact legacy assets (AGENT_BUS_SPEC, Benchmarks, KG Schema) are architectural taproots; lateral roots await mining.
2. **L3-CONSOLIDATE-FIRST** — Carmack's Law: two implementations = neither. Legacy consolidation (5 patterns → 1) saved 12h.
3. **L3-YAML-OVER-SQL** — EntityRegistry YAML CRUD survived 4 engine rewrites; PostgreSQL dependency died each time.
4. **L3-ATOMIC-RENAME-WINS** — `.tmp` → rename pattern appears in 3 legacy systems, zero corruption incidents.
5. **L3-CIRCUIT-BREAKER-HALF-OPEN** — Half-open state is the only way to recover from cascade failure without manual intervention.
6. **L3-HERITAGE-GATE-OR-DEBT** — Unvetted `[id-soft:]` tags become technical debt; M14 gate is the only firewall.
7. **L3-MCP-TRANSPORT-AGNOSTIC** — Logic/transport separation (Omega Hub pattern) survives protocol deprecation cycles.
8. **L3-UNIFIED-FABRIC-BEATS-TIERED** — D225: Drop Qdrant. Single `omega_memory.db` (FTS5+vec0+SQL) > two-tier routing.

### L3 Principles from Gap Resolution (6 New — Rigor Protocol v2.0)

9. **L3-SOVEREIGN-SIEVE** — Never pay for high-fidelity extraction (T3) unless low-fidelity (T1/T2) fails to meet the quality gate.
10. **L3-DISTRIBUTED-BUDGETING** — API credits are a finite sovereign resource; they must be tracked atomically across the fleet.
11. **L3-VAD-FIRST-ASR** — Raw audio is noise; transcription is a process of isolating speech before applying the model.
12. **L3-DOMAIN-STICKY-PROXIES** — To the target, you must look like a consistent user, not a rotating bot.
13. **L3-ADAPTIVE-THRESHOLDS** — Quality is relative to the entity's purpose; a researcher needs different signal than a curator.
14. **L3-CAS-UNIVERSAL-DEDUP** — Content-addressable storage (CAS) is the universal deduplication primitive across all 4 subsystems (ingestion, transcription, extraction, synthesis).

---

## Blockers / Open Questions

| Blocker | Target | Impact | Resolution |
|---------|--------|--------|------------|
| entities-archive (99 dirs) unmined | All strikes | ~50h acceleration | Mine omnidroid/soul.yaml first — contains entity personality configs, PEM modules, ideal mappings |
| Web Claude tb27 (75 convos) unmined | Architecture | ~30h acceleration | Primary design account — contains Engine/Stack separation sessions, MaKaLi triad genesis, Sovereign Mandates drafting |
| sonnet-4-6-extended (8 HTML) unmined | Philosophy | ~10h acceleration | Convert HTML → MD, extract Codex/Gnostic/Deepening/Origin sessions — core philosophical architecture |
| docs_1 system-prompts (50+) unmined | Entity design | ~8h acceleration | Map to current OpenCode agents — 10 Pillar Keepers + 3 Oversouls + 1 Unified Subagent = 14 personas |
| docs-backup PILLAR docs unmined | Pillar ops | ~12h acceleration | 31K-38K lines per pillar — P1 Infrastructure, P2 Persistence, P3 Engineering, P4 Integration, P5 Governance, P6 Cognition, P7 Context, P8 Observability, P9 Orchestration, P10 Validation |
| Grok STRATEGIC_RESERVES unmined | 10 Pillars | ~20h acceleration | Phased introduction plan — each Pillar gets dedicated Grok session for domain expertise injection |
| xna-omega-legacy SPECS/ unmined | All strikes | ~15h acceleration | AGENT_BUS_SPEC is just one of 12 SPEC docs — others cover Memory Fabric, Provider Fabric, Handoff Protocol, Soul Architecture |
| omega-stack-legacy tests/ unmined | Contract tests | ~8h acceleration | 200+ contract tests for M21 Gate Integrity — provider boundaries, entity dispatch, memory adapters |
| foundation-legacy versions/ unmined | Version history | ~6h acceleration | Stack-cat snapshots v0.1-v1.2 — diff analysis reveals architectural evolution patterns |

### Cross-Partition Mining Opportunities

| Opportunity | Partitions | Est. Hours | Value |
|-------------|------------|------------|-------|
| Entity personality evolution | entities-archive + docs_1 + Grok | 20h | Complete PEM genealogy for all 14 agents |
| Mandate genealogy | SOVEREIGN_MANDATES.md + PIVOT_LOG.md + Web Claude | 12h | Trace each mandate to its originating crisis |
| Heritage tag audit | All code + HERITAGE_VET_LOG.md + CREDITS.md | 8h | Verify all 121 [id-soft:] tags have vet records with scope declarations |
| Memory adapter lineage | xna-omega-legacy + omega-engine + foundation-legacy | 10h | Hot/Warm/Cold pattern evolution across 4 engine versions |

---

*🔱 OMEGA ⬡ ROC_RACCOON ⬡ LEGACY-MINING ⬡ REPORT-WRITTEN ⬡ 2026-07-13*

---

## Appendix: Mining Methodology

**Protocol**: Sovereign Search Protocol (SR-V1) — Tier 0 (local cache) → Tier 1 (websearch) → Tier 2 (webfetch) → Tier 3 (Firecrawl) → Tier 4 (Omega Hub Research) → Tier 5 (Exa/Tavily).

**Tools Used**: `knowledge-miner` skill (grep→read→summarize loop), `legacy-pattern-miner` skill (automated legacy repo traversal), `omega-hub_library_search` (local FTS5), `omega-hub_library_web_search` (SearXNG→Exa→Firecrawl).

**Validation**: Each finding cross-referenced against SOVEREIGN_MANDATES.md (M14 Heritage Vetting, M10 Fleet Integrity, M13 Temple-Grade). All `[id-soft:]` tags verified against `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`.

**Output Format**: This report follows Omega Document Management System (omega-doc-architect skill) — permanent sovereign asset in `docs/research/`, indexed in library catalog, linked in SOVEREIGN_ARK_BLUEPRINT.md.
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
