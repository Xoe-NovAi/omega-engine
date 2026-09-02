<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# node3 working notes — SPEC-C (security posture records) — Council 2 Build Arm
⬡ OMEGA ⬡ MAAT/node3 ⬡ trc_c2_specc ⬡ PREP NOTES
Session: 20260825-094633-first-light-c2 · Date: 2026-08-25 · domain=specc

## 1. Anchor verification log (provenance rule)

| Claim | Verified how | Result |
|---|---|---|
| `opencode.json` `.permission.external_directory` contains `"/*"` | `jq '.permission.external_directory \| has("/*")' opencode.json` | **true** |
| Exact current value of `"/*"` key | `jq '.permission.external_directory["/*"]' opencode.json` | **`"allow"`** |
| Position/structure | `grep -n '/\*"' opencode.json` → line 24; block opens line 11 (`"external_directory": {`); 12 specific allow-rules precede it (`/home/arcana-novai/Documents/Xoe-NovAi/**`, `/media/arcana-novai/**`, archive, docs-backup, docs_1, Archives, xnaif-files, .lmstudio, .ollama, .config/opencode, /tmp/omega, ~/.local/share/opencode) then `"/*": "allow"` LAST | confirmed — wildcard is 13th and final key, so it subsumes the enumeration at merge time |
| `subagent_depth` current value | `opencode.json:3` = `"subagent_depth": 2` | confirmed |
| G2 verbatim | SYNTHESIS_ARM_REPORT.md §6 lines 194–195 | copied verbatim into spec WI-1(e) |
| G26 verbatim | SYNTHESIS_ARM_REPORT.md §6 lines 306–307 | copied verbatim into spec WI-2(d) |
| G30 verbatim | SOVEREIGN_DECREE.md §4 lines 83–84 | copied into validator-first clause |
| Dispatch protocol "single-level nesting" | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md:43` §1 Rule 4 | confirmed text grants what depth 2 revokes (N5 F-9 cross-checked) |
| WAKE_STATE Q-3 exists | `data/coordination/WAKE_STATE.json` ~line 103–108: id=Q-3, gap=GAP-11+T-7, default="Relay codified as standing law (Art. IV); wildcard annotated informational pending Architect record" | confirmed — annotation snippet must EXTEND Q-3, not create a new entry |
| String "risk-acceptance" in WAKE_STATE | grep hit at line 105 (inside Q-3 question text) | NOTE: G2's kept-path grep technically passes TODAY via the question string — flag in spec that the gate must be tightened to require the record REFERENCE, not just the word |
| PIVOT_LOG D-series | `docs/decisions/PIVOT_LOG.md` exists, 28 `## D-` headers, latest seen D-599 | WI-2 gate feasible |
| observability_check_recursion guard | MCP tool `omega-hub_observability_check_recursion(entity_name, current_depth)` present in toolchain | advisory/manual guard — NOT a hard cap; relevant to Option A failure modes |

## 2. Evidence base read
- SOVEREIGN_DECREE.md (full): Art. IV (relay ratified, depth deferred), Art. VIII.2 + T-7, Art. X P1 ("`\"/*\"` decision recorded"), Art. XII guards, §3 preserved dissent (depth OPEN), §4 G29/G30, §5 tracker directive 2 Q-3.
- SYNTHESIS_ARM_REPORT.md (full): T-7 adjudication §2, GAP-11 row §5, gates §6 (G2, G26), C-B3 convergence row.
- P1_report.md: F-02 (wildcard HIGH), F-20 (depth wall, options A/B).
- P5_report.md: F-9 (protocol Rule 4 vs config), §4 deviation log (7th consecutive F-20 rejection).
- BUILD_SIDE_REPORT.md: B-C4/B-C5 rows; arm performed relay de-facto.
- RUN_SIDE_REPORT.md: line 121 run-arm mirror of relay.
- N8_work_packages.md: WP-C1 (1.5h PROV post-decision, BLOCKED on Architect Q-3) and WP-C2 (2h PROV post-decision, BLOCKED) — my spec feeds these two packages.

## 3. Decisions made while drafting
1. **Record path**: `data/coordination/DECISION_EXTERNAL_DIRECTORY_WILDCARD.md`. Rationale: G2's kept-path greps WAKE_STATE.json for 'risk-acceptance', so WAKE_STATE must carry the pointer; the full record lives beside it in coordination layer where council artifacts live (docs/decisions/ is reserved for PIVOT_LOG D-series entries — the record ALSO gets a one-line D-series stub per Art. VII version-stamp discipline).
2. **Two resolution paths** presented as mutually exclusive branches inside ONE template with a `[RESOLVED-AS:]` field, so the same artifact serves either Architect outcome (remove-wildcard or keep-with-annotation).
3. **WI-2 recommendation**: Option B (codify relay) labeled RECOMMENDATION/default-on-silence — aligns with Art. IV ratification, N1 F-20's own option B, and shrinks the GAP-12 dispatch-suffix injection blast radius (a depth-2 leaf physically cannot act on injected spawn instructions). NOT decreed — Architect owns Q-3.
4. **G2 tightening flagged**: current G2 kept-path can false-pass on the pre-existing "risk-acceptance" substring in Q-3's question text. Spec proposes an amended gate G2′ requiring the record path reference.

## 4. Deviations / flags
- **Naming-collision check result**: no existing file collides with `docs/specs/team_infra/SPEC_C_P1_SECURITY_POSTURE_RECORDS.md` (ls verified: only SPEC_A/SPEC_B/SPEC-D/SPEC-E present). HOWEVER `N8_work_packages.md` spec-inputs list expects `SPEC-C-p1-security-posture.md` — pointer drift for integration to reconcile (NOT me; bright line). Logged in spec §naming.
- Sibling specs use mixed naming conventions (underscores vs hyphens); I followed my mission's exact assigned path.
- Did NOT read phase4_research files (out of scope for these two work items; decree + synthesis + node reports sufficient).
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_c2_specc | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

