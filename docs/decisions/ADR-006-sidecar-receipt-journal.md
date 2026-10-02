<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ADR-006: Sidecar Receipt Journal

**Status:** Accepted — 2026-10-02 · Handoff read-state subsystem

## Context
Inspection found **0 of 10 packets had `read_by`** — read and unread packets
were identical, so "has anyone seen this?" was unanswerable. The obvious fix,
mutating the envelope in place to add receipts, **crashed on legacy packets**
whose schema lacked the field — and any mutation risks the same class of
failure on every historical format.

## Decision
Record read state in an **append-only sidecar**: one `{packet_id}.receipts.jsonl`
file per packet, one JSON line per receipt, **fsync per receipt**. The envelope
file itself is **never mutated** after creation.

## Consequences
- **M28-clean pure addition**: receipts add files; nothing existing is altered
  or destroyed, so the audit trail only ever grows.
- Legacy packets gain read-state without a migration — the sidecar is
  independent of envelope schema.
- Reads are distinguishable from unreads for the first time (reading remains
  distinct from accepting: a receipt records *looked*, not *decided*).
- Cost: a second file per packet, and readers must join envelope + sidecar.

## Alternatives Considered
- **Mutate envelope in place**: the observed crash on legacy packets; also
  destroys the original submitted body as evidence.
- **Separate receipts database**: re-introduces the single-hot-file coupling
  rejected in ADR-003, and makes receipts harder to audit than a plain
  append-only file.
- **Leave read state implicit** (status quo): 0/10 `read_by` proves implicit
  state is indistinguishable from no state.