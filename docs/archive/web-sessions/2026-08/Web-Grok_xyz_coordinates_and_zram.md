<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

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
