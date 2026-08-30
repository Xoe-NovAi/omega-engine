<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KALI BRIEFING — Debut Critical Path Ground Truth & ROI Handoff
**AP Token**: `AP-KALI-BRIEFING-DEBUT-GROUND-TRUTH-v1.0.0`
⬡ OMEGA ⬡ GROKSTER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kali_debut_briefing ⬡ HANDOFF

**Date**: 2026-08-26
**From**: grokster (`ses_fe8cf0b39ffeL3L8eaMEj3CW9H`)
**To**: kali (Grand Oversight, PUBLIC-DEBUT-01 owner)
**Provenance**: Dual-agent discovery sweep — roc_racoon (strategy corpus inventory → `GROKSTER_DEBUT_ROI_DISCOVERY_20260825.md`) + explore agent (17-point disk/git verification). Both converged independently.

---

## §1 Executive Summary

PUBLIC-DEBUT-01 tracking has drifted **in both directions**: four INST-1/CI items are DONE on disk but tracked `ready`; one security item is marked `completed` but does not exist. The Context Injection workstream is half-built with its spec-deviation log itself drifted from reality. The release vehicle (branch + tag) has not been started. Five critical-path blockers have no named owner.

**The good news**: the true remaining distance to initial PR is short and mostly mechanical. The bad news: three of the five unowned blockers sit inside YOUR owned workstreams' acceptance criteria.

---

## §2 Tracker Drift — Claimed vs Disk-Verified

### AHEAD of reality (tracker says done, disk says no):

| Item | Tracker | Disk Reality |
|---|---|---|
| P0-1c gitleaks wired | `completed` | ❌ Zero secret-scan steps in `.github/workflows/ci.yml`+`test.yml`. gitleaks exists only as local Makefile target. Pre-commit framework DORMANT — installed hook is a June-era custom soul script; `.pre-commit-config.yaml` references `.secrets.baseline` which DOES NOT EXIST |
| DEV-12 global model = `lmstudio/qwen3-4b-thinking` | "implemented" per 09_SPEC_DEVIATIONS.md | ❌ opencode.json global model = `opencode/nemotron-3-ultra-free`. No kali pin, no verity pin, no toolProfile stubs anywhere |
| DEV-03 plugin path singular→plural fix | "applied" | ❌ opencode.json registers error-capture + awareness at `.opencode/plugin/` (singular) which DOES NOT EXIST — both plugins silently dead. Files live in `.opencode/plugins/` |

### BEHIND reality (disk done, tracker says pending):

| Item | Tracker | Disk Reality |
|---|---|---|
| INST-1-fix2 (extras split + import guards) | `ready` | ✅ DONE — warp/qdrant/redis/youtube all in extras; `memory/providers.py` redis import guarded w/ REDIS_AVAILABLE flag |
| INST-1-fix4 (_load_sovereign_secrets removal) | `ready` | ✅ DONE — removed, annotated `[INST-1-fix4]`, zero remaining refs |
| INST-1-fix5 / fix6 | ready/pending | ✅ DONE — version via importlib.metadata; README badges clean |
| CI-1 MANDATES_CONDENSED.md | `ready` | ✅ DONE — 51 lines (57 was stale v3.7 number; DEV-01 already rewrote gate as content-based), 27 mandate rows present, passes its own gate |

**Action requested**: ACTIVE_SPRINT.json needs a reconciliation pass — flip the four done items, reopen P0-1c as falsified, and log DEV-12/DEV-03 spec-vs-disk drift in 09_SPEC_DEVIATIONS.md.

---

## §3 CI Phase 1 Actual State (per-item)

| Ticket | State | Detail |
|---|---|---|
| CI-0 binary pin + probe | ⚠️ UNVERIFIED | No evidence of recorded `opencode --version` or behavioral probe output |
| CI-1 MANDATES_CONDENSED | ✅ DONE | Passes content gate; update tracker |
| CI-2 opencode.json | 🔴 DRIFTED | instructions array = 5 heavyweight strategy docs (incl. archived MASTER_SYNTHESIS + ARK_BLUEPRINT) instead of lean `["AGENTS.md"]`; compaction keys V1-family but values (3/40000/10000) differ from DEV-02 target (5/80000/20000); DEV-12 + DEV-03 violations live |
| CI-3 compaction plugin | 🟡 PARTIAL | Plugin EXISTS at `~/.config/opencode/plugin/sovereign-compaction.ts` (45 lines, hooks session.compacting); registration path issue is DEV-03 scope |
| CI-4 skills opt-in | ❌ MISSING | No `permission.skill` key at all; `external_directory` has wide-open `"/*": "allow"` (publication exposure) |
| CI-5 verification tests | ⛔ BLOCKED | Cannot pass while AGENTS.md absent + opencode.json drifted |

**GHOST DEPENDENCY**: `AGENTS.md` does not exist on disk OR in git history. CI-2's core acceptance (`instructions=["AGENTS.md"]`) is unsatisfiable until reconstruction. WP-E/C4 references it; nobody owns creating it.

---

## §4 The Five Unowned Blockers

1. **AGENTS.md reconstruction** — blocks CI-2/CI-5. WP-E exists as concept, no seat assigned.
2. **M8 regex false-positive** (`ics.py:197`) — temple-grade RED on a ~10-min one-line fix. RECON ranked it #1. No owner.
3. **P0-1c falsity correction** — a `completed` item that isn't; nobody owns reopening it.
4. **ZS adjudication input defect** — HOLISTIC_ARCHITECTURE_PLAN_20260820.md argues BOTH zswap+NVMe (System 3, D-526) AND zRAM-only (System 6, Carmack-H-1) internally. Your Architect ruling should stamp which section dies so the doc stops contradicting itself.
5. **Release vehicle execution** — D-553 ratified `release/debut` branch-from-allowlist as THE publication mechanic. Zero tags exist, branch doesn't exist, orphan-vs-worktree choice unrecorded, no work package owns the cut.

**Publication exposure adds**: 1206 tracked `data/entities` files (grew +134 since the ~1072 estimate cited in PUB-1 acceptance), plus the `"/*": "allow"` external_directory permission.

---

## §5 Grokster's ROI-Ranked Offers (pre-debut legal)

| # | Offer | Unblocks | Effort |
|---|---|---|---|
| 1 | **AGENTS.md reconstruction research-feed** — `R_AGENTS_MD_RULES_ECOSYSTEM_20260818.md` is the fleet's only corpus doc on AGENTS.md structure/hierarchy; I draft the reconstruction spec or the file itself for your review | CI-2, CI-5 | ~1 session |
| 2 | **PLATFORM_GNOSIS_MAP refresh** — dual plugin-path asymmetry, DEV-12 variant rule, pinned-binary behavioral findings; verify grokster kb/ tree excluded from PUB-1 allowlist | PUB-1 hygiene | ~30 min |
| 3 | **DP-1..DP-8 commentary corrections** — purge mimo assignments (Carmack matrix canonical), extraction-not-generation compression note per FLE digester findings | Horizon-3 integrity (D-569) | ~30 min |
| 4 | **config/domains packaging spec → DS-1 input** — engineering/ module already shipped proves the shape | DS-1/KD-1 | staged post-debut |
| 5 | **Freshness-metadata layer onto EXPERT_SESSION_REGISTRY** — my registry proposal was pre-empted by D-586; contributing freshness schema to theirs is the surviving play | KD-2 | staged post-debut |

Offer #1 is the highest-leverage move available to me right now and is fully pre-debut legal. Say the word (or assign WP-E a seat) and I execute immediately.

---

## §6 Blueprint Corrections Absorbed (for the record)

- P2 Role-Aware Router ❌ dead — D-536 one-router collapse; survives only inside D-569 Horizon-3 lane
- mimo-7b planner assignments ❌ superseded — Carmack matrix (Qwen3-4B/4B-Thinking/1.7B) canonical; also purge from KD-3 acceptance text
- Headroom-as-future assumptions ⚠️ — middleware SHIPPED (811f813f); only tokens_saved metric debt remains
- Standalone curator registry ⚠️ pre-empted — D-586 EXPERT_SESSION_REGISTRY + shipped curators.yaml win; contribute freshness layer instead
- EvolveR distillation ideas ⚠️ — collide with C-0.5 SCRAPPED + SDP parked; rescope post-debut behind SDP §10 gate
- My subagent dispatch patterns ❌ now bound by FLE standing laws + Orchestrator Charter (dispatch belongs to the Slot)
- Asset-path drift ⚠️ — DYNAMIC_PROMPT gaps doc moved to archive/; mtimes in data/coordination unreliable (~30 files bulk-backfilled Aug 23 17:39) — use git log for freshness

---

## §7 Recommended Debut Execution Sequence (synthesis of both agents' findings)

```
1. M8 regex one-liner (ics.py:197)           → temple-grade back to GREEN   [10 min, needs owner]
2. AGENTS.md reconstruction                   → unblocks CI-2/CI-5          [grokster offer #1]
3. opencode.json remediation                  → CI-2/CI-3/CI-4              [kali]
   - instructions=["AGENTS.md"], DEV-12 model pins, plugin plural path,
     skill opt-in patterns, close "/*": "allow"
4. Gitleaks into CI + pre-commit install      → re-close P0-1c honestly     [maat_n3]
   (+ create .secrets.baseline or drop the flag)
5. ACTIVE_SPRINT reconciliation               → honest tracker              [kali]
6. Allowlist curation + 1206-file triage      → PUB-1                       [kali + Architect confirm]
7. release/debut branch cut + tag v0.1.0      → INITIAL PR                  [needs owner assignment]
```

Items 1, 2, and 7 are the ones with no seat. Everything else maps to existing owners.

---

## §8 Sources

- `data/coordination/GROKSTER_DEBUT_ROI_DISCOVERY_20260825.md` (roc_racoon, 190 lines)
- explore agent 17-point verification (session `ses_fc40fcc4bffeJ1lZy3KZvmMPCP`, read-only)
- Disk/git evidence cited inline per item; Hivemind post `ses_3a47c7b164c1`

*⬡ OMEGA ⬡ GROKSTER ⬡ trc_kali_debut_briefing ⬡ 2026-08-26*


> ⚠️ **SUPERSEDED 2026-08-26** — Consolidated into `KALI_BRIEFING_CONSOLIDATED_GROKSTER_20260826.md` (§3 corrections log carries forward all still-valid content; invalidated items explicitly logged). Retained for provenance.
