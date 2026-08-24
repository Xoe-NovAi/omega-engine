# 🔱 Ken Walger Mining Operation — Context Document for @jem Synthesis
**AP Token**: `AP-KEN_CONTEXT_FOR_JEM-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_ken_context ⬡ ACTIVE

**Date**: 2026-07-18
**Purpose**: Supporting context for @jem's synthesis of the Ken Walger mining operation
**Source**: Roc Racoon deep research (9 repos + blog, 62 pages, 27-term adoption matrix)

---

## 1. TECHNICAL DEBT ASSESSMENT — What Exists vs What Needs Building

### ✅ ALREADY BUILT (Can Be Leveraged Immediately)

| System | Location | Maturity | Notes |
|--------|----------|----------|-------|
| **M22 Response Provenance** | `src/omega/observability/provenance.py` — `GenerateResult.provider_name: str` | **WIRED & TESTED** | Contract tests in `test_contract_m21.py` lines 100-150. NOT a prerequisite — base provenance is operational. |
| **BatchPersistenceWriter** | `src/omega/memory/` — 50 ops/batch, 2s flush | **OPERATIONAL** | MAS batch ingestion must EXTEND this, not rebuild. |
| **SovereignIngestionPipeline** | `Sieve → Sign → IngestedDocument` | **OPERATIONAL** | Canonical ingestion path. MAS v0.1 must extend `IngestedDocument` dataclass. |
| **SovereignSigner** | HMAC-SHA256 in ingestion pipeline | **OPERATIONAL** | Keep as fallback. ForensicReceipt upgrades to Ed25519. |
| **Meditate Framework** | `src/omega/meditate/` + `lenses.yaml` | **Phase A COMPLETE** | WAD-backed lens loading via `lens_registry.py`. Custom 6-lens set for Ken Mining = WAD YAML config. |
| **sqlite-vec Adapter** | `src/omega/memory/sqlite_vec_adapter.py` | **Strike 10 COMPLETE** | Single-row upsert exists. Needs `upsert_batch()` method added. |
| **Hivemind** | `data/coordination/` — locks, Redis Pub/Sub, handoffs, heartbeats | **PARTIAL** | H-0 (cold-store), H-1 (inbox/ack), H-2 (TTL) ALREADY EXIST. Only H-3 (learned routing) is new. |
| **27-Term Adoption Matrix** | `sovereign_collab/KEN_TERM_ADOPTION_MATRIX.md` (141 lines) | **COMPLETE** | 23 ADOPT, 12 KEEP, 4 SYNTHESIZE, 3 PARALLEL. All decisions documented. |
| **Airlock Study** | `sovereign_collab/AIRLOCK_STUDY.md` (469 lines) | **DESIGN COMPLETE** | Full SAR-0004 architecture, YAML policy engine, 4-stage boundary, integration points. Implementation: 10-14h. |
| **ForensicReceipt Study** | `sovereign_collab/FORENSIC_RECEIPT_STUDY.md` (457 lines) | **DESIGN COMPLETE** | Ed25519 + hash chain. Module target: `src/omega/provenance/`. M22 upgrade from observational → cryptographic. |
| **Universal Doc Reader** | `universal_doc_reader.py` (81 lines) | **FUNCTIONAL** | Handles 8 formats. Fallback if all2md fails. NOT an MCP server. |
| **Grounding Research** | `docs/research/R_KEN_WALGER_MINING_GROUNDING_20260718.md` (362 lines) | **COMPLETE** | 6-domain grounding: sqlite-vec, Hivemind, M22, ForensicReceipt, all2md, serial architecture. |
| **Execution Plan** | `docs/strategy/R_KEN_MINING_EXECUTION_PLAN_20260719.md` (264 lines) | **COMPLETE** | Jem cross-referenced: 7 GO, 2 CONDITIONAL-GO, 1 NO-GO. 10-phase matrix with mandate compliance. |

### ❌ NOT YET BUILT (Needs Implementation)

| System | Blocking Phase | Estimated Effort | Critical? |
|--------|---------------|-----------------|-----------|
| **MAS v0.1 Schema** (`MiningIngestedDocument`) | Phase 0 | 3-4h | **YES** — extends `IngestedDocument` with trace_id, span_id, agent_pillar, phase |
| **all2md install + verification** | Phase 0 | 30min | **YES** — MUST verify before committing to blog ingestion |
| **sqlite-vec `upsert_batch()`** | Phase 3 | 2-3h | YES — transaction-wrapped batch inserts, LlmMac 500-2000 rows/txn |
| **ForensicReceipt module** | Phase 6 | 5-7h | UPGRADE — `src/omega/provenance/`, Ed25519, hash chain, M14 vet record required |
| **Airlock module** | Phase 10+ | 10-14h | FILL GAP — `src/omega/airlock/`, NormalizedPayload, PolicyEngine, 4-stage boundary |
| **Hivemind H-3 (learned routing)** | Phase 1 | 2-3h | NEW — AgensFlow pattern. H-0 to H-2 already exist. |
| **27 heritage vet records** | M14 compliance | 2-3h (batch) | REQUIRED — All `[heritage: kenwalger-2026]` tags need vet records before code merge |
| **Workbench DB restoration** | BLOCKER | 2-4h | CRITICAL — Schema exists, 0 tables. Project tracking cannot start without it. |

### 📊 Debt Summary

- **~60% of needed infrastructure already exists** (Jem's cross-reference finding)
- **Total effort**: 26-35h (reduced from Roc's 29-44h due to existing infrastructure)
- **Critical path**: Phase 0 (MAS schema + all2md verify) → Phase 3 (sqlite-vec batch) → Phase 4 (blog ingestion) → Phase 5 (Prose Tax eval) → Phase 6 (ForensicReceipt) → Phase 7 (Meditate synthesis) → Phase 9 (serial execution)

---

## 2. all2md VERIFICATION STATUS — What We Know, What's Blocked

### What all2md IS
- Python library: `pip install all2md`
- 40+ format support (HTML, PDF, DOCX, ODT, RTF, etc.)
- AST-based extraction (not regex)
- **MCP server built-in** — can serve as tool for agent fleet
- Zero external dependencies for core functionality

### What We DON'T Know
- **NOT installed** in the codebase — zero grep matches for `all2md`
- **NOT verified** on Ken's specific blog HTML (`kenwalger.com/blog/`)
- **UNKNOWN**: Does it handle Ken's blog post structure correctly? (headings, code blocks, embedded images, navigation chrome)
- **UNKNOWN**: Does it handle the 62-page blog crawl efficiently? (rate limiting, pagination, content extraction vs page structure)

### The Actual Blocker
The blocker is NOT all2md's capability — it's the **verification gap**. We know all2md handles 40+ formats and has MCP server support. What we DON'T know is whether it correctly extracts content from Ken's specific HTML structure without losing:
- Code blocks (critical for his MCP/tool-calling posts)
- Table structures (his adoption matrices, comparison tables)
- Embedded links (his cross-references between posts)
- Metadata (post dates, titles, series organization)

### Verification Protocol (from Execution Plan)
```bash
# 1. Install all2md
pip install all2md

# 2. Test on a sample blog post
python -c "from all2md import to_markdown; print(to_markdown('https://kenwalger.com/blog/ai-post'))"

# 3. If all2md works → GO for Phase 0
# 4. If all2md fails → fallback to universal_doc_reader.py + BeautifulSoup
```

### Fallback Chain
1. **Primary**: all2md (40+ formats, MCP server, AST-based)
2. **Fallback**: `universal_doc_reader.py` (81 lines, 8 formats) + BeautifulSoup for HTML
3. **Nuclear**: Manual extraction via `webfetch` + markdown conversion

### Risk Assessment
- **Probability of all2md failure on Ken's HTML**: LOW-MEDIUM
- **Impact if failure**: HIGH — blocks Phase 4 (blog ingestion)
- **Mitigation**: Install and verify in Phase 0, not Phase 4. If it fails, we have fallbacks.

---

## 3. SIGNET INTEGRATION OPTIONS — Real Integration Paths

### What Signet IS
- **Signet MCP**: Prismer-AI's production-ready MCP server for AI provenance
- **ForensicReceipt**: Ed25519-signed receipt with SHA-256 hash chain
- **83 tests**, Apache-2.0/MIT licensed
- **NOT the same as sovereign-sdk-sieve** — Sieve = Prose Tax optimization, Signet = cryptographic signing

### Integration Paths

#### Path A: Direct MCP Server Integration (Recommended)
- **How**: Add Signet as MCP tool in `opencode.json` tool registry
- **What**: `signet-mcp` server provides `sign()` and `verify()` tools
- **Pros**: Zero code changes, immediate availability, 83 tests validate
- **Cons**: External dependency, MCP overhead per call
- **Effort**: 1-2h (config only)

#### Path B: Library Integration (ForensicReceipt Module)
- **How**: Import `signet` Python package into `src/omega/provenance/forensic_receipt.py`
- **What**: Direct function calls, no MCP overhead
- **Pros**: Tighter integration, lower latency, Omega-native error handling
- **Cons**: Code changes, M14 vet record required, M21 contract tests needed
- **Effort**: 5-7h (module + tests + vetting)

#### Path C: Hybrid (Sign for High-Value, HMAC for Routine)
- **How**: Use HMAC-SHA256 (existing SovereignSigner) for routine ingestion, Ed25519 (Signet) for mining artifacts
- **What**: Two-tier provenance: cheap crypto for volume, expensive crypto for value
- **Pros**: Performance-friendly, cost-effective, pragmatic
- **Cons**: Two signing systems to maintain, policy complexity
- **Effort**: 3-4h (policy routing + two-tier implementation)

### MCP Server Interface (Ken's sovereign-sdk)
```
Ken's sovereign-sdk provides:
- sovereign-sign: Ed25519 signing tool
- sovereign-verify: Receipt verification tool  
- sovereign-ledger: Append-only receipt store
- sovereign-audit: Compliance verification

Omega integration point: ModelGateway.generate() post-processing
- After GenerateResult is returned
- Before observability logging
- Sign the response with ForensicReceipt
- Log receipt hash alongside provider_name
```

### What Ken's Work Proves
- ForensicReceipt is PRODUCTION-READY (83 tests, Apache-2.0)
- Ed25519 signing is the right choice (not RSA, not ECDSA)
- Hash chain provides tamper-evidence without blockchain overhead
- Local verification is primary (cloud anchor via OpenTimestamps is optional)

---

## 4. AIRLOCK ARCHITECTURE GAP — What's Missing, Full vs Partial

### The Gap (SAR-0004)
**Omega has inbound governance (ModelGateway, M2 Firewall) but ZERO outbound governance.**

| Direction | Current State | Risk |
|-----------|---------------|------|
| **Inbound** (User → Model) | ModelGateway routes, speculative decode, provider fabric | Covered |
| **Outbound** (Model/Tool → External) | **NOTHING** | Data exfiltration, token budget overflow, credential leakage, compliance violation |

**Every tool call, every model response sent to external API, every webhook — passes through NO inspection.**

### Full Implementation (10-14h)
```
src/omega/airlock/
├── __init__.py
├── boundary.py          # AirlockBoundary — 4-stage orchestrator
├── payload.py           # NormalizedPayload + normalizers (OpenAI, Anthropic, Gemini, Raw)
├── policy.py            # PolicyEngine — YAML rule evaluation (raw/fields/telemetry scopes)
├── telemetry.py         # AirlockTelemetry — sieve convergence metrics
├── receipt.py           # ReceiptBuilder → ForensicReceipt + ledger
├── exceptions.py        # AirlockPolicyViolation, AirlockConfigurationError
├── normalizers/
│   ├── __init__.py
│   ├── openai.py
│   ├── anthropic.py
│   ├── gemini.py
│   ├── openrouter.py
│   └── raw.py
└── config/
    └── policy.yaml      # Omega-specific policies (M8, M22, M23 compliance)
```

**Components**:
1. **NormalizedPayload** — Provider-neutral inspection surface
2. **PolicyEngine** — YAML rules (raw/fields/telemetry scopes)
3. **AirlockBoundary** — Async 4-stage orchestrator (policy → sieve → sign → ledger)
4. **AirlockTelemetry** — Sieve convergence metrics
5. **ReceiptBuilder** — ForensicReceipt + sovereign-ledger commit

**Integration Points**:
- `ModelGateway.generate()` → wrap outbound provider calls
- Tool execution pipeline → wrap outbound tool calls
- Hivemind outbound → wrap webhook/MCP calls

### Partial Implementation — Phase 1 (3-4h)
Focus on the CRITICAL gap: **credential leakage prevention**.

```
src/omega/airlock/
├── __init__.py
├── boundary.py          # Simplified 2-stage: policy → release (no sieve, no sign)
├── payload.py           # NormalizedPayload + normalizers
├── policy.py            # PolicyEngine — YAML rules (raw scope only)
└── config/
    └── policy.yaml      # M8 (telemetry block), credential block, stack trace block
```

**What Partial Covers**:
- ✅ Credential exfiltration prevention (raw scope DENY rules)
- ✅ Stack trace leakage prevention
- ✅ Telemetry beaconing prevention
- ❌ Prose Tax optimization (no sieve integration)
- ❌ ForensicReceipt signing (no cryptographic evidence)
- ❌ Token budget governance (no telemetry scope rules)
- ❌ Hivemind secret leakage prevention (no fields scope rules)

### Decision for @jem
**Recommendation**: Partial implementation (Phase 1) is sufficient for mining operation. Full implementation is Horizon 2 work. The mining pipeline doesn't generate outbound payloads — it INGESTS. Airlock matters more for production deployment than for the mining operation itself.

---

## 5. RAM CONSTRAINT ANALYSIS — Why Serial Is the Only Option

### Physical Constraints
- **RAM**: 14GiB unified memory (no GPU)
- **CPU**: Ryzen 5700U (8 cores, 15W TDP)
- **Storage**: NVMe SSD (fast I/O, not the bottleneck)
- **zRAM**: Active (compressed swap, adds overhead)

### Model Memory Footprints (Verified from Grounding Research)

| Model | Size | RAM Usage | Notes |
|-------|------|-----------|-------|
| **Phi-3 Mini (3.8B Q4)** | ~2.2GB | ~3.5GB (with KV cache) | Lightweight, fast |
| **Qwen 2.5 (7B Q4)** | ~4.5GB | ~6.5GB (with KV cache) | Sweet spot for code tasks |
| **Mistral 7B Q4** | ~4.2GB | ~6.2GB (with KV cache) | Good general purpose |
| **Llama 3.1 8B Q4** | ~4.7GB | ~7GB (with KV cache) | Heavy but capable |
| **DeepSeek V4 Flash** | ~8GB | ~10GB+ (with KV cache) | Cloud-only via API |

### Why Parallel Is Impossible
**ArXiv:2603.04428 (2026)**: On constrained hardware, every "parallel operation" is time-sliced concurrency on a single scheduler thread. Memory bandwidth, not compute, is the binding constraint.

**The Math**:
- 14GiB total RAM
- ~2GiB OS overhead
- ~1GiB application overhead (Python, SQLite, Qdrant)
- **~11GiB available for models**
- One 7B Q4 model = ~6.5GB with KV cache
- **One model loaded at a time** = only option for parallel work

**What "Parallel" Actually Means on 14GiB**:
- Sequential model loads (not concurrent)
- Time-sliced CPU usage (not true parallelism)
- zRAM pressure when switching models (compression/decompression overhead)
- Thermal throttling under sustained load (15W TDP)

### Serial Architecture (Verified)
```
Phase 0: Load Phi-3 Mini (3.5GB) → MAS schema design
Phase 1: Unload Phi-3 → Load Qwen 2.5 (6.5GB) → Hivemind hardening
Phase 2: Unload Qwen → Load Phi-3 (3.5GB) → M22 audit (code review, lightweight)
Phase 3: Unload Phi-3 → Load Qwen 2.5 (6.5GB) → sqlite-vec batch implementation
Phase 4: Unload Qwen → Load Phi-3 (3.5GB) → all2md verification + blog ingestion
...and so on
```

**Key Insight**: The tools (all2md, Signet, sqlite-vec) are LOCAL and don't need GPU/CPU for inference. Only the AGENT doing the work needs a model loaded. The mining pipeline itself is tool-driven, not model-driven.

---

## 6. ADOPTION MATRIX DETAIL — P0 vs P1 for 23 ADOPT Items

### P0 — CRITICAL PATH (Blocks mining operation or violates mandates)

| # | Term | Why P0 | Blocking Phase |
|---|------|--------|----------------|
| 15 | **ForensicReceipt** | Upgrades M22 from observational → cryptographic. Required for mining artifact provenance. | Phase 6 (but NOT prerequisite — base M22 works) |
| 18 | **Airlock (SAR-0004)** | CRITICAL GAP — zero outbound governance. But NOT blocking mining (mining ingests, doesn't egress). | Phase 10+ (Horizon 2) |
| 14 | **Sieve-and-Sign Pattern** | Mining pipeline architecture: extract → filter → sign → store. This IS the pipeline design. | Phase 0 (MAS schema design) |
| 13 | **Write-Side Custody** | M2 Firewall principle at ingestion layer. MAS v0.1 must enforce at write time. | Phase 0 (MAS schema) |
| 16 | **Ingestion Boundary** | Component implementing M2 at data ingress. MAS pipeline must have this. | Phase 0 (MAS schema) |

### P1 — NICE TO HAVE (Improves quality, doesn't block)

| # | Term | Why P1 | Can Defer? |
|---|------|--------|-----------|
| 1 | **The Prose Tax** | Quantifies M18. Measurable, not blocking. | Yes — Phase 5 evaluation |
| 2-8 | **8 Computational Taxes** | Taxonomy formalization. Improves vocabulary, doesn't block code. | Yes — documentation |
| 10 | **Pre-Paid Retrieval Precision** | Architectural pattern. Nice to have, not blocking. | Yes — Phase 5 evaluation |
| 11 | **Fiscal Architecture** | Engineering discipline. Improves design decisions. | Yes — documentation |
| 12 | **Digital Attic** | Anti-pattern name. Useful for avoiding bad patterns. | Yes — documentation |
| 17 | **Sovereign Gateway** | Component implementing ModelGateway. Already exists. | Yes — rename existing |
| 19 | **Point of Genesis** | Future edge work. Not relevant to mining. | Yes — Horizon 3 |
| 20 | **Sovereign Envelope** | Wire format for ForensicReceipt. Comes with ForensicReceipt. | Yes — Phase 6 |
| 21 | **Capability Gradient** | Hardware reality framing. Already implicit in M7. | Yes — documentation |
| 22 | **Escalation Boundary** | ModelGateway fallback chain. Already exists. | Yes — rename existing |
| 23 | **Cognitive Appliance** | Omega Desktop (future). Not relevant to mining. | Yes — Horizon 4 |

### P0 Summary
**Only 5 terms are truly P0** for the mining operation. The rest improve quality and vocabulary but don't block execution. The mining pipeline can proceed with base M22 provenance (HMAC-SHA256) and add ForensicReceipt (Ed25519) in Phase 6.

---

## 7. RISK FACTORS — What @jem Might Not See

### Risk 1: all2md Failure on Ken's HTML (MEDIUM probability, HIGH impact)
- **What**: all2md may not correctly extract content from Ken's blog structure
- **Why @jem might miss**: The grounding research assumes all2md works based on its 40+ format claim. No one has actually TESTED it on `kenwalger.com/blog/`.
- **Mitigation**: Verify in Phase 0. If it fails, `universal_doc_reader.py` + BeautifulSoup is the fallback.

### Risk 2: M14 Heritage Vetting Backlog (HIGH probability, MEDIUM impact)
- **What**: 27 terms need vet records before code can be merged. ForensicReceipt and Airlock are the only CODE patterns needing full vet. The rest are terminology (lightweight vet).
- **Why @jem might miss**: The execution plan mentions M14 but doesn't quantify the vetting effort. 27 vet records at ~5min each = 2.5h of documentation work.
- **Mitigation**: Batch-vet all 27 in a single session. Most are terminology (not code), so vetting is lightweight.

### Risk 3: ForensicReceipt M23 Violation (LOW probability, CRITICAL impact)
- **What**: If Ed25519 signing fails, it could mask tool failures (Sovereign Boundary Violation)
- **Why @jem might miss**: The execution plan mentions M23 but doesn't specify the degradation pattern.
- **Mitigation**: ForensicReceipt MUST be non-blocking. Design: `try: forensic_receipt = mint() except: logger.warning("ForensicReceipt degraded"); forensic_receipt = None`. Existing HMAC-SHA256 is the fallback.

### Risk 4: Workbench DB Restoration (BLOCKER)
- **What**: Schema exists, 0 tables. Project tracking cannot start without it.
- **Why @jem might miss**: The execution plan mentions it but doesn't quantify the effort or specify who does it.
- **Mitigation**: 2-4h to restore schema + seed Ken mining project. Must be done BEFORE Phase 0 execution.

### Risk 5: MAS Schema M2 Violation (LOW probability, HIGH impact)
- **What**: MAS v0.1 could leak into Core Engine if not placed correctly.
- **Why @jem might miss**: The execution plan says "extend IngestedDocument" but doesn't specify WHERE the extension lives.
- **Mitigation**: `MiningIngestedDocument` extends `IngestedDocument` which is already in Core (`oracle/ingestion.py`). The extension MUST also be in Core. MAS-specific fields (trace_id, span_id, agent_pillar, phase) go into the Core dataclass, NOT into WAD-specific code.

### Risk 6: Memory Pressure During Serial Phases (MEDIUM probability, HIGH impact)
- **What**: Model loading/unloading could trigger OOM or zRAM pressure
- **Why @jem might miss**: The grounding research documents the constraint but doesn't specify the monitoring protocol.
- **Mitigation**: Monitor via `omega-hub_get_hardware_stats()` between phases. Unload model before loading next. If zRAM active, reduce thread count.

### Risk 7: Hivemind H-3 Scope Creep (MEDIUM probability, MEDIUM impact)
- **What**: "Learned routing" (AgensFlow pattern) could expand beyond mining needs
- **Why @jem might miss**: The execution plan doesn't define what H-3 actually IS — just that it's "new work."
- **Mitigation**: Define H-3 as MINIMAL learned routing: agent capability → task matching. NOT full AgensFlow automation. Scope: 2-3h, not 2-3 days.

### Risk 8: Prose Tax Evaluation Misinterpretation (LOW probability, MEDIUM impact)
- **What**: sovereign-sdk-sieve might not apply to Ken's blog content (it's designed for code/documentation, not narrative)
- **Why @jem might miss**: The adoption matrix assumes Prose Tax applies universally. Ken's blog is narrative-heavy, not code-heavy.
- **Mitigation**: Phase 5 evaluation should test sieve on both code blocks AND narrative content. If sieve only works on code, the 15% threshold policy rule should be adjusted.

---

## 📋 CROSS-REFERENCE SUMMARY

### What @jem Already Has
- `R_KEN_MINING_EXECUTION_PLAN_20260719.md` — Jem's own cross-reference (7 GO, 2 CONDITIONAL-GO, 1 NO-GO)
- `KEN_TERM_ADOPTION_MATRIX.md` — 27-term decision log
- `AIRLOCK_STUDY.md` — Full SAR-0004 architecture
- `FORENSIC_RECEIPT_STUDY.md` — Ed25519 + hash chain design
- `R_KEN_WALGER_MINING_GROUNDING_20260718.md` — 6-domain grounding research

### What @jem Needs (This Document)
- **Specific file paths** for existing infrastructure (not just descriptions)
- **RAM constraint math** (14GiB - 2GiB OS - 1GiB app = 11GiB for models)
- **P0 vs P1 prioritization** for 23 ADOPT terms
- **Risk factors** that the execution plan doesn't quantify
- **all2md verification status** (NOT installed, NOT tested, actual blocker is verification gap)
- **Signet integration paths** (MCP server vs library vs hybrid)
- **Airlock scope decision** (Partial for mining, Full for Horizon 2)

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ KEN_CONTEXT_FOR_JEM ⬡ 2026-07-18 ⬡ ACTIVE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
