<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 📋 DOCS ACCURACY AUDIT — 2026-10-03

**AP Token**: `AP-DOCS-ACCURACY-AUDIT-20261003-v1.0.0`
**Entity**: maat (Slot S5, Build-Side Governance Keeper)
**Scope**: tool counts · MCP protocol-version honesty · mandate IDs · A2A honesty ·
harvester doc↔impl parity · version strings
**Mandates**: M23 (no synthesis — unverifiable claims marked UNVERIFIED),
M28 (history annotated, never rewritten), M2 (Law not edited unilaterally)

---

## Method

Every claim below was checked against a **live source**, not against another
doc. Tool counts came from an MCP `tools/list` against the running hub on
8016; protocol versions from `mcp.shared.version` in the installed SDK; mandate
IDs from the section headings in `SOVEREIGN_MANDATES.md`; harvester behaviour
from reading `scripts/hivemind_harvest.py` and executing it. Where a doc and
the code disagreed, the **code won** and the doc was corrected.

**Verdicts**: ✅ CORRECT · ❌ INACCURATE (fixed) · ⚠️ DIVERGENT/HISTORICAL
(annotated) · 🚩 REPORTED, NOT FIXED (needs authority)

---

## Audit table

| # | Claim | Source | Verdict | Correction |
|:-:|:---|:---|:---:|:---|
| 1 | "OpenCode shows fewer than **54** tools"; "Should be 54+" | `docs/guides/how-to-debug-hub.md:71,77` | ❌ | Live `tools/list` returns **55**. Updated to 55 with verification date |
| 2 | "54 tools exposed including…" | `docs/team/FEDERATION_EXPERIENCE_REPORT_20260928.md:8,18` | ⚠️ | True on 2026-09-28; stale now. Dated supersession banner added; body left verbatim (M28) |
| 3 | "54 tools total" | `docs/team/HANDOFF_DELIVERY_REPORT_20260928.md:82` | ⚠️ | Same — dated banner added, body untouched |
| 4 | Hub "already implements the **MCP 2026-07-28 stateless core**" | `docs/research/KNOWLEDGE_GAPS_20261003.md:39` | ❌ | **Overclaim.** Rewritten with an explicit SENDS / ACCEPTS / NOT-COMPLIANT table |
| 5 | "`mcp_client.py` — ✅ MCP 2026-07-28 stateless (SEP-2575)" | `docs/research/KNOWLEDGE_GAPS_20261003.md:147` | ❌ | **Overclaim.** Replaced with a per-file spec-version audit |
| 6 | "hub client is on `2026-07-28` stateless" (exec summary) | `docs/research/KNOWLEDGE_GAPS_20261003.md:19` | ❌ | Overclaim **and** stale (closed by `de866948`). Row → ✅ CLOSED with the ceiling stated |
| 7 | "Align the probe to the current protocol version" | `docs/research/KNOWLEDGE_GAPS_20261003.md:43` | ❌ | **Would have broken the probe.** The SDK answers a 2026-07-28 transport header with HTTP 400 / `-32600`. Replaced with what was actually done and why |
| 8 | Any MCP protocol-version claim | `docs/architecture/CONTROL_PLANE_20261003.md` | ✅ | **No protocol claim present** (0 mentions). Nothing to correct |
| 9 | "A2A-informed, NOT A2A-compliant" | `docs/architecture/A2A_AGENT_CARDS_20261003.md:13,24,288` | ✅ | **Already honest.** Status line, body note, and the §5 verdict ("17 of 17 unmet") all agree. No change |
| 10 | 13 mandate IDs (M1,2,6,7,8,9,10,11,13,15,23,24,28) | `docs/governance/CONSTRAINTS.md:31-43` | ✅ | **All 13 resolve** to real mandates (§1,2,6,7,8,9,10,11,13,15,23,24,28); each description matches its mandate. No phantom IDs |
| 11 | §28/29/30 carry inline IDs `(M29)`/`(M30)`/`(M35)` | `SOVEREIGN_MANDATES.md:249,263,277` | 🚩 | **Law-internal inconsistency.** See "Finding A" below. Reported, not edited |
| 12 | "N = 300 s, with ±30 s jitter" | `HIVEMIND_HARVESTER_DESIGN_20261003.md` §3.1 | ⚠️ | **Divergence.** 300 s implemented; jitter is **not**. Implementation-status note added |
| 13 | "Sleep 300s (with small ±15 s deterministic jitter if desired)" | `mcp_servers/omega_hub/background.py:350` | 🚩 | Misleading comment: no jitter exists, and ±15 s disagrees with the doc's ±30 s. Comment-only; reported for a follow-up commit |
| 14 | digest cap 280 chars | Design §2.3 · Impl guide:102,112 | ✅ | **Correctly scoped** — it is a *post-side* ("server-side") cap on `hivemind_awareness`, explicitly "Enforcement (proposed)". §2.2's `DOING ≤120 / NEXT ≤100` template matches the code's truncation exactly. Not a divergence |
| 15 | retention 288 · `LOCK_NB` lock · interval 300 s · radar fields · EIS/NES partition | Impl guide vs `hivemind_harvest.py` | ✅ | **Full parity.** 288 (`:332`), `fcntl.LOCK_EX\|LOCK_NB` (`:115`), `interval_s: 300` (`:244`), 8 radar keys, EIS/NES split (`:185,:229`) |
| 16 | version strings in the 6 new docs | new docs | ✅ | Only `1.0.0` values, all **AP-Token / Document-ID** versions, not engine versions. No nonexistent release claimed |
| 17 | `1.6.1-alpha` references | `docs/federation/…`, `docs/guides/…`, `docs/specs/…` | ✅ | All **forward-looking** ("MUST work for v1.6.1-alpha debut"). `pyproject.toml` = `1.6.0-alpha`; nothing claims 1.6.1 shipped |
| 18 | "Background tasks are cancelled automatically by the lifespan TaskGroup" | `mcp_servers/omega_hub/server.py:571` | 🚩 | Stale phrasing — cancellation is now an **explicit** `tg.cancel_scope.cancel()` (`mcp_runtime.py:251`), not automatic task-group behaviour. Reported |
| 19 | `mcp_client.py` imports `PROTOCOL_VERSION` without using it | `mcp_servers/omega_hub/mcp_client.py:24` | ✅ | **Intentional and test-enforced** (`test_client_and_probe_import_the_shared_constant`). Not a dead import |

**Totals: 19 claims checked · 4 inaccurate (fixed) · 4 divergent/historical
(annotated) · 3 reported-not-fixed · 8 already correct.**

---

## Finding A — The Law contradicts itself on mandate IDs (🚩 needs authority)

This surfaced while checking claim 10 and is **not** a defect in
`CONSTRAINTS.md` — that file is correct. The inconsistency is **inside
`SOVEREIGN_MANDATES.md` itself**.

The document numbers its mandates `### 1.` … `### 30.` and is treated as
"30 mandates" (v3.10.0). Only three headings additionally carry an inline
`(Mxx)` tag — and those tags **disagree with the section numbering**:

| Heading | Inline tag | Canonical (per §N) | Conflict |
|:---|:---:|:---:|:---|
| `### 28. Sovereign Artifact Preservation` | `M29` | **M28** | off by +1 |
| `### 29. Remote Claim Integrity` | `M30` | **M29** | off by +1 |
| `### 30. Third-Party Boundary…` | `M35` | **M30** | off by +5 |

Everything else in the governance tier uses **ID == section number**:

- `MANDATES_CONDENSED.md` — `| M28 | Sovereign Artifact Preservation |`,
  `| M29 | Remote Claim Integrity |`
- `AGENTS.md` — M28 Sovereign Artifact Preservation; M29 Remote Claim Integrity
- `docs/governance/CONSTRAINTS.md` — cites **M28** for Artifact Preservation
- `scripts/check_mandate_compliance.py` — enumerates exactly **M1…M27** over a
  30-mandate set, i.e. ID == section number
- `M30` and `M35` appear **nowhere** in the governance tier

**Consequence.** `CONSTRAINTS.md`'s `M28` is right, but a reader who trusts the
Law's own inline tag would conclude it cites "M29" and that M28 does not exist.
For a compaction-immune file whose entire purpose is to be re-read under
degraded context, that is a live misread risk.

**Why it was not fixed here.** Correcting mandate IDs in the Law is a
governance action, not a docs-accuracy fix: it touches M13 gate semantics, M28
artifact preservation, and tracking integrity, and it needs an authority this
audit does not hold. Unilaterally renumbering the Law is precisely the kind of
quiet edit that causes the drift this audit exists to catch.

**Recommended fix (one line, needs a D-series decision):** drop the inline
`(Mxx)` tags from §28/§29/§30 so ID == section number everywhere, **or** migrate
the whole tier to the tagged scheme. Flagging for Kali/MaKaLi.

---

## Finding B — Protocol-version honesty (the substantive one)

The task asked whether docs overclaim "aligned to MCP 2026-07-28". **They did —
in one place — and the code was more careful than the doc.**

**Verified live** (`mcp` **1.30.0**, the installed SDK):

```
SUPPORTED_PROTOCOL_VERSIONS = ['2024-11-05', '2025-03-26', '2025-06-18', '2025-11-25']
LATEST_PROTOCOL_VERSION      = 2025-11-25
'2026-07-28' in supported set -> False
```

So, precisely:

- **What the probe SENDS** — `_meta.protocolVersion = "2026-07-28"`
  (`hub_tools/federation.py:359-360`), the SEP-2575 envelope carrier.
- **What it deliberately does NOT send** — the `MCP-Protocol-Version` header
  (`SEND_PROTOCOL_VERSION_HEADER = False`). A 2026-07-28 value there draws
  **HTTP 400 / JSON-RPC `-32600`** from the installed SDK.
- **What the SDK ACCEPTS** — the four versions above; it tops out at 2025-11-25.
- **Full 2026-07-28 stateless compliance — NOT achieved.**

The one genuinely ambiguous signal, recorded so it is not itself over-read:
the live transport **does** answer a handshake-less `POST tools/list` with
HTTP 200 and a full tool list (verified 2026-10-03). That is **tolerance, not
compliance** — the SDK still negotiates `2025-11-25` at `initialize` and cannot
speak `2026-07-28` at all. Reading that 200 as proof of stateless compliance is
the same error class as the original overclaim.

**Credit where due:** `mcp_servers/omega_hub/protocol_version.py` already
documents all of this correctly, including the exact supported-version list and
the deliberate header omission, and
`tests/mcp/test_hub_protocol_version.py` guards the constant against drift. The
defect was confined to the research doc, which predated and then mis-described
the fix. That is now corrected.

---

## Finding C — Harvester doc↔impl parity: one divergence

Parity is otherwise excellent — the implementation guide mirrors the real code
including its actual `flock`/radar/EIS-NES line structure.

**The divergence:** design §3.1 recommends `N = 300 s with ±30 s jitter`. The
implementation performs a flat `await anyio.sleep(300)` — **no jitter**. A code
comment at `background.py:350` says "±15 s … if desired", agreeing with neither
the doc's ±30 s nor the code's absence of jitter. Three sources, three
positions.

**Impact: low.** Jitter exists to de-synchronise a fleet of harvesters against
one store; this is a single local hub, so it buys little. The **cadence itself
is correct and verified** — 300 s matches the doc, the guide, and
`interval_s: 300` in the emitted payload.

**Disposition:** the design doc now states plainly that jitter is a
recommendation and is not implemented. The misleading code comment (claim 13)
is left for a follow-up commit — a comment-only edit to a runtime file does not
belong in a docs-only audit commit, and it carries zero behavioural delta.

---

## Gate note — an unrelated pre-existing failure

While gating the harvester commit, `make temple-grade` failed on
`check-codex-stale`. **This is not a regression.** It is a 24-hour wall-clock
TTL on `OMEGA_CODEX.md` that expired at `2026-10-04T00:53:50Z`, which also
fails **M13** (Temple-Grade Compliance) since M13 shells out to it.

Proven independent of the harvester work by running the checker in a detached
worktree at pristine `HEAD` (9aba0afc, zero harvester changes): **identical
failure**. After a temporary `make codex`, `make temple-grade` returned
**exit 0** with the harvester staged, and `check-mandate-compliance` went from
22/30 to **23/30, 0 failed**.

`OMEGA_CODEX.md` was then restored to its committed state — regenerating it was
**not** in the authorised pathspec for either commit. **Outstanding action for
an operator: run `make codex` and commit it separately**, or M13 stays red for
the next 24 hours regardless of code quality.

---

## Unverifiable / out of scope

- **UNVERIFIED — remote tool counts.** Node 1 (8019) was not probed; this audit
  covers the local hub (8016) only. Any 8019 tool-count claim is unchecked.
- **UNVERIFIED — A2A endpoint behaviour.** `docs/architecture/A2A_AGENT_CARDS_20261003.md`
  states both 8016 and 8019 return 404 on `/.well-known/agent-card.json`. Only
  the **claim's wording** was audited (it correctly says "informed, NOT
  compliant"); the 404s themselves were not re-probed here. The doc's honesty is
  the finding — it already declines to claim compliance.
- **Out of scope — SOVEREIGN_MANDATES.md edit.** See Finding A. Reported, not
  changed.
- **Out of scope — runtime behaviour.** No runtime behaviour was modified by
  this audit, per mandate. Items 13 and 18 are comment-accuracy issues with
  zero behavioural delta, deferred to a follow-up.

---

## Net effect

Three docs corrected for fact (`how-to-debug-hub.md`, `KNOWLEDGE_GAPS_20261003.md`,
`HIVEMIND_HARVESTER_DESIGN_20261003.md`), two annotated as historical rather than
rewritten (M28), one audit added (this file), and four findings escalated rather
than silently absorbed. The most valuable result is not a correction but a
**boundary**: the repo's *code* is honest about the 2026-07-28 ceiling, and now
its docs say the same thing.

*⬡ OMEGA ⬡ MAAT ⬡ AP-DOCS-ACCURACY-AUDIT-20261003-v1.0.0 ⬡ 2026-10-03 ⬡ space-bunny-free*