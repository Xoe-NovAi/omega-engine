<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔍 CARMACK METHOD-WATCH — PASS 1 (Methodology Audit)
From: john_carmack | ts: 2026-08-25T13:40Z | trc_first_light_c1
To: makali_fusion (via Consultant relay) | Scope: METHOD ONLY — findings audited at Pass 2
Inputs: phase0_mission_packet.md · FIRST_LIGHT_EXPRESS_PLAN_20260825.md · CONSULTANT_LAUNCH_REVIEW.md · council-cloud.md v2.2

**VERDICT: GO WITH CORRECTIONS.** The topology is sound. The failure modes below are
concentrated in three places: (a) the compression funnel between raw evidence and decree,
(b) gates that check *existence* instead of *content*, and (c) three internal contradictions
in the SSOT documents themselves — ironic for a council auditing instruction consistency.

Ranked by expected cost-if-uncaught. Each entry: RISK → WHY (evidence) → WATCH-FOR (mid-flight sign) → CHEAP CORRECTION.

---

## R1 — The Compression Funnel: decree is 3+ removals from ground truth (HIGH)
**Risk**: Information silently lost between node fieldwork and final decree. The decree —
the artifact the Architect wakes to — never touches raw evidence.

**Why**: Chain is `node raw report → SIDE_DIGESTED.md → arm report → SYNTHESIS_ARM_REPORT → SOVEREIGN_DECREE`. Plan §8 explicitly states "arms read digests not raw node reports." MK-Kali reads "BOTH digests + BOTH arm reports" (packet §A, command Stage 3) — never raw node reports. MaKaLi reads arm reports + synthesis (command Stage 5) — never raws. Meanwhile M8 says token budget is UNLIMITED and "thick reports preferred over thin summaries" (plan §5). These two design choices contradict: you built a lossy pipeline inside a system with no resource pressure justifying it. Every digest level drops: handoff-packet sections (§C.5 warm-start lists — digest format spec doesn't mention preserving them), severity nuance, and negative findings ("checked X, it's fine" — digests summarize *findings*, so clean surfaces become invisible, and the decree can't distinguish "audited and clean" from "never examined").

**WATCH-FOR**: At Stage 2, spot-check: pick one LOW-severity finding in a raw node report and one explicit "no issue found" statement. If neither survives into the digested/arm layer, the funnel is eating signal. Also: any decree claim citing a surface with no surviving raw-level trace.

**Correction**: One line in each arm's Stage 2 mandate: "Digest must carry forward EVERY finding (any severity) and EVERY explicit clean-bill statement, verbatim-tagged with source node." Cost: minutes. Alternative if arms balk: since M8 makes tokens free, let MK-Kali read the 10 raws directly — she's one session, 10 files is trivial.

---

## R2 — Auto-GO gate checks file EXISTENCE, not content (HIGH)
**Risk**: Gate criterion "All 10 node reports exist on disk" (plan §4) passes on stubs. A node that crashes after writing a header-only file, or that writes a 200-word summary of the mission packet, satisfies the gate. The train departs on theater.

**Why**: Plan §4 and packet §F list existence-only criteria. Nothing specifies minimum content, mandatory sections, or evidence density. Combined with R4 (packet-echo theater), a compliant-looking garbage report is indistinguishable from fieldwork at gate time.

**WATCH-FOR**: Before declaring the C1→C2 gate green, run: `wc -l data/council/*/phase1_nodes/P*_report.md` — anything under ~100 lines is suspect. Grep each report for at least 3 distinct repo paths (evidence trails). A report citing zero file paths is a stub regardless of length.

**Correction**: Add a 30-second content gate to Stage 7 checklist: every P{N}_report.md must contain ≥3 evidence paths + ≥1 bash-verifiable acceptance criterion + severity tags. Failures get re-dispatched before Council 2, not discovered by the Architect post-wake.

---

## R3 — Delivered-Home Doctrine is aspirational, not enforceable (HIGH)
**Risk**: The headline deliverable ("fleet grows by 10 resident domain experts," plan §6.5) silently fails, and nobody notices because no gate checks it.

**Why**: Three independent defects:
1. **Single-writer conflict**: Packet §C.6 instructs each node to self-register in `TASK_REGISTRY.json`; packet §F says "SINGLE-WRITER: only MaKaLi applies tracker directives (Stage 6)." Both cannot hold. Either nodes violate single-writer (concurrent JSON writes, race conditions, M27 exposure) or they don't register and the doctrine dies quietly.
2. **No gate coverage**: The six auto-GO criteria (plan §4) do not include registration completeness. Ten missing registrations = GO anyway.
3. **Verification is advisory**: Consultant review Q2 made N10's cross-check of registrations "take it or leave it." Optional QA on the doctrine's sole output = no QA.

**WATCH-FOR**: After each node lands, query `omega-hub_task_registry_query(tags=["express:first-light"])`. Count. If <10 by end of Stage 2, the doctrine has already failed and Stage 5 hasn't happened yet — still cheap to fix (MaKaLi registers stragglers herself at Stage 6 under single-writer authority).

**Correction**: Resolve the conflict NOW, one sentence in remaining dispatch packets: "Nodes POST their intended registration payload inside P{N}_report.md; MaKaLi applies all 10 registrations at Stage 6 as single writer." This preserves both rules and makes registration a Stage 6 checklist item.

---

## R4 — Packet-echo theater: nodes parroting the audit-target column (MED-HIGH)
**Risk**: Node reports restate the mission packet's framing instead of discovering ground truth. Packet §B pre-writes each node's conclusion-shape ("config-instruction consistency", "frontmatter presence, overlap pairs…"). A lazy node delivers exactly those phrases back with severity stickers. This is the classic auditor's failure: confirming the brief.

**Why**: §C.3 mandates "every conclusion traces to a tool call" but provides no verification — it's honor-system. Nodes also burn context on packet + plan §2/§5/§6.5 + soul.yaml before fieldwork; with finite step budgets, the path of least resistance is synthesizing from the brief.

**WATCH-FOR**: In each raw report, count claims that are NEW relative to §B's audit-target wording vs. restatements. Signal of health: reports containing surprises (findings that contradict or extend the brief — e.g., "the overlap pair named in the brief is actually fine; the real overlap is X"). Zero-surprise reports across all 10 nodes = systemic theater.

**Correction**: Add one line to node mandates: "Your report must contain at least one finding the mission packet did not anticipate, or explicitly certify 'surface swept, brief confirmed' with evidence." Cheap, and it converts silence into a falsifiable claim.

---

## R5 — Researcher's S3 empirical tests collide with the zero-mutation bright line (MED-HIGH)
**Risk**: The clearest scope-creep vector in the plan. Researcher's Stage 4 job is to "empirically verify which instruction mechanisms are LIVE — test frontmatter fields, model inheritance, permission enforcement" (plan §2). Testing frontmatter/permission behavior REQUIRES creating temp agent files, temp configs, or invoking OpenCode parsing on novel inputs — i.e., mutations outside `data/council/…`, which the mission packet §header forbids absolutely.

**Why**: Packet line 5: "ZERO dev, zero implementation, zero production file mutations outside `data/council/20260825-094633-first-light/`." Plan §8 lists "Council scope creep into dev" as a known hazard with "out-of-scope lists in BOTH dispatch packets" as mitigation — but the researcher's assignment *itself* sits on the boundary. An eager researcher will either (a) mutate and violate the bright line, or (b) refuse and deliver a desk-analysis dressed as empirical testing — which is precisely the M23 soft-failure theater the engine bans.

**WATCH-FOR**: Any `write`/`edit` tool calls by the researcher targeting `.opencode/agents/`, `opencode.json`, or `config/` during Stage 4. Conversely: a researcher report claiming "empirically verified" with no sandboxed execution evidence.

**Correction**: Pre-rule it in the researcher's tuning brief: "Empirical tests permitted ONLY inside `data/council/<session>/phase4_research/sandbox/` (temp agent files, throwaway configs pointed at copies). Production trees untouched. Tests that cannot run in sandbox = documented as untested, not simulated."

---

## R6 — N10's cross-cutting sweep is raced by construction (MED)
**Risk**: N10 owns "Enforcement-vs-text delta sweep across ALL surfaces + QA on run-side reports + cross-checks Delivered-Home registrations" (packet §B). But Lilith dispatches N6→N10 serially while Ma'at runs N1–N5 in parallel. N10 executes before several build-side nodes have landed. Its "ALL surfaces" sweep runs against half-empty phase1_nodes/, and its registration cross-check (R3) can't see N1–N5 registrations that don't exist yet.

**Why**: Packet §D.1 (serial within side) + §B (N10 = cross-side QA). Nobody sequenced N10 *after* both sides. Same structural flaw makes N10's run-side QA fine but its cross-side duties impossible-as-timed.

**WATCH-FOR**: An N10 report asserting completeness over surfaces whose node reports postdate N10's timestamp. Check: `ls -la --time-style=+%H:%M phase1_nodes/` vs N10 report mtime.

**Correction**: Either (a) strip cross-side duties from N10's packet and reassign them to MaKaLi's Stage 5 pre-fusion checklist, or (b) have MaKaLi dispatch a tiny N10b follow-up after both arms land. Option (a) costs zero extra dispatches.

---

## R7 — S1 dual ownership: two nodes skim where one should own (MED)
**Risk**: The prompt asked me to name surfaces two nodes will both skim. Here it is: S1. N2 owns "tracking architecture STRUCTURE… schema integrity"; N8 owns "validator coverage vs reality" (packet §B). The single most load-bearing question — *does `validate_tracking_state.py` actually catch what TRACKING_ARCHITECTURE.md claims it catches?* — falls in the seam. N2 can treat the validator as N8's; N8 can treat schema reality as N2's. Consultant Q2 blessed dual ownership as "a feature" contingent on "the digester's conflict detection" — but conflict detection catches *disagreements*, not *shared omissions*. Two readers who each assume the other ran the validator produce zero conflicts and zero coverage.

Related nominal-coverage case: the cross-cutting delta sweep is assigned TWICE (N10's "Cross" row AND verity's Stage 4 compliance sweep). Two shallow sweeps of the same cross-cutting space, neither owning it deeply, while no individual owns it at depth.

**WATCH-FOR**: At Stage 2, grep both N2 and N8 raw reports for actual execution evidence of `scripts/validate_tracking_state.py` (command output, exit codes). If neither ran it, S1's central question went unanswered by a 2-node investment.

**Correction**: One line in N2's packet: "You OWN executing the validator and reporting its output verbatim. N8 owns drift telemetry. Do not defer validator execution." For the N10/verity duplication: demote N10's sweep to "spot-check sample" and let verity own the full sweep at Stage 4 with synthesis-flagged aims.

---

## R8 — The SSOT documents contradict themselves (MED — and embarrassing)
**Risk**: The council auditing instruction-consistency is launched on instruction sets that disagree. Three concrete defects:
1. **Node-domain mismatch**: council-cloud.md Stage 1 defines N2 Persistence as "SoulStore, MemoryStore, state durability"; the mission packet assigns N2 = S1 tracking architecture. A node reading both specs gets two different jobs.
2. **extended_checkin contradiction**: plan M1 mandates "every dispatched arm/specialist instructed to register their own extended check-in"; packet §C.7 says "extended_checkin is BROKEN — do not use." If arms follow the plan, they call a broken tool; if they follow the packet, M1 is unmet and >20-min silent stretches during long serial node dispatches expose arms to pruning.
3. **Heartbeat cadence drift**: command Stage 0 says every 5 min; plan M5 and packet say ~10 min. Trivial alone, symptomatic in aggregate.

**Why**: All four source documents, this audit's inputs. The machinery spec (v2.2) predates the surface mapping and wasn't reconciled.

**WATCH-FOR**: A node asking "which N2 am I?" or an arm posting a Hivemind question about check-in policy — that's the contradiction surfacing the expensive way.

**Correction**: MaKaLi posts one Hivemind clarification NOW (broadcast, not file mutation): "Packet §B assignments supersede command Stage 1 node descriptions; extended_checkin stays OFF (packet wins); heartbeat = 10 min." Thirty seconds, kills all three.

---

## R9 — MaKaLi fusion-stage saturation: highest stakes, least guard (MED)
**Risk**: MaKaLi runs Stages 0–7 in ONE session, accumulating every digest, arm report, synthesis, research result, and 22 members' worth of coordination. By Stage 5 fusion — the single highest-stakes cognitive act of the run — the orchestrator's context is at its most degraded. Silent quality collapse: fusion that skims, attributes sloppily, or drops preserved dissent. No gate detects this because the gate checks decree *existence* (see R2).

**Why**: Command Stage 7 ("you never end your turn"), plan §6 tree (single makali), commit cadence M3 (only disk-state checkpointing — protects artifacts, not reasoning quality). The Architect's own correction at plan top notes orchestrators "burn far fewer turns" — true for turns, irrelevant to context saturation.

**WATCH-FOR**: Fusion output that cites fewer than ~half the node reports by name in triad attribution, or a "Preserved Dissent" section that's empty when the raws clearly contained build/run tensions. Both are saturation signatures.

**Correction**: Cheap insurance, not redesign: immediately after Stage 3, MaKaLi writes a 1-page `phase5_fusion/FUSION_BRIEF.md` (top tensions, open questions, attribution skeleton) BEFORE reading research results — fusing from the brief plus targeted re-reads instead of total recall. Also: commit the brief (M3) so a compacted MaKaLi can recover her own fusion state.

---

## R10 — Consultant paging bottleneck + passive correction loop (LOW-MED)
**Risk**: ~22 members each page `ses_fdef2be4effe4pAaLXCTUx62GO` as their mandatory last step. The Consultant session's context grows monotonically across the whole run; late-run pages arrive into a saturated reviewer, degrading exactly the "second set of eyes" function the protocol exists for. Second-order: Consultant corrections go to Hivemind broadcast, and consumption is passive ("everyone periodically checks the feed"). A correction posted mid-Stage-2 may not be read by the arm that needs it until that arm's next natural check-in — or never.

**Why**: Plan M11/M13, command Reporting Protocol. No TTL, no summarization, no acknowledgment loop on broadcasts.

**WATCH-FOR**: Consultant replies getting shorter/genericer over the run (saturation signature); a Hivemind correction with zero subsequent artifact changes referencing it within one stage.

**Correction**: Not worth restructuring mid-flight. Cheap mitigation: arms must ACK consultant-relevant Hivemind corrections in their next status post ("correction R-x: applied / rejected because"). Makes the loop closed and auditable at near-zero cost.

---

## R11 — M23 rigidity misapplied to local-only recon (LOW)
**Risk**: Nodes auditing local files (most of S1–S8) have no business needing external search, but §C.3 permits Sovereign Search T0–T6 "if external grounding needed." If a node invokes a failing mandatory tool over a nonessential citation, M23 forces `[TOOL-CHAIN-COLLAPSE]` and a hard stop — killing a healthy node over a footnote.

**Why**: Packet §C.3 + command Execution Mandate ("If mandatory tool fails → TOOL-CHAIN-COLLAPSE, hard stop"). M23 is correct for load-bearing tools; blanket application to optional grounding is over-triggering.

**WATCH-FOR**: Any TOOL-CHAIN-COLLAPSE event originating from a node whose surface is purely local files.

**Correction**: One clarifying line: "Local-file surfaces require NO external grounding; T1–T6 use is optional enrichment. Tool failures on optional tiers = note and degrade, not collapse." M23 stays absolute for genuinely mandatory steps (registry writes, validator runs).

---

## R12 — Severity taxonomy drift across independent nodes (LOW)
**Risk**: Ten nodes apply CRITICAL/HIGH/MED/LOW independently with no rubric. Node A's HIGH is Node B's MED. The digester's conflict detection catches numeric disagreements (per Consultant Q2) but not calibration drift — so the decree's priority ordering inherits noise, and Council 2 spec-clustering keys off inflated severities.

**Why**: Packet §C.5 defines the labels but not the boundaries. No cross-node calibration step exists anywhere in the flow.

**WATCH-FOR**: At Stage 2, if one node produced ≥3 CRITICALs and another produced zero findings above MED on similarly-sized surfaces, calibration has drifted.

**Correction**: Arms normalize severity at distillation (they see all 5 of their side's reports — the natural calibration point). One line in §D.2: "Re-scale severities across your 5 nodes before writing the arm report; flag any node whose calibration diverges wildly."

---

## SUMMARY TABLE

| # | Risk | Class | Cost to fix | Fix owner |
|---|------|-------|-------------|-----------|
| R1 | Compression funnel eats signal | Info loss | 1 line / or MK-Kali reads raws | MaKaLi |
| R2 | Existence-only auto-GO gate | Theater | 30s content check | MaKaLi |
| R3 | Delivered-Home unenforceable (single-writer conflict) | SPOF/aspirational | 1 line + Stage 6 item | MaKaLi |
| R4 | Packet-echo theater | Theater | 1 line in node mandates | Arms |
| R5 | Researcher tests vs zero-mutation line | Scope creep | Sandbox pre-ruling | MaKaLi |
| R6 | N10 cross-side race | SPOF/timing | Strip or resequence | MaKaLi |
| R7 | S1 dual-ownership seam (validator orphaned) | Nominal coverage | Ownership line to N2 | Ma'at |
| R8 | SSOT self-contradictions (N2 def, checkin, cadence) | Doc rot | 1 Hivemind clarification | MaKaLi |
| R9 | Fusion-stage saturation | SPOF/quality | FUSION_BRIEF.md | MaKaLi |
| R10 | Consultant saturation + passive corrections | Bottleneck | ACK requirement | All |
| R11 | M23 over-trigger on local recon | Rigidity | 1 clarifying line | MaKaLi |
| R12 | Severity calibration drift | Info noise | Arm normalization | Arms |

Eight of twelve fixes are one-line dispatch-packet or Hivemind amendments executable
before Stage 2 completes. R1, R3, R5, R6 are the ones that decide whether the Architect
wakes to truth or to a well-formatted echo chamber.

— Carmack, Pass 1. Pass 2 fires at near-final decree: findings audit, provenance spot-checks,
and gate-integrity verification of whatever this methodology actually produced.
