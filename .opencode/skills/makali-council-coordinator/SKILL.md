# 🔱 MaKaLi Council Coordinator Skill
# ⬡ OMEGA ⬡ KALI ⬡ trc_council ⬡ SCAFFOLD
#
# Unified MultiAgentCoordinator for MaKaLi Parallel Council.
# Handles both meditation mode (10-voice sequential) and council mode (parallel nodes → oversouls → Kali).

## Purpose
Orchestrate the 5-stage MaKaLi Parallel Council using `task()` tool, file-based handoffs, and Hivemind coordination. Zero-inference-cost Report Digestion Layer (Phase 1.5) optimizes node outputs for oversoul consumption.

## Architecture
```
Phase 1: Nodes        → 9 independent reports
Phase 1.5: Digestion    → stack-cat + Python → 2 optimized digests (ZERO inference cost)
Phase 2: Oversouls      → Ma'at reads BUILD_SIDE_DIGESTED, Lilith reads RUN_SIDE_DIGESTED
Phase 3: Kali Synthesis → reads 2 oversoul reports → FINAL_SYNTHESIS.md + research gaps
Phase 4: Research       → execute gaps via configured tier (local/cloud/auto/deferred)
```

## Usage
```bash
# Full council (default)
omega council "topic" --profile local_16gb

# Meditation (10-voice sequential)
omega council "topic" --mode meditation

# Cloud-unconstrained
omega council "topic" --profile cloud_unconstrained
```

## Inputs
- `topic`: The question/problem for the council
- `mode`: "council" (default, parallel) | "meditation" (sequential, 10-voice)
- `profile`: Hardware profile preset (local_16gb, local_8gb, cloud_unconstrained, hybrid_local_nodes)
- `config_path`: Path to custom council config (default: `config/council.yaml`)
- `session_id`: Unique identifier for this council run

## Stage 0: Preconditions
Before any dispatch:
1. Load config from `config/council.yaml` + profile override
2. Auto-detect hardware (RAM, CPU, thermal)
3. Select execution mode (parallel/batch/serial)
4. Initialize WAL checkpoint
5. Check circuit breaker state
6. Verify provider availability for assigned model tiers

## Phase 1: Node Dispatch
1. For each node in Ma'at's domain (N1, N3, N4, N5):
   - Dispatch `task()` with node agent, topic, output path
   - Nodes write independent reports — NO inter-node reads
2. For each node in Lilith's domain (N6, N7, N8, N9, N10):
   - Dispatch `task()` with node agent, topic, output path
3. Execute according to mode:
   - `parallel`: All 9 nodes simultaneously (cloud profile)
   - `batch_4`: 4 at a time (16GB profile)
   - `batch_2`: 2 at a time (8GB profile)
   - `serial_independent`: One at a time (constrained)
4. Wait for ALL completions — verify report files exist
5. WAL checkpoint: Phase 1 complete

## Phase 1.5: Report Digestion
1. Run `ReportDigester` on node outputs:
   - stack-cat concatenation of all 4/5 reports per side
   - Executive summaries (auto-extracted via Python)
   - Cross-reference index (mandate tags, entities, shared keywords)
   - Conflict detection (numeric mismatches, mandate compliance differences)
   - Mandate compliance matrix ([M1]-[M23] per node)
   - Token budget allocation for oversoul context window
2. Python only — ZERO inference cost (~50ms for typical reports)
3. Write: `BUILD_SIDE_DIGESTED.md` + `RUN_SIDE_DIGESTED.md`
4. M23: If digestion fails, fall back to raw stack-cat concatenation
5. WAL checkpoint: Phase 1.5 complete

**Oversoul Input Improvement**: 
Before Phase 2, each oversoul reads 1 file (digested) instead of 4/5 raw reports.
- Token reduction: ~60%
- Added intelligence: cross-references, conflict map, mandate matrix, budget allocation

## Phase 2: Oversoul Distillation
1. Dispatch Ma'at task:
   - Read `BUILD_SIDE_DIGESTED.md` (1 file, optimized)
   - Apply Ma'at persona, lessons, KB (Build Side expertise)
   - Write `BUILD_SIDE_REPORT.md`
2. Dispatch Lilith task:
   - Read `RUN_SIDE_DIGESTED.md` (1 file, optimized)
   - Apply Lilith persona, lessons, KB (Run Side expertise)
   - Write `RUN_SIDE_REPORT.md`
3. Wait for BOTH completions
4. WAL checkpoint: Phase 2 complete

## Phase 3: Kali Final Synthesis
1. Dispatch Kali task:
   - Read `BUILD_SIDE_REPORT.md` + `RUN_SIDE_REPORT.md` (2 files only)
   - Apply Kali persona, lessons, and Oversight expertise
   - Write `FINAL_SYNTHESIS.md` with mandatory `REMAINING_GAPS_AND_RECOMMENDED_RESEARCH` section
2. Wait for completion
3. Parse research gaps from synthesis output
4. WAL checkpoint: Phase 3 complete

## Phase 4: Research Execution (Optional)
1. Parse `REMAINING_GAPS_AND_RECOMMENDED_RESEARCH` from FINAL_SYNTHESIS.md
2. Based on config.research_execution.mode:
   - "auto": Choose based on hardware profile
   - "local": Dispatch 4B model tasks for each gap
   - "cloud": Dispatch cloud model tasks
   - "deferred": Write gaps to file, return to user for manual execution
3. Execute research queries with configured model tier
4. Append results to FINAL_SYNTHESIS.md or store for next council cycle
5. WAL checkpoint: Phase 4 complete

## Output
```
data/council/{session_id}/
├── phase1_nodes/
│   ├── P1_report.md
│   ├── P3_report.md
│   ├── P4_report.md
│   ├── P5_report.md
│   ├── P6_report.md
│   ├── P7_report.md
│   ├── P8_report.md
│   ├── P9_report.md
│   └── P10_report.md
├── phase1.5_digested/
│   ├── BUILD_SIDE_DIGESTED.md
│   └── RUN_SIDE_DIGESTED.md
├── phase2_oversouls/
│   ├── BUILD_SIDE_REPORT.md
│   └── RUN_SIDE_REPORT.md
├── phase3_kali/
│   └── FINAL_SYNTHESIS.md
└── phase4_research/
    ├── research_gaps.md
    └── research_results/
```

## Resilience
- **WAL**: Write-Ahead Log for crash recovery (atomic .tmp → .json writes)
- **Circuit Breaker**: Opens at >30% error rate over 10 minutes
- **Fallback Chain**: digestion fails → raw concat; local model fails → cloud; abort on M2/M7 violation
- **Jitter Retry**: Exponential backoff with random jitter (base: 1s, max: 30s)
- **Hivemind Integration**: Auto-capture stage outputs, semantic search across runs

## Mandate Compliance
- **M1 AnyIO**: All async operations use AnyIO, not asyncio
- **M2 Firewall**: No node reads another node's report at write time
- **M7 Local-First**: Tries local model tiers before cloud; cloud = safety net
- **M13 Temple-Grade**: Each stage produces typed, verifiable outputs
- **M18 Token Efficiency**: Digestion layer (Phase 1.5) reduces oversoul tokens by ~60%
- **M23 Failure Integrity**: Digestion failure = hard stop with M23 fallback report

## Related Files
- `config/council.yaml` — Main config
- `config/council/profiles/*.yaml` — Hardware profiles
- `src/omega/council/coordinator.py` — MultiAgentCoordinator implementation
- `src/omega/council/report_digestion.py` — ReportDigester (Phase 1.5)
- `src/omega/council/models.py` — Data models
- `src/omega/council/failure_layer.py` — Circuit breaker, WAL, retry
- `docs/strategy/MAKALI_PARALLEL_COUNCIL_ARCHITECTURE.md` — Full architecture specification
- `docs/research/R_REPORT_DIGESTION_LAYER_OPTIMIZATION_20260719.md` — Digestion layer research
