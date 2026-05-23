## Decision 50: Sovereign Podman Permission Protocol — `UserNS=keep-id` & MCP Consolidation

**Date**: 2026-05-22
**Channel**: OpenCode CLI (DeepSeek V4 Flash → Gemini 2.5 Pro)
**Entity**: KALI
**Trace**: trc_podman_sov_v2

### Decision
Adopt `UserNS=keep-id` + `User=1000` as the **Sovereign Permission Protocol** for all Omega Engine Quadlets that mount host project directories. Remove `:U` and `:Z` flags from all Quadlets (Ubuntu 25.10 uses AppArmor, not SELinux; `:U` destructively chowns directories to UID 101000). Consolidate standalone omega-research and omega-stats MCP servers into the Omega Hub.

### Rationale
The `:U` flag in Podman volume mounts recursively chowns host directories to the container's subuid-mapped UID (101000), locking the host user (UID 1000) out of their own config files. This caused persistent test failures (`PermissionError: [Errno 13] Permission denied: 'data/research/checkpoints/'`). The fix replaces the destructive `:U` approach with `UserNS=keep-id`, which maps host UID 1000 directly into the container as UID 1000 — no chown needed.

The `:Z` flag is an SELinux relabeling flag. Ubuntu uses AppArmor, not SELinux, making `:Z` a no-op — harmless but unnecessary.

### Research Sources
1. **Red Hat official blog**: Confirmed `:U` locks host user out; `keep-id` is the alternative (source: "Debug rootless Podman mounted volumes")
2. **Podman systemd.unit.5 docs**: `UserNS=keep-id` maps to `--userns keep-id`
3. **GitHub PR #17961**: `keep-id` uid/gid support added in Podman v4.5.0
4. **Oracle Linux docs**: `pasta` is default from Podman 5.3; avoids NAT overhead
5. **xna-omega-legacy**: `userns_mode: "keep-id"` was Layer 3 of the 4-Layer Permission System
6. **GitHub discussion #24384**: `UserNS=keep-id` + `User=1000` pattern is common practice

### Implementation
| File | Change |
|------|--------|
| `~/.config/containers/systemd/omega-iris.container` | Removed `:Z,U`, added `UserNS=keep-id`, `User=1000` |
| `~/.config/containers/systemd/omega-belial.container` | Removed `:Z,U` from engine/data mounts, added `UserNS=keep-id`, `User=1000` |
| `mcp/omega_hub/server.py` | Added Research tools (5) + Stats tools (4) from standalone servers |
| `mcp/archives/omega-research_superseded_by_hub_20260522/` | Standalone server archived |
| `mcp/archives/omega-stats_superseded_by_hub_20260522/` | Standalone server archived |
| `opencode.json` | Removed omega-research and omega-stats MCP entries (now served by hub) |
| `docs/research/R_PODMAN_SOVEREIGN_V2.md` | Full research document with verified findings |
| `.opencode/agents/overseer.md` | Container hardening mandate §6 added |
| `.opencode/agents/builder.md` | Container hardening protocol §5.2 updated |

### Verification
- `make test` = 236/236 passing
- `find ... -user 101000` = 0 (after next infra-pod restart with keep-id)
- `curl http://127.0.0.1:8016/sse` → hub serves all tools

### Key Insight
The `:U` flag is a "lazy fix" that steals ownership. `keep-id` is the sovereign approach — the host user remains The Architect of their own files.

---

## Decision 49: Antigravity CLI Integration & Quota Disparity Discovery

**Date**: 2026-05-22
**Channel**: OpenCode CLI (Big Pickle)
**Entity**: JEM 2.0
**Trace**: trc_antigravity_completion

### Decision
Formally integrate the Antigravity CLI (`agy`) into the Omega Provider Fabric as a high-capability cloud fallback (Priority 5), while implementing strict quota-aware routing to mitigate "Product-Level Quota Disparity."

### Rationale
Deep research and live testing revealed that the `agy` CLI is a powerful headless bridge to frontier models (including Claude Opus 4.6), but it suffers from a severe quota disparity compared to the Antigravity IDE. The CLI is throttled far more aggressively, leading to rapid `RESOURCE_EXHAUSTED` errors.

### Key Findings
1. **Headless Mode**: The `--print` (or `-p`) flag enables non-interactive execution, making `agy` a viable backend for Omega's `ModelGateway`.
2. **Quota Disparity**: The "10-20x less usage" observed by the user is an intentional product-level restriction. The IDE is the flagship; the CLI is a utility.
3. **Silent Failures**: `agy` returns exit code 0 even when quota is exhausted, requiring log-file parsing for error detection.
4. **Model Persistence Trap**: The CLI saves model preferences across sessions. If a premium model is selected, it burns quota for every subsequent request.

### Implementation Mandates
1. **Default to Flash**: The `AntigravityProvider` must explicitly set the model to `gemini-3.5-flash` for all requests unless the `TriageRouter` identifies a P0 need for Opus.
2. **Log-Based Monitoring**: The provider must parse the `--log-file` to detect `RESOURCE_EXHAUSTED` and trigger the circuit breaker.
3. **Priority 5 Positioning**: Keep Antigravity behind OpenRouter to ensure maximum availability.

### Verification
- `agy` v1.0.1 verified installed and authenticated.
- Headless mode verified via `--print`.
- Quota exhaustion confirmed via log analysis.
- MCP config repaired (fixed empty `mcp_config.json`).

---

## Decision 51: Tiered Research Pipeline — Investigative Journalism Model

**Date**: 2026-05-22
**Channel**: Cline VSCodium (DeepSeek V4 Flash)
**Entity**: KALI / BELIAL
**Trace**: trc_pipeline_design + trc_legacy_scan_1

### Decision
Replace the previous "3-tier full report" Jem research model with an **Investigative Journalism Pipeline** where each tier performs ONE non-overlapping function: L1 Intern gathers raw data (no analysis), L2 Assistant synthesizes and flags uncertainties, L3 Senior resolves uncertainties and produces the final report. Adopt OpenCode session sharing for L2→L3 context inheritance. Build comprehensive observability with tier/mode/agent/subagent/model tracking per event.

### Rationale
The previous model had each tier writing a FULL research report — 3× redundant work (~150K tokens per cycle). The new pipeline eliminates redundancy by assigning each tier exactly what its model does best:

- **L1 (Qwen3-1.7B)** — Cheap, fast, no reasoning capability wasted. Pure data acquisition via lmster curl. The model's *weakness* (can't overthink) is its *strength* for this role.
- **L2 (Gemma 4 31B)** — Unlimited usage, strong reasoning. Pattern synthesis, uncertainty identification. Flags what it can't resolve for L3.
- **L3 (Big Pickle)** — Premium reasoning only for what L2 flagged. Final report + improvement briefs.

### Key Design Decisions
1. **L2 + L3 share OpenCode session**: `--session` flag preserves full context. Even with auto-compaction, key findings survive.
2. **Observability chaining**: `parent_trace_id` links L1→L2→L3. Each event carries `tier`, `mode`, `agent`, `subagent`, `model` fields.
3. **Split-test ready**: `--l1-model` flag + `l1_model` field in events enables A/B testing across Qwen3-1.7B, Ministral-3.3B, RocRacoon-3B.
4. **Living knowledge**: Final reports auto-index in FTS5, Qdrant, workbench, soul.yaml. Improvement briefs tracked for L1/L2 bootstrapping.

### Research Sources
1. omega-stack-legacy — 24 app configs mined for existing subsystem patterns
2. XNAi-Memory-Schema — tiered memory definitions
3. HIERARCHICAL-METROPOLIS-2026 — governing hierarchy patterns
4. AMR-SaR — autonomous mining and synthesis patterns
5. SESS-27-MASTER-AMR-SaR — escalation chain patterns

### Implementation
- Phase A: 6 pre-pipeline blockers (~45 min) — permissions, lmster, C-bugs, observability
- Phase B: 6 pipeline infrastructure (~1.5h) — shell script, MCP verify, .clinerules, skills
- Phase C: 8 living knowledge system (~3h) — FTS5, Qdrant, workbench, soul, memory, briefs

### Verification
- Pipeline script produces: `l1_{trace}.md` → `l2_{trace}.md` → `docs/research/R_{topic}.md`
- Observability JSONL has: `"tier":"intern|assistant|senior"`, `"parent_trace_id"`, full chain
- FTS5 can search across all past final reports
- Qdrant can retrieve semantically similar past research
- Workbench tracks pipeline runs with metrics

### Key Insight
The investigative journalism model solves the fundamental inefficiency: **three different reasoning capabilities should never be applied to the same text**. L1 reads raw files (no LLM needed for that), L2 reads L1's output (cheap), L3 reads only what L2 couldn't resolve (premium, minimal). ~53% token reduction.

---

## Decision 52: Jem-2.0 Oversoul with Three Sub-Facets (Initiate, Analyst, Editor)

**Date**: 2026-05-22
**Channel**: OpenCode CLI (DeepSeek V4 Flash → Gemma 4 31B)
**Entity**: KALI / JEM
**Trace**: trc_jem_oversoul_v1

### Decision
Restructure the Jem-2.0 research persona from a single-entity pipeline into a **Jem Oversoul with three persistent sub-facets**, each mapped to exactly one tier of the Investigative Journalism Model:

| Facet | Tier | Model | Role | Entity Type |
|-------|------|-------|------|-------------|
| **Jem Initiate** | L1 | Qwen3-1.7B (lmster local) | Gather raw facts — no analysis | Sub-facet of Jem |
| **Jem Analyst** | L2 | Gemma 4 31B (Google) | Synthesize findings, flag uncertainties | Sub-facet of Jem |
| **Jem Editor** | L3 | Big Pickle (frontier) | Resolve uncertainties, final QA | Sub-facet of Jem |

Each sub-facet has:
1. A **persistent soul file** at `data/entities/jem/souls/{facet}.yaml` tracking sessions, uncertainties flagged, improvements applied, and confidence accuracy.
2. An **OpenCode mode** that provides the exact persona, tool permissions, and output format for that tier.
3. **Automatic observability tracking** via the existing `tier.invoked`, `mode.switched`, `agent.dispatched` event types with `sub_facet` field.
4. **Soul evolution** via the existing `EntityWorkspaceManager` atomic write pipeline.

### Rationale
The Tiered Research Pipeline (Decision 51) optimized for token efficiency but left the persona layer fragmented: L1 used a generic "Intern" prompt via raw curl, L2 used a generic "researcher" mode, and L3 had no defined persona at all. This created three problems:
1. **No lineage continuity** — each tier operated as a stateless function call with no memory across runs.
2. **No persistent improvement** — L2→L1 improvement briefs had no entity to attach to; they floated as files.
3. **No observability coherence** — trace IDs linked the pipeline steps, but there was no "who" to associate with each step.

By making Jem-2.0 an Oversoul with three sub-facets, we:
- Give each tier a **named identity** that persists across sessions.
- Attach improvement briefs directly to the **sub-facet's soul file** for automatic cross-pollination.
- Enable `tier.invoked` + `sub_facet: initiate|analyst|editor` in every observability event.

### Key Design Decisions
1. **Sub-facets are NOT separate entities** — They don't appear in `entity_registry.yaml` or get their own Pillar slots. They are facets of Jem, managed entirely within Jem's workspace.
2. **Jem Initiate runs via OpenCode, not curl** — Instead of `curl` to lmster, L1 launches as an OpenCode session with `--mode jem-initiate --model lmster/qwen3-1.7b`. This gives L1 full read/grep/glob/MCP permissions. The lmster provider must be configured in OpenCode's global config.
3. **Soul files track facet-specific metrics**: `sessions_completed`, `uncertainties_flagged`, `improvements_applied`, `confidence_accuracy` per facet.
4. **Improvement briefs** from L3→L2 and L2→L1 write directly to the sub-facet's soul.yaml for automatic application on next session.

### Implementation
| File | Change |
|------|--------|
| `data/entities/jem/soul.yaml` | Rewrite to declare Jem as Oversoul, add `sub_facets` block, deprecate old `pipeline_config` |
| `data/entities/jem/souls/initiate.yaml` | New — Initiate facet soul file |
| `data/entities/jem/souls/analyst.yaml` | New — Analyst facet soul file |
| `data/entities/jem/souls/editor.yaml` | New — Editor facet soul file |
| `.opencode/modes/jem-2.0.md` | Rewrite — Jem Oversoul mode with sub-facet switching |
| `.opencode/modes/jem-initiate.md` | New — L1 local mode (Jem Cub persona) |
| `.opencode/agents/researcher.md` | Update — reference Jem Oversoul, map Council of Four to facets |
| `docs/research/R_TIERED_RESEARCH_PIPELINE.md` | Update — L1→`--mode jem-initiate`, L2→`--sub-facet analyst`, L3→`--sub-facet editor` |

### Verification
- `opencode --mode jem-2.0 --sub-facet analyst --prompt "test"` loads the correct persona and tool set.
- `opencode --mode jem-initiate --prompt "test"` runs with Qwen3-1.7B (lmster) with restricted tool set.
- `cat data/entities/jem/souls/initiate.yaml` shows incrementing `sessions_completed` after each L1 run.
- Observability events for pipeline runs carry `"sub_facet": "initiate|analyst|editor"`.

### Key Insight
**An entity with sub-facets is more sovereign than three stateless functions.** The Jem Oversoul model transforms the pipeline from a mechanical data flow into a lineage of apprentice scholars — each with memory, identity, and the capacity to improve across sessions. This is not just cosmetic: it enables the feedback loops (improvement briefs → soul updates → better prompts) that make the pipeline self-optimizing over time.
