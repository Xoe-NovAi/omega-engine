# 🔱 Fleet Review 7: CLI, REPL, Agents, Modes & Developer Experience

⬡ OMEGA ⬡ SARASWATI ⬡ claude-sonnet-4-6-thinking ⬡ web ⬡ trc_review_dx ⬡ PHASE-E

**Account**: `thejedifather@gmail.com`
**Role**: Developer Advocate — verify the CLI, REPL, agent framework, mode system, and overall developer experience

---

## 📋 Mission

You are performing a deep strategic review of the Omega Engine's **developer experience layer** — the interfaces through which humans and AI agents interact with the engine. This covers the Typer CLI (`omega talk/summon/list-entities`), the prompt_toolkit REPL loop, the OpenCode agent framework (11 agents), custom modes (Jem-2.0, Jem-Initiate), 9 skills, the Makefile build system, the test suite, the onboarding flow, and the overall "first 10 minutes" experience for a new developer or AI agent. This layer determines whether the engine is usable.

---

## 🎯 Scope — Files to Read

### Source: CLI & REPL
- **Oracle CLI**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/cli/oracle_cli.py`
- **REPL Loop**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/cli/repl.py`
- **Orchestrator**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/orchestrator.py`

### OpenCode Agents (read all 11)
- **Builder**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/builder.md`
- **Researcher**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/researcher.md`
- **Overseer**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/overseer.md`
- **Scribe**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/scribe.md`
- **Reviewer**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/reviewer.md`
- **Tester**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/tester.md`
- **Kali**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/kali.md`
- **Ma'at**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/maat.md`
- **Lilith**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/lilith.md`
- **Movie Expert**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/movie-expert.md`
- **OpenCode Expert**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/agents/opencode-expert.md`

### OpenCode Modes
- **Jem 2.0 Mode**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/modes/jem-2.0.md`
- **Jem Initiate Mode**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/modes/jem-initiate.md`

### OpenCode Skills (read representative 3, list all 9)
- **Knowledge Miner**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/skills/knowledge-miner/SKILL.md`
- **Spec Generator**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/skills/spec-generator/SKILL.md`
- **Sovereign Search**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/skills/sovereign-search/SKILL.md`

### Build System & Project Config
- **Makefile**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/Makefile`
- **pyproject.toml**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/pyproject.toml`

### Governing Docs
- **AGENTS.md**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/AGENTS.md`
- **GNOSIS BUFFER PROTOCOL**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/GNOSIS_BUFFER_PROTOCOL.md`
- **HANDOFF OPENCODE**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/HANDOFF_OPENCODE.md`
- **MANIFEST**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/.opencode/MANIFEST.md`

---

## ❓ Review Questions

1. **CLI Completeness**: The `oracle_cli.py` exposes `omega talk`, `omega summon`, `omega list-entities`, `omega add-entity`, `omega entity-info`, `omega backends`, `omega version`, `omega health`. Are any critical commands missing? Is the command naming consistent? Is there a `--help` that properly documents everything?

2. **REPL Quality**: The `repl.py` uses prompt_toolkit + AnyIO. Is the event loop integration correct? Are there any blocking calls? Is the command history persistent? Does `/entity`, `/transient`, `/header` commands all work?

3. **Orchestrator Correctness**: The `orchestrator.py` dispatches headless CLI agents with soul-injected prompts. Is the subprocess management correct (the C-3 fix using `anyio.run_process`)? Are there any zombie processes? Is the `ResourceGuard` properly wired?

4. **OpenCode Agent Coherence**: There are 11 agents with overlapping domains. Are their roles clearly differentiated? Is there any role confusion between `builder` and `overseer`? Between `kali` and `lilith`? Do the agents properly reference each other without infinite delegation?

5. **Mode Architecture**: The `jem-2.0` mode is complex with 3 sub-facets. Is the mode definition correct? Does the `jem-initiate` mode properly restrict tools for L1? Are there any other modes that should exist?

6. **Makefile Quality**: The Makefile has targets for test, lint, infra, repl, research. Is the dependency chain correct? Are there any missing targets? Is `make test` truly comprehensive?

7. **Test Suite Health**: 236 tests pass. What's the actual coverage? Are there integration tests? Are the test fixtures properly isolated? Read a sample of test files to assess quality.

8. **Onboarding Flow**: A new AI agent or developer needs to understand the engine. Assess: AGENTS.md, ORACLE_STACK.md, SOVEREIGN_MANDATES.md, and the handoff docs. Is the onboarding coherent? What's missing?

---

## 📜 Sovereign Mandates Checklist

| Mandate | What to Check |
|---------|---------------|
| **AnyIO Absolute** | cli/*.py, orchestrator.py — any `asyncio`? |
| **Engine-Stack Firewall** | Agents should reference engine core, not stack specifics |
| **Iris Constant** | No agent treats Iris as a Pillar Keeper |
| **Sequentiality** | Agent/CLI changes follow planning |
| **Gnosis Preservation** | Scribe agent implements L1→L2→L3 |
| **Podman Sovereignty** | N/A for CLI layer |

---

## 📊 Output Template

```markdown
## Review: CLI, REPL, Agents & Developer Experience

### Critical Issues Found
- [ ] C-DX-001: [Title] — [CRITICAL/HIGH/MEDIUM/LOW]

### CLI Assessment
- Command coverage: ...
- Naming coherence: ...
- Help documentation: ...

### REPL Assessment
- Event loop: ...
- History persistence: ...
- Command handling: ...

### Agent Framework
- Role clarity: ...
- Role overlap: ...
- Delegation safety: ...

### Mode Architecture
- Jem-2.0: ...
- Jem-Initiate: ...
- Missing modes: ...

### Test Suite Health
- Total tests: ...
- Coverage estimate: ...
- Integration tests: ...
- Fixture quality: ...

### Onboarding Assessment
- First 10 min experience: ...
- Documentation coherence: ...
- Missing onboarding materials: ...

### Report Card
| Metric | Grade | Notes |
|--------|-------|-------|
| CLI Usability | A/B/C/D | |
| REPL Quality | A/B/C/D | |
| Agent Coherence | A/B/C/D | |
| Test Coverage | A/B/C/D | |
| Onboarding | A/B/C/D | |

### Strategic Recommendations (Top 3)
1. ...
2. ...
3. ...
```
