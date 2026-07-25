# 🔱 Critical Sprint Knowledge Gaps — Agent Support Hardening
**AP Token**: `AP-CRITICAL-SPRINT-KG-AGENT-SUPPORT-v1.0.0`  
⬡ OMEGA ⬡ GROK_CLI ⬡ RESEARCH ⬡ SPRINT ⬡ 2026-07-25

**Status**: COMPLETE — ground-truth audit + strategy/execution hardening  
**Owner**: @grok_cli (Consulting Cloud Mind) · Review: @kali  
**Companion plan**: `docs/sprints/current/EXECUTION_PLAN_20260725.md` v1.1  
**Agent card**: `docs/sprints/current/AGENT_SPRINT_CARD.md`

---

## §1 Executive Verdict

Prior gap-closure docs (`KNOWLEDGE_GAP_CLOSURE.md`, `KNOWLEDGE_GAP_CLOSURE_FULL.md`) correctly **researched** 46+ historical gaps. They incorrectly implied **execution closure** and “no remaining blind spots.”

**As of 2026-07-25T21:30Z ground truth, the highest-harm gaps are no longer “unknown MCP patterns” or “how to encrypt vault secrets.” They are agent-support failures:**

| Rank | Gap ID | Name | Harm to agents | Status |
|------|--------|------|----------------|--------|
| 1 | **SG-01** | SSOT / plan / hub / anchor **triple drift** | Agents execute yesterday’s tracks | 🔴 OPEN |
| 2 | **SG-02** | **Phase D gate script inverted / vanity checks** | False PASS → premature Phase D | 🔴 OPEN → fix shipped in this work |
| 3 | **SG-03** | **C-0.5 hook unregistered** (file exists, config missing) | M5/M11 stay red; Scribe/Roc blocked | 🔴 OPEN |
| 4 | **SG-04** | **Dirty-tree coordination hazard** (VaultCore unification uncommitted) | Dual-write / revert / silent break | 🔴 OPEN |
| 5 | **SG-05** | **W-1 claimed operational, SOCKS silent** | Agents plan free-tier multi-IP that does not exist | 🔴 OPEN |
| 6 | **SG-06** | **Workhorse continuity under D-432** (free Google only) | Wrong model choices, 16k TPM cliff | 🟡 PARTIAL |
| 7 | **SG-07** | **Soul hardening design open, AGENTS already mutated** | Implementation thrash before RFC consensus | 🟡 OPEN |
| 8 | **SG-08** | **Playbook mission queue stale** (still “V-1 not yet”) | New agents re-open finished tickets | 🟡 OPEN |
| 9 | **SG-09** | **MCP pin vs installed version drift** | Surprise upgrades / false “pinned to 1.27” belief | 🟢 LOW (bounded) |
| 10 | **SG-10** | **False “all gaps closed” narrative** | Stops gap detection; converges to local max (GAP-S-05) | 🔴 META |

**Principle (2026 multi-agent systems):** Gap detection must distinguish **research-closed** (we know what to do) from **execution-closed** (done signal is green on the machine). SSOT entries need **freshness stamps** and **ground-truth commands**, not prose status alone.

---

## §2 Method

| Step | Action | Evidence |
|------|--------|----------|
| 1 | Hydrate D-277 | Hivemind, git, Codex, HMC, SESSION_ANCHOR |
| 2 | Read plan + KG closure + Ark + Playbook | `docs/sprints/current/*`, strategy SSOT |
| 3 | Ground-truth commands | hooks, mcp pin, warp listeners, restic timers, vault tree |
| 4 | Adversarial cross-check | GAP-S-01..05, Soul Hardening RFC, dirty git |
| 5 | External patterns | Multi-agent SSOT freshness + prioritization loop; MCP version discipline |

**Temporal mandate**: Sources and decisions dated **2026-07-25**.

---

## §3 Ground Truth Snapshot (2026-07-25T21:30Z)

| Claim in plan/hub | Machine truth | Delta |
|-------------------|---------------|-------|
| Plan status PRE-LAUNCH, 3 blockers | Tracks A/C/D marked complete in HMC; many code paths already landed | Plan stale |
| mcp pin TODAY | `pyproject.toml`: `mcp>=1.27,<2`; installed **1.28.1**; `requirements.txt` pins **1.27.1** | Pin done; version story inconsistent |
| C-0.5 hook registered | `.opencode/hooks/session_end.py` **exists**; `.opencode/opencode.json` has **no hooks key** | Not registered |
| W-1 operational / 8081–8083 | **No listeners** on 8081–8083 | Not live |
| PolicyKit rule install | Rule content exists under `/tmp/99-omega-warp.rules`; system path not agent-verifiable | Partial |
| Phase D gate script objective | Several checks **pass when feature MISSING** (L3 count expects `0`; restic timer expects `NOT CONFIGURED`) | Dangerous |
| VaultCore complete | Uncommitted mass rewrite (KeyVault deleted, BlindVault, scanners) | Code present, not landed |
| All KG closed | Research yes; execution + meta-SSOT no | Overclaim |
| SESSION_ANCHOR | Still KG-1/2 “next KG-3…” while hub shows KG-1..6 done | Anchor stale |

---

## §4 Critical Gaps Detail

### SG-01 — SSOT Triple Drift (P0)

**Symptom**: Four “truth” surfaces disagree:

1. `EXECUTION_PLAN_20260725.md` — PRE-LAUNCH  
2. `HMC_COLLABORATION_HUB.md` — tracks complete, sprint advanced  
3. `SESSION_ANCHOR.md` — KG mid-flight  
4. `.opencode/anchored-summary.md` — Guard & Distill C-11 next  

**Agent failure mode**: Hydrating agents re-do Track D, re-open V-1 design, or skip live P0s (hook, WARP, commit hygiene).

**Hardening**:
- Truth hierarchy (see AGENT_SPRINT_CARD)  
- Plan status must be **reality-stamped** with `LAST_VERIFIED` + shell probes  
- SESSION_ANCHOR update on every major track flip (M15)

### SG-02 — Phase D Gate Script Vanity / Inversion (P0)

`scripts/verify_phase_d_gate.py` used:

| Check | Expected substring | Actual meaning |
|-------|--------------------|----------------|
| Soul distillation ≥1 L3/week | `"0"` | **Passes when zero L3** |
| Restic weekly check | `"NOT CONFIGURED"` | **Passes when timer missing** |
| C-1′ / C-2′ / C-10 | `grep` for keywords | Passes on comments / dead code |
| make temple-grade | count of PASS lines == 11 | Fragile parse |

**Hardening**: Rewrite to fail-closed, real probes (file presence + config keys + timer enabled + pytest exit codes). Shipped in this workstream.

### SG-03 — C-0.5 Hook Unregistered (P0)

- Hook implementation: `.opencode/hooks/session_end.py`  
- Config: **missing** from `.opencode/opencode.json`  
- Unblocks: Scribe, Roc proposal distillation, M5/M11 compliance trajectory  

**Hardening**: Exact JSON patch + **restart OpenCode** as single Track A remaining step. Do not mark C-0.5 ✅ until a session_end fire is logged.

### SG-04 — Dirty-Tree Coordination Hazard (P0)

Working tree contains concurrent unfinished programs:

- VaultCore unification + secret scanners + pre-commit  
- Oracle/provider/search/worker edits  
- Soul hardening prose in AGENTS.md + roc soul  
- Hub edits  

**Agent failure mode**: Second agent “implements VaultCore” against deleted KeyVault; or `git checkout --` nukes another’s day.

**Hardening**:
- **Freeze zones** per path prefix (AGENT_SPRINT_CARD)  
- One lander for vault slice; no parallel rewrites of `src/omega/vault/`  
- Prefer commit slices over mega-diff before Phase D gate

### SG-05 — W-1 Phantom Capacity (P0)

Hub/codex claim WARP pool fixed/active. **No SOCKS listeners** on 8081–8083.

**Agent failure mode**: G-1c / free-tier multi-IP plans assume capacity that is not there (classic GAP-S-01 phantom supercomputer pattern).

**Hardening**: Status language must be **probe-backed**:

```bash
ss -lntp | rg '808[123]' || echo FAIL
curl --socks5 127.0.0.1:8081 https://ifconfig.me
```

### SG-06 — Workhorse Continuity under D-432 (P1)

Architect constraint: **zero paid Google**. Gemma free-tier cliff remains real for fat sessions. Recommended chain (D-441..444) exists in hub but is not a single agent-facing “default model card.”

**Hardening**: Put default fallback chain on AGENT_SPRINT_CARD; forbid “just enable billing” as plan step without Architect override of D-432.

### SG-07 — Soul Hardening Pre-Consensus Mutation (P1)

RFC open (`R_AGENT_SOUL_FILE_HARDENING_20260725.md`) while AGENTS.md already carries SoulHealthScorer / CI gate design as mandatory.

**Hardening**: Mark design as **RFC / not gate** until Kali + Verity threshold decision; implementation owners only after Discussion Thread replies.

### SG-08 — Playbook Stale Mission Queue (P1)

`FLEET_TEAM_PLAYBOOK.md` §3 still lists C-0→… with “V-1 not yet.” Agents reading playbook alone regress.

**Hardening**: Point §3 to EXECUTION_PLAN + AGENT_SPRINT_CARD as **live mission**; playbook keeps durable rules only.

### SG-09 — MCP Version Story (P2)

| Surface | Value |
|---------|-------|
| pyproject | `mcp>=1.27,<2` |
| requirements.txt | `mcp==1.27.1` |
| installed venv | `1.28.1` |

Within `<2` bound — OK for CG-01 intent. Still confuses agents who “verify pin = 1.27.1.”

**Hardening**: Single SSOT pin line on sprint card; align requirements to installed or document “range OK.”

### SG-10 — False Closure Meta-Gap (P0 narrative)

Declaring “no remaining blind spots” after research only recreates **GAP-S-05** (closed loop / local maximum). Residual gap list must stay open-ended with **last_verified** timestamps.

---

## §5 What Is Actually Closed (Do Not Re-Research)

| Domain | State | Do not re-open as research |
|--------|-------|----------------------------|
| CG-01 MCP migration knowledge | Researched; pin present | Only execute version alignment + header audit |
| CG-04 / V-1 crypto pattern | Age+Argon2id validated | Land uncommitted code; don’t reselect vault crypto |
| CG-02 / C-2′ hardware | 5700U Zen2 profile validated | Keep max-1 local inference |
| C-3 local restic design | Scripts exist | Need timer/repo probe, not new design |
| KG-1..6 contribution research | Docs exist | Apply, don’t re-survey FOSS |
| R19 privacy model research | Spec complete | Implement only after gate + vault land |

---

## §6 Prioritization Model (Agent-Support First)

Score used for this sprint residual backlog:

```
priority = 3*blocks_other_agents
         + 2*false_green_risk
         + 2*architect_ops_dependency
         + 1*phase_d_gate_criterion
         - 1*research_already_done
```

| Item | Score driver | Owner | Effort |
|------|--------------|-------|--------|
| Register C-0.5 + restart | blocks_other_agents | @kali | 5 min |
| Fix gate script fail-closed | false_green_risk | @verity / any | 30 min |
| Commit vault slice / freeze zone | blocks_other_agents | @maat/P3 | 1–2 h |
| W-1 live probe + bring-up | architect_ops + phantom capacity | Carmack/P1 + Architect | 15–45 min |
| Refresh plan + anchor + card | false_green / drift | @grok_cli / @kali | this docset |
| Align mcp pin story | low | @maat/P3 | 10 min |
| Soul RFC replies | design thrash | fleet Discussion Threads | async |

---

## §7 Strategy Implications (Ark-Compatible)

Does **not** reorder Ark super-urgent G-1 ∥ W-1. It **adds an integrity layer** agents need to execute those tickets without thrash:

1. **Freshness SLA** for sprint SSOT surfaces (plan, hub summary, SESSION_ANCHOR): max 12h drift during active multi-agent work.  
2. **Probe-backed status** for infrastructure claims (WARP, hooks, restic timers, mcp version).  
3. **Dirty-tree freeze zones** before parallel tracks touch shared packages.  
4. **Gate scripts fail-closed** (M23 spirit — no soft pass on missing mandatory tools).  
5. Keep **research vs execution** columns separate in every gap table.

---

## §8 Deliverables from This Workstream

| Deliverable | Path |
|-------------|------|
| This research report | `docs/research/R_CRITICAL_SPRINT_AGENT_SUPPORT_GAPS_20260725.md` |
| Hardened execution plan v1.1 | `docs/sprints/current/EXECUTION_PLAN_20260725.md` |
| One-page agent card | `docs/sprints/current/AGENT_SPRINT_CARD.md` |
| Residual gaps addendum | `docs/sprints/current/KNOWLEDGE_GAP_CLOSURE.md` § residual |
| Fail-closed gate script | `scripts/verify_phase_d_gate.py` |
| Session anchor refresh | `data/coordination/SESSION_ANCHOR.md` |
| Sprint llms index | `docs/sprints/current/llms.txt` |

---

## §9 Sources

| Source | Role |
|--------|------|
| Live machine probes 2026-07-25 | Ground truth |
| `docs/sprints/current/KNOWLEDGE_GAP_CLOSURE*.md` | Prior research closure (overclaimed execution) |
| `docs/research/R_GAP_S_ADVERSARIAL_GAPS.md` | Phantom capacity + test mirage patterns |
| `docs/research/R_AGENT_SOUL_FILE_HARDENING_20260725.md` | Open RFC vs AGENTS mutation |
| HMC hub + SESSION_ANCHOR + EXECUTION_PLAN | Drift evidence |
| Multi-agent SSOT freshness / prioritization patterns (2026 design practice) | Freshness SLA, research vs execution split |
| MCP version discipline (protocol dated versions + SDK bounds) | Pin narrative hygiene |

---

*⬡ OMEGA ⬡ GROK_CLI ⬡ CRITICAL-SPRINT-KG ⬡ AGENT-SUPPORT ⬡ 2026-07-25*
