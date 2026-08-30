<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Research: A2A Communication Protocol
**AP Token**: `AP-RESEARCH-A2A-PROTOCOL-v1.0.0`
**Status**: PROPOSED / BLUEPRINT
**Owner**: Jem / Pillar P4 (Integration)

## 🎯 Objective
Define a machine-readable, interoperable protocol for Agent-to-Agent (A2A) delegation, allowing the Omega Engine to coordinate with other sovereign agents via a standardized "Task-based" interaction model.

## 🛠️ Architectural Design

### 1. Core Abstractions
The protocol treats every interaction as a `Task` dispatch rather than a simple chat message.

- **Agent Card**: A JSON manifest served at `/.well-known/agent.json` describing:
    - `capabilities`: List of skills, tools, and domains.
    - `endpoint`: The A2A communication URL.
    - `policy`: Budget limits, security requirements, and response time expectations.
- **Task Object**: The atomic unit of work.
    - `taskId`: UUID for tracking.
    - `contextId`: Shared session ID for multi-turn continuity.
    - `input_artifacts`: Typed data (text, files, JSON) required for the task.
    - `instructions`: The specific goal for the remote agent.
    - `output_schema`: A Pydantic/JSON-schema for the expected result.
- **Artifact**: The output of a task.
    - `type`: (e.g., `research_report`, `code_snippet`, `json_data`).
    - `content`: The actual data.
    - `metadata`: Provenance, confidence score, and timestamps.

### 2. Interaction Lifecycle
The protocol is natively asynchronous to support long-running cognitive work.

`Discovery (Agent Card)` $\rightarrow$ `Task Submission (POST /tasks)` $\rightarrow$ `Execution (Remote Agent)` $\rightarrow$ `Status Polling / Webhooks` $\rightarrow$ `Artifact Retrieval`.

**State Transitions**:
`SUBMITTED` $\rightarrow$ `WORKING` $\rightarrow$ `INPUT_REQUIRED` (Clarification) $\rightarrow$ `COMPLETED` / `FAILED`.

### 3. Integration with Link P9 (Orchestrator)
Link P9 acts as the Omega Engine's A2A Gateway:
- **Outbound**: P9 translates an internal `delegate()` call into an A2A `Task` object and handles the polling/webhook lifecycle.
- **Inbound**: P9 exposes an A2A endpoint, allowing external agents to "summon" Omega entities by treating them as A2A servers.

## 📉 Risk & Mitigation
- **Security**: Untrusted agents could send malicious tasks. *Mitigation*: Implement HMAC-signed task envelopes and a "Sandbox" for remote artifacts.
- **Interoperability**: Different agents use different schemas. *Mitigation*: Strict adherence to the Linux Foundation A2A standard with a "Translation Layer" for legacy agents.

## 🔖 Heritage
This pattern derives from: `[Google A2A Protocol / Linux Foundation A2A Standard 2025]`
Evolution: Integrates with Omega's P9 Orchestrator for seamless internal/external delegation.
