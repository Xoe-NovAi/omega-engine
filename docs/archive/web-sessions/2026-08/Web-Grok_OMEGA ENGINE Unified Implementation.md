<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

**OMEGA ENGINE**  
**Unified Implementation Manual v3.1**  
**Document Status:** Approved for Engineering Execution  
**Date:** 4 August 2026  

**Target Hardware:** AMD Ryzen 7 5700U + Vega 8 iGPU, 12 GB UMA  
**Target OS:** Ubuntu 24.04 LTS or 26.04 LTS (25.04 is EOL)  
**Core Stack:** Python 3.12, AnyIO, llama-cpp-python (Vulkan), Qdrant (INT8 + spatial), Redis (Symbolic WARM only), FastAPI, TRL/PEFT (GRPO), optional Headroom  

This manual unifies the concrete technical implementations from prior sessions with the architectural, hardware, and customization refinements developed in the current design thread. It is written for autonomous CLI / AI development agents.

---

### 0. Non-Negotiable Principles

1. **Engine = pure runtime logic.** Zero baked-in content, personalities, cosmologies, or ethics.
2. **WAD / IWAD model.**  
   - Engine (`src/omega/`) = immutable runtime.  
   - IWAD = required base content (default MaKaLi cosmology + default Guidance Set schema).  
   - PWAD = optional user/community packs (personalities, tools, memory policies, spatial themes, fine-tunes, alternative cosmologies). Users never fork the engine.
3. **Local sovereignty first.** Cloud models are optional planners / fallbacks only.
4. **Memory hierarchy is first-class:**  
   Physical RAM → 16 GB zRAM (zstd + multi-comp) → NVMe swap (lower priority) + cgroup protection.
5. **Vega 8 is the primary compute engine.** Full offload (`n_gpu_layers=-1`) + MoE expert offload/mmap + speculative pairs.
6. **Spatial memory from day one.** Every Qdrant payload carries `pos_x`, `pos_y`, `pos_z` (and extensible attributes).
7. **Guidance Sets are data.** Optional, packable, defeasible. Engine only provides the review/logging mechanism.
8. **Graceful degradation.** No single failure (network, inference, I/O) may crash the main loop.

---

### 1. Hardware & Environment Foundation

**BIOS / Kernel**
- Set UMA Frame Buffer to maximum available (or use modern `amdttm` parameters if required by kernel).
- Recommended zRAM: 16 GB, zstd, multi-comp, optional writeback.
- NVMe swap of 16–32 GB at lower priority.
- cgroup v2: protect the Omega daemon with `MemoryMin` / high `MemoryHigh`.

**System packages (Ubuntu 24.04/26.04)**
```bash
sudo apt update && sudo apt install -y build-essential cmake python3-dev python3-venv \
  vulkan-tools libvulkan-dev mesa-vulkan-drivers git curl redis-server
```

**Project skeleton**
```bash
mkdir -p omega-engine/{data/{telemetry,qdrant_storage},models,omega/{api,core,memory,telemetry},ui}
cd omega-engine
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

**Critical compile**
```bash
CMAKE_ARGS="-DGGML_VULKAN=ON" pip install llama-cpp-python --no-cache-dir --force-reinstall
```

**Core dependencies (pin appropriately)**
```
anyio>=4.4
fastapi>=0.111
uvicorn>=0.30
qdrant-client>=1.18
redis>=5.0
aiofiles
torch peft trl datasets transformers
elevenlabs
# optional but recommended
headroom-ai
```

**Environment variables**
```
ELEVENLABS_API_KEY=
ELEVENLABS_WEBHOOK_SECRET=
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379/0
MODEL_PATH=./models/...
```

---

### 2. Core Runtime Components

#### 2.1 Local Executor (`omega/core/llm.py`)
- Full Vega 8 offload (`n_gpu_layers=-1`).
- `n_batch=512`, `n_ctx` sized to remaining UMA headroom, `n_threads=8` (physical cores), `flash_attn=True`.
- Support for MoE expert offload (`--n-cpu-moe` / tensor overrides) and GBNF / JSON schema constraints.
- Optional speculative path (Gemma MTP or draft model).

#### 2.2 SEDA Ring-Bus (`omega/core/bus.py`)
AnyIO memory-object streams, topic-based fan-out, `send_nowait` with back-pressure drop, TaskGroup lifecycle.  
Memory logging, telemetry, UI streams, and inference stages are independent workers. Never block the generation path.

#### 2.3 Unified Memory Fabric

**Qdrant (single source of truth)**
- Collection with INT8 scalar quantization (`always_ram=True`).
- Payload indices on `user_id`, `memory_type`, `session_id`, spatial fields.
- Dual-branch retrieval:
  - Declarative (static facts/preferences) — no time decay.
  - Episodic (raw traces) — exponential time decay + consolidation penalty.
- **Mandatory spatial fields** on every point: `pos_x`, `pos_y`, `pos_z` (float), plus extensible attributes.

**Symbolic WARM Tier (Redis)**
- Task Canvas: lightweight markdown/JSON list of nodes.
- Bulky payloads stored under `payload:{node_id}` with TTL.
- LLM sees only the Canvas; retrieves full payload via tool `fetch_node_payload(node_id)` when needed.
- Top-down assembly order: L3 Persona (markdown file) → L1 Declarative facts → WARM Canvas.

**Background Consolidator**
- Runs on idle / low-pressure schedule.
- Clusters old episodic points, synthesizes declarative summaries, marks sources consolidated, writes spatial coordinates.

#### 2.4 Sovereign Bridge (`omega/api/bridge.py`)
- FastAPI endpoint `/webhooks/elevenlabs`.
- **Must** read raw body bytes before any JSON parsing for correct HMAC-SHA256 verification.
- 30-minute replay window.
- Instant 200 OK after publishing to SEDA bus (`system.log_event`).
- Never perform heavy work inside the webhook handler.

#### 2.5 Telemetry & Sovereignty Flywheel
- JSONL harvesters for SFT successes, DPO (local reject / cloud chosen), GRPO prompts.
- Nightly (or idle) GRPO loop using TRL + PEFT LoRA (4-bit), continuous batching, verifiable reward functions (schema match, etc.), constrained to remaining VRAM.
- All training data remains local.

#### 2.6 Guidance Set Mechanism (Engine-level only)
- Schema for optional Guidance Sets (list of ideals, expression form, review cadence, logging policy).
- Nightly / on-demand review hook.
- Defeasible: entity may stand by a choice with rationale.
- Full logging for later model × persona × guidance studies.
- Content of any Guidance Set lives in IWAD or PWAD.

---

### 3. MaKaLi Default IWAD (Base Content)

Three sovereign parts of one undivided whole (no hierarchy):

- **Maat** — light / build-time domain, order and structure.
- **Lilith** — dark / runtime domain, protects sovereignty and prevents ossification into law-without-heart.
- **Kali** — reconciling presence that holds tension and produces high-density synthesis.

Default pillar domains are currently engineering-focused (engine is still building itself). Future PWADs replace or extend them freely.

Hierarchical language (“apex”, “reports up to”, etc.) is incorrect and must be purged wherever it appears.

---

### 4. Directory Structure (Canonical)

```
omega-engine/
├── data/
│   ├── qdrant_storage/
│   ├── telemetry/          # .jsonl
│   └── persona.md          # L3 default
├── models/
├── omega/
│   ├── api/bridge.py
│   ├── core/
│   │   ├── bus.py
│   │   └── llm.py
│   ├── memory/
│   │   ├── router.py
│   │   ├── symbolic.py
│   │   └── consolidator.py
│   └── telemetry/
│       ├── logger.py
│       └── omega_train.py
├── ui/                     # optional Next.js / TUI
├── main.py
├── pyproject.toml / requirements
└── omega.service
```

---

### 5. Agent Execution Runbook (Strict Order)

1. Provision OS, Vulkan, zRAM + NVMe swap, cgroup, directory tree, venv, compile llama-cpp-python with Vulkan.
2. Implement and unit-test SEDA bus (`omega/core/bus.py`).
3. Implement Local Executor with full offload + GBNF.
4. Implement Symbolic WARM + Qdrant dual-branch router with spatial fields.
5. Wire non-blocking memory logger into the bus.
6. Implement Sovereign Bridge (raw-body HMAC) and publish to bus.
7. Implement telemetry harvesters and GRPO trainer.
8. Write `main.py` bootstrap (TaskGroup + bus + FastAPI + consolidator).
9. Create systemd unit with core pinning (`taskset -c 0-7`), MemoryMax, SIGTERM handling.
10. End-to-end verification script (mock signed webhook → SEDA → Qdrant write).
11. Optional: Headroom proxy, speculative draft pair, TUI / Mind Palace UI.

---

### 6. Systemd Unit (Production)

```ini
[Unit]
Description=Omega Engine Sovereign Daemon
After=network.target redis.service

[Service]
Type=simple
User=omega
WorkingDirectory=/opt/omega-engine
EnvironmentFile=/opt/omega-engine/.env
ExecStart=/usr/bin/taskset -c 0-7 /opt/omega-engine/venv/bin/python main.py
Restart=always
RestartSec=5
KillSignal=SIGTERM
TimeoutStopSec=20
MemoryHigh=10G
MemoryMax=11G

[Install]
WantedBy=multi-user.target
```

(Adjust Memory* values after measuring real pressure with 16 GB zRAM.)

---

### 7. Verification & Observability

- `vulkaninfo` confirms Vega 8.
- `zramctl` + `swapon --show` + PSI pressure.
- Mock signed ElevenLabs webhook → 200 + Qdrant point appears with spatial fields.
- SEDA back-pressure drop under artificial load.
- GRPO dry-run on a tiny telemetry file without OOM.
- Guidance Set review hook fires and logs without affecting generation latency.

---

### 8. Explicitly Parked / Future

- 42 Ideals of Maat (full design preserved; resumes post-debut as Guidance Set content).
- Deeper esoteric WADs (TDA, Qliphoth, etc.).
- Full Godot 4 / OpenXR spatial explorer (xyz fields already present).
- P2P Omegaverse realm protocol.
- Community WAD authoring tooling and safety model.

---

### 9. Success Criteria for v3.1 Debut

- Engine boots cleanly on 12 GB UMA with 16 GB zRAM.
- Full iGPU offload of an 8B-class model remains responsive under concurrent SEDA + memory + webhook load.
- Symbolic Canvas keeps context lean.
- Webhook → bus → Qdrant path is non-blocking and verified.
- Nightly GRPO can run without destabilizing the interactive path.
- A second PWAD (e.g. Scientific or Tarot Journey) can be loaded with zero engine code changes and produces a recognizably different experience.
- No hierarchical MaKaLi language remains in code or docs.

---

This manual is the single source of truth for implementation.  
All prior technical drafts are superseded by the patterns and constraints stated here.  

Proceed phase-by-phase according to the Agent Execution Runbook.  
Report any deviation from the hardware contract or the WAD purity rule immediately.
