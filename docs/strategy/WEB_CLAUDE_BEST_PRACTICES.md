# 🔱 Web Claude Best Practices — Omega Engine
**AP Token**: `AP-WEB-CLAUDE-BEST-PRACTICES-v2.0.0`
⬡ OMEGA ⬡ KALI ⬡ antigravity-claude-sonnet-4-6 ⬡ opencode ⬡ trc_playbook ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: CANONICAL — Single-source for Web Claude (claude.ai Projects) interactions
**Supersedes**: v1.0.0 (2026-08-08), `docs/research/R_CLAUDE_PROJECT_INSTRUCTIONS.md`, `docs/research/R_CLAUDE_PROJECT_SETUP_PLAN.md`, `docs/kb/CLAUDE_PROJECTS.md`

---

## 📋 TABLE OF CONTENTS (LLM-Friendly)

| Section | Purpose |
|---------|---------|
| 1. What Web Claude Is (And Is Not) | Platform scope, what it does, what OpenCode CLI does |
| 2. The Omega Engine Web Claude Loop | Full end-to-end workflow from pack to artifact ingestion |
| 3. Free Tier Reality | Hard limits, available models, quota management |
| 4. Context Pack Creation (OpenCode → Web Claude) | How to build packs that give Claude what it needs |
| 5. Claude Project Setup | Project creation, system prompt, file upload |
| 6. System Prompt Mastery | ClaSSIC template, force KB search, project type templates |
| 7. File Organization & RAG Behavior | 12-file rule, ordering, RAG failure modes |
| 8. Running the Session | Token discipline, thinking modes, mid-session strategy |
| 9. Artifact Extraction & Handoff | Download, naming, ingestion by OpenCode CLI |
| 10. Multi-Account Strategy | 8-account rotation, parallel streams, carry-over |
| 11. Cross-Platform Validation | When to cross-check with Web Grok / Web Gemini |
| 12. File Update Protocol | Critical bug #10841, maintenance habits |
| 13. Sovereign Boundary Protocols | Mandates, PII sanitization, what crosses the boundary |
| 14. Quick Reference Cards | Pack checklist, session checklist, account log |
| 15. Hydration Protocol | What an agent must do before assisting with Web Claude work |

---

## 📋 EXECUTIVE SUMMARY

Web Claude (`claude.ai` Projects) is the **external deep-analysis layer** of the Omega Engine dev flow. It provides access to Claude's full reasoning capability without consuming OpenCode CLI token budget. With 8 accounts (each with a rolling free-tier quota refreshing every 5 hours), it represents a significant free Claude model capacity — if used with the right strategy.

**The core value proposition**: Web Claude has no local file access. The Context Packer bridges that gap by distilling the engine's state into uploadable bundles. Web Claude then performs deep code review, architecture analysis, research synthesis, or spec generation that would be prohibitively expensive on the CLI. The artifacts come back as `.md` files and are ingested by OpenCode CLI agents.

**Platform Separation** (NON-NEGOTIABLE):
- **Web Claude** (`claude.ai`) → deep analysis, code review, research, spec generation
- **OpenCode CLI** (Antigravity SDK) → implementation, file edits, test execution, local operations
- These are **not interchangeable**. Web Claude cannot touch local files. OpenCode CLI has full local access but limited free Claude usage. They are complementary layers.

**Available Models (Free Tier)**:
| Model | Thinking Mode | Best For |
|-------|--------------|----------|
| **Haiku 4.5** | Extended Thinking | Quick classification, simple extraction, fast synthesis |
| **Sonnet 4.6** | Thinking | Deep code review, architecture analysis, complex reasoning |
| ~~Opus 4.8~~ | ~~N/A~~ | **NOT available on free tier** |

**Note**: OpenCode CLI via Antigravity SDK provides access to Sonnet 4.6 and Opus 4.6. That is a separate platform and separate token budget. This document covers Web Claude only.

---

## 1. WHAT WEB CLAUDE IS (AND IS NOT)

### What It Is
- **External analysis engine**: reads what you give it, reasons deeply, returns structured artifacts
- **Token budget multiplier**: 8 accounts × rolling free quota = significant capacity for code review and research
- **No-local-access reviewer**: compensated for by the Context Packer tool
- **Superior for**: pre-refactor code review, architecture vetting, research synthesis, spec generation, documentation review

### What It Is NOT
- **Not Claude Code / Claude CLI** — there is no local file access, no shell execution, no git operations
- **Not a replacement for OpenCode CLI** — it cannot edit files, run tests, or interact with the engine
- **Not a persistent agent** — each new conversation starts fresh (Project Knowledge provides continuity)
- **Not a real-time collaborator** — the loop is asynchronous: pack → upload → session → download artifact → ingest

### When to Use Web Claude vs. OpenCode CLI
| Use Web Claude | Use OpenCode CLI |
|---------------|-----------------|
| Pre-sprint code review (before major refactor) | Implementation, file edits, test runs |
| Architecture vetting against Omega mandates | Incremental development |
| Research synthesis from uploaded materials | Local file analysis with full access |
| Spec / design document generation | Context pack creation |
| Second-opinion validation on a decision | Artifact ingestion and integration |
| Outsourcing deep analysis to preserve CLI tokens | Hivemind coordination |

---

## 2. THE OMEGA ENGINE WEB CLAUDE LOOP

This is the canonical end-to-end workflow. Every Web Claude engagement follows this loop.

```
┌─────────────────────────────────────────────────────────────┐
│                    OPENCODE CLI (Local)                     │
│                                                             │
│  1. PLAN: Identify what you need from Web Claude            │
│     (code review? architecture review? research synthesis?) │
│                                                             │
│  2. PACK: Run Context Packer with appropriate profile       │
│     → context_packs/{profile}/ (≤12 .md files + manifest)  │
│     → System prompt (XML ClaSSIC template)                  │
│     → Chat initiation prompt                                │
└────────────────────────┬────────────────────────────────────┘
                         │  (manual: open browser)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  WEB CLAUDE (claude.ai)                     │
│                                                             │
│  3. SETUP: Create/reuse Project                             │
│     → Paste system prompt into Custom Instructions          │
│     → Upload knowledge files (≤12)                          │
│                                                             │
│  4. SESSION: Paste chat initiation prompt, run analysis     │
│     → Use Sonnet 4.6 (Thinking) for deep work               │
│     → Use Haiku 4.5 (Extended Thinking) for quick tasks     │
│     → Monitor token usage; if hitting limit → see §10       │
│                                                             │
│  5. EXTRACT: Download artifact as .md file                  │
│     → Save to local folder with versioned filename          │
└────────────────────────┬────────────────────────────────────┘
                         │  (manual: save .md file)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    OPENCODE CLI (Local)                     │
│                                                             │
│  6. INGEST: Tell OpenCode CLI agent to read artifact        │
│     → Agent reads with full local context                   │
│     → Agent validates against Omega mandates                │
│     → Agent integrates findings into dev work               │
│     → Log artifact in WEB_CLAUDE_ARTIFACT_REGISTRY.md       │
│                                                             │
│  7. OPTIONAL CROSS-CHECK: Send same pack to Web Grok        │
│     or Web Gemini for second opinion (see §11)              │
└─────────────────────────────────────────────────────────────┘
```

**Key insight**: The OpenCode CLI session that created the context pack is the right session to hand the artifact back to. That session has the full local context, mandates awareness, and decision history needed to integrate Web Claude's findings properly.

---

## 3. FREE TIER REALITY

### Hard Limits (2026)
| Dimension | Value |
|-----------|-------|
| Context window | 200K tokens |
| Projects (free) | 5 max |
| RAG activation | 13+ files triggers RAG mode |
| File size | 30MB per file |
| Custom Instructions | ~1,000 words max |
| Quota reset | Rolling 5-hour window |

### Token Budget per Session
```
Context pack bundles:   ~41K tokens (typical)
Manifest:                 ~573 tokens
System prompt:          ~1,848 tokens
────────────────────────────────────────
Loaded context:         ~43K tokens
Headroom for chat:     ~157K tokens (78% of 200K)
```
**Rule**: Keep pack total ≤80K tokens. This leaves 120K for the conversation — enough for one deep review cycle. If you need more than one review cycle, start a new conversation (same Project, same files).

### Quota Management
- The free tier quota is a **rolling window**, not a daily reset
- Large packs (>80K tokens) burn quota fast — a single deep session can exhaust an account
- When a limit is hit mid-session before artifacts are produced: **switch accounts** (§10) and carry the initiation prompt forward
- When a limit is hit after artifacts are produced: download and move on to next task on next account

---

## 4. CONTEXT PACK CREATION (OPENCODE → WEB CLAUDE)

The Context Packer (`.opencode/skills/context-packer/`) is the **only sanctioned path** for engine state to leave the local boundary (M8, M23).

### 4.1 Packer Workflow
```bash
# 1. Select or create a profile in packer-config.yaml
# 2. Run packer
python .opencode/skills/context-packer/packer.py <profile_name>
# 3. Output: context_packs/<profile_name>/
#    ├── 00_PROJECT_MANIFEST.md   (entry point, signed)
#    ├── CLAUDE_PROJECT_SYSTEM_PROMPT.md  (paste into Custom Instructions)
#    ├── CHAT_INITIATION_PROMPT.md  (paste as first message)
#    └── <thematic bundles>.md    (upload as Project Knowledge)
```

### 4.2 What the Packer Does (Pipeline)
1. **Selection** — Glob patterns from profile YAML determine which files are included
2. **Consolidation** — Files grouped into thematic bundles (e.g., `core_logic`, `mandates`, `decisions`)
3. **Pruning** — Collapses whitespace, merges low-priority themes if over `max_slots: 12`
4. **PII Masking** — TOKENIZE mode strips sensitive values before any file crosses the boundary
5. **XML Escaping** — Bare `<` characters escaped for safe XML embedding
6. **Provenance headers** — Each bundled file prefixed with `FILE`, `SIZE`, `LANG`, `SHA256`, `PURPOSE`
7. **Manifest** — `00_PROJECT_MANIFEST.md` lists all bundles with token counts and purpose
8. **Ed25519 Signing** — Manifest signed for tamper-evidence

### 4.3 Pack Design Principles
- **One theme per file** — cross-file blindness is a verified RAG failure mode; don't split one topic across files
- **≤12 files total** — 13+ triggers RAG mode (see §7)
- **≤500 lines per file** (ideal), ≤2000 acceptable
- **LITM ordering** — Lost-in-the-Middle: put critical context at START and END of upload order
  - START: manifest, grounding, current decisions
  - MIDDLE: implementation details, mandates, research
  - END: handoff prompt, what you want Claude to produce
- **Descriptive filenames**: `core_engine_review_20260808.md` not `bundle3.md`
- **Version stamp packs**: `context_packs/pre-refactor-sprint-20260808/` — traceable and re-usable

### 4.4 Profile Design for Common Tasks
| Task | Key Files to Include | Omit |
|------|---------------------|------|
| **Pre-refactor code review** | src/ target modules, SOVEREIGN_MANDATES.md, existing tests, PIVOT_LOG decisions | Unrelated modules, .venv, data/ |
| **Architecture vetting** | OMEGA_ENGINE.md, ORACLE_STACK.md, relevant src/, strategy docs | Test fixtures, large data files |
| **Research synthesis** | Research brief, prior research docs, mandate constraints | Source code |
| **Spec generation** | Existing specs, mandates, prior decisions, system context | Implementation details |
| **Documentation review** | Doc files, DOC_STYLE_GUIDE.md, LLM_FRIENDLY_DOCS_BP.md | Source code |

### 4.5 What Crosses the Boundary (Sanctioned)
| Crosses Boundary ✅ | Stays Local ❌ |
|--------------------|--------------|
| Source code (PII-masked) | API keys, secrets, .env |
| Architecture docs | Internal decision rationale (unless explicitly included) |
| Sovereign Mandates | Soul.yaml (entity internal state) |
| Prior decisions (PIVOT_LOG excerpts) | Production data |
| Research briefs | Personal account credentials |

---

## 5. CLAUDE PROJECT SETUP

### 5.1 Project Creation (5 minutes)
1. `claude.ai` → Projects → "New Project"
2. Name after the **task outcome**: `Omega Engine Pre-Refactor Review 20260808` (not `omega-review`)
3. Settings → Custom Instructions → paste content of `CLAUDE_PROJECT_SYSTEM_PROMPT.md`
4. Add Knowledge → upload all `.md` files from `context_packs/<profile>/` **except** `CLAUDE_PROJECT_SYSTEM_PROMPT.md` and `CHAT_INITIATION_PROMPT.md`
5. Verify: "Based on the manifest in `00_PROJECT_MANIFEST.md`, list all included bundles"
6. If Claude lists the bundles correctly → direct context mode confirmed. If it says "I'll search my knowledge" → RAG mode triggered (reduce file count)

### 5.2 Reusing a Project
- A Project persists until you delete it. Reuse across accounts for same-task continuity.
- If files changed: follow **File Update Protocol** (§12) — do NOT re-upload with same filename
- If starting a new topic: create a new Project rather than repurposing (avoids context bleed)

### 5.3 Cross-Account Pack Carry-Over
When switching accounts mid-task (quota hit):
1. The **same pack files** upload to the new account's Project
2. In the new conversation: paste a brief "continuation prompt" summarizing what was established
3. Do NOT assume the new account has any memory of the previous session

---

## 6. SYSTEM PROMPT MASTERY

### 6.1 The ClaSSIC Template (Mandatory)
All system prompts use XML tags — Claude's training is XML-rich; Anthropic recommends it for structure.

```xml
<hierarchy>
In the event of a conflict between these Custom Instructions and the Project Knowledge files,
these Custom Instructions take absolute precedence.
</hierarchy>

<kb_search>
Before answering, always search the project knowledge first.
If anything in the knowledge applies, quote and prioritize it over general knowledge.
</kb_search>

<role>
You are a [specific role] with [experience]. You specialize in [sub-specialty].
Your approach is [methodology]. You always [behavioral rule]. You never [anti-pattern].
</role>

<context>
Audience: Expert Python systems engineer building local-first sovereign AI infrastructure.
Project: Omega Engine — sovereign, local-first AI runtime. No cloud dependencies. No telemetry.
Hardware: AMD Ryzen 5 5600G (6-core), 32GB RAM, no discrete GPU.
</context>

<constraints>
- FORBIDDEN: asyncio (use AnyIO — M1)
- FORBIDDEN: cloud dependencies in recommendations (M7)
- FORBIDDEN: telemetry, analytics, phone-home (M8)
- MUST: enforce Engine-Stack Firewall — core (src/omega/) ≠ stacks (config/wads/) (M2)
- MUST: Temple-Grade T1-T11 compliance for all generated artifacts (M13)
- MUST: flag any [id-soft:] heritage tags that lack vet records (M14)
</constraints>

<output_format>
Produce a structured Markdown report suitable for download as a .md file.
Include: Executive Summary, Findings (by category), Recommendations (prioritized), Decision Points.
End with: "ARTIFACT COMPLETE — ready for OpenCode CLI ingestion".
</output_format>
```

### 6.2 Force KB Search (Most Impactful Single Instruction)
Always include in Custom Instructions:
```
Before answering, always search the project knowledge first.
If anything in the knowledge applies, quote and prioritize it over general knowledge.
```
Community-verified as "more impactful than any other single tuning."

### 6.3 Behavioral Rules (Always Include)
- Proactively flag problems, risks, better approaches — don't wait to be asked
- Teach me unknown best practices relevant to the task
- Acknowledge gaps explicitly — say "I don't know" or "my knowledge ends at X" when appropriate
- No AI-isms: avoid "Genuinely", "Honestly", "It's important to note", "Delve", "Tapestry", "Landscape", "Realm", "Crucial"
- Cite specific sources when referencing uploaded docs (quote the bundle and section)
- End every artifact with "ARTIFACT COMPLETE" so I know when to download

### 6.4 Project Type Templates

**Code Review (Pre-Sprint)**
```xml
<role>
You are a senior Python systems architect with deep expertise in async systems, AnyIO,
and local-first AI infrastructure. You specialize in identifying architectural drift,
mandate violations, and suboptimal patterns before they compound.
</role>
<task>
Perform a deep code review of the provided source modules. Identify: (1) Mandate violations
(M1-M25), (2) Architectural anti-patterns, (3) Technical debt hotspots, (4) Missing test
coverage, (5) Refactoring opportunities. Produce a prioritized findings report.
</task>
```

**Architecture Vetting**
```xml
<role>
You are the Omega Engine's external architecture reviewer. Your job is to stress-test
proposed designs against the Sovereign Mandates and identify where the proposed approach
will create problems 3-6 months from now.
</role>
<task>
Review the proposed architecture against: (1) Sovereign Mandates M1-M25, (2) Existing
engine patterns in provided bundles, (3) Known failure modes from PIVOT_LOG decisions.
Produce: Go/No-Go verdict with specific conditions.
</task>
```

**Research Synthesis**
```xml
<role>
You are the Omega Engine research synthesizer. You distill raw research materials into
actionable recommendations grounded in the project's specific constraints and goals.
</role>
<task>
Synthesize the provided research materials into: (1) Key findings relevant to our context,
(2) Recommendations ranked by impact vs. effort, (3) Decision matrix for open questions,
(4) What to research next (gaps identified).
</task>
```

**Spec Generation**
```xml
<role>
You are the Omega Engine specification writer. You produce implementation-ready specs
that local OpenCode CLI agents can execute directly without further clarification.
</role>
<task>
Generate a complete implementation spec for [feature]. Include: (1) Data models,
(2) API contracts, (3) Test requirements, (4) Mandate compliance checklist,
(5) Step-by-step implementation plan with file-level guidance.
</task>
```

### 6.5 Chain-of-Thought Variants
| Variant | Use Case |
|---------|---------|
| "Think step by step" | General reasoning tasks |
| "Think in `<scratchpad>`, then respond in `<answer>`" | High-stakes decisions |
| "Consider [M1], [M2], [M7] before concluding" | Mandate compliance check |
| "For each finding, rate: severity (P0/P1/P2), effort (S/M/L), mandate (Mx)" | Code review triage |

---

## 7. FILE ORGANIZATION & RAG BEHAVIOR

### 7.1 The 13-File RAG Threshold (CRITICAL)
| File Count | Behavior |
|-----------|---------|
| ≤12 files | **Direct context** — all files fully loaded into window |
| 13+ files | **RAG mode activates** — Claude says "To save space, I'll look up information as needed" |
| RAG mode | Uses `project_knowledge_search` — partial fragments, cross-file blindness, hallucination risk |

**Rule**: Stay ≤12 files. Always. The Context Packer enforces `max_slots: 12` for this reason.

**Detection**: Ask "List all files in your project knowledge." If Claude lists them without searching → direct context. If it starts searching → RAG mode.

### 7.2 RAG Failure Modes
- Hallucinates details contradicting actual file contents
- Scores noise as signal past ~10 files
- Cross-file blindness: insights spanning 3+ files never fully assembled
- Silent: Claude doesn't tell you it's in RAG mode unless you check

### 7.3 Bundle Ordering (Lost-in-the-Middle Mitigation)
Claude's attention peaks at START and END of context (Liu et al. 2023). Upload order matters:

| Position | What to Put Here |
|----------|----------------|
| **1st** | `00_PROJECT_MANIFEST.md` — orientation, entry point |
| **2nd** | Grounding / current state (OMEGA_ENGINE.md excerpt, GROUNDED_TRUTH.md) |
| **3rd** | Decisions / PIVOT_LOG excerpts |
| **Middle** | Implementation bundles, mandates, research |
| **2nd to last** | Specific files being reviewed |
| **Last** | Handoff instructions / what to produce |

---

## 8. RUNNING THE SESSION

### 8.1 Chat Initiation Protocol
Always start with the **Chat Initiation Prompt** from the context pack (generated by packer). This prompt:
- References the manifest and asks Claude to confirm it loaded correctly
- Provides the specific task framing for this session
- Sets the output format expectations

If the packer didn't generate one, use this pattern:
```
I've uploaded [N] files to this project. Please confirm you can access them by listing
the bundle names from 00_PROJECT_MANIFEST.md. Then: [specific task].
Produce your output as a structured Markdown report ending with "ARTIFACT COMPLETE".
```

### 8.2 Model Selection
- **Sonnet 4.6 (Thinking)**: All deep work — code review, architecture, complex synthesis
- **Haiku 4.5 (Extended Thinking)**: Quick tasks — summarization, extraction, simple Q&A

### 8.3 Token Discipline During Session
- Don't ask Claude to re-read files it already has in context — waste of tokens
- Ask targeted questions rather than open-ended "tell me everything"
- If approaching token limit mid-session: ask Claude to produce a partial artifact and stop
- Never ask Claude to regenerate the full artifact if you already have a partial — download partial, start new conversation referencing it

### 8.4 Thinking Mode Usage
Both models have Thinking modes that show extended reasoning before the response. For complex code review:
- Enable Thinking — the reasoning trace reveals HOW Claude analyzed the code, not just what it found
- This is particularly valuable for mandate compliance checks where you want to see Claude's reasoning path
- For simple tasks, disable Thinking to save tokens

### 8.5 When to Stop and Switch Accounts
- Quota warning appears → finish current thought, ask for artifact, download, switch
- Token limit hit before artifact complete → note where Claude stopped, paste continuation prompt on next account
- Session drifting / Claude losing track → start new conversation in same Project

---

## 9. ARTIFACT EXTRACTION & HANDOFF

### 9.1 Download Protocol
1. Wait for "ARTIFACT COMPLETE" signal in Claude's response
2. Download as `.md` file via the Claude UI download button
3. Save to a **designated local folder** with a versioned filename:
   ```
   docs/hardening/omega-hub/claude-project/artifacts/<task>-<date>-<account>.md
   ```
   Example: `pre-refactor-code-review-20260808-acct1.md`

### 9.2 Artifact Naming Convention
```
<task-type>-<target>-<date>-<account-index>.md

Examples:
  code-review-health-monitor-20260808-acct1.md
  arch-vet-provider-fabric-20260808-acct3.md
  research-synthesis-vulkan-inference-20260808-acct2.md
  spec-soul-store-v2-20260808-acct1.md
```

### 9.3 OpenCode CLI Ingestion Protocol
After saving the artifact:
1. Return to the **same OpenCode CLI session** that generated the context pack (it has the full local context)
2. Tell the agent: "Read and review `<artifact path>`"
3. Agent performs local validation:
   - Cross-references findings against actual local files (Web Claude only saw the pack)
   - Flags any recommendations that conflict with mandates or recent decisions
   - Integrates accepted recommendations into the dev work
4. Log the artifact in `data/coordination/WEB_CLAUDE_ARTIFACT_REGISTRY.md`

### 9.4 Artifact Quality Check (Agent Validation Checklist)
When reviewing a Web Claude artifact, the OpenCode CLI agent checks:
```
☐ Findings reference actual bundled file content (not hallucinated)
☐ Recommendations are mandate-compliant (M1, M2, M7, M8, M13)
☐ No cloud dependencies introduced (M7)
☐ No asyncio recommended (M1)
☐ AnyIO patterns correctly suggested
☐ Any [id-soft:] heritage tags have vet records in HERITAGE_VET_LOG.md
☐ Recommended tests use anyio.pytest_plugin
☐ Recommendations are consistent with PIVOT_LOG decisions
```

---

## 10. MULTI-ACCOUNT STRATEGY

### 10.1 The 8-Account Pool
You have 8 Web Claude accounts cycling through Google accounts in order (top to bottom in browser login). Each has a rolling 5-hour free quota.

**Two operating modes**:

**Sequential (default)**: Use accounts one at a time, drain quota on each, move to next.
- Best for: single deep analysis task that spans multiple sessions
- Carry the context pack forward; paste continuation prompt on new account

**Parallel**: Multiple accounts running different tasks simultaneously.
- Best for: running architecture review on one account while spec generation runs on another
- Each account needs its own context pack (task-specific)
- Artifacts from each stream return to OpenCode CLI independently

### 10.2 Account Rotation Log
Track state in `data/coordination/WEB_CLAUDE_ACCOUNT_TRACKER.md`:
```
Account | Google Login Index | Last Used | Task | Status | Reset ~
--------|-------------------|-----------|------|--------|--------
acct-1  | 1st in list       | 2026-08-08 14:00 | pre-refactor review | DRAINED | ~19:00
acct-2  | 2nd in list       | 2026-08-08 14:30 | arch vet | IN USE  | —
acct-3  | 3rd in list       | —          | —    | FRESH   | —
...
```

### 10.3 Mid-Session Account Switch Protocol
When quota is hit **before** artifact is complete:
1. Ask Claude: "Produce a partial artifact of everything you've found so far. End with PARTIAL ARTIFACT."
2. Download the partial artifact
3. Open next account, create Project with same pack files
4. First message: "I have a partial artifact from a previous session. [paste summary of what was covered]. Continue from where that left off, focusing on [remaining scope]."

When quota is hit **after** artifact is complete:
1. Download the complete artifact
2. Move to next account for the next task (no carry-over needed)

### 10.4 Parallel Stream Discipline
- Never run the same task on two accounts simultaneously (wastes quota, produces redundant artifacts)
- Parallel streams should cover **different** aspects: e.g., acct-1 reviews `src/omega/oracle/`, acct-2 reviews `src/omega/hub/`
- Artifacts from parallel streams are merged by the OpenCode CLI agent during ingestion

---

## 11. CROSS-PLATFORM VALIDATION

### 11.1 When to Cross-Check
Not every artifact needs cross-validation. Use it when:
- The recommendation involves a major architectural decision (>1 week of implementation)
- Web Claude's recommendation conflicts with your intuition or prior decisions
- The stakes of getting it wrong are high (e.g., breaking the test suite, violating M7)

### 11.2 Cross-Check Protocol
1. Use the **same context pack** (or a trimmed version) on Web Grok or Web Gemini
2. Ask the same core question but do NOT show them Web Claude's artifact first
3. Compare independently — look for:
   - **Agreement**: High confidence, proceed
   - **Different emphasis**: Both valid, prioritize the one more aligned with mandates
   - **Contradiction**: Do NOT proceed. Return to OpenCode CLI for local arbitration
4. All findings return to OpenCode CLI. Local analysis is the final arbiter.

### 11.3 Platform Strengths for Cross-Validation
| Platform | Strong For | Cross-Check When |
|----------|-----------|-----------------|
| **Web Grok** | Real-time data, X/GitHub search, adversarial thinking | Need to know if a library/pattern is still maintained in 2026 |
| **Web Gemini** | Long-document synthesis, structured analysis, Workspace integration | Need a different analytical perspective on a complex architecture |
| **Web Claude** | Code review, mandate compliance, instruction-following | Primary platform |

---

## 12. FILE UPDATE PROTOCOL (CRITICAL — Bug #10841)

**Verified bug**: Re-uploading a file with the same name keeps the old cached version. Claude silently references stale content.

**Correct procedure**:
1. **Delete** the old file from Project Knowledge first
2. **Wait** for confirmation it's removed (Claude UI shows deletion)
3. **Upload** new version with a version-stamped name: `grounding-v2-20260808.md`
4. **Start a brand-new conversation** — existing conversations cache old content
5. **Clear browser cache** before the new session if you suspect issues
6. **Wait 10 seconds** after editing Custom Instructions before starting a conversation

### Maintenance Habits
- **`DECISIONS.md` in pack**: Append one paragraph per concluded Web Claude session. Re-upload (with delete-first). This is how decisions survive across chats.
- **`LESSONS.md` in pack**: Log every Web Claude misread, hallucination, or drift you observe. Use to improve future packs and system prompts.
- **Prune packs every 2 weeks**: Remove stale bundles, regenerate from source.
- **Version stamp packs**: `pre-refactor-sprint-20260808/` — never overwrite a pack directory, create new ones.

---

## 13. SOVEREIGN BOUNDARY PROTOCOLS

### 13.1 Mandates Affecting Web Claude Usage
| Mandate | What It Means for Web Claude |
|---------|------------------------------|
| **M1 AnyIO** | All code recommendations must use AnyIO — reject any asyncio suggestions |
| **M2 Engine-Stack Firewall** | No WAD-specific logic in core engine recommendations |
| **M7 Local-First** | Prefer local inference solutions; flag any cloud-dependent recommendations |
| **M8 Zero Telemetry** | Context packer must strip all telemetry endpoints; no analytics in generated code |
| **M9 Error Integrity** | Typed errors, no bare `except:` in any generated code |
| **M13 Temple-Grade** | All generated artifacts must pass T1-T11 checklist before integration |
| **M14 Heritage Vetting** | Flag any `[id-soft:]` tags without vet records in HERITAGE_VET_LOG.md |
| **M16 Modularization** | No hardcoded paths in generated core code |
| **M23 Failure Integrity** | Web Claude's "soft suggestions" are not law — validate locally before implementing |

### 13.2 PII & Secrets Protocol
The Context Packer handles this automatically (TOKENIZE mode). But always verify:
```
☐ No API keys in bundled files
☐ No .env content included
☐ No personal account credentials
☐ No production database URLs
☐ Soul.yaml NOT included (entity internal state stays local)
```
If you ever manually add files to a pack (bypassing the packer), run the above checklist manually.

### 13.3 The Boundary Principle
**Content can cross the boundary (sanitized). Decisions stay local.**

Web Claude is a reviewer, not a decision-maker. Its output is a recommendation. The local OpenCode CLI agent — with full context of the engine's history, prior decisions, and mandate obligations — makes the final call on what gets implemented.

---

## 14. QUICK REFERENCE CARDS

### Card 1: Full Session Checklist
```
PRE-SESSION (OpenCode CLI):
☐ Identify task type → select appropriate packer profile
☐ Run packer: python .opencode/skills/context-packer/packer.py <profile>
☐ Verify output: ≤12 files, manifest present, PII masked
☐ Check account tracker → select next available account

SETUP (claude.ai):
☐ Create/open Project with task-named title
☐ Paste CLAUDE_PROJECT_SYSTEM_PROMPT.md into Custom Instructions
☐ Upload all .md files from pack EXCEPT system prompt and chat initiation
☐ Verify direct context mode: "List all files in project knowledge"

SESSION:
☐ Paste CHAT_INITIATION_PROMPT.md as first message
☐ Select Sonnet 4.6 (Thinking) for deep work
☐ Monitor token usage
☐ Wait for "ARTIFACT COMPLETE" signal

POST-SESSION (OpenCode CLI):
☐ Download artifact as .md with versioned filename
☐ Save to docs/hardening/omega-hub/claude-project/artifacts/
☐ Tell OpenCode CLI agent to read and validate artifact
☐ Run agent validation checklist
☐ Log in WEB_CLAUDE_ARTIFACT_REGISTRY.md
☐ Update account tracker
```

### Card 2: Pack Build Checklist
```
☐ Profile selected in packer-config.yaml
☐ Include: target source files, mandates, recent decisions
☐ Exclude: .venv, __pycache__, secrets, soul.yaml, data/
☐ max_slots: 12 enforced
☐ PII masking: TOKENIZE mode active
☐ Output: context_packs/<profile-date>/
☐ Manifest: 00_PROJECT_MANIFEST.md present
☐ System prompt: CLAUDE_PROJECT_SYSTEM_PROMPT.md present
☐ Chat prompt: CHAT_INITIATION_PROMPT.md present
☐ Total tokens: ≤80K (check manifest)
```

### Card 3: Account Tracker Quick View
```
See: data/coordination/WEB_CLAUDE_ACCOUNT_TRACKER.md
Rotation: top-to-bottom through Google login list
Reset: 5-hour rolling window from last heavy usage
Rule: never run same task on two accounts simultaneously
```

---

## 15. HYDRATION PROTOCOL

**Before any agent assists with Web Claude work, they MUST:**

1. Read this entire document
2. Read `data/coordination/WEB_CLAUDE_ARTIFACT_REGISTRY.md` — what has already been sent/received?
3. Read `data/coordination/WEB_CLAUDE_ACCOUNT_TRACKER.md` — which accounts are available?
4. Identify the task type → map to project type template (§6.4)
5. Confirm the right packer profile exists or create one
6. After ingesting a returned artifact: log it in the registry before proceeding

---

## 16. SOURCE CITATIONS

### Tier 1: Official
- Anthropic Projects RAG: https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects
- Anthropic XML Tags: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags
- Anthropic Prompt Caching: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- OWASP LLM Injection: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html

### Tier 2: Community & Research (2026)
- Liu et al. 2023 — Lost in the Middle (attention curve): https://arxiv.org/abs/2307.03172
- AI Tools Guidebook 2026: https://aitoolsguidebook.com/en/articles/claude-projects-advanced-workflow
- Practicaly.ai 2026: https://www.practicaly.ai/p/what-are-md-files-in-claude

### Tier 3: Local Research
- `docs/research/R_CONTEXT_PACK_FORMAT_MD_VS_XML_20260808.md` — Format decision evidence
- `.opencode/skills/context-packer/SKILL.md` — Packer documentation
- `data/coordination/WEB_CLAUDE_ARTIFACT_REGISTRY.md` — Artifact history

---

*⬡ OMEGA ⬡ KALI ⬡ antigravity-claude-sonnet-4-6 ⬡ opencode ⬡ trc_playbook ⬡ 2026-08-08 v2.0.0*
