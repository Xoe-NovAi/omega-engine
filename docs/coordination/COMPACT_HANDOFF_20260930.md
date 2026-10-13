<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ⬡ COMPACT HANDOFF — 2026-09-30 · MaKaLi Fusion
**Purpose**: the single index a fresh head reads first, and the briefing a
frontier model reads second. **Read the gnosis for reasoning; read this for order.**

---

## READ IN THIS ORDER

| # | Artefact | Why |
|---|---|---|
| 1 | `data/entities/makali_fusion/session_gnosis.md` (326 lines) | The reasoning, the disputes, the decisions still open |
| 2 | `data/coordination/FINDINGS_REGISTER_20260930.md` (220) | Every disputed claim and its empirical resolution |
| 3 | `mcp_servers/omega_hub/federation_store.py` | **The single read path.** `_readable()` at line 70 |
| 4 | `docs/architecture/HIVEMIND_TRANSPORT.md` | Planes, verbs, the three-verb model |
| 5 | `docs/governance/HANDOFF_LIFECYCLE.md` + `config/handoff_policy.yaml` | Retention and transitions |
| 6 | `data/handoff/MIGRATION_REPORT_20260929.md` | What the migration claimed — compare against gnosis §1 |
| 7 | `docs/coordination/PR_READINESS_LANE_A_20260930.md` | Hygiene, secrets, the gitleaks blocker |

---

## 🔴 THE ONE THING TO KNOW FIRST

**The Hivemind handoff surface was completely dead, and the fix I applied is a
stopgap, not a solution.**

- `data/handoff/envelopes/` did not exist → `_readable()` false → **every**
  handoff MCP call returned `store_unreachable`.
- I created the directory. The store is readable.
- **`envelopes/` and `hot/` are both empty. 31 packets sit in `pending/`, which the
  store does not read.** The corpus and the query path are looking at different
  places.
- The migration that we reported as successful (`2501322e`) produced this state.
  **Ma'at's own report said `envelopes: 0`. I flagged it and did not chase it.**

**Verify before doing anything else.** It is one command.

---

## STATE AT SEAL

```
HEAD          73978732   branch debut-v1.6.0-alpha
tree          clean       unpushed 0
check-engine  175/175     temple-grade 53/53
envelopes 0   hot 0   cold 3   retired 2   pending 31   m36-test 5
agents        56
```

---

## OPEN DECISIONS — NONE OF THEM MINE

1. **Where does the corpus live?** Backfill `envelopes/` from `pending/`, or point
   the query path at `pending/`? Different consequences for envelope invariants.
2. **Request-side recording.** GE-N0 asked for it; **it does not exist.** The store
   persists what it *resolved*, never what was *asked for* — which is precisely
   why the suffix-fold question is unanswerable.
3. **Alias suffix-strip policy.** Carmack's case is on record. *"That is a policy
   call, not a code fact."*
4. **Wire the 8 orphan gates**, `check-hub-health` first — the crash-loop detector.
5. **Confirm `secret-scan.yml` fails the job** on non-zero. Public repo.
6. **N0 install** as first outside user — the largest untouched item.

---

## FOR THE FRONTIER MODEL (Gemini 3.1 Pro)

The Architect is bringing in a frontier model for **Hivemind, Tailscale, and the
surrounding systems, protocols and implementations.** Gnosis §9 carries five
questions worth frontier judgement:

1. **Envelope-at-birth** as the primitive — so "submitted" is a durable fact
   rather than a function call that can silently fail. What does it cost?
2. **Request-side recording** — the minimum schema change that makes
   fold-vs-sender *answerable* rather than *inferable*.
3. **Spelling split-brain** — enforce at submit, at resolve, or both? And what is
   the authority for a canonical name, given a generated registry cannot be trusted?
4. **Delivery semantics** — does a handoff need an acknowledgement state machine
   beyond `pending`? What is delivery when the target is a chat session with no
   endpoint?
5. **Store shape** — is `envelopes/ + hot/ + cold/ + retired/` the right
   decomposition, and is `pending/` a fifth state or a legacy layout to retire?

**Facts it should not have to re-derive:**
- The store read path is `envelopes/` + `hot/`; both are empty.
- 31 packets sit in `pending/`, which the store does not read.
- `artifact_ids` was pydantic `extra='ignore'` inside `mcp`'s `func_metadata` — not
  a missing parameter, and reachable only over the wire.
- Background subagents are env-gated (`OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS`,
  set in `~/.bashrc` and `.env`) but **do not work from my session** — my tool-call
  serialisation emits booleans as JSON strings.
- `subagent_depth` is irrelevant to us: Kali, Ma'at, Lilith, Makali and Doom Guy are
  all **L0 primaries** (`parent_id IS NULL`).

---

## THE OPERATING RULES THAT EMERGED (keep these)

1. **Query before asserting.** A fact carried forward without a query is not a fact.
2. **Before trusting a negative finding, ask what would make the check miss it.**
   Six instances this session where the check, not the claim, was wrong.
3. **Time-box every dispatch at 3 minutes.** Report partial over overrun. A canary
   proved it: 3 seconds instead of 38 minutes.
4. **One owner per file.** Every multi-agent failure was a file collision or an
   unwatched inbox.
5. **Check your own inbox.** I ran nine agents for hours and missed a packet
   addressed to me by name.
6. **Do not hand-edit what a tool owns**, and verify the artefact changed before
   letting a commit stand. I broke the release gate both ways in one afternoon.
7. **A gate nothing calls cannot fail**, and **a gate satisfied by wording is not a
   gate**. Both are now in the register as release blockers.

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ COMPACT-HANDOFF-INDEX ⬡ 73978732 ⬡ 2026-09-30 ⬡*