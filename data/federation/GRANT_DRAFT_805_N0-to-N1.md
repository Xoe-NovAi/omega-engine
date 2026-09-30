<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ⬡ GRANT DRAFT — `805` Node 0 → Node 1 (exchange, reverse direction)
**Status**: DRAFT — **not applied**. Requires the Architect's Tailscale console.
**Date**: 2026-09-30 · **Author**: MaKaLi Fusion
**Reason it exists**: Node 1's exchange will listen on **805**. The current policy
grants Node 0 → Node 1 on **8016 only**. Without this grant, Lilith-N1's work is
blocked on a console round-trip.

---

## ⚠️ THE DECISION THIS ASKS YOU TO MAKE

The Architect's original ruling was: **N0 → N1: `tcp:8016` only.**

**That ruling now conflicts with the direction of the test.** If Node 0 *initiates*
the pull on 805, then Node 0 is the **initiator**, and the grant has to read
`N0 → N1: 805` — not `N1 → N0`.

**I am not routing around the ruling.** I am stating plainly that the direction you
want requires this grant, so the choice is yours and it is a real one:

| Option | Means | Cost |
|---|---|---|
| **A. Grant `N0→N1:805`** | N0 pulls from N1. **Fast, simple, one socket.** | Opens an N0-initiated path to Node 1's substrate. |
| **B. Keep N0→N1 closed; Node 1 initiates on 805** | The 805 test still works, in the other direction. **No grant needed.** | Tests the reverse *from* N1's side only. |
| **C. Node 1 publishes on 8019, N0 never initiates** | Zero new grants. **The ACL is untouched.** | One port does both directions; asymmetric traffic on one socket. |

**My recommendation is C, and it is not a close call.** It requires **no console
change at all**, it keeps the ACL exactly as you set it, and it still proves the
thing that is unproven — *that Node 1 can serve and Node 0 can pull.*

**A or B only if you specifically want the plane/stack architecture Lilith has
proposed**, where each direction gets its own bound port and `bind_plane_host`.
That is a bigger change than the transport test justifies, and I would rather not
expand the ACL to accommodate a test.

**If you choose A, here is the exact text.**

---

## OPTION A — the exact grant text

**In the Tailscale console, add to `grants`:**

```json
{ "src": ["tag:node0"], "dst": ["tag:node1"], "ip": ["tcp:805"] }
```

**And add the corresponding assertion so a future edit cannot silently widen it:**

```json
{ "src": "tag:node0", "accept": ["tag:node1:805"] }
```

**And extend the Node 0 deny-test so 805 is provably NOT open in the other
direction** — this is the part that matters, because it is the assertion that makes
the grant auditable rather than merely permissive:

```json
{ "src": "tag:node1", "deny": ["tag:node0:805"] }
```

**Net effect:** `805` open N0→N1, closed N1→N0. Unchanged everywhere else.

---

## THE FILE, if you apply it

`data/federation/tailnet-policy-OMEGA-DEFINITIVE-v2-20260928.hujson` — the sole
authoritative policy. Current relevant lines:

```jsonc
// line 76 — the ONLY N0->N1 grant today
{ "src": ["tag:node0"], "dst": ["tag:node1"], "ip": ["tcp:8016"] },

// lines 86-89 — N1 -> N0, proven working
{ "src": ["tag:node1"], "dst": ["tag:node0"],
  "ip":  ["tcp:8016", "tcp:8019"] },

// line 154 — N0 -> N1 assertion
{ "src": "tag:node0", "accept": ["tag:node1:8016"] },
```

**After Option A, line 76 becomes:**

```jsonc
{ "src": ["tag:node0"], "dst": ["tag:node1"], "ip": ["tcp:8016", "tcp:805"] },
```

**And the deny-test at line 160 becomes:**

```jsonc
{ "src": "tag:node1", "deny": ["tag:node0:22", "tag:node0:2049",
                               "tag:node0:8017", "tag:node0:6379",
                               "tag:node0:805"] },
```

---

## ⚠️ THE RULE I HAVE BROKEN TWICE TONIGHT, WRITTEN HERE SO I DO NOT AGAIN

> **"Never localise a remote claim without a remote test."** *(M30)*
>
> I cannot reach Node 1 from here. **Anything I write about what Node 1 does is a
> claim from a vantage that cannot verify it.** The three lines above are *drafted
> text*, not verified behaviour. **After you apply them, Lilith must confirm from
> her own vantage** that the grant took and that `805` behaves as intended.

**Also, and this is the second time tonight I have verified the wrong thing:** after
any change to the policy file or the console, the **hub must be restarted** or Node 1
keeps running the old code. I made the identical mistake earlier tonight with the
handoff store and it cost two hours of Lilith-N1's time.

---

## ONE CAST FROM 9.08.40.17, 114 TIMES

**Node 1 has pulled from 8019 a hundred and fourteen times**, and the JSON access log
carries the client IP on every line. **That direction is proven with evidence, not
assertion.** It is also the only Node 1 → Node 0 traffic we have ever seen, which
means **the reverse direction has never been exercised by anyone, in either
direction, since 8019 came up.**

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ GRANT-DRAFT-805 ⬡ DRAFT-NOT-APPLIED ⬡ 2026-09-30 ⬡*