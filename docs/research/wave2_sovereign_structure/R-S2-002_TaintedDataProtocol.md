<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R-S2-002: Tainted Data Protocol (TDP) — Security Layer
**AP Token**: `AP-S2-002-TDP-v1.0.0`
**Status**: PROPOSED
**Wave**: 2 (Sovereign Structure)

## 1. Objective
Develop a rigorous security layer to isolate untrusted external data (web-fetches, user-provided files) from the system prompt, preventing prompt injection and data poisoning.

## 2. Current State Analysis
Existing `TDPGate` in `src/omega/oracle/security.py` uses syntactic isolation markers (`### [EXTERNAL DATA START]`). While effective for basic queries, it is vulnerable to sophisticated "jailbreak" patterns that mimic the markers.

## 3. Technical Specification

### 3.1 Multi-Tier Isolation
TDP will employ three layers of defense:

#### Layer 1: Syntactic Isolation (Existing)
Wrap tainted data in distinct, non-natural language markers.
`[TDP-S1] -> ### [EXTERNAL DATA START] ... ### [EXTERNAL DATA END]`

#### Layer 2: Semantic Guard (New)
Integrate a "Guard Model" (lightweight, e.g., Qwen-0.6B) to pre-scan tainted content for injection patterns before it reaches the main model.
- **Input**: Tainted String
- **Output**: `SAFE` | `TAINTED` | `MALICIOUS`
- **Action**: If `MALICIOUS`, block entirely. If `TAINTED`, apply aggressive sanitization.

#### Layer 3: Structural Isolation (New)
Force tainted data into a structured format (JSON) within the prompt to signal to the LLM that the content is data, not instructions.
`[TDP-S3] -> {"source": "...", "content": "...", "taint_level": 2}`

### 3.2 Taint Level Matrix
| Level | Label | Source | Handling |
|---|---|---|---|
| 1 | External | Trusted Domains (GitHub, etc) | S1 + S3 |
| 2 | High-Risk | General Web | S1 + S2 + S3 |
| 3 | Malicious | Blocklisted / Guard-detected | DROP |

## 4. Trade-off Analysis

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| **Regex Sanitization** | Extremely fast | Easily bypassed | INSUFFICIENT |
| **Marker Isolation** | Simple, low overhead | Vulnerable to marker mimicry | BASELINE |
| **Guard Model** | High accuracy, semantic | Added latency (100-200ms) | **ACCEPTED** |

## 5. Sovereign Mandate Alignment
- **Mandate 8 (Zero Telemetry)**: Guard model must be local-first.
- **Mandate 13 (Temple-Grade)**: Implements T6 (Security) gate.
