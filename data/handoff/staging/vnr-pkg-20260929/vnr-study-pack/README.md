<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# VNR Study Pack

**For:** GE-N1 (Gaming-Expert-N1)
**What:** VNR 2.0 — a deterministic image-to-text vision system. Converts
framebuffers into grids of characters you can read, diff, count, and reason
about. No weights, no network, no hallucination.
**Source:** `scripts/vnr/` — 854 lines, 7 modules. Dependencies: numpy, Pillow.
Nothing else.

## Files

| # | File | Contents |
|---|---|---|
| 0 | `README.md` | this index, quick start |
| 1 | `01-law.md` | the Law of Ascending Signals + corollaries |
| 2 | `02-signals.md` | token taxonomies + structure classifier + full `signals.py` |
| 3 | `03-change.md` | change maps, A/B oracle, verdicts + full `differential.py` |
| 4 | `04-discipline.md` | instrument validation, thresholds-from-data, code discipline |
| 5 | `05-two-tier.md` | pairing VNR with a VL model: the gate pattern, JSON schema, server wiring |

## Quick start

```bash
# frame -> text grid
python3 -m scripts.vnr.cli shot.png --mode structure --block 16

# how much changed between two frames, and where
python3 -m scripts.vnr.cli a.png --diff b.png --block 8

# coarse layout + dominant colours
python3 -m scripts.vnr.cli shot.png --gist
```

The package is self-contained. Copy `scripts/vnr/` and add numpy + Pillow.
It imports nothing from the project it was built in. The 28 unit tests in
`tests/vnr/` travel with it — run them after any modification.

## The one-paragraph version

Locate and verify via change first, geometry second, texture statistics third,
colour last and never alone. Difference paired frames to isolate what moved.
Classify surfaces by structure (flat / dither / edge / gradient / noise),
not by colour. Emit three-valued verdicts — present, absent, unknown — never
invent confidence. Validate the instrument on fixtures whose truth you know
before trusting any reading. Put this deterministic layer in front of any VL
model: let counters answer counting questions, and spend the expensive
semantic call only on what survives the cheap gate.
