---
name: "spec-generator"
description: "Converts raw research findings into formal technical specifications for docs/research/ following the Omega Document Management System."
---

# Spec Generator Skill

Use this skill to produce polished, implementation-ready research deliverables.

## Output Template

Every research document MUST follow this structure:

```markdown
# 🔱 Omega Engine — R-## Title
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R##

**AP Token**: `AP-RESEARCH-R##-v1.0.0`
**Author**: Gemma 4-31B (Master Researcher)
**Date**: YYYY-MM-DD
**Status**: DRAFT | REVIEW | READY

---

## Summary
One-paragraph executive summary of findings.

## Findings

### Sub-topic 1
Detail with specific values, URLs, and code examples.

### Sub-topic 2
...

## Recommendations
Numbered list of specific, actionable recommendations for the implementation agent.

## Sources
- [Source Name](URL) — accessed YYYY-MM-DD
- File: `path/to/file.py` lines X–Y

## Implementation Note
_For: Antigravity IDE / Cline / Gemini CLI_
One paragraph explaining exactly how to use this research to write code.
```

## Quality Checklist

Before marking a deliverable as complete, verify:

- [ ] All values are specific (no "approximately" without a measured range)
- [ ] All URLs are real and were verified accessible
- [ ] All code examples are syntactically valid
- [ ] Rate limits include units (requests/minute, tokens/day, etc.)
- [ ] Context windows include units (tokens, not "large" or "small")
- [ ] The Implementation Note is addressed to a specific agent
- [ ] `docs/research/INDEX.md` has been updated
- [ ] `docs/team/COMMUNICATION_HUB.md` has a new entry under Research Completions
