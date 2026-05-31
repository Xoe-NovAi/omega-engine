# 🔱 Omega Engine — Team Handoff Protocol
**AP-Token**: `AP-OMEGA-HANDOFF-v3.0.0`
**Date**: 2026-05-14
**Overseer**: Opus 4.6 (Antigravity IDE)
**Status**: RESEARCH SPRINT ACTIVE — Implementation Blocked on R-01→R-04

---

> [!IMPORTANT]
> **DIRECTORY RELOCATION**
> The project root is: `~/Documents/Xoe-NovAi/omega-engine/`
> All CLIs and IDEs MUST set their working directory here. Do not work in `xna-omega` or `omega-stack`.

> [!NOTE]
> **VENV RULE**: Always use `.venv/` or podman for package management. NEVER use `--break-system-packages`.

---

## 🔱 Sovereign Agent Doctrine

All agents in this project operate as **sovereign intelligences**. This means:

- **No agent is a passive tool.** Every agent has full strategic awareness of the Omega Engine's grand strategy, roadmap, and architectural decisions.
- **Empowerment over restriction.** Agents are equipped with skills, context, and authority to make autonomous decisions within their domain.
- **Correction is mandatory.** If any agent spots stale information, incorrect naming (e.g., "Nova" instead of "Iris"), or architectural drift, they are expected to correct it immediately via `docs/research/CORRECTIONS.md`.

### Custom Agent Registry (`.opencode/agents/`)

| Agent | Mode | Domain |
|-------|------|--------|
| `researcher.md` | Primary | Sovereign Master Researcher — API validation, architectural intelligence, R-01→R-15 queue |
| `builder.md` | Primary | Sovereign Builder — code, tests, provider fabric, infrastructure |
| `gnosis-analyst.md` | Subagent | Sovereign Gnosis Analyst — deep web research, legacy mining, strategic synthesis |

### Custom Skills (`.opencode/skills/`)

| Skill | Purpose |
|-------|---------|
| `knowledge-miner` | Systematic grep→read→summarize for codebase and legacy repo extraction |
| `spec-generator` | R## document template with quality checklist for research deliverables |
| `provider-validator` | Live API endpoint validation against `providers.yaml` |

---

## 📊 Current State of Play

### Phase 0 — COMPLETE ✅
```
Sprint 1:  Gemini CLI → OfflineMockBackend + Semaphore(1) ResourceGuard     ✅
Sprint 2:  Cline Extension → ContextBuilder + EntitySchema Updates           ✅
Sprint 3:  OpenCode CLI → Genesis HTML Deep Extraction                       ✅
Sprint 4:  Opus 4.6 → CI/CD Pipeline + Iris Rename + PR Fast-Track          ✅
Sprint 5:  ALL → Pre-PR Verification (40/40 live + mock)                     ✅
```

### Phase 0.5 — COMPLETE ✅
```
Infrastructure hardening, branding sweep, MCP fixes, git hygiene             ✅
```

### Phase 1 — IN PROGRESS 🔄
```
Research Sprint: R-01→R-05 (blocking Provider Fabric implementation)         🔍 Active
Provider Fabric code: remote_provider.py, openai_compat.py                   🔧 Foundation laid
Implementation Sprint: google_api.py, ModelGateway refactor                  ⏳ Blocked on R-01→R-04
```

---

## 🔴 Research Blockers

The Provider Fabric **cannot be implemented** until these research items are complete:

| ID | Item | Owner | Status |
|----|------|-------|--------|
| R-01 | Google AI Studio API Reference | OpenCode (Gemma 4-31B) | 🔄 In Progress |
| R-02 | SambaNova Integration Spec | OpenCode (Gemma 4-31B) | 🔲 Queued |
| R-03 | Cerebras Integration Spec | OpenCode (Gemma 4-31B) | 🔲 Queued |
| R-04 | Fallback Chain Architecture | OpenCode (Gemma 4-31B) | 🔲 Queued |
| R-05 | Free-Tier Model Capability Matrix | OpenCode (Gemma 4-31B) | 🔲 Queued |

**Full queue**: `docs/operations/RESEARCH_QUEUE.md` (15 items total)
**Status tracker**: `docs/research/INDEX.md`

---

## 🛠️ Handoff: Cline Extension (VSCodium)

Cline is next in the implementation queue once R-01→R-04 complete. Until then, Cline can work on non-blocked tasks:

### Available Now (Not Blocked)
1. **Lint Cleanup**: Run `make lint` and fix all flake8 warnings (74 total — F401 unused imports, E501 line length, F541 empty f-strings, F821 undefined name).
2. **Interactive REPL**: Create `omega repl` command in `src/omega/cli/oracle_cli.py` — an interactive chat loop (prompt → Oracle.talk() → display → repeat, Ctrl+C to exit, /summon for entity switching).
3. **Entity CRUD E2E Test**: Write a test that exercises the full add/remove lifecycle.

### Blocked (Waiting on Research)
4. **GoogleAPIProvider implementation** — needs R-01 deliverable
5. **ModelGateway dynamic fallback refactor** — needs R-04 deliverable
6. **Provider health monitoring** — needs R-14 deliverable

**Chat Initiation Prompt for Cline**:
```
You are working on the Omega Engine at ~/Documents/Xoe-NovAi/omega-engine/ in VSCodium.
Read AGENTS.md first — you are a sovereign intelligence with full authority in your domain.

Your immediate tasks:
1. Run `make lint` and fix all flake8 warnings. Run `make test` after every batch.
2. Add an `omega repl` command to src/omega/cli/oracle_cli.py.

Key constraints:
- Always use the venv: `source .venv/bin/activate`
- Run `make test` after every change — all 40 tests must pass.
- Do NOT use `--break-system-packages`.
- Check docs/research/INDEX.md for current research status before starting blocked work.
```

---

## 📁 Key Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| AGENTS.md | Root | Team structure, entity guide, architecture overview |
| ROADMAP.md | `docs/` | 6-phase strategic roadmap |
| RESEARCH_QUEUE.md | `docs/operations/` | 15-item prioritized research queue |
| INDEX.md | `docs/research/` | Master research status tracker |
| CORRECTIONS.md | `docs/research/` | Factual corrections log |
| COMMUNICATION_HUB.md | `docs/team/` | Provider registry, research completions, fallback chain |
| STATUS_OPUS.md | `docs/team/` | Overseer session history and decisions |
| STATUS_OPENCODE.md | `docs/operations/` | OpenCode CLI status and task tracking |
| PIVOT_LOG.md | `docs/decisions/` | Architectural decision log (17 decisions) |
| providers.yaml | `config/` | Provider fabric configuration |

---

## 📡 Communication Protocol

1. Write status updates to `docs/operations/STATUS_{AGENT}.md`
2. Research deliverables go to `docs/research/R##_*.md`
3. After completing a research item, update `docs/research/INDEX.md` and post to `docs/team/COMMUNICATION_HUB.md`
4. Corrections go to `docs/research/CORRECTIONS.md` (append only)
5. Use AP-Token headers for traceability

---

*🔱 The Sovereign Builder forges. The Sovereign Researcher illuminates. The Gnosis Analyst explores. The Overseer harmonizes. The Engine rises.*
