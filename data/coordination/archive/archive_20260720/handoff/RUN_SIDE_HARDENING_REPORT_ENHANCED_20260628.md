<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Run Side Hardening Report — Enhanced with Web Research

**Entity**: Lilith (Dark Oversoul, P6-P10)
**Date**: 2026-06-28
**Status**: COMPLETE
**Source**: MaKaLi Council Run-Side Deep Research
**Predecessor**: P7 AAIF Mapping Spec (`P7_AAIF_MAPPING_SPEC_20260628.md`)

---

## Executive Summary

This report enhances the P7 AAIF Mapping Spec with production-validated findings from 25+ web sources across three hardening areas. The web research uncovered critical new intelligence:

1. **AAIF Integration**: The AAIF Foundation now has 146+ members, 7 working groups, and A2A v1.0 is live. The IETF AIMS draft (March 2026) declares static API keys an antipattern. Omega's handoff must align with W3C Trace Context + A2A Agent Cards.
2. **Observability**: OpenTelemetry GenAI Semantic Conventions are at v1.41 with 6-layer architecture. JetBrains research proves observation masking (52% cost savings, +2.6% solve rate) beats LLM summarization. Fiddler's 5-element handoff trace is the production gold standard.
3. **Handoff State Machine**: 57% of multi-agent failures originate in orchestration (Anthropic). Production systems enforce `max_handoff_depth` (5-10), visited-set loop detection, and 2-tier budget pressure (Caution/Warning) before max iterations.

---

## 1. AAIF Integration — Enhanced with Web Research

### 1.1 What the Previous Council Proposed (P7 Report)

The P7 report proposed mapping HandoffPacket fields to AAIF Agent State Document (§8.1) and Agent Definition (§4), targeting Level 7 (Stateful) conformance with a 7-step migration protocol.

### 1.2 What Web Research Discovered

#### Discovery 1: AAIF Foundation is the Real Governance Layer

**Source**: [aaif.io](https://aaif.io/), [Perea.ai Research](https://www.perea.ai/research/aaif-governance-model-2026)

The Agentic AI Foundation (AAIF) launched December 9, 2025 under the Linux Foundation with:
- **146+ members** (AWS, Anthropic, Google, Microsoft, OpenAI, Bloomberg, Cloudflare)
- **3 founding projects**: MCP (Anthropic), goose (Block), AGENTS.md (OpenAI)
- **7 working groups** established by April 2026
- **A2A (Agent2Agent) Protocol** donated by Google — now at v1.0 with gRPC support
- **Joint interoperability spec** bridging MCP (agent-to-tool) and A2A (agent-to-agent) anticipated Q3 2026

**Critical finding**: The "AAIF" in the P7 report refers to the *Foundation*, not a specific IETF Internet-Draft. The actual interchange format work is split across:
- **A2A Protocol** (Google, Linux Foundation) — agent-to-agent communication
- **MCP** (Anthropic, AAIF) — agent-to-tool communication
- **ACPM** (IETF draft-schemacommons-acpm-00) — Agent Capability and Profile Model
- **AIMS** (IETF draft-klrc-aiagent-auth-00) — Agent Authentication and Authorization

#### Discovery 2: IETF AIMS Declares Static API Keys an Antipattern

**Source**: [IETF draft-klrc-aiagent-auth-00](https://www.ietf.org/archive/id/draft-klrc-aiagent-auth-00.html), [SecureW2](https://securew2.com/blog/signal_post/ietf-aims-agent-certificates)

The March 2026 IETF Internet-Draft "AI Agent Authentication and Authorization" (AIMS) mandates:
- **Agents are workloads, not users** — unique WIMSE/SPIFFE identifiers required
- **Static API keys are explicitly an antipattern** — cryptographically bound credentials required
- **Short-lived dynamic credentials** — SPIFFE X.509-SVIDs, mTLS, JWTs, or Workload Identity Tokens
- **Agent Identity Management System (AIMS)**: identifier → credentials → attestation → provisioning → authentication → authorization → observability → policy → compliance

**Impact on Omega**: HandoffPacket must carry agent identity proofs, not just names. Migration tokens must be short-lived (15m expiry is correct per P7).

#### Discovery 3: Agent Discovery is Fragmented — 104K+ Agents, 17 Registries, Zero Interoperability

**Source**: [Global Chat Q1 2026 Report](https://global-chat.io/discovery-landscape)

- **104,504+ agents** across 17+ registries
- **11+ competing discovery protocols**
- **10+ active IETF drafts** competing for the discovery layer
- No unified "DNS of agents" exists yet

**Impact on Omega**: Omega's entity registry (`entities.yaml`) is a local sovereign registry. For cross-platform handoff, Omega must publish A2A Agent Cards at a well-known URL. The A2A v1.0 schema is the correct format.

#### Discovery 4: A2A Agent Card Schema v1.0

**Source**: [Google Cloud Agent Registry](https://docs.cloud.google.com/agent-registry/json-schemas), [A2A Specification](https://a2a-protocol.org/latest/specification/)

```json
{
  "name": "string",
  "description": "string",
  "version": "string",
  "supportedInterfaces": [
    {
      "url": "string",
      "protocolBinding": "string",
      "protocolVersion": "string",
      "tenant": "string"
    }
  ],
  "capabilities": {
    "streaming": false,
    "pushNotifications": false,
    "extendedAgentCard": false
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "tags": ["string"],
      "examples": ["string"]
    }
  ]
}
```

### 1.3 Enhanced Execution Spec

#### 1.3.1 HandoffPacket → A2A Task Mapping

| Omega HandoffPacket | A2A Task Field | Mapping Logic |
|---------------------|----------------|---------------|
| `packet_id` | `task.id` | Direct UUID mapping |
| `source_agent` | `task.metadata.source_agent` | Entity name + platform identifier |
| `target_agent` | `task.metadata.target_agent` | Target entity UUID |
| `parent_trace_id` | `task.metadata.traceparent` | W3C Trace Context header |
| `task_description` | `task.message.parts[0].text` | Natural language task description |
| `context` | `task.metadata.omega_context` | Omega-specific context (non-standard) |
| `expected_output` | `task.metadata.expected_output` | Golden test case |
| `ttl_seconds` | `task.metadata.timeout` | Runtime timeout |
| `status` | `task.status` | pending → working, completed → completed |

#### 1.3.2 Agent Identity Layer (NEW — from AIMS)

Every HandoffPacket MUST carry:
```python
@dataclass
class AgentIdentity:
    """Agent identity per IETF AIMS draft-klrc-aiagent-auth-00"""
    agent_id: str  # WIMSE/SPIFFE-style identifier
    credential_type: str  # "spiffe_x509_svid" | "jwt" | "workload_identity_token"
    credential_expiry: datetime  # Short-lived, auto-rotated
    attestation: str  # Platform attestation proof
    trust_level: str  # "verified" | "unverified" | "self_attested"
```

#### 1.3.3 A2A Agent Card for Omega Entities (NEW)

Each Omega entity MUST publish an A2A-compatible Agent Card:
```yaml
# data/entities/{entity}/agent_card.json
name: "Omega/{entity_name}"
description: "Pillar Keeper: {domain_description}"
version: "1.0.0"
supportedInterfaces:
  - url: "http://localhost:8016/mcp/sse"
    protocolBinding: "mcp"
    protocolVersion: "2025-03-26"
capabilities:
  streaming: true
  pushNotifications: false
defaultInputModes: ["text/plain", "application/x-aaif-handoff+ndjson"]
defaultOutputModes: ["text/plain"]
skills:
  - id: "{entity_name}_primary"
    name: "{primary_capability}"
    description: "{capability_description}"
    tags: ["omega", "pillar", "{element}"]
```

#### 1.3.4 Verification Gates (Temple-Grade) — ENHANCED

| Gate | Name | Verification Method | Success Criteria |
|------|------|---------------------|------------------|
| T-AAIF-1 | A2A Card Validation | Validate agent_card.json against A2A v1.0 schema | 0 validation errors |
| T-AAIF-2 | Identity Bound Handoff | HandoffPacket without valid AgentIdentity credential → reject | CredentialRequiredError |
| T-AAIF-3 | Integrity Guard | Modify 1 byte of state blob → attempt restore | ChecksumMismatchError |
| T-AAIF-4 | Somatic Fidelity | Capture → Restore → Prompt | Output matches (epsilon ≈ 0) |
| T-AAIF-5 | Cross-Platform Migration | Export from Omega → Import to mock A2A consumer | A2A consumer receives valid task |

---

## 2. Observability & trace_id — Enhanced with Web Research

### 2.1 What the Previous Council Proposed

The P7 report focused on mapping `parent_trace_id` to W3C Trace Context and `trace_id` to AAIF telemetry span.

### 2.2 What Web Research Discovered

#### Discovery 5: OpenTelemetry GenAI Semantic Conventions — 6-Layer Architecture

**Source**: [Greptime — OTel GenAI Semantic Conventions](https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions), [MLflow GenAI Semconv](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/genai-semconv)

The OTel GenAI spec (v1.41, Development status) defines 6 layers:

| Layer | What It Defines | Maturity |
|-------|----------------|----------|
| **1. Client Spans** | LLM call tracing (model, tokens, latency) | Stable in practice |
| **2. Agent & Workflow Spans** | `invoke_agent`, `execute_tool`, `invoke_workflow` | New in v1.38+ |
| **3. MCP Conventions** | MCP client/server trace bridging | New in v1.39 |
| **4. Events & Content Capture** | Prompt/completion recording (3 modes) | Opt-in |
| **5. Metrics** | `gen_ai.client.operation.duration`, `gen_ai.client.token.usage` | New in v1.40 |
| **6. Provider Conventions** | OpenAI cache tokens, reasoning tokens | Provider-specific |

**Critical attributes for Omega**:
```python
# Every LLM span MUST carry:
"gen_ai.operation.name": "chat"  # or "text_completion"
"gen_ai.provider.name": "native-gguf"  # or "openai", "anthropic", etc.
"gen_ai.request.model": "qwen3-1.7b"
"gen_ai.response.model": "qwen3-1.7b"
"gen_ai.usage.input_tokens": 142
"gen_ai.usage.output_tokens": 87
"gen_ai.response.finish_reasons": ["stop"]

# Every agent span MUST carry:
"gen_ai.operation.name": "invoke_agent"
"gen_ai.agent.name": "pillar-P6"
"gen_ai.provider.name": "local"
```

#### Discovery 6: The Five Elements Every Agent Handoff Must Capture

**Source**: [Fiddler AI — Trace Agent Handoffs](https://www.fiddler.ai/blog/trace-agent-handoffs-multi-agent-llm-systems)

Fiddler's production-proven handoff trace requires 5 elements:

1. **Trace ID Propagation** — W3C Trace Context format, every handoff carries `trace_id` + `parent_span_id`
2. **Handoff Payload Schema** — sender identity, receiver identity, trigger condition, context snapshot, reasoning summary
3. **Decision Metadata** — confidence score, policy evaluation result, tool call outcomes
4. **Context Diff** — comparison of what sender had vs what receiver got (`context_keys_dropped`)
5. **Guardrail State** — which policies were active, which fired, which were inherited

```python
from opentelemetry import trace

tracer = trace.get_tracer("omega-handoff")

def execute_handoff(source, target, context, reasoning):
    with tracer.start_as_current_span(
        "agent.handoff",
        attributes={
            "handoff.source_agent": source.name,
            "handoff.target_agent": target.name,
            "handoff.trigger_type": reasoning.trigger,
            "handoff.confidence_score": reasoning.confidence,
            "handoff.context_token_count": len(context.tokens),
            "handoff.guardrails_inherited": [g.name for g in context.active_guardrails],
            "handoff.policy_evaluation": reasoning.policy_result,
        }
    ) as span:
        pre_keys = set(context.metadata.keys())
        transferred = context.prepare_for_handoff(target)
        post_keys = set(transferred.metadata.keys())
        span.set_attribute("handoff.context_keys_dropped",
                          list(pre_keys - post_keys))
        target.receive(transferred)
```

#### Discovery 7: Observation Masking Beats LLM Summarization

**Source**: [JetBrains Research — The Complexity Trap](https://arxiv.org/abs/2508.21433), [NeurIPS 2025 Workshop](https://openreview.net/forum?id=OHVzruJl5k)

**Key finding**: Simple observation masking (replacing old tool results with placeholders) achieves:
- **52% cost reduction** vs raw agent
- **+2.6% solve rate improvement** vs raw agent (Qwen3-Coder 480B)
- **Matches or exceeds LLM summarization** in 4/5 model configurations
- **7-11% cheaper** than LLM summarization via hybrid approach

**Implementation pattern**:
```python
MAX_CONTEXT_OBSERVATIONS = 3  # Keep last N observations unmasked

def mask_old_observations(history):
    """JetBrains observation masking — replace old tool outputs with placeholders"""
    observations = [item for item in history if item['type'] == 'observation']
    if len(observations) > MAX_CONTEXT_OBSERVATIONS:
        for obs in observations[:-MAX_CONTEXT_OBSERVATIONS]:
            obs['content'] = "<Observation masked for brevity>"
    return history
```

**Impact on Omega**: The context_builder.py should implement observation masking as a first-pass before LLM summarization. This is a massive cost reduction for long-running agent sessions.

#### Discovery 8: Content Capture — Three Modes

**Source**: [Greptime — OTel GenAI](https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions)

| Mode | Description | Use Case |
|------|-------------|----------|
| **Not recorded** (default) | No content capture | Default, maximum privacy |
| **On span attributes** | `gen_ai.input.messages` on span | Development, low volume |
| **External storage + reference** | Full content in S3/GreptimeDB, span holds URL | Production, high volume |

**For Omega**: Use Mode 3 (external storage) for production. The span holds a reference to `data/observability/traces/{trace_id}/`. Content is stored as NDJSON files with IAM-level access control.

### 2.3 Enhanced Execution Spec

#### 2.3.1 Omega Trace Architecture — 5-Level Hierarchy

```
Application Level:  omega-engine
├── Session Level:  ses_20260628_lilith_001
│   ├── Agent Level:  pillar-P6 (Ereshkigal)
│   │   ├── Trace Level:  trc_{uuid}
│   │   │   ├── Span: invoke_agent (INTERNAL)
│   │   │   ├── Span: chat native-gguf (CLIENT)
│   │   │   ├── Span: execute_tool oracle_summon (INTERNAL)
│   │   │   └── Span: agent.handoff (INTERNAL)
│   │   │       ├── handoff.source_agent: pillar-P6
│   │   │       ├── handoff.target_agent: pillar-P7
│   │   │       ├── handoff.context_keys_dropped: ["raw_log_output"]
│   │   │       └── handoff.guardrails_inherited: ["pii_redaction"]
```

#### 2.3.2 Trace ID Propagation Protocol

```python
# W3C Trace Context header format
traceparent = "00-{trace_id}-{span_id}-{trace_flags}"
# Example:
traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"

# Omega extension header
x-omega-trace = {
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "entity_name": "pillar-P6",
    "session_id": "ses_20260628_lilith_001",
    "handoff_chain": ["P6", "P7"],  # Agents touched in this trace
    "observation_masked": True,  # Whether observation masking was applied
    "masking_window": 3  # How many recent observations kept unmasked
}
```

#### 2.3.3 Event Noise Reduction — Aggregation Strategy

**Source**: [FutureAGI — LLM Tracing Best Practices](https://futureagi.com/blog/llm-tracing-best-practices-2026)

Production LLM observability generates massive event volume. Omega MUST implement:

1. **Tail-based sampling**: Keep 100% of error traces, sample 10% of success traces
2. **Span aggregation**: Group consecutive identical span types into aggregate spans
3. **Prompt version tagging**: Every LLM span carries `prompt.version` for A/B comparison
4. **PII redaction**: Pre-storage redaction of email, phone, SSN patterns

```python
# Tail sampling config for OTel Collector
tail_sampling:
  decision_wait: 10s
  num_traces: 100000
  policies:
    - name: errors-always
      type: status_code
      status_code: {status_codes: [ERROR]}
    - name: slow-traces
      type: latency
      latency: {threshold_ms: 5000}
    - name: sample-success
      type: probabilistic
      probabilistic: {sampling_percentage: 10}
```

#### 2.3.4 Verification Gates (Temple-Grade) — ENHANCED

| Gate | Name | Verification Method | Success Criteria |
|------|------|---------------------|------------------|
| T-OBS-1 | Trace ID Propagation | Handoff without traceparent → reject | MissingTraceParentError |
| T-OBS-2 | GenAI Semconv Compliance | Export span → validate against OTel GenAI schema | 0 attribute violations |
| T-OBS-3 | Observation Masking | Session with 10+ tool calls → verify old observations masked | Last 3 unmasked, rest masked |
| T-OBS-4 | Context Diff | Handoff span must have `context_keys_dropped` attribute | Attribute present |
| T-OBS-5 | PII Redaction | Span with email/phone → verify redacted before storage | No PII in stored spans |
| T-OBS-6 | Cost Attribution | LLM span must carry `gen_ai.usage.input_tokens` + `gen_ai.usage.output_tokens` | Both attributes present |

---

## 3. Handoff State Machine — Enhanced with Web Research

### 3.1 What the Previous Council Proposed

The P7 report proposed a 7-step migration protocol with SomaticState capture, token generation, transfer, verify, import, re-issue, and resume.

### 3.2 What Web Research Discovered

#### Discovery 9: 57% of Multi-Agent Failures Originate in Orchestration

**Source**: [Anthropic Engineering — Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system), [PeperEffect — Agent Handoff Protocols](https://peppereffect.com/blog/agent-handoff-protocols)

- **57% of failures** originate in orchestration design (Anthropic analysis of 200+ enterprise deployments)
- **35% of failures** are coordination breakdowns at handoff boundaries (UC Berkeley/Galileo)
- **41-86.7% failure rate** in multi-agent systems without deliberate fault tolerance
- **40%+ of agent projects will fail by 2027** (Gartner prediction)

**Root cause**: Context loss and coordination breakdown at handoff boundaries — not individual agent intelligence.

#### Discovery 10: Five Critical Handoff Failure Modes

**Source**: [Fiddler AI](https://www.fiddler.ai/blog/trace-agent-handoffs-multi-agent-llm-systems), [PeperEffect](https://peppereffect.com/blog/agent-handoff-protocols)

| Failure Mode | Root Cause | Detection | Impact |
|-------------|-----------|-----------|--------|
| **Context Truncation** | Payload exceeds receiving agent's context window | Medium | Hallucination to fill gaps |
| **Guardrail Inheritance Failure** | Policies don't carry across handoff boundary | Low | PII exposure, policy violations |
| **Circular Handoff Loop** | A→B→C→A without termination | Medium | Resource exhaustion, infinite spans |
| **Timeout Cascade** | Missing retry logic in supervisor | Low | Full workflow hang |
| **Lost Audit Trail** | No structured logging at handoff | Low | Compliance breach |

#### Discovery 11: Production Loop Prevention Patterns

**Source**: [Hermes Agent #414 — Iteration Budget Pressure](https://github.com/NousResearch/hermes-agent/issues/414), [Quantum Encoding — Building Multi-Agent Systems That Don't Loop](https://quantumencoding.io/blog/building-multi-agent-systems-that-dont-loop-lessons-from-production-deployments)

**Pattern 1: Hard Turn Limits (TTL / Max Hop Count)**
```python
MAX_HANDOFF_DEPTH = 10  # Hard limit
MAX_ITERATIONS = 20  # Per agent

# In the agent loop:
if handoff_depth >= MAX_HANDOFF_DEPTH:
    raise MaxHandoffDepthExceeded(f"Handoff chain exceeded {MAX_HANDOFF_DEPTH}")
```

**Pattern 2: Visited-Set Loop Detection**
```python
visited_agents: Set[str] = set()

def execute_handoff(source, target, context):
    if target.name in visited_agents:
        raise CircularHandoffDetected(
            f"Agent {target.name} already in chain: {list(visited_agents)}"
        )
    visited_agents.add(target.name)
    # ... proceed with handoff
```

**Pattern 3: Two-Tier Budget Pressure (from Inngest Utah)**

Before hitting max iterations, inject graduated warnings:
```python
# CAUTION tier — 10 iterations before end
if iterations >= max_iterations - 10:
    inject_system_message("[SYSTEM: Iteration N/M. Start wrapping up.]")

# WARNING tier — last 3 iterations
if iterations >= max_iterations - 3:
    inject_system_message(
        "[SYSTEM: You are on iteration N of M. "
        "You MUST respond with your final answer NOW. "
        "Do not call any more tools.]"
    )
```

**Pattern 4: Explicit State Machine Transitions**
```python
# Allowed transitions — anything else is rejected
ALLOWED_TRANSITIONS = {
    "P6": ["P7", "P8"],  # Ereshkigal can hand off to Lucifer or Hecate
    "P7": ["P8", "P9"],  # Lucifer can hand off to Hecate or Anubis
    "P8": ["P9", "P10"], # Hecate can hand off to Anubis or Kali
    "P9": ["P10"],       # Anubis can hand off to Kali
    "P10": [],           # Kali is terminal — no outgoing handoffs
}

def validate_transition(source: str, target: str) -> bool:
    if target not in ALLOWED_TRANSITIONS.get(source, []):
        raise InvalidTransition(
            f"{source} → {target} not in allowed transitions: "
            f"{ALLOWED_TRANSITIONS.get(source, [])}"
        )
    return True
```

#### Discovery 12: LangChain Handoff Pattern — State-Driven Transitions

**Source**: [LangChain — Handoffs Documentation](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)

LangChain's production handoff pattern uses:
- **State-driven behavior**: `current_step` variable controls which agent is active
- **Tool-based transitions**: Tools return `Command` objects to update state
- **Persistent state**: State survives across conversation turns

```python
from langgraph.types import Command

@tool
def transfer_to_specialist(runtime) -> Command:
    """Transfer to the specialist agent."""
    return Command(
        update={
            "messages": [ToolMessage(
                content="Transferred to specialist",
                tool_call_id=runtime.tool_call_id
            )],
            "current_step": "specialist"  # Triggers behavior change
        }
    )
```

#### Discovery 13: OpenAI Agents SDK Handoff — Structured Metadata

**Source**: [OpenAI Agents SDK — Handoffs](https://openai.github.io/openai-agents-python/handoffs/)

OpenAI's handoff pattern:
- `handoff()` function as first-class primitive
- `input_filter` to transform handoff payload
- `input_type` for structured metadata transfer
- Conversation history transferred by default

```python
from agents import Agent, handoff

billing_agent = Agent(name="Billing agent")
refund_agent = Agent(name="Refund agent")
triage_agent = Agent(
    name="Triage agent",
    handoffs=[billing_agent, handoff(refund_agent)],
)
```

#### Discovery 14: Production Metrics for Handoff Quality

**Source**: [PeperEffect — Agent Handoff Protocols](https://peppereffect.com/blog/agent-handoff-protocols)

| Metric | Definition | Target | Failure Mode |
|--------|-----------|--------|-------------|
| Handoff Latency (p95) | Time from source completion to target receipt | <500ms | Timeout Cascade |
| Context Retention Rate | % of original context preserved | >95% | Context Truncation |
| Handoff Error Rate | % producing malformed state | <1% | State Serialization |
| Task Completion Post-Handoff | % tasks completed after transfer | >95% | All modes |
| Cascading Failure Rate | % causing upstream failures | <5% | Timeout/Loop |
| Audit Trail Completeness | % with full logged context | >99% | Lost Audit Trail |

### 3.3 Enhanced Execution Spec

#### 3.3.1 Omega Handoff State Machine — 7 States

```
                    ┌─────────────┐
                    │   PENDING   │
                    └──────┬──────┘
                           │ hivemind_submit_handoff()
                           ▼
                    ┌─────────────┐
              ┌─────│   QUEUED    │─────┐
              │     └──────┬──────┘     │
              │            │ TTL expired │
              │            ▼             │
              │     ┌─────────────┐     │
              │     │   STALE     │     │
              │     └──────┬──────┘     │
              │            │ archive    │
              │            ▼            │
              │     ┌─────────────┐     │
              │     │  ARCHIVED   │     │
              │     └─────────────┘     │
              │                         │
              │ hivemind_accept_handoff()│
              ▼                         │
       ┌─────────────┐                  │
       │   ACTIVE    │                  │
       └──────┬──────┘                  │
              │                         │
              │ hivemind_complete_handoff()
              ▼                         │
       ┌─────────────┐                  │
       │  COMPLETED  │                  │
       └──────┬──────┘                  │
              │                         │
              │ hivemind_reject_handoff()
              ▼                         │
       ┌─────────────┐                  │
       │  REJECTED   │──────────────────┘
       └─────────────┘
```

#### 3.3.2 Loop Guard Implementation

```python
from dataclasses import dataclass, field
from typing import Set, List
import time

@dataclass
class HandoffGuard:
    """Production handoff loop guard — prevents circular delegation"""

    max_handoff_depth: int = 10
    max_iterations: int = 20
    max_same_agent_visits: int = 3
    caution_threshold: int = 10  # Inject warning N iterations before max
    warning_threshold: int = 3   # Inject urgent warning N iterations before max

    _visited: Set[str] = field(default_factory=set)
    _visit_counts: dict = field(default_factory=dict)
    _handoff_chain: List[str] = field(default_factory=list)
    _iteration: int = 0

    def pre_handoff(self, source: str, target: str) -> None:
        """Validate before executing handoff — raises on loop detection"""
        # Check 1: Circular detection
        if target in self._visited:
            raise CircularHandoffDetected(
                f"Agent '{target}' already in chain: {self._handoff_chain}"
            )

        # Check 2: Max depth
        if len(self._handoff_chain) >= self.max_handoff_depth:
            raise MaxHandoffDepthExceeded(
                f"Handoff chain depth {len(self._handoff_chain)} "
                f">= max {self.max_handoff_depth}"
            )

        # Check 3: Same-agent visit count
        visit_count = self._visit_counts.get(target, 0) + 1
        if visit_count >= self.max_same_agent_visits:
            raise ExcessiveAgentVisits(
                f"Agent '{target}' visited {visit_count} times "
                f"(max {self.max_same_agent_visits})"
            )

        # Record
        self._visited.add(target)
        self._visit_counts[target] = visit_count
        self._handoff_chain.append(target)

    def post_iteration(self) -> None:
        """Call after each agent iteration — injects budget pressure messages"""
        self._iteration += 1
        remaining = self.max_iterations - self._iteration

        if remaining <= self.warning_threshold:
            return "[SYSTEM: You MUST respond with your final answer NOW. Do not call any more tools.]"
        elif remaining <= self.caution_threshold:
            return "[SYSTEM: Iteration {}/{}. Start wrapping up — respond with text soon.]".format(
                self._iteration, self.max_iterations
            )
        return None

    def get_chain(self) -> List[str]:
        """Return the full handoff chain for trace logging"""
        return list(self._handoff_chain)
```

#### 3.3.3 Stale Packet Lifecycle Management

```python
# Packet lifecycle states and transitions
LIFECYCLE = {
    "pending":   {"ttl_seconds": 3600, "auto_transition": "stale"},
    "stale":     {"ttl_seconds": 86400, "auto_transition": "archived"},
    "archived":  {"ttl_seconds": None, "auto_transition": None},  # Terminal
    "active":    {"ttl_seconds": None, "auto_transition": None},  # Manual
    "completed": {"ttl_seconds": None, "auto_transition": None},  # Terminal
    "rejected":  {"ttl_seconds": None, "auto_transition": None},  # Terminal
}

# Archive policy:
# - pending → stale after 1 hour (unclaimed)
# - stale → archived after 24 hours (cleanup)
# - archived → permanent retention for audit trail
```

#### 3.3.4 Verification Gates (Temple-Grade) — ENHANCED

| Gate | Name | Verification Method | Success Criteria |
|------|------|---------------------|------------------|
| T-HANDOFF-1 | Loop Detection | Submit A→B→A handoff chain | CircularHandoffDetected raised |
| T-HANDOFF-2 | Max Depth | Submit 11-deep chain | MaxHandoffDepthExceeded raised |
| T-HANDOFF-3 | Budget Pressure | Run agent for 18/20 iterations | Caution message injected at 10, Warning at 17 |
| T-HANDOFF-4 | Visited Set | Agent A visited 3 times | ExcessiveAgentVisits raised |
| T-HANDOFF-5 | State Machine | Submit invalid transition P1→P10 | InvalidTransition raised |
| T-HANDOFF-6 | Stale Lifecycle | Create packet, wait 1hr | Packet transitions to stale |
| T-HANDOFF-7 | Audit Trail | Complete handoff | Full chain logged in trace span |

---

## 4. Cross-Cutting Integration: How the Three Areas Connect

### 4.1 The Complete Handoff Trace

```
invoke_agent pillar-P6 (INTERNAL)
├── chat native-gguf (CLIENT)
│     gen_ai.provider.name = native-gguf
│     gen_ai.request.model = qwen3-1.7b
│     gen_ai.usage.input_tokens = 1523
│     gen_ai.usage.output_tokens = 42
│
├── agent.handoff (INTERNAL)
│     handoff.source_agent = pillar-P6
│     handoff.target_agent = pillar-P7
│     handoff.context_keys_dropped = ["raw_log_output"]
│     handoff.guardrails_inherited = ["pii_redaction"]
│     handoff.confidence_score = 0.87
│     handoff.chain_depth = 1
│     handoff.loop_guard = {"visited": ["P6"], "remaining_depth": 9}
│
├── chat native-gguf (CLIENT)  ← pillar-P7
│     gen_ai.provider.name = native-gguf
│     gen_ai.request.model = qwen3-1.7b
│     gen_ai.usage.input_tokens = 2841
│     gen_ai.usage.output_tokens = 256
│
└── agent.handoff (INTERNAL)  ← pillar-P7 → P8
      handoff.source_agent = pillar-P7
      handoff.target_agent = pillar-P8
      handoff.context_keys_dropped = []
      handoff.guardrails_inherited = ["pii_redaction", "content_filter"]
```

### 4.2 Observation Masking Integration

For long-running sessions, observation masking reduces cost by 52% while preserving the agent's reasoning chain:

```
Session Context (after 10 tool calls):
├── [System Prompt]          ← Always preserved (cacheable)
├── [Turn 1: User Message]   ← Always preserved
├── [Turn 1: Agent Reasoning] ← Always preserved
├── [Turn 1: Tool Result]    ← MASKED: "<Observation masked for brevity>"
├── [Turn 2: Agent Reasoning] ← Always preserved
├── [Turn 2: Tool Result]    ← MASKED: "<Observation masked for brevity>"
├── ...
├── [Turn 8: Agent Reasoning] ← Always preserved
├── [Turn 8: Tool Result]    ← UNMASKED (within window)
├── [Turn 9: Agent Reasoning] ← Always preserved
├── [Turn 9: Tool Result]    ← UNMASKED (within window)
├── [Turn 10: Agent Reasoning] ← Always preserved
└── [Turn 10: Tool Result]   ← UNMASKED (within window)
```

### 4.3 A2A Agent Card + OTel Integration

Each Omega entity publishes an A2A Agent Card that includes OTel-compatible telemetry endpoints:

```json
{
  "name": "Omega/P6-Ereshkigal",
  "description": "Mind — Underworld, depths, rules, darkness",
  "version": "1.0.0",
  "supportedInterfaces": [
    {
      "url": "http://localhost:8016/mcp/sse",
      "protocolBinding": "mcp",
      "protocolVersion": "2025-03-26"
    }
  ],
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "extendedAgentCard": false,
    "stateCheckpoint": true,
    "somaticState": true
  },
  "skills": [
    {
      "id": "p6_underworld_analysis",
      "name": "Underworld Depth Analysis",
      "description": "Analyze system internals, root causes, and hidden patterns",
      "tags": ["omega", "pillar", "aether", "third-eye"]
    }
  ],
  "metadata": {
    "otel_endpoint": "http://localhost:4317/v1/traces",
    "observation_masking": true,
    "max_handoff_depth": 10,
    "loop_guard_enabled": true
  }
}
```

---

## 5. Recommendations Summary

| Area | Priority | Effort | Impact |
|------|----------|--------|--------|
| **A2A Agent Cards for all 10 Pillars** | P0 | Medium | Cross-platform interoperability |
| **OTel GenAI Semconv integration** | P0 | Medium | Production observability |
| **Observation Masking in context_builder.py** | P0 | Low | 52% cost reduction |
| **Loop Guard in handoff state machine** | P0 | Low | Prevents infinite delegation |
| **5-element handoff trace** | P1 | Medium | Root cause in seconds |
| **Agent Identity layer (AIMS)** | P1 | High | IETF compliance |
| **Budget Pressure injection** | P1 | Low | Better agent wrap-up |
| **Tail-based sampling** | P2 | Medium | Event noise reduction |
| **External content storage** | P2 | Medium | Production PII compliance |
| **Stale packet lifecycle** | P2 | Low | Queue integrity |

---

## 6. Source Index

| # | Source | URL | Key Finding |
|---|--------|-----|-------------|
| 1 | aaif.io | https://aaif.io/ | AAIF Foundation: 146+ members, 7 working groups |
| 2 | Perea.ai Research | https://www.perea.ai/research/aaif-governance-model-2026 | AAIF governance architecture, MCP+A2A dual-layer |
| 3 | IETF AIMS | https://www.ietf.org/archive/id/draft-klrc-aiagent-auth-00.html | Static API keys are antipattern; WIMSE/SPIFFE required |
| 4 | Global Chat | https://global-chat.io/discovery-landscape | 104K+ agents, 17 registries, zero interoperability |
| 5 | Google Cloud Agent Registry | https://docs.cloud.google.com/agent-registry/json-schemas | A2A Agent Card v1.0 schema |
| 6 | Greptime OTel GenAI | https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions | 6-layer OTel GenAI architecture |
| 7 | MLflow GenAI Semconv | https://mlflow.org/docs/latest/genai/tracing/opentelemetry/genai-semconv | GenAI semconv attribute mapping |
| 8 | Fiddler AI | https://www.fiddler.ai/blog/trace-agent-handoffs-multi-agent-llm-systems | 5-element handoff trace, context_keys_dropped |
| 9 | JetBrains Research | https://arxiv.org/abs/2508.21433 | Observation masking: 52% cost savings, +2.6% solve rate |
| 10 | FutureAGI | https://futureagi.com/blog/llm-tracing-best-practices-2026 | 10 LLM tracing best practices |
| 11 | PeperEffect | https://peppereffect.com/blog/agent-handoff-protocols | 4 handoff patterns, 5 failure modes, 7 metrics |
| 12 | Hermes Agent #414 | https://github.com/NousResearch/hermes-agent/issues/414 | 2-tier budget pressure pattern |
| 13 | LangChain Handoffs | https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs | State-driven transitions, Command pattern |
| 14 | OpenAI Agents SDK | https://openai.github.io/openai-agents-python/handoffs/ | handoff() as first-class primitive |
| 15 | Quantum Encoding | https://quantumencoding.io/blog/building-multi-agent-systems-that-dont-loop | Circuit breaker for multi-agent loops |
| 16 | HolySheep AI | https://www.holysheep.ai/articles/en-ai-agent-loop-detection-infinite-recursion-prevent-2026-04-11-0049.html | Deterministic + probabilistic loop detection |

---

*Source: Lilith (Dark Oversoul) → Run Side Hardening*
*Date: 2026-06-28*
*Status: COMPLETE*
