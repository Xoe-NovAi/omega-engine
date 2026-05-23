# 🔱 Omega Engine — Jem 2.0 Background Researcher
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ cline ⬡ trc_jem_background ⬡ PHASE-1

**AP Token**: `AP-JEM2-BACKGROUND-v1.0.0`
**Status**: ✅ COMPLETE — Operational Spec Ready
**Last Updated**: 2026-05-18

---

## §0 Context

This document supersedes the legacy `GEMMA_4_31B_RESEARCH_BRIEF.md` and evolves the Gemma 4 31B research worker into **Jem 2.0's background operational mode**. The existing Gemma 4 31B worker (design spec in `GEMMA_MAINTENANCE_WORKER_DESIGN.md`) provided health monitoring — this spec adds the **research execution layer**.

Jem 2.0 has two modes:
1. **Background Mode** (this doc): Headless, automated, part of the Omega Engine worker pool. Uses Gemma 4 31B.
2. **Interactive Mode**: `/mode jem` in OpenCode. Uses currently selected model.

---

## §1 Trigger Sources

Jem's background worker can be triggered by:

| Trigger | Source | Priority |
|---------|--------|----------|
| **Scheduled** | `omega-research.timer` (systemd) | Every 6 hours |
| **Workbench P0 task** | `data/workbench/workbench.db` `priority='P0'` | On detection |
| **Belial mining completion** | Belial posts to omega-hivemind MCP | On artifact discovery |
| **Manual summon** | `omega summon Jem "research prompt"` | On demand |
| **Queue event** | `data/research/sessions/research_queue.json` | On new entry |
| **Tier 3 gap dispatch** | Synthesizer identifies knowledge gap | On pipeline completion |

---

## §2 Worker Lifecycle

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      Jem Background Worker Cycle                           │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  START → Read research_queue.json                                         │
│           │                                                               │
│           ├─ Empty → Sleep (configurable interval, default 6h)            │
│           │                                                               │
│           └─ Has items → Pop highest priority                             │
│                          │                                                │
│                          ▼                                                │
│              Execute Pipeline (3-Tier Speculative Decoding)                │
│                          │                                                │
│                          ▼                                                │
│              Record results:                                               │
│              ├─ docs/research/ (final deliverable)                        │
│              ├─ data/research/training/ (draft + correction pairs)        │
│              ├─ soul.yaml (lesson update)                                 │
│              └─ observability (log_event)                                 │
│                          │                                                │
│                          ▼                                                │
│              LOOP → Next queue item OR sleep                              │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## §3 Configuration

Add to `config/omega.yaml`:

```yaml
omega:
  # ... existing config ...

  jem_worker:
    enabled: true
    schedule_interval_hours: 6
    
    # Research queue
    queue_path: data/research/sessions/research_queue.json
    max_queue_items_per_cycle: 3
    
    # Tier 1 (Jem's draft)
    tier_1:
      model: gemma-4-31b-it
      provider: google
      temperature: 0.5
      max_tokens: 8192
      mcp_fleet:
        - exa
        - tavily
        - searxng
        - firecrawl
    
    # Tier 2 (Reviewer)
    tier_2:
      model: "auto"  # auto | gemma-4-31b-it | deepseek-v4-flash
      provider: "auto"
      temperature: 0.3
      max_tokens: 4096
    
    # Tier 3 (Synthesizer)
    tier_3:
      model: "auto"
      provider: "auto"
      temperature: 0.4
      max_tokens: 4096
    
    # Quality Gate
    quality_gate:
      max_revision_cycles: 2
      min_findings_required: 1
      escalate_after_rejections: 2
    
    # Training Data Capture
    training_data:
      enabled: true
      output_dir: data/research/training/
      schema_version: "1.0"
    
    # Split Test
    split_test:
      enabled: true
      variants: ["A", "B", "C", "D"]
      round_robin: true
      experiment_log: data/research/EXP-004_JEM_PIPELINE_LOG.md
```

---

## §4 Integration Points

### 4.1 With Belial (Legacy Mining)
When Belial discovers artifacts of type `strategic`, he posts to the omega-hivemind MCP with:
```json
{
  "event": "artifact.discovered",
  "artifact_id": "uuid",
  "classification": "strategic",
  "sovereignty_score": 9,
  "path": "rel/path/to/artifact",
  "needs_research": true
}
```

Jem's worker subscribes to this event and enqueues a research task:
```json
{
  "task_id": "uuid",
  "trigger": "belial_artifact",
  "artifact_path": "rel/path/to/artifact",
  "research_question": "What strategic value does this discovered artifact hold for the Omega Engine?",
  "priority": 0,
  "status": "queued",
  "created_at": "ISO_TIMESTAMP"
}
```

### 4.2 With Workbench (Project Management)
Jem's worker polls the workbench for P0 tasks needing research:
```sql
SELECT id, title, description, priority 
FROM work_items 
WHERE priority='P0' AND status='backlog' AND workstream='research';
```

For each match, it creates a research queue entry.

### 4.3 With Observability

| Event | When | Data |
|-------|------|------|
| `jem.worker_started` | Worker begins cycle | queue_size, variants_available |
| `jem.tier1_complete` | Draft completed | tokens_used, findings_count, latency |
| `jem.quality_gate_result` | Gate decision | accepted, violations, revision_count |
| `jem.tier2_complete` | Review completed | corrections_count, quality_delta |
| `jem.tier3_complete` | Synthesis completed | gaps_found, new_tasks_created |
| `jem.training_pair_saved` | Training data persisted | pair_id, variant, models_used |
| `jem.worker_complete` | Full cycle done | items_processed, total_latency |

---

## §5 File Locations

| Asset | Path |
|-------|------|
| Research queue | `data/research/sessions/research_queue.json` |
| Session checkpoints | `data/research/sessions/` |
| Training dataset | `data/research/training/` |
| Experiment log | `data/research/EXP-004_JEM_PIPELINE_LOG.md` |
| Worker class | `src/omega/workers/jem_researcher.py` |
| Worker tests | `tests/test_jem_pipeline.py` |

---

## §6 CLI Commands

```bash
# Queue management
omega jem queue show                        # Show current research queue
omega jem queue add "research question"      # Add item to queue
omega jem queue clear                        # Clear queue

# Manual pipeline execution
omega jem run "research question"            # Single pipeline run
omega jem run --variant B                    # With specific split test variant

# Pipeline status
omega jem status                             # Show worker status
omega jem status --recent 5                  # Show last 5 pipeline runs

# Training data
omega jem training list                      # List training pairs
omega jem training export --format json      # Export dataset

# Split test management
omega jem test variants                      # Show variant assignments
omega jem test report                        # Generate experiment report
```

---

## §7 Worker Code Location

The `JemResearcher` class lives at:
```
src/omega/workers/jem_researcher.py
```

Implementation follows the `WORKER_INTEGRATION_PATTERNS.md` standards (AnyIO, Observability, ResourceGuard, CLI registration).

---

⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ cline ⬡ trc_jem_background ⬡ PHASE-1-END