# AGENT/NODE SYSTEM DISCOVERY MAP — Full Context Hydration
**AP Token**: `AP-NODE-SYSTEM-DISCOVERY-v1.0.0`
**Date**: 2026-08-22
**Author**: researcher (Sovereign Researcher)
**Mission**: Full-spectrum local discovery of agent & Node strategy/protocol corpus — enable deepening/enhancement work
**Method**: Direct read of 16 core artifacts (no subagent summaries). Every claim traceable to file read this session.

---

## §1 The Five-Layer Architecture (as verified on disk)

```
L0 ENGINE SLOTS (immutable core)
   src/omega/ics.py:64-81 ROLE_CONSTANTS — 16 slots:
   GRAND_OVERSIGHT · BUILD_OVERSOUL · RUNTIME_OVERSOUL · N1-N10 ·
   MESSENGER_BRIDGE(Iris) · MAKALI_COUNCIL · CONTAINING_FIELD(Sophia)
        ↓ mapped at runtime by
L1 WAD CONTENT (M2 Firewall: engine=slots, WAD=entities)
   config/wads/_omega_default/
   ├── entities/dispatch.yaml   19 entity→role mappings (dispatch_registry.py mtime cache)
   ├── roles.yaml               N1-N10 name/model/temperature/domains
   ├── hierarchy.yaml           Sophia(Field)→Kali(Founder)→Ma'at(CTO,N1-N5)/Lilith(CISO,N6-N10)→10 keepers
   └── entities.yaml            entity registry
        ↓ instantiated as
L2 OPENCODE AGENT FILES (.opencode/agents/*.md — M10 cap 14)
   Active 13: kali maat lilith makali doom_guy roc_racoon researcher jem
              john_carmack grokster verity scribe node
   Deprecated: build.md · Archived: archive/grok_cli.md
   node.md = generic slot-parameterized agent (--slot NX, reads roles.yaml)
        ↓ running as
L3 SESSION SYSTEMS (the living layer)
   ├── Node Expert Sessions (D-586): 10 persistent KB sessions under Ma'at/Lilith;
   │     genesis→dormant→paged; ANY agent pages ANY Node; all dormant since 2026-08-21 genesis
   ├── Conversational Subagents v1.0.0: task_id continuation, R1-R13,
   │     turn-boundary transaction model (B1-B15 evidence)
   └── Interactive-origin sessions: study-only until post-debut mail plugin (E12)
        ↓ governed by
L4 PROTOCOL STACK (behavior law)
   Dispatch:    SUBAGENT_DISPATCH_PROTOCOL v3 (HandoffPacket, inline-context lesson,
                decision tree §11, L2.5 Dual-Artifact §12)
   Engage:      CONVERSATIONAL_SUBAGENT_PROTOCOL v1.0.0 (R1-R13)
   Recover:     STALLED_SUBAGENT_RECOVERY v2.0.0 (G1-G3 multi-file doctrine)
   Resume:      STRP v1.0.0 (mandatory task_ids, standardized format)
   Onboard:     NODE_ONBOARDING_PROTOCOL v1.0.0 (G→M→A→D→W→C→X→E, MR-1..14, consultable bar)
   Coordinate:  HIVEMIND_PROTOCOL v1.3.0 + FLEET_TEAM_PLAYBOOK v1.1.0
   Provenance:  ICS-S headers (PP-4 [NODE] tag + P5 session_id — IMPLEMENTED 2026-08-22, 16 tests)
        ↓ feeding
L5 KNOWLEDGE LAYER (compounding assets)
   config/domains/curators.yaml — 13 registered domains, curator-write governance
   Node KBs/DOMAIN_INDEXes (N7 complete: 84KB KB, consultable)
   souls/proposed_lessons (L1→L2→L3, [N_X]-tagged) · session_gnosis snapshots
   Tracking: ACTIVE_SPRINT.json(T0) · GAP_REGISTRY · TASK_REGISTRY(T3) · INJECTION_LEDGER
```

## §2 Protocol Lineage (failure-derived — each generation bought by incidents)

| Gen | Doc | Incident that bought it |
|-----|-----|------------------------|
| 1 | SUBAGENT_DISPATCH §0 | 3× empty Jem dispatches → inline-context mandatory (80% failure cause) |
| 2 | STRP v1.0.0 | Lost subagent state → mandatory task_ids |
| 3 | STALLED_RECOVERY v2.0 | Multi-file stalls 2/2 → G1 manifest/G2 recovery/G3 audit |
| 4 | CONV_SUBAGENT R1-R13 | Relay experiments B1-B15 → queueing semantics, DB-audit-on-empty |
| 5 | NODE_ONBOARDING MR-1..14 | N7 genesis arc → announced-intent≠work, append-only, evidence-class labels |

Coherence check: **STRONG**. All five generations enforce file-first, same-task_id recovery, disk-truth-over-replies, terminus declarations. No contradictions found between generations.

## §3 Drift Register (verified findings — enhancement raw material)

| # | Finding | Evidence | Severity |
|---|---------|----------|----------|
| DR-1 | **MANIFEST.md stale (v4.0.0, 2026-06-04)** — references `.opencode/modes/` dir, quality.md, jem_discovery/synthesis/verification.md, plan.md; none exist. Fleet composition/count wrong. | MANIFEST §2 vs actual tree listing | HIGH |
| DR-2 | **Dual Node architecture unreconciled** — engine-layer (`node --slot NX` + roles.yaml + data/entities/p1..p10 workspaces) vs session-layer (D-586 overseer-run sessions). roles.yaml N10="stress testing/chaos" vs charter N10="test honesty/contract tests" — ALREADY DIVERGED. p1-p10 workspace existence unverified. | LATTICE §4.3,§9 vs PLAN §4 | HIGH |
| DR-3 | **Sophia escalation stale** — OVERSIGHT_HIERARCHY routes Sovereign Gaps to Sophia; OMEGA_ENGINE says MaKaLi Apex Mind replaced Sophia. | OVERSIGHT_HIERARCHY §3 vs OMEGA_ENGINE §3 | MED |
| DR-4 | **HIVEMIND_PROTOCOL v1.3.0 predates all session systems** (2026-06-25) — no Node paging, no CSP, no injection ledger; live-feed section deprecated by Playbook §4.1 but protocol not updated. | HIVEMIND header date vs Playbook §4.1 | MED |
| DR-5 | **Dispatch capability registry mismatch** — §3 lists 11 agents incl. `pillar` type; current fleet = 13 active, no pillar agent file. §11 decision tree lacks the D-586 page format (`task(task_id=<session_id>, subagent_type=<overseer>)`). | DISPATCH §3,§11 vs PLAN §3 | MED |
| DR-6 | **PP-4/P5 status contradiction** — PLAN §6 marks PP-4 "Deferred per Architect — implement with P5"; ICS_SYSTEM documents BOTH IMPLEMENTED 2026-08-22 with 16 tests. | PLAN §6 PP-4 row vs ICS_SYSTEM §Node Designation | MED |
| DR-7 | **roles.yaml models stale** — qwen3-0.6b for N10, qwen3-1.7b elsewhere; predates D-585 canonical matrix (Qwen3-4B planner / 4B-Thinking executor / 1.7B critic). | roles.yaml vs N6 charter D-585 | LOW |
| DR-8 | **curators.yaml gaps** — AFFINITY_PRESETS schema references mimo-7b-rl-q4_k_m (verify in registry); domain_loader.py missing → governance is spec-only. | curators.yaml §hooks vs disk find | LOW |
| DR-9 | **Agent count reconciliation** — M10 cap 14; build.md deprecated-but-present; MANIFEST claims 14; OMEGA_ENGINE claims 12; actual active = 13. | three docs vs tree | LOW |
| DR-10 | **Four dispatch/recovery docs without layering map** — DISPATCH(launch)/CSP(engage)/STALLED(recover)/STRP(resume) overlap; no single "which protocol when" table. | corpus-wide | LOW |
| DR-11 | **opencode.json lacks CI-2 changes** — Context Injection Phase 1 (instructions array, compaction buffer, per-agent model routing, plugin registration) not yet landed; only Antigravity provider block present. | opencode.json vs ACTIVE_SPRINT CI-2 | INFO |
| DR-12 | **KD/DS tracker drift** — ACTIVE_SPRINT carries only DOCUMENTATION-SYSTEM; manual carries both DS and KD (KD-1..KD-3 unregistered at Tier-0). | Roc T2 finding | INFO |

## §4 Enhancement Seams (prioritized — where deepening pays most)

### HIGH
- **E-1 Unify the dual Node architecture**: make PLAN §4 charters the SSOT for Node domains; regenerate roles.yaml FROM charters (or replace with pointer); rule on `node --slot NX` fate (deprecate vs fallback-executor role); verify/retire p1-p10 workspaces. Kills DR-2/DR-7.
- **E-2 Ratify N11 evaluator + N12 curator**: charters fully drafted in NODE_GAP_SYNTHESIS_RESEARCHER_20260822.md; closes coverage orphans (evals, curation/search/ingestion cluster) and aligns 5 session-less KD domains.
- **E-3 MANIFEST v5.0 rewrite**: current 13-agent fleet, both session systems, 4 plugins (awareness/error-capture/silent-stall-sensor/sovereign-compaction), 20+ skills, 8 commands, ICS-S adoption convention.

### MEDIUM
- **E-4 HIVEMIND_PROTOCOL v2.0**: add Node-page flow, CSP engagement rules, injection-ledger duty; formally deprecate live feeds; reference ICS-S provenance.
- **E-5 Protocol layering map**: one page — "launching?→DISPATCH · iterating?→CSP · stalled?→G1-G3 · resuming?→STRP · onboarding expert?→NOP" — inserted into AGENTS.md.
- **E-6 Sync PLAN §6**: mark PP-4/P5 implemented; add experiment X7 ("[N7] tag verified in live ICS header during next page").
- **E-7 Curators↔Nodes bridge**: map each of 13 domains to owning Node/charter; feed mapping into domain_loader.py spec (KD post-debut) so content-layer governance and session-layer expertise converge instead of paralleling.

### LOW
- **E-8 Session lifecycle automation**: E-ritual closure nudges via existing plugins; SESSION_REGISTRY.md generation (P3 of plan).
- **E-9 Consultable telemetry**: pages/month ledger per Node — evidence feed for growth gate (≥3 off-domain pages ⇒ new Node case).
- **E-10 Doc hygiene batch**: Sophia→MaKaLi fix, hive/ row removal from OMEGA_ENGINE §3, agent-count reconciliation, KD tracker registration.

## §5 Strengths to Preserve (do NOT break while enhancing)

1. Failure-derived rule lineage — every rule cites its incident; audit trail culture is rare and load-bearing.
2. File-first doctrine — consistent across all five protocol generations.
3. Turn-boundary transaction model — documented concurrency semantics with B1-B15 evidence.
4. Universality clause — any agent pages any Node; oversight ≠ gatekeeping.
5. Cost honesty — n=1 genesis data (~1 day/~6 cycles), resume economics (~185K input/turn), stall-rate expectations (2/2 multi-file).
6. Zero-new-agent-files discipline — expertise scales as KBs/sessions, M10 cap intact.

## §6 Source Register (all read in full/part this session)

| Artifact | Location | Freshness |
|----------|----------|-----------|
| Node Expert Sessions Plan | data/coordination/NODE_EXPERT_SESSIONS_PLAN.md | CURRENT (D-586, 2026-08-21) |
| Node Onboarding Protocol v1.0.0 | .opencode/agent/NODE_ONBOARDING_PROTOCOL.md | CURRENT (2026-08-22) |
| Conversational Subagent Protocol v1.0.0 | .opencode/agent/CONVERSATIONAL_SUBAGENT_PROTOCOL.md | CURRENT (2026-08-21) |
| Stalled Subagent Recovery v2.0.0 | .opencode/agent/STALLED_SUBAGENT_RECOVERY.md | CURRENT (2026-08-20) |
| Subagent Dispatch Protocol v3 | docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md | PARTIAL-STALE (2026-07-12; §12 added 08-16) |
| STRP v1.0.0 | docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md | CURRENT (2026-07-21) |
| Oversight Hierarchy | docs/architecture/OVERSIGHT_HIERARCHY.md | STALE (2026-07-06, Sophia) |
| Lattice & Node Slot Mechanics | data/coordination/LATTICE_NODE_MECHANICS_20260818.md | CURRENT (2026-08-18) |
| ICS System | docs/architecture/ICS_SYSTEM.md | CURRENT (2026-08-22) |
| Fleet Team Playbook v1.1.0 | docs/strategy/FLEET_TEAM_PLAYBOOK.md | CURRENT (DOC-1 stamped 08-17) |
| Agent & Mode Manifest v4.0.0 | .opencode/MANIFEST.md | STALE (2026-06-04) |
| Hivemind Protocol v1.3.0 | docs/strategy/HIVEMIND_PROTOCOL.md | STALE (2026-06-25) |
| Conversational Subagents Study | docs/research/R_CONVERSATIONAL_SUBAGENTS_STUDY_20260821.md | CURRENT (evidence base B1-B15) |
| hierarchy.yaml / roles.yaml / dispatch refs | config/wads/_omega_default/ | roles.yaml STALE models |
| Domain Curator Registry | config/domains/curators.yaml | CURRENT (D-569, post-debut Horizon 3) |
| opencode.json (repo) | .opencode/opencode.json | PRE-CI-2 |

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_node_system_discovery ⬡ 2026-08-22*
