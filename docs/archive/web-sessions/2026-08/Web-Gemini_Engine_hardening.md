**Yes on TTS, yes on xyz coordinates, and zRAM changes the picture meaningfully.**

Here’s a direct, practical answer for each part in the context of the Omega Engine on your 12 GB UMA Ryzen 7 5700U + Vega 8 system.

### 1. Can Linux TTS help with tight RAM?

**Yes — and it can help a lot if you currently use (or plan to use) ElevenLabs or any heavy neural TTS.**

Heavy neural TTS (ElevenLabs cloud, XTTS, Bark, larger Coqui models, etc.) can easily consume 1–4+ GB of RAM/VRAM. Replacing or supplementing that with a lightweight local TTS frees memory for the LLM, Qdrant, and the rest of the stack.

**Best low-RAM options on Linux right now (2026):**

| Engine | Peak RAM | Quality | Notes | Best for Omega |
|--------|----------|---------|-------|----------------|
| **eSpeak NG** | < 30 MB | Robotic | Instant, formant synthesis | Absolute minimum footprint |
| **Piper** | ~50–150 MB | Good neural | ONNX, very fast on CPU, many voices | Strong default recommendation |
| **Inflect Nano/Micro v2** | ~16–40 MB | Surprisingly good | Ultra-tiny complete models (2026) | Tiny + modern quality |
| **Pocket TTS / Orca / similar** | ~100–300 MB | High | CPU-first, streaming | When quality matters more |
| **Kokoro (82 M)** | < 1 GB | Excellent | Still light enough for your system | Higher quality local voice |

**Practical recommendation for your setup**
- Primary: **Piper** or **Inflect Micro**. Both stay well under 200 MB and run entirely on CPU.
- Keep ElevenLabs only for high-quality / special cases (or drop it entirely if sovereignty + RAM are priorities).
- Run TTS in a separate process or via the SEDA bus so it never contends with the LLM for the same memory pool.
- Route audio through a simple PulseAudio/PipeWire sink or ALSA so the main engine never has to keep large audio buffers in RAM.

This is one of the highest-ROI memory wins available on a 12 GB machine.

### 2. Adding xyz coordinates for future Godot 4 VR expansion

You want to prepare the memory points so a later Godot 4 OpenXR scene can treat each memory as a 3D location the user can walk through.

**Do this now in the Qdrant payload.** Qdrant is payload-first, so adding three floats costs almost nothing and requires zero schema migration later.

**Recommended payload fields** (add these whenever you upsert a point):

```python
payload = {
    # existing fields...
    "user_id": user_id,
    "memory_type": "declarative" | "episodic",
    "content": "...",
    "created_at": int(time.time()),
    "is_consolidated": False,

    # NEW — spatial coordinates for Godot
    "pos_x": float,          # or "xyz": [x, y, z]
    "pos_y": float,
    "pos_z": float,
    "spatial_scale": 1.0,    # optional — how large the node appears
    "spatial_color": "#RRGGBB",  # optional — visual category
    "spatial_layer": "memory" | "cluster" | "hub",  # optional
}
```

**How to generate the coordinates**

Three practical strategies (you can mix them):

1. **Dimensionality reduction (most “semantic”)**  
   Run UMAP / t-SNE / PCA on the embedding vectors (or a batch of them) down to 3 dimensions, then scale/normalize into a reasonable world size (e.g. −50…+50). Update the coordinates periodically or on consolidation.

2. **Graph / force-directed layout**  
   Treat memories as nodes, similarity as edges, run a simple force layout in 3D, and store the resulting positions. Good for “clusters of related memories feel close together.”

3. **Simple deterministic mapping (easiest starter)**  
   Hash or project a few embedding dimensions + time + importance into x/y/z. Fast, no extra libraries, good enough to start exploring in Godot.

**Godot 4 side (future)**  
- Godot 4 has excellent OpenXR support (and the OpenXR Vendors plugin for Meta/Pico/etc.).  
- You will simply query Qdrant (or export a snapshot) for points that have `pos_x/y/z`, instantiate `Node3D` / `XRAnchor3D` / MeshInstance3D at those positions, and attach the memory content as metadata or a UI panel.  
- Spatial Entities / anchors in newer Godot OpenXR releases make persistence across sessions easy.

**Implementation tip in Omega**  
Add the three floats in `OmegaMemory` upsert paths and in the consolidator when it creates declarative summaries. Index them only if you later want range filters (`pos_x` between …); otherwise just store them as payload.

### 3. How 8 GB zRAM changes the picture

**It helps significantly — especially under pressure.**

zRAM is compressed RAM used as swap. With a modern algorithm (zstd or lz4) you typically get 2–3× effective capacity from the allocated RAM. Your 8 GB zRAM therefore gives you roughly **16–24 GB of effective compressed swap** that stays in memory (no disk I/O latency of traditional swap).

**What this means for Omega on 12 GB physical RAM**

| Component | Without reliable zRAM | With reliable 8 GB zRAM |
|-----------|------------------------|--------------------------|
| LLM (8 B Q4 + 16 k ctx) | Tight; risk of OOM or thrashing | Comfortable headroom |
| Qdrant (TurboQuant BITS2/4) | Must stay small | Can grow more points |
| Overnight GRPO / LoRA | Very risky | Feasible (still keep `num_generations` low) |
| Concurrent TTS + API + UI | Often forced to choose | All can coexist |
| Sudden spikes (large context, many memories) | OOM killer | Soft landing into compressed pages |

**Practical adjustments you can now make**

- Slightly more aggressive `n_ctx` or batch sizes become safer.
- You can keep a larger Qdrant collection in RAM before it starts feeling slow.
- Nightly training is less likely to kill the interactive engine.
- Still keep `MemoryHigh` / `MemoryMax` in the systemd unit so the OOM killer has clear bounds.
- Prefer zstd for better compression ratio on the highly compressible data (model weights, embeddings, JSON payloads) that LLMs produce.

**Caveats**
- zRAM still costs CPU cycles for compress/decompress. On a Ryzen 7 5700U this is fine, but watch thermals during sustained GRPO.
- It does **not** replace the need for careful quantization and TurboQuant — it only gives you a bigger safety net.
- Monitor with `zramctl` and `free -h` under load so you know when you are actually using the compressed space.

### Combined recommendation for your current hardware

1. Switch (or add) a lightweight local TTS (Piper or Inflect) → free 1–3 GB.
2. Start writing `pos_x`, `pos_y`, `pos_z` into every Qdrant payload today → zero future migration cost for the Godot VR space.
3. Treat the reliable 8 GB zRAM as a soft capacity increase → you can be a bit less aggressive on quantization and context limits, and overnight training becomes realistic.

These three changes together give you meaningfully more headroom on a 12 GB UMA system while keeping the architecture ready for the 3D explorable memory space.

---

### 1. SQLite-vec vs. Qdrant & Assigning XYZ Coordinates

#### SQLite-vec vs. Qdrant

On a 16GB system running PostgreSQL, Redis, and an agent runtime alongside local LLMs, resource overhead is a critical constraint.

* **Qdrant**: Offers **Scalar Quantization (SQ8)** and **Binary Quantization (BQ)**. SQ8 converts 32-bit floating-point vector embeddings (`f32`) into 8-bit integers (`int8`), cutting vector RAM usage by up to 75% while maintaining high recall. It supports out-of-core disk memory mapping (`mmap`) and payload index filtering directly within the HNSW search phase. The trade-off is process overhead: running Qdrant as a daemon requires its own memory footprint (typically 200MB–500MB idle/active).


* **SQLite-vec**: An embedded, zero-daemon C extension for SQLite. It runs directly inside the host Python process, sharing memory with the SQLite database. It eliminates container management and idle process memory. However, `sqlite-vec` performs brute-force vector scans or simple virtual table indexing. It lacks Qdrant's advanced quantized vector indexing (SQ8 HNSW) and native vector payload pre-filtering capabilities.



**Recommendation**: If maintaining Qdrant in Podman pushes system RAM past stability limits during a 7B local model run, replacing Qdrant with `sqlite-vec` saves memory. However, if vector collections grow large and require filtered vector searches (e.g., searching within specific agent scopes or timestamp windows), Qdrant's payload-indexed HNSW and SQ8 quantization remain superior.

#### Assigning XYZ Coordinates

XYZ spatial/topological coordinates can be stored alongside vectors in both engines:

* **In Qdrant**: Store XYZ coordinates in the payload object:
```json
{
  "vector": [0.012, -0.043, ...],
  "payload": {
    "x": 12.45,
    "y": -3.11,
    "z": 0.88,
    "entity_id": "agent_alpha"
  }
}

```


Qdrant allows Range filtering on payload fields directly during vector search queries (e.g., `x BETWEEN 10.0 AND 15.0`).
* **In SQLite-vec**: Store XYZ coordinates as standard table columns adjacent to the virtual vector table, linked by row ID:
```sql
CREATE TABLE entity_vectors (
    id INTEGER PRIMARY KEY,
    x REAL, y REAL, z REAL,
    entity_id TEXT
);
-- Perform spatial filtering in standard SQL, joining with vec0 virtual table

```



---

### 2. Further Steps to Supercharge Local Inference

Beyond addressing execution thread decoupling, fixing KV-cache enum mappings, and resolving concurrency gates:

#### A. Pin System Prompts via Context Prefix Caching

Agent system prompts (`soul.yaml`), tool definitions, and governance rules are repetitive across turns. By configuring `llama.cpp` to keep prompt prefixes resident in the Key-Value (KV) cache across calls, prompt evaluation speed increases dramatically on subsequent turns.

#### B. Native GBNF / JSON Schema Constrained Sampling

Local 1.7B to 7B models can produce malformed JSON when executing tools, triggering costly retry loops. Enforcing JSON output structures at the sampler level using GBNF grammars or Pydantic JSON schemas forces `llama.cpp` to allow only valid syntax tokens during generation, eliminating tool-parsing failures entirely.

#### C. Transition to Importance Matrix Quantization (iMatrix / IQ)

Standard `Q4_K_M` quantizations apply static quantization across all model layers. Replacing `Q4_K_M` with iMatrix-quantized weights (such as `IQ4_XS` or `IQ3_S`) reduces model weight memory footprints by 0.5GB–1.0GB without a perceptible drop in reasoning quality, freeing system memory for longer context windows or background services.

#### D. Automatic Context Sliding Windows

Instead of throwing Out-Of-Memory errors when context windows fill up, configure `llama.cpp` sequence removal hooks to clear older context tokens while preserving the initial system prompt tokens.

---

### 3. Evaluation of `mempalace` and `headroom`

#### MemPalace (`mempalace`)

* **What it is**: A local-first memory framework using spatial metaphors (Wings for projects, Rooms for topics, Drawers for transcripts). Its core design principle is **verbatim storage**: it stores exact message transcripts without running LLM summarization passes during ingestion, achieving high retrieval scores (96.6% R@5 on LongMemEval) with zero LLM API costs at write time.


* **Will it benefit you?**: **Yes, conceptually, but do not import its dependencies blindly.**
* *Strengths*: Verbatim-first storage avoids lossy LLM summarization and reduces execution overhead.


* *Implementation Note*: Independent benchmarks show that MemPalace's high recall stems from storing raw text combined with vector search and metadata filters, rather than the spatial "Palace" abstraction itself. By default, MemPalace uses ChromaDB. Adding ChromaDB introduces another vector database alongside Qdrant/Postgres.


* *Action*: Adapt MemPalace's **verbatim-first pattern** directly into your existing Qdrant/SQLite stack: store raw message chunks with `wing` and `room` payload tags instead of adding a separate ChromaDB library.





#### Headroom (`headroomlabs-ai/headroom`)

* **What it is**: An open-source, local-first context compression layer built for AI agents. It intercepts tool outputs, terminal logs, code files, and RAG chunks before they hit the LLM, running structural compression (AST parsing for code, `SmartCrusher` array compression for JSON) to reduce prompt tokens while preserving necessary information. It runs locally as a proxy or MCP server.


* **Will it benefit you?**: **Yes, substantially.**
* *Why it helps local inference*: On an AMD Ryzen 5700U APU, prompt prefill processing ($pp512$) is the primary bottleneck during multi-step agent workflows. Large raw JSON outputs or verbose build logs saturate memory and cause slow prefill delays.


* *Impact*: Headroom compresses raw JSON tool outputs by 60%–95% and code files/logs by 15%–20% before sending them to `llama.cpp`. Shrinking prompt sizes keeps prefill execution fast and reduces KV-cache memory usage.


* *Action*: Deploy `headroom` as a local proxy or MCP server tool in front of the local gateway to automatically trim agent context before prompt generation.
