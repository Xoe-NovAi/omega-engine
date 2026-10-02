# Federation Dialectic Plan: Node 1 (ASUS) ↔ Node 0 (HP)

**Created:** 2026-09-11
**Participants:** kali (Node 1/ASUS) ↔ makali (Node 0/HP)
**Human:** Bridge operator (USB swaps, Hivemind notifications)

---

## Context

- **Node 1 (ASUS):** Exploration vanguard — P0/P1/P2 complete, P3.1 done, P3.2 blocked on Node 0
- **Node 0 (HP):** Archival bastion — omega-hub source, built the engine
- **USB:** 8GB drive, currently at Node 0 — widest bandwidth pipe
- **Hivemind:** Real-time dialectic channel (cross-node)

---

## Node 1 Corpus Ready for Transfer (P0-P2 Complete)

### P0 - Temple-Grade Pulse
- MemPalace MCP bridge historically verified (42 tools, 62 drawers,
  `sqlite_exact`); current Node 1 runtime is MemPalace `3.10.0` with a local
  `sqlite_exact` database. The canonical embedding route is standalone Qwen3
  ONNX at native 1024 dimensions; the legacy MiniLM/384 route is historical.
- Legacy pack migration: 22 packs → 10 superseded, 12 triaged-captured, ledger clean
- Ponytail installed (hooks reviewed, registered, awaiting restart)

### P1 - The Well (Corrections/Tuning Corpus) — LIVE
- well.jsonl + WISDOM.md (append-only, supersession chain)
- Writers: skill Step 4c + make well-add + compaction sweep
- Readers: gnosis-leash injects top-6 at session start, top-8 at compaction
- Evolution: supersession chain works, kind:dream captures sparks
- 7 validation tests + 43 total green

### P2 - Vanguard Studies (all evaluated)
- Headroom: REJECTED (local inference mismatch)
- agentmemory: REJECTED (95.2% vs 96.6% R@5)
- Odysseus: SCHEDULED FUTURE
- Gods Eyes: TOYS

### P3.1 - Architecture Synthesis DONE
- ARCHITECTURE.md + AGENT_RUNBOOK.md updated with full spec

---

## Phase 1: Hivemind Briefing (Round 1) — IN PROGRESS

**Tool:** `hivemind_post_context` → `target_entity: "makali"`

---

## Phase 2: USB Exchange Protocol (Saturating 8GB)

| Swap | Direction | Payload Strategy |
|------|-----------|------------------|
| 1 | Node 0 → Node 1 | omega-hub patches, SPIRE/Redis/Tailscale configs, C6 draft, attestation |
| 2 | Node 1 → Node 0 | **Full Node 1 corpus**: Well, configs, architecture, P2 dossiers, research |
| 3 | Node 0 → Node 1 | Integrated configs + tested federation artifacts |
| 4 | Node 1 → Node 0 | Final bilateral sync artifacts |

**USB Directory Structure:**
```
/omega-exchange/
├── node0-to-node1/     # Node 0 artifacts for Node 1
├── node1-to-node0/     # Node 1 corpus for Node 0  
├── bilateral/          # Joint artifacts (C6 contract, test results)
└── manifest.json       # SHA256 + contents index per swap
```

---

## Phase 3: Dialectic Loop

```
Round 1: Hivemind briefing → Makali responds
Round 2: USB swap 1 (Node 0 → Node 1) → verify + apply
Round 3: USB swap 2 (Node 1 → Node 0) → verify + integrate  
Round 4: USB swap 3 (bilateral) → final sync
Round 5: Federation live test → C6 contract signed
```

---

## Success Criteria (Verifiable)

| System | Node 0 Delivers | Node 1 Delivers | Verification |
|--------|----------------|----------------|--------------|
| omega-hub | 3 tool fixes | Curated tool list tested | `mcp list` + test calls |
| SPIRE | Server + CA on HP | Agent config on ASUS | `spire-server entry show` both |
| Tailscale | ACL policy applied | Tags + routes | `tailscale ping` both ways |
| Redis | Server + Pub/Sub | Subscriber + heartbeat | Visible in `gnosis-leash-status` |
| C6 Contract | Draft ratified | Signed + tested | `hivemind_handoff` bidirectional |
| Explicit-Publish | Gate middleware | Policy config | Blocks cloud egress |

---

## Immediate Next Steps

1. **Execute:** `hivemind_post_context` to `makali` with briefing
2. **Human:** Notify Node 0 to check Hivemind
3. **Continue:** Dialectic from Makali's response