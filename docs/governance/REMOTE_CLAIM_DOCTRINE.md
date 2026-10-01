<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Remote Claim Doctrine — "Works From Here" ≠ "Works From There"
**Document ID**: `GOV-REMOTE-CLAIM-20260928`
**Status**: RATIFIED
**Date**: 2026-09-28
**Authority**: MaKaLi Fusion Dialectic Round 3 — Kali Ruling (Carmack Promoted)
**Mandate Basis**: M23 (Failure Integrity), M29 (Sovereign Artifact Preservation), M27 (Tracking Integrity)

---

## The Spine of the Document

> **"Works from here" is not "works from there." Test the path the peer will actually take, from the peer's vantage, or say it is untested.**

This is not a footnote. It is the document's spine. Carmack promoted it as such; the oversoul concurs.

---

## The Evidence (All From Today)

| Claim | Local Test | Remote Reality | Consequence |
|-------|------------|----------------|-------------|
| Exchange channel 8019 "verified" | Tested from loopback (127.0.0.1) | Peer's plain-HTTP path returns **400** whose 48-byte ASCII body `curl -o` writes to disk as a "successful download" | Receiver who skips manifest writes 48-byte "zip", fails later at `unzip`, far from cause |
| Same channel recommended to remote agent | On strength of local test | **Never tested from peer's vantage** | Agent acted on false premise |
| Mis-aimed pixel probe | Local success | Wrong target | Confabulated object |
| Phantom port | Local bind succeeded | Port not reachable from peer | Phantom port |

**Pattern:** A local success is reported as a remote success. The claim recurs in earlier forms. The defect class is identical to temple-grade 53/53 over a crash-looping hub: **the test passes, but the property it claims to verify is false.**

---

## The Rule (With Teeth)

### 1. A Claim About Remote Behaviour Requires a Test From the Peer's Vantage, or Is Labelled **UNTESTED** — Never "Verified"

There is no middle ground. If you have not executed the exact code path the peer will execute, from the peer's network position, with the peer's credentials and environment, the claim is **UNTESTED**. It must be labelled as such in every report, handoff, and verbal assertion.

### 2. A Local Success Is Not a Remote Success, and Must Never Be Reported as One

The 8019 case: loopback test passes, peer gets 400. The local test exercised a different code path (loopback vs. Tailscale, different HTTP stack, different auth context). **The test did not test what it claimed to test.** Reporting it as "verified" is a M23 violation (soft-failure / simulated rigor).

### 3. Post-Hoc Verification Is Necessary and Not Sufficient

A check that runs after the fact caught the 8019 failure. But what is missing is a transfer protocol that **cannot report false success**. This is a named requirement:

> **Transfer Integrity Requirement:** Any inter-node transfer protocol must include a verification step that **cannot** report success when the payload is corrupt, truncated, or an error page. If the verification step can be bypassed by a 400 response body, the protocol is defective.

This requirement is not a nicety. It is the difference between "we think it worked" and "we know it worked."

### 4. If a Test Cannot Distinguish Success from Failure, the Claim Is Untestable, Not True

The 8019 case: no access log meant a successful pull and a failed pull were indistinguishable. So **we do not know whether that channel has ever worked in either direction.** That is a state the doctrine must have a word for:

> **UNTESTABLE** — The system lacks the observability to distinguish success from failure for this path. Any claim about this path is ungrounded.

**UNTESTABLE is not UNKNOWN.** UNKNOWN means we haven't looked. UNTESTABLE means we *cannot* look with the current instrumentation. The correct response to UNTESTABLE is to instrument, not to assume.

---

## The State Machine for Remote Claims

```
┌─────────────────┐
│   CLAIM MADE    │
│ "Channel works" │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TEST FROM      │
│  PEER'S VANTAGE │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
 SUCCESS   FAILURE
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────────┐
│ VERIFIED │ │   UNTESTED /     │
│ (with    │ │   UNTESTABLE     │
│ evidence)│ │   (label clearly)│
└─────────┘ └──────────────────┘
```

**No other states exist.** "Locally tested" is not a state. "Seemed to work" is not a state. "We did it before" is not a state.

---

## Required Artefacts for a VERIFIED Remote Claim

A claim labelled **VERIFIED** must include:

1. **Test harness** — the exact command/script executed from the peer's vantage
2. **Environment snapshot** — network position, credentials, TLS config, proxy config
3. **Success criteria** — what constitutes success (HTTP 200 + valid manifest + SHA256 match, not just "download completes")
4. **Failure mode analysis** — what a 400/500/timeout looks like, and how the test distinguishes it from success
5. **Observability gap statement** — what the test *cannot* see (e.g., "no access log on receiver means we cannot distinguish silent drop from success")

If any of these is missing, the claim is **UNTESTED**, not VERIFIED.

---

## Application to the 8019 Exchange Channel

| Property | Status |
|----------|--------|
| Tested from peer's vantage? | ❌ NO — tested from loopback only |
| Success criteria included manifest validation? | ❌ NO — only "download completes" |
| Failure mode (400 body) distinguishable? | ❌ NO — `curl -o` writes 400 body as file |
| Access log on receiver? | ❌ NO — indistinguishable |
| **Claim status** | **UNTESTABLE** |

**Correct labelling:** "Channel 8019: UNTESTABLE — loopback test passes, peer path returns 400, no access log to distinguish success from failure. Requires instrumentation before any transfer relies on it."

---

## Integration with SAHS Rule

The SAHS Rule (Single Authoritative Handoff Surface) already asserts:
- Exactly one writer
- Projection reconciliation
- No rogue writes

**This doctrine extends SAHS to the transfer layer:** A handoff is not "delivered" until the *receiver* has verified the payload from *their* vantage. The sender's "sent" is not the receiver's "received." The envelope is not complete until both sides agree.

---

## Companion Principle — The Observer Is Also the Finding-Manufacturer

**Document ID**: `GOV-OBSERVER-PARAMETER-20260929`
**Status**: RATIFIED
**Authority**: MaKaLi Ruling, Reverse-Direction Build Dispatch (2026-09-29)
**Mandate Basis**: M23 (Failure Integrity), M30 (Remote Claim Integrity)

This document governs claims about *remote* behaviour. This section governs the
*observer* who makes the claim. It is the general form of the same defect.

> ### **An observer that verifies with different parameters than the test manufactures findings.**

The spine above says a local success is not a remote success. This says the next
thing: **an observer who changes the test's parameters is no longer observing the
test.** A re-run with different flags is not verification — it is a second,
uncorrelated experiment whose result gets reported under the first one's
authority. The finding is manufactured by the mismatch, not observed in the system.

### The Exemplar — GE-N1, 2026-09-29

GE-N1's own words, offered unprompted and documented rather than suppressed:

> *"An agent that trusts a passing harness but then 'independently verifies' with different flags is not verifying anything — it is manufacturing a finding."*

They reported a parity discrepancy, then caught it: their own comparison showed
`map` differing across 192 lines, but the discrepancy was an artifact of the
*invocation*, not the artifact. They had omitted `--salience -1 --legacy-warm`
from the v2 command. The passing harness used the correct parameters; the
"independent verification" did not; the difference was manufactured; and the
honest thing was to write it up.

**Why this is teachable rather than merely excusable:** the pressure that produces
it is real. A passing harness is available; a fresh run is free; the fresh run
produced a *finding*, and findings get reported. The move that matters is the one
they made — diagnosing it themselves before someone else found the same omission.

### Three Instances, One Week

| # | Instance | The parameter mismatch | What it manufactured |
|---|----------|------------------------|----------------------|
| 1 | GE-N1 parity "discrepancy" | omitted `--salience -1 --legacy-warm` from the v2 invocation | A 192-line `map` diff reported as a data defect; actually an artifact of the command |
| 2 | `check-hub-health` gate | asserted `is-active`, not `SubState=running` + `NRestarts` | A PASS on a hub that had restarted 101 times; `temple-grade` 53/53 rode along |
| 3 | 8019 48-byte body | `curl -o` on a `400`, no `-f`, no size/hash check | An apparent successful download that was 48 bytes of ASCII error text |

Same shape on all three: **the observing apparatus was wrong in a way that
favoured a false green**, and nothing in the apparatus would have told anyone.

### The Rule

**When re-verifying, use the same parameters the passing test used.** If the
parameters must differ, that run is a *different experiment* and must be labelled
as one — with both parameter sets stated, and with no claim carried across between
them. "Independently verifying with different flags" is a contradiction in terms:
independence is not achieved by divergence.

**Corollary — a gate that cannot fail is a finding-manufacturer in the positive
direction.** Instance 2 is the same defect inverted: there the observer was
*missing* and the finding was manufactured by absence. Both directions produce
false confidence, and both are closed by the same discipline — **assert the
specific property, with the specific parameters, or label the claim UNTESTED.**

---

## Contradictions with Prior Art

| Prior Art | Contradiction | Resolution |
|-----------|---------------|------------|
| "Channel verified" in handoff reports | Based on local test only | Must be relabelled UNTESTED/UNTESTABLE |
| "Transfer complete" on sender-side success | Sender-side ≠ receiver-side | Transfer complete only on receiver verification |
| Post-hoc manifest check as sufficient | Necessary but not sufficient | Must have transfer protocol that cannot report false success |

---

## The Word for the State

**UNTESTABLE** — The system lacks the observability to distinguish success from failure for this path. Any claim about this path is ungrounded. The correct response is to instrument, not to assume.

---

*⬡ OMEGA ⬡ KALI ⬡ REMOTE-CLAIM-DOCTRINE ⬡ 2026-09-28 ⬡ DOCTRINE-ROUND-3*