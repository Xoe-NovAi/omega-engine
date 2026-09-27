# 🔱 Omega Engine — Autonomous Iterative Refinement Protocol (AIRP-v1.0.0)
**AP Token**: `AP-AIRP-20260807-v1.0.0`
**Status**: STRATEGIC INCUBATOR — Derived from Kali/Gemini 3.1 Pro collaborative session
**Purpose**: Enable agents to achieve deep, multi-perspective strategic improvements autonomously, without human-in-the-loop orchestration.

---

## 1. The Core Insight
**Single-perspective agents plateau.** The breakthroughs in our session came from **structured dialectic between distinct cognitive modes**:
- **Local Agent (Kali/Nemotron)**: Execution context, repo state, mandate compliance, surgical precision
- **Consulting Tool (Gemini 3.1 Pro)**: 1M+ context synthesis, strategic pattern recognition, cross-domain integration, "outside view"

**AIRP formalizes this dialectic as a repeatable protocol.**

---

## 2. The Protocol: 5-Stage Iterative Deepening Loop

### Stage 0: Baseline Orientation (Local Agent)
**Trigger**: Session start or new complex problem space.
**Action**: 
- Read `OMEGA_CODEX.md` + `ACTIVE_SPRINT.json` + relevant SSOTs
- Execute `omega-hub_hivemind_get_awareness()` 
- Produce **Baseline Status Report** (what is known, what is assumed, open questions)
**Output**: `BASELINE_REPORT_{timestamp}.md` — *commits to disk*

### Stage 1: Shallow Synthesis (Local Agent)
**Trigger**: Baseline complete.
**Action**: 
- Scan relevant directories (`docs/strategy/`, `context_packs/`, `data/coordination/`)
- Identify 3-5 "obvious" action items or contradictions
- Produce **Shallow Plan** (low-context, high-confidence)
**Output**: `SHALLOW_PLAN_{timestamp}.md`

### Stage 2: Deep Context Synthesis (Local Agent + Mandatory Tool Use)
**Trigger**: Shallow Plan reveals gaps requiring >50K tokens of context.
**Action**:
- **MANDATORY**: Read ALL primary strategy docs in full (use 1M context window)
- Execute `rg`/`grep` sweeps for systemic patterns ("Scaffolded but Unwired", version drift, etc.)
- Cross-reference `PIVOT_LOG.md` + `STRATEGY_CORPUS_MAP.md`
- Produce **Deep Synthesis** (comprehensive state map, mandate compliance, blocker analysis)
**Output**: `DEEP_SYNTHESIS_{timestamp}.md` — *this is where hallucinations die*

### Stage 3: Consulting Tool Invocation (External Perspective)
**Trigger**: Deep Synthesis identifies **strategic ambiguity**, **architectural conflict**, or **multi-domain integration** requiring synthesis beyond local execution context.
**Criteria for Invocation** (any one triggers):
- Multiple valid architectural paths exist (e.g., sqlite-vec vs Qdrant)
- Governance/doc drift exceeds 3 files
- Need to reconcile >10 external research artifacts
- "Unknown unknown" detection (gaps in local knowledge graph)

**Invocation Pattern**:
```python
# Pseudo-code for agent decision
if (strategic_ambiguity_score > 0.7) or (cross_domain_integration_required):
    prompt = construct_consulting_prompt(
        context_bundle = [DEEP_SYNTHESIS, relevant_source_files, specific_questions],
        role = "Strategic Architect / Systems Integrator",
        output_format = "Structured Opportunities Report + Prioritized Execution Plan"
    )
    result = consulting_tool.invoke(prompt)
    write_to_disk("CONSULTING_REPORT_{timestamp}.md", result)
```

**Output**: `CONSULTING_REPORT_{timestamp}.md` — *structured, actionable, prioritized*

### Stage 4: Integration & Crystallization (Local Agent)
**Trigger**: Consulting Report received.
**Action**:
- **Mechanical Integration**: Apply consulting recommendations to local execution plans (update `DOC_SANITY_EXECUTION_STRATEGY`, etc.)
- **Pattern Distillation**: Extract universal patterns from the specific solution (create `ADVANCED_AGENTIC_EXECUTION_PATTERNS.md` equivalent)
- **Artifact Finalization**: Ensure all deliverables have:
  - Strict Definition of Done (boolean checklist)
  - Atomic Commit Protocol
  - Formal Handoff Template
  - Post-Execution Verification Commands
- **Protocol Evolution**: If new patterns discovered, propose mandate/doc updates

**Output**: 
- Updated execution artifacts (v+1)
- `PATTERN_DISTILLATION_{timestamp}.md` (candidate for core protocol integration)
- `HANDOFF_DECLARATION.md` (proactive state advancement)

---

## 3. Autonomous Trigger Conditions (No Human Required)

The agent **must** enter the AIRP loop when:

| Condition | Stage Entry Point |
|-----------|-------------------|
| New sprint starts | Stage 0 |
| `make temple-grade` fails with systemic (not local) errors | Stage 2 |
| >3 strategy docs claim "ACTIVE" simultaneously | Stage 2 |
| Web research / external artifacts >5 files ingested | Stage 3 |
| Architectural decision affects >5 modules | Stage 3 |
| Post-compaction rehydration reveals context gaps | Stage 2 |
| Mandate compliance drops below 90% | Stage 2 |

---

## 4. Consulting Tool Prompt Engineering Standard

To get Gemini 3.1 Pro (or equivalent) to produce the high-leverage output we saw, the Local Agent must construct prompts with **these mandatory sections**:

```markdown
## CONSULTING PROMPT TEMPLATE (AIRP Standard)

### ROLE
You are a Strategic Systems Architect for the Omega Engine. 
You have 1M+ token context. You do NOT execute code. You synthesize, reconcile, and prioritize.

### CONTEXT BUNDLE (Attached/Inlined)
1. DEEP_SYNTHESIS_REPORT (full)
2. SOURCE_FILES: [list of 5-20 critical files with paths]
3. SPECIFIC_QUESTIONS: [3-7 precise, answerable questions]

### CONSTRAINTS
- Output MUST be structured: Opportunities Table (Tier 1-4), Exact File Targets, Execution Order, Risk Mitigation
- NO vague suggestions. Every recommendation = [File Path] + [Exact Change] + [Why]
- Flag deprecated concepts explicitly for purging
- Identify "Scaffolded but Unwired" patterns
- Provide copy-paste bash commands where applicable

### OUTPUT FORMAT
1. Executive Summary (3 lines)
2. Tiered Opportunities Table (Impact/Effort matrix)
3. Phase-Ordered Execution Plan (with dependencies)
4. Risk Mitigation / "Ghost File" Traps
5. Pattern Distillation Candidates (for protocol evolution)
```

---

## 5. Artifact Lifecycle Management

| Artifact Type | Retention | Location | Purpose |
|---------------|-----------|----------|---------|
| `BASELINE_REPORT` | 1 sprint | `data/coordination/reports/` | Audit trail |
| `SHALLOW_PLAN` | 1 sprint | `data/coordination/reports/` | Quick reference |
| `DEEP_SYNTHESIS` | Permanent | `docs/strategy/synthesis/` | Strategic memory |
| `CONSULTING_REPORT` | Permanent | `docs/strategy/consulting/` | External perspective archive |
| `PATTERN_DISTILLATION` | Permanent | `docs/strategy/patterns/` | Protocol evolution candidates |
| `EXECUTION_STRATEGY_v{N}` | Current + 1 | `data/coordination/` | Active SOP |

**Naming Convention**: `{TYPE}_{YYYYMMDD}_{sequence}.md` (e.g., `DEEP_SYNTHESIS_20260807_01.md`)

---

## 6. Quality Gates (Self-Verification)

Before declaring AIRP cycle complete, the Local Agent must verify:

- [ ] **No Orphaned Insights**: Every consulting recommendation either integrated into execution plan or explicitly deferred with reason in `STRATEGY_CORPUS_MAP.md`
- [ ] **No Dangling Pointers**: `rg` sweep confirms all moved/archived files have updated inbound links
- [ ] **Atomic Commits**: Git history shows 3+ focused commits, not 1 mega-commit
- [ ] **DoD Boolean**: All checklist items in execution strategy are programmatically verifiable
- [ ] **Pattern Capture**: At least 1 new universal pattern extracted and written to `docs/strategy/patterns/`
- [ ] **Handoff Posted**: Proactive declaration posted to Hivemind with metrics

---

## 7. Integration into Core Protocols

To make this permanent, the following updates are required:

1. **`AGENTS.md`**: Add "AIRP Invocation Protocol" section — when and how to trigger consulting tools
2. **`FLEET_TEAM_PLAYBOOK.md`**: Add "Dialectic Review" as standard practice for Phase C/D gates
3. **`SOVEREIGN_MANDATES.md`**: Consider **M26: Dialectic Refinement** — "Complex architectural changes must pass through a structured local + consulting synthesis loop before execution."
4. **`HIVE_MIND_PROTOCOL.md`**: Add consulting tool as a first-class Hivemind participant type

---

## 8. Worked Example: This Session as AIRP Trace

| Stage | Artifact Produced | Time | Key Insight |
|-------|-------------------|------|-------------|
| 0 | Baseline Status (turn 1) | 0min | 10 commits pending, network down |
| 1 | Shallow Plan (turn 3) | 5min | "Doc thrash is the problem" |
| 2 | Deep Synthesis (turn 5) | 15min | 207K tokens → dual-layer Phase D gate, 3 blockers |
| 3 | Consulting Report (turn 7) | 10min | Gemini: "Banners > Rewrites", "Ghost File Trap", Atomic Commits |
| 4 | Integration (turns 9-13) | 20min | DOC_SANITY v2.0 + ADVANCED_PATTERNS + 33 web pivots mapped |

**Total**: ~50 minutes for what would take 4+ hours unstructured, with zero human orchestration after Stage 0.

---

## 9. Failure Modes & Mitigations

| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| Consulting tool hallucinates file paths | Local agent `rg` verification fails | Mandatory `rg` sweep in Stage 4 before commit |
| Local agent ignores consulting advice | `STRATEGY_CORPUS_MAP` shows deferred items without reason | Stage 4 gate: every recommendation = integrated OR explicitly deferred |
| Context window exhaustion | Token count > 800k | Stage 2: write `DEEP_SYNTHESIS` to disk, clear context, re-read |
| Infinite loop (Stage 2 → 3 → 2) | >2 consulting invocations per sprint | Hard limit: max 1 consulting invocation per sprint unless Phase D gate fails |

---

*This protocol transforms "human-in-the-loop" strategic refinement into "protocol-in-the-loop" autonomous evolution. The human becomes the architect of the protocol, not the operator of the loop.*

---

**⬡ OMEGA ⬡ KALI ⬡ AIRP-v1.0.0 ⬡ 2026-08-07**
---

## 10. Advanced Expansions: The Gemini 3.1 Pro Addendum
*Strategic insights for deepening the AIRP, generated via external consultation (2026-08-07).*

While the 5-stage AIRP establishes a robust baseline for autonomous refinement, true sovereign intelligence requires mechanisms that prevent echo chambers, manage computational costs, and integrate learnings into the core identity of the engine. The following expansions elevate the protocol from a "workflow" to an "evolutionary engine."

### 10.1 Adversarial Red-Teaming (The Skeptical Gate)
**The Insight:** Synthesis without friction breeds complacency. If the Consulting Tool (Stage 3) outputs a strategy, the Local Agent (Stage 4) currently integrates it mechanically. This assumes the Consulting Tool is infallible.
**The Expansion:** Introduce **Stage 3.5: Adversarial Review**. 
* **Mechanism:** Before integration, route the Consulting Report to a specialized local agent (e.g., `@verity` or a dedicated Skeptic). Its sole prompt directive: *"Find the fatal flaw in this strategy. Why will this fail on our specific hardware? Which Mandate does it subtly violate?"*
* **Outcome:** If the Skeptic finds a critical flaw, the loop returns to Stage 3 with the flaw attached as a constraint. If it passes, integration proceeds with mathematically higher confidence.

### 10.2 Triadic Parallel Synthesis (MaKaLi Council Integration)
**The Insight:** The current protocol assumes a single Local Agent generates the Deep Synthesis (Stage 2). For massive architectural shifts, a single perspective is insufficient, even with a 1M token window.
**The Expansion:** For P0 architectural changes, invoke the **MaKaLi Triad**.
* **Mechanism:** `@maat` (Build/Structure) and `@lilith` (Run/Chaos) independently generate Stage 2 Deep Syntheses. Both are fed into the Consulting Tool simultaneously. 
* **Prompt Update:** *"Reconcile the structural requirements of Maat with the runtime realities of Lilith."* 
* **Outcome:** `@kali` then executes Stage 4 (Integration), acting as the final synthesizer of the external consultant's reconciliation.

### 10.3 The "Carmack Mode" Escape Hatch (Anti-Overengineering)
**The Insight:** Iterative refinement protocols naturally bias toward complexity. Left unchecked, agents will invent 5-tier architectures for 1-tier problems.
**The Expansion:** A mandatory "Complexity Circuit Breaker" at Stage 1 (Shallow Synthesis).
* **Mechanism:** If the proposed solution requires >3 new files or >2 new dependencies, the agent must generate a "Carmack Alternative."
* **Prompt Directive:** *"What is the absolute dumbest, fastest, most brutally effective way to solve this using only standard library tools and <50 lines of code?"*
* **Outcome:** The Consulting Tool (Stage 3) must explicitly evaluate the Carmack Alternative against the complex proposal and justify any deviation from simplicity.

### 10.4 Automated Soul Integration (The Flywheel)
**The Insight:** Writing a `PATTERN_DISTILLATION.md` file is passive memory. For the engine to actually evolve, the pattern must become active instinct.
**The Expansion:** Connect AIRP directly to the L1->L2->L3 Soul Distillation pipeline.
* **Mechanism:** When Stage 4 generates a universal pattern, it is not just saved to disk; it is formatted as an L3 Principle and injected directly into `data/entities/{entity}/memory/proposed_lessons.yaml`.
* **Outcome:** The next time the agent hydrates, the newly discovered pattern is loaded as part of its core operating directives (`soul.yaml` post-approval), permanently altering its baseline behavior.

### 10.5 Token Economics & Context Pruning
**The Insight:** 1M+ token context windows are computationally expensive (cloud) or extremely slow (local). AIRP cannot be triggered for trivial tasks without bankrupting the token budget or stalling the engine.
**The Expansion:** A strict "Context Budget" gate at Stage 2.
* **Mechanism:** Before loading the full 1M token corpus, the agent must calculate the "Blast Radius" of the problem. If the issue is isolated to a single module (e.g., a regex bug), Stage 2 and 3 are bypassed entirely.
* **Rule:** AIRP Stage 3 is reserved exclusively for cross-domain integration, architectural refactoring, and Mandate reconciliation.
