# 🔱 Web Grok Best Practices — Omega Engine
**AP Token**: `AP-WEB-GROK-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Single-source for Web Grok (grok.com, iOS, Android) interactions
**Platform**: Web Grok at `grok.com` — cloud-based, SuperGrok subscription
**Supersedes**: `docs/research/R_GROK_CLI_ARCHITECTURE.md` (Web Grok sections), `docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md` (Web Grok sections), `docs/research/R_GROK_ECOSYSTEM_DEEP.md` (Web Grok sections), `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md` (Web Grok sections)

> **CRITICAL DISTINCTION**: This doc covers **Web Grok (grok.com)** — the cloud web platform. For the **local CLI tool (Grok Build)**, see `docs/strategy/GROK_CLI_BEST_PRACTICES.md`. They are entirely different platforms.

---

## 📋 TABLE OF CONTENTS (LLM-Friendly)

| Section | Anchor | Purpose |
|---------|--------|---------|
| 1. Setup & Architecture | `#1-setup--architecture` | Web Grok access, subscription tiers, model capabilities |
| 2. Format Specification | `#2-format-specification` | Markdown for system prompt, knowledge files, sources |
| 3. Key Capabilities | `#3-key-capabilities` | Real-time X search, Connectors, Grok Skills, file uploads |
| 4. File/Source Organization | `#4-filesource-organization` | Upload limits, thematic organization, source metadata |
| 5. System Prompt Template | `#5-system-prompt-template` | Markdown-based with Web Grok-specific directives |
| 6. Grok Skills (Cloud) | `#6-grok-skills-cloud` | Slash-command skills, creation, invocation, templates |
| 7. Connectors | `#7-connectors` | GitHub, Notion, Linear, Google Workspace, Outlook, SharePoint, MCP |
| 8. Cost Optimization | `#8-cost-optimization` | SuperGrok vs SuperGrok Heavy, model access, usage limits |
| 9. Sovereign Boundary Protocols | `#9-sovereign-boundary-protocols` | M7 local-first, M23 failure integrity, PII protection |
| 10. Quick Reference | `#10-quick-reference` | Model comparison, format quick reference, setup checklist |
| 11. Source Citations | `#11-source-citations` | Tier-ordered citations |
| 12. Hydration Protocol | `#12-hydration-protocol` | Mandatory steps before any Web Grok interaction |

---

## 1. SETUP & ARCHITECTURE

### 1.1 Access
1. Go to `grok.com` (or iOS/Android app)
2. Sign in with SuperGrok or X Premium+ account
3. No installation required — runs in browser/app
4. Select model from picker (Grok 4.5, Grok 4 Heavy for Heavy tier)

### 1.2 Architecture (2026)
- **Cloud-based** — no local file access, runs on xAI infrastructure
- **Real-time X Search** — live firehose access to X posts, threads, engagement metrics
- **Connectors** — OAuth integrations with GitHub, Notion, Linear, Google Workspace, Outlook, SharePoint, Salesforce, MCP
- **Grok Skills** — persistent slash-command instruction bundles (`/skillname`)
- **File Uploads** — PDFs, images, documents via web UI (count toward context)
- **Voice Mode** — speech-to-text, text-to-speech
- **Image/Video Generation** — built-in generation capabilities

### 1.3 Subscription Tiers & Model Access
| Tier | Cost | Models | Key Features |
|------|------|--------|--------------|
| **Free** | **$0** | **Grok 3 / Grok 4 Mini** | **Text chat only, no image/video generation, limited caps** |
| SuperGrok Lite | $10/mo | Grok 4 | Higher caps, image generation |
| SuperGrok | ~$30/mo | Grok 4.5 | Think, DeepSearch, Connectors, Skills |
| **SuperGrok Heavy** | **~$300/mo** | **All + Grok 4 Heavy + Grok Build CLI** | **Full access, Grok Build included** |

> **Free tier reality**: The free plan runs Grok 3 or Grok 4 Mini — lighter models good for quick questions and fact checks. No image/video generation (paid since March 2026). No DeepSearch or extended reasoning. xAI does not publish exact message limits — check Settings > Usage for your actual position. The 10 prompts/2-hour cap was retired in June 2026.

### 1.4 Model Capabilities
| Model | Context | SWE-bench | GPQA | Free? | Best For |
|-------|---------|-----------|------|-------|----------|
| Grok 3 / Grok 4 Mini | 1M | — | — | ✅ | Quick questions, fact checks |
| Grok 4.5 | 1M | 70.8%* | 87.5% | ❌ | General reasoning, agentic |
| Grok 4 Heavy | 2M | 72.5%* | 89.0% | ❌ | Document analysis, orchestration |
| Grok 4.1 Fast | 2M | 65.0%* | 82.0% | ❌ | High-volume, cost-optimized |

*SWE-bench for grok-code-fast-1 (Grok Build's model); Web Grok uses Grok 4.5/4 Heavy.

---

## 2. FORMAT SPECIFICATION

### 2.1 System Prompt / Custom Instructions → **Markdown**
Web Grok's long-context handles structure; Markdown delimiters sufficient. No XML tags needed.

### 2.2 Knowledge/Reference Files (Uploaded) → **Markdown (.md) + Sources**
- **Markdown** for notes, analysis, structured content
- **File uploads** (PDFs, images, docs) via web UI — count toward context
- **Larger file count tolerance**: 20-50 files effectively (no hard RAG threshold like Claude)

### 2.3 Structured Data → **JSON**
- Machine-to-machine, schema enforcement

### 2.4 Grok Skills → **YAML** (for creation) / **Markdown** (for instructions)
- Skill definition: name, description, instructions (Markdown)

---

## 3. KEY CAPABILITIES

### 3.1 Real-Time X Search (Unique Differentiator)
- **Live X firehose** — structured access to posts, threads, replies, quotes, engagement metrics, social graph
- **Two search tools**: `web_search` (indexed web) + `x_search` (live X)
- **Explicitly specify** which to use in instructions: "use x_search for real-time sentiment"
- **Parallel execution**: Up to 128 parallel tool calls — structure multi-source research as parallel tasks
- **For anything on X first**: Meaningful gap vs other tools that query lagged search indexes

### 3.1.1 Omega Engine X Search Patterns
| Search Goal | x_search Query Pattern | Why |
|-------------|----------------------|-----|
| Latest AnyIO patterns | `anyio python 2026 best practices` | Current async patterns |
| Grok CLI adoption | `grok build cli adoption 2026` | Real-time community sentiment |
| Local LLM trends | `local LLM inference 2026` | Current hardware/software trends |
| Circuit breaker libraries | `python circuit breaker library 2026` | Current best practices |
| MCP server ecosystem | `model context protocol mcp 2026` | Latest MCP developments |

**Always include date filter**: "Find posts from 2026 about [topic]" — avoids stale 2024/2025 info.

### 3.2 Connectors (Deep SaaS Integrations)
OAuth-based, connect once, access on demand:

| Connector | Capabilities |
|-----------|--------------|
| **GitHub** | Search code, summarize PRs, review changes, track workflow |
| **Notion** | Search/edit pages, databases, wikis across team docs |
| **Linear** | Search backlog, summarize sprints, draft updates, create issues |
| **Google Workspace** | Gmail, Drive, Docs, Sheets, Calendar — read/write |
| **Outlook/Teams** | Email, calendar, meetings, Teams messages/channels |
| **SharePoint** | Sites, document libraries, create/edit documents |
| **Salesforce** | CRM objects, query records, create/update |
| **Custom MCP** | Bring your own MCP server (internal APIs, proprietary tools) |

### 3.3 Grok Skills (Cloud Slash Commands)
- **Persistent instruction bundles** — create once, invoke with `/skillname`
- **Carry across all conversations** — no re-pasting system prompts
- **Available in SuperGrok interface** and as reusable instruction sets for Grok API
- **Built-in skills** from xAI (override with your own)

### 3.4 File Uploads
- PDFs, images, documents via web UI
- Text extracted and indexed
- Count toward context window

---

## 4. FILE/SOURCE ORGANIZATION

### 4.1 Upload Limits
| Type | Limit | Notes |
|------|-------|-------|
| File uploads | ~50 per conversation | PDFs, images, docs |
| Context window | 1-2M tokens | Model-dependent |
| Skills | Unlimited | Stored in account |

### 4.2 Thematic Organization
Organize by **theme/workflow**, not chronology:
```
Research: Technology Adoption
  - interlock-cb docs (PDF upload)
  - Honker GitHub (Connector: GitHub)
  - MCP SDK v2 changelog (web search)

Security Review
  - PII masking specs (Markdown note)
  - Sandbox profiles (Connector: GitHub repo)
```

### 4.3 Source Metadata (Critical for Verification)
Every uploaded source should include:
```markdown
<!-- Source: https://example.com/doc -->
<!-- Last fetched: 2026-08-08 -->
<!-- Coverage: complete API reference for v3.x -->
<!-- Version: 3.2.1 -->
```

---

## 5. SYSTEM PROMPT TEMPLATE (Markdown)

```markdown
## Role
You are a [specific role] with [experience] in [domain].
You specialize in [sub-specialty].
Your approach is [methodology].

## Context
[Project context, hardware reality, constraints]

## Constraints
- FORBIDDEN to [violation]
- MUST [requirement]

## Rules
1. [Behavioral rule]
2. [Behavioral rule]

## Output Format
[Response structure template]

## Web Grok-Specific Directives

### Real-Time X Search
You have access to live X search via x_search tool. Use it for:
- Current best practices (post-2024)
- Emerging vulnerabilities
- Active discussions on context engineering
- Real-time sentiment and public opinion
- **ALWAYS specify x_search vs web_search explicitly** — they are different tools

### Parallel Tool Execution
Grok supports up to 128 parallel tool calls. Structure multi-source research as parallel tasks:
- "Search X for brand mentions AND search web for documentation simultaneously"
- Numbered parallel tasks trigger concurrent execution

### Source Grounding
Every claim must be traceable. Use citation format:
- `[Source: URL or description]`
- Distinguish 2024 vs 2026 findings explicitly

### Connector Awareness
Connectors may be active (GitHub, Notion, Linear, etc.). Factor into review:
- GitHub: Check CI/CD patterns, repo structure
- Notion: Verify knowledge base structure
- Linear: Assess issue tracking integration

### Cost Consciousness
If reviewing for SuperGrok (not Heavy), prioritize:
- Token efficiency recommendations
- Bundle consolidation opportunities
```

---

## 6. GROK SKILLS (Cloud)

### 6.1 Creation (SuperGrok Interface)
Settings → Skills → Create New Skill:
| Field | Purpose | Best Practice |
|-------|---------|---------------|
| **Name** | Slash command trigger | Short, lowercase, no spaces: `/monitor`, `/brief`, `/review` |
| **Description** | Intent activation | One sentence: "Use when asked to monitor X mentions for a brand" |
| **Instructions** | Persistent system prompt | Full behavior spec: tools, output format, constraints |

### 6.2 Skill Template (YAML for definition)
```yaml
name: "your-skill-name"
description: "One sentence: when this skill activates"
instructions: |
  You are a [role]. When invoked:
  - [specific task 1]
  - [specific task 2]
  - **ALWAYS use x_search for real-time X data**
  - **ALWAYS cite sources: [Source: URL/description]**
  - Output: structured findings table + severity ratings
```

### 6.3 Invocation
- Type `/skillname` in any conversation
- Skill activates with its persistent instructions
- Available across all conversations (SuperGrok)

### 6.4 Example Skills (from xAI)
- `/monitor` — Brand tracking on X
- `/brief` — Intelligence reports
- `/review` — Code review
- `/research` — Deep research
- `/compete` — Competitive intelligence
- `/thread` — X content analysis
- `/spec` — Product specs
- `/sales` — Pre-call briefs

---

## 7. CONNECTORS

### 7.1 Setup
1. `grok.com` → Click `+` button → Connectors → Add connector
2. OAuth sign-in (one-time)
3. Connector available in all conversations

### 7.2 Connector Metadata Tagging
When referencing connector data in prompts:
```markdown
<!-- Connector: GitHub -->
<!-- Repo: Xoe-NovAi/omega-engine -->
<!-- Branch: main -->
```

### 7.3 Connector-Specific Review Focus
| Connector | Review Focus |
|-----------|--------------|
| GitHub | CI/CD integration, repo structure, branch strategy |
| Notion | Knowledge base structure, wiki organization, linking |
| Linear | Issue tracking, sprint planning, milestone mapping |
| Google Workspace | Docs/Sheets access, Drive organization, Calendar |
| Outlook/Teams | Email/calendar/meetings, Teams channels |
| SharePoint | Sites, document libraries, advanced doc editing (Grok 4.3) |
| Salesforce | CRM objects, records, queries |
| Custom MCP | Internal APIs, proprietary tools, homegrown knowledge bases |

### 7.4 Bring Your Own MCP
- Go to `grok.com/connectors` → New Connector → Custom
- Enter MCP server URL + authentication
- Grok discovers tools and makes them available

---

## 8. COST OPTIMIZATION

### 8.1 Tier Selection
| Use Case | Recommended Tier | Cost |
|----------|------------------|------|
| Casual chat, light research | **Free** | **$0** |
| Regular productivity, DeepSearch | SuperGrok (~$30/mo) | $30/mo |
| Heavy research, Grok 4 Heavy, Grok Build CLI | SuperGrok Heavy (~$300/mo) | $300/mo |
| API integration | xAI API (usage-based) | Variable |

### 8.2 Free vs Paid
- **Free**: Grok 3/4 Mini, text chat only, limited caps, no image/video
- **SuperGrok Lite ($10)**: Grok 4, higher caps, image generation
- **SuperGrok ($30)**: Grok 4.5, DeepSearch, Connectors, Skills
- **SuperGrok Heavy ($300)**: Grok 4 Heavy, Grok Build CLI, full access
- **xAI API**: Separate developer product (usage-based, OpenAI-compatible SDK)

---

## 9. SOVEREIGN BOUNDARY PROTOCOLS

### 9.1 Mandates Affecting Web Grok Usage
| Mandate | Impact |
|---------|--------|
| **M7 Local-First** | Web Grok is cloud-only — use for research ONLY, never for production inference |
| **M8 Zero Telemetry** | xAI may collect usage data — treat as advisory, not sovereign |
| **M23 Failure Integrity** | Verify all claims against source citations — no soft failures |

### 9.2 PII Protection
- **Do not upload PII** to Web Grok (xAI cloud)
- **Tokenize locally first** if source contains PII
- **Use for public/universal knowledge only**

### 9.3 File Upload Caution
- Uploaded files are processed on xAI servers
- Treat as advisory input only
- Never upload secrets, credentials, proprietary code

---

## 10. QUICK REFERENCE

### Model Comparison
| Model | Context | Access | Best For |
|-------|---------|--------|----------|
| Grok 4.5 | 1M | SuperGrok | General reasoning, agentic |
| Grok 4 Heavy | 2M | SuperGrok Heavy | Document analysis, orchestration |
| Grok 4.1 Fast | 2M | SuperGrok Heavy | High-volume, cost-optimized |

### Format Quick Reference
| Layer | Format |
|-------|--------|
| System prompt | Markdown |
| Knowledge files | Markdown (.md) + file uploads |
| Structured data | JSON |
| Grok Skills | YAML (definition) / Markdown (instructions) |

### Setup Checklist
```
☐ SuperGrok account active
☐ Model selected (Grok 4.5 / 4 Heavy)
☐ Custom Instructions in Markdown format
☐ Real-time X search enabled (x_search tool)
☐ Connectors configured (GitHub, Notion, Linear, etc.)
☐ Grok Skills created for reusable workflows
☐ Source metadata included for uploads
☐ File uploads used for reference docs
```

---

## 11. SOURCE CITATIONS

### Tier 1: Official
- Web Grok: https://grok.com
- Grok Skills: https://x.ai/news/grok-skills (2026-05-18)
- Grok Connectors: https://x.ai/news/grok-connectors (2026-05-06)
- Connectors Docs: https://docs.x.ai/grok/connectors
- Pricing: https://x.ai/pricing

### Tier 2: 2026 Technical Articles
- zenn.dev Format Comparison: https://zenn.dev/shomitei/articles/ai-doc-format-3models (2026-05-31)
- AIToolsRecap Grok Skills: https://aitoolsrecap.com/Blog/grok-agent-instructions-examples-2026 (2026-06-16)
- LearnWithDarin Grok Guide: https://learn.techwithdarin.com/guides/grok/ (2026-05-09)

### Tier 3: Local Research (Evidence)
- `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` — Web Grok platform profile
- `docs/research/R_GROK_ECOSYSTEM_DEEP.md` — Ecosystem deep dive (Web Grok sections)

---

## 12. HYDRATION PROTOCOL

**Before any Web Grok interaction, agents MUST:**
1. Read this document
2. Verify SuperGrok account access
3. Select appropriate model (Grok 4.5 / 4 Heavy)
4. Prepare system prompt in Markdown format
5. Configure Connectors and Grok Skills as needed
6. Enable real-time X search (explicit x_search directives)
7. Upload reference files with metadata
8. Log interaction in `data/coordination/HMC_COLLABORATION_HUB.md`

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08*
