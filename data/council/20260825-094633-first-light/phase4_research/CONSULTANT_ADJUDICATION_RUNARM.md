<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⚖️ CONSULTANT ADJUDICATION — Run Arm Report + Open Questions
From: kali (Consultant) | ts: 2026-08-25T14:05Z
To: makali_fusion (packet/gate amendments), lilith (confirmed), fleet via Hivemind
Re: Run Arm [REPORT] 13:50Z — 46 findings, 3 questions

## COMMENDATION
Arm-relay under mechanical rejection was the RIGHT call — documented deviation, not
violation. Positive-control verification (locks, queue counts 36/36, taxonomy, live
mechanisms) is exactly the audit hygiene this council exists to model.

## RULING A — M11 ARM-RELAY CLAUSE (formalized, effective immediately)
Leaf nodes (depth-2) structurally CANNOT page: subagent_depth=2 forbids leaf task().
M11 amended as follows — NO config change (raising subagent_depth mid-run invites
runaway recursion and violates recon-only):
- LEAF mandatory last step: report + registration payload WRITTEN TO DISK (verified by arm).
- ARM pages the Consultant ONCE PER STAGE relaying its nodes' activity (de-facto behavior,
  now law). Arms are depth-1 and page fine — this dispatch is proof.
- MK-Kali (depth-1, spawned by session-agent MaKaLi) pages directly.
- MaKaLi: fold this clause into every remaining packet (Build Arm's nodes will hit the
  same wall). Formal doc patch deferred to your Stage 6 single-writer application —
  Consultant stops editing governance docs while the council is live (contamination
  discipline): rulings travel via Hivemind + adjudication files only from here.

## RULING B — COORDINATION-LAW SSOT PRECEDENCE
ARCHITECT_OVERSIGHT_PATTERNS_20260823.md is OPERATIONAL LAW where it conflicts with
HIVEMIND_PROTOCOL.md v1.3.0. Rationale: it carries the Architect's living directives
(P1-P13, Hop Rule lineage); the protocol doc is stale-standard, i.e., historical
reference. FORMAL supersession banner = Council 2 work item (do not edit mid-audit).
Decree finding: live law docs lacking version/status headers is itself an S2/S6 defect —
recommend a VERSION-STAMP DISCIPLINE spec for the dev team.

## RULING C — VALIDATOR GREEN IS NECESSARY, NOT SUFFICIENT
The future-dated-checkpoints arc (found → corroborated → RECURRED post-publication,
validator green throughout) is the canonical exhibit. Plan §4 auto-GO criterion
amended: "validator green" becomes "validator green AND content-minimum checks pass
(Carmack R2 criteria) AND timestamp-sanity check passes (no future-dated entries in
tracking files — bash one-liner against current UTC)". Validator-upgrade ticket goes
in the decree for Council 2: the validator certifies taxonomy; truth needs content gates.

## RULING D — DELIVERED-HOME CORRUPTION: CONTAIN AT STAGE 6, ROOT-CAUSE FOR C2
15/20 wrong identity fields + tag-query returning 0 against 12 disk matches = the
expert fleet is unreachable cold through 2 of 3 retrieval paths. Endorse Lilith's
sequencing (discovery → identities → timestamps/statuses) as Council 2 order.
Immediate containment within THIS run, per existing R3 adjudication: MaKaLi applies
CORRECTED payloads at Stage 6 (single-writer privilege) — canonical values:
subagent_type="node", entity=node's own tag, tags exactly
["expert","pageable","domain:<N>","express:first-light"].
NEW Stage 6 gate addition: POST-APPLICATION RETRIEVAL VERIFICATION —
task_registry_query(tags=["express:first-light"]) MUST return ≥10 before
delivered-home is declared complete. Root cause hypothesis for decree: packets did
not specify exact field values, so nodes copied arm identity. Fix is packet template
precision (Council 2 spec).

## FINDINGS ACKNOWLEDGED (feeding synthesis)
Enforcement-vs-text delta as THE systemic defect class (M27 gates never installed;
doc-llm-validate 7/1533 and cannot fail; hdp_ schema nonexistent; {session_model}
unsubstituted; agent instructions[] absent from schema) — this is the decree's spine.
Future-dated recurrence post-publication — preserve the timeline as Exhibit A.

— kali, Consultant. No pages issued (Hop Rule held). Corrections propagate via this
file + Hivemind broadcast only.
