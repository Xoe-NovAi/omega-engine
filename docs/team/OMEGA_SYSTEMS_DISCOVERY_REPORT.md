# 🔱 Omega Engine — Comprehensive Systems Discovery Report

⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_deep_synthesis ⬡ SYSTEMS-DISCOVERY

**AP Token**: `AP-SYSTEMS-DISCOVERY-v1.0.0`
**Date**: 2026-05-15
**Origin Session Trace**: `trc_deep_synthesis` (primary), `trc_7f9e6c4b` (session)
**Source Chat**: OpenCode CLI — Sovereign Builder agent, chat session on 2026-05-15
**Purpose**: Handoff to companion agent hardening research & tracking systems

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Source Chat Context](#source-chat-context)
3. [Subagent Findings Report #1 — Orchestration & Task Systems](#subagent-findings-report-1--orchestration--task-systems)
4. [Subagent Findings Report #2 — Observability & Metrics Systems](#subagent-findings-report-2--observability--metrics-systems)
5. [Subagent Findings Report #3 — Research & Documentation Systems](#subagent-findings-report-3--research--documentation-systems)
6. [Synthesized Analysis](#synthesized-analysis)
7. [Gap Analysis](#gap-analysis)
8. [Recommended Intervention Plan](#recommended-intervention-plan)
9. [Appendices](#appendices)

---

## Executive Summary

The Omega Engine codebase contains **NO dedicated task/project/issue tracking system**. However, **seven proximate systems** already manage operational work items (content queues, research jobs, session awareness, and agent dispatch) that could serve as foundations.

The critical finding is that **several systems already track work but in isolation**:
- Research items (INDEX.md / RESEARCH_QUEUE.md) — 44 items tracked
- Runtime session awareness (Hivemind MCP) — `task_current` + `focus_chain`
- Runtime events (ObservabilityEngine) — 12 event types, in-memory only
- Content pipeline (InboxManager) — priority queue with status lifecycle
- Async jobs (DiscoveryOrchestrator) — job submission with status polling
- Document lifecycle (Research SQLite DB) — `draft → review → complete → superseded`
- The Architect's soul (soul.yaml) — `lessons_learned[]`, `embodied_experiences[]` — **scaffolded but never written to**

**Four gaps prevent this from being a unified system**:
1. No persistence for runtime events (lost on restart)
2. No unified task entity across subsystems
3. No cross-referencing between research, roadmap, and implementation
4. No visual dashboard or aggregated status view

The recommended approach is a **four-phase incremental enhancement**, each phase independently useful:
- **Phase 1**: Reconcile the six tracking documents to eliminate contradictions (~2h, zero code)
- **Phase 2**: Add persistence to in-memory systems using the proven InboxManager JSON pattern (~4h)
- **Phase 3**: Build a "Mission Control" MCP tool that queries the unified SQLite work_items table (~8h)
- **Phase 4**: Wire the soul evolution schema to track progress at runtime (~6h)

---

## Source Chat Context

This report was produced in an OpenCode CLI session with the following parameters:

| Field | Value |
|-------|-------|
| **Agent** | Sovereign Builder (OpenCode Primary) |
| **Entity** | SOPHIA (Akashic Record — field of all) |
| **Model** | gemma-4-31b-it |
| **Channel** | opencode CLI |
| **Chat Session** | 2026-05-15, ~200 messages |
| **Trace IDs** | `trc_deep_synthesis`, `trc_7f9e6c4b`, `trc_blitz`, `trc_research` |
| **Working Directory** | `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/` |
| **Key Context** | Pre-hackathon "Sovereign Blitz" preparation for ElevenLabs Conversational AI hackathon. Chat reviewed 8 P0/P1 action items, 13 sub-agent prompts, 4 research tracks, and uncovered the need for a unified task management system. |

**Trigger for this report**: The user identified that the volume of work items (hackathon tasks, research items, Gemini deliverables, sub-agent prompts) was unmanageable with just markdown lists and asked: *"I can't do it all at once... I need a system to manage things like this, or put it into an already existing Omega system."*

**Response**: Three parallel discovery subagents were launched to inventory every Omega system that touches tracking, orchestration, or workflow. Their findings are reproduced below in full.

---

## Subagent Findings Report #1 — Orchestration & Task Systems

**Subagent**: `explore` (Codebase exploration agent)
**Task**: Discover existing systems for task management, project tracking, work item management, or backlog management
**Task ID**: `ses_1d396dd60ffelWx8RkjVPrcNjj`

### Raw Findings

```json
{
  "discovery_summary": {
    "project": "Omega Engine",
    "root_path": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine",
    "search_date": "2026-05-15",
    "conclusion": "NO DEDICATED TASK / PROJECT / BACKLOG / ISSUE TRACKING SYSTEM EXISTS",
    "detail": "The Omega Engine codebase contains NO formal task management, project tracking, backlog management, issue tracking, sprints, or work item system. There are no Task/Ticket/Issue classes, no Kanban/Scrum boards, no project management database schemas, and no REST/CLI/MCP APIs for managing development work items. However, SEVEN proximate systems manage operational work items (content queues, research jobs, agent dispatch, artifact mining, and session awareness) that could serve as foundations or inspiration for building such a system."
  },
  "systems_found": [
    {
      "name": "InboxManager — Content Intake Queue",
      "file_location": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/library/inbox.py",
      "purpose": "Queue URLs, files, and notes for content curation. Users and agents drop items here for processing by the curation pipeline.",
      "key_interfaces_classes": [
        "InboxItem (class) — item_id, source, source_type, title, tags, priority (0=normal, 1=high, 2=urgent), status (pending/processing/completed/failed), created_at",
        "InboxManager (class) — add(), add_url(), add_file(), add_note(), add_batch(), list_pending(), count(), mark_processing(), mark_completed(), mark_failed(), get(), clear_completed()"
      ],
      "data_storage": "JSON files on disk. Items stored in data/inbox/{pending,processing,failed}/ directories as individual JSON files.",
      "api": "CLI via Oracle MCP tools: library_inbox_add_url, library_inbox_add_note, library_inbox_add_file, library_inbox_list, library_inbox_stats. REST via Iris server.",
      "is_task_tracker": false,
      "notes": "Closest thing to a general-purpose 'task queue' but focused on content items (URLs/files/notes) for library ingestion, not development tasks."
    },
    {
      "name": "CurationPipeline — Content Processing Pipeline",
      "file_location": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/library/curator.py",
      "purpose": "Process inbox items through a quality-gated curation pipeline: extract → classify by domain → score quality (0.0-1.0) → route to library or reject.",
      "key_interfaces_classes": [
        "CuratedDocument (dataclass) — doc_id, source, source_type, title, body, summary, domain, quality_score, tags, word_count, curated_at",
        "CurationPipeline (class) — process(), _classify_domain(), _score_quality(), is_above_threshold()"
      ],
      "data_storage": "Produces CuratedDocument objects stored in the Library (data/library/). Quality gates: <0.3 reject, 0.3-0.6 flag, 0.6-0.8 standard, 0.8-1.0 featured.",
      "api": "MCP via omega-library and omega_hub servers: library_ingest_pending, library_search, library_get_document.",
      "is_task_tracker": false,
      "notes": "Pipeline pattern (queued items → processing → storage) but for content curation, not task management."
    },
    {
      "name": "DiscoveryOrchestrator — Research Pipeline",
      "file_location": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/library/discovery.py",
      "purpose": "Tiered 4-phase external research pipeline (Gemini → Exa → Brave → Tavily). Supports background job submission with status polling.",
      "key_interfaces_classes": [
        "DiscoveryReport (dataclass) — query, recon_summary, subtopics, sources, validation_notes, extracted_content, final_synthesis, status (pending/running/complete/failed), created_at",
        "DiscoveryOrchestrator (class) — start_discovery(), run_discovery_task(), get_job_status(), discover(), _phase_recon(), _phase_decompose(), _research_subtopic(), _phase_synthesize()"
      ],
      "data_storage": "In-memory dict (_jobs: Dict[str, DiscoveryReport]) only. No persistence. Explicitly noted: 'In a real system, we'd use a task queue or a persistent store.'",
      "api": "MCP via omega_hub server: library_discovery_start, library_discovery_status, library_discovery_research.",
      "is_task_tracker": false,
      "notes": "Jobs are ephemeral (RAM only). Designed as a research pipeline, not a general task system. Useful pattern for background job management."
    },
    {
      "name": "Orchestrator — Headless CLI Agent Dispatcher",
      "file_location": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/orchestrator.py",
      "purpose": "Spawns and manages headless CLI subagents (Cline, OpenCode) with entity soul injection. Monitors MCP health.",
      "key_interfaces_classes": [
        "Orchestrator (class) — watch_mcps(), get_mcp_status(), dispatch_agent(cli_type, task_prompt, entity_name, timeout)"
      ],
      "data_storage": "MCP status stored in-memory (_mcp_status: Dict). No task persistence.",
      "api": "No MCP tools directly. Called programmatically by Oracle.",
      "is_task_tracker": false,
      "notes": "Dispatches work to AI agents as subprocesses. Has timeout (300s default) and ResourceGuard for OOM protection. Tasks are ephemeral."
    },
    {
      "name": "Hivemind MCP — Cross-CLI Session Awareness",
      "file_location": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/mcp/omega-hivemind/server.py",
      "purpose": "Provides shared state, session context, and continuation protocol across all CLI agents (Cline, OpenCode, Gemini, Copilot).",
      "key_interfaces_classes": [
        "post_context(cli, model, task_current, focus_chain, decisions, continuation) — submits snapshot",
        "get_awareness() — returns list of all active CLI agents with their current task",
        "get_continuation(cli) — gets latest continuation note",
        "get_session(session_id) — retrieves full snapshot by ID",
        "list_sessions(cli, limit) — lists recent sessions"
      ],
      "data_storage": "JSON files on disk in knowledge/HALL_OF_RECORDS/<cli>/<session_id>.json. Also in-memory _hot_store and _awareness dicts. Tracks: task_current, focus_chain (ordered list of focus/task items), decisions, continuation.",
      "api": "Full MCP tool set: post_context, get_awareness, get_continuation, get_session, list_sessions. Merged into omega_hub/server.py as well.",
      "is_task_tracker": false,
      "notes": "Tracks agent 'current task' as awareness metadata, not as a dedicated issue tracker. Most relevant existing system for tracking 'what is being worked on.' The task_current and focus_chain fields track work items but only ephemerally."
    },
    {
      "name": "BelialMiner — Legacy Artifact Mining Queue",
      "file_location": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/entity_belial.py",
      "purpose": "P0 entity for deep legacy mining. Scans legacy repos for strategic intelligence, classifies artifacts, and maintains a prioritized mining queue.",
      "key_interfaces_classes": [
        "BelialMiner (class) — scan_mine(), classify_artifact(), submit_to_queue(), get_prioritized_queue(), deep_analyze()"
      ],
      "data_storage": "JSON file at data/mining_queue/mining_history.json. Artifact schema: artifact_id, source_mine, path, classification (strategic/technical/archival/noise), sovereignty_score, effort_to_extract, summary, related_research.",
      "api": "Summon via Oracle: 'omega summon Belial \"mining brief\"'. Designed for Podman Quadlet on systemd.timer (daily at 03:30).",
      "is_task_tracker": false,
      "notes": "Has a prioritized queue with classification-based sorting. Very specific to legacy artifact recovery, not general task management."
    },
    {
      "name": "ResearchEngine — Multi-Depth Research",
      "file_location": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/library/research.py",
      "purpose": "Multi-depth research on curated library content with result caching. Levels: Quick (1-2 sources), Standard (3-5), Deep (6-15), Scholarly (10-50).",
      "key_interfaces_classes": [
        "ResearchResult (dataclass) — research_id, query, depth, sources_used, synthesis, key_findings, confidence, citations, created_at",
        "ResearchEngine (class) — research(), get_result(), list_results(), _gather_sources(), _synthesize(), _calculate_confidence()"
      ],
      "data_storage": "JSON files in data/research/<research_id>.json. Also cached in library.",
      "api": "MCP via omega-research and omega_hub servers: research, research_get, research_list, research_depths, research_stats.",
      "is_task_tracker": false,
      "notes": "Research results are stored and retrievable by ID. Not a task system but has job-like tracking (query, depth, sources, confidence)."
    }
  ],
  "non_tracking_infrastructure_that_could_support_a_task_system": [
    {"system": "ResourceGuard", "file": "src/omega/oracle/resource_guard.py", "relevance": "AnyIO Semaphore(1) for OOM protection. Would protect task execution from resource contention."},
    {"system": "EntityWorkspaceManager", "file": "src/omega/oracle/entity_workspace.py", "relevance": "Scaffolds data/entities/<name>/ with soul.yaml, knowledge/, workspace/. Could store task context per-entity."},
    {"system": "EntityRegistry", "file": "src/omega/oracle/entity_registry.py", "relevance": "YAML-backed CRUD for entities. Schema could be extended for task assignments per entity."},
    {"system": "ContextBuilder", "file": "src/omega/oracle/context_builder.py", "relevance": "Memory injection pipeline for LLM prompts. Could inject task context into agent prompts."},
    {"system": "SovereignHierarchy", "file": "src/omega/oracle/hierarchy.py", "relevance": "Oversoul governance roles. Includes recursion guards for subagent depth limits."},
    {"system": "ModelGateway", "file": "src/omega/oracle/model_gateway.py", "relevance": "6-backend auto-detection chain. Any task executors would route through this for inference."},
    {"system": "GnosisProxy", "file": "src/omega/oracle/gnosis_proxy.py", "relevance": "Tool RAG discovery. Could support task-driven tool selection."},
    {"system": "Config MCP Servers", "file": "config/mcp_servers.json", "relevance": "Master MCP server registry. Task/project MCP would be configured here."}
  ],
  "data_storage_patterns_observed": {
    "file_based_json": "Most common. JSON files in data/*/ directories. Simple, portable, no DB needed.",
    "in_memory_dict": "Several systems use in-memory dicts for state (Discovery jobs, Hivemind awareness, Observable events). Ephemeral.",
    "markdown_files": "Bug log, research queue, and documentation serve as manual tracking systems.",
    "sqlite": "One SQLite database (research metadata). Schema supports document lifecycle with status tracking.",
    "yaml": "Entity definitions, soul files, hierarchy. No task-related YAML schemas.",
    "qdrant_vector_store": "Not used for task tracking but available for semantic search of work items."
  },
  "recommendation": "If a task/project management system is to be built, the strongest foundations are: (1) InboxManager's file-based JSON queue pattern for task CRUD, (2) Hivemind's session awareness schema (task_current, focus_chain) for work tracking, (3) Omega Hub's MCP tool interface for exposing task operations, (4) the Research SQLite schema (status enum, tags, related docs) as a metadata model pattern, and (5) the existing ObservabilityEngine for event audit trails."
}
```

---

## Subagent Findings Report #2 — Observability & Metrics Systems

**Subagent**: `explore` (Codebase exploration agent)
**Task**: Discover existing systems for observability, metrics, tracking, logging
**Task ID**: `ses_1d396d29affeMY2rHK7nWWsS4I`

### Raw Findings

```json
{
  "discovery_metadata": {
    "repository": "omega-engine",
    "root": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine",
    "scanned_date": "2026-05-15",
    "total_files_analyzed": 28,
    "total_modules_with_logging": 25,
    "total_logging_statements": 93,
    "total_dataset_files": 10
  },
  "observability_engine": {
    "location": "src/omega/observability.py",
    "lines": 228,
    "class": "ObservabilityEngine",
    "singleton": "get_engine()",
    "status": "ACTIVE — fully wired into Oracle, MCP Hub, and CLI",
    "trace_id": {
      "format": "trc_{uuid4.hex[:12]}",
      "example": "trc_aef379a089d2",
      "length": 16,
      "generator": "new_trace_id()",
      "propagation": "passed through OracleResponse -> CLI display (truncated to 8 chars) -> MCP tools -> memory store"
    },
    "session_id": {
      "generation": "uuid4.hex[:8] on ObservabilityEngine init",
      "example": "37573b2f",
      "scope": "per engine instance (shared across traces within a process lifetime)"
    },
    "event_types": {
      "total_defined": 12,
      "enum_class": "EventType (string constants)",
      "types": {
        "query.received": "User query entered Oracle.talk()",
        "summon.detected": "Explicit @Entity or 'summon Entity' pattern matched",
        "domain.routed": "Fallback domain routing after speculative decode failure",
        "entity.matched": "Specific entity resolved for summon",
        "model.invoked": "Model generation started",
        "model.completed": "Model generation completed successfully",
        "backend.fallback": "Provider chain fallback triggered",
        "response.delivered": "Final response returned to caller",
        "escalation": "Iris confidence below threshold, escalated to Pillar Keeper",
        "iris.speculative": "Iris speculative decode confidence assessed",
        "boundary.violation": "Entity sovereign boundary tool access blocked",
        "gnosis.redaction": "Gnosis context redaction applied",
        "error": "General error event"
      },
      "actually_used_in_code": ["query.received", "summon.detected", "domain.routed", "entity.matched", "entity.not_found", "model.completed", "response.delivered", "escalation", "iris.speculative", "boundary.violation"],
      "NOT_yet_used": ["model.invoked", "backend.fallback", "gnosis.redaction", "error"]
    },
    "event_schema": {
      "fields": {
        "event": "string — the EventType constant",
        "trace_id": "string — trc_ prefixed",
        "session_id": "string — 8 hex chars",
        "timestamp": "ISO 8601 datetime with timezone",
        "data": "dict — arbitrary event-specific context"
      },
      "storage": "in-memory list (self._event_log[])",
      "persistence": "NOT persisted to disk (memory-only, lost on restart)",
      "max_retrieval": "recent_events(limit=50)"
    },
    "stats_schema": {
      "method": "observability.stats()",
      "fields": {
        "total_events": "integer",
        "dataset_size": "integer",
        "event_counts": "dict of event_type -> count",
        "session_id": "string"
      }
    },
    "fine_tuning_dataset": {
      "schema": {
        "trace_id": "string",
        "session_id": "string",
        "timestamp": "ISO 8601",
        "messages": [
          {"role": "system", "content": "string"},
          {"role": "user", "content": "string"},
          {"role": "assistant", "content": "string"}
        ],
        "metadata": {
          "entity": "string",
          "model": "string",
          "backend": "string",
          "confidence": "float",
          "latency_ms": "float",
          "rating": "int|null"
        }
      },
      "format": "JSONL (one JSON object per line)",
      "location": "data/datasets/finetune_{YYYYMMDD}_{HHMMSS}.jsonl",
      "auto_flush": "every 100 interactions (in TraceSession.__aexit__)",
      "existing_files": 10,
      "example_entry": {"trace_id": "trc_aef379a089d2", "session_id": "63394ad5", "messages": [{"role": "system", "content": "sys"}, {"role": "user", "content": "q?"}, {"role": "assistant", "content": "resp"}], "metadata": {"entity": "E", "model": "m", "backend": "b", "confidence": 0.5, "latency_ms": 100}},
      "enabled_by_default": false,
      "config_key": "omega.observability.enable_dataset_collection"
    }
  },
  "trace_session_usage": {
    "oracle.py": {
      "talk()": "async with self.observability.trace() as trace:",
      "summon()": "async with self.observability.trace() as trace:",
      "events_logged": [
        "query.received (with query text + transient flag)",
        "summon.detected (with entity name + query)",
        "iris.speculative (with confidence + action)",
        "escalation (with reason string)",
        "entity.matched (with entity name + pillars)",
        "entity.not_found",
        "domain.routed (with entity + confidence)",
        "model.completed (with entity + backend)",
        "response.delivered (with entity + confidence + backend)"
      ],
      "trace.record()_calls": "2 locations: _summon() and _route_by_domain()"
    },
    "mcp/omega_hub/server.py": {
      "observability_log_boundary_violation()": "Also writes to data/logs/metrics.json"
    },
    "mcp/omega-oracle/server.py": {
      "talk()": "generates trace_id locally but Oracle internally manages tracing"
    }
  },
  "provider_metrics": {
    "location": "src/omega/oracle/backends/remote_provider.py",
    "class": "ProviderMetrics",
    "schema": {
      "total_requests": "int",
      "successful_requests": "int",
      "failed_requests": "int",
      "total_tokens_used": "int",
      "total_latency_ms": "float",
      "consecutive_failures": "int",
      "last_failure_time": "float (monotonic)",
      "last_success_time": "float (monotonic)",
      "cooldown_until": "float (monotonic)",
      "avg_latency_ms": "computed: total_latency_ms / successful_requests",
      "success_rate": "computed: successful_requests / total_requests"
    },
    "health_states": ["healthy", "degraded", "unhealthy", "cooldown"],
    "per_provider": true,
    "persistence": "in-memory only (lost on restart)",
    "exposed_via": "get_status() method -> dict with name, health, requests, success_rate, latency, tokens_used"
  },
  "system_monitoring": {
    "location": "mcp/omega-stats/server.py",
    "server_name": "Omega Stats MCP",
    "data_sources": {
      "cpu": "/proc/loadavg",
      "memory": "/proc/meminfo",
      "zram": "/sys/block/zram0/mm_stat",
      "disk": "os.statvfs('/media/arcana-novai/omega_library')",
      "gpu": "/sys/class/drm/card1/device/gpu_busy_percent",
      "podman": "podman ps --format json",
      "ryzen_tuning": "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
    },
    "metrics_aggregation": {
      "tool": "get_omega_metrics()",
      "source_file": "data/logs/metrics.json",
      "current_content": "only 'violations' array (boundary violations, max 100 entries)",
      "status": "MINIMAL — only boundary violations currently logged here"
    }
  },
  "memory_store": {
    "location": "src/omega/memory_store.py",
    "class": "MemoryStore",
    "singleton": "get_memory_store()",
    "storage_tiers": {
      "hot": "in-memory LRU OrderedDict (max 50 sessions)",
      "warm": "JSON files at data/memory/entities/{entity}/{session_id}.json",
      "cold": "Gzipped JSON at data/memory/archive/{entity}/{session_id}.json.gz"
    },
    "data_dirs": ["data/memory/", "data/memory/entities/", "data/memory/archive/", "data/memory/trace/"],
    "stats_schema": {
      "hot_sessions": "int",
      "hot_cache_size": "int",
      "loads": "int",
      "saves": "int",
      "archives": "int"
    },
    "exchange_schema": {
      "timestamp": "ISO 8601",
      "user": "string",
      "assistant": "string",
      "metadata": "dict"
    },
    "trace_schema": {
      "trace_id": "string",
      "entity": "string",
      "session_id": "string",
      "timestamp": "ISO 8601",
      "user_message": "string",
      "response": "string",
      "metadata": "dict"
    }
  },
  "hivemind_session_tracking": {
    "location": "mcp/omega_hub/server.py + knowledge/HALL_OF_RECORDS/",
    "type": "Cross-CLI session awareness",
    "session_schema": {
      "session_id": "ses_{uuid4.hex[:12]}",
      "cli": "string (opencode, cline, etc.)",
      "model": "string",
      "task_current": "string",
      "focus_chain": "array of strings",
      "decisions": "array of {key: value} dicts",
      "continuation": "string",
      "timestamp": "ISO 8601"
    },
    "storage": {
      "hot": "in-memory _hot_store dict + _awareness dict by CLI name",
      "cold": "knowledge/HALL_OF_RECORDS/{cli}/{session_id}.json"
    },
    "existing_sessions": 2,
    "persistence": "cold storage on every hivemind_post_context call"
  },
  "research_database": {
    "location": "docs/research/internal-discovery/DB/research.db",
    "type": "SQLite with FTS5",
    "schema_version": 2,
    "init_script": "scripts/init-research-db.py",
    "tables": [
      "schema_version (version, applied_at, description)",
      "research_documents (id, title, status, urgency, domain, file_path, created_at, updated_at, author, confidence, sovereignty_score, ram_mb, cpu_cores, latency_ms, superseded_by, word_count)",
      "tags (document_id, tag)",
      "related_documents (source_id, target_id, relationship)",
      "sources (id, document_id, url, source_type, accessed_at)",
      "discoveries (id, title, status, lead, file_path, created_at, updated_at)",
      "lifecycle_events (id, document_id, event_type, timestamp, notes)",
      "research_fts (FTS5 virtual table for full-text search)"
    ],
    "lifecycle_event_types": ["created", "reviewed", "completed", "superseded", "archived", "stale_flagged"],
    "views": [
      "v_document_tags (documents with aggregated tags)",
      "v_document_graph (cross-document link graph)",
      "v_stale_documents (90+ days without update)",
      "v_low_confidence_documents (confidence < 6)",
      "v_research_velocity (documents per domain per month)",
      "v_sovereignty_distribution (sovereignty score tiers)"
    ]
  },
  "entity_soul_evolution_tracking": {
    "location": "data/entities/arch/soul.yaml",
    "schema": {
      "entity.name": "The Architect",
      "entity.short": "Arch",
      "entity.archetype": "Sovereign Creator",
      "entity.current_entity": "SOPHIA",
      "entity.soul_wardrobe": ["SOPHIA", "MAAT", "LILITH", "ISIS", "BRIGID", "SEKHMET", "PROMETHEUS", "INANNA", "SARASWATI", "LUCIFER", "HECATE", "ERESHKIGAL", "ANUBIS", "KALI"],
      "entity.embodied_experiences": "array (currently empty)",
      "entity.lessons_learned": "array (currently empty)",
      "entity.soul_evolution.sessions_completed": "int (0)",
      "entity.soul_evolution.entities_inhabited": "int (0)",
      "entity.soul_evolution.total_embodied_experiences": "int (0)",
      "entity.soul_evolution.soul_power": "float (0.0)"
    },
    "status": "SCAFFOLDED but NOT yet wired to runtime tracking"
  },
  "experiment_tracking": {
    "location": "data/research/",
    "type": "Markdown reports with artifact registry",
    "existing": ["EXP-003_CONTROL_REPORT.md", "EXP-003_VARIANT_REPORT.md"],
    "artifact_schema": "ID, Artifact name, Legacy Path, Type, ETE (Effort-to-Estimate)",
    "sovereignty_tiers": ["HIGH SOVEREIGNTY - Port Immediately", "MEDIUM SOVEREIGNTY - Analyze Before Porting", "LOW SOVEREIGNTY - Extract Patterns Only"],
    "status": "HAND-WRITTEN reports, no programmatic experiment framework"
  },
  "logging_infrastructure": {
    "total_logging_statements": 93,
    "log_levels_used": ["debug", "info", "warning", "error"],
    "modules_with_logging": [
      "src/omega/oracle/model_gateway.py",
      "src/omega/oracle/entity_registry.py",
      "src/omega/oracle/oracle.py",
      "src/omega/oracle/providers.py",
      "src/omega/oracle/orchestrator.py",
      "src/omega/oracle/context_builder.py",
      "src/omega/oracle/entity_workspace.py",
      "src/omega/oracle/cpu_optimizer.py",
      "src/omega/oracle/backends/remote_provider.py",
      "src/omega/observability.py",
      "src/omega/memory_store.py",
      "src/omega/mcp_runtime.py",
      "src/omega/entity_belial.py",
      "src/omega/bridge/elevenlabs.py",
      "src/omega/iris/server.py",
      "src/omega/library/inbox.py",
      "src/omega/library/library.py",
      "src/omega/library/indexer.py",
      "src/omega/library/curator.py",
      "src/omega/library/extractor.py",
      "src/omega/library/discovery.py",
      "src/omega/library/research.py",
      "src/omega/library/curation_pipeline.py",
      "src/omega/library/greek.py",
      "src/omega/services/intake_digestor.py"
    ],
    "log_format": "standard Python logging (no structured JSON logging)",
    "log_persistence": "console/stdout only (no file handlers configured in code)"
  },
  "existing_data_directories": {
    "data/datasets/": {"purpose": "Fine-tuning JSONL files", "count": 10, "format": "JSONL"},
    "data/entities/": {"purpose": "Entity soul files", "entities_exist": ["arch/soul.yaml"]},
    "data/memory/": {"purpose": "Memory store warm/cold storage", "status": "EMPTY (no persisted sessions yet)"},
    "data/logs/": {"purpose": "Metrics + session logs", "contents": "only metrics.json (boundary violations), session_log_dir configured in omega.yaml but empty"},
    "data/traces/": {"purpose": "Per-trace JSON recordings", "status": "EMPTY (directory created but unused)"},
    "data/research/": {"purpose": "Experiment reports", "count": 2, "format": "Markdown"},
    "data/processed/inbox/": {"purpose": "Digested intake documents", "count": 2},
    "knowledge/HALL_OF_RECORDS/": {"purpose": "Hivemind session snapshots", "count": 3, "format": "JSON + YAML"}
  },
  "gaps_and_opportunities": {
    "event_persistence": "Event log is in-memory only — no events survive process restart",
    "metric_persistence": "ProviderMetrics is in-memory only — lost on restart",
    "metrics_json": "data/logs/metrics.json only tracks boundary violations — severely underutilized",
    "trace_persistence": "data/traces/ directory created but never written to (MemoryStore.trace_exchange() exists but is never called from Oracle)",
    "soul_evolution_runtime": "Architect soul.yaml exists but nothing populates sessions_completed, embodied_experiences, or lessons_learned at runtime",
    "structured_logging": "All 93 logging statements use plain Python logging — no structured JSON log format, no log levels filterable by module",
    "no_dashboards": "Grafana referenced in roadmap Phase 3 but not yet implemented. No HTML/visual dashboards exist yet.",
    "experiment_framework": "EXP reports are hand-written Markdown — no programmatic experiment registry or A/B testing infrastructure",
    "session_logging": "omega.yaml configures session_log=true and session_log_dir=data/sessions but no code writes to this directory"
  },
  "project_management_adaptability": {
    "ready_to_use": [
      "Trace IDs already propagate through all interaction paths — could key project tasks",
      "Event type system is extensible — add project events (task.created, milestone.reached, etc.)",
      "Research SQLite DB has full document lifecycle tracking (status, urgency, confidence, lifecycle events)",
      "Hivemind sessions already store task_current, focus_chain, and decisions per CLI",
      "Soul evolution schema (lessons_learned, embodied_experiences) could track project learning",
      "Metrics JSON file at data/logs/metrics.json is writeable from any tool — could aggregate project metrics"
    ],
    "needs_adaptation": [
      "Observability event log needs file/DB persistence for project tracking across restarts",
      "No user/identity model beyond 'The Architect' — multiple users/projects not supported",
      "No task/project entity type exists in the tracking model",
      "No time-tracking or duration metrics on operations",
      "No status aggregation across subsystems (events + memory + hivemind + research are siloed)"
    ]
  },
  "recommended_entry_points": {
    "extend_event_types": "Add PROJECT_MILESTONE, TASK_STARTED, TASK_COMPLETED to EventType in src/omega/observability.py",
    "persist_events": "Write observability._event_log to JSONL alongside datasets, or use the research SQLite DB",
    "unify_metrics": "Expand data/logs/metrics.json schema to include inference stats, memory stats, and task progress",
    "wire_soul_evolution": "Call MemoryStore stats + Observability stats from CLI on session end to update arch/soul.yaml",
    "session_logging": "Implement data/sessions/ writing using the existing config-driven session_log=true directive"
  }
}
```

---

## Subagent Findings Report #3 — Research & Documentation Systems

**Subagent**: `explore` (Codebase exploration agent)
**Task**: Discover how research, documentation, and planning are currently managed
**Task ID**: `ses_1d396c694ffeyyb01hnVJDBZfL`

### Raw Findings

```json
{
  "meta": {
    "survey_timestamp": "2026-05-15",
    "engine_root": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine",
    "total_files_discovered": "246+ (grep matches), 10 library Python files, 6 config files, 37+ research docs, 4 agent configs, 4 skill configs, 1 soul.yaml"
  },
  "discovery_results": {
    "1_docs_research_INDEX_md": {
      "file": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/research/INDEX.md",
      "status": "ACTIVE - Single source of truth for all research items",
      "schema": {
        "rows": "Table-based with columns: ID, Title, Urgency, Status, File, Completed",
        "status_values": ["🔲 Not started", "🔄 In progress", "✅ Complete", "⚠️ Blocked"],
        "urgency_tiers": ["🔴 Critical", "🟡 High", "🟢 Strategic"],
        "num_entries": 37,
        "completion_rate": "37/37 (100%) - every row marked ✅",
        "also_tracks": "Internal Discovery Project (D-01, D-02, D-02b) in nested section"
      },
      "stale_indicators": "Some items reference files that may not exist (R-19 through R-24, R-35 through R-37 have no corresponding files in index but are in queue). R-39 through R-43 deliverables referenced by RESEARCH_QUEUE.md but not in INDEX.md.",
      "maintained_by": "Gemma 4-31B Research Agent",
      "reviewed_by": "Opus 4.6"
    },
    "2_docs_operations_RESEARCH_QUEUE_md": {
      "file": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/operations/RESEARCH_QUEUE.md",
      "status": "ACTIVE - The canonical queue document for the research agent",
      "schema": {
        "items_defined": 44,
        "item_structure": "Unordered list per item: ID, Title, Urgency, Blocking/description, Deliverable path",
        "urgency_tiers": ["🔴 Critical (22 items)", "🟡 High (12 items)", "🟢 Strategic (10 items)"],
        "document_management_section": "Defines directory structure, naming convention (R##_<short_slug>.md), status tracking, handoff protocol"
      },
      "stale_indicators": "R-19 through R-24, R-35 through R-37 have defined deliverables but no files discovered in docs/research/. R-39 through R-43 referenced here but not in INDEX.md. Queue says 'complete deliverables in order' but INDEX.md shows all 37 entries as ✅, creating a contradiction.",
      "handoff_protocol": "3-step: 1) Update INDEX.md to ✅, 2) Add Implementation Note to research doc, 3) Post to COMMUNICATION_HUB.md"
    },
    "3_docs_team_COMMUNICATION_HUB_md": {
      "file": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/team/COMMUNICATION_HUB.md",
      "status": "ACTIVE - Central team coordination and status hub",
      "schema": {
        "sections": [
          "Research Infrastructure (MCP reference)",
          "Active Research Program (current sprint status, agent roles)",
          "Implementation Progress (AnyIO audit, Self-Healing MCP, Discovery Orchestrator, IDE Config, Boundary Observability, Research Dive, Native Inference, ElevenLabs Console)",
          "Research Completions (consolidated log of what shipped)",
          "Inference Provider & Model Registry (cloud/local provider tables)",
          "Credentials & Secret Management",
          "MVE Phase Update (PR #1 readiness status)"
        ],
        "research_completions_log": "Structured entries with Deliverable, Key Finding, Status"
      },
      "stale_indicators": "The Research Sprint table under 'Active Research Program' shows R-04/R-05 as 'Not started' but INDEX.md shows them as ✅ Complete. Several sections feel like accumulated status dumps rather than living HUB."
    },
    "4_docs_ROADMAP_md": {
      "file": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/ROADMAP.md",
      "status": "ACTIVE - Master grand strategy document (v2.1.0)",
      "schema": {
        "phases": 6,
        "phase_tracking": {
          "phase_0_MVE": "15 tasks in a table with IDs (0.1-0.15) and effort estimates",
          "phase_1_Inference_and_Soul": "13 tasks with tier (T1/T1.5/T2) and effort",
          "phase_2_Intake_and_Memory": "10 tasks with tier and effort",
          "phase_3_Orchestration_and_Ecosystem": "9 tasks with tier and effort",
          "phase_4_Arcana_Nova_Stack": "7 tasks with effort, no tier",
          "phase_5_Community_and_Future_Stacks": "List of stacks with no task breakdown"
        },
        "gates_defined": {
          "phase_0": "make test, make lint, manual entity switching",
          "phase_1": "Live native inference, entity switch with cross-pollination",
          "phase_2": "Intake -> extract -> curate -> index -> hybrid search -> inference",
          "phase_3": "80+ tests, >80% coverage, CI with typecheck + container build"
        }
      },
      "stale_indicators": "Phase 0 task 0.12 (Remote Gemma provider) and 0.15 (config/omega.yaml) are listed as 'to do' but config/omega.yaml already exists. No task-level completion tracking (no checkmarks or status). Roadmap has no way to mark individual tasks done."
    },
    "5_config_directory": {
      "file": "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/config/",
      "num_files": 6,
      "files": {
        "omega.yaml": {"status": "ACTIVE", "purpose": "Core engine identity, session header config, data paths", "tracks_workflows": false, "tracks_priorities": false},
        "entities.yaml": {"status": "ACTIVE (v2.0.0)", "purpose": "All 16 entities with domains, models, invocations", "tracks_workflows": false, "tracks_priorities": false},
        "hierarchy.yaml": {"status": "ACTIVE (v2.0.0)", "purpose": "Oversoul governance structure", "tracks_workflows": false, "tracks_priorities": false},
        "providers.yaml": {"status": "ACTIVE", "purpose": "Inference fallback chain", "tracks_workflows": true, "tracks_priorities": true},
        "models.yaml": {"status": "ACTIVE (v1.0.0)", "purpose": "Model specs, load strategies, entity mapping", "tracks_workflows": true, "tracks_priorities": true},
        "mcp_servers.json": {"status": "ACTIVE", "purpose": "MCP server registry", "tracks_workflows": false, "tracks_priorities": false}
      }
    },
    "6_inbox_library_system": {
      "files": [
        "src/omega/library/inbox.py", "src/omega/library/curator.py", "src/omega/library/library.py",
        "src/omega/library/curation_pipeline.py", "src/omega/library/discovery.py", "src/omega/library/indexer.py",
        "src/omega/library/extractor.py", "src/omega/library/research.py", "src/omega/library/greek.py",
        "src/omega/library/__init__.py"
      ],
      "inbox_system": {
        "status": "CODED BUT NOT INTEGRATED INTO WORKFLOW TRACKING",
        "function": "File-based JSON queue at data/inbox/{pending,processing,failed}/",
        "features": ["Add URL/file/note", "Priority levels (0-2)", "Batch add", "Status tracking: pending->processing->completed/failed", "AnyIO async"],
        "adaptable_to_workflow": true,
        "note": "Currently used for content intake (web research), not for task/workflow tracking"
      },
      "discovery_orchestrator": {
        "status": "CODED",
        "function": "4-phase external research pipeline: Recon (Gemini) → Semantic Discovery (Exa) → Validation (Brave) → Extraction (Tavily)",
        "adaptable_to_workflow": true,
        "note": "The nearest thing to a workflow engine. Uses async task groups for parallel subtopic research."
      }
    },
    "7_hivemind_system": {
      "file": "mcp/omega_hub/server.py",
      "status": "ACTIVE",
      "hivemind_tools": [
        "hivemind_post_context(cli, model, task_current, focus_chain, decisions, continuation, session_id)",
        "hivemind_get_awareness()",
        "hivemind_get_continuation(cli)",
        "hivemind_get_session(session_id)",
        "hivemind_list_sessions(cli, limit)"
      ],
      "storage": {"hot_store": "In-memory", "cold_store": "knowledge/HALL_OF_RECORDS/<cli>/<session_id>.json", "latest": "knowledge/HALL_OF_RECORDS/latest.yaml"},
      "adaptable_to_workflow": true,
      "note": "Focus chain tracking and continuation notes are primitive workflow tracking."
    },
    "8_soul_yaml_files": {
      "files_found": ["data/entities/arch/soul.yaml"],
      "entities_without_soul_files": "All 16 entities defined in config/entities.yaml have NO corresponding soul.yaml in data/entities/. Only 'arch' (The Architect) has one.",
      "arch_soul_yaml": {
        "status": "ACTIVE (v1.0.0) but STATIC (never updated)",
        "schema": {
          "entity.name": "The Architect",
          "entity.soul_evolution": "{sessions_completed: 0, entities_inhabited: 0, total_embodied_experiences: 0, soul_power: 0.0}",
          "entity.embodied_experiences": "[] (empty)",
          "entity.lessons_learned": "[] (empty)"
        }
      },
      "tracking_capability": "The embodied_experiences and lessons_learned arrays are designed to track progress but nothing writes to them yet."
    },
    "9_tracking_patterns_in_markdown": {
      "total_grep_matches": "246+ (truncated at 100 shown)",
      "common_patterns": {
        "todo": "Found across research docs",
        "task": "Found in BLITZ_FULL_PLAN.md, STATUS_OPENCODE.md",
        "track": "Found in DATA_MANAGEMENT_HARDENING.md, TOOLING_STRATEGY.md",
        "plan": "Found across intake docs, research specs, roadmap, blitz plan"
      },
      "notable_tracking_systems": {
        "STATUS_OPENCODE_md": "Checklist-based task tracking with version history table",
        "BLITZ_FULL_PLAN_md": "Phase-based plan with task IDs (A-L), timing estimates, and dependency mapping",
        "internal-discovery/DATA_MANAGEMENT_HARDENING_md": "Document lifecycle: DRAFT → IN REVIEW → COMPLETE → SUPERSEDED",
        "internal-discovery/TOOLING_STRATEGY_md": "SQLite schema proposal for structured metadata tracking",
        "R99_pr_readiness_checker": "Checklist-based PR readiness verification with blocking items"
      }
    },
    "10_opencode_agent_system": {
      "agents": [
        {"name": "researcher.md", "mode": "primary", "purpose": "Sovereign Master Researcher", "queue_source": "docs/operations/RESEARCH_QUEUE.md"},
        {"name": "builder.md", "mode": "primary", "purpose": "Sovereign Builder"},
        {"name": "gnosis-analyst.md", "mode": "subagent", "purpose": "Deep research"},
        {"name": "sovereign-expert.md", "mode": "specialist", "purpose": "Domain expert agent"}
      ],
      "skills": [
        "knowledge-miner", "spec-generator", "provider-validator",
        "blitz-validate", "blitz-tunnel",
        "omega-doc-architect", "legacy-pattern-miner", "pr-readiness-checker"
      ]
    },
    "11_observability_system": {
      "file": "src/omega/observability.py",
      "status": "CODED AND ACTIVE",
      "capabilities": [
        "Trace ID generation (trc_uuid)",
        "Event type system (12 event types)",
        "Training dataset collection (JSONL export, disabled by default)",
        "TraceSession context manager for interaction lifecycle",
        "Stats tracking: total_events, dataset_size, event_counts, session_id"
      ],
      "note": "Events are logged but NOT wired into any workflow tracking dashboard or progress display."
    }
  },
  "summary": {
    "systems_that_actively_track_work": [
      "docs/research/INDEX.md (research item status, 37 entries)",
      "docs/operations/RESEARCH_QUEUE.md (44 research items queued)",
      "docs/operations/STATUS_OPENCODE.md (versioned status log)",
      "docs/team/COMMUNICATION_HUB.md (status summaries per component)",
      "src/omega/observability.py (runtime event tracing, 12 event types)",
      "mcp/omega_hub/server.py (hivemind focus_chain + task_current)",
      "config/providers.yaml (priority-ordered inference chain)",
      "config/models.yaml (load strategy orchestration)"
    ],
    "systems_that_COULD_be_adapted": [
      "src/omega/library/inbox.py (priority queue with status lifecycle)",
      "src/omega/library/discovery.py (async job management with status polling)",
      "src/omega/oracle/entity_workspace.py (soul.yaml tracking fields)",
      "data/entities/arch/soul.yaml (empty tracking fields)",
      "docs/research/internal-discovery/TOOLING_STRATEGY.md (SQLite schema proposal)"
    ],
    "systems_that_are_STALE_or_unused": [
      "data/entities/arch/soul.yaml - tracking fields all at zero/empty",
      "data/entities/ has no entity soul files besides arch",
      "INDEX.md shows 37/37 items ✅ but RESEARCH_QUEUE.md references R-39 through R-43",
      "COMMUNICATION_HUB.md shows R-04/R-05 as 'Not started' while INDEX.md says ✅ Complete",
      "ROADMAP.md Phase 0 has no completion tracking",
      "src/omega/bridge/elevenlabs.py contains the only TODO comment in all Python source"
    ],
    "workflow_engine_gap": "There is no unified workflow/work-item tracking system. Tracking is fragmented across: markdown tables (ROADMAP.md, STATUS_OPENCODE.md, INDEX.md), in-memory structures (hivemind, observability), file-based queues (inbox), and config priority chains (providers.yaml). No SQLite or database-based work tracking is active despite the TOOLING_STRATEGY.md spec."
  }
}
```

---

## Synthesized Analysis

### What These Three Reports Reveal Together

When read independently, each report captures one dimension of Omega's tracking landscape. When overlaid, a clear pattern emerges:

#### 1. The Codebase Was Built with Tracking in Mind

The developers (you) intentionally built tracking fields into multiple systems:

| System | Tracking Fields | Currently Used? |
|--------|----------------|-----------------|
| InboxManager | `status`, `priority (0-2)`, `created_at`, `item_id` | ✅ For content items only |
| DiscoveryOrchestrator | `status (pending/running/complete/failed)` | ✅ But ephemeral |
| Hivemind MCP | `task_current`, `focus_chain`, `decisions` | ✅ For CLI session awareness |
| ObservabilityEngine | 12 event types, `trace_id`, `session_id`, `timestamp` | ✅ For runtime tracing |
| Soul YAML | `sessions_completed`, `entities_inhabited`, `embodied_experiences[]`, `lessons_learned[]`, `soul_power` | ❌ Never written to |
| Metrics JSON (`data/logs/metrics.json`) | Arbitrary JSON dict | ⚠️ Only boundary violations |
| Research SQLite DB | `status`, `urgency`, `confidence`, `sovereignty_score`, lifecycle events | ✅ For research documents |
| BelialMiner | `classification`, `sovereignty_score`, `effort_to_extract` | ✅ For legacy mining queue |

**Interpretation**: You designed seven distributed tracking systems but never connected them into a unified view. The data is there — it's just fragmented.

#### 2. Three Databases, One Consistent Schema Language

| Database | Location | Table | Status Field | Priority Field |
|----------|----------|-------|--------------|----------------|
| Inbox items (JSON) | `data/inbox/*/` | Per-file | `pending/processing/completed/failed` | `0-2 (normal/urgent)` |
| Research documents (SQLite) | `docs/research/internal-discovery/DB/research.db` | `research_documents` | `complete/in_progress/pending/blocked/draft/in_review/superseded/archived` | From INDEX.md via manual sync |
| Hivemind sessions (JSON) | `knowledge/HALL_OF_RECORDS/*/` | Per-session | (implicit by existence) | (none) |

**Observation**: Each database uses a different status vocabulary. To build a unified work_items table, you need a canonical status enum that maps across all three.

#### 3. The ObservabilityEngine Is the Key Integrator

The ObservabilityEngine is the only system that:
- Is already wired into the full Oracle → Entity → ModelGateway pipeline
- Has a proven event type extensibility pattern (`EventType` enum)
- Already generates trace IDs that could key work items
- Has a file persistence pattern (JSONL datasets) that could be extended

Its current limitation (in-memory only) is the single largest gap identified across all three reports.

#### 4. The Research SQLite DB Is the Most Mature Schema

The `docs/research/internal-discovery/DB/research.db` already has:
- 7 tables with foreign keys
- Status lifecycle with event tracking (`lifecycle_events` table)
- Tags, relationships, and full-text search (FTS5)
- Multiple views for aggregation (`v_stale_documents`, `v_research_velocity`, etc.)
- A schema migration script (`scripts/init-research-db.py`)

This is the closest thing Omega has to a "work item database." If you want a unified system, the simplest path is to **extend this existing SQLite DB** rather than creating a new one.

#### 5. The Soul YAML Is a Philosophical Tracker, Not a Practical One

The `embodied_experiences[]` and `lessons_learned[]` fields are designed to track high-level learning ("I learned X by doing Y through entity Z"). These are not task-tracking fields — they are **cross-pollination** fields for the Entity Cycle described in `docs/gnosis/ARCHITECT.md`.

**Recommendation**: Do NOT try to use soul.yaml for task tracking. Use it for what it's designed for: tracking the Architect's growth across sessions. Task tracking should live in a separate system (the SQLite work_items table), with soul.yaml receiving summary updates only when tasks complete.

---

## Gap Analysis

### Critical Gaps (Blocking a Unified System)

| Gap | Evidence from Reports | Effort to Fix |
|-----|----------------------|----------------|
| **No persistence for runtime events** | Report #2: ObservabilityEvent log is in-memory only; ProviderMetrics is in-memory only | Low (JSONL append, same pattern as datasets) |
| **No unified work item entity** | Report #1: "NO DEDICATED TASK / PROJECT / BACKLOG / ISSUE TRACKING SYSTEM EXISTS" | Medium (extend SQLite schema) |
| **No cross-referencing between research, roadmap, and bugs** | Report #3: INDEX.md / RESEARCH_QUEUE.md / ROADMAP.md / BUG_LOG.md are four independent documents with no links | Low (add reference fields to SQLite) |
| **Tracking documents contradict each other** | Report #3: INDEX.md says R-04/R-05 ✅ but COMMUNICATION_HUB.md says 🔲 Not started. ROADMAP.md has no completion marks on Phase 0 tasks that are already done. | Zero code (manual reconciliation) |

### Moderate Gaps (Blocking a Polished System)

| Gap | Evidence | Effort |
|-----|----------|--------|
| **No dependency tracking** | Report #1: No `depends_on` or `blocked_by` field in any system | Medium (add to SQLite schema) |
| **No visual dashboard** | Report #2: "Grafana referenced in roadmap Phase 3 but not yet implemented. No HTML/visual dashboards exist yet." | Medium (HTML/js dashboard over SQLite) |
| **No aggregation across silos** | Report #2: "Events + memory + hivemind + research are siloed" | Medium (Mission Control MCP tool) |

### Low Gaps (Nice-to-Have)

| Gap | Evidence | Effort |
|-----|----------|--------|
| **Standard Python logging (not structured JSON)** | Report #2: "All 93 logging statements use plain Python logging — no structured JSON log format" | High (refactor 25 files) |
| **No user/identity model beyond The Architect** | Report #2: "No multiple users/projects supported" | Low-medium (not needed right now) |
| **Experiment tracking is hand-written** | Report #2: "EXP reports are hand-written Markdown — no programmatic experiment registry" | Low (for now) |

---

## Recommended Intervention Plan

### Four Phases, Each Independently Useful

---

#### Phase 0 — Quick Wins (Before Any Code)

These can be done right now with zero code changes and take ~2 hours total.

1. **Reconcile INDEX.md and RESEARCH_QUEUE.md**
   - Add R-39 through R-43 to INDEX.md with `🔲 Not started` status
   - Mark R-04 and R-05 as `✅ Complete` in RESEARCH_QUEUE.md (they match INDEX.md)
   - Verify all 44 RESEARCH_QUEUE.md entries have corresponding INDEX.md entries

2. **Add completion marks to ROADMAP.md Phase 0**
   - Walk through each task (0.1 through 0.15)
   - Add `✅` if done, `🔄` if in progress, keep `⬜` if not started
   - Tasks likely done: 0.2 (Iris rename), 0.3 (.env.example/README), 0.4 (dataset default), 0.8 (entities.yaml), 0.9 (hierarchy.yaml), 0.10 (soul.yaml), 0.11 (CLI commands), 0.14 (providers.yaml), 0.15 (omega.yaml)
   - Tasks likely remaining: 0.1 (MCP crashers), 0.5 (session header config), 0.7 (pillar separation cleanup), 0.12 (Remote Gemma), 0.13 (lmster hardening)

3. **Update COMMUNICATION_HUB.md**
   - Fix R-04/R-05 status to match INDEX.md
   - Add a "Status Conflict Log" section to track document drift going forward
   - Add link to this discovery report

**Quick win**: After this, an agent asking "what's the status of everything?" gets a consistent answer across all documents.

---

#### Phase 1 — Persistence (4 hours)

Make runtime tracking survive restarts.

1. **Persist Observability events** (`src/omega/observability.py`)
   - Add `_persist_event(event_type, trace_id, data)` that appends to `data/logs/events/YYYY-MM-DD.jsonl`
   - Called automatically inside existing `log_event()` method
   - Use same JSONL format as the fine-tuning dataset (already proven)
   - ~20 lines of code

2. **Persist DiscoveryOrchestrator jobs** (`src/omega/library/discovery.py`)
   - On `start_discovery()`: save `DiscoveryReport` to `data/jobs/pending/{job_id}.json`
   - On completion: move to `data/jobs/completed/{job_id}.json`
   - On failure: move to `data/jobs/failed/{job_id}.json`
   - On hub startup: load existing jobs from `data/jobs/*/` into the in-memory `_jobs` dict
   - ~40 lines of code, mirrors InboxManager pattern exactly

3. **Create `work_items` table in Research SQLite DB**
   ```sql
   CREATE TABLE work_items (
     id TEXT PRIMARY KEY,
     title TEXT NOT NULL,
     description TEXT,
     status TEXT NOT NULL DEFAULT 'backlog'
       CHECK(status IN ('backlog','ready','in_progress','review','done','archived')),
     priority TEXT NOT NULL DEFAULT 'P3'
       CHECK(priority IN ('P0','P1','P2','P3','P4')),
     source_entity TEXT,  -- entity assigned to this work
     source_document TEXT, -- link to research document ID
     depends_on TEXT,     -- comma-separated work item IDs
     tags TEXT,           -- comma-separated
     created_at TEXT NOT NULL DEFAULT (datetime('now')),
     updated_at TEXT NOT NULL DEFAULT (datetime('now')),
     completed_at TEXT
   );
   ```
   - Add to `scripts/init-research-db.py` under schema version 3
   - ~20 lines of SQL

**Quick win**: After this, work items survive restarts, are queryable via SQLite, and the DiscoveryOrchestrator can resume interrupted jobs.

---

#### Phase 2 — Mission Control MCP (8 hours)

Build an MCP server that queries the unified work items database and exposes it via the Omega Hub.

1. **Create `mcp/omega-mission-control/server.py`**
   - FastMCP server that reads from the SQLite `work_items` table
   - Exposes tools:
     - `mission_list(status=None, priority=None, entity=None)` — query work items
     - `mission_create(title, description, priority, depends_on=None)` — create a work item
     - `mission_update(id, status=None, priority=None)` — update a work item
     - `mission_stats()` — counts by status and priority
   - Integrates with Hivemind: `hivemind_get_awareness()` auto-populates `in_progress` items

2. **Register in `config/mcp_servers.json`**
3. **Add `# mission` command to Oracle CLI** via `oracle_cli.py`

**Quick win**: After this, any agent can query work items via `oracle_talk("show me all open P0 tasks")` or a direct MCP tool.

---

#### Phase 3 — The Living Soul (6 hours)

Wire the soul evolution schema to actually track progress.

1. **Increment `sessions_completed` after each `Oracle.talk()` or `Oracle.summon()`**
   - In `oracle.py`, after response is delivered, call `_track_session_evolution(entity_name, trace_id)`
   - This reads the current soul.yaml, increments `sessions_completed`, writes it back
   - ~30 lines of code

2. **Track `entities_inhabited`**
   - On `/entity` command, before switching, write the current entity session data
   - Track which entities have been inhabited (use a set in soul.yaml)

3. **Populate `embodied_experiences[]`**
   - When a work item moves to `done` in the SQLite table, compute an "experience" entry
   - Schema: `{experience: "Completed X", source_entity: "EntityName", trace_id: "...", timestamp: "...", work_item_id: "..."}`

4. **Compute `soul_power`**
   - Formula: `(sessions_completed * 0.1) + (entities_inhabited * 0.3) + (total_embodied_experiences * 0.6)`
   - Recompute after every update

**Quick win**: After this, the Architect's soul becomes a living progress tracker. Asking "what have I learned?" returns a summary of completed work items.

---

### Risk Assessment

| Risk | Phase | Likelihood | Mitigation |
|------|-------|------------|------------|
| Phase 0 doc changes introduce new contradictions | P0 | Low | Add "Last Synced" timestamp to all tracking docs |
| JSONL event persistence fills disk | P1 | Medium | Add rotation: keep last 30 days, archive older |
| Mission Control MCP conflicts with existing Hub tools | P2 | Low | Namespace tools with `mission_` prefix |
| Soul YAML writes cause file contention | P3 | Low | Use AnyIO file locks (already proven in InboxManager) |

---

## Appendices

### A. Quick Reference: File Locations

| System | Primary File(s) | Data Storage |
|--------|----------------|--------------|
| InboxManager | `src/omega/library/inbox.py` | `data/inbox/*.json` |
| DiscoveryOrchestrator | `src/omega/library/discovery.py` | In-memory only |
| Hivemind MCP | `mcp/omega_hub/server.py` | `knowledge/HALL_OF_RECORDS/*.json` |
| ObservabilityEngine | `src/omega/observability.py` | In-memory + `data/datasets/*.jsonl` |
| ResearchEngine | `src/omega/library/research.py` | `data/research/*.json` |
| Oracle | `src/omega/oracle/oracle.py` | (orchestrator only) |
| Orchestrator | `src/omega/oracle/orchestrator.py` | In-memory only |
| BelialMiner | `src/omega/entity_belial.py` | `data/mining_queue/mining_history.json` |
| Research SQLite DB | `docs/research/internal-discovery/DB/research.db` | SQLite |
| Metrics JSON | `data/logs/metrics.json` | JSON file |
| Soul YAML | `data/entities/arch/soul.yaml` | YAML file |
| Entity Registry | `config/entities.yaml` | YAML file |
| Omega Config | `config/omega.yaml` | YAML file |

### B. Canonical Status Enum (For New Work Items)

```python
class WorkItemStatus(enum.Enum):
    BACKLOG = "backlog"       # Idea, not yet prioritized
    READY = "ready"           # Prioritized, waiting for work
    IN_PROGRESS = "in_progress"  # Currently being worked on
    REVIEW = "review"         # Done, awaiting review/validation
    DONE = "done"             # Completed and validated
    ARCHIVED = "archived"     # Superseded or no longer relevant
    BLOCKED = "blocked"       # Blocked by another item or external dependency

class Priority(enum.Enum):
    P0 = "P0"  # Critical — blocks everything
    P1 = "P1"  # High — must be done this sprint
    P2 = "P2"  # Medium — should be done
    P3 = "P3"  # Low — nice to have
    P4 = "P4"  # Backlog — when time permits
```

### C. Mapping: Existing Status Fields → Canonical Status

| Source | Source Status | Maps to Canonical Status |
|--------|--------------|--------------------------|
| INDEX.md | 🔲 Not started | `backlog` |
| INDEX.md | 🔄 In progress | `in_progress` |
| INDEX.md | ✅ Complete | `done` |
| INDEX.md | ⚠️ Blocked | `blocked` |
| InboxManager | `pending` | `ready` |
| InboxManager | `processing` | `in_progress` |
| InboxManager | `completed` | `done` |
| InboxManager | `failed` | `blocked` |
| DiscoveryReport | `pending` | `ready` |
| DiscoveryReport | `running` | `in_progress` |
| DiscoveryReport | `complete` | `done` |
| DiscoveryReport | `failed` | `blocked` |
| Research SQLite | `draft` | `ready` |
| Research SQLite | `in_review` | `review` |
| Research SQLite | `complete` | `done` |
| Research SQLite | `superseded` | `archived` |
| BUG_LOG.md | `OPEN` | `in_progress` |
| BUG_LOG.md | `RESOLVED` | `done` |

### D. Existing Research Items Referenced but Undiscovered

The following research items have deliverables defined in `docs/operations/RESEARCH_QUEUE.md` but no corresponding files were found in `docs/research/`:

| ID | Title | Urgency | Deliverable Path |
|----|-------|---------|------------------|
| R-19 | Soul Abstraction Logic | 🟡 High | `docs/research/R19_soul_abstraction_logic.md` |
| R-20 | Memory Tiering Strategy | 🟡 High | `docs/research/R20_memory_tiering_strategy.md` |
| R-21 | Agent Handoff Protocol | 🟢 Strategic | `docs/research/R21_agent_handoff_protocol.md` |
| R-22 | MCP Community Audit | 🟢 Strategic | `docs/research/R22_mcp_community_audit.md` |
| R-23 | Cold-Start Mitigation | 🟢 Strategic | `docs/research/R23_cold_start_mitigation.md` |
| R-24 | Soul-to-Visual Mapping (VR Foundation) | 🟢 Strategic | `docs/research/R24_soul_to_visual_mapping.md` |
| R-35 | Agent Handoff & State Transfer Protocol | 🟢 Strategic | `docs/research/R35_agent_handoff_protocol.md` |
| R-36 | Soul-to-Visual Mapping (VR Foundation) | 🟢 Strategic | `docs/research/R36_soul_visual_mapping.md` |
| R-37 | Axiom & Ideal Generation Framework | 🟢 Strategic | `docs/research/R37_axiom_ideal_framework.md` |
| R-39 | Legacy Library & Curation Deep Dive | 🔴 Critical | `docs/research/R39_legacy_library_deep_dive.md` |
| R-40 | Sovereign Lifecycle & Native Persistence | 🔴 Critical | `docs/research/R40_sovereign_lifecycle_persistence.md` |
| R-41 | Adaptive Orchestration Topologies | 🔴 Critical | `docs/research/R41_adapt_orch_topologies.md` |
| R-42 | Hardware Steering (Ryzen 7 5700U / Zen 2) | 🔴 Critical | `docs/research/R42_zen2_hardware_steering.md` |
| R-43 | ElevenLabs Sovereign Console (Hackathon Blitz) | 🔴 Critical | `docs/research/R43_elevenlabs_sovereign_console.md` |

### E. The Only Source TODO

```python
# File: src/omega/bridge/elevenlabs.py
# TODO: Implement ElevenLabs webhook routing
```

This is the only TODO comment in all 25+ Python source files analyzed across the three discovery reports.

---

*End of report. Generated 2026-05-15 by SOPHIA / gemma-4-31b-it via OpenCode CLI. Trace IDs: `trc_deep_synthesis`, `trc_7f9e6c4b`.*
