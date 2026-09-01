<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SOTE Master Index

**AP Token**: `AP-SOTE-INDEX-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ {session_model} ⬡ opencode ⬡ trc_sote_index ⬡ ACTIVE

**Date**: YYYY-MM-DD
**Cadence**: Weekly (D-SOTE-001)
**SOTEs to date**: N
**Regeneration**: {Manual|Auto} (script: `scripts/regenerate_sote_index.py`)

---

## All SOTEs

| Week | Date | Title | Main Report | Voices | Status | Top Finding |
|------|------|-------|-------------|--------|:------:|-------------|
| YYYY-WNN | YYYY-MM-DD | {title} | [link](YYYY-WNN/STATE_OF_ENGINE_vN.N.N.md) | N | {status} | {finding} |

---

## Voice Index (YYYY-WNN)

| # | Voice | Session ID | File | Focus |
|---|-------|------------|------|-------|
| 1 | {Voice} | {session_id} | [01_VOICE.md](YYYY-WNN/voices/01_VOICE.md) | {focus} |
| 2 | {Voice} | {session_id} | [02_VOICE.md](YYYY-WNN/voices/02_VOICE.md) | {focus} |
| ... | ... | ... | ... | ... |

---

## Decision Index (PIVOT_LOG)

**Status**: {N} decisions proposed across {N} voices, **{M} absorbed into PIVOT_LOG.md as of YYYY-MM-DD**.

| D# | Date | Title | Source Voice | Status |
|----|------|-------|--------------|:------:|
| D-{VOICE}-{NNN} | YYYY-MM-DD | {title} | {Voice} | {status} |

---

## Mandate Compliance Trend

| Week | Pass | Warn | Fail | % | Notes |
|------|------|------|------|--:|-------|
| YYYY-WNN | {pass} | {warn} | {fail} | {pct}% | {notes} |

---

## L3 Lessons (This Cycle)

| L# | Title | Confidence | Source |
|----|-------|:----------:|--------|
| L3-{NAME} | {title} | {conf} | {source} |

---

## Cross-Week Themes

- **{Theme}**: {description}
- **{Theme}**: {description}

---

## Meta-Learning

**What worked**: {items}
**What didn't**: {items}

**Full meta**: [YYYY-WNN/meta/WHAT_WORKED_WHAT_DIDNT.md](YYYY-WNN/meta/WHAT_WORKED_WHAT_DIDNT.md)

---

## Next SOTE: YYYY-W{N+1} (YYYY-MM-DD)

**Trigger**: Monday YYYY-MM-DD, 06:00 UTC
**Likely topic**: {topic}
**Owner**: Kali (Oversoul) or designated delegate
**Hivemind broadcast**: `intent=sote-open` at trigger

---

## Regeneration Notes

This index is regenerated {Manually|Automatically} for W{NN}. Future weeks will use `scripts/regenerate_sote_index.py` (pending, ~200 lines, one-time build). The script will:
1. Scan `docs/strategy/sote/YYYY-WNN/` for week folders
2. Parse each week's `STATE_OF_ENGINE_v*.md` for top finding
3. Parse each voice file for PIVOT_LOG decision IDs
4. Cross-walk to `docs/decisions/PIVOT_LOG.md` for absorption status
5. Compute mandate compliance trend from `scripts/check_mandate_compliance.py`
6. Emit updated `INDEX.md`

---

*⬡ OMEGA ⬡ KALI ⬡ SOTE-INDEX-v1.0.0 ⬡ YYYY-MM-DD*

*The SOTE is a practice. The index is its memory. The meta-learning is its evolution.*