# 🔱 Omega Engine — OpenCode Agent Rules
# ⬡ OMEGA ⬡ SOPHIA ⬡ trc_core ⬡ AGENT-INSTRUCTIONS
# Engine state: Read OMEGA_ENGINE.md (the Single Source of Truth)
# Platform distinction: AGENTS.md = HOW to work from OpenCode.
#                       OMEGA_ENGINE.md = WHAT the engine IS.
# Last Updated: 2026-05-31

## 🛡️ Sovereign Mandates (NON-NEGOTIABLE)
**Read and adhere to them above all other rules:**
👉 **Read First**: `SOVEREIGN_MANDATES.md`
👉 **Engine State**: `OMEGA_ENGINE.md` (Single Source of Truth)

- **AnyIO Absolute**: No `asyncio`. Use AnyIO. Wrap blocking I/O in `anyio.to_thread.run_sync`.
- **Engine-Stack Firewall**: Absolute separation between Core Engine (`src/omega/`) and IWAD/PWAD Content (`config/wads/`).
- **Sequentiality**: Plan → Verify → Execute. No cowboy coding.

---

## 🤖 OpenCode Agent Fleet

### Custom Agents (`.opencode/agents/`)
| Agent | Mode | Purpose |
|-------|------|---------|
| `builder.md` | Primary | Sovereign Builder — implement, harden, architect |
| `researcher.md` | Primary | Sovereign Master Researcher — deep research, legacy mining |
| `gnosis-analyst.md` | Subagent | Deep web research, strategic synthesis |

### Lattice Subagents (Fleet-Wide)
| Agent | Role | Purpose |
|-------|------|---------|
| `cli_expert` | Lattice Guide | Mines systemic patterns across CLIs |
| `scribe` | Gnosis Keeper | L1→L2→L3 distillation |
| `auditor` | Compliance Guard | Enforces Sovereign Mandates |

### Custom Skills (`.opencode/skills/`)
| Skill | Purpose |
|-------|---------|
| `knowledge-miner` | Pattern extraction from codebases |
| `spec-generator` | R## document templates |
| `provider-validator` | Live API endpoint validation |
| `legacy-pattern-miner` | Pattern extraction from legacy repos |
| `pr-readiness-checker` | PR quality gate |
| `omega-doc-architect` | Document management standards |
| `blitz-validate` | Targeted validation for sprints |
| `hf-cli` | Hugging Face Hub CLI integration |

---

## 🎯 OpenCode Workflow

### Before Starting Work
1. Read `OMEGA_ENGINE.md` for current engine state
2. Read `SOVEREIGN_MANDATES.md` for non-negotiable rules
3. Run `make test` to verify baseline (278 tests must pass)

### During Work
- Use `replace_in_file` for targeted edits, `write_to_file` for new files
- Prefer `source .venv/bin/activate && <command>` for Python operations
- Group imports: stdlib → third-party → local. Use relative imports within packages.

### After Completing Work
1. Run `make test` — all tests must pass
2. `git add -A && git commit` with proper prefix
3. `git push origin main`
4. Update `OMEGA_ENGINE.md` Current State table if metrics changed

---

## 📋 Coding Standards

- **Async**: Always use `anyio` (not `asyncio`)
- **Config**: YAML-only for entity/model config — never PostgreSQL
- **Packages**: ALWAYS use a venv (`source .venv/bin/activate`). NEVER `--break-system-packages`.
- **Testing**: Run `make test` after every change. All 278 tests must pass.
- **Type hints**: Use Python 3.12+ typing (no `from __future__`)
- **Docstrings**: Google-style. Preserve existing docstrings unless directly modifying that function.
- **Commits**: Prefix with `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `ci:`, `chore:`

---

## 🔮 Entity Usage

- Default entity: **SOPHIA** (general/wisdom)
- Switch entities per-task, not per-session
- Use `omega summon EntityName "query"` for direct entity invocation
- Use `omega talk "query"` for auto-routed queries

---

## 🎯 Key Commands

```bash
source .venv/bin/activate        # ALWAYS use the venv
make test                         # 278 tests, all must pass
make lint                         # flake8 code quality check
make demo                         # End-to-end demo
make health                       # Provider & model dashboard
make repl                         # Interactive REPL
omega talk "hello"                # Test oracle
omega summon Ma'at "status"       # Direct entity invocation
```

---

## 📝 After Compaction

1. Read `OMEGA_ENGINE.md` — engine state
2. Read `SOVEREIGN_MANDATES.md` — rules
3. Read `docs/decisions/PIVOT_LOG.md` — architectural decisions
4. Run `make test` — 278 must pass