# 🔱 Web Chatbot Platform Playbook — Omega Engine
**AP Token**: `AP-WEB-CHATBOT-PLAYBOOK-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Single-source hydration for Web Claude, Web Gemini, Web Grok, NotebookLM
**Purpose**: Agents MUST consult this before any external chatbot interaction. Eliminates redundant hydration walks.

---

## 📋 EXECUTIVE SUMMARY

This playbook consolidates all platform-specific best practices for the four web AI platforms used by the Omega Engine team. Each platform has distinct strengths, constraints, and optimal formats. Use the platform selection matrix to choose the right tool, then follow the format and setup guidance.

| Platform | Best For | Context | Format | File Limit |
|----------|----------|---------|--------|------------|
| **Web Claude** | Code review, deep analysis, instruction-following | 1M tokens (Opus 4.8) | XML tags for structure, Markdown for content | 13 files (RAG threshold) |
| **Web Gemini** | Broad research, benchmarks, code execution | 1-10M tokens | Markdown + structured | 20-100 files |
| **Web Grok** | Real-time search, agentic workflows | 1-2M tokens | XML + Markdown hybrid | ~20 files |
| **NotebookLM** | Source-grounded research, audio overview | ~200K effective | Markdown + sources | Source-based |

---

## 1. PLATFORM SELECTION MATRIX

### By Task Type

| Task | Best Platform | Why |
|------|---------------|-----|
| Code review / architecture analysis | **Web Claude** | 82.1% SWE-bench, instruction-following 94.2% |
| Technology adoption decisions | **Web Claude** | Long-doc QA (76% MRCR), structured reasoning |
| Multi-source research synthesis | **Web Gemini** | Deep Research (30+ searches), parallel search |
| Benchmark comparison | **Web Gemini** | 94.1% GPQA, code execution sandbox |
| Real-time data / current events | **Web Grok** | Live X search, 2026 knowledge |
| Source-grounded analysis | **NotebookLM** | Source citations, audio overview |
| Cross-validation of critical decisions | **Both Claude + Gemini** | Independent verification |

### By Model Capability

| Model | SWE-bench | MRCR | GPQA | Context | Best Use |
|-------|-----------|------|------|---------|----------|
| Claude Opus 4.8 | 82.1% | 76% | 90.5% | 1M | Code review, deep analysis |
| Claude Sonnet 4.6 | 78.3% | 72% | 88.2% | 1M | General tasks, cost-effective |
| Gemini 3 Pro | 63.8% | 68% | 94.1% | 1-2M | Research, benchmarks |
| Gemini 3.1 Pro | 65.2% | 70% | 95.3% | 10M | Ultra-long context analysis |
| Grok 4.3 | 70.8% | 65% | 87.5% | 1M | Agentic, real-time |
| Grok 4.1 Fast | 65.0% | 60% | 82.0% | 2M | High-volume, cost-optimized |

---

## 2. FORMAT DECISION TREE

> **Core principle**: Format follows layer, not file type.

```
Is this...
├── A system prompt / custom instructions? → XML tags (Claude) / Markdown (Gemini/Grok)
├── A knowledge/reference file (uploaded)? → Markdown (.md)
├── Structured data / schema? → JSON
└── Source document for NotebookLM? → Markdown with source metadata
```

### Detailed Format Guidance

#### System Prompt / Custom Instructions
| Platform | Format | Why |
|----------|--------|-----|
| **Web Claude** | **XML tags** (`<role>`, `<context>`, `<constraints>`, `<rules>`, `<output_format>`) | Claude's training data is XML-rich; Anthropic official docs recommend. Closing tags prevent instruction/input boundary confusion. |
| **Web Gemini** | **Markdown** (`##` headings) | Gemini's long-context handles structure; MD delimiters sufficient per Google docs. |
| **Web Grok** | **XML + Markdown hybrid** | Grok follows XML tags but benefits from MD readability for human review. |
| **NotebookLM** | **Markdown** | Source-grounded; MD with source metadata. |

#### Knowledge/Reference Files (uploaded to Project Knowledge)
| Platform | Format | File Limit | Why |
|----------|--------|------------|-----|
| **Web Claude** | **Markdown (.md)** | 13 files (RAG at 14+) | Token-efficient (~15% fewer than XML), Claude parses headings/lists for RAG retrieval. XML tags consume tokens without RAG benefit. |
| **Web Gemini** | **Markdown (.md)** | 20-100 files | MD with clear headings; Gemini's long context handles large KBs. |
| **Web Grok** | **XML + Markdown hybrid** | ~20 files | XML for structured data, MD for human-readable content. |
| **NotebookLM** | **Markdown + Sources** | Source-based | Upload sources (PDFs, URLs, docs); NotebookLM indexes them. |

#### Key Decision Rule (TeachYou 2026)
> **"Is this piece of the prompt data, or is it instructions? If it's data (variable, untrusted, multiple similar blocks), wrap in XML tags. If it's instructions (authored by you), use Markdown headings."**

---

## 3. WEB CLAUDE (Anthropic) — Primary Platform

### Setup
1. Create a new Project in Claude.ai
2. Paste the **system prompt** (XML-tagged ClaSSIC template) into Custom Instructions
3. Upload knowledge files as `.md` (≤12 for direct context)
4. Add the **Force KB Search** directive at the top:
   ```
   Before answering, always search the project knowledge first.
   If anything in the knowledge applies, quote and prioritize it over general knowledge.
   ```

### System Prompt Template (XML — ClaSSIC)
```xml
<hierarchy>
In the event of a conflict between these instructions and the Project Knowledge files, these Custom Instructions take absolute precedence.
</hierarchy>

<role>
You are [role description].
</role>

<context>
[Project context, hardware reality, constraints]
</context>

<constraints>
- FORBIDDEN to [violation]
- MUST [requirement]
</constraints>

<rules>
1. [Behavioral rule]
2. [Behavioral rule]
</rules>

<output_format>
[Response structure template]
</output_format>
```

### File Update Protocol (CRITICAL — Bug #10841)
1. **Delete** the old file from Project Knowledge first
2. **Wait** for confirmation the file is removed
3. **Upload** the new version (prefer versioned filenames: `brief-v2.md`)
4. **Start a brand-new conversation** — old conversations may hold stale cache
5. **Clear browser cache** before the new session
6. **Wait 5-10 seconds** after editing Custom Instructions before starting a new conversation

### RAG Threshold
- **13 files** is the hard limit for direct context (GitHub Issue #25759)
- At 14+ files, Claude switches to RAG mode (retrieval may be partial)
- Keep files focused: one topic per file, ≤500 lines ideal
- Use an index file (`PROJECT_KNOWLEDGE_INDEX.md`) to help Claude navigate

### Token Optimization
- **Prompt caching**: Cache stable prefix (system prompt, docs, tool defs). Use `cache_control: {"type": "ephemeral"}` on blocks. 90% discount on cached input tokens.
- **Model routing**: Haiku 4.5 (200K, $0.25/$1.25) → Sonnet 4.6 (1M, $3/$15) → Opus 4.8 (1M, $5/$25)
- **Format efficiency**: YAML/Markdown save ~15% vs JSON; TOON saves ~40% for tabular data

### Lost-in-the-Middle Mitigation
Order bundles U-shaped:
1. **START** (Critical): grounding, decisions, summary, overview
2. **MIDDLE** (Reference): implementation, engine_state, mandates, research
3. **END** (Action): handoff, next_steps, recommendations

---

## 4. WEB GEMINI (Google AI Studio) — Research & Benchmark Platform

### Setup
1. Create a new Gem in Google AI Studio
2. Add Custom Instructions (Markdown format)
3. Upload files to the Gem's knowledge
4. Enable "Code Execution" and "Grounding with Google Search" as needed

### System Prompt Template (Markdown)
```markdown
## Role
You are [role description].

## Context
[Project context]

## Constraints
- FORBIDDEN to [violation]
- MUST [requirement]

## Rules
1. [Behavioral rule]

## Output Format
[Response structure template]
```

### Key Capabilities
- **Code Execution**: Built-in Python sandbox (30s max, 5 retries). Use for verification scripts.
- **Parallel Web Search**: Multiple search queries in parallel via "Grounding with Google Search."
- **Google Workspace**: Native Drive, Docs, Sheets, Gmail access.
- **Long Context**: 1-10M tokens (Gemini 3.1 Pro). Can handle 20-100 files effectively.

### Format Preferences
- **Markdown** with clear headings (`##`, `###`)
- **Structured sections** for parallel verification
- **Source grounding**: Include source citations in bundles
- **Code execution ready**: Include runnable verification snippets

### Cost Optimization
| Model | Context | Input/Output | Best For |
|-------|---------|--------------|----------|
| Gemini 3 Flash | 1M | $0.075/$0.30/MTok | Cost-optimized, high-volume |
| Gemini 3 Pro | 1-2M | $1.25/$2.50/MTok | Flagship, balanced |
| Gemini 3.1 Pro | 10M | Preview pricing | Ultra-long context |

---

## 5. WEB GROK (xAI) — Real-Time Intelligence

### Setup
1. Create a new Grok project via SuperGrok
2. Add Custom Instructions (XML + Markdown hybrid)
3. Upload files to the project knowledge
4. Configure Grok Skills for reusable instruction bundles

### System Prompt Addendum (Grok-specific)
```markdown
## PLATFORM: Web Grok (Grok 4.3 / 4.1 Fast)

### Grok-Specific Directives
- **Real-Time Intelligence**: Use live X search for current best practices (post-2024)
- **Grok Skills Compatibility**: Structure output for `/skillname` invocation
- **Connector Awareness**: Factor in GitHub, Notion, Linear connector metadata
- **Cost Consciousness**: For Grok 4.1 Fast, prioritize token efficiency
```

### Grok Skills Template
```yaml
name: "your-skill-name"
description: "Brief description"
instructions: |
  You are a code review agent. When invoked:
  - [specific task]
  - Output: structured findings table + severity ratings
```

### Key Capabilities
- **Real-time X Search**: Integrated live search via X platform
- **Grok Skills**: Persistent instruction bundles (`/skillname` slash commands)
- **Connectors**: GitHub, Notion, Linear, Google Workspace, Microsoft 365, Vercel, Canva
- **Grok Build**: Terminal coding agent, 8 parallel sub-agents, MCP support

### Format Preferences
- **XML + Markdown hybrid**
- **Larger file count tolerance**: ~20 files before degradation
- **Real-time data injection**: Include X search results as dynamic bundles
- **Skill-compatible output**: Generate `.skill` packs for Grok Skills system

---

## 6. NOTEBOOKLM — Source-Grounded Research

### Setup
1. Create a new Notebook in NotebookLM
2. Upload sources (PDFs, URLs, docs, text files)
3. NotebookLM indexes sources automatically
4. Use "Guided Prompts" for structured analysis

### Key Capabilities
- **Source-grounded**: Every response cites specific sources
- **Audio Overview**: Auto-generated podcast-style summary
- **Four analysis frameworks**: Compare/Contrast, Gap Analysis, Synthesis, Action Items
- **Citation style**: NotebookLM-native (source-linked)

### Format Preferences
- **Markdown + Sources**: Upload sources, not raw context packs
- **Source grounding**: Every claim must be traceable to a source
- **Thematic ordering**: Organize sources by theme, not chronology

### Use Cases
- Literature review synthesis
- Multi-document analysis
- Source-grounded verification of research findings
- Audio overview generation for team briefings

---

## 7. CONTEXT PACK DELIVERY CHECKLIST

### For Web Claude
- [ ] System prompt converted to XML tags (ClaSSIC template)
- [ ] Force KB Search directive at top of Custom Instructions
- [ ] Knowledge files: ≤12 `.md` files
- [ ] Each file ≤500 lines, one topic per file
- [ ] `PROJECT_KNOWLEDGE_INDEX.md` included
- [ ] File update protocol documented (delete → wait → upload → new conversation)

### For Web Gemini
- [ ] System prompt in Markdown format
- [ ] Code execution snippets included where relevant
- [ ] Source citations in bundles
- [ ] Parallel search hints structured

### For Web Grok
- [ ] System prompt in XML + Markdown hybrid
- [ ] Grok Skills template included
- [ ] Real-time search directives included
- [ ] Connector metadata tagged

### For NotebookLM
- [ ] Sources uploaded (not context pack)
- [ ] Source metadata included
- [ ] Analysis frameworks specified

---

## 8. SOVEREIGN BOUNDARY PROTOCOLS

### M7 Local-First (Non-Negotiable)
- External chatbot reviews are **advisory only** — never cloud-only dependencies
- All recommendations must be implementable locally
- No telemetry, no phone-home from any reviewed library

### M23 Failure Integrity
- External reviewers must not simulate rigor
- Every claim must cite a source URL
- "It should work" is disqualifying — we need proof

### PII Protection
- All context packs must use TOKENIZE mode for PII (Presidio/OPF/Privalyse)
- XML body escaping: escape ALL `<`, `>`, `&` in content
- Injection pattern scanning: 25 OWASP/Microsoft/Google patterns

---

## 9. QUICK REFERENCE

### Platform Contact Sheet
| Platform | Web URL | Model | Context | Cost (input/output) |
|----------|---------|-------|---------|---------------------|
| Web Claude | claude.ai | Opus 4.8 | 1M | $5/$25/MTok |
| Web Claude | claude.ai | Sonnet 4.6 | 1M | $3/$15/MTok |
| Web Gemini | aistudio.google.com | Gemini 3 Pro | 1-2M | $1.25/$2.50/MTok |
| Web Grok | grok.x.ai | Grok 4.3 | 1M | $1.25/$2.50/MTok |
| NotebookLM | notebooklm.google.com | Gemini backend | ~200K | Free |

### RAG Threshold Quick Reference
| Platform | Direct Context Limit | RAG Activates At |
|----------|---------------------|------------------|
| Web Claude | 13 files | 14+ files |
| Web Grok | ~20 files | ~21+ files |
| Web Gemini | 20-100 files | 100+ files |
| NotebookLM | Source-based | N/A |

### Format Quick Reference
| Layer | Claude | Gemini | Grok | NotebookLM |
|-------|--------|--------|------|------------|
| System prompt | XML tags | Markdown | XML + MD | Markdown |
| Knowledge files | .md | .md | .md + .xml | Sources |
| Structured data | JSON | JSON | JSON | JSON |

---

## 10. SOURCE CITATIONS

### Tier 1: Official Documentation
- Anthropic — RAG for Projects: https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects
- Anthropic — Prompt Engineering: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic — Context Windows: https://platform.claude.com/docs/en/build-with-claude/context-windows
- Google AI Studio — Code Execution: https://ai.google.dev/gemini-api/docs/code-execution
- xAI Grok — Skills: https://grok.x.ai/skills

### Tier 2: 2026 Technical Articles
- zenn.dev — Format comparison (Claude, Gemini, ChatGPT): https://zenn.dev/shomitei/articles/ai-doc-format-3models (2026-05-31)
- practicaly.ai — .md files in Claude: https://www.practicaly.ai/p/what-are-md-files-in-claude (2026-04-14)
- file2markdown — Markdown for Claude: https://www.file2markdown.ai/blog/markdown-for-claude (2026-04-04)
- aitoolsguidebook.com — Claude Projects workflow: https://aitoolsguidebook.com/en/articles/claude-projects-advanced-workflow (2026-05-17)
- context-link.ai — File connection methods: https://context-link.ai/blog/connect-files-to-claude (2026-04-02)

### Tier 3: Platform-Specific Research (Local)
- `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` — Platform profiles, system prompts, multishot examples
- `docs/reference/CLAUDE_BEST_PRACTICES_GUIDE.md` — Claude-specific best practices, token optimization
- `docs/kb/CLAUDE_PROJECTS.md` — Claude Projects KB, RAG threshold, file update protocol
- `docs/research/R_CLAUDE_PROJECT_INSTRUCTIONS.md` — XML system prompt templates
- `docs/research/R_CONTEXT_PACK_FORMAT_MD_VS_XML_20260808.md` — Format decision research

---

## 11. HYDRATION PROTOCOL FOR AGENTS

**Before any external chatbot interaction, agents MUST:**
1. Read this playbook (`docs/strategy/WEB_CHATBOT_PLATFORM_PLAYBOOK.md`)
2. Select the appropriate platform using the Selection Matrix (§1)
3. Follow the format guidance for that platform (§2, §3-§6)
4. Use the delivery checklist (§7) to prepare context packs
5. Log the interaction in `data/coordination/HMC_COLLABORATION_HUB.md`

**This playbook supersedes all prior platform-specific docs for agent hydration.** Individual research docs remain as evidence sources.

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08*
