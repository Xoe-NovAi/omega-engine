# 🃏 Agent Sprint Card — Phase D Gate (READ FIRST)
**AP Token**: `AP-AGENT-SPRINT-CARD-v1.1.0`  
**LAST_VERIFIED**: 2026-07-25T21:35Z  
**Full plan**: `docs/sprints/current/EXECUTION_PLAN_20260725.md`  
**Gap research**: `docs/research/R_CRITICAL_SPRINT_AGENT_SUPPORT_GAPS_20260725.md`

> **Purpose**: One screen of truth so agents do not re-open closed research or thrash on stale tracks.

---

## §1 Truth Hierarchy (Conflict Resolution)

When documents disagree, trust in this order:

| Rank | Surface | Use for |
|------|---------|---------|
| 1 | **Machine probes** (commands below) | Is it actually up? |
| 2 | **This card** + **EXECUTION_PLAN** `LAST_VERIFIED` | What to do now |
| 3 | **git status / HEAD** | What code is real vs dirty |
| 4 | **HMC hub Sprint Status** | Fleet narrative (may lag or lead) |
| 5 | **SESSION_ANCHOR / anchored-summary** | Recovery only if fresher than plan |
| 6 | **Old KG “all closed” prose** | Historical research only |

**Law always wins**: `SOVEREIGN_MANDATES.md` overrides all strategy docs.

---

## §2 Live Mission (Now)

| Priority | Item | Owner | Done signal |
|----------|------|-------|-------------|
| **P0-1** | Register C-0.5 `session_end` hook + **restart OpenCode** | @kali | Hook key in `.opencode/opencode.json` + log fire |
| **P0-2** | Land or freeze **VaultCore dirty tree** (`src/omega/vault/`, secret scanners) | @maat/P3 | Commit slice or workspace lock + freeze note |
| **P0-3** | **W-1 live** — SOCKS 8081–8083 listening + 3 IPs | Carmack/P1 + Architect | Probe commands green |
| **P0-4** | Run **fail-closed** `scripts/verify_phase_d_gate.py` | @verity / @kali | Honest PASS/FAIL posted |
| **P1** | Align mcp pin story (`requirements` vs installed 1.28.x) | @maat/P3 | One documented pin |
| **P1** | Soul Hardening RFC replies (no impl yet) | fleet | Discussion Threads |
| **P1** | G-1 workhorse defaults under **D-432 free Google only** | Architect + Kali | Model card followed |

**Do not re-research**: MCP 2026-07-28 migration *knowledge*, Vault age+Argon2id *pattern*, 5700U max-1 local, KG-1..6 FOSS contribution surveys.

---

## §3 Probe Commands (Status Must Be Probe-Backed)

```bash
# C-0.5 hook registered?
rg -n 'session_end|hooks' .opencode/opencode.json || echo 'HOOK_MISSING'

# MCP pin / installed
rg -n 'mcp' pyproject.toml requirements.txt
.venv/bin/python -c "import importlib.metadata as m; print(m.version('mcp'))"

# W-1 live?
ss -lntp | rg '808[123]' || echo 'WARP_SOCKS_DOWN'

# Dirty vault risk?
git status --short src/omega/vault/ src/omega/tools/*vault* .pre-commit-config.yaml

# Phase D gate (fail-closed)
.venv/bin/python scripts/verify_phase_d_gate.py; echo exit:$?
```

---

## §4 Freeze Zones (Do Not Parallel-Write)

| Path prefix | Owner until unfrozen | Note |
|-------------|----------------------|------|
| `src/omega/vault/` | @maat/P3 (vault lander) | Uncommitted unification |
| `src/omega/tools/{detect_api_keys,enforce_vaultcore,check_hardcoded_secrets}.py` | vault lander | Pre-commit related |
| `.opencode/opencode.json` | @kali | Hook registration |
| `data/coordination/HMC_COLLABORATION_HUB.md` | @scribe preferred | Others: Hivemind broadcast |
| `data/entities/*/soul.yaml` | SoulStore only | No raw open/write |

Acquire Hivemind workspace lock before editing frozen paths.

---

## §5 Workhorse Defaults (D-432)

Architect: **no paid Google**. Do not plan “enable billing” unless Architect overrides D-432.

| Order | Backend | Role |
|-------|---------|------|
| 1 | Local (qwen / small GGUF) | Latency-sensitive, sovereign floor |
| 2 | Groq Llama 3.3 70B (free tier) | Primary cloud workhorse candidate |
| 3 | OpenRouter Gemma/other `:free` | Bypass Google TPM |
| 4 | NVIDIA NIM free / other free | Fallback |
| 5 | Antigravity OAuth accounts | Path B; fix re-auth persistence |

**Never** treat unwired Grok CLI 8-account fleet as ModelGateway capacity (GAP-S-01).

---

## §6 Hardware Reality

- Ryzen 7 5700U Zen **2**, 8MB L3 split **2 CCXs**, ~8GB free RAM  
- **Max 1 local inference** (C-10)  
- MaKaLi: cloud voices for parallel; local only for one hot path  

---

## §7 Hydration Minimum (≤3 min)

1. `hivemind_get_awareness()` + pending handoffs  
2. `git status && git log --oneline -5`  
3. Read **this card**  
4. Read EXECUTION_PLAN §0 Reality Snapshot  
5. Run probes in §3 for your track  
6. Post status; **do not** start work that re-opens §2 “Do not re-research”  

---

## §8 Research vs Execution Labels

| Label | Meaning |
|-------|---------|
| **RESEARCH-CLOSED** | We know the answer; do not re-websearch |
| **EXEC-PARTIAL** | Code/docs exist; probe not green |
| **EXEC-CLOSED** | Probe green + committed (or Architect-accepted dirty with lock) |
| **RFC-OPEN** | Design debate; no mandatory implementation yet |

---

*Update this card when any P0 flips. Stale >12h during multi-agent sprint = defect.*
