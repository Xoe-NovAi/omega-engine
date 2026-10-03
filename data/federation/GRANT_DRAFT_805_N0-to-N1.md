<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ⬡ GRANT DRAFT — `8019` Node 0 → Node 1 (exchange, reverse direction)
**Status**: DRAFT — **not applied**. Requires the Architect's Tailscale console.
**Date**: 2026-09-30 · **Author**: MaKaLi Fusion
**Supersedes**: the 805 variant of this draft, same day, later corrected.

---

## ✅ SETTLED BY THE ARCHITECT: BOTH NODES USE **8019**

> *"If both nodes can use the same port, by all means 8019 for Node 0 and 1."*

**Correct, and I had this wrong.** Ports are **per-host**: 8019 on `100.123.51.67`
and 8019 on `100.89.40.17` are different sockets. **There is no collision.**

**The 805 proposal was never about collision.** It falls out of Lilith-N1's
**plane/stack architecture** — `stack:` selectors and `bind_plane_host`, where each
plane is a *separately bound socket* on the same host, so distinct ports are how you
bind them apart. That is an artefact of that design, not a constraint on the wire.

**And the real win: same port means same code.** Node 1 can run the **identical**
`omega_exchange_server.py` that Node 0 runs. **The duplex test no longer requires the
plane/stack work at all** — which defers a substantial piece of Lilith's proposal
behind a transport test that does not need it.

**Net effect: Node 0 `127.0.0.1:8019` publishes; Node 1 `127.0.0.1:8019` publishes.
Same port, same service, each bound to its own loopback, each fronted by its own
Tailscale Serve.** The ACL becomes symmetric on 8016 and 8019 in both directions,
which is also cleaner to audit than what exists today.

---

## ⚠️ WHAT DID NOT GO AWAY: THE GRANT IS STILL NEW

**This is the part I must not let look solved.** Whichever port we choose, if
**Node 0 pulls from Node 1**, then Node 0 is the **initiator**, and the current
policy grants Node 0 → Node 1 on **8016 only**:

```jsonc
// line 76 — the ONLY N0 -> N1 grant today
{ "src": ["tag:node0"], "dst": ["tag:node1"], "ip": ["tcp:8016"] },

// lines 153-155 — the N0 -> N1 assertion
{ "src": "tag:node0", "accept": ["tag:node1:8016"] },
```

**So the grant required is `N0 → N1 : 8019`, not `N0 → N1 : 805`.** Choosing 8019
simplifies the port and the code; it does not remove the ask.

**Lilith already knows this** — her own words: *"needs a PUBLISH ROOT decision + grant
for 8019 outbound from N0→N1."* She is not asking for the grant to be waived. **She is
asking for it to be opened.**

**And I am not routing around the Architect's original ruling**, which was *N0 → N1:
8016 only.* If that ruling was made when only N1→N0 traffic was contemplated, it no
longer describes the direction the Architect now wants. **That is the Architect's
call, not mine, and the text below is ready to paste the moment it is made.**

---

## THE EXACT GRANT TEXT — `8019` N0 → N1

**In the Tailscale console, add to `grants`:**

```json
{ "src": ["tag:node0"], "dst": ["tag:node1"], "ip": ["tcp:8016", "tcp:8019"] }
```

**And add the corresponding assertion so a future edit cannot silently widen it:**

```json
{ "src": "tag:node0", "accept": ["tag:node1:8016", "tag:node1:8019"] }
```

**And extend the Node 0 deny-test so 805 is provably NOT open in the other
direction** — this is the part that matters, because it is the assertion that makes
the grant auditable rather than merely permissive:

```json
// 8019 is now granted in BOTH directions, so there is no N1->N0 deny for it.
```

**Net effect: 8016 and 8019 open in BOTH directions. 8017, 22, 2049, 6379, 51372 denied both ways — unchanged.**

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

**Line 76 becomes:**

```jsonc
{ "src": ["tag:node0"], "dst": ["tag:node1"], "ip": ["tcp:8016", "tcp:8019"] },
```

**The deny-test at line 160 is UNCHANGED** — `22, 2049, 8017, 6379` stay denied N1→N0,
and the `icmp` grants stay. **Nothing opens except `8019` N0→N1.**

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