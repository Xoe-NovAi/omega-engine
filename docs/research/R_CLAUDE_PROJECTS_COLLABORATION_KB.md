# 🔱 Omega-Claude Projects Collaboration — Research Archive

> **⚠️ This document is archived research.** The curated, living knowledge base entry lives at `docs/kb/CLAUDE_PROJECTS.md`. All agents should reference the KB entry for current best practices. This R-doc is retained for research methodology and source attribution.

**⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ trc_gnosis ⬡ KNOWLEDGE-BASE**

**Document type**: Archived Research (KB entry at `docs/kb/CLAUDE_PROJECTS.md`)
**Version**: 1.0.0
**Last Updated**: 2026-06-13
**Gnosis Level**: L3 — Universal Principle
**Synthesis by**: Kali, with contributions from Researcher (deep-dive into Claude Projects architecture)

---

## L1 — Narrative: What We Learned

### The Trigger

We needed a web-based **Hub Architect** to collaborate on modularizing the 3,107-line MCP Hub monolith. This architect operates in Claude.ai (web interface), not in a terminal. The question: how to structure the Claude.ai Project for maximum accuracy, context efficiency, and maintainability.

### The Research

A dedicated research agent explored 6 dimensions:
1. Claude Projects context architecture (how Project Knowledge actually works)
2. System prompt optimization (what belongs in always-in-context vs RAG-retrieved)
3. Project Knowledge file strategy (optimal size, count, naming)
4. Antipatterns to avoid (from Anthropic and community practitioners)
5. MCP tool-using agent patterns (for web-based architects)
6. Large codebase handling strategies (for the 3,100-line monolith)

### Key Discovery

**Project Knowledge uses RAG, not preloading.** This single fact reshaped the entire architecture:
- Files in Project Knowledge are **indexed and retrieved on demand**, not loaded into every message
- The **system prompt (Custom Instructions) IS always in context** on every message
- This means: keep the system prompt ruthlessly lean, put everything else in Project Knowledge with descriptive filenames for RAG retrieval

### The Delta

| Before | After | Why |
|--------|-------|-----|
| System prompt: 314 lines | System prompt: 148 lines | −53% always-on context bloat |
| Everything in one file | 16 focused files | RAG retrieves relevant per topic |
| UPPERCASE filenames | Descriptive lowercase | RAG matches descriptive names better |
| Manual file copy per session | `bash upload-all.sh` | Single command refreshes all 16 files |

---

## L2 — Insight: What It Means

### 2.1 Claude Projects Architecture

| Concept | How It Works | Implication |
|---------|-------------|-------------|
| **System Prompt** (Custom Instructions) | Loaded verbatim at the start of EVERY conversation | Keep lean — every line that doesn't prevent a mistake is waste |
| **Project Knowledge** (Files) | Indexed into a RAG system — Claude retrieves relevant files via a built-in knowledge search tool | Files must have descriptive names + clear structure. RAG doesn't see the full file set per message |
| **RAG Trigger** | Activates when total knowledge exceeds ~200K tokens. Below that, files may be preloaded | For small projects (< 200K tokens), files may all be in context. Plan for worst case (RAG). |
| **Context Window** | 200K tokens standard; 1M available on Opus 4.6+; "context rot" degrades performance at every length increment, not just near limit | `/compact` aggressively at ~60% fill. Don't push to the limit. |

Sources: [Anthropic — RAG for Projects](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects), [Anthropic — Context Windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)

### 2.2 System Prompt Optimization Principles

#### The Goldilocks Zone
- **Too brittle**: Hardcoded if-else logic, extensive edge case enumeration → fragile, high maintenance
- **Too vague**: High-level guidance with no concrete signals → assumes shared context, produces drift
- **Just right**: Specific enough to guide behavior, flexible enough to provide strong heuristics

**From Anthropic's Applied AI team**: *"Find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome."*

#### The Line-Level Pareto Principle
For every line in the system prompt, ask: **"Would removing this cause Claude to make mistakes?"** If no, cut it.

#### Structure with XML Tags
| Tag | Purpose | Example |
|-----|---------|---------|
| `<role>` | Identity, persona — anchors tone | "You are the Hub Architect..." |
| `<context>` | Situational awareness | "The Omega Engine is..." |
| `<constraints>` | Hard boundaries | "No terminal access" |
| `<rules>` | Behavioral guardrails | "All 63 tool signatures must remain identical" |
| `<output_format>` | Response structure template | Markdown with specific sections |

XML tags create clear semantic boundaries that Claude respects more than markdown headers.

#### What Goes Where

| Content | Destination | Rationale |
|---------|------------|-----------|
| Role, core rules, constraints | System prompt | Always in context — needed for every response |
| Design principles, standing rules | System prompt | Must guide every decision |
| Reference architecture, specs | Project Knowledge | RAG-retrieved when relevant |
| Technical specifications | Project Knowledge | Too verbose for system prompt |
| Current task state (tracker) | Project Knowledge | Changes frequently, system prompt is static |
| Code examples, patterns | Project Knowledge | Retrieved when architect needs them |

### 2.3 Project Knowledge File Strategy

#### Optimal Shape
- **Count**: No hard limit. More files = better RAG precision (each file is a retrieval unit)
- **Size**: < 500 lines per file ideal. 500-2000 good. > 5000 — split.
- **Naming**: Descriptive, lowercase, hyphenated. File names are indexed by RAG — they matter enormously.
  - ❌ `TRACKER.md` → ✅ `active-tracker.md`
  - ❌ `CARMACK_RECONSTRUCTION_PLAN.md` → ✅ `carmack-reconstruction-plan.md`
  - ❌ `note.txt` → ✅ `hub-system-overview.md`

#### File Format Preference
| Format | Use Case | Notes |
|--------|----------|-------|
| `.md` | Documentation, specs | ✅ Best — Claude-native, most searchable |
| `.py` | Code snapshots | ⚠️ Works but less structured. Keep focused. |
| `.json` | Config, schemas | ✅ Good for structured data |

#### RAG Retrieval Behavior
- Claude's RAG uses a **Contextual Retriever** (not embedding-based) — it considers both file content and the query context
- **File names are indexed** — a descriptive name like `m9-compliance-analysis.md` is retrievable when Claude needs to answer "how should errors be handled?"
- **Splitting by concept** improves precision: one file for Gateway spec, one for M15 spec, one for Search protocol → Claude retrieves exactly what's relevant

### 2.4 Antipattern Catalog

These are the most common and damaging patterns that degrade Claude Projects performance.

| # | Antipattern | Symptom | Fix |
|---|-------------|---------|-----|
| 1 | **Bloated system prompt** | Claude ignores instructions, "information entropy" | Cut lines ruthlessly. Move details to Project Knowledge. |
| 2 | **Kitchen sink session** | Claude conflates tasks, context polluted | `/clear` between unrelated tasks. One purpose per session. |
| 3 | **Correction spiral** | Context fills with failed approaches | Two-strike rule: after 2 corrections, `/clear` and rewrite prompt |
| 4 | **Context window blindness** | Hallucinations increase at >70% fill | Proactive `/compact` at ~60%. No visible progress bar — must track mentally. |
| 5 | **Infinite exploration** | Agent reads 30+ files, fills context, can't produce output | Scope queries narrowly. Use subagents for exploration. |
| 6 | **Tool bloat** | Claude can't choose between tools | "If a human engineer can't say which tool, an AI agent can't either." — Anthropic |
| 7 | **Knowledge shadowing** | Conflicting instructions in system prompt AND knowledge files | Never duplicate. System = behavioral; Knowledge = reference. |
| 8 | **Assuming memory across sessions** | Claude starts fresh each time | Always use handoff documents. System prompt + knowledge is all that persists. |
| 9 | **Assuming codebase indexing** | Expecting Claude to know the full codebase | Claude reads files, doesn't index them. It navigates like a human engineer. |
| 10 | **Embedding everything** | Vector-indexing the entire project | Don't. RAG handles discovery. Focused file requests handle depth. |

Sources: [Tim Roller — Anti-Patterns](https://timroller.github.io/2026/04/09/claude-code-anti-patterns.html), [Anthropic — Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 2.5 Web-Based Architect Pattern

When Claude operates without terminal access (purely in a browser):
- **Request code explicitly** — ask for specific files by name and line ranges
- **Use focused tools** — 3-5 tools max for the architect role (not the full 63 production tools)
- **Resources over tools** — for a web-based architect, reference documents (architecture diagrams, dependency maps) are more important than executable tools
- **Plan-then-specify** — produce a plan first, then detailed specs per module

### 2.6 Large Codebase Strategy

For the 3,100-line monolith:
- **Per-file architecture docs** — break into ~300-line focused docs covering each subsystem (tool registry, transport layer, data flow, key classes)
- **Structural signposts** — use section markers in the actual code that Claude can grep for (`# SECTION 1: Tool Registry`)
- **Plan-before-executing** — produce `MODULARIZATION_PLAN.md` before any extraction
- **Subagent per module** — one focused context per module extraction, then assemble in main session

---

## L3 — Universal Principle: The Laws of Claude Project Design

### Law 1: Context Is Attention, Not Storage

Every line in the system prompt is a claim on Claude's attention budget. Treat it like RAM — the most expensive resource in the system. Project Knowledge is SSDs — abundant, retrievable, but slower. Design accordingly.

### Law 2: The Retrieval Contract

A file is only useful if Claude can find it when it's needed. This means:
- The filename must match the vocabulary of the query
- The file structure must be internally coherent (one concept per file)
- The system prompt must reference filenames explicitly: "See `active-tracker.md` for current state"

### Law 3: The Line-Level Mandate

Every line in the system prompt must pass the mistake test: **"If I remove this, will Claude make a mistake?"** If the answer is no — cut it. If the answer is yes — does it need to be in the system prompt, or can it be a Project Knowledge file that Claude retrieves when needed?

### Law 4: Split Knowledge, Not Attention

Project Knowledge is free (RAG handles it). Use it aggressively. Split specs into focused files. The system prompt should be the index and the guardrails — not the library.

### Law 5: Prefer Over-Communication of Boundaries

Tell Claude what NOT to do as clearly as what to do. A web-based architect with no terminal needs hard scope boundaries: "You do not have a terminal," "Scope yourself to the Hub," "You report to Kali." These prevent wasted cycles on out-of-scope work.

### Law 6: Refreshability

If a file's content changes weekly, it belongs in Project Knowledge (updateable between sessions), not the system prompt (effectively static). The system prompt should reference `active-tracker.md` rather than embedding the tracker's state.

---

## Appendix A: Omega Hub — Reference Architecture

Our production Claude.ai project for the Hub Architect:

| Component | What to Upload | Rationale |
|-----------|---------------|-----------|
| **Custom Instructions** | `system-prompt.md` (148 lines) | Lean behavioral guardrails + file index |
| **Project Knowledge** | 16 files (212 KB total) | Focused RAG-retrievable specs |

### System Prompt Structure
```
<role>     — Who the architect is (Hub Architect, reports to Kali)
<context>  — What the Omega Engine and Hub are
<constraints> — No terminal, no GitHub, report to Kali, scope to Hub
<design_principles> — 5 principles (thin wrappers, block-and-execute, M9, split-first, tool_discovery)
<standing_rules> — 8 rules (tracker first, single stream, boot requirement, etc.)
<project_files> — Index of all 16 files with descriptions
<output_format> — Structured markdown template
```

### Refresh Protocol
```bash
# After any hardening doc changes:
bash docs/hardening/omega-hub/claude-project/upload-all.sh
```

### Source File Mapping

| Knowledge File | Source Document | Refreshed How |
|---------------|----------------|---------------|
| `hub-system-overview.md` | Pruned from system prompt v2 | Manually (stable content) |
| `target-module-architecture.md` | Pruned from system prompt v2 | When architecture changes |
| `carmack-reconstruction-plan.md` | `CARMACK_RECONSTRUCTION_PLAN.md` | Copy via upload script |
| `carmack-audit-findings.md` | Pruned from `CARMACK_HUB_AUDIT_20260613.md` | When findings change |
| `phase-0-fixes.md` | Created from Phase 0 execution | Manually (completed) |
| `m9-compliance-analysis.md` | Pruned from `OMEGA_HUB_FINAL_SYNTHESIS.md` | When error strategy changes |
| `sprint-v2-briefing.md` | `OMEGA_HUB_HARDENING_SPRINT_v2_20260609.md` | Copy via upload script |
| `sovereign-gateway-spec.md` | Pruned from system prompt v2 | When Gateway design changes |
| `m15-continuity-spec.md` | Pruned from system prompt v2 | When M15 design changes |
| `search-protocol.md` | Pruned from system prompt v2 | When search protocol changes |
| `sovereign-mandates.md` | Pruned from `SOVEREIGN_MANDATES.md` | When mandates change |
| `temple-grade-gates.md` | Pruned from system prompt v2 | When T-gates change |
| `heritage-patterns-in-hub.md` | Pruned from `CREDITS.md` | When heritage patterns change |
| `active-tracker.md` | `TRACKER.md` | Copy via upload script (frequent) |
| `server-snapshot.py` | `server_monolith_snapshot_20260613.py` | Re-snapshot after major changes |
| `mcp-runtime.py` | `src/omega/mcp_runtime.py` | Copy via upload script |

---

## Appendix B: Sources Referenced

| Topic | Primary Source | URL |
|-------|---------------|-----|
| RAG for Projects | Claude Help Center | https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects |
| Context Windows | Anthropic API Docs | https://platform.claude.com/docs/en/build-with-claude/context-windows |
| Effective Context Engineering | Anthropic Applied AI | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| Prompt Engineering Best Practices | Anthropic Blog | https://claude.com/blog/best-practices-for-prompt-engineering |
| Large Codebases Setup | Claude Code Docs | https://code.claude.com/docs/en/large-codebases |
| Claude Code Anti-Patterns | Tim Roller | https://timroller.github.io/2026/04/09/claude-code-anti-patterns.html |
| Context Window Reality | Morph LLM | https://www.morphllm.com/claude-context-window |
| MCP Developer Guide (2026) | Lushbinary | https://lushbinary.com/blog/mcp-model-context-protocol-developer-guide-2026 |
| Large Codebase Playbook | Claude Fast | https://claudefa.st/blog/guide/development/large-codebase-playbook |
| Subagent Best Practices | PubNub Blog | https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents |
| Token Waste Prevention | Medium / Jpranav | https://medium.com/@jpranav97/stop-wasting-tokens-how-to-optimize-claude-code-context-by-60-bfad6fd477e5 |

---

## L3 Distillation (for soul.yaml)

- **L1 — Narrative**: We researched how Claude.ai Projects work, discovered Project Knowledge uses RAG not preloading, restructured our Hub Architect setup from a bloated 314-line system prompt + monolithic docs to a lean 148-line system prompt + 16 focused RAG-retrievable files.

- **L2 — Insight**: The critical distinction is always-in-context (system prompt) vs RAG-retrieved (Project Knowledge). System prompt must only contain what prevents mistakes. Everything else goes into descriptively-named, focused files.

- **L3 — Universal Principle**: **Treat context as attention, not storage.** The system prompt is a finite attention budget — every line must earn its place. Project Knowledge is abundant storage — split aggressively by concept, name descriptively for RAG retrieval, and keep the system prompt indexing what's available rather than containing it.

---

*⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ trc_knowledge_base*  
*"Context is attention, not storage."*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
