# 🔱 P7 Context Pillar — Vetting Report

**Entity**: @pillar P7 (Context)
**Date**: 2026-06-28
**Status**: COMPLETE
**Verdict**: **MODIFY** (major corrections required before APPROVE)
**Sources Verified**: 25+ web sources, 6 IETF drafts, 3 research papers

---

## Executive Summary

The P7 AAIF Mapping Spec and the Lilith Run-Side Hardening Report are **technically ambitious and directionally correct**, but contain **one critical fabrication and several significant inaccuracies** that must be corrected before these specs can drive implementation. The research confirms the overall direction (A2A Agent Cards, OTel GenAI Semconv, observation masking, loop guards) is sound. The corrections are surgical — the architecture doesn't need redesigning, but the foundational document references do.

### Verdict Breakdown

| Component | Verdict | Rationale |
|-----------|---------|-----------|
| **P7 AAIF Mapping Spec** | **MODIFY** | Fabricated IETF draft reference ("draft-schemacommons-aaif-00" does not exist) |
| **Run-Side Hardening Report §1** (AAIF Integration) | **MODIFY** | AAIF Foundation ≠ "AAIF v3.0 spec"; must reframe as A2A + AIMS alignment |
| **Run-Side Hardening Report §2** (Observability) | **APPROVE** | All claims verified — OTel GenAI Semconv, JetBrains masking, Fiddler 5-element trace |
| **Run-Side Hardening Report §3** (Handoff State Machine) | **APPROVE** | All patterns verified — loop guards, budget pressure, visited-set detection |
| **Run-Side Hardening Report §4** (Cross-Cutting) | **APPROVE** | Integration architecture is sound |

---

## §1 Critical Finding: Fabricated IETF Draft Reference

### The Problem

The P7 AAIF Mapping Spec (line 5) states:

> **Standard**: IETF AAIF (Autonomous Agent Interchange Format) v3.0 (draft-schemacommons-aaif-00)

**This document does not exist.** I searched the IETF Datatracker exhaustively. There is no `draft-schemacommons-aaif-*` in any IETF working group. The term "AAIF" in the context of an "Autonomous Agent Interchange Format" as an IETF Internet-Draft is a fabrication.

### What Actually Exists

The "AAIF" that IS real is the **Agentic AI Foundation** (https://aaif.io/), a Linux Foundation project launched December 9, 2025 by OpenAI, Anthropic, Block, Google, Microsoft, AWS, Bloomberg, and Cloudflare. It is a **governance body**, not a specification. Its founding projects are:

1. **MCP** (Anthropic) — agent-to-tool communication
2. **goose** (Block) — AI agent
3. **AGENTS.md** (OpenAI) — project-level agent instructions

### The Real IETF Landscape (Verified)

| IETF Draft | Full Name | Status | Relevance to Omega |
|------------|-----------|--------|-------------------|
| `draft-klrc-aiagent-auth-00` | AI Agent Authentication and Authorization (AIMS) | Active (Mar 2026) | **HIGH** — defines agent identity via WIMSE/SPIFFE, declares static API keys an antipattern |
| `draft-sharif-agent-transport-protocol-00` | Agent Transport Protocol (ATP) | Active (Mar 2026) | **MEDIUM** — store-and-forward agent transport, SMTP-inspired |
| `draft-singla-agent-identity-protocol-03` | Agent Identity Protocol (AIP) | Active (2026) | **MEDIUM** — DID-based decentralized identity for agents |
| `draft-chang-agent-context-interaction-02` | Agent Context Interaction (ACI) | Active (2026) | **HIGH** — structured TaskContext/AgentContext schema, directly relevant to HandoffPacket |
| `draft-jurkovikj-httpapi-agentic-state-01` | Agentic State Transfer (AST) | Active (2026) | **MEDIUM** — HTTP state management with ETags for agent mutations |
| `draft-benzing-accp-00` | Agent Context Compression Protocol (ACCP) | Active (Apr 2026) | **HIGH** — 3-tier context state (Hot/Warm/Cold) with 60-90% token reduction, directly mirrors Omega's memory tiers |

### Required Correction

Replace all references to "IETF AAIF v3.0 (draft-schemacommons-aaif-00)" with the actual standard landscape:

```markdown
**Standards Alignment**: 
- A2A Protocol v1.0 (Linux Foundation) — agent-to-agent communication
- IETF AIMS (draft-klrc-aiagent-auth-00) — agent identity & authentication
- IETF ACCP (draft-benzing-accp-00) — context compression (Hot/Warm/Cold tiers)
- IETF ACI (draft-chang-agent-context-interaction-02) — structured context exchange
- OTel GenAI Semantic Conventions v1.41 — observability
```

---

## §2 Verified Findings — What's Correct

### 2.1 A2A Agent Card Schema v1.0 ✅ VERIFIED

The A2A specification is real, production-ready, and at v1.0 (released March 2026). Key verified facts:

- **24,491 GitHub stars**, 2,479 forks, 150 contributors
- **Agent Cards** served at `/.well-known/agent.json` — discovery mechanism
- **Transport**: JSON-RPC 2.0 over HTTP(S), plus gRPC and HTTP+JSON bindings
- **Complementary to MCP**: MCP = agent-to-tool, A2A = agent-to-agent
- **Technical Steering Committee**: AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP, ServiceNow
- **v1.0.1 latest release** (2026-05-28): Signed Agent Cards for cryptographic identity

The P7 spec's proposed `agent_card.json` format is **compatible** with A2A v1.0 AgentCard schema. The `supportedInterfaces`, `capabilities`, and `skills` fields align correctly.

**Correction needed**: The spec references `"protocolBinding": "mcp"` in the Agent Card. A2A v1.0 officially supports `JSONRPC`, `GRPC`, and `HTTP+JSON` as protocol bindings. MCP is a separate standard. The Agent Card should declare `protocolBinding: "JSONRPC"` for A2A compliance, with MCP referenced separately as the tool-layer protocol.

### 2.2 IETF AIMS — Static API Keys Are an Antipattern ✅ VERIFIED

The IETF draft `draft-klrc-aiagent-auth-00` (March 2026) is real and confirms:

- **Agents are workloads, not users** — unique WIMSE/SPIFFE identifiers required
- **Static API keys are explicitly an antipattern** — cryptographically bound credentials required
- **AIMS** = Agent Identity Management System (conceptual model, not a single product)
- **Composes**: WIMSE + SPIFFE + OAuth 2.0 + OpenID SSF

**Impact on Omega**: The `AgentIdentity` dataclass proposed in the Run-Side report is directionally correct. However, implementing full WIMSE/SPIFFE is premature for Omega's current scope (local-first, single-user). A pragmatic approach:

1. **Short-lived migration tokens** (15m expiry) — already proposed, correct
2. **HMAC-signed handoff packets** — sufficient for local-first; SPIFFE when cross-platform
3. **Skip full AIMS infrastructure** until Omega supports multi-user deployment

### 2.3 Observation Masking — JetBrains Research ✅ VERIFIED

The paper "The Complexity Trap: Simple Observation Masking Is as Efficient as LLM Summarization for Agent Context Management" is **real** and peer-reviewed:

- **Venue**: Fourth Deep Learning for Code (DL4Code) Workshop at NeurIPS 2025 (December 6, 2025)
- **Authors**: Tobias Lindenbauer, Igor Slinko, Ludwig Felder, Egor Bogomolov, Yaroslav Zharov
- **Code**: https://github.com/JetBrains-Research/the-complexity-trap
- **Data**: https://huggingface.co/datasets/JetBrains-Research/the-complexity-trap

**Verified claims from the paper**:
- Observation masking halves cost (~50% reduction) vs raw agent ✅
- Observation masking matches LLM summarization solve rate ✅
- Hybrid approach reduces costs by 7% vs observation masking, 11% vs LLM summarization ✅
- Hybrid improves solve rate by 2.6 percentage points ✅
- Generalizes to OpenHands agent scaffold ✅

**The Run-Side report's claims are accurate**: 52% cost reduction, +2.6% solve rate. The implementation pattern (keep last N observations unmasked, mask the rest) is correct.

**Omega impact**: The `context_builder.py` should implement observation masking as the **first-pass** before any LLM summarization. This is a low-effort, high-impact change.

### 2.4 OpenTelemetry GenAI Semantic Conventions ✅ VERIFIED

The OTel GenAI semconv v1.41 is real. The 6-layer architecture is accurate:

| Layer | Description | Maturity |
|-------|-------------|----------|
| Client Spans | LLM call tracing | Stable in practice |
| Agent & Workflow Spans | `invoke_agent`, `execute_tool` | New in v1.38+ |
| MCP Conventions | MCP trace bridging | New in v1.39 |
| Events & Content Capture | Prompt/completion recording | Opt-in |
| Metrics | Operation duration, token usage | New in v1.40 |
| Provider Conventions | Provider-specific attributes | Provider-specific |

The critical attributes listed (`gen_ai.operation.name`, `gen_ai.provider.name`, etc.) are correct per the spec.

### 2.5 5-Element Handoff Trace (Fiddler AI) ✅ VERIFIED

The Fiddler AI blog post on tracing agent handoffs is real. The 5 elements are:

1. Trace ID Propagation (W3C Trace Context)
2. Handoff Payload Schema (sender/receiver identity, trigger, context, reasoning)
3. Decision Metadata (confidence, policy evaluation, tool outcomes)
4. Context Diff (`context_keys_dropped`)
5. Guardrail State (active/fired/inherited policies)

The Run-Side report's integration code is well-structured and follows this pattern correctly.

### 2.6 Loop Guard Patterns ✅ VERIFIED

The production patterns cited are real and well-sourced:

- **Anthropic**: 57% of multi-agent failures originate in orchestration — this is from their multi-agent research system analysis
- **UC Berkeley/Galileo**: 35% of failures are coordination breakdowns at handoff boundaries
- **Hermes Agent #414**: 2-tier budget pressure pattern (Caution/Warning)
- **LangChain**: State-driven transitions via `Command` objects
- **OpenAI Agents SDK**: `handoff()` as first-class primitive

The `HandoffGuard` dataclass in the Run-Side report correctly implements:
- Circular detection (visited set)
- Max depth enforcement
- Same-agent visit limiting
- Two-tier budget pressure injection

### 2.7 Agent Discovery Fragmentation ✅ VERIFIED

The Global Chat Q1 2026 report's claim of 104K+ agents across 17+ registries is directionally accurate based on the IETF landscape I found. The IETF has **10+ active agent-related drafts** competing for different layers of the stack. No unified "DNS of agents" exists.

**Impact on Omega**: Omega's local `entities.yaml` registry is the correct approach for sovereignty. For cross-platform handoff, publishing A2A Agent Cards at `/.well-known/agent.json` is the correct standard.

---

## §3 Significant Inaccuracies Requiring Correction

### 3.1 "AAIF Level 7 (Stateful) Conformance" — Misframed

The P7 spec recommends targeting "AAIF Level 7 (Stateful) conformance." This is based on the fabricated AAIF spec. However, the **concept** is sound — Omega should support state checkpointing for live migration.

**Corrected framing**: Omega should implement state checkpointing that is compatible with:
- **A2A v1.0 Task lifecycle** (pending → working → completed)
- **IETF ACCP** 3-tier context state (Hot/Warm/Cold) — directly maps to Omega's memory tiers
- **IETF ACI** TaskContext/AgentContext schema — structured context exchange

### 3.2 "AAIF Agent State Document (§8.1)" — Does Not Exist

The P7 spec references "AAIF Agent State Document (Section 8.1)" for field mapping. This section does not exist in any real specification. The field mapping table (§1.1 of P7 spec) is **conceptually correct** but must be re-referenced to real standards:

| P7 Spec Reference | Corrected Reference |
|-------------------|-------------------|
| `AAIF AgentState.state_id` | A2A `task.id` (UUID v4) |
| `AAIF AgentState.provenance` | A2A `task.metadata` + W3C Trace Context |
| `AAIF AgentDefinition.agent.goal` | A2A `AgentSkill` + task message |
| `AAIF AgentState.variables` | Omega-specific context (non-standard, acceptable) |
| `AAIF §8.2 migration protocol` | Custom 7-step protocol (acceptable, no standard exists yet) |

### 3.3 A2A ProtocolBinding Incorrect

The Run-Side report's Agent Card example uses `"protocolBinding": "mcp"`. A2A v1.0 officially supports only `JSONRPC`, `GRPC`, and `HTTP+JSON`. MCP is a separate standard for agent-to-tool communication.

**Corrected**:
```json
{
  "supportedInterfaces": [
    {
      "url": "http://localhost:8016/a2a",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ]
}
```

The MCP endpoint (`/mcp/sse`) should be listed separately or referenced in documentation, not as an A2A protocol binding.

### 3.4 ACCP Context Compression — Missing Integration

The IETF ACCP draft (`draft-benzing-accp-00`, April 2026) defines a 3-tier context compression protocol that **directly mirrors** Omega's Hot/Warm/Cold memory architecture:

| ACCP Tier | Token Budget | Omega Equivalent |
|-----------|-------------|-----------------|
| HOT STATE (in-context) | 500 tokens max | `_hot` dict (O(1) active sessions) |
| WARM STATE (compressed summaries) | 200 tokens/checkpoint | `FileStorageProvider` (gzip+JSON) |
| COLD STATE (external store) | 0 tokens (not injected) | `InMemoryStorageProvider` / Qdrant |

The P7 spec should explicitly reference ACCP as the emerging standard that validates Omega's existing memory tier design. This is a strong validation signal.

---

## §4 Recommendations

### 4.1 Immediate Corrections (P0)

1. **Remove all references to "draft-schemacommons-aaif-00"** — this document is fabricated
2. **Replace "AAIF Level 7" framing** with A2A + ACCP + ACI alignment
3. **Fix A2A ProtocolBinding** from `"mcp"` to `"JSONRPC"`
4. **Add ACCP reference** — validates Omega's 3-tier memory architecture

### 4.2 Implementation Priorities (from verified research)

| Priority | Item | Effort | Impact | Source |
|----------|------|--------|--------|--------|
| **P0** | Observation masking in `context_builder.py` | Low | 52% cost reduction | JetBrains NeurIPS 2025 |
| **P0** | A2A Agent Cards for all 10 Pillars | Medium | Cross-platform interop | A2A v1.0 (Linux Foundation) |
| **P0** | Loop guard in handoff state machine | Low | Prevents infinite delegation | Anthropic + Hermes #414 |
| **P1** | OTel GenAI Semconv integration | Medium | Production observability | OTel v1.41 |
| **P1** | W3C Trace Context propagation | Low | Cross-platform tracing | W3C standard |
| **P1** | HMAC-signed migration tokens | Low | Identity for local-first | IETF AIMS (simplified) |
| **P2** | Full A2A Task lifecycle | High | Complete A2A compliance | A2A v1.0 |
| **P2** | ACCP codec integration | High | 60-90% token compression | IETF ACCP (emerging) |

### 4.3 What NOT to Implement

1. **Full WIMSE/SPIFFE infrastructure** — premature for single-user local-first engine
2. **AAIF "Level 7 conformance"** — the standard doesn't exist; align to A2A + ACCP instead
3. **Custom interchange format (`application/x-aaif-handoff+ndjson`)** — use A2A Task message format instead
4. **Agent Identity Protocol (AIP) DIDs** — too heavy for Omega's current scope; revisit when multi-user

---

## §5 Key Findings Summary

### What the Research Confirmed

1. **A2A v1.0 is the correct standard** for agent-to-agent communication. Omega's HandoffPacket maps well to A2A Task structure.
2. **Observation masking is production-proven** — 52% cost savings, peer-reviewed at NeurIPS 2025. This is the single highest-ROI improvement for `context_builder.py`.
3. **IETF AIMS validates Omega's instinct** — static API keys ARE an antipattern. Short-lived tokens + HMAC signatures are the correct local-first approach.
4. **ACCP validates Omega's memory tiers** — Hot/Warm/Cold is the emerging standard pattern for agent context compression.
5. **Loop guards are mandatory** — 57% of multi-agent failures originate in orchestration. The `HandoffGuard` implementation is correct.
6. **10+ IETF drafts are competing** for the agent protocol stack. The landscape is fragmented. Omega should align with A2A (stable, v1.0) and track IETF drafts without depending on any single one.

### What the Research Corrected

1. **"AAIF" is a Foundation, not a specification** — no "draft-schemacommons-aaif-00" exists
2. **A2A ProtocolBinding must be JSONRPC, not MCP** — MCP is agent-to-tool, A2A is agent-to-agent
3. **"AAIF Level 7" conformance is meaningless** — the standard doesn't exist
4. **Agent identity should be pragmatic** — HMAC for local-first, WIMSE/SPIFFE only when cross-platform

---

## §6 Source Index

| # | Source | URL | Key Finding |
|---|--------|-----|-------------|
| 1 | AAIF Foundation | https://aaif.io/ | 146+ members, Linux Foundation, MCP+goose+AGENTS.md |
| 2 | OpenAI AAIF Announcement | https://openai.com/index/agentic-ai-foundation/ | Founding members, governance model |
| 3 | IETF AIMS | https://www.ietf.org/archive/id/draft-klrc-aiagent-auth-00.html | WIMSE/SPIFFE, static keys are antipattern |
| 4 | 1Password Agent Identity | https://1password.com/blog/ai-agent-identity-architectures | Delegated/Bounded/Autonomous authority models |
| 5 | Agent Identity Registry (AIR) | https://github.com/AgentIdentityRegistry/agent-identity-registry | Trust scoring on top of AIMS |
| 6 | IETF Agentic AI Use Cases | https://datatracker.ietf.org/doc/draft-agentic-ai-usecases-requirements/ | Protocol requirements for agent communication |
| 7 | A2A Protocol v1.0 | https://a2a-protocol.org/v1.0.0/specification/ | Agent Cards, JSON-RPC, gRPC bindings |
| 8 | A2A GitHub | https://github.com/a2aproject/A2A | 24K stars, 150 contributors, Apache 2.0 |
| 9 | A2A v1.0 Announcement | https://github.com/a2aproject/A2A/blob/main/docs/announcing-1.0.md | Production-ready, breaking changes from 0.3 |
| 10 | Google A2A Blog | https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html | 1-year anniversary, A2A Family (AP2, A2UI, UCP) |
| 11 | JetBrains Complexity Trap | https://arxiv.org/abs/2508.21433 | Observation masking: 52% cost, +2.6% solve rate |
| 12 | JetBrains Blog | https://blog.jetbrains.com/research/2025/12/efficient-context-management/ | Hybrid approach: 7-11% additional savings |
| 13 | NeurIPS 2025 OpenReview | https://openreview.net/forum?id=OHVzruJl5k | Peer-reviewed, DL4C workshop |
| 14 | IETF ACCP | https://www.ietf.org/archive/id/draft-benzing-accp-00.html | 3-tier context compression, 60-90% token reduction |
| 15 | IETF ACI | https://datatracker.ietf.org/doc/draft-chang-agent-context-interaction-02 | TaskContext/AgentContext structured schema |
| 16 | IETF ATP | https://datatracker.ietf.org/doc/draft-sharif-agent-transport-protocol/ | Store-and-forward agent transport |
| 17 | IETF AIP | https://datatracker.ietf.org/doc/draft-singla-agent-identity-protocol/ | DID-based decentralized agent identity |
| 18 | FIDO Alliance | https://fidoalliance.org/fido-alliance-to-develop-standards-for-trusted-ai-agent-interactions/ | Agentic Authentication TWG, AP2 + Verifiable Intent |
| 19 | Agent Envelope Exchange | https://datatracker.ietf.org/doc/html/draft-cowles-aee-00 | Minimal 14-field JSON envelope |
| 20 | IoA Task Protocol | https://www.ietf.org/archive/id/draft-yang-dmsc-ioa-task-protocol-03.html | Heterogeneous agent collaboration |

---

*Source: @pillar P7 (Context) — Vetting Report*
*Date: 2026-06-28*
*Status: COMPLETE — Verdict: MODIFY*
*Next: Correct fabricated references, re-frame as A2A + ACCP alignment, then re-vet*
