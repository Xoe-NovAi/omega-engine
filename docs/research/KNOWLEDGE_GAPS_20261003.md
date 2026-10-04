<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# Omega Engine — Current Knowledge Gaps (Web Research)
**AP Token**: `AP-KNOWLEDGE-GAPS-20261003-v1.0.0`
**Date**: 2026-10-03
**Researcher**: MaKaLi Fusion (Oversoul) — 3 frontier search batches + internal audit
**Status**: COMPLETE

---

## Executive Summary — Top 7 Gaps

| # | Gap | Severity | Evidence |
|:--|:---|:---|:---|
| 1 | **Governance Decay** — compaction silently erases standing constraints | 🔴 CRITICAL | arXiv 2606.22528 (Jun 2026); validated in LangGraph/AutoGen/OpenAI SDK |
| 2 | **MCP spec drift** — federation probe uses `2024-11-05` while hub client is on `2026-07-28` stateless | 🔴 CRITICAL | `hub_tools/federation.py:307` vs `mcp_client.py:8` |
| 3 | **No control planes** — kill switch / escalation / approval / throttling | 🟠 HIGH | arXiv 2605.20173 ("build the dashboard before the agent") |
| 4 | **A2A v1.0 not adopted** — signed agent cards, capability discovery, task delegation | 🟠 HIGH | a2a-protocol.org v1.0 (Mar 2026, Linux Foundation AAIF) |
| 5 | **No agent identity standard** — WIMSE + OAuth 2.0 (IETF draft) | 🟡 MEDIUM | IETF draft-klrc-aiagent-auth |
| 6 | **No OTel GenAI tracing** — model/token/cost semantic conventions | 🟡 MEDIUM | OpenTelemetry GenAI conventions (2026) |
| 7 | **Hall of Records not addressable** — ARC pattern (ID-addressable log + compact citations) | 🟡 MEDIUM | arXiv 2607.25066 (Jul 2026) |

---

## 🔴 TIER 1 — Critical Gaps (safety / correctness)

### Gap 1: Governance Decay (compaction erases mandates)
**The finding (arXiv 2606.22528, "Governance Decay", Jun 2026):**
> In-context governance constraints that agents reliably obey while visible can be **silently removed by compaction**, causing the same agent to perform prohibited tool actions later in the session. Validated across LangGraph, LangMem, AutoGen, and the OpenAI Agents SDK under standard summarization-memory and recency-eviction configs.

**Why it matters to us:** Our compaction survival stack (M15: `session_gnosis.md`, `SESSION_ANCHOR.md`, Headroom compression) rehydrates *task* context but has **no mechanism to re-assert standing constraints** (SOVEREIGN_MANDATES, soul.yaml boundaries, PIVOT_LOG rulings) after compaction. A compacted agent could violate M1/M2/M23 without the constraint being in-context.

**Recommended action:** Add a **Constraint Re-assertion Layer** to the hydration triple — a compact, always-re-injected `CONSTRAINTS.md` (mandate IDs + one-line prohibitions) that survives compaction by construction and is re-asserted at every post-compact hydration. Treat standing constraints as **compaction-immune**, not as ordinary context.

### Gap 2: MCP protocol version drift (internal inconsistency)
**The finding:** `mcp_servers/omega_hub/mcp_client.py:8` already implements the **MCP 2026-07-28 stateless core** (SEP-2575 removed the initialize/initialized handshake). But `hub_tools/federation.py:307` still probes peers with `"protocolVersion":"2024-11-05"` — a **2-year-old protocol string**.

**Why it matters:** The federation health probe may false-flag or mis-negotiate against peers that have moved to the 2026-07-28 spec. It also signals spec drift inside our own hub.

**Recommended action:** Align the probe to the current protocol version (or better: omit `protocolVersion` and rely on capability negotiation, since 2026-07-28 is stateless). Add a single `PROTOCOL_VERSION` constant imported by both files so they cannot drift again.

### Gap 3: No formal control planes
**The finding (arXiv 2605.20173, "A Methodology for Selecting and Composing Runtime Architecture Patterns for Production LLM Agents", 2026):**
> Build the dashboard before the agent. The trace is the contract. ... P6 control planes in this order: **kill switch, escalation, approval, throttling**.

**Why it matters:** Our fleet can post blockers and hand off work, but there is **no kill switch** (halt a runaway subagent), **no approval gate** (human-in-the-loop for destructive ops), **no throttling** (rate-limit token/tool spend), and **no escalation path** (auto-promote a blocker to the Architect). These are the four control planes every production agent system needs.

**Recommended action:** Implement the four control planes as hub-side tools (M2-compliant, `mcp_servers/omega_hub/`): `control.kill(session_id)`, `control.escalate(packet_id)`, `control.approve(operation_id)`, `control.throttle(entity, budget)`. Wire `kill` and `throttle` into the harvester radar (Gap: a blocked agent should show `🔴 KILLED`).

---

## 🟠 TIER 2 — Architectural Gaps

### Gap 4: A2A Protocol v1.0 not adopted
**The finding:** A2A v1.0 shipped **March 2026** under the Linux Foundation (Agentic AI Foundation; TSC: AWS, Cisco, Google, IBM, Microsoft, Salesforce, SAP, ServiceNow). It is the peer-coordination complement to MCP:
- **MCP** = tool/context integration at the *individual agent* level.
- **A2A** = peer coordination, negotiation, and *delegation between agents*.
- Key primitives: **signed Agent Cards** (JSON metadata: identity, capabilities, skills, endpoint, auth), capability discovery, task management, multi-protocol bindings (JSON+HTTP, gRPC, JSON-RPC), version negotiation, multi-tenancy.

**Why it matters:** Our federation (WireGuard mesh, Exchange, handoffs) is a *custom* peer-coordination layer. We have an A2A bridge branch (`node1/all-5-mcp-green`) but it predates the v1.0 standard. Adopting A2A gives us interoperable capability discovery and signed agent identity for free.

**Recommended action:** Map our handoff/Exchange semantics onto A2A v1.0 primitives. Publish an **Agent Card** per sovereign entity. Adopt the protobuf normative model (`specification/a2a.proto`) rather than hand-rolling JSON.

### Gap 5: No standardized agent identity
**The finding (IETF draft-klrc-aiagent-auth):** Best practices for AI-agent auth leverage **WIMSE** (Workload Identity in Multi-System Environments) + the **OAuth 2.0** family. Key principle: *"Observability is a security control, not solely an operational feature"* — deployments MUST reconstruct agent behavior and authorization context after execution.

**Why it matters:** Our federation authenticates via Tailscale node identity, but there is **no agent-level identity** (an agent acting on behalf of a user/workload). The MCP roadmap explicitly calls for *"a standardized way to recognize and trust agent identities, built on existing standards rather than pasted API keys and long-lived tokens."*

**Recommended action:** Define an agent identity model (workload identity per sovereign seat) and bind it to the Agent Card (Gap 4). Treat audit reconstruction as a first-class requirement (we already have PIVOT_LOG + handoff receipts — formalize the linkage).

### Gap 6: No OpenTelemetry GenAI tracing
**The finding:** OpenTelemetry GenAI semantic conventions (2026) are the standard for tracing LLM calls with **model, token, and cost attributes** alongside auto-instrumented HTTP. The vLLM/Grafana stack demonstrates OTel → Prometheus → Grafana as the standard observability substrate for LLM fleets.

**Why it matters:** We have zero telemetry (M8) by design — but M8 forbids *external* telemetry, not *local* observability. We currently have no structured trace of token/cost/model per inference. The harvester design already proposed a Prometheus scrape target; OTel is the natural substrate.

**Recommended action:** Emit OTel GenAI spans locally (no exporter off-host) for inference calls. Ship a `latest.json` → Prometheus text-format endpoint alongside the harvester output. This is M8-compliant (local-only) and unlocks the zero-inference dashboard the harvester research recommended.

### Gap 7: Hall of Records is not addressable (ARC pattern)
**The finding (arXiv 2607.25066, "ARC: Addressable Recall Compaction", Jul 2026):**
> ARC separates archival storage from active-context presentation. It stores tool observations in an **append-only, ID-addressable log** and replaces older observations with **compact citations**. The agent can request stored content by ID without re-executing tools or relying on similarity retrieval. **99.40%** needle-in-a-haystack accuracy vs 88.12% baseline.

**Why it matters:** Our `HALL_OF_RECORDS` is append-only cold storage, but compaction (Headroom) summarizes rather than citing. Adopting ARC's ID-addressable citation model would let a compacted agent recall exact prior observations by ID instead of re-reading or re-executing.

**Recommended action:** Extend the harvester digest schema with an optional `citations: [id]` field pointing into HALL_OF_RECORDS. Compaction replaces verbose history with citations; the agent re-fetches by ID on demand.

---

## 🟡 TIER 3 — Frontier Opportunities

| # | Opportunity | Source | Fit |
|:--|:---|:---|:---|
| 8 | **MCP Tasks** — async long-running ops with polling, mid-flight input, durable handles | MCP 2026-07-28 spec / roadmap | Our handoffs are a custom Tasks layer; MCP-native Tasks would standardize |
| 9 | **MCP Skills** — rich structured agent workflows discovered via MCP | MCP roadmap | Could publish sovereign-slot playbooks as MCP Skills |
| 10 | **Continuous Context Management (CCM)** — compact *every turn*, not at threshold | arXiv 2609.35540 | Alternative to threshold-triggered Headroom |
| 11 | **ACM** — agent-owned context editing tools; offload to external memory, query on demand | arXiv 2607.23809 | Agent-autonomous compaction vs engine-imposed |
| 12 | **ACON** — optimized compression, 26–54% peak token reduction | arXiv 2510.00615 | Headroom improvement |
| 13 | **Agentic commerce (ACP / AP2)** — agent payments protocols | IETF draft references | Out of scope for debut; note for future |
| 14 | **CompactionRL** — the *summary model* alone changed task accuracy by 6.5 pts | arXiv 2607.05378 | Validates investing in compaction quality |

---

## 📊 Internal Knowledge State Audit

**Library domains (document counts):** modelgate 31, sentinel 25, link 11, sysadmin 11, context 9, datastore 9, bridge 9, buildmaster 8, watchtower 7, movie_expert 4, sophia 4, verifier 4, networking 3, lilith 2, jem 2, programming 2, roc_racoon 1, testing 1, systems 1, integration 1, research 1.

**Coverage gaps in the library:** thin coverage of `research` (1), `systems` (1), `integration` (1), `testing` (1) — the exact domains the gaps above touch (control planes, OTel, A2A, compaction). The library is strong on governance (modelgate/sentinel) but weak on the 2026 agent-runtime frontier.

**Spec-version audit (hub):**
- `mcp_client.py` — ✅ MCP 2026-07-28 stateless (SEP-2575)
- `hub_tools/federation.py:307` — ❌ probes with `2024-11-05` (drift)
- `federation_envelope.py` — envelope dir renamed from `envelopes/` 2026-09-30 (current)

---

## 🎯 Prioritized Action Queue

| Pri | Action | Effort | Mandate link |
|:---|:---|:---|:---|
| P0 | Fix MCP probe version drift (`federation.py:307`) | S | M23 (probe honesty) |
| P0 | Constraint Re-assertion Layer (compaction-immune `CONSTRAINTS.md`) | M | M11/M15 (soul/continuity integrity) |
| P1 | Four control planes (kill/escalate/approve/throttle) | L | M23/M28 (failure/preservation) |
| P1 | A2A v1.0 Agent Cards per sovereign seat | M | S9 (federation) |
| P2 | OTel GenAI local spans + Prometheus endpoint | M | M8 (local-only observability) |
| P2 | ARC-style addressable citations in harvester digest | M | S7 (context) |
| P3 | MCP Tasks / Skills adoption | L | S4 (integration) |

---

## Sources (accessed 2026-10-03)
- MCP 2026-07-28 spec — modelcontextprotocol.io/specification/draft
- MCP Roadmap (2026-08-22) — blog.modelcontextprotocol.io/posts/mcp-roadmap/
- A2A v1.0 (2026-03) — a2a-protocol.org/latest/blog/2026/03/12/... ; aaif.io/blog/a2a-joins-aaif
- A2A core spec — agent2agent.info/specification/core
- IETF draft-klrc-aiagent-auth — ietf.org/archive/id/draft-klrc-aiagent-auth-03.html
- Governance Decay — arXiv 2606.22528 (alphaxiv.org/abs/2606.22528)
- ARC — arXiv 2607.25066
- ACM — arXiv 2607.23809
- CCM — arXiv 2609.35540
- ACON — arXiv 2510.00615
- CompactionRL — arXiv 2607.05378
- SUPO (ACL 2026) — aclanthology.org/2026.acl-long.966
- Runtime patterns — arXiv 2605.20173
- Multi-agent orchestration survey — mdpi.com/1999-5903/18/6/326
- Orchestration of MAS — arXiv 2601.13671
- OTel GenAI observability — docs.base14.io/guides/ai-observability/llm-observability
- TruePlane (control plane) — platform.tracxn.com/a/d/company/.../trueplane

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ KNOWLEDGE-GAPS-20261003 ⬡ v1.0.0 ⬡*
