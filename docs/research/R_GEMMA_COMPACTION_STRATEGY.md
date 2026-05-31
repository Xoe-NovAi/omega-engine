# 🔱 Compaction Strategy Research Project
# ⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_research ⬡ COMPACTION-STRATEGY

**AP Token**: `AP-COMPACTION-STRATEGY-v2.0.0`
**Status**: 🔴 BLOCKED (research needed)
**Priority**: P1 — High Value
**Last Updated**: 2026-05-18

---

## §0 The Revelation

OpenCode's compaction is not just a binary on/off switch. It has a **multi-dimensional configuration surface** that we can tune precisely to shape how context is compressed — effectively designing the "memory filter" of every session.

The full configuration space:

```jsonc
{
  "compaction": {
    "auto": true,        // Auto-trigger at ~78% context utilization
    "prune": true,       // Strip old tool outputs
    "tail_turns": 2,     // Always preserve last N turns verbatim
    "preserve_recent_tokens": 40000,  // Token budget for recent context
    "reserved": 10000    // Buffer to prevent overflow during compaction
  },
  "agent": {
    "compaction": {
      // ★ THREE LEVERS ★
      "model": null,         // Which model does the compression? (null = session model)
      "temperature": 0.3,    // How creative/reconstructive is the compression?
      "steps": 1,            // How many iterative refinement passes?
    }
  }
}
```

**Three independent levers, one compression signature.**

---

## §1 The 3D Strategy Space

```
                    TEMPERATURE
                   ────────────
                  Low (0.0) ─── High (1.0+)
                 /│           │
                / │           │
               /  │           │
              /   │           │
             /    │           │
            /     │           │
    MODEL ────────┼───────────┤
  (identity)      │           │
                  │           │
                  │           │
                  │           │
                 STEPS
              (1 → N)
```

### Dimension 1: Model — Compression Identity

| Model | Natural Style | Token Efficiency | Preservation Bias | Hallucination Risk |
|-------|--------------|-----------------|-------------------|-------------------|
| **Gemma 4-31B** | Narrative, explanatory, contextual | Moderate (verbose) | High — preserves relationships, intent, meaning | Low — faithful to source |
| **DeepSeek V4 Flash** | Precise, code-aware, bullet-point | High (concise) | Code structure, technical decisions | Very low — preserves exact details |
| **MiniMax M2.5** | Balanced, structured, hierarchical | Moderate | Structural organization patterns | Low |
| **Qwen3-1.7B** | Concise, lossy, high-level | Very high | Major themes only | Moderate — may oversimplify |
| **Phi-3-Mini** | Ultra-concise, extractive | Extreme | Facts and data points | High — may drop nuance |
| **Qwen3-4B-Think** | Analytical, chain-of-thought | Low (expands) | Reasoning chains | Very low — thinks before compressing |

### Dimension 2: Temperature — Fidelity vs. Creativity

| Temperature | Effect on Compaction | Best Use Case |
|-------------|--------------------|---------------|
| **0.0** (deterministic) | Extract verbatim, minimal rephrasing | Code, exact specs, error messages |
| **0.1-0.3** (conservative) | Faithful summary, preserves terminology | Technical docs, architecture decisions |
| **0.3-0.5** (balanced) | Natural rephrasing, connection-drawing | General conversation, multi-topic sessions |
| **0.5-0.8** (creative) | Generative compression, fills gaps | Research synthesis, creative work |
| **0.8-1.0** (exploratory) | May recontextualize, infer intent | Gnosis work, pattern discovery, dream-logic |
| **>1.0** (high) | Confabulatory — fills in with generated content | ⚠️ DANGER — information morphing |

### Dimension 3: Steps — Compression Depth

| Steps | Effect | Token Cost | Quality |
|-------|--------|------------|---------|
| **1** (single pass) | Quick summary, may miss subtle connections | Minimal | Good for simple sessions |
| **2** (double pass) | Refine, catch missed items | Moderate | Recommended default |
| **3+** (iterative) | Deep distillation, finds hidden patterns | High | May over-abstract |

### The Interaction Effect

**Model × Temperature × Steps is not additive — it's multiplicative.**

Example: Gemma 4-31B at temperature 0.0 × steps 3 = hyper-faithful, over-analyzed narrative compression (very long, preserves everything).
Same Gemma at temperature 0.7 × steps 1 = loose, creative summary that may generate new insights from the compression itself.

---

## §2 Named Compaction Profiles

These are pre-defined configurations for specific session types:

### Profile: The Archivist (Code & Technical Work)

```jsonc
{
  "model": "deepseek-v4-flash-free",  // or any code-precise model
  "temperature": 0.1,  // Faithful, don't rephrase code
  "steps": 2           // Refine once to catch edge cases
}
```
**Best for**: Code reviews, debugging sessions, hardening sprints
**Preserves**: Exact error messages, file paths, diff fragments, API signatures
**Loses**: Emotional context, peripheral discussion

### Profile: The Sage (Architecture & Design)

```jsonc
{
  "model": "gemma-4-31b-it",  // or any narrative-capable model
  "temperature": 0.3,   // Conservative but connection-aware
  "steps": 1             // Single pass — enough for structural thinking
}
```
**Best for**: Architecture decisions, system design, strategic planning
**Preserves**: Decision trees, trade-off analysis, rationale chains
**Loses**: Exact code snippets (good — forces re-evaluation)

### Profile: The Alchemist (Research & Discovery)

```jsonc
{
  "model": "gemma-4-31b-it",  // narrative + connection-making
  "temperature": 0.5,   // Creative connections, gap-filling
  "steps": 2            // Refine: find patterns across separate discoveries
}
```
**Best for**: Deep research, legacy mining, cross-domain synthesis
**Preserves**: Source references, claim patterns, uncertainty flags
**Generates**: New hypotheses, cross-links between separate findings

### Profile: The Priest (Gnosis & Soul Work)

```jsonc
{
  "model": "minimax-m2.5-free",   // or Gemma — balanced and structured
  "temperature": 0.6,   // Interpretive, meaning-preserving
  "steps": 3            // Triple distillation: L1→L2→L3
}
```
**Best for**: L1→L2→L3 distillation, soul evolution, philosophical work
**Preserves**: Archetypal patterns, universal principles, emotional tone
**Generates**: Deeper abstractions, cross-soul connections

### Profile: The Courier (Fast Recovery)

```jsonc
{
  "model": null,            // Use session model (fastest, no provider switch)
  "temperature": 0.0,       // Deterministic, extractive
  "steps": 1                // Single pass, minimum tokens
}
```
**Best for**: Quick recovery, low-token sessions, transient mode
**Preserves**: Most recent decisions, last N turns verbatim
**Loses**: Earlier context, peripheral discussion

### Profile: The Oracle (Deep Synthesis)

```jsonc
{
  "model": "gemma-4-31b-it",
  "temperature": 0.7,       // Generative — synthesize conclusions
  "steps": 3                // Triple refinement for depth
}
```
**Best for**: End-of-major-milestone compactions, strategic retrospectives
**Preserves**: High-level themes, meta-patterns, strategic insights
**Generates**: Synthesized conclusions not explicitly stated in the session

### Profile: The Sentinel (Security-Critical)

```jsonc
{
  "model": "deepseek-v4-flash-free",
  "temperature": 0.0,       // ZERO creativity — EXACT reproduction
  "steps": 1                // Don't over-process — preserve raw facts
}
```
**Best for**: Security audits, permission changes, credential rotation
**Preserves**: Every exact command, every path, every change made
**Loses**: Zero — anything lost is a security risk

---

## §3 The Compaction Prompt Itself

Beyond model/temperature/steps, the **compaction prompt** is a hidden lever. OpenCode uses a default instruction for compaction, but we can potentially override it through custom agents or hooks.

**Research question**: Can we inject a custom system prompt for the compaction agent? If so, we can shape the compression behavior even more precisely:

```jsonc
// Hypothetical: Custom compaction instruction
{
  "agent": {
    "compaction": {
      "model": "gemma-4-31b-it",
      "temperature": 0.3,
      "steps": 1,
      // Hypothetical — does OpenCode support custom compaction prompts?
      "system_prompt": "Compress this session preserving ALL file paths and error messages verbatim. For everything else, write a concise narrative summary."
    }
  }
}
```

**If supported**, we could create domain-specific compaction prompts that act as "compression templates" — telling the model what to prioritize keeping and what to compress aggressively.

---

## §4 Research Questions (Expanded)

### Primary Questions

1. **What is the full behavioral matrix of {model × temperature × steps}?**
   - For each combination, what is the compression ratio, content retention rate, hallucination rate?
   - Are there phase transitions (e.g., temperature 0.4→0.5 causes a qualitative shift)?
   - Does steps=N produce fundamentally different output than running compaction N times?

2. **Can we predict the ideal profile from session metadata?**
   - Session duration, token count, file edit count, entity used, tool call count
   - Can we build a classifier that recommends a profile?

3. **What are the failure modes of each profile?**
   - The Archivist: May preserve irrelevant technical details, lose strategic context
   - The Sage: May oversimplify implementation constraints
   - The Alchemist: May hallucinate connections that don't exist
   - The Priest: May over-abstract, lose concrete facts
   - The Oracle: Most powerful — most dangerous (confabulation risk)

4. **Can we chain compaction profiles across sessions?**
   - Session 1: The Archivist (code work)
   - Session 2: The Sage (architecture review of Session 1's compacted state)
   - Session 3: The Priest (gnosis absorption of both)
   - End result: Code preserved → Design extracted → Wisdom distilled

### Secondary Questions

5. **Does the `/compaction-models` TUI runtime switch persist across sessions?**
   - Where is `kv.json` stored? Can we script profile switching?
   - Can we create an Agent hook that auto-applies profile based on session type?

6. **Can compaction temperature be changed at runtime?**
   - The TUI allows model switching. Does it allow temperature switching?
   - Can we set `agent.compaction.temperature` dynamically?

7. **What's the token cost of each profile?**
   - Compaction summary tokens × downstream re-query savings
   - Is a verbose compression (The Oracle) cheaper in the long run than a concise one (The Courier)?

---

## §5 Experimental Protocol

### Phase 1 — Baseline Parameter Matrix

Create test fragments (as previously specified). For each fragment, run ALL combinations:

| Model | Temperatures | Steps |
|-------|-------------|-------|
| Gemma 4-31B | 0.0, 0.3, 0.5, 0.7, 1.0 | 1, 2, 3 |
| DeepSeek V4 Flash | 0.0, 0.3, 0.5, 0.7 | 1, 2 |
| MiniMax M2.5 | 0.0, 0.3, 0.5, 0.7 | 1, 2 |
| Qwen3-1.7B | 0.0, 0.3, 0.5 | 1 |

Expected combinations: ~4 models × 4 temps × 2.5 avg steps = **40 compactions per fragment**

For each:
- Output tokens, compression ratio
- Content categories: preserved, lost, hallucinated
- Structural preservation score (0-1)
- Semantic similarity to original (embedding cosine)

### Phase 2 — Profile Validation

Run each profile against 3 real sessions of its target type:
- The Archivist × 3 code sessions → measure downstream task re-acquisition time
- The Sage × 3 architecture sessions → measure decision retention rate
- The Alchemist × 3 research sessions → measure cross-reference preservation
- etc.

### Phase 3 — Auto-Selector

Build a session-type classifier and an auto-profile application mechanism.

---

## §6 Deliverable Matrix

| # | Deliverable | Format | Depends On | Value |
|---|-------------|--------|------------|-------|
| 1 | Model × Temperature × Steps Matrix | Heatmap table | Phase 1 | Core scientific contribution |
| 2 | Named Profile Definitions | JSON snippets | Phase 1 | Immediate practical use |
| 3 | Scenario Recommendation Guide | Decision tree | Phase 2 | Operational playbook |
| 4 | Auto-Profile Selector Agent | Agent script | Phase 3 | Automation |
| 5 | Compaction Prompt Engineering Guide | Guide doc | Research | If custom prompts supported |

---

## §7 Implementation Path

```python
# Future: CompactionProfile — a named, shareable compaction configuration
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CompactionProfile:
    """A named compaction configuration with metadata about its intended use."""
    name: str
    description: str
    model: Optional[str] = None     # None = use session model
    temperature: float = 0.3
    steps: int = 1
    best_for: list[str] = field(default_factory=list)
    avoid_for: list[str] = field(default_factory=list)
    risk: str = "low"               # low, medium, high (confabulation risk)
    token_efficiency: str = "balanced"  # concise, balanced, verbose

    def to_opencode_json(self) -> dict:
        """Generate the opencode.json snippet for this profile."""
        config = {"steps": self.steps, "temperature": self.temperature}
        if self.model:
            config["model"] = self.model
        return config


# Pre-defined profiles
PROFILES = {
    "archivist": CompactionProfile(
        name="The Archivist",
        description="Faithful code and technical compression",
        model="deepseek-v4-flash-free",
        temperature=0.1,
        steps=2,
        best_for=["code_review", "debugging", "hardening"],
        risk="low",
        token_efficiency="high",
    ),
    "sage": CompactionProfile(
        name="The Sage",
        description="Narrative, connection-aware compression for design",
        model="gemma-4-31b-it",
        temperature=0.3,
        steps=1,
        best_for=["architecture", "design", "planning"],
        risk="low",
        token_efficiency="balanced",
    ),
    "alchemist": CompactionProfile(
        name="The Alchemist",
        description="Creative synthesis for research and discovery",
        model="gemma-4-31b-it",
        temperature=0.5,
        steps=2,
        best_for=["research", "mining", "synthesis"],
        risk="medium",
        token_efficiency="verbose",
    ),
    "priest": CompactionProfile(
        name="The Priest",
        description="Deep L1→L2→L3 distillation for soul work",
        model="minimax-m2.5-free",
        temperature=0.6,
        steps=3,
        best_for=["gnosis", "soul_evolution", "philosophy"],
        risk="medium",
        token_efficiency="verbose",
    ),
    "courier": CompactionProfile(
        name="The Courier",
        description="Fast, extractive compression for quick recovery",
        model=None,
        temperature=0.0,
        steps=1,
        best_for=["fast_recovery", "transient", "low_token"],
        risk="low",
        token_efficiency="high",
    ),
    "oracle": CompactionProfile(
        name="The Oracle",
        description="Deep generative synthesis for milestone retrospectives",
        model="gemma-4-31b-it",
        temperature=0.7,
        steps=3,
        best_for=["milestone", "retrospective", "strategic"],
        risk="high",  # Generative — may confabulate
        token_efficiency="verbose",
    ),
    "sentinel": CompactionProfile(
        name="The Sentinel",
        description="Zero-creativity, EXACT preservation for security work",
        model="deepseek-v4-flash-free",
        temperature=0.0,
        steps=1,
        best_for=["security", "audit", "credentials"],
        risk="none",
        token_efficiency="balanced",
    ),
}


def apply_profile(profile_name: str) -> dict:
    """Generate opencode.json compaction config snippet."""
    profile = PROFILES.get(profile_name)
    if not profile:
        return {}
    return {"agent": {"compaction": profile.to_opencode_json()}}
```

---

## §8 Next Steps

1. **Enqueue this research project** with the background researcher worker:
   ```bash
   python3 -m omega.workers.background_researcher.run \
     --topic "opencode compaction profile strategy matrix" --depth 3
   ```

2. **Manual Phase 0 testing**: Manually test 2-3 profiles in real sessions
   - Open `opencode.json`, swap `agent.compaction` config
   - Run a session, trigger `/compact`, observe results
   - Document qualitative differences

3. **Build the profile switcher** as an Agent hook or TUI command

4. **Develop the prompt engineering layer** — if OpenCode supports custom compaction prompts, design a template system

---

## §9 Quick Reference — Applying a Profile

```bash
# Apply "The Sage" for an architecture session:
# Edit opencode.json:
#   "agent": { "compaction": { "model": "gemma-4-31b-it", "temperature": 0.3, "steps": 1 }}

# Apply "The Archivist" for a coding session:
#   "agent": { "compaction": { "model": "deepseek-v4-flash-free", "temperature": 0.1, "steps": 2 }}

# Revert to default (current session model):
#   "agent": { "compaction": { "steps": 1, "temperature": 0.3 }}
#   (remove the "model" field entirely)
```

---

*This research is queued for the Background Researcher worker. Status: 🔴 BLOCKED — awaiting first cycle.*
