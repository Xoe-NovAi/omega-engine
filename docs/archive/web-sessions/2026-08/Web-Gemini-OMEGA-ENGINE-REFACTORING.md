# OMEGA ENGINE REFACTORING & TEMPLE HARDENING MANUAL (v3.1 / v1.9.0)

**Document Status:** Authoritative Engineering Manual
**Target Hardware:** AMD Ryzen 7 5700U + Vega 8 iGPU (12 GB UMA)
**Core Architecture:** Immutable Runtime + WAD Data Stack (IWAD/PWAD)
**Primary Environment:** OpenCode CLI, Ubuntu Linux

---

## Non-Negotiable Architectural Principles

1. **Engine Runtime Purity:** The core codebase (`src/omega/`) strictly encapsulates execution logic. It contains zero hardcoded cosmologies, personalities, ethical codes, or domain specifics.
2. **WAD Layering Paradigm:** System identity and capabilities are declared entirely via interchangeable data packages.
* **Engine (`src/omega/`):** Immutable runtime logic.
* **Base IWAD:** Essential default schema, base memory rules, and default Guidance Sets.
* **PWADs (Patch WADs):** Plug-and-play packs containing persona modules, domain toolsets, fine-tuned adapters, and custom spatial themes.


3. **Horizontal Triad Co-Equality:** The MaKaLi framework represents three co-equal, sovereign components of an undivided whole—**Maat** (structure/build-time order), **Lilith** (runtime sovereignty/anti-ossification), and **Kali** (reconciling synthesis). Hierarchical terms ("apex", "reports to") are strictly forbidden.
4. **Local Hardware Supremacy:** Full computational offload to the Vega 8 iGPU, context prefill compression, 16 GB zRAM compression, and zero-telemetry local operation. Cloud endpoints function strictly as opt-in planners or fallback executors.

---

## I. Hardware Allocation, Memory Hierarchy & OS Hardening

### 1.1 Memory Tiering & Kernel Tuning

The Ryzen 7 5700U relies heavily on proper memory partitioning between the physical 12 GB UMA pool and compressed memory blocks.

* **zRAM Configuration:** Configure `/etc/systemd/zram-generator.conf` to establish a 16 GB compressed memory tier using `zstd`.
```ini
[zram0]
zram-size = 16384
compression-algorithm = zstd
max-zram-size = 16384

```


* **Kernel Parameters:** Apply sysctl memory rules via `/etc/sysctl.d/99-omega-memory.conf` to push cold pages toward the 16–32 GB NVMe swap file.
```ini
vm.swappiness = 80
vm.vfs_cache_pressure = 50
vm.dirty_background_ratio = 5
vm.dirty_ratio = 10

```


* **cgroup v2 Protection:** Protect the primary runtime inside `/etc/systemd/system/omega.service`.
```ini
[Unit]
Description=Omega Engine Sovereign Daemon
After=network.target

[Service]
Type=simple
User=omega
WorkingDirectory=/opt/omega-engine
EnvironmentFile=/opt/omega-engine/.env
ExecStart=/usr/bin/taskset -c 0-7 /opt/omega-engine/venv/bin/python main.py
Restart=always
RestartSec=5
MemoryAccounting=true
MemoryMin=4G
MemoryHigh=10G
MemoryMax=11G

[Install]
WantedBy=multi-user.target

```



### 1.2 Inference Engine Tuning

* Compile `llama-cpp-python` with `DGGML_VULKAN=ON` to utilize the Vega 8 graphics queue.
* Configure the environment with `export GGML_VK_ALLOW_GRAPHICS_QUEUE=1`.
* Ensure full iGPU offloading (`n_gpu_layers=-1`), physical core pinning (`n_threads=8`), and `n_batch=512`.

### 1.3 Context Compression & RAM Conservation

* **AST Compression:** Route verbose JSON/tool payloads through a local proxy running `SmartCrusher` array compression prior to prompt injection, easing KV-cache allocation.
* **Lightweight TTS:** Utilize **Piper** or **Kokoro** natively as a dedicated CPU sub-process, preserving VRAM entirely for the LLM.

---

## II. Concurrency, Event Routing & SEDA Bus

### 2.1 AnyIO Structured Concurrency

All asynchronous execution loops must utilize AnyIO `TaskGroup` contexts (`anyio>=4.4`) with strict cancellation semantics. Blocking operations on the main thread during concurrent tool runs or streaming are prohibited.

### 2.2 SEDA Ring-Bus Architecture

Implement a Staged Event-Driven Architecture (SEDA) over non-blocking memory streams.

```python
import anyio
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream
from typing import Dict, Any, List

class SEDARingBus:
    def __init__(self, buffer_size: int = 1024):
        self.buffer_size = buffer_size
        self.subscribers: Dict[str, List[MemoryObjectSendStream]] = {}

    def subscribe(self, topic: str) -> MemoryObjectReceiveStream:
        send_stream, receive_stream = anyio.create_memory_object_stream(self.buffer_size)
        self.subscribers.setdefault(topic, []).append(send_stream)
        return receive_stream

    async def publish(self, topic: str, event: Dict[str, Any]) -> None:
        if topic in self.subscribers:
            dead_streams = []
            for stream in self.subscribers[topic]:
                try:
                    stream.send_nowait(event)
                except anyio.WouldBlock:
                    pass # Back-pressure drop policy
                except anyio.ClosedResourceError:
                    dead_streams.append(stream)
            for dead in dead_streams:
                self.subscribers[topic].remove(dead)

bus = SEDARingBus()

```

---

## III. Memory Subsystem & Spatial Substrate

The architecture relies on a strictly Postgres-free, localized Qdrant configuration to manage vectors and JSON payload structures simultaneously.

### 3.1 Direct Qdrant Configuration

Deploy Qdrant with Scalar INT8 Quantization (`SQ8`) to drastically minimize the RAM footprint, operating completely independently of relational database overlays.

```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, ScalarQuantization, ScalarQuantizationConfig, ScalarType

def initialize_qdrant_schema(client: QdrantClient, collection_name: str = "omega_memory"):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            quantization_config=ScalarQuantization(
                scalar=ScalarQuantizationConfig(type=ScalarType.INT8, always_ram=True)
            )
        )
        for field in ["user_id", "memory_type", "session_id"]:
            client.create_payload_index(collection_name, field_name=field, field_schema="keyword")

```

### 3.2 Dual-Branch Rescoring Math

Retrieval pipelines apply continuous mathematical decay to surface context:

* **Declarative Score:** $Score_{decl} = Similarity \times (1.0 + 0.5 \times Importance)$
* **Episodic Score:** $Score_{episodic} = Similarity \times e^{-\lambda \cdot \Delta t} \times S_{consol}$

Where $S_{consol} = 0.4$ if the memory is already clustered and consolidated, else $1.0$.

### 3.3 Spatial Memory Generation

To support visual frontends, every Qdrant point must include XYZ coordinates mapped into its JSON payload alongside structural attributes (`spatial_scale`, `spatial_color`, `spatial_layer`). These are generated via dimensionality reduction (UMAP/t-SNE) mapped over the 384-dimension embedding vectors.

---

## IV. Engine-Level Guidance & Defeasibility

### 4.1 Pure Data Guidance Sets

The Omega Engine processes moral, structural, or behavioral constraints entirely through data files passed in the WAD architecture.

```python
from pydantic import BaseModel
from typing import List

class GuidanceIdeal(BaseModel):
    id: str
    statement: str
    expression_form: str  
    weight: float = 1.0

class GuidanceSet(BaseModel):
    pack_id: str
    title: str
    review_cadence: str   
    ideals: List[GuidanceIdeal]

```

### 4.2 Defeasibility Engine

Entities are permitted to deviate from a loaded Guidance Set provided the divergence is captured and logged with a mathematically evaluated rationale. These deviations are dumped into local `.jsonl` audit trails for later DPO/GRPO training.

---

## V. Sovereign Bridge & External Ingestion

FastAPI acts as the ingress bridge. Webhooks (such as ElevenLabs triggers) must read raw HTTP body bytes directly to compute HMAC-SHA256 signatures prior to executing any JSON parsing, securing the engine against malformed payload attacks. Ensure a strict 30-minute replay protection window is enforced on timestamps.

---

## VI. Local Sovereignty Flywheel

* **Telemetry Harvesting:** Extract successful tool execution traces and defeasibility overrides into `executor_dpo.jsonl`.
* **GRPO Trainer:** Execute a continuous batching loop using `TRL` and PEFT (4-bit LoRA), constrained strictly under cgroup limits to prevent OS lockups. A verifiable reward function checks for correct JSON schema formatting in model completions to dynamically update weights.

---

## VII. End-to-End Qdrant Verification

Use the following pipeline test to validate the Postgres-free Qdrant implementation before initializing the SEDA bus.

```python
from qdrant_client import QdrantClient, models

def verify_qdrant_foundation():
    print("[+] Testing Postgres-Free Qdrant Setup...")
    client = QdrantClient(path="./data/qdrant_db")
    collection_name = "omega_memory"
    
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
        )
    
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=1,
                vector=[0.1] * 384,
                payload={"memory_type": "declarative", "content": "Foundation test", "pos_x": 1.2, "pos_y": 0.5, "pos_z": -1.1}
            )
        ]
    )
    
    res = client.retrieve(collection_name=collection_name, ids=[1])
    assert len(res) == 1
    assert res[0].payload["memory_type"] == "declarative"
    print("[✔] Solid Qdrant Foundation Verified.")

if __name__ == "__main__":
    verify_qdrant_foundation()

```

---

## VIII. Platform Migration & OpenCode CLI Operations

The `gemini-xna` and `opencode-xna` frameworks are entirely deprecated in favor of streamlining operations. The OpenCode command line interface functions as the singular, primary AI development platform.

Bind the OpenCode CLI directly to the local engine using the OpenAI-compatible REST API endpoint exposed by the Vulkan-accelerated backend:

```bash
export OPENCODE_API_BASE="http://127.0.0.1:8080/v1"
export OPENCODE_API_KEY="omega-local-key"
opencode config set default_model "local-executor-base"

```

---

## IX. Data Sanitization & Legacy Architecture Purge

The previous twenty-six sphere toroidal architecture and the one hundred and eight gates have been strictly deprecated. Ensure all initial WAD configurations and databases are purged of these concepts.

```python
from qdrant_client import QdrantClient, models

def purge_legacy_architectures():
    client = QdrantClient(path="./data/qdrant_db")
    collection_name = "omega_memory"
    deprecated_terms = ["26 sphere toroidal", "108 gates"]

    for term in deprecated_terms:
        client.delete(
            collection_name=collection_name,
            points_selector=models.Filter(
                must=[models.FieldCondition(key="content", match=models.MatchText(text=term))]
            )
        )
    print("[✔] Legacy architectures successfully purged from Qdrant.")

if __name__ == "__main__":
    purge_legacy_architectures()

```

---

## X. Multi-Persona Podcast Ingestion (NotebookLM)

To supply NotebookLM with multi-persona text transcripts, the 3-persona system generation must have loose behavioral constraints. Over-constraining the personas degrades foundational output.

* **Relaxed Prompting:** Focus explicitly on foundational structural elements: distinct speaker tags (`Speaker A`, `Speaker B`, `Speaker C`) and clear semantic transitions.
* **Vector Feeding:** Allow the Qdrant instance to fetch contextual nodes based entirely on cosine similarity and episodic decay equations. Feed these nodes into the prompt as raw context, allowing NotebookLM to synthesize the final audio structure without competing against rigid behavioral directives inside the local pre-processing pipeline.
