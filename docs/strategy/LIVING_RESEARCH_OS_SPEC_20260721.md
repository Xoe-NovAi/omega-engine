# 🔱 Omega Engine — Living Research OS: Architecture & Build Spec
**AP Token**: `AP-LIVING-RESEARCH-OS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ {session_model} ⬡ opencode ⬡ trc_living_research ⬡ SPEC

**Date**: 2026-07-21  
**Status**: LAYER 2 ACTIVE SPEC — **not** strategy SSOT  
**Strategy master**: [`SOVEREIGN_ARK_BLUEPRINT.md`](SOVEREIGN_ARK_BLUEPRINT.md) **v5.1+ §3.2** (Phase D)  
**Owner**: Kali (Sprint Coordinator) + Researcher (Implementation) + P3 Engineering (Build)
**Origin**: User vision — "I want a system that will forever support ongoing research, a perpetually researching and refining, living intelligence"
**Kali ratification**: `data/coordination/KALI_FEEDBACK_STRATEGY_UNIFY_20260721.md` — APPROVE with this banner (amendment 1)

---

## ⚠️ SUPERSESSION BANNER (READ BEFORE ANY IMPLEMENTATION)

> **This document’s body still contains earlier design prose** (SQLite job store, Gap Detector as a service, ~14h full build, start Phase 1 immediately).  
> **Where the body conflicts with the table below or with Ark §3.2, the body is SUPERSEDED.**  
> Implementers and agents MUST follow Ark §3.2 + this banner — **not** §5 SQLite schema, **not** Phase 4 GapDetector service classes.

**Binding amendments** (Ark v5.1 §3.2 · D-357 · D-358 · D-364 · Kali 2026-07-21):

| Spec body says (SUPERSEDED) | **Do this instead (AUTHORITATIVE)** |
|-----------------------------|-------------------------------------|
| SQLite Research Job Store as runtime SSOT (§5, Phase 2) | **DEFERRED** — YAML job board + `fcntl.flock` until >100 jobs or multi-claimer (D-357) |
| Gap Detector as standalone service / 6 scanners (Phase 4) | **DEFERRED** — extend `_grow_frontier()` in `loop.py` only (D-358) |
| Start Phase 1 (content) immediately | **Blocked** until Phase C gate: **C-0** (test honesty) + **C-1′** (SoulStore) |
| Total ~14h including SQLite + service | Near-term Phase D ≈ **9.5h** (D-1…D-4 as in Ark) + **D-T** tests |
| Novelty optional | **Required** for D-4 (random + contradiction); INDEX noise policy required |
| VerificationGate / 7-stage workflow | **DEFERRED** (D-V) — preserved in `RESEARCHER_QUEUE_DESIGN_20260721.md` |

**Still valid in this document:** vision (§0), three broken seams diagnosis, component inventory of existing code, content-cache intent (as D-1 shape).

---



## §0 The Vision

Not a research campaign. Not sprints. Not a job board that gets archived after 8 weeks.

A **perpetual research operating system** — an infrastructure that:

1. **Continuously identifies** what it doesn't know
2. **Researches** those gaps autonomously (background loop + on-demand + fleet)
3. **Persists** all findings permanently (every search, every session, every source)
4. **Distills** findings into permanent knowledge (L1→L2→L3 soul evolution)
5. **Feeds** new knowledge back into its own gap detection
6. **Never stops** improving — a living intelligence that compounds understanding over time

The loop is: **Find → Research → Persist → Distill → Evolve → Find again.**

This document defines the architecture to make it real.

---

## §1 Current State — What Exists, What's Broken, What's Missing

### 1.1 What Already Exists (3,699 Lines of Working Code)

The components are built. The problem is they aren't wired into a closed loop.

| Component | File | Lines | Status | What It Does |
|-----------|------|-------|--------|--------------|
| **BackgroundResearcherLoop** | `src/omega/workers/background_researcher/loop.py` | 642 | ✅ Working | State machine: Triage → Search → Extract → Distill → Converge → Update. Runs every 20 min via systemd timer. |
| **Distiller** | `src/omega/workers/background_researcher/distiller.py` | 1,186 | ✅ Working | 3-tier cognitive pipeline (T1: Qwen3-4B → T2: MiniMax M2.5 → T3: Gemini 2.5 Pro). Circuit breakers per tier. |
| **SoulUpdater** | `src/omega/workers/background_researcher/soul_updater.py` | 236 | ✅ Working | Writes L3 to `soul.yaml`, creates `R_AUTO_*.md` research docs. Entity matching by keyword. |
| **ConvergenceDetector** | `src/omega/workers/background_researcher/convergence.py` | 87 | ✅ Working | 4 stopping conditions: multi-source verification, claim exhaustion, contradiction flagging, depth ceiling. |
| **EnhancedPriorityQueue** | `src/omega/workers/background_researcher/models.py` | 223 | ✅ Working | Weighted fair scheduling (2:1 high:normal). Prevents starvation. |
| **TopicScheduler** | `src/omega/workers/background_researcher/scheduler.py` | 145 | ✅ Working | Round-robin rotation with aging decay and deepening factor. Reads `config/research_topics.yaml`. |
| **SearchPersistence** | `src/omega/search/search_persistence.py` | 607 | ⚠️ Partial | Metadata-only persistence. `persist_search` decorator exists but only stores query/response JSON, not page content. |
| **SearchFleet** | `src/omega/workers/background_researcher/search_fleet.py` | 484 | ✅ Working | Cloud search orchestration with credit budget management. |
| **SoulUtils** | `src/omega/soul_utils.py` | 89 | ✅ Working | Loads soul context from `soul.yaml` + `proposed_lessons.yaml`. |

**Total working code**: ~3,700 lines across 10 files. The infrastructure is real.

### 1.2 What's Broken (Three Broken Seams)

#### Seam 1: Search Results Vanish (CRITICAL)

**Current state**:
- `search_persistence.py` stores metadata: query, tier, tool, latency, status, `results_json`
- `results_json` contains the raw API response (JSON), NOT the cleaned markdown content
- `.firecrawl/` has 33 files — all Claude-related (hf_cli_ref.md, claude_prompts.json), **zero from research**
- `search_history.db` has 38 records — mostly "test query" and "warp proxy pool", **zero real research**
- Every agent session re-discovers sources already found

**What's missing**: A content cache that captures the actual page content (markdown) from `websearch`/`webfetch` into `.firecrawl/{hash}.md` so subsequent sessions can retrieve it without re-fetching.

**Root cause**: The `persist_search` decorator (line 334 of `search_persistence.py`) wraps search tools and stores metadata, but never writes the content to the file cache. The `.firecrawl/` cache only stores Firecrawl (T3) results, not websearch/webfetch (T1/T2) results.

#### Seam 2: Background Researcher Is Orphaned

**Current state**:
- `TopicScheduler` reads from `config/research_topics.yaml` — 6 hardcoded topics (voice latency, llama.cpp optimization, MCP ecosystem, soul metrics, P2P soul exchange, VR mapping)
- `_grow_frontier()` scans `docs/research/INDEX.md` for 🔲/🔄 markers, scrapes FIXME/TODO comments (now disabled per D-kal-163), checks entity knowledge gaps, reads checkpoint recovery
- `EnhancedPriorityQueue` receives topics from scheduler + frontier
- **The YAML job board** (`data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md`) has 18 well-crafted jobs with dependencies, capabilities, timeboxing
- **No code reads the YAML job board programmatically** — it's a manual checklist

**What's missing**: A bridge between the job board and the background researcher's queue. The background researcher should read open P0/P1 jobs from the board and inject them into its `EnhancedPriorityQueue`.

#### Seam 3: Soul Evolution Doesn't Feed Back Into Gap Detection

**Current state**:
- `SoulUpdater` writes L3 principles to `soul.yaml` and creates `R_AUTO_*.md` research docs
- `_grow_frontier()` scans `docs/research/INDEX.md` for 🔲/🔄 markers
- Auto-generated `R_AUTO_*.md` files are **NOT registered in INDEX.md**
- New knowledge doesn't create new research topics

**What's missing**: When `SoulUpdater` creates a research doc, it should also register it in `docs/research/INDEX.md` and optionally propose a follow-up research topic based on `GnosisPacket.recommended_directions`.

### 1.3 What's Missing Entirely (New Components Needed)

| Component | Purpose | Status |
|-----------|---------|--------|
| **Content Cache** | Persist web search page content to `.firecrawl/` for cross-session reuse | ❌ Not built |
| **Job Board Bridge** | Wire YAML/SQLite job board into background researcher queue | ❌ Not built |
| **Gap Detector** | Standalone service that continuously scans for knowledge gaps and proposes new research topics | ❌ Not built (logic exists in `_grow_frontier()`, needs extraction) |
| **Research Job Store** | SQLite-backed runtime coordination (atomic claims, TTL enforcement, status tracking) | ❌ Not built (YAML is manual-only) |
| **Research Verification** | Quality gate for completed research (self-verify → peer review → human review) | ❌ Not built (ConvergenceDetector does topic-level, not quality-level) |

---

## §2 The Architecture — The Living Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GAP DETECTOR (new)                              │
│                                                                     │
│  Scans continuously:                                                │
│  • soul.yaml — missing L3 principles per entity domain              │
│  • docs/research/INDEX.md — items marked 🔲 (not started)           │
│  • entity knowledge/ dirs — empty or sparse                         │
│  • contradiction flags — pending_review.md                          │
│  • human-proposed topics — config/research_topics.yaml              │
│  • auto-research follow-ups — GnosisPacket.recommended_directions   │
│  • job board open items — RESEARCH_PLAN_PHASE1_4_20260813.md unclaimed P0/P1   │
│                                                                     │
│  Output: prioritized list of ResearchTask objects                   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   RESEARCH ENGINE (exists, 3,700 lines)             │
│                                                                     │
│  BackgroundResearcherLoop.run_cycle():                              │
│    1. TopicScheduler.get_next_topic()  ← from Gap Detector          │
│    2. _triage()                        ← heuristic scoring          │
│    3. _search()                        ← SearXNG + cloud fleet      │
│    4. _extract()                       ← Sovereign Pipeline         │
│    5. Distiller.distill()              ← L1→L2→L3 gnosis           │
│    6. ConvergenceDetector.check()      ← "deep enough?"             │
│    7. SoulUpdater.update()             ← writes to soul + docs      │
│    8. _enqueue_adjacent()             ← self-expanding frontier     │
│                                                                     │
│  + On-demand (agent-triggered via enqueue_user_request)             │
│  + Grok fleet (parallel, when ACP bridge is built)                  │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                PERSISTENCE LAYER (partially exists)                  │
│                                                                     │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │ Content Cache    │  │ search_history.db │  │ Research Docs      │  │
│  │ .firecrawl/      │  │ (metadata, EXISTS)│  │ R_AUTO_*.md        │  │
│  │ (NEW — fills gap)│  │                  │  │ (EXISTS)           │  │
│  └─────────────────┘  └──────────────────┘  └────────────────────┘  │
│                                                                     │
│  ┌─────────────────┐  ┌──────────────────┐                          │
│  │ HALL_OF_RECORDS  │  │ Job Board Store  │                          │
│  │ cycle_*.jsonl    │  │ (SQLite, NEW)    │                          │
│  │ (EXISTS)         │  │                  │                          │
│  └─────────────────┘  └──────────────────┘                          │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SOUL ENGINE (exists, 325 lines)                  │
│                                                                     │
│  SoulUpdater:                                                       │
│  • L3 principles → soul.yaml (per entity)                           │
│  • L1+L2 findings → R_AUTO_*.md research docs                      │
│  • Soul edit history → SoulEditHistory audit trail                   │
│  • Cross-pollination → entity knowledge/ directories                │
│                                                                     │
│  SoulUtils:                                                         │
│  • Loads soul context for oracle injection                          │
│  • Reads proposed_lessons.yaml (blind staging)                      │
│                                                                     │
│  ConvergenceDetector:                                               │
│  • Flags contradictions for human review → pending_review.md        │
│  • Multi-source verification (3+ agreeing sources)                  │
│  • Depth ceiling (depth >= 3 + verification >= 1)                   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
                     (back to GAP DETECTOR)
```

The loop is closed. Every finding creates new gaps. Every gap triggers new research. The intelligence compounds.

---

## §3 Build Spec — Four Phases

### Phase 1: Content Persistence (The Missing Seam)

⚠️ **SUPERSESSION BANNER**: This phase is **ACTIVE** per Ark v5.1 §3.2 (D-1). Implement as specified. The schema additions and content cache logic are authoritative.

**Goal**: Every web search from every agent permanently captures page content.

**File to modify**: `src/omega/search/search_persistence.py`

**Change**: Enhance `SearchPersistence.wrap_search()` to also write page content to `.firecrawl/` as markdown.

**Current code** (line 232-316):
```python
def wrap_search(self, tool_name, tier, query, results, latency_ms, status, ...):
    # Stores metadata in SQLite — but page content is lost
    record = SearchRecord(...)
    self.db.insert(record)
    return search_id
```

**New behavior**:
```python
def wrap_search(self, tool_name, tier, query, results, latency_ms, status, ...):
    # 1. Store metadata in SQLite (existing)
    record = SearchRecord(...)
    self.db.insert(record)

    # 2. NEW: Extract and cache page content
    content = self._extract_content(results, tool_name)
    if content:
        cache_path = self._cache_content(query, content, tool_name, tier)
        # 3. NEW: Update record with cache path
        self.db.update_cache_path(record.search_id, str(cache_path))

    return search_id
```

**New methods to add**:
```python
def _extract_content(self, results: Any, tool_name: str) -> Optional[str]:
    """Extract readable markdown from search results."""
    # websearch returns: {"results": [{"title": ..., "url": ..., "content": ...}]}
    # webfetch returns: markdown string
    # searxng returns: {"results": [{"title": ..., "url": ..., "content": ...}]}
    # Parse each format, extract text content, join with separators

def _cache_content(self, query: str, content: str, tool_name: str, tier: int) -> Path:
    """Write content to .firecrawl/ with deterministic filename."""
    import hashlib
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    cache_dir = Path(".firecrawl")
    cache_dir.mkdir(exist_ok=True)
    cache_path = cache_dir / f"{content_hash}.md"
    cache_path.write_text(content)
    # Also write a sidecar JSON with metadata
    meta_path = cache_dir / f"{content_hash}.meta.json"
    meta_path.write_text(json.dumps({
        "query": query, "tool": tool_name, "tier": tier,
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "content_hash": content_hash,
    }))
    return cache_path
```

**Schema addition** to `search_results` table:
```sql
ALTER TABLE search_results ADD COLUMN cache_path TEXT;
ALTER TABLE search_results ADD COLUMN content_hash TEXT;
CREATE INDEX IF NOT EXISTS idx_search_cache ON search_results(cache_path);
```

**New query method**:
```python
@classmethod
def get_cached_content(cls, query: str) -> Optional[str]:
    """Retrieve cached content for a previously-searched query."""
    # FTS5 search on query, return cache_path content

@classmethod
def search_cache(cls, keyword: str) -> List[Dict]:
    """Search cached content by keyword (FTS5)."""
```

**⚠️ Heads-up**: Deterministic hash means two different queries returning identical content (e.g., fetching the same URL twice) will overwrite the previous sidecar metadata. Not a cache integrity failure — just metadata for one query replaces another. Acceptable for v1. Future enhancement: content-addressed dedup with multiple metadata entries.

**Effort**: ~3 hours
**Impact**: Every future search is permanently retrievable. The single highest-ROI change.
**Verification**: After implementation, run a websearch, check `.firecrawl/` for the cached file, verify `search_history.db` has `cache_path` populated.

---

### Phase 1.5: NotebookLM Ingestion Pipeline (NEW — 2026-07-23 Mining)

⚠️ **SUPERSESSION BANNER**: This phase is **NEW** and **ACTIVE** per Ark v5.1 §3.2 (NL-1 ticket). Not in original spec — added by R52c mining.

**Goal**: Implement the 5-notebook segmented ingestion strategy from R52c spec to feed current Omega docs into NotebookLM for LLM-assisted research.

**Source Spec**: `docs/research/archive/R52c_notebooklm_ingestion_strategy.md`

**Notebook Mapping** (per R52c):

| Notebook ID | Notebook Name | Included Paths / Files | Purpose |
| :--- | :--- | :--- | :--- |
| **NB-01** | **Core Engine Architecture** | `src/omega/**/*`, `config/**/*`, `Makefile`, `README.md` | Technical implementation, config, and build logic. |
| **NB-02** | **Strategic Gnosis** | `docs/strategy/**/*`, `docs/ROADMAP.md`, `docs/decisions/PIVOT_LOG.md`, `AGENTS.md`, `ORACLE_STACK.md` | High-level vision, architectural decisions, and agent rules. |
| **NB-03** | **Research Archive** | `docs/research/**/*` | Detailed technical research, API specs, and audit reports. |
| **NB-04** | **Ops & Integration** | `docs/operations/**/*`, `docs/integration/**/*`, `docs/intake/**/*`, `docs/index.md` | Deployment, operational guides, and external integrations. |
| **NB-05** | **Validation Suite** | `tests/**/*`, `scripts/**/*` | Test cases, validation scripts, and utility tools. |

**Script to implement**: `scripts/prepare_notebooklm.py`

**Script Logic & Design** (per R52c):

**A. File Discovery & Filtering**
- **Allowed Extensions**: `.py`, `.md`, `.yaml`, `.json`, `.sh`, `.sql`
- **Exclusions**: `**/__pycache__/**`, `**/.pytest_cache/**`, `**/.git/**`, `**/.venv/**`

**B. Content Cleaning (Signal Enhancement)**
- **Path Injection**: Every file's content prepended with standardized header:
  `--- FILE: {relative_path} ---`
- **Whitespace Normalization**: Remove trailing spaces and collapse triple+ newlines into double newlines.
- **Header Preservation**: Ensure Markdown headers (`#`, `##`) are maintained to help NotebookLM recognize document structure.
- **Code-to-Text Optimization**: For Python files, remove excessively long comment blocks that are redundant with documentation.

**C. Chunking Strategy**
- **Default**: One file = One source.
- **Large File Handling**: If a file exceeds 1MB (rare in this repo), split by top-level function or class definition to keep context window focused.
- **Consolidation**: Very small files (<1KB) in the same directory concatenated into a single `{directory}_bundle.txt` to save source slots.

**D. Export Structure**
The script will output to `notebooklm_export/{NB-ID}/{filename}`, allowing for simple drag-and-drop upload to the respective notebook.

**Refresh Schedule** (per R52c):

| Trigger | Frequency | Action |
| :--- | :--- | :--- |
| **Routine Sync** | Weekly (Monday 09:00) | Full rebuild of all 5 notebooks. |
| **Strategic Pivot** | Per Major PR / Phase | Re-sync **NB-02** and **NB-03** immediately after design changes. |
| **Implementation Spike** | Per Feature Completion | Sync **NB-01** and **NB-05** after new modules are hardened. |

**Naming Convention**: `OMEGA_NL_{YYYYMMDD}_{VERSION}` (e.g., `OMEGA_NL_20260723_v1`)

**Effort**: ~4 hours (script + 5 notebook creation + validation)
**Impact**: Enables LLM-assisted research on current Omega docs via NotebookLM's grounded reasoning.
**Verification**: After implementation, run script, verify 5 export directories created, manually upload to NotebookLM, test query retrieval.

---

### Phase 2: Job Board Bridge

⚠️ **SUPERSESSION BANNER**: This phase is **SUPERSEDED** per Ark v5.1 §3.2 (D-2) and D-357. 
- **Do NOT implement SQLite Research Job Store** (§5, Phase 2 in original spec) — **DEFERRED** per D-357
- **Do implement**: YAML job board + `fcntl.flock` bridge as specified below
- **Do NOT implement**: SQLite schema, claim TTL, P0/P1 auto-queue, verification gates, content TTL tiers T1/T2/T3
- **Do NOT implement**: 7-stage workflow — **DEFERRED** per D-358

**Goal**: Background researcher reads open jobs from the job board and prioritizes them.

**File to modify**: `src/omega/workers/background_researcher/loop.py`

**Change**: Add `_load_board_jobs()` method that reads from `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` and injects unclaimed P0/P1 jobs into the `EnhancedPriorityQueue`.

**New method in `BackgroundResearcherLoop`**:
```python
async def _load_board_jobs(self) -> None:
    """Load open P0/P1 jobs from the research board into the queue."""
    board_path = Path("data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md")
    if not board_path.exists():
        return

    import yaml
    board = yaml.safe_load(board_path.read_text())
    jobs = board.get("jobs", [])

    for job in jobs:
        if job.get("status") != "open":
            continue
        if job.get("depends_on"):
            # Check if dependencies are met
            deps_met = all(
                self._is_job_complete(dep, jobs)
                for dep in job["depends_on"]
            )
            if not deps_met:
                continue

        priority = 0.95 if job.get("priority") == "P0" else 0.75
        topic = f"{job['id']}: {job['title']} — {'; '.join(job.get('queries', [])[:3])}"

        # Check if already in queue
        existing = [t.topic for t in self.queue.to_list()]
        if not any(job["id"] in t for t in existing):
            self.queue.enqueue(
                topic,
                base_priority=priority,
                user_requested=False,
            )
            logger.info(f"Board job {job['id']} enqueued: {job['title']}")

def _is_job_complete(self, job_id: str, jobs: list) -> bool:
    """Check if a job is completed."""
    for j in jobs:
        if j["id"] == job_id:
            return j.get("status") == "completed"
    return False
```

**Integration point**: Call `_load_board_jobs()` at the start of `run_cycle()`, after step 2 (scheduling) and before step 3 (dequeue):

```python
# In run_cycle(), after line 243:
await self._load_board_jobs()  # NEW: Load board jobs into queue
```

**Effort**: ~2 hours
**Impact**: Background researcher stops doing random topic round-robin and starts working on the actual research backlog. Two systems become one.
**Verification**: Add a P0 job to the YAML board, wait for the next background cycle, check logs for "Board job R0X enqueued".

---

### Phase 3: Auto-Indexing of Generated Research

⚠️ **SUPERSESSION BANNER**: This phase is **ACTIVE** per Ark v5.1 §3.2 (D-3). Implement as specified. The INDEX.md registration and follow-up topic emission are authoritative.

**Goal**: When the soul updater creates research docs, they're registered in the research index and propose follow-up topics.

**File to modify**: `src/omega/workers/background_researcher/soul_updater.py`

**Change**: After `_write_research_doc()`, register the new doc in `docs/research/INDEX.md` and emit follow-up topics.

**New method in `SoulUpdater`**:
```python
async def _register_in_index(self, task: ResearchTask, doc_path: Path) -> None:
    """Register auto-generated research doc in INDEX.md."""
    index_path = Path("docs/research/INDEX.md")
    if not await anyio.Path(index_path).exists():
        return

    existing = await anyio.Path(index_path).read_text()
    slug = doc_path.stem
    # Don't register if already present
    if slug in existing:
        return

    # Append to the Research Item Registry table
    entry = f"| R-AUTO-{slug[:20]} | {task.topic} | 🟡 Background | 🔄 | [{doc_path.name}]({doc_path.name}) | {datetime.now(timezone.utc).date()} |\n"

    # Find the last table row and append after it
    lines = existing.split("\n")
    insert_idx = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("| R-"):
            insert_idx = i + 1

    lines.insert(insert_idx, entry.rstrip())
    await anyio.Path(index_path).write_text("\n".join(lines))
    logger.info(f"Registered {doc_path.name} in INDEX.md")
```

**New method for follow-up topics**:
```python
async def _emit_followup_topics(self, task: ResearchTask, gnosis: GnosisPacket) -> None:
    """Emit recommended follow-up topics to the gap detector."""
    if not gnosis.recommended_directions:
        return

    followup_path = Path("data/research/pending_followups.jsonl")
    followup_path.parent.mkdir(parents=True, exist_ok=True)

    for direction in gnosis.recommended_directions:
        entry = {
            "topic": direction.get("topic", task.topic),
            "source_task": task.topic,
            "source_session": task.session_id,
            "recommended_by": "distiller_t3",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "priority": direction.get("priority", 0.6),
        }
        async with await anyio.open_file(str(followup_path), "a") as f:
            await f.write(json.dumps(entry) + "\n")
```

**Integration**: Call both after `_write_research_doc()` in the `update()` method:
```python
# In SoulUpdater.update(), after writing research doc:
await self._register_in_index(task, doc_path)
await self._emit_followup_topics(task, gnosis)
```

**Effort**: ~2 hours
**Impact**: Auto-generated research feeds back into the gap detector, closing the loop. New knowledge creates new research topics.
**Verification**: Run a background cycle, check INDEX.md for the new entry, check `pending_followups.jsonl` for follow-up topics.

---

### Phase 4: Gap Detector as a Service

⚠️ **SUPERSESSION BANNER**: This phase is **DEFERRED** per Ark v5.1 §3.2 (D-4) and D-358. 
- **Do NOT implement** `GapDetector` as a standalone service with 6 scanner classes — **DEFERRED** per D-358
- **Do implement**: Extend `_grow_frontier()` in `loop.py` only (~20 lines) with novelty engine (random + contradiction scanning)
- **Do NOT implement**: SoulGapScanner, IndexGapScanner, EntityGapScanner, ContradictionScanner, FollowupScanner, BoardGapScanner as separate classes
- **Do NOT implement**: GapDetector service class, deduplication, scoring, ResearchTask proposal pipeline
- **Required addition**: Novelty engine (random topic sampling + cross-domain contradiction scanning) + INDEX noise policy

**Original Goal (SUPERSEDED)**: Extract gap-scanning logic into a standalone service that continuously proposes new research.

**New file**: `src/omega/workers/background_researcher/gap_detector.py`

**Purpose**: Replace the ad-hoc `_grow_frontier()` method with a structured gap detection service that:
1. Scans all gap sources (soul, index, entity knowledge, contradictions, follow-ups, job board)
2. Deduplicates against existing queue and recently-completed topics
3. Scores gaps by urgency and relevance
4. Proposes new ResearchTask objects

**Architecture**:
```python
class GapDetector:
    """Continuously scans for knowledge gaps and proposes new research."""

    def __init__(self):
        self.sources = [
            SoulGapScanner(),        # Missing L3 principles per entity domain
            IndexGapScanner(),       # 🔲/🔄 items in research INDEX.md
            EntityGapScanner(),      # Empty/sparse entity knowledge/ dirs
            ContradictionScanner(),  # Items in pending_review.md
            FollowupScanner(),       # pending_followups.jsonl from distiller
            BoardGapScanner(),       # Open P0/P1 jobs from YAML board
        ]

    async def detect_gaps(self) -> List[ResearchTask]:
        """Scan all sources, deduplicate, score, return prioritized tasks."""
        raw_gaps = []
        for source in self.sources:
            gaps = await source.scan()
            raw_gaps.extend(gaps)

        # Deduplicate (by topic similarity)
        deduped = self._deduplicate(raw_gaps)

        # Score (urgency × relevance × novelty)
        scored = self._score(deduped)

        # Return top N as ResearchTask objects
        return [ResearchTask(topic=g.topic, priority=g.score) for g in scored[:10]]
```

**Scanner implementations** (each ~30-50 lines):

| Scanner | Source | Logic |
|---------|--------|-------|
| `SoulGapScanner` | `data/entities/*/soul.yaml` | Check if entity has <3 L3 principles in its domain. Gap = "Research [domain] for entity [name]." |
| `IndexGapScanner` | `docs/research/INDEX.md` | Items with 🔲 status. Gap = item title. |
| `EntityGapScanner` | `data/entities/*/knowledge/` | Empty or <5 files. Gap = "Build knowledge base for [entity]." |
| `ContradictionScanner` | `data/research/pending_review.md` | Unresolved contradictions. Gap = topic + "resolve contradiction." |
| `FollowupScanner` | `data/research/pending_followups.jsonl` | Distiller T3 recommendations. Gap = recommended topic. |
| `BoardGapScanner` | `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` | Open P0/P1 jobs. Gap = job title + queries. |

**Integration**: Replace `_grow_frontier()` in `loop.py` with:
```python
async def _grow_frontier(self) -> None:
    """Use GapDetector to find new research topics."""
    from .gap_detector import GapDetector
    detector = GapDetector()
    gaps = await detector.detect_gaps()
    for gap in gaps:
        self.queue.enqueue(gap.topic, base_priority=gap.priority)
```

**Effort**: ~4 hours
**Impact**: The system proactively identifies what it doesn't know, rather than waiting for humans to propose topics. This is the "intelligence" in "living intelligence."
**Verification**: Run gap detector, verify it finds real gaps (empty entity knowledge dirs, 🔲 index items), verify it doesn't duplicate topics already in the queue.

---

## §4 Implementation Order & Dependencies

```
Phase 1 (Content Persistence)
  │
  ├──→ Phase 3 (Auto-Indexing) ← depends on content being persisted
  │         │
  │         └──→ Phase 4 (Gap Detector) ← depends on INDEX.md being updated
  │
  └──→ Phase 2 (Job Board Bridge) ← independent of Phase 1
```

**Phase 1 and Phase 2 can be built in parallel.** Phase 3 depends on Phase 1. Phase 4 depends on Phase 3.

**Total effort**: ~14 hours across 4 phases.
**Recommended order**: Phase 1 → Phase 2 (parallel) → Phase 3 → Phase 4.

---

## §5 Data Model — Research Job Store (SQLite)

The YAML job board is good for human readability and git tracking. But runtime coordination (atomic claims, TTL enforcement, status tracking) needs SQLite. The YAML seeds the DB; the DB is the runtime SSOT.

**Schema** (`data/research/research_jobs.db`):

```sql
CREATE TABLE IF NOT EXISTS research_jobs (
    id TEXT PRIMARY KEY,               -- "R01", "R02", etc.
    title TEXT NOT NULL,
    phase INTEGER,
    sprint TEXT,
    priority TEXT,                      -- "P0", "P1", "P2"
    status TEXT DEFAULT 'open',         -- open|claimed|in_progress|completed|deferred|cancelled
    claimed_by TEXT,                    -- entity name
    claimed_at TIMESTAMP,
    claim_expires_at TIMESTAMP,         -- claimed_at + claim_ttl_hours
    depends_on TEXT,                    -- JSON array of job IDs
    capabilities TEXT,                  -- JSON array of capability tags
    queries TEXT,                       -- JSON array of search queries
    deliverable TEXT,                   -- expected output file path
    decision_gate TEXT,                 -- the question to answer
    sources_count INTEGER DEFAULT 0,
    key_findings TEXT,                  -- summary of findings
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT REFERENCES research_jobs(id),
    finding_text TEXT NOT NULL,
    source_url TEXT,
    confidence REAL,                   -- 0.0-1.0
    l1_narrative TEXT,
    l2_insight TEXT,
    l3_principle TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT REFERENCES research_jobs(id),
    decision_text TEXT NOT NULL,
    status TEXT DEFAULT 'open',         -- open|answered|implemented|rejected
    answer TEXT,
    pivot_log_entry TEXT,               -- link to PIVOT_LOG.md
    decided_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**YAML → SQLite seed script** (`src/omega/research/job_store.py`):
```python
def seed_from_yaml(yaml_path: str, db_path: str) -> None:
    """Load YAML job board into SQLite as initial seed."""
    board = yaml.safe_load(Path(yaml_path).read_text())
    for job in board.get("jobs", []):
        insert_job(job)
```

**Effort**: ~3 hours (included in Phase 2 estimate).

---

## §6 Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Content persistence rate** | 100% of websearch/webfetch results cached | `ls .firecrawl/ \| wc -l` grows with each research session |
| **Background ↔ Board sync** | Board P0 jobs appear in researcher queue within 20 min | Check logs for "Board job R0X enqueued" |
| **Follow-up emission** | Distiller T3 recommendations create pending_followups.jsonl entries | `wc -l data/research/pending_followups.jsonl` > 0 after research cycle |
| **INDEX.md auto-registration** | R_AUTO_*.md files appear in INDEX.md | `grep "R-AUTO" docs/research/INDEX.md` returns results |
| **Gap detector coverage** | Detects at least 5 gap types | Unit test covering all 6 scanner types |
| **Loop closure** | A finding in cycle N creates a new research topic in cycle N+1 | Integration test: seed a gap → run cycle → verify new topic enqueued |
| **Zero ephemeral searches** | Every search result persists across sessions | `search_history.db` record count grows; `.firecrawl/` file count grows |

---

## §7 What Already Works (Don't Touch)

These components are battle-tested and should NOT be modified unless there's a specific bug:

1. **`BackgroundResearcherLoop.run_cycle()`** — The state machine is solid. Atomic locking, checkpoint recovery, Hivemind posting. Only add `_load_board_jobs()` call.
2. **`Distiller.distill()`** — 3-tier pipeline with circuit breakers. Don't touch the tier logic.
3. **`EnhancedPriorityQueue`** — Weighted fair scheduling works. Only consume its output.
4. **`TopicScheduler`** — Round-robin with aging works for the existing topic set. The Gap Detector replaces it, but keep it as a fallback.
5. **`ConvergenceDetector`** — 4 stopping conditions are correct. Don't add more.
6. **`SoulUpdater._write_to_soul()`** — L3 → soul.yaml works. Only add INDEX.md registration and follow-up emission.

---

## §8 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Content cache grows unbounded | Disk fill on 5700U (limited storage) | TTL eviction: delete files older than 30 days. LRU cap: 10GB max. |
| Gap detector creates infinite topics | Queue overflow, resource exhaustion | Deduplication by topic similarity. Max 10 topics per scan. Priority floor at 0.3. |
| Board job bridge creates duplicate work | Background researcher re-does foreground research | Check `claimed_by` before injecting. Only inject `status=open` jobs. |
| Auto-indexing creates noisy INDEX.md | Hard to find real research among auto-generated entries | Use 🟡 Background in urgency column for auto-generated entries (vs 🔴/🟡 for manual). |
| SQLite job store conflicts with YAML | Two sources of truth | YAML = seed (loaded once). SQLite = runtime SSOT. Never write back to YAML. |

---

## §9 Post-Compaction Recovery

This spec is the canonical reference for the Living Research OS. After compaction:

1. **Read this document** (`docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md`)
2. **Read the session anchor** (`data/coordination/SESSION_ANCHOR.md`)
3. **Check which phase is in progress** (look for WIP markers in the spec)
4. **Resume from the exact line** where work stopped

The three agent audit reports are preserved at:
- `data/coordination/CARMACK_RESEARCH_AUDIT_20260721.md` — John Carmack's first-principles audit
- `data/coordination/RESEARCHER_QUEUE_DESIGN_20260721.md` — Researcher's queue architecture (1,171 lines)
- `data/coordination/GROKSTER_RESEARCH_QUEUE_ANALYSIS_20260721.md` — Grokster's debut analysis

---

*⬡ OMEGA ⬡ KALI ⬡ {session_model} ⬡ opencode ⬡ trc_living_research ⬡ CANONICAL*
