# 🔱 Context Pack Format: Markdown vs XML — Definitive Answer
**AP Token**: `AP-CONTEXT-PACK-FORMAT-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE
**Date**: 2026-08-08
**Status**: DEFINITIVE — resolves Gap 2 (Data Format Selection) for Web Claude context packs

---

## ❓ The Question

Should context pack files be `.md` or `.xml`? Or a combination?

## ✅ The Definitive Answer

**Neither alone. It is a layered decision:**

| Layer | Format | Why |
|-------|--------|-----|
| **System prompt / Custom Instructions** | **XML tags** | Native boundary clarity, Claude training-data affinity, prompt-injection defense |
| **Knowledge / reference files** (uploaded) | **Markdown** | Token-efficient, human-readable, RAG-searchable (Claude parses headings/lists) |
| **Structured data** (schemas, configs) | **JSON** | Machine-to-machine, schema enforcement |

> **"MD is the safest for general purposes. However, using different formats for different layers is the practical solution."** — Cross-model consensus (Claude, Gemini, ChatGPT), zenn.dev 2026-05-31

---

## 📚 Evidence

### 1. Layered consensus (all three providers agree)
Source: https://zenn.dev/shomitei/articles/ai-doc-format-3models (2026-05-31, cross-model comparison)

| Layer | Role | Recommended Format |
|-------|------|--------------------|
| Prompt Structure | Defining boundaries and roles | **XML** |
| Content | Body text readable by humans | **Markdown** |
| Data | Structured/schema-based data | **JSON** |
| Web Ingestion | Temporary state before conversion | HTML (→ convert to MD) |

- **XML**: closing tags make it hard to misinterpret where instructions end and input begins; acts as prompt-injection defense. Claude's training data is rich in XML. Anthropic's official guide recommends `<document>`, `<instructions>` tags.
- **Markdown**: most token-efficient (HTML→MD reduces tokens 20-30%); Claude navigates headings/subheadings to find sections. Best for RAG/knowledge bases.
- **Provider affinity ranking** (XML): Claude > ChatGPT > Gemini. Claude pushes XML; Gemini says "MD delimiters are enough"; ChatGPT is use-case-dependent.

### 2. Anthropic official guidance
  Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- "Structure prompts with XML tags" — XML tags help Claude parse complex prompts unambiguously.
- "Put longform data at the top" — improves performance across all models.
- For multiple documents: wrap each in `<documents><document>` with `<source>` + `<document_content>` subtags.

### 3. Claude Projects KB (our own, v2.0.0)
  Source: `docs/kb/CLAUDE_PROJECTS.md`
- **File format table**: `.md` = "Best — Claude-native, most searchable" for documentation/specs.
- **System prompt**: XML tags create clearer semantic boundaries than markdown headers alone. **ClaSSIC template** (`<role> <context> <constraints> <rules> <project_files> <output_format>`).
- **Force KB search** directive at top of Custom Instructions.

### 4. Our own platform-tuning research (2026-07-18)
  Source: `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md`
- Web Claude (Sonnet 5): **XML native** — "XML tags are genuinely the best structuring method for Claude."
- Web Gemini: **Markdown + structured** — Gemini excels with clear Markdown headings.
- Web Grok: **XML + Markdown hybrid**.

### 5. Our own knowledge-gaps research (2026-07-19)
  Source: `docs/research/R_CONTEXT_PACKER_KNOWLEDGE_GAPS_20260719.md` §Gap 2
- XML = baseline (1.0x tokens), Claude comprehension ⭐⭐⭐⭐⭐ (native)
- Markdown = ~0.85x (15% fewer tokens), comprehension ⭐⭐⭐⭐ (good)
- **Primary**: XML (Claude-native); **Manifest**: Markdown (human entry point)

---

## 📐 Application to `context_packs/tech-architecture-research/`

### Current state (9 files, all `.md`)
| File | Role | Correct format? |
|------|------|-----------------|
| `CLAUDE_PROJECT_SYSTEM_PROMPT.md` | System prompt (pasted, NOT uploaded) | ⚠️ **Should be XML tags** — currently uses `## ROLE`, `## CONTEXT` markdown headers |
| `CHAT_INITIATION_PROMPT.md` | First message | ✅ Markdown (content) |
| `PROJECT_KNOWLEDGE_INDEX.md` | Index/manifest | ✅ Markdown (human entry point) |
| `GROUNDED_TRUTH.md` | Reference | ✅ Markdown |
| `KEY_MANDATES.md` | Reference | ✅ Markdown |
| `DECISION_MATRIX_TEMPLATE.md` | Reference | ✅ Markdown |
| `RESEARCH_BRIEF.md` | Reference | ✅ Markdown |
| `RESEARCH_REPORT.md` | Reference | ✅ Markdown |
| `UNOVERENGINEERING_PLAN.md` | Reference | ✅ Markdown |

### The one refinement needed
The **system prompt** (`CLAUDE_PROJECT_SYSTEM_PROMPT.md`) is pasted into the Custom Instructions box — it is NOT uploaded as a knowledge file. Per Anthropic guidance + our own ClaSSIC template, it should use **XML tags** for the instruction boundaries, not markdown headers.

Current (markdown headers):
```markdown
## ROLE
...
## PROJECT CONTEXT
...
## BEHAVIORAL DIRECTIVES
```

Recommended (XML tags, per ClaSSIC template):
```xml
<role>...</role>
<context>...</context>
<constraints>...</constraints>
<rules>...</rules>
<project_files>...</project_files>
<output_format>...</output_format>
```

### Why the knowledge files should STAY markdown
1. **RAG-searchable**: Claude parses headings/lists to find the right section during retrieval.
2. **Token-efficient**: MD uses ~15% fewer tokens than XML.
3. **Human-reviewable**: The user reads these files; MD is the human entry point.
4. **Update-friendly**: MD re-uploads cleanly without reformatting.

### Why the system prompt should be XML
1. **Boundary semantics**: Closing tags prevent misinterpretation of where instructions end.
2. **Claude-native**: Anthropic's training data is XML-rich; official docs recommend it.
3. **Prompt-injection defense**: XML boundaries harden against injection.
4. **Consistency**: Matches our documented ClaSSIC template and prior packs (provider-fabric-review used `.xml` for content bundles).

---

## 🎯 Bottom Line

| Question | Answer |
|----------|--------|
| Should knowledge files be `.md` or `.xml`? | **`.md`** — token-efficient, RAG-searchable, human-readable |
| Should the system prompt be `.md` or `.xml`? | **`.xml`** — native boundary semantics, Claude affinity |
| Combination? | **YES** — Markdown for content, XML for structure, JSON for data |

**Action**: Convert `CLAUDE_PROJECT_SYSTEM_PROMPT.md` to XML-tagged structure (keep `.md` extension for the file, but use XML tags inside — it is pasted, not uploaded). Keep all 8 knowledge files as `.md`.

---

## References
- https://zenn.dev/shomitei/articles/ai-doc-format-3models (2026-05-31) — cross-model format comparison
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices — Anthropic XML guidance
- https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects — RAG for projects
- `docs/kb/CLAUDE_PROJECTS.md` — our Claude Projects KB (v2.0.0)
- `docs/research/R_CONTEXT_PACKER_PLATFORM_TUNING_20260718.md` — platform tuning
- `docs/research/R_CONTEXT_PACKER_KNOWLEDGE_GAPS_20260719.md` — Gap 2 format selection

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_research ⬡ 2026-08-08*