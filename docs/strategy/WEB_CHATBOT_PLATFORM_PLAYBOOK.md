# 🔱 Web Chatbot Platform Playbook — Omega Engine
**AP Token**: `AP-WEB-CHATBOT-PLAYBOOK-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Index for platform-specific best practices
**Purpose**: Agents start here, then navigate to platform-specific doc

---

## 📋 TABLE OF CONTENTS (LLM-Friendly)

| Section | Anchor | Purpose |
|---------|--------|---------|
| 1. Platform Selection Matrix | `#1-platform-selection-matrix` | Choose the right platform for your task |
| 2. Format Decision Tree | `#2-format-decision-tree` | XML vs Markdown vs JSON by layer |
| 3. Platform-Specific Docs | `#3-platform-specific-docs` | Links to canonical best practices per platform |
| 4. Context Pack Delivery | `#4-context-pack-delivery` | Unified checklist for all platforms |
| 5. Sovereign Boundary Protocols | `#5-sovereign-boundary-protocols` | Universal mandates affecting all platforms |
| 6. Hydration Protocol | `#6-hydration-protocol` | Mandatory steps before any external chatbot interaction |

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
| **Local terminal coding agent** | **Grok CLI (Grok Build)** | Local file access, sandbox, 8 parallel sub-agents, ACP |
| Cross-validation of critical decisions | **Claude + Gemini** | Independent verification |

### By Model Capability

| Model | SWE-bench | MRCR | GPQA | Context | Best Use |
|-------|-----------|------|------|---------|----------|
| Claude Opus 4.8 | 82.1% | 76% | 90.5% | 1M | Code review, deep analysis |
| Claude Sonnet 4.6 | 78.3% | 72% | 88.2% | 1M | General tasks, cost-effective |
| Gemini 3 Pro | 63.8% | 68% | 94.1% | 1-2M | Research, benchmarks |
| Gemini 3.1 Pro | 65.2% | 70% | 95.3% | 10M | Ultra-long context analysis |
| Grok 4.5 (Web) | 70.8%* | 65% | 87.5% | 1M | Agentic, real-time X search |
| Grok 4 Heavy (Web) | 72.5%* | 68% | 89.0% | 2M | Document analysis, orchestration |
| grok-code-fast-1 (CLI) | 70.8% | — | — | — | Local coding, parallel sub-agents |

*SWE-bench for grok-code-fast-1 (Grok Build's model); Web Grok uses Grok 4.5/4 Heavy.

---

## 2. FORMAT DECISION TREE

> **Core principle**: Format follows layer, not file type.

```
Is this...
├── A system prompt / custom instructions? → XML tags (Claude) / Markdown (Gemini/Grok/NotebookLM)
├── A knowledge/reference file (uploaded)? → Markdown (.md)
├── Structured data / schema? → JSON
├── Source document for NotebookLM? → Markdown with source metadata
├── Local CLI config/rules/skills? → TOML (config), Markdown (rules/skills)
└── Sandbox profiles? → TOML
```

### Detailed Format Guidance

#### System Prompt / Custom Instructions
| Platform | Format | Why |
|----------|--------|-----|
| **Web Claude** | **XML tags** (`<role>`, `<context>`, `<constraints>`, `<rules>`, `<output_format>`) | Claude's training data is XML-rich; Anthropic official docs recommend. Closing tags prevent instruction/input boundary confusion. |
| **Web Gemini** | **Markdown** (`##` headings) | Gemini's long-context handles structure; MD delimiters sufficient per Google docs. |
| **Web Grok** | **Markdown** | Long-context handles structure; MD delimiters sufficient. |
| **Grok CLI (Grok Build)** | **Markdown** (rules files) + **TOML** (config) | Local files; rules appended to system prompt, config in TOML. |
| **NotebookLM** | **Markdown** | Source-grounded; MD with source metadata. |

#### Knowledge/Reference Files (uploaded to Project Knowledge)
| Platform | Format | File Limit | Why |
|----------|--------|------------|-----|
| **Web Claude** | **Markdown (.md)** | 13 files (RAG at 14+) | Token-efficient (~15% fewer than XML), Claude parses headings/lists for RAG retrieval. XML tags consume tokens without RAG benefit. |
| **Web Gemini** | **Markdown (.md)** | 20-100 files | MD with clear headings; Gemini's long context handles large KBs. |
| **Web Grok** | **Markdown (.md) + file uploads** | 20-50 files | MD for notes, file uploads for PDFs/docs via web UI. |
| **Grok CLI (Grok Build)** | **Local files** (workspace) | Unlimited (local) | Direct filesystem access; respects `.gitignore`; sandbox controls writes. |
| **NotebookLM** | **Markdown + Sources** | Source-based | Upload sources (PDFs, URLs, docs); NotebookLM indexes them. |

#### Key Decision Rule (TeachYou 2026)
> **"Is this piece of the prompt data, or is it instructions? If it's data (variable, untrusted, multiple similar blocks), wrap in XML tags. If it's instructions (authored by you), use Markdown headings."**

---

## 3. PLATFORM-SPECIFIC DOCS

| Platform | Canonical Doc | Purpose |
|----------|---------------|---------|
| **Web Claude** | `docs/strategy/WEB_CLAUDE_BEST_PRACTICES.md` | Setup, XML system prompt, file org, RAG, token optimization, sovereign boundaries |
| **Web Gemini** | `docs/strategy/WEB_GEMINI_BEST_PRACTICES.md` | Setup, Markdown system prompt, code execution, parallel search, source grounding |
| **Web Grok** | `docs/strategy/WEB_GROK_BEST_PRACTICES.md` | Setup, Markdown system prompt, real-time X search, Connectors, Grok Skills (cloud) |
| **Grok CLI (Grok Build)** | `docs/strategy/GROK_CLI_BEST_PRACTICES.md` | Local CLI, TUI/headless/ACP, sandbox, local skills, local-first architecture |
| **NotebookLM** | `docs/strategy/NOTEBOOKLM_BEST_PRACTICES.md` | Source upload, analysis frameworks, audio overview, citation style |

**Agents MUST read the platform-specific doc for their target platform before any interaction.**

---

## 4. CONTEXT PACK DELIVERY CHECKLIST

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
- [ ] System prompt in Markdown format
- [ ] Real-time X search enabled (explicit x_search directives)
- [ ] Connectors configured (GitHub, Notion, Linear, etc.)
- [ ] Grok Skills created for reusable workflows
- [ ] Source metadata included for uploads

### For Grok CLI (Grok Build)
- [ ] SuperGrok Heavy subscription verified
- [ ] Sandbox profile selected (`workspace` for dev, `strict` for untrusted)
- [ ] Custom rules for Omega Engine mandates (M1, M7, M8, M13, M23)
- [ ] Local skills in `~/.grok/skills/` for reusable workflows
- [ ] `.gitignore` respected (secrets excluded by default)
- [ ] For headless/ACP: `grok agent stdio` or `-p` with `--output-format streaming-json`

### For NotebookLM
- [ ] Sources uploaded (not context pack)
- [ ] Source metadata included
- [ ] Analysis frameworks specified

---

## 5. SOVEREIGN BOUNDARY PROTOCOLS (Universal)

### M7 Local-First (Non-Negotiable)
- External chatbot reviews are **advisory only** — never cloud-only dependencies
- All recommendations must be implementable locally
- **Grok CLI (Grok Build) aligns with M7** — local-first architecture, snippet-only transmission
- No telemetry, no phone-home from any reviewed library

### M23 Failure Integrity
- External reviewers must not simulate rigor
- Every claim must cite a source URL
- "It should work" is disqualifying — we need proof

### PII Protection
- All context packs must use TOKENIZE mode for PII (Presidio/OPF/Privalyse)
- XML body escaping: escape ALL `<`, `>`, `&` in content
- Injection pattern scanning: 25 OWASP/Microsoft/Google patterns
- **Never upload PII/secrets** to cloud platforms (Web Grok, Web Gemini, Web Claude, NotebookLM)
- **Grok CLI**: Sandbox deny lists for credential files (`**/.env`, `**/*.pem`)

---

## 6. HYDRATION PROTOCOL

**Before any external chatbot/CLI interaction, agents MUST:**
1. Read this playbook (`docs/strategy/WEB_CHATBOT_PLATFORM_PLAYBOOK.md`)
2. Select the appropriate platform using the Selection Matrix (§1)
3. Read the platform-specific best practices doc (§3)
4. Follow the format guidance for that platform
5. Use the delivery checklist (§4) to prepare context packs
6. Log the interaction in `data/coordination/HMC_COLLABORATION_HUB.md`

**This playbook + platform-specific docs supersede all prior platform-specific docs for agent hydration.**

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08*
