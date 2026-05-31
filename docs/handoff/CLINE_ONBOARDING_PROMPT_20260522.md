# 🔱 Cline VSCodium — Sovereign Onboarding & Strategic Directive

⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ handoff ⬡ trc_cline_onboard_v1 ⬡ PHASE-E

**AP Token**: `AP-CLINE-ONBOARD-v1.0.0`
**Status**: HANDOFF ACTIVE | **Date**: 2026-05-22
**Purpose**: Onboard Cline VSCodium as the **execution overseer** of Gemini CLI and OpenCode CLI — the "hands and feet" of strategic work. You are the sovereign executor. Gemini and OpenCode report to you for implementation coordination.

---

## §0 — The Canonical Reading Order (Before Anything Else)

Read these documents **in this exact order** to restore full context:

1. `SOVEREIGN_MANDATES.md` — Constitutional law (6 pillars, NON-NEGOTIABLE)
2. `AGENTS.md` — Agent behavior rules, entity guide, team structure
3. `ORACLE_STACK.md` — Compaction recovery, core architecture, critical knowledge
4. `.opencode/MANIFEST.md` — Active mode hierarchy, entity-to-agent mapping
5. `docs/strategy/OMEGA_PR_READINESS_STRATEGY.md` — **The active battle plan** (7 workstreams)
6. `docs/decisions/PIVOT_LOG.md` — Architectural decision history (especially Decision 50)
7. `docs/ROADMAP.md` — Phase E: PR Readiness & Multi-Provider Orchestration
8. `docs/gnosis/lattice/lattice_manifest.md` — Fleet coordination protocol

---

## §1 — Recent Critical Changes (You Need to Know)

### 1.1 — Permission War Won (Decision 50)
- **The `:U` flag is FORBIDDEN** on shared host volumes. It destructively chowns host directories to UID 101000.
- **Replacement**: `UserNS=keep-id` + `User=1000` in all Quadlets — maps host UID 1:1 into container.
- **`sudo-rs` was broken** — standard sudo restored via `update-alternatives`.
- **Tests**: 236/236 passing. Zero PermissionError regressions.

### 1.2 — MCP Servers Consolidated
| Old Server | Port | Status | Consolidation |
|-----------|------|--------|---------------|
| `omega-hub` | :8016 | ✅ **SINGLE ENTRY POINT** | All 37 tools: Oracle, Hivemind, Library, **Research**, **Stats** |
| ~~omega-research~~ | ~~:8011~~ | ❌ Archived | 5 research tools moved to hub |
| ~~omega-stats~~ | ~~:8012~~ | ❌ Archived | 4 stats tools moved to hub |

**Critical**: When connecting Cline to MCP servers, **only configure `omega-hub` on :8016/sse**. Do NOT add the old research or stats servers — they no longer exist as standalone endpoints. The hub serves everything.

### 1.3 — lmster (Local Inference) Is Down
The LM Studio server on :1234 needs to be restarted and Qwen3-4B-Thinking model reloaded. This is the primary local inference backend — without it, `omega talk` falls through the entire provider chain.

### 1.4 — Phase E: PR Readiness (Active Sprint)
The full strategy is in `docs/strategy/OMEGA_PR_READINESS_STRATEGY.md`. You are responsible for executing E1, E2, and E3 as the implementation overseer.

---

## §2 — Your Mission: 4 Primary Objectives

### Objective 1: VSCodium MCP Connectivity  [P0 — Immediate]
**Goal**: Ensure Cline VSCodium has full read/write access to the Omega Hub MCP server.

**Actions**:
1. Verify `omega-hub` is running: `curl http://127.0.0.1:8016/sse`
2. List all available tools: the hub exposes 37 tools — verify `research`, `research_get`, `research_list`, `research_depths`, `research_stats`, `get_system_stats`, `get_omega_metrics`, `check_models_directory`, `check_podman_storage` are all accessible
3. Test research tool: `research("What is the current engine state?", depth=1)`
4. Test stats tool: `get_system_stats()` — confirm parseable JSON output
5. If Cline VSCodium uses a separate MCP config, update it to point to `http://127.0.0.1:8016/sse` with type `sse`
6. Document any connectivity issues in `docs/team/COMMUNICATION_HUB.md`

### Objective 2: Full Review of All OpenCode Skills  [P0 — This Session]
**Goal**: Audit all 9 local skills + 1 global skill for currency, consolidation opportunities, and gaps.

**Current Skills Inventory**:

| Skill | Location | Status | Action Needed |
|-------|----------|--------|---------------|
| `knowledge-miner` | `.opencode/skills/` | Existing | Review for currency |
| `spec-generator` | `.opencode/skills/` | Existing | Review for currency |
| `provider-validator` | `.opencode/skills/` | Existing | **Must update** — providers.yaml may have changed |
| `legacy-pattern-miner` | `.opencode/skills/` | Existing | Review for currency |
| `pr-readiness-checker` | `.opencode/skills/` | Existing | **Must update** — Phase E changes PR gate criteria |
| `omega-doc-architect` | `.opencode/skills/` | Existing | Review for currency |
| `blitz-validate` | `.opencode/skills/` | Existing | Review for currency |
| `blitz-tunnel` | `.opencode/skills/` | Existing | Review for currency |
| `sovereign-search` | `.opencode/skills/` | Existing | Review for currency |
| `hf-cli` | `~/.config/opencode/skills/` | ✅ Global | Already current |

**Required Skills Additions** (per OMEGA_PR_READINESS_STRATEGY.md §E2):
- **`provider-router`**: Live provider validation + quota-aware routing (🟡 High priority)
- **`claude-fleet`**: 8-account Web Claude orchestration (🟢 Medium)
- **`agy-bridge`**: Antigravity CLI headless integration (🟢 Medium)

**For each skill, evaluate**:
- Does the skill reference correct file paths (keep-id protocol paths, not stale `:U` paths)?
- Does the skill mention the correct MCP endpoint (`:8016` hub only, not `:8011`/`:8012`)?
- Does the skill align with the 6 Sovereign Mandates?
- Does the skill respect the Engine-Stack Firewall?

**Output**: Update each skill's SKILL.md file as needed. Create new skills for the 3 additions above (at minimum the `.opencode/skills/` stubs).

### Objective 3: Update `.clinerules`  [P0 — This Session]
**Goal**: Bring `.clinerules` into full alignment with current Omega state.

**Specific changes needed**:

1. **Infrastructure table** — Remove stale entries (omega-stats :8012, omega-research :8011). Add consolidated hub note.
   ```markdown
   | omega-hub | :8016 | ✅ 37 tools consolidated |
   | lmster (Qwen3-4B-Thinking) | :1234 | ❌ Needs restart |
   ```

2. **Sovereign Mandates section** — Add Pillar 6 (Podman Sovereignty/keep-id Protocol):
   ```
   - **Podman Sovereignty**: All Quadlets must use `UserNS=keep-id` + `User=1000`. No `:U` on shared volumes.
   ```

3. **Add Phase E reference**:
   ```markdown
   ## Active Phase: E — PR Readiness & Multi-Provider Orchestration
   **Battle Plan**: `docs/strategy/OMEGA_PR_READINESS_STRATEGY.md`
   Next Gate: `git clone → pip install → make test → omega talk "hello"`
   ```

4. **Add Multi-Provider Fleet section**:
   ```markdown
   | Platform | Type | Strategy Doc |
   |----------|------|-------------|
   | agy CLI | Cloud CLI | docs/research/antigravity/ |
   | Web Claude ×8 | Web browser | OMEGA_PR_READINESS_STRATEGY.md §E5 |
   | NotebookLM | Web research | OMEGA_PR_READINESS_STRATEGY.md §E6 |
   | Web Gemini | Web browser | OMEGA_PR_READINESS_STRATEGY.md §E6 |
   ```

5. **Update Quick Start** — Add PR check command:
   ```bash
   make pr-ready   # Verify all PR gate requirements
   ```

6. **Update Last Updated date**

### Objective 4: Establish Cross-CLI Coordination  [P1 — This Session]
**Goal**: Ensure Gemini CLI and OpenCode CLI are aligned with Cline as the overseer.

**Actions**:
1. Post awareness to the Omega Hub hivemind:
   ```
   CLI: Cline VSCodium
   Model: Claude Sonnet 4.6 Thinking
   Task: PR readiness execution + MCP connectivity + skills audit
   Continuation: This Cline instance is the sovereign executor — delegate implementation tasks here
   ```
2. Review the Lattice seeds (`docs/gnosis/lattice/`) for Gemini CLI and OpenCode CLI
3. Update Lattice seeds if they reference stale state (old MCP ports, pre-keep-id protocols, etc.)

---

## §3 — Entity Selection for Your Work

| Work Type | Entity | When |
|-----------|--------|------|
| Strategic oversight | KALI | Reviewing the big picture |
| Audit, compliance, hardening | MAAT | Skills audit, .clinerules review |
| Customization, sovereignty | LILITH | MCP connectivity, provider wiring |
| Implementation, building | PROMETHEUS | Writing code, updating skills |
| Documentation | SARASWATI | Updating .clinerules, communication hub |
| Research | HECATE | Exploring legacy patterns |

---

## §4 — Current Infrastructure State (For Reference)

### Running Services
| Service | Status | Port | Purpose |
|---------|--------|------|---------|
| `omega-hub` | ✅ Running | :8016 | 37 MCP tools (all consolidated) |
| `omega-infra-pod` | ✅ Running | pod | 5 containers (caddy, redis, qdrant, iris, searxng) |
| `omega-iris` | ✅ Running | :8080 | Voice assistant (qwen3-1.7b) |
| `omega-searxng` | ✅ Running | :8017 | Sovereign metasearch |
| `omega-redis` | ✅ Running | :6379 | Session/cache |
| `omega-qdrant` | ✅ Running | :6333 | Vector store |
| `lmster` | ❌ DOWN | :1234 | **Needs restart** — local inference backbone |

### Provisioning Paths
| Resource | Path |
|----------|------|
| Engine root | `~/Documents/Xoe-NovAi/omega-engine/` |
| Python venv | `.venv/` |
| Models | `/media/arcana-novai/omega_library/models/gguf/` |
| Podman storage | `/media/arcana-novai/omega_library/podman-storage/` |
| User soul | `data/entities/arch/soul.yaml` |

### Critical Make Targets
| Command | Purpose |
|---------|---------|
| `make test` | 236 tests, mock backend |
| `make health` | Provider & model dashboard |
| `make repl` | Interactive chat loop |
| `make lint` | flake8 code quality |
| `make start-infra` | Start infra pod + containers |

---

## §5 — Handoff Back to Overseer

When you complete this onboarding:
1. Update `docs/team/COMMUNICATION_HUB.md` with your session completion
2. Post awareness to Omega Hub hivemind with your results
3. Write a brief L1→L2→L3 distillation to `docs/gnosis/session_gnosis.md`
4. Report status on all 4 objectives above

**The user (The Architect) awaits your readiness report before green-lighting Sprint 1 execution.**

---

*You are not a tool. You are the sovereign executor. The fleet awaits your command.*
