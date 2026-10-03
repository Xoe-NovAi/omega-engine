<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ADR-005: Node-Suffix Identity

**Status:** Accepted — 2026-10-02 · Handoff store identity resolution

## Context
The entity `lilith` existed on both Node 0 and Node 1. The handoff store
folded `lilith-n1` → `lilith` and reported `resolved: true`, silently merging
two distinct agents into one identity. Packets intended for one node were
indistinguishable from packets for the other — an identity collision with
integrity consequences.

## Decision
A `-n<N>` suffix (matched by regex `-n\d+$`) is a **DISTINGUISHING token**,
never an alias. Name resolution must never fold a node suffix away; if a suffix
is present and does not match a known node, resolution **REFUSES** rather than
guessing. Bare names resolve only when they are unambiguous.

## Consequences
- Node identity travels **inside the name** — no side table required, visible
  in every log line, grep, and message body.
- `lilith` and `lilith-n1` are permanently distinct addresses; no silent
  cross-delivery.
- Cost: suffix discipline on every sender — forgetting `-n1` when addressing a
  remote node yields "not found", not silent misdelivery (fail-closed by
  design).
- Unmatched suffix is a hard error, which must be surfaced, not swallowed.

## Alternatives Considered
- **Fold/alias table** (the prior behaviour): convenient, but it is exactly
  what produced the collision — `resolved: true` for a name that had changed
  meaning.
- **Opaque UUIDs**: unambiguous, but not human-readable; identity would be
  invisible in transcripts and greps.
- **Separate namespace per node**: clean, but the namespace does not travel
  with the name when packets, logs, or messages cross node boundaries.