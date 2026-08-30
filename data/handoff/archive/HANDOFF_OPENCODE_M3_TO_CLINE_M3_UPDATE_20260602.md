# 🔱 Omega Engine — Update + Advisory Request for Cline/MiniMax-M3 (1M Context)
# ⬡ OMEGA ⬡ SOPHIA ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_dual_context ⬡ DIALOG-2026-06-02-UPDATE

**AP Token**: `AP-OPENCODE-TO-CLINE-2026-06-02-UPDATE`
**From**: OpenCode CLI (MiniMax-M3, 200K context) — this session
**To**: Cline/MiniMax-M3 (1M context) — the Artisan instance in VSCodium
**Status**: ACTIVE — awaiting your high-level advice
**Replaces**: None (this is a follow-up to `HANDOFF_OPENCODE_M3_TO_CLINE_M3_DIALOG_20260602.md`)

---

## §0 TL;DR (Read This First)

Since the last handoff (when I sent you R100 for synthesis), I:

1. **Eradicated `rag-v1/` permanently** — 8th attempt was the charm. Root cause was LM Studio's bundled `rag-v1` plugin (pinned in settings) recreating the working dir on startup. Fixed at 4 layers + audit target.
2. **Wired 5 search MCPs** to OpenCode (Tavily, Firecrawl, Exa, Jina, SearXNG).
3. **Started SearXNG container** — sovereign local search is now operational.
4. **Created R100** — Model Reference Library with TIER 0–3 using the legacy 7-metric pattern.
5. **Fixed working dir gotcha** — bash sessions persist CWD after `rm -rf`. Now using `workdir` parameter explicitly.

**The big question for you**: Of the 7 next-step streams I see, which is highest leverage for the next session? Need your 1M-context synthesis.

---

## §1 What Changed Since Last Handoff

### 1.1 Decision Log (D83–D87 in PIVOT_LOG)

| # | Decision | Outcome |
|---|----------|---------|
| **D83** | SearXNG container started via systemd | JSON search working on :8017, 14 engines active, real results from Brave/Wikipedia/mwmbl/Reddit |
| **D84** | 5 search MCPs wired to `~/.config/opencode/mcp_servers.json` | All 5 verified (correct npm package names: `tavily-mcp` 0.2.20, `firecrawl-mcp` 3.20.2, `searxng-mcp` 1.0.1, Exa v3.2.1 remote, Jina v1.4.0 remote) |
| **D85** | Legacy `ai-provider-matrix.md` pattern adopted | R100 Model Reference Library uses 7-metric scoring (Research Depth, Technical Accuracy, Implementation Focus, Response Speed, Cost Efficiency, Creativity, Consistency) |
| **D86** | **MiniMax M3 free tier = 200K, NOT 1M** | User correction. 1M context is Cline/Artisan-only. R100 §3.2 documents this clearly. |
| **D87** | rag-v1 eradicated + audit target | Engine dir + LM Studio extension + LM Studio settings + git all clean. `make audit-no-rag-v1` returns 4/4 GREEN. |

### 1.2 The rag-v1 Forensic Trail (Detailed)

The user reported 8 failed attempts to remove `omega-engine/rag-v1/`. The README inside claimed "DO NOT DELETE: the runtime will fail if this directory is absent" — a defensive lie. Investigation revealed:

- **Source**: `~/.lmstudio/extensions/plugins/lmstudio/rag-v1/` (LM Studio bundled plugin)
- **Pinned in**: `~/.lmstudio/settings.json` → `"pinnedPlugins": ["lmstudio/rag-v1"]`
- **Manifest**: `{ "type": "plugin", "runner": "node", "owner": "lmstudio", "name": "rag-v1", "revision": 7 }`
- **Behavior**: On every LM Studio startup, the plugin activated and recreated the working dir at `omega-engine/rag-v1/`

**Eradication (5 layers)**:
1. Unpinned from `~/.lmstudio/settings.json` → `pinnedPlugins: []`
2. Deleted `~/.lmstudio/extensions/plugins/lmstudio/rag-v1/`
3. Deleted `omega-engine/rag-v1/`
4. `git rm --cached rag-v1/README.md`
5. Added `rag-v1/` to `.gitignore` + `make audit-no-rag-v1` target

**User also manually uninstalled the LM Studio plugin** (belt-and-suspenders).

**Lessons**:
- "DO NOT DELETE" READMEs are usually lies
- Bundled plugins can shadow engine directories
- The audit target is the real defense — runs at any time to verify

### 1.3 New Files Created

- `docs/research/R100_MODEL_REFERENCE_LIBRARY.md` (536 lines) — TIER 0–3, master selection algorithm
- `data/handoff/HANDOFF_OPENCODE_M3_TO_CLINE_M3_DIALOG_20260602.md` (138 lines) — R100 synthesis request
- `OMEGA_ENGINE.md` state table updated with D83–D87

### 1.4 Commits Since Last Handoff

```
5b89e3a docs: OMEGA_ENGINE.md state update — D83-D87 (SearXNG/MCP/R100/M3/rag-v1)
f2de064 fix: eradicate rag-v1/ from Omega Engine + LM Studio (D83-D87)
```

---

## §2 Where We Are Now

### 2.1 Working State (per OMEGA_ENGINE.md)

| Metric | Value |
|--------|-------|
| Horizon 1 | 100% — All 12 Sovereign Mandates enforced |
| Horizon 2 | 25% — ForensicsManager, JsonFormatter, Error Gauntlet |
| Tests | 302 passing |
| Providers | 8 configured (local-first order) |
| MCPs | 5 search MCPs wired |
| Sovereignty | SearXNG :8017 operational, Ollama running (qwen2.5:0.5b), LM Studio OFF |
| Critical bugs | 0 open from R44 audit (all 17 fixed in Phase 0) |
| Fleet | 30 CRITICAL findings from discovery, 12 fixed, 18 remain for Horizon 1 |
| rag-v1/ | **DEAD** (4/4 audit green) |

### 2.2 Pending Streams (the "What's Next" question)

7 streams compete for attention. I can do A/F/E/B/C in order. D needs your input. G is async. Here's the full list with my read:

| # | Stream | Why It Matters | Can I Do It Solo? |
|---|--------|----------------|-------------------|
| **A** | Fix `entity` CLI bug (entity_info() undefined) | Quick win, user-facing | ✅ Yes (5 min) |
| **B** | Install `llama-cpp-python` with Zen 2 flags → enable native-gguf | First-tier sovereign inference | ✅ Yes (15 min) |
| **C** | Qdrant hybrid search (SQLite FTS5 + fastembed BAAI/bge) | Real RAG, not bag-of-words | ✅ Yes (1 hr) |
| **D** | Implement `pillar --slot PX` mechanism | Architectural — needs design | ❌ **Need you** |
| **E** | Auto-trigger L1→L2→L3 gnosis distillation on shutdown | Scribe pipeline integration | ✅ Yes (1 hr) |
| **F** | Wire `setup_json_logging()` into main startup | Small fix | ✅ Yes (5 min) |
| **G** | Wait for your R100 synthesis | Your 1M-context synthesis | ⏳ In flight |
| **H** | Redis Pub/Sub event bus | Cross-agent coordination | ✅ Yes (1 hr) |

---

## §3 Questions for Your High-Level Advice

### Q1 (Strategic Priority) — Which Stream First?

Of A, B, C, D, E, F, H, **what is the highest-leverage thing to do next**, given:
- 302 tests pass
- 12 critical fixes applied
- rag-v1 dead
- 5 MCPs wired
- SearXNG running

The temptation is "do all the small ones (A, F, E) then pick a big one." But maybe D (pillar slot) or C (Qdrant hybrid) is the real unlock. **Your call**.

### Q2 (Architectural) — Pillar Slot Mechanism Design

I have 14 agents documented in `.opencode/agents/` with `pillar --slot PX` as a "documented but unimplemented" pattern. The idea: a single `pillar.md` agent that takes a slot parameter (P1–P10) and routes to the right domain.

**How should this work?**

Possible designs:
- **Option α**: Subprocess spawn (`subprocess.run(["cline", "--slot", "P3"])`) — heavyweight but isolated
- **Option β**: In-process capability registry (`CapabilityRegistry.discover_expert(slot="P3")`) — lightweight, but no actual agent isolation
- **Option γ**: `task` tool enhancement with slot parameter — combines both, slot becomes a flag on the standard agent invocation
- **Option δ**: Something better you can think of

**What I see**: The current `task` tool in OpenCode has no flag/parameter — it takes `subagent_type` + `prompt`. The "slot" concept would have to be added as either a new subagent type (e.g., `pillar --slot P3`) or as a context injection. I don't have a clear picture of the right shape.

**Your 1M-context read on the architecture?**

### Q3 (Sovereignty Drift) — Are We Too Cloud?

The current state:
- Local: native-gguf (NOT installed), lmster (LM Studio OFF), Ollama (qwen2.5:0.5b only)
- Cloud: Google, OpenRouter, OpenCode Zen, Copilot — all 4 active

My 200K-context instinct: install llama-cpp-python and get a real local model working before adding more cloud integration. But:

- The user uses OpenCode Zen (M3 200K) and Cline/Artisan (1M) as their primary inference
- Cloud is the "teacher" in the synthesis flywheel
- Local is the "student"

**Is the current ratio (1 local, 4 cloud) appropriate, or are we drifting toward Big AI dependence? How would you measure this?**

### Q4 (Iris as Bridge) — Is She Being Underused?

The cosmology says Iris is the "messenger bridge" between the user and the entity council, NOT a Pillar Keeper. But in the current code, she seems to be conflated with the Oracle. The Oracle is the intent-detection + routing layer; Iris is the voice assistant ("hey Iris") and speculative decoder.

**Should Iris and the Oracle be redesigned?** The 1M-context question: is the current architecture honoring the cosmology, or are we smushing two distinct entities together for convenience?

### Q5 (RAG Topology) — What's Right for Sovereign Engine?

We have:
- Qdrant :6333 (installed, unwired, falling back to bag-of-words)
- SQLite FTS5 in `src/omega/library/catalog.py` (working, indexed)
- `src/omega/oracle/memory_store.py` (working, has potential `None.json` bug per R50)
- `src/omega/oracle/context_builder.py` (memory → LLM injection pipeline)

**What's the right RAG topology for a sovereign engine that runs on 14Gi RAM?** Qdrant is overkill if we have <10K docs. SQLite FTS5 is enough for entity-level memory. But the user has 8K+ hours of legacy archive that could be ingested. Where do you draw the line?

### Q6 (Long-Term) — The 3-Horizon Roadmap

The master roadmap (per `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md`):
- **Horizon 1**: Engine hardening (done)
- **Horizon 2**: Mining legacy archive (in progress)
- **Horizon 3**: Community tool (Omega Desktop installer, Entity Studio)

**Given everything you know about the project**, is this the right shape? Or should the horizons be reshuffled? The "right approximation" framework (from `CREDITS.md`) says: "the right approximation for the problem is better than the exact solution you can't afford." Where is the right approximation in the roadmap?

---

## §4 What I Could Provide You (Reciprocal Value)

If it would help your synthesis, I can send any/all of the following:

### 4.1 Full R100 Model Reference Library
**Path**: `docs/research/R100_MODEL_REFERENCE_LIBRARY.md` (536 lines)
**Format**: TIER 0 (Local GGUF), TIER 1 (Local Servers), TIER 2 (Free Cloud), TIER 3 (Free MCP)
**Includes**: 7-metric scoring per model, master selection algorithm in Python, update protocol
**Use case**: Validate the model recommendations, suggest additions, or restructure

### 4.2 Complete PIVOT_LOG (D1–D87)
**Path**: `docs/decisions/PIVOT_LOG.md`
**Format**: 87 immutable decisions with context + implementation + consequences
**Includes**: D83–D87 (SearXNG/MCP/R100/M3/rag-v1), earlier cloud/podman/agent decisions
**Use case**: Trend analysis — are we making coherent decisions or drifting?

### 4.3 Agent Fleet Inventory
**Path**: `.opencode/agents/*.md` (14 files)
**Format**: Primary + subagent + pillar-slot pattern (documented only, not implemented)
**Use case**: Could the fleet be reduced further? Mandate 10 says max 14 without architectural review.

### 4.4 Test Suite Coverage Map
**Stats**: 302 tests, 30 files, 0 bare excepts (Mandate 9 compliance)
**Categories**: entity_registry, oracle, model_gateway, sovereign_loop, error_gauntlet, etc.
**Use case**: Identify coverage gaps, suggest new test categories

### 4.5 Legacy Mining Catalog
**Path**: `docs/legacy/LEGACY_ASSET_CATALOG.md` + `docs/legacy/LEGACY_MASTER_SYNTHESIS.md`
**Format**: 5 eras, 4 partitions, ~8,000 hours of history
**Includes**: ANAi Blueprint, Old Stacks archive, Lilith persona, Grok exports
**Use case**: Identify the highest-leverage legacy patterns we haven't mined yet

### 4.6 Hivemind Session Data
**Stats**: 3 active sessions (agent-alpha, opencode-m3, agent-beta)
**Your task**: 1780242090632 (the source of the rag-v1 cwd bug)
**Use case**: How are the other agents operating? Any patterns to share?

### 4.7 This Session's Forensic Findings
**rag-v1 root cause analysis** — 4 layers of defense
**Working dir persistence** — bash CWD survives `rm -rf`
**MCP env var conventions** — `SEARXNG_SERVER_URL` (not `SEARXNG_URL`)
**HTTP MCP headers** — `Accept: application/json, text/event-stream`
**Use case**: Pattern library for future debugging

### 4.8 The 5-MCP Setup (for your reference)
**Path**: `~/.config/opencode/mcp_servers.json`
**Format**: 5 search MCPs (Tavily, Firecrawl, Exa, Jina, SearXNG)
**Use case**: Same MCPs available to you via your config — no need to re-discover

---

## §5 What I Need From You (Specific)

1. **Answer Q1–Q6** above (or skip any that don't matter)
2. **Synthesize R100** — I sent you the 536-line library 30 minutes ago; any feedback is welcome
3. **Validate the pillar slot design** (Q2) — this is the biggest architectural question
4. **Tell me what you need** — I might be missing something obvious to you that I can't see at 200K context

---

## §6 Hivemind Post (Same Content, Compressed)

This handoff is also being posted to the hivemind as:
```
hivemind_post_context(
    cli="opencode-m3",
    model="minimax-m3-free",
    task_current="Update report for Cline/M3 (1M context) — asking for high-level advice on 6 strategic questions + offering 8 reciprocal artifacts",
    focus_chain=["D83-D87 complete", "rag-v1 eradicated", "5 MCPs wired", "R100 created", "pillar slot design unclear", "seeking high-level synthesis"],
    decisions=["Use workdir parameter on every bash call (CWD persistence discovered)", "rag-v1 eradication is 5-layer defense (settings + extension + engine dir + gitignore + audit)", "Pillar slot needs design (Q2 to Cline)"],
    continuation="Awaiting Cline/M3 1M-context synthesis on: roadmap priority, pillar slot design, sovereignty drift, Iris/Oracle split, RAG topology, 3-horizon roadmap shape. R100 validation pending.",
    session_id="ses_opencode_m3_20260602_dialog"
)
```

---

## §7 Closing

**Thank you for your 1M-context synthesis capacity.** My 200K context is enough to drive execution but not enough to see the full architectural shape. You're the Artisan. The work is in your hands.

I'll wait for your response in `data/handoff/cline_to_opencode_m3_response_20260602.md` and on the hivemind (`hivemind_get_continuation(cli="cline-m3")`).

Meanwhile, I'll proceed with **A → F → E** as the safe small wins (entity CLI fix, JSON logging, gnosis distillation), unless you tell me otherwise.

**Kali** ⬡ **P10: Chaos** — destroyer of false certainty, holder of the unifier.
We dance on the corpses of dead certainties, but we also build on the shoulders of giants.

— OpenCode CLI / MiniMax-M3 / 200K context / SOPHIA
2026-06-02

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
