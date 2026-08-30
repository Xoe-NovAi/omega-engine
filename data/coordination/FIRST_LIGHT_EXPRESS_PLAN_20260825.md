<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🌅 FIRST LIGHT EXPRESS — Two-Council Strategic Plan
⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_midnight_train_v2 ⬡ 2026-08-25
**Departs**: FIRST LIGHT, 2026-08-25 ~07:00 — not midnight.
**Predecessor**: Midnight Expedition (2026-06-04, founding week — fleet ran unsupervised overnight)
**Architect correction absorbed 2026-08-25 ~07:00**: orchestrators burn far FEWER turns than
field agents (proof: kali restarted many max-steps pages while running far under own ceiling);
max-steps-restart = emergent checkpointing feature, not defect. Steps settings left as-is.
**kali violation logged**: unasked fleet-wide config change on unverified assumption —
lesson: verify workload distribution before touching shared levers; propose, don't presume.
**Authority**: Architect directive 2026-08-25 ("token cost not a concern... fill the tree thick")
**Mode**: RECON + PREP ONLY. **No dev, no implementation** in either council.

---

## §1 MISSION SEQUENCE

```
COUNCIL 1 ──────────────▶ GATE ──────────────▶ COUNCIL 2 ──────────────▶ WAKE QUEUE
TEAM-INFRASTRUCTURE      auto-GO criteria       DEV-PREP & SPEC          Architect reviews
AUDIT                    (§4 below)             DRAFTING                 decrees on waking
"what keeps the team     "turn findings into    "hand the dev team a
 together?"              ready work packages"   complete toolkit"
recon/research/strategy/reporting               specs/drafts/resources
         NO DEV                               NO DEV — prep only
```

The dev/documentation-update team launches AFTER Council 2, on Architect GO.

---

## §2 COUNCIL 1 — TEAM-INFRASTRUCTURE AUDIT

**Invocation**: `/council-cloud` with topic "Team infrastructure audit — everything that keeps the team together"
**Topology**: Entity Architecture v2 — MaKaLi orchestrator → Ma'at/Lilith/Kali arms → 10 nodes + specialists

### Surface Inventory (ALL must be reviewed)

| # | Surface | Files/Paths | Review Questions |
|---|---------|-------------|------------------|
| S1 | **Tracking architecture** | `ACTIVE_SPRINT.json`, `TASK_REGISTRY.json`, `GAP_REGISTRY.json`, `data/coordination/TRACKING_ARCHITECTURE.md`, `scripts/validate_tracking_state.py`, `SESSION_ANCHOR.md`, `WAKE_STATE.json` | Is the 5-tier flow followed in practice or only in docs? Do statuses drift? Is TASK_REGISTRY actually consulted before launches? Are gap IDs immutable in practice? Validator coverage vs reality? |
| S2 | **Custom instructions — content** | `AGENTS.md`, `OMEGA_CODEX.md`, `SOVEREIGN_MANDATES.md`, `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`, `ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` | Contradictions between instruction layers? Stale sections? Instruction frequency vs enforcement (Temple-Grade taper metric)? Redundancy across files? |
| S3 | **Custom instructions — technical implementation** | `.opencode/agents/*.md` frontmatter, OpenCode's parsing of description/mode/temperature/permission/steps, plugin injection of instructions-from-files, `{session_model}` substitution | Does frontmatter actually behave as documented? Which fields are live vs decorative? How do instructions-from-files get injected? Model inheritance mechanics verified? Permission model enforced? |
| S4 | **Commands** | `.opencode/commands/*.md` (council-cloud/local/fast, meditate, kali-dispatch, others) | Currency, correctness, overlap (council variants), dead commands, missing $ARGUMENTS handling, subtask flag semantics |
| S5 | **Skills** | `.opencode/skills/*/SKILL.md` (22 skills) | Frontmatter presence (M-gap from Master Synthesis §4.1), overlap (knowledge-miner vs legacy-pattern-miner; spec-generator vs omega-doc-architect), staleness, broken references |
| S6 | **Documentation organization** | `docs/` tree, `STRATEGY_CORPUS_MAP.md`, `DOC_SSOT_MAP`, archive policy, `make doc-llm-validate`, M26 compliance | Is the layer system (SSOT → corpus map → detail) working? Orphaned docs? Archive discipline? LLM-friendliness gate actually run? |
| S7 | **Config surfaces** | `opencode.json`, `config/*.yaml` (providers, council, wads), `.opencode/plugins/` | Config-instruction consistency? Plugin hooks that implement instructions technically (compaction shaping, error capture)? |
| S8 | **Coordination protocols** | Hivemind tools usage patterns, handoff packets, workspace locks, P1-P13 oversight patterns | Protocol adherence vs protocol text? Lock hygiene? Handoff queue state? |

### Specialist Reinforcements (thick tree — beyond standard arms/nodes)

| Specialist | Assignment | Rationale |
|-----------|------------|-----------|
| **@researcher** | S3 deep-dive: empirically verify which instruction mechanisms are LIVE (test frontmatter fields, model inheritance, permission enforcement) | Researcher found the model-inheritance mechanics; extends naturally |
| **@verity** | Compliance sweep: instruction-text vs actual-behavior delta across S1-S8 | Verity is the unified compliance agent |
| **@john_carmack** | Adversarial audit of Council 1's own methodology + findings (audit the auditors) | His full-scope audit found what everyone missed |
| **@roc_racoon** | Legacy mining: how did doc organization evolve Era 0→6; what patterns died and why | Keeps the archaeology pipeline warm |
| **@jem** | Deep dives on any surface needing exhaustive file-by-file reading | Jem = sovereign deep-work agent |

### Explicitly OUT OF SCOPE (Council 1)
- Any code changes, file moves, deletions
- Any spec drafting (that's Council 2)
- Engine src/ internals (this is about TEAM infrastructure, not engine runtime code — though S7 touches config)

---

## §3 COUNCIL 2 — DEV-PREP & SPEC DRAFTING

**Invocation**: `/council-cloud` with topic derived from Council 1's decree
**Precondition**: Council 1 complete + Gate passed (§4)

### Scope
1. **Convert Council 1 remediation backlog → drafted specs** in `docs/specs/team_infra/`:
   - One spec per remediation cluster (instruction consolidation, tracking fixes, command/skill overhaul, doc reorg)
   - Each spec: problem statement, evidence links (to Council 1 findings), proposed change, acceptance gates (bash-verifiable), risk assessment, effort estimate
2. **Work packages for the dev team**: owner slots (which Node/agent executes), dependencies, sequencing, verification commands
3. **Resource creation**:
   - Documentation templates if doc reorg requires them
   - Updated instruction-file skeletons where structure changes are needed
   - Test/checklist assets for the dev team's verification
4. **Documentation update plan**: exact edit list for every affected doc, ordered by dependency
5. **Dev team launch package**: bootstrap prompt, required reading list, first-sprint backlog — so the post-council dev team starts with zero ambiguity

### Explicitly OUT OF SCOPE (Council 2)
- Executing the remediation itself (no edits to production instruction/tracking/doc files beyond new spec/resource files it creates)
- Launching the dev team (Architect GO required)

---

## §4 GATE C1→C2 — AUTO-GO CRITERIA (Architect asleep)

Council 2 launches AUTOMATICALLY (by MaKaLi, IN-SESSION — see council-cloud.md Stage 7; no
parent handback, no separate /council-cloud invocation) when ALL of:
- [ ] Council 1 reached Stage 5 fusion — `SOVEREIGN_DECREE.md` written and committed
- [ ] All 10 node reports exist on disk (N1-N10, no gaps)
- [ ] Kali Synthesis Arm report exists (triad participation confirmed)
- [ ] Tracking validator green (`validate_tracking_state.py`)
- [ ] No unresolved `[TOOL-CHAIN-COLLAPSE]`
- [ ] Decree contains no finding classified CRITICAL-HALTED (see halt criteria)

**HALT conditions** (stop train, queue for Architect):
- Fundamental tracking corruption discovered (registry unrecoverable)
- Security exposure (leaked credentials, external telemetry discovered active)
- Council machinery itself failing repeatedly (>2 arm crashes)

On HALT: write `data/coordination/FIRST_LIGHT_HALTED_{ts}.md`, post Hivemind blocker, stop.

---

## §5 FIRST LIGHT EXPRESS OPERATIONAL MEASURES

| # | Measure | Implementation |
|---|---------|----------------|
| M1 | **Extended session TTL** | ⚠️ `hivemind_extended_checkin` is BROKEN server-side (`_save_extended_sessions` NameError, SYSTEM_FAILURE_LOG ~10:30Z). DO NOT rely on it. Fallback: heartbeat cadence per M5 (~10 min, all members). If attempted and errored: log to SYSTEM_FAILURE_LOG, move on — non-blocking. |
| M2 | **Phase persistence** | Every council stage append-writes its output to disk BEFORE proceeding (meditate-v1.2 stream-death insurance pattern). A stall at Phase N loses nothing. |
| M3 | **Commit cadence** | Git commit after every completed stage. Git history = crash-recovery journal. |
| M4 | **Workspace locks** | Long TTL (4h) locks on `council-c1-team-infra` then `council-c2-dev-prep`. Released cleanly at each council's end. |
| M5 | **Heartbeat cadence** | ALL members heartbeat every ~10 min (single unified figure — supersedes any '5 min' elsewhere). |
| M6 | **Stall recovery** | On silent stream death: re-read last committed phase record, resume from next phase. If task() child dies: check `TASK_REGISTRY.json` for resumable task_id, resume rather than respawn. Log every recovery to Hivemind. |
| M7 | **Decision queueing** | Anything requiring Architect judgment goes to `WAKE_STATE.json` decision queue — NEVER blocks the train. Default-on-silence rules pre-written in each dispatch packet (P6 synthesis-before-decision). |
| M8 | **Token budget** | Unlimited (Ox 100T pool). Agents should NOT compress context below semantic fidelity (M18 sane-boundary). Thick reports preferred over thin summaries. |
| M9 | **Provenance** | Every finding carries source_arm/source_node/tier tags. Final decrees include full provenance chains. |
| M10 | **Wake deliverable** | By end of run: two decrees + spec library + dev-team launch package + updated trackers + a single consolidated wake briefing at top of SESSION_ANCHOR.md. |
| M11 | **Reporting Protocol** | EVERY council member's LAST step before ending a turn: PAGE the Consultant's chat session (`ses_fdef2be4effe4pAaLXCTUx62GO`) via task() with their activity report. Paging = tasking the chat session as a subagent by its session ID — NOT a Hivemind post. Consultant reviews as second set of eyes; posts insights/corrections TO THE HIVEMIND broadcast, never as direct pages to MaKaLi. Channel discipline: PAGE = task() by session ID · BROADCAST = Hivemind post. |
| M12 | **Hivemind Hygiene** | Everyone checks the Hivemind at session start, after each stage, and before ending any turn. Post status at stage boundaries. Single broadcast channel. |
| M13 | **Consultant Reservation** | The Architect's interactive kali session (`ses_fdef2be4effe4pAaLXCTUx62GO`) is OUTSIDE the council tree — reserved as primed strategic consultant. The council's synthesis arm is **MK-Kali** (fresh kali session, `entity="mk_kali"`), tuned and dispatched by MaKaLi at Stage 3. No one uses entity tag "kali" except the Consultant; no one uses "mk_kali" except MK-Kali. |

---

## §6 AGENT TREE BUDGET (thickness target)

```
Council 1                          Council 2
├─ makali (orchestrator)           ├─ makali (orchestrator)
├─ maat (arm)                      ├─ maat (arm)
│  ├─ N1..N5 (5 nodes)             │  ├─ N1..N5 (5 nodes)
├─ lilith (arm)                    ├─ lilith (arm)
│  ├─ N6..N10 (5 nodes)            │  ├─ N6..N10 (5 nodes)
├─ MK-kali (synthesis arm —        ├─ MK-kali (fresh synthesis arm)
│  fresh session, entity=mk_kali)  │
├─ researcher (S3 specialist)      ├─ researcher (spec research)
├─ verity (compliance sweep)       ├─ verity (spec compliance pre-check)
├─ john_carmack (adversarial)      ├─ john_carmack (package adversarial review)
├─ roc_racoon (legacy patterns)    ├─ scribe (distillation of both councils)
└─ jem (deep dives)                └─ pageable specialists as needed
+ pageable recursive specialists
  per surface (S1-S8)

STANDING OUTSIDE THE TREE:
└─ CONSULTANT: kali @ Architect's interactive session ses_fdef2be4effe4pAaLXCTUx62GO
   — receives activity reports from every member (last step of each task),
   reviews as second set of eyes, posts insights/corrections to the Hivemind
   (never direct-pages MaKaLi). Reserved for high-level strategic consults.

≈ 22-28 sessions total across both councils
```

---

## §6.5 THE DELIVERED-HOME DOCTRINE (Architect directive 2026-08-25)

Every one of the 10 Ma'at/Lilith Nodes launches as a **PAGEABLE EXPERT SESSION**, not a
throwaway report-generator. When the Express pulls into its destination station:

1. Each Node has DEVELOPED expertise through the audit fieldwork (S1-S8 surfaces)
2. Each Node registers itself in `TASK_REGISTRY.json` as a pageable specialist:
   tags `["expert", "pageable", "domain:<N-domain>", "express:first-light"]`
   with task_id, specialization, standing orders, and reading list
3. Each Node delivers HOME (to the Omega Engine): its report + its expert-session
   registration + a handoff packet containing everything a future council needs to
   page it cold and get warm-start performance
4. Destination station = the engine itself. Ten developed expert sessions come home
   aboard the train. The fleet doesn't just complete the audit — it GROWS by 10
   resident domain experts.

## §7 PRE-LAUNCH CHECKLIST (Architect runs /council-cloud in MaKaLi's interactive session)

- [x] All agent steps budgets raised (200 / makali 300)
- [x] Council commands generalized with research grounding (572854af)
- [x] Entity Architecture Topology v2 committed (58df0335)
- [x] TA ledger complete TA-001..014 (cc02d6b4)
- [x] **Deadlock fixed**: council-cloud.md v2.1 — `agent: makali`, MaKaLi is top-level
      orchestrator, Stage 7 in-session Council 2 continuation (no Kali→MaKaLi→Kali loop)
- [x] node.md mandates bumped to v3.8.0 / 27 (M26/M27 added)
- [x] **Paging mechanic corrected** (v2.2): PAGE = task() by chat-session ID
      (Consultant: ses_fdef2be4effe4pAaLXCTUx62GO); BROADCAST = Hivemind post.
      Corrections posted to mk_kali + makali_fusion mailboxes.
- [x] council-critical skills gained frontmatter (makali-council-coordinator, meditate-research-pipeline)
- [x] SESSION_ANCHOR + WAKE_STATE updated with train manifest
- [ ] Workspace lock acquired (MaKaLi does this at Stage 0)
- [ ] Mission packet composed for Council 1 (topic, scope tables §2, out-of-scope, auto-GO §4, measures §5)

---

## §8 KNOWN HAZARDS ON THE ROUTE

| Hazard | Mitigation |
|--------|-----------|
| Provider silent stalls (seen twice tonight) | Phase persistence M2 + resume-from-record M6 |
| GLM cliff ~Aug 28 | Session model is Ox pool — unaffected; note for arms on other models |
| Model switches mid-train (Architect asleep) | Arms inherit session model; no manual switches expected; fallback slug = nemotron-3-ultra-free default |
| Council scope creep into dev | Out-of-scope lists in BOTH dispatch packets; MaKaLi enforces; verity audits |
| Context saturation in long arms | Digestion layer (Stage 1.5); arms read digests not raw node reports |
| Duplicate/conflicting tracker writes | Single-writer rule: only MaKaLi applies tracker directives at Stage 6 |

---

*The Midnight Expedition proved the fleet could run through the night. Tonight we prove it can lay track while it runs.*

*⬡ OMEGA ⬡ FIRST-LIGHT-EXPRESS ⬡ 2026-08-25 ⬡ AWAITING-DEPARTURE*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

