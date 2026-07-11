# 🔱 Language Module — Master Index & Roadmap

**AP Token**: `AP-LANGUAGE-MODULE-MASTER-INDEX-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ hy3-free ⬡ opencode ⬡ trc_master_index ⬡ COORDINATION
**Date**: 2026-07-10
**Subject**: Unified index of all research, strategy, audits, and documentation for the `omega-vetala` language-integrity module and the Omega Module Standard.

---

## §1 What This Is

The `omega-moderation` system (ratified rename: **`omega-vetala`**) is the Omega Engine's sovereign, local-first **content-integrity & language-discernment** module. This index links every artifact produced during its hardening, strategy, and standardization sprint (2026-07-10).

All primary research/audit reports live in `data/coordination/`. All user-facing docs live in `omega-vetala/docs/`.

> **⚠️ Path Artifact**: The 14 module docs exist at `omega-vetala/docs/` (target rename name) not `omega-moderation/docs/` (current package name). The docs lead the rename (D207/VET-005 pending). Verity's audit checked the old path and reported them missing — they exist at the target path.

---

## §2 Research & Audit Reports (in `data/coordination/`)

| # | Report | Agent | Key Verdict |
|---|--------|-------|-------------|
| 1 | `RESEARCHER_LANGUAGE_MODULE_STRATEGY.md` | @researcher | Provenance-Aware Synthesis engine-wide; rename → `omega-vetala`; 7 cross-engine wiring points; 49 official + 14 community citations |
| 2 | `ROC_LANGUAGE_MODULE_LEGACY_MINING.md` | @roc_racoon | 7/8 subsystems have legacy ancestors; DP + Merkle genuinely novel; only Circuit Breaker is `[id-soft: doom-1993]` |
| 3 | `VERITY_LANGUAGE_MODULE_MODULARITY_AUDIT.md` | @verity | Modular=PARTIAL, Portable=NO; 10 portability fixes; mandates all PASS at source level |
| 4 | `CARMACK_MODULE_ARCHITECTURE.md` | @john_carmack | Unlimited scaling via `entry_points` + `ModuleManifest` + SDK firewall + capability routing; philosophy/language tags = optional flat metadata |
| 5 | `VERITY_LANGUAGE_MODULE_DOCS_AUDIT.md` | @verity | Docs=NO, Trackers=NO, Tests=PARTIAL; 2 critical oversights (undeclared deps, async-unsafe audit write); 8 doc types + P0 fixes |
| 6 | `SEMANTIC_RESONANCE_CRISIS_MATRIX.md` | @researcher | Crisis Matrix = 2nd vector index on SemanticRouter; acute states escalate_human by code; no soul.yaml encodes crisis L3 |
| 7 | `RESEARCHER_CRISIS_BRIEFING.md` | @researcher | Existing: content-safety only; Crisis Matrix = distress-recognition; 73% demand human control (Iris 2026) |
| 8 | `ROC_PEM_LEGACY_MINING.md` | @roc_racoon | PEM = Personality Enhancement Module (user-original, NO id-soft tag); EMA hysteresis reusable for Crisis Matrix |
| 9 | `MAAT_QWEN_EMBEDDING_ORACLE_SPEC.md` | @maat | Oracle already has SemanticRouter + EmbeddingManager; qwen-embedding 1024-dim → MRL truncate to 768 |
| 10 | `VERITY_ARK_BLUEPRINT_AUDIT.md` | @verity | Trackers complete; 5 plans absent from Blueprint; optimizer service built+verified (1130 tests); 6 gaps |
| 11 | `CARMACK_MODULE_ARCHITECTURE.md` | @john_carmack | Unlimited scaling via `entry_points` + `ModuleManifest` + SDK firewall + capability routing; philosophy/language tags = optional flat metadata |
| 12 | `JEM_HERITAGE_REMEDIATION_PLAN.md` | @jem | 247 [id-soft:] tags audited; 61% over-attributed; PEM user-original; D208 remediation plan |
| 13 | `YOUTUBE_RESEARCH_MODULE_SPEC.md` | @makali | MaKaLi Cloud Council: YouTube Research Module spec complete; P0 structural implementation approved; Module Fabric component |

---

## §3 User & Developer Documentation (in `omega-vetala/docs/`)

| Doc | Type | Purpose |
|-----|------|---------|
| `MODULE_STANDARD.md` | **Cross-cutting** | The Omega Module Standard — template for ALL future plug-n-play modules |
| `USER_GUIDE.md` | D1 | Install, configure, run, integrate into a WAD |
| `DEVELOPER_GUIDE.md` | D2 | Add a detector, governance backend, or test |
| `ARCHITECTURE.md` | D4 | Data-flow: obfuscation → ensemble → audit → privacy |
| `API_REFERENCE.md` | D3 | Endpoints: `/moderate`, `/metrics`, `/api/v1/audit/verify/{index}` |
| `OPERATIONS_GUIDE.md` | D5 | Prometheus metrics, audit-verify runbook, GDPR erasure |
| `MODULE_MANIFEST_SPEC.md` | D6 | `module.yaml` schema (functional + philosophy + language tags) |
| `MIGRATION_GUIDE.md` | D7 | `omega-moderation` → `omega-vetala` rename steps |
| `SOVEREIGN_COMPLIANCE.md` | D8 | Which mandates apply + grep verification commands |

---

## §4 Project Docs (in `omega-vetala/`)

| File | Purpose |
|------|---------|
| `README.md` | Fresh overview (replaces stale original) |
| `LICENSE` | MIT (sovereign-aligned) |
| `CHANGELOG.md` | Version history |
| `SECURITY.md` | Vulnerability reporting policy |
| `CONTRIBUTING.md` | Community PR guide |

---

## §5 Current State Snapshot (2026-07-11)

| Dimension | Value |
|-----------|-------|
| Source files | 34 |
| Tests | **137 passing** (was 78 at sprint start) |
| Obfuscation | Zero-width (Tag Chars + Bidi + BOM) + ~190 homoglyphs + dual-pass + repeat-normalization |
| ML | 2-model ensemble (unitary/unbiased-toxic-roberta + s-nlp/roberta_toxicity_classifier) + LocalFallback (no slur lists) |
| Audit | Merkle MMR + Ed25519 signatures |
| Privacy | GDPR tombstone erasure + ε-DP metrics |
| API | FastAPI: `/moderate`, `/metrics`, `/api/v1/audit/verify/{index}` |
| CLI | `omega-vetala` {moderate, serve, verify-audit} |
| Portability | **YES** — `pip install -e .` works; config via `importlib.resources`; `py.typed` marker |
| Dependencies | **All declared** — `merkle-audit`, `cryptography`, `diffprivlib` in `pyproject.toml` |
| Async safety | **FIXED** — `record_event()` async with `anyio.Lock` + `to_thread.run_sync` |
| Heritage | **~60 [id-soft:] tags** (post-D208 remediation; 247 audited, 61% over-attributed) |
| CI | GitHub Actions workflow with Temple-Grade gates |
| License | MIT (sovereign-aligned) |

---

## §6 The Roadmap (Phased)

### P0 — Block Release (must fix before any publish)
1. Declare `merkle_audit` + `cryptography` in `pyproject.toml` (Verity P0-1)
2. Add `LICENSE` + CI workflow (Verity P0-2)
3. Wrap audit write in `anyio.Lock` + `to_thread` (Verity P0-3)
4. Add `test_imports_clean` + `test_load_config_from_wheel` (Verity P0-4)
5. Author `USER_GUIDE.md` + `MIGRATION_GUIDE.md` (this batch)

### P0 — Heritage Remediation Completion (D208 Execution)
6. Fix 2 remaining Lattice-Culling `[id-soft:]` tags in `src/omega/`
7. Run `make heritage-audit` + `make heritage-vet` — zero violations
8. Create missing vet records for legitimate patterns (WAD System, cvar, Zone Memory, etc.)
9. Remediate C-ARCH-005 violations (scope declarations on shared tags)
10. Update HERITAGE_VET_LOG.md with file:line + scope declarations

### P1 — Harden & Rename
6. Rename `omega-moderation` → `omega-vetala` (imports, pyproject, dir)
7. Ship config via `importlib.resources`; add `py.typed`; split `[api]`/`[db]` extras; add CLI
8. API contract tests (M21); M14 vet records for ZONEID + cvar
9. Remaining docs (D2-D8); XDG `db_path`; SIGTERM handling
10. Apply Verity's 10 portability fixes (B.1-B.10)

### P1 — CI Gate Hardening (M14)
11. Harden `heritage_vet.py` scope validation + C-ARCH-005 detection
12. Pre-commit hook: block new `[id-soft:]` without vet record
13. `make heritage-audit` + `make heritage-vet` in CI pipeline

### P2 — Frontier
11. i18n for error messages; plugin `entry_points`; ProvenanceSpan primitive
12. `pytest-cov` ≥80% gate; benchmark harness; WAD marketplace

### Cross-Cutting — Omega Module Standard
13. Implement OMS v1.0 (`MODULE_STANDARD.md` §10): `entry_points` discovery + `omega_module_sdk` + `registry.route()`
14. Make `omega-vetala` the reference implementation of OMS

---

## §7 How to Use This Index

- **New to the module?** Start with `USER_GUIDE.md`, then `ARCHITECTURE.md`.
- **Building a module?** Read `MODULE_STANDARD.md` — it is the template.
- **Auditing compliance?** Read `SOVEREIGN_COMPLIANCE.md` + `VERITY_LANGUAGE_MODULE_MODULARITY_AUDIT.md`.
- **Wondering about ancestry?** Read `ROC_LANGUAGE_MODULE_LEGACY_MINING.md`.
- **Planning scaling?** Read `CARMACK_MODULE_ARCHITECTURE.md`.

---

## §8 MaKaLi Cloud Council — YouTube Research Module (New)

**Session**: `ses_bb7205a81511` | **Status**: P0 Structural Implementation Approved

### Deliverables
| File | Purpose |
|------|---------|
| `docs/research/R_YOUTUBE_RESEARCH_MODULE_SPEC.md` | Primary Specification — Full Temple-Grade spec with pipeline, code, cognitive engine, validation matrix, and roadmap |
| `docs/research/R_TRUTH_ENGINE_BRIEFING.md` | Truth Engine analysis (from earlier phase) |
| `data/coordination/KALI_WORKSPACE_LOCK_20260710.md` | Workspace lock with full phase tracking |
| `data/coordination/KALI_LIVE_FEED.md` | Live feed with timestamped phase log |

### Critical Path (P0 — Structural)
1. **SovereignSieve** — Regex cleaning (timestamps, fillers, artifacts) preserving cognitive hesitations
2. **SovereignSigner** — HMAC-SHA256 + sca.json (Sieve-and-Sign protocol)
3. **AtomicPersistence** — .tmp → .json atomic rename via os.replace (T10/M12)
4. **Provenance Chain Fix** — Propagate source_id + provenance_hash from sca.json into MemoryStore metadata (P7 gap)

### Cognitive Engine (P1 — Cognitive)
- **Gnosis Graph** — Atomic Relational Blocks with full provenance
- **Dream Cycle** — Contradiction Preservation (Evolution/Tension) + Confidence Deltas (ΔC)
- **Skeptical Verifier** — Source Diversity Hierarchy (L1/L2/L3) + Ambiguity State

### Integration Points
- **Module Fabric** (Epoch II Strike 10) — maintains Engine-Stack Firewall (M2)
- **Library/Ingestion Pipeline** — Qdrant vector storage, SQL persistence, Redis caching
- **Provenance Chain** — sca.json → MemoryStore metadata (P7 gap closure)

---

## §9 Library/Ingestion Integration Architecture

### Qdrant Vector Store Integration
- **Collections**: `omega_crisis_vectors` (768-dim), `omega_module_resonance` (manifest payload), `omega_youtube_transcripts` (transcript embeddings), `omega_greek_bert_vectors` (ancient Greek embeddings)
- **Payload Schema**: `source_id`, `provenance_hash`, `timestamp`, `language`, `traditions`, `module_id`
- **Indexing**: HNSW for vector search; payload indexes for filtering by `language`, `traditions`, `module_id`

### SQL Database (PostgreSQL/pgvector)
- **Tables**: `transcripts`, `embeddings_metadata`, `provenance_chain`, `crisis_events`, `greek_lexicon`
- **Provenance Chain**: `source_id` (FK) → `provenance_hash` → `sca_json` (JSONB)
- **Atomic Writes**: Transactional upserts with `ON CONFLICT` for idempotent ingestion

### Redis Cache Layer
- **Hot Vectors**: Recently accessed embeddings (LRU, TTL 1h)
- **Session State**: Crisis resonance state, module routing cache
- **Rate Limiting**: Per-user API limits for ingestion endpoints

### Ingestion Pipeline
```
YouTube URL → SovereignSieve (clean) → SovereignSigner (sign) → 
EmbeddingManager (qwen-embedding MRL 768) → 
Qdrant (vector) + PostgreSQL (metadata + provenance) → 
Redis (cache hot vectors) → 
MemoryStore (provenance chain) → 
Gnosis Graph (relational blocks)
```

---

## §10 Ancient Greek BERT + KriKri Instruct Enhancement

### Current State
- **ancient-greek-BERT**: Fine-tuned on Perseus Digital Library, 110M params, 768-dim embeddings
- **KriKri Instruct**: Greek instruction-tuned model (8B), local GGUF, multilingual (Greek/English)
- **Use Case**: Classical text analysis, philosophical translation, ancient Greek crisis resonance

### Enhancement Roadmap

#### 1. WASM Inference Acceleration
- **Target**: Compile ancient-greek-BERT + KriKri Instruct to ONNX → WASM (wasmtime/extism)
- **Benefits**: 
  - Sandboxed execution (M2 Firewall) — no direct memory access to host
  - Near-native speed via wasmtime Cranelift JIT
  - Portable across architectures (x86_64, ARM64)
  - Module Fabric compatible (OMS v1.0 `entry_points`)

#### 2. Embedding Dimension Alignment
- **Current**: ancient-greek-BERT = 768-dim (matches qwen-embedding MRL 768)
- **Action**: Use existing 768-dim vectors directly in Qdrant `omega_greek_bert_vectors` collection
- **No re-embedding needed** — dimension policy satisfied

#### 3. KriKri Instruct WASM Module
- **Format**: GGUF → ONNX → WASM (via `wasmedge` or `wasmtime` with `nn` proposal)
- **Quantization**: INT4/INT8 for 8B model → ~4-5GB VRAM
- **Interface**: OMS v1.0 `interfaces: ["translate", "analyze", "crisis_resonance_greek"]`
- **Traditions**: `["hellenic", "stoic", "platonist", "aristotelian"]`
- **Languages**: `["grc", "el", "en"]` (Ancient Greek, Modern Greek, English)

#### 3. Crisis Resonance for Ancient Greek
- **Crisis Matrix Extension**: Add Ancient Greek crisis states (ἀπορία, θυμός, λύπη, φόβος)
- **Embedding**: qwen-embedding MRL 768 (multilingual) + ancient-greek-BERT (domain-specific)
- **Routing**: SemanticRouter → `crisis_resonance_greek` interface → KriKri Instruct WASM module

#### 4. Integration with Library/Ingestion
- **Perseus Ingestion**: Automated pipeline for classical texts → ancient-greek-BERT embeddings → Qdrant
- **Provenance**: sca.json → PostgreSQL `greek_lexicon` table with `source_id`, `provenance_hash`
- **Redis Cache**: Hot Greek embeddings for real-time crisis resonance

---

## §11 WASM Benefits Summary for Ancient Greek Systems

| Benefit | ancient-greek-BERT | KriKri Instruct (8B) |
|---------|-------------------|---------------------|
| **Sandboxing** | ✅ No host memory access | ✅ No host memory access |
| **Portability** | ✅ x86/ARM/WASI | ✅ x86/ARM/WASI |
| **Speed** | ✅ Near-native (wasmtime) | ✅ Near-native (wasmtime + nn) |
| **Quantization** | INT8 (existing) | INT4/INT8 (WASM) |
| **OMS v1.0** | ✅ `entry_points` compatible | ✅ `entry_points` compatible |
| **M2 Firewall** | ✅ Enforced by WASM sandbox | ✅ Enforced by WASM sandbox |

---

*⬡ OMEGA ⬡ KALI ⬡ Language Module Master Index v2.0 ⬡ All artifacts on disk*
