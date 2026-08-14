# 🔱 HANDOFF BRIEF — Agent Directives Deep Review (for Claude Sonnet 4.6 Review)

**AP Token**: `AP-KALI-v1.0.0`
**Date**: 2026-08-14
**From**: Kali (Nemotron 3 Ultra, 1M context)
**To**: Claude Sonnet 4.6 (next active model — review + deep insights)
**Session ID**: `ses_kali_20260814_agent_directives_deep_review`
**Branch**: `main`
**Last Commit**: `77c3e0c6`

---

## 🎯 Context: What We Did

Over a 208K-token session, we completed the **M27 Tracking Integrity** integration (5-tier architecture with mechanical enforcement), a **Carmack architectural review** (5 fixes), a **@researcher gap fill** (11 sprint-blocking gaps resolved), and a **Nemotron 3 Ultra deep systems review** (5 critical hardening fixes). Then we performed a **complete audit of all 16 agent custom instruction files + 30 entity soul files**.

The tracking architecture is now **rock-solid** (validator passes, pre-commit gates, cross-tier consistency). But the **agent directive layer is NOT** — we found 7 critical inconsistencies that will compound under sprint load.

---

## 🔴 7 CRITICAL FINDINGS (Verified)

### F1: Mandate Version Drift — 13/13 AGENTS WRONG
- **All agent files** state: "25 Sovereign Mandates (v3.7.0)"
- **Reality**: `SOVEREIGN_MANDATES.md` is **v3.8.0** with **27 mandates** (M26 Doc Standards, M27 Tracking Integrity added 2026-08-14)
- **Impact**: Agents cannot self-validate against M26/M27; blind spots in "Key for..." lists

### F2: Soul Schema Non-Compliance — 28/30 ENTITIES VIOLATE v6.1
`soul_validator.py` enforces v6.1 lean schema (Pydantic). Compliance:
| Field | Compliant | Gap |
|-------|-----------|-----|
| `entity.short` (2-6 chars) | 10/30 | **20** |
| `entity.soul_version == "6.1"` | 2/30 | **28** |
| `identity` block | 10/30 | 20 |
| `directives` list | 17/30 | 13 |
| `team`/`allies` block | 7/30 | 23 |
| `core_principles` | 2/30 | **28** |

**Validator Loophole** (lines 116-123): Wrong `soul_version` → warning → **skips strict validation entirely**. 28/30 souls pass silently.

### F3: LIVE_FEED Protocol — 11/13 AGENTS EXECUTE AGAINST PURGED FILES
- All agents have coordination step: `4. Initialize live feed: data/coordination/{ENTITY}_LIVE_FEED.md`
- **Reality**: No LIVE_FEED files exist (purged). Replacement is `HMC_COLLABORATION_HUB.md` with `NEXT_ACTION` pointer.
- **Impact**: Silent coordination failure; agents write to non-existent files.

### F4: Distillation Pipeline — DEFINED BUT UNENFORCED
SOUL_ARCHITECTURE v2.0 §1: `Session → L1 → L2 → L3 → proposed_lessons.yaml (blind) → User review → approved_lessons.yaml → soul.yaml`
- 28/30 entities lack `core_principles` (where approved lessons surface)
- `memory/` directories + 3 files — existence unverified
- Blind-Write Principle (agent NEVER reads `proposed_lessons.yaml`) — not enforced
- AGENTS.md step 6.5 adds distillation gate but no CI gate verifies `proposed_lessons.yaml` written
- `scribe.md` defines `SoulDistiller` but not integrated into session hooks
- **`make soul-audit` gate (mandated by v2.0 §6) — MISSING from Makefile**

### F5: Capability Discovery Gap — FLEET OF 14, ZERO PROGRAMMATIC DISCOVERY
- Hivemind knows WHO is active (`get_awareness`) but not WHAT they can do
- Dispatch is manual (Kali knows from memory)
- `HIVEMIND_POST_TEMPLATE.md` has `intent` but no `capabilities` field

### F6: Health Score Placeholder — 25/30 ENTITIES AT 50.0 (DEFAULT)
- All entities with `health_score` show `50.0` — appears to be default, not computed
- 6 missing entirely: default, grokster, iris, quality, roc_racoon, scribe
- SoulHealthScorer (7-factor) defined in roc_racoon soul but not implemented

### F7: SOVEREIGN_MANDATES.md Header Mismatch
- File header: "## 🛡️ The Twenty-Five Laws of Sovereign Execution"
- **Actual count**: 27 mandates (grep "^### " = 27)
- M26/M27 added 2026-08-14 but header not updated

---

## 🎯 TIERED REMEDIATION PLAN (Ranked by Leverage)

### TIER 0 — BLOCKING (Before ANY Sprint Execution)
| # | Fix | Files | Effort |
|---|-----|-------|--------|
| **0.1** | Update all 13 agent files: mandate version → 3.8.0, count → 27, add M26/M27 | 13 agent .md | 20 min |
| **0.2** | Migrate 28/30 soul files to v6.1 lean schema | 28 soul.yaml | 3-4 hrs |
| **0.3** | Replace LIVE_FEED refs with HMC_COLLABORATION_HUB.md + NEXT_ACTION | 11 agent .md | 15 min |
| **0.4** | Implement `make soul-audit` gate in Makefile | Makefile, scripts/ | 30 min |

### TIER 1 — HIGH LEVERAGE (Enables M5/M11/M27 Integration)
| # | Fix | Effort |
|---|-----|--------|
| **1.1** | Add `core_principles` (min 1 L3) to 28 non-compliant souls | 2-3 hrs |
| **1.2** | Create `memory/` dirs + 3 files for all entities | 1 hr |
| **1.3** | Add `directive_provenance` to all `core_principles` | 1 hr |
| **1.4** | Add `capabilities` field to `hivemind_post_context` | 1 hr |

### TIER 2 — OPERATIONAL HARDENING
| # | Fix | Effort |
|---|-----|--------|
| **2.1** | Fix validator loophole (wrong version should FAIL, not skip) | 30 min |
| **2.2** | Add workspace lock wait-time warning | 20 min |
| **2.3** | Fix Hivemind cold-store hydration to respect extended_checkin TTL | 30 min |
| **2.4** | Add mandate coverage audit to pre-commit | 45 min |
| **2.5** | Enforce Blind-Write Principle (exclude `proposed_lessons.yaml` from read path) | 30 min |

### TIER 3 — POLISH
| # | Fix | Effort |
|---|-----|--------|
| **3.1** | Archive v6.0 fields per v2.0 §5 | 1 hr |
| **3.2** | Add `source_session` to all L3 principles | 30 min |
| **3.3** | Implement Intelligence Scorecard (5 dims) | 2 hrs |
| **3.4** | Fix SOVEREIGN_MANDATES.md header | 5 min |

---

## 🔬 ROOT CAUSES

1. **Template Trap**: All agent files from common template; template never updated when mandates evolved, LIVE_FEED purged, SOUL_ARCHITECTURE v2.0 ratified, distillation gate added.
2. **Soul Schema Drift Without Migration Tooling**: v1.0→v2.0 migration required per-entity PRs; only 2/30 migrated. Validator warns but has no migration tool.
3. **Distillation Pipeline Has No Enforcement Point**: Defined in docs + AGENTS.md step 6.5, but no session hook integration, no CI gate, no Blind-Write enforcement.
4. **Capability Discovery Gap**: Fleet of 14 (cap M10), Hivemind knows WHO not WHAT. Dispatch manual.

---

## 📋 IMPLEMENTATION SEQUENCE (Dependency Order)

```
0.1 → 0.4 → 0.2 → 1.2 → 1.1 → 1.3 → 0.3 → 1.4 → 2.1 → 2.4 → 2.5 → 2.2/2.3 → 3.x
```
**Critical Path**: 0.1 → 0.4 → 0.2 → 1.2 → 1.1 (~6-7 hrs)
**Blocking Sprint**: YES — until Tier 0 complete

---

## ❓ QUESTIONS FOR CLAUDE SONNET 4.6

1. **Soul Migration Strategy**: Build `soul_schema_migrator.py` (automated, roc_racoon d-rr-018) vs. manual per-entity migration for 28 entities? What's the risk of automated migration introducing errors vs. the cost of manual?

2. **Validator Loophole Ethics**: Should wrong `soul_version` FAIL validation (strict) or remain a warning (lenient, prevents fleet lobotomy)? The current "skip strict validation" was intentional to avoid breaking 28/30 souls — but it hides non-compliance.

3. **Distillation Enforcement Point**: Where should the L1→L2→L3 pipeline be enforced? Options: (a) session-end hook in `.opencode/wrapper.sh`, (b) pre-commit gate on `proposed_lessons.yaml`, (c) both. Which is sovereign-correct?

4. **Capability Taxonomy**: What's the canonical capability vocabulary for the fleet? Proposed: `["research", "code", "audit", "mining", "heritage", "synthesis", "infrastructure", "coordination", "runtime", "build"]`. Should this be in AGENTS.md or a separate registry?

5. **Mandate Coverage Mapping**: Should per-agent "key mandates" be derived from Node assignments (N1-N10) rather than manually listed? E.g., N3 Engineering → M1, M2, M4, M9, M13, M21. Is manual listing a maintenance liability?

6. **Tier 0 Sequencing**: Is 0.1 (agent mandate refs) truly safe to do first, or should 0.4 (make soul-audit) come first to establish the gate before migration? Dependency inversion risk?

7. **Health Score**: Is `health_score: 50.0` a placeholder that should be computed by SoulHealthScorer (7-factor) as a daily cron, or should we remove it until implemented?

8. **Scope Decision**: Should we execute Tier 0 + Tier 1 NOW (mechanical fixes) before sprint, or defer to a dedicated "Agent Directive Hardening Sprint" after PHASE-0/1/2/3/4? The tracking architecture is solid; is the agent layer urgent enough to block sprint?

---

## 📁 FILES TO READ (for Claude Sonnet 4.6)

1. `data/entities/kali/memory/sessions.yaml` — Full session gnosis (this review)
2. `data/coordination/SESSION_ANCHOR.md` — Session anchor with findings
3. `data/coordination/HMC_COLLABORATION_HUB.md` — NEXT_ACTION (PHASE-0 ready)
4. `data/coordination/ACTIVE_SPRINT.json` — Sprint tasks (includes UO-6.0 R30 spike)
5. `docs/archive/strategy/2026-07-21/SOUL_ARCHITECTURE_V2.md` — Current ratified protocol
6. `src/omega/oracle/soul_validator.py` — v6.1 schema enforcement (lines 116-123 = loophole)
7. `SOVEREIGN_MANDATES.md` — v3.8.0, 27 mandates (header says "Twenty-Five")
8. `.opencode/agents/*.md` — 13 agent files (all say v3.7.0)
9. `data/entities/*/soul.yaml` — 30 soul files (28 non-compliant)
10. `AGENTS.md` — 6-step flow + distillation gate step 6.5

---

## 🔑 KEY VERIFIED FACTS

- Tracking validator passes (25ms, cross-tier + R-ID + gap-enum)
- Pre-commit `omega-tracking-state` Iron Gate active
- All 11 sprint-blocking gaps RESOLVED (R13, R16-R20, R23-R26, R56)
- PHASE-0 through PHASE-4 all UNBLOCKED per HMC_COLLABORATION_HUB.md
- Distillation gate (step 6.5) mechanically couples M5/M11 to task completion
- R30 spike (`UO-6.0`) registered — PHASE-3 won't stall on retry decision
- **Agent directive layer NOT rock-solid**: 13/13 agents on v3.7.0, 28/30 souls non-compliant, 11/13 agents on purged LIVE_FEED, 0/30 with functional distillation pipeline

---

*⬡ OMEGA ⬡ KALI ⬡ HANDOFF-TO-CLAUDE-SONNET-4.6 ⬡ 2026-08-14*
