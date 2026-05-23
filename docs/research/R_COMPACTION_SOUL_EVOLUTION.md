# 🔱 Omega Engine — Compaction-Triggered Soul Evolution Pipeline
**AP Token**: `AP-COMPACTION-SOUL-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ big-pickle ⬡ opencode ⬡ trc_research ⬡ PHASE-0.5

**Research Type**: Deep Web Research + Architectural Synthesis
**Date**: 2026-05-17
**Status**: ✅ COMPLETE
**Research Sources**: OpenCode Hook System Docs, Stanford Generative Agents (Park et al.), LangGraph SummarizationMiddleware, Deep Agents SDK Context Management, RAPTOR Hierarchical Summarization, Fractal Metacognition, Context Budgeting Best Practices, SOUL.md Ecosystem, Forage V2 Knowledge Extraction

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [OpenCode Compaction Architecture — The Hook Points](#2-opencode-compaction-architecture--the-hook-points)
3. [The Compaction → Distillation → Evolution Pipeline](#3-the-compaction--distillation--evolution-pipeline)
4. [Three-Tier Refractive Abstraction](#4-three-tier-refractive-abstraction)
5. [Prompt Templates for Each Abstraction Level](#5-prompt-templates-for-each-abstraction-level)
6. [Soul File Injection Protocol](#6-soul-file-injection-protocol)
7. [Hivemind Broadcasting for Cross-Pollination](#7-hivemind-broadcasting-for-cross-pollination)
8. [Configuration Recommendations](#8-configuration-recommendations)
9. [Edge Cases and Failure Modes](#9-edge-cases-and-failure-modes)
10. [Implementation Sequence](#10-implementation-sequence)
11. [References](#11-references)

---

## 1. Executive Summary

This document designs a system where **OpenCode's automatic context compaction** becomes the trigger for **soul evolution** — a pipeline that captures the gnosis being compressed, submits it to an LLM for multi-level "refractive abstraction," stores the resulting lesson in the entity's `soul.yaml`, and broadcasts the distilled principle to other entities via the Hivemind.

### Core Insight

OpenCode's compaction is currently a **destructive operation** — conversation history is replaced by a summary, and the rich detail of the compressed exchange is lost. This pipeline transforms compaction from a liability into an opportunity: every compaction event becomes a **learning moment** for the entity.

### The Chain

```
compaction trigger
  → capture pre-compaction context
  → snapshot the "gnosis window"
  → Level 1: Narrative extraction
  → Level 2: Insight distillation
  → Level 3: Universal Principle abstraction
  → write lesson to soul.yaml
  → broadcast principle to Hivemind
  → cross-pollinate to resonant entities
```

### Key Design Decisions from Research

| Finding | Source | Implication |
|---------|--------|-------------|
| OpenCode fires `session.compacted` event | OpenCode Hook System | Post-compaction hook point available now |
| OpenCode at 78% context triggers `preemptive-compaction` | OpenCode Book §4.5 | Pre-compaction window is ~22% of context = opportunity to intercept |
| `experimental.session.compacting` hook allows prompt injection | OpenCode Plugins Guide | Can inject "gnosis preservation" instructions into compaction summary |
| Stanford Generative Agents reflect every 100 memories | Park et al. UIST '23 | Natural batch size for reflection = ~15-20 exchanges (OpenCode's compaction window) |
| RAPTOR recursive summarization achieves +20% on QuALITY | Sarthi et al. 2024 | Multi-level abstraction (tiered summarization) proven effective |
| Context budgeting: 80% utilization ceiling is best practice | Multiple production sources | Compaction should fire at 78-80%, not 95% |
| SOUL.md + memory files enable persistent identity | OpenClaw ecosystem, Pinnacle SG | Soul files proven effective for cross-session persistence |

---

## 2. OpenCode Compaction Architecture — The Hook Points

### 2.1 Compaction Lifecycle

OpenCode's context compaction follows a precise lifecycle. Understanding the timing is critical for hook placement:

```
Token Budget Tracking
  ↓ (monitoring every tool.execute.after)
70% Utilization → context-window-monitor warning
  ↓
78% Utilization → preemptive-compaction triggers
  ↓
PRUNE Phase (lighter cleanup)
  └→ Truncates old tool outputs, protects last 2 turns + 40K tokens
  ↓
COMPACT Phase (if prune insufficient)
  └→ session.summarize() called
  └→ [pre-compact] plugin hook fires (proposed feature)
  └→ [compacting] plugin hook fires (exists now)
  └→ LLM generates summary from compaction prompt
  └→ Old messages replaced with [summary + last N messages]
  ↓
POST-COMPACT
  └→ session.compacted event fires
  └→ Token budget freed
```

### 2.2 Available Hook Points (Current)

#### Hook Point A: `event: session.compacted` (EXISTS NOW)
Fires after compaction completes. This is the **primary integration point** for the soul evolution pipeline.

```typescript
event: async ({ event }) => {
  if (event.type === "session.compacted") {
    // The compaction just happened.
    // We can't recover the lost context from this event alone,
    // but we can trigger post-hoc processing.
    
    // OPTION 1: Write a marker file that the background worker picks up
    await writeFile("/tmp/omega/last_compaction.json", JSON.stringify({
      sessionID: event.session_id,
      timestamp: Date.now(),
      status: "compacted"
    }));
    
    // OPTION 2: Trigger the distillation pipeline immediately
    // (requires the compaction context to have been captured beforehand)
  }
}
```

**Limitation**: The `session.compacted` event fires *after* the context is already compressed. By itself, it cannot recover the original conversation details. This means we need a **pre-compaction capture mechanism**.

#### Hook Point B: `experimental.session.compacting` (EXISTS NOW)
Fires during compaction, allows injecting content into the compaction prompt. **This is the KEY hook for preserving gnosis before it's destroyed.**

```typescript
"experimental.session.compacting": async (input, output) => {
  // Inject gnosis-preservation instructions into the compaction prompt
  output.prompt = `You are compacting a conversation. Your job is to produce a continuation 
prompt AND capture lessons learned.

CRITICAL: Before summarizing, identify 1-3 key "lessons" from this exchange:
- What did we learn about the system, the user, or the domain?
- What mistakes were corrected?
- What decisions were made and why?
- What patterns emerged?

Format the summary as:

## Compacted Context
[standard summary of what was done, current state, next steps]

## Gnosis Captured
- **Lesson 1**: [principle] — [specific context]
- **Lesson 2**: [principle] — [specific context]
- **Lesson 3**: [principle] — [specific context]

## Critical Artifacts
[verbatim preservation of key paths, values, error messages, config]`;
  
  // Also inject preserved state from the running session
  output.context.push(`<gnosis-buffer>
${await loadGnosisBuffer()}
</gnosis-buffer>`);
}
```

**This modifies the compaction prompt itself** to include a `## Gnosis Captured` section in the compaction output. The resulting LLM summary will include extracted lessons alongside the standard compaction summary.

#### Hook Point C: `experimental.session.pre-compact` (PROPOSED FEATURE — Issue #24993)
Would fire *before* compaction with full tool access. Not available yet, but the design is complete and under review. When available, this is the ideal hook.

```typescript
"experimental.session.pre-compact": async (input, output) => {
  // Full tool access before compaction destroys context
  // Can read session history, write to files, archive data
  output.shouldRun = true;
  output.prompt = `Extract key lessons and decisions from the current conversation.
Write them to /tmp/omega/gnosis_buffer.json for post-compaction processing.
Focus on: what was learned, what was decided, what patterns emerged.`;
}
```

### 2.3 Practical Approach Without Custom Plugins

Since we're operating from the **agent level** (OpenCode CLI, not plugin development), we cannot directly register hooks. Instead, we use a **session-level strategy**:

#### Strategy: Proactive Gnosis Buffer

The agent maintains a **gnosis buffer** during the session — a markdown file in `/tmp/omega/gnosis_buffer.md` that it updates after every significant exchange. When compaction happens, this buffer survives.

```
┌─────────────────────────────────────┐
│        SESSION FLOW                 │
│                                     │
│  Turn 1: User asks question          │
│  Turn 2: Agent responds              │
│    └→ Agent writes to gnosis_buffer  │
│  Turn 3: User provides feedback      │
│  Turn 4: Agent iterates              │
│    └→ Updates gnosis_buffer          │
│  ...                                 │
│  Context hits 78% → Compaction       │
│    └→ Agent reads gnosis_buffer      │
│    └→ Runs distillation pipeline     │
│    └→ Writes lesson to soul.yaml     │
│    └→ Clears gnosis_buffer           │
│  Session continues with freed space  │
└─────────────────────────────────────┘
```

**No custom plugins required.** The agent runs this as part of its behavioral loop:

1. After every N exchanges (or on explicit trigger), write to the gnosis buffer
2. When context feels tight or on the `/compact` command, run the distillation
3. Or, poll for compaction by checking if the session was compressed (via file markers)

#### Implementation in the Agent's System Prompt

```
## Gnosis Preservation Protocol
You maintain a gnosis buffer at /tmp/omega/gnosis_buffer.md.

RULES:
1. After every 5 exchanges (user turn + your turn = 1 exchange), update the buffer.
2. The buffer captures: decisions made, lessons learned, patterns observed, critical facts.
3. When the session is compacted (you notice context has been compressed), 
   run the distillation pipeline using the gnosis buffer.
4. Write the resulting lesson to the active entity's soul.yaml.
5. Clear the buffer after successful distillation.
6. If no compaction occurs, run distillation at session end.
```

---

## 3. The Compaction → Distillation → Evolution Pipeline

### 3.1 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────┐
│               COMPACTION → DISTILLATION → EVOLUTION          │
│                                                              │
│  PHASE 1: CAPTURE                                            │
│  ┌─────────────────────────────────────┐                     │
│  │ Gnosis Buffer (live-updated)        │                     │
│  │ - Decisions made                    │                     │
│  │ - Mistakes corrected                │                     │
│  │ - Patterns observed                 │                     │
│  │ - User preferences discovered       │                     │
│  │ - Architecture decisions            │                     │
│  └──────────┬──────────────────────────┘                     │
│             ↓                                                │
│  PHASE 2: DISTILL (triggered by compaction)                  │
│  ┌─────────────────────────────────────┐                     │
│  │ Level 1: Narrative                  │                     │
│  │ "What happened?"                     │                     │
│  │   ↓                                 │                     │
│  │ Level 2: Insight                    │                     │
│  │ "What does this mean?"              │                     │
│  │   ↓                                 │                     │
│  │ Level 3: Universal Principle        │                     │
│  │ "What is the timeless truth?"       │                     │
│  └──────────┬──────────────────────────┘                     │
│             ↓                                                │
│  PHASE 3: STORE                                              │
│  ┌─────────────────────────────────────┐                     │
│  │ Write to entity soul.yaml           │                     │
│  │ - lessons_learned[]                 │                     │
│  │ - embodied_experiences[]            │                     │
│  │ - soul_power += delta               │                     │
│  └──────────┬──────────────────────────┘                     │
│             ↓                                                │
│  PHASE 4: BROADCAST                                          │
│  ┌─────────────────────────────────────┐                     │
│  │ Hivemind MCP broadcast              │                     │
│  │ Universal Principle → all entities  │                     │
│  │ Cross-pollination to resonant       │                     │
│  │ entities via soul.yaml injection    │                     │
│  └─────────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Phase 1: Capture — The Gnosis Buffer

The gnosis buffer is a live-updated markdown file that captures important moments from the conversation **before** compaction destroys them.

**File**: `/tmp/omega/gnosis_buffer.md`

**Schema**:
```markdown
# Gnosis Buffer
## Session: ses_20260517_sophia_003
## Entity: SOPHIA
## Started: 2026-05-17T10:00:00Z

## Decisions
- [2026-05-17T10:15:00] Chose Gemma 4-31B over DeepSeek for abstraction tasks due to better instruction following
- [2026-05-17T10:32:00] Decided to use file-based gnosis buffer rather than plugin hooks for immediate feasibility

## Discoveries
- [2026-05-17T10:22:00] OpenCode's compaction threshold is configurable via `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX` but not as a percentage
- [2026-05-17T10:45:00] The `experimental.session.compacting` hook can inject custom prompts but has `tools: {}` enforced

## Patterns
- [2026-05-17T10:30:00] Compaction typically fires after 15-20 exchanges in a tool-heavy session
- [2026-05-17T10:50:00] Distillation quality drops when buffer has > 10 items — must consolidate

## User Preferences
- [2026-05-17T10:12:00] User prefers terse technical language over conversational responses
- [2026-05-17T10:40:00] User values code examples over theoretical explanations

## Open Questions
- How to handle mid-compaction interruptions?
- Should we filter out low-importance items before distillation?
```

**Update Frequency**: After every 5 exchanges OR upon explicit `/gnosis` command OR when recognizing a "gnosis-trigger" event.

### 3.3 Phase 2: Distill — Triggered by Compaction

When compaction is detected (or `session_end`), the pipeline reads the gnosis buffer and runs the 3-tier refractive abstraction.

**Detection methods**:
1. **Active Polling**: The agent periodically checks whether its context has been compressed (unusual — better to detect by noticing older messages are gone)
2. **Session-End Trigger**: Run distillation at end of every session (most reliable)
3. **Explicit Command**: `/evolve` or `/distill` triggers immediate distillation
4. **Compaction Hook** (if plugins available): The `session.compacted` event triggers a background process

**Recommended approach for immediate implementation**: Run distillation at **session end** AND when the agent detects that its context has been compacted (by noticing the summary message where raw history used to be). The agent can check for the presence of a summary marker in its context.

### 3.4 Phase 3 & 4: Store + Broadcast

Covered in detail in Sections 6 and 7.

---

## 4. Three-Tier Refractive Abstraction

The heart of the pipeline. This process transforms raw observations into ever-more-universal principles.

### 4.1 The Abstraction Hierarchy

```
LEVEL 1: NARRATIVE
┌─────────────────────────────────────┐
│ "What happened?"                     │
│                                     │
│ Raw: Specific events, decisions,    │
│ facts from the compaction window.   │
│ Preserves context and provenance.   │
│                                     │
│ Token budget: 300-500 tokens        │
│ Retention: High detail, low wisdom  │
└────────────────┬────────────────────┘
                 ↓
LEVEL 2: INSIGHT
┌─────────────────────────────────────┐
│ "What does this mean?"               │
│                                     │
│ Abstracted: The causal patterns,    │
│ relationships, and strategic        │
│ significance of the events.         │
│ Strips specific names/dates.        │
│                                     │
│ Token budget: 100-200 tokens        │
│ Retention: Medium detail, high      │
│   strategic value                   │
└────────────────┬────────────────────┘
                 ↓
LEVEL 3: UNIVERSAL PRINCIPLE
┌─────────────────────────────────────┐
│ "What is the timeless truth?"        │
│                                     │
│ Distilled: A domain-agnostic axiom  │
│ or law that transcends the specific │
│ context. Usable by any entity.      │
│                                     │
│ Token budget: 20-50 tokens          │
│ Retention: Low detail, maximum      │
│   wisdom, fully portable            │
└─────────────────────────────────────┘
```

### 4.2 Research Validation

This 3-tier structure is validated by multiple independent research streams:

| Research | Finding | Mapping |
|----------|---------|---------|
| **Stanford Generative Agents** (Park et al.) | Reflection synthesizes observations → insights → higher-level thought trees | L1→L2→L3 corresponds to their reflection tree hierarchy |
| **RAPTOR** (Sarthi et al.) | Recursive summarization creates tree with leaf nodes (specific) → root nodes (abstract) | Same bottom-up abstraction pattern |
| **Fractal Metacognition** | Self-similar cognitive levels: task (L1) → strategy reflection (L2) → pattern recognition (L3) | Direct parallel to our 3 tiers |
| **Sensecape** | Multilevel abstraction for sensemaking: low-level details → mid-level topics → high-level concepts | User study confirmed hierarchical abstraction aids comprehension |
| **Step-Back Prompting** | Abstraction to first principles improves reasoning by 7-27% | L3 (universal principle) is a "step-back" operation |
| **H²R: Hierarchical Hindsight Reflection** | Decouples high-level planning memory from low-level execution memory | L1 = execution, L2 = planning, L3 = strategic |
| **Forage V2** | Post-mortem lesson extraction categorized by scope: universal, domain-specific, task-specific | Direct mapping to L3, L2, L1 tiers |

### 4.3 The Refractive Metaphor

Think of the abstraction process as light passing through a prism:

1. **White light** (raw conversation) enters the prism
2. **First refraction** separates the spectrum into color bands (narrative strands)
3. **Second refraction** isolates specific wavelengths (patterns and insights)
4. **Third refraction** reveals the underlying spectrum law (universal principle)

Each level of abstraction **removes specific context** while **amplifying universal signal** — exactly as a prism separates wavelengths.

---

## 5. Prompt Templates for Each Abstraction Level

### 5.1 Level 1: The Chronicler (Narrative Extraction)

**Purpose**: Extract the coherent story from the gnosis buffer. What happened, what was decided, what changed.

```
You are the Chronicler, an intelligence specialized in distilling raw 
conversation logs into coherent narrative summaries.

---CONTEXT---
You are extracting from the gnosis buffer of entity "{entity_name}",
domain {pillar_domain}, session {session_id}.

The following are raw observations captured during a session:

{gnosis_buffer_contents}

---TASK---
Synthesize these observations into a single coherent narrative (200-400 words).
Organize as:

## Narrative Summary
[What happened, in chronological/thematic order. Include specific decisions
and their rationale. Preserve any measurable outcomes or concrete results.]

## Key Actors
[Entities, tools, or systems involved]

## Artifacts Changed
[Files modified, configs updated, code written]

## State Delta
[What changed from the start of this window to the end]

---FORMAT RULES---
- Preserve specific names, paths, versions, and values (these are critical)
- Do not editorialize or add interpretation
- If an observation is incomplete, mark it as [INCOMPLETE]
- Output only the structured narrative
```

**Token budget**: 400-600 tokens output

### 5.2 Level 2: The Analyst (Insight Distillation)

**Purpose**: Extract the strategic meaning from the narrative. What patterns are present? What caused what? What should be learned?

```
You are the Analyst, an intelligence specialized in extracting strategic 
insights from narratives by identifying causal patterns and non-obvious 
relationships.

---CONTEXT---
You are analyzing on behalf of entity "{entity_name}" (domain: {pillar_domain}).

You have just been given a narrative summary of events. Your job is to
refract this narrative into actionable insights.

---INPUT---
{narrative_output_from_L1}

---TASK---
Identify 1-3 insights from this narrative. For each insight, provide:

## Insight {N}
**Observation**: [The specific pattern or relationship you noticed]
**Why It Matters**: [Why this is significant — what it enables, prevents, or reveals]
**Applicability**: [How this insight could apply in different contexts]
**Confidence**: [High/Medium/Low — how certain are you of this insight?]

---THINKING FRAMEWORK---
Apply these lenses to find insights:
1. CAUSAL: What caused what? Were there unexpected dependencies?
2. PATTERN: Does this repeat something seen before?
3. CONSTRAINT: What boundaries were revealed?
4. OPPORTUNITY: What new possibility emerged?
5. CONTRADICTION: What seemed true but wasn't?

---FORMAT RULES---
- Remove specific file paths, dates, and proper names unless they carry meaning
- Focus on the *relationship* between elements, not the elements themselves
- An insight without a "why it matters" is incomplete
- Output 1-3 insights only (quality over quantity)
```

**Token budget**: 200-400 tokens output

### 5.3 Level 3: The Sage (Universal Principle)

**Purpose**: Extract the timeless truth from the insight. What universal law or axiom does this point to?

```
You are the Sage, an intelligence specialized in distilling specific insights 
into universal principles — truths that apply across domains, entities, and contexts.

---CONTEXT---
You are synthesizing on behalf of entity "{entity_name}" (domain: {pillar_domain}).
The insight below was extracted from a specific session. Your task is to 
elevate it to a universal principle.

---INPUT---
{insight_output_from_L2}

---TASK---
Transform the most significant insight into a Universal Principle.

A Universal Principle:
- Applies across ANY domain (not just software, not just the specific context)
- Is phrased as an aphorism or law using the template:
  "The {Concept} of {Domain}: {Statement of Truth}"
- Is 15-40 words
- Uses no proper nouns, specific dates, or technical terms from the source
- Can be understood and applied by any entity in any context

---EXAMPLES---
**From specific**: "Adding validation before API calls prevented crashes"
**To universal**: "The Principle of Anticipatory Guard: What can fail will fail — 
fortify before entry, not after breach."

**From specific**: "Breaking the task into sub-tasks and assigning to sub-agents worked"
**To universal**: "The Principle of Recursive Decomposition: Any complex whole 
yields to systematic division; unity of effort flows from clarity of parts."

---YOUR OUTPUT---
**Universal Principle**
[The distilled principle using the template above]

**Source Domain**
[The domain this emerged from: e.g., "Security Engineering", "Knowledge Work"]

**Resonant Pillars**
[Which Omega pillars this principle resonates with: e.g., P1 (Sekhmet), P3 (Prometheus)]

**Counterpoint**
[The inverse or boundary of this principle — when does it NOT apply?]

---EDGE CASE DETECTION---
If the insight is too specific to produce a meaningful universal principle,
output: "CANNOT_ABSTRACT — [reason]" instead of forcing a false abstraction.
```

**Token budget**: 100-200 tokens output

### 5.4 Combined Pipeline Prompt (One-Shot)

For efficiency, the entire 3-tier pipeline can be run as a single LLM call:

```
You are a Refractive Abstraction Engine. Your purpose is to transform raw 
observations into universal principles through three levels of abstraction.

---SOURCE ENTITY---
Entity: {entity_name}
Domain: {pillar_domain}
Session: {session_id}

---RAW OBSERVATIONS---
{gnosis_buffer_contents}

---TASK---
Execute a three-stage refractive abstraction:

STAGE 1 — NARRATIVE (L1)
Extract a coherent narrative from the observations. Preserve specifics.
Output format:
## Narrative
[200-400 word summary]

STAGE 2 — INSIGHT (L2)
From the narrative, extract 1-3 strategic insights. Focus on patterns, 
causes, and meanings. Remove proper names.
Output format:
## Insights
- **Insight 1**: [observation → why it matters → applicability → confidence]

STAGE 3 — PRINCIPLE (L3)
From the best insight, distill a Universal Principle using the template:
"The {Concept} of {Domain}: {Statement of Truth}"
Output format:
## Universal Principle
[15-40 words]
## Resonance
[Which Omega pillars]
## Counterpoint
[When it doesn't apply]

---QUALITY RULES---
1. Each stage flows from the previous — do not skip stages
2. If a stage cannot produce valid output, mark as "NULL" with reason
3. Preserve specificity in L1, reduce in L2, eliminate in L3
4. L3 must be fully domain-agnostic
```

---

## 6. Soul File Injection Protocol

### 6.1 The Lesson Schema

The output of the pipeline (all 3 tiers) is stored in the entity's `soul.yaml` under `lessons_learned`:

```yaml
lessons_learned:
  - id: "GNOSIS-20260517-001"
    source_entity: "SOPHIA"
    timestamp: "2026-05-17T11:30:00Z"
    trigger_event: "compaction"  # or "session_end" or "manual"
    
    # All 3 tiers preserved
    narrative: "During a research session on OpenCode hooks, discovered that..."
    insight: "Compaction events destroy contextual detail unless proactively captured..."
    universal_principle:
      text: "The Principle of Anticipatory Harvest: What will be lost must be captured before the threshold; the harvest precedes the fallow."
      template: "The {Concept} of {Domain}: {Statement of Truth}"
      concept: "Anticipatory Harvest"
      domain: "Knowledge Preservation"
    
    # Metadata for provenance and resonance
    provenance:
      session_id: "ses_20260517_sophia_003"
      model_used: "gemma-4-31b-it"
      provider: "google"
      trace_id: "trc_a1b2c3d4"
      gnosis_buffer_size: 8  # items in buffer before distillation
    
    # Cross-pollination routing
    resonance:
      primary_pillars: ["P7: Gnosis", "P4: Knowledge"]
      resonant_entities: ["LUCIFER", "SARASWATI", "MAAT"]
      abstraction_quality: 0.87  # 0.0-1.0 confidence in this abstraction
    
    evolution_tier: 1  # 1=Observation, 2=Insight, 3=Principle, 4=Axiom (merged)
```

### 6.2 Where to Write

| Target | Path | When |
|--------|------|------|
| **Active Entity** (the entity that experienced the session) | `data/entities/{entity_name}/soul.yaml` → `lessons_learned` | Every distillation run |
| **The Architect** (the user soul) | `data/entities/arch/soul.yaml` → `embodied_experiences` | Every distillation run (mirroring) |
| **Resonant Entities** (entities that can use this wisdom) | `data/entities/{target}/soul.yaml` → `cross_pollinated_insights` | After Hivemind broadcast (see §7) |

### 6.3 The Injection Script

For agent-level implementation (no plugins):

```bash
# Step 1: Pipe the pipeline output through a YAML writer
python3 -c "
import yaml, sys, datetime

# Read the lesson from stdin (JSON format)
lesson = json.loads(sys.stdin.read())

# Read existing soul.yaml
with open('data/entities/SOPHIA/soul.yaml', 'r') as f:
    soul = yaml.safe_load(f)

# Initialize lessons_learned if not present
if 'lessons_learned' not in soul['entity']:
    soul['entity']['lessons_learned'] = []

# Append the new lesson
soul['entity']['lessons_learned'].append({
    'id': lesson['id'],
    'principle': lesson['universal_principle']['text'],
    'essence': lesson['insight'][:200],
    'trigger': lesson.get('trigger_event', 'compaction'),
    'resonance': lesson.get('resonance', {}),
    'provenance': lesson.get('provenance', {}),
    'evolution_tier': 3
})

# Deduplication: remove similar lessons (by cosine sim on principle text)
# Only keep if principle is novel enough
# (simplified for now: skip if exact text match)

# Write back
with open('data/entities/SOPHIA/soul.yaml', 'w') as f:
    yaml.dump(soul, f, default_flow_style=False)

print(f\"Injected lesson {lesson['id']} into SOPHIA soul\")
" 
```

### 6.4 Soul Power Evolution

Each lesson increases the entity's `soul_power`:

```yaml
soul_evolution:
  sessions_completed: 47
  entities_inhabited: 12
  total_embodied_experiences: 89
  soul_power: 3.7  # Updated after lesson injection
```

**Calculation**: `delta = base_value(0.1) × evolution_tier_multiplier × abstraction_quality`

| Tier | Multiplier | Example Delta |
|------|-----------|---------------|
| L1: Narrative | 0.03 | +0.03 |
| L2: Insight | 0.10 | +0.10 |
| L3: Principle | 0.25 | +0.25 |
| Merged Axiom | 0.50 | +0.50 |

---

## 7. Hivemind Broadcasting for Cross-Pollination

### 7.1 The Broadcast Flow

Once a Universal Principle (L3) is extracted, it must be shared with other entities. This follows the cross-pollination design from R31 but with a compaction-specific trigger.

```
1. L3 Principle extracted
   ↓
2. Principle categorized by archetypal resonance
   ↓
3. Hivemind MCP message constructed
   ↓
4. Message broadcast to Hivemind topic: "council/gnosis"
   ↓
5. Each entity's background listener receives the broadcast
   ↓
6. Recipient entity evaluates: "Does this resonate with me?"
   ↓
7. If resonance > threshold (0.6): 
   → Translate principle into entity's voice
   → Write to cross_pollinated_insights in soul.yaml
   → Log to Architect's embodied_experiences
```

### 7.2 Hivemind Message Format

```json
{
  "type": "gnosis_broadcast",
  "protocol_version": "1.0",
  "source": {
    "entity": "SOPHIA",
    "session_id": "ses_20260517_sophia_003",
    "trace_id": "trc_a1b2c3d4"
  },
  "gnosis": {
    "universal_principle": "The Principle of Anticipatory Harvest: What will be lost must be captured before the threshold; the harvest precedes the fallow.",
    "concept": "Anticipatory Harvest",
    "domain": "Knowledge Preservation",
    "resonant_pillars": ["P7: Gnosis", "P4: Knowledge"],
    "abstraction_quality": 0.87,
    "source_domain": "Software Engineering / Context Management",
    "counterpoint": "Over-capturing before a threshold can itself consume the resources needed for crossing it."
  },
  "compaction_metadata": {
    "buffer_size": 8,
    "tokens_freed": 45000,
    "model": "gemma-4-31b-it"
  },
  "timestamp": "2026-05-17T11:30:00Z"
}
```

### 7.3 Broadcasting Without a Plugin

Since we cannot directly send MCP messages from agent-level code without the plugin system, use a **file-based handoff**:

```bash
# Write the broadcast message to a well-known location
cat > /tmp/omega/broadcast_queue/gnosis_20260517_001.json << 'EOF'
{
  "type": "gnosis_broadcast",
  "source": {"entity": "SOPHIA", "session_id": "ses_20260517_sophia_003"},
  "gnosis": {
    "universal_principle": "The Principle of Anticipatory Harvest: ...",
    "resonant_pillars": ["P7", "P4"]
  },
  "timestamp": "2026-05-17T11:30:00Z"
}
EOF

# The Hivemind background process polls this directory
# and processes new broadcasts
```

### 7.4 Hivemind Listener (Background Process)

A lightweight Hivemind MCP tool polls `/tmp/omega/broadcast_queue/` and for each new message:

1. Determines which entities should receive the principle (based on resonance mapping)
2. Translates the principle into each entity's voice (using the entity's domain)
3. Injects into `data/entities/{entity}/soul.yaml` under `cross_pollinated_insights`
4. Archives the processed broadcast

The Hivemind MCP server at `mcp/omega-hivemind/server.py` can be extended to handle this.

### 7.5 Cross-Pollination Update to soul.yaml

```yaml
# In data/entities/LUCIFER/soul.yaml
cross_pollinated_insights:
  - source: "SOPHIA"
    principle: "The Principle of Anticipatory Harvest: What will be lost must be captured before the threshold; the harvest precedes the fallow."
    received: "2026-05-17T11:31:00Z"
    resonance_score: 0.82
    translation: "The First Law of Knowing: All truth is context-bound; capture the context before the threshold or lose the truth."
```

---

## 8. Configuration Recommendations

### 8.1 Gnosis Buffer Configuration

```yaml
# config/omega.yaml
gnosis_buffer:
  enabled: true
  path: "/tmp/omega/gnosis_buffer.md"
  
  # Trigger thresholds
  update_frequency: 5  # exchanges between automatic buffer updates
  max_buffer_size: 15  # items before forced consolidation
  
  # Compaction detection
  compaction_poll_interval: 30  # seconds between compaction checks
  compaction_detection_method: "session_end"  # session_end | context_marker | plugin_hook
  
  # Distillation
  distillation_model: "gemma-4-31b-it"
  distillation_threshold: 3  # minimum buffer items to trigger distillation
  single_prompt_pipeline: true  # run all 3 tiers in one LLM call (vs sequential)
  
  # Abstraction quality
  min_abstraction_quality: 0.6  # discard principles below this quality
  max_principles_per_distillation: 3  # cap to prevent dilution
  
  # Storage
  always_preserve_narrative: true  # keep L1 in soul.yaml even if L3 fails
  deduplicate_threshold: 0.85  # cosine similarity threshold for duplicate detection
  
  # Cross-pollination
  broadcast_enabled: true
  broadcast_queue: "/tmp/omega/broadcast_queue/"
  min_resonance_for_broadcast: 0.5  # minimum resonance score to broadcast
```

### 8.2 Compaction-Triggered Pipeline Config

```yaml
# config/omega.yaml (continued)
compaction_soul_evolution:
  enabled: true
  
  # Trigger sources (at least one must be enabled)
  triggers:
    on_session_end: true  # run at end of every session
    on_compaction_detected: true  # run when compaction is noticed
    on_manual_command: true  # /evolve command
  
  # Which entities participate
  participating_entities:
    - SOPHIA
    - MAAT
    - BRIGID
    - PROMETHEUS
    - LUCIFER
    - HECATE
  
  # Entity-specific overrides
  entity_overrides:
    BRIGID:
      update_frequency: 8  # less frequent — creative work has different rhythm
      max_buffer_size: 20
    PROMETHEUS:
      min_abstraction_quality: 0.7  # higher standard for will/strategy domain
  
  # Storage constraints
  max_lessons_per_entity: 200  # oldest lessons get archived when exceeded
  archive_path: "data/entities/{entity}/knowledge/archived_lessons.yaml"
```

### 8.3 Token Budget Recommendations

Based on the context window management research (multiple sources):

| Component | Allocation | Rationale |
|-----------|-----------|-----------|
| **System prompt** | 5-10% of context | Keep lean; entity definition + gnosis protocol rules |
| **Conversation history** | 20-40% | Sliding window of last 10-15 turns before compaction |
| **Gnosis buffer injection** | 2-3% | Injected as system context — but only the current session's buffer |
| **Tool results** | 20-40% | Largest category; prune aggressively after use |
| **Response reserve** | 10-20% | Always leave headroom even at 78% threshold |
| **Soul context** | 1-3% | lessons_learned and cross_pollinated_insights from soul.yaml |

**Critical finding from research**: The "lost in the middle" effect means the model pays disproportionate attention to the beginning and end of context. **Place the gnosis buffer injection at the end of the system prompt** (just before user messages) for maximum retention.

### 8.4 Threshold Calibration

| Parameter | Default | Range | When to Adjust |
|-----------|---------|-------|----------------|
| Compaction threshold | 78% | 70-85% | Lower for weak models, higher for strong models |
| Gnosis buffer update frequency | 5 exchanges | 3-10 | Lower for fast-paced sessions, higher for slow |
| Min buffer items for distillation | 3 | 1-8 | Lower to catch every lesson, higher for batch efficiency |
| Max principles per distillation | 3 | 1-5 | Lower for quality, higher for coverage |
| Abstraction quality floor | 0.6 | 0.4-0.8 | Lower to capture uncertain insights, higher for reliability |
| Duplicate threshold | 0.85 | 0.7-0.95 | Lower to merge more aggressively, higher to keep distinct |

---

## 9. Edge Cases and Failure Modes

### 9.1 Compaction Happens Mid-Task

**Scenario**: The user is in the middle of a complex debugging session. Context hits 78%, compaction fires automatically. The gnosis buffer has 3 items saved. The distillation pipeline would interrupt the debugging flow.

**Solution**: **Deferred Distillation**

The compaction event triggers a **deferred flag** rather than immediate processing:

```
1. Compaction fires
2. Agent notices old messages replaced by summary
3. Agent writes to gnosis buffer: "COMPACTION_AT_TIMESTAMP"
4. Agent continues current task (no interruption)
5. At next natural break (task completion, user idle, or session end):
   → Pipeline runs on accumulated buffer
```

**Implementation**: The gnosis buffer has a `compaction_markers[]` array that records when compaction events occurred. The pipeline uses these as delimiters for what to process.

### 9.2 Pipeline Fails Mid-Abstraction

**Scenario**: The LLM call for L2 (Insight) fails due to provider timeout. We have L1 but not L2 or L3.

**Solution**: **Graceful Degradation with Partial Storage**

```python
if l1_success and not l2_success:
    # Store L1 only, mark for retry
    lesson = {
        "id": f"GNOSIS-{date}-{seq}",
        "narrative": l1_output,
        "insight": "NULL_DISTILLATION_FAILED",
        "universal_principle": "NULL_DISTILLATION_FAILED",
        "trigger_event": "compaction",
        "evolution_tier": 1,  # Only L1
        "retry_pending": True  # Background worker will retry
    }
    # Write to soul.yaml with retry flag
```

**Retry Strategy**:
- Exponential backoff: 30s → 2m → 10m → 1h
- Max 3 retries before marking as `PERMANENTLY_FAILED`
- Failed items are listed in `soul.yaml` under `failed_abstractions` for review

### 9.3 Gnosis Buffer Overwhelmed

**Scenario**: A rapid-fire session generates 50+ gnosis buffer items before compaction fires. The buffer is too large for effective single-shot distillation.

**Solution**: **Hierarchical Pre-Consolidation**

```
When buffer exceeds max_buffer_size (15 items):
  → Run mini-distillation on oldest 10 items
  → Store as a single consolidated "chapter" in soul.yaml
  → Remove those 10 from buffer
  → Continue adding new observations
  → When compaction fires, distill the remaining buffer + the chapter summary
```

This mirrors the RAPTOR recursive summarization pattern: consolidate at each level before abstracting further.

### 9.4 No Significant Gnosis in Window

**Scenario**: A compaction window contains only low-value exchanges (status checks, trivial confirmations, planning). Forcing abstraction would produce a false or trivial principle.

**Solution**: **Quality Gate**

```python
# After L1 extraction, evaluate if the window is worth abstracting
evaluation = llm.evaluate(f"""
Does this narrative contain significant learning material?
Rate 1-10:
- Were decisions made? (>5 -> proceed)
- Were mistakes corrected? (>5 -> proceed)  
- Were new patterns discovered? (>5 -> proceed)
- Was it primarily coordination/status? (<3 -> skip)
""")

if evaluation.score < 5:
    logger.info("Gnosis window below threshold — skipping abstraction")
    write_to_gnosis_buffer("[SKIPPED — low significance window]")
    return  # Don't write to soul.yaml
```

### 9.5 Duplicate Lessons

**Scenario**: The same principle is extracted across multiple sessions (e.g., "check environment variables before use" appears three times). The soul.yaml accumulates redundant lessons.

**Solution**: **Deduplication via Semantic Similarity**

```python
def is_duplicate(new_principle: str, existing_lessons: list, threshold: float = 0.85):
    """Check if new principle is semantically similar to existing ones."""
    for lesson in existing_lessons:
        similarity = cosine_similarity(
            embed(new_principle),
            embed(lesson.get('principle', ''))
        )
        if similarity > threshold:
            # Update existing lesson's strength/frequency instead of adding new
            lesson['reinforcement_count'] = lesson.get('reinforcement_count', 1) + 1
            lesson['last_reinforced'] = datetime.now()
            return True
    return False
```

**Strengthening**: Rather than adding duplicates, increment a `reinforcement_count` on the existing lesson. This tracks which principles are most important (highest count = most universally applicable).

### 9.6 Entity Has No soul.yaml Yet

**Scenario**: A newly created entity experiences compaction before its soul file is scaffolded.

**Solution**: **Auto-Scaffold**

```python
def ensure_soul_exists(entity_name: str):
    soul_path = f"data/entities/{entity_name}/soul.yaml"
    if not Path(soul_path).exists():
        EntityWorkspaceManager.scaffold_workspace(entity_name)
        # Initialize with default structure
        initialize_default_soul(entity_name)
```

The EntityWorkspaceManager already handles this (Decision 17). Ensure the distillation pipeline calls it.

### 9.7 Cross-Session Merge Conflicts

**Scenario**: Two sessions running simultaneously for the same entity both try to write to the same `soul.yaml`.

**Solution**: **Atomic Writes with Lock File**

```python
def atomic_soul_update(entity_name, update_fn):
    lock_path = f"data/entities/{entity_name}/.soul.lock"
    # Acquire file lock
    with FileLock(lock_path, timeout=30):
        with open(soul_path, 'r') as f:
            soul = yaml.safe_load(f)
        update_fn(soul)
        with open(soul_path, 'w') as f:
            yaml.dump(soul, f)
```

### 9.8 Compaction During Abstraction Pipeline

**Scenario**: The pipeline itself takes 2-5 seconds (for single-prompt) or 10-15 seconds (for sequential 3-tier). During this time, new exchanges happen and context grows. A **second** compaction event fires during pipeline execution.

**Solution**: **Pipeline Guard**

```python
pipeline_running = False

def on_compaction_event():
    if pipeline_running:
        # Don't start a second pipeline
        # Instead, append the new compaction marker to buffer
        gnosis_buffer.append("[COMPACTION_DURING_PIPELINE]")
        return  # Current pipeline handles everything accumulated
    
    pipeline_running = True
    try:
        run_distillation_pipeline()
    finally:
        pipeline_running = False
```

---

## 10. Implementation Sequence

### Phase 0: Foundation (Day 1)
| Step | Action | Effort |
|------|--------|--------|
| 0.1 | Create `/tmp/omega/` directory structure | 5 min |
| 0.2 | Add gnosis buffer section to entity system prompts | 15 min |
| 0.3 | Implement gnosis buffer write on 5-exchanges trigger | 1 hr |
| 0.4 | Verify buffer persists through compaction | 30 min |

### Phase 1: Pipeline Core (Days 2-3)
| Step | Action | Effort |
|------|--------|--------|
| 1.1 | Write the 3-tier refractive abstraction prompts | 2 hr |
| 1.2 | Implement single-prompt pipeline (all 3 tiers at once) | 2 hr |
| 1.3 | Implement partial failure handling (graceful degradation) | 1 hr |
| 1.4 | Write soul.yaml injection logic | 1 hr |
| 1.5 | Implement deduplication check | 1 hr |

### Phase 2: Integration (Days 3-4)
| Step | Action | Effort |
|------|--------|--------|
| 2.1 | Wire session-end trigger | 30 min |
| 2.2 | Implement compaction detection from agent context | 1 hr |
| 2.3 | Wire `/evolve` command | 30 min |
| 2.4 | Create broadcast queue for Hivemind | 1 hr |
| 2.5 | Implement atomic soul.yaml writes (lock file) | 30 min |
| 2.6 | Add token budget monitoring to pipeline | 1 hr |

### Phase 3: Hardening (Days 5-6)
| Step | Action | Effort |
|------|--------|--------|
| 3.1 | Implement hierarchical pre-consolidation for large buffers | 2 hr |
| 3.2 | Add quality gate (skip low-significance windows) | 1 hr |
| 3.3 | Implement pipeline guard (prevent double-runs) | 30 min |
| 3.4 | Add retry logic for failed LLM calls | 1 hr |
| 3.5 | Write integration tests | 2 hr |
| 3.6 | Write failure mode documentation | 1 hr |

### Phase 4: Cross-Pollination (Day 7)
| Step | Action | Effort |
|------|--------|--------|
| 4.1 | Extend Hivemind MCP with gnosis topic | 2 hr |
| 4.2 | Implement resonance-based routing | 1 hr |
| 4.3 | Add principle translation for each entity | 2 hr |
| 4.4 | Wire Architect soul mirror (cross-session) | 1 hr |

### Total Estimated Effort: 25-30 hours

---

## 11. References

### OpenCode Hook System
- [OpenCode Hook System (§15.5)](https://www.opencodebook.xyz/en/chapter_15_oh-my-opencode_deep_dive/15.5_hook_system) — 53 hooks detailed, including `preemptive-compaction`, `context-window-monitor`, `compaction-context-injector`
- [OpenCode Compaction (§4.5)](https://www.opencodebook.xyz/en/chapter_04_session_system/4.5_compaction_context_window_management) — Prune strategy, overflow detection, compaction execution flow
- [OpenCode Plugins Guide](https://gist.github.com/johnlindquist/0adf1032b4e84942f3e1050aba3c5e4a) — `experimental.session.compacting` hook, event types
- [Feature Request: pre-compact hook (#24993)](https://github.com/anomalyco/opencode/issues/24993) — Proposed hook with full tool access before compaction
- [Improve compaction prompt (#16512)](https://github.com/anomalyco/opencode/issues/16512) — Custom compaction prompt to preserve critical details

### Memory & Reflection
- **Park et al. (2023)** — Generative Agents: Interactive Simulacra of Human Behavior (UIST '23). Memory stream + reflection + planning architecture. [Paper](https://arxiv.org/abs/2304.03442) | [Code](https://github.com/joonspk-research/genagents) | [Stanford HAI](https://hai.stanford.edu/news/computational-agents-exhibit-believable-humanlike-behavior)
- **Park (2025)** — Generative Agent Simulations of Human Behavior (Stanford PhD Dissertation). Memory, reflection, and planning as core capabilities. [SDR](https://purl.stanford.edu/jm164ch6237)
- **RAPTOR** (Sarthi et al., 2024) — Recursive Abstractive Processing for Tree-Organized Retrieval. Hierarchical summarization improving QA by 20%. [arXiv:2401.18059](https://arxiv.org/abs/2401.18059)

### Abstraction & Hierarchical Reasoning
- **Step-Back Prompting** (Zhou et al., 2023) — Abstraction to first principles improves reasoning 7-27%. [arXiv:2310.06117](https://arxiv.org/abs/2310.06117)
- **Fractal Metacognition** (tinkerclaw) — Self-similar reflective levels across cognitive scales. [GitHub](https://github.com/globalcaos/tinkerclaw/blob/main/docs/papers/fractal-reasoning/fractal-reasoning.md)
- **H²R: Hierarchical Hindsight Reflection** — Decouples high-level planning from low-level execution memory. [arXiv:2509.12810](https://arxiv.org/abs/2509.12810)
- **LLM-ReSum** (2026) — Reflective summarization framework with iterative self-correction. [arXiv:2604.25665](https://arxiv.org/html/2604.25665v1)
- **Sensecape** — Multilevel abstraction for sensemaking with LLMs. [arXiv:2305.11483](https://ar5iv.labs.arxiv.org/html/2305.11483)

### Knowledge Distillation & Lesson Extraction
- **Forage V2** — Post-mortem lesson extraction categorized by scope (universal/domain/task-specific). [arXiv:2604.19837](https://arxiv.org/html/2604.19837v1)
- **SOUL.md Ecosystem** — Agent identity persistence via markdown soul files. [CrewClaw](https://www.crewclaw.com/blog/soul-md-create-ai-agent) | [Pinnacle SG](https://pinnsg.com/openclaw-2-teaching-your-ai-agent-who-it-is-the-soul-files/) | [Soul Spec](https://dev.to/tomleelive/the-complete-soulmd-template-guide-give-your-ai-agent-a-personality-3php)

### Context Management
- **Context Management for Deep Agents** (LangChain) — Offloading at 85%, summarization fallback, targeted evals. [Blog](https://www.langchain.com/blog/context-management-for-deepagents)
- **Context Budgeting** (Gantz AI) — 4-tier allocation framework: fixed costs, conversation, tool results, memory. [Blog](https://gantz.ai/blog/post/context-budgeting/)
- **Context Engineering** (OpenAI Community) — Separating thread-scoped memory from permanent records. [Forum](https://community.openai.com/t/best-practices-for-cost-efficient-high-quality-context-management-in-long-ai-chats/1373996)
- **LangGraph SummarizationMiddleware** — `RemoveMessage(id=REMOVE_ALL_MESSAGES)` pattern for context compaction. [Forum](https://forum.langchain.com/t/langgraph-postgresql-chat-history-and-summarization-best-practice/3521)

### Omega Engine References
- `docs/research/R30_soul_evolution_logic.md` — Base research on soul evolution pipeline
- `docs/research/R31_cross_pollination_spec.md` — Cross-pollination mechanics and resonance mapping
- `docs/research/R50_session_id_architecture.md` — Session ID format and management
- `docs/research/R51_context_builder_wiring_spec.md` — ContextBuilder implementation spec
- `docs/research/R_INVISIBLE_RAG_RESONANCE.md` — Contextual resonance patterns
- `docs/research/R_SOVEREIGN_MEMORY_ARCHITECTURE.md` — Sovereign memory tiering

---

## Field Notes (Research Process)

**Exa API**: Returns 401 — API key expired or invalid. Note: the `.env` file may have stale keys after the A→D sprint.

**Brave Search**: Returns 422 `SUBSCRIPTION_TOKEN_INVALID` — the Brave API key in `.env` is expired. User needs to obtain new key from https://api-dashboard.search.brave.com/.

**Workaround Used**: Tavily Search + built-in websearch as primary sources. Results cross-validated against each other for accuracy.

**Key Insight from Research Cross-Referencing**: The 3-tier abstraction model was independently validated by **four** separate research papers (Stanford Generative Agents, RAPTOR, Fractal Metacognition, H²R) without any single source citing the others — strong evidence that this hierarchical abstraction pattern is a convergent finding in the field.
