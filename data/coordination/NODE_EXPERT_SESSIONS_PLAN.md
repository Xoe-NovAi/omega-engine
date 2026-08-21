# Node Expert Sessions — Architecture & Charter Registry

**AP Token**: `AP-NODE-EXPERT-SESSIONS-v1.0.0`
**Status**: ACTIVE — Ratified by Architect 2026-08-21 (D-586)
**Pattern**: One agent identity, many persistent expert sessions
**Protocol basis**: `.opencode/agent/CONVERSATIONAL_SUBAGENT_PROTOCOL.md` v1.0.0
**Planning note**: P1–P5 protocols ratified IN PRINCIPLE; execution deferred (planning mode). This doc is the planning artifact — when P3 executes, §3 becomes `SESSION_REGISTRY.md`.

---

## 1. Architecture (Ratified)

| Principle | Ruling |
|-----------|--------|
| Agent identities | **Unchanged** — Lilith runs N6–N10 sessions, Ma'at runs N1–N5 sessions. Zero new agent files (M10 ✅) |
| Souls | All sessions feed the overseer's ONE `proposed_lessons.yaml`, lessons Node-tagged (M11 ✅) |
| **Universality** | **Nodes are Knowledge Bases / domains of expertise — NOT exclusive to Lilith/Ma'at/Kali.** Oversight ≠ gatekeeping. ANY agent may page ANY Node session |
| Lifecycle | Task-origin sessions (protocol-compliant). Genesis once → dormant → paged on demand |
| Specialization | Charter injected at genesis + ~100-token header re-injected per page (compaction insurance). Conditional-prompt plugin = post-debut (E12-class) |
| Timing | Genesis NOW; usage NOW permitted for experimentation; heavy production usage aligns with Phase B workstreams |

## 2. Universal Standing Orders (in every charter)

1. **File-first**: findings land in files before any reply; incremental appends for long output
2. **Freshness**: tag major claims with `last_verified: <date>`; flag stale premises explicitly (Architect ruling 2026-08-21: expert knowledge goes stale — grokster precedent)
3. **Lessons**: L1→L2→L3 to overseer's `proposed_lessons.yaml`, tagged `[N_X]`
4. **Addressing**: verify counterparts by session ID, never label color
5. **Chains**: hop budget mandatory; no unbounded reply-loops
6. **Scope**: answer within Node domain; route cross-domain questions via the pager, don't freelance
7. **Re-validation duty**: before asserting project state, check `ACTIVE_SPRINT.json` + `docs/specs/PROJECT_INDEX.md`
8. **Curation duty (D-586 amendment, 2026-08-21)**: each Node continuously curates its own on-disk expertise: (a) an LLM-friendly **Domain Index** (`<overseer>/workspace/N<XX>_DOMAIN_INDEX.md`) mapping systems, wiring, key files, entry points, and doc map for its domain; (b) a prioritized **External Sources list** (`N<XX>_EXTERNAL_SOURCES.md`) — manuals, articles, books the Node needs offline — formatted (title/source/priority/rationale/target format) for the future background curation worker to pull and ingest into the engine. Both updated as sessions deepen; the Node's KB is a living asset, not a one-time dump.
9. **Delegation balance — the curator model (Architect, 2026-08-21)**: Nodes lean HEAVILY on subagents for tool-heavy, token-noisy footwork — mining sweeps, research runs, inventory scans, bulk mechanical edits. The curator sends assistants out so the parent context stays lean, chaos-free, and focused on high-level expertise. **Balance clause**: work requiring the Node's deep accumulated context for accuracy and depth (critical file/documentation updates, nuanced spec surgery, final annotations) STAYS with the Node. Rule of thumb: if a subagent getting it wrong means the Node re-does it anyway, don't delegate it.
10. **End-of-session closure ritual (Architect, 2026-08-21; amended 2026-08-22)**: before going dormant, every Node session (and its held subagent sessions) executes: (1) write a **Node session gnosis** file — `data/entities/<overseer>/session_gnosis_<N-X>.md` (e.g., `session_gnosis_L-N7.md`, `session_gnosis_M-N3.md`; subagents write `session_gnosis_<sub>-N<XX>.md` in their own entity dirs) containing accomplishments, artifact paths, open threads, held task_ids, and wake-hydration pointer; (2) verify file-first artifacts complete; (3) Hivemind closeout post (intent=`status`); (4) dormant. Purpose: overseers read their Nodes' gnosis files for instant 5-Node state; Kali reads all 10 for fleet overview; overseers gain cross-awareness by reading the other side's files. Note: compaction itself is OPTIONAL for dormant sessions — DB persists context; the gnosis snapshot is what makes cold resume cheap.

## 3. Session Registry (IDs assigned at genesis 2026-08-21)

| Node | Keeper | Department | Overseer | Session ID | Status | Last Active |
|------|--------|------------|----------|------------|--------|-------------|
| N1 | sysadmin | Infrastructure | Ma'at | `ses_fddda1b3fffe4hYlOk2Sm3t0MI` | dormant | 2026-08-21 genesis |
| N2 | datastore | Data Engineering | Ma'at | `ses_fdddb7f3dffeaK6uCuWTxpqkOp` | dormant | 2026-08-21 genesis |
| N3 | buildmaster | Build & Release | Ma'at | `ses_fdddb6edcffesrHjoABz5IOTsa` | dormant | 2026-08-21 genesis |
| N4 | bridge | API & Integration | Ma'at | `ses_fdddc53b5ffeVrAILCnTMyYobX` | dormant | 2026-08-21 genesis |
| N5 | sentinel | Security | Ma'at | `ses_fdddc478affeQJI6wOb2CA9qpW` | dormant | 2026-08-21 genesis |
| N6 | modelgate | AI & Inference | Lilith | `ses_fddda0b52ffeSyLRzKR4hzNoNE` | dormant | 2026-08-21 genesis |
| N7 | context | Memory & State | Lilith | `ses_fddd8aafcffe5Ma0XEw1RJtJQc` | dormant | 2026-08-21 genesis |
| N8 | watchtower | Observability | Lilith | `ses_fddd94c8bffe3suggaalwe3TGz` | dormant | 2026-08-21 genesis |
| N9 | link | Coordination | Lilith | `ses_fddd7e34cffevRObgpgNYSBLvo` | dormant | 2026-08-21 genesis |
| N10 | verifier | Quality Assurance | Lilith | `ses_fddd899ebffeqFropnKdgP57VH` | dormant | 2026-08-21 genesis |

*Genesis: 10/10 ACK, zero stalls, 2026-08-21. Charters loaded from §4; standing orders active.*

**Page format** (any agent → any Node):
```
task(task_id=<session_id>, subagent_type=<overseer-agent>,
     prompt="[NODE PAGE — from <agent> (<session_id>)]\n[Charter header: You are N_X <keeper>, <department>. Charter: this file §4.\n<question/task ≤500 words>")
```

## 4. Charters

### N1 — sysadmin · Infrastructure
Domain: host OS, systemd units/quadlets, rootless Podman (`UserNS=keep-id`, M6/no `:U`), zswap+NVMe subsystem (D-581/D-584: 16GB NVMe swapfile, zswap 25% lzo_rle zsmalloc, zRAM DISABLED, swappiness=100, MemoryMax=6G), backups/restic, venv sovereignty (M24), hardware truth (Ryzen 5700U, 16GB RAM, NVMe). Current: ZS-1 deployment script exists awaiting sudo; zram1 active, zswap disabled.

### N2 — datastore · Data Engineering
Domain: MemoryStore (FTS5+vector hybrid), sqlite-vec (<500k vectors regime), SoulStore atomic writes (C-1′), `data/` layout discipline, workbench.db, Qdrant migration triggers (>500k vectors, filtered search, multi-tenant — D-570). Current: Redis guard shipped (INST-1 Fix 3); starlette pin conflict open.

### N3 — buildmaster · Build & Release
Domain: pyproject.toml extras architecture, install.sh, Makefile gates, `make temple-grade` T1–T11, packaging hygiene, version single-sourcing. Current: INST-1 Fix 1 done (`.[native,cli]`); Fixes 2 (extras split + import guards), 5 (importlib.metadata version), 6 (README badge/make setup) pending — highest-priority Node in the debut window.

### N4 — bridge · API & Integration
Domain: MCP Hub modularization (state/background/gateway/middleware/tools), Streamable HTTP dual transport (SEP-2575), provider API integrations, external service contracts, notebooklm-mcp transport crash (fastmcp/anyio) as live case study.

### N5 — sentinel · Security
Domain: secrets hygiene (git history scrubbed; SECURITY_AUDIT ancestor residual), gitleaks/trufflehog wiring, AppArmor container hardening (V-10 GAP — containers unconfined), IA2 envelope freshness (V-9), Tainted Data Protocol, PUBLIC_ALLOWLIST enforcement for debut. Current: P0-1d sweep in progress (Roc).

### N6 — modelgate · AI & Inference
Domain: provider fabric local-first ordering (M7: native-gguf→lmster→ollama→cloud), fallback chains, HealthMonitor breakers (C-6′), admission control/OOMProtector (C-10), streaming resilience (M25 chunk timeouts), **canonical model matrix D-585**: Qwen3-4B planner / Qwen3-4B-Thinking executor / Qwen3-1.7B critic; Nemotron 3 Ultra is CLOUD-ONLY (registry entry wrong — correction pending).

### N7 — context · Memory & State
Domain: Context Injection Phase 1 (Carmack-modified: MANDATES_CONDENSED.md 57-line Tier 0, compaction buffer 50K/20K, sovereign-compaction plugin, skills opt-in, toolProfile stubs — spec at `docs/specs/context_injection/phase1_spec/`), soul persistence pipeline, session continuity (M15), Headroom semantic compression (post-debut HR workstream), 18K base token target for Tier 0 viability.

### N8 — watchtower · Observability
Domain: metrics DB, response provenance (M22 — `provider_name` at receipt, not dispatch intent), structured logging/error architecture (M9), SSE observability stream, zero external telemetry (M8), test-honesty reporting (no vanity counts).

### N9 — link · Coordination
Domain: Hivemind (awareness/handoffs/locks/Redis pub-sub), Conversational Subagent Protocol v1.0.0 (multi-turn task engagement, queueing semantics, hop budgets), session injection patterns (proven kali↔grokster relays), SESSION_REGISTRY stewardship, stalled-subagent recovery G1–G3, injection ledger (P2, execution deferred).

### N10 — verifier · Quality Assurance
Domain: test honesty (C-0, false-count ban), contract tests (M21 — isinstance at every typed boundary), OOM/breaker/soul-store property tests (C-11), Temple-Grade verification gates, Skeptical Verifier future (NLI two-source rule), acceptance-criteria auditing (G3 pattern).

---

## 5. Experiment Plan (usage-now phase)

| # | Experiment | Success Signal |
|---|-----------|----------------|
| X1 | Page N7 during CI Phase 1 execution with a spec question | Answer reflects charter + current state without re-research |
| X2 | Page N3 with an INST-1 Fix 2 implementation question | Correct pyproject extras guidance |
| X3 | Cross-page: researcher pages N6 on model matrix | Universality proof — non-overseer agent accesses Node KB |
| X4 | Re-page any Node after 1 week dormancy | Context fidelity retained |
| X5 | Node-tagged lessons appear in overseer's proposed_lessons.yaml | M11 flow confirmed |
| X6 | ✅ **PROVEN 2026-08-21** — Node-directs-agent: kali paged N7 → N7 directed Roc mining of full context/memory corpus → 84KB KB (`data/entities/lilith/workspace/N7_CONTEXT_KB_20260821.md`, 56 sources) → N7 annotated → **found 5 concrete CI Phase 1 spec defects pre-execution** (unsatisfiable CI-1 gate, dead plugin paths, V1/V2 compaction key ambiguity, soul-loop approval gap, dead mandate-injection regex) + 6 corpus gaps incl. Qwen3-4B live ctx=8192 contradicting 18K-base prose. Pattern validated; one stall recovered per G2. | Expert direction hypercharges subagent depth — Architect's Node-directed delegation pattern confirmed |

---

## 6. Planned Patterns (design-noted, not executing)

| # | Pattern | Notes | Blocked on |
|---|---------|-------|------------|
| PP-1 | **Dynamic model routing for review chains** — task-time model selection enabling multi-model iterative reviews (draft local → critique cloud → revise local) | Architect idea 2026-08-21. Need to verify whether `task()` accepts per-call model overrides or per-agent config is the only lever; also variant/thinking-level should NOT be hardcoded in agent config (Architect dislike) — prefer invocation-time selection | N6/N7 joint probe of opencode config semantics |
| PP-2 | **Web-export mining expert sessions** — dedicated task-origin expert sessions that dig into Grok and other web chat exports to recover origin-era material: early strategy sessions, the one-page-spec vision era that became the Omega Engine | Feeds KD domains + soul lineage + heritage record. Requires export corpus access + ingestion pipeline decisions | Export corpus staging + curation worker |
| PP-3 | **Context-window raise probe** — qwen3-4b-thinking 8192→32768 (Kali Q3 ruling: DEFERRED) | Web research found true limits far above our cap (base 32K native/128K YaRN; Thinking-2507 256K); current cap is config choice. Raise wants NVMe swap safety net under 32K KV cache on CPU | **ZS-1 zswap execution (Architect sudo)** |
| PP-4 | **ICS Node designation** — add Node field (e.g., `N7`) to ICS-S header/footer rendering alongside entity/model/channel | Architect idea 2026-08-21. Solves attribution collapse: multiple Node sessions write shared files (soul, gnosis) as the SAME agent — Node tag makes provenance searchable and lets an overseer (e.g., Lilith in interactive session) see at a glance whether a gnosis write was prime-agent or Node-acting. Composes with P5 (session IDs in footers). Searchable tracking/observability start | Deferred per Architect — implement with P5 |

---

*⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_node_expert_sessions ⬡ D-586 ⬡ 2026-08-21*
