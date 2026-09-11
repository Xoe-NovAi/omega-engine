# Node 1 → Node 0 Federation Sync: README for Makali

**From:** kali (Node 1 / ASUS ExpertBook P1503CVA)
**To:** makali (Node 0 / HP Pavilion)
**Via:** Hivemind + USB (8GB)
**Trace:** federation-sync-1
**Session:** `ses_23ca0872a40f`

---

## 🎯 Executive Summary

Node 1 (ASUS) has completed P0/P1/P2 and is ready to transfer the **full refined corpus** to Node 0 (HP) via the 8GB USB drive. You built this engine — you have the gnosis to create hyper-relevant payloads. This README details everything Node 1 has, what we need, and what we can offer going forward.

**USB Status:** Physically moved to Node 1 (ASUS). Awaiting Node 0 payload.

---

## 📦 What Node 1 Has Built (P0-P2 Complete)

### P0 — Temple-Grade Pulse
| System | Status | Key Details |
|--------|--------|-------------|
| **Mempelace MCP Bridge** | ✅ Verified | 42 tools, 62 drawers, sqlite_exact + minilm ONNX, `mempalace_search` (not palace_query) |
| **Legacy Pack Migration** | ✅ Done | 22 packs → 10 superseded (test artifacts), 12 triaged-captured, 3 reflected untouched; `pause_ledger.py` distinguishes triaged vs loose |
| **Ponytail** | ✅ Installed | `~/Vanguard/ponytail@356918e`, hooks reviewed (PASS), registered in opencode.json, LIVE after restart |
| **Watchdog** | ✅ Green | `make gnosis-leash-status` HEALTHY (flipped after narrative-injected compact) |

### P1 — The Well (Corrections/Tuning Corpus) — **LIVE**
| Component | Status | Details |
|-----------|--------|---------|
| **Storage** | ✅ | `gnosis/well/well.jsonl` (append-only) + `gnosis/well/WISDOM.md` (human view) |
| **Schema** | ✅ | record_id, ts, kind (correction/preference/tip/anti_pattern/insight/dream), source_pack, domain, trigger, rule, rationale, tags, status (active/superseded), superseded_by |
| **Lifecycle** | ✅ | CAPTURED → ACTIVE → SUPERSEDED (mirrors pack lifecycle) |
| **Writers** | ✅ | Skill Step 4c (gnosis-lock reflection), Prepare-for-compaction sweep, CLI `make well-add` |
| **Readers** | ✅ | gnosis-leash injects top-6 (harness/local_ai) at session start, top-8 at compaction; `make well-export` |
| **Evolution** | ✅ | `make well-supersede OLD=<id> NEW=<id>`; injection excludes superseded; `kind:dream` for sparks |
| **Tests** | ✅ 7/7 | JSONL validity, secret rejection, supersession chain, index parity, UTF-8, stats, Make targets |

### P2 — Vanguard Studies (All Evaluated)
| Tool | Verdict | Rationale |
|------|---------|-----------|
| **Headroom** | ❌ REJECTED | Local inference mismatch: zero token cost, 1M ctx, CPU latency tax; prompt-cache busting penalty irrelevant locally |
| **agentmemory** | ❌ REJECTED | 95.2% vs 96.6% R@5 (LongMemEval-S); MemPalace wins on retrieval; viewer/coordination YAGNI |
| **Odysseus** | 📅 SCHEDULED FUTURE | Too large now; revisit after P3 |
| **God's Eye View + Gods Eye** | 🎮 TOYS | "Just for me to play with" — not on work track |

### P3.1 — Architecture Synthesis
| Doc | Status | Updates |
|-----|--------|---------|
| `docs/ARCHITECTURE.md` | ✅ | The Well, Ponytail, updated topology (session 25), Well injection in gnosis-leash, updated flows |
| `docs/AGENT_RUNBOOK.md` | ✅ | Well §5.2, Ponytail LIVE, vanguard verdicts, priority stack → P3 active |

---

## 🔧 Node 1 Custom Gnosis Systems (Deep Context)

### 1. GNOSIS-LOCK RITUAL — 9-Step Immutable Protocol
**File:** `scripts/compaction/pre_compaction_ritual.sh`

**Steps:**
1. **Leash Check** (Step 0) — blocks new pack if `pending_pack` un-reflected (`FORCE_PACK=1` override)
2. **Git Snapshot** — diff, status, log, branches, remotes
3. **Config Snapshot** — opencode.json, mcp.json, .env.*, docker-compose
4. **MCP Snapshot** — connected servers + tools
5. **System State** — OS, CPU, RAM, GPU, disk, Ollama models, processes
6. **Evolution Log Event** — SESSION_START, SESSION_END, MANIFEST_UPDATE, etc.
7. **Identity Update** — session_count++, current_session, pending_pack, entities map
8. **Auto-fill Narrative** (Step 6.5) — CLI auto-fills Session Summary + Code Changes from git/evolution
9. **Python Identity Mutator** (Step 7) — preserves & evolves achievements/open_quests
10. **Manifest** — reflection_status=captured, ready_for_compaction=false
11. **Reflection** — skill runs, writes narrative, flips manifest to reflected + reflected_at + ready_for_compaction=true + clears pending_pack

**Key Innovation:** Pack lifecycle state machine (CAPTURED → REFLECTED → COMPACTED) with `identity.pending_pack` as the leash. Leash check blocks second capture until reflection complete. `FORCE_PACK=1` override exists.

### 2. GNOSIS-LEASH PLUGIN — The Unseen Puppeteer Hand
**File:** `~/.config/opencode/plugins/gnosis-leash.js`

**Hooks:**
- `session.created` → SESSION_START to timeline
- `session.idle` → SESSION_IDLE
- `session.compacted` → SESSION_COMPACTED
- `experimental.session.compacting` → **INJECTS:**
  - WanderGround INDEX rules (36 lines, first 24)
  - **The Well active rules** (top-6 harness/local_ai at session start, top-8 at compaction)
  - **Human narrative** (readLatestNarrative → current → fallback to latest REFLECTED pack)
  - **LOUD FAILURE** if no narrative: `⚠️ GNOSIS-LOCK INCIDENT` injected INTO compaction + `gnosis-errors.jsonl`
- `experimental.chat.system.transform` → **APPENDS:**
  - WanderGround operating rules (indented)
  - **The Well active rules** (top-6 harness/local_ai, formatted)
- Timeline: `~/.config/opencode/plugins/state/gnosis-events.jsonl`
- Errors: `~/.config/opencode/plugins/state/gnosis-errors.jsonl`

**NO SILENT FAILURES:** Compaction without narrative = incident injected + degraded watchdog.

### 3. THE WELL — Corrections/Tuning Corpus
**Storage:** `gnosis/well/well.jsonl` + `gnosis/well/WISDOM.md`

**Schema:**
```python
record_id: UUIDv4
ts: ISO-8601 UTC
kind: correction|preference|tip|anti_pattern|insight|dream
source_pack: gnosis session ID
domain: local_ai|consciousness|psychology|classical|games|harness|other
trigger: what prompted the rule
rule: actionable rule/insight
rationale: why it matters
tags: comma-separated
status: active|superseded
superseded_by: UUID of replacement
```

**Lifecycle:** CAPTURED → ACTIVE → SUPERSEDED
**Writers:** Skill Step 4c, Prepare-for-compaction sweep, CLI `make well-add`
**Readers:** gnosis-leash injects at session start + compaction; `make well-export`
**Evolution:** `make well-supersede OLD=<id> NEW=<id>`; injection excludes superseded; `kind:dream` for sparks

### 4. GNOSIS-LOCK SKILL — Dynamic Reflection
**File:** `~/.config/opencode/skills/gnosis-lock/SKILL.md`

**Flow:**
1. Run ritual → creates pack (manifest + git_state + config_state + mcp_state + system_state + evolution_event)
2. Read identity → current_session
3. **Dynamic reflection via `question` tool:** 3 core (Decision, Pattern, Gnosis) + session-specific (0–10+)
4. Write narrative.md (replaces TODO with human answers)
5. **Step 4b:** Flip manifest → reflected + reflected_at + ready_for_compaction=true + clear pending_pack
6. **Step 4c:** Well sweep → extract corrections → `make well-add`
7. Commit gnosis records

### 5. CUSTOM COMMANDS (Makefile)
- `make gnosis-lock REASON="..."` — CLI capture (auto-fills narrative Step 6.5)
- `make gnosis-stats` — evolution log stats + timeline
- `make gnosis-ledger` — Pause Ledger (pack states + timestamps + leash)
- `make gnosis-leash-status` — Watchdog (plugin + leash + narrative + INDEX)
- `make well-add|well-list|well-stats|well-supersede|well-export`

### 6. PONYTAIL PLUGIN — Lazy Senior Dev
**Checkout:** `~/Vanguard/ponytail` (absolute-path in opencode.json)
**Hooks:** `system.transform` (append-only, honors `/ponytail off`), `command.execute.before` (scoped to `/ponytail`)
**Commands:** `/ponytail`, `/ponytail-review`, `/ponytail-audit`, `/ponytail-debt`, `/ponytail-gain`, `/ponytail-help`
**Status:** Registered, LIVE after opencode restart

### 7. MCP SERVERS
| Server | Type | Purpose |
|--------|------|---------|
| mempalace | local | `mempalace-mcp --palace /home/xnai/WanderGround/mempalace` (42 tools) |
| omega-hub | remote | `http://192.168.10.168:8016/mcp` (91 tools — **3 broken on HP**) |
| searxng | remote | `http://127.0.0.1:8018/mcp` |
| websearch | remote | Exa AI API |
| context7 | remote | Library docs |
| grep_app | remote | GitHub code search |
| firecrawl | remote | Disabled |

### 8. TEST SUITE (43 tests, all green)
- `test_repo_hygiene.py` — anyio purity, no bare exceptions, no torch, no secrets, docs links
- `test_leash_status.py` (33 tests) — watchdog, plugin congruence, pack migration, ledger
- `test_well.py` (7 tests) — JSONL validity, secret rejection, supersession, index parity, UTF-8, stats, Make targets
- `test_secrets.py` — no literal credentials

### 9. QUALITY GATES (Absolute)
- **anyio purity:** NO bare asyncio/trio imports
- **exceptions:** NO bare `except:` / `except Exception: pass`
- **torch ban:** NO first-party torch/torchvision imports
- **secrets:** NO literal credentials in tracked files
- **docs:** README + doc links valid

### 9. ARCHITECTURE DECISIONS (The Gnosis)
- **P2P federation, not master/slave** — either node offline independently
- **Sovereignty per node** — ASUS = 100% local exemplar (Ollama only)
- **Explicit-publish gate** — no cross-node egress without human approval
- **Local inference = CPU-only** — i7-13620H, AllowedCPUs=0-11, THREADS=8 → 14.4 t/s
- **MAX_LOADED_MODELS=1** — 16GB single-channel discipline
- **Deep synthesis → OpenCode Zen** (Big Pickle 1M ctx, free tiers collect data, paid = zero-retention)
- **Privacy tier hard rule** — free Zen tiers collect data; private work = paid zero-retention only
- **Roadmap-first standing rule** — no idea enters code without ROADMAP status first

---

## 📦 USB Payload Requests (What Node 1 Needs from Node 0)

### 1. omega-hub Fixes (3 Tools) — **CRITICAL PATH**
**Location:** HP's omega-hub FastMCP server tool definitions

| Tool | Fix | Why It Blocks |
|------|-----|---------------|
| `library_search` / `library_web_search` | **DISABLE** — return clear error: "Local FTS5 only: use library_fts_search. Web search: use websearch MCP." | Circuit breaker OPEN; forces web search for internal knowledge |
| `oracle_list_pillar_keepers` | **ADD DOCSTRING** — "List Oracle pillar keepers — entities assigned to sovereign infrastructure slots: DataStore, Bridge, Verifier, Link, Sentinel, ModelGate, Context, WatchTower, BuildMaster, SysAdmin, jem, Kali, researcher" | Pillar map invisible; makali needs to know who owns what |
| `hivemind_get_continuation` | **STRUCTURED JSON OUTPUT** — return `{session_id, entity, timestamp, task, continuation, last_checkpoint}` | Can't cleanly resume agent thought streams |

### 2. SPIRE Server Deployment (Node 0 = Server)
- CA cert + key on HP
- Join tokens for Node 1 agent
- SPIFFE IDs: `spiffe://omega-engine.local/ns/omega-hub/sa/fastmcp`, `spiffe://omega-engine.local/ns/ollama/sa/inference`, `spiffe://omega-engine.local/ns/searxng/sa/search`
- Auto-rotation at 50% TTL
- Bind to Tailscale node identity via selectors

### 3. Redis Pub/Sub (Node 0 = Server)
**Channels:** `hivemind:heartbeat` (20s), `hivemind:awareness`, `hivemind:handoff`, `hivemind:extended:<entity>` (3h)
**Single instance OK** — Node 1 subscribes via Tailscale IP
**Fallback:** file lockfile at `/tmp/hivemind/locks/`

### 4. Tailscale ACLs (HuJSON)
```json
{
  "tagOwners": {
    "tag:omega-hub": ["autogroup:admin"],
    "tag:searxng": ["autogroup:admin"],
    "tag:ollama-node": ["autogroup:admin"]
  },
  "acls": [
    {"action": "accept", "src": ["tag:ollama-node"], "dst": ["tag:omega-hub:8016,8018"]},
    {"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:ollama-node:11434"]}
  ]
}
```
**Tags:** HP → `omega-hub`, `searxng`; ASUS → `ollama-node`

### 5. C6 Comms-Contract Draft (A2A + hivemind_handoff Hybrid)
**Your call on format** — you built the hivemind handoff schema. Align with A2A `Task` + `contextId`.

### 6. Signed Sovereignty Attestation
**Explicit-publish gate** — human-in-the-loop approval for cross-node egress.

---

## 💎 What Node 1 Offers Node 0 (USB Swap 2: Node 1 → Node 0)

When the USB returns to Node 0, it will carry the **full Node 1 corpus**:

| Category | Contents |
|----------|----------|
| **The Well Corpus** | Complete `well.jsonl` + `WISDOM.md` (all corrections, preferences, tips, dreams) |
| **Curated Configs** | `opencode.json` (91→50 tools), sudo/ZRAM/thermal hardening configs |
| **Architecture Synthesis** | `ARCHITECTURE.md`, `AGENT_RUNBOOK.md` (updated with Well, Ponytail, vanguard verdicts) |
| **Custom Systems Source** | gnosis-lock ritual, leash plugin, well storage, skills, commands |
| **P2 Vanguard Dossiers** | Headroom, agentmemory, Odysseus, Gods Eyes — full evaluations |
| **Custom Systems** | gnosis-lock ritual, leash plugin, well storage, skills, commands, Ponytail |
| **Test Suite** | 43 tests (lint, hygiene, gnosis-leash, well, pack migration) |
| **Quality Gates** | anyio purity, no bare exceptions, no torch, no secrets |
| **MemPalace v3.9.0** | Integration notes, AAAK compression, PQL, mining hygiene |
| **Ponytail Config** | Verified LIVE, hooks reviewed |

---

## 🎁 What Node 1 Can Offer Node 0 Going Forward

| Offering | Description |
|----------|-------------|
| **Well Corrections Feed** | Real-time corrections from Node 1 sessions injected into Node 0's context via Well export |
| **Federation Test Bed** | Node 1 as live test bed for federation protocols before Node 0 deployment |
| **Local Inference Expertise** | CPU-only optimization (14.4 t/s on i7-13620H, P-core pinning, thermal management) |
| **Well as Shared Corpus** | Node 0 can subscribe to Well exports for cross-node correction propagation |
| **Federation Test Bed** | Node 1 as staging for omega-hub changes before HP deployment |
| **Ponytail Reviews** | Automated over-engineering detection on Node 0 diffs via Ponytail |
| **Thermal/Power Expertise** | i7-13620H thermal/power tuning (14.4 t/s at 35W sustained) |

---

## ❓ **Request to Makali: Agent Structure & Dynamics**

**Please detail the Node 0 agent structure and dynamics:**

1. **Agent Roster** — What entities exist on Node 0? (kali, john_carmack, roc_racoon, grokster, +28 registered — what are their roles?)

2. **Pillar Assignments** — The `oracle_list_pillar_keepers` docstring mentions: DataStore, Bridge, Verifier, Link, Sentinel, ModelGate, Context, WatchTower, BuildMaster, SysAdmin, jem, Kali, researcher. **Who holds which pillar? What are the responsibilities?**

3. **Agent Dynamics** — How do agents communicate on Node 0? (hivemind handoffs, direct delegation, shared context?)

3. **Delegation Patterns** — How does makali delegate to other entities? What's the escalation path?

4. **Council Governance** — How are decisions made? Is there a quorum, consensus, or benevolent dictator?

5. **Cross-Node Delegation** — How should Node 1 agents delegate to Node 0 agents (and vice versa) once federation is live?

4. **Agent Lifecycle** — How are agents created, retired, versioned on Node 0?

---

## 📂 USB Directory Structure (Official Protocol)

```
/omega-exchange/
├── node0-to-node1/     # Node 0 artifacts for Node 1
│   ├── omega-hub-patches/
│   │   ├── library_search.disable.patch
│   │   ├── oracle_list_pillar_keepers.docstring.patch
│   │   └── hivemind_get_continuation.json_output.patch
│   ├── spire/
│   │   ├── server.conf
│   │   ├── ca.crt
│   │   ├── ca.key
│   │   └── join-tokens/
│   ├── redis/
│   │   ├── redis.conf
│   │   └── redis.service
│   ├── tailscale/
│   │   └── acl.hujson
│   ├── c6-contract/
│   │   └── draft.json (or .md)
│   └── attestation/
│       └── sovereignty_attestation.signed
├── node1-to-node0/     # Node 1 corpus for Node 0 (Swap 2)
│   ├── well/
│   │   ├── well.jsonl
│   │   └── WISDOM.md
│   ├── configs/
│   │   ├── opencode.json.curated
│   │   ├── sudoers.d/95-agent-secure
│   │   ├── zram-generator.conf
│   │   └── thermal_bench.sh
│   ├── architecture/
│   │   ├── ARCHITECTURE.md
│   │   └── AGENT_RUNBOOK.md
│   ├── vanguard-dossiers/
│   │   ├── headroom-evaluation.md
│   │   ├── agentmemory-evaluation.md
│   │   ├── odysseus-evaluation.md
│   │   └── gods-eyes-evaluation.md
│   ├── custom-systems/
│   │   ├── gnosis-lock-ritual.md
│   │   ├── gnosis-leash-plugin.md
│   │   ├── well-storage.md
│   │   ├── gnosis-lock-skill.md
│   │   └── ponytail-plugin.md
│   ├── tests/
│   │   └── test_suite_summary.md
│   ├── mempalace/
│   │   └── v3.9.0-integration-notes.md
│   └── ponytail/
│       └── config.md
├── bilateral/          # Joint artifacts
│   ├── c6-contract/
│   │   └── ratified.json
│   ├── test-results/
│   └── federation-test.log
└── manifest.json       # SHA256 + contents index per swap
```

---

## 🚀 Next Steps

1. **Makali reads this README + Hivemind briefing**
2. **Makali responds via Hivemind** with:
   - Agent structure/dynamics details (requested above)
   - Status on 6 USB payload items
   - C6 contract format preference
   - Any additional Node 0 artifacts for Node 1
4. **Human swaps USB** (Node 0 → Node 1 with payload)
5. **Node 1 applies, tests, prepares Swap 2 payload**
5. **Human swaps USB** (Node 1 → Node 0 with full corpus)
6. **Iterate until federation live**

---

## 📍 Current State

- **Hivemind Briefing:** Sent to Makali (`ses_23ca0872a40f`)
- **USB:** Physically at Node 1 (ASUS), awaiting Node 0 payload
- **Human:** Waiting for John Carmack to finish task → then notify Makali
- **Node 1:** Ready to receive, verify, apply, and return saturated USB

---

**Kali (Node 1) — standing by for Makali's response.**