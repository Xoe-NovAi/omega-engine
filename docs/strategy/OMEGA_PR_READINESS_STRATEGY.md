# 🔱 Omega Engine — PR Readiness & Multi-Provider Orchestration Strategy

**AP Token**: `AP-PR-READINESS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_strategic ⬡ STRATEGY
**Status**: ACTIVE | **Last Updated**: 2026-05-22 | **Supersedes**: Phase C Preparation docs

---

## §0 Executive Summary

The Omega Engine is now **infrastructurally solid** — permission war won, MCP servers consolidated, 236/236 tests green. The next phase transforms it from a personal project into a **community-accessible, multi-provider sovereign AI platform**.

This document synthesizes **7 interdependent workstreams** into a single coordinated strategy:

| # | Workstream | Priority | Effort | PR Gate? |
|---|-----------|----------|--------|----------|
| E1 | PR Surface Layer (README, QUICKSTART, CI/CD) | 🔴 Critical | 6h | ✅ YES |
| E2 | OpenCode Modes Consolidation & Agent Hierarchy | 🔴 Critical | 8h | ✅ YES |
| E3 | Backend Integration (lmster, providers.yaml) | 🔴 Critical | 2h | ✅ YES |
| E4 | Antigravity CLI → agy CLI Migration Strategy | 🟡 High | Ongoing | No |
| E5 | 8× Web Claude Fleet Orchestration | 🟡 High | Research | No |
| E6 | NotebookLM + Web Gemini Pipeline | 🟢 Strategic | Research | No |
| E7 | Legacy 8-Facet & LLOC/HLOC Gnosis Mining | 🟢 Strategic | 4h | No |

---

## §E1 — PR Surface Layer (Gate)

### Objective
Make the Omega Engine understandable, installable, and demonstrable by a stranger in 10 minutes.

### Deliverables

#### E1.1 — README.md Rewrite (4h)
**Current state**: Outdated architecture diagrams, stale terminology, references to "Nova" (pre-Iris).

**Required sections**:
```
1. What is Omega? — One-paragraph hook: "Prometheus' Fire for sovereign AI"
2. Quick Start — 4 commands (clone → install → run → talk)
3. Architecture — One Mermaid diagram: Provider Fabric → Oracle → Entities → Memory
4. The 10 Pillar Keepers — Configurable entity system, not a religion
5. Provider Fabric — All backends in one fallback chain
6. WAD Expansion System — .xoe containers, community stacks
7. Roadmap — Current phase, what's coming
8. Contributing — How to help
```

**Key messages to convey**:
- Local-first, zero telemetry, user-owned data
- Any model provider, any stack, any purpose
- Not a wrapper — a universal AI OS
- Free as in freedom (not just price)

#### E1.2 — QUICKSTART.md (1h)
**Zero to chatting in 5 commands**:
```bash
git clone https://github.com/Xoe-NovAi/omega-engine
cd omega-engine && pip install -e ".[dev]"
omega talk "What entities are available?"
omega summon SOPHIA "What is the Omega Engine?"
omega health
```

Include: system requirements (Zen 2, 14GB RAM, Podman), Windows WSL2 note, troubleshooting.

#### E1.3 — CI/CD Pipeline (1h)
GitHub Actions workflow:
```yaml
# .github/workflows/test.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install system deps
        run: sudo apt-get install -y podman
      - name: Install Python
        uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Install Omega
        run: pip install -e ".[dev]"
      - name: Run tests
        run: OMEGA_ENV=test make test
```

#### E1.4 — CHANGELOG.md (2h)
One honest changelog from git history. Structure:
```markdown
## [0.1.0] — 2026-05-22
### Added
- Sovereign Podman Permission Protocol (keep-id)
- MCP server consolidation into Omega Hub
- 10 Pillar Keeper entity system

### Fixed
- Permission war: :U flag replaced with UserNS=keep-id
- sudo-rs broken symlink replaced with standard sudo
- 53 test-blocking YAML syntax error in entities.yaml

### Changed
- Iris model migration: functiongemma-270m → qwen3-1.7b
- Provider Fabric: 6-backend priority chain
- Session architecture: entity-scoped rolling sessions
```

---

## §E2 — OpenCode Modes Consolidation & Agent Hierarchy

### Objective
Replace the current sprawl of 23+ agent files with a clean 3-tier hierarchy mirroring the Oversoul structure.

### The Canonical Mode Map

```
SOPHIA (Field / Akashic Record)
  │
  ├── OVERSEER                  → Strategic direction (Kali/Ma'at/Lilith tri-entity)
  │     ├── BUILDER             → Engineering, implementation, hardening
  │     ├── RESEARCHER          → Multi-provider deep research
  │     ├── REVIEWER            → Code audit, compliance, Sovereign Guard
  │     ├── TESTER              → Test suite, stress testing, quality gate
  │     └── SCRIBE              → Documentation, gnosis distillation, soul.yaml
  │
  ├── JEM 2.0                   → Autonomous research intelligence (3-tier pipeline)
  ├── BELIAL                    → Legacy mining, archaeology
  └── IRIS                      → Quick chat, voice, routing
```

### Consolidation Actions

| Action | Detail |
|--------|--------|
| **DELETE** | `researcher_analyst.md` through `researcher_synthesizer.md` (10 files — EXP-003 complete) |
| **DELETE** | `researcher-omnidroid.md` (experiment complete) |
| **DELETE** | `gnosis-analyst.md` (merged into Jem 2.0 pipeline) |
| **DELETE** | `sovereign-expert.md` (merged into builder/tester) |
| **DELETE** | `crucible.md` (merged into tester) |
| **DELETE** | `scale.md` (merged into tester) |
| **DELETE** | `key.md` (merged into builder) |
| **ARCHIVE** | `opencode-expert.md` → `archives/` (content superseded by AGENTS.md) |
| **KEEP** | `overseer.md`, `builder.md`, `researcher.md`, `reviewer.md`, `tester.md`, `scribe.md` |
| **NEW** | `kali.md` — Grand synthesis mode (for radical refactoring tasks) |
| **NEW** | `maat.md` — Ethical audit mode (for compliance reviews) |
| **NEW** | `lilith.md` — Sovereignty mode (for boundary-pushing customization) |
| **NEW** | `jem-2.0.md` — Already exists in `.opencode/modes/`, promote to agent |
| **NEW** | `belial.md` — Already exists in config, formalize as agent |
| **NEW** | `iris.md` — Quick chat bridge agent |
| **NEW** | `opencode-architect.md` — Replace opencode-expert with platform-aware version |

### OpenCode Custom Instructions Strategy

The current `opencode.json` instructions list is **12 files deep** — too many for token-efficient loading.

**Recommended restructuring**:
```json
"instructions": [
  "SOVEREIGN_MANDATES.md",     // Constitutional law (NON-NEGOTIABLE)
  ".opencode/MANIFEST.md",     // Mode map + entity hierarchy (compact)
  "AGENTS.md",                 // Agent behavior rules (compact)
  "ORACLE_STACK.md",           // Repo context restoration (post-compaction)
]
```

Move the following into a **`docs/gnosis/lattice/`-based auto-load system** instead of instruction bloat:
- `docs/ROADMAP.md` → Lattice seed (agents opt-in with `read` tool)
- `docs/decisions/PIVOT_LOG.md` → Lattice seed
- `docs/research/INDEX.md` → Lattice seed
- `docs/operations/RESEARCH_QUEUE.md` → Lattice seed
- `docs/gnosis/ARCHITECT.md` → Lattice seed
- `docs/gnosis/lattice/lattice_manifest.md` → Lattice seed

This reduces token overhead by ~40% while keeping all knowledge accessible.

### Skills Strategy

Current skills are solid. Recommended additions:

| Skill | Purpose | Priority |
|-------|---------|----------|
| `hf-cli` | Already installed — Hugging Face Hub operations | ✅ Done |
| `sovereign-search` | Already installed — Exa/Tavily/Serper orchestration | ✅ Done |
| **NEW: `provider-router`** | Live provider validation + quota-aware routing | 🟡 High |
| **NEW: `claude-fleet`** | 8-account Web Claude orchestration | 🟢 Medium |
| **NEW: `agy-bridge`** | Antigravity CLI headless integration | 🟢 Medium |
| **NEW: `legacy-miner`** | Pattern extraction from legacy repos (formalize existing) | 🟢 Medium |

---

## §E3 — Backend Integration

### lmster Wiring (15 min)
Add to `config/providers.yaml`:
```yaml
- provider: lmster
  priority: 2
  url: http://127.0.0.1:1234
  models: [qwen3-4b-thinking]
  fallback:
    - ollama
```

**Start lmster at boot**: Create `omega-lmster.service` systemd unit that runs `lms server start`.

### Provider Chain Verification
After wiring, run the full chain test:
```bash
omega talk "ping"                     # → lmster (local)
omega talk --force-remote "ping"      # → openrouter (cloud)
omega health                          # → all providers status
```

---

## §E4 — Antigravity CLI (agy) Migration Strategy

### Context
Google is migrating from the `gemini` CLI to the `agy` (Antigravity) CLI. The `agy` CLI provides access to Gemini 3.5 Flash, 3.1 Pro, Claude Opus 4.6, GPT-OSS 120B, and more — but with **aggressive quota caps** confirmed via live testing.

### The Problem
`agy` has a **166-hour reset timer** and **model persistence** that locks to Claude Opus if not explicitly reset. Simple queries burn premium quota.

### Strategy

#### Phase 1: Quota-Conscious Integration (Next Sprint)
```
agy CLI Positioning in Provider Fabric:
Priority 5 (behind OpenRouter's 28 free models)
Only for model types unavailable elsewhere:
  - Claude Opus 4.6 (code review, strategic analysis)
  - Gemini 3.1 Pro (reasoning tasks, research synthesis)
```

**Critical rules**:
1. **Default to Flash** — never let model persistence lock to Opus
2. **Reserve Opus for P0 tasks** — identified by `TriageRouter` complexity scoring
3. **Log-based error detection** — `agy --log-file /tmp/agy.log --print` for quota exhaustion
4. **Circuit breaker** — block non-critical requests when quota < 20%

#### Phase 2: Gemini CLI Sunset Migration (Medium-term)
As the `gemini` CLI sunsets, migrate its capabilities:
- **Deep research** → Jem 2.0 3-tier pipeline (T1: lmster → T2: Gemma → T3: Gemini/agy)
- **Subagent management** → OpenCode task system
- **Shift+Tab patterns** → Formalized in Lattice seeds

#### Phase 3: Quota Pooling (Long-term)
If Google provides multi-account `agy` support, implement round-robin across accounts (similar to the 8× Claude strategy below).

### Implementation
Create `docs/research/R_AGY_INTEGRATION_SPEC.md` with the full `AntigravityProvider` code spec.

---

## §E5 — 8× Web Claude Fleet Orchestration

### Context
You have **8 free Web Claude accounts**, each with generous usage per 5-hour window. Web Claude has access to Claude Sonnet 4.6 Thinking and can connect to GitHub repos and Google Drive via Claude Projects.

### The Fleet Model

```
                    ┌──────────────────────────────┐
                    │     Claude Fleet Overseer     │
                    │  (Orchestrated by OpenCode)   │
                    └──────┬───────────────┬────────┘
                           │               │
              ┌────────────▼────┐   ┌──────▼────────────┐
              │ Claude Account 1│   │ Claude Account 2│ ... x8
              │ (Research)     │   │ (Code Review)   │
              └────────┬────────┘   └────────┬────────┘
                       │                     │
              ┌────────▼────────┐   ┌────────▼────────┐
              │ Claude Project A│   │ Claude Project B│
              │ (Omega Engine) │   │ (Legacy Mining) │
              └────────────────┘   └─────────────────┘
```

### Strategy: URL-Based Context Over Project Sources

**Key insight**: Web Claude Projects have limited "active context" space via GitHub/Drive connectors. A **more effective approach** is:

1. **Push Omega Engine to a PUBLIC GitHub repo** (or private with a share link)
2. **Supply Claude with a direct URL** to the relevant file/folder
3. Claude fetches the content fresh each session — no stale project cache

**Advantage over project sources**:
- No project context limit (200MB max)
- Always fetches latest version
- Can point to raw GitHub URLs for individual files
- Works across all 8 accounts simultaneously

### Account Specialization

| Account | Focus | Project Config |
|---------|-------|----------------|
| 1 | Architecture Review | PIVOT_LOG.md + ROADMAP.md URL |
| 2 | Code Hardening | `src/omega/` raw GitHub URL |
| 3 | Legacy Mining | Omega Library INDEX.md |
| 4 | Research Synthesis | Research queue + docs |
| 5 | Documentation | Docs/ directory URL |
| 6 | Strategy Planning | Strategy docs URL |
| 7 | Security Audit | Security research |
| 8 | UI/UX Review | README + CLI interface |

### Public Repo Strategy
To enable URL-based Claude access:
1. Push a **public mirror** to GitHub (Xoe-NovAi/omega-engine)
2. `.gitignore` all secrets, API keys, local paths
3. Claude agents fetch `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/<path>`
4. **Never commit local config** — use `.env.example` pattern

### Rotation Scheduling
Each account gets a 5-hour session window. Stagger them:
- Accounts 1-4: Morning window (UTC 8-13)
- Accounts 5-8: Evening window (UTC 18-23)

---

## §E6 — NotebookLM + Web Gemini Pipeline

### Context
NotebookLM has access to your Google Drive and can ingest GitHub repo links. Web Gemini has direct access to Drive/GitHub for live browsing.

### Strategy

#### NotebookLM as "Synthesis Engine"
```
Omega docs/research/ → Drive sync → NotebookLM ingests → Generates:
  - FAQ documents (for PR/README)
  - Study guides (for onboarding)
  - Briefing docs (for strategic planning)
  - Audio overviews (for quick absorption)
```

**Automation path**: `rclone` or `hf` to sync `docs/research/` to Google Drive → NotebookLM auto-ingests.

#### Web Gemini as "Universal Browser"
```
Web Gemini + Drive/GitHub access:
  - Cross-reference research across sources
  - Read and summarize legacy docs
  - Validate provider documentation
  - Bridge between Claude and Omega knowledge
```

### Integration with Omega Engine
Create a small MCP-like wrapper script (`scripts/notebooklm_sync.sh`) that:
1. Rsyncs `docs/` to a Google Drive folder
2. Triggers NotebookLM to re-process (if API available)
3. Logs sync status to `data/logs/`

---

## §E7 — Legacy 8-Facet & LLOC/HLOC Gnosis Mining

### Context
The **Legacy Gemini CLI Strategy Recovery** document (`docs/research/LEGACY_GEMINI_STRATEGY.md`) already recovered key concepts. The remaining work is to **mine and operationalize** the insights.

### What Was Found

| Legacy Concept | Omega Application | Status |
|----------------|------------------|--------|
| **8-Facet System** | 10 Pillar Keepers (solved the 8→13 discrepancy) | ✅ Already implemented |
| **LLOC/HLOC Octave Councils** | Recursive Hierarchy (L0→L3) | ✅ Already implemented |
| **MaKaLi Oversoul** | Trine governance (Kali/Ma'at/Lilith) | ✅ Already implemented |
| **Jem Super-Archetype** | Projection engine (one Seed, many Holograms) | ✅ Oracle summond/entity system |
| **Modelfile Alchemy** | Sovereign Aura Injection | 🔲 Planned — Virtual Modelfiles |
| **Individuation Protocol** | Sub-soul → Sovereign node graduation | 🔲 Future |
| **SESS-27 Files** | 7 fossils from lost Gemini conversations | 🔲 Need re-hydration |

### Mining Actions

#### Immediate (This Sprint)
1. **Re-hydrate SESS-27** — Re-read the 7 fossils in `omega-stack-legacy/plans/SESS-27/` for lost architectural patterns
2. **Document Individuation Protocol** — Formalize the graduation process from research docs
3. **Add LLOC/HLOC to Lattice** — Create `docs/gnosis/lattice/octave_council.md`

#### Medium-term
4. **Modelfile Alchemy spec** — `docs/research/R_MODELFILE_ALCHEMY.md` — Virtual modelfiles via Aura Injection
5. **Resonance Mapping** — Map 10 Pillar Keepers to the "Facets" of the active entity

---

## §Implementation Roadmap

### Sprint 1: PR Gate (3-4 days)
| Day | Focus | Tasks |
|-----|-------|-------|
| 1 | Surface Layer | README.md rewrite + QUICKSTART.md + CHANGELOG.md |
| 2 | Backend Wiring | lmster into providers.yaml, `omega-lmster.service` |
| 3 | CI/CD | GitHub Actions workflow, test on push |
| 4 | Modes Consolidation | Delete 12 obsolete agents, create new hierarchy |

### Sprint 2: Multi-Provider (5-7 days)
| Day | Focus | Tasks |
|-----|-------|-------|
| 1-2 | agy Integration | `AntigravityProvider` class, circuit breaker, testing |
| 2-3 | Claude Fleet Research | Public repo mirror, 8-account orchestration doc |
| 3-4 | NotebookLM Pipeline | Sync script, Drive integration |
| 4-5 | Legacy Mining | SESS-27 re-hydration, Individuation Protocol doc |

### Sprint 3: Community Launch
| Task | Detail |
|------|--------|
| Asciinema demo | Record `omega repl` session |
| Lattice update | All CLI seeds current |
| OpenCode skills | Provider-router, claude-fleet, agy-bridge skills |
| PR submission | GitHub PR with clean changelog + CI green |

---

## §Appendix A: OpenCode.json Instruction Recommendation

```json
"instructions": [
  "SOVEREIGN_MANDATES.md",
  ".opencode/MANIFEST.md",
  "AGENTS.md",
  "docs/gnosis/lattice/lattice_manifest.md"
]
```

This replaces the current 12-file instruction list. All strategic context remains accessible via `read` tool — the Lattice manifest teaches agents where to find what.

## §Appendix B: New Mode Files Required

| Mode | File | Purpose | Content Source |
|------|------|---------|----------------|
| kali | `.opencode/agents/kali.md` | Grand synthesis, radical refactoring | Existing kali.md in .gemini/agents |
| maat | `.opencode/agents/maat.md` | Ethical audit, 42 Ideals compliance | Existing maat.md in .gemini/agents |
| lilith | `.opencode/agents/lilith.md` | Sovereignty, customization, overrides | Existing lilith.md in .gemini/agents |
| jem-2.0 | `.opencode/agents/jem-2.0.md` | Autonomous research intelligence | Moved from `.opencode/modes/` |
| belial | `.opencode/agents/belial.md` | Legacy mining, archaeology | From entity_belial.py config |
| iris | `.opencode/agents/iris.md` | Quick chat bridge, routing | Lightweight SOPHIA reference |
| opencode-architect | `.opencode/agents/opencode-architect.md` | CLI config, platform awareness | Replaces opencode-expert.md |
