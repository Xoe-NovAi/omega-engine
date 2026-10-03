<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 01 — The Law of Ascending Signals

## The law

> **Locate and verify via (1) change, (2) geometry, (3) texture statistics.
> Colour LAST, never sole evidence.**

Every analysis starts at the top of the ladder and descends only as far as
needed. If change answers the question, stop. If geometry answers it, stop.
Colour is the weakest signal and is never authoritative on its own.

## Corollaries

**Colour is never sole evidence.** Palettes are shared. A sprite's colours are
a subset of the scene's colours; an exact colour match proves nothing without
position, motion, or structure behind it. Any verdict resting on colour alone
is void.

**Achromatic surfaces are first-class.** True neutrals (low saturation, high
luminance) are the dominant signature of manufactured things — UI chrome,
cards, paper, plastic, painted surfaces. A chroma gate separates them from
tinted backgrounds of equal brightness. Nature keys on hue; machinery keys on
neutral chroma plus hard geometry.

**Validate the eye before the reading.** Render a known-good fixture first. If
the instrument cannot see a thing you placed deliberately, its verdicts on
things you did not place are void.

**Verify the shared artifact.** When two observers disagree, confirm both read
the same final composited frame — same buffer, same render pass, same frame —
before concluding anything about perception. Most "perception gaps" are two
parties correctly describing two different inputs.

**Surplus means occlusion; deficit means absence.** When the measured content
of an expected region *exceeds* what should be there, something is painted
over it. When it falls short, the thing is missing. Read the sign of the
error, not just its magnitude.

**Thresholds come from measured distributions, not intuition.** Collect frames
whose ground truth you know, compute each statistic per class, print the
distributions side by side, and set thresholds where the data separates. If
the distributions overlap, the instrument is not your discriminator for that
signal. Say so.

**Verdicts are three-valued.** Present, absent, unknown. "I don't know" is a
first-class outcome. A classifier that cannot say it is uncertain will invent
confidence it does not have.
