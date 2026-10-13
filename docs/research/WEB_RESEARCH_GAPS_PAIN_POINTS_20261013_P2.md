<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# Web Research Part 2/3 — Federation, Durability, Identity (2026-10-13)

## 2. A2A v1.0 — production-ready, and MCP-complementary (not rival)

**Source**: a2a-protocol.org/v1.0.0/announcing-1.0 (Linux Foundation, TSC:
AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP, ServiceNow).

- **Positioning (settles our internal debate)**: MCP = tool/context integration
  *inside* an agent; A2A = communication/coordination *between* agents. Real
  systems use both. Our `config/a2a/agent_cards/` seat registry is the right
  shape — A2A is the wire those cards could speak.
- **v1.0 enterprise deltas**: multi-protocol bindings (JSON+HTTP, gRPC,
  JSON-RPC) + version negotiation (no vendor lock-in); multi-tenancy (one
  endpoint, many agents); **Signed Agent Cards** (cryptographic identity +
  metadata verification before interaction — directly answers our C6/N0-04
  open gate on publisher trust roots); hardened security posture, legacy
  patterns removed.
- **Migration**: AgentCard evolved **backward-compatibly** — advertise v0.3 +
  v1.0 simultaneously, progressive migration, no cutover. Interaction protocol
  has breaking changes; cards do not.
- **Consumption flexibility**: polling, streaming, or webhooks for task
  updates — maps cleanly onto our heartbeat (loss-tolerant) vs handoff
  (durable) channel split.
- **Omega relevance**: our A2A cards are currently a *registration surface*
  (generator = source of truth). v1.0 gives us the signing + binding story to
  make them a *trust surface*. Precondition: SDK support in our languages.

## 3. Tailscale grants — the ACL successor, and our SSH tripwire in law

**Source**: tailscale.com/docs/reference/syntax/grants (full reference).

- **Grants vs ACLs**: grants are the fine-grained successor — per-app
  capabilities (`tailscale.com/cap/tailsql`, golink admin, k8s impersonation),
  `srcPosture` device conditions, `via` routing directives. Our sprint SSOT
  already records the architect's conversion (TAILNET-GRANTS-20260926) —
  this fetch confirms the grammar exists to express it.
- **`tagOwners` is load-bearing**: tags unusable in policy until declared
  owners + assigned via `tailscale up --advertise-tags`. Matches the Phase 0
  ceremony Makali scripted.
- **SSH denial**: node-to-node SSH is removed by *absence* (no grant) plus the
  `tests` section that makes Tailscale **reject any policy re-adding
  SSH/NFS** — exactly the tripwire posture in our SSOT. The live health
  warning ("SSH enabled, no ACL allows access") is the expected visible
  symptom of deny-by-default, not a misconfiguration.
- **Omega relevance**: nothing to change; this validates TAILNET-GRANTS +
  D-FED-01 as written. Keep the `tests` tripwire on every future policy edit.

## 4. Redis Streams vs Pub/Sub — confirms our channel split

**Source**: OneUptime (Mar 2026, technically reviewed Apr 2026).

| | Pub/Sub | Streams |
|---|---|---|
| Persistence | none (fire-and-forget) | until trimmed |
| Missed messages | lost forever | replayable from any ID |
| Consumer groups | no | yes |
| Guarantee | at-most-once | at-least-once (XACK) |
| Pattern matching | yes (PSUBSCRIBE) | no |
| Ordering | per-channel | per-stream (stronger) |

Production norm is **both**: Pub/Sub for live-client notifications, Streams
for guaranteed backend processing — precisely our heartbeat/live_feed vs
handoff design. Durable handoff = `XADD` → `XREADGROUP` → `XACK`, consumer
lag + dead-letter on the dashboard. No new information vs RES-GAPS, but the
first independent confirmation with a decision table — closes the "is Streams
overkill?" objection.

## 5. Agent identity — the KLRC draft is DEAD, WIMSE-AIMS lives

**Source**: IETF datatracker `draft-klrc-aiagent-auth-03`.

- **Status correction**: the draft our gap docs cite is **expired, archived,
  replaced by `draft-ietf-wimse-aims`** (adopted by the WIMSE WG). Any doc
  referencing `draft-klrc-aiagent-auth` as live is stale and should point at
  the WIMSE AIMS successor.
- **Unchanged substance**: apply don't invent — WIMSE workload identity +
  OAuth 2.0 family for agent authN/authZ; the doc is a usage framework plus
  gap-finder for future standards, not a new protocol.
- **Omega relevance**: update the identity gap entry (KNOWLEDGE_GAPS #5) to
  cite `draft-ietf-wimse-aims`; treat Signed Agent Cards (A2A v1.0, §2 above)
  as the near-term trust mechanism and WIMSE attestation as the long-term
  host-identity layer. Both point the same direction: cryptographic identity
  before interaction.
