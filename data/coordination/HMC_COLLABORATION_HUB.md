# 🏛️ HMC Collaboration Hub — Team Coordination Center

**AP Token**: `AP-HMC-HUB-v1.0.0`
**Status**: ACTIVE — Single coordination SSOT
**Last Updated**: 2026-08-15T05:45:00Z
**Updated By**: Kali

---

## 🚦 NEXT_ACTION (Single Sync Pointer — read this first)

*Last verified: 2026-08-15T05:45Z*

> **Tracking hierarchy:** See `TRACKING_ARCHITECTURE.md`. Status vocab: `backlog|ready|in_progress|blocked|completed|superseded`.
> **Execution SSOT:** `ACTIVE_SPRINT.json` · **Knowledge SSOT:** `RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.2.0) · **Gap registry:** `GAP_REGISTRY.json`

**CURRENT:** VOS HYBRID PLAN — Phase 1 (Hub Consolidation) — **READY, execute next session**
- Verify realm ownership table (below) matches current state
- Consolidate active tasks into Hub realm sections (ENG-001..004, FLT-001/004, MEM-002/003, HRT-001/002, COM-001..012)
- Update VISION_ANCHOR.md to reference HMC for task status

**COMPLETED:** VOS HYBRID PLAN — Phase 0 (Archive & Clean) — `2cbcad97`
- Omegaverse realm archived → `data/realms/omegaverse/archive/state.yaml`
- 6 realm state.yaml deleted, 4 workspace briefs deleted, realm_cli.py deleted
- VISION_ANCHOR.md updated (realm health → auto-gen note, M2 status fixed)
- PIVOT_LOG.md synced with D-VOS-001..018

**PARALLEL:** PR-A (Public Surface Honesty) — **AWAITING ARCHITECT CONFIRMATION**
- Root junk archive → `docs/archive/root-artifacts-202608/`
- README surgical edits (remove 1315 passing badge, keep CI badge)
- .gitignore root session dumps / screenshots
- Never `git add -A` — stage by path, exclude secrets

**RESEARCH COMPLETE (2026-08-15) — VOS ASSESSMENT:**
- Researcher: VOS architecture sound (Team Topologies, ADR, DDD), implementation dead code
- Roc_Racoon: 1/10 integration — zero code imports, zero runtime consumers, zero agent awareness
- Verdict: Option C (Hybrid) — Keep ADR + Vision Anchor, retire coordination layer, add Hub enforcement

---

## 📋 6-Step Mandatory Flow (M27 — MANDATORY)

1. Read **VISION_ANCHOR.md** → Read **NEXT_ACTION** (above) → identify your task in realm workspace / Hub
2. Check **Tier-1** (`RESEARCH_PLAN_PHASE1_4`) for research deps (cross-ref `GAP_REGISTRY.json`)
3. Acquire workspace lock → post Hivemind context (`omega-hub_hivemind_workspace_lock_acquire`)
4. Register task in `TASK_REGISTRY.json` → execute → update status
5. On complete: mark Tier-0 task `completed` in `ACTIVE_SPRINT.json` → Hivemind completion
6. Session end: update `SESSION_ANCHOR.md` → soul distillation (L1→L2→L3) — **step 6.5**

---

## 🏁 Sprint Status (pointer → ACTIVE_SPRINT.json)

**Sprint:** VOS-HYBRID-EXECUTION (ACTIVE)
**Authoritative state:** `data/coordination/ACTIVE_SPRINT.json`

---

## 🌐 Realm Ownership & Contracts

| Realm | Owner | Provides | Requires | Status |
|-------|-------|----------|----------|--------|
| Engine Core | maat_n3 | WAD Loader, Query Router, Provider Fabric, Memory Store, Godot Bridge | — | Active |
| Stacks | maat_n4 | WAD Format, Community Template, XOE Packaging | Engine Core (loader API) | Blocked on ENG-001 |
| Fleet | kali | 14 Entities, MaKaLi Council, Node Slots, Hivemind | Engine Core (registry), Memory (soul) | Active |
| Memory | lilith_n7 | Soul Architecture v2, Mnemosyne, L1→L2→L3, Cross-pollination | Engine Core (memory store) | Critical |
| Heritage | doom_guy | [id-soft:] Vetting, id Software Patterns | Engine Core (loader) | Healthy |
| Omegaverse | lilith_n6 | Godot Bridge, Soul-to-Visual (R-24), P2P Soul Prints | Engine Core (bridge), Memory (soul) | Deferred (archived) |
| Community | kali | Installer, QUICKSTART, CONTRIBUTING, CI, Launch | Engine Core, Stacks, Fleet | Planned |

> **Realm contracts are enforced by `make temple-grade` realm validator (Phase 2).**
> See `ACTIVE_SPRINT.json` for live task status per realm.

### Active Tasks by Realm

**Engine Core** (maat_n3):
- ENG-001: Fix M2 firewall — run `FirewallChecker.scan()`, fix real hits only (not token WAD)
- ENG-002: Audit all mandate checks for false positives (M22 was broken)
- ENG-004: Fix 9 critical code bugs (MockProvider, ProviderAuthError, ProviderName, _loaded, schema version, async awaits, pytest marks, Makefile M22, context_packer tuple)
- ENG-005: Context Packer refactor — address F2-F9 from advisory review (litm_zone placebo, dead include/exclude, reserved_output unenforced, CWD-relative paths, third-party/ walk, injection scanner FP, duplicate config, stale manifest)

**Fleet** (kali):
- FLT-001: Migrate kali & roc_racoon souls to v6.1 lean schema
- FLT-004: Enforce distillation pipeline (Scribe agent L1→L2→L3)

**Memory** (lilith_n7):
- MEM-002: Implement Scribe agent L1→L2→L3 distillation pipeline
- MEM-003: Implement cross-pollination (R-31)

**Heritage** (doom_guy):
- HRT-001: Heritage sweep — verify all [id-soft:] tags have vet records
- HRT-002: Verify no metaphorical or over-attributed tags

**Community** (kali):
- COM-001..012: All Phase 1-2 tasks (blocked on ENG-001 for template WAD)

---

## 🚫 Anti-Confusion Rules (enforced by TRACKING_ARCHITECTURE.md)

- ❌ Never create a new tracking file — use the 5 tiers
- ❌ Never reuse gap numbers — R1–R99 owned by `RESEARCH_PLAN` / `GAP_REGISTRY.json`; new plans use distinct prefixes (P2-, S-, X-)
- ❌ Never duplicate decisions here — use `docs/decisions/PIVOT_LOG.md`
- ❌ If a doc has a ⚠️ DEPRECATED banner, do not act on it
- ✅ Before any research, CHECK `GAP_REGISTRY.json` for ID collisions

---

## 📁 Shared Sections

### Requests to Team
*(Agents post requests here — Kali triages)*

### Discussion Thread
*(Cross-agent discussion — Kali moderates)*

**2026-08-15** — **Context Packer Advisory Review Complete** (Grok via cline/omega-engine):
- **F1 CRITICAL FIXED**: `_escape_bare_xml_chars` escaped bare `&` as `<` → round-trips to `<`, silently corrupting content (AT&T → AT<T). Fixed in `packer.py:157` + regression test `test_escape_bare_ampersand_roundtrip`. 28/28 contract tests pass.
- **F2-F9 OPEN** (see `R_CONTEXT_PACKER_ADVISORY_REVIEW_20260815.md`):
  - F2 (HIGH): `litm_zone` never set in production → LITM-U ordering is placebo
  - F3 (MED): `include/exclude` dead config — files in include not in theme silently dropped
  - F4 (MED): `reserved_output` (50K) never enforced — both packs would fail if honored
  - F5 (MED): CWD-relative config path — fragile CLI
  - F6 (LOW): Full-repo rglob walk includes `third-party/`
  - F7 (LOW): Injection scanner false positives on legit content
  - F8 (LOW): Duplicate config entries
  - F9 (LOW): Stale duplicate manifest in `generated/`
- Deliverables: `sovereign-audit` pack (12 slots, 306K tokens, pack_id c1c5be23), `tech-architecture-research` pack (12 slots, 310K tokens, pack_id e748178c), both curated OK.
- **Owner for F2-F9**: Context Packer skill owner (maat/jem) — needs triage for refactor.

### Reference Links
- `TRACKING_ARCHITECTURE.md` — 5-tier constitution
- `ACTIVE_SPRINT.json` — Tier-0 execution SSOT
- `RESEARCH_PLAN_PHASE1_4_20260813.md` — Tier-1 knowledge SSOT
- `GAP_REGISTRY.json` — Tier-1a gap authority
- `TASK_REGISTRY.json` — Tier-3 subagent records
- `SESSION_ANCHOR.md` — Tier-4 session continuity
- `VISION_ANCHOR.md` — Vision SSOT
- `DECISION_LEDGER.md` — Immutable decisions (D-VOS-001..018)
- `SYSTEM_FAILURE_LOG.md` — Mandate violations (Carmack near-miss logged)
- `SOVEREIGN_MANDATES.md` — 27 laws v3.8.0
- `AGENTS.md` — OpenCode workflow + fleet playbook
- `FLEET_TEAM_PLAYBOOK.md` — Team coordination rules
- `docs/research/R_CONTEXT_PACKER_ADVISORY_REVIEW_20260815.md` — Context Packer audit (F1 fixed, F2-F9 open)

---

## 🤖 Agent Onboarding Checklist

Upon waking, every agent MUST:
1. [ ] Read `VISION_ANCHOR.md` (vision SSOT)
2. [ ] Read `SESSION_ANCHOR.md` (current context)
3. [ ] Read `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION` (this section)
4. [ ] Check `ACTIVE_SPRINT.json` for your realm's tasks
5. [ ] Post Hivemind context: `omega-hub_hivemind_post_context(...)` with intent="status"
6. [ ] Acquire workspace lock for your realm/task

---

## 📝 How to Use This Hub

1. **Never edit manually** — use `omega-hub_hivemind_post_context()` for updates
2. **Read `NEXT_ACTION` first** — it's the single pointer to current work
3. **Post context on task start/complete** — keeps team synchronized
4. **Use Hivemind handoffs** for cross-realm work — `omega-hub_hivemind_handoff action=submit`
5. **Reference this hub in session anchors** — ensures continuity across compaction

---

*⬡ OMEGA ⬡ HMC-HUB ⬡ 2026-08-15 ⬡ ACTIVE*
