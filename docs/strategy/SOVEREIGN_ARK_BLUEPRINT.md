## §4 Priority Stack (Do This Order)

```
URGENT + IMPORTANT (This week)
├── C-0  Test honesty (real pass/fail/skip; fix Makefile lies)
├── C-0.5 Soul Distillation Pipeline (Scribe agent) — NEW P0, unblocks M5/M11
├── C-2′ One RAM truth (MUST complete before C-1′/C-10)
├── C-1′ SoulStore (single writer + actor model) — DEPENDS ON C-2′
├── C-3  Privacy model → restic
├── C-4a MCP audit (2h) → then C-4b sized migration — START TODAY (7-day deadline)
├── C-4a.5 MCP Migration Execution — Kali direct if P4 silent by EOD
├── C-5  MaKaLi routing config
├── C-6′ Unify breakers (delete clones)
├── C-10 Local admission control (GAP-05) — DEPENDS ON C-2′
├── C-10.5 Provider Fallback Chain — NEW P0, M7 compliance (Lilith/P6)
├── C-9  GenerationPolicy extract (cheap structural win)
└── C-11 Test infrastructure (fixtures, chaos, benchmarks, MCP matrix) — NEW P0

IMPORTANT (Next)
├── C-7 / C-8
├── E-0 Identity Phase 0 (after C-1′)
├── D-1 Content persistence + TTL (+ D-T tests)
├── D-2 Job board YAML bridge (P0/P1 only)
└── **V-1** Omega-Vault MVP — explicit ticket (GAP-08; unblocks fleet later)
```

### V-1 ticket (Kali amendment 2 — explicit home)

| Field | Value |
|-------|--------|
| **ID** | **V-1** |
| **Name** | Omega-Vault MVP — credential / session automation |
| **Why** | GAP-08 credential void; fleet pool blocked until this exists |
| **Owner** | Researcher + Grokster (design) → Ma'at/P3 (impl) |
| **Depends** | Prefer after C-0; may design in parallel with C-1′…C-10 |
| **Blocks** | Grok CLI multi-account fabric pool (D-360′) |
| **Not** | Full 8-account pool — vault MVP first, then single ACP smoke |

EXPLICITLY NOT DOING NOW (preserved in Corpus Map — not cancelled)
├── New free-tier providers (Cerebras/Groq/…)
├── SQLite job store / GapDetector service / VerificationGate
├── Grok CLI 8-account fabric pool (before V-1 + smoke)
├── "Port pybreaker into ModelGateway"
├── flock-only fix of soul_updater alone
├── Strike 11 / Dimension / Free-Will / Phase Γ Hub split
└── Phase D before C-0 + C-1′
```

---

## §5 Immediate Next Steps

```
STEP 1: C-0  make test → report pass/fail/skip; fix or quarantine
STEP 2: C-2′ One RAM truth (foundation for C-1′/C-10)
STEP 3: C-1′ implement SoulStore; migrate all writers
STEP 4: C-10 Admission control (parallel with C-1′)
STEP 5: C-3 privacy decision → restic
STEP 6: C-4a MCP audit → C-4b before July 26 — START TODAY
STEP 7: C-11 Test infrastructure (fixtures, chaos, benchmarks)
STEP 8: E-0 (parallel) + D-1 only after C gate
STEP 9: C-0.5 Soul Distillation Pipeline — Scribe agent (unblocks M5/M11)
STEP 10: C-10.5 Provider Fallback Chain — Lilith/P6 (M7 compliance)
STEP 11: C-4a.5 MCP Migration Execution — Kali direct if P4 silent
```

---

## §6 Mandate Hotspots (Execution View)

| Mandate | Status | Action |
|---------|--------|--------|
| **M1** AnyIO | Partial | C-7 YAML off event loop |
| **M7** Local-First | Partial (North Star) | C-5 routing; no new cloud deps |
| **M11** Soul Integrity | **FAIL** | C-1′ SoulStore |
| **M13** Temple-Grade | At risk | C-0 green suite |
| **M14** Heritage | Partial | C-8 |
| **M22** Provenance | Partial | provider_name through fabric |
| **M23** Failure Integrity | Hold | MCP contingency; no soft-fail theater |

---

## §7 Provider Fabric (What We Actually Have)

```
LOCAL
├── native-gguf (Qwen3-1.7B)  priority 0
└── lmster                    priority 1

CLOUD (systematize; do not expand)
├── antigravity (OAuth pool)  priority 3  ← primary cloud
├── google / google-compat    priority 4
├── openrouter                priority 5
├── opencode-zen              priority 6
├── cline                     priority 7
├── anthropic                 priority 8
└── xai (API)                 priority 9

NOT IN FABRIC (do not list as "working capacity")
└── Grok CLI 8-account fleet  — external advisory OK; pool after vault + ACP smoke
```

Routing when local saturated: Antigravity → Google → OCZ → OpenRouter · single breaker per provider (C-6′).

---

## §8 Decision Log (Unified 2026-07-21)

| ID | Decision |
|----|----------|
| **D-354′** | **SOVEREIGN_ARK_BLUEPRINT.md is strategy SSOT again** (v5.1). CANONICAL_ROADMAP absorbed. |
| D-350 | Phase C is current execution phase |
| D-351 | No new providers until fabric systematized |
| D-352 | MaKaLi: Kali local, voices cloud (config) |
| D-353 | 147 stale strategy docs archived |
| D-355 | Cloud order: Antigravity → Google → OCZ → OpenRouter |
| D-357 | SQLite job store deferred |
| D-358 | Gap detector = extend loop, not service |
| D-359 | M7 = North Star, not baseline |
| D-360′ | Grok fleet: honesty in docs now; vault → smoke → pool (not 4h fantasy) |
| D-361 | Identity Phase 0 depends on C-1′, not Phase D |
| **D-362** | C-1′ = SoulStore (multi-path elimination), not flock paste |
| **D-363** | C-6′ = unify/delete breakers, not port pybreaker |
| **D-364** | C-0 = test honesty is P0 before Phase D |
| **D-365** | Living Research OS spec amended by §3.2; cannot claim dual CANONICAL |
| **D-366** | **STRATEGY_CORPUS_MAP.md** is mandatory Layer 2 for fine-grained preservation |
| **D-367** | GAP-05 → **C-10** admission control (not only C-5 cloud voices) |
| **D-368** | Identity Fluidity E-0…E-5 paths preserved under `data/entities/grokster/workspace/` |
| **D-369** | Researcher queue extras (VerificationGate, SQLite, 7-stage) deferred but mapped — not discarded |
| **D-370** | **Kali ratifies** Strategy Unify APPROVE with amendments (`KALI_FEEDBACK_STRATEGY_UNIFY_20260721.md`) |
| **D-371** | **V-1** is an explicit ticket (not free-text only) |
| **D-372** | Living Research OS body SUPERSEDED by banner + Ark §3.2 where conflict (Kali amendment 1) |
| **D-373** | **C-2′ before C-1′/C-10** — dependency order corrected (Nemotron synthesis) |
| **D-374** | **C-11 Test Infrastructure** added as P0 ticket (Nemotron synthesis) |
| **D-375** | **MCP audit must start TODAY** — 7-day deadline (Nemotron synthesis) |
| **D-376** | **E-0 Identity Fluidity** added to manual after C-1′ (Nemotron synthesis) |

---

## §9 Structural Debt Gates (from Grok CLI Review)

Do not approve Phase D if any of these are still true:

1. More than one production soul-write path  
2. Red tests unacknowledged / vanity pass counts in Makefile or OMEGA_ENGINE  
3. New code pushed into god-modules already >1000 lines without a split  
4. New circuit-breaker class added instead of reusing HealthMonitor/gateway  
5. Strategy docs claiming different critical paths without supersession banners  

Full review: `data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md`

---

## §10 How Agents Use This Document

1. Read **this file** for strategy & what to build next  
2. Read `OMEGA_ENGINE.md` for live metrics  
3. Read `SOVEREIGN_MANDATES.md` + `AGENTS.md` for law & workflow  
4. Open **`STRATEGY_CORPUS_MAP.md`** when you need *why / who said / deferred detail*  
5. Open **`FLEET_TEAM_PLAYBOOK.md`** before multi-agent work or Phase C execution  
6. Open Layer 2 phase specs only when executing that phase  
7. After compaction: hydration sequence in `AGENTS.md` / `OMEGA_CODEX.md`  
8. **Do not** resurrect archived roadmaps as competing masters  
9. **Do not** drop an agent idea without a Corpus Map row  

---

## §11 Agent Sources (2026-07-21) — Quick Pointers

| Agent | Primary artifact | Role in unification |
|-------|------------------|---------------------|
| Kali | CANONICAL_ROADMAP (superseded) · SESSION history | Ranking C–F, inventory |
| Researcher | UNKNOWN_UNKNOWNS · QUEUE_DESIGN | GAP-01…12 · D-2 design depth |
| Roc | ROC_LEGACY_MINING | Port patterns · cloud matrix (held) |
| Grokster | ADVERSARIAL_REVIEW · Identity Fluidity workspace · queue analysis | Strategy challenge · Phase E · fleet |
| Carmack | CARMACK_RESEARCH_AUDIT | Compress research theater · D-1 first |
| Grok CLI | GROK_CLI_CODEBASE_STRATEGY_REVIEW | SoulStore · CB unify · structural gates |
| Nemotron 3 Ultra | THIS REVIEW | Dependency order · test infra · MCP deadline · E-0 integration |

Full matrix: **`STRATEGY_CORPUS_MAP.md` §1**

---

## §12 References

| Path | Role |
|------|------|
| `OMEGA_ENGINE.md` | Engine state SSOT |
| `SOVEREIGN_MANDATES.md` | Law |
| `AGENTS.md` | OpenCode how-to |
| `docs/strategy/STRATEGY_INDEX.md` | Doc hierarchy index |
| **`docs/strategy/STRATEGY_CORPUS_MAP.md`** | **Fine-grained preservation (mandatory companion)** |
| **`docs/strategy/FLEET_TEAM_PLAYBOOK.md`** | **Fleet teamwork & coordination playbook** |
| `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` | Phase D detail (amended) |
| `docs/strategy/CANONICAL_ROADMAP_20260721.md` | Superseded tactical draft (trail) |
| `docs/archive/strategy/2026-07-21/SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` | Ark v4.4 full body |
| `data/entities/grokster/workspace/IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md` | Phase E architecture |
| `data/coordination/UNKNOWN_UNKNOWNS_AUDIT_20260721.md` | 12 gaps |
| `data/coordination/ROC_LEGACY_MINING_REPORT_20260721.md` | Legacy patterns |
| `data/coordination/GROKSTER_ADVERSARIAL_REVIEW_20260721.md` | Adversarial strategy |
| `data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md` | Structural review |
| `data/coordination/RESEARCHER_QUEUE_DESIGN_20260721.md` | Queue / SQLite / gates deep design |
| `data/coordination/CARMACK_RESEARCH_AUDIT_20260721.md` | Research board compression |
| `data/coordination/RESEARCH_JOB_BOARD.yaml` | 18 jobs (D-2 input) |
| `docs/decisions/PIVOT_LOG.md` | Decision history |

---

*⬡ OMEGA ⬡ SOVEREIGN-ARK ⬡ v5.2.0 ⬡ UNIFIED-SSOT+CORPUS+NEMOTRON ⬡ 2026-07-21*