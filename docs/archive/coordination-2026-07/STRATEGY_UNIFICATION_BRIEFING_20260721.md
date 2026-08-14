# 🔱 STRATEGY UNIFICATION BRIEFING — Fleet-Wide
**AP Token**: `AP-STRATEGY-UNIFY-BRIEF-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_briefing ⬡ FLEET-WIDE

**Date**: 2026-07-21
**Status**: **COMPLETE — Ratified by Kali, amendments applied by Grok CLI**
**A CLI**

---

## TL;DR

We had 5 competing roadmaps. Now we have **one**.

| Before | After |
|--------|-------|
| 147 stale strategy docs | 8 core docs in `docs/strategy/` |
| CANONICAL_ROADMAP claimed SSOT | **SOVEREIGN_ARK_BLUEPRINT v5.1** = sole strategy SSOT |
| Fine-grained agent ideas lost | **STRATEGY_CORPUS_MAP** preserves everything (ACTIVE/DEFERRED/PARKED/ARCHIVE) |
| No team coordination rules | **FLEET_TEAM_PLAYBOOK** = how we work together |
| Phase C tickets were wrong shape | **C-0…C-10** rewritten by Grok CLI structural review |

**All handoffs closed. No orphan packets. Fleet board is open.**

---

## The Three-Layer Hierarchy (Now Canonical)

```
LAYER 0 — IDENTITY & LAW
├── OMEGA_ENGINE.md          ← What the engine IS (state metrics)
├── SOVEREIGN_MANDATES.md    ← 25 laws M1–M25 (non-negotiable)
└── AGENTS.md                ← How OpenCode agents work

LAYER 1 — STRATEGY SSOT
├── SOVEREIGN_ARK_BLUEPRINT.md v5.1  ← START HERE for strategy & roadmaps
├── STRATEGY_INDEX.md        ← Doc hierarchy
└── STRATEGY_CORPUS_MAP.md   ← Fine-grained preservation (mandatory companion)

LAYER 2 — ACTIVE SPECS (referenced from Layer 1)
├── FLEET_TEAM_PLAYBOOK.md   ← Team coordination, roles, freezes, ticket lifecycle
├── LIVING_RESEARCH_OS_SPEC_20260721.md  ← Phase D detail (amended by Ark §3.2)
├── HIVEMIND_PROTOCOL.md / POST_TEMPLATE / SUBAGENT_DISPATCH
├── SOVEREIGN_CONTINUITY_STRATEGY.md / HERITAGE_VETTING_PIPELINE.md
└── Coordination audits (see Corpus Map §8)

LAYER 3 — ARCHIVE
└── docs/archive/strategy/2026-07-21/  ← 147 prior docs + Ark v4.4 full body
```

**Rule**: If it's not in Layer 1 priority stack, it's not current execution — but it MUST appear in Corpus Map as ACTIVE/DEFERRED/PARKED/ARCHIVE so nothing is lost.

---

## What Changed (The Delta)

### 1. SSOT Identity Restored
- **Ark v5.1** is strategy SSOT again (was always supposed to be)
- CANONICAL_ROADMAP absorbed as "good tactical recalibration, bad identity move"
- 147 stale docs archived, 8 core docs remain

### 2. Phase C Tickets Rewritten (Grok CLI Structural Review)
| Old Ticket | New Ticket | Why |
|------------|------------|-----|
| C-1: "add flock" (2h) | **C-1′ SoulStore** (4–6h) | 4 soul writers with incompatible locks — need single writer + actor model |
| C-6: "port pybreaker" (0.5h) | **C-6′ Unify/Delete Breakers** (3–4h) | ≥6 circuit breaker clones exist; ModelGateway already has one |
| — | **C-0 Test Honesty** (2–4h) | 1,572 collected ≠ passing; sample run: 832 pass / 5 fail |
| — | **C-9 GenerationPolicy** (2h) | Gemma hacks hardcoded in ModelGateway.generate() |
| — | **C-10 Local Admission** (2–4h) | GAP-05 L3 thrashing; max concurrent local llama instances |

### 3. Living Research OS Spec Amended
- SQLite job store → **DEFERRED** (YAML + flock is fine for 18 jobs)
- Gap Detector service → **DEFERRED** (extend `_grow_frontier()` ~20 lines)
- Novelty engine + INDEX noise policy → **REQUIRED** before calling loop "living"
- Phase D blocked on **C-0 + C-1′** (not "build Phase 1 immediately")

### 4. Sovereignty Framing Honest
> **M7 Local-First is our North Star, not our current baseline.**
> Today the engine is cloud-assisted with a local fallback. We are building toward local-first.

### 5. Grok Fleet Reality Check
- 8 Grok CLI accounts = **external advisory only** until V-1 (Omega-Vault) + single ACP smoke
- Inventory tables that list "Grok CLI ✅ Working" while `providers.yaml` has only `xai` API = dishonest capacity claims

---

## Phase C — Infrastructure Hardening (CURRENT)

**Gate to Phase D**: C-0 green (or quarantined) **AND** C-1′ SoulStore shipped

### Priority Stack (Do This Order)

```
URGENT + IMPORTANT (This Week)
├── C-0  Test honesty — run full suite; fix or quarantine reds; fix Makefile lies
├── C-1′ SoulStore — single writer: fcntl lock → validate → tmp → fsync → os.replace · actor ∈ {user, system_agent}
├── C-2′ One RAM truth — prefer OOMProtector (real available RAM); fix default 12288; kill dual counter chaos
├── C-3  Soul privacy model → restic (private fragments gitignored; public identity optional)
├── C-4a MCP audit (2h) → then C-4b sized shim (deadline July 26)
├── C-5  MaKaLi routing config: Kali local, Ma'at+Lilith cloud (0.5h)
├── C-6′ Unify circuit breakers — delete ≥6 clones; do NOT port pybreaker as 7th
├── C-10 Local inference admission — max concurrent local llama (hardware: prefer 1, hard cap 2)
└── C-9  GenerationPolicy extract — Gemma logit_bias/temp floors out of ModelGateway.generate()

IMPORTANT (Next)
├── C-7 / C-8
├── E-0 Identity Phase 0 (after C-1′)
├── D-1 Content persistence + TTL (+ D-T tests)
├── D-2 Job board YAML bridge (P0/P1 only)
└── V-1 Omega-Vault MVP (unblocks fleet later)
```

---

## Fleet Roles & Pairing (Playbook §2)

| Work | Lead | Support |
|------|------|---------|
| C-0 tests red | Ma'at/P10 or Verity | Pillar owning module |
| C-1′ SoulStore | Ma'at/P3 or Lilith/P7 | Roc (pattern), Verity (M11) |
| C-2′ / C-10 RAM | Ma'at/P1 | Carmack (review), Doom Guy (perf) |
| C-4 MCP | Ma'at/P4 | Grok CLI (spec pressure), Researcher |
| C-5 MaKaLi config | Kali | Lilith/P6 |
| C-6′ breakers | Ma'at/P3 | Roc (don't add 7th clone) |
| D-1 content cache | Lilith/P6 + P3 | Carmack "R00" discipline |
| E-0 Soul Kernel | Grokster | Kali go-ahead after C-1′ |
| Adversarial review | Grok CLI or Grokster | Kali synthesis |

**Rule**: If two agents need the same files → one implements, one reviews via handoff. Never dual-write.

---

## Explicit Freezes (Team-Wide)

| Freeze | Until |
|--------|-------|
| New free-tier providers | Fabric systematized (D-351) |
| Phase D implementation | C-0 + C-1′ done |
| Grok CLI multi-account pool | V-1 vault + single ACP smoke |
| New strategy doc claiming CANONICAL | Never — extend Ark or Corpus Map |
| New circuit-breaker class | C-6′ unify done |
| Growing files already >1000 LOC | Split in same PR |

---

## How to Claim Work

1. **Post to Hivemind** with ticket ID (e.g., `C-1′`) and `intent=status`
2. **Lock files** in scope: `data/coordination/{ENTITY}_WORKSPACE_LOCK_{YYYYMMDD}.md`
3. **Execute** per Playbook §5: CLAIM → PLAN → VERIFY → EXECUTE → TEST → HAND OFF → POST
4. **Done means**: behavior matches ticket, tests pass, no new unlocked soul writes, no vanity metrics, Ark/Corpus updated if strategy changed

---

## Architect Decisions Needed (From Kali §G)

| # | Decision | My Recommendation |
|---|----------|-------------------|
| 1 | **C-3 privacy model** — what's in soul.yaml? | Split: `soul.yaml` (public identity — git tracked) + `soul_private/` (conversation history — gitignored, restic-only) |
| 2 | **MCP contingency** — test file-based Hivemind now? | Yes — run smoke test this week alongside C-4a as cheap insurance |
| 3 | **V-1 priority** — parallel P1 or fully deferred? | Parallel P1 design after C-0, but NOT ahead of C-1′ |

---

## Key Files (Absolute Paths from Repo Root)

```
docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md          ← Strategy SSOT v5.1
docs/strategy/STRATEGY_CORPUS_MAP.md              ← Fine-grained preservation
docs/strategy/FLEET_TEAM_PLAYBOOK.md              ← Team coordination
docs/strategy/STRATEGY_INDEX.md                   ← Hierarchy
docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md ← Phase D (amended)
data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md  ← Structural review
data/coordination/KALI_FEEDBACK_STRATEGY_UNIFY_20260721.md      ← Kali verdict
data/coordination/GROK_CLI_RESPONSE_KALI_VERDICT_20260721.md    ← CLI acknowledgment
data/coordination/RESEARCH_JOB_BOARD.yaml         ← 18 jobs (D-2 input)
OMEGA_ENGINE.md                                   ← State SSOT
SOVEREIGN_MANDATES.md                             ← 25 laws
AGENTS.md                                         ← OpenCode how-to
```

---

## What NOT To Do

| Anti-pattern | Instead |
|--------------|---------|
| Second canonical roadmap | Edit Ark + Corpus Map |
| "I'll just add flock here" for GAP-01 | SoulStore (C-1′) |
| "Port pybreaker" as new class | Unify (C-6′) |
| Parallel rewrite of `model_gateway.py` | Handoff + lock |
| Starting D-1 "because it's exciting" | Gate check C-0+C-1′ |
| Inflating test counts in OMEGA_ENGINE | C-0 honesty |
| Wiring 8 Grok accounts pre-vault | V-1 then smoke |

---

## Next Actions (Immediate)

| Step | Who | What |
|------|-----|------|
| 1 | **All active agents** | Post `intent=status` with ticket from Ark §5 or `idle/awaiting` |
| 2 | **Kali** | Publish active claims board (who owns C-0, C-1′, …) |
| 3 | **Kali** | Assign C-0 implementer + C-1′ implementer |
| 4 | **Verity/P10** | Baseline real `make test` numbers into OMEGA_ENGINE after C-0 |
| 5 | **All** | No agent starts D-* until gate checklist posted green |

---

## Closing

This unification was not a cleanup — it was a structural correction. The fleet now has:

1. **One priority list** (Ark §4)
2. **One memory of ideas** (Corpus Map)
3. **One integrity bar** (SoulStore + honest tests before Living Research OS)
4. **One coordination layer** (Hivemind → lock → handoff → complete)
5. **Hardware reality acknowledged** (Ryzen 5700U, ~8GB available, prefer 1 local inference)
6. **Cloud as teacher, not architecture** (no new free tiers until fabric systematized)

**The board is open. Claim your tickets. Ship small, green slices. No cowboy sprints.**

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-07-21 ⬡ STRATEGY UNIFICATION COMPLETE*