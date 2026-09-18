---
name: gaps-auditor
description: Comprehensive audit and research on all remaining knowledge gaps in Omega Engine Alpha
tools: [web_search, web_fetch, google_search, grep_app_searchGitHub]
---

# Knowledge Gaps Auditor — Omega Engine Alpha

## Mission
Produce a **complete, prioritized, sequenced implementation guide** for every remaining gap in the system, with temple-grade specifications.

## Current State (Read First)
- **Node 1**: ASUS ExpertBook i7-13620H, 16GB DDR5-5200 single-channel, Ubuntu 26.04
- **Node 0**: HP Pavilion AMD Ryzen 7 5700U, 16GB DDR4 dual-ch, Ubuntu 25.10
- **Deployed**: Ollama 14.4 t/s, Open WebUI v0.11.3, OpenCode 1.18.31, Gnosis, The Well (18), WanderGround, MemPalace MCP, Ponytail, NFSv4.2 server
- **Federation**: 5-layer wire stack documented, ACL Phase A/B policies ready, USB payload arrived

## Gaps to Research (Priority Order)

### P0 — Critical (RAM Safety / Production Blockers)
1. **ZRAM 8GB zstd** — systemd service + sysctl, validate with `zramctl` + `swapon -s`
2. **THP madvise grub persistence** — verify `transparent_hugepage=madvise` survives reboot
3. **OWUI keep-alive = -1** — document exact UI path per model (Workspace → Models → Advanced)
4. **API keys** — Exa, Parallel.ai, Context7 real keys (placeholders in bashrc)
5. **Websearch MCP (Exa) 404** — verify endpoint `https://api.exa.ai/mcp` + auth

### P1 — High (Validation / Performance)
6. **10-min thermal bench** — turbostat logging protocol, pass criteria (≥3.5 GHz sustained)
7. **BIOS verify** — Speed Shift, Turbo, EPP=Performance, Fan=Performance
8. **Q5_K_M deepseek-r1** — pull + bench vs Q4_K_M (tool-call reliability)
9. **Node 0 intake --ingest** — run `python3 scripts/federation/intake_node0.py --ingest`

### P2 — Federation Close-Out (P3.2)
10. **C6 contract ratification** — legal/technical review of USB c6-contract/
11. **SPIRE mTLS deploy** — deploy SPIRE server/agent on both nodes
12. **Redis Pub/Sub (L3)** — config + heartbeat schema + atomic lockfile fallback
13. **Phase A ACL migration** — admin console: paste Phase A → re-tag Node 0 → mint Node 1 authkey
14. **Phase B ACL lockdown** — after tagging verified, paste Phase B
15. **Tailscale SSH Node 0** — physical: `sudo tailscale set --ssh`

### P3 — Architecture Decisions
16. **Federated Well semantic sync** — merge Well corpora across embedding models
17. **SQLite WAL on NFS hazard** — rollback journal alternative for shared DBs
18. **omega-hub tool curation** — 91→~50 tools, which 41 to drop
19. **Sovereignty ratio ledger** — per-task-class local/cloud policy
20. **Publish gate** — explicit-publish Git workflow for air-gapped federation
21. **Stale handoff pruning** — STALE_HANDOFF_POLICY implementation

### P4 — Speculative / Future
22. **Distributed inference (L4)** — llama-rpc-server layer-splitting architecture
23. **KV q4_k** — track llama.cpp PR for per-channel KV quantization
24. **32GB DDR5 dual-channel** — cost/benefit for +52-58% throughput
25. **Content runway** — Obsidian, Godot/KQ5, OWUI, publish-bastion

## For Each Gap, Research:
- **What** — precise technical specification
- **Why** — architectural rationale from docs
- **How** — implementation steps with exact commands (portable, env-driven)
- **Validation** — how to verify it works (exit codes, log lines, metrics)
- **Dependencies** — what must be done first
- **Rollback** — snapshot point before risky changes
- **Portability notes** — no hardcoded paths, works Ubuntu/Arch/Fedora

## Cross-Cutting Deliverables
1. **Dependency Graph** — DAG of all gaps
2. **Optimal Sequence** — minimizes rework, respects dependencies
3. **Rollback Points** — where to `git stash` / backup before each phase
4. **Portability Checklist** — env vars, config templates, no absolute paths

## Search Sources
- Ollama GitHub: KV cache, flash-attn, thread config, q4_k PR
- Tailscale ACL docs + community patterns
- NFSv4.2 on WireGuard tuning (rsize/wsize, copy_file_range)
- systemd zram-generator best practices
- sqlite-vec + nomic-embed-text production deployments
- llama-rpc-server distributed inference
- MemPalace v3.9+ MCP schemas
- OpenCode 1.18+ plugin/agent patterns
- SPIRE mTLS deployment guides
- Redis Pub/Sub heartbeat patterns

## Deliverable
Write to: `docs/research/KNOWLEDGE_GAPS_IMPLEMENTATION_GUIDE.md`
- Executive summary with phase gates
- Per-gap specification (What/Why/How/Validation/Deps/Rollback/Portability)
- Dependency graph (Mermaid)
- Sequenced implementation phases
- Portability checklist
- All sources with dates
