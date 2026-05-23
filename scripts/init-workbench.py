#!/usr/bin/env python3
"""
Omega Sovereign Workbench — Database Initialization Script
Creates the project management infrastructure for the Xoe-NovAi Foundation.

AP Token: AP-WORKBENCH-DB-v1.0.0
⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_workbench ⬡ DB-INIT

Usage:
    python3 scripts/init-workbench.py              # Initialize database
    python3 scripts/init-workbench.py --seed        # Initialize + seed with current projects
    python3 scripts/init-workbench.py --stats       # Show statistics
"""

import sqlite3
import os
import sys
import json
from datetime import datetime

WORKBENCH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "workbench"
)
DB_PATH = os.path.join(WORKBENCH_DIR, "workbench.db")

# ── Schema (extends research.db work_items with projects + decisions) ──────

SCHEMA_SQL = """
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now')),
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description)
VALUES (1, 'Initial workbench schema: projects, work_items with project_id, decisions, artifacts');

-- Projects registry
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK(status IN ('active','paused','completed','archived','planned')),
    priority TEXT NOT NULL DEFAULT 'P3'
        CHECK(priority IN ('P0','P1','P2','P3','P4')),
    era TEXT,
    partition_location TEXT,
    estimated_value TEXT CHECK(estimated_value IN ('critical','high','medium','low')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);

-- Work items (extends research.db schema with project_id)
CREATE TABLE IF NOT EXISTS work_items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'backlog'
        CHECK(status IN ('backlog','ready','in_progress','review','done','archived','blocked')),
    priority TEXT NOT NULL DEFAULT 'P3'
        CHECK(priority IN ('P0','P1','P2','P3','P4')),
    project_id TEXT REFERENCES projects(id),
    workstream TEXT,
    source_entity TEXT,
    source_document TEXT,
    depends_on TEXT,
    tags TEXT,
    trace_id TEXT,
    estimated_hours REAL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_work_items_project ON work_items(project_id);
CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(status);
CREATE INDEX IF NOT EXISTS idx_work_items_priority ON work_items(priority);

-- Immutable decisions register
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    context TEXT NOT NULL,
    decision TEXT NOT NULL,
    rationale TEXT NOT NULL,
    alternatives TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK(status IN ('active','superseded','reversed')),
    project_id TEXT REFERENCES projects(id),
    trace_id TEXT,
    author TEXT DEFAULT 'The Architect',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    superseded_by TEXT,
    UNIQUE(id)
);

CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project_id);
CREATE INDEX IF NOT EXISTS idx_decisions_status ON decisions(status);

-- Legacy artifacts catalog (mined assets tracker)
CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    artifact_type TEXT CHECK(artifact_type IN ('document','code','config','model','chat_log','persona','skill','strategy','research','tutorial')),
    partition TEXT CHECK(partition IN ('root','omega_library','omega_vault','external')),
    path TEXT NOT NULL,
    size_bytes INTEGER,
    era TEXT,
    classification TEXT CHECK(classification IN ('strategic','technical','archival','noise')),
    sovereignty_score INTEGER CHECK(sovereignty_score BETWEEN 1 AND 10),
    effort_to_extract TEXT CHECK(effort_to_extract IN ('low','medium','high')),
    mining_status TEXT NOT NULL DEFAULT 'unmined'
        CHECK(mining_status IN ('unmined','queued','in_progress','mined','partial','deprecated')),
    summary TEXT,
    related_research TEXT,
    discovered_at TEXT NOT NULL DEFAULT (datetime('now')),
    mined_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_artifacts_partition ON artifacts(partition);
CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts(mining_status);
CREATE INDEX IF NOT EXISTS idx_artifacts_classification ON artifacts(classification);
CREATE INDEX IF NOT EXISTS idx_artifacts_sovereignty ON artifacts(sovereignty_score);

-- Cross-document references
CREATE TABLE IF NOT EXISTS references_bridge (
    source_type TEXT CHECK(source_type IN ('artifact','decision','project','work_item')),
    source_id TEXT NOT NULL,
    target_type TEXT CHECK(target_type IN ('artifact','decision','project','work_item','research_doc')),
    target_id TEXT NOT NULL,
    relationship TEXT DEFAULT 'references',
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (source_type, source_id, target_type, target_id)
);

-- Views
CREATE VIEW IF NOT EXISTS v_project_summary AS
SELECT 
    p.id, p.name, p.status, p.priority, p.era,
    COUNT(w.id) AS total_tasks,
    SUM(CASE WHEN w.status = 'done' THEN 1 ELSE 0 END) AS tasks_done,
    SUM(CASE WHEN w.status = 'blocked' THEN 1 ELSE 0 END) AS tasks_blocked,
    SUM(CASE WHEN w.status IN ('backlog','ready') THEN 1 ELSE 0 END) AS tasks_pending,
    SUM(CASE WHEN w.status = 'in_progress' THEN 1 ELSE 0 END) AS tasks_active,
    COUNT(d.id) AS decisions_made
FROM projects p
LEFT JOIN work_items w ON w.project_id = p.id
LEFT JOIN decisions d ON d.project_id = p.id
GROUP BY p.id;

CREATE VIEW IF NOT EXISTS v_mining_pipeline AS
SELECT 
    classification,
    mining_status,
    COUNT(*) AS count,
    SUM(CASE WHEN sovereignty_score >= 8 THEN 1 ELSE 0 END) AS high_value
FROM artifacts
GROUP BY classification, mining_status
ORDER BY classification, mining_status;

CREATE VIEW IF NOT EXISTS v_recent_decisions AS
SELECT id, substr(decision, 1, 80) AS decision_preview, project_id, author, created_at
FROM decisions
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 20;
"""


def init_database():
    """Create the workbench database and schema."""
    os.makedirs(WORKBENCH_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    print(f"✅ Workbench database initialized: {DB_PATH}")
    print(f"   Schema version: 1")


def seed_projects(conn):
    """Seed the database with known projects from discovery."""
    projects = [
        # Core Engine Projects
        ("prj_engine_core", "Omega Engine Core", "EntityRegistry, ModelGateway, Provider Fabric, CLI, MCP Hub — the universal runtime", "active", "P0", "Era 6", "critical"),
        ("prj_provider_fabric", "Provider Fabric & Key Pool", "Google 8-key rotation, SambaNova, Cerebras, native inference, provider chain hardening", "active", "P1", "Era 6", "critical"),
        ("prj_soul_engine", "Soul Engine & Cross-Pollination", "soul.yaml evolution, abstraction pipeline, cross-entity memory sharing, R-30/R-31 implementation", "planned", "P1", "Era 6", "high"),
        
        # Systems Hardening Projects
        ("prj_agent_hardening", "OpenCode Agent & Skill Hardening", "Fix frontmatter on all agents and skills, merge overlaps, create missing skills", "planned", "P0", "Era 6", "critical"),
        ("prj_mcp_consolidation", "MCP Server Consolidation", "Fix critical bugs, choose Hub architecture, eliminate duplication, adopt Streamable HTTP", "planned", "P0", "Era 6", "critical"),
        ("prj_memory_wiring", "MemoryStore Wiring", "Wire MemoryStore into oracle.py flow, implement context injection in ContextBuilder", "planned", "P1", "Era 6", "high"),
        ("prj_handoff_protocol", "Agent Handoff Protocol", "Create omega-handoff MCP server, implement /handover CLI, HandoffState schema", "planned", "P1", "Era 6", "high"),
        
        # Workbench Infrastructure
        ("prj_workbench", "Sovereign Workbench", "Project registry, decision register, work tracking CLI, strategy timeline", "active", "P1", "Era 6", "high"),
        
        # Legacy Mining Projects
        ("prj_mine_old_stacks", "Mine: Old Stacks Archive", "Full dump at Archives/Old-Stacks/Xoe-NovAi — the only surviving pre-Omega complete stack", "planned", "P0", "Eras 1-3", "critical"),
        ("prj_mine_docs_backup", "Mine: Docs Backup Strategy Documents", "Full docs-backup/internal_docs with ANAi strategy, Arcana-NovAi implementation", "planned", "P0", "Eras 1-4", "critical"),
        ("prj_mine_vault", "Mine: Omega Vault", "Ancestral Hub, stack-cat snapshots, XNAi copies, origins", "planned", "P1", "Eras 0-3", "high"),
        ("prj_mine_grok", "Mine: Grok Account Exports", "8 accounts of full chat history from the undocumented period (Nov 2025 - Mar 2026)", "planned", "P1", "Era 3", "high"),
        ("prj_mine_tarot", "Mine: Tarot Genesis Materials", "First 5 Cards Grok Chat, Lilith Deck design docs, card notes — THE ABSOLUTE ORIGINS", "planned", "P1", "Era 0", "high"),
        ("prj_mine_mnemosyne", "Mine: Mnemosyne Memory Archive", "Kabbalistic 13-sphere memory system on omega_library", "planned", "P2", "Era 5", "medium"),
        ("prj_mine_system_prompts", "Mine: System Prompts Library", "50+ system prompts across all eras — every era's understanding of the system", "planned", "P1", "Eras 0-6", "high"),
        ("prj_mine_lmstudio", "Mine: LM Studio & Ollama Configs", "Custom model configs, KV cache tuning, offload ratios, persona experiments", "planned", "P2", "Era 3", "medium"),
        ("prj_mine_legacy_repos", "Mine: Legacy Repos (omega-stack + xna-omega)", "Deep pattern extraction from 33,000+ files and 560MB Temple Grade era", "planned", "P1", "Eras 4-5", "critical"),
        
        # Community Projects
        ("prj_community_tool", "Omega Desktop Community Tool", "One-click installer, Entity Studio, Stack Builder Wizard, Data Sovereignty Toolkit", "planned", "P2", "Era 6", "high"),
        ("prj_foundation_docs", "Xoe-NovAi Foundation Documentation", "Positioning framework, tutorials, articles, community onboarding from mined assets", "planned", "P2", "Era 6", "medium"),
        
        # Stack Projects
        ("prj_arcana_nova", "Arcana-Nova Stack", "10 Pillar Keepers, 42 Ma'at Ideals, Tarot circuitry, VR scenes, 156 axioms", "planned", "P2", "Era 6", "high"),
        ("prj_torment_stack", "Torment Stack", "Planescape: Torment inspired — The Nameless One, Dak'kon, Annah, 15 philosophies", "planned", "P3", "Era 6", "medium"),
    ]
    
    for p in projects:
        conn.execute("""
            INSERT OR IGNORE INTO projects (id, name, description, status, priority, era, estimated_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, p)
    
    conn.commit()
    print(f"   Seeded {len(projects)} projects")


def seed_decisions(conn):
    """Seed the decisions register with key architectural decisions from PIVOT_LOG.md."""
    decisions = [
        ("dec_001", "New Repo Location", "Create omega-engine at ~/Documents/Xoe-NovAi/omega-engine/", "Both existing repos have architectural drift. Fresh repo from proven concepts.", "Keep at ~/omega/ (confusion), Keep at xna-omega/ (Temple Grade drift)", "prj_engine_core"),
        ("dec_002", "Original Pantheon", "Use the 10-entity syncretic pantheon from ChatGPT genesis export", "This was the user's original design. Single-pantheon systems lose flexibility.", "Egyptian-only pantheon", "prj_arcana_nova"),
        ("dec_003", "Engine vs Stack", "Omega is the ENGINE. Stacks (Arcana-Nova, Torment) are instantiations ON TOP.", "Clarified by user question: 'Is Omega the engine that runs every stack, not the stack itself?'", "Omega as a single stack", "prj_engine_core"),
        ("dec_004", "YAML Entity Storage", "Entities stored in YAML files, not PostgreSQL", "PostgreSQL coupling blocked CI/CD in xna-omega. YAML is user-editable, version-control friendly.", "PostgreSQL entity storage (Temple Grade)", "prj_engine_core"),
        ("dec_005", "Provider Chain Priority", "Priority: native GGUF → lmster → Google 8-key → SambaNova → Cerebras → Ollama", "Local-first sovereignty mandate. Cloud providers are high-capability extensions, not the primary.", "Cloud-first priority", "prj_provider_fabric"),
        ("dec_006", "AnyIO Sovereignty", "All async code uses AnyIO, not asyncio", "Prevents event loop conflicts, enables structured concurrency, multi-backend compatibility.", "Mixed asyncio/anyio (Temple Grade)", "prj_engine_core"),
        ("dec_007", "Zero Telemetry", "No tracking, no analytics, no phone-home. Ever.", "Core Lilith Axiom. The system must be trustable without auditing.", "Opt-out telemetry", "prj_engine_core"),
        ("dec_008", "MCP Hub Consolidation", "Consolidate MCP into omega_hub as primary endpoint", "Standalone servers created duplication. Hub provides single point of integration for OpenCode.", "6 standalone MCP servers with overlapping tools", "prj_mcp_consolidation"),
        ("dec_009", "OpenCode as Primary CLI", "OpenCode (MIT, Go, 75+ providers, 30K LOC) as the agent framework", "Most granular permission system, local server architecture, LSP native, full MCP support.", "Claude Code (proprietary, 500K LOC), Cline (VS Code only)", "prj_agent_hardening"),
        ("dec_010", "MemoryStore Tiering", "Hot/Warm/Cold tiering with YAML + JSON persistence", "Industry patterns confirm this approach (Letta's OS model, Mem0's extraction). No framework lock-in.", "Mem0 integration, Letta runtime adoption", "prj_memory_wiring"),
    ]
    
    for d in decisions:
        conn.execute("""
            INSERT OR IGNORE INTO decisions (id, context, decision, rationale, alternatives, project_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, d)
    
    conn.commit()
    print(f"   Seeded {len(decisions)} decisions")


def seed_artifacts(conn):
    """Seed the artifacts catalog with known high-value assets from discovery."""
    artifacts = [
        # P0: Critical artifacts (from R44_ENGINE_STACK_SEPARATION.md)
        ("art_old_stacks", "Old Stacks Full Dump", "The only surviving complete pre-Omega stack with Dockerfiles, docker-compose, config.toml", "code", "root", 
         "~/Documents/Archives/Old-Stacks/Xoe-NovAi/", None, "Eras 1-3", "strategic", 9, "low", "unmined",
         "Contains the purest form of the original Chainlit+FastAPI+RAG architecture"),
        ("art_ana_strategy", "ANAi Strategy Blueprint", "Arcana-NovAi implementation strategy and systems blueprint", "strategy", "root",
         "~/Documents/docs-backup/internal_docs/01-strategic-planning/", None, "Era 1", "strategic", 10, "medium", "unmined",
         "The missing strategic layer for Arcana-Nova stack implementation"),
        ("art_first_cards", "First 5 Cards Grok Chat", "1833-line genesis document — the absolute origin of the project", "chat_log", "omega_library",
         "/media/arcana-novai/omega_library/intake/mining_queue/Omega-Early-Material/tarot/First 5 cards Grok Chat 05-25-2025.txt",
         1833*80, "Era 0", "strategic", 10, "low", "unmined",
         "THE genesis document. Shows the original archetypal exploration that seeded all entities."),
        ("art_lilith_persona", "Lilith Persona JSON", "Complete Lilith persona with voice profile, behavioral patterns, query modifiers", "persona", "root",
         "~/Documents/docs_1/personas/lilith.json", None, "Era 0", "technical", 9, "low", "unmined",
         "Ready-made template for soul.yaml enhancement"),
        ("art_positioning", "Omega Positioning Framework", "12-file, 488+ line community positioning blueprint for all 3 audience tiers", "strategy", "omega_library",
         "/media/arcana-novai/omega_library/intake/inbox/omega-positioning-framework/", None, "Era 5", "strategic", 10, "low", "unmined",
         "The complete community rollout blueprint — average users, technical, esoteric"),
        ("art_system_prompts", "System Prompts Library (50+)", "Every era's understanding of the system captured in system prompts", "document", "root",
         "~/Documents/docs_1/system-prompts/", None, "Eras 0-6", "technical", 8, "medium", "unmined",
         "Chronological record of how the system was understood at each stage"),
        ("art_foundation_vs_arcana", "Foundation vs Arcana Document", "The Feb 2026 document that first formalized Engine vs Stack separation", "strategy", "root",
         "~/Documents/Xoe-NovAi/omega-stack-legacy/docs/03-reference/architecture/2026-02-06-xoe-novai-foundation-vs-arcana-novai-v1.0.0.md",
         None, "Era 4", "strategic", 10, "low", "mined",
         "Already referenced in R44. Key concepts extracted."),
        ("art_xnai_blueprint", "XNAI Blueprint", "715-line complete v0.1.4-stable blueprint with 5 design patterns and 42-issue matrix", "document", "root",
         "~/archive/foundation-legacy/versions/Xoe-NovAi/library/XNAI_blueprint.md", None, "Era 2", "technical", 9, "low", "unmined",
         "Production-hardened patterns: retry, circuit breaker, fsync, non-blocking subprocess"),
        ("art_session_1e18", "The Engine/Stack Pivot Session", "5,600+ line session that birthed the Engine vs Stack separation", "chat_log", "root",
         "~/Documents/Xoe-NovAi/xna-omega-legacy/opencode-omega-engine-vision-deepening-session-ses_1e18-05-13-2026.md",
         None, "Era 5", "strategic", 10, "low", "mined",
         "Already referenced. Contains the pivotal question that changed the architecture."),
        ("art_roc_test", "RocRacoon Test v1 — LM Studio", "First local model experimentation with custom persona roleplay", "research", "omega_library",
         "/media/arcana-novai/omega_library/intake/mining_queue/RocRacoon Test v1 - LM Studio.md", None, "Era 3", "technical", 7, "low", "unmined",
         "Shows the birth of the entity-persona concept through local model experimentation"),
        ("art_lmstudio_configs", "LM Studio Custom Model Configs", "KV cache tuning (q8_0), GPU offload ratios (0.5-0.56), context length experimentation", "config", "root",
         "~/.lmstudio/.internal/user-concrete-model-default-config/", None, "Eras 3-4", "technical", 8, "low", "unmined",
         "Early local model optimization experiments with specific quant and hardware tuning"),
        ("art_strategy_master", "STRATEGY-MASTER-INDEX.md", "Navigation hub for all strategies across the omega-stack era", "strategy", "root",
         "~/Documents/Xoe-NovAi/omega-stack-legacy/STRATEGY-MASTER-INDEX.md", None, "Era 4", "strategic", 8, "low", "mined",
         "Already referenced. Cross-reference for completeness."),
        ("art_resonance_map", "Resonance Mappings YAML", "26-sphere domain-to-entity routing map from Temple Grade era", "config", "root",
         "~/Documents/Xoe-NovAi/xna-omega-legacy/resonance_mappings.yaml", None, "Era 5", "technical", 8, "low", "mined",
         "Domain routing patterns that could enhance the current entity registry"),
        
        # P1: High-value artifacts
        ("art_stack_cat", "Stack-Cat Snapshots", "Complete point-in-time project copies from the XNAi era", "code", "omega_vault",
         "/media/arcana-novai/omega_vault/from main partition/stack-cat-v0_1_2-full/", None, "Era 2", "archival", 7, "medium", "unmined",
         "Complete project structure at specific historical points"),
        ("art_grok_exports", "Grok Account Exports (8 accounts)", "Full chat history from the undocumented Nov 2025 - Mar 2026 period", "chat_log", "omega_library",
         "/media/arcana-novai/omega_library/intake/inbox/grok-accounts-exports/", None, "Era 3", "archival", 7, "high", "unmined",
         "The missing 4 months of development history"),
        ("art_mnemosyne", "Mnemosyne Kabbalistic Memory System", "13-sphere tiered memory system with handoffs and vaults", "code", "omega_library",
         "/media/arcana-novai/omega_library/data_archive/mnemosyne/", None, "Era 5", "technical", 7, "medium", "unmined",
         "The most complete pre-Omega memory architecture — could enhance current MemoryStore"),
        ("art_ancestral_hub", "ANCESTRAL_HUB Origins", "Pre-March 2025 origin documents and legacy configs", "document", "omega_vault",
         "/media/arcana-novai/omega_vault/ANCESTRAL_HUB/origins/", None, "Era 0", "archival", 8, "medium", "unmined",
         "May contain the oldest recoverable design notes"),
        ("art_legacy_entity_code", "Legacy EntityRegistry Source", "Fully functional YAML entity registry from omega-stack codebase", "code", "root",
         "~/Documents/Xoe-NovAi/omega-stack-legacy/app/XNAi_rag_app/core/entities/registry.py", None, "Era 4", "technical", 8, "low", "mined",
         "Reference implementation. Current omega-engine simplified from this."),
        ("art_circuit_breaker", "Legacy Circuit Breaker", "Production-grade circuit breaker implementation", "code", "root",
         "~/Documents/Xoe-NovAi/omega-stack-legacy/src/omega/circuit_breaker.py", None, "Era 4", "technical", 8, "low", "unmined",
         "Directly portable — implement in current providers.py"),
        ("art_ollama_history", "Ollama Testing History", "Krikri-8B tested for Omega system awareness", "chat_log", "root",
         "~/.ollama/history", None, "Era 4", "archival", 4, "low", "unmined",
         "Shows early testing of local models for Omega knowledge"),
        ("art_xnai_versions", "XNAi Old Version Snapshots", "Multiple XNAi v0.1.2 snapshots", "code", "omega_library",
         "/media/arcana-novai/omega_library/intake/mining_queue/XNAi Old Versions/", None, "Era 2", "archival", 6, "medium", "unmined",
         "Historical versions for architecture comparison"),
        ("art_telemetry_audit", "8-Telemetry-Disable Pattern", "Comprehensive telemetry audit script and 8-point verification", "code", "root",
         "~/archive/foundation-legacy/versions/Xoe-NovAi/ (telemetry audit scripts)", None, "Era 2", "technical", 8, "medium", "unmined",
         "Could be revived for community Data Sovereignty Toolkit"),
    ]
    
    for a in artifacts:
        conn.execute("""
            INSERT OR IGNORE INTO artifacts (id, name, description, artifact_type, partition, path, size_bytes, era, classification, sovereignty_score, effort_to_extract, mining_status, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, a)
    
    conn.commit()
    print(f"   Seeded {len(artifacts)} artifacts")


def seed_work_items(conn):
    """Create work items for all known tasks (backlog only - not executing)."""
    items = [
        # ── Workstream A: Agent & Skill Hardening ──
        ("wi_agent_frontmatter", "Fix frontmatter on researcher.md, researcher-omnidroid.md, sovereign-expert.md", "Add mode, permission, steps, description frontmatter to 3 agent files", "backlog", "P0", "prj_agent_hardening", "A"),
        ("wi_skill_frontmatter", "Fix frontmatter on 5 skill files", "Add name, description to omega-doc-architect, legacy-pattern-miner, pr-readiness-checker, blitz-validate, blitz-tunnel", "backlog", "P0", "prj_agent_hardening", "A"),
        ("wi_merge_skills", "Merge overlapping skill pairs", "knowledge-miner + legacy-pattern-miner, spec-generator + omega-doc-architect", "backlog", "P2", "prj_agent_hardening", "A"),
        ("wi_create_handoff_skill", "Create agent-handoff skill", "Formal handoff protocol documentation as an OpenCode skill", "backlog", "P1", "prj_agent_hardening", "A"),
        ("wi_create_soul_skill", "Create soul-evolution skill", "Lesson extraction, abstraction pipeline, cross-pollination as a skill", "backlog", "P1", "prj_agent_hardening", "A"),
        ("wi_create_mcp_skill", "Create mcp-server skill", "MCP server creation standards as a skill", "backlog", "P1", "prj_agent_hardening", "A"),

        # ── Workstream B: MCP Consolidation ──
        ("wi_fix_hub_get_engine", "Fix get_engine() undefined in omega_hub/server.py", "Add missing import of get_engine from omega.observability", "backlog", "P0", "prj_mcp_consolidation", "B"),
        ("wi_fix_hub_asyncio", "Replace asyncio.create_task with anyio.create_task_group", "Fix violation of AnyIO mandate in library_discovery_start", "backlog", "P0", "prj_mcp_consolidation", "B"),
        ("wi_fix_hub_await", "Add await to library.domains() and library.stats()", "Both are async functions called without await in omega_hub", "backlog", "P0", "prj_mcp_consolidation", "B"),
        ("wi_choose_hub_architecture", "Choose and implement MCP architecture (Hub or Standalone)", "Single source of truth for MCP tools. Eliminate all duplication.", "backlog", "P1", "prj_mcp_consolidation", "B"),
        ("wi_mcp_file_locking", "Add file locking to shared metrics.json writes", "Prevent race conditions on concurrent MCP writes", "backlog", "P1", "prj_mcp_consolidation", "B"),
        ("wi_mcp_streamable_http", "Upgrade MCP servers to Streamable HTTP transport", "Replace SSE with MCP 2025-11-25 spec Streamable HTTP", "backlog", "P2", "prj_mcp_consolidation", "B"),
        ("wi_mcp_best_practices", "Apply MCP best practices to all tools", "≤15 tools per server, NOT-for guards, OTel spans, progress notifications, structured output", "backlog", "P2", "prj_mcp_consolidation", "B"),

        # ── Workstream C: Memory & Handoff ──
        ("wi_wire_memorystore", "Wire MemoryStore into oracle.py talk() and summon()", "Add add_exchange calls after every response generation", "backlog", "P1", "prj_memory_wiring", "C"),
        ("wi_implement_context_injection", "Implement context injection in oracle.py", "Use ContextBuilder to inject recent exchanges before generation", "backlog", "P1", "prj_memory_wiring", "C"),
        ("wi_abstraction_pipeline", "Implement lesson abstraction pipeline", "LLM-based extraction of substantive lessons from sessions (R-30)", "backlog", "P1", "prj_soul_engine", "C"),
        ("wi_cross_pollination", "Implement cross-pollination mechanics", "Share lessons between entities based on domain overlap (R-31)", "backlog", "P1", "prj_soul_engine", "C"),
        ("wi_create_handoff_mcp", "Create omega-handoff MCP server", "HandoffState schema, save/load/list/finalize endpoints", "backlog", "P1", "prj_handoff_protocol", "C"),
        ("wi_handover_cli", "Implement /handover CLI command", "omega handover save/load/list for structured agent handoffs", "backlog", "P1", "prj_handoff_protocol", "C"),
        ("wi_orchestrator_handoff", "Add handoff posting to Orchestrator", "Auto-post handoff to Hivemind after dispatched agent completes", "backlog", "P1", "prj_handoff_protocol", "C"),

        # ── Workstream D: Workbench Infrastructure ──
        ("wi_project_cli", "Implement omega project CLI commands", "list, add, status, focus commands for project management", "backlog", "P1", "prj_workbench", "D"),
        ("wi_work_cli", "Implement omega work CLI commands", "list, add, start, complete commands for task tracking", "backlog", "P1", "prj_workbench", "D"),
        ("wi_decision_cli", "Implement omega decision CLI commands", "log, query commands for immutable decision register", "backlog", "P1", "prj_workbench", "D"),
        ("wi_project_context", "Wire project context into entity routing", "Inject active project context into system prompts", "backlog", "P2", "prj_workbench", "D"),

        # ── Workstream E: Cross-Agent Awareness ──
        ("wi_a2a_agent_cards", "Create A2A Agent Card for each entity", "GET /.well-known/agent.json with capabilities", "backlog", "P3", "prj_engine_core", "E"),
        ("wi_a2a_task_endpoint", "Add A2A task endpoint to omega_hub", "POST /a2a/tasks with JSON-RPC 2.0 + SSE streaming", "backlog", "P3", "prj_engine_core", "E"),
        ("wi_hivemind_ttl", "Add TTL and presence to Hivemind", "Auto-expire stale sessions, heartbeat mechanism", "backlog", "P2", "prj_mcp_consolidation", "E"),

        # ── Critical Engine Bugs (from R44) ──
        ("wi_fix_c1", "C-1: Fix gnosis_proxy.py broken import (from src.omega → from .)", "Change import to relative path. BLOCKS ALL INFERENCE.", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c2", "C-2: Fix soul.yaml race condition and non-atomic write", "Use tempfile + os.replace for atomic writes, add anyio.Lock", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c3", "C-3: Replace blocking subprocess.run in async context", "Use anyio.run_process in orchestrator.py", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c4", "C-4: Add NativeGGUFProvider to ResourceGuard protection", "Add to isinstance check in model_gateway.py", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c7", "C-7: Fix or remove anyio.Deque() in curation_pipeline.py", "Replace with collections.deque or delete file", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c8", "C-8: Rotate exposed API keys in version control", "Move Exa, Brave, Tavily keys to .env. Rotate all compromised keys.", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c9", "C-9: Add .env to .gitignore", "Remove tracked .env file, track only .env.example", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c10", "C-10: Fix setup.sh install extras", "Change 'iris' to correct extras: cli,voice,all,dev", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c11", "C-11: Fix Belial container missing dependencies", "Add httpx, anyio, pyyaml to container image", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c12", "C-12: Fix providers.yaml native-gguf model path", "Add phi-4-mini to models.yaml or correct path", "backlog", "P0", "prj_provider_fabric", "F"),
        ("wi_fix_c13", "C-13: Replace asyncio.create_task with anyio in MCP Hub", "Use anyio.create_task_group", "backlog", "P0", "prj_mcp_consolidation", "F"),
        ("wi_fix_c14", "C-14: Fix Belial relative paths", "Use DATA_DIR consistent with rest of codebase", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c15", "C-15: Fix duplicate PodmanArgs in Belial container", "Combine into single line", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c16", "C-16: Fix setup.sh wrong image tags", "Align with docker-compose.yml versions", "backlog", "P0", "prj_engine_core", "F"),
        ("wi_fix_c17", "C-17: Fix entity_workspace.py BASE_DIR off by one", "Change from 5 .parent calls to 4", "backlog", "P0", "prj_engine_core", "F"),

        # ── Provider Chain ──
        ("wi_google_key_pool", "Implement GoogleKeyPool class", "Round-robin rotation across 8 API keys with rate limit tracking", "backlog", "P1", "prj_provider_fabric", "G"),
        ("wi_reorder_providers", "Reorder provider chain to native→lmster→cloud", "Update config/providers.yaml to match desired priority", "backlog", "P1", "prj_provider_fabric", "G"),
        ("wi_add_sambanova", "Add SambaNova provider", "Implement from research R-02 spec", "backlog", "P1", "prj_provider_fabric", "G"),
        ("wi_add_cerebras", "Add Cerebras provider", "Implement from research R-03 spec", "backlog", "P1", "prj_provider_fabric", "G"),
        ("wi_build_llamacpp", "Build llama-cpp-python with Zen 2 flags", "Compile with -march=znver2, AVX2, FMA, F16C", "backlog", "P1", "prj_provider_fabric", "G"),
        ("wi_fix_native_gguf", "Fix NativeGGUFProvider integration", "Model path, ResourceGuard, test suite", "backlog", "P1", "prj_provider_fabric", "G"),
        
        # ── Legacy Mining ──
        ("wi_mine_old_stacks", "Deep mine: Old Stacks archive", "Extract Dockerfiles, docker-compose, config.toml, Makefiles from pre-Omega era", "backlog", "P0", "prj_mine_old_stacks", "H"),
        ("wi_mine_docs_backup", "Deep mine: docs-backup strategy docs", "Extract ANAi Systems Blueprint, Arcana-NovAi implementation strategy", "backlog", "P0", "prj_mine_docs_backup", "H"),
        ("wi_mine_grok", "Deep mine: 8 Grok accounts", "Full chat history extraction from undocumented Nov 2025 - Mar 2026 period", "backlog", "P1", "prj_mine_grok", "H"),
        ("wi_mine_tarot", "Deep mine: Tarot genesis materials", "First 5 Cards Grok Chat, Lilith Deck design, card notes", "backlog", "P1", "prj_mine_tarot", "H"),
        ("wi_mine_system_prompts", "Deep mine: System prompts library", "Catalog 50+ system prompts chronologically, extract era understanding", "backlog", "P1", "prj_mine_system_prompts", "H"),
        ("wi_mine_circuit_breaker", "Extract and port legacy circuit breaker", "Port circuit breaker pattern to current providers.py", "backlog", "P1", "prj_mine_legacy_repos", "H"),
        
        # ── Community ──
        ("wi_community_installer", "Design Omega Desktop installer", "One-command install with auto hardware detection", "backlog", "P2", "prj_community_tool", "I"),
        ("wi_entity_studio", "Design Entity Studio prototype", "Visual entity editor (CLI-first, web later)", "backlog", "P2", "prj_community_tool", "I"),
        ("wi_community_docs", "Publish Omega Positioning Framework as community docs", "Reformat intake docs for public consumption", "backlog", "P2", "prj_foundation_docs", "I"),
    ]
    
    for item in items:
        conn.execute("""
            INSERT OR IGNORE INTO work_items (id, title, description, status, priority, project_id, workstream)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, item)
    
    conn.commit()
    print(f"   Seeded {len(items)} work items")


def seed_all():
    """Seed the database with all discovered projects, decisions, artifacts, and tasks."""
    conn = sqlite3.connect(DB_PATH)
    
    print("\n   ── Seeding Projects ──")
    seed_projects(conn)
    
    print("   ── Seeding Decisions ──")
    seed_decisions(conn)
    
    print("   ── Seeding Artifacts ──")
    seed_artifacts(conn)
    
    print("   ── Seeding Work Items ──")
    seed_work_items(conn)
    
    conn.close()
    print("\n✅ Seed complete!")


def show_stats():
    """Display database statistics."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("\n📊 Workbench Statistics:")
    print("─" * 40)
    
    cur.execute("SELECT COUNT(*) FROM projects")
    print(f"   Projects:     {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM work_items")
    print(f"   Work Items:   {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM work_items WHERE status = 'backlog'")
    print(f"   Backlog:      {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM decisions")
    print(f"   Decisions:    {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM artifacts")
    print(f"   Artifacts:    {cur.fetchone()[0]}")
    
    cur.execute("SELECT COUNT(*) FROM artifacts WHERE mining_status = 'unmined'")
    print(f"   Unmined:      {cur.fetchone()[0]}")
    
    print("\n   ── By Priority ──")
    for row in conn.execute("SELECT priority, COUNT(*) FROM work_items GROUP BY priority ORDER BY priority"):
        print(f"   {row[0]}: {row[1]} items")
    
    print("\n   ── By Workstream ──")
    for row in conn.execute("SELECT workstream, COUNT(*) FROM work_items WHERE workstream IS NOT NULL GROUP BY workstream ORDER BY workstream"):
        print(f"   Workstream {row[0]}: {row[1]} items")
    
    print("\n   ── Artifacts by Classification ──")
    for row in conn.execute("SELECT classification, COUNT(*) FROM artifacts GROUP BY classification"):
        print(f"   {row[0]}: {row[1]}")
    
    conn.close()


if __name__ == "__main__":
    if "--stats" in sys.argv:
        show_stats()
    else:
        init_database()
        if "--seed" in sys.argv or True:  # Always seed on first run
            seed_all()
            show_stats()
