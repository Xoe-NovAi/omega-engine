# ⬡ Omega Engine Alpha

**A sovereign, CPU-only local-AI harness for the ASUS ExpertBook P1503CVA (Node 1) — paired with the HP Pavilion Archival Bastion (Node 0) in a dual-node P2P federation.**

[![OpenCode](https://img.shields.io/badge/OpenCode-1.18.30-61dafb?logo=opencode)](https://opencode.ai)
[![Ollama](https://img.shields.io/badge/Ollama-0.33.3-ff6b35?logo=ollama)](https://ollama.ai)
[![Big Pickle](https://img.shields.io/badge/Big%20Pickle-1M%20ctx-8b5cf6?logo=opencode)](https://opencode.ai/zen)
[![Status](https://img.shields.io/badge/Status-Active%20Development-00ff88)](https://github.com/xnai/omega-engine-alpha)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🎯 What This Is

**Omega Engine Alpha** is a local-first AI development harness that turns a commodity laptop (ASUS ExpertBook P1503CVA, Intel i7-13620H, 16GB DDR5, no GPU) into a **sovereign inference engine** capable of:

- **14.4 tokens/sec** on 3B-4B models (CPU-only, P-core + HT sibling pinning)
- **1M-token context** via OpenCode Zen's Big Pickle (cloud) + local 8K-128K context
- **Dual-node P2P federation** with HP Pavilion (Node 0) — HP runs the Archival Bastion (Git SSOT, omega-hub MCP, Qdrant/SQLite stores); ASUS runs the Exploration Vanguard (CPU inference, spatial knowledge, real-time experimentation)
- **Gnosis Lock Protocol** — cryptographic session continuity across compactions (9-step ritual, evolution log, identity tracking)
- **Spatial knowledge substrate** — sqlite-vec 3D embeddings, MemPalace episodic memory, Three.js/WebXR concept constellations

---

## ⚡ Quickstart (Node 1 — This Machine)

```bash
# 1. Clone & enter
git clone https://github.com/xnai/omega-engine-alpha.git
cd omega-engine-alpha

# 2. One-shot environment setup (Ollama pinning, Open WebUI, systemd)
make env-setup
make env-apply

# 3. Verify inference speed
make bench MODEL=phi4-mini

# 4. Launch chat or HTTP server
make python-chatbot        # Interactive CLI
make python-serve          # OpenAPI server on :8080

# 5. Open WebUI (runs in Docker on :3000)
docker compose up -d

# 6. Federation status (requires Node 0 online)
./test_connection.sh
python3 ~/hivemind_first_contact.py
```

**Requirements:** Ubuntu 26.04+, 16GB+ RAM, Python 3.12+, Docker, `loginctl enable-linger $USER` (for systemd user timers).

---

## 🏗️ Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│  NODE 0 (HP Pavilion) — ARCHIVAL BASTION                        │
│  • Git SSOT (omega-engine.bundle)                               │
│  • omega-hub MCP (91 tools on :8016)                            │
│  • Qdrant + SQLite stores, Hivemind coordination                │
│  • Council agents (kali, roc_racoon, grokster, ...)             │
└──────────────────────────┬──────────────────────────────────────┘
                           │ LAN :8016  /  Tailscale
┌──────────────────────────▼──────────────────────────────────────┐
│  NODE 1 (ASUS ExpertBook) — EXPLORATION VANGUARD                │
│  • Ollama (14.4 t/s, P-core+HT pin) + Open WebUI (:3000)        │
│  • Big Pickle (1M ctx) + OpenCode Zen free/paid models          │
│  • WanderGround: sqlite-vec 3D, MemPalace, MkDocs, 3D viewer    │
│  • gnosis-leash plugin: auto Gnosis Lock + compaction injection │
│  • Gnosis Lock: 9-step ritual, evolution log, identity v17      │
└─────────────────────────────────────────────────────────────────┘
```

**Silicon Specialization:** Node 0 = AMD Ryzen 7 5700U (8C/16T, DDR4 dual-channel) — archival stability; Node 1 = Intel i7-13620H (6P+4E, DDR5 single-channel) — raw inference throughput.

---

## 📚 Documentation Index

| Document | Audience | Purpose |
|----------|----------|---------|
| **[GETTING_STARTED.md](docs/GETTING_STARTED.md)** | End users | 5-minute spin-up from zero |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Everyone | System topology, data flows, federation |
| **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** | Contributors | Code conventions, testing, PR flow |
| **[PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md)** | Plugin authors | OpenCode plugin + gnosis-leash pattern |
| **[WANDERGROUND_SPEC.md](docs/WANDERGROUND_SPEC.md)** | Explorers | Spatial knowledge, MemPalace, 3D substrate |
| **[CODE_QUALITY.md](docs/CODE_QUALITY.md)** | Devs | Absolute anyio async wiring, no torch, style |
| **[SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md)** | Operators | Live ops, session log, hardware tuning |
| **[HARDWARE.md](docs/HARDWARE.md)** | Engineers | Pin-trap, BIOS, thermal, RAM, storage |
| **[SYSTEM_GUIDE.md#12-session-log](docs/SYSTEM_GUIDE.md#12-session-log)** | Historians | Append-only session log (2026-09-08 → present) |

---

## 🧪 Make Targets (The Daily Interface)

```bash
make help                  # List all targets
make bench MODEL=phi4-mini # Inference benchmark
make bench-all             # Full model sweep
make python-chatbot        # Interactive CLI
make python-serve          # HTTP server
make env-setup|env-apply|env-revert  # Ollama systemd round-trip
make gnosis-lock           # 9-step pre-compaction ritual
make gnosis-stats          # Evolution log stats
make create-coder MODEL=... # Build custom Modelfile model
```

---

## 🔐 Gnosis Lock Protocol (Session Continuity)

```bash
# Run before any compaction (automated via gnosis-leash plugin)
make gnosis-lock

# Manual ritual steps:
# 1. Capture git state, opencode config, MCP status
# 2. Build system_state.json (validated JSON)
# 3. Write narrative + evolution log entry
# 4. Log SESSION_END event (evolution log v1.0)
# 5. Update identity.json (session counter++)
```

---

## 🤝 Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** — code-quality gates (absolute anyio, no torch, test coverage), PR template, code-review checklist, semantic commits.

---

## 📜 License

**MIT** — see [LICENSE](LICENSE). All code, docs, and configs are free to use, modify, and distribute.

---

## 🔗 Links

- **OpenCode Zen Models**: https://opencode.ai/zen
- **MemPalace**: https://github.com/MemPalace/mempalace
- **sqlite-vec**: https://github.com/asg017/sqlite-vec
- **Gnosis Lock Spec**: [docs/WANDERGROUND_SPEC.md](docs/WANDERGROUND_SPEC.md)
- **Federation Spec**: [docs/WANDERGROUND_SPEC.md#4-federation--p2p](docs/WANDERGROUND_SPEC.md#4-federation--p2p)

---

*Built with sovereignty, curiosity, and a refusal to accept black-box AI.*