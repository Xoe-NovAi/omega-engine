# ⬡ Omega Engine Alpha

**A sovereign, CPU-only local-AI harness for the ASUS ExpertBook P1503CVA (Node 1) — paired with the HP Pavilion Archival Bastion (Node 0) in a dual-node P2P federation.**

[![OpenCode](https://img.shields.io/badge/OpenCode-1.18.32-61dafb?logo=opencode)](https://opencode.ai)
[![Ollama](https://img.shields.io/badge/Ollama-0.33.3-ff6b35?logo=ollama)](https://ollama.ai)
[![Big Pickle](https://img.shields.io/badge/Big%20Pickle-dynamic%20runtime-8b5cf6?logo=opencode)](https://opencode.ai/zen)
[![Status](https://img.shields.io/badge/Status-Active%20Development-00ff88)](https://github.com/xnai/omega-engine-alpha)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🎯 What This Is

**Omega Engine Alpha** is a local-first AI development harness that turns a commodity laptop (ASUS ExpertBook P1503CVA, Intel i7-13620H, 16GB DDR5, no GPU) into a **sovereign inference engine** capable of:

- **14.4 tokens/sec** on 3B-4B models (CPU-only, P-core + HT sibling pinning)
- **Hosted long-context routes** with live capacity metadata; local Ollama context is capped at `OLLAMA_CONTEXT_LENGTH=8192`
- **Dual-node P2P federation** with HP Pavilion (Node 0) — HP runs the Archival Bastion (Git SSOT, omega-hub MCP, Qdrant/SQLite stores); ASUS runs the Exploration Vanguard (CPU inference, local memory, real-time experimentation, and the target spatial-knowledge migration)
- **Gnosis Lock Protocol** — fallback session reflection and recovery across compactions (9-step ritual, evolution log, identity tracking)
- **Portable Continuity Kernel** — local SQLite is the authoritative continuity state/event store; MemPalace is a one-way searchable projection
- **Spatial knowledge target** — sqlite-vec atlas, MemPalace projection, and Three.js/WebXR constellations; the atlas/viewer are not currently deployed on Node 1

---

## ⚡ Quickstart (Node 1 — This Machine)

```bash
# 1. Clone & enter
git clone https://github.com/xnai/omega-engine-alpha.git
cd omega-engine-alpha

# 2. One-shot environment setup (requires sudo for systemd)
cp .env.ollama.example .env.ollama
make env-setup
make env-show
make status

# 3. Verify inference speed
make bench MODEL=phi4-mini

# 4. Launch chat or HTTP server
make python-chatbot        # Interactive CLI
make python-serve          # OpenAPI server on :8000

# 5. Open WebUI (runs in Docker on :3000)
docker compose up -d

# 6. Federation (requires Node 0; see the federation operator guide)
# This repository does not ship live first-contact scripts.
# Start with: docs/federation/README.md
```

**Requirements:** Ubuntu 26.04+, 16GB+ RAM, Python 3.12+, Docker, `loginctl enable-linger $USER` (for systemd user timers).

---

## 🏗️ Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│  NODE 0 (HP Pavilion) — ARCHIVAL BASTION                        │
│  • Git SSOT (omega-engine.bundle)                               │
│  • omega-hub MCP (55 tools live 2026-10-07)                                │
│  • Qdrant + SQLite stores, Hivemind coordination                │
│  • Council agents (kali, roc_racoon, grokster, ...)             │
└──────────────────────────┬──────────────────────────────────────┘
                           │ LAN :8016  /  Tailscale
┌──────────────────────────▼──────────────────────────────────────┐
│  NODE 1 (ASUS ExpertBook) — EXPLORATION VANGUARD                │
│  • Ollama (14.4 t/s, P-core+HT pin) + Open WebUI (:3000)        │
│  • Big Pickle + hosted routes (live capacity metadata)          │
│  • WanderGround: MemPalace live; sqlite-vec atlas/3D viewer target │
│  • gnosis-leash plugin: auto Gnosis Lock + compaction injection │
│  • Gnosis Lock: 9-step ritual, evolution log, identity ledger    │
└─────────────────────────────────────────────────────────────────┘
```

**Silicon Specialization:** Node 0 = AMD Ryzen 7 5700U (8C/16T, DDR4 dual-channel) — archival stability; Node 1 = Intel i7-13620H (6P+4E, DDR5 single-channel) — raw inference throughput.

---

## 🔍 Session Recall

Two years of agent work lives in a local SQLite database. These tools let you (and any
agent) search it instead of asking the user to repeat themselves.

```bash
# Install (once)
sudo npm install -g agent-historian && ochist skill install --global   # cross-agent recall
pip install sqlite-utils                                                 # optional FTS5 layer

# Search past conversations (regex; --global avoids project-only misses)
ochist grep "pin trap" --global --limit 5
ochist sessions --limit 10
ochist show <session-slug>            # outline first, then drill down
ochist part <part-id>                 # exact text of one part

# Structured questions — counts, cost, schema, which sessions edited a file
ocdb-ro --search "gnosis" --limit 5
ocdb-ro "SELECT ROUND(SUM(cost),2) AS usd FROM session"
ocdb-ro --schema part
```

Three agent skills are auto-discovered from `~/.agents/skills/`: `agent-history`
(prose recall), `opencode-db` (structured queries), `claude-history` (Claude/Pi/OMP).

> ⚠️ **Never run `opencode db <query>` against production `opencode.db`.** It opens the
> database read-write and executes DDL/DML freely — verified by an accidental write
> during this work. Use `ocdb-ro`, which enforces read-only twice over. Also never use
> `immutable=1`: it ignores the WAL and silently returns stale data.

Strategy, citations, and the 46 GB Node 0 case:
**[OPENCODE_DB_MANAGEMENT_BRIEFING.md](docs/OPENCODE_DB_MANAGEMENT_BRIEFING.md)** ·
Porting rules: **[PORTABILITY.md](docs/PORTABILITY.md)**

---

## 📚 Documentation Index

Start at **[docs/INDEX.md](docs/INDEX.md)** for the full map. Curated highlights:

| Document | Audience | Purpose |
|----------|----------|---------|
| **[INSTALLATION.md](docs/INSTALLATION.md)** | Operators | Reproducible Node 1 installation and verification |
| **[USER_GUIDE.md](docs/USER_GUIDE.md)** | End users | Local inference, memory, recovery, and optional-service workflows |
| **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** | Operators/agents | Symptom diagnosis, safe recovery, and escalation |
| **[PRIVACY_SECURITY.md](docs/PRIVACY_SECURITY.md)** | Operators/agents | Data classes, hosted-model policy, secrets, and federation boundaries |
| **[GETTING_STARTED.md](docs/GETTING_STARTED.md)** | New users | Shortest safe path from zero |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Everyone | System topology, data flows, federation |
| **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** | Contributors | Code conventions, testing, PR flow |
| **[PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md)** | Plugin authors | OpenCode plugin + gnosis-leash pattern |
| **[WANDERGROUND_SPEC.md](docs/WANDERGROUND_SPEC.md)** | Explorers | Spatial knowledge, MemPalace, 3D substrate |
| **[CODE_QUALITY.md](docs/CODE_QUALITY.md)** | Devs | Absolute anyio async wiring, no torch, style |
| **[SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md)** | Operators | Live ops, session log, hardware tuning |
| **[HARDWARE.md](docs/HARDWARE.md)** | Engineers | Pin-trap, BIOS, thermal, RAM, storage |
| **[AGENT_RUNBOOK.md](docs/AGENT_RUNBOOK.md)** | Agents | Node 1 ops awareness: gnosis-lock, /compact, quality gates |
| **[GNOSIS_USAGE.md](docs/GNOSIS_USAGE.md)** | Operators | Gnosis Lock protocol deep-dive & exact commands |
| **[WELL_SYSTEM.md](docs/WELL_SYSTEM.md)** | Everyone | The Well: operating-memory corpus, schema, auto-injection into system prompts |
| **[OPENCODE_DB_MANAGEMENT_BRIEFING.md](docs/OPENCODE_DB_MANAGEMENT_BRIEFING.md)** | Operators/agents | Session-DB read, search, index, backup strategy; the 46 GB case; 35 cited sources |
| **[PORTABILITY.md](docs/PORTABILITY.md)** | Engine developers | What must not leak into the future Omega CLI |
| **[CONTINUITY_KERNEL.md](docs/CONTINUITY_KERNEL.md)** | Engine developers | Portable semantic write-through kernel, WAD contract, and recovery acceptance test |
| **[Federation Subsystem](docs/federation/README.md)** | Everyone | Dual-node P2P architecture, NFSv4.2, Tailscale WireGuard, Two-Phase ACLs |
| **[ROADMAP.md](docs/ROADMAP.md)** | Everyone | Single ordered backlog: phases, vanguard tools, finish gates |
| **[Model cards](docs/models/README.md)** | Researchers | Canonical model registry, evidence labels, and card contract |
| **[Nex-N2.5-Pro card](docs/models/nex-n2-5-pro.md)** | Model evaluators | Current OpenRouter candidate, strengths, quirks, and validation plan |
| **[SYSTEM_GUIDE.md#12-session-log-append-only](docs/SYSTEM_GUIDE.md#12-session-log-append-only)** | Historians | Append-only session log (2026-09-08 → present) |

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
# Capture a fallback/recovery pack; then run /gnosis-lock reflection
make gnosis-lock
# After reflection, type /compact with no arguments in the TUI.

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
- **Federation Spec**: [docs/federation/README.md](docs/federation/README.md)

---

*Built with sovereignty, curiosity, and a refusal to accept black-box AI.*