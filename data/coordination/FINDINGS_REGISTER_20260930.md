<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ⬡ FINDINGS REGISTER — 2026-09-30
**Purpose**: every unverified claim, disputed finding, and empirical resolution
from the stabilization session. Written so a fresh head does not re-derive them.
**Rule applied throughout**: a claim is settled only when executed, never when
inferred from reading or from a brief.

---

## 1. THE M36 ISOLATION — disputed, then resolved empirically

**Roc's static claim (call-graph trace):**
> `state.py:490-494` derives `HANDOFF_PENDING/ACTIVE/COMPLETED/STALE/ARCHIVE`
> **at import time**. `tools.py:64` imports them **by value**. M36 re-roots only
> `HANDOFF_BASE`. Therefore "the M36 re-root does not isolate the live queue at
> all for submit/accept/complete/reject/list" and "the isolation is cosmetic on
> the write path."

**Empirical resolution:**
```
data/handoff/m36-test/pending/   20 packets
data/handoff/pending/ CROSS-VALIDATOR   0 packets
```

**Why Roc was wrong, precisely:** the submit path (`tools.py:1320`) does *not*
use the by-value constant — it calls `_federation_store()`, which does
`from .. import state as _state; return FederationStore(_state.HANDOFF_BASE)`,
a **module-attribute read at call time** that follows the re-root. The by-value
constants appear at `tools.py:1516, 1570, 1617`, which belong to
**accept/complete/reject** — paths M36 never calls.

**VERDICT: the faucet is closed for the path M36 uses.**

**RESIDUAL, real but latent:** if M36 ever calls accept/complete/reject, or if
any new code reaches for `HANDOFF_PENDING` by name, it will hit the live queue
while a re-root is in effect. The by-value imports are a footgun that reads as
correct. **Not fixed. Documented here instead.**

---

## 2. THE `HANDOFF_BASE` DIALECTIC — resolved by trace, not by argument

Two opposed briefs were commissioned (Doom Guy for, Carmack against). Both
converged on the same empirical question and **neither could answer it by
reading**. Rather than synthesise a decision from two opinions, the trace was run.

**Roc's verdict: `RACE NOT REACHABLE TODAY`, with one seam.**
- M36 is reached from `m33_probe.py:566-567` (`M33Probe.final_accepted`, sync).
- The Hub binds the class at `hub_tools/m33_probe.py:40` via
  `spec_from_file_location`, but **none of its 6 registered tools reach line 566**.
- The Hub does load `src/omega/oracle/` broadly (`state.py:36-41`, `server.py:109`,
  `tools.py:152,281`, `gateway.py:49`) — the earlier `grep -rn m36 mcp_servers/`
  returned empty only because M36 is reached by **class name**, not the string
  "m36".
- **UNTRACED SEAM:** `server.py:523` imports `CAPABILITY_REGISTRY` from
  `subagent_dispatcher`, the documented M33 caller path. Its internals were not
  traced inside the box. **This is the one open question on the dialectic.**

**Carmack's own position, on the record:** he proposed the motion and then argued
against acting on it *this week* — "correct architecture, wrong target, and the
cheap alternative is not yet proven insufficient." He cited the quarter's pattern:
two days on a phantom outage that was a security decision, two months on a
rendering bug that was a missing asset.

**Doom Guy's refinement worth keeping:** thread the root *below* the MCP
boundary so the global is never mutated, making the `finally` block (added in
`626507ac`) deletable. The race disappears at the source rather than being
defended against.

**STATUS: unresolved, correctly. Awaiting the `subagent_dispatcher` trace.**

---

## 3. TWO "CANNOT VERIFY" REPORTS THAT WERE WRONG

Both from Lilith during sprint reconciliation, both resolved in the opposite
direction on direct check.

| Agent's claim | Truth | Why the agent was wrong |
|---|---|---|
| "Three superseded policy variants not verifiable; grepping for a superseded marker found nothing" | **Markers present** — 2 `SUPERSEDED` hits in each 09-26 file, 1 `AUTHORITATIVE` in v2 | Grep scope, not absence |
| "`artifact_ids` strict-args fix is not greppable; cannot confirm in working tree" | **Present** at `server.py:201-204` (`model_config["extra"] = "forbid"`, `model_rebuild(force=True)`) | The fix is **general** across all 54 tools, so grepping for the *parameter name* finds nothing. The fix is correctly not artifact-specific. |

**This is the fourth instance today** of the same pattern: an agent reported
absence where the thing was present, and the reporting method was the error.
Earlier three: a truncated tool list read as a total, a stale generated registry
read as a roster, and a policy file called stale when it was correct.

**The pattern is now: *the check is more likely wrong than the claim*.** Every
future verification should ask *"what would make this check miss it?"* first.

---

## 4. THE BACKGROUND FEATURE — settled, and the cause is mine

`OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true` is in `~/.bashrc` **and** `.env`
(both verified to resolve; deliberately **not** in `opencode.json`, which has
`additionalProperties: false` and would risk the provider/MCP config).

**It does not work for me, and it is not a product problem.** The tool-call
serialisation emits my boolean as a JSON **string**:
```
background: true   -> SchemaError: Expected boolean | undefined, got "true"
background: false  -> SchemaError: Expected boolean | undefined, got "false"
```
Both values fail identically, so it is stringification, not a value problem.
Two attempts made, then stopped rather than guess at a serialisation boundary.

**DB proof it never engaged:** across all 15 `task` calls this session,
`metadata.background = NULL` and `metadata.jobId = NULL`.

**The canary cost 3 seconds instead of 38 minutes.** That is the entire argument
for the 3-minute time box, and it is now policy.

---

## 5. OPEN ITEMS, RANKED

1. **`subagent_dispatcher` trace** — the one seam that decides the `HANDOFF_BASE`
   dialectic. Half an hour. Everything else waits on it.
2. **Alias suffix-strip policy** — Architect's call. Carmack's case (cut it,
   fix senders) is in the brutal review; the counter-case is that it is load-bearing
   today because senders are non-compliant.
3. **Retroactive merge of the 10 alias forks** — blocked on 2.
4. **Per-entity liveness semantics** — "resolves" ≠ "reachable" for a chat-session
   peer is undefined.
5. **By-value `HANDOFF_*` imports in `tools.py:64`** — latent footgun, §1.
6. **M9 gate**: fixed to AST in `49952015`. Residual — the gate is scoped to bare
   `except:` only; typed-handler discipline has no gate.
7. **N0 install as first outside user** — the largest untouched item.

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ FINDINGS-REGISTER ⬡ 2026-09-30 ⬡*