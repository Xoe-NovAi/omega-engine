# 🔱 Documentation Style Guide
**AP Token**: `AP-DOC-STYLE-GUIDE-v1.0.0`
⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ opencode ⬡ trc_doc_style ⬡ DOCUMENTATION-STANDARDS

**Date**: 2026-07-06
**Purpose**: Establish consistent documentation standards for clarity, maintainability, and professionalism across all Omega Engine documentation.

## 🎯 Scope & File Categories

This style guide applies to all Markdown (`.md`) documentation files in the Omega Engine repository. However, **not all files require the same header format.** Files are classified into categories:

### Category 1: Reference Docs (Omega Header Required)
Operational, living documentation that defines standards and architecture.
- System documentation (`OMEGA_ENGINE.md`, `SOVEREIGN_MANDATES.md`, etc.)
- Strategy documents (`docs/strategy/*.md` — active only, not archive)
- Standards (`docs/standards/*.md`)
- User guides and tutorials (`docs/user/*.md`)
- Reference materials (`docs/reference/*.md`)
- Architecture docs (`docs/architecture/*.md`)
- Knowledge base (`docs/knowledge/*.md`)
- Tutorials (`docs/tutorials/*.md`)

### Category 2: Agent Files (YAML Frontmatter + Omega Header)
Agent definitions use OpenCode YAML frontmatter for tooling, plus Omega header for provenance.
- Agent definitions (`.opencode/agents/*.md`)

### Category 3: Skill Files (YAML Frontmatter Only)
Skills are OpenCode system configurations. Omega headers are noise here.
- Skill definitions (`.opencode/skills/*/SKILL.md`)

### Category 4: R-Docs (R-Doc Format)
Research artifacts use their own established format (`# R-XX` headers). Omega headers are not used.
- Research docs (`docs/research/R*.md`)

### Category 6: Knowledge Base (LLM-Friendly Required)
Living best-practice guides that evolve with the system.
- Location: `docs/knowledge/` (primary) or `docs/research/KB_*`
- Format: Full LLM-Friendly (Frontmatter + Answer-First + Self-Contained Code + Structured Data + Dependency Graphs + llms.txt)
- Versioning: Semantic (MAJOR.MINOR.PATCH) with Change Log
- Maintenance: Quarterly review + incident-driven updates
- Ownership: Assigned entity per guide
- Examples: Research best practices, architecture patterns, operational runbooks

### Category 7: Working Docs (EXEMPT)
Ephemeral session artifacts consumed by path, not by header. No Omega header required.
- Team handoffs (`docs/team/*.md`)
- Intake notes (`docs/intake/*.md`)
- Coordination files (`data/coordination/*.md`)

### Category 8: Archives (EXEMPT)
Frozen documents. Never modify archived files.
- Archive directories (`docs/archive/`, `docs/strategy/archive/`)

### Category 9: Root Docs (Already Standardized)
Root-level engine documents. Already have Omega headers.
- `OMEGA_ENGINE.md`, `SOVEREIGN_MANDATES.md`, `ORACLE_STACK.md`, `CREDITS.md`, `AGENTS.md`

### Category 10: Sprint Plans (LLM-Friendly Format)
Sprint plans and ticket pages use the LLM-native format for agent consumption.
- Sprint plan index (`docs/sprints/*/index.md`)
- P0/P1 ticket pages (`docs/sprints/*/02-p0-tickets/*.md`, `docs/sprints/*/03-p1-tickets/*.md`)
- Research indexes (`docs/sprints/*/08-research-index.md`)
- **Required**: `LLM_FRIENDLY_DOCS_BP.md` compliance + YAML frontmatter with `llm_metadata`
- **Validation**: `make doc-llm-validate` must pass
- **Output**: `llms.txt` + `llms-full.txt` generated via `make sprint-plan-llm`

## 📄 File Structure & Headers

### Required File Header
Reference docs (Category 1) and Agent files (Category 2) MUST begin with this exact format:

```markdown
# 🔱 [Document Title]
**AP Token**: `AP-[UNIQUE-IDENTIFIER]-v[VERSION]`
⬡ OMEGA ⬡ [ENTITY] ⬡ [MODEL] ⬡ opencode ⬡ trc_[purpose] ⬡ [STATUS]

**Date**: YYYY-MM-DD
**Purpose**: [One-sentence purpose statement]
**Tags**: [tag1, tag2, tag3]
**Cross-references**: [file1.md, file2.md]
```

### Header Field Definitions
- **Document Title**: Clear, descriptive title using Title Case
- **AP Token**: Unique identifier following format `AP-[PROJECT]-v[MAJOR].[MINOR].[PATCH]`
- **ENTITY**: Primary persona/entity associated with document (e.g., LILITH, NEMOTRON-3-ULTRA, KALI)
- **MODEL**: AI model used for creation (e.g., gemma-4-31b-it, nemotron-3-ultra)
- **trc_[purpose]**: Traceability code indicating document purpose:
  - `trc_doc_inventory` - Documentation audits and tracking
  - `trc_doc_style` - Style guides and standards
  - `trc_doc_user` - User guides and tutorials
  - `trc_doc_ref` - Reference materials and specifications
  - `trc_doc_deep` - Deep dives and architectural explanations
  - `trc_doc_strat` - Strategic plans and roadmaps
  - `trc_doc_proc` - Procedures and operational guides
  - `trc_doc_agent` - Agent definitions and capabilities
  - `trc_doc_skill` - Skill descriptions and usage
- **STATUS**: Current document state (DRAFT, REVIEW, STANDARD, DEPRECATED)
- **Date**: ISO 8601 format (YYYY-MM-DD)
- **Purpose**: Single sentence describing the document's intent and audience
- **Tags**: Comma-separated keywords for discoverability (e.g., `oracle, routing, provider-fabric`)
- **Cross-references**: Comma-separated list of related files (e.g., `ORACLE_STACK.md, MEMORY_STORE.md`)

### Example Header
```markdown
# 🔱 Omega Engine — Sovereign Master Researcher
**AP Token**: `AP-RESEARCHER-GUIDE-v2.1.0`
⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ opencode ⬡ trc_doc_user ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Comprehensive guide to using the Sovereign Master Researcher agent for deep research and knowledge curation.
```

## 📝 Writing Standards

### Language & Tone
- **Clear and Concise**: Use plain language; avoid jargon unless defined
- **Active Voice**: Prefer "The system does X" over "X is done by the system"
- **Inclusive Language**: Use gender-neutral terms; avoid assumptions about user identity
- **Professional Yet Approachable**: Maintain technical accuracy while remaining accessible
- **Consistent Terminology**: Use defined terms consistently throughout

### Sentence Structure
- **Maximum Length**: Aim for <25 words per sentence; maximum 40 words
- **One Idea Per Sentence**: Avoid compound sentences that conflate multiple concepts
- **Clear Subjects**: Begin sentences with clear subjects when possible
- **Avoid Ambiguity**: Replace pronouns with specific nouns when clarity is needed

### Paragraph Structure
- **Topic Sentence First**: Begin paragraphs with the main idea
- **3-5 Sentences Ideal**: Keep paragraphs focused and scannable
- **Blank Line Separation**: Use blank lines to separate paragraphs
- **Single Idea Per Paragraph**: Each paragraph should address one concept

## 🏗️ Structural Elements

### Section Hierarchy
Use markdown heading levels consistently:
- `#` - Document title (only once, at the top)
- `##` - Major sections
- `###` - Subsections
- `####` - Sub-subsections
- Avoid going deeper than `####` unless absolutely necessary

### Section Naming
- Use Title Case for section headings
- Be descriptive and specific
- Avoid vague titles like "Overview" or "Details" without context
- Use parallel structure for related sections (e.g., "Input Parameters", "Output Parameters", "Return Values")

### Lists
- **Ordered Lists**: Use for sequential steps or ranked items
- **Unordered Lists**: Use for non-sequential collections of items
- **Parallel Structure**: Keep list items grammatically consistent
- **Punctuation**: 
  - Complete sentences: End with period
  - Fragments: No punctuation needed
  - Consistency within each list is key

### Code Blocks
- **Language Specifiers**: Always specify language (```python, ```bash, ```json, etc.)
- **Syntax Highlighting**: Enable when supported by the renderer
- **Line Numbers**: Generally avoid unless referencing specific lines
- **Long Lines**: Break long lines for readability (aim for <100 characters)
- **Placeholder Values**: Use clear placeholders like `your_api_key_here`, `PATH/TO/FILE`

### Tables
- **Header Row**: Always include a header row
- **Alignment**: Use colons in separator row for alignment (`:---` for left, `---:` for right, `:---:` for center)
- **Vertical Bars**: Ensure proper spacing around `|` for readability
- **Multi-line Cells**: Avoid when possible; use lists within cells if necessary
- **Width**: Allow natural width; don't force specific column widths unless critical

### Blockquotes & Admonitions
- **Blockquotes**: Use `>` for quotes, citations, or callouts
- **Admonitions**: When needed, use clear labels:
  - `> **NOTE**: Important information`
  - `> **WARNING**: Critical caution`
  - `> **TIP**: Helpful suggestion or optimization`
  - `> **EXAMPLE**: Illustrative use case`

## 🔤 Language & Mechanics

### Spelling & Grammar
- **Dictionary**: Use American English spelling (color, not colour; program, not programme)
- **Technical Terms**: Maintain consistent capitalization (e.g., "API", "JSON", "HTTP")
- **Acronyms**: Define on first use (e.g., "Application Programming Interface (API)")
- **Numbers**: 
  - Spell out zero through nine
  - Use numerals for 10 and above
  - Always use numerals for percentages, versions, and measurements
  - Use commas in large numbers (1,000; 10,000; 1,000,000)

### Punctuation
- **Serial Comma**: Use the Oxford comma (e.g., "apples, bananas, and oranges")
- **Quotation Marks**: Use double quotes for speech and quotations; single for quotes within quotes
- **Dashes**: 
  - Hyphen (`-`): Compound words (well-known, state-of-the-art)
  - En dash (`–`): Ranges (pages 5–10, January–March)
  - Em dash (`—`): Parenthetical statements—like this one
- **Spaces**: Single space between words and after punctuation

### Dates & Times
- **ISO 8601**: Use YYYY-MM-DD for dates (2026-07-06)
- **Timestamps**: Use ISO 8601 with timezone when precision needed (2026-07-06T14:30:00Z)
- **Time Ranges**: Use en dash (2026-07-01–2026-07-31)
- **Relative Dates**: Avoid ("last week", "soon"); use specific dates when possible

### Version Numbers
- **Semantic Versioning**: Use MAJOR.MINOR.PATCH format (1.0.0, 2.1.3)
- **Leading Zeros**: Avoid (use 1.0, not 01.00)
- **Comparisons**: Use "greater than", "less than", or symbols (>, <, ≥, ≤)
- **Version Ranges**: Use standard notation (>=1.0.0 <2.0.0)

## 🏷️ Tagging & Metadata

### Heritage Tags
When referencing id Software patterns, include appropriate heritage tags:
- Format: `[id-soft: game-year] Pattern Name — brief explanation`
- Examples:
  - `[id-soft: doom-1993] WAD System — Engine-content separation philosophy`
  - `[id-soft: quake-1996] Lazy Deletion — Efficient resource management`
  - `[id-soft: quake3-1999] Hard-Boundary Struct — Memory safety pattern`

### Cross-References
- **Internal Links**: Use relative paths (`[Related Guide](./user-guide.md)`)
- **External Links**: Use full URLs with descriptive text (`[Omega Engine Website](https://omega.example.com)`)
- **Section Links**: Use anchor links (`[See Architecture](#system-architecture)`)
- **Avoid**: Bare URLs without context

### File References
- **Code Files**: Use backticks with relative path (`src/omega/oracle/oracle.py`)
- **Configuration Files**: Use backticks with relative path (`config/providers.yaml`)
- **Commands**: Use backticks with full command (`omega talk "hello"`)
- **Environment Variables**: Use backticks with dollar notation (`$OMEGA_DATA_DIR`)

## 📐 Formatting & Layout

### Line Length
- **Target**: 80-100 characters per line
- **Maximum**: 120 characters (for readability in standard editors)
- **Exceptions**: Code blocks, URLs, tables, and YAML frontmatter may exceed this limit
- **Enforcement**: This is a **guideline**, not a CI gate. Long lines are flagged as informational warnings, not errors. Do not break lines solely to meet the limit if it reduces readability.

### Whitespace
- **Paragraph Separation**: One blank line between paragraphs
- **Section Separation**: Two blank lines before new `##` section
- **List Items**: Single spacing within lists; blank line between list and following paragraph
- **Code Blocks**: Blank line before and after
- **Tables**: Blank line before and after
- **Images**: Blank line before and after

### Indentation
- **Spaces Only**: Never use tabs; use spaces for indentation
- **Consistent Indentation**: Use 2 or 4 spaces consistently within a file
- **List Indentation**: Indent list contents by 2 spaces from marker
- **Code Block Indentation**: Align with surrounding text or use 0 indentation

### Emphasis
- **Bold**: `**bold text**` for key terms, important concepts, and UI elements
- *Italics*: `*italic text*` for emphasis, book titles, and foreign words
- **Code**: `` `code` `` for file names, commands, variables, and technical terms
- ~~Strikethrough~~: `~~strikethrough~~` for deprecated information (rarely used)
- **Avoid**: Overuse of emphasis; reserve for truly important elements

## 🖼️ Media & Assets

### Images
- **Format**: Prefer SVG for diagrams, PNG for screenshots, JPEG for photographs
- **Alt Text**: Always provide descriptive alt text for accessibility
- **Dimensions**: Specify width/height when necessary for layout
- **Attribution**: Credit sources when using third-party images
- **Location**: Store in `docs/assets/` with appropriate subdirectories

### Diagrams
- **Preferred**: Mermaid syntax for flowcharts, sequence diagrams, and state diagrams
- **Alternative**: PlantUML for complex UML diagrams
- **Fallback**: Exported PNG/SVG from drawing tools with source files retained
- **Labeling**: Use clear, legible labels; ensure text is readable at 100% zoom

### Embedded Content
- **Avoid**: Embedding videos or interactive content that requires external dependencies
- **Prefer**: Links to external resources with clear descriptions
- **Exception**: Simple animated GIFs for demonstrating short processes (under 5 seconds, under 1MB)

## 🔄 Version Control & Maintenance

### File Naming
- ** kebab-case**: Use lowercase with hyphens (documentation-style-guide.md)
- **Descriptive**: Names should clearly indicate content
- **Versioning**: Avoid putting version numbers in filenames; use AP Token instead
- **Special Characters**: Avoid spaces, underscores, and special characters
- **Extensions**: Always use `.md` for Markdown files

### Duplicate Content
- **Avoid**: Copying large sections between documents
- **Prefer**: Single source of truth with references/linking
- **Exception**: Small, reusable snippets (definitions, warnings, etc.)
- **Synopsis**: When duplication is unavoidable, maintain a master version and reference it

### Deprecation
- **Mark Clearly**: Use `DEPRECATED` in STATUS field and add warning banner
- **Migration Path**: Always provide guidance on alternatives
- **Timeline**: Specify when deprecated content will be removed
- **Backlinks**: Update all references to point to new location

## 📋 Validation Checklist

Before submitting documentation changes, verify:

### [ ] File Category
- [ ] Correct category identified (Reference, Agent, Skill, R-Doc, Working, Knowledge Base, Archive, Root, Sprint Plan)
- [ ] Header format matches category requirements
- [ ] Working docs and archives marked as EXEMPT from Omega headers
- [ ] Knowledge Base docs (Category 6) have full LLM-Friendly format
- [ ] Sprint Plan docs (Category 9) have LLM-Friendly format + llms.txt generation

### [ ] Header Compliance (Categories 1-2 only)
- [ ] Correct AP Token format
- [ ] Valid ENTITY, MODEL, trc_*, and STATUS values
- [ ] Current date in YYYY-MM-DD format
- [ ] Clear, single-sentence purpose statement
- [ ] Tags and Cross-references populated

### [ ] Language Quality
- [ ] No spelling or grammar errors (run spell checker)
- [ ] Consistent terminology throughout
- [ ] Active voice preferred over passive
- [ ] Inclusive and professional tone
- [ ] Appropriate technical level for target audience

### [ ] Structural Integrity
- [ ] Proper heading hierarchy (no skipping levels)
- [ ] Descriptive, Title Case section headings
- [ ] Logical flow and organization
- [ ] Appropriate use of lists, tables, and code blocks
- [ ] Adequate white space and visual hierarchy

### [ ] Technical Accuracy
- [ ] All technical claims verified against current codebase
- [ ] Code examples tested and functional
- [ ] Configuration examples match actual file formats
- [ ] Command examples work as documented
- [ ] Version numbers current and accurate

### [ ] Formatting Consistency
- [ ] Header follows exact specification
- [ ] Consistent spacing and indentation
- [ ] Proper use of emphasis (bold, italics, code)
- [ ] Correct table and list formatting
- [ ] Appropriate use of blockquotes and admonitions

### [ ] References & Links
- [ ] All internal links resolve correctly
- [ ] External links are accessible and relevant
- [ ] Anchor links point to existing headers
- [ ] No broken or dead links
- [ ] Citations and references properly formatted

### [ ] Legal & Compliance
- [ ] No copyrighted material without permission
- [ ] Proper attribution for third-party content
- [ ] Heritage tags included where appropriate
- [ ] No proprietary information disclosed
- [ ] Compliance with licensing requirements

## 📚 Examples

### Well-Formed Header
```markdown
# 🔱 Omega Engine — Provider Fabric Deep Dive
**AP Token**: `AP-PROVIDER-FABRIC-v3.2.1`
⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Comprehensive examination of the model gateway provider fabric, including local-first priority, fallback chains, and synthesis architecture.
**Tags**: provider-fabric, model-gateway, local-first, circuit-breaker
**Cross-references**: ORACLE_STACK.md, config/providers.yaml, src/omega/oracle/model_gateway.py
```

### Proper Section Structure
```markdown
## 🛠️ Configuration

### Environment Variables

The following environment variables configure the provider fabric:

| Variable | Description | Default |
|----------|-------------|---------|
| `OMEGA_MODELS_CONFIG` | Path to models.yaml | `config/models.yaml` |
| `VAULT_MASTER_KEY` | Encryption key for secrets | *(required)* |
| `SEARXNG_BASE_URL` | Base URL for SearXNG instance | `http://localhost:8080` |

#### Primary Sources (Tier 0-2)
These providers are queried first in the synthesis flywheel:

```yaml
providers:
  - name: native-gguf
    type: local
    priority: 0
    # ... additional configuration
```

> **NOTE**: Local providers are always attempted before cloud providers per Mandate 7 (Local-First).
```

### Code Examples
```python
# Initialize the provider factory
def initialize_providers(config_path: str) -> List[BaseProvider]:
    """Create and configure all providers based on configuration.
    
    Args:
        config_path: Path to the models.yaml configuration file
        
    Returns:
        List of initialized provider instances
    """
    config = load_config(config_path)
    providers = []
    
    for provider_config in config["providers"]:
        provider = create_provider(provider_config)
        providers.append(provider)
    
    return providers
```
 
## ✅ Validation Checklist
 
Before submitting any documentation PR, verify:
 
### All Categories
- [ ] File has correct header format for its category
- [ ] AP Token follows format `AP-[PROJECT]-v[MAJOR].[MINOR].[PATCH]`
- [ ] Date is ISO 8601 (YYYY-MM-DD)
- [ ] Purpose is one clear sentence
- [ ] Tags are lowercase, comma-separated
- [ ] Cross-references use relative paths from repo root
- [ ] No broken internal links
- [ ] Code blocks have language tags
- [ ] Tables have header rows
 
### Category 1 (Reference Docs) + Category 8 (Sprint Plans)
- [ ] **LLM-Friendly Standards** (`LLM_FRIENDLY_DOCS_BP.md`):
  - [ ] YAML frontmatter with `schema_version: "1.0"` and `llm_metadata`
  - [ ] Answer-first sections (`## What` / `## Why` / `## Acceptance Criteria`)
  - [ ] Self-contained code blocks (imports, types, file path comments)
  - [ ] Structured YAML for dependencies, research, acceptance criteria
  - [ ] Token budget within limits (run `make doc-token-check`)
  - [ ] `make doc-llm-validate` passes
- [ ] Sprint Plans (Category 8 only):
  - [ ] Modular structure: `index.md` + `02-p0-tickets/` + `08-research-index.md`
  - [ ] `llms.txt` + `llms-full.txt` generated via `make sprint-plan-llm`
 
### Category 2 (Agent Files)
- [ ] OpenCode YAML frontmatter present
- [ ] Omega header present (below YAML)
- [ ] Agent capabilities match fleet needs
 
## 🔄 Maintenance & Updates

### Review Schedule
- **Quarterly**: Comprehensive review of all documentation
- **Monthly**: Review of high-traffic/user-facing documentation
- **Per Release**: Update documentation accompanying code changes
- **As Needed**: Update when inaccuracies are identified

### Update Process
1. **Identify Need**: Through user feedback, code changes, or scheduled review
2. **Create Branch**: `docs/[description]-YYYYMMDD` from main branch
3. **Make Changes**: Following this style guide
4. **Validate**: Run documentation validation script
5. **Pull Request**: Submit for review with clear description of changes
6. **Review**: Address feedback from maintainers
7. **Merge**: After approval, merge to main branch
8. **Notify**: Announce significant updates via appropriate channels

### Versioning
- **Minor Changes**: Increment PATCH version (v1.0.0 → v1.0.1)
- **Feature Changes**: Increment MINOR version (v1.0.0 → v1.1.0)
- **Breaking Changes**: Increment MAJOR version (v1.0.0 → v2.0.0)
- **Documentation-Only**: Typically PATCH unless introducing new structure

## 📜 Changelog

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-07-06 | v1.0.0 | Initial documentation style guide release | NEMOTRON-3-SUPER |

---
*Last Updated: 2026-07-06 | Author: Nemotron-3-ULTRA | Version: v1.0.0*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
