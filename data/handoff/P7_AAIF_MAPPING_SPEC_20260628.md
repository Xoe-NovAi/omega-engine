# 🔱 AAIF Mapping & State Checkpointing — Execution Spec

> **⚠️ CORRECTION (2026-06-29): This Document Referenced a Fabricated Standard**
>
> The original spec referenced `draft-schemacommons-aaif-00` which **does not exist**.
> No such IETF draft has ever been submitted. This has been corrected to reference the real standards:
>
> - **Google A2A v1.0**: https://github.com/google/A2A (Linux Foundation JDF, March 2026)
> - **IETF draft-klrc-aiagent-auth-02**: WIMSE/SPIFFE agent identity (expires Dec 2026)
> - **KGC-001**: Re-scoped to reference real A2A v1.0 + draft-klrc-aiagent-auth-02
>
> The corrected implementation is at `src/omega/oracle/a2a_bridge.py`.
> See `data/entities/roc_racoon/workspace/A2A_AGENT_CARD_SPEC.md` for the full spec.

---

**Project**: Omega Engine Handoff Alignment
**Entity**: @pillar P7 (Context)
~~**Standard**: IETF AAIF (Autonomous Agent Interchange Format) v3.0 (draft-schemacommons-aaif-00)~~
**Standard**: ~~AAIF~~ **[CORRECTION: Google A2A v1.0 + IETF draft-klrc-aiagent-auth-02]**
**Status**: ~~PROPOSED~~ **SUPERSEDED (see correction notice above)**
**Date**: 2026-06-28
**Source**: MaKaLi Council Run-Side (Lilith → P7 Context)

---

> **NOTE**: All references to ~~AAIF~~ below refer to the fabricated spec. They have been preserved for audit purposes but are superseded by the real A2A v1.0 and draft-klrc-aiagent-auth-02 standards. All ~~AAIF~~ references should be read as "Google A2A v1.0" for the protocol layer and "draft-klrc-aiagent-auth-02" for the authentication layer.

---

## ~~1. AAIF Mapping Specification~~ **1. Corrected: A2A Mapping Specification**

The Omega HandoffPacket is a runtime-specific delegation record. ~~To achieve AAIF compatibility, it must be mapped to the AAIF Agent State Document (Section 8.1) and the AAIF Agent Definition (Section 4).~~
**[CORRECTION: The HandoffPacket maps to A2A Agent Cards + Task messages.]**

### ~~1.1 Field Mapping Table~~ **1.1 Corrected Field Mapping (A2A v1.0 + draft-klrc-aiagent-auth-02)**

| Omega HandoffPacket Field | ~~AAIF Semantic Equivalent~~ A2A Equivalent | Location | Mapping Logic |
|--------------------------|--------------------------|---------------|---------------|
| `packet_id` | ~~state_id~~ task_id | A2A Task | Direct mapping (UUID v4) |
| `source_agent` | ~~provenance.source_platform~~ source_agent | A2A Task.source | SPIFFE ID of source entity |
| `target_agent` | ~~agent_id~~ target_agent | A2A Task.target | SPIFFE ID of target entity |
| `parent_trace_id` | ~~traceparent~~ trace_id | A2A metadata | Map to W3C Trace Context header |
| `trace_id` | ~~span_id~~ trace_id | A2A metadata | Map to current telemetry span |
| `task_type` | ~~goal / role~~ skill_id | A2A Task.skills | Map task_type to a specific A2A skill |
| `task_description` | ~~instructions~~ instructions | A2A Task.input | Map description to task input |
| `relevant_files` | ~~context[]~~ context | A2A Task.context | Map file paths to context sources |
| `context` | ~~variables~~ variables | A2A Task.metadata | Map to task-scope variables |
| `expected_output` | ~~evaluation.test_cases~~ output | A2A Task.output | Map output requirements |
| `ttl_seconds` | ~~timeout~~ ttl | A2A Task.ttl | Direct mapping |
| `status` | ~~status~~ status | A2A Task.status | Map pending -> submitted |
| `result` | ~~conversation[]~~ artifacts | A2A Task.artifacts | Append result as final artifact |

---

## ~~2. State Checkpointing Strategy~~ **2. State Checkpointing Strategy (Unchanged)**

To implement "Sovereign Continuity" (M15) and "SomaticState" (M20), Omega will use a **Hybrid Somatic-Semantic Checkpoint**.

### 2.1 The Checkpoint Payload

The checkpoint will be a serialized ~~AAIF Agent State Document~~ **[CORRECTION: A2A Card + SomaticState bundle]** containing:

1. **Somatic Layer (Binary)**: A base64-encoded blob of the model's KV cache and internal state captured via `llama_copy_state_data` (SomaticState M20).
2. **Semantic Layer (JSON)**:
   - Memory Pointers: Offsets and keys for the Hot/Warm/Cold memory tiers.
   - Cognitive State: The current `focus_chain` and `decisions` list mapped to ~~AgentState.variables~~ **[CORRECTION: A2A Task metadata]** .
   - Pipeline Position: Current step in the HandoffPacket sequence.
3. **Integrity Layer**: A SHA-256 checksum of the canonical JSON (excluding the checksum field).

### ~~2.2 The 7-Step Migration Protocol (AAIF §8.2)~~ **2.2 The 7-Step Migration Protocol (A2A Mapping)**

Omega will implement cross-platform migration as follows:

1. **Capture**: SomaticState capture -> A2A Card + Task JSON generation.
2. **Token**: Generate a signed, short-lived `migration_token` (15m expiry).
3. **Transfer**: Stream the state via ~~application/x-aaif-handoff+ndjson~~ **[CORRECTION: JSON-RPC 2.0 over HTTP]** .
4. **Verify**: Recipient verifies checksum and migration_token via ~~AAIF~~ **[CORRECTION: draft-klrc-aiagent-auth-02 SPIFFE verification]** .
5. **Import**: Restore SomaticState -> Hydrate memory -> Resume pipeline.
6. **Re-issue**: Re-evaluate tool calls against the new platform's tool catalogue.
7. **Resume**: Trigger the agent's think loop.

---

## ~~3. Conformance Level Analysis~~ **3. Capability Mapping (A2A v1.0)**

~~AAIF defines 7 cumulative levels (Core -> Stateful).~~
**[CORRECTION: A2A v1.0 defines capability negotiation per Agent Card.]**

### ~~3.1 Recommendation: Level 7 (Stateful)~~ **3.1 Recommendation: Full Agent Card Coverage**

~~**Omega Engine MUST target Level 7 (Stateful) conformance.**~~
**[CORRECTION: Omega Engine MUST generate complete A2A Agent Cards for all entities.]**

Rationale:
- ~~**Sovereignty**: Levels 1-6 focus on definition (how to start an agent). Level 7 focuses on state (how to move a living agent).~~ **[CORRECTION: A2A Agent Cards publish entity capabilities for discovery. The more complete the card, the more discoverable the entity.]**
- ~~**Mandate Alignment**: Level 7 is the only level that supports `state.checkpoint`, which is the formal requirement for Mandate 11 (Soul Integrity) and Mandate 15 (Sovereign Continuity).~~ **[CORRECTION: A2A Cards directly support M15 (Sovereign Continuity) via SPIFFE identity and M11 (Soul Integrity) via skill enumeration.]**
- ~~**Competitive Advantage**: By achieving Level 7, Omega becomes the first sovereign runtime capable of "Live Migration" of AI souls across different local hardware/providers.~~ **[CORRECTION: By publishing Agent Cards, Omega enables cross-platform agent discovery — a critical step toward community-scale sovereign AI.]**

---

## 4. Verification Gates (Temple-Grade)

| Gate | Name | Verification Method | Success Criteria |
|------|------|---------------------|------------------|
| ~~T-AAIF-1~~ T-A2A-1 | Schema Validation | Run ~~aaif-validator~~ **[CORRECTION: A2A schema validation]** on exported Agent Card JSON | 0 validation errors |
| ~~T-AAIF-2~~ T-A2A-2 | Integrity Guard | Modify 1 byte of state blob -> Attempt restore | Restore MUST fail with ChecksumMismatchError |
| ~~T-AAIF-3~~ T-A2A-3 | Somatic Fidelity | Capture state -> Restore -> Prompt | Output must match original session output |
| ~~T-AAIF-4~~ T-A2A-4 | Capability Negotiation | Request restore on platform without state.checkpoint | Platform MUST reject with UnsatisfiedCapabilityError |

---

*Source: MaKaLi Council Run-Side -> P7 Context Pillar*
*Reported by: @pillar P7 (Context)*
*Date: 2026-06-28*
*Corrected: 2026-06-29*
