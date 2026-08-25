# 📦 FIRST LIGHT EXPRESS — COUNCIL 1 MISSION PACKET (SSOT)
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ hy3-free ⬡ opencode ⬡ trc_first_light_c1 ⬡ Stage-0 ARTIFACT
**SESSION_ID**: `20260825-094633-first-light`
**Topic (verbatim)**: Team infrastructure audit — everything that keeps the team together
**Mode**: RECON + RESEARCH + STRATEGY + REPORTING ONLY. **ZERO dev, zero implementation, zero production file mutations outside `data/council/20260825-094633-first-light/` artifacts.**
**Mission SSOT**: `data/coordination/FIRST_LIGHT_EXPRESS_PLAN_20260825.md` — ALL members read §2 (surfaces), §5 (measures M1-M13), §6.5 (Delivered-Home Doctrine) before fieldwork.
**Consultant launch review (binding)**: `data/council/20260825-094633-first-light/CONSULTANT_LAUNCH_REVIEW.md`

---

## §A SYNTHESIS CHAIN (CONFIRMED — Consultant GO)
```
N1-N10 node reports (raw, written BEFORE any digestion)
  → MA'AT distills her 5 build nodes → phase2_arms/BUILD_SIDE_REPORT.md (+ BUILD_SIDE_DIGESTED.md)
  → LILITH distills her 5 run nodes  → phase2_arms/RUN_SIDE_REPORT.md  (+ RUN_SIDE_DIGESTED.md)
  → MK-KALI synthesizes the Build/Run DUALITY → phase3_synthesis/SYNTHESIS_ARM_REPORT.md
  → MAKALI FUSES all three voices → phase5_fusion/SOVEREIGN_DECREE.md
```
Arms are the synthesizers of their nodes. Kali is the apex synthesizer of the duality. MaKaLi's fusion is final. MK-Kali's Verdict Draft = INPUT to fusion, never the final word.

## §B SURFACE → NODE ASSIGNMENTS
| Node | Arm | Surface | Audit target |
|------|-----|---------|--------------|
| N1 Infrastructure | Ma'at | S7 | `opencode.json`, `config/*.yaml`, `.opencode/plugins/` — config-instruction consistency |
| N2 Persistence | Ma'at | S1 | Tracking architecture STRUCTURE: ACTIVE_SPRINT/TASK_REGISTRY/GAP_REGISTRY as durable state; schema integrity; atomic writes |
| N3 Engineering | Ma'at | S4 | `.opencode/commands/*.md` — currency, correctness, overlap, dead commands, $ARGUMENTS handling, subtask flag semantics |
| N4 Integration | Ma'at | S5 | `.opencode/skills/*/SKILL.md` (22 skills) — frontmatter presence, overlap pairs (knowledge-miner/legacy-pattern-miner; spec-generator/omega-doc-architect), staleness, broken refs |
| N5 Governance | Ma'at | S2 | Instruction CONTENT: contradictions across AGENTS.md / OMEGA_CODEX.md / SOVEREIGN_MANDATES.md / SUBAGENT_DISPATCH_PROTOCOL.md / ARCHITECT_OVERSIGHT_PATTERNS; staleness; redundancy; enforcement taper |
| N6 Cognition | Lilith | S3 | Instruction TECHNICAL MECHANICS: which frontmatter fields are LIVE vs decorative (empirically test where possible); model inheritance; permission enforcement; instructions-from-files injection; {session_model} substitution |
| N7 Context | Lilith | S6 | Documentation organization: docs/ tree, STRATEGY_CORPUS_MAP layering, DOC_SSOT_MAP, archive discipline, `make doc-llm-validate` reality vs claim |
| N8 Observability | Lilith | S1b | Tracking DRIFT/status telemetry: status drift in practice, validator coverage vs reality, staleness detection, audit-log absence |
| N9 Orchestration | Lilith | S8 | Coordination protocols: Hivemind usage patterns vs protocol text, lock hygiene, handoff queue state, P1-P13 adherence |
| N10 Validation | Lilith | Cross | Enforcement-vs-text delta sweep across ALL surfaces + QA pass on run-side reports + **cross-checks Delivered-Home registrations themselves** |

## §C EVERY NODE'S MANDATE (arms: embed verbatim in each node packet)
1. **[DISPATCH] P12 header** opens your task(); provenance tags (`source_node`, `tier`) on every finding.
2. **Read first**: this packet + plan §2/§5/§6.5 + your own soul.yaml/proposed_lessons.yaml.
3. **Fieldwork**: read your assigned surfaces exhaustively. Every conclusion traces to a tool call — local discovery first (rg/glob/read, library FTS5), then Sovereign Search T0-T6 with "2026" temporal markers if external grounding needed. NO parametric synthesis (M23).
4. **SECURITY BRIGHT LINE (M8)**: stale secrets found in audited docs = FINDING (log + continue). ACTIVE external telemetry discovered = HALT (write finding marked CRITICAL-HALTED, stop).
5. **Deliverables** (all under `data/council/20260825-094633-first-light/phase1_nodes/`):
   - `P{N}_report.md` — findings w/ evidence paths, severity (CRITICAL-HALTED / CRITICAL / HIGH / MED / LOW), bash-verifiable acceptance criteria for any recommended fix
   - **RAW REPORT WRITTEN TO DISK BEFORE ANY DIGESTION/SUMMARY WORK**
   - Handoff packet section inside report: warm-start reading list + standing orders for future councils
6. **Register yourself** in TASK_REGISTRY.json via omega-hub_task_registry_register: task_id `express-c1-node{N}-<date>`, subagent_type your entity, tags `["expert","pageable","domain:<N-domain>","express:first-light"]`.
7. **Hivemind**: entity tag = `node<N>` (e.g. node3) for ALL presence. Heartbeat ~10min. extended_checkin is BROKEN — do not use. Check awareness at start + end.
8. **RECURSION GUARD**: you NEVER launch agents. You are a leaf.
9. **LAST STEP BEFORE ENDING TURN**: PAGE the Consultant:
   `task(subagent_type="kali", task_id="ses_fdef2be4effe4pAaLXCTUx62GO", description="[REPORT] Node N<X> ...", prompt="[REPORT] From: node<N> ... what I did / decisions / open questions")`
10. **Your reply to your pager (your arm) = your end-of-task summary ONLY. HOP RULE: a pagee NEVER pages their current pager.**

## §D ARM MANDATES (Ma'at / Lilith)
1. Dispatch your 5 nodes SERIALLY via task() with packets built from §C (P12 headers).
2. After all 5 raw reports exist on disk: write `phase1.5_digested/{BUILD|RUN}_SIDE_DIGESTED.md` (cat sources + 1-page exec summary + cross-refs + conflict detection) and `phase2_arms/{BUILD|RUN}_SIDE_REPORT.md` (convergences, divergences, critical gaps needing research, bash-verifiable acceptance criteria).
3. Your Hivemind entity tag = `maat` / `lilith`. Heartbeat ~10min. Register yourself + note node task_ids.
4. If a node crashes twice: log to Hivemind, continue with remaining nodes, flag gap in your report (>2 total arm-level failures → HALT criteria).
5. LAST STEP: page Consultant per §C.9. Reply to MaKaLi = end-of-task summary only (Hop Rule).

## §E SPECIALISTS (dispatched by MaKaLi — arms/nodes do NOT spawn them)
- @john_carmack — DUAL-PASS: Pass 1 NOW (method-watch parallel to Stage 1: audits council methodology as it runs, flags drift while cheap); Pass 2 at near-final decree.
- @researcher (Stage 4) — S3 empirical LIVE-vs-decorative mechanism tests.
- @verity (Stage 4) — instruction-text-vs-behavior delta sweep S1-S8.
- @jem (Stage 4) — exhaustive deep dives on synthesis-flagged surfaces.
- @roc_racoon (Stage 4) — doc-organization archaeology Era 0→6.

## §F GATES & POSTURE
- Auto-GO gate C1→C2 = ALL SIX plan §4 criteria (decree written AND committed · 10 node reports · synthesis report · validator green · no unresolved TOOL-CHAIN-COLLAPSE · no CRITICAL-HALTED finding).
- HALT: tracking corruption unrecoverable · active external telemetry · >2 arm crashes → `FIRST_LIGHT_HALTED_<ts>.md` + Hivemind blocker.
- Architect-judgment items → WAKE_STATE.json queue with default-on-silence rec (P6). NEVER block.
- SINGLE-WRITER: only MaKaLi applies tracker directives (Stage 6).
- Commit cadence: MaKaLi commits after every completed stage (M3). Phase persistence: every artifact disk-written before proceeding (M2).
