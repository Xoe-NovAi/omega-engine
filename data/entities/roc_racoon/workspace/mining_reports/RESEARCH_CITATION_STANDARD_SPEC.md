<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Research Documentation Citation Standard — Design Specification
# ⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_citation_standard
**Date**: 2026-06-21
**Status**: DESIGN SPEC — Not Yet Implemented
**Designer**: Verity (Compliance & Gnosis Agent)

**Sprint**: Post-SearXNG (H2-L)
**Priority**: MEDIUM
**AP Token**: `AP-CITATION-STANDARD-v1.0.0`

---

## Table of Contents

1. [Purpose & Scope](#1-purpose--scope)
2. [Citation Format Schema](#2-citation-format-schema)
3. [Source Quality Scoring Rubric](#3-source-quality-scoring-rubric)
4. [Required Document Structure](#4-required-document-structure)
5. [Cross-Referencing Protocol](#5-cross-referencing-protocol)
6. [Tier Classification for Source Depth](#6-tier-classification-for-source-depth)
7. [Automation & CI Gate](#7-automation--ci-gate)
8. [Backfill Process](#8-backfill-process)
9. [Edge Cases & Exemptions](#9-edge-cases--exemptions)
10. [Roadmap Addition](#10-roadmap-addition)
11. [Appendix A — Template](#appendix-a--template)
12. [Appendix B — Lint Rules](#appendix-b--lint-rules)

---

## §1. Purpose & Scope

### 1.1 Why This Standard Exists

The Omega Engine produces research documents across multiple agent workspaces (`data/entities/*/workspace/mining_reports/`) and the central repository (`docs/research/`). These documents inform architectural decisions, mandate compliance rulings, and guide the Sovereign Evolution Roadmap. Without a consistent citation standard:

- **Claims cannot be verified**: A finding about "SearXNG health check timeouts" is useless if the reader cannot trace it to the source.
- **Source quality is invisible**: A Stack Overflow answer and an official GitHub commit receive equal weight today.
- **Cross-document trust erodes**: If Document B cites Document A's finding but Document A has no sources, Document B inherits zero provenance.
- **Audit trails break**: Mandate compliance audits (M9, M13, M17, M21) require traceability from claim to evidence.

### 1.2 Scope

| Area | In Scope | Out of Scope |
|------|----------|--------------|
| Mining reports | `data/entities/roc_racoon/workspace/mining_reports/*.md` | Temporary scratch files |
| Research docs | `docs/research/R*.md` | Session transcripts |
| Verification reports | `data/entities/*/workspace/*_VERIFICATION_*.md` | Handoff packets |
| Architecture specs | `docs/strategy/*.md`, `docs/architecture/*.md` | Configuration YAML files |
| Audit reports | Verity compliance reports | Inline code comments |

### 1.3 Gold Standard Reference

The document `SEARXNG_DEEP_RESEARCH_20260621.md` in the Roc Racoon mining reports directory sets the current gold standard with **54 sourced citations**. All new research documents should match or exceed this standard. The key features that make it gold-standard:

1. Every factual claim has an inline source anchor
2. Sources are grouped by tier (Official → Community → Verification)
3. Each source has a quality score and access date
4. Verification status is explicit per source
5. Cross-references to sibling documents are present

---

## §2. Citation Format Schema

### 2.1 Required Fields

Every citation in every research document MUST contain the following fields. They appear in a markdown bullet or table entry:

| Field | Type | Format | Example |
|-------|------|--------|---------|
| **URL** | `string` | Fully qualified URL or absolute file path | `https://github.com/searxng/searxng/blob/master/searx/settings.yml` |
| **Title** | `string` | Human-readable page/document title | "SearXNG settings.yml — Official Configuration Reference" |
| **Access Date** | `date` | `YYYY-MM-DD` | `2026-06-21` |
| **Source Quality Score** | `integer` | `1-10` per §3 rubric | `10` |
| **Topic Tags** | `string` | Comma-separated keywords | `searxng, configuration, health-check, podman` |
| **Verified** | `boolean` | `Yes` or `No` | `Yes` |

### 2.2 Optional Fields

| Field | Type | When to Use |
|-------|------|-------------|
| **Author/Creator** | `string` | When source has a named author or maintainer |
| **Publication Date** | `date` | When source has a known publication/first-commit date |
| **Verified By** | `string` | Entity name that performed the verification (e.g., `roc_racoon`) |
| **Notes** | `string` | Any caveat, methodology note, or context about the source |

### 2.3 Inline Citation Format

For inline citations within document body text, use the following anchor pattern:

```
[Source: TITLE | Score: N | Verified: Yes/No]
```

**Examples**:

```
The default timeout configuration in SearXNG is 30 seconds
[Source: searxng/settings.yml | Score: 10 | Verified: Yes].

This differs from the Podman health check default of 60s
[Source: Podman Healthcheck Docs | Score: 10 | Verified: Yes].
```

**For cross-document citations**:

```
[Source: SEARXNG_DEEP_RESEARCH_20260621.md §1.3 | Score: 9 | Verified: Yes]
```

### 2.4 Full Source List Entry Format

In the `## Sources` section, each entry uses this structure:

```markdown
1. **URL**: `https://github.com/searxng/searxng/blob/master/searx/settings.yml`
   **Title**: SearXNG settings.yml — Official Configuration Reference
   **Score**: 10 (Official Primary)
   **Accessed**: 2026-06-21
   **Tags**: searxng, configuration, health-check, podman
   **Verified**: Yes
   **Verifier**: roc_racoon
   **Notes**: Verified against live `podman exec` output — line 142 matches default 30s timeout.
```

**Compact format for high-density documents** (when space is constrained):

```markdown
1. [searxng/settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml)
   — Official config reference (Score: 10, 2026-06-21, Verified: Yes)
   Tags: searxng, configuration
```

---

## §3. Source Quality Scoring Rubric

### 3.1 The 10-Point Scale

| Score | Category | Definition | Example | Verification Required? |
|-------|----------|------------|---------|----------------------|
| 10 | **Official Primary** | Official code, docs, or spec from the project maintainers | `searxng/searxng` source code; official Podman documentation; Python language spec | No (trusted by definition) |
| 9 | **Verified Primary** | Primary source verified by an Omega agent through live execution | `podman exec` output; live API response captured and logged; `curl` response verified against docs | Yes (agent must document the verification procedure) |
| 8 | **Official Secondary** | Official blog, changelog, PR description, or release notes from maintainers | SearXNG release notes on GitHub; Podman changelog; npm package release page | No |
| 7 | **Expert Analysis** | Deep analysis by a recognized domain expert with verifiable credentials | DeepWiki analysis of SearXNG architecture; Carmack's .plan files; academic paper | Recommended |
| 6 | **Technical Blog** | Technical blog post by a domain practitioner | Medium blog on SearXNG deployment; Dev.to article on Podman networking; personal blog by maintainer | Recommended |
| 5 | **Community Docs** | Community-maintained documentation (not official) | Arch Wiki; NixOS options reference; Awesome list | Recommended |
| 4 | **Forum / Q&A** | Q&A with an accepted answer or upvoted solution | Stack Overflow accepted answer; GitHub Discussion with maintainer response; Reddit with official reply | Recommended |
| 3 | **General Blog** | General blog post or article without domain expertise signal | "How I set up my search engine" personal blog; Medium post by generalist | Yes |
| 2 | **Social Media** | Unstructured social media content | Tweets; Reddit comments; Hacker News comments; Discord messages | Yes |
| 1 | **Speculation** | Unverified claim, speculation, or "I think" statements | "I think SearXNG supports this"; forum post with no accepted answer; LLM output used as source | No (should not be cited without explicit caveat) |

### 3.2 Minimum Acceptable Score by Context

| Context | Minimum Score | Rationale |
|---------|--------------|-----------|
| Architectural decision documentation | 7 | Decisions must be grounded in high-quality evidence |
| Mandate compliance ruling | 8 | Compliance claims require official or verified sources |
| Bug report / security finding | 9 | Must be verified against live system |
| General research / background | 4 | Lower bar for exploratory research |
| Legacy pattern mining | 5 | Community docs may be the only surviving sources |
| Cross-reference to Omega document | 9 | Internal Omega documents are verified by definition |

### 3.3 Score Downgrade Rules

A source's score MUST be downgraded in these circumstances:

1. **Staleness**: If a source is >2 years old for a fast-moving project (JS ecosystem, AI tools), downgrade by 1-2 points.
2. **Contradiction**: If two sources of equal or higher score contradict the source, downgrade by 1 point.
3. **Incomplete verification**: If a source that "Recommended" or "Yes" in verification was not actually verified, mark as `Verified: No` and note why.
4. **Second-hand evidence**: If the source cites another source rather than providing primary evidence, treat as the cited source's category, not the current source's.

### 3.4 Score Display in Documents

When displaying in source lists, always include both the numeric score and the category name:

```
Score: 10 (Official Primary)
Score: 4 (Forum / Q&A)
```

---

## §4. Required Document Structure

### 4.1 Mandatory Section Order

Every research document MUST follow this section order:

```
1. Header (ICS-S session header with ⬡ OMEGA branding)
2. Table of Contents (if document > 100 lines)
3. Body content (research findings, analysis, verification)
4. Sources section (see §4.2)
5. Cross-Reference section (optional, see §5)
6. L1→L2→L3 Distillation section
7. Footer (maintainer metadata)
```

### 4.2 Sources Section Template

The Sources section MUST appear as the **second-to-last section** (immediately before L1→L2→L3 Distillation). It uses this structure:

```markdown
---

## Sources

### Official Documentation
<!-- Score 10 sources — official project docs, source code, specs -->

### Primary Verification
<!-- Score 9 sources — live-verified by Omega agents -->

### Official Secondary
<!-- Score 8 sources — changelogs, release notes, official blogs -->

### Expert & Technical Analysis
<!-- Score 6-7 sources — deep dives by recognized experts -->

### Community & General
<!-- Score 3-5 sources — community docs, blogs, forums -->

### Social & Speculative
<!-- Score 1-2 sources — use sparingly, must be justified -->

---
```

If a category has zero entries, it may be omitted from the document.

### 4.3 Minimum Source Requirement

| Document Length | Minimum Sources | Minimum Score Threshold |
|----------------|----------------|------------------------|
| < 50 lines | 1 | 4 |
| 50-200 lines | 3 | 5 (at least 1 must be ≥ 7) |
| 200-500 lines | 5 | 5 (at least 2 must be ≥ 8) |
| > 500 lines | 10 | 5 (at least 3 must be ≥ 8) |

Documents that do not meet the minimum source requirement MUST include a justification in a `## Source Limitations` section immediately before the Sources section.

---

## §5. Cross-Referencing Protocol

### 5.1 When to Cross-Reference

Cross-references are used when a finding is **derived from, depends on, or extends** a previously mined document. Use a cross-reference instead of re-citing the original external source.

### 5.2 Cross-Reference Format

```markdown
Source: [SEARXNG_DEEP_RESEARCH_20260621.md §1.3] — Health check best practices (Verified: Yes)
     ↳ Original: [SearXNG settings.yml | Score: 10 | Accessed: 2026-06-21]
```

The `↳ Original` line traces back to the primary external source. This creates a **citation chain** that can be audited.

### 5.3 Citation Chain Integrity

When a cross-reference is used, ALL documents in the chain must have verified sources:

```
Document C cites Document B
  → Document B must have a verified source for that claim
    → Document B's source cites Document A
      → Document A must have a verified original external source
```

If any link in the chain is `Verified: No`, the cross-reference must note it:

```markdown
Source: [UNIFIED_GAP_MAP_20260612.md §2.4] — Provider timeout issue
     ↳ Original: UNVERIFIED — see GAP_MAP source §3
     Status: PENDING VERIFICATION
```

### 5.4 Cross-Reference Section

Documents MAY include a separate `## Cross-References` section (before Sources) when they extensively reference sibling documents:

```markdown
## Cross-References

This document extends findings from:

| Source Document | Section | Relationship |
|----------------|---------|--------------|
| `SEARXNG_DEEP_RESEARCH_20260621.md` | §1.3 | Base health check findings re-verified |
| `SEARXNG_VALIDATION_20260621.md` | §2.1 | Validation methodology reused |
| `SEARXNG_JEM_VERIFICATION_20260621.md` | §4.0 | Contradictory finding — see §3.2 this doc |
```

---

## §6. Tier Classification for Source Depth

In addition to the Quality Score (1-10), each source SHOULD be classified by **depth tier** to indicate how thoroughly it was used:

| Tier | Label | Definition | Mark |
|------|-------|------------|------|
| T1 | **Referenced** | Mentioned in passing; not deeply analyzed | `[T1]` |
| T2 | **Extracted** | Specific facts, configs, or data extracted from source | `[T2]` |
| T3 | **Verified** | Source claims were verified against live system | `[T3]` |
| T4 | **Cross-Validated** | Source agreement/corroboration sought across 2+ independent sources | `[T4]` |

**Usage**: Add the tier mark at the end of the citation entry:

```markdown
1. [searxng/settings.yml](https://github.com/searxng/searxng/blob/master/searx/settings.yml)
   (Score: 10, 2026-06-21, Verified: Yes) [T3]
```

---

## §7. Automation & CI Gate

### 7.1 `make verify-sources` Command

A CI gate that validates all research documents against the citation standard.

**Implementation approach**: A shell script at `scripts/verify_sources.sh` that uses `grep`, `awk`, and Python to check each document.

**Validation checks**:

```
Check 1: "## Sources" section exists
  → grep -q "## Sources" "$file"
  → FAIL if missing (exit code 1)

Check 2: Each source entry has a URL
  → grep -E '^\s*\d+\.\s+\*\*URL\*\*|^\s*\d+\.\s+\[' "$file"
  → FAIL if any source entry lacks a URL-like pattern

Check 3: Each source entry has a Score
  → grep -E 'Score:\s+\d+' "$file"
  → FAIL if any source entry lacks "Score: N"

Check 4: Each source entry has an Access Date or Accessed
  → grep -E '[Aa]ccess' "$file" | grep -E '\d{4}-\d{2}-\d{2}'
  → FAIL if any source entry lacks a date

Check 5: Each source entry has Topic Tags (for new docs only)
  → grep -E 'Tags:' "$file"
  → WARN if missing (not yet required for backfilled docs)

Check 6: Minimum source count per document length (see §4.3)
  → Count sources, count lines, compare against threshold
  → FAIL if below threshold

Check 7: No source has Score 1-2 without justification
  → grep -E 'Score:\s+[12]' "$file"
  → WARN if found — requires manual review

Check 8: Verified field present on each source
  → grep -E 'Verified:' "$file"
  → WARN if missing
```

### 7.2 Proposed Shell Script Structure

```bash
#!/usr/bin/env bash
# scripts/verify_sources.sh
# Verifies all research documents against the Citation Standard.
# Usage: ./scripts/verify_sources.sh [files...]
# If no files given, scans all known research directories.

set -euo pipefail

FAILED=0
WARNED=0
DOCS_DIRS=("data/entities/*/workspace/mining_reports/" "docs/research/")

check_has_sources_section() {
    local file="$1"
    if ! grep -q "## Sources" "$file"; then
        echo "FAIL: $file — missing '## Sources' section"
        return 1
    fi
    return 0
}

check_has_scores() {
    local file="$1"
    local count
    count=$(grep -c 'Score:' "$file" 2>/dev/null || echo 0)
    if [ "$count" -eq 0 ]; then
        echo "FAIL: $file — no source entries with Score: field"
        return 1
    fi
    return 0
}

check_has_dates() {
    local file="$1"
    local count
    count=$(grep -cE '[Aa]ccessed?:?\s+\d{4}-\d{2}-\d{2}' "$file" 2>/dev/null || echo 0)
    if [ "$count" -eq 0 ]; then
        echo "WARN: $file — no source entries with Access Date"
        return 1
    fi
    return 0
}

# ... additional check functions ...

main() {
    local files=("$@")
    if [ "${#files[@]}" -eq 0 ]; then
        # Gather all research documents
        while IFS= read -r -d '' f; do
            files+=("$f")
        done < <(find "${DOCS_DIRS[@]}" -name '*.md' -print0 2>/dev/null || true)
    fi

    for file in "${files[@]}"; do
        check_has_sources_section "$file" || ((FAILED++))
        check_has_scores "$file" || ((FAILED++))
        check_has_dates "$file" || ((WARNED++))
    done

    echo "---"
    echo "Results: $FAILED failures, $WARNED warnings"
    exit $((FAILED > 0 ? 1 : 0))
}

main "$@"
```

### 7.3 Makefile Integration

Add to `Makefile`:

```makefile
# ── Source verification ──
.PHONY: verify-sources
verify-sources:
	@echo "🔍 Checking citation standard compliance..."
	@scripts/verify_sources.sh
	@echo "✅ All documents pass citation standard checks."

# ── Full verification suite ──
.PHONY: verify-full
verify-full: test temple-grade heritage-map verify-sources
	@echo "🏛️ All verification gates passed."
```

### 7.4 CI Integration (Future)

When GitHub Actions are active, the `verify-sources` gate should run on every PR that modifies `*.md` files:

```yaml
# .github/workflows/verify-sources.yml (FUTURE)
name: Source Verification
on:
  pull_request:
    paths:
      - 'data/entities/*/workspace/mining_reports/*.md'
      - 'docs/research/*.md'
jobs:
  verify-sources:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify citation standard
        run: make verify-sources
```

---

## §8. Backfill Process

### 8.1 Priority Order

Existing documents (40+ in Roc Racoon's mining reports alone, plus 45+ in `docs/research/`) need backfill. Priority order:

| Priority | Document Type | Example | Target Date |
|----------|--------------|---------|-------------|
| P0 | Documents cited by other documents | `SEARXNG_DEEP_RESEARCH_20260621.md`, `UNIFIED_GAP_MAP_20260612.md` | Sprint end |
| P1 | Architectural decision documents | `docs/strategy/*.md`, `docs/decisions/PIVOT_LOG.md`-adjacent | Next sprint |
| P2 | Verification reports | `*_VERIFICATION_*.md`, `*_VALIDATION_*.md` | Within 2 sprints |
| P3 | Single-source mining reports | `*_MINING_*.md` (single legacy source) | Best effort |
| P4 | Internal notes / scratch | Files with `< 20` lines | Not required |

### 8.2 Backfill Procedure

For each document being backfilled:

1. **Read the document** to identify all factual claims
2. **Identify the source** for each claim (may require re-searching)
3. **Score each source** using the rubric (§3)
4. **Verify critical sources** (Score ≥ 8 claims should be verified against live system)
5. **Insert the `## Sources` section** in the correct position (second-to-last)
6. **Add inline citations** using the `[Source: ...]` anchor format
7. **Update the L1→L2→L3 section** if needed to reflect source quality
8. **Mark the document header** with `**Sources**: Backfilled YYYY-MM-DD`

### 8.3 Backfill Header Annotation

```markdown
**Citation Status**: Backfilled 2026-06-21 by Verity
**Source Count**: 12 (Score 10: 3, Score 9: 2, Score 5: 4, Score 4: 3)
**Verification Rate**: 5/12 sources verified against live system
```

---

## §9. Edge Cases & Exemptions

### 9.1 Self-Verified Claims

When a claim is verified by the agent's own live execution (e.g., `podman exec` output, `curl` response), it counts as **Score 9 (Verified Primary)** but MUST include the command used in the Notes field:

```markdown
**Notes**: Verified via `podman exec searxng-container cat /etc/searxng/settings.yml | grep timeout`
```

### 9.2 LLM-Generated Content

LLM outputs are **never** acceptable as primary sources. If an LLM produced a finding that was then verified against a real system, the source is the **real system** (Score 9), not the LLM. The LLM may be mentioned in Notes:

```markdown
**Notes**: Hypothesis generated by Claude 4.5 Sonnet; verified against live SearXNG instance.
```

### 9.3 Orphan Sources

If a source URL is dead (404, domain expired, repo deleted), mark it as:

```markdown
**URL**: `https://example.com/dead-link` (⚠️ DEAD — archived at `data/archives/sources/example_backup.html`)
**Score**: 5 (Community Docs — degraded from 7 due to dead link)
```

The recommended action is to archive the content via `firecrawl_scrape` or `webfetch` into `data/archives/sources/` at time of first citation.

### 9.4 Confidential / Private Sources

If a source is not publicly accessible (private repo, internal email, personal conversation), mark as:

```markdown
**URL**: `private://internal-email-2026-06-15` (not publicly accessible)
**Score**: 8 (Official Secondary — internal source)
**Notes**: Internal email from SearXNG maintainer. Not for redistribution.
```

### 9.5 Source Exemption for Distillation-Only Documents

Documents that are purely L1→L2→L3 distillations with no new external research (e.g., a soul.yaml update record) are exempt from the minimum source requirement but MUST still include:

```markdown
## Sources

No external sources cited. This document is a pure distillation of:
- Session gnosis from [SESSION_ID]
- Prior findings from [SOURCE_DOCUMENT.md §N]
```

---

## §10. Roadmap Addition

Add the following block to `SOVEREIGN_EVOLUTION_ROADMAP.md` after the H2-K section.

### Phase H2-L: Research Documentation Standards (NEW — 2026-06-21)

**Priority**: MEDIUM
**Sprint**: Post-SearXNG (Sprint F)
**Goal**: Every research document meets the citation standard defined in `RESEARCH_CITATION_STANDARD_SPEC.md`.

| # | Task | Owner | Effort | Impact | Status |
|---|------|-------|--------|--------|--------|
| H2-L1 | Design citation schema + quality rubric | Verity | 1h | 🔴 HIGH | ✅ SPEC DONE |
| H2-L2 | Write `RESEARCH_CITATION_STANDARD_SPEC.md` (this doc) | Verity | 2h | 🔴 HIGH | ✅ SPEC DONE |
| H2-L3 | Create `scripts/verify_sources.sh` CI gate | P3 (Engineering) | 1h | 🟡 MED | ⏳ PENDING |
| H2-L4 | Add `verify-sources` target to Makefile | P3 (Engineering) | 15m | 🟡 MED | ⏳ PENDING |
| H2-L5 | Backfill 10 P0 documents with source sections | Roc Racoon | 4h | 🟡 MED | ⏳ PENDING |
| H2-L6 | Backfill 15 P1-P2 documents | Roc Racoon | 6h | 🟢 LOW | ⏳ PENDING |
| H2-L7 | Train fleet agents on citation standard (M18 efficiency) | Verity | 30m | 🟡 MED | ⏳ PENDING |
| H2-L8 | Add source quality score to all new docs going forward | All agents | Ongoing | 🟡 MED | ⏳ PENDING |

**Success criteria**:
- `make verify-sources` passes with 0 failures
- P0 documents backfilled within 1 sprint of spec approval
- 90% of new research documents include source sections within 2 sprints

**Mandate alignment**:
- **M5 (Gnosis Preservation)**: Citations ensure gnosis is traceable to its origin
- **M11 (Soul Integrity)**: Verified sources strengthen soul lessons
- **M17 (Cognitive Integrity)**: Cross-referencing prevents memory drift
- **M18 (Token Efficiency)**: Structured citations reduce ambiguity; no wasted tokens on unverifiable claims
- **M22 (Response Provenance)**: Citation provenance is the research analogue of response provenance

---

## §11. Appendix A — Template

### Complete Document Template

```markdown
# 🔱 [Document Title]
# ⬡ OMEGA ⬡ [ENTITY] ⬡ [MODEL] ⬡ [CHANNEL] ⬡ [TRACE]
**Date**: YYYY-MM-DD
**Status**: [DRAFT | COMPLETE | VERIFIED]
**Author**: [Entity name]
**Sources**: Backfilled YYYY-MM-DD (if applicable)
**Source Count**: N (Score 10: X, Score 9: Y, Score <5: Z)

---

## Table of Contents

...

## [Research Body]

...content with inline citations...

[Source: Title | Score: N | Verified: Yes/No]

...

---

## Cross-References (optional)

...

---

## Sources

### Official Documentation

1. **URL**: `https://example.com/official-docs`
   **Title**: Official Documentation Title
   **Score**: 10 (Official Primary)
   **Accessed**: YYYY-MM-DD
   **Tags**: topic, subtopic
   **Verified**: Yes
   **Verifier**: entity_name
   **Notes**: ...

### Primary Verification

...

### Community & General

...

---

## L1→L2→L3 Distillation

### L1 (Narrative)
...

### L2 (Insight)
...

### L3 (Universal Principle)
...

---

*Maintained by: [Entity] | Last updated: YYYY-MM-DD*
```

---

## §12. Appendix B — Lint Rules (for Future `mdl` or `markdownlint` Extension)

When implementing a markdown linter rule for citation standard, encode these rules:

| Rule ID | Check | Severity | Auto-fixable? |
|---------|-------|----------|---------------|
| `OMEGA-CITE-001` | Document has `## Sources` section | error | no |
| `OMEGA-CITE-002` | Sources section is before `## L1→L2→L3 Distillation` | error | no |
| `OMEGA-CITE-003` | Each source entry has URL-like pattern | error | no |
| `OMEGA-CITE-004` | Each source entry has `Score:` with integer 1-10 | error | no |
| `OMEGA-CITE-005` | Each source entry has access date in `YYYY-MM-DD` | error | no |
| `OMEGA-CITE-006` | Each source entry has `Verified:` field | warning | no |
| `OMEGA-CITE-007` | Each source entry has `Tags:` field | warning | no |
| `OMEGA-CITE-008` | No score below minimum threshold without justification | warning | no |
| `OMEGA-CITE-009` | Inline citations match entries in Sources section | warning | no |
| `OMEGA-CITE-010` | Cross-reference chain integrity (all links traceable) | warning | no |

---

*⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_citation_standard*
*Designer: Verity (Compliance & Gnosis Agent) | Date: 2026-06-21*
*Reviewed by: — (pending fleet review)*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
