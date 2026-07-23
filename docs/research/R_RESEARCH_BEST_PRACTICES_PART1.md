# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-22

---

## §0 Executive Summary

This guide captures **production-tested best practices** for designing autonomous agent research jobs in the Omega Engine ecosystem, synthesized from:
- 8 authoritative sources (2024-2026)
- Internal Omega Engine research (Guard & Distill campaign)
- Practical implementation lessons from GAP-001 and GAP-007 job specs
- Anthropic, Golchian, Agentmelt, Particula, and Gemini Deep Research patterns

**Purpose**: Enable consistent, high-sovereignty agents (Researcher, Ma'at, Kali, Verity, etc.) to design research jobs that are:
- **Spec-driven** (not prompt-driven)
- **Context-engineered** (not prompt-engineered)
- **Quality-gated** (with Temple-Grade, Doc Standards, Mandate alignment)
- **Living documents** (specs versioned like code)
- **Cost-aware** (token budgeting integrated with C-10.5 quota tracker)

**Scope**: Applies to all research tasks in `docs/research/` and `docs/strategy/` requiring deep investigation, synthesis, and deliverable creation.

---

## §1 Core Principles — The Foundation

### 1.1 Spec-Driven, Not Prompt-Driven (Golchian 2026)
> "The single most expensive habit in agentic development is typing a vague prompt and hoping."

**Implementation**:
- Write specs **backward from acceptance checks** (Definition of Done)
- A spec is a **contract**: behavior, constraints, verification
- **Agent drafts spec → Human reviews/fixes → Agent executes** (self-spec workflow)
- **Living spec**: Version specs like code; incidents → spec fixes, not just implementation fixes

### 1.2 Context Engineering > Prompt Engineering (Agentmelt 2026)
> "What carries a multi-turn agent is everything else you put in the context window — assembled deliberately, in the right order, with the right compression."

**Implementation**:
- **7 Context Slots** (in order):
  1. System prompt (role, scope, constraints, stopping conditions)
  2. Tool definitions (JSON schemas)
  3. Long-term memory (selective retrieval)
  4. Retrieved knowledge (RAG chunks)
  5. Conversation history (compressed)
  6. Scratchpad / working memory (explicit conclusions)
  7. Current step's instruction
- **Failure Modes to Fix** (not with better prompts):
  - **Poisoning**: Write conclusions, not raw text; validate before commit
  - **Distraction**: Compress: summarize tail, rewrite scratchpad
  - **Confusion**: Select context, don't dump; retrieve relevant subset
  - **Clash**: Explicit conflict resolution in synthesis; evidence pyramid

### 1.3 Start Simple, Add Complexity (Anthropic 2024)
> "Many patterns can be implemented in a few lines of code. Add multi-agent only when simpler solutions fall short."

**Decision Rule** (Particula 2026):
- **Single-loop agent** (or no agent): Under ~15-20 steps with tightly coupled work
- **Deep agent** (planner + filesystem + isolated subagents + memory): Beyond 15-20 steps with separable exploratory sub-tasks
- **Cost reality**: Deep agents use ~15× tokens of single chat; KV-cache hit rate becomes primary production metric

### 1.4 Point at Code, Not Ideas (Golchian 2026)
> "Give the agent the same context you would give a new engineer on their first day: here is how we do things here."

**Implementation**:
- Reference existing Omega patterns, files, conventions
- Point to specific code: `src/omega/hub/task_registry.py`, `docs/strategy/HERITAGE_VETTING_PIPELINE.md`
- Reference internal docs: `OMEGA_CODEX.md`, `SOVEREIGN_MANDATES.md`, `AGENTS.md`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-22*
*Part 1/8: Core Principles*
*This guide is a living document. Updates must be made via PR with spec-driven changes.*