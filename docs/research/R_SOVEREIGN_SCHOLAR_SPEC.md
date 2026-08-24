# 🔱 Sovereign Scholarly Knowledge Base (SSKB) Specification
**AP Token**: `AP-SSKB-SPEC-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_sskb_spec ⬡ SCHOLARLY-SOVEREIGNTY

## §0 Executive Summary
The **Sovereign Scholarly Knowledge Base (SSKB)** transforms the Omega Engine from a general-purpose agent runtime into a professional-grade, censorship-resistant research instrument. The system implements a **Sovereign Ingestion Loop** that autonomously discovers, extracts, and verifies scholarly data using a tiered extraction strategy (Fast $\rightarrow$ Surgical $\rightarrow$ Deep). To ensure absolute sovereignty, the SSKB utilizes **Content-Addressable Storage (CAS)** and decentralized indexing, decoupling knowledge from centralized servers.

---

## §1 The Sovereign Ingestion Loop (Architecture)

### 1.1 The Pipeline Flow
`Discovery Queue` $\rightarrow$ `Tiered Extractor` $\rightarrow$ `Sovereign Verifier` $\rightarrow$ `CAS Archiver` $\rightarrow$ `Knowledge Distiller`

### 1.2 Tiered Extraction Strategy
| Tier | Tool | Use Case | Sovereignty Audit |
| :--- | :--- | :--- | :--- |
| **Fast** | `Trafilatura` | Static blogs, news, simple articles | 100% Local, No Telemetry |
| **Surgical** | `Custom Python` | arXiv, Project Gutenberg, PubMed | 100% Local, API-only (no auth) |
| **Deep** | `Crawl4AI` | SPAs, JS-heavy sites, Anti-bot | Local Playwright + Local LLM |

### 1.3 The Sovereign Verification Gate (Triangulation Protocol)
To defeat sycophancy and hallucinations, the engine implements a **Triangulation Protocol**:
1. **Extraction**: LLM extracts metadata (Author, Date, DOI).
2. **Verification**: The engine queries the **Open Library** and **Crossref** APIs using the extracted DOI.
3. **Resolution**: If $\ge 2$ sources agree, the metadata is marked `VERIFIED`. If they disagree, it is marked `DISPUTED` and flagged for human review.

---

## §2 Sovereign Archiving & Bedrock

### 2.1 Content-Addressable Storage (CAS)
- **Storage**: Files are stored by their SHA-256 hash.
- **Format**: **WARC (Web ARChive)**. Stores the raw HTTP response, headers, and payload.
- **Indexing**: **Local IPFS Node**. Ensures that even if the original URL vanishes, the content is retrievable via its CID (Content Identifier).

### 2.2 Scholarly Patterns
- **Zotero-Integration**: `Collection` entities in `EntityRegistry` group documents by project/theme.
- **BibTeX Automation**: Generation of `references.bib` files using `pybtex`.
- **DOI Resolver**: Dedicated tool to resolve DOIs to direct PDF downloads via open-access mirrors.

---

## §3 Implementation Roadmap

### Phase 1: The Bedrock (Immediate)
- **SovereignWorker**: systemd-managed background worker for async job processing.
- **Tiered Strategy**: Integration of `Trafilatura` and `Crawl4AI`.
- **CAS Integration**: SHA-256 based file storage in `data/archive/cas/`.

### Phase 2: The Verifier (Short-term)
- **Verification Gate**: Wire Crossref and Open Library API checks.
- **WARC Implementation**: Use `warcio` for raw captures.
- **Local IPFS**: Deploy rootless Podman container for `ipfs-daemon`.

### Phase 3: The Scholar (Mid-term)
- **GraphRAG**: Transition to a Knowledge Graph (NetworkX/Neo4j local).
- **BibTeX Engine**: Automatic `.bib` generation and CSL formatting.
- **Sovereign Mirror**: "Opposing View" search for adversarial research.

### Phase 4: The Archive (Long-term)
- **Decentralized Indexing**: P2P index sharing with other Omega instances.
- **Somatic Research Replay**: Load the cognitive state of a research session.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
