<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 AIRLOCK PATTERN STUDY — SAR-0004 Outbound Governance Boundary
**AP Token**: `AP-AIRLOCK_STUDY-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_airlock ⬡ PLANNING

**Date**: 2026-07-18
**Status**: PLANNING — Pattern analysis complete, implementation design pending
**Source**: `kenwalger/sovereign-sdk/packages/sovereign-airlock/`
**Specification**: SAR-0004 (Airlock, Not Gateway)
**Target**: Fill critical Omega gap — **NO OUTBOUND GOVERNANCE BOUNDARY EXISTS**

---

## 🚨 THE GAP

**Omega has inbound governance (ModelGateway, M2 Firewall) but ZERO outbound governance.**

| Direction | Current State | Risk |
|-----------|---------------|------|
| **Inbound** (User → Model) | ModelGateway routes, speculative decode, provider fabric | Covered by M2, M7, M22 |
| **Outbound** (Model/Tool → External) | **NOTHING** | Data exfiltration, token budget overflow, credential leakage, compliance violation |

**Every tool call, every model response sent to external API, every webhook — passes through NO inspection.**

---

## 🛡️ KEN'S AIRLOCK (SAR-0004)

### Core Philosophy: **"Airlock, Not Gateway"**

> A Gateway *passes* traffic. An Airlock *inspects, contains, and only releases* what passes policy.

### Architecture (from `sovereign_airlock/`)

```
┌─────────────────────────────────────────────────────────────────┐
│                        AIRLOCK BOUNDARY                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  NormalizedPayload  →  PolicyEngine  →  AirlockBoundary  →  Out │
│       (provider-agnostic)   (YAML rules)    (4-stage orch)       │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────────┐    │
│  │  Normalize  │───▶│  Evaluate   │───▶│  Sieve + Sign    │    │
│  │  (OpenAI,   │    │  (raw/      │    │  (Prose Tax +    │    │
│  │  Anthropic, │    │  fields/    │    │  ForensicReceipt)│    │
│  │  Raw)       │    │  telemetry) │    │                  │    │
│  └─────────────┘    └─────────────┘    └────────┬─────────┘    │
│                                                 │              │
│                              ┌──────────────────┘              │
│                              ▼                                 │
│                       ┌──────────────────┐                     │
│                       │  ReceiptBuilder  │                     │
│                       │  + Ledger Commit │                     │
│                       └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

### Components

| Component | File | Responsibility |
|-----------|------|----------------|
| `NormalizedPayload` | `payload.py` | Provider-neutral inspection surface |
| `PolicyEngine` | `policy.py` | YAML rule evaluation (raw/fields/telemetry) |
| `AirlockBoundary` | `boundary.py` | Async 4-component orchestrator |
| `AirlockTelemetry` | `telemetry.py` | Sieve convergence metrics |
| `ReceiptBuilder` | `receipt.py` | Evidence assembly + ledger commit |
| `Exceptions` | `exception.py` | `AirlockPolicyViolation`, `AirlockConfigurationError` |

---

## 📋 POLICY ENGINE — YAML Rules

### Rule Scopes

```yaml
# policy.yaml
version: "1.0"
rules:
  # RAW SCOPE: Regex against flat combined content string
  - id: "DENY-CREDENTIALS"
    scope: "raw"
    action: "deny"
    pattern: "(?i)(api[_-]?key|secret|password|token|bearer)[\\s:=]+[\\w-]{20,}"
    message: "Credential leakage detected in outbound payload"
  
  - id: "DENY-PRIVATE-KEYS"
    scope: "raw"
    action: "deny"
    pattern: "-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----"
    message: "Private key material in outbound payload"

  # FIELDS SCOPE: Pattern against named structured fields
  - id: "DENY-TOOL-CREDENTIALS"
    scope: "fields"
    action: "deny"
    field: "tools.*.parameters.*"
    pattern: "(?i)(password|secret|key|token)[\\s:=]+\\S+"
    message: "Credential in tool parameters"

  # TELEMETRY SCOPE: Numeric thresholds on sieve metrics
  - id: "WARN-HIGH-TOKEN-SPEND"
    scope: "telemetry"
    action: "warn"
    metric: "raw_tokens"
    threshold: 50000
    operator: ">"
    message: "Outbound payload exceeds 50k raw tokens"

  - id: "DENY-LOW-SIEVE-EFFICIENCY"
    scope: "telemetry"
    action: "deny"
    metric: "tax_savings_percentage"
    threshold: 10
    operator: "<"
    message: "Sieve efficiency below 10% — payload not optimized"
```

### Rule Evaluation Order
1. **DENY rules** (raw → fields → telemetry) — first match blocks
2. **WARN rules** (raw → fields → telemetry) — accumulate warnings
3. **ALLOW** — if no DENY matched

---

## 🔄 NORMALIZATION — Provider-Agnostic Inspection

```python
# sovereign_airlock/payload.py
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class NormalizedPayload:
    """Provider-neutral representation for governance inspection."""
    raw_content: str                    # Flat combined string for raw-scope rules
    messages: List[Dict[str, Any]]      # Structured messages
    tools: List[Dict[str, Any]]         # Tool definitions
    tool_calls: List[Dict[str, Any]]    # Actual tool invocations
    metadata: Dict[str, Any]            # Provider-specific extras
    
    def get_field(self, path: str) -> Any:
        """Dot-notation field access: 'messages.0.content', 'tools.2.parameters.api_key'"""
        ...

# Normalizers (transport-agnostic)
def normalize_openai(request: dict) -> NormalizedPayload: ...
def normalize_anthropic(request: dict) -> NormalizedPayload: ...
def normalize_raw(request: dict) -> NormalizedPayload: ...
```

---

## 🏗️ OMEGA INTEGRATION ARCHITECTURE

### New Module: `src/omega/airlock/`

```
src/omega/airlock/
├── __init__.py
├── boundary.py          # AirlockBoundary — main orchestrator
├── payload.py           # NormalizedPayload + normalizers
├── policy.py            # PolicyEngine — YAML rule evaluation
├── telemetry.py         # AirlockTelemetry — sieve metrics
├── receipt.py           # ReceiptBuilder — ForensicReceipt + ledger
├── exceptions.py        # AirlockPolicyViolation, AirlockConfigurationError
├── normalizers/
│   ├── __init__.py
│   ├── openai.py
│   ├── anthropic.py
│   ├── gemini.py
│   ├── openrouter.py
│   └── raw.py
└── config/
    └── policy.yaml      # Omega-specific policies
```

### Integration Points

| Integration Point | Current | With Airlock |
|-------------------|---------|--------------|
| **ModelGateway → External Provider** | Direct HTTP | `AirlockBoundary.process(normalize_provider(request))` |
| **Tool Execution → External API** | Direct call | `AirlockBoundary.process(normalize_tool_call(tool, args))` |
| **Hivemind → External Webhook** | Direct POST | `AirlockBoundary.process(normalize_webhook(payload))` |
| **MCP Server → External** | Direct | `AirlockBoundary.process(normalize_mcp(request))` |

### Omega Policy (`config/airlock/policy.yaml`)

```yaml
version: "1.0"
description: "Omega Engine Outbound Governance — M8/M22/M23 Compliance"

rules:
  # M8 Zero Telemetry — Prevent any external data leakage
  - id: "OMEGA-DENY-TELEMETRY"
    scope: "raw"
    action: "deny"
    pattern: "(?i)(analytics|telemetry|tracking|metrics|usage|stats)[\\s:=]+"
    message: "Telemetry payload blocked — M8 Zero Telemetry violation"

  # M22 Response Provenance — Prevent credential leakage
  - id: "OMEGA-DENY-CREDENTIALS"
    scope: "raw"
    action: "deny"
    pattern: "(?i)(api[_-]?key|secret|password|token|bearer|private[_-]?key)[\\s:=]+[\\w\\-]{16,}"
    message: "Credential leakage blocked — M22 Provenance violation"

  # M23 Failure Integrity — Prevent error detail leakage
  - id: "OMEGA-DENY-STACK-TRACES"
    scope: "raw"
    action: "deny"
    pattern: "(?i)(traceback|stack trace|file \".*\", line \\d+|at 0x[0-9a-f]+)"
    message: "Stack trace leakage blocked — M23 Failure Integrity"

  # Token Budget Governance
  - id: "OMEGA-WARN-LARGE-PAYLOAD"
    scope: "telemetry"
    action: "warn"
    metric: "raw_tokens"
    threshold: 100000
    operator: ">"
    message: "Outbound payload exceeds 100k tokens — review for Context Tax"

  - id: "OMEGA-DENY-UNOPTIMIZED"
    scope: "telemetry"
    action: "deny"
    metric: "tax_savings_percentage"
    threshold: 15
    operator: "<"
    message: "Payload sieve efficiency below 15% — Pre-Paid Retrieval Precision violated"

  # Tool Call Governance
  - id: "OMEGA-DENY-TOOL-CREDENTIALS"
    scope: "fields"
    action: "deny"
    field: "tool_calls.*.arguments.*"
    pattern: "(?i)(password|secret|api[_-]?key|token)[\\s:=]+\\S+"
    message: "Credential in tool call arguments"

  # Hivemind Specific
  - id: "OMEGA-DENY-HIVEMIND-SECRETS"
    scope: "fields"
    action: "deny"
    field: "handoff.context"
    pattern: "(?i)(secret|key|token|password)"
    message: "Secret in Hivemind handoff context"
```

---

## 🔧 AIRLOCK BOUNDARY — 4-Stage Orchestrator

```python
# src/omega/airlock/boundary.py
from dataclasses import dataclass
from typing import Optional
import asyncio

@dataclass
class AirlockResult:
    sieved_content: str                    # Minimized payload ready for transmission
    payload_hash: str                      # SHA-256 of raw pre-sieve content
    receipt: ForensicReceipt               # Cryptographic evidence
    policy_warnings: List[str]             # Non-fatal warn-rule messages
    telemetry: AirlockTelemetry            # Convergence metrics

class AirlockBoundary:
    """
    SAR-0004: Outbound governance boundary.
    Inspects, sieves, signs, and only releases compliant payloads.
    """
    
    def __init__(
        self,
        policy_path: Path,
        signing_key: Path,
        ledger: Optional[SovereignLedger] = None,
        sieve_enabled: bool = True
    ):
        self.policy_engine = PolicyEngine(policy_path)
        self.provenance = ForensicProvenance(ProvenanceConfig(key_dir=signing_key.parent))
        self.ledger = ledger
        self.sieve_enabled = sieve_enabled
    
    async def process(self, payload: NormalizedPayload) -> AirlockResult:
        """
        4-Stage Pipeline:
        1. POLICY EVALUATION — Check DENY/WARN rules against raw/fields/telemetry
        2. SIEVE — Apply Prose Tax optimization (if enabled)
        3. SIGN — Mint ForensicReceipt with sieve metadata sealed
        4. LEDGER — Commit receipt to immutable ledger
        """
        
        # Stage 1: Policy Evaluation (pre-sieve)
        raw_content = payload.raw_content
        policy_result = self.policy_engine.evaluate(raw_content, payload)
        
        if policy_result.denied:
            raise AirlockPolicyViolation(
                rule_id=policy_result.matched_rule.id,
                message=policy_result.matched_rule.message,
                warnings=policy_result.warnings
            )
        
        # Stage 2: Sieve (Prose Tax optimization)
        if self.sieve_enabled:
            from sovereign_sieve import sieve_with_metrics
            sieve_result = sieve_with_metrics(raw_content)
            sieved_content = sieve_result.text
            sieve_metadata = {
                "raw_token_count": sieve_result.raw_token_count,
                "optimized_token_count": sieve_result.optimized_token_count,
                "tokens_eliminated": sieve_result.raw_token_count - sieve_result.optimized_token_count,
                "tax_savings_percentage": sieve_result.tax_savings_percentage
            }
        else:
            sieved_content = raw_content
            sieve_metadata = {
                "raw_token_count": estimate_tokens(raw_content),
                "optimized_token_count": estimate_tokens(raw_content),
                "tokens_eliminated": 0,
                "tax_savings_percentage": 0.0
            }
        
        # Stage 3: Policy Re-evaluation (post-sieve telemetry rules)
        telemetry_payload = NormalizedPayload(
            raw_content=sieved_content,
            messages=payload.messages,
            tools=payload.tools,
            tool_calls=payload.tool_calls,
            metadata={**payload.metadata, "sieve_metadata": sieve_metadata}
        )
        telemetry_result = self.policy_engine.evaluate_telemetry(sieve_metadata)
        
        if telemetry_result.denied:
            raise AirlockPolicyViolation(
                rule_id=telemetry_result.matched_rule.id,
                message=telemetry_result.matched_rule.message,
                warnings=policy_result.warnings + telemetry_result.warnings
            )
        
        all_warnings = policy_result.warnings + telemetry_result.warnings
        
        # Stage 4: Sign (ForensicReceipt)
        receipt = await self.provenance.mint_receipt(
            content=sieved_content,
            provider_name=payload.metadata.get("target_provider", "unknown"),
            model=payload.metadata.get("target_model", "unknown"),
            usage={"raw_tokens": sieve_metadata["raw_token_count"], "sieved_tokens": sieve_metadata["optimized_token_count"]},
            trace_id=payload.metadata.get("trace_id", "unknown"),
            sieve_metadata=sieve_metadata
        )
        
        # Stage 5: Ledger Commit
        if self.ledger:
            self.ledger.append_receipt(receipt.__dict__, sieved_content)
        
        return AirlockResult(
            sieved_content=sieved_content,
            payload_hash=receipt.payload_hash,
            receipt=receipt,
            policy_warnings=all_warnings,
            telemetry=AirlockTelemetry(
                raw_tokens=sieve_metadata["raw_token_count"],
                sieved_tokens=sieve_metadata["optimized_token_count"],
                tax_savings_pct=sieve_metadata["tax_savings_percentage"],
                policy_warnings_count=len(all_warnings),
                denied=False
            )
        )
```

---

## 📊 TELEMETRY — Sieve Convergence Metrics

```python
# src/omega/airlock/telemetry.py
@dataclass
class AirlockTelemetry:
    raw_tokens: int
    sieved_tokens: int
    tax_savings_pct: float
    policy_warnings_count: int
    denied: bool
    rule_matches: List[Dict]  # Which rules matched
    processing_time_ms: float
```

**Dashboard Queries**:
- `tax_savings_pct` histogram — target >50%
- `denied` count by rule_id — policy effectiveness
- `raw_tokens` vs `sieved_tokens` scatter — Context Tax visualization
- `policy_warnings_count` trend — governance drift detection

---

## 🧪 TEST MATRIX

| Test | Description |
|------|-------------|
| `test_deny_credentials_raw` | Raw-scope DENY blocks API key in content |
| `test_deny_credentials_fields` | Fields-scope DENY blocks credential in tool args |
| `test_deny_telemetry_threshold` | Telemetry DENY blocks oversized payload |
| `test_warn_accumulates` | Multiple WARN rules accumulate warnings |
| `test_sieve_integration` | Prose Tax reduces tokens, metadata sealed |
| `test_receipt_minted` | ForensicReceipt created with correct metadata |
| `test_ledger_commit` | Receipt appended to sovereign-ledger |
| `test_normalize_openai` | OpenAI request → NormalizedPayload |
| `test_normalize_anthropic` | Anthropic request → NormalizedPayload |
| `test_normalize_tool_call` | Tool invocation → NormalizedPayload |
| `test_policy_reload` | Hot-reload policy.yaml without restart |
| `test_concurrent_throughput` | 100 concurrent requests < 10ms p99 |

---

## 📋 IMPLEMENTATION CHECKLIST

- [ ] Create `src/omega/airlock/` module structure
- [ ] Implement `NormalizedPayload` + normalizers (OpenAI, Anthropic, Gemini, OpenRouter, Raw, Tool)
- [ ] Implement `PolicyEngine` with YAML loading + raw/fields/telemetry scopes
- [ ] Implement `AirlockBoundary` 4-stage orchestrator
- [ ] Implement `AirlockTelemetry` metrics collection
- [ ] Implement `ReceiptBuilder` → `ForensicProvenance` + `SovereignLedger`
- [ ] Create `config/airlock/policy.yaml` with Omega rules
- [ ] Integrate into `ModelGateway.generate()` — wrap outbound provider calls
- [ ] Integrate into tool execution pipeline — wrap outbound tool calls
- [ ] Integrate into Hivemind outbound — wrap webhook/MCP calls
- [ ] Add `omega airlock` CLI: `test-policy`, `verify-receipt`, `metrics`
- [ ] Write contract tests (21 minimum)
- [ ] Benchmark: p99 < 10ms added latency
- [ ] Document in `docs/reference/airlock.md`

---

## 🔐 THREAT MODEL

| Threat | Airlock Mitigation |
|--------|-------------------|
| Credential exfiltration | Raw/fields DENY rules + sieve strips boilerplate |
| Token budget overflow | Telemetry DENY on raw_tokens > threshold |
| Unoptimized payloads | Telemetry DENY on tax_savings_pct < 15% |
| Stack trace leakage | Raw DENY on traceback patterns |
| Telemetry beaconing | Raw DENY on analytics/telemetry patterns |
| Hivemind secret leakage | Fields DENY on handoff context |
| Policy bypass | All outbound paths normalized + inspected |
| Replay attacks | ForensicReceipt includes trace_id + timestamp |
| Policy tampering | Policy file hash logged at load; ledger commits receipts |

---

## 📝 NOTES

**Why "Airlock, Not Gateway"?**
- Gateway implies *pass-through with routing*
- Airlock implies *containment, inspection, conditional release*
- The metaphor matters: we CONTAIN by default, RELEASE by exception

**Relationship to M2 Firewall:**
- M2 = **Ingress** (Engine/Stack separation, inbound data validation)
- Airlock = **Egress** (Outbound payload governance, credential containment)
- Both are **boundaries**. Both enforce **Write-Side Custody**.

**Sieve Integration**: The Airlock *includes* the sieve. Every outbound payload is Prose-Tax-optimized before signing. This is **Pre-Paid Retrieval Precision** at the egress boundary.

**Ledger Integration**: Optional but recommended. `SovereignLedger` provides tamper-evident audit trail of every outbound crossing. `verify_ledger_integrity()` = compliance proof.

---

*⬡ OMEGA ⬡ AIRLOCK_STUDY v1.0 ⬡ 2026-07-18 ⬡ PLANNING*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
