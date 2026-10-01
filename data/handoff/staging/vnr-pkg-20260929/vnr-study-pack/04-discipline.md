<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 04 — Instrument Discipline

## Validate on fixtures first

Before trusting any reading on a live frame, run the instrument against
frames whose truth you know. Collect labelled examples per class, compute
every statistic per class, print the distributions side by side, and look for
separation. Where distributions overlap, the instrument is not your
discriminator for that signal — that is a legitimate outcome, and it exists to
stop you forcing a weak instrument into service. Thresholds are set from data,
then recorded alongside the measurements that justified them.

A parallel bypass is worth building: one check that deliberately reads the raw
source and skips the entire analysis pipeline. It is the one link that cannot
inherit the pipeline's bug twice. When the pipeline and the bypass agree,
trust the reading. When they disagree, suspect the pipeline.

## Module discipline

Modules **return data**; only the CLI prints. This is what makes the package
callable from inside a benchmark loop without capturing stdout, and what
makes it unit-testable. Honour it in any integration: analysis functions take
arrays and return values, and rendering to text happens at the boundary.

## Parity harness

A frozen copy of the previous renderer version is kept alongside the package,
and a parity harness asserts byte-identical output on a fixture set after
every change. Any modification that silently shifts semantics fails the
harness. If you fork the package, keep the harness — it is the proof that a
refactor changed structure without changing meaning.

## Scope discipline

Small crops are sound; whole-frame search is the known failure mode.
`--find` (exact-RGB bbox) on a full frame is unreliable — prefer `--crop`
then `--find`. The same principle generalises: narrow the region with a
cheap signal (change bbox, expected region from a sidecar) before spending
an expensive classifier on it.

## Tracking caveat

Centroid trackers (`track.py`) follow a colour centroid. On any frame where
the background shares that colour, the tracker latches onto the wrong thing
and reports it confidently. Never trust a track without an independent check
— change-differential or geometry — confirming the tracked point moved with
the object rather than with the scenery.
