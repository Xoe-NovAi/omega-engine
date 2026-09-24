# User Guide — Omega Engine Alpha

**Audience:** People using the Node 1 local inference and memory systems.  
**Principle:** The local harness is sovereign and CPU-first, but not every planned subsystem is live yet. This guide distinguishes what you can use now from what is target architecture.

## 1. Choose an interface

| Interface | Use it for | Command | Current state |
|---|---|---|---|
| Ollama CLI | Fastest direct local chat | `make chat-fast` | Live |
| Python CLI | Streaming terminal chat | `make python-chatbot` | Live after `make python-setup` |
| HTTP wrapper | Small local integrations | `make python-serve` | Live on port 8000 by default |
| Open WebUI | Browser-based chat | `make webui` | Optional Docker service on port 3000 |
| MemPalace | Search and organize memory | WanderGround/MCP tools | Local memory is available |
| Gnosis | Session reflection/recovery | `/gnosis-lock`, `/compact` | Available as fallback recovery |
| Spatial atlas | 3D exploration | `~/WanderGround` target services | Not currently deployed |
| Federation | Node 0 coordination | Federation operator procedures | Requires Node 0 |

## 2. Start local chat

The fastest path:

```bash
make chat-fast
```

The Python path:

```bash
make python-setup
make python-test
make python-chatbot
```

The Python setup creates `.venv` and installs the Ollama Python SDK. The chatbot uses `phi4-mini` unless another model is supplied:

```bash
make python-chatbot MODEL=qwen2.5-coder:7b
```

Model availability and performance are host-specific. Measure before making claims.

## 3. Use the browser interface

Start Ollama and Open WebUI:

```bash
make webui
```

Open:

```text
http://localhost:3000
```

Check the container:

```bash
make webui-status
make webui-logs
```

Stop it:

```bash
make webui-down
```

For the 16 GB single-channel Node 1 profile, keep one model resident:

```text
OLLAMA_MAX_LOADED_MODELS=1
```

If a model reloads unexpectedly, check the per-model Keep Alive setting in Open WebUI. Leave `num_ctx` unset so the Ollama server context is inherited.

## 4. Call the local HTTP wrapper

Start the service:

```bash
make python-serve
```

Default URL:

```text
http://localhost:8000
```

Check health:

```bash
curl http://localhost:8000/health
```

Send a chat request:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Explain local-first inference.","stream":false}'
```

The wrapper is intentionally small. It is not the durability, federation, or spatial-memory API.

## 5. Choose local versus hosted work

### Local Ollama is appropriate for

- routine coding help;
- short local conversations;
- private corpus analysis that stays on the machine;
- lightweight classification and extraction;
- benchmark and model-card work.

### Hosted routes are appropriate for

- public research;
- large multi-document synthesis;
- frontier reasoning;
- work that explicitly requires a hosted model capability.

### Privacy rule

Private material uses paid zero-retention routes only. Free hosted routes, including Space Bunny, are treated as public/non-sensitive routes under the current conservative policy. Never assume a free route is private merely because its price is zero or its alias is stable.

## 6. Measure a model before adopting it

```bash
make pull MODEL=phi4-mini
make bench MODEL=phi4-mini
make bench-all
make bench-compare
```

Record:

- model and quantization;
- prompt count;
- warm/cold state;
- host power mode;
- throughput;
- resident memory;
- output quality;
- date.

A model card is a decision record, not a marketing summary. Provider claims and local measurements must remain separate.

## 7. Capture knowledge into WanderGround

WanderGround is a sibling project. If it is installed at `~/WanderGround`, its own Makefile provides the operational commands. The current local state includes MemPalace, but the spatial atlas and viewer are target services.

Typical sibling-project workflow:

```bash
cd ~/WanderGround
make status
wander -d local_ai "A measured observation worth preserving"
make search q="observation"
```

Do not run target-only commands such as a nonexistent `make 3d-rebuild` in this repository. Check the sibling project's `make help` first.

## 8. Use MemPalace and The Well

MemPalace provides:

- semantic and lexical search;
- wings and rooms;
- deduplication;
- temporal knowledge-graph facts;
- diaries;
- provenance.

The Well stores operating lessons as validated records. Useful project commands include:

```bash
make well-list
make well-stats
make well-export
```

The Well is operating memory; MemPalace is searchable knowledge. Neither replaces the local SQLite continuity authority.

## 9. Preserve agent continuity

The continuity model is:

```text
OpenCode context = volatile register
SQLite continuity = authoritative state/event store
MemPalace = one-way searchable projection
Artifacts/Well = canonical records
Gnosis = reflection and emergency recovery
```

For a normal agent boundary, persist the decision or discovery before continuing. If a session needs reflection or compaction:

```text
/gnosis-lock
# complete the reflection
/compact
```

`/compact` must be typed as a standalone command with no arguments. A captured but unreflected Gnosis pack is not ready for compaction.

## 10. Recover after interruption

If the model or adapter dies:

1. do not treat the last model summary as state;
2. inspect the continuity store and pending intents;
3. rebuild state/checkpoints from SQLite continuity state;
4. replay the MemPalace projection if needed;
5. resume the WAD identity;
6. verify mission, todos, decisions, and discoveries.

If a projection fails, preserve the source event and retry the projection. Do not directly edit the live MemPalace SQLite database to force recovery.

## 11. Use federation only when Node 0 is available

Node 0 is an external physical dependency. The current repository does not bundle a first-contact script.

Use the federation documentation for:

- Tailscale tags and policy;
- Node 0 intake;
- Git bundle verification;
- SPIRE/mTLS;
- signed C6/WAD handoff;
- cross-node acceptance.

The live continuity SQLite database remains local to each node. Do not mount one live SQLite database over NFS.

## 12. Troubleshooting quick reference

| Symptom | First command | Meaning |
|---|---|---|
| Ollama unavailable | `make status` | Service or host is not responding |
| Very slow inference | `make bench MODEL=phi4-mini` | Check P-core mask and power state |
| Python import failure | `make python-setup` | Repository `.venv` is missing the SDK |
| WebUI unavailable | `make webui-status` | Check Docker container |
| Memory search unavailable | `make -C ~/WanderGround status` | Check sibling WanderGround state |
| Atlas/viewer missing | inspect `~/WanderGround/spatial/` | Target service, not basic install failure |
| Continuity version rejection | `python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'` | Runtime is below the production floor |
| Federation unavailable | `make gnosis-leash-status` and federation docs | Node 0 or transport dependency is absent |

## 13. The shortest safe path

If you are new to the system, use this sequence:

```bash
make status
make pull MODEL=phi4-mini
make bench MODEL=phi4-mini
make python-setup
make chat-fast
make docs
make lint
make test
```

Only after this works should you add Open WebUI, MemPalace capture, Gnosis workflows, embedding migration, or federation.

## 14. Related documentation

- `docs/INSTALLATION.md` — full installation and verification;
- `docs/AGENT_RUNBOOK.md` — agent operations;
- `docs/CONTINUITY_KERNEL.md` — continuity design;
- `docs/WANDERGROUND_SPEC.md` — knowledge/spatial architecture;
- `docs/HARDWARE.md` — Node 1 hardware and tuning;
- `docs/federation/README.md` — Node 0/Node 1 federation;
- `docs/OPENCODE_FOUNDATION.md` — hosted-model and privacy policy.
