# Web Research: Knowledge Gaps & Blockers for Omega Engine PR
**Date**: 2026-10-02
**Author**: Jem (Sovereign Synthesizer)
**Status**: RESEARCH ONLY — no changes implemented

---

## 1. MCP Tool Documentation Standards

### Industry Best Practices
| Source | Key Findings |
|--------|--------------|
| **Anthropic MCP Spec** (modelcontextprotocol.io) | Tools must expose: name, description, inputSchema (JSON Schema), outputSchema (optional), annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint). Each tool uniquely identified by name. |
| **FastMCP** (github.com/jlowin/fastmcp) | Auto-generates tool docs from Python type hints + docstrings. Uses Pydantic models for input/output schemas. Provides `@tool` decorator that extracts schema automatically. |
| **LangChain MCP Adapter** | Wraps MCP tools as LangChain tools. Documents: transport (stdio/HTTP/SSE), authentication, tool filtering (allowedTools/disabledTools), structured content support. |
| **LlamaIndex MCP** | Exposes LlamaIndex workflows/tools as MCP servers. Documents: server configuration, tool discovery, sampling support. |

### Recommendations for Omega
1. **Adopt JSON Schema for all MCP tool inputs/outputs** — align with MCP spec §Tools
2. **Add tool annotations** — readOnlyHint, destructiveHint, idempotentHint, openWorldHint per tool
3. **Generate docs from code** — use FastMCP-style decorators or Pydantic models to auto-extract schemas
4. **Document each tool with**: description, input schema, output schema, error codes, examples, annotations
5. **Location**: `docs/reference/api/mcp-tools/` (new directory)

### Key Links
- MCP Spec Tools: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- FastMCP: https://github.com/jlowin/fastmcp
- LangChain MCP: https://docs.langchain.com/oss/python/langchain/mcp

---

## 2. Diátaxis Implementation

### How Top Projects Implement Diátaxis
| Project | Structure | Cross-References |
|---------|-----------|------------------|
| **Cloudflare** (developers.cloudflare.com) | Four top-level dirs: `tutorials/`, `how-to/`, `reference/`, `explanation/` | Uses "compass" pattern — each page links to related content in other quadrants |
| **Gatsby** (gatsbyjs.com/docs) | Diátaxis-aligned restructure (2023). Quadrants as top-level nav. | Sidebar shows related tutorials/how-to/reference/explanation per page |
| **Prefect** (docs.prefect.io) | `tutorials/`, `guides/` (how-to), `concepts/` (explanation), `api-ref/` (reference) | Explicit "See also" sections linking across quadrants |
| **Diátaxis Reference Repo** (github.com/LifeChef/Diataxis_Reference) | `Blog_Engine_Example/` with all four quadrants working together | Demonstrates production-ready cross-quadrant linking |

### Folder Structure Pattern
```
docs/
├── tutorials/          # Learning-oriented (study)
├── how-to/             # Task-oriented (work)
├── reference/          # Information-oriented (lookup)
│   ├── api/            # Auto-generated API docs
│   └── cli/            # CLI reference
├── explanation/        # Understanding-oriented (context)
└── index.md            # Quadrant map + compass
```

### Recommendations for Omega
1. **Formalize existing dirs** as canonical Diátaxis quadrants (already partially done)
2. **Populate `docs/tutorials/`** — currently only 1 file (critical gap)
3. **Add `docs/index.md`** with quadrant map and compass navigation
4. **Implement cross-references** — "See also" sections linking related content across quadrants
5. **Move scattered docs** from `docs/research/`, `docs/guides/` into correct quadrants

### Key Links
- Diátaxis Official: https://diataxis.fr/
- Applying Diátaxis: https://diataxis.fr/application
- Cloudflare testimonial: https://github.com/evildmp/diataxis-documentation-framework/blob/main/index.rst

---

## 3. API Reference Generation

### Tools Comparison
| Tool | Language | Approach | Used By |
|------|----------|----------|---------|
| **Sphinx + autodoc/apidoc** | Python, C++ | Import-time introspection, RST/Markdown | Python, Django, Flask, Requests, Linux Kernel, Podman |
| **pdoc** | Python | Zero-config, AST-based, live-reload server | Google, Microsoft, Meta, Mozilla, mitmproxy |
| **mkdocstrings** | Python | MkDocs plugin, uses Sphinx/pdoc backends | MkDocs projects |
| **TypeDoc** | TypeScript | AST-based, JSDoc/TSDoc comments | TypeScript projects |
| **rustdoc** | Rust | Compiler-integrated, markdown in doc comments | All Rust crates (docs.rs) |
| **Sphinx-AutoAPI** | Python, Go, .NET, JS | Static analysis (no import), multi-language | Multi-language projects |

### Recommendations for Omega
1. **Use pdoc for Python API docs** — zero-config, supports Google/numpydoc docstrings, type annotations, cross-linking, live preview. Used by Google, Microsoft, Meta.
2. **Generate to `docs/reference/api/`** — already has 20 files, fits existing structure
3. **Integrate with pre-commit/CI** — run pdoc on `src/omega/` changes, fail if new public APIs undocumented
4. **For MCP tools** — use FastMCP-style schema extraction (Pydantic models → JSON Schema)

### Key Links
- pdoc: https://pdoc.dev/ (used by Google, Microsoft, Meta, Mozilla)
- Sphinx apidoc: https://www.sphinx-doc.org/en/master/usage/extensions/apidoc.html
- mkdocstrings: https://mkdocstrings.github.io/

---

## 4. Architecture Decision Records (ADRs)

### Standard Format (Michael Nygard Template)
```markdown
# ADR-XXX: Title

## Status
Proposed | Accepted | Rejected | Deprecated | Superseded

## Context
What is the issue motivating this decision?

## Decision
What is the change we're proposing/doing?

## Consequences
What becomes easier or more difficult?
```

### How Major Projects Structure ADRs
| Project | Location | Naming | Index |
|---------|----------|--------|-------|
| **Kubernetes** | `docs/adr/` | `ADR-XXXX-short-title.md` | `README.md` with table |
| **etcd** | `Documentation/adr/` | `ADR-XXX-title.md` | Auto-generated index |
| **CockroachDB** | `docs/architecture/decisions/` | `YYYY-MM-DD-title.md` | Chronological list |
| **MADR** (Markdown ADR) | `docs/adr/` | `ADR-XXXX-title.md` | `adr-log.md` |

### Recommendations for Omega
1. **Adopt Nygard template** — Title, Status, Context, Decision, Consequences
2. **Location**: `docs/adr/` (exists with 3 files — expand)
3. **Naming**: `ADR-XXXX-short-kebab-title.md` (zero-padded 4 digits)
4. **Index file**: `docs/adr/README.md` with table of all ADRs
5. **Status values**: proposed, accepted, rejected, deprecated, superseded
6. **Link from PRs/Issues** — traceability per GDS Way guidance

### Key Links
- Nygard Template: https://github.com/architecture-decision-record/architecture-decision-record/blob/main/locales/en/templates/decision-record-template-by-michael-nygard/index.md
- MADR: https://adr.github.io/madr/
- GDS Way: https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html

---

## 5. Documentation CI/CD Validation

### Standard Checks in CI
| Check | Tool | Purpose |
|-------|------|---------|
| **Link checking** | `markdown-link-check`, `@rogerchappel/linkcheck`, `mkdocs-link-check` | Catch broken internal/external links, validate anchors |
| **Prose linting** | **Vale** (primary), markdownlint | Style guide enforcement (Google, Microsoft), banned phrases, terminology |
| **Spell checking** | Vale (Hunspell dicts), cspell | Catch typos in docs and code comments |
| **Example testing** | doctest (Python), cargo test --doc (Rust) | Verify code examples in docs actually run |
| **Freshness checks** | Custom scripts | Detect docs not updated when code changes (last-reviewed dates, code-to-doc mapping) |

### Best Practices from Industry
- **Run external link checks on schedule** (not per-PR) — external sites break on their own clock
- **Exclude internal-only hosts** CI cannot reach
- **Vale for prose** — markup-aware, parses Markdown/AsciiDoc/RST/HTML, skips code blocks, supports custom rules
- **GitLab uses Vale in CI** — error-level rules fail pipeline, warnings/suggestions in MR diff
- **Mintlify runs Vale + broken-link checks in CI** automatically

### Recommendations for Omega
1. **Add Vale to CI** — with Google/Microsoft style guide packages + custom Omega rules
2. **Add link checker** — `@rogerchappel/linkcheck` (local-first, JSON output for CI)
3. **Add doctest for Python examples** — verify `docs/reference/api/` code snippets
4. **Add freshness check** — script comparing `src/omega/` mtime vs `docs/` mtime
5. **Run external links weekly** (scheduled workflow), internal links per-PR

### Key Links
- Vale: https://github.com/vale-cli/vale (used by GitLab, Mintlify, Microsoft)
- Linkcheck: https://github.com/rogerchappel/linkcheck
- Datadef guide: https://datadef.io/guides/en/docs-checks-in-ci (2026)

---

## 6. Documentation Versioning

### Strategies Comparison
| Strategy | Tool | How It Works | Best For |
|----------|------|--------------|----------|
| **Versioned directories** | Docusaurus | `versioned_docs/version-X.Y.Z/`, `versions.json`, `versioned_sidebars/` | High-traffic, rapid changes between versions |
| **Git branches** | Sphinx/mkdocs | Each version = branch, deploy per branch | Simple projects, few versions |
| **Branch + symlinks** | Read the Docs | `latest` → `main`, `stable` → latest tag | Open source projects on RTD |
| **mdBook** | Rust | Separate book per version, or `mdbook-epub` | Rust projects (docs.rs handles versioning) |

### Docusaurus Versioning (Reference Implementation)
```
website/
├── docs/                    # Current version (next)
├── versioned_docs/
│   ├── version-1.0.0/
│   └── version-2.0.0/
├── versioned_sidebars/
│   ├── version-1.0.0-sidebars.json
│   └── version-2.0.0-sidebars.json
└── versions.json            # ["2.0.0", "1.0.0"]
```
- CLI: `npm run docusaurus docs:version 1.1.0`
- Keeps < 10 versions (Jest maintains only latest few)
- Fallback: missing doc in v2 falls back to v1

### Recommendations for Omega
1. **Use Docusaurus-style versioned directories** — aligns with Diátaxis structure, supports fallback
2. **Version on release** — tag `vX.Y.Z` triggers `docs:version X.Y.Z`
3. **Keep ≤ 10 versions** — archive older to `docs/archive/versions/`
4. **Deploy all versions** — `docs.omega-engine.dev/v1.0.0/`, `docs.omega-engine.dev/latest/`
5. **Start simple** — no versioning until post-debut (per Docusaurus warning: "most of the time you don't need versioning")

### Key Links
- Docusaurus Versioning: https://docusaurus.io/docs/versioning
- Docusaurus v3.10: https://github.com/facebook/docusaurus/blob/main/website/versioned_docs/version-3.3.2/guides/docs/versioning.mdx

---

## 7. Documentation Accessibility (WCAG)

### WCAG 2.1 AA Requirements for Docs
| Requirement | Implementation |
|-------------|----------------|
| **Heading hierarchy** | Real `<h1>`-`<h6>`, no skipped levels, one `<h1>` per page |
| **Alt text** | Informative images: descriptive alt; decorative: `alt=""` or CSS background; complex: alt + extended description |
| **Semantic HTML** | `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, lists (`<ul>`/`<ol>`), tables with `<th scope="col|row">` |
| **Link text** | Descriptive (not "click here"), indicate external/file links |
| **Color contrast** | 4.5:1 normal text, 3:1 large text |
| **Keyboard navigation** | Focus visible, logical tab order, skip links |
| **Language declaration** | `<html lang="en">`, `<html lang="fr">` for translations |

### Tools for Validation
- **axe-core** / **Lighthouse** — automated testing in CI
- **Vale rules** — can enforce heading hierarchy, alt text presence
- **markdownlint** — MD013 (line length), MD025 (single h1), MD026 (heading style)

### Recommendations for Omega
1. **Enforce single H1 per page** — Vale rule + markdownlint MD025
2. **Require alt text for all images** — Vale rule for Markdown images
3. **Validate heading hierarchy** — no skipped levels (H1→H3), Vale custom rule
4. **Semantic HTML in generated output** — ensure Docusaurus/MkDocs theme outputs proper landmarks
5. **Add accessibility CI check** — axe-core in Playwright/Cypress

### Key Links
- WCAG 2.1: https://www.w3.org/TR/2017/WD-WCAG21-20171207/
- WAI Headings: https://www.w3.org/WAI/tutorials/page-structure/headings
- Deque Checklist: https://media.dequeuniversity.com/public/en/docs/deque_web_accessibility_checklist.pdf

---

## 8. Documentation Search

### Search Solutions Comparison
| Solution | Type | Cost | Best For |
|----------|------|------|----------|
| **Algolia DocSearch** | Hosted SaaS | Free for dev docs | Docusaurus, VuePress, VitePress — official support |
| **Typesense DocSearch** | Self-hosted/Cloud | Open source | Docusaurus community plugin, full control |
| **Local Search** | Client-side (Lunr.js, MiniSearch) | Free, no external deps | Small docs, offline, privacy-first |
| **Custom SearchBar** | Any | Flexible | Specialized needs |

### Implementation Patterns
- **Algolia DocSearch**: Apply → get credentials → add `@docusaurus/theme-search-algolia` → weekly crawl
- **Typesense**: Run `typesense-docsearch-scraper` → add `docusaurus-theme-search-typesense`
- **Local Search**: Build index at build time (Lunr.js, MiniSearch, FlexSearch) → client-side search

### Recommendations for Omega
1. **Start with Local Search** (MiniSearch or FlexSearch) — no external deps, works offline, privacy-first, fast
2. **Upgrade to Algolia DocSearch** post-debut — free for dev docs, better relevance, handles versioning/language
3. **Configure per-version/per-language indices** — avoid v1 results in v2, English results in French
4. **Search analytics** — track queries with no results to identify content gaps

### Key Links
- Docusaurus Search: https://docusaurus.io/docs/search
- Algolia DocSearch: https://github.com/algolia/docsearch
- Typesense DocSearch: https://typesense.org/docs/

---

## 9. Documentation Feedback Loops

### Feedback Mechanisms Used by Major Projects
| Mechanism | Projects | Implementation |
|-----------|----------|----------------|
| **GitHub Issues** | Microsoft, GitHub, LSST (Rubin) | "Edit this page" → PR, or "Open issue" with pre-filled template |
| **Thumbs up/down** | GitHub Docs, Mintlify, LSST | Simple widget at page bottom, submits to backend |
| **Detailed feedback forms** | Google, MDN, Sentry | Progressive disclosure: thumbs down → form with categories |
| **GitHub Discussions** | FumaDocs, many OSS | Dedicated "Docs Feedback" category |
| **Analytics** | Mintlify, Docusaurus (GA/Plausible) | Page views, scroll depth, search queries, feedback sentiment |

### LSST/Rubin Feedback Architecture (Technote SQR-090)
- **UI**: Thumbs up/down → progressive detailed form (GitHub/Google/MDN style)
- **API**: Receives submissions, stores in InfluxDB/Sasquatch
- **Integration**: Links to "Contribute on GitHub" — empowers users to fix docs
- **Deployment**: Shared across all Documenteer/Sphinx sites

### Recommendations for Omega
1. **Add "Edit this page" link** — every doc page links to GitHub edit URL (standard Docusaurus/MkDocs feature)
2. **Add thumbs up/down widget** — simple, low-friction, sends to GitHub Issues or local endpoint
3. **Create "Documentation Feedback" GitHub Issue template** — pre-filled with page URL, browser, context
4. **Add GitHub Discussions category** — "Documentation" for longer discussions
5. **Track search analytics** — queries with zero results = content gaps

### Key Links
- LSST Feedback System: https://sqr-090.lsst.io/
- Mintlify Feedback: https://mintlify.com/docs/optimize/feedback
- Microsoft Feedback: https://github.com/MicrosoftDocs/Contribute/blob/main/Contribute/content/provide-feedback.md

---

## 10. Documentation Localization (i18n)

### Tools & Workflows
| Tool | Type | Integration | Used By |
|------|------|-------------|---------|
| **Crowdin** | SaaS (free for OSS) | CLI upload/download, GitHub Actions, Docusaurus native | Docusaurus, VuePress, many OSS |
| **Weblate** | Self-hosted/Cloud | Git integration, continuous localization, Sphinx support | LibreOffice, Godot, many GNU projects |
| **Git-based** | Native | Translations as PRs, `i18n/[locale]/` dirs | Docusaurus v2+, MkDocs (manual) |

### Docusaurus i18n Workflow (Reference)
```javascript
// docusaurus.config.js
i18n: {
  defaultLocale: 'en',
  locales: ['en', 'fr', 'fa'],
  localeConfigs: {
    fa: { direction: 'rtl' }  // RTL support
  }
}
```
- Source files: `website/i18n/[locale]/docusaurus-plugin-content-docs/**/*.md`
- Crowdin config: `crowdin.yml` maps source → translation paths
- CLI: `crowdin upload sources` / `crowdin download`

### Recommendations for Omega
1. **Design for i18n from start** — use `<Translate>` components, ICU Message Format for plurals
2. **Use Crowdin** — free for OSS, Docusaurus native integration, CLI for CI automation
3. **Structure**: `docs/i18n/[locale]/` mirroring quadrant dirs
4. **Start with 1-2 languages** — Spanish, Chinese (high developer populations)
5. **Automate in CI** — upload sources on main branch, download translations on schedule

### Key Links
- Docusaurus i18n: https://docusaurus.io/docs/i18n/tutorial
- Docusaurus + Crowdin: https://www.docusaurus.io/docs/3.8.1/i18n/crowdin
- Weblate: https://weblate.org/ (continuous localization)

---

## Summary: Priority Recommendations for Omega

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| **P0** | Populate `docs/tutorials/` (Diátaxis) | Medium | Critical — learning path missing |
| **P0** | Add Vale + linkcheck to CI | Low | Prevents regression |
| **P0** | Adopt Nygard ADR template | Low | Architecture traceability |
| **P1** | Integrate pdoc for API docs | Medium | Auto-sync code↔docs |
| **P1** | Add MCP tool annotations + schema docs | Medium | MCP compliance |
| **P1** | Implement local search (MiniSearch) | Low | Discoverability |
| **P2** | Add feedback widget + GitHub Issue template | Low | User-driven improvement |
| **P2** | Design for i18n (Crowdin-ready) | Medium | Global reach |
| **P3** | Version docs on release (Docusaurus-style) | Medium | Release management |
| **P3** | Full WCAG 2.1 AA audit | Medium | Accessibility compliance |

---

*⬡ OMEGA ⬡ JEM ⬡ WEB_RESEARCH_KNOWLEDGE_GAPS_20261002 ⬡ 2026-10-02 ⬡*