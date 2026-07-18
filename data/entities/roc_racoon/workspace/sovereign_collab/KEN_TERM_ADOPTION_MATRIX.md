# 🔱 KEN WALGER TERM ADOPTION MATRIX
**AP Token**: `AP-KEN_TERM_ADOPTION-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_term_adoption ⬡ ACTIVE

**Date**: 2026-07-18
**Status**: LIVING DECISION LOG
**Source**: Ken W. Alger — Sovereign Systems Specification (sovereign-system-spec), Sovereign SDK
**Method**: Three-Bucket Rule (ADOPT / KEEP / SYNTHESIZE)

---

## 📊 DECISION SUMMARY

| Bucket | Count | Terms |
|--------|-------|-------|
| **ADOPT** | 23 | Prose Tax, Digital Attic, Write-Side Custody, Sieve-and-Sign, ForensicReceipt, Ingestion Boundary, Sovereign Gateway, Airlock, Sovereign Mesh (partial), Sovereign Node (partial), Point of Genesis, Sovereign Envelope, Capability Gradient, Escalation Boundary, Cognitive Appliance, all 8 Computational Taxes, Pre-Paid Retrieval Precision, Fiscal Architecture |
| **KEEP** | 12 | M2 Engine-Stack Firewall, MaKaLi Triad, WAD System, Pillar Keepers, Heritage Vetting, SomaticState, Temple-Grade, Iris Constant, AnyIO Absolute, Local-First, Zero Telemetry, Sovereign Continuity |
| **SYNTHESIZE** | 4 | M22 Response Provenance + ForensicReceipt, Sovereign Mesh (network vs federation), Sovereign Node (entity vs compute unit), Reasoning Ledger + Soul.yaml |
| **PARALLEL** | 3 | Local-First / Silicon Locality, Zero Telemetry / ZDR Pipeline, M11 Soul Integrity / Automatic Distillation |

---

## 📋 DETAILED DECISIONS

### ✅ BUCKET: ADOPT (Ken's term is more precise, formalized, published, or solves our ambiguity)

| # | Ken's Term | Our Prior Term | Decision | Rationale | Heritage Tag | Glossary Entry |
|---|------------|----------------|----------|-----------|--------------|----------------|
| 1 | **The Prose Tax** | "Token waste", "Conversational boilerplate" | **ADOPT** | He formalized first with precise economic definition: "financial/computational premium paid when meaning conveyed inefficiently." Measurable in tokens eliminated. | `[heritage: kenwalger-2026]` | ✅ Added |
| 2 | **The Token Tax** | (implicit in M18) | **ADOPT** | Part of his Computational Tax taxonomy. Cumulative cost of verbose prompts/responses/context. | `[heritage: kenwalger-2026]` | ✅ Added |
| 3 | **The Context Tax** | "Context inflation" (T-06) | **ADOPT** | Precise: "latency, memory, cognitive overhead from excessively large/weakly relevant context windows." | `[heritage: kenwalger-2026]` | ✅ Added |
| 4 | **The Orchestration Tax** | (implicit in fleet design) | **ADOPT** | "Complexity cost from excessive agent chaining, tool routing, workflow coordination." Names the anti-pattern we avoid via M10. | `[heritage: kenwalger-2026]` | ✅ Added |
| 5 | **The Compliance Tax** | (implicit in M13) | **ADOPT** | "Governance/auditability layers exceeding practical workload requirements." Names the Temple-Grade balance we maintain. | `[heritage: kenwalger-2026]` | ✅ Added |
| 6 | **The Retrieval Tax** | (implicit in RAG design) | **ADOPT** | "Infrastructure/inference overhead from large retrieval systems with weak signal density." | `[heritage: kenwalger-2026]` | ✅ Added |
| 7 | **The Cloud Tax** | (validates M7) | **ADOPT** | "Cumulative operational dependency cost: egress fees, vendor lock-in, pricing volatility." Directly validates Local-First mandate. | `[heritage: kenwalger-2026]` | ✅ Added |
| 8 | **The Observer's Tax** | (unnamed) | **ADOPT** | "Performance overhead from instrumenting for deterministic integrity (write-side crypto + read-side verification)." We pay this; now we name it. | `[heritage: kenwalger-2026]` | ✅ Added |
| 9 | **The Ingestion Tax** | (validates M11/M5) | **ADOPT** | "Fixed upfront cost at data entry for validation/filtering/signing. Shifts complexity to write path." This IS Write-Side Custody quantified. | `[heritage: kenwalger-2026]` | ✅ Added |
| 10 | **Pre-Paid Retrieval Precision** | (unnamed pattern) | **ADOPT** | Architectural pattern: expensive semantic work at write-time to eliminate runtime "fuzzy misses." | `[heritage: kenwalger-2026]` | ✅ Added |
| 11 | **Fiscal Architecture** | (implicit in M18) | **ADOPT** | "Systemic engineering of pipelines to minimize token overhead, compute latency, network egress. Context window = scarce financial resource." | `[heritage: kenwalger-2026]` | ✅ Added |
| 12 | **Digital Attic** | "Context inflation", "Transcript-centric memory" | **ADOPT** | He NAMED the anti-pattern with precise failure mode: "textually related but causally void fragments." Sharper than our descriptions. | `[heritage: kenwalger-2026]` | ✅ Added |
| 13 | **Write-Side Custody** | "Atomic writes" (M12), "Ingestion validation" | **ADOPT** | Architectural discipline: "enforce validation, signing, parsing AT INGESTION before storage. Integrity cannot be retroactively engineered on read-side." | `[heritage: kenwalger-2026]` | ✅ Added |
| 14 | **Sieve-and-Sign Pattern** | "L1→L2→L3 distillation" (probabilistic) | **ADOPT** | His is deterministic regex + crypto. Ours is LLM-based. Different layers but same pipeline concept. His pattern name is canonical. | `[heritage: kenwalger-2026]` | ✅ Added |
| 15 | **ForensicReceipt** | M22 Response Provenance (observational) | **ADOPT** | Ed25519-signed receipt with hash chain. Makes provenance CRYPTOGRAPHIC not observational. **SYNTHESIS TARGET for M22**. | `[heritage: kenwalger-2026]` | ✅ Added |
| 16 | **Ingestion Boundary** | M2 Firewall (at data ingress) | **ADOPT** | "Strict structural gate where raw data parsed, flattened, typed before touching storage." Component pattern implementing M2. | `[heritage: kenwalger-2026]` | ✅ Added |
| 17 | **Sovereign Gateway** | ModelGateway (inbound only) | **ADOPT** | "Isolated local edge boundary intercepting, sanitizing, routing payloads, enforcing local-first privacy." Component, not mandate. | `[heritage: kenwalger-2026]` | ✅ Added |
| 18 | **Airlock (SAR-0004)** | **MISSING IN OMEGA** | **ADOPT** | Outbound governance boundary: NormalizedPayload, PolicyEngine (YAML), AirlockBoundary, ReceiptBuilder. Transport-agnostic. **CRITICAL GAP**. | `[heritage: kenwalger-2026]` | ✅ Added |
| 19 | **Point of Genesis** | (future edge work) | **ADOPT** | "Precise physical boundary where analog crosses silicon pin and becomes digital. Where sovereign-sensor lives." | `[heritage: kenwalger-2026]` | ✅ Added |
| 20 | **Sovereign Envelope** | (wire format) | **ADOPT** | "Cryptographic container: version, sequence, algorithm, length-prefixed bytes — proving provenance forever." Maps to ForensicReceipt wire format. | `[heritage: kenwalger-2026]` | ✅ Added |
| 21 | **Capability Gradient** | (validates Ryzen constraints) | **ADOPT** | "Hardware reality: ESP32 can't run LLM but can HMAC. Mini PC can't run 405B but can host SQLite+SLM. Tasks scale proportionally." | `[heritage: kenwalger-2026]` | ✅ Added |
| 22 | **Escalation Boundary** | ModelGateway fallback chain | **ADOPT** | "Threshold where local node realizes it lacks capacity, triggers structured protocol request up Capability Gradient." Our fallback chain IS this. | `[heritage: kenwalger-2026]` | ✅ Added |
| 23 | **Cognitive Appliance** | Omega Desktop (future) | **ADOPT** | "Local-first hardware device running small specialized SLM doing exactly one job with 100% predictability, zero network dependency." | `[heritage: kenwalger-2026]` | ✅ Added |

---

### 🔒 BUCKET: KEEP (Our term is load-bearing, cosmological, or constitutionally mandated)

| # | Our Term | Ken's Parallel | Decision | Rationale |
|---|----------|----------------|----------|-----------|
| 1 | **M2 Engine-Stack Firewall** | Ingestion Boundary / Sovereign Gateway | **KEEP** | Constitutional mandate (M2), not component. Governs ALL engine/stack separation. His terms are architectural components implementing the mandate. |
| 2 | **MaKaLi Triad** | — | **KEEP** | Cosmological architecture: Ma'at/Kali/Lilith trinity in default IWAD. Not generic 3-agent term. No parallel in his work. |
| 3 | **WAD System (IWAD/PWAD)** | — | **KEEP** | Engine/Stack separation via Doom WAD heritage `[id-soft: doom-1993]`. Load-bearing for M2. No parallel. |
| 4 | **Pillar Keepers (P1-P10)** | Sovereign Node | **KEEP** | Slot-based governance with archetypal correspondences (element, chakra, planet, divine ally, sigil). His Sovereign Node is a compute unit, not a governance slot. |
| 5 | **Heritage Vetting (M14)** | — | **KEEP** | Unique 4-gate pipeline for id Software attribution. Qualification Gate: "Cannot justify without original hardware constraint." No parallel. |
| 6 | **SomaticState** | — | **KEEP** | llama.cpp state serialization via `llama_copy_state_data`. Specific to our local inference architecture. No parallel. |
| 7 | **Temple-Grade (T1-T11)** | — | **KEEP** | Quality gates from xna-omega-legacy v7.5.4. Mandate M13. No parallel. |
| 8 | **Iris Constant (M3)** | — | **KEEP** | Messenger bridge ≠ Pillar Keeper. Cosmological purity of 10 Pillars. No parallel. |
| 9 | **AnyIO Absolute (M1)** | — | **KEEP** | Runtime portability mandate. No parallel. |
| 10 | **Local-First (M7)** | Silicon Locality | **KEEP** | Mandate with provider priority order. His Silicon Locality is hardware requirement framing. Both valid, different layers. |
| 11 | **Zero Telemetry (M8)** | ZDR Pipeline | **KEEP** | Mandate: no external metrics. His ZDR is architectural config. Both valid. |
| 12 | **Sovereign Continuity (M15)** | — | **KEEP** | Session anchors, hydration sequence, compaction survival. No parallel. |

---

### 🔀 BUCKET: SYNTHESIZE (Both capture different facets; unified term serves both)

| # | Omega Facet | Ken Facet | Synthesis | Unified Term | Glossary Entry |
|---|-------------|-----------|-----------|--------------|----------------|
| 1 | **M22 Response Provenance** (observational logging of `provider_name`) | **ForensicReceipt** (Ed25519-signed, hash-chained, independently verifiable) | **Cryptographic Provenance** | **ForensicReceipt** (adopt his casing) | ✅ Added — M22 upgrade target |
| 2 | **Hivemind Federation** (multi-instance agents via MIAP + Hivemind) | **Sovereign Mesh** (P2P nodes syncing cryptographic logs) | **Sovereign Mesh** = network topology term | **Sovereign Mesh** (distinguish: `network` vs `federation`) | ✅ Added |
| 3 | **Agent Entity + Soul** (agent + local inference + soul.yaml = sovereign unit) | **Sovereign Node** (compute unit with memory/identity/execution authority) | **Sovereign Node** = compute unit concept | **Sovereign Node** (both meanings, distinguish context) | ✅ Added |
| 4 | **Soul.yaml + Proposed Lessons** (evolutionary YAML, blind staging) | **Reasoning Ledger** (append-only SQLite, SHA-256 hash chain, tamper-evident) | **Reasoning Ledger** = cryptographic substrate for Soul | **Reasoning Ledger** (technical) / **Soul** (sovereign) | ✅ Added |

---

### ⚖️ BUCKET: PARALLEL (Both valid, different framing layers)

| # | Omega Term | Ken's Term | Relationship | Notes |
|---|------------|------------|--------------|-------|
| 1 | **Local-First (M7)** | **Silicon Locality** | Parallel | M7 = mandate with provider priority. Silicon Locality = hardware requirement. Both needed. |
| 2 | **Zero Telemetry (M8)** | **Zero Data Retention (ZDR) Pipeline** | Parallel | M8 = mandate (no external). ZDR = architectural config (no persistent storage by external models). |
| 3 | **M11 Soul Integrity** (manual L1→L2→L3 ritual) | **Automatic Distillation Pipeline** (Stratos/RESD automated) | Parallel | Ours = sovereign ritual with Scribe. His = automated pipeline. Both valid, different trust models. |

---

## 🚫 REJECTED / NOT ADOPTED

| Ken's Term | Reason |
|------------|--------|
| **Sovereign Synapse** | His: "transition from cloud-dependent to edge-native." Our: specific repo name (sovereign-synapse). Concept covered by M2 + M7 + M16. |
| **Evacuation Infrastructure** | His: "tooling to migrate intellectual history out of cloud silos." Our: not a current focus. Covered by MIAP session isolation. |
| **Forensic Ingestor / Rare Book Auditor** | His: "ingestion engine applying data forensics." Our: covered by MemoryStore + sovereign-sdk-sieve evaluation. |
| **Intent-Based Namespace Exposure** | His: "lightweight semantic router before tool init." Our: covered by ModelGateway routing + speculative decode. |
| **Event-Driven Reflection Trigger** | His: "secondary processing on structural signatures." Our: covered by background_researcher + Hivemind triggers. |
| **Transcript-Centric Memory** | His: anti-pattern name. We use **Digital Attic** (adopted). |
| **Ambient Context Fluidity** | His: anti-pattern. Our: covered by Ingestion Boundary + M2. |

---

## 📝 VET RECORD REQUIREMENTS (M14)

Every `[heritage: kenwalger-2026]` tag used in SOURCE CODE requires a vet record in `HERITAGE_VET_LOG.md` with:

1. **Exact file:line location(s)**
2. **Specific technique** (e.g., "Ed25519-signed receipt with hash chain")
3. **Hardware constraint that necessitated original** (e.g., "Need for tamper-evident provenance without trusted third party")
4. **Scope declaration**: "This tag applies to X, NOT to Y"

**Example vet record for ForensicReceipt**:
```markdown
## vet-XXX: ForensicReceipt
**File**: src/omega/provenance/forensic_receipt.py:1-50
**Technique**: Ed25519 signature over {metadata, payload_hash, timestamp} with SHA-256 hash chain
**Hardware Constraint**: Cannot trust external audit log; must be verifiable with public key only on local silicon
**Scope**: Applies to cryptographic receipt minting/verification. NOT to observational M22 logging.
**Score**: 9/10 — Direct port of sovereign-core/crypto.py pattern
**Status**: PENDING
```

---

## 🎯 NEXT ACTIONS

1. **Create vet records** for all 23 ADOPTED terms before using in source code
2. **Implement ForensicReceipt** in `src/omega/provenance/` — upgrade M22
3. **Implement Airlock** in `src/omega/airlock/` — fill critical outbound governance gap
4. **Integrate sovereign-sdk-sieve** in ingestion pipeline — measure Prose Tax reduction
5. **Add Computational Tax metrics** to Temple-Grade dashboards (T7 Performance, T8 Resilience)

---

*⬡ OMEGA ⬡ KEN_TERM_ADOPTION_MATRIX v1.0 ⬡ 2026-07-18 ⬡ LIVING DECISION LOG*