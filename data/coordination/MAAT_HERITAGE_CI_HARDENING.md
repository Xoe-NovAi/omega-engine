# 🔱 MA'AT — Heritage CI Hardening Implementation Plan (D208 Follow-up)
**Date**: 2026-07-10
**Status**: IN PROGRESS
**Trace**: maat-heritage-ci-20260710

---

## 🎯 Mission
Harden the heritage vetting pipeline per D208. Jem's audit revealed systemic over-attribution because the M14 Qualification Gate was not enforced strictly enough.

---

## 📋 Implementation Tasks

### 1. SOVEREIGN_MANDATES.md — M14 Clarification (D208)
**File**: `SOVEREIGN_MANDATES.md`
**Action**: Add strict scope enforcement, classification taxonomy, and qualification gate to M14

### 2. CI Gate Hardening — `make heritage-vet` Enhancement
**Target**: Enhance existing `scripts/heritage_vet.py`
**Requirements**:
- Scope Validation: Every `[id-soft:]` tag must have a corresponding vet record with matching file:line
- Classification Enforcement: Tag must declare scope (e.g., `[id-soft: doom-1993] ZONEID` not just `[id-soft: doom-1993]`)
- Pre-commit Hook: Block commits adding `[id-soft:]` without vet record
- Scope Validation: Flag tags used to justify multiple concepts in same file (C-ARCH-005 violation)

### 3. Script: `scripts/heritage_vet.py` (Enhanced)
**Enhancements**:
- Parse scope declarations from tags (format: `[id-soft: GAME-YEAR] Pattern Name`)
- Cross-reference with `HERITAGE_VET_LOG.md` vet records including file:line locations
- Validate scope declarations match vet record scope
- Detect C-ARCH-005 violations (same tag used for multiple concepts)
- Output: PASS/FAIL with specific violations

### 4. Script: `scripts/heritage_audit.py` (New)
**Purpose**: Audit and classify all tags
**Features**:
- Classify all tags as LEGITIMATE / METAPHORICAL / OVER-ATTRIBUTED
- Generate remediation report
- Output corrected CREDITS.md registry

### 5. Makefile Updates
**Add targets**:
```makefile
heritage-vet:          # Enhanced validation with scope checking
heritage-audit:        # Classification audit
heritage-vet-strict:   # Strict mode for CI
```

### 6. Pre-commit Hook Enhancement
**File**: `.githooks/pre-commit`
**Add**: Check for new `[id-soft:]` tags without corresponding vet records

---

## 🔧 Technical Design

### Tag Format (Enhanced)
```
# [id-soft: GAME-YEAR] Pattern Name — why this code exists
```
**Required components**:
1. Game code: `doom-1993`, `quake-1996`, `quake2-1997`, `quake3-1999`, `doom3-2004`, `doom3bfg-2012`, `wolf3d-2012`
2. Pattern Name: Specific technique name (e.g., "ZONEID", "BSP Culling", "Zone Memory")
3. Justification: Brief explanation of why this code exists

### Vet Record Enhancement
Vet records in `HERITAGE_VET_LOG.md` must include:
- `file_locations`: List of `file:line` where the tag appears
- `scope`: Declaration of what this tag applies to (and explicitly what it does NOT apply to)

### Classification Taxonomy
| Classification | Criteria | Action |
|----------------|----------|--------|
| **LEGITIMATE** | Direct port of id Software technique; has vet record with score ≥7; scope declared | Keep tag |
| **METAPHORICAL** | Rhetorical analogy only (e.g., "Thinker Chain like Quake thinker") | Convert to plain comment — NO tag |
| **OVER-ATTRIBUTED** | User-original work that merely resembles id Software pattern | STRIP tag — NO tag |

### C-ARCH-005 Violation Detection
Flag when the same `[id-soft: GAME-YEAR] Pattern` tag is used to justify multiple distinct concepts in the same file.

---

## 📦 Deliverables

1. ✅ Updated `SOVEREIGN_MANDATES.md` with M14 clarification
2. ✅ Enhanced `scripts/heritage_vet.py` with scope validation
3. ✅ New `scripts/heritage_audit.py` for classification
4. ✅ Updated `Makefile` with new targets
5. ✅ Enhanced `.githooks/pre-commit` with heritage tag check
6. ✅ Implementation plan at `data/coordination/MAAT_HERITAGE_CI_HARDENING.md`

---

## ✅ Acceptance Criteria

- [ ] `make heritage-vet` passes with zero violations on current codebase
- [ ] `make heritage-audit` produces classification report
- [ ] Pre-commit hook blocks commits with unvetted `[id-soft:]` tags
- [ ] All existing tags classified as LEGITIMATE/METAPHORICAL/OVER-ATTRIBUTED
- [ ] C-ARCH-005 violations detected and reported
- [ ] M14 in SOVEREIGN_MANDATES.md reflects D208 clarification

---

## 🐝 Hive Mind Coordination
- Post context with tag `heritage-ci-hardening-complete` upon completion
- Heartbeat every 5-10 minutes during implementation