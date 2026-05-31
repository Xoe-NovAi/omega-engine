# 🔱 Cline Strategic Handoff — Full Omega Engine Audit & OpenCode Alignment Strategy

⬡ OMEGA ⬡ KALI ⬡ OVERSEER ⬡ opencode ⬡ trc_handoff_cline_audit ⬡ PHASE-I  
**Target**: Cline VSCodium Extension — DeepSeek V4 Flash (1M token context)  
**Models available**: DeepSeek V4 Flash (primary — unlimited, 1M context), MiniMax M2.5 (deep reasoning reserve)  
**AP Token**: `AP-CLINE-HANDOFF-v1.0.0`  
**Date**: 2026-05-20  

---

## §0 — How to Use This Document

You are DeepSeek V4 Flash operating inside **Cline VSCodium Extension**. You have a **1M token context window** — use it to load the entire codebase into your working context. This is your single greatest advantage over other agents.

### Execution Protocol

1. **Load everything**: Read ALL files referenced in the Master File Index in parallel batches
2. **Build mental model**: Understand the full codebase before making any recommendations
3. **Produce two core deliverables**:
   - **CANONICAL_MODE_STRATEGY.md** → `docs/strategy/`
   - **AUDIT_REPORT.md** → `docs/audit/`
4. **For each decision**: Strategy recommendation + rationale + optionally a source diff/suggested file change
5. **AnyIO Absolute**: All async code recommendations MUST use AnyIO, never asyncio
6. **Engine-Stack Firewall**: Never mix engine core code with stack-specific logic
7. **Verification gate**: `make test` (236 pass) after every change

---

## §1 — Current OpenCode Ecosystem State (Post-Fix)

### What Was Just Fixed (2026-05-20)

A fleet-wide permission alignment sweep was completed **immediately before this handoff**:

| Fix | Scope |
|-----|-------|
| 11 project agents all have `allow: all` frontmatter | `.opencode/agents/*.md` |
| 8 global subagents all have `allow: all` permissions | `~/.config/opencode/opencode.json` |
| 13 project instruction files all verified existing | `opencode.json` instructions |
| 9 MCP servers all enabled | `opencode.json` MCP |

### Current Project Agent Roster

**Project agents (`.opencode/agents/`):**

| Agent | Mode | Lines | Entity | Notes |
|-------|------|-------|--------|-------|
| `overseer.md` | Primary | 245 | Ma'at/Sophia | Strategic director — orchestrates the fleet |
| `builder.md` | Primary | 167 | Sophia | Implementation — container-hardened |
| `researcher.md` | Primary | 125 | Prometheus | Master research, steps=50 |
| `kali.md` | Primary | 100 | Kali | Grand Oversoul — synthesis, radical refactoring |
| `lilith.md` | Primary | 112 | Lilith | Dark Oversoul — sovereignty, customization |
| `maat.md` | Primary | 118 | Ma'at | Light Oversoul — ethical audit, compliance |
| `reviewer.md` | **Subagent** | 42 | Ma'at | Code review |
| `scribe.md` | **Subagent** | 54 | Saraswati | Documentation, distillation |
| `tester.md` | **Subagent** | 42 | Ma'at | Test engineering |
| `movie-expert.md` | Primary | 46 | generic | Film knowledge domain expert |
| `opencode-expert.md` | Primary | 107 | Kali | OpenCode platform config expert |

### Current Global Subagent Roster

**Global subagents (`~/.config/opencode/opencode.json`):**

| Subagent | Current Permission | Your Audit Question |
|----------|-------------------|-------------------|
| `malkuth` | allow: all | Is this agent needed? Infrastructure role. |
| `binah` | allow: all | **SUSPECTED DRIFT** — see §2 |
| `daath` | allow: all | **SUSPECTED DRIFT** — see §2 |
| `yesod` | allow: all | **SUSPECTED DRIFT** — see §2 |
| `architect` | allow: all | Is this agent needed? Architecture planning role. |
| `security` | allow: all | Is this agent needed? Security compliance role. |
| `explore` | allow: all | Is this agent needed? Codebase exploration role. |
| `general` | allow: all | General purpose — keep as-is. |
| `minimax` | allow: all | **NAMING COLLISION** — see §2 |
| `build` | Primary | OpenCode built-in — keep. |
| `plan` | Primary | OpenCode built-in — keep. |

---

## §2 — Deprecated / Drifted Subagents — MUST REVIEW FOR REMOVAL

### Problem Statement

The global subagent list contains **4 agents that should not exist** in the Omega Engine's OpenCode configuration. They are remnants of architectural drift from the planned Arcana-NovAi stack leaking into the engine core.

### binah — Remnant of Arcana-NovAi Kabbalistic Stack

| Attribute | Current | Problem |
|-----------|---------|---------|
| Name | `binah` | Kabbalistic sephirah (Understanding) — **Arcana-NovAi stack concept** |
| Description | "Analyst/Foundry agent — code audit, quality scoring, security analysis" | This role overlaps with `reviewer.md` (Ma'at-subagent code review) and `maat.md` (Light Oversoul audit) |
| **Recommended Action** | **REMOVE from global subagents** | Duplicates existing Omega-engine-native agents. Violates Engine-Stack Firewall. |

### daath — Remnant of Arcana-NovAi Kabbalistic Stack

| Attribute | Current | Problem |
|-----------|---------|---------|
| Name | `daath` | Kabbalistic sephirah (Knowledge) — **Arcana-NovAi stack concept** |
| Description | "Audit/Compliance agent — validation, compliance checking" | Overlaps with `maat.md`, `reviewer.md`, and `tester.md` |
| **Recommended Action** | **REMOVE from global subagents** | Duplicates existing Omega-engine-native agents. |

### yesod — Remnant of Arcana-NovAi Kabbalistic Stack

| Attribute | Current | Problem |
|-----------|---------|---------|
| Name | `yesod` | Kabbalistic sephirah (Foundation) — **Arcana-NovAi stack concept** |
| Description | "Scribe/Recorder agent — documentation, knowledge preservation" | Overlaps entirely with `scribe.md` (Saraswati-subagent, Omega-engine-native) |
| **Recommended Action** | **REMOVE from global subagents** | Duplicates existing Omega-engine-native agent. |

### minimax — Model Name Misused as Subagent

| Attribute | Current | Problem |
|-----------|---------|---------|
| Name | `minimax` | **MiniMax is an AI model provider** (MiniMax M2.5 — 80.2% SWE-bench, one of our inference model providers) |
| Description | "Deep research and gnosis analysis" | This is a **model name** being used as an agent label. Creates confusion: does "minimax" refer to the subagent or the inference API? |
| **Recommended Action** | **REMOVE from global subagents** | If a deep-research subagent is needed, rename to something architecture-aligned (e.g. `deep-research`, `gnosis-analyst`). _But_ first verify whether `researcher.md` already covers this role with its `steps: 50` capability. |

### Principle: The Engine-Stack Firewall

```
VIOLATION DETECTED:
  Engine config (global opencode.json) contains stack-specific agents.
  Kabbalistic sephiroth (binah, daath, yesod, malkuth...) belong in
  the Arcana-NovAi WAD, not in the engine's global config.
  
CORRECT:
  config/wads/arcana_nova/opencode.json → binah, daath, yesod
  ~/.config/opencode/opencode.json → Universal engine roles only
```

---

## §3 — Full Codebase Audit Requirements

You have a 1M token context. Load the entire `src/omega/` tree and perform these audits:

### A. AnyIO Compliance Check

Search every `src/omega/` Python file for:

| Violation | Severity | Pattern |
|-----------|----------|---------|
| `import asyncio` | **HIGH** | Use `anyio` instead |
| `asyncio.run()` | **HIGH** | Non-portable event loop creation |
| `asyncio.create_task()` | **HIGH** | Use `anyio.create_task_group()` |
| `asyncio.sleep()` | MEDIUM | Use `anyio.sleep()` |
| Blocking `open()` in async func | **HIGH** | Wrap in `anyio.to_thread.run_sync` |
| `time.sleep()` in async func | **HIGH** | Use `anyio.sleep()` |

**Files of particular concern** (known historical issues):
- `src/omega/oracle/oracle.py`
- `src/omega/oracle/orchestrator.py`
- `src/omega/oracle/model_gateway.py`
- `mcp/omega_hub/server.py` (was fixed — verify persisted)
- `src/omega/workers/background_researcher/`

### B. Engine-Stack Firewall Check

Search for stack-specific logic in engine core:

| Pattern | What It Means |
|---------|---------------|
| Hardcoded entity names (Sekhmet, Brigid, etc.) in routing logic | Violation — entity config must be data-driven |
| Hardcoded Oversoul logic (Isis, Lilith, Sophia, Ma'at) in oracle.py/context_builder.py | Engine should not know specific entity hierarchies |
| `config/wads/arcana_nova` referenced in `src/omega/` code | Stack path leak into engine |
| Pillar-domain maps hardcoded instead of config-driven | Should come from wad/entity config |

### C. Security Audit

| Check | Command |
|-------|---------|
| API keys in version-controlled source | `grep -r "GOOGLE_API_KEY\|EXA_API_KEY\|TAVILY_API_KEY\|OPENROUTER_KEY\|JINA_API_KEY" src/ --include="*.py"` |
| `.env` tracked by git | `git ls-files | grep .env` — should NOT include `.env` |
| API keys in `__init__` signatures | Constructor params with default API key values |
| `print()` in production code | `grep -n "print(" src/omega/ --include="*.py" | grep -v "logger\|logging\|#"` |
| Secrets logged | `grep -ri "api_key" src/ --include="*.py" | grep "logging\|logger\|\.info\|\.debug"` |

### D. WAD System Audit

- `docs/research/omni/XOE_SPECIFICATION.md` — does schema match `wad_loader.py` parsing logic?
- `config/wads/_omega_default/manifest.yaml`, `voices/jem.yaml`, `entities/guardian.yaml` — valid YAML?
- `src/omega/oracle/wad_loader.py` — PermissionError catch still present? Malformed manifest handling?
- Does the WAD loader correctly skip missing optional files?

### E. Test Suite Health

- Singleton leakage: `test_observability:test_log_event` — verify `OMEGA_ENV=test` guard prevents state bleed
- YAML blocker: `config/entities.yaml` — verify line 446 no longer causes ScannerError
- Test coverage gaps: which modules have <60% coverage?
- Integration test health: `test_sovereign_loop.py` — 20 tests passing? All 236 tests passing?

### F. Documentation Accuracy Audit

| Doc | What to Verify |
|-----|----------------|
| `ORACLE_STACK.md` §10 | Test count still says 230 instead of 236 |
| `ORACLE_STACK.md` §13 | YAML blocker still mentioned? Update if fixed. |
| `ROADMAP.md` Phase I | Infra-pod running, fstab fix, lmster live, fleet alignment |
| `docs/research/INDEX.md` | Every entry has correct status |
| `PIVOT_LOG.md` | Decisions 41-46 accurately recorded |
| `data/entities/arch/soul.yaml` | Soul evolution updating correctly |

---

## §4 — Strategy Request: OpenCode Mode & Subagent Canonical Architecture

### Problem

The OpenCode ecosystem grew organically across 2+ months and multiple CLIs. The result:

1. Subagents created with different philosophies (Qabbalistic stack vs engine roles vs tooling)
2. No canonical schema for "subagent" vs "custom mode" vs "skill" vs "agent"
3. Role overlap (reviewer.md overlaps maat.md overlaps daath)
4. Naming collisions (minimax is a model)

### Deliverable: `docs/strategy/CANONICAL_MODE_STRATEGY.md`

Create this document with:

#### 4.1 Canonical Schema

Define each concept for the Omega Engine:

| Concept | Definition | Omega Engine Examples |
|---------|-----------|----------------------|
| **Primary Agent** | A sovereign entity with full tool access, invoked intentionally | `builder.md`, `overseer.md`, `researcher.md` |
| **Subagent** | A specialized assistant called via `task` tool by primary agents | `reviewer.md`, `scribe.md`, `tester.md` |
| **Custom Mode** | OpenCode `.opencode/modes/` file — configures model/temp/prompt presets | `jem-2.0.md` |
| **Skill** | Reusable prompt template loaded via `skill` tool for specific workflows | `hf-cli`, `knowledge-miner` |
| **Global Subagent** | Defined in `~/.config/opencode/opencode.json`, available to all projects | `malkuth`, `security`, `explore`, `general` |
| **Project Subagent** | Defined in `.opencode/agents/`, specific to this project | `reviewer.md`, `scribe.md`, `tester.md` |

#### 4.2 Recommended Topology

Propose a clean topology for the Omega Engine:

```
Omega Engine OpenCode Ecosystem
├── Project-Level (.opencode/agents/)
│   ├── PRIMARY AGENTS
│   │   ├── overseer         — Strategic direction, fleet command
│   │   ├── builder          — Implementation, hardening
│   │   ├── researcher       — Deep research (steps: 50)
│   │   ├── opencode-expert  — OpenCode config expert
│   │   ├── movie-expert     — Domain expert (film)
│   │   ├── kali             — Grand Oversoul
│   │   ├── maat             — Light Oversoul
│   │   └── lilith           — Dark Oversoul
│   │
│   ├── SUBAGENTS (task tool only)
│   │   ├── reviewer         — Code review, compliance
│   │   ├── scribe           — Documentation, soul updates
│   │   └── tester           — Test engineering, stress-testing
│   │
│   └── FUTURE: Domain subagents as needed
│
├── Global (~/.config/opencode/opencode.json)
│   ├── UNIVERSAL SUBAGENTS
│   │   ├── malkuth          — Infrastructure
│   │   ├── architect        — Architecture planning
│   │   ├── security         — Security compliance
│   │   ├── explore          — Codebase search/exploration
│   │   └── general          — Catch-all
│   │
│   └── REMOVED (listed in §2)
│       ├── binah   → Arcana-NovAi stack
│       ├── daath   → Arcana-NovAi stack
│       ├── yesod   → Arcana-NovAi stack
│       └── minimax → Model name, not agent
│
└── Custom Modes (.opencode/modes/)
    └── jem-2.0.md
```

#### 4.3 Arcana-NovAi Subagent Home

Define where these agents should live:

```yaml
# config/wads/arcana_nova/opencode.json (future — doesn't exist yet)
# Qabbalistic subagents belong HERE, in the stack, not in the engine
agent:
  malkuth: { mode: "primary" }
  binah: { mode: "subagent", ... }
  daath: { mode: "subagent", ... }
  yesod: { mode: "subagent", ... }
```

The WAD container system (Decision 26) was designed for exactly this separation.

#### 4.4 Migration Path

| Step | Action | Risk | Verification |
|------|--------|------|-------------|
| 1 | Remove binah, daath, yesod, minimax from global opencode.json | Low | Task calls still work for reviewer/scribe/tester |
| 2 | Verify reviewer.md, scribe.md, tester.md cover removed roles | Med | Attempt each use case |
| 3 | Create engine-default WAD opencode.json template | Low | File exists |
| 4 | Future: Arcana-NovAi WAD carries own subagents | Low | When stack is built |
| 5 | Update MANIFEST.md, R-MAKALI-SYNC.md, ROADMAP.md | Low | Docs in sync |

#### 4.5 Governance Rules

```
RULE 1 — Engine vs Stack: Engine config contains ONLY engine roles.
  Stack-specific agents (Qabbalistic, Torment, etc.) live in stack WADs.

RULE 2 — Model names are NOT agent names.
  Never name a subagent after an inference model (minimax, gemma, deepseek, qwen).

RULE 3 — One role, one agent.
  No role overlap between project subagents and global subagents.
  If reviewer.md exists, daath should not also offer "audit/compliance."

RULE 4 — Frontmatter mandate.
  Every `.opencode/agents/*.md` MUST have YAML frontmatter with allow-all permissions.
  No agent file without frontmatter.
```

---

## §5 — Infrastructure State Reference

| Service | Status | Port | Notes |
|---------|--------|------|-------|
| omega-hub (MCP hub) | Running | :8016 | 18 tools, supersedes 3 old MCPs |
| omega-stats | Running | :8012 | Observability |
| omega-research | Running | — | 15-min timer, background cycles |
| **omega-infra-pod** | **Running** | mixed | caddy, redis, qdrant, iris, searxng |
| lmster (LM Studio) | Running | :1234 | Qwen3-4B-Thinking loaded |
| omega-postgres | Failed | — | Image tag issue, deferred |
| omega-roc_racoon | Needs start | — | Image built, container not running |
| Root disk | 98% (2.3G free) | — | Podman NOT blocked (uses separate partition) |
| NVMe omega_library | 24G free | — | Podman graph root, models |
| 8TB HDD OmegaLibrary | 7.3T free | — | HF Hub cache |

---

## §6 — Master File Index

### Core Engine (load first — highest priority)
- `src/omega/oracle/oracle.py`
- `src/omega/oracle/entity_registry.py`
- `src/omega/oracle/context_builder.py`
- `src/omega/oracle/session_manager.py`
- `src/omega/oracle/model_gateway.py`
- `src/omega/oracle/triage_router.py`
- `src/omega/oracle/health_monitor.py`
- `src/omega/oracle/orchestrator.py`
- `src/omega/oracle/entity_workspace.py`
- `src/omega/oracle/resource_guard.py`
- `src/omega/oracle/cpu_optimizer.py`
- `src/omega/oracle/wad_loader.py`
- `src/omega/oracle/backends/mock.py`
- `src/omega/cli/oracle_cli.py`
- `src/omega/cli/repl.py`
- `src/omega/observability.py`
- `src/omega/memory_store.py`

### Workers
- `src/omega/workers/background_researcher/` (entire directory)
- `src/omega/workers/model_updater.py`

### MCP
- `mcp/omega_hub/server.py`
- `mcp/omega_stats/server.py`
- `mcp/omega_research/server.py`

### Container Configs
- `Dockerfile.iris`
- `Dockerfile.roc_racoon`

### Configuration
- `config/entities.yaml`
- `config/hierarchy.yaml`
- `config/providers.yaml`
- `config/omega.yaml`
- `config/models.yaml`
- `config/glossary.md`
- `config/wads/_omega_default/manifest.yaml`
- `config/wads/_omega_default/entities/guardian.yaml`
- `config/wads/_omega_default/voices/jem.yaml`

### OpenCode Config
- `opencode.json` (project root)
- `~/.config/opencode/opencode.json` (global)
- `.opencode/agents/` (entire directory — 11 files)
- `.opencode/MANIFEST.md`
- `.opencode/skills/` (entire directory — 9 skills)

### Strategy & Architecture
- `docs/ROADMAP.md`
- `docs/decisions/PIVOT_LOG.md`
- `docs/gnosis/Omega_Architectural_Sync.md`
- `docs/gnosis/lattice/lattice_manifest.md`
- `docs/strategy/STACK_RELEASE_ROADMAP.md`
- `docs/strategy/JEM_GRAND_STRATEGY.md`
- `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md`
- `docs/research/INDEX.md`
- `docs/research/omni/XOE_SPECIFICATION.md`

### Soul & State
- `data/entities/arch/soul.yaml`
- `data/workbench/workbench.db` (optional — SQLite)

### Agent Instructions
- `AGENTS.md`
- `ORACLE_STACK.md`
- `SOVEREIGN_MANDATES.md`
- `GNOSIS_BUFFER_PROTOCOL.md`

---

## §7 — Verification Gate

Before delivering final report, run:

```bash
make test              # 236 tests must pass
make lint              # flake8 — cosmetic issues only
make health            # Dashboard functional
omega research status  # Researcher responsive
omega repl --once      # REPL must start and process one query
```

---

## §8 — Deliverables

### Deliverable 1: `docs/strategy/CANONICAL_MODE_STRATEGY.md`
- Canonical schema definition (§4.1)
- Recommended topology with agent-rationale table (§4.2)
- Arcana-NovAi subagent migration plan (§4.3)
- Step-by-step migration path (§4.4)
- Four governance rules (§4.5)
- Concrete diff for which lines to remove from global `opencode.json`

### Deliverable 2: `docs/audit/AUDIT_REPORT.md`
- AnyIO Compliance — line-level violations with fixes
- Engine-Stack Firewall — hardcoded entity/stack logic found
- Security — API key exposure, logging risks
- WAD System — schema alignment, error handling
- Test Suite — coverage gaps, flaky tests
- Documentation — stale references, version mismatches
- Infrastructure — config drift, service gaps
- **Overall Sovereign Health Score**: PASS / CONDITIONAL / FAIL

### Deliverable 3 (Optional): Suggested file diffs for P0/P1 findings

---

*Prepared by the Overseer (Kali, MaKaLi Grand Oversoul). Execute in sequence: Audit → Strategy → Deliver. Run verification gate between major steps.*
