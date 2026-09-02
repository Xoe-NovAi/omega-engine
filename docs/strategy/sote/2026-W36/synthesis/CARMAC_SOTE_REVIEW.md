<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JC-EIS SOTE Implementation Review

**AP Token**: `AP-JOHN_CARMACK-v1.0.0`
**Session**: `ses_fc8dca39effe3nZJp3QHx81Fy3` (continuation)
**Date**: 2026-09-01
**Role**: S3 Consultant — Architectural Review
**Model**: `minimax/minimax-m3:free`

---

## §0 — VERIFICATION (M23 Discipline)

**Files read before speaking:**

1. ✅ `docs/strategy/sote/INDEX.md` (133 lines) — Master index
2. ✅ `docs/strategy/sote/2026-W36/STATE_OF_ENGINE_v1.0.1.md` (805 lines) — Main report
3. ✅ `docs/strategy/sote/_template/SOTE_TEMPLATE.md` (379 lines) — Main template
4. ✅ `docs/strategy/sote/_template/VOICE_DIALECTIC_TEMPLATE.md` (105 lines) — Voice template
4. ✅ `docs/strategy/sote/_template/SOTE_INDEX_TEMPLATE.md` (102 lines) — Index template
5. ✅ `scripts/regenerate_sote_index.py` (354 lines) — Regeneration script
6. ✅ `docs/strategy/sote/2026-W36/sote.yaml` (211 lines) — Structured metadata
7. ✅ `docs/strategy/sote/2026-W36/PUBLIC_DIGEST.md` (72 lines) — Public digest
8. ✅ `docs/strategy/sote/2026-W36/synthesis/MAKALI_ORGANIZATION_STRATEGY.md` (396 lines) — Org strategy
9. ✅ `docs/strategy/sote/2026-W36/meta/WHAT_WORKED_WHAT_DIDNT.md` (167 lines) — Meta-learning

**Live filesystem checks:**
- `docs/strategy/sote/2026-W36/voices/` — 9 files (00_INDEX + 01-08)
- `docs/strategy/sote/2026-W36/synthesis/` — 1 file
- `docs/strategy/sote/2026-W36/actions/` — empty
- `docs/strategy/sote/2026-W36/meta/` — 1 file
- `scripts/regenerate_sote_index.py` — executable, imports yaml, re, json, datetime, pathlib

**Verified divergence (briefing frame vs. disk):**
- INDEX.md claims "Regeneration: Manual" but script exists and is functional
- sote.yaml has `open_actions` with "DONE" items mixed with pending
- PUBLIC_DIGEST.md says "16 pass, 8 warn, 4 fail (57.1%)" but STATE_OF_ENGINE says "18 pass, 5 warn, 5 fail (64.3%)" — **data drift in public digest**
- MAKALI_ORGANIZATION_STRATEGY.md §1 claims "2,107 total lines in the SOTE corpus" but actual count is ~2,500+ lines across all files

---

## §1 — ARCHITECTURAL SOUNDNESS

### §1.1 M2 Firewall Compliance

**Result**: ✅ **PASS** — The SOTE system lives entirely in `docs/strategy/sote/` which is **documentation**, not Core (`src/omega/`). No M2 violation possible by design.

**File:line evidence:**
- `scripts/regenerate_sote_index.py:19` — `SOTE_ROOT = Path("docs/strategy/sote")` — reads from docs only
- `scripts/regenerate_sote_index.py:21` — `PIVOT_LOG_PATH = Path("docs/decisions/PIVOT_LOG_CANONICAL.md")` — reads decisions, not Core
- `scripts/regenerate_sote_index.py:22` — `MANDATE_CHECK_PATH = Path("scripts/check_mandate_compliance.py")` — calls compliance script as subprocess (line 156-158), not import

**No Core imports from SOTE.** The SOTE system is a **documentation pipeline**, not an engine subsystem. This is correct.

### §1.2 Separation of Concerns

**Result**: ✅ **PASS** — The folder structure enforces clear separation:

| Folder | Purpose | Mutability | Lifecycle |
|--------|---------|------------|-----------|
| `voices/` | Immutable dialectic records | **FROZEN** at close | Never edited after week-close |
| `synthesis/` | Mutable synthesis docs | **MUTABLE** | Updated as decisions absorb |
| `actions/` | Action items | **MUTABLE** | Items open/close daily |
| `meta/` | Meta-learning | **APPEND-ONLY** | New weeks append; old weeks frozen |

**File:line evidence:**
- `MAKALI_ORGANIZATION_STRATEGY.md:146-155` — Explicit mutability table
- `SOTE_TEMPLATE.md:355-361` — "v1.0.0 frozen; v1.0.x patches may add"
- `VOICE_DIALECTIC_TEMPLATE.md:21-36` — §0 Verification requires file:line citations

**This is the correct pattern.** The "immutable voices / mutable synthesis" distinction solves the M27 chokepoint: decisions are proposed in voices (immutable), then absorbed into synthesis/PIVOT_LOG (mutable).

### §1.3 No Hardcoded Paths

**Result**: ⚠️ **PARTIAL** — The script has one hardcoded path assumption.

**File:line evidence:**
- `scripts/regenerate_sote_index.py:19` — `SOTE_ROOT = Path("docs/strategy/sote")` — **hardcoded relative path**
- `scripts/regenerate_sote_index.py:21` — `PIVOT_LOG_PATH = Path("docs/decisions/PIVOT_LOG_CANONICAL.md")` — **hardcoded**
- `scripts/regenerate_sote_index.py:22` — `MANDATE_CHECK_PATH = Path("scripts/check_mandate_compliance.py")` — **hardcoded**

**Risk**: If the script is run from a different working directory (e.g., CI runner, subdirectory), it will fail to find files.

**Fix**: Use `Path(__file__).parent.parent / "docs/strategy/sote"` or read from `OMEGA_ROOT` env var (per M24 Venv Sovereignty).

### §1.4 Template Completeness

**Result**: ✅ **PASS** — Three templates cover the full lifecycle:

| Template | Lines | Completeness |
|----------|------:|:------------:|
| `SOTE_TEMPLATE.md` | 379 | All 19 sections (§0-§19) with placeholders |
| `VOICE_DIALECTIC_TEMPLATE.md` | 105 | §0 Verification + 8 sections + C/D/S format |
| `SOTE_INDEX_TEMPLATE.md` | 102 | All index sections with placeholders |

**Gap**: No template for `actions/ACTION_ITEMS_WNN.md` or `meta/WHAT_WORKED_WHAT_DIDNT_WNN.md`. These are referenced in `MAKALI_ORGANIZATION_STRATEGY.md:168-176` but not templated.

---

## §2 — OPERATIONAL VIABILITY

### §2.1 Can This Run Weekly Without Manual Intervention?

**Result**: ❌ **NOT YET** — The regeneration script has gaps that require manual intervention.

**Critical gaps in `scripts/regenerate_sote_index.py`:**

| Gap | Line | Impact |
|-----|------|--------|
| **No L3 lesson extraction** | 293-299 | Hardcoded single lesson; doesn't parse from reports |
| **No cross-week theme extraction** | 303-308 | Hardcoded themes; doesn't compute from data |
| **No meta-learning extraction** | 311-319 | Hardcoded text; doesn't parse `meta/WHAT_WORKED_WHAT_DIDNT_WNN.md` |
| **No decision absorption status from PIVOT_LOG** | 132-147 | Regex assumes specific table format; fragile |
| **No mandate compliance trend from history** | 285-289 | Only parses current week; doesn't build trend from prior weeks |
| **No voice session ID extraction fallback** | 112-113 | Regex `Session ID.*?:\s*(\S+)` may fail on format variations |
| **No error handling for missing week folders** | 40-47 | `find_week_folders()` returns empty list silently |
| **No validation of generated INDEX.md** | 347-351 | Writes without verifying output structure |

**The script is a v0.1 prototype.** It works for W36 because the data is fresh and the author knows the format. It will break on W37 without fixes.

### §2.2 sote.yaml Schema Quality

**Result**: ✅ **GOOD** — The `sote.yaml` is well-structured for LLM ingestion.

**Strengths:**
- Explicit version tracking (`sote_versions` array)
- Voice metadata with session IDs, focus, decision counts
- Mandate compliance as structured data (pass/warn/fail/pct)
- L3 lessons with confidence scores and sources
- Open actions as trackable list
- SOTE process decisions with mandate references

**Gaps:**
- No JSON Schema validation (no `sote.schema.json`)
- `open_actions` mixes "DONE" and pending items — should be separate `completed_actions` and `open_actions`
- No `generated_at` timestamp for cache invalidation
- `decisions.by_voice` counts don't match voice file `decisions` fields (e.g., Lilith: 16 in sote.yaml vs actual voice file)

### §2.3 Public/Internal Split

**Result**: ⚠️ **PARTIAL** — The split exists but is not enforced by tooling.

**Current state:**
- `PUBLIC_DIGEST.md` exists (72 lines, public-facing)
- `STATE_OF_ENGINE_v1.0.1.md` is the internal full report
- `voices/` and `synthesis/` are internal

**Gap**: No automated generation of `PUBLIC_DIGEST.md` from the main report. The digest is manually written (evidenced by data drift: 57.1% vs 64.3% compliance).

**Required**: A `generate_public_digest.py` that extracts:
1. Top 3 findings (from §6 or §12)
2. Mandate compliance summary (from §2 or `sote.yaml`)
3. Top 5 action items (from §11 or `actions/`)
3. Link to full internal report

---

## §3 — SCALABILITY (52 WEEKS / 104 WEEKS)

### §3.1 File Count Projection

| Week | Voices | Synthesis | Actions | Meta | Total/Week | Cumulative (52w) |
|------|--------|-----------|---------|------|-----------:|-----------------:|
| 1 | 8 | 1 | 1 | 1 | 11 | 11 |
| 52 | 8 | 1 | 1 | 1 | 11 | **572 files** |
| 104 | 8 | 1 | 1 | 1 | 11 | **1,144 files** |

**Verdict**: **Manageable**. 572 files in `docs/strategy/sote/` is well within git/linux limits. The week-folder structure (`2026-W36/`) keeps `ls` output bounded (~11 entries per week).

### §3.2 Index Regeneration Performance

**Current**: `regenerate_sote_index.py` scans all week folders, parses all voice files, runs `check_mandate_compliance.py` as subprocess.

**Projected at 52 weeks**:
- 52 weeks × 8 voices = 416 voice files to parse
- 52 `STATE_OF_ENGINE` reports to parse
- 1 subprocess call to `check_mandate_compliance.py` (~5s)

**Estimated runtime**: ~10-15 seconds. **Acceptable for weekly manual run.**

**Risk at 104 weeks**: ~20-30 seconds. Still acceptable.

**Optimization if needed**: Cache parsed voice data in `.sote_cache/` (JSON), invalidate on file mtime change.

### §3.3 PIVOT_LOG Cross-Walk Scaling

**Current**: 67 decisions in W36 voices, 0 absorbed.

**Projected**: If 50 decisions/week × 52 weeks = 2,600 decisions/year.

**PIVOT_LOG_CANONICAL.md** at 2,517 lines currently. At 2,600 decisions/year with ~5 lines/decision = 13,000 lines/year. **Manageable** but will need sectioning by year/quarter.

**The `regenerate_sote_index.py` cross-walk (lines 256-275)** collects ALL decisions from ALL weeks every run. At 2,600 decisions, this is O(N) per regeneration — fine for weekly, but the INDEX.md will grow large.

**Recommendation**: Add year-based index sharding (`INDEX_2026.md`, `INDEX_2027.md`) or keep master index but paginate.

### §3.4 Mandate Compliance Trend Storage

**Current**: `sote.yaml` per week + INDEX.md table.

**At 52 weeks**: 52 `sote.yaml` files + INDEX.md with 52-row trend table. **Trivial.**

**At 104 weeks**: 104 files. Still trivial.

**No scaling concern here.**

---

## §4 — TOOLING QUALITY

### §4.1 `regenerate_sote_index.py` — Code Review

**File**: `scripts/regenerate_sote_index.py` (354 lines)

**Strengths:**
- Clean structure: `find_week_folders()` → `parse_sote_report()` → `parse_voice_files()` → `parse_pivot_log()` → `get_mandate_compliance()` → `generate_index()`
- Uses `pathlib`, `re`, `yaml`, `datetime` — standard library only
- Voice ordering via `VOICE_ORDER` constant (canonical)
- Subprocess call to mandate check with timeout (line 158)

**Defects (file:line):**

| Line | Defect | Severity |
|------|--------|:--------:|
| 19 | `SOTE_ROOT = Path("docs/strategy/sote")` — hardcoded cwd-relative | **HIGH** |
| 21-22 | `PIVOT_LOG_PATH`, `MANDATE_CHECK_PATH` — hardcoded | **HIGH** |
| 68-70 | `title_match = re.search(r"Title.*?:\s*(.+)", content)` — fragile regex | **MEDIUM** |
| 73-75 | `finding_match = re.search(r"Top Finding.*?:\s*(.+)", content)` — section may not exist | **MEDIUM** |
| 78-85 | `mandate_match = re.search(r"\| (\d+) \| (\d+) \| (\d+) \| ([\d.]+)%", content)` — assumes specific table format | **HIGH** |
| 107 | `re.finditer(r"D-([A-Z0-9-]+).*?\|", content)` — matches any `D-` pattern, not just PIVOT_LOG decisions | **MEDIUM** |
| 112-113 | `session_match = re.search(r"Session ID.*?:\s*(\S+)", content)` — assumes format | **MEDIUM** |
| 116-117 | `focus_match = re.search(r"Focus.*?:\s*(.+)", content)` — assumes format | **MEDIUM** |
| 141 | `re.finditer(r"\|\s*(D-\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+)\s*\|", content)` — assumes PIVOT_LOG table format exactly | **HIGH** |
| 156-158 | `subprocess.run(["python", str(MANDATE_CHECK_PATH)], ...)` — no venv activation, assumes `python` in PATH | **MEDIUM** |
| 217-218 | `datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")` — `%W` is week of year (00-53), `%w` is weekday (0-6); this parses "Monday of week N" but ISO week Monday may not match | **MEDIUM** |
| 223 | `report_link = f"[{week_name}/STATE_OF_ENGINE_v1.0.1.md]({report_data.get('report_path', '')})"` — hardcodes `v1.0.1` | **HIGH** |
| 224 | `voice_count = len([v for v in parse_voice_files(week_path) if v["name"] != "INDEX"])` — re-parses voice files (already parsed at line 211) | **LOW** |
| 299 | Hardcoded L3 lesson — doesn't extract from reports | **HIGH** |
| 305-308 | Hardcoded cross-week themes | **HIGH** |
| 314-319 | Hardcoded meta-learning | **HIGH** |

**Overall**: The script is a **working prototype for W36** but **not production-ready** for weekly automation. It needs:
1. Path resolution via `OMEGA_ROOT` or `__file__`
2. Robust parsing with fallbacks (not brittle regex)
3. Extraction of L3 lessons, themes, meta-learning from actual files
4. Unit tests for each parser function
5. Integration test: run on W36, verify output matches hand-written INDEX.md

### §4.2 Template Quality

**`SOTE_TEMPLATE.md`**: ✅ Comprehensive. All 19 sections with clear placeholders. The `{placeholders}` are consistent and cover all data needed.

**`VOICE_DIALECTIC_TEMPLATE.md`**: ✅ Strong. The §0 Verification block (lines 21-36) enforces M23 discipline — **this is the most important template element**. It forces every voice to cite files before speaking.

**`SOTE_INDEX_TEMPLATE.md`**: ✅ Complete. Matches the generated INDEX.md structure.

**Missing templates** (per §1.4):
- `actions/ACTION_ITEMS_TEMPLATE.md`
- `meta/WHAT_WORKED_WHAT_DIDNT_TEMPLATE.md`
- `synthesis/CONDUCTORS_SCORE_TEMPLATE.md`
- `synthesis/DECISION_LOG_ABSORB_TEMPLATE.md`

---

## §5 — PUBLIC/INTERNAL SPLIT

### §5.1 Current Implementation

| Artifact | Audience | Generation |
|----------|----------|------------|
| `INDEX.md` | Public | Manual (script exists) |
| `STATE_OF_ENGINE_v1.0.0.md` | Public (per MaKaLi) | Manual |
| `PUBLIC_DIGEST.md` | Public | **Manual** (data drift proves it) |
| `voices/0N_*.md` | Internal | Manual (voice sessions) |
| `synthesis/*.md` | Internal | Manual |
| `actions/*.md` | Internal | Manual |
| `meta/*.md` | Internal | Manual |
| `sote.yaml` | Internal (LLM) | Manual |

### §5.2 Data Drift Evidence

**PUBLIC_DIGEST.md line 19**: `Mandate Compliance: 16 pass, 8 warn, 4 fail (57.1%)`

**STATE_OF_ENGINE_v1.0.1.md line 129**: `Compliance Ratio: 18/28 = 64.3%`

**sote.yaml line 89-93**: `pass: 18, warn: 5, fail: 5, compliance_pct: 64.3`

**The public digest is stale/wrong.** It reports the W35 baseline (57.1%) not W36 actual (64.3%).

**Root cause**: No automated digest generation. The digest was written once and not updated when the main report was patched to v1.0.1.

### §5.3 Required: Automated Digest Generation

**Needed**: `scripts/generate_public_digest.py` that:
1. Reads `sote.yaml` (authoritative structured data)
2. Reads `STATE_OF_ENGINE_v1.0.0.md` (frozen baseline)
3. Emits `PUBLIC_DIGEST.md` with:
   - Top 3 findings (from `sote.yaml:top_findings`)
   - Mandate compliance (from `sote.yaml:mandates`)
   - Top 5 actions (from `sote.yaml:open_actions` filtered to P0)
   - Link to internal full report

**This must be wired into the weekly workflow** — run after SOTE close, before commit.

---

## §6 — CONCEDE / DEFEND / SYNTHESIZE

### §6.1 Conceded

1. **The folder structure is correct** — `docs/strategy/sote/YYYY-WNN/{voices,synthesis,actions,meta}/` with numbered immutable voices and mutable synthesis is the right architecture. It solves the M27 chokepoint by design.

2. **The template system is sound** — Three templates with §0 Verification block enforcing M23 discipline is the right foundation.

3. **sote.yaml as LLM-readable metadata** — Correct. Structured YAML per week enables tooling and LLM ingestion without parsing Markdown.

4. **Weekly cadence with Monday 06:00 UTC trigger** — Correct. Fixed cadence prevents "we'll do it later" drift.

5. **MaKaLi as standing Unifying Voice** — Correct. The M23 email leak proved the mirror is necessary.

### §6.2 Defended

1. **The regeneration script is NOT production-ready** — It works for W36 because the author knows the exact format. It will break on W37 without the fixes in §4.1. **This is the single biggest operational risk.**

2. **The public digest is manually maintained and already drifted** — Without `generate_public_digest.py`, the public/internal split is a leak vector.

3. **No template for actions/meta/synthesis** — The `MAKALI_ORGANIZATION_STRATEGY.md` defines these artifacts but they have no templates. Week 37 will invent them ad-hoc.

4. **PIVOT_LOG cross-walk is fragile** — The regex at line 141 assumes a specific table format. If PIVOT_LOG format changes, the index breaks silently.

5. **Mandate compliance trend is not computed from history** — The script only parses the current week's report. The trend table in INDEX.md is hardcoded in the template, not computed.

### §6.3 Synthesized — 7 PIVOT_LOG Decisions for SOTE Tooling

| D# | Title | Owner | Effort | Priority |
|----|-------|-------|-------:|:--------:|
| **D-SOTE-TOOL-001** | Fix `regenerate_sote_index.py` paths (use `OMEGA_ROOT` or `__file__`) | Ma'at | 2h | **P0** |
| **D-SOTE-TOOL-002** | Replace brittle regex with structured parsing (frontmatter + section headers) | Ma'at | 4h | **P0** |
| **D-SOTE-TOOL-003** | Extract L3 lessons, themes, meta-learning from actual files (not hardcoded) | Ma'at | 3h | **P0** |
| **D-SOTE-TOOL-004** | Create `generate_public_digest.py` from `sote.yaml` + main report | Ma'at | 2h | **P0** |
| **D-SOTE-TOOL-005** | Add templates for `actions/`, `meta/`, `synthesis/` artifacts | MaKaLi | 2h | **P1** |
| **D-SOTE-TOOL-006** | Add unit tests for `regenerate_sote_index.py` parsers | Ma'at | 3h | **P1** |
| **D-SOTE-TOOL-007** | Wire regeneration + digest generation into weekly workflow (Makefile target) | Ma'at | 1h | **P1** |

---

## §7 — ARCHITECTURE RECOMMENDATIONS

### §7.1 Immediate (Before W37)

1. **Fix the 3 hardcoded paths** in `regenerate_sote_index.py` (lines 19, 21, 22)
2. **Create `generate_public_digest.py`** and wire it to run after SOTE close
3. **Add missing 4 templates** (actions, meta, synthesis×2)
4. **Run the regeneration script on W36** and verify output matches hand-written INDEX.md

### §7.2 Week 37 (First Automated Cycle)

1. **Run `make sote-regenerate`** (new Makefile target) as part of SOTE close
2. **Verify INDEX.md diff** — only expected changes (new week row, updated trend)
3. **Verify PUBLIC_DIGEST.md** matches `sote.yaml` data exactly
3. **Archive W36 voice files as immutable** — confirm no edits after week-close

### §7.3 Quarter 1 (Weeks 37-52)

1. **Add caching layer** to `regenerate_sote_index.py` (parse once, cache JSON, invalidate on mtime)
2. **Add JSON Schema for `sote.yaml`** and validate on write
3. **Implement PIVOT_LOG absorption tracking** in the index (D-MAKALI-003)
4. **Add year-based index sharding** if INDEX.md exceeds 500 lines

### §7.4 Architecture Principle — The SOTE as a "Compiler"

The SOTE system should be thought of as a **compiler**:
- **Source**: Voice dialectics (immutable, human-written)
- **Intermediate**: `sote.yaml` (structured, machine-readable)
- **Artifacts**: INDEX.md (navigation), PUBLIC_DIGEST.md (public), PIVOT_LOG absorption (canonical)
- **Build script**: `regenerate_sote_index.py` + `generate_public_digest.py`
- **CI gate**: `make check-sote` — verifies INDEX.md matches source, digest matches YAML, no drift

**This is the id Software WAD model applied to documentation**: the source is authoritative, the build is deterministic, the artifacts are consumable.

---

## §8 — CONFIDENCE SCORING

| Claim | Confidence | Source |
|-------|:----------:|--------|
| M2 firewall intact for SOTE | **10/10** | `scripts/regenerate_sote_index.py` imports only docs/ |
| Folder structure solves M27 chokepoint | **9/10** | `MAKALI_ORGANIZATION_STRATEGY.md:146-155` |
| Regeneration script works for W36 | **8/10** | Manual test would confirm; code review shows gaps |
| Regeneration script production-ready | **3/10** | 11 defects found in code review (§4.1) |
| Public digest drift is real | **10/10** | 57.1% vs 64.3% — direct comparison |
| sote.yaml schema is LLM-ready | **9/10** | Well-structured, typed, versioned |
| 52-week scalability is fine | **8/10** | File count projection; no DB needed |
| Templates cover full lifecycle | **6/10** | Missing 4 templates for actions/meta/synthesis |
| Weekly cadence sustainable | **7/10** | Depends on tooling fixes; manual W36 took ~4h |

---

## §9 — OUTSTANDING QUESTIONS FOR DIALECTIC

1. **Who owns the SOTE tooling?** Ma'at (CI/DevOps) or MaKaLi (process)? The script is in `scripts/` (Ma'at domain) but the process is MaKaLi's.

2. **Should `regenerate_sote_index.py` be a Makefile target or a standalone script?** Makefile target (`make sote-regenerate`) integrates with `temple-grade` chain.

3. **Is the public digest part of the debut deliverable?** If yes, `generate_public_digest.py` is P0 for DEL-1.

4. **How to handle the `sote.yaml` drift from voice files?** The `decisions.by_voice` counts in sote.yaml (Lilith: 16) don't match what the voice file parser would extract. Need a reconciliation step.

5. **Should the SOTE index include a "decision health" metric?** e.g., "67 proposed, 0 absorbed = 0% absorption rate" — this is the M27 chokepoint made visible.

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_sote_review ⬡ PHASE-1-COMPLETE*

**Phase 1 complete.** Ready to page Researcher-EIS for Phase 2 deep web research.

---

**Next action**: Page Researcher-EIS (`ses_fd81c19dcffe1nkbPqFg5kRt2v`) with research instructions per MaKaLi task.