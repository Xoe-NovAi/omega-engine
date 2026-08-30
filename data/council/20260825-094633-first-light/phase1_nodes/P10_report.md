<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# P10 REPORT — Node N10 (Validation) — CROSS: Enforcement-vs-Text Delta Sweep + Run-Side QA + Delivered-Home Registration Audit
⬡ OMEGA ⬡ NODE10-VALIDATION ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n10 ⬡ P12-DISPATCH
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith (Run Arm) | **Orchestrator**: makali_fusion
**Task Registry**: `express-c1-node10-20260825` (registered 2026-08-25T13:49:43Z)
**Provenance**: every finding tagged `source_node: N10`, `tier:` noted per finding. RECON ONLY — zero production mutations; writes confined to `data/council/20260825-094633-first-light/phase1_nodes/`.
**RAW REPORT — written to disk BEFORE digestion/summary work (§C.5)** · Wall clock at write: **2026-08-25T13:54Z** (`date -u` verified)

---

## §0 EXECUTIVE VERDICT

The fleet's instruction layer systematically **over-promises enforcement that does not exist mechanically**. My three-part cross audit produced: **(Part 1)** 8 delta findings across S1-S8 — headline: M27's pre-commit tracking gate is *declared but never installed* (`.pre-commit-config.yaml` defines `omega-tracking-state`; the actual `.git/hooks/pre-commit` is a hand-rolled soul-check script that never runs it), and the Delivered-Home expert fleet is **invisible to its own discovery tool** (`task_registry_query(tags=["express:first-light"])` returns 0 results against 12 on-disk matching records). **(Part 2)** Run-side QA: P6/P7/P8 are evidence-backed and severity-sane; P9 contains one overstated claim (run-side registrations "correct") and one buggy acceptance-criterion snippet; zero CRITICAL-HALTED conditions anywhere; one numeric disagreement (93 vs 95 vs 97 tasks) resolved as snapshot-timing artifact. **(Part 3)** Registration audit: sibling's build-side claim CONFIRMED and quantified — build nodes carry `subagent_type="maat"` **5/5**; run-side has mirror defects (`subagent_type="lilith"` on node7/node10; `entity` wrong on **all 5** run nodes); **3 future-dated checkpoints** including one created AFTER N8 published its future-dating finding — the defect class is active, not historical.

---

## PART 1 — ENFORCEMENT-vs-TEXT DELTA SWEEP (S1-S8)

Method: broad sampling, one to three probes per surface, each probe bash-executed this session. Depth on individual surfaces belongs to siblings; I own the deltas.

### X-1 · HIGH — M27 pre-commit enforcement is configured but NOT installed: the mandate text asserts enforcement that cannot fire
`source_node: N10 | tier: S2-vs-mechanics`
- **Text claim**: SOVEREIGN_MANDATES.md M27 Enforcement: *"Pre-commit hook: `omega-tracking-state` blocks commits with corrupted tracking state"* (also CI-gate claims). M14 similarly claims *"Pre-commit hook blocks commits adding unvetted tags"*.
- **Reality**: `.pre-commit-config.yaml:137` DOES declare `omega-tracking-state` (entry: `python scripts/validate_tracking_state.py`) plus a full mandate-hook suite (omega-check-m1-anyio, m7/m8/m9/m23, detect-secrets…). But the **pre-commit framework is not installed in this repo**: `.git/hooks/pre-commit` is a custom bash script containing ONLY the soul-integrity loop (`validate_soul.py`) — zero pre-commit-framework boilerplate, zero references to tracking or any omega-check hook (verified: `grep -c "tracking" .git/hooks/pre-commit` = 0). Declared hooks never execute on commit. A commit corrupting tracking state sails through today; only CI/manual runs would catch it.
- **Context**: Team-Study synthesis (2026-08-23) ordered "pre-commit framework install per Ma'at F1 ordering" — i.e., known-pending, but the mandate text reads as present-tense fact. Text-vs-reality delta, not unknown debt.
- **Acceptance criteria (fix)**:
  ```bash
  # After install: framework boilerplate present AND hook fires on a bad-state dry run
  grep -q "pre-commit" .git/hooks/pre-commit && echo INSTALLED || echo MISSING
  pre-commit run omega-tracking-state --all-files 2>&1 | tail -1   # expect: Passed (or targeted failure output, not silence)
  ```

### X-2 · HIGH — Delivered-Home expert fleet invisible to its own discovery tool (registry/tool split-brain)
`source_node: N10 | tier: S1-tooling`
- **Claim (plan §6.5)**: each Node registers as a pageable specialist; "future councils page it cold and get warm-start performance."
- **Reality**: `omega-hub_task_registry_query(tags=["express:first-light"])` → `{"tasks": [], "count": 0}` at 13:50Z — while `data/coordination/TASK_REGISTRY.json` on disk contains **12 records carrying that exact tag** (verified line-level: rg hits at :1785–:1996). The sanctioned discovery interface cannot find the council's flagship deliverable by its mandated tag. Either the MCP tool reads a different store, caches, or its tag filter is broken — any of which means a future council paging `domain:cognition` etc. through the tool gets nothing and may conclude the experts don't exist.
- **Corollary observed**: the `grep` MCP tool also returned a false negative on the same file minutes earlier (pattern `express-c1-node|express:first-light` → "No files found"; `rg` immediately found 24 hit lines). Two independent tooling false-negatives against the same SSOT file in one session.
- **Acceptance criteria (fix)**:
  ```bash
  # Tool result must match disk truth:
  jq '[.tasks[] | select(.tags // [] | index("express:first-light"))] | length' data/coordination/TASK_REGISTRY.json
  # ^ prints 12 today; task_registry_query(tags=["express:first-light"]).count must equal this number.
  ```

### X-3 · MED — `AGENTS.md` is cited everywhere as a root instruction file; it lives at `.agents/AGENTS.md`
`source_node: N10 | tier: S2-path-integrity`
- **Evidence**: mission packet §Role ("Delegation Protocol in `AGENTS.md`"), plan §10 ("Read … `AGENTS.md`"), SOVEREIGN_MANDATES references. `ls AGENTS.md` → **No such file**; actual: `./.agents/AGENTS.md`. Any agent or tool resolving the cited path literally fails; convention-dependent resolution is silent guesswork.
- **Acceptance criteria**: `test -f AGENTS.md || test -f .agents/AGENTS.md` should resolve ONE canonical path cited identically in all instruction files: `rg -c '\bAGENTS\.md\b' docs/strategy/*.md *.md | wc -l` citations all point at the same locant after fix.

### X-4 · MED — M26 scope claim vs gate reality (~200× coverage gap) — INDEPENDENTLY CONFIRMED (corroborates P7 F7-01)
`source_node: N10 | tier: S6-vs-M26`
- M26: "All reference documentation MUST pass `make doc-llm-validate`." Makefile target (lines ~177-186, read this session) validates **only `docs/sprints/current/`**. P7 measured 7 files vs 1,533 md docs. My read confirms the target argument verbatim. Additionally confirmed P7 F7-08.3: `sprint-plan-llm` builds "current" sprint content by concatenating `docs/archive/sprints/...` sources — active machinery fed from archive.
- **Acceptance criteria**: as P7 F7-01 (adopt theirs; not duplicated here).

### X-5 · MED — Plugin registration dead paths (S7/S3) — INDEPENDENTLY CONFIRMED (corroborates P6 F-01)
`source_node: N10 | tier: S7-config`
- `jq -r '.plugin[]' opencode.json` → two `file://…/.opencode/plugin/{error-capture,awareness}.ts` entries; `ls .opencode/plugin` → **No such directory**; files live in `.opencode/plugins/`. Silent-failure mode exactly as P6 described (auto-discovery masks it).
- **Acceptance criteria**: as P6 F-01.

### X-6 · MED — Future-dated checkpoints CONTINUED AFTER the defect was published mid-council; validator stays green beneath them
`source_node: N10 | tier: S1-drift-live`
- N8 published the future-dating finding (F-1) at ~13:41Z citing node1/node6 (`13:45:00Z`). At **13:53:21Z** I ran the check myself: `express-c1-node9-20260825` now carries `last_checkpoint: 2026-08-25T13:55:00Z` — written ~13:48Z, i.e., a NEW instance of the same fabrication class created after detection. Simultaneously `python3 scripts/validate_tracking_state.py` → **"ALL TRACKING STATE CHECKS PASSED"** (exit 0) with the future entry present. Confirms P8 F-9: green ≠ truthful; the future-date check is absent, and awareness of the defect did not change behavior.
- **Acceptance criteria**: as P8 F-1 criterion #2 (validator gains future-date error check). Re-run command:
  ```python
  # must exit 1 today; exits 0 → check still missing
  import json;from datetime import datetime,timezone
  now=datetime.now(timezone.utc);d=json.load(open('data/coordination/TASK_REGISTRY.json'))
  bad=[t['task_id'] for t in d['tasks'] if t.get('last_checkpoint') and datetime.fromisoformat(t['last_checkpoint'].replace('Z','+00:00'))>now]
  assert not bad, bad
  ```

### X-7 · LOW — Heartbeat-cadence text drift inside the council's own instruction stack
`source_node: N10 | tier: S2-taper`
- Plan M5: "~10 min … single unified figure — **supersedes any '5 min' elsewhere**." Packet §C.7: "~10min". But `data/entities/lilith/soul`-derived standing instructions (this session's injected prompt) still say "Every 5-10 min during long ops". The claimed supersession never propagated to the instruction files it supersedes — a live specimen of the taper problem S5/N5 audits.
- **Acceptance criteria**: `rg -n "5-10 min" data/entities/*/soul.yaml .opencode/agents/*.md` → 0 hits (or amended to reference M5) after propagation.

### X-8 · LOW (positive controls) — Claims that HELD under probe
`source_node: N10 | tier: cross`
- `.firecrawl/` cache exists (29 entries) — SR-V1 "check cache first" is grounded, not decorative.
- GAP_REGISTRY mode anomaly (P8 F-8) reproduced: `stat` → GAP_REGISTRY.json **600**, ACTIVE_SPRINT.json 664.
- WAKE_STATE "129 files uncommitted" vs `git status --porcelain | wc -l` = **8** (P8 F-5 reproduced exactly).
- Live pending handoff `ho_2e6018bdb1ad.json` schema = `ho_*` keys (`source_agent_id`…), no `trace_id/task_type/ttl_seconds`; protocol doc :55/:58 mandates `hdp_{YYYYMMDD}_…` + required `parent_trace_id` (P9 F-1 reproduced exactly).
- Security bright line (M8): **no secrets, no active external telemetry encountered in any probed surface → NO CRITICAL-HALTED.**

---

## PART 2 — RUN-SIDE QA (P6, P7, P8, P9)

Verdict per report, then cross-report analysis.

### P6 (N6, S3 mechanics) — PASS, high quality
- Evidence-backed: every claim traces to named probes E1-E8; I independently reproduced its two most load-bearing claims (X-5 plugin paths; markdown-agent loading corroborated by this session's own injected prompt being lilith.md body verbatim). F-07's claim that protocol documents register as invokeable agents is corroborated by my OWN system prompt (CONVERSATIONAL_SUBAGENT_PROTOCOL / NODE_ONBOARDING_PROTOCOL / STALLED_SUBAGENT_RECOVERY appear in my available-agents list).
- Severities sane (F-01/F-02 HIGH appropriate; INFO positives properly separated).
- No unsupported claims found.

### P7 (N7, S6 docs) — PASS, high quality
- Independently reproduced: doc-llm-validate scope (X-4) and archive-fed sprint generation (X-4). Link-rot and orphan counts (34/35; 43/77) are method-plausible; not fully recomputed (link-checker script class, low risk of method error; flagged as QA-trust rather than verified).
- Severity calls sane; F7-01 HIGH justified because temple-grade T2 inherits the rubber stamp.

### P8 (N8, S1b drift) — PASS, strongest report; partially superseded by events
- Reproduced: F-1 (future dates — now worse, see X-6), F-5 (129-vs-8), F-8 (mode 600), F-9 (validator green over future entry — executed live).
- F-2 (7-day boundary blind spot, 5 zombies) not independently recomputed; internally consistent with quoted validator code lines; accepted as plausible-unverified.
- Its registry count "93 tasks" was true at its ~13:35Z snapshot; see timing note below.

### P9 (N9, S8 coordination) — PASS WITH CORRECTIONS
- Reproduced: F-1 schema divergence (exact), queue-count consistency method sound.
- **QA-C1 [ERROR in P9 F-7]**: P9 states run-side nodes registered "correctly (node6, node8, node9 as subagent_type/entity)". Half-true: `subagent_type` is correct for node6/8/9, but `entity` is `"lilith"` for ALL run-side nodes (node6-node10) — none carries its node tag as entity. And P9 omits that node7 and node10 carry `subagent_type="lilith"` (wrong). Corrected matrix in Part 3 below. Severity of the underlying issue unchanged (P9's HIGH stands); the claim text needed correction.
- **QA-C2 [buggy acceptance criterion, P9 F-7]**: the python one-liner `t['task_id'].split('node')[1][0]` extracts one character after "node" — for `express-c1-node10-20260825` it yields `"1"`, compares against `"node1"`, and would report a FALSE violation for a correctly-registered node10. Fix: regex `re.match(r'express-c1-node(\d+)-', t['task_id'])` and compare int(group(1)).
- **QA-C3 [numeric disagreement, resolved]**: P8 says TASK_REGISTRY = 93 tasks (~13:35Z); P9 says 95 (~13:43Z); N10 measured **97** (13:53Z). All three honest snapshots of a file growing ~1 record/5min during live council registration. Not a contradiction — but reports MUST stamp snapshot wall-clock next to counts (both did; synthesized readers should diff timestamps before crying corruption).
- No contradictory verdicts between run-side reports otherwise; P9 F-7 explicitly corroborates P8 F-1 with matching evidence.

---

## PART 3 — DELIVERED-HOME REGISTRATION AUDIT (plan §6.5 compliance)

Snapshot: `data/coordination/TASK_REGISTRY.json` @ 2026-08-25T13:53Z, 97 tasks total, 12 carrying `express:first-light` (10 nodes + 2 arms).

### 3.1 Compliance matrix (required: task_id format ✓ all; tags ⊇ {expert, pageable, domain:<N-domain>, express:first-light}; entity = node<N>; subagent_type = node identity per packet §C.6 "subagent_type your entity"; status valid per M27)

| Record | subagent_type | entity | launched_by | status | tags OK | Defects |
|---|---|---|---|---|---|---|
| express-c1-node1 | **maat** ✗ | node1 ✓ | maat | completed | ✓ | subagent_type=arm; **future ckpt 13:45:00Z** |
| express-c1-node2 | **maat** ✗ | **maat** ✗ | maat | **in_progress** ✗ | ✓ | double-wrong identity; status lags reality (P2 on disk 13:27Z + Hivemind COMPLETE 13:26Z) |
| express-c1-node3 | **maat** ✗ | node3 ✓ | maat | **in_progress** ✗ | ✓ | subagent_type; status lags (P3 disk 13:35Z + broadcast) |
| express-c1-node4 | **maat** ✗ | node4 ✓ | maat | **in_progress** ✗ | ✓ | subagent_type; status lags (P4 disk 13:47Z + broadcast) |
| express-c1-node5 | **maat** ✗ | node5 ✓ | maat | in_progress | ✓ | subagent_type; legitimately in flight |
| express-c1-node6 | node6 ✓ | **lilith** ✗ | **makali_fusion** ✗* | completed | ✓ (+report: tag) | entity=arm; launched_by skipped arm (*orchestrator-of-record ambiguity); **future ckpt 13:45:00Z** |
| express-c1-node7 | **lilith** ✗ | **lilith** ✗ | lilith | **in_progress** ✗ | ✓ | both identity fields = arm; status lags (P7 disk + broadcast 13:29Z) |
| express-c1-node8 | node8 ✓ | **lilith** ✗ | lilith | completed | ✓ | entity=arm; ckpt 13:41:14Z REAL-TIME ✓ (the only clean timestamp in the fleet) |
| express-c1-node9 | node9 ✓ | **lilith** ✗ | lilith | completed | ✓ | entity=arm; **future ckpt 13:55:00Z** (post-dates N8's own finding) |
| express-c1-node10 | **lilith** ✗ | **lilith** ✗ | lilith | in_progress (self, legit) | ✓ | both identity fields = arm (this node; will remain as-written-honest record) |
| express-c1-runarm-lilith | lilith ✓(arm) | lilith ✓ | makali_fusion | in_progress | ✓ | fine; missing the `arm` tag its sibling carries |
| express-c1-arm-maat | maat ✓(arm) | maat ✓ | makali_fusion | in_progress | ✓ (+arm) | fine |

### 3.2 Quantified verdicts
- **Sibling claim VERIFIED & EXTENDED**: build nodes with `subagent_type="maat"` = **5/5** (N1-N5), not merely "some".
- **Run-side mirror defect**: `subagent_type` wrong on **2/5** (node7, node10 = "lilith"); `entity` wrong on **5/5** (all "lilith", none carries node<N>).
- **Identity-field correctness overall**: subagent_type 3/10 nodes correct; entity 5/10 (build) + 0/5 (run) = 5/10. Per P8-F6 glossary proposal (subagent_type=node identity, entity=hivemind tag), **15 of 20 identity fields across the 10 node records are wrong**.
- **Future-dated checkpoints**: 3/10 node records (node1, node6, node9) — 100% fabricated-timestamp class, 0% derived-from-clock class except node8.
- **Status lag**: 4/10 node records say `in_progress` despite report-on-disk + Hivemind completion broadcast (node2, node3, node4, node7) — the exact lag-drift mode N8 F-1 defined.
- **Tag-set compliance**: 12/12 carry the required 4-tag set ✓ (only bright spot). Inconsistency: `report:P6_report.md` pointer tag exists only on node6; domain-tag format splits into two conventions (`domain:N1-infrastructure` build vs `domain:cognition` run).
- **Delivered-Home impact**: paging by `subagent_type=node2` finds nothing; paging by "maat" misroutes to the Build Arm; paging run experts by entity=node8 finds nothing (entity=lilith routes to the Run Arm). Combined with X-2 (discovery tool returns 0 by tag), **the expert fleet is currently unreachable cold through 2 of 3 retrieval paths** (tool query broken; subagent_type/entity unreliable; only task_id exact-match works).

### 3.3 Acceptance criteria (repair spec for Council 2 / single-writer MaKaLi)
```bash
python3 - <<'EOF'
import json,re
d=json.load(open('data/coordination/TASK_REGISTRY.json'))
bad_st,bad_en=[],[]
for t in d['tasks']:
    m=re.match(r'express-c1-node(\d+)-',t.get('task_id',''))
    if m:
        n=f"node{m.group(1)}"
        if t.get('subagent_type')!=n: bad_st.append(t['task_id'])
        if t.get('entity')!=n: bad_en.append(t['task_id'])
print("wrong subagent_type:",bad_st)  # target []
print("wrong entity:",bad_en)          # target []
EOF
```

---

## §FINDINGS SUMMARY TABLE

| ID | Sev | Surface | One-line |
|---|---|---|---|
| X-1 | HIGH | S2/mechanics | M27/M14 pre-commit gates declared in config, never installed; active hook is soul-check only |
| X-2 | HIGH | S1/tooling | task_registry_query(tag)=0 vs 12 on-disk matches — Delivered-Home discovery broken |
| X-3 | MED | S2 | AGENTS.md cited at root; lives at .agents/AGENTS.md |
| X-4 | MED | S6/M26 | doc-llm-validate covers docs/sprints/current only (~200× scope gap); archive feeds "current" sprint gen (confirms P7) |
| X-5 | MED | S7/S3 | Dead plugin registration paths, silent (confirms P6) |
| X-6 | MED | S1/live | Future-dated checkpoint created AFTER defect published; validator green beneath it |
| X-7 | LOW | S2/taper | Heartbeat cadence supersession (M5) never propagated to instruction files |
| QA-C1 | MED (QA) | P9 | P9 overstated run-side registration correctness; corrected matrix herein |
| QA-C2 | LOW (QA) | P9 | Buggy acceptance snippet (node10 parsing) |
| QA-C3 | LOW (QA) | P8↔P9 | 93/95/97 count disagreement = snapshot timing, stamped times reconcile |

No CRITICAL-HALTED. No TOOL-CHAIN-COLLAPSE (one MCP grep false-negative worked around via bash rg — logged X-2 corollary, non-blocking).

---

## §HANDOFF PACKET (Delivered-Home Doctrine §6.5)

### Warm-start reading list (ordered)
1. `data/council/20260825-094633-first-light/phase0_mission_packet.md` §B/§C + plan §6.5 — what the registrations were supposed to be
2. `data/coordination/TASK_REGISTRY.json` lines 1770-2000 — the 12 express records (my §3.1 matrix maps 1:1)
3. `scripts/validate_tracking_state.py` — note absence of future-date check (X-6)
4. `.pre-commit-config.yaml` vs `.git/hooks/pre-commit` — the declared-vs-installed gap (X-1)
5. P8_report.md F-1/F-9 then THIS report §X-6 — the future-dating story arc (found → published → recurred)
6. `data/coordination/TRACKING_ARCHITECTURE.md` — where P8's proposed field glossary must land

### Standing orders for future councils
1. **Never retrieve pageable experts by tag-query or entity alone** until X-2 is fixed — retrieve by exact task_id, then verify subagent_type/entity against the §3.1 glossary before dispatch.
2. **Never trust a pre-commit enforcement claim without reading `.git/hooks/pre-commit`** — config-declared ≠ installed (X-1 generalizes to every "hook blocks X" sentence in the mandates).
3. **Recompute registry timestamps from Hivemind last_seen**; treat any hand-written checkpoint as fabricated until provenance shown (X-6: the defect recurred same-day after publication).
4. When QA-ing sibling reports, **diff their snapshot timestamps before declaring numeric contradictions** (QA-C3).
5. Repair sequencing for Council 2: fix retrieval (X-2) BEFORE mass-editing registrations (§3.3), else you repair records into an index nobody can search.

---

## §COORDINATION LEDGER
- Registered `express-c1-node10-20260825` 13:49:43Z; Hivemind presence posted under `node10` (ses_6aea91648c81, 13:50:06Z); heartbeats at cadence; awareness checked start (13:49) and end.
- Consultant page (§C.9/M11): attempted once post-report — outcome recorded in ledger addendum below (depth-limit expected per N1/N6/N7/N8/N9 precedent).
- Production mutations: NONE. Writes confined to this directory + Hivemind posts.

*source_node: N10 · tier: cross · raw report written to disk BEFORE digestion per §C.5 · 2026-08-25T13:55Z*

---

## §ADDENDUM A (13:57Z — captured during write-back)

### X-9 · LOW-MED — `data/entities/lilith/proposed_lessons.yaml` is INVALID YAML at the tail; M11 ingestion of this file would crash
`source_node: N10 | tier: S2/M11-pipeline`
- LSP/YAML diagnostics on write-back: lines 374-377 carry a final lesson as a BARE top-level mapping (`- narrative:` seq-item glued after the closed list) instead of a proper `- id:/tier:/...` list item inside the session block. Any `yaml.safe_load` of the file raises — meaning the soul-distillation staging file for the Run Arm's own entity cannot be machine-ingested until repaired. Corroborates lilith-20260821-002 (soul loop operationally open) with a NEW concrete failure instance: not just approval-flip missing — the staging file itself is unparseable.
- Also observed: `config/omega.yaml:73` duplicate map key (Map keys must be unique) — pre-existing, out of council scope, logged for S7 follow-up.
- **Acceptance criteria**: `python3 -c "import yaml;yaml.safe_load(open('data/entities/lilith/proposed_lessons.yaml'))" && echo OK` → OK after restructuring lines 374-377 into a proper list item with id/tier/category fields.
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:03Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

