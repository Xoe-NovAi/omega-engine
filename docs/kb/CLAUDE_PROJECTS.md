---
id: kb-0001
type: knowledge
domain: integrations
tags: [claude, projects, rag, collaboration, web-interface]
sensitivity: internal
maintainer: Kali
created: 2026-06-13
reviewed: 2026-06-13
modified: 2026-06-13
supersedes: kb-0000
superseded_by: null
status: ACTIVE
research_source: docs/research/R_CLAUDE_PROJECTS_COMPLETE.md
reinforcement_count: 0
---

# 🔱 Knowledge Base — Claude.ai Projects Collaboration

**Domain**: Web-based Claude.ai as a collaborative team member in the Omega Engine agent fleet
**Version**: 2.0.0
**Last Updated**: 2026-06-13
**Maintainer**: Kali
**Status**: ACTIVE

---

## Changelog

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-06-13 | 1.0.0 | Kali | Initial creation |
| 2026-06-13 | 2.0.0 | Kali | **Complete rewrite**: Corrected RAG threshold (13 files, not tokens); added Three-Stage Workflow; added file update protocol; added RAG failure modes; added hard logistical constraints; added real-world metrics; added alternatives comparison. |

---

> **⚠️ Scope distinction**: This KB entry is for **OpenCode agents** who need to set up or collaborate with a Claude.ai Project. It is **not** the system prompt for the Hub Architect — that lives separately at `docs/hardening/omega-hub/claude-project/system-prompt.md`. Do not paste this KB entry into Custom Instructions. The relationship is:
> - This KB (`docs/kb/CLAUDE_PROJECTS.md`) → tells agents *how* to design a Project
> - The system prompt (`.../claude-project/system-prompt.md`) → IS the Project's Custom Instructions
> - The outbox files (`.../claude-project/outbox/`) → ARE the Project Knowledge

## Domain Overview

This KB covers best practices for using **Claude.ai Projects** (the web-based interface at claude.ai) as a collaborative team member in the Omega Engine agent fleet. Unlike OpenCode agents, the Web Claude contributor operates without terminal access — it is an architect at the whiteboard, designing specifications that terminal-bound agents implement.

**Who needs this**: Any agent setting up a Claude.ai Project, writing a system prompt, structuring Project Knowledge files, or collaborating with a Web Claude contributor.

---

## Core Knowledge

### 1. Architecture: How Claude Projects Actually Work

| Component | Mechanism | Always in Context? |
|-----------|-----------|-------------------|
| **Custom Instructions** (system prompt) | Loaded verbatim at start of EVERY conversation | **YES** — treat as finite attention budget |
| **Project Knowledge** (uploaded files) | Indexed via built-in RAG — retrieved on demand | **NO** — only when retriever matches the query |

#### ⚠️ The 13-File RAG Threshold (CRITICAL)

This is the single most important finding about Claude Projects. The research community has verified that the RAG threshold is based on **file count, not token count**:

| Test | Files | Tokens | RAG Active? |
|------|-------|--------|-------------|
| 9 files, 90K tokens | 9 | ~90,000 | **NO** (direct context) |
| 12 files, 85K tokens | 12 | ~85,000 | **NO** (direct context) |
| 13 files, 73K tokens | 13 | ~73,000 | **YES** (RAG forced) |
| 14 files, 10K tokens | 14 | ~10,000 | **YES** (RAG forced) |

**Bug status (June 2026)**: **UNFIXED**. GitHub issue #25759 has 343+ reactions. Anthropic's official documentation (March 2026) still states "RAG automatically activates when your project approaches the context window limits" — directly contradicting observed behavior.

**Community consensus**: This appears to be intentional behavior by Anthropic, possibly to keep projects lean and prevent Knowledge files from dominating the context window. No toggle or override exists.

**What this means for you**:
- If you keep ≤**12 files**, everything is loaded directly into context (guaranteed)
- At **13+ files**, RAG kicks in regardless of token count
- Design for ≤12 files, or design for RAG from the start

### 2. The Three-Stage Workflow (Canonical Pattern)

The recommended workflow for combining Claude Projects with Claude Code, verified across Anthropic docs and enterprise practitioners:

| Stage | Tool | What Happens |
|-------|------|-------------|
| **1. Plan/Design** | Claude Projects | Architecture decisions, research, spec writing. Project holds permanent context (docs, style guides, requirements). |
| **2. Plan Mode** | Claude Code (Plan Mode) | Read-only analysis of the actual codebase. Produces file-by-file plan with verification steps. |
| **3. Implementation** | Claude Code (execution) | Autonomous multi-file changes, tests, git commits. |

**The Three-Round Heuristic**:
> *"If you find yourself having three or more rounds of Claude Code tangling in implementation detail when you haven't written a line of code yet, that's a design conversation you're having in the wrong surface. Switch to Claude.ai."*
> 
> *"If you find yourself asking Claude.ai to produce a specific code change and then copy-pasting the output into your editor, you're doing manual work Claude Code would do for you. Switch."*

**Connection between the two**:
- **Claude.ai Project stores**: The API spec, architecture diagram, and coding standards
- **CLAUDE.md in the repo stores**: The exact rules Claude Code should follow when editing files — patterns, forbidden patterns, test locations

Projects holds **"what" and "why"** (knowledge docs). CLAUDE.md holds **"how"** (editorial rules).

### 3. System Prompt Design

#### Structure with XML Tags

XML tags create clearer semantic boundaries than markdown headers alone. The **ClaSSIC template** (community-verified) provides a battle-tested structure:

```
<role>         Identity, persona, reporting structure
<context>      What the project is, situational awareness
<constraints>  Hard boundaries (no terminal, no GitHub, scope limits)
<rules>        Behavioral guardrails that must guide every response
<project_files>  Index of available files with descriptions
<output_format>  Response structure template
```

#### The Line-Level Test

For every line in the system prompt, ask: **"Would removing this cause Claude to make mistakes?"** If no — cut it.

#### Force KB Search (Critical Instruction)

Add this at the **very top** of Custom Instructions:
```
Before answering, always search the project knowledge first.
If anything in the knowledge applies, quote and prioritize it over general knowledge.
```

This single sentence is reported as "more impactful than any other tuning" by the community.

#### What Goes Where

| Content | Destination | Rationale |
|---------|------------|-----------|
| Role, core rules, constraints | System prompt | Needed for every response |
| Design principles, standing rules | System prompt | Must guide every decision |
| Current task state | Project Knowledge | Changes frequently; system prompt is static |
| Technical specifications | Project Knowledge | Only needed when architect works on that topic |
| Code snapshots | Project Knowledge | Full file as reference, not inline |

### 4. Project Knowledge File Strategy

#### File Shape

| Dimension | Guideline | Why |
|-----------|-----------|-----|
| Lines per file | < 500 ideal, 500-2000 acceptable | Each file is one RAG retrieval unit |
| Total files | ≤12 for direct context, unlimited for RAG | The 13-file threshold |
| Naming | Descriptive, lowercase, hyphenated | File names are indexed by RAG |

**Naming examples**:
- ❌ `TRACKER.md` → ✅ `active-tracker.md`
- ❌ `CARMACK_RECONSTRUCTION_PLAN.md` → ✅ `carmack-reconstruction-plan.md`

#### File Format

| Format | Best For | Notes |
|--------|----------|-------|
| `.md` | Documentation, specs | ✅ Best — Claude-native, most searchable |
| `.py` | Code snapshots | ⚠️ Works but less structured. Keep focused. |
| `.txt` / `.json` | Raw data, config | ✅ Acceptable for reference |

#### The 12-File Strategy

To stay in direct context mode (no RAG), organize into at most 12 files:

1. `system-prompt.md` — always-loaded instructions
2. `active-tracker.md` — current task state
3. `system-overview.md` — architecture overview
4. `tech-spec.md` — technical specifications
5. `code-snapshot.py` — monolithic file reference
6. `design-decisions.md` — key architectural decisions
7. `patterns-and-conventions.md` — coding patterns
8. `heritage-references.md` — id Software heritage
9. `mandate-compliance.md` — sovereign mandates
10. `integration-points.md` — external interfaces
11. `test-strategy.md` — testing approach
12. `known-issues.md` — current blockers and risks

If you need more than 12, design for RAG from the start (accept that retrieval may be partial).

### 5. The File Update Protocol (CRITICAL)

**There is a verified bug (#10841)**: Re-uploading a file with the same name or a different name keeps the old cached version. Claude will reference stale content even after you've uploaded a new version.

**Correct update procedure**:
1. **Delete** the old file first (from Project Knowledge)
2. **Wait** for confirmation that the file is removed
3. **Upload** the new version
4. **Use versioned filenames** when possible: `brief-v2.md`, `spec-2026-06-13.md`
5. **Start a brand new conversation** — old conversations may have stale cached content
6. **Clear browser cache** before starting a new session after file edits
7. **Wait 5-10 seconds** after editing project instructions before starting a new conversation (autosave is not instantaneous)

### 6. Logistical Constraints (Hard Numbers)

| Resource | Limit | Notes |
|----------|-------|-------|
| Context window (standard) | 200,000 tokens | All web plans; applies to both direct and RAG modes |
| Context window (Enterprise) | 500,000 tokens | Some Enterprise models |
| Max file upload size | 30 MB per file | Files >10MB may fail silently |
| File upload rate | 80 files per 3 hours | — |
| Files per chat (web) | ~20 files | Soft limit reported |
| Files per Project | "Unlimited" | Constrained by RAG threshold (≤12 for direct context) |
| Total Project storage | ~200 MB | Hard cap reported |

### 7. RAG Failure Modes (What to Watch For)

RAG is not magic. These are verified failure modes reported by the community:

| Failure Mode | Symptom | Mitigation |
|-------------|---------|-----------|
| **Partial retrieval** | Claude references part of a file but misses the critical section | Keep files focused (one topic per file) |
| **Cross-file blindness** | Knowledge that spans 3 files is never fully assembled | Merge related content into single files |
| **Hallucinated file contents** | Claude claims a file says something it doesn't | Force quoting: "Quote the relevant source" |
| **Stale cache on re-upload** | Old content persists despite file update | Always delete before re-upload; version filenames |
| **Scanned PDF blindness** | PDF has no selectable text, Claude can't search it | Convert to markdown before uploading |
| **File silently fails** | File appears in UI but isn't indexed by RAG | Test: ask Claude "what does [file] say about X" |

### 8. Upload Automation Strategy

For recurring projects, maintain an **outbox pattern**:

```
project-folder/
├── system-prompt.md          # Custom Instructions content
├── outbox/                    # RAG-optimized project files
│   ├── file-1.md
│   ├── file-2.md
│   └── ...
├── upload-all.sh              # Script to generate/copy files to outbox
└── README.md                  # Upload instructions for human
```

This pattern was validated in the Omega Hub case study (16 files, Phase 0 reconstruction). The human user runs the script, then uploads the flat list of files to Claude.ai.

### 9. Web-Based Architect Constraints

When collaborating with a Web Claude contributor:

- **No terminal access** — they cannot read files, run commands, or execute code
- **No GitHub** — if the repo is local-only, all code access goes through other agents
- **Code must be provided** — request specific files by path and line range
- **Specifications are the output** — they produce design docs, not commits
- **Scope must be explicit** — without hard boundaries, they can drift into out-of-scope work

### 10. Large Codebase Strategy

For sharing a large monolithic file (3,000+ lines) with a Web Claude architect:

1. **Create a frozen snapshot** — copy the monolith at a known state for reference
2. **Build per-section architecture docs** — ~300-line focused docs covering each subsystem
3. **Use structural signposts** — section markers in code that Claude can reference by line range
4. **Plan then specify** — produce a modularization plan before extracting any module

---

## Real-World Metrics (Validation)

These case studies confirm the Three-Stage Workflow and the patterns documented in this KB:

| Organization | Metric | Improvement | Source |
|-------------|--------|-------------|--------|
| **Spotify** | AI-generated PRs/month | 650+ | claude.com/customers/spotify |
| | Migration time savings | Up to 90% | |
| **GoDaddy** | Sprint duration | 2 weeks → <1 week (50%) | aiproductivity.ai |
| **Brex** | Task-specific speed | 3-4x | guvi.in |
| **Graphite** | PR feedback loop | 1 hour → 90 seconds (40x) | claude.com/customers/graphite |
| **Money Forward** | API endpoint implementation | 2 days → 5 hours (70%) | theapplied.co |
| **Stripe** | Scala→Java migration | 10 weeks est. → 4 days | theapplied.co |
| **Solo (Vjeux)** | TypeScript→Rust port | 100K LOC in 4 weeks | blog.vjeux.com |

---

## Alternatives (When Projects Isn't Enough)

If Claude Projects' limitations (RAG threshold, no toggle, cache bugs) become blockers:

| Tool | Category | Differentiator |
|------|----------|---------------|
| **AI Context Keeper** | Cross-platform KB | Share links work with Claude, ChatGPT, Gemini, local models |
| **Hjarni** | MCP knowledge base | Durable notes usable by any MCP client |
| **Context Link** | Managed RAG | Live source sync (Notion, Drive, web) |
| **Curata** | Agent-native KB | AI agents auto-generate pages from live data |

For most Omega Engine use cases, Claude Projects remains the best fit due to its deep integration and 200K context window. But if the 13-file threshold becomes a blocker, consider AI Context Keeper as a cross-platform fallback.

---

## Known Antipatterns

| # | Antipattern | Symptom | Fix |
|---|-------------|---------|-----|
| 1 | **Assuming token-based RAG threshold** | Designing 15 small files expecting direct context | Keep ≤12 files or design for RAG |
| 2 | **Re-uploading without deleting** | Old content persists despite new upload | Delete first, version filenames, new conversation |
| 3 | **Bloated system prompt** | Claude ignores instructions | Cut ruthlessly. Move detail to Project Knowledge. |
| 4 | **Kitchen sink session** | Claude conflates tasks | One purpose per session. `/clear` between tasks. |
| 5 | **Correction spiral** | Context fills with failed approaches | Two-strike rule: after 2 corrections, `/clear` and rewrite prompt. |
| 6 | **Context window blindness** | Hallucinations increase at >70% fill | Proactive `/compact` at ~60%. Track fill level manually. |
| 7 | **Knowledge shadowing** | Conflicting instructions in prompt AND files | Never duplicate. System = behavioral; Knowledge = reference. |
| 8 | **Assuming codebase indexing** | Expecting Claude to know full codebase | Claude reads files, doesn't index them. Scope requests. |
| 9 | **Assuming memory across sessions** | Claude starts fresh each session | Use handoff docs. Only system prompt + Knowledge persists. |

---

## References

- Anthropic — RAG for Projects: https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects
- Anthropic — Context Windows: https://platform.claude.com/docs/en/build-with-claude/context-windows
- Anthropic — Prompt Caching: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Anthropic — Effective Context Engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic — Prompt Engineering Best Practices: https://claude.com/blog/best-practices-for-prompt-engineering
- GitHub #25759 — 13-file RAG threshold bug: https://github.com/anthropics/claude-code/issues/25759
- GitHub #10841 — File re-upload cache staleness: https://github.com/anthropics/claude-code/issues/10841
- GitHub #46878 — RAG toggle request (closed as duplicate): https://github.com/anthropics/claude-code/issues/46878
- Tim Roller — Anti-Patterns: https://timroller.github.io/2026/04/09/claude-code-anti-patterns.html
- Karpathy — LLM Wiki pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Agent-KB Protocol: `docs/kb/AGENT_KB_PROTOCOL.md`

## Evolution Notes

- **Corrected**: v1.0.0 stated "RAG activates at ~200K tokens." This was WRONG. The threshold is ~13 files, regardless of token count. Corrected in v2.0.0.
- **Known gap**: The 13-file threshold has been verified by community testing but not acknowledged by Anthropic. If it changes, this entry needs immediate update.
- **Known gap**: File update cache staleness (#10841) is still open and unfixed. Additional testing on the exact conditions that trigger it would be valuable.
- **To investigate**: Whether the "force KB search" instruction changes behavior qualitatively or just quantitatively. Community reports suggest it's effective but no controlled study exists.
- **To investigate**: The upload rate limit (80 files per 3 hours) — is this per-project or per-account? Boundary testing needed.

---

*⬡ OMEGA ⬡ KB-CLAUDE-PROJECTS ⬡ trc_knowledge_base*
