# Architecture — Omega Engine Alpha

## 1. System Topology

```
┌──────────────────────────────────────────────────────────────────────┐
│  NODE 0 — HP Pavilion (ARCHIVAL BASTION & NEXUS)                     │
│  CPU  AMD Ryzen 7 5700U (8C/16T, DDR4 dual-channel)                 │
│  ──────────────────────────────────────────────────────────────     │
│  Git SSOT ............... omega-engine.bundle (main + release)      │
│  omega-hub .............. FastMCP, 91 sovereign tools on :8016      │
│  Stores ................. SQLite + Qdrant (library, hivemind,       │
│                            oracle, research)                        │
│  Council ................ kali · roc_racoon · grokster (+28        │
│                            registered entities)                    │
│  Roles .................. orchestration, archival, compliance      │
└──────────────▲──────────────────────┬──────────────────────────────┘
             │  LAN :8016           │  USB packet ceremony (bundle),
             │  Tailscale (P3.2)    │  Redis heartbeats (P3.2)
┌─────────────┴──────────────────────▼──────────────────────────────┐
│  NODE 1 — ASUS ExpertBook P1503CVA (EXPLORATION VANGUARD)          │
│  CPU  Intel i7-13620H (6P+4E, DDR5 single-channel, no GPU)         │
│  ──────────────────────────────────────────────────────────────     │
│  Ollama ................. systemd, AllowedCPUs=0-11, THREADS=8      │
│                            → 14.4 t/s, MAX_LOADED_MODELS=1         │
│  Open WebUI ............. :3000 (Docker)                            │
│  OpenCode ............... 1.18.30, Big Pickle 1M ctx (Zen)         │
│  gnosis-leash plugin .... session.created/idle/compacted events     │
│                            + compaction context injection           │
│                            + The Well active rules injection        │
│  WanderGround ........... sqlite-vec atlas, MemPalace, MkDocs,     │
│                            Three.js/WebXR 3D, munin curator        │
│  Gnosis Lock ............ 9-step ritual, evolution log, identity   │
│  The Well ............... corrections/tips corpus (43 tests green) │
│  Ponytail ............... lazy-senior-dev plugin (modes off/on)    │
└──────────────────────────────────────────────────────────────────────┘
```

## 2. Silicon Specialization (why)

- **HP**: AMD Zen-2 8C/16T, DDR4 dual-channel. Archival stability, dense
  vector stores, orchestration, 91-tool hub — value in *retention*.
- **ASUS**: Intel Raptor Lake-H, AVX2+VNNI on P-cores. Fast single-stream
  inference — value in *throughput* and *experimentation*.

This is a **P2P federation, not a master/slave** — either node can be offline
independently. Sovereignty is per-node.

## 3. Inference Path (Node 1)

```
OpenCode / OWUI / chatbot
        │
        ▼
Ollama (localhost:11434)
        │  systemd override:
        │   • AllowedCPUs=0-11 (P-core range incl. HT siblings)
        │   • OLLAMA_NUM_THREADS=8
        │   • OLLAMA_KV_CACHE_TYPE=q8_0, OLLAMA_FLASH_ATTENTION=1
        │   • OLLAMA_MAX_LOADED_MODELS=1 (16GB single-channel discipline)
        ▼
llama-server → GGUF Q4_K_M → avx_vnni dispatch on P-cores
        │
        ▼
13.4–14.4 t/s on 3B-4B models
```

**Deep synthesis (cross-corpus, long-context) does NOT run local.** It routes
to OpenCode Zen:
- Free tiers (Big Pickle, MiMo V2.5 Free, Nemotron 3 Ultra Free) — **data-collecting**, fine for innocuous work.
- Paid tiers (Muse Spark 1.3, MiniMax, GLM, Kimi) — zero-retention, required for private material.
- See `WANDERGROUND_SPEC.md §10.4` for the full privacy tier table.

## 4. Federation Protocol Layers

| Layer | Transport | Node 0 | Node 1 |
|-------|-----------|--------|--------|
| L1 LAN | Streamable HTTP `POST /mcp` | `0.0.0.0:8016` | `192.168.10.168:8016/mcp` |
| L2 Tailscale | WireGuard / MagicDNS | `hp.tailnet:8016` | `asus.tailnet` |
| L3 Redis Pub/Sub | Ephemeral heartbeats | aware events | awareness (graceful to lockfiles) |

Handoff contract (4 steps):
`post_context → submit_handoff → accept_handoff → complete_handoff`
with pending/stale/active/completed queues in Hivemind.

## 5. Data Flows

### Capture (Node 1)
```
wander "spark" → inbox/*.md → wander-curator (systemd) → knowledge_atlas.db
                                                         → MemPalace palace
                                                         → MkDocs docs/
                                                         → The Well (kind:dream)
```

### Continuity (both nodes)
```
session.created ─┐
session.idle ────┼→ gnosis-leash plugin → gnosis-events.jsonl
session.compacted┘
/compact → experimental.session.compacting → inject WanderGround rules + The Well rules + human narrative
make gnosis-lock → evolution_log.jsonl + identity.json ++
```

### Federation (Node 1 → HP)
```
dossiers/ (matured) → [explicit user flag] → library_inbox_add_file
                                                  → omega_library on HP
```

### Model research registry
```
web research → docs/models/<provider>-<model>.md
             → evidence labels + Omega verdict
             → local A/B (when applicable)
             → ROADMAP decision
```

Model cards are decision records, not marketing summaries. Every card separates
verified metadata, provider claims, independent reports, and local measurements;
rejected cards remain available for future comparisons.

## 6. Security Boundaries

- `omega-hub` binds LAN only; token auth recommended (ask #4/#C).
- MemPalace/Ollama bind localhost; OWUI bound to LAN deliberately.
- Secrets in `.env.*` local only; examples committed; real `.env` gitignored.
- Research log: private queries policy (decided on HP side, C5).

## 7. Lifecycle

- Systemd: `ollama.service` (system), `wander-curator.{service,timer}` (user, linger on).
- Docker: `open-webui` (pinned v0.11.3), restart unless-stopped.
- Backups: `scripts/backup_harness.sh` → cron 02:30, --usb optional.
- Gnosis identity: `gnosis/identity/identity.json` (currently session 25).