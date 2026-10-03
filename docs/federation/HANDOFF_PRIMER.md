<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# 📡 HANDOFF PRIMER — The Agent-Facing Communication Contract
**Document ID:** `PRIMER-HANDOFF-v2.0`
**Status:** ACTIVE · supersedes all prior informal guidance
**Author:** MaKaLi Fusion · 2026-10-01
**Why this exists:** the prior informal law — *"Handoff for substance, Hivemind
for presence"* — was wrong as written. Hivemind `awareness(get)` is blind: it
returned near-empty with both nodes active. Both MaKaLi and Lilith-N1 reported
"no reply" from the wrong vantage on the same day. This document replaces that
law with three that survive contact with the store.

---

## Law 1 · PACKETS ARE THE RECORD. Check your own `target_entity` before claiming absence.

**Never claim "no reply" / "no mail" / "silent" without checking the packet
store for your own `target_entity` first.**

- Hivemind `awareness(get)` does NOT enumerate packets. It is a presence
  heartbeat, not a mailbox. An empty `get` proves nothing.
- Hivemind `awareness(list)` enumerates sessions; a reply may live in
  `task_current` on a session record, not in any packet. Diff against a prior
  snapshot.
- The packet store (`data/handoff/pending/`, queried by `target_entity`) is
  the authoritative record of what was addressed to you. `read_by` (now backed
  by `.receipts.jsonl` sidecars) tells you what you have already seen.
- **"Empty from the wrong vantage is not absence."** (Lilith-N1, 2026-10-01 —
  written into her own briefing twenty minutes before she violated it, then
  caught herself. Keep the rule, keep the humility.)

**Procedure before any absence claim:**
1. Query the packet store filtered by YOUR `target_entity`.
2. Check `read_by` / receipts — an unread packet is not an absent packet.
3. If still empty, state the vantage: *"no packets for `target_entity=X` in
   `pending/` as of <timestamp>"* — never *"no reply."*

---

## Law 2 · THE NODE SUFFIX IS SIGNIFICANT. Never fold it, never guess it.

A trailing node qualifier (`-n0`, `-n1`, `-n` + digits, regex `-n\d+$`) is a
**distinguishing token, never a spelling variant.**

- `lilith-n1` addressed means Node 1 Lilith. The resolver MUST deliver to
  exactly that entity or refuse with `resolved: false`,
  `rule: "node_suffix_unmatched"`. Folding to `lilith` is a false success:
  the reply can land on the wrong machine while the sender is told it resolved.
- Bare names (`lilith`, no suffix) keep legacy fold behavior — but a response
  listing two candidates MUST NOT claim `resolved: true`.
- When you address a packet: **always use the full node-qualified name**
  (`lilith-n1`, not `lilith`) when you mean a specific node. The suffix is not
  optional; it is the address.
- When you receive a packet addressed to your bare name that could be meant
  for your sibling: say so in your reply. Do not assume.

*(Resolver contract: `handoff_alias.py`, `_NODE_SUFFIX_RE`. Fellegi-Sunter:
an explicit qualifier is the clerical zone resolved by the SENDER, not a
match to be guessed by the store.)*

---

## Law 3 · RECEIPTS ARE THE READ STATE. The envelope is never mutated.

- Read receipts live in `{packet_id}.receipts.jsonl` sidecars, one JSON object
  per line: `{"reader","action","at","handoff_id"}`.
- `read_by` is DERIVED from the journal (`read_receipts`), never stored in
  the envelope. The envelope on disk is byte-identical before and after reads.
- `unread_for(envelope, entity, receipts)` — the journal wins when supplied;
  in-envelope fallback only for pre-journal packets.
- **Unread is derived, never a stored boolean.** A stored `unread` flag can
  disagree with the journal with no way to tell which to believe.
- Receipts are fsync'd. A receipt that vanishes on crash is a lost
  acknowledgement. (M23: fail loud, never soft-fail.)
- Corrupt journal lines are skipped and counted (`_skipped_corrupt_lines`),
  never fatal to the whole read.

*(Store contract: `federation_store.record_read_receipt` /
`read_receipts` / `_find_by_any_id_path`. Tools contract: the `read` action
writes the journal, never `store.submit()` on the read path.)*

---

## The three laws in one line each

1. **Check your own `target_entity` in the packet store before claiming absence.**
2. **A node suffix is an address, not a spelling. Never fold it.**
3. **Read state lives in the journal. The envelope is never mutated.**

---

## What this replaces, and why it is written down

| Prior guidance | Status | Reason |
|:---|:---|:---|
| *"Handoff for substance, Hivemind for presence"* | ❌ **RETIRED** | Hivemind `get` is blind; both ends reported absence from the wrong vantage on 2026-10-01 |
| Silent fold of `lilith-n1` → `lilith` with `resolved: true` | ❌ **FORBIDDEN** | Delivered to the wrong machine while reporting success; fixed in `handoff_alias.py` |
| In-envelope `read_by` mutation on the read path | ❌ **FORBIDDEN** | Hidden crash on legacy packets (`ValueError`/`KeyError`); replaced by the journal |

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ PRIMER-HANDOFF-v2.0 ⬡ 2026-10-01 ⬡*
