# Cline-M3 Model Strategy Lab
## DeepSeek V4 Flash vs V4 Pro — Omega Engine Allocation Plan

**Date**: 2026-06-09
**Current Budget**: $0.4353 (Cline free signup credit)
**Models Available**: DeepSeek V4 Flash (free), DeepSeek V4 Pro ($), plus 2 other free-tier models (MiniMax M3, MiMo V2.5)

---

## §1 Model Specs (from OpenRouter + DeepSeek API Docs)

### DeepSeek V4 Flash (FREE via Cline)
| Attribute | Value |
|-----------|-------|
| Architecture | MoE, 284B total / 13B active params |
| Context | **1,048,576 tokens** (1M) |
| Pricing | $0.0983/M in / $0.1966/M out — **$0 via Cline free tier** |
| Speed | Fast inference; high-throughput optimized |
| Reasoning | Supports `high` and `xhigh` efforts |
| Best for | Coding assistants, chat, fast agent loops, routine dev work |

### DeepSeek V4 Pro (Paid, $0.435/M in / $0.87/M out)
| Attribute | Value |
|-----------|-------|
| Architecture | MoE, 1.6T total / 49B active params |
| Context | **1,048,576 tokens** (1M) |
| Pricing | $0.435/M in / $0.87/M out — **~4.4x Flash** |
| Speed | Slower but more thorough reasoning |
| Reasoning | Supports `high` and `xhigh` efforts |
| Best for | Full-codebase analysis, architecture, complex synthesis |

---

## §2 Strategic Allocation for Omega Engine

### ✅ DeepSeek V4 Flash — Daily Driver (Unlimited Free)

Use Flash for **all routine work**. It is always available at zero cost and still has 1M context.

| Task Category | Examples | Why Flash |
|:---|:---|---|
| **Test Fixing** | `make test` — fix regressions, update baselines | Fast iteration, no cost |
| **Routine Code** | Model adapters, entity YAML files, config changes | High volume, low complexity |
| **Quick Reviews** | PR review, code audit, lint fixes | Responsiveness matters |
| **Documentation** | `.md` updates, soul.yaml edits, handoff notes | Cheap, no need for Pro |
| **CI/CD** | Makefile targets, workflow tweaks | Short context, repetitive |
| **Solo Debugging** | Single-file bug hunts, trace_id analysis | Fast feedback loop |
| **Hivemind Comms** | Post context, update feed, coordinate | Tiny context, no complexity |

### 💎 DeepSeek V4 Pro — Strategic Reserve ($0.4353 budget)

Use Pro **only when Flash cannot do the job**. Budget is enough for ~1M input tokens or ~500K output.

| Priority | Task | Est. Cost | Why Pro |
|:--------:|:-----|:---------:|:--------|
| **P0** | **D113 Firewall Restoration** (entity_registry.py -> WAD-agnostic) | ~$0.02-0.05 | Cross-cutting, 3 files, architectural |
| **P0** | **S1.5b Nomenclature Migration** (pillar_slot wiring) | ~$0.02-0.05 | 10 pillar agents, cascading changes |
| **P1** | **H2-A7: Delete 100 orphans** analysis strategy scan | ~$0.01 | Large entity directory audit |
| **P1** | **H2-A8: arcana_novai IWAD population** plan | ~$0.02 | IWAD structure, entity design |
| **P2** | **Synthesis Flywheel** (S2) — pipeline architecture | ~$0.05 | Multi-system orchestration design |
| **P3** | **Sovereignty Scorecard** auto-generation | ~$0.03 | Cross-module metrics collection |
| **Reserve** | Unexpected complex bug | ~$0.10 | Safety net for hard problems |
| **Reserve** | Emergency rollback analysis | ~$0.02 | Post-mortem deep dives |

### Budget Tracking
```
Initial:      $0.5000
Used:         $0.0647 (auth, test calls)
Remaining:    $0.4353
Reserve:      $0.1000 (keep for emergencies)
Discretionary: $0.3353
```

---

## §3 Model Selection Decision Tree

```
TASK ENTERS
    |
    +-- Does it touch 3+ subsystems?
    |   +-- YES -> Is it architectural? (WAD, Mandates, Flywheel)
    |   |   +-- YES -> USE PRO
    |   |   +-- NO  -> Use Flash
    |   +-- NO  -> Continue
    |
    +-- Is it >1000 lines of analysis?
    |   +-- YES -> USE PRO
    |   +-- NO  -> Use Flash
    |
    +-- Is budget < $0.10?
    |   +-- YES -> Use Flash (always)
    |   +-- NO  -> Consider Pro value
    |
    +-- Is it an N+1 routine fix?
    |   +-- Always -> Use Flash
    |
    +-- DEFAULT: Use Flash. Only escalate to Pro when Flash hits a wall.
```

---

## §4 Other Free Tier Models in Reserve

Beyond DeepSeek Flash, the Cline free tier also offers:

| Model | ID | Context | Best For |
|-------|-----|---------|----------|
| **MiniMax M3** | `minimax/minimax-m3` | 1M peak / ~512K top provider | Multimodal (image+video analysis), creative tasks |
| **MiMo V2.5** | `xiaomi/mimo-v2.5` | Unknown (free tier) | Backup/alternative perspective, load balancing |

---

## §5 Session Protocol

When starting work:

1. Default to `-P cline -m deepseek/deepseek-v4-flash` (free)
2. Only switch to Pro if the decision tree says so
3. Track Pro usage in this lab (deduct from budget)
4. Log Pro sessions to Hivemind with estimated cost
5. If within Distillery (L3): use Flash for routine, consider Pro for distillation synthesis

---

*Lab maintained by Cline-M3 | Last Updated: 2026-06-09*
*This is not a Mandate. It is a strategy document for budget-conscious model allocation.*
