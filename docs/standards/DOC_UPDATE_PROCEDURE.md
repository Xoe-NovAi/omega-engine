# 🔱 Documentation Update Procedure
**AP Token**: `AP-DOC-UPDATE-PROC-v1.0.0`
⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ opencode ⬡ trc_doc_proc ⬡ DOCUMENTATION-STANDARDS

**Date**: 2026-07-06
**Purpose**: Standardized procedure for updating Omega Engine documentation to ensure consistency, accuracy, and traceability.

---

## 🎯 Overview

This procedure defines the mandatory steps for creating, updating, and reviewing documentation in the Omega Engine repository. All agents and contributors MUST follow this process.

---

## 📋 When to Update Documentation

### Mandatory Updates (Trigger-Based)
| Trigger | Required Action | Timeline |
|---------|----------------|----------|
| Code change affecting public API | Update relevant reference docs | Same PR |
| New feature added | Add/update user guide & reference | Same PR |
| Configuration change | Update config reference & user guide | Same PR |
| New mandate or mandate change | Update SOVEREIGN_MANDATES.md & AGENTS.md | Same PR |
| New agent or agent capability change | Update AGENTS.md & agent file | Same PR |
| New skill added | Create skill doc & update AGENTS.md | Same PR |
| Architecture decision (PIVOT_LOG entry) | Update relevant architecture docs | Within 24 hours |
| Test count change | Update OMEGA_ENGINE.md metrics | Same PR |
| Version bump | Update all version references | Same PR |

### Scheduled Updates (Time-Based)
| Frequency | Scope | Owner |
|-----------|-------|-------|
| Per Release | Full documentation review | Release Manager |
| Monthly | High-traffic docs (User Manual, Onboarding) | Documentation Sprint |
| Quarterly | Complete documentation audit | Documentation Sprint |
| Per Sprint | Sprint-specific docs (retrospectives, plans) | Sprint Owner |

---

## 🔄 Update Workflow

### Step 1: Identify Need
- **Code Review**: Reviewer flags documentation gap in PR
- **User Feedback**: Issue filed about unclear/missing docs
- **Scheduled Audit**: Monthly/quarterly review identifies stale content
- **Self-Identification**: Author realizes docs need update during work

### Step 2: Create Branch
```bash
# From main branch
git checkout main
git pull origin main

# Create documentation branch
git checkout -b docs/[description]-YYYYMMDD
# Examples:
# docs/onboarding-guide-20260706
# docs/troubleshooting-update-20260706
# docs/api-reference-fix-20260706
```

### Step 3: Make Changes
Follow the **Documentation Style Guide** (`docs/standards/DOC_STYLE_GUIDE.md`):

1. **Update Header**: Increment AP Token version, update Date, verify ENTITY/MODEL
2. **Make Focused Changes**: One logical change per commit
3. **Verify Technical Accuracy**: Test all code examples, commands, config snippets
4. **Update Cross-References**: Fix any broken internal links
5. **Update Version References**: Bump version numbers where applicable

### Step 4: Validate
```bash
# Run documentation validation script
python scripts/validate_docs.py

# Check for broken links
python scripts/check_links.py

# Verify all code examples work
# (Run commands manually or via test suite)

# Run spell check
.venv/bin/pip install codespell
codespell docs/
```

### Step 5: Commit
```bash
# Stage changes
git add docs/path/to/file.md

# Commit with standardized message
git commit -m "docs: [section] - [brief description]

- [Detail 1]
- [Detail 2]

AP-Token: AP-[TOKEN]-v[X.Y.Z]"
```

### Step 6: Pull Request
```bash
# Push branch
git push origin docs/[description]-YYYYMMDD

# Create PR with:
# Title: docs: [section] - [description]
# Description:
#   - What changed
#   - Why it changed
#   - Validation performed
#   - Related issues/PRs
```

### Step 7: Review
**Required Reviewers**: 
- Documentation Sprint Owner (for style/structure)
- Domain Expert (for technical accuracy)
- Release Manager (for version/impact)

**Review Checklist**:
- [ ] Header follows style guide
- [ ] Technical accuracy verified
- [ ] Code examples tested
- [ ] No broken links
- [ ] Consistent terminology
- [ ] Version numbers updated
- [ ] Cross-references intact
- [ ] AP Token incremented correctly

### Step 8: Merge & Notify
```bash
# After approval
git checkout main
git pull origin main
git merge docs/[description]-YYYYMMDD
git push origin main

# Clean up branch
git branch -d docs/[description]-YYYYMMDD
git push origin --delete docs/[description]-YYYYMMDD
```

**Notification**: Post to Hivemind and relevant channels:
```
docs: [section] updated - [brief description]
Files: docs/path/to/file.md
Version: AP-[TOKEN]-v[X.Y.Z]
```

---

## 📝 Versioning Rules

### AP Token Versioning
Format: `AP-[PROJECT]-v[MAJOR].[MINOR].[PATCH]`

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Typo fix, formatting | PATCH | v1.0.0 → v1.0.1 |
| Content addition/clarification | MINOR | v1.0.0 → v1.1.0 |
| Structural rewrite, breaking change | MAJOR | v1.0.0 → v2.0.0 |
| Complete rewrite | MAJOR | v1.0.0 → v2.0.0 |

### Document Status Values
| Status | Meaning |
|--------|---------|
| DRAFT | Work in progress, not reviewed |
| REVIEW | Under review, not approved |
| STANDARD | Approved, current, maintained |
| DEPRECATED | Superseded, marked for removal |
| ARCHIVED | Historical, read-only |

---

## 📁 File Organization Rules by Document Type

### System State Documents
**Files**: `OMEGA_ENGINE.md`, `SOVEREIGN_MANDATES.md`, `AGENTS.md`
**Update Authority**: Any agent changing engine state
**Validation**: `make test`, `make temple-grade`, `make heritage-map`
**Frequency**: Every state change

### Strategy Documents
**Location**: `docs/strategy/`
**Update Authority**: Sprint owners, Kali, Ma'at
**Validation**: Cross-reference with PIVOT_LOG
**Frequency**: Per sprint/phase

### Reference Documents
**Location**: `docs/reference/`
**Update Authority**: Domain experts
**Validation**: Code example testing
**Frequency**: Per API/config change

### User Guides
**Location**: `docs/user/`
**Update Authority**: Documentation Sprint
**Validation**: New user testing
**Frequency**: Monthly + per feature

### Deep Dives
**Location**: `docs/deep/`
**Update Authority**: Domain experts
**Validation**: Technical review
**Frequency**: Per architecture change

### Agent & Skill Definitions
**Location**: `.opencode/agents/*.md`, `.opencode/skills/*.md`
**Update Authority**: Agent owner, Documentation Sprint
**Validation**: Agent launch test
**Frequency**: Per capability change

---

## 🛠️ Validation Scripts

### `scripts/validate_docs.py`
Checks:
- [ ] All files have valid headers
- [ ] AP Token format correct
- [ ] No broken internal links
- [ ] Version numbers consistent
- [ ] Required sections present
- [ ] Style guide compliance

### `scripts/check_links.py`
Checks:
- [ ] All internal `.md` links resolve
- [ ] All external URLs accessible (optional)
- [ ] Anchor links point to existing headers

### `scripts/check_versions.py`
Checks:
- [ ] OMEGA_ENGINE.md version matches pyproject.toml
- [ ] USER_MANUAL.md version matches
- [ ] CHANGELOG.md has entry for current version

---

## 📋 Pre-Commit Checklist

Before committing documentation changes:

- [ ] Header follows exact specification
- [ ] AP Token incremented appropriately
- [ ] Date is current (YYYY-MM-DD)
- [ ] ENTITY and MODEL fields accurate
- [ ] trc_* code matches document purpose
- [ ] STATUS reflects current state
- [ ] Purpose statement is one clear sentence
- [ ] All code examples tested and working
- [ ] All commands verified
- [ ] Configuration snippets match actual files
- [ ] Internal links resolve
- [ ] No broken external links (or marked as known)
- [ ] Terminology consistent with glossary
- [ ] Heritage tags included where applicable
- [ ] Cross-references to PIVOT_LOG decisions
- [ ] Version numbers updated in all locations
- [ ] Spell check passed
- [ ] Validation script passes

---

## 🚨 Emergency Updates

For critical documentation fixes (security, safety, blocking issues):

1. **Bypass normal review**: Direct commit to main with `docs: HOTFIX - [description]`
2. **Notify immediately**: Hivemind post + team notification
3. **Follow up**: Full review within 24 hours
4. **Document**: Add to CHANGELOG.md with HOTFIX tag

---

## 📚 Related Documents

- `docs/standards/DOC_STYLE_GUIDE.md` — Writing and formatting standards
- `docs/standards/CODE_STYLE_GUIDE.md` — Code example standards
- `docs/strategy/DOCUMENT_MANAGEMENT_SYSTEM.md` — Document lifecycle
- `OMEGA_ENGINE.md` — System state (update on every change)
- `SOVEREIGN_MANDATES.md` — Constitutional law (update on mandate change)
- `AGENTS.md` — Agent rules (update on agent change)
- `docs/decisions/PIVOT_LOG.md` — Architectural decisions

---

## 📜 Changelog

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-07-06 | v1.0.0 | Initial documentation update procedure | NEMOTRON-3-SUPER |

---
*Last Updated: 2026-07-06 | Author: NEMOTRON-3-SUPER | Version: v1.0.0*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
