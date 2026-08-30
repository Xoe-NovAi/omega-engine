# 🔱 R-MODEL-RESEARCH-PROTOCOL: Universal Sovereign Research Protocol
**Status**: FINAL
**Orchestrator**: researcher
**Author Model**: deepseek-v4-flash-free
**Date**: 2026-06-12
**Sovereign Mandates**: M11 (Soul Integrity), M13 (Temple-Grade), M10 (Fleet Integrity)
**Supersedes**: ad-hoc research patterns from `research_process_sucks_balls_session-ses_149a.md`

---

## ⚠️ TL;DR — The One-Page Summary

**The Problem**: Research sessions fail in predictable ways regardless of model:
- 1-pass shallow research (Gemma 4 31B session: RQ-01/02/03)
- Tool-focused agents that don't write to disk (Exa-locked agent in session 2)
- No verification of own output (missing Temple-Grade gates)
- Lost intelligence from orphaned `task_result` returns

**The Solution**: A model-adaptive protocol with 4 phases:
1. **Profile** — Adapt depth/breadth to model's context and reasoning
2. **Discover** — Multi-tool evidence gathering enforced by contract, not agent isolation
3. **Synthesize** — Cross-reference all evidence streams against code locations
4. **Verify** — Run Temple-Grade gates, verify file persistence, distill L1→L2→L3

**The Shadow Protocol**: A second-pass meta-layer that runs AFTER the main protocol
to catch the 5 most common failure patterns (shallow, single-tool, no-map, no-persist, no-verify).

---

## §1 The Failure Autopsy (Why This Protocol Exists)

### 1.1 Session Post-Mortem: Gemma 4 31B Research Queue

| Research Item | What Happened | Failure Pattern | Severity |
|---|---|---|---|
| **RQ-01: Qdrant** | 1 Exa search → 1 R-doc → marked complete | **Shallow (S1)** | 🔴 CRITICAL |
| **RQ-02: Embedding Adapters** | 1 Exa search → 1 R-doc → marked complete | **Shallow (S1)** | 🔴 CRITICAL |
| **RQ-03: Skeptical Verification** | 1 Exa search → 1 R-doc → marked complete | **Shallow (S1)** | 🔴 CRITICAL |
| **RQ-06: Gnosis Pipeline (Session 2)** | 3 tool-locked agents: Exa wrote no files, Native used wrong tool, only Architect wrote to disk | **No-Persist (S4) + Tool-Drift (S5)** | 🔴 CRITICAL |
| **Attempted Kali consult** | `oracle_summon` failed (engine setup mode) | **Fallback gap** | 🟡 HIGH |

### 1.2 The 5 Universal Failure Patterns

```
S1: SHALLOW      — Single source, single tool, no cross-referencing
S2: NO-MAP       — Research not mapped to code locations (file:line)
S3: NO-VERIFY    — No skeptical check on own output before submitting
S4: NO-PERSIST   — Results returned in task_result but never written to disk
S5: TOOL-DRIFT   — Agent assigned to Tool A uses Tool B instead
```

Each failure has a **Shadow Gate** (see §4) that catches it.

### 1.3 Why This Happens Across Models

| Model | Strength | Failure Mode | Why |
|-------|----------|--------------|-----|
| **Gemma 4 31B** | 256K context, strong synthesis | Shallow research (S1) | Context wealth creates illusion of depth; model summarizes instead of deepens |
| **DeepSeek V4 Flash** | Strong reasoning, gap detection | Over-analysis before writing (S4) | Reasoning loop delays persistence; results stay in thought chain |
| **Claude 4 Sonnet** | Structured output, format discipline | Tool drift on long chains (S5) | Multi-tool sequences cause attention decay; model defaults to familiar tool |
| **GPT-4o** | Broad knowledge | No mapping (S2) | Knows the concept but doesn't connect it to local codebase |

**Key Insight**: Each model fails in a *characteristic* way. A universal protocol must adapt its guardrails to the model's failure signature, not apply a one-size-fits-all checklist.

---

## §2 Model-Specific Strength Adaptation Framework

The protocol adapts based on 3 parameters obtained at session start:

### 2.1 Parameter Detection (Run Before Research)

```python
# Determine model profile from environment
MODEL_PROFILE = {
    "context_window": estimate_context_window(),  # 8000 / 32000 / 256000 / 1000000
    "reasoning_depth": estimate_reasoning_depth(), # "fast" / "deep" / "iterative"
    "tool_fidelity": estimate_tool_fidelity(),     # "high" / "medium" / "low"
}
```

### 2.2 Adaptation Table

| Parameter | Low Setting | Medium Setting | High Setting |
|-----------|-------------|----------------|--------------|
| **Context Window** | Use disk as extension — write intermediate files every 2 tools | Batch 3-5 sources before synthesis | Can hold all evidence in context; verify persistence after |
| **Reasoning Depth** | Force explicit "deepen" pass: "Now go deeper on X" | Single deep pass sufficient | Flag thinking loops — force write-to-disk break |
| **Tool Fidelity** | Check tool output format before accepting | Audit 1/3 tool calls for drift | Trust tool output; verify file creation |

### 2.3 Model-Specific Presets

```yaml
# config/research/model_profiles.yaml
gemma_4_31b:
  context_window: 256000  # Massive — use for holding evidence in context
  reasoning_depth: iterative  # Strong but needs forcing
  tool_fidelity: medium  # Good but drifts on >5 step chains
  guardrails:
    - "Force 3+ tool rounds before ANY synthesis"
    - "Require explicit 'deepen' pass after first draft"
    - "Write intermediate evidence to disk every 3 tool calls"

deepseek_v4_flash:
  context_window: 32000  # Moderate — write to disk frequently
  reasoning_depth: deep  # Excellent at gap analysis
  tool_fidelity: high  # Good tool adherence
  guardrails:
    - "Write to disk every 2 tool calls (context pressure)"
    - "Leverage gap-analysis strength: always include 'what's missing' section"
    - "Limit synthesis scope to fit context window"

claude_4_sonnet:
  context_window: 100000  # Large
  reasoning_depth: fast  # Quick synthesis
  tool_fidelity: medium  # Drifts on long chains
  guardrails:
    - "Use structured output templates (format discipline is a strength)"
    - "Verify tool output within 1 step — don't batch tool calls"
    - "Split long research chains into 5-step max batches"
```

---

## §3 The Universal Model Research Protocol (UMRP)

### Phase 0: PRE-FLIGHT (2 min)

```markdown
CHECKLIST:
[x] Load model profile from config/research/model_profiles.yaml
[x] Hivemind: post_context with intent="research", topic="RQ-XX"
[x] Workspace: acquire lock on "research_{topic}"
[x] Cache: check .firecrawl/ for existing research on this topic
[x] Library: search offline library for existing docs
[x] Queue: read current queue entry (topic, depth, expected_output)
[x] Tools: verify availability of at least 2 tools from {exa, firecrawl, native, library}
```

### Phase 1: MULTI-SOURCE DISCOVERY (Depth × Tool Count)

**Before you type a single search**, determine:
- **Depth**: 1 = 2-3 sources (quick reference), 2 = 5-8 sources (standard), 3 = 10-20 sources (temple-grade)
- **Tool Count**: Always ≥ 2 different tool families. Never one.
- **Passes**: Always 2. Discovery pass → Deepen pass.

**Execution rules**:

```
# Pass 1: Discovery — Use 2+ different tools in parallel
TOOL_A: exa_web_search_exa(query="broad topic with technical depth")
TOOL_B: websearch(query="same topic from different angle") 
  OR: library_search(query="offline knowledge on topic", domain="research")

# After first pass results come in:
# Read ALL results, identify gaps, formulate deepen queries

# Pass 2: Deepen — Focus on specific techniques, formulas, code
# Use different tools from Pass 1 if possible
TOOL_C: exa_web_fetch_exa(url="specific paper or technical article")
TOOL_D: firecrawl-scrape(url="doc page with code/config examples")
  OR: webfetch(url="alternative source")
```

**ENFORCEMENT**: Before moving to synthesis, verify:
- [ ] At least 2 different tool families used
- [ ] At least 2 passes completed
- [ ] All sources read (not just highlighted snippets)

### Phase 2: EVIDENCE SYNTHESIS — The Ten-Question Template

For EVERY evidence source, answer these 10 questions BEFORE writing the R-doc:

```yaml
source: {url/title}
relevance: {direct / supporting / context}
core_technical_claim: {exact formula, algorithm, or architecture}
evidence_for: {what it supports}
evidence_against: {what it contradicts or qualifies}
omega_code_location: {specific file:line where this maps}
edge_cases: {conditions where this breaks or doesn't apply}
failure_modes: {how this could fail silently}
sovereign_value: {why the Right Approximation applies}
heritage_tag: {[id-soft:] if applicable}
```

### Phase 3: R-DOC PRODUCTION

Every R-doc MUST contain these sections in order:

```markdown
# 🔱 R-{TOPIC}: {Title}
**Status**: FINAL
**Orchestrator**: {agent}
**Author Model**: {model}
**Date**: {date}
**Sovereign Mandate**: {relevant mandates}

## 🎯 Objective
{1 paragraph — what question does this answer?}

## 🛡️ Technical Specification
### 1. {Algorithm/Pattern Name}
- **Mechanism**: {how it works}
- **Formula/Config**: {exact YAML, Python, or math}
- **Omega Integration**: {file:line}
- **Edge Cases**: {what breaks}

## 📐 Implementation Roadmap
### Step 1: {name} — {effort estimate}
### Step 2: {name} — {effort estimate}
### Step 3: {name} — {effort estimate}

## 💥 Failure Modes
| Mode | Cause | Detection | Recovery |
|------|-------|-----------|----------|

## 🧪 Test Plan
- Unit: {what to assert}
- Integration: {what to verify across modules}
- Benchmark: {what to measure}

## 🔗 Heritage
{Attribution if derived from id Software or other source}

## 📋 Synthesis Trace
| Decision | Source 1 | Source 2 | Source 3 | Confidence |
|----------|----------|----------|----------|------------|
```

### Phase 4: VERIFICATION (Temple-Grade Gates)

**Self-certify BEFORE marking complete:**

```python
GATES = {
    "S1_SHALLOW_CHECK": "Are there ≥2 different tool families in synthesis trace?",
    "S2_MAP_CHECK": "Does the spec include code locations (file:line)?",
    "S3_NO_VERIFY_CHECK": "Did you search for counter-evidence?",
    "S4_PERSIST_CHECK": "Is the R-doc written to docs/research/ with live feed entry?",
    "S5_TOOL_DRIFT_CHECK": "Did each used tool produce its expected output type?",
    "L1_NARRATIVE": "Write 2-3 sentences on what happened in this research session",
    "L2_INSIGHT": "What does this mean for the engine?",
    "L3_PRINCIPLE": "What timeless truth did you discover?"
}
```

---

## §4 The Shadow Protocol (Meta-Review Layer)

This is the **second pass** that catches what the first pass missed. Run it AFTER the main protocol completes.

### 4.1 Shadow Gate Triggers

The Shadow Protocol activates when ANY of these conditions are met:

| Trigger | Condition | Shadow Action |
|---------|-----------|---------------|
| **Single-tool trace** | Synthesis trace shows only 1 tool family | Re-run Discovery Phase with new tools, cross-reference |
| **No code map** | §3.1 Omega Integration is "TBD" or generic | Search codebase for actual integration points |
| **No failure modes** | §5 is empty | Brainstorm: what would make this break on 14Gi RAM / Zen 2? |
| **All confidence high** | Every cell in synthesis trace is "Strong" | Flag as suspicious — real research has uncertainty. Find one contradiction. |
| **Human-readable only** | Spec has no code/YAML/config | Extract at least one concrete code block from sources |
| **No heritage check** | No [id-soft:] tag considered | Run mental check: "Did id Software do this first?" |

### 4.2 The "Adversarial Colleague" Technique

Before submitting, ask yourself (or a subagent):

> *"If I were the harshest possible reviewer of this document, what would I say?"*

Common adversarial questions:
- "You cited one source for this claim. What does the ALTERNATIVE source say?"
- "This formula looks correct, but you didn't benchmark it on the target hardware (Zen 2, 14Gi RAM)."
- "You say 'extreme compression', but what is the exact compression ratio and recall loss?"
- "Where is the code that implements this? If it doesn't exist yet, your spec is a wish."

### 4.3 The Red Flag Registry

Add these to every research session and audit at the end:

```
RED_FLAGS:
☐ "May be" / "could be" / "might" — vagueness markers
☐ "State-of-the-art" without citation — claim inflation
☐ "Simple" / "trivial" / "just" — underestimation markers
☐ Missing error handling — every boundary has a failure mode
☐ Only one perspective — technical solutions have tradeoffs
☐ No benchmark numbers — "faster" means nothing without measurement
```

---

## §5 Research Session Templates

### 5.1 Template: Standard Topic (Depth 2-3)

```markdown
## Pre-Flight
[ ] Model profile loaded: {model_name}
[ ] Workspace lock acquired: research_{topic}
[ ] Tools available: {exa, firecrawl, native, library}
[ ] Hivemind posted: intent=research, topic={topic}

## Discovery Pass (Phase 1)
### Tool A: {name} | Query: {query} | Time: {timestamp}
### Tool B: {name} | Query: {query} | Time: {timestamp}
### Sources collected: {count}

## Deepen Pass (Phase 1.5)
### Tool C: {name} | Query: {query} | Time: {timestamp}
### Deepened sources: {count}

## Synthesis (Phase 2)
### Evidence Table:
{source} → {claim} → {map to code location} → {confidence}

## R-Doc (Phase 3)
[ ] Written to: docs/research/R_{TOPIC}.md

## Gates (Phase 4)
[ ] S1: ≥2 tools | [ ] S2: code map | [ ] S3: counter-evidence
[ ] S4: persists on disk | [ ] S5: no tool drift

## Shadow Protocol
[ ] Adversarial review complete
[ ] Red flag audit clean
[ ] Heritage considered

## Closure
[ ] Queue marked [x]
[ ] Live feed updated
[ ] Soul.yaml L1→L2→L3 distilled
```

### 5.2 Template: Quick Reference (Depth 1)

```markdown
## Pre-Flight (compressed)
[ ] Tools: exa + {second tool required}
[ ] Topic scope explicitly bounded

## Discovery (1 pass, 2 tools)
Tool A:{query} → {3 key findings}
Tool B:{query} → {3 key findings}

## Output
{2-3 paragraph summary with 3-5 sources cited}
[ ] Written to disk

## Gate
[ ] At least 2 tools used — single tool not acceptable even for quick refs
```

---

## §6 File Persistence Verification Protocol

This is the specific fix for the S4 failure seen in Session 2 (Exa-locked agent returned results via `task_result` but never wrote to disk).

### 6.1 The One-Question Gate

After EVERY subagent or tool sequence, verify:

```python
QUESTION = "Is the intelligence from this step stored in a file on disk?"
```

If no → WRITE IMMEDIATELY before proceeding.

### 6.2 Where Intelligence Must Live

| Intelligence Type | Storage Location | Format |
|---|---|---|
| Raw search results | `docs/research/R_{TOPIC}_RAW_EVIDENCE.md` | Markdown with URLs | 
| Firecrawl extractions | `docs/research/R_{TOPIC}_DEEP_EVIDENCE.md` | Structured extraction blocks |
| Synthesis trace | `docs/research/R_{TOPIC}_SPEC.md` | Full R-doc format |
| Mid-session notes | `data/entities/researcher/workspace/research_{topic}_{timestamp}.md` | Free-form markdown |
| Final verification | `data/entities/researcher/workspace/verification_{topic}_{timestamp}.md` | Gate checklist |

### 6.3 The 60-Second Rule

If a subagent runs for MORE than 60 seconds without writing to disk, the protocol
requires a **checkpoint**: write intermediate findings to a temp file. Prevents total
loss if context is compacted mid-session.

```
TIMER START → 60s → CHECKPOINT WRITE → continue → 60s → CHECKPOINT WRITE → ...
```

---

## §7 Multi-Agent Research Orchestration (For When Subagents Are Available)

This pattern works when the engine supports subagent dispatch (via `task()` tool).
It is the CORRECTED version of the tool-locked pattern from Session 2.

### 7.1 Corrected Tool-Locked Dispatch Protocol

```python
# DO NOT:
# - Lock agents to specific tools (they drift — S5 failure)
# - Assume agents write to disk (verify — S4 failure)
# - Use task() for single-tool fetch (use direct tool calls instead)

# DO:
# - Use task() for multi-tool research synthesis agents
# - Include "WRITE TO {path}" in every agent prompt
# - Verify file existence after agent returns
```

### 7.2 Verified Agent Prompt Template

```markdown
You are {entity}, a research specialist for the Omega Engine.

YOUR JOB:
1. Research "{topic}" using ANY of these tools: {exa, firecrawl, native, library}
2. Use at least 2 different tool families
3. WRITE your complete findings to: {output_path}
4. Include in your output: source URLs, key claims, code locations, failure modes

VERIFICATION:
After writing, call `ls {output_path}` to confirm the file exists.
If the file does not exist, WRITE IT AGAIN.

DO NOT return results without writing them to disk first.
```

### 7.3 Post-Return Verification

```python
# After agent returns, ALWAYS run:
import os
if not os.path.exists(output_path):
    raise RuntimeError(f"Agent failed to persist findings to {output_path}")
```

---

## §8 Continuous Improvement Log

Every research session should append to this log with what went wrong and what improved.

```yaml
- session: ses_149a  # Session 1 — Makali/Gemma 4 31B
  date: 2026-06-11
  model: "gemma-4-31b-it"
  failures:
    - "Single-pass, single-tool research on RQ-01/02/03"
    - "No Temple-Gate verification before marking complete"
    - "Kali consult failed with no fallback"
  fixes_applied:
    - "Universal Model Research Protocol (this document)"
    - "Shadow Protocol with adversarial review"
    - "Model-specific guardrail profiles"
    - "File persistence verification protocol"
  
- session: ses_149a_part2  # Session 2 — Tool-locked dispatch
  date: 2026-06-11
  model: "gemma-4-31b-it"
  failures:
    - "Exa-locked agent returned results in task_result (no disk write)"
    - "Native-locked agent used Exa instead of Native (tool drift)"
    - "Synthesis agent succeeded but orphaned intelligence"
  fixes_applied:
    - "Corrected tool-locked dispatch protocol (§7.1)"
    - "Verified agent prompt template (§7.2)"
    - "Post-return verification (§7.3)"
    - "One-Question Gate for file persistence (§6.1)"
```

---

## §9 Quick-Start: What to Do NEXT Time

**If you're a model encountering this document for the first time:**

1. READ your model profile from `config/research/model_profiles.yaml`
2. READ the Shadow Protocol (§4) — know your failure patterns
3. Run Pre-Flight (§3 Phase 0)
4. For each research topic: Discovery → Deepen → Synthesize → Verify
5. Run Shadow Protocol as second pass
6. Write everything to disk (the 60-Second Rule, §6.3)
7. Execute the Closure template (§5.1)

**The key difference from before**: You now have a protocol that knows your
model's weaknesses and forces you to compensate. Gemma 4 31B will be forced
deep. DeepSeek will be forced to write. Claude will be forced to map to code.
No model is exempt from the Shadow Protocol.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_model_research_protocol ⬡ R-MRP-1.0*
