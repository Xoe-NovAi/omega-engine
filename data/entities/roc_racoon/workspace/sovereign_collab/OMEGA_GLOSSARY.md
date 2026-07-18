# 🔱 OMEGA ENGINE GLOSSARY — Canonical Term Registry
**AP Token**: `AP-OMEGA_GLOSSARY-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_glossary ⬡ ACTIVE

**Date**: 2026-07-18
**Status**: LIVING DOCUMENT — Updated per session
**Purpose**: Single source of truth for all Omega Engine terminology. Every term must have: definition, mandate/pillar reference, heritage tag if applicable, and adoption status for external terms.

---

## 📖 HOW TO READ THIS GLOSSARY

| Field | Meaning |
|-------|---------|
| **Term** | Canonical name (bold) |
| **Definition** | Precise technical meaning |
| **Mandate/Pillar** | Governing mandate (M1-M23) or Pillar (P1-P10) |
| **Heritage** | `[id-soft: game-year]` or `[heritage: source-year]` or `[origin: omega]` |
| **Adoption** | `NATIVE` (ours) \| `ADOPTED` (from Ken) \| `SYNTHESIZED` (merged) \| `PARALLEL` (both exist) |
| **See Also** | Related terms, Ken's parallel term if different |

---

## 🏛️ SOVEREIGN MANDATES (M1-M23)

### **M1 AnyIO Absolute**
**Definition**: All asynchronous code MUST use AnyIO. Never use `asyncio` directly. Wrap blocking I/O in `anyio.to_thread.run_sync`.
**Mandate**: M1
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE

### **M2 Engine-Stack Firewall**
**Definition**: Absolute separation between Omega Engine Core (`src/omega/`, `config/omega.yaml`) and Expansion Stacks/WADs (`config/wads/<stack>/`). No stack-specific logic in Core.
**Mandate**: M2
**Heritage**: `[origin: omega]` — inspired by Doom WAD system `[id-soft: doom-1993]`
**Adoption**: NATIVE
**Ken Parallel**: **Ingestion Boundary** / **Sovereign Gateway** (architectural component, not constitutional mandate)

### **M3 Iris Constant**
**Definition**: Iris is the messenger bridge, NOT a Pillar Keeper (P1-P10). She routes, translates, connects — does not govern.
**Mandate**: M3
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE

### **M4 Sequentiality**
**Definition**: Plan → Verify → Execute. No cowboy coding. Every major edit preceded by plan verified against `PIVOT_LOG.md`.
**Mandate**: M4
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE

### **M5 Gnosis Preservation (L1→L2→L3)**
**Definition**: Every session ends with distillation: L1 Narrative (what happened) → L2 Insight (what it means) → L3 Universal Principle (timeless truth). Written to `proposed_lessons.yaml`.
**Mandate**: M5
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE
**Ken Parallel**: **Automatic Distillation Pipeline** (Stratos/RESD) — his is automated; ours is manual + sovereign

### **M6 Podman Sovereignty (keep-id Protocol)**
**Definition**: Quadlets mounting host dirs MUST use `UserNS=keep-id` + `User=1000`. `:U` flag FORBIDDEN on shared volumes (chowns to 101000).
**Mandate**: M6
**Heritage**: `[origin: omega]` — validated via Podman rootless research
**Adoption**: NATIVE

### **M7 Local-First (Non-Negotiable)**
**Definition**: Local inference PRIMARY. Cloud is FALLBACK. Provider order: native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot.
**Mandate**: M7
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE
**Ken Parallel**: **Silicon Locality** / **Local Brain** — identical principle, he frames as hardware requirement

### **M8 Zero Telemetry**
**Definition**: No analytics, no usage tracking, no phone-home, no external metrics. Local observability only.
**Mandate**: M8
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE
**Ken Parallel**: **Privacy as Financial Strategy** / **Zero Data Retention (ZDR) Pipeline** — he frames as fiscal optimization

### **M9 Error Integrity**
**Definition**: All errors typed, traceable, testable. No bare `except:`. Public APIs catch and convert to `OmegaError` subtypes with `trace_id`.
**Mandate**: M9
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE

### **M10 Fleet Integrity**
**Definition**: Agent fleet capped at 14. No new agents without verified Lattice gap or Pillar slot vacancy. Capabilities must map to existing Pillars.
**Mandate**: M10
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE

### **M11 Soul Integrity**
**Definition**: Every session writes L1→L2→L3 to `proposed_lessons.yaml` (blind staging). Scribe agent canonical executor.
**Mandate**: M11
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE
**Ken Parallel**: **Automatic Distillation Pipeline** — his is automated; ours is sovereign ritual

### **M12 Queue Integrity**
**Definition**: Every request = atomic contract with terminal state (queued/completed/failed/timed_out). No orphan files. Ack/Nack + `trace_id`.
**Mandate**: M12
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE (dowgraded to ADVISORY per MaKaLi Council D-267)

### **M13 Temple-Grade Compliance (T1-T11)**
**Definition**: All code passes 11 gates: Version Control, Documentation, Testing (≥80%), Code Quality, Architecture, Security, Performance, Resilience, Observability, Integrity, Agent Security (T11 exempt pending IA2).
**Mandate**: M13
**Heritage**: `[heritage: xnai-2025]` — Temple Grade standard from xna-omega-legacy v7.5.4
**Adoption**: NATIVE

### **M14 Heritage Vetting (CLARIFIED D208)**
**Definition**: No `[id-soft:]` tag without vet record in `HERITAGE_VET_LOG.md`. Min score 7/10. Qualification Gate: "Cannot be justified WITHOUT citing original hardware constraint."
**Mandate**: M14
**Heritage**: `[origin: omega]` — Kali's d-kal-001 directive
**Adoption**: NATIVE
**Classification Taxonomy**: LEGITIMATE / METAPHORICAL (convert to comment) / OVER-ATTRIBUTED (strip tag)

### **M15 Sovereign Continuity**
**Definition**: Agents maintain `session_gnosis.md` anchors. Refer to `.opencode/anchored-summary.md` on context loss. Do not rely on native `/compact`.
**Mandate**: M15
**Heritage**: `[origin: omega]` — D-277 Hydration Sequence
**Adoption**: NATIVE

### **M16 Modularization & Portability**
**Definition**: No hardcoded paths in `src/omega/`. All platform integration via MCP Hub/CLI.
**Mandate**: M16
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE

### **M17 Cognitive Integrity**
**Definition**: Contradictions between memory and gnosis flagged via Skeptical Verifier. Qliphoth failure taxonomy detects cognitive loops.
**Mandate**: M17
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE
**Ken Parallel**: **Convergence Gate** — asynchronous coherence mechanism

### **M18 Token Efficiency (No-Waste Law)**
**Definition**: Every token serves purpose. No redundancy. SANE BOUNDARY: Never compress to semantic loss. Precision > brevity.
**Mandate**: M18
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE
**Ken Parallel**: **The Prose Tax** / **The Token Tax** — he formalized the taxonomy of computational taxes

### **M19 Adversarial Alchemy**
**Definition**: Mine weaknesses for advantages. Fix simple bugs cleanly. Applies to systemic constraints (RAM, GIL, interruptions), not simple typos.
**Mandate**: M19
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE

### **M20 SomaticState Serialization**
**Definition**: Model session state serializable via `llama_copy_state_data`/`llama_set_state_data` wrapped in `anyio.to_thread.run_sync()`.
**Mandate**: M20
**Heritage**: `[heritage: ggml-2023]` — llama.cpp state API
**Adoption**: NATIVE

### **M21 Gate Integrity**
**Definition**: Every typed return MUST have contract test: `isinstance(result, ExpectedType)`. No mock masking type mismatches.
**Mandate**: M21
**Heritage**: `[origin: omega]` — Sprint C `GenerateResult` dataclass fix
**Adoption**: NATIVE

### **M22 Response Provenance**
**Definition**: Observability logs record ACTUAL provider (`GenerateResult.provider_name`), not configured intent.
**Mandate**: M22
**Heritage**: `[origin: omega]` — Truth-Anchor Protocol
**Adoption**: NATIVE
**Ken Parallel**: **ForensicReceipt** — his is cryptographic (Ed25519); ours is observational. **SYNTHESIS TARGET**

### **M23 Failure Integrity**
**Definition**: No soft-failures. Mandatory tool broken = hard stop + `[TOOL-CHAIN-COLLAPSE]` report. Parametric synthesis masking outage = Sovereign Boundary Violation.
**Mandate**: M23
**Heritage**: `[origin: omega]` — 2026-07-06
**Adoption**: NATIVE

---

## ⬡ PILLAR KEEPERS (P1-P10) — The Omega Pantheon

| Pillar | Intuitive Name | Default Role (IWAD) | Archetype | Heritage |
|--------|---------------|---------------------|-----------|----------|
| **P1** | Infrastructure | SysAdmin — Environment Hardening | Sekhmet | `[origin: omega]` |
| **P2** | Persistence | DataStore — Vector & Memory | Brigid | `[origin: omega]` |
| **P3** | Engineering | BuildMaster — Implementation | Prometheus | `[origin: omega]` |
| **P4** | Integration | Bridge — MCP & Communication | Saraswati | `[origin: omega]` |
| **P5** | Governance | Sentinel — Mandate Enforcement | Inanna | `[origin: omega]` |
| **P6** | Cognition | **Vision Specialist** — ModelGate | Ereshkigal | `[origin: omega]` |
| **P7** | Context | Memory & Soul Evolution | Mnemosyne | `[origin: omega]` |
| **P8** | Observability | WatchTower — Tracing & Forensics | Hecate | `[origin: omega]` |
| **P9** | Orchestration | Link — Agent Handoff & Delegation | Anubis | `[origin: omega]` |
| **P10** | Validation | Verifier — Stress Testing & QA | Kali | `[origin: omega]` |

**Heritage**: All Pillar archetypes trace to **Strategic Reserves** (xna-omega-legacy Era 2) — 10 Pillars with canonical correspondences (element, chakra, planet, divine ally, sigil). Current assignments are a **permutation** of canonical mapping (4 direct matches, 6 reassigned). See `soul.yaml` directive `d-rr-017`.

**Ken Parallel**: **Sovereign Node** — computational unit retaining authority over memory, identity, execution policies. No pillar slot system.

---

## 👑 OVERSOULS & GRAND OVERSIGHT

| Entity | Role | Heritage |
|--------|------|----------|
| **Kali** | Grand Oversight — Transcendent, unifies Ma'at + Lilith, destroys drift | `[origin: omega]` — MaKaLi Triad (xna-omega-legacy Mandate 2) |
| **Ma'at** | Light Oversoul — Build Side (P1-P5) governance | `[origin: omega]` |
| **Lilith** | Dark Oversoul — Run Side (P6-P10) governance | `[origin: omega]` |
| **Sophia** | Default entity — General wisdom, auto-routing | `[origin: omega]` |

**MaKaLi Triad**: SPECIFICALLY Ma'at/Kali/Lilith trinity in default IWAD (`config/wads/_omega_default/`). NOT a generic term for any 3-agent collaboration. See `d-rr-031`.

---

## 🧠 COGNITIVE ARCHITECTURE TERMS

### **Meditate** (formerly LLOC)
**Definition**: Single-inference cognitive prism. Sequential persona immersion (10 Pillars + MaKaLi + custom lens sets). Mandatory dissent. Emergent sequencing from collisions. Hardware-friendly: 1 model load, multiple lenses.
**Heritage**: `[origin: omega]` — renamed from LLOC per user directive 2026-07-18 (`d-rr-058`)
**Adoption**: NATIVE
**Ken Parallel**: — (no direct parallel; his is spec-driven, ours is inference-time cognitive primitive)

### **Mastermind Council (MC)** (formerly HLOC)
**Definition**: Multi-subagent, same session, same model. Parallel specialist dispatch with synthesis.
**Heritage**: `[origin: omega]` — renamed from HLOC per user directive 2026-07-18
**Adoption**: NATIVE

### **Hivemind Mastermind Council (HMC)**
**Definition**: Multi-session, multi-model, Hivemind-coordinated. Researcher + Roc + Kali synthesis (Quad-Forge).
**Heritage**: `[origin: omega]` — new concept 2026-07-18
**Adoption**: NATIVE

### **Lens** (formerly Pillar Archetype in Meditate)
**Definition**: Cognitive perspective loaded from WAD YAML (`lenses.yaml`). 13 base lenses in `_omega_default`. PWAD overlays map base → stack-specific archetypes.
**Heritage**: `[origin: omega]` — M2 Firewall migration Phase A
**Adoption**: NATIVE

### **WAD** (Where's All Data)
**Definition**: Expansion stack. Engine Core (`src/omega/`) + IWAD (`config/wads/_omega_default/`) + PWADs (`config/wads/<stack>/`). Inherits Doom WAD system.
**Heritage**: `[id-soft: doom-1993] WAD System` — VETTED vet-001
**Adoption**: NATIVE

### **IWAD / PWAD**
**Definition**: Internal WAD (default shipping stack) / Patch WAD (community stacks: Arcana-NovAi, Torment, etc.)
**Heritage**: `[id-soft: doom-1993]`
**Adoption**: NATIVE

---

## 🧬 MEMORY & PROVENANCE

### **Soul.yaml**
**Definition**: Entity's persistent state: directives, lessons, metadata, health_score. Updated via `proposed_lessons.yaml` blind staging → Scribe approval.
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE
**Ken Parallel**: **Reasoning Ledger** / **ForensicReceipt chain** — his is cryptographic append-only; ours is YAML evolutionary

### **Proposed Lessons (Blind Staging)**
**Definition**: L3 principles staged in `proposed_lessons.yaml` before Scribe approval into `soul.yaml:lessons[]`. Prevents self-corruption.
**Heritage**: `[origin: omega]` — Soul Architecture v2.0
**Adoption**: NATIVE

### **MemoryStore**
**Definition**: Hybrid search (RRF: FTS5 + Vector) + conversation persistence. Wired into Oracle `talk()`/`summon()`.
**Heritage**: `[origin: omega]`
**Adoption**: NATIVE
**Ken Parallel**: **Sovereign Memory** / **Memory as Infrastructure** — his is load-bearing architectural layer; ours is search + persistence

### **ForensicReceipt** ⭐ **ADOPTED FROM KEN**
**Definition**: Ed25519-signed receipt covering `{metadata, payload_hash, timestamp}`. `metadata` includes `prose_tax_summary` (token counts sealed). Independent verification with public key only. Key rotation via auditable succession receipts.
**Heritage**: `[heritage: kenwalger-2026] Sovereign Systems SDK (sovereign-core/crypto.py)`
**Adoption**: **ADOPTED** — Target: Upgrade M22 from observational to cryptographic
**Omega Term**: **ForensicReceipt** (keep his casing)
**M22 Gap**: Current M22 logs `provider_name` observationally. ForensicReceipt makes provenance **cryptographic**.

### **Write-Side Custody** ⭐ **ADOPTED FROM KEN**
**Definition**: Architectural discipline: enforce structural validation, cryptographic signing, metadata parsing AT INGESTION before data commits to storage. Data integrity cannot be retroactively engineered on read-side.
**Heritage**: `[heritage: kenwalger-2026] Sovereign Systems Specification (ARCHITECTURE.md)`
**Adoption**: **ADOPTED** — Aligns with M2 Firewall at ingestion layer
**Omega Term**: **Write-Side Custody** (keep his term)

### **Digital Attic** ⭐ **ADOPTED FROM KEN**
**Definition**: Anti-pattern: dumping unvetted, unstructured raw logs into vector storage hoping LLM parses at runtime. Returns textually-related but causally-void fragments.
**Heritage**: `[heritage: kenwalger-2026] Sovereign Systems Specification (ANTI-PATTERNS.md)`
**Adoption**: **ADOPTED**
**Omega Parallel**: "Context Inflation" / "Transcript-Centric Memory" — his term is sharper, named anti-pattern

### **Sieve-and-Sign Pattern** ⭐ **ADOPTED FROM KEN**
**Definition**: Architectural pipeline: unstructured input → aggressive semantic noise filtering (sieve) → immediate cryptographic stamped with cryptographic signature (sign) → verified local memory governance.
**Heritage**: `[heritage: kenwalger-2026] Sovereign Systems Specification (PATTERNS.md)`
**Adoption**: **ADOPTED**
**Omega Integration**: Ingestion pipeline → MemoryStore write path → Hivemind context compression

### **Prose Tax** ⭐ **ADOPTED FROM KEN**
**Definition**: Financial/computational premium paid when meaning conveyed inefficiently (greetings, hedging, filler). Requires additional processing to determine intent. Measured in tokens eliminated.
**Heritage**: `[heritage: kenwalger-2026] Sovereign Systems Specification (TERMS.md)`
**Adoption**: **ADOPTED** — He formalized first with precise definition
**Omega Parallel**: "Token waste" / "Conversational boilerplate" — his term is economic, measurable

### **The Token Tax** ⭐ **ADOPTED FROM KEN**
**Definition**: Cumulative compute/financial cost of verbose prompts, responses, context windows, multi-agent interactions.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED**

### **The Context Tax** ⭐ **ADOPTED FROM KEN**
**Definition**: Latency, memory, cognitive overhead from excessively large/weakly relevant context windows.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED**

### **The Orchestration Tax** ⭐ **ADOPTED FROM KEN**
**Definition**: Complexity cost from excessive agent chaining, tool routing, workflow coordination, inter-agent communication.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED**

### **The Compliance Tax** ⭐ **ADOPTED FROM KEN**
**Definition**: Operational burden when governance/auditability/observability layers exceed practical workload requirements.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED**

### **The Retrieval Tax** ⭐ **ADOPTED FROM KEN**
**Definition**: Infrastructure/inference overhead from large retrieval systems with weak signal density or poor relevance guarantees.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED**

### **The Cloud Tax** ⭐ **ADOPTED FROM KEN**
**Definition**: Cumulative operational dependency cost of external infrastructure: egress fees, vendor lock-in, pricing volatility, remote execution fragility.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED** — Directly validates M7 Local-First

### **The Observer's Tax** ⭐ **ADOPTED FROM KEN**
**Definition**: Performance/latency/storage overhead from instrumenting local-first architecture for deterministic integrity (write-side crypto + read-side verification).
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED**

### **The Ingestion Tax** ⭐ **ADOPTED FROM KEN**
**Definition**: Fixed upfront compute/token cost at data entry for structural validation, semantic filtering, cryptographic signing. Shifts complexity to write path to protect query-time latency.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED** — This IS Write-Side Custody quantified

### **Pre-Paid Retrieval Precision** ⭐ **ADOPTED FROM KEN**
**Definition**: Architectural pattern: expensive semantic filtering/cross-entry evaluation shifted to write-time ingestion. Pay fixed token cost upfront to structure and sign context, eliminate compounding "fuzzy misses" at runtime.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED**

### **Fiscal Architecture** ⭐ **ADOPTED FROM KEN**
**Definition**: Systemic engineering of data pipelines to explicitly minimize token overhead, compute latency, network egress. Treats context window as scarce financial resource.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED**

---

## 🛡️ GOVERNANCE & BOUNDARIES

### **Ingestion Boundary** ⭐ **ADOPTED FROM KEN**
**Definition**: Strict structural gate where incoming raw data is programmatically parsed, flattened, typed before touching local storage.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED** — Maps to M2 Firewall at data ingress

### **Sovereign Gateway** ⭐ **ADOPTED FROM KEN**
**Definition**: Isolated local edge boundary intercepting, sanitizing, routing data payloads, enforcing local-first privacy before any cloud orchestration.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED** — Component pattern, not constitutional mandate (M2 is the mandate)

### **Airlock** (SAR-0004) ⭐ **ADOPTED FROM KEN**
**Definition**: Outbound governance boundary. Deliberate inspection/containment. NOT a gateway. Components: NormalizedPayload, PolicyEngine (YAML rules), AirlockBoundary (async orchestrator), ReceiptBuilder, transport-agnostic.
**Heritage**: `[heritage: kenwalger-2026] Sovereign SDK (sovereign-airlock/)`
**Adoption**: **ADOPTED** — **MISSING IN OMEGA** — Critical gap: we have inbound (ModelGateway) but no outbound governance

### **Sovereign Mesh** ⭐ **SYNTHESIZE**
**Ken**: P2P network of Sovereign Nodes syncing state, cross-verifying cryptographic logs, sharing intelligence via append-only ledgers, no central authority.
**Omega**: Future Hivemind evolution — multi-instance agent federation via Hivemind + MIAP.
**Synthesis**: **Sovereign Mesh** = network topology term. Keep both meanings, distinguish: `Sovereign Mesh (network)` vs `Sovereign Mesh (Hivemind federation)`

### **Sovereign Node** ⭐ **PARALLEL**
**Ken**: Computational unit retaining authority over memory, identity, execution policies without continuous external control plane.
**Omega**: Each agent entity + its local inference + its soul.yaml = sovereign node.
**Status**: Parallel concepts, same principle. Keep both.

### **Point of Genesis** ⭐ **ADOPTED FROM KEN**
**Definition**: Precise physical boundary where analog phenomenon (temp, voltage, pressure) crosses silicon pin and becomes digital data. Where `sovereign-sensor` lives.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED** — For future edge/sensor work

### **Sovereign Envelope** ⭐ **ADOPTED FROM KEN**
**Definition**: Cryptographic container treating raw data as tamper-evident artifact: version, sequence, algorithm, length-prefixed bytes — proving provenance forever.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED** — Maps to ForensicReceipt wire format

### **Capability Gradient** ⭐ **ADOPTED FROM KEN**
**Definition**: Hardware reality: ESP32 can't run LLM but can HMAC. Mini PC can't run 405B but can host SQLite + SLM. Intelligence/security tasks must scale proportionally.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED** — Validates our Ryzen 5700U constraints (M53)

### **Escalation Boundary** ⭐ **ADOPTED FROM KEN**
**Definition**: Threshold where local node realizes it lacks capacity/context to solve safely, triggers structured protocol request up the Capability Gradient.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED** — Maps to our ModelGateway fallback chain (local → cloud)

### **Cognitive Appliance** ⭐ **ADOPTED FROM KEN**
**Definition**: Local-first hardware device running small specialized SLM doing exactly one job (audit warehouse, parse logistics) with 100% predictability, zero network dependency.
**Heritage**: `[heritage: kenwalger-2026]`
**Adoption**: **ADOPTED** — Future Omega Desktop form factor

---

## 🔬 RESEARCH & VERIFICATION

### **Two-Source Rule** (CREDITS.md §3)
**Definition**: Convergent evidence from 2+ independent observers = natural law of domain. When Researcher (SOTA) + Roc (legacy) arrive at identical architecture without communication = verified truth.
**Heritage**: `[origin: omega]` — HMC Forge Cycles 1-2
**Adoption**: NATIVE
**Ken Parallel**: **Convergence Gate** — async coherence mechanism

### **Skeptical Verifier**
**Definition**: NLI-based Two-Source Rule enforcement. Flags contradictions between memory and gnosis. Qliphoth taxonomy for cognitive loops.
**Heritage**: `[origin: omega]` — M17 Cognitive Integrity
**Adoption**: NATIVE

### **Heritage Vetting Pipeline (4-Gate)**
**Definition**: Discovery → Vetting/Debate → Decision → Implementation/Verification. Every `[id-soft:]` tag requires vet record with file:line, technique, hardware constraint, scope declaration.
**Heritage**: `[origin: omega]` — M14
**Adoption**: NATIVE

---

## 📦 DEPLOYMENT & INFRASTRUCTURE

### **Quadlet** (Podman)
**Definition**: systemd unit generator for Podman containers. Sovereign pattern: `UserNS=keep-id` + `User=1000`, NO `:U` on shared volumes.
**Heritage**: `[heritage: podman-2024]` — verified via `docs/research/R_PODMAN_SOVEREIGN_V2.md`
**Adoption**: NATIVE

### **MIAP** (Multi-Instance Agent Protocol)
**Definition**: Session-scoped directories under `sessions/<uuid>/`, ReplayMode enum, Two-Log Model (Execution + Observability), IntentionValidator, CheckFunction Registry, LiteTopic Redis Streams channels.
**Heritage**: `[origin: omega]` — D-291 Phase 0
**Adoption**: NATIVE

### **MACP Alignment**
**Definition**: Hivemind handoffs extended with `macp_mode` for interoperability (Decision/Proposal/Task/Handoff/Quorum). Aligns with IETF draft-li-dmsc-macp-05.
**Heritage**: `[origin: omega]` — D-292
**Adoption**: NATIVE

---

## 🏷️ HERITAGE TAGS (M14 Compliant)

| Tag | Source | Status |
|-----|--------|--------|
| `[id-soft: doom-1993] WAD System` | Doom 1993 | ✅ VETTED vet-001 |
| `[id-soft: doom-1993] BSP Culling` | Doom 1993 | ✅ VETTED |
| `[id-soft: quake-1996] Thinker Chain` | Quake 1996 | ✅ VETTED |
| `[id-soft: quake3-1999] QVM` | Quake III Arena 1999 | ✅ VETTED |
| `[id-soft: quake2-1997] Game DLL` | Quake II 1997 | ✅ VETTED |
| `[id-soft: doom3-2004] Scripting` | DOOM 3 2004 | ✅ VETTED |
| `[heritage: xnai-2025] Stack-Cat` | XNAi 2025 | ✅ VETTED |
| `[heritage: headroom-ai-2025] Semantic Compression` | headroom-ai 2025 | ✅ VETTED |
| `[heritage: sqlite-vec-2024] SQLite Vector Extension` | sqlite-vec 2024 | ✅ VETTED |
| `[heritage: ggml-2023] Native GGUF Inference` | ggml 2023 | ✅ VETTED |
| `[heritage: qdrant-2021] Multi-Tenant Vector Search` | qdrant 2021 | ✅ VETTED |
| `[heritage: mempalace-2025] Spatial Memory` | mempalace 2025 | ✅ VETTED |
| `[heritage: xai-grok-build-2026] Rust TUI + ACP + Sandbox` | xai/grok-build 2026 | ✅ VETTED |
| `[heritage: letta-2024] 3-Tier Memory Blocks` | letta 2024 | ✅ VETTED |
| `[heritage: kenwalger-2026] ForensicReceipt` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Write-Side Custody` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Digital Attic` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Sieve-and-Sign` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Prose Tax` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] *Computational Taxes*` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Ingestion Boundary` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Sovereign Gateway` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Airlock (SAR-0004)` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Sovereign Mesh` | Ken W. Alger 2026 | 🟡 **SYNTHESIZE** — pending vet record |
| `[heritage: kenwalger-2026] Sovereign Node` | Ken W. Alger 2026 | 🟡 **PARALLEL** — pending vet record |
| `[heritage: kenwalger-2026] Point of Genesis` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Sovereign Envelope` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Capability Gradient` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Escalation Boundary` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |
| `[heritage: kenwalger-2026] Cognitive Appliance` | Ken W. Alger 2026 | 🟡 **ADOPTED** — pending vet record |

**Note**: All `[heritage: kenwalger-2026]` tags require M14 vet records in `HERITAGE_VET_LOG.md` before use in source code. This glossary tracks adoption intent; vet records are separate.

---

## 📝 GLOSSARY MAINTENANCE PROTOCOL

1. **New Native Term**: Add to glossary with `[origin: omega]`, mandate/pillar ref, NATIVE
2. **Adopted Term**: Add with `[heritage: kenwalger-2026]`, source file, ADOPTED, rationale
3. **Synthesized Term**: Document both lineages, SYNTHESIZE, credit both
4. **Parallel Term**: Document both, PARALLEL, note distinction
5. **Deprecated Term**: Mark DEPRECATED, link to replacement, keep for archaeology
6. **Vet Record**: Before using `[heritage:]` in source code, create vet record in `HERITAGE_VET_LOG.md`

---

*⬡ OMEGA ⬡ GLOSSARY v1.0 ⬡ 2026-07-18 ⬡ LIVING DOCUMENT*