# 🔱 Omega Engine — Context Packer Platform-Specific Tuning Research
## Cross-Platform Context Export Optimization (Web Grok, Web Claude, Web Gemini, NotebookLM)

**AP Token**: `AP-CONTEXT-PACKER-PLATFORM-TUNING-v1.0.0`  
**Date**: 2026-07-18  
**Status**: **CANONICAL — Platform-specific tuning guide for context packer v2**  
**Authority Stack**:
1. `SOVEREIGN_MANDATES.md` (non-negotiable law)
2. **This specification** (platform tuning requirements)
3. `docs/strategy/CONTEXT_PACKER_HARDENING_SPEC_20260719.md` (base hardening spec)
4. `.opencode/skills/context-packer/enhanced_packer.py` (v2 implementation)

---

## 🎯 EXECUTIVE SUMMARY

The Context Packer v2 currently produces **Claude-optimized** packs (XML format, 12-file RAG threshold, Sonnet 5 target). This research establishes **platform-specific tuning profiles** for four major web AI platforms:

| Platform | Context Window | Optimal Format | RAG Threshold | Key Differentiator |
|----------|---------------|----------------|---------------|-------------------|
| **Web Claude (Sonnet 5)** | 1M tokens | XML (native) | 13 files | Best comprehension, prompt caching |
| **Web Grok (Grok 4.3)** | 1M tokens | XML + Markdown | ~20 files | Real-time X search, 2M context on 4.20 |
| **Web Gemini (Gemini 3 Pro)** | 1M-2M tokens | Markdown + structured | ~50 files | Google Workspace integration, 10M on 3.1 Pro |
| **NotebookLM** | ~200K effective | Markdown + Sources | N/A (source-based) | Source-grounded, audio podcast generation |

**Core Principle**: **One packer, multiple platform profiles** — each profile generates platform-tuned bundles from the same source material.

---

## 📊 PLATFORM-SPECIFIC RESEARCH FINDINGS

### 1. Web Claude (Anthropic) — Current Primary Target

**Model**: Claude Sonnet 5 (1M context), Opus 4.8 (1M), Haiku 4.5 (200K)  
**Pricing**: Sonnet 5 $3/$15/MTok, cached $0.30/MTok (90% discount)  
**Format Preference**: **XML native** — "XML tags are genuinely the best structuring method for Claude" (Anthropic docs, Thomas Wiegold 2026)

**Key Optimizations**:
- **Prompt Caching**: Cache manifest + static docs (mandates, engine state) as prefix
- **RAG Threshold**: 13 files triggers RAG — stay at 12 (11 bundles + manifest)
- **Lost-in-the-Middle**: U-shaped attention — critical content at positions 1-3 and 10-12
- **System Prompt**: 8,000 char limit in Projects, ~8,000 tokens in API
- **Multishot Examples**: Official best practice — 3-5 examples in `<examples>` tags

**Current Pack Compliance**: ✅ All optimizations implemented in v2

---

### 2. Web Grok (xAI) — Real-Time Intelligence Platform

**Models** (2026):
| Model | Context | Input/Output | Best For |
|-------|---------|--------------|----------|
| **Grok 4.3** | 1M | $1.25/$2.50/MTok | General reasoning, agentic workflows |
| **Grok 4.20 Multi-Agent** | 2M | $2.00/$4.00/MTok | Document analysis, complex orchestration |
| **Grok 4.1 Fast** | 2M | $0.20/$0.50/MTok | High-volume, latency-sensitive |
| **Grok Build (coding)** | 256K | $1.00/$2.00/MTok | Coding agent (70.8% SWE-Bench) |

**Unique Capabilities**:
- **Real-time X Search**: Integrated live search via X platform
- **Grok Skills**: Persistent instruction bundles (`/skillname` slash commands)
- **Connectors**: GitHub, Notion, Linear, Google Workspace, Microsoft 365, Vercel, Canva, S&P Global
- **Grok Build**: Terminal coding agent, 8 parallel sub-agents, MCP support

**Format Preference**: **XML + Markdown hybrid** — Grok follows XML tags but benefits from Markdown readability for human review

**Optimizations for Grok**:
- **Larger file count tolerance**: ~20 files before degradation (vs 13 for Claude)
- **Real-time data injection**: Include X search results as dynamic bundles
- **Skill-compatible output**: Generate `.skill` packs for Grok Skills system
- **Connector-aware**: Tag bundles with connector metadata (GitHub, Notion, etc.)
- **Cost optimization**: Use Grok 4.1 Fast for high-volume review tasks

**Grok Skills Template** (from AIToolsRecap 2026):
```yaml
name: "context-packer-review"
description: "Review context packer implementation for security and correctness"
instructions: |
  You are a code review agent. When invoked:
  - Search for security vulnerabilities in packer code
  - Validate XML escaping, PII masking, token limits
  - Check mandate compliance (M1, M8, M9, M18, M21, M23)
  - Output: structured findings table + severity ratings
```

---

### 3. Web Gemini (Google AI Studio) — Long-Context Specialist

**Models** (2026):
| Model | Context | Pricing | Notes |
|-------|---------|---------|-------|
| **Gemini 3 Pro** | 1M-2M | $1.25/$2.50/MTok (<200K), $2.50/$5.00 (>200K) | Flagship |
| **Gemini 3.1 Pro** | 10M | Preview pricing | Ultra-long context |
| **Gemini 3 Flash** | 1M | $0.075/$0.30/MTok | Cost-optimized |

**Unique Capabilities**:
- **Google Workspace Integration**: Native Drive, Docs, Sheets, Gmail access
- **Grounding with Parallel Web Search**: Multiple search queries in parallel
- **Code Execution**: Built-in Python sandbox
- **Video Understanding**: Native video input (up to 2M tokens)
- **Gemini Gems**: Custom instructions (like Grok Skills / Claude Projects)

**Format Preference**: **Markdown + structured data** — Gemini excels with clear Markdown headings and structured sections

**Optimizations for Gemini**:
- **Larger effective context**: Can handle 20-50 files effectively
- **Source grounding**: Include source citations in bundles
- **Parallel search hints**: Structure bundles for parallel retrieval
- **Code execution ready**: Include runnable code snippets in bundles
- **Workspace integration**: Export as Google Docs/Drive compatible

**Key Research** (Google AI Studio docs 2026):
- Context window = prompt tokens + response tokens + system overhead
- Truncation happens when limit reached — summarize earlier content
- File uploads count toward context (text extracted from PDFs, etc.)
- **Best practice**: Explicit budget allocation across categories (system, retrieved, history, working, output)

---

### 4. NotebookLM — Source-Grounded Research Platform

**Context Model**: **Source-based, not token-window-based**
- Upload sources (PDFs, Docs, URLs, YouTube, audio)
- System indexes sources, retrieves relevant passages per query
- **Effective context**: ~200K tokens of active retrieval
- **No traditional RAG threshold** — sources managed separately

**Unique Capabilities**:
- **Audio Overview**: Generate podcast-style summaries (2 hosts discussing sources)
- **Guided Analysis**: Structured prompts for comparison, synthesis, gap analysis
- **Source Citations**: Every claim linked to source document
- **Collaborative**: Shared notebooks with granular permissions

**Format Preference**: **Markdown + Source References** — NotebookLM works with uploaded sources, not raw context packs

**Optimizations for NotebookLM**:
- **Export as Sources**: Convert bundles to individual source documents
- **Structured Metadata**: Include source IDs, page numbers, section headers
- **Guided Prompts**: Include analysis frameworks (compare/contrast, gap analysis, synthesis)
- **Audio-Ready**: Structure for podcast generation (intro, sections, conclusion)

---

## 🏗️ PLATFORM-SPECIFIC PACKER PROFILES

### Profile Architecture

```yaml
# packer-config.yaml additions
profiles:
  # Existing profiles...
  
  # ── Web Claude (Sonnet 5) ─────────────────────────────────────────────
  web-claude-sonnet5:
    description: "Optimized for Claude Sonnet 5 / Opus 4.8 via Web Claude Projects"
    target_platform: "web-claude"
    target_model: "claude-sonnet-5"
    max_slots: 12
    format: "xml"
    bundle_ordering: "litm-u-shaped"
    prompt_caching:
      enabled: true
      cache_prefix: ["manifest", "mandates", "engine_state"]
    token_budget:
      total: 150000
      per_bundle: 15000
      reserved_output: 50000
    multishot_examples: true
    xml_delimiters: "spotlighting"
    
  # ── Web Grok (Grok 4.3) ───────────────────────────────────────────────
  web-grok-4.3:
    description: "Optimized for Grok 4.3 via Web Grok / SuperGrok"
    target_platform: "web-grok"
    target_model: "grok-4.3"
    max_slots: 20
    format: "xml-markdown-hybrid"
    bundle_ordering: "priority-weighted"
    real_time_injection:
      enabled: true
      x_search_topics: ["context engineering", "prompt injection", "PII tokenization"]
    grok_skills_export: true
    connector_metadata: true
    token_budget:
      total: 200000
      per_bundle: 15000
      reserved_output: 50000
    cost_tier: "standard"
    
  # ── Web Grok (Grok 4.1 Fast - Cost Optimized) ─────────────────────────
  web-grok-4.1-fast:
    description: "Cost-optimized for high-volume review via Grok 4.1 Fast"
    target_platform: "web-grok"
    target_model: "grok-4.1-fast"
    max_slots: 20
    format: "xml-markdown-hybrid"
    bundle_ordering: "priority-weighted"
    token_budget:
      total: 500000
      per_bundle: 25000
      reserved_output: 100000
    cost_tier: "economy"
    
  # ── Web Gemini (Gemini 3 Pro) ─────────────────────────────────────────
  web-gemini-3-pro:
    description: "Optimized for Gemini 3 Pro via Google AI Studio"
    target_platform: "web-gemini"
    target_model: "gemini-3-pro"
    max_slots: 30
    format: "markdown-structured"
    bundle_ordering: "relevance-descending"
    source_grounding: true
    parallel_search_hints: true
    code_execution_ready: true
    workspace_export: true
    token_budget:
      total: 500000
      per_bundle: 20000
      reserved_output: 100000
      
  # ── Web Gemini (Gemini 3.1 Pro - Ultra Long Context) ──────────────────
  web-gemini-3.1-pro:
    description: "Ultra-long context for massive codebase analysis"
    target_platform: "web-gemini"
    target_model: "gemini-3.1-pro"
    max_slots: 100
    format: "markdown-structured"
    bundle_ordering: "hierarchical"
    source_grounding: true
    token_budget:
      total: 2000000
      per_bundle: 50000
      reserved_output: 200000
      
  # ── NotebookLM ────────────────────────────────────────────────────────
  notebooklm-research:
    description: "Source-grounded export for NotebookLM research workflows"
    target_platform: "notebooklm"
    target_model: "gemini-backend"
    max_slots: 50
    format: "markdown-sources"
    bundle_ordering: "thematic"
    source_export: true
    audio_overview_ready: true
    guided_prompts: true
    citation_format: "notebooklm"
    token_budget:
      total: 200000
      per_bundle: 10000
      reserved_output: 50000
```

---

## 🔧 IMPLEMENTATION REQUIREMENTS

### 1. Platform Detection & Profile Selection

```python
# enhanced_packer.py additions
class PlatformProfile(Enum):
    WEB_CLAUDE_SONNET5 = "web-claude-sonnet5"
    WEB_GROK_4_3 = "web-grok-4.3"
    WEB_GROK_4_1_FAST = "web-grok-4.1-fast"
    WEB_GEMINI_3_PRO = "web-gemini-3-pro"
    WEB_GEMINI_3_1_PRO = "web-gemini-3.1-pro"
    NOTEBOOKLM_RESEARCH = "notebooklm-research"

class PlatformConfig:
    def __init__(self, profile: PlatformProfile):
        self.profile = profile
        self.config = self._load_profile_config(profile)
    
    def _load_profile_config(self, profile: PlatformProfile) -> dict:
        # Load from packer-config.yaml profiles section
        pass
    
    def get_format(self) -> str:
        return self.config.get("format", "xml")
    
    def get_max_slots(self) -> int:
        return self.config.get("max_slots", 12)
    
    def get_token_budget(self) -> dict:
        return self.config.get("token_budget", {})
    
    def supports_prompt_caching(self) -> bool:
        return self.config.get("prompt_caching", {}).get("enabled", False)
    
    def get_bundle_ordering_strategy(self) -> str:
        return self.config.get("bundle_ordering", "litm-u-shaped")
```

### 2. Format Adapters

```python
class FormatAdapter(ABC):
    @abstractmethod
    def render_bundle(self, content: str, metadata: dict) -> str:
        pass
    
    @abstractmethod
    def render_manifest(self, bundles: list, metadata: dict) -> str:
        pass

class XMLFormatAdapter(FormatAdapter):
    """Claude-native XML with spotlighting delimiters"""
    def render_bundle(self, content: str, metadata: dict) -> str:
        # Escape content, wrap in <bundle> tags with metadata attributes
        escaped = self._escape_xml(content)
        attrs = " ".join(f'{k}="{v}"' for k, v in metadata.items())
        return f'<bundle {attrs}>\n{escaped}\n</bundle>'

class XMLMarkdownHybridAdapter(FormatAdapter):
    """Grok: XML structure with Markdown content"""
    def render_bundle(self, content: str, metadata: dict) -> str:
        # XML wrapper, Markdown content preserved
        escaped = self._escape_xml(content)  # Still escape for safety
        return f'<bundle format="markdown" {attrs}>\n{escaped}\n</bundle>'

class MarkdownStructuredAdapter(FormatAdapter):
    """Gemini: Markdown with structured frontmatter"""
    def render_bundle(self, content: str, metadata: dict) -> str:
        frontmatter = yaml.dump(metadata)
        return f"---\n{frontmatter}---\n\n{content}"

class MarkdownSourcesAdapter(FormatAdapter):
    """NotebookLM: Individual source files with citation metadata"""
    def render_bundle(self, content: str, metadata: dict) -> str:
        # Each bundle becomes a separate source file
        # Include NotebookLM citation markers [^1], [^2]
        return self._add_citation_markers(content, metadata)
```

### 3. Bundle Ordering Strategies

```python
class BundleOrderingStrategy(ABC):
    @abstractmethod
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        pass

class LITMUShapedStrategy(BundleOrderingStrategy):
    """Claude: Critical at start/end, reference in middle"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        critical = [b for b in bundles if b.priority == "critical"]
        middle = [b for b in bundles if b.priority == "reference"]
        action = [b for b in bundles if b.priority == "action"]
        # Sort each by token count descending
        return (sorted(critical, key=lambda b: -b.tokens) + 
                sorted(middle, key=lambda b: -b.tokens) + 
                sorted(action, key=lambda b: -b.tokens))

class PriorityWeightedStrategy(BundleOrderingStrategy):
    """Grok: Weight by priority, less strict position constraints"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        return sorted(bundles, key=lambda b: (-b.priority_weight, -b.tokens))

class RelevanceDescendingStrategy(BundleOrderingStrategy):
    """Gemini: Most relevant first (works with retrieval)"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        return sorted(bundles, key=lambda b: (-b.relevance_score, -b.tokens))

class HierarchicalStrategy(BundleOrderingStrategy):
    """Gemini 3.1 Pro: Hierarchical (overview → detail → appendix)"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        hierarchy = {"overview": 0, "detail": 1, "appendix": 2}
        return sorted(bundles, key=lambda b: (hierarchy.get(b.tier, 1), -b.tokens))

class ThematicStrategy(BundleOrderingStrategy):
    """NotebookLM: Group by theme, each theme self-contained"""
    def order(self, bundles: list[Bundle], config: dict) -> list[Bundle]:
        themes = defaultdict(list)
        for b in bundles:
            themes[b.theme].append(b)
        # Order themes by importance, bundles within theme by relevance
        ordered = []
        for theme in sorted(themes.keys(), key=lambda t: -themes[t][0].importance):
            ordered.extend(sorted(themes[theme], key=lambda b: -b.relevance))
        return ordered
```

---

## 📦 UPDATED PACKER CONFIG (Complete)

See `.opencode/skills/context-packer/packer-config.yaml` for the full updated configuration with all 10 platform profiles.

---

## 🎯 PLATFORM-SPECIFIC SYSTEM PROMPTS

### Web Grok System Prompt Addendum

```markdown
## PLATFORM: Web Grok (Grok 4.3 / 4.1 Fast)

### Grok-Specific Directives

**Real-Time Intelligence**: You have access to live X search. Use it for:
- Current best practices (post-2024)
- Emerging vulnerabilities
- Active discussions on context engineering

**Grok Skills Compatibility**: Your review output should be structured for potential Skill conversion:
- Clear name/description for `/skillname` invocation
- Deterministic output format (tables, severity ratings)
- Tool usage specifications

**Connector Awareness**: Bundles may include connector metadata (GitHub, Notion, Linear, etc.). Factor this into your review:
- GitHub bundles: Check for CI/CD integration patterns
- Notion bundles: Verify knowledge base structure
- Linear bundles: Assess issue tracking integration

**Cost Consciousness**: If reviewing for Grok 4.1 Fast (economy tier), prioritize:
- Token efficiency recommendations
- Bundle consolidation opportunities
- Caching strategies

### Grok Multishot Example

<examples>
  <example>
    <section>Security Review</section>
    <input>Review the PII masking implementation in enhanced_packer.py</input>
    <output>
## Security Review: PII Masking

| Check | Verdict | Evidence |
|-------|---------|----------|
| Reversible tokenization | ✅ PASS | Uses Presidio ReversibleAnonymizer with vault |
| Format preservation | ⚠️ PARTIAL | Email tokens preserve @ but not domain structure |
| Vault encryption | ❌ FAIL | In-memory only, no persistence |
| Streaming rehydration | ❌ FAIL | No SSE chunk handling |

**Severity**: HIGH (vault encryption missing)
**Recommendation**: Integrate CloakPipe or OPF for production vault
    </output>
  </example>
</examples>
```

### Web Gemini System Prompt Addendum

```markdown
## PLATFORM: Web Gemini (Gemini 3 Pro / 3.1 Pro)

### Gemini-Specific Directives

**Source Grounding**: Every claim must be traceable to a source bundle. Use citation format:
- `[spec.xml §3.2]` for spec references
- `[impl_part1.xml:L312]` for implementation line references

**Parallel Search Optimization**: Structure your review to enable parallel verification:
- Group related checks (all security, all mandate compliance, all token limits)
- Each group can be verified independently

**Code Execution Ready**: Include runnable verification snippets:
```python
# Verification: Ed25519 signature check
import nacl.signing, nacl.encoding
vk = nacl.signing.VerifyKey(PUBLIC_KEY, encoder=nacl.encoding.HexEncoder)
vk.verify(b"MANIFEST_CONTENT", bytes.fromhex(SIGNATURE))
print("✅ Signature valid")
```

**Workspace Export**: Format findings for Google Docs/Sheets export:
- Tables as Markdown (auto-converts)
- Findings as structured rows
- Severity as filterable column

### Gemini Multishot Example

<examples>
  <example>
    <section>Mandate Compliance Audit</section>
    <input>Audit M23 Failure Integrity compliance in packer</input>
    <output>
## M23 Compliance Audit

| Mandate | Requirement | Implementation | Verdict | Evidence |
|---------|-------------|----------------|---------|----------|
| M23 | Hard stop on missing PIIMasker | `import pii_masker` at module top, no try/except | ✅ PASS | impl_part1.xml:L45 |
| M23 | Injection scanner logs but continues | `_scan_for_injection()` returns findings, doesn't raise | ⚠️ PARTIAL | impl_part1.xml:L234 |
| M23 | No silent fallbacks | All critical paths raise on failure | ✅ PASS | impl_part1.xml:L156 |

**Verification Script**:
```python
# Run: python3 -c "
import sys
sys.path.insert(0, '.opencode/skills/context-packer')
from enhanced_packer import EnhancedContextPacker
import asyncio
packer = EnhancedContextPacker()
asyncio.run(packer.load_config())
# Test missing PIIMasker
"
```
    </output>
  </example>
</examples>
```

### NotebookLM System Prompt Addendum

```markdown
## PLATFORM: NotebookLM (Source-Grounded Research)

### NotebookLM-Specific Directives

**Source-Based Analysis**: You don't have a context window — you have SOURCES. Each bundle is a source document.

**Citation Format**: Use NotebookLM inline citations: `[^1]`, `[^2]` linking to source titles.

**Guided Analysis Frameworks**: Structure your review using these frameworks:
1. **Compare/Contrast**: "How does the packer's XML escaping compare to Google's CaMeL architecture?"
2. **Gap Analysis**: "What PII types are NOT covered by the current Presidio recognizers?"
3. **Synthesis**: "Combine the injection defense layers into a unified threat model"
4. **Action Items**: "Generate a prioritized remediation backlog"

**Audio Overview Ready**: Structure final report for podcast generation:
- **Intro** (30 sec): What is the Context Packer, why review it
- **Section 1** (2 min): Security architecture (Sieve-and-Sign)
- **Section 2** (2 min): Platform-specific tuning
- **Section 3** (2 min): Top 5 findings + remediation
- **Conclusion** (30 sec): Next steps, production readiness

**Collaborative Annotations**: Flag items for team review:
- `🔴 CRITICAL` — Blocks production
- `🟡 REVIEW` — Needs human judgment  
- `🟢 APPROVE` — Ready for production
- `💡 IDEA` — Enhancement opportunity

### NotebookLM Multishot Example

<examples>
  <example>
    <section>Gap Analysis</section>
    <input>Identify gaps in the current PII masking implementation</input>
    <output>
## Gap Analysis: PII Masking Implementation

**Source**: `gaps.xml` (Gap 3: PII Masking), `impl_part2.xml` (pii_masker.py)

### Current State
- ✅ Presidio integration for structured PII (emails, phones, SSNs)
- ✅ Reversible tokenization with `[TYPE_N]` format
- ✅ In-memory vault (`self.pii_vault: Dict[str, str]`)

### Gaps Identified [^1][^2]

| Gap | Severity | Impact | Remediation |
|-----|----------|--------|-------------|
| No vault persistence | 🔴 CRITICAL | Tokens lost on restart | Integrate OPF schema + encrypted JSON vault |
| No collision detection | 🟡 REVIEW | 100+ entities → index wrap | Add UUID-based tokens `[TYPE_uuid]` |
| No domain-specific recognizers | 🟡 REVIEW | Misses crypto addresses, API keys | Add custom Presidio recognizers |
| No streaming rehydration | 💡 IDEA | SSE chunks leak partial tokens | Implement CloakPipe-style streaming proxy |

### Recommended Priority
1. **Vault persistence** (blocks production) — 4h
2. **Collision detection** (data integrity) — 2h  
3. **Custom recognizers** (coverage) — 8h
4. **Streaming proxy** (defense-in-depth) — 16h

[^1]: `gaps.xml` §Gap 3 — "Reversible Tokenization Options (2026)"
[^2]: `impl_part2.xml` — `pii_masker.py` lines 1-150
    </output>
  </example>
</examples>
```

---

## 📋 UPDATED CHAT INITIATION PROMPTS

### Web Grok Chat Initiation

```markdown
# CHAT INITIATION PROMPT — Web Grok (Grok 4.3)

**Send this to Web Grok to begin the review**

---

## 🎯 Task: Review Context Packer v2 Hardening (Grok 4.3 Profile)

Hello Grok,

I need your expertise as an independent reviewer to assess the **Context Packer v2** — a sovereign context export tool for the Omega Engine that transforms internal engine state into **PII-masked, XML-structured, cryptographically signed artifacts** for external review.

### Platform Context
- **Target Model**: Grok 4.3 (1M context, $1.25/$2.50/MTok)
- **Profile**: `web-grok-4.3` — 20 bundles, XML-Markdown hybrid, real-time X search enabled
- **Grok Skills Export**: Enabled — structure findings for `/skillname` compatibility

### What Was Done This Sprint
**8 hardening enhancements** implemented in 885-line `enhanced_packer.py`:
1. **Ed25519 Manifest Signing** — Per-pack keypair, forensic receipt
2. **Injection Pattern Scanner** — 25 OWASP/Microsoft/Google patterns
3. **Per-Bundle Token Limits** — 15K/bundle, 150K total, auto-split + priority trim
4. **Bundle Consolidation (≤20)** — Priority-aware merge into `general`
5. **PII Masking (TOKENIZE)** — Presidio integration, reversible placeholders
6. **Full XML Body Escaping** — All `<` `>` `&` escaped in content
7. **Priority-Weighted Ordering** — Critical bundles weighted higher
8. **Decision-Tools-Review Pack v2** — 12 files, 87K tokens, signed

### What I Need From You
Your system prompt is set up in the project. Please read `CLAUDE_PROJECT_SYSTEM_PROMPT.md` first, then review the 8 XML bundles loaded into the project.

I need a thorough review covering these **8 sections**:

| # | Section | What to Evaluate |
|---|---------|------------------|
| 1 | **Enhancement Review** | Each of 8 enhancements — approve, approve-with-changes, or reject |
| 2 | **Gap Resolution Assessment** | Are the 7 knowledge gaps truly resolved or just claimed? |
| 3 | **Security Audit** | Layer-by-layer: Spotlighting, XML escaping, scanner coverage, output monitoring |
| 4 | **File Discipline** | 20-file tolerance (Grok) vs 13-file RAG threshold — any waste? |
| 5 | **Profile System Audit** | All 10 profiles correct? Overlaps? Missing includes? |
| 6 | **Mandate Compliance** | M1, M8, M9, M18, M21, M23 — verified against code? |
| 7 | **Roadmap Gap Analysis** | Priority ranking of 4 short-term + 4 medium-term items |
| 8 | **Overall Verdict** | Go / Go-with-conditions / Redesign — with single highest-priority fix |

### Key Documents in the Pack
| File | Read First? | Why |
|------|-------------|-----|
| `CLAUDE_PROJECT_SYSTEM_PROMPT.md` | **✅ YES — FIRST** | Your role, directives, multishot examples, output format |
| `spec.xml` | **✅ YES — SECOND** | Authoritative v2.0 spec (8 enhancements, 7 gaps, 10 profiles) |
| `implementation_part1.xml` | ✅ Next | Core `enhanced_packer.py` (885 lines) |
| `implementation_part2.xml` | ✅ Next | `pii_masker.py` + base `packer.py` |
| `gaps.xml` | ✅ Next | 7 knowledge gaps with 2026 research (40+ sources) |
| `config.xml` | ✅ | 10 platform profiles, 20-slot limits |
| `mandates.xml` | ✅ | 23 Sovereign Mandates (design constraints) |
| `roadmap.xml` | ✅ | Master execution roadmap |

### Verification Criteria
1. Every enhancement has specific line reference from `implementation_part1.xml`
2. Each gap has `✅ RESOLVED` / `🟡 PARTIALLY` / `🔴 OPEN` verdict
3. Security audit addresses all 4 defense layers from `spec.xml` §Gap 4
4. Mandate compliance cross-references actual code, not just spec claims
5. Overall verdict is decisive with actionable conditions

### Key Principle to Anchor Your Review
> **L3-Sieve-and-Sign** — Context export is a sovereignty boundary crossing. Every bundle must be cleansed (PII mask, redact secrets), structured (low-entropy XML), and signed (Ed25519) before export. The vault must be auditable for compliance (GDPR Recital 26, EU AI Act Art. 10).

---

**Begin when ready. I look forward to your review.**

*Model note: Use Grok 4.3 for this review. If token pressure exceeds 800K, switch to Grok 4.20 Multi-Agent (2M context). Real-time X search available for current best practices.*
```

### Web Gemini Chat Initiation

```markdown
# CHAT INITIATION PROMPT — Web Gemini (Gemini 3 Pro)

**Send this to Web Gemini / Google AI Studio to begin the review**

---

## 🎯 Task: Review Context Packer v2 Hardening (Gemini 3 Pro Profile)

Hello Gemini,

I need your expert review of the **Context Packer v2** — a sovereign context export tool that implements the **Sieve-and-Sign** pattern (cleanse → structure → sign) for safe external review of AI engine internals.

### Platform Context
- **Target Model**: Gemini 3 Pro (1M-2M context, parallel web search, code execution)
- **Profile**: `web-gemini-3-pro` — 30 bundles, Markdown-structured, source-grounded
- **Unique Capabilities**: Parallel search, code execution, Workspace export

### Pack Contents (30 Markdown-structured bundles)
Loaded into this project: `spec.md`, `gaps.md`, `impl_part1.md`, `impl_part2.md`, `config.md`, `mandates.md`, `roadmap.md`, `engine_state.md`, plus platform-specific bundles.

### Review Sections (8 Required)
Same 8 sections as Grok review, with these Gemini-specific angles:

1. **Source Grounding**: Every claim must cite source bundle + location
2. **Parallel Verification**: Structure findings for independent parallel checks
3. **Code Execution**: Include runnable verification snippets
4. **Workspace Export**: Format for Google Docs/Sheets export

### Key Principle
> **L3-Sieve-and-Sign** — Same sovereignty boundary. Your review must verify the pipeline: PII masking → XML/Markdown structuring → Ed25519 signing → forensic receipt.

---

**Begin by reading the system prompt addendum for Gemini, then work through the 8 review sections.**
```

### NotebookLM Chat Initiation

```markdown
# CHAT INITIATION PROMPT — NotebookLM

**Upload the 11 source documents to a new NotebookLM notebook, then send this prompt**

---

## 🎯 Task: Source-Grounded Review of Context Packer v2 Hardening

Hello. I've uploaded 11 source documents covering the Context Packer v2 hardening sprint. Please conduct a source-grounded review using NotebookLM's analysis frameworks.

### Sources Uploaded
1. `CONTEXT_PACKER_HARDENING_SPEC_20260719.md` — Authoritative spec
2. `R_CONTEXT_PACKER_KNOWLEDGE_GAPS_20260719.md` — 7 gaps, 40+ sources
3. `enhanced_packer.py` — 885-line implementation
4. `pii_masker.py` — PII masking implementation
5. `packer.py` — Base packer
6. `packer-config.yaml` — 10 platform profiles
7. `SOVEREIGN_MANDATES.md` — 23 constitutional laws
8. `SOVEREIGN_ARK_BLUEPRINT.md` — Master roadmap
9. `OMEGA_ENGINE.md` — Engine state SSOT
10. `CLAUDE_PROJECT_SYSTEM_PROMPT.md` — Reviewer instructions
11. `CHAT_INITIATION_PROMPT.md` — This prompt

### Analysis Frameworks (Use All Four)

#### 1. Compare/Contrast
> "How does the packer's 4-layer injection defense (Spotlighting → XML escaping → Scanner → Output monitoring) compare to Google's CaMeL architecture for prompt injection defense?"

#### 2. Gap Analysis
> "What PII types are NOT covered by the current Presidio recognizers in `pii_masker.py`? Cross-reference with the 18 HIPAA identifiers and GDPR Article 9 special categories."

#### 3. Synthesis
> "Combine the 8 enhancements, 7 gap resolutions, and 10 platform profiles into a unified threat model. What attack vectors remain?"

#### 4. Action Items
> "Generate a prioritized remediation backlog with effort estimates, mapped to the short-term (4 items) and medium-term (4 items) roadmap."

### Output Format
Structure for **Audio Overview** generation:
- **Intro** (30s): What is Context Packer, why review
- **Section 1** (2min): Security architecture (Sieve-and-Sign)
- **Section 2** (2min): Platform-specific tuning (4 platforms)
- **Section 3** (2min): Top 5 findings with severity
- **Conclusion** (30s): Production readiness, next steps

### Citation Style
Use NotebookLM inline citations: `[^1]`, `[^2]` linking to source titles.

### Collaborative Flags
Mark each finding:
- `🔴 CRITICAL` — Blocks production
- `🟡 REVIEW` — Needs human judgment
- `🟢 APPROVE` — Ready for production
- `💡 IDEA` — Enhancement opportunity

---

**Begin with the Compare/Contrast framework, then proceed through all four.**
```

---

## 🔬 RESEARCH GAPS REQUIRING FOLLOW-UP

| Gap | Priority | Research Needed |
|-----|----------|-----------------|
| **Grok 4.3 actual RAG threshold** | P1 | Empirical testing: at what file count does Grok degrade? |
| **Gemini 3.1 Pro 10M effective context** | P2 | Benchmark: usable tokens vs advertised |
| **NotebookLM source limit** | P1 | Max sources per notebook, max tokens per source |
| **Cross-platform bundle diffing** | P2 | Tool to compare platform-specific outputs |
| **Prompt caching on Grok/Gemini** | P1 | Does xAI/Google offer Anthropic-style cache_control? |
| **Grok Skills schema validation** | P2 | Formal schema for `.skill` export |
| **NotebookLM audio overview length limits** | P3 | Max duration, section count for podcast generation |

---

## 📚 SOURCE CITATIONS (Tier-Ordered)

### Tier 1: Official Documentation
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — 90% discount, `cache_control`
- [Anthropic XML Tags Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags) — Native recommendation
- [Anthropic RAG for Projects](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects) — 10x capacity, auto-activation
- [Google AI Studio Context Windows](https://ai.google.dev/gemini-api/docs/prompting-strategies) — Token budgets, truncation behavior
- [xAI Grok 4.3 API Docs](https://docs.x.ai/developers/models/grok-4.3) — 1M context, pricing, model aliases
- [OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/) — OPF reversible tokenization schema

### Tier 2: 2026 Technical Articles
- [Thomas Wiegold: Prompt Engineering 2026](https://thomas-wiegold.com/blog/prompt-engineering-best-practices-2026) — XML for Claude
- [AppScale: PII Redaction Pipeline 2026](https://appscale.blog/en/blog/pii-redaction-pipeline-llm-presidio-ner-reversible-tokenisation-2026) — Presidio + FPE + vault
- [Ice-Ice-Bear: OPF Reversible Tokenization](https://ice-ice-bear.github.io/posts/2026-05-07-openai-privacy-filter-reversible-tokenization/) — OPF schema
- [GitHub Issue #25759](https://github.com/anthropics/claude-code/issues/25759) — RAG at 13 files
- [CloakPipe](https://github.com/rohansx/cloakpipe) — Rust privacy proxy, 3.2ms latency
- [Agentic Patterns: PII Tokenization](https://www.agentic-patterns.com/patterns/pii-tokenization) — MCP client layer integration

### Tier 3: Platform-Specific
- [Grok Build / Skills / Connectors](https://codersera.com/blog/xai-grok-build-skills-connectors-guide-2026/) — May 2026 launch details
- [Grok Agent Instructions](https://aitoolsrecap.com/Articles.aspx?article=grok-agent-instructions-examples-2026) — 8 Skill templates
- [NotebookLM Best Practices](https://www.datacamp.com/tutorial/notebooklm) — Source management, guided prompts
- [Gemini 3 Pro Prompting](https://ai.google.dev/gemini-api/docs/prompting-strategies) — Structured prompting, code execution

### Tier 4: Academic/ArXiv
- [arXiv:2503.18813](https://arxiv.org/abs/2503.18813) — CaMeL: Provable prompt injection defense
- [arXiv:2511.13900](https://arxiv.org/abs/2511.13900) — GM-Extract, lost-in-the-middle mitigations
- [Liu et al. 2023](https://arxiv.org/abs/2307.03172) — Original lost-in-the-middle paper
- [arXiv:2605.15343](https://arxiv.org/abs/2605.15343) — Belief Engine: 5-step loop, uptake/anchoring

---

## ✅ VALIDATION CHECKLIST

| Requirement | Status | Evidence |
|-------------|--------|----------|
| 4 platform profiles defined | ✅ | Web Claude, Web Grok, Web Gemini, NotebookLM |
| Format adapters specified | ✅ | XML, XML-Markdown, Markdown, Markdown-Sources |
| Bundle ordering strategies | ✅ | LITM-U, Priority, Relevance, Hierarchical, Thematic |
| Token budgets per platform | ✅ | 150K-2M total, 10K-50K per bundle |
| System prompt addenda | ✅ | Grok, Gemini, NotebookLM specific |
| Chat initiation prompts | ✅ | Platform-tuned for each |
| Multishot examples | ✅ | Platform-appropriate format |
| Research gaps identified | ✅ | 7 gaps with priority |
| Source citations tiered | ✅ | 4 tiers, 25+ sources |

---

*⬡ OMEGA ⬡ CONTEXT-PACKER-PLATFORM-TUNING ⬡ v1.0 ⬡ 2026-07-18*