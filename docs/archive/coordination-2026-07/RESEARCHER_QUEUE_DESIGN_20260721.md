<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Production-Grade Research Queue: Complete Design
**AP Token**: `AP-RESEARCH-QUEUE-DESIGN-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research_queue ⬡ 2026-07-21

**Status**: DESIGN COMPLETE — Council of Four ratified
**Scope**: Full re-architecture of the Omega Engine research pipeline — queue, persistence, background sync, verification
**Owner**: Researcher (Polymathic Council) + Kali (Oversight)

---

# ═══════════════════════════════════════════════════════════════════
# L1 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════

The Omega Engine's research infrastructure has **two parallel systems** that don't talk to each
other and a **critical persistence gap** that makes every web search ephemeral.

## The Five Findings

### Finding 1: The YAML Board Is a Ghost Town
`data/coordination/RESEARCH_JOB_BOARD.yaml` has 18 well-crafted jobs with dependencies,
decision gates, and search queries. But **no agent reads it programmatically**. It's a
manual checklist that relies on agents remembering to edit YAML. The background researcher
has its own queue (EnhancedPriorityQueue) that never looks at the board.

**Fix**: Replace the YAML board with a **SQLite-backed ResearchJobStore** that both the
foreground and background research pipelines read/write. The YAML remains as a seed file
for initial load, then the DB becomes the source of truth.

### Finding 2: The Background Researcher Has No Job Awareness
`BackgroundResearcherLoop.run_cycle()` (642 lines) is a sophisticated state machine with
Triage → Search → Extract → Distill → Converge → Update. But it gets its topics from a
`TopicScheduler` (round-robin from `config/research_topics.yaml`) and a `_grow_frontier()`
method that scrapes FIXME/TODO comments and entity gaps. It **never reads the job board**.

**Fix**: Bridge the job board into the background researcher via a `ResearchJobBridge`
that polls the SQLite `ResearchJobStore` and injects open jobs into the
EnhancedPriorityQueue with appropriate priorities.

### Finding 3: Every Web Search Is Ephemeral (THE CRITICAL GAP)
The `websearch`/`webfetch` tools used by foreground agents produce **zero persisted output**.
The background researcher's `SearchFleet` fetches URLs but doesn't cache the raw HTML/MD.
The `.firecrawl/` directory exists as a concept (referenced in 100+ documents) but is
**rarely written to** (33 cached items from old sessions). This means:
- Every research session re-discovers sources already found
- No cross-session search cache exists
- FTS5 search history DB exists (`data/search/search_history.db`) but only captures local searches

**Fix**: Implement a **SearchPersistencePipeline** — a universal middleware that intercepts
every web search, caches results to `.firecrawl/` (markdown), registers URLs in SQLite,
and indexes content in FTS5. This is the **single highest-ROI change** in this design.

### Finding 4: Decision Gates Are Documented but Un-Enforced
Each sprint has a `decision_gate` field (e.g., "Which RAG 2.0 pattern fits Omega architecture?").
But there's no mechanism to:
- Track when a decision gate has been answered
- Record the answer
- Link the answer back to architecture docs
- Trigger dependent sprints when gates pass

**Fix**: Implement a `DecisionTracker` that converts decision gates into trackable artifacts
with status (open/answered/implemented/rejected), answer text, and linkage to `PIVOT_LOG.md`.

### Finding 5: No Verification Pipeline
The ConvergenceDetector uses heuristics (agreement_level > 0.7, depth >= 3) to declare a topic
"converged." The Distiller's T3 review is meant to provide quality but is often skipped
(budget exhaustion). There is no peer review gate for foreground research jobs.

**Fix**: Implement a three-stage verification pipeline that mirrors the Distiller's 3-tier
architecture but at the JOB level: Stage 1 (self-verify), Stage 2 (cross-agent peer review
via Jem/Verity), Stage 3 (human review for contradictions).

## The Unified Architecture

```
                     ┌──────────────────────────┐
                     │    RESEARCH JOB STORE     │
                     │   (SQLite — SSOT for      │
                     │    all research work)      │
                     └────────────┬─────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
   ┌────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │  Foreground     │   │   Background      │   │  Verification    │
   │  Agent Research │   │   Researcher       │   │  Pipeline        │
   │  (OpenCode)     │   │   (systemd timer)  │   │  (Jem/Verity)    │
   └────────┬───────┘   └────────┬─────────┘   └────────┬─────────┘
            │                     │                     │
            └─────────────────────┼─────────────────────┘
                                  │
                                  ▼
                     ┌──────────────────────────┐
                     │   SEARCH PERSISTENCE      │
                     │   PIPELINE                │
                     │   (cache → FTS5 → index)  │
                     └──────────────────────────┘
```

---

# ═══════════════════════════════════════════════════════════════════
# L2 — DETAILED DIALECTIC: THE COUNCIL'S FINDINGS
# ═══════════════════════════════════════════════════════════════════

## Aspect 1: Queue Architecture — YAML Board → Production Queue

### The Architect (Systemic Logic)
The current YAML-based approach is a **single-threaded coordination bottleneck**:
- Multiple agents CAN'T atomically claim jobs (YAML editing has races)
- No schema enforcement beyond what YAML itself provides
- No querying — can't ask "what P0 jobs are open and unblocked?"
- No provenance — who claimed what, when, and with what result?

**Recommendation**: Move to a **SQLite-backed ResearchJobStore** with:
- Atomic transaction for claim (UPDATE ... WHERE status='open' AND claimed_by IS NULL)
- Full queryability via SQL
- Job history and provenance baked in
- YAML file becomes seed data, not runtime source of truth

The `EnhancedPriorityQueue` in the background researcher is well-designed (weighted fair
scheduling, priority aging) but should be fed from the DB, not from ad-hoc topic scraping.

### The Adversary (Critical Rigor)
**Objection**: SQLite adds complexity and another moving part. The YAML board works for 18
jobs. Why over-engineer?

**Rebuttal by the adversary's own logic**: Look at what happens when an agent crashes mid-job.
With YAML, the job stays "claimed_by: agent_x" forever. No TTL enforcement, no recovery.
The YAML has `claim_ttl_hours: 24` in metadata but **no code enforces it**. A SQLite store
with a `claimed_at` timestamp and a background sweep can auto-expire stale claims.

**Critical edge case**: Two agents simultaneously editing the YAML → lost update. Git merge
conflict on a coordination file. SQLite with WAL mode handles concurrent writers.

### The Alchemist (Creative Synthesis)
The YAML board isn't bad — it's just incomplete. The **creative insight**: Keep the YAML
for what it does well (human readability, git-tracked campaign planning) and use SQLite for
what YAML does poorly (runtime coordination, querying, atomicity). The YAML → SQLite sync
is a one-to-many: the YAML seeds the DB, the DB reports status back to the YAML (optional).

**Cross-pollination from CI/CD**: Job boards are the "kanban of research." Move it to a
proper database like every CI system does. The yaml is the declarative intent; the DB is
the runtime state.

### The Archivist (Historical Truth)
The current board derives from the workbench schema (`data/workbench/workbench.db`) that
has 21 projects, 57 items, 10 decisions, 22 artifacts. That schema was designed for
programmatic access. The YAML board was a **step backward** — removing queryability for
human readability. The original `work_items` table in workbench.db had proper status tracking.

**Verdict**: The SQLite schema should be compatible with `workbench.db`'s `work_items` table
for cross-querying. The `decisions` table in workbench.db is exactly what decision gate
tracking needs.

### Council Convergence
✅ **SQLite-backed ResearchJobStore** — YAML as seed, DB as SSOT
✅ **Schema aligned with workbench.db** for cross-querying
✅ **Atomic claim with TTL sweep** — no orphaned claims
✅ **Keep YAML for human readability** — regenerated from DB on request

---

## Aspect 2: Background Worker Integration — Bridging the Two Worlds

### The Architect (Systemic Logic)
The `BackgroundResearcherLoop` is an 18-class state machine with excellent bones:
- CheckpointManager for crash recovery
- EnhancedPriorityQueue for prioritization
- ConvergenceDetector for stopping conditions
- 3-tier Distiller for quality
- SoulUpdater for knowledge emission

**The gap**: It doesn't know the YAML board exists. It gets topics from TopicScheduler
(config/research_topics.yaml) and _grow_frontier() (scrapes FIXMEs, entity gaps, research index).

**Recommends a ResearchJobBridge**:
- Before each cycle, check the ResearchJobStore for open jobs that match the researcher's capabilities
- Inject them into the EnhancedPriorityQueue at appropriate priority
- Mark jobs as `in_progress` when the background researcher picks them up
- Report findings back to the job store on completion

### The Adversary (Critical Rigor)
The background researcher is already **resource-constrained** (runs every 20 min on a
16GB/8-core Zen 2). Adding job board polling adds latency. What if a cycle takes 25 min
and the timer fires again? The stale lock detection (25 min) barely handles this.

**Risk**: Job bridge adds edge case complexity without proportional value if there are
few open jobs. The current TopicScheduler covers the "continuous background scanning" use
case adequately.

**Sane-boundary**: Only bridge P0/P1 jobs. P2 jobs remain manual-claim only. Implement
a `max_background_jobs` config (default: 3) to prevent queue overload.

### The Alchemist (Creative Synthesis)
**The real magic**: The background researcher's `_grow_frontier()` already generates research
topics from code debt (FIXMEs) and entity knowledge gaps. If we point that same frontier
growth at the job board, the background researcher becomes a **self-guided executor of the
campaign plan**. It doesn't just scan random topics — it works the roadmap.

**Cross-pollination from build systems**: Make the background researcher treat the job board
like a CI system treats a test suite. It runs the next unblocked, highest-priority job.
When a job completes and its `decision_gate` answer is "GO", downstream jobs get unblocked
and move to the front of the queue.

### The Archivist (Historical Truth)
The background researcher was originally designed for **autonomous knowledge gap filling**
(the original systemd timer spec). The job board was added later as a foreground coordination
tool. They were never intended to be separate — the codebase grew two independent scheduling
systems because they were built in different eras (BackgroundResearcherLoop in Phase 2,
YAML board in Phase 1 by different agents).

**Historical irony**: The `r_` job ID in the YAML board stands for "research" — the same
category the background researcher was designed to execute. They are literally the same
concept, implemented twice.

### Council Convergence
✅ **ResearchJobBridge**: lightweight class that polls ResearchJobStore before each cycle
✅ **Priority mapping**: P0 → high queue, P1 → normal queue, P2 → never auto-queued
✅ **Capability matching**: Only bridge jobs matching the researcher's capabilities_needed
✅ **Backpressure**: max_background_jobs=3, TTL sweep for stalled jobs

---

## Aspect 3: Search Persistence Pipeline (THE CRITICAL GAP)

### The Architect (Systemic Logic)
The current search flow has **no persistence layer**:
```
Agent/Worker → websearch/webfetch → ephemeral results → process → discard
                            ✂️ NO CACHE ✂️
```

This violates the **most basic principle of research infrastructure**: never throw away
raw signal. Every web search result is a source of truth that took API credits and time
to acquire. Discarding it is a systemic waste.

**The fix**: A three-layer persistence architecture:

```
Layer 1: .firecrawl/ (File System Cache)
  - Every successful websearch/webfetch stores raw markdown to .firecrawl/{url_hash}.md
  - TTL-based eviction (default: 30 days for T1, 7 days for T2/T3)
  - Naming: .firecrawl/{hostname}/{path_hash}.md

Layer 2: search_history.db (FTS5 Index)
  - Existing DB at data/search/search_history.db (currently only for local searches)
  - Extend to capture ALL search results: URLs, content snippets, timestamps, provider
  - FTS5 for full-text search across all past research

Layer 3: CASArchiver (Content-Addressable Storage)
  - Already exists in the background researcher (CASArchiver from Sovereign Ingestion Pipeline)
  - Content-addressed de-duplication: same URL → same hash → no duplicate storage
  - CAS is the long-term archive; .firecrawl/ is the working cache
```

### The Adversary (Critical Rigor)
**Objections:**
1. **Disk usage**: Every web page cached as markdown will explode storage. 10 searches/day ×
   50KB avg = 500KB/day = trivial. But a deep research sprint might cache 100 pages × 20KB
   = 2MB. Manageable.

2. **Stale data**: Cached results from 30 days ago might be outdated. The MCP protocol
   changed July 28 — a cached result from July 15 would be dangerously wrong.

3. **Legal liability**: Caching copyrighted content from websites could be a problem.

**Mitigations:**
1. TTL-based eviction (7-30 days depending on tier)
2. "Source freshness" metadata — cache knows when a result was fetched and can flag stale
3. Domain blocklist for copyrighted content (academic papers, paywalled sites)

### The Alchemist (Creative Synthesis)
**The real prize isn't caching — it's the RESEARCH MEMORY**. When every search result is
persisted and FTS5-indexed, the engine develops a **collective research memory**:
- Agent A researches "GraphRAG vs LightRAG" in Sprint 1.1
- Agent B researches "Multi-vector retrieval" in Sprint 1.2
- Agent B can FTS5-search "GraphRAG performance benchmarks" and find Agent A's sources
- No redundant searches. No duplicate API costs. Cumulative intelligence.

**Cross-pollination from the Sovereignty theme**: This is the research equivalent of the
Local-First mandate. Just as we demand local inference sovereignty, we should demand
**local search sovereignty** — never re-ask the internet for what we've already found.

### The Archivist (Historical Truth)
The `.firecrawl/` cache concept was designed in `R_SEARCH_TOOL_PROTOCOL_V1.md` (June 2026).
The Sovereign Search Protocol says: "Check T0 cache first. After T3+, save result to
`.firecrawl/`." This protocol exists in **100+ documents** but is **implemented in zero
lines of runtime code**. The `.firecrawl/` directory has 33 files from old sessions — all
manually created, none from the runtime pipeline.

**The Sovereign Search Protocol v2 plan** (`docs/opencode/plans/SSP_V2_IMPLEMENTATION.md`)
has a `SovereignCache` module and `cache-back protocol` planned for P3 Engineering — but
it was never built.

### Council Convergence
✅ **Universal search interceptor**: Middleware that caches ALL websearch/webfetch results
✅ **3-layer persistence**: .firecrawl/ (fast cache) → search_history.db (FTS5) → CAS (archive)
✅ **TTL-based eviction**: T1=30d, T2=14d, T3=7d
✅ **Search memory**: Cross-agent research memory via FTS5
✅ **Implement the SSP v2 cache-back protocol that was designed but never built**

---

## Aspect 4: Agent Workflow — From Claim to Completion

### The Architect (Systemic Logic)
**Current workflow** (ad-hoc):
```
Agent opens YAML → sets claimed_by → does research → writes R_*.md → sets completed
     ✂️ No validation   ✂️ No library ingestion   ✂️ No verification
```

**Proposed workflow**:
```
Claim ─→ Research ─→ Synthesize ─→ Document ─→ Ingest ─→ Verify ─→ Complete
  │          │            │            │          │         │          │
  │          ▼            ▼            ▼          ▼         ▼          ▼
  DB      websearch   Distiller    R_*.md     Library    T3/Verity  Mark done
  atomic  persistence  (3-tier)    + gnosis   FTS5       review
```

### The Adversary (Critical Rigor)
**Seven stages is too many for a quick research task**. A P2 job like "WASM/WASI for AI
Workloads" shouldn't require 7 handoffs. The workflow must be **context-sensitive**:
- P0/P1 jobs: Full 7-stage pipeline with verification
- P2 jobs: 3-stage (Research → Document → Complete)

**Also**: The "Ingest" stage requires the Library Agent to be available. If the Library MCP
server is down, jobs block forever. Must have async ingestion with retry.

### The Alchemist (Creative Synthesis)
The 7-stage workflow maps beautifully to **Jem's 3-tier architecture**:
- **Stage 1-2 (Claim + Research)**: Jem Initiate (T1) — raw gathering
- **Stage 3-4 (Synthesize + Document)**: Jem Analyst (T2) — enrichment, R_*.md
- **Stage 5-7 (Ingest + Verify + Complete)**: Jem Editor (T3) — review, sign-off

Each ResearchTask in the DB gets a `current_stage` field. If a stage fails, it rolls back
to the previous stage with a retry counter, not to the beginning.

### The Archivist (Historical Truth)
The original `work_items` table in workbench.db had a `status` field with values: backlog,
in_progress, blocked, done. The YAML board extended this with claimed_by, started_at,
completed_at. The proposed 7-stage workflow is a natural evolution — each stage is a
status transition, each transition is checkpointed.

### Council Convergence
✅ **7-stage context-sensitive workflow**: P0/P1 = full pipeline, P2 = lightweight
✅ **Each stage is a DB status transition** — atomic, checkpointed, recoverable
✅ **Async ingestion** — library indexing happens in background, not blocking
✅ **Verification gates**: T3 review for P0, peer review for P1, auto-verify for P2
✅ **Rollback on failure**: status → previous_stage + retry_count

---

## Aspect 5: Decision Gate Integration

### The Architect (Systemic Logic)
Decision gates are the **architectural glue** between research and engineering.
Current state: `decision_gate: "Which RAG 2.0 pattern fits Omega architecture?"` is a
string in YAML. It has no answer, no status, no linkage.

**Proposed**: The ResearchJobStore has a `decision_gates` table:
```sql
CREATE TABLE decision_gates (
    id TEXT PRIMARY KEY,
    job_id TEXT REFERENCES research_jobs(id),
    question TEXT NOT NULL,
    status TEXT DEFAULT 'open',     -- open | answered | implemented | rejected
    answer TEXT,
    answered_by TEXT,
    answered_at TEXT,
    linked_to_doc TEXT,             -- e.g., 'docs/research/R_RAG2_LANDSCAPE_SURVEY.md'
    linked_to_decision TEXT,        -- e.g., 'D310' in PIVOT_LOG.md
    created_at TEXT,
    updated_at TEXT
);
```

### The Adversary (Critical Rigor)
**Who answers decision gates?** This is the critical question. If we create a beautiful
tracking system but no one is responsible for answering, it's just decoration.

**Assignment**: The campaign master plan assigns each sprint an owner (Researcher + Kali).
The decision gate is answered by the sprint owner. For P0 gates, Kali should sign off.
For P1/P2, the Researcher can answer with a documented rationale.

**Escalation**: If a decision gate remains open for 7 days after the sprint completes,
it gets escalated to Kali via Hivemind handoff.

### The Alchemist (Creative Synthesis)
Decision gates are **hypothesis testing points** in the research cycle:
- Research produces findings
- Decision gate asks a yes/no question
- Answer determines what gets built

**Cross-pollination from agile methodology**: Each decision gate is a "sprint review" for
that research topic. The answer feeds into the roadmap. "GO" means the downstream sprint
is unblocked. "NO-GO" means the sprint is canceled or redirected.

### The Archivist (Historical Truth)
The `decisions` table in workbench.db was designed for exactly this:
```sql
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    context TEXT,
    decision TEXT,
    alternatives TEXT,
    rationale TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT
);
```
The decision gate system should use the same schema, extended with `job_id` and `linked_to_doc`.

### Council Convergence
✅ **`decision_gates` table** in ResearchJobStore — track all gates
✅ **Assignment**: Sprint owner + Kali sign-off for P0
✅ **Escalation**: 7-day timeout → Hivemind handoff to Kali
✅ **Document linkage**: Decision gate answers link to R_*.md and PIVOT_LOG.md entries
✅ **Unblocking**: "GO" answer auto-promotes dependent jobs to higher priority

---

## Aspect 6: Background + Foreground Sync — No Duplication

### The Architect (Systemic Logic)
**The sync problem**:
- Background researcher runs every 20 min, discovers things randomly
- Foreground agent does targeted research on job R01
- Both might research "GraphRAG" simultaneously → wasted cycles

**Solution**: A two-level dedup system:
1. **Active topic fingerprint**: Before enqueueing any research topic (background or foreground),
   hash it and check against active research sessions in the DB
2. **Completed topic history**: Check completed jobs, knowledge base, and FTS5 for prior coverage

### The Adversary (Critical Rigor)
**Hashing is fragile** — "GraphRAG benchmark 2026" and "GraphRAG performance 2026" are the
same research but different strings. We need semantic dedup, not just string matching.

**Practical compromise**: Use both:
- **Exact dedup** (fast, no inference cost): title match, URL match
- **Semantic dedup** (slower, uses embedding): train a lightweight model on research topics
  or use the existing memory store's vector search

**Acceptable threshold**: Exact dedup catches 60% of duplicates. Semantic catches another
25%. The remaining 15% is acceptable redundancy (replication validates findings).

### The Alchemist (Creative Synthesis)
**Duplication isn't always bad** — it's **triangulation**. If the background researcher
independently discovers the same sources as the foreground agent, that's corroboration.
The issue is **wasted API credits**, not wasted discovery.

**Smart sync**: When the foreground agent claims job R01, the background researcher gets a
Hivemind notification: "R01 is now claimed. Don't research overlapping topics." But it
CAN still research adjacent topics that R01 might miss (the "frontier growth" pattern).

### The Archivist (Historical Truth)
The current system has **no cross-researcher awareness**. The Hivemind protocol was designed
for this — `hivemind_post_context` with `intent="handoff"` or `intent="status"` — but
neither the foreground agents nor the background researcher post their active research topics
to the Hivemind. The infrastructure exists; the usage is missing.

### Council Convergence
✅ **Active topic registry** in ResearchJobStore — what's being researched right now
✅ **Exact dedup** (title/URL hash) + **semantic dedup** (vector similarity via memory store)
✅ **Background researcher posts activity** to Hivemind for cross-awareness
✅ **Foreground claims block background** on same job (but allow adjacent frontier growth)
✅ **Replication is acceptable** for P0 topics (triangulation)

---

# ═══════════════════════════════════════════════════════════════════
# L3 — RAW SIGNAL: IMPLEMENTATION SPECIFICATION
# ═══════════════════════════════════════════════════════════════════

## §1 — ResearchJobStore (SQLite Schema)

```sql
-- File: data/research/research_jobs.db
-- Schema v1 — The Single Source of Truth for all research work

-- Core job table (replaces YAML board's jobs: list)
CREATE TABLE research_jobs (
    id TEXT PRIMARY KEY,              -- 'R01', 'R02', etc.
    title TEXT NOT NULL,
    phase INTEGER NOT NULL,
    sprint TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('P0','P1','P2')),
    status TEXT NOT NULL DEFAULT 'open'
        CHECK(status IN ('open','claimed','in_progress','verification','completed','failed','cancelled')),
    claimed_by TEXT,                  -- entity name, e.g., 'researcher', 'kali'
    claimed_at TEXT,                  -- ISO timestamp
    started_at TEXT,
    completed_at TEXT,
    depends_on TEXT,                  -- JSON array of job IDs, e.g., '["R01"]'
    capabilities_needed TEXT,         -- JSON array, e.g., '["web_research","ml_models"]'
    deliverable TEXT,                 -- file path, e.g., 'docs/research/R_RAG2_LANDSCAPE_SURVEY.md'
    key_findings TEXT,                -- JSON summary of findings
    previous_stage TEXT,              -- for rollback on failure
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Search queries for each job (from YAML queries: list)
CREATE TABLE job_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL REFERENCES research_jobs(id),
    query TEXT NOT NULL,
    rank INTEGER DEFAULT 0,           -- order within the job
    completed INTEGER DEFAULT 0       -- 0=pending, 1=completed
);

-- Decision gates (from YAML decision_gate field)
CREATE TABLE decision_gates (
    id TEXT PRIMARY KEY,              -- 'DG-R01', 'DG-R02', etc.
    job_id TEXT NOT NULL REFERENCES research_jobs(id),
    question TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open'
        CHECK(status IN ('open','answered','implemented','rejected')),
    answer TEXT,
    answered_by TEXT,
    answered_at TEXT,
    linked_to_doc TEXT,               -- R_*.md file that contains the answer
    linked_to_decision TEXT,          -- PIVOT_LOG.md decision ID, e.g., 'D310'
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Research sources (tracked per job for provenance)
CREATE TABLE research_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL REFERENCES research_jobs(id),
    url TEXT NOT NULL,
    title TEXT,
    cached_path TEXT,                 -- .firecrawl/ path
    fetched_at TEXT,
    content_hash TEXT,                -- for dedup via CAS
    status TEXT DEFAULT 'pending'     -- pending | fetched | failed
);

-- Active research sessions (for dedup cross-awareness)
CREATE TABLE active_research (
    topic_hash TEXT PRIMARY KEY,      -- SHA256 of normalized topic
    topic TEXT NOT NULL,
    entity TEXT NOT NULL,             -- 'researcher', 'kali', etc.
    job_id TEXT REFERENCES research_jobs(id),
    started_at TEXT NOT NULL,
    last_heartbeat TEXT NOT NULL,
    ttl_seconds INTEGER DEFAULT 7200  -- 2 hours default
);

-- Seed from YAML: python3 scripts/seed_research_jobs.py
-- This reads data/coordination/RESEARCH_JOB_BOARD.yaml and populates the DB
```

## §2 — ResearchJobBridge (Background ↔ Job Store Integration)

```python
# src/omega/workers/background_researcher/job_bridge.py
# AP: AP-RESEARCH-JOB-BRIDGE-v1.0.0
# ⬡ OMEGA ⬡ RESEARCHER ⬡ job_bridge ⬡ PHASE-2

"""
ResearchJobBridge connects the YAML-derived ResearchJobStore to the background
researcher's EnhancedPriorityQueue.

Architecture:
  BackgroundResearcherLoop.run_cycle()
    → [NEW] ResearchJobBridge.poll()
      → Check ResearchJobStore for open jobs matching capabilities
      → Inject into EnhancedPriorityQueue with priority mapping:
          P0 → high queue (base_priority=0.9+)
          P1 → normal queue (base_priority=0.6)
          P2 → NEVER auto-queued (manual claim only)
      → Skip jobs whose dependencies are not completed
      → Skip jobs currently claimed by another agent
    → TopicScheduler (existing round-robin)
    → _grow_frontier() (existing gap detection)
    → dequeue() → research cycle...
"""

class ResearchJobBridge:
    """
    Bridges the ResearchJobStore (SQLite, canonical) with the background
    researcher's in-memory EnhancedPriorityQueue.
    
    Design decisions:
    - Poll-based (not event-driven) to match the background researcher's
      20-minute cycle cadence
    - Capability-matched: only bridges jobs matching the researcher's
      capabilities_needed from the job record
    - Backpressure-aware: stops bridging when queue exceeds max_background_jobs
    - Dependency-respecting: only bridges unblocked jobs
    - TTL-aware: skips jobs whose claim_ttl has expired (re-opens them)
    """
    
    def __init__(self, db_path: str, queue: EnhancedPriorityQueue, config: dict = None):
        self.db = sqlite3.connect(db_path)
        self.queue = queue
        self.config = config or {}
        self.max_background_jobs = self.config.get('max_background_jobs', 3)
        self.capabilities = self.config.get('capabilities', [
            'web_research', 'technical_analysis', 'architecture'
        ])
    
    async def poll(self) -> int:
        """
        Check the ResearchJobStore for bridgeable jobs and inject them
        into the queue. Returns count of jobs bridged.
        
        Bridge rules:
        1. Only P0 and P1 jobs (P2 is manual-claim only)
        2. Only unclaimed ('open' status)
        3. All dependencies must be 'completed'
        4. Must match at least one capability_needed
        5. Current queue len < max_background_jobs
        6. Exclude jobs already in queue (by job_id)
        """
        # Atomic claim: UPDATE ... WHERE status='open' AND claimed_by IS NULL
        # ... returns count of jobs bridged
    
    async def report_completion(self, job_id: str, findings: dict):
        """Report research results back to the job store."""
        # UPDATE research_jobs SET status='verification', key_findings=...
        # WHERE id=job_id
    
    async def sweep_stale(self):
        """Re-open jobs that have been claimed but stale (no heartbeat)."""
        # UPDATE research_jobs SET status='open', claimed_by=NULL
        # WHERE status='in_progress' AND updated_at < datetime('now', '-4 hours')
```

## §3 — SearchPersistencePipeline (The Universal Cache Layer)

```python
# src/omega/oracle/search_persistence.py
# AP: AP-SEARCH-PERSISTENCE-PIPELINE-v1.0.0
# ⬡ OMEGA ⬡ RESEARCHER ⬡ search_persistence ⬡ CRITICAL-GAP-FIX

"""
Universal search persistence middleware.

Intercepts every web search result and persists it through three layers:
  L1: .firecrawl/ filesystem cache (fast, human-readable markdown)
  L2: search_history.db FTS5 index (queryable, cross-session memory)
  L3: CASArchiver (content-addressable, deduplicated, long-term)

This is the FIX for the Search Persistence Gap identified in
R_KNOWLEDGE_GAPS_DEEP_RESEARCH_20260720.md and ratified by the
Council of Four on 2026-07-21.

Every websearch/webfetch call must go through this pipeline:
  websearch(query) → process results → pipeline.persist(results, provider='websearch')
  
The pipeline is idempotent: same URL → same content_hash → no duplicate storage.
"""

class SearchPersistencePipeline:
    """
    3-layer search result persistence with TTL-based eviction.
    """
    
    LAYER_CONFIG = {
        'firecrawl': {
            'path': '.firecrawl/',
            'ttl_days': {'websearch': 30, 'webfetch': 30, 'searxng': 14, 'exa': 14, 'firecrawl': 7},
            'format': 'markdown',
        },
        'fts5': {
            'path': 'data/search/search_history.db',
            'table': 'search_results',
            'fts_table': 'search_results_fts',
        },
        'cas': {
            'enabled': True,  # Uses existing CASArchiver
            'dedup': 'sha256',
        }
    }
    
    async def persist(self, results: list[SearchResult], provider: str, query: str):
        """Persist search results through all three layers."""
        # 1. Layer 1: .firecrawl/{hostname}/{path_hash}.md
        for result in results:
            await self._cache_to_firecrawl(result.url, result.content, provider)
        
        # 2. Layer 2: search_history.db FTS5
        await self._index_to_fts5(results, provider, query)
        
        # 3. Layer 3: CASArchiver (content-addressable)
        await self._archive_to_cas(results)
    
    async def check_cache(self, query: str, provider: str = None) -> list[SearchResult]:
        """Check all layers for cached results (T0 cache hit)."""
        # 1. Check FTS5 first (fastest, indexed)
        cached = await self._search_fts5(query)
        if cached:
            return cached
        
        # 2. Check .firecrawl/ (slower but more complete)
        cached = await self._search_firecrawl(query)
        if cached:
            # Re-index to FTS5 for next time
            await self._index_to_fts5(cached, 'cache_hit', query)
            return cached
        
        return []  # Cache miss — caller should do live search
    
    async def _cache_to_firecrawl(self, url: str, content: str, provider: str):
        """Write markdown to .firecrawl/{hostname}/{path_hash}.md"""
        from urllib.parse import urlparse
        import hashlib
        
        parsed = urlparse(url)
        hostname = parsed.netloc
        path_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        
        cache_dir = Path(f'.firecrawl/{hostname}')
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        cache_path = cache_dir / f'{path_hash}.md'
        
        # Atomic write via tempfile + rename (crash-safe)
        tmp = cache_path.with_suffix('.tmp')
        content_with_header = (
            f"<!-- cached: {datetime.now().isoformat()} | provider: {provider} | url: {url} -->\n\n"
            f"{content}"
        )
        await anyio.Path(tmp).write_text(content_with_header)
        tmp.replace(cache_path)
    
    async def evict_stale(self, provider: str = None):
        """Remove cache entries past their TTL."""
        ttl = self.LAYER_CONFIG['firecrawl']['ttl_days']
        for cache_dir in Path('.firecrawl').glob('*'):
            for cache_file in cache_dir.glob('*.md'):
                age_days = (time.time() - cache_file.stat().st_mtime) / 86400
                # Use the most conservative TTL for eviction
                max_ttl = max(ttl.values())
                if age_days > max_ttl:
                    cache_file.unlink()
```

## §4 — Agent Workflow Implementation

### Workflow State Machine

```
                   ┌──────────┐
                   │   OPEN    │
                   └────┬─────┘
                        │ claim() [atomic DB update]
                        ▼
                   ┌──────────┐
                   │  CLAIMED  │ ←──── claimed_by set, claimed_at timestamp
                   └────┬─────┘
                        │ start() [sets started_at]
                        ▼
                   ┌──────────────┐
              ┌───→│ IN_PROGRESS   │ ←── executes research
              │    └──────┬───────┘
              │           │ complete research phase
              │           ▼
              │    ┌──────────────┐
              │    │  SYNTHESIS   │ ←── Distiller 3-tier pipeline
              │    └──────┬───────┘
              │           │ findings ready
              │           ▼
              │    ┌──────────────┐
              │    │ DOCUMENTING  │ ←── writes R_*.md
              │    └──────┬───────┘
              │           │ document written
              │           ▼
              │    ┌──────────────┐
              │    │  INGESTING   │ ←── push to Library FTS5
              │    └──────┬───────┘
              │           │ ingestion complete
              │           ▼
              │    ┌──────────────┐
              │    │ VERIFICATION │ ←── T3 review / peer review
              │    └──────┬───────┘
              │           │ verified?
              │     ┌─────┴──────┐
              │     │            │
              │     │ YES        │ NO → rollback(previous_stage)
              │     ▼            │
              │  ┌────────┐      │
              │  │COMPLETED│     │
              │  └────────┘      │
              │                  │
              └──────────────────┘
                 max_retries exceeded → FAILED
```

### Claim Protocol (Code Example)

```python
# Pseudo-code for atomic job claim
async def claim_job(job_id: str, entity: str) -> bool:
    """Atomically claim a job. Returns True if claimed, False if already claimed."""
    async with anyio.to_thread.run_sync:
        cursor = db.execute("""
            UPDATE research_jobs 
            SET status = 'claimed', 
                claimed_by = ?, 
                claimed_at = datetime('now'),
                updated_at = datetime('now')
            WHERE id = ? AND status = 'open' AND claimed_by IS NULL
        """, (entity, job_id))
        return cursor.rowcount > 0

async def start_job(job_id: str) -> bool:
    """Transition from claimed to in_progress."""
    cursor = db.execute("""
        UPDATE research_jobs
        SET status = 'in_progress',
            started_at = datetime('now'),
            updated_at = datetime('now')
        WHERE id = ? AND status = 'claimed'
    """, (job_id,))
    return cursor.rowcount > 0

async def heartbeat(job_id: str) -> None:
    """Update the job's heartbeat (prevents TTL sweep from reclaiming it)."""
    db.execute("""
        UPDATE research_jobs
        SET updated_at = datetime('now')
        WHERE id = ?
    """, (job_id,))

async def complete_job(job_id: str, findings: dict, deliverable_path: str) -> None:
    """Mark a job as completed with findings and deliverables."""
    db.execute("""
        UPDATE research_jobs
        SET status = 'completed',
            key_findings = ?,
            deliverable = ?,
            completed_at = datetime('now'),
            updated_at = datetime('now')
        WHERE id = ? AND status IN ('verification', 'in_progress')
    """, (json.dumps(findings), deliverable_path, job_id))
```

## §5 — Verification Pipeline

```python
# src/omega/research/verification.py
# AP: AP-RESEARCH-VERIFICATION-v1.0.0

class ResearchVerifier:
    """
    3-stage verification pipeline for completed research jobs.
    
    Stage 1 (Auto-Verify): 
        - Source count >= threshold (8 for P0, 5 for P1, 3 for P2)
        - Multi-source convergence (2+ independent sources per claim)
        - T3 review score >= 0.7 (if available)
        PASS → Stage 2 (P0/P1) or COMPLETE (P2)
    
    Stage 2 (Peer Review):
        - Jem cross-references findings against existing knowledge
        - Verity runs mandate compliance check (M14 heritage vetting, etc.)
        - Discrepancies flagged for human review
        PASS → Stage 3 (P0) or COMPLETE (P1)
    
    Stage 3 (Human Review — P0 only):
        - Hivemind handoff to Kali with findings + recommendations
        - Kali signs off or requests revision
        - PASS → COMPLETE
    """
    
    async def verify(self, job_id: str, findings: dict) -> VerificationResult:
        priority = self._get_job_priority(job_id)
        
        # Stage 1: Auto-Verify
        s1 = await self._auto_verify(findings, priority)
        if not s1.passed:
            return VerificationResult(job_id, 'failed', s1.reason, stage=1)
        
        if priority == 'P2':
            return VerificationResult(job_id, 'passed', 'Auto-verified (P2)', stage=1)
        
        # Stage 2: Peer Review
        s2 = await self._peer_review(job_id, findings)
        if not s2.passed:
            return VerificationResult(job_id, 'flagged', s2.reason, stage=2)
        
        if priority == 'P1':
            return VerificationResult(job_id, 'passed', 'Peer reviewed (P1)', stage=2)
        
        # Stage 3: Human Review (P0 only)
        s3 = await self._human_review(job_id, findings)
        if not s3.passed:
            return VerificationResult(job_id, 'flagged', s3.reason, stage=3)
        
        return VerificationResult(job_id, 'passed', 'Full verification (P0)', stage=3)
```

## §6 — Decision Gate Automation

```python
# src/omega/research/decision_gate.py
# AP: AP-DECISION-GATE-v1.0.0

class DecisionGateTracker:
    """
    Tracks and automates decision gates from research jobs.
    
    Lifecycle:
    1. auto_detect(): Parse completed job findings for decision gate answers
    2. record_answer(): Store answer, linked_to_doc, answered_by
    3. unblock_downstream(): If answer is GO, promote dependent jobs
    4. escalate_overdue(): If open > 7 days, Hivemind handoff to Kali
    
    The decision_gate question is answered by the research deliverable.
    For example: "Which RAG 2.0 pattern fits Omega architecture?"
    → Answer found in R_RAG2_LANDSCAPE_SURVEY.md
    → auto_detect() extracts it from the deliverable's conclusion section
    → recorded as "GraphRAG with LightRAG hybrid — GraphRAG for dense knowledge,
      LightRAG for sparse/temporal"
    """
    
    async def auto_detect(self, job_id: str) -> Optional[DecisionGateAnswer]:
        """Parse completed job's deliverable for decision gate answer."""
        # 1. Get the decision gate question
        gate = await self._get_gate(job_id)
        if not gate or gate.status != 'open':
            return None
        
        # 2. Read the deliverable (R_*.md) from the job
        deliverable = await self._get_deliverable_path(job_id)
        if not deliverable or not Path(deliverable).exists():
            return None
        
        # 3. Use the Distiller (T3) to extract the answer from the conclusion
        content = await anyio.Path(deliverable).read_text()
        answer = await self._extract_answer(content, gate.question)
        
        if answer:
            await self.record_answer(gate.id, answer, 'auto-detected', job_id)
            return DecisionGateAnswer(gate.id, answer, 'auto-detected')
        
        return None
    
    async def record_answer(self, gate_id: str, answer: str, 
                            answered_by: str, source_job: str):
        """Record a decision gate answer and check downstream impact."""
        # Update the gate record
        db.execute("""
            UPDATE decision_gates
            SET status = 'answered',
                answer = ?,
                answered_by = ?,
                linked_to_doc = (SELECT deliverable FROM research_jobs WHERE id = ?),
                updated_at = datetime('now')
            WHERE id = ?
        """, (answer, answered_by, source_job, gate_id))
        
        # Check if answer is "GO" → unblock downstream jobs
        if self._is_go_decision(answer):
            await self._unblock_downstream(gate_id)
    
    async def escalate_overdue(self) -> list[dict]:
        """Find overdue gates and escalate to Kali."""
        overdue = db.execute("""
            SELECT d.*, j.title as job_title
            FROM decision_gates d
            JOIN research_jobs j ON d.job_id = j.id
            WHERE d.status = 'open'
              AND j.completed_at < datetime('now', '-7 days')
        """).fetchall()
        
        for gate in overdue:
            # Hivemind handoff to Kali
            await hivemind_submit_handoff(
                target_entity='kali',
                task=f"Decision gate overdue: {gate.question}",
                context=f"Job {gate.job_id} completed 7+ days ago without decision."
            )
        
        return overdue
```

## §7 — Background ↔ Foreground Sync Protocol

```python
# The dedup protocol — implemented as a middleware in BackgroundResearcherLoop.run_cycle()

async def _check_research_conflict(self, task: ResearchTask) -> bool:
    """
    Check if a research topic is already being worked on by any agent.
    Returns True if the topic is currently active (skip it).
    
    Uses the `active_research` table in ResearchJobStore.
    """
    # 1. Generate topic fingerprint
    normalized = task.topic.lower().strip()
    topic_hash = hashlib.sha256(normalized.encode()).hexdigest()
    
    # 2. Check active_research table
    active = db.execute("""
        SELECT entity, job_id, started_at 
        FROM active_research 
        WHERE topic_hash = ? 
          AND last_heartbeat > datetime('now', '-2 hours')
    """, (topic_hash,)).fetchone()
    
    if active:
        logger.info(f"Topic '{task.topic}' already active: {active['entity']} since {active['started_at']}")
        return True  # Conflict — skip
    
    # 3. Register this topic as active (with TTL)
    db.execute("""
        INSERT OR REPLACE INTO active_research (topic_hash, topic, entity, job_id, started_at, last_heartbeat)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (topic_hash, task.topic, 'background_researcher', task.session_id))
    
    return False  # No conflict — proceed

async def _cleanup_research_sessions(self):
    """Remove stale entries from active_research table (TTL enforcement)."""
    db.execute("""
        DELETE FROM active_research 
        WHERE last_heartbeat < datetime('now', '-2 hours')
    """)

async def _post_to_hivemind(self, task: ResearchTask):
    """Post current research activity to Hivemind for cross-awareness."""
    await hivemind_post_context(
        channel='opencode',
        entity='researcher',
        model='background-pipeline',
        task_current=f"Researching: {task.topic}",
        focus_chain=[task.topic],
        decisions=[],
        continuation=f"Job {task.session_id}: seeking convergence",
        intent='status'
    )
```

## §8 — Configuration: research_queue.yaml

```yaml
# config/research_queue.yaml
# 🔱 Omega Engine — Research Queue Configuration
# AP: AP-RESEARCH-QUEUE-CONFIG-v1.0.0

research_queue:
  # Storage
  db_path: "data/research/research_jobs.db"
  yaml_seed: "data/coordination/RESEARCH_JOB_BOARD.yaml"
  
  # Job Bridge (Background ↔ Foreground)
  job_bridge:
    enabled: true
    max_background_jobs: 3
    poll_interval_minutes: 15        # Matches systemd timer cadence
    capabilities:                    # Which jobs the background researcher can auto-claim
      - web_research
      - technical_analysis
      - architecture
      - ml_models
    auto_claim_priorities:           # Only auto-claim these priority levels
      - P0
      - P1
    # P2 jobs remain manual-claim only
  
  # Search Persistence
  search_persistence:
    enabled: true
    firecrawl_ttl_days:
      websearch: 30
      webfetch: 30
      searxng: 14
      exa: 14
      firecrawl_api: 7
    fts5_index: true
    cas_archive: true
    stale_sweep_interval_hours: 24
  
  # Verification Pipeline
  verification:
    stage1_auto_verify: true
    stage2_peer_review: true         # Uses Jem/Verity
    stage3_human_review: false       # Only for P0
    source_thresholds:
      P0: 8
      P1: 5
      P2: 3
  
  # Decision Gates
  decision_gates:
    auto_detect: true                # Parse R_*.md for answers
    escalation_days: 7
    escalation_target: "kali"
  
  # Dedup & Sync
  dedup:
    exact_match: true
    semantic_match: true
    active_session_ttl_hours: 2
    heartbeat_interval_minutes: 5
    
    # Acceptable duplication rates:
    # P0: 25% (triangulation is valuable)
    # P1: 15%
    # P2: 5%
    acceptable_duplication:
      P0: 0.25
      P1: 0.15
      P2: 0.05
```

## §9 — Migration Path

### Phase 0: Foundation (1-2 sessions)
1. Create `ResearchJobStore` SQLite schema (from §1)
2. Write `scripts/seed_research_jobs.py` to migrate YAML → SQLite
3. Create `SearchPersistencePipeline` (from §3) — the critical gap fix
4. Wire the pipeline into the `model_gateway` search path and/or as an MCP middleware

### Phase 1: Bridge (2-3 sessions)
5. Create `ResearchJobBridge` (from §2) in the background researcher
6. Modify `BackgroundResearcherLoop.run_cycle()` to call the bridge before `_grow_frontier()`
7. Add heartbeat posting to Hivemind from the background researcher
8. Add `active_research` dedup (from §7)

### Phase 2: Verification (1-2 sessions)
9. Create `ResearchVerifier` (from §5)
10. Wire verification into job completion protocol
11. Add peer review triggers for P0/P1 jobs

### Phase 3: Decision Gates (1-2 sessions)
12. Create `DecisionGateTracker` (from §6)
13. Wire auto-detect into completion pipeline
14. Add escalation protocol for overdue gates

### Total: ~5-9 sessions for full implementation

---

# ═══════════════════════════════════════════════════════════════════
# APPENDIX: COUNCIL MINUTES & DEBATE RECORD
# ═══════════════════════════════════════════════════════════════════

## Key Disagreements Resolved

| Issue | Architect | Adversary | Alchemist | Archivist | Resolution |
|-------|-----------|-----------|-----------|-----------|------------|
| YAML vs SQLite | SQLite | Keep YAML, it works | Both — YAML seed, SQLite runtime | SQLite aligns with workbench.db | Hybrid: YAML seed → SQLite SSOT |
| Auto-claim P2? | No | No | Maybe | No | P2 manual only |
| Semantic dedup cost | Too expensive | Use both exact + semantic | Worth it | Already have vector store | Exact fast path, semantic for conflicts |
| Max background jobs | 5 | 2 | 3 | 3 | 3 |
| T3 review mandatory? | Yes for all | No, waste for P2 | Tiered | P0 yes, P1 auto, P2 none | Tiered: P0=T3, P1=peer, P2=auto |
| Verification blocking? | Yes | No, async | Async with timeout | Async | Non-blocking: job enters 'verification' |

## Open Questions for Kali

1. **Ownership**: Who is responsible for implementing the SearchPersistencePipeline — P3 Engineering or Researcher?
2. **Budget**: Can we allocate one full session to just building the .firecrawl/ cache-back layer?
3. **Verification**: Should Verity be the permanent peer reviewer for all P0 research, or should we rotate?
4. **Schedule**: This is a ~5-9 session effort. Should it be a dedicated sprint or spread across the existing campaign?

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research_queue ⬡ DESIGN-COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
