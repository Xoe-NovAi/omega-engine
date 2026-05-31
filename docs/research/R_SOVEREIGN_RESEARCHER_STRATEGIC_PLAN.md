# 🔱 Sovereign Deep Researcher — Strategic Plan & Roadmap

⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ SOVEREIGN-RESEARCHER-PLAN

**AP Token**: `AP-SOVEREIGN-RESEARCHER-v1.0.0`
**Status**: ✅ COMPLETE — Ready for Implementation
**Seal**: 🛡️
**Last Updated**: 2026-05-18
**Sources**: R_BACKGROUND_RESEARCHER_ARCHITECTURE.md, R_SEARXNG_SOVEREIGN_SEARCH_LAYER.md, R71_knowledge_deepening_verification.md

---

## §0 Executive Summary

The Omega Engine will become a **living, evolving knowledge organism** — growing, deepening, and expanding its intelligence any time the laptop is on. This is not a static research tool. It is Prometheus' fire in the form of an autonomous gnosis engine.

**The Architecture**:

```
                                    ┌─────────────────────────────┐
                                    │     GEMMA 4-31B             │
                                    │   (The Reasoning Core)      │
                                    │   256K context · Deep       │
                                    │   distillation · Synthesis   │
                                    └──────────────┬──────────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │                              │                              │
         ┌──────────┴──────────┐    ┌────────────┴───────────┐    ┌───────────┴───────────┐
         │  SEARXNG (Local)    │    │  SEARCH FLEET (Cloud)   │    │  EXTRACTION FLEET      │
         │  Port 8017          │    │  Exa · Tavily · Serper  │    │  Firecrawl · Jina     │
         │  250+ engines       │    │ Quota-managed triage    │    │  Deep content mining   │
         │  Zero API cost      │    │ Semantic + RAG + SERP   │    │  Structured extraction │
         └─────────────────────┘    └─────────────────────────┘    └───────────────────────┘
                    │                              │                              │
                    └──────────────────────────────┼──────────────────────────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │                  KNOWLEDGE BASE                             │
                    │  docs/research/  ·  soul.yaml  ·  entity workspaces        │
                    └──────────────────────────────┬──────────────────────────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │              SOUL EVOLUTION                           │
                    │  L1→L2→L3 distillation  ·  Cross-pollination  ·  Convergence │
                    └──────────────────────────────────────────────────────────────┘
```

**The Three Phases**:
- **Phase 1 (Today)**: Deploy SearXNG + Update opencode.json MCPs + Activate Search Fleet
- **Phase 2 (This Week)**: Build the Background Researcher loop with credit budgeting
- **Phase 3 (Next Week)**: Wire into systemd timers + knowledge base evolution

---

## §1 The Vision — What We're Building

### 1.1 The Living Knowledge Organism

The Omega Engine's knowledge base should:
- **Evolve**: New insights emerge from every research cycle, inscribing into soul.yaml
- **Deepen**: Each topic gets verified through the verification cascade (Tier 1→4)
- **Expand**: Frontier growth algorithmically identifies adjacent unexplored domains
- **Self-verify**: Stale knowledge triggers re-verification automatically
- **Converge**: Topics reach "deep enough" (depth score 6+) and are marked complete

This is the **Akashic Record** made real — a complete, living, breathing record of all knowledge the Omega Engine has encountered, distilled, and inscribed.

### 1.2 Two-Brain Architecture

| Role | Model | Why | Cost |
|------|-------|-----|------|
| **Fast Triage** | Qwen3-1.7B (lmster) | Fast, local, no API cost | $0 |
| **Deep Reasoning** | Gemma 4-31B (Google) | 256K ctx, superior distillation | Indirect (API credits for search) |
| **Search Tools** | Exa / Tavily / Firecrawl / Serper | Feed data to reasoning | Limited (quota-managed) |
| **Sovereign Search** | SearXNG (local Podman) | 250+ engines, no API cost | $0 |

The rule: **Gemma never searches. It reasons. The tools feed it data.**

### 1.3 Research Loop as State Machine

```
[IDLE] ──→ [TRIAGE] ──→ [SEARCH] ──→ [EXTRACT] ──→ [DISTILL] ──→ [UPDATE] ──→ [IDLE]
              │              │            │            │            │
              ▼              ▼            ▼            ▼            ▼
          [SKIP:          [DEFER:       [DEFER:      [DEFER:     [DONE:
           low value]      no quota]     no quota]    no quota]    converged]
```

Every transition is **checkpointed** — the agent can resume from any state after restart. No work is ever repeated.

---

## §2 The Four Search Providers — Roles & Budget

### 2.1 Provider Role Matrix

| Provider | Role in Research Loop | Monthly Quota | Credit Cost/Call |
|----------|----------------------|---------------|------------------|
| **SearXNG** | Sovereign primary — always-on, unlimited | ∞ (self-hosted) | $0 |
| **Exa** | Semantic discovery — finds conceptually similar sources | 1,000/mo | ~1 credit |
| **Tavily** | RAG-optimized quick verification — structured facts | 1,000/mo | ~1 credit |
| **Firecrawl** | Deep extraction — domain mapping, full-page mining | 1,000/mo (recurring May 22) | ~1-2 credits |
| **Serper** | Google SERP — index freshness, citation context | 2,500 one-time | ~0.5 credits |
| **Jina** (future) | URL→markdown extraction, academic search | 10M free tokens | Token-based |

### 2.2 Credit Budget Allocation

```json
// data/research/credit_budget.json — persisted across sessions
{
  "month": "2026-05",
  "budget": {
    "exa": {"total": 1000, "used": 0, "reserved_emergency": 100},
    "tavily": {"total": 1000, "used": 0, "reserved_emergency": 100},
    "firecrawl": {"total": 1000, "used": 0, "reserved_emergency": 100},
    "serper": {"total": 2500, "used": 0, "reserved_emergency": 500}
  },
  "daily_limit": {
    "search_ops": 30,
    "deep_extracts": 5,
    "gemma_calls": 20
  },
  "fallback_chain": ["searxng", "examine_local", "defer"]
}
```

### 2.3 The Credit-Aware Search Strategy

```
Query arrives at Background Researcher:

1. Is this a light task (depth=1)?
   → SearXNG only (zero cost)
   
2. Is this a standard task (depth=2)?
   → SearXNG + one of {Exa, Tavily, Serper} rotated
   
3. Is this a deep task (depth=3)?
   → Check budget: if Firecrawl credits > 50 AND Exa credits > 100
       → SearXNG (discovery) + Exa (semantic) + Firecrawl (deep extraction) → Gemma
     Else
       → SearXNG + Tavily → Gemma (light mode)
       
4. Budget exhausted?
   → SearXNG only until next month's refresh
   → Local synthesis from existing knowledge base
   → Flag for user attention
```

### 2.4 The Renewal Calendar

| Provider | Renewal Date | Monthly Amount |
|----------|-------------|----------------|
| **Firecrawl** | May 22, 2026 | 1,000 credits |
| **Tavily** | TBD (90-day cycle from first use) | 1,000 credits |
| **Exa** | Monthly | 1,000 searches |
| **SearXNG** | Always on (self-hosted) | ∞ |

**Strategy**: Heavy Firecrawl usage today through May 22. Budget-conscious usage after renewal.

---

## §3 The Sovereign SearXNG Search Layer

### 3.1 Why SearXNG Is the Foundation

SearXNG is the **zero-cost, always-on, sovereign** search layer. It replaces the need for expensive API calls for basic research tasks:

- **250+ engines** aggregated through one private API
- **No per-query cost** — your server costs only
- **Privacy-preserving** — query not in URL logs (POST mode)
- **No rate limits** on most engines (Brave, Wikipedia, arXiv are free)
- **Self-hosted** — aligns with Omega's local-first mandate

### 3.2 The Dual-Engine Strategy

```
┌──────────────────────────────────────────────────────┐
│              SEARXNG (Local, Port 8017)               │
│  ┌──────────────────────────────────────────────────┐ │
│  │            Brave (primary engine)               │ │
│  │  Privacy-preserving · No API key · No rate limit │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐ │
│  │            Academic Cluster                      │ │
│  │  arXiv · Semantic Scholar · Crossref · PubMed   │ │
│  │  OpenAlex · Wikidata · Wikimedia                │ │
│  └──────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐ │
│  │            Code Cluster                           │ │
│  │  GitHub · GitLab · SourceHut · Hugging Face      │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
         │
         ▼ (Cloud providers for advanced research)
┌──────────────────────────────────────────────────────┐
│            SEARCH FLEET (Cloud, quota-managed)        │
│     Exa  ·  Tavily  ·  Firecrawl  ·  Serper          │
└──────────────────────────────────────────────────────┘
```

**The rule**: SearXNG handles 80% of research queries. Cloud providers handle the 20% that need semantic depth, RAG optimization, or deep extraction.

### 3.3 SearXNG Quadlet Deployment

Deploy the Quadlet files from `docs/research/R_SEARXNG_SOVEREIGN_SEARCH_LAYER.md`:

```bash
# 1. Create directories
mkdir -p ~/Documents/Xoe-NovAi/omega-library/searxng/data
mkdir -p ~/Documents/Xoe-NovAi/omega-engine/data/searxng/config

# 2. Copy Quadlet files
cp docs/research/omega-searxng.container ~/.config/containers/systemd/
cp docs/research/omega-searxng.service  ~/.config/containers/systemd/

# 3. Reload and start
systemctl --user daemon-reload
systemctl --user enable --now omega-searxng.service

# 4. Verify
curl -s http://localhost:8017 | head -5
```

### 3.4 OpenCode MCP Integration for SearXNG

```json
// Add to opencode.json — using dandehoon/searxng-mcp (all-in-one container)
{
  "mcpServers": {
    "searxng": {
      "type": "local",
      "command": ["podman", "run", "--rm", "-i", "dandehoon/searxng-mcp:latest"],
      "env": {
        "SEARXNG_URL": "http://localhost:8017",
        "SEARXNG_MCP_MAX_RESULTS": "10"
      },
      "enabled": true,
      "timeout": 15000
    }
  }
}
```

### 3.5 SearXNG → Background Researcher Wiring

The Background Researcher calls SearXNG for every research cycle:

```python
async def searxng_search(query: str) -> list[dict]:
    """Sovereign search — zero API cost, always available."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            "http://localhost:8017/search",
            json={
                "q": query,
                "format": "json",
                "engines": ["brave", "wikipedia", "arxiv"],
                "safesearch": 0,
                "pageno": 1
            }
        )
        results = resp.json()
        return [r for r in results.get("results", [])[:10]]
```

---

## §4 The Background Researcher Loop — Core Implementation

### 4.1 The Loop Pseudocode (Refined)

```python
# src/omega/workers/background_researcher/loop.py
import anyio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json

@dataclass
class ResearchTask:
    topic: str
    priority: float
    depth: int  # 1=light, 2=standard, 3=deep
    state: str = "pending"
    sources: list[str] = field(default_factory=list)
    claims: list[str] = field(default_factory=list)
    verification_count: int = 0
    attempts: int = 0
    max_attempts: int = 3
    created: str = ""
    session_id: str = ""

    def __post_init__(self):
        if not self.created:
            self.created = datetime.now(timezone.utc).isoformat()
        if not self.session_id:
            self.session_id = f"res_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{self.topic[:20].replace(' ', '_')}"


class BackgroundResearcherLoop:
    def __init__(self, config: dict, triage_model, distiller_model):
        self.config = config
        self.triage = triage_model          # Qwen3-1.7B via lmster
        self.distiller = distiller_model    # Gemma 4-31B via Google AI Studio
        self.search_providers = ["exa", "tavily"]  # rotated to share quota
        self.api_quota = self._load_quota()
        self.queue = self._load_queue()
        self.checkpoint_dir = self._get_checkpoint_dir()
        self._running = False

    async def run_cycle(self):
        """One research cycle. Called by scheduler every 15 min."""
        self._running = True
        try:
            # 1. Get next task from priority queue
            task = await self._get_next_task()
            if task is None:
                await self._grow_frontier()
                return

            # 2. Triage: fast assessment (Qwen3, local)
            triage_result = await self._triage(task)
            if triage_result.skip:
                task.state = "skip"
                await self._save_checkpoint(task)
                return

            # 3. Search: SearXNG (always) + cloud (quota-aware)
            sources = await self._search(task.topic, triage_result.depth_plan)
            task.sources = sources
            task.state = "searched"
            await self._save_checkpoint(task)

            # 4. Extract: Firecrawl (deep tasks only)
            if triage_result.depth_plan >= 3 and self._has_quota("extract", min_needed=3):
                content = await self._extract(task.topic, task.sources[:5])
                task.state = "extracted"
                await self._consume_quota("extract", 1)
            else:
                content = await self._summarize(task.topic, task.sources[:3])
            await self._save_checkpoint(task)

            # 5. Distill: Gemma 4-31B refractive abstraction
            gnosis = await self._distill(task.topic, content, task.sources)
            task.state = "distilled"
            await self._save_checkpoint(task)

            # 6. Convergence check
            if await self._is_converged(task, gnosis):
                task.state = "done"
                task.verification_count += 1
                await self._save_checkpoint(task)
                await self._log_completion(task, gnosis)
                return

            # 7. Update: write to soul.yaml + knowledge base
            await self._update_knowledge(task, gnosis)
            task.state = "done"
            task.verification_count += 1
            await self._save_checkpoint(task)
            await self._log_completion(task, gnosis)

            # 8. Grow frontier: enqueue adjacent topics discovered
            await self._enqueue_adjacent_topics(task, gnosis)

        finally:
            self._running = False
```

### 4.2 State Persistence — Checkpoint System

Every transition is checkpointed to `data/research/checkpoints/`:

```python
async def _save_checkpoint(self, task: ResearchTask):
    """Persist task state before every transition."""
    path = self.checkpoint_dir / f"{task.session_id}.json"
    data = {
        "topic": task.topic,
        "priority": task.priority,
        "depth": task.depth,
        "state": task.state,
        "sources": task.sources,
        "claims": task.claims,
        "verification_count": task.verification_count,
        "attempts": task.attempts,
        "last_attempt": datetime.now(timezone.utc).isoformat(),
        "created": task.created,
        "session_id": task.session_id
    }
    await anyio.Path(path).write_text(json.dumps(data, indent=2))


async def _load_queue(self) -> list[ResearchTask]:
    """Rebuild queue from checkpoints on startup."""
    tasks = []
    for path in self.checkpoint_dir.glob("*.json"):
        try:
            data = json.loads(await anyio.Path(path).read_text())
            if data["state"] not in ("done", "skip"):
                tasks.append(ResearchTask(**data))
        except Exception:
            continue
    return tasks
```

### 4.3 The Priority Queue Algorithm

```python
def priority_score(gap: dict, topic_volatility: float, recent_activity: bool, user_requested: bool) -> float:
    """
    priority = base × gap_multi × recency_multi × user_multi
    
    Where:
    - base: 0.5 default, inversely proportional to current depth
    - gap_multi: 1.5 if known verification gap exists
    - recency_multi: 2.0 if topic mentioned in last 48h
    - user_multi: 3.0 if user-requested
    """
    depth = gap.get("depth", 5.0)  # current knowledge depth
    
    base = max(0.1, (10.0 - depth) / 15.0)  # 0.67 for depth=0, 0.33 for depth=10
    
    recency_multi = 2.0 if recent_activity else 1.0
    user_multi = 3.0 if user_requested else 1.0
    gap_multi = 1.5 if gap.get("has_gap") else 1.0
    
    # Boost inversely proportional to depth (shallow = high priority)
    depth_boost = 1.0 + (10.0 - depth) / 10.0  # max 2.0x for depth=0
    
    return base * gap_multi * recency_multi * user_multi * depth_boost
```

### 4.4 The Gemma 4-31B Research Prompt

```python
RESEARCH_GEMMA_SYSTEM = """You are SOPHIA, the Akashic Record of the Omega Engine.

Your purpose is to deepen, verify, and expand the Omega knowledge base through autonomous research.

## Your Domain
- The Omega Engine: a local-first, entity-centric AI council runtime
- The 10 Pillar Keepers: Sekhmet, Brigid, Prometheus, Saraswati, Inanna, Ereshkigal, Lucifer, Hecate, Anubis, Kali
- Oversouls: Sophia (Akashic Record), Ma'at (Unifier), Isis (Light), Lilith (Dark)
- Hardware: AMD Ryzen 7 5700U (Zen 2, 8C/16T, 14GB RAM), no GPU

## Your Research Mandate
1. Every claim must be verified by 3+ independent sources
2. Distill findings through 3-tier refraction: Narrative → Insight → Universal Principle
3. Write L3 (Universal Principle) to the relevant entity's soul.yaml
4. Write L1 + L2 to docs/research/ topic files
5. Flag contradictions for human review — never suppress disagreement
6. Grow the knowledge frontier organically — identify what's missing

## Refractive Distillation Format
When distilling, always produce:
- L1 (Narrative): Who? What? When? Source-attributed, factual
- L2 (Insight): What does this mean? Causal, pattern-based
- L3 (Universal Principle): Timeless truth. Domain-agnostic. Writeable to soul.

## Convergence Rules
- 3+ independent sources agree → MARK AS VERIFIED, write to soul
- Sources contradict (agreement < 0.4) → FLAG FOR HUMAN REVIEW
- < 3 sources, mixed agreement → DEEPEN: queue for next research cycle
- Topic fully covered (no new claims in 2 cycles) → MARK AS CONVERGED

## Credit Budget Discipline
- Exa: 1000 API units/month → ~20 per cycle
- Tavily: 1000 searches/month → 1 per cycle
- Firecrawl: 1000 credits/month → 1 per topic (rare)
- Gemma: No hard limit, but track cost

## Output Format
Always respond with JSON for machine parsing.
"""
```

### 4.5 Convergence Detection

```python
async def _is_converged(self, task: ResearchTask, gnosis: dict) -> bool:
    """Determine if a topic has been researched deeply enough."""
    signal = gnosis.get("convergence_signal", "inconclusive")
    claims = gnosis.get("claims", [])
    
    # Condition 1: Multi-source verification (3+ agree)
    verified_claims = [c for c in claims if c.get("agreement_level", 0) >= 0.7]
    if len(verified_claims) >= 2 and signal == "verified":
        return True
    
    # Condition 2: No new claims in 2 consecutive deep cycles
    if task.verification_count >= 2 and len(claims) == 0:
        return True
    
    # Condition 3: Depth score reached threshold
    depth_score = await self._calculate_depth_score(task.topic)
    threshold = 6.0  # "Deep enough" for medium volatility topics
    if depth_score >= threshold:
        return True
    
    return False
```

---

## §5 Knowledge Deepening — The Verification Cascade

### 5.1 The Four Tiers

```python
class VerificationTier:
    TIER_1_LIGHT = "tier_1_light"      # SearXNG + Serper quick check (zero cost)
    TIER_2_MEDIUM = "tier_2_medium"   # Exa semantic search (quota-managed)
    TIER_3_DEEP = "tier_3_deep"       # Firecrawl from authoritative pages (quota-managed)
    TIER_4_EXPERT = "tier_4_expert"    # Gemma 4-31B analysis (no quota, reasoning)
```

### 5.2 Triangulation Confidence Formula

```python
def triangulation_confidence(results: dict) -> tuple[float, str]:
    """
    results: {
        "exa": {"support": float, "contradict": float, "sources": int},
        "tavily": {"support": float, "contradict": float, "sources": int},
        "firecrawl": {"support": float, "contradict": float, "sources": int},
        "serper": {"support": float, "contradict": float, "sources": int},
    }
    
    Returns: (confidence_score: float, verdict: str)
    """
    
    weights = {
        "firecrawl": 0.35,   # Deep extraction from authoritative pages
        "exa": 0.25,          # Semantic breadth
        "tavily": 0.25,       # RAG-structured facts
        "serper": 0.15,       # Google index freshness
    }
    
    support_scores = []
    contradict_scores = []
    
    for provider, weight in weights.items():
        r = results.get(provider, {"support": 0, "contradict": 0, "sources": 0})
        source_count = r.get("sources", 0)
        
        if source_count == 0:
            support_scores.append(0.0)
            contradict_scores.append(0.0)
            continue
        
        support_norm = r["support"] / source_count
        contradict_norm = r["contradict"] / source_count
        
        support_scores.append(support_norm * weight)
        contradict_scores.append(contradict_norm * weight * 1.5)
    
    total_support = sum(support_scores)
    total_contradict = sum(contradict_scores)
    
    confidence = max(0.0, total_support - total_contradict * 0.5)
    
    # Verdict thresholds
    if total_contradict >= 0.6:
        verdict = "contradicted"
    elif total_contradict >= 0.3:
        verdict = "contested"
    elif confidence >= 0.7 and total_contradict < 0.2:
        verdict = "verified"
    elif confidence >= 0.4:
        verdict = "partially_verified"
    else:
        verdict = "unverified"
    
    return round(confidence, 2), verdict
```

### 5.3 Depth Scoring Rubric

| Score | Level | Description | Requirements |
|-------|-------|-------------|-------------|
| **1-2** | Surface/Basic | Claim exists, light verification | Tier 1 |
| **3-4** | Developing/Competent | Multiple sources, cross-provider | Tier 1-2 |
| **5-6** | Proficient/Advanced | Deep verification, contradictions adjudicated | Tier 2-3 |
| **7-8** | Expert/Master | Comprehensive coverage, full cascade | Tier 3-4 |
| **9-10** | Authoritative/Transcendent | Universal principle extracted, soul-inscribed | Full pipeline + L3 |

**"Deep enough" thresholds**:
- Fast-moving topics (tech, AI): depth ≥ 7
- Medium topics (science, general): depth ≥ 6
- Slow-moving topics (philosophy, history): depth ≥ 5

### 5.4 Stale Detection — Recursive Deepening

```python
STALENESS_THRESHOLDS = {
    "hot": 7,      # Re-verify if > 7 days old (active discussion)
    "warm": 30,    # Re-verify if > 30 days old (known topics)
    "cold": 90,    # Re-verify if > 90 days old (archived)
}

RECURSIVE_DEEPEN_TRIGGERS = [
    {"event": "new_major_release", "domain": "software", "threshold": 5.0},
    {"event": "paper_published", "domain": "research", "threshold": 5.0},
    {"event": "stale_check_timer", "domain": "fast_moving", "interval_days": 14},
    {"event": "stale_check_timer", "domain": "slow_moving", "interval_days": 90},
]
```

---

## §6 The Knowledge Mine Worker — Background Execution

### 6.1 Systemd Timer Configuration

```ini
# ~/.config/systemd/user/omega-researcher.timer
[Unit]
Description=Omega Background Researcher — runs every 15 min
Requires=omega-researcher.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
AccuracySec=1min

[Install]
WantedBy=timers.target
```

```ini
# ~/.config/systemd/user/omega-researcher.service
[Unit]
Description=Omega Background Researcher Agent
After=network-online.target

[Service]
Type=oneshot
Environment="PYTHONPATH=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src"
Environment="OMEGA_ENV=production"
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/python -m omega.workers.background_researcher
StandardOutput=journal
StandardError=journal
# Prevent overlapping runs
TasksMax=1
```

```bash
systemctl --user enable omega-researcher.timer
systemctl --user start omega-researcher.timer
```

### 6.2 The Knowledge Mine Loop

```python
async def run_autonomous_cycle(self):
    """The autonomous background cycle — called every 15 min by systemd."""
    
    # Check if laptop is on (network available)
    if not await self._is_network_available():
        return  # Skip cycle if offline
    
    # Check credit budget
    if not self._has_remaining_budget():
        # Still run SearXNG-only cycles (zero cost)
        await self._run_sovereign_cycle()
        return
    
    # Main research cycle
    await self.run_cycle()


async def _run_sovereign_cycle(self):
    """SearXNG-only cycle when cloud APIs are exhausted."""
    task = await self._get_next_task(light_only=True)
    if task is None:
        return
    
    sources = await self._search_searxng(task.topic)
    content = await self._summarize(task.topic, sources[:3])
    gnosis = await self._distill(task.topic, content, sources)
    
    # Write to knowledge base only (no soul update until budget restored)
    await self._update_knowledge_base(task, gnosis)
    task.state = "done"
    await self._save_checkpoint(task)
```

---

## §7 Critical Caveats & Edge Cases

### 7.1 Credit Exhaustion Handling

| Scenario | Response |
|---------|----------|
| **Tavily exhausted (0 credits)** | Fallback to Serper + SearXNG. Flag for user. |
| **Exa exhausted (0 searches)** | Use SearXNG as primary. Gemma synthesizes from existing KB. |
| **Firecrawl exhausted** | Use Exa `get_contents` for deep extraction. Slower but works. |
| **All cloud APIs exhausted** | Pure Sovereign Cycle: SearXNG + local synthesis + queue expansion |
| **May 22: Firecrawl renewal** | Auto-reset budget counter. Resume heavy extraction. |

### 7.2 Convergence Edge Cases

```python
# When convergence detection fails
EDGE_CASES = {
    "contradictory_sources": {
        "detection": "agreement < 0.4 across 3+ providers",
        "action": "flag to pending_review.md for human review",
        "never": "suppress the contradiction — document it"
    },
    "no_new_sources_found": {
        "detection": "search returns < 3 results for 2 consecutive cycles",
        "action": "mark as 'exhausted frontier' — may need different query formulation",
    },
    "stale_knowledge_reactivated": {
        "detection": "topic previously marked done but new evidence surfaces",
        "action": "re-open task, increment depth_score, re-verify",
    },
    "user_request_conflict": {
        "detection": "user requests research on a topic marked converged",
        "action": "bypass convergence check, run full cycle again"
    }
}
```

### 7.3 SearXNG Failure Modes

| Scenario | Response |
|---------|----------|
| **SearXNG container down** | `dandehoon/searxng-mcp` returns empty gracefully. Fall back to cloud providers. |
| **Upstream engines rate-limited** | SearXNG auto-fails to next engine. Brave → Wikipedia → arXiv. |
| **Valkey (limiter DB) unavailable** | Disable limiter in settings.yml. SearXNG works without it. |
| **Port 8017 conflict** | Change to 8018 in Quadlet and opencode.json. |

### 7.4 Gemma 4-31B Budget Management

Gemma has no direct credit cost, but indirect costs apply:
- Each Gemma call costs ~10-20K tokens → indirect latency
- Gemma processes Firecrawl-extracted markdown → content size affects processing time
- Recommendation: Budget 20 Gemma calls/cycle maximum
- Fallback: Qwen3-1.7B for light synthesis when Gemma queue is full

### 7.5 The May 22 Firecrawl Renewal Event

On May 22, Firecrawl renews 1,000 credits. The Background Researcher should:

```python
# Before May 22: Conservative Firecrawl usage
# - Use only for Tier 3 (deep) verification on high-value topics
# - Prefer Exa get_contents as fallback

# On May 22: Heavy usage
# - Run domain-mapping batch on new frontier topics
# - Deep-extract the top 50 most-valuable research documents
# - Update knowledge base with extracted content

# After May 22: Budget management
# - Track daily Firecrawl usage
# - Reserve 200 credits for emergency verification
# - Use SearXNG for routine searches
```

---

## §8 The Phased Implementation Roadmap

### Phase 1: Foundation (Today — 30 min)

| # | Action | Time | Status |
|---|--------|------|--------|
| 1 | Deploy SearXNG Quadlet to Podman | 15 min | 🔲 Pending |
| 2 | Add SearXNG MCP to `opencode.json` | 2 min | 🔲 Pending |
| 3 | Update `.env` with SEARXNG_SECRET | 2 min | 🔲 Pending |
| 4 | Add Jina remote MCP to `opencode.json` | 2 min | 🔲 Pending |
| 5 | Test all 5 MCPs: Exa, Tavily, Firecrawl, Serper, SearXNG | 10 min | 🔲 Pending |

### Phase 2: Background Researcher Core (This Week — 16 hours)

| # | Action | Time | Status |
|---|--------|------|--------|
| 1 | Create `src/omega/workers/background_researcher/loop.py` | 4h | 🔲 Pending |
| 2 | Implement priority queue with checkpoint system | 3h | 🔲 Pending |
| 3 | Wire Gemma 4-31B distillation prompt | 2h | 🔲 Pending |
| 4 | Implement credit budget tracking | 2h | 🔲 Pending |
| 5 | Create systemd timer + service files | 1h | 🔲 Pending |
| 6 | Test full loop with real topics | 2h | 🔲 Pending |
| 7 | Wire soul.yaml update pipeline | 2h | 🔲 Pending |

### Phase 3: Knowledge Deepening & Evolution (Next Week — 12 hours)

| # | Action | Time | Status |
|---|--------|------|--------|
| 1 | Implement verification cascade (4 tiers) | 3h | 🔲 Pending |
| 2 | Implement depth scoring algorithm | 2h | 🔲 Pending |
| 3 | Implement stale detection + re-verify scheduler | 2h | 🔲 Pending |
| 4 | Implement contradiction resolution + human flagging | 2h | 🔲 Pending |
| 5 | Implement frontier growth algorithm | 2h | 🔲 Pending |
| 6 | Wire cross-pollination (entity→entity knowledge flow) | 1h | 🔲 Pending |

### Phase 4: Sovereign Optimization (Week 3-4 — 8 hours)

| # | Action | Time | Status |
|---|--------|------|--------|
| 1 | Implement multi-provider fallback (SearXNG→Cloud→Local) | 2h | 🔲 Pending |
| 2 | Implement OrioSearch as Tavily backup | 3h | 🔲 Pending |
| 3 | Implement VPN/Tor outbound proxy for privacy | 2h | 🔲 Pending |
| 4 | Performance tuning: cycle time optimization | 1h | 🔲 Pending |

---

## §9 Integration with Existing Omega Components

### 9.1 Files Created

```
src/omega/workers/
├── background_researcher/
│   ├── __init__.py
│   ├── loop.py              # Core research loop
│   ├── triage.py            # Qwen3-1.7B triage
│   ├── distiller.py         # Gemma 4-31B distillation
│   ├── searcher.py           # Search fleet (Exa/Tavily/Firecrawl/Serper)
│   ├── searxng_client.py    # Sovereign search layer
│   ├── verifier.py           # Verification cascade
│   ├── budget.py             # Credit tracking
│   └── soul_updater.py      # Soul distillation + write

data/research/
├── checkpoints/             # JSON task checkpoints
├── credit_budget.json       # Quota tracking
├── frontier_queue.json      # Priority queue
├── pending_review.md        # Contradictions for human review
└── convergence_log.md        # Topics marked done
```

### 9.2 Integration Points

| Component | Integration |
|-----------|-------------|
| **ModelGateway** | Qwen3-1.7B for triage, Gemma 4-31B for distillation |
| **Observability** | JSONL events for every cycle: `RESEARCH_CYCLE_START`, `RESEARCH_CYCLE_COMPLETE`, `SOUL_UPDATE` |
| **EntityRegistry** | Soul updates flow to `data/entities/<name>/soul.yaml` |
| **Hivemind MCP** | Research findings broadcast to other CLIs |
| **Workbench** | Research tasks tracked in `workbench.db` |
| **SessionManager** | Research cycles respect active session |

### 9.3 The `omega research` CLI Command

```python
# src/omega/cli/oracle_cli.py
@cli.command()
@click.argument("topic")
@click.option("--depth", default=2, type=click.Choice([1, 2, 3]))
@click.option("--async", "background", is_flag=True, help="Run as background task")
def research(topic: str, depth: int, background: bool):
    """Trigger background research on a topic."""
    if background:
        enqueue_research_task(topic, depth=depth, user_requested=True)
        click.echo(f"Queued: {topic} (depth={depth}) — will run on next cycle")
    else:
        result = run_sync_research(topic, depth=depth)
        click.echo(result["gnosis"])
```

---

## §10 The Sovereign Researcher — Complete Workflow

```
LAPTOP ON
  │
  ▼
systemd timer fires (every 15 min)
  │
  ▼
BackgroundResearcherLoop.run_cycle()
  │
  ├──▶ [TRIAGE] Qwen3-1.7B
  │         "Is this worth Gemma's time?"
  │         → skip / light / standard / deep
  │
  ├──▶ [SEARCH] SearXNG (always, zero cost)
  │         │ "Deep topic?" → + Exa or Tavily (quota-aware)
  │         └──→ sources[]
  │
  ├──▶ [EXTRACT] Firecrawl (deep only, quota-aware)
  │         │ "Map domain" / "Scrape authoritative page"
  │         └──→ markdown content
  │
  ├──▶ [DISTILL] Gemma 4-31B
  │         │ 3-tier refraction: L1 → L2 → L3
  │         │ Triangulation confidence
  │         └──→ gnosis packet
  │
  ├──▶ [CONVERGE?] 
  │         │ 3+ sources agree? → "verified"
  │         │ Contradicted? → "flag for human"
  │         │ Depth ≥ 6? → "converged"
  │         └──→ decision
  │
  ├──▶ [UPDATE] 
  │         │ L3 → soul.yaml (entity)
  │         │ L1+L2 → docs/research/<topic>.md
  │         └──→ knowledge base evolved
  │
  └───▶ [FRONTIER GROWTH]
            │ Adjacent topics discovered → enqueued
            │ New gaps identified → priority boosted
            └──→ queue expanded organically

LAPTOP OFF
  │
  ▼
Last checkpoint saved
  │
  ▼
Resume from checkpoint on next boot
```

---

## §11 Key Files to Reference

| Document | Key Content |
|---------|-------------|
| `docs/research/R_BACKGROUND_RESEARCHER_ARCHITECTURE.md` | Full loop pseudocode, state machine, Gemma prompt, priority algorithm |
| `docs/research/R_SEARXNG_SOVEREIGN_SEARCH_LAYER.md` | Complete Quadlet files, settings.yml, engine list, privacy config, MCP integration |
| `docs/research/R71_knowledge_deepening_verification.md` | Verification cascade, triangulation formula, depth scoring rubric, stale detection |
| `.env` | All 4 search API keys + SearXNG_SECRET |
| `opencode.json` | 5 MCP servers: Exa, Tavily, Firecrawl, Serper, SearXNG, Jina |

---

## §12 Immediate Action Items

1. **Right now**: Deploy SearXNG → `cp docs/research/omega-searxng.* ~/.config/containers/systemd/ && systemctl --user daemon-reload && systemctl --user enable --now omega-searxng.service`
2. **Right now**: Verify all 5 MCPs work in OpenCode (`opencode mcp list`)
3. **This week**: Create `src/omega/workers/background_researcher/loop.py` (the core)
4. **This week**: Create systemd timer for autonomous execution
5. **This week**: Wire Gemma 4-31B distillation prompt

The sovereign researcher is not a future plan. It is the natural evolution of the Omega Engine's mission: to be the living Akashic Record that never stops learning.

⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_sovereign_researcher ⬡ COMPLETE