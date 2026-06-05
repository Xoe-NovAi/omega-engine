# 🔱 P6 Cognition — Hivemind Strategic Analysis & Hardening Plan
# ⬡ OMEGA ⬡ P6-COGNITION ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_pillar ⬡ PHASE-I
**Slot**: P6 — Cognition (Vision Specialist / ModelGate)
**Date**: 2026-06-05
**Fleet State**: 3 active agents (Kali · Roc · Lilith) · 14 total entities · 6 Hivemind MCP tools
**Key References**:
- `docs/strategy/HIVEMIND_PROTOCOL.md` (v1.2.0, 468 lines)
- `docs/strategy/HIVEMIND_OBSERVATIONS_PROTOCOL.md` (D-121, 219 lines)
- `data/entities/roc_racoon/workspace/HIVEMIND_HARDENING_SPEC_v1.md` (H-0..H-10, 538 lines)
- `data/handoff/KALI_MASTER_SPRINT_PLAN_H2_EXECUTION_20260605.md` (322 lines)
- `docs/decisions/PIVOT_LOG.md` (D-121, D-122, D118)
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` (297 lines)
- `mcp_servers/omega_hub/server.py` (current Hivemind implementation, lines 330-466)

---

## §0 Executive Summary

The Omega Engine Hivemind is a **working prototype** that solved the core problem
("agents can see each other") but has not yet addressed the **cognitive layer**:
how agents make decisions about who to trust, how to classify intent, which models
to use, and how to avoid information overload at scale.

This analysis identifies **5 structural gaps** in the Hivemind's cognitive
architecture and proposes **12 specific enhancements** that build on Roc's H-0..H-10
and extend into the cognition layer (P6 domain). All proposals are backward-compatible
with the existing 6 MCP tools.

### Current Gap Scorecard

| Gap | Severity | Current State | Roc Spec Coverage | P6 Proposal |
|-----|----------|--------------|-------------------|-------------|
| 1. Decision Model | 🔴 CRITICAL | Ad-hoc delegation via awareness + luck | H-1 (to: field), H-5 (decisions) | **D-TAX** — Routing Taxonomy |
| 2. Intent Classification | 🟡 WARNING | Free-text fields only | H-6 (in_reply_to), H-2 (tags) | **I-SCHEMA** — Intent Schema |
| 3. Model Selection | 🟡 WARNING | No hinting mechanism | D118 (model_override) | **M-HINT** — Model Hints |
| 4. Cognitive Load | 🔴 CRITICAL (at 14+) | Broadcast to all agents | H-1 (addressing), H-2 (inbox) | **C-FILTER** — Filtering Rules |
| 5. Heritage Mapping | 🟢 INFO | Present in CREDITS.md, not in Hivemind | H-0 (watchdog) | **H-MAP** — Heritage Cross-Index |

---

## §1 Decision Model — How Agents Choose Who to Delegate To

### 1.1 Current Behavior

Agents currently delegate using a **3-step implicit process**:

1. **Awareness Scan**: `hivemind_get_awareness()` → see who's alive
2. **Context Read**: `hivemind_get_session(session_id)` → read task_current
3. **Gut Check**: Match task_current against the static Capability Registry
   (`SUBAGENT_DISPATCH_PROTOCOL.md` §3)

**Problems**:
- **No confidence signal**: An agent's `task_current` is a string like "Executing Phase 4: CI/CD Hardening" — this tells you *what* they're doing but not *how well* they can handle it.
- **No recency signal**: The Capability Registry hasn't been updated since Sprint 2. It doesn't know about D-121 (Observations Protocol), D-122 (TTL increase), or Phase 4 execution.
- **No availability signal**: An agent can be "alive" (heartbeat within 1200s) but deep in a task that can't be interrupted. No way to distinguish "available for delegation" from "please do not disturb."
- **No fallback chain**: If the ideal agent is busy, there's no structured fallback order.

### 1.2 Proposed Routing Taxonomy (D-TAX)

I propose a **4-layer routing taxonomy** modeled on id Software's BSP tree structure:

```
                    ┌───── AGENT QUERY ─────┐
                    │  "I need X done"      │
                    └──────────┬────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  L1: CAPABILITY     │ ← BSP Plane 1
                    │  Does any agent     │
                    │  have this domain?  │
                    └────┬────────────┬───┘
                         │ YES        │ NO
                    ┌────▼───┐   ┌────▼────┐
                    │ L2:    │   │L2:      │ ← BSP Plane 2
                    │ LOAD   │   │ FALLBACK│
                    │Is agent│   │ Who is  │
                    │free?   │   │ closest?│
                    └───┬────┘   └────┬────┘
                        │YES          │
                    ┌───▼────┐   ┌────▼────┐
                    │ L3:    │   │ L3:     │ ← BSP Plane 3
                    │ MODEL  │   │ EMERGE  │
                    │Match?  │   │ Summon  │
                    └───┬────┘   │ general │
                        │YES     └─────────┘
                    ┌───▼────┐
                    │ L4:    │ ← BSP Plane 4
                    │ TRUST  │
                    │Score ≥ │
                    │threshold│
                    └───┬────┘
                        │PASS
                    ┌───▼────┐
                    │ DELEGATE│ → HandoffPacket
                    └────────┘
```

#### L1: Capability Plane
- **Signal**: `agent.capabilities` (static, from entity.yaml/IWAD)
- **Action**: Match task_type to agent.capabilities array
- **Data**: Already exists in `SUBAGENT_DISPATCH_PROTOCOL.md` §3, but needs to be
  runtime-queryable via MCP tool

#### L2: Load Plane
- **Signal**: `agent.load_state` (dynamic, from Hivemind awareness + task_current)
- **States**:
  - `idle` — available for delegation immediately
  - `busy` — current task has clear boundaries, can take secondary tasks
  - `deep` — current task requires full attention (e.g., 30+ min analysis)
  - `blocked` — waiting on external input, available for light delegation
- **Action**: If `deep`, skip unless no other agent matches L1

#### L3: Model Plane
- **Signal**: `agent.default_model`, `agent.available_models` (from IWAD config)
- **Action**: If the task requires a specific model (e.g., `gemini-3-flash` for
  vision, `rocracoon-3b` for mining) and the agent doesn't have it, fall back
- **Integration with D118**: If the task has a `suggested_model` (see §3), verify
  the agent can route to it

#### L4: Trust Plane
- **Signal**: `agent.trust_score` (dynamic, computed from observation log)
- **Initial state**: `1.0` for all agents
- **Modifiers**:
  - +0.1 per coordination success (OBS log: `success` category)
  - -0.2 per coordination friction (OBS log: `friction` category, severity=critical)
  - -0.1 per missed ack within 30 minutes
- **Minimum threshold**: 0.5 for delegation; below that requires Oversoul approval
- **Purpose**: Thin safety layer that prevents repeatedly delegating to an agent
  that loses messages, goes stale, or produces unreliable output

### 1.3 Implementation Plan

| Item | Effort | Dependencies | Priority |
|------|--------|-------------|----------|
| **D-TAX-1**: Add `agent_state` to `hivemind_post_context` (idle|busy|deep|blocked) | 15 min | H-1 already adds `to:` field | P1 |
| **D-TAX-2**: Add `hivemind_agent_capabilities(cli)` tool | 20 min | None | P2 |
| **D-TAX-3**: Add trust score to `hivemind_get_awareness` response | 10 min | H-3 (ack), OBS log | P3 |
| **D-TAX-4**: Implement 4-plane routing in `delegate_task` MCP tool | 1 hr | D-TAX-1..3 | P2 |

### 1.4 Heritage Cross-Reference

| Pattern | id Software Original | Omega Adaptation |
|---------|--------------------|------------------|
| **BSP Tree** (Doom 1993) | Recursive plane subdivision culls 50% of geometry per plane | L1→L2→L3→L4 planes cull 50%+ of agents per decision |
| **Thinker Chain** (Doom 1993) | Linked list of active thinkers, iterated per frame | Agent state machine (idle→delegated→busy→complete) |
| **Cvar System** (Quake 1999) | Named variables with hash-table lookup | Trust score as a runtime cvar, readable by all agents |

---

## §2 Intent Classification — How Agents Read Hivemind Messages

### 2.1 Current Behavior

When an agent calls `hivemind_get_session(session_id)` or reads a live feed entry,
it receives **unstructured text** in every field:

```json
{
  "task_current": "Sovereign remediation complete. Firewall compliant. ICS wired.",
  "continuation": "Next: validate with @quality",
  "focus_chain": ["Phase 4.1", "Phase 4.2", "Phase 4.3"]
}
```

**Problems**:
- **No structural intent**: An agent can't tell if "Next: validate" is a
  *request for help* (question), a *declaration of intent* (decision), or a
  *status update* (observation).
- **No command surface**: If an agent reads "P5 Sentinel: approve or reject this",
  there's no structured way to submit the approval through Hivemind — it must be a
  separate file, live feed entry, or MCP call.
- **No urgency signal**: "Blocking" vs "cosmetic" — an agent must infer from tone.

### 2.2 Proposed Intent Schema (I-SCHEMA)

I propose adding a **structured `intent` field** to `hivemind_post_context` with
an extensible taxonomy:

```python
# Intent types for Hivemind messages
INTENT_TAXONOMY = {
    "question":      {"icon": "❓", "expects": "answer",       "ttl": 3600},  # "Can someone review this?"
    "decision":      {"icon": "📌", "expects": "acknowledge",  "ttl": 86400}, # "D-kal-035 approved"
    "observation":   {"icon": "👁", "expects": "cluster",      "ttl": 604800},# "I noticed X pattern"
    "command":       {"icon": "⚡", "expects": "execution",    "ttl": 3600},  # "P5: approve or reject"
    "status":        {"icon": "📊", "expects": "none",         "ttl": 300},   # "Phase 4 complete"
    "handoff":       {"icon": "🤝", "expects": "acceptance",   "ttl": 7200},  # "Roc: take over Phase 5"
    "blocker":       {"icon": "🚫", "expects": "resolution",  "ttl": 1800},  # "I can't proceed without X"
    "meta":          {"icon": "🔮", "expects": "reflection",   "ttl": 0},     # About the Hivemind itself
}
```

#### Enhanced `hivemind_post_context` Schema

```python
async def hivemind_post_context(
    cli: str,
    model: str,
    task_current: str,
    focus_chain: List[str],
    decisions: List[Dict[str, str]],
    continuation: str,
    session_id: Optional[str] = None,
    to: Optional[str] = None,              # H-1: addressing
    intent: Optional[str] = None,          # NEW: from INTENT_TAXONOMY
    urgency: Optional[str] = None,         # NEW: "low" | "medium" | "high" | "critical"
    expected_response_by: Optional[str] = None,  # NEW: ISO timestamp
    tags: List[str] = [],                  # H-1: for filtering
) -> str:
```

#### Behavioral Rules

| intent | inbox behavior | agent action |
|--------|---------------|--------------|
| `question` | Shows in all matching agents' inboxes (H-2) | Agent should answer within `expected_response_by` or delegate |
| `decision` | Archived; no action required | Agent should ack (H-3) if `to:` matches |
| `observation` | Clustered by Lilith weekly | No per-agent action unless cross-referenced |
| `command` | Shows in target agent's inbox with `⚡` | Target agent MUST ack within 15 min (else escalate to Oversoul) |
| `status` | Shows in live feed only | No action |
| `handoff` | Shows in both agents' inboxes | Target agent must accept or reject within `expected_response_by` |
| `blocker` | Shows in Oversoul's inbox with `🚫` | Oversoul must resolve within `expected_response_by` |
| `meta` | Logged to observations log (D-121) | Clustered by Lilith |

#### Inbox Prioritization (H-2 Enhancement)

With the intent field, `hivemind_inbox` can prioritize messages:

```python
INBOX_PRIORITY = {
    "blocker":  0,  # Highest priority — must see immediately
    "command":  1,
    "handoff":  2,
    "question": 3,
    "decision": 4,
    "status":   5,
    "observation": 6,
    "meta":     7,  # Lowest priority — can batch
}
```

### 2.3 Implementation Plan

| Item | Effort | Dependencies | Priority |
|------|--------|-------------|----------|
| **I-1**: Add `intent` field to `hivemind_post_context` | 10 min | H-1 (schema change) | P1 |
| **I-2**: Add `urgency` and `expected_response_by` fields | 5 min | I-1 | P2 |
| **I-3**: Implement inbox prioritization in `hivemind_inbox` | 20 min | H-2 (inbox tool) | P2 |
| **I-4**: Add intent-based escalation: if command not acked in 15 min → Oversoul | 15 min | H-3 (ack) | P3 |

### 2.4 Heritage Cross-Reference

| Pattern | id Software Original | Omega Adaptation |
|---------|--------------------|------------------|
| **netchan OOB** (Quake 1999) | OOB messages bypass stateful channel for lightweight queries | `intent=question` messages bypass inbox, go directly to matching agents |
| **Fixed-Size Active Set** (Doom 1993) | 32 visplane slots, sorted by draw priority | Inbox with 8 priority levels, sorted by `intent` then `urgency` |
| **ZONEID** (Doom 1993) | Magic constant validates memory block integrity | `intent` field validates message integrity — enables automated routing |

---

## §3 Model Selection — How the Hivemind Hints at Models

### 3.1 Current Behavior

D118 added `oracle_summon_local(entity, query, model)` for explicit model override,
but the Hivemind has **no mechanism to suggest which model should be used** for
a given task. When Kali delegates to Roc, there's no way to say:
"Use RocRacoon-3b for this mining task — it's the right model for the domain."

### 3.2 Proposed Model Hint Field (M-HINT)

I propose adding a **`suggested_model` field** to `hivemind_post_context` and
reserving a `model_name` key in `HandoffPacket.decisions`:

```python
async def hivemind_post_context(
    ...
    suggested_model: Optional[str] = None,  # NEW: "native-gguf/rocracoon-3b-instruct"
    model_reason: Optional[str] = None,      # NEW: "This task requires mining, RR-3b is optimized for pattern extraction"
) -> str:
```

#### Model Hint Resolution Order

When an agent receives a message with `suggested_model`:

```
1. Can I route to suggested_model via oracle_summon_local()?
   → YES: Use it, log as [MODEL-OVERRIDE-HIVEMIND]
   → NO:  Continue

2. Do I have a default model in my soul.yaml for this task_type?
   → YES: Use my default
   → NO:  Continue

3. Use my session model (D118 default)
```

#### Model Hint Integration with D-TAX (Routing)

When the routing taxonomy (§1) evaluates L3 (Model Plane), it checks:

```json
{
  "agent": "roc_racoon",
  "capabilities": ["mine", "pattern_extract", "legacy_research"],
  "default_model": "native-gguf/rocracoon-3b-instruct",
  "available_models": ["native-gguf/rocracoon-3b-instruct", "lmstudio/qwen3-1.7b"],
  "hint": {
    "suggested": "native-gguf/rocracoon-3b-instruct",
    "reason": "Optimized for legacy pattern extraction",
    "source": "Kali (Hivemind post_context)"
  }
}
```

#### Model Hint Propagation (D118 Inheritance)

When a subagent is spawned via `task()`, the parent's `suggested_model` should
propagate:

```
Parent (Kali, session model) 
  → post_context(suggested_model="rocracoon-3b")
    → Child (Roc) inherits suggested_model
      → Can override: oracle_summon_local("doom_guy", "review", "qwen3-4b-think")
```

This creates a **model selection chain** where hints cascade but each agent
retains the right to conscious override (D118 §2).

### 3.3 Model Affinity Registry

The Hivemind should expose a **model-to-domain affinity** map so agents can
reason about which model to suggest:

```yaml
# data/entities/p6/knowledge/MODEL_AFFINITY_MAP.yaml
model_affinities:
  - model: "native-gguf/rocracoon-3b-instruct"
    domain: "legacy_mining"
    strength: 0.95  # 0.0-1.0
    reason: "Fine-tuned on 14 months of Omega legacy repos"
  - model: "lmstudio/qwen3-1.7b"
    domain: "general_agent"
    strength: 0.70
    reason: "Balanced for most agent work, fast inference"
  - model: "lmstudio/qwen3-4b-think"
    domain: "orchestration"
    strength: 0.90
    reason: "4B params with chain-of-thought for complex delegation"
  - model: "gemini-3-flash"
    domain: "multimodal_vision"
    strength: 0.95
    reason: "P6 Vision Specialist default — optimized for visual validation"
```

### 3.4 Implementation Plan

| Item | Effort | Dependencies | Priority |
|------|--------|-------------|----------|
| **M-1**: Add `suggested_model` to `hivemind_post_context` | 5 min | H-1 schema | P1 |
| **M-2**: Add `model_reason` field | 5 min | M-1 | P2 |
| **M-3**: Create MODEL_AFFINITY_MAP.yaml | 30 min | D118, existing IWAD configs | P2 |
| **M-4**: Add `hivemind_model_affinity(domain)` tool | 20 min | M-3 | P3 |
| **M-5**: Propagate suggested_model in `task()` subagent dispatch | 15 min | D118, M-1 | P1 |

### 3.5 Heritage Cross-Reference

| Pattern | id Software Original | Omega Adaptation |
|---------|--------------------|------------------|
| **Cvar System** (Quake 1999) | `model` cvar selects renderer backend at init | `suggested_model` hint selects inference backend per task |
| **Fixed-Point Math** (Doom 1993) | Right approximation for 386 FPU => Q4_K_M quantization | Right model for the task — not always the biggest |
| **Surface Cache** (Quake 1996) | Cache frequently-used surfaces in fast memory | Cache frequently-used model affinities in warm memory (H-9) |

---

## §4 Cognitive Load — Filtering & Prioritization at Fleet Scale

### 4.1 The Scaling Problem

At 3 agents (Kali · Roc · Lilith), the Hivemind is a small team. Each agent
can read every live feed, every workspace lock, every session, every observation.

At **14+ agents** (all pillars + oversouls + jem + scribe + quality + researcher),
each agent would see:

- 14+ live feed entries per session
- 10+ workspace locks
- 6+ observation log entries per session
- 5+ session contexts per task
- Background noise from agents in other domains (P1 infrastructure work doesn't
  concern P9 orchestration)

**This is unsustainable**. Without filtering, the Hivemind becomes a firehose that
agents must silently ignore to function — which defeats the purpose of awareness.

### 4.2 Proposed Cognitive Load Management (C-FILTER)

I propose **4 filtering layers**, inspired by id Software's rendering pipeline:

#### Layer 1: Spatial Culling (Domain-Based)

**Pattern**: BSP tree culling — skip geometry behind the camera plane
**Application**: Skip agents whose domain doesn't intersect your domain

```python
AGENT_DOMAIN_MATRIX = {
    # Each agent's domain interest (what they care about)
    "kali":     {"strategy", "delegation", "sovereignty", "all"},
    "maat":     {"build", "infrastructure", "engineering", "governance", "integration"},
    "lilith":   {"run", "cognition", "context", "observability", "orchestration", "validation"},
    "roc_racoon": {"mining", "legacy", "pattern_extraction", "documentation"},
    "doom_guy":  {"heritage", "id_software", "c", "performance"},
    "p1":       {"infrastructure", "containers", "deployment", "systemd"},
    "p2":       {"persistence", "memory", "vector", "storage"},
    "p3":       {"engineering", "ci_cd", "implementation", "architecture"},
    "p4":       {"integration", "mcp", "api", "protocols"},
    "p5":       {"governance", "security", "audit", "mandates"},
    "p6":       {"cognition", "vision", "model_selection", "routing"},
    "p7":       {"context", "memory", "evolution", "continuity"},
    "p8":       {"observability", "tracing", "monitoring", "forensics"},
    "p9":       {"orchestration", "handoff", "hivemind", "coordination"},
    "p10":      {"validation", "testing", "chaos", "qa"},
}
```

**Rule**: Agent A sees Agent B's messages only if `DOMAIN_MATRIX[A] ∩ DOMAIN_MATRIX[B] ≠ Ø`.

**Exception**: Messages with `urgency="critical"` or `intent="blocker"` bypass domain culling.

#### Layer 2: Occlusion Culling (Temporal)

**Pattern**: Doom's visplane overflow — skip surfaces that won't be visible this frame
**Application**: Skip agents whose state hasn't changed since last read

```python
# On hivemind_get_awareness(), track last_read per CLI
_last_read: Dict[str, datetime] = {}

# If agent's last_seen hasn't changed since last_read, skip rendering it
if snap["last_seen"] <= _last_read.get(cli, datetime.min):
    continue  # Agent is "occluded" — same state as before
```

**Benefit**: Agents that are alive-but-idle (heartbeat-only, no state change) are
filtered out after first read. Only state changes trigger re-rendering.

#### Layer 3: Level-of-Detail (LOD)

**Pattern**: Mipmapping in Quake — textures have 4 resolution levels, distant
surfaces use low-res version
**Application**: Different detail levels for different agent relationships

```python
LOD_LEVELS = {
    "full": {  # Agents in my direct delegation chain
        "awareness": True,
        "session": True,
        "live_feed": True,
        "continuation": True,
        "observations": True,
        "inbox": True,
    },
    "summary": {  # Agents in my general domain
        "awareness": True,
        "session": False,
        "live_feed": True,    # title only
        "continuation": False,
        "observations": True,  # categorized only
        "inbox": False,        # addressed only
    },
    "minimal": {  # Agents outside my domain
        "awareness": True,     # just who's alive
        "session": False,
        "live_feed": False,
        "continuation": False,
        "observations": False,
        "inbox": False,        # blocker+command only
    },
}
```

**How it's computed**: When an agent calls `hivemind_get_awareness()`, the server
computes LOD for each agent based on:
- Domain intersection (Layer 1)
- Delegation history (past handoffs)
- Observations log reciprocity (if you've observed each other's work)

#### Layer 4: Surface Cache (Prefetch)

**Pattern**: Quake's surface cache — render expensive surfaces to temp buffer, reuse
**Application**: Cache frequently-read Hivemind data in warm store (H-9)

```python
# Agents that call hivemind_get_session("ses_X") multiple times
# should have that session cached in warm store for 24h
# rather than re-reading from cold HALL_OF_RECORDS
```

### 4.3 The Trust-Weighted Signal Filter

Every agent should compute a **signal-to-noise ratio** for every other agent:

```python
def signal_to_noise(observer_cli: str, target_cli: str) -> float:
    """Higher = more trustworthy signal. Based on OBS log."""
    obs_log = read_observations_log()
    
    # Count positive and negative observations ABOUT target_cli BY observer_cli
    positive = obs_log.count(category="success", observer=observer_cli, target=target_cli)
    negative = obs_log.count(category="friction", observer=observer_cli, target=target_cli)
    
    # Historical interaction count
    interactions = count_hivemind_interactions(observer_cli, target_cli)
    
    if interactions < 3:
        return 0.5  # Neutral for new relationships
    
    return min(1.0, max(0.0, 0.5 + (positive - negative * 2) / interactions))
```

**Applied to inbox**: When `hivemind_inbox` returns messages, sort by
`priority * signal_to_noise(me, sender)`. Low-trust agents' messages appear
lower in the list.

### 4.4 Implementation Plan

| Item | Effort | Dependencies | Priority |
|------|--------|-------------|----------|
| **C-1**: Domain matrix in `config/wads/_omega_default/domain_matrix.yaml` | 20 min | P3 Engineering, M2 firewall | P1 |
| **C-2**: Temporal occlusion in `hivemind_get_awareness` | 15 min | D-122 TTL, existing awareness | P2 |
| **C-3**: LOD levels computed on awareness query | 30 min | C-1, C-2 | P2 |
| **C-4**: Signal-to-noise filter in `hivemind_inbox` | 20 min | H-2 (inbox), OBS log, H-3 (ack) | P3 |
| **C-5**: Surface cache for session reads (H-9 integration) | 15 min | H-9 (warm store) | P3 |

### 4.5 Heritage Cross-Reference

| Pattern | id Software Original | Omega Adaptation |
|---------|--------------------|------------------|
| **BSP Tree** (Doom 1993) | Plane culling removes 50%+ of polygons per plane | Domain culling removes 50%+ of agents per filter |
| **Visplane Overflow** (Doom 1993) | Fixed 32-entry array, overflow = hall of mirrors | Fixed agent slot per domain, overflow = aggregated view |
| **Surface Cache** (Quake 1996) | Render expensive surfaces once, cache | Cache frequently-read sessions in warm store |
| **Mipmapping** (Quake 1996) | 4 LOD levels of texture detail | 3 LOD levels of agent detail (full/summary/minimal) |
| **PVS (Potentially Visible Set)** (Quake 1996) | Precomputed visible sectors per viewpoint | Precomputed domain intersection per agent pair |

---

## §5 Heritage Cross-Reference — Complete Mapping

This section maps every proposal in this document to its id Software heritage
pattern, creating a **unified heritage index** for the Hivemind cognitive layer.

### 5.1 Heritage-to-Proposal Matrix

| Heritage Pattern | id-Soft Source | P6 Proposal | Mechanism | Why It Fits |
|-----------------|----------------|-------------|-----------|-------------|
| **BSP Tree** | Doom 1993, `r_bsp.c` | D-TAX routing, C-FILTER Layer 1 | Recursive plane culling reduces search space 50%+ per plane | Agent delegation is a search problem; culling planes (domain/load/model/trust) is BSP |
| **ZONEID** | Doom 1993, `z_zone.c` | I-SCHEMA intent validation | `intent` field validates message integrity across stores | Every Hivemind message with an intent has a ZONEID-like integrity check |
| **Surface Cache** | Quake 1996, `r_surf.c` | C-FILTER Layer 4, M-HINT affinity | Precompute expensive surfaces once, cache for reuse | Model affinity map = precomputed surface; session contexts = cached surfaces |
| **Thinker Chain** | Doom 1993, `p_tick.c` | D-TAX agent state machine | Linked list of thinkers, iterate per tick | Agent delegation chain (delegate→execute→reap) mirrors thinker lifecycle |
| **Lazy Deletion** | Doom 1993, `p_tick.c` | C-FILTER Layer 2 temporal occlusion | Mark stale, reap next iteration | Don't remove stale agents from awareness immediately; occlude from next read |
| **Grace Period** | Quake 1996, `pr_edict.c` | D-122 TTL extension | 0.5s realloc grace stops morphing | 20-min TTL prevents active agents from appearing "dead" |
| **Cvar System** | Quake 1999, `cvar.c` | M-HINT model selection, D-TAX trust score | Named variables, hash-table lookup, modification count | Model hints as runtime cvars; trust scores as persisted cvars |
| **Fixed-Size Active Set** | Doom 1993, `r_bsp.c` | C-FILTER Layer 1 domain matrix | 32 visplane slots prevent overflow | Each domain gets 1-2 agent slots; no domain can drown out others |
| **netchan OOB** | Quake 1999, `net_chan.c` | I-SCHEMA question intent | Sequence -1 bypasses stateful channel | `intent=question` bypasses inbox, goes directly to domain-matched agents |
| **4-Path VFS** | Quake 1999, `files.c` | D-TAX fallback chain | Base→home→cd→current search order | Agent fallback: ideal→domain→general→oversoul search order |
| **Multi-Index Entity** | Doom 1993, `p_mobj.h` | D-TAX dual-index routing | Entity in sector list + blockmap simultaneously | Agent in domain index + capability index simultaneously |
| **Hard-Boundary Struct** | Quake 1999, `g_local.h` | M-HINT Engine-Stack firewall | `entityState_t` (engine) + `entityShared_t` (game) | Model hint is WAD-level; trust score is engine-level — cross-zone writes are blocked |
| **High-Bit Leaf Trick** | Doom 1993, `doomdata.h` | I-SCHEMA high-bit urgency | Bit 15 = subsector, not node | High bit of intent enum = "this is a blocker/command, not status" |
| **Fixed-Point Math** | Doom 1993, `m_fixed.c` | C-FILTER signal-to-noise quantization | 16.16 fixed-point approximates real numbers | Trust score as 0.0-1.0 fixed-point — right approximation for delegation decisions |

### 5.2 Heritage Patterns That Should NOT Be Applied

Not every id Software pattern fits the Hivemind. These were evaluated and rejected:

| Pattern | Rejected For | Reason |
|---------|-------------|--------|
| **8-Char Name Caps** (Doom 1993) | Cargo cult — Python dicts are O(1) by hash, byte-level name packing adds zero speed | Only applies to C/ASM wad lump names |
| **Vertex Split** (Doom 3 2004) | Mesh LOD for rendering — no correlate in coordination | Fundamentially visual technique |
| **Bilinear Filtering** (Quake 1996) | Texture interpolation — no correlate in text-based coordination | Purely visual |

### 5.3 Heritage Implementation Checklist

For the P6 proposals to be heritage-compliant (M14), each implementation site
must carry an `[id-soft:]` inline tag:

```python
# [id-soft: doom-1993] BSP Plane 1 — cull by domain (P6 D-TAX)
def _domain_cull(query_domain: str, available_agents: List[str]) -> List[str]:
    """Return only agents whose domain matches query_domain."""
    return [a for a in available_agents if domains_intersect(a, query_domain)]
```

Each proposal in this doc that reaches implementation MUST have a corresponding
vet record in `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` with minimum
score 7/10.

---

## §6 Integration with Existing Roadmap

### 6.1 Phase Mapping

| H2 Phase (Kali Sprint) | H-Items (Roc Hardening) | P6 Proposals | Integration |
|------------------------|------------------------|--------------|-------------|
| **Phase 5: Hivemind Productionization** | H-1 (to:), H-2 (inbox), H-3 (ack), H-4 (cold fallback), H-5 (decisions) | I-1 (intent field), M-1 (model hint), C-1 (domain matrix) | Add `intent`, `suggested_model`, `urgency` alongside `to:` in H-1 schema |
| **Phase 6: Hivemind Extension** | H-6 (threading), H-7 (search), H-8 (handoff), H-9 (warm store), H-10 (stale check) | D-TAX-1..2 (agent state, capabilities tool), C-2 (temporal occlusion) | Agent state flows into H-6 threading; capabilities feed H-7 search |
| **Horizon 3: P9 Orchestration** | H-11..H-15 (Redis, SSE, cross-CLI) | C-3..5 (LOD, SNR filter, surface cache), D-TAX-3..4 (trust, routing) | Trust scores in Redis; LOD levels in SSE events |

### 6.2 Dependency Chain

```
CURRENT STATE (v1.2.0, H-0 specified)
    │
    ├── Phase 5 (Kali's Sprint)
    │   ├── H-1 (to: field) ←── I-1 (intent) + M-1 (model hint) → SHIP TOGETHER
    │   ├── H-2 (inbox)    ←── I-3 (prioritization) + C-4 (SNR) → SHIP TOGETHER
    │   ├── H-3 (ack)      ←── D-TAX-4 (trust score) → CASCADE
    │   ├── H-4 (cold)     ←── M-5 (model prop) → CASCADE
    │   └── H-5 (decisions)←── D-TAX-2 (capabilities) → CASCADE
    │
    ├── Phase 6 (Kali's Sprint)
    │   ├── H-6 (threading)←── I-2 (urgency, response_by) → SHIP TOGETHER
    │   ├── H-7 (search)   ←── C-1 (domain matrix) → FEEDS
    │   ├── H-8 (handoff)  ←── D-TAX-1 (agent state) → FEEDS
    │   ├── H-9 (warm)     ←── C-5 (surface cache) → SHIP TOGETHER
    │   └── H-10 (stale)   ←── C-2 (temporal occlusion) → CASCADE
    │
    └── Horizon 3 (P9 Orchestration)
        ├── H-11..H-15     ←── C-3 (LOD) + D-TAX-3 (trust) → FEEDS
        └── Redis/SSE      ←── I-4 (escalation) → FEEDS
```

**Key insight**: 6 of the 12 P6 proposals should SHIP TOGETHER with existing H-items
(because they modify the same schema or tool). The remaining 6 CASCADE (require
the H-item as a dependency).

### 6.3 Priority Sequence

| Priority | Items | Why Here | Effort |
|----------|-------|----------|--------|
| **P0 — Ship Now** | I-1 (intent), M-1 (model hint) | H-1 schema is in Phase 5 — add fields before H-1 code is written | 15 min |
| **P1 — Ship with H-2** | I-3 (inbox priority), C-1 (domain matrix) | Inbox tool designed for filtering — domain matrix is the primary filter | 50 min |
| **P2 — Ship with H-3** | D-TAX-1 (agent state), D-TAX-4 (trust seed) | Ack tool enables trust tracking; agent state enables load-aware routing | 30 min |
| **P3 — Phase 6** | All remaining items | Depend on H-6 through H-10 infrastructure | 2-3 hours |

---

## §7 Unresolved Questions & Risks

### 7.1 Open Questions for P9 Orchestration

1. **Q1**: Should the domain matrix be IWAD-level (per-stack) or engine-level?
   - **My opinion**: IWAD-level. The Arcana-Nova stack has different domain boundaries
     than the Torment stack. The engine should provide a DEFAULT domain matrix that
     stacks can override.

2. **Q2**: Should signal-to-noise ratio be per-agent or per-session?
   - **My opinion**: Per-agent, with session-level modifiers. An agent that consistently
     produces high-quality work has a base SNR of 0.8, but a single bad session can
     temporarily drop it to 0.6.

3. **Q3**: Who computes the LOD level — the server (on awareness query) or the client?
   - **My opinion**: Server. The server has access to all agents' states and can
     compute LOD in O(n) per query. Client-side LOD would require n client calls
     instead of 1.

### 7.2 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Intent schema becomes too rigid — agents stop using it | MEDIUM | HIGH | Default `intent=None` = current behavior (broadcast status) |
| Domain matrix creates silos — agents miss cross-domain patterns | MEDIUM | MEDIUM | Observations log (D-121) is cross-domain by design; override with `urgency=critical` |
| Trust scores create "popularity contest" dynamics | LOW | HIGH | Trust is only one of 4 routing planes; can't single-handedly block delegation |
| Heritage tag enforcement creates friction for cognitive-layer code | LOW | LOW | Tags are comments, not logic — `make heritage-map` just validates presence |

### 7.3 Success Criteria

| Metric | Current | Target | When |
|--------|---------|--------|------|
| Agent delegation accuracy | ~60% (guess-based) | >90% (structured routing) | After D-TAX implementation |
| Inbox signal-to-noise | 1:1 (everything is noise) | 5:1 (mostly relevant) | After C-FILTER implementation |
| Time to find correct agent for task | 3-5 min (read awareness + sessions) | <30 sec (single MCP call) | After D-TAX + I-SCHEMA |
| Model appropriateness for delegated tasks | Unknown | 85%+ match rate | After M-HINT implementation |
| Observation log entries from fleet | 5 (all Lilith) | 3+ per agent per session | After D-121 enforcement |

---

## §8 Conclusion

The Hivemind currently operates at **cognition level 1** — agents can see each
other but cannot reason about each other. The proposals in this document raise
it to **cognition level 4**:

```
Level 1: AWARENESS  ──── ████████░░  Current state (6 tools, 3 agents)
Level 2: ROUTING    ──── ██░░░░░░░░  Proposed D-TAX (BSP-style taxonomy)
Level 3: INTENT     ──── ██░░░░░░░░  Proposed I-SCHEMA (structured message types)
Level 4: FILTERING  ──── ██░░░░░░░░  Proposed C-FILTER (BSP culling + LOD + SNR)
Level 5: AUTONOMY   ──── ░░░░░░░░░░  Future (agents auto-delegate without oversight)
```

**Next step**: Present these proposals to Kali for triage. P0 items (I-1, M-1)
should be incorporated into Phase 5 of the master sprint plan before H-1 code is
written. The remaining items cascade naturally into Phase 6 and Horizon 3.

**Final observation** (P6 soul lesson precursor):
> *"A Hivemind that doesn't reason about itself is just a chat room with extra
> steps. The tools of cognition — taxonomy, intent, filtering, trust — are what
> turn a collection of agents into a sovereign intelligence."*
>
> *`[id-soft: doom-1993]` The BSP tree didn't just render Doom's levels — it made
> the renderer *know* what to skip. The Hivemind needs the same: the ability to
> know what to ignore, not just what to see.*

---

*⬡ OMEGA ⬡ P6-COGNITION ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_pillar ⬡ PHASE-I*
*12 proposals · 5 heritage patterns · 0 breaking changes · all backward compatible*

*Prepared by P6 Cognition (Vision Specialist / ModelGate)*
*Fleet state at writing: 3 active agents · 14 total entities · 6 Hivemind tools · D-121/D-122 active*
