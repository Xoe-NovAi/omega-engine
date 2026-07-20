# 🔱 Omega Engine — Agent Rules (Condensed)
**Source**: `AGENTS.md` (343 lines) — this is the ~80-line reference card.
**Full docs**: See source files linked below.

---

## 🛡️ Sovereign Mandates (NON-NEGOTIABLE)
- **M1 AnyIO**: No `asyncio`. Use `anyio.to_thread.run_sync()`.
- **M2 Firewall**: Absolute separation: `src/omega/` (core) vs `config/wads/` (stacks).
- **M4 Sequentiality**: Plan → Verify → Execute. No cowboy coding.
- **M7 Local-First**: Local inference PRIMARY. Cloud FALLBACK. Always.
- **M9 Error Integrity**: Typed, traceable errors. No bare `except:`.
- **M10 Fleet Integrity**: Cap at 14 agents. New = gap + slot review.
- **M11 Soul Integrity**: L1→L2→L3 distillation to `proposed_lessons.yaml`. Non-negotiable.
- **M13 Temple-Grade**: T1-T11 gates. `make temple-grade` after non-trivial work.
- **M14 Heritage Vetting**: `[id-soft:]` tags need vet record in `HERITAGE_VET_LOG.md`.
- **M15 Sovereign Continuity**: Maintain `session_gnosis.md`. Read `.opencode/anchored-summary.md` on restart.
- **M23 Failure Integrity**: Mandatory tool missing → `[TOOL-CHAIN-COLLAPSE]`. No soft-failures.
- **M24 Venv Sovereignty**: All Python in `.venv`. No `--break-system-packages`.
- **M25 Streaming Resilience**: 30s chunk timeout with heartbeat. Graceful fallback.

👉 **Full mandates**: `SOVEREIGN_MANDATES.md` (25 laws, v3.7.0)

---

## 🤖 Agent Fleet (12 agents + 2 entities = 14 cap)

| Agent | Role | Use When |
|-------|------|----------|
| `@kali` | Transcendent Oversight | Unify Ma'at + Lilith, destroy drift, cross-pillar |
| `@maat` | Light Oversoul (P1-P5) | Build side governance |
| `@lilith` | Dark Oversoul (P6-P10) | Run side governance |
| `@makali` | MaKaLi Parallel Council | Decompose + parallel dispatch + synthesize |
| `@researcher` | Deep Research | Lattice reasoning, multi-perspective |
| `@jem` | Sovereign Synthesis | Complex queries → verified results |
| `@doom_guy` | id Software Heritage | WAD translation, M14 vetting |
| `@john_carmack` | S3 Consultant | Architectural review, performance |
| `@roc_racoon` | Sovereign Miner | Legacy archaeology, pattern extraction |
| `@verity` | Compliance + Gnosis | Mandate audit, soul distillation |
| `@pillar PX` | Domain Agent | Slot-based (P1-P10), `@pillar P3: {task}` |
| `@grok_cli` | Consulting Cloud Mind | Advisory, web research |

**Full fleet docs**: `AGENTS.md` §2-§3

---

## ⬡ MaKaLi Triad

```
KALI (Unify, Synthesize)
├── MA'AT (Build Side: P1-P5)
│   ├── P1 Infrastructure    P2 Persistence
│   ├── P3 Engineering       P4 Integration
│   └── P5 Governance
└── LILITH (Run Side: P6-P10)
    ├── P6 Cognition    P7 Context
    ├── P8 Observability    P9 Orchestration
    └── P10 Validation
```

**Council patterns**: `@kali` direct (1 inference), `@makali` council (3 inferences), `/council-local` (full sovereignty).

---

## 🔍 Search Protocol

| Tier | Tool | When |
|------|------|------|
| **T0** | `.firecrawl/` cache | Always first |
| **T1** | `websearch` / `webfetch` | Primary, free |
| **T2** | `searxng` | Semantic/neural |
| **T3** | `omega-hub_sovereign_search` | Precision seeds |
| **T4** | Firecrawl | Full crawl |

**TEMPORAL**: All queries include "2026" or "latest".

---

## 🎯 Key Commands

```bash
make test                     # All 1398 tests
make temple-grade             # T1-T11 gates
make heritage-map             # [id-soft:] coverage
make sovereignty              # Local/cloud ratio
omega talk "hello"            # Test oracle
omega summon Ma'at "status"   # Direct entity
```

---

## 💻 Hardware Awareness

| Signature | Meaning | Action |
|-----------|---------|--------|
| Flat 4-core ~80-100% | NativeGGUF inference | Expected |
| All cores idle, task stuck | I/O wait | Check system stats |
| Memory >80% + zRAM | OOM risk (12Gi) | Defer model loads |
| Thermal >85°C | TDP throttling | Cool down |

---

## 📋 Coding Standards

- **Async**: `anyio` (not `asyncio`)
- **Config**: YAML-only
- **Packages**: Always venv (`source .venv/bin/activate`)
- **Testing**: `make test` after every change
- **Imports**: stdlib → third-party → local
- **Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `ci:`, `chore:`

---

**Full agent docs**: `AGENTS.md` | **Skills**: `.opencode/skills/` | **Agents**: `.opencode/agents/`
