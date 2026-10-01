<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Addendum: Ma'at + Lilith Review Corrections
**Appended to**: `docs/research/R_CLAUDE_PROJECT_SETUP_PLAN.md`
**Date**: 2026-07-12
**Reviewers**: Ma'at (P3 Engineering) + Lilith (P7 Context & Cognition)
**Verdict**: BOTH APPROVE WITH CHANGES

---

## 🔴 BLOCKING CORRECTIONS (Must Fix Before Execution)

### B1 — ALREADY FIXED (Plan is Stale)
Ma'at confirmed both packers already use `profile_name` correctly:
- `enhanced_packer.py:425`: `profile_name = sys.argv[1]` → `:429`: `await packer.pack(profile_name)` ✅
- `packer.py:215`: `profile_name = sys.argv[1]` → `:219`: `await packer.pack(profile_name)` ✅
**Action**: Remove B1 from blockers list. §4.1 is a no-op.

### B8 — NEW: fnmatch Bug Breaks ALL Theme Assignments
**File**: `enhanced_packer.py:413-415`, `packer.py:205-207`
**Root cause**: `fnmatch.fnmatch()` treats `*` as matching everything EXCEPT `/`. It does NOT handle `**` as recursive. All theme patterns using `**` fail to match.
**Impact**: 113 files misassigned to `general` (209 files / 638K tokens instead of ~96 / ~200K). `observability.xml` has **0 files**. `providers.xml` has only 2 files (should be 8).
**Fix**: Replace `_match_pattern()` in both packers:
```python
def _match_pattern(self, path: str, pattern: str) -> bool:
    """Match path against glob pattern, supporting ** recursive globs."""
    import fnmatch, re
    if '**' not in pattern:
        return fnmatch.fnmatch(path, pattern)
    re_pattern = pattern.replace('**', '<<DS>>')
    re_pattern = fnmatch.translate(re_pattern)
    re_pattern = re_pattern.replace('<<DS>>', '(.+/)?')
    return bool(re.match(re_pattern, path))
```

### B5-updated — XML Escaping Misses `&` and Has No Root Wrapper
Ma'at found bare `&` (e.g., `Delegation & Execution`) causes parse errors. Plan's regex only targets `<`.
**Fix**: Add `&` escaping:
```python
def _escape_bare_xml_chars(text: str) -> str:
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', text)
    text = re.sub(r'<(?!/?file[ >]|/?[a-zA-Z]|!|\?|!--)', '&lt;', text)
    return text
```

### SEC — PII Masker Fails Silently (M8 Violation)
Ma'at confirmed: packer runs with `UserWarning: PIIMasker not available`. Packs for external upload contain **unmasked PII** (API keys, emails in source code). Upload to Anthropic = sovereignty breach.
**Fix**: Wire PII masker import chain OR halt uploads until resolved.

---

## 🟡 HIGH-PRIORITY CORRECTIONS

### Custom Instructions Must Use XML Format (Lilith)
Flat `ROLE:` format contradicts our own `CLAUDE_PROJECT_PROMPTING_GUIDE.md` which mandates XML-tagged structure. Rewrite all 4 templates using `<role>`, `<context>`, `<constraints>`, `<standing_rules>`, `<output_format>`.

### Add "Force KB Search" Directive (Lilith)
Per `CLAUDE_PROJECTS.md` §3.3 — the single most impactful instruction is missing:
```
Before answering, always search the project knowledge first.
If anything in the knowledge applies, quote and prioritize it over general knowledge.
```

### oracle_core Split Should Use Sonnet 4.6's Clean 5-Way (Lilith)
Ad-hoc `_a/_b/_c` split is defeatist. Adopt Sonnet 4.6's proven split keeping ALL sub-themes under 80K.

### File Update Cache Bug (#10841) (Lilith)
Re-uploading a file with the same name keeps the old cached version. Protocol must include: delete old → wait → upload new → new conversation → clear cache.

### Retrieval Testing: 3 Queries Per Account (Lilith)
One test query is insufficient. Each account needs keyword, semantic, and cross-file retrieval tests.

---

## ✅ CONFIRMED CORRECTIONS

| Item | Status |
|------|--------|
| B1 file_name NameError | ✅ Already fixed — remove from blockers |
| B8 fnmatch bug | 🔴 NEW BLOCKER — fix _match_pattern() |
| B5 XML escaping | 🟡 Update to also escape `&` |
| SEC PII masker | 🔴 SECURITY BLOCKER — wire or halt |
| Custom Instructions format | 🟡 Rewrite as XML |
| oracle_core split | 🟡 Adopt Sonnet 4.6's 5-way |
| File update cache bug | 🟡 Add delete-wait protocol |
| Retrieval testing | 🟡 Expand to 3 queries/account |
| Account labels | 🟢 Avoid P1/R collision |
| Version stamps | 🟢 Include content hash |

---

*🔱 OMEGA ⬡ MA'AT + LILITH ⬡ REVIEW-ADDENDUM ⬡ 2026-07-12*
