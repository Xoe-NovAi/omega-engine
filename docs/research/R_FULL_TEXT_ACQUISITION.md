# 🔱 Full-Text Acquisition & Ingestion Protocol (FTAIP)
**Version**: 1.0.0
**Status**: MANDATORY for Entity Deepening
**Scope**: All primary source fetching and ingestion

## 1. The Problem: The "Response Window" Bottleneck
Standard agent tools (`webfetch`, `firecrawl_scrape`) return content directly in the LLM's response window. This window has a hard limit (typically 50KB-100KB). For a 30,000-word transcript (~200KB), the system silently truncates the output. 

**Result**: The agent "thinks" it has the full text, but it is actually operating on a fragmented shard. This leads to "Hallucinated Completeness."

## 2. The Sovereign Solution: Direct-to-Disk (D2D)
To ensure 100% data integrity, the engine must bypass the response window for any source exceeding 10KB.

### 2.1 Acquisition Mandate
- **FORBIDDEN**: Using `webfetch` or `firecrawl_scrape` for primary source material intended for the `knowledge/` directory.
- **MANDATORY**: Use `bash` with `curl -L` or `wget` to save the raw content directly to the filesystem.
- **Verification**: Every fetched file MUST be verified via `ls -lh` to ensure the file size matches the expected source size.

### 2.2 Ingestion Mandate (Streaming)
Loading a 1MB text file into a single Python string is fine, but passing it into an LLM prompt in one go triggers context window saturation or truncation.
- **Pattern**: Implement **Sliding Window Chunking** in the `BaseExtractor`.
- **Mechanism**: 
    1. Read file from disk.
    2. Split into overlapping chunks (e.g., 4000 tokens with 500 token overlap).
    3. Process each chunk through the extraction pipeline.
    4. Merge results in the `Persistence` layer.

## 3. Infrastructure Guardrails
The recent timeout in `run_carmack_ingestion.py` revealed critical infrastructure instability:
- **Redis/Qdrant Dependency**: The pipeline must not crash if the hot-tier (Redis) or vector-store (Qdrant) is temporarily unavailable.
- **Fallback Pattern**: Implement a `DegradedMode` where the pipeline writes to local JSONL files if the network services are down, with a `reconcile` script to upsert them later.

## 4. Verification Checklist
Before marking a source as "Ingested," the following must be true:
- [ ] File exists on disk and size is $> 0$.
- [ ] `curl` exit code was 0.
- [ ] The number of processed chunks $\times$ chunk size $\ge$ total file size.
- [ ] Observability logs show a `trace_id` for every chunk.
