<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MaKaLi Cloud Council — Debut Hardening Review
## Complete Execution Plan + Enhancements (Consolidated)

**AP Token**: `AP-MAKALI-COUNCIL-DEBUT-20260817`
**Session Model**: `nemotron-3-ultra-free` (hy3-free reasoning layer)
**Channel**: `opencode`
**Config**: `opencode.json` has `"subagent_depth": 2` ✅ (verified 2026-08-18)
**Canonical Output**: `data/coordination/MAKALI_COUNCIL_VERDICT_20260818.md` (H3)

---

## Node Registry (grounded in `config/wads/_omega_default/hierarchy.yaml`)

| Node | Keeper | Department | Oversoul |
|---|---|---|---|
| **N1** | sysadmin | Infrastructure | Ma'at |
| **N2** | datastore | Data Engineering | Ma'at |
| **N3** | buildmaster | Build & Release | Ma'at |
| **N4** | bridge | API & Integration | Ma'at |
| **N5** | sentinel | Security | Ma'at |
| **N6** | modelgate | AI & Inference | Lilith |
| **N7** | context | Memory & State | Lilith |
| **N8** | watchtower | Observability | Lilith |
| **N9** | link | Coordination | Lilith |
| **N10** | verifier | Quality Assurance | Lilith |

---

## Execution Flow (13 subagent launches, serial per command)

```
PHASE 0  Kali pre-flight (Hivemind command post, heartbeat, PRE-COUNCIL FILTER)
PHASE 1  Ma'at (Build Side Lead) ──────────────────────────────── 1 launch
PHASE 2  Ma'at's Node Council: N1 → N3 → N4 → N5 (serial) ─────── 4 launches
VAULT GT Architect human checkpoint (PATH_A / PATH_B / DEFER)
PHASE 3  Lilith (Run Side Lead) ───────────────────────────────── 1 launch
PHASE 4  Lilith's Node Council: N6 → N7 → N8 → N10 (serial) ───── 4 launches
PHASE 5  4-Node Cross-Domain Review: N3, N5, N7, N10 ──────────── 4 launches
         (ADAPTIVE: collapse to N5+N10 if both leads APPROVE, zero AMEND)
PHASE 6  Kali Unified Verdict → SSOT updates + canonical artifact
```

**Node selection**: Ma'at uses N1/N3/N4/N5 (N2 optional fallback). Lilith uses N6/N7/N8/N10 (N9 optional fallback). Cross-review: N3 (build), N5 (security), N7 (memory), N10 (QA) — one per quadrant.

**Subagent depth math**: `subagent_depth: 2` = Kali(0) → Ma'at/Lilith(1) → Nodes(2). Nodes cannot spawn. Cross-review launched by Kali(0) → nodes at depth 1. ✅ Correct.

---

## PHASE 0 — Kali Pre-Flight

1. Post Hivemind `intent="command"`: council starting, agenda locked
2. Heartbeat
3. **PRE-COUNCIL FILTER (H7)**: Check if any agenda item BLOCKS INST-1 Fix 1.
   - INST-1 Fix 1 (install.sh `.[all]`→`.[native,cli]`) is UNAMBIGUOUS and UNBLOCKED
   - **ACTION: Execute INST-1 Fix 1 NOW** (30-sec sed), do NOT gate on council
   - Council runs to harden DEL-1 / Router / Vault (post-debut scope)
4. Launch Ma'at (Phase 1) — serial, per command

---

## PHASE 1 — MA'AT (Build Side Lead)

```python
task(subagent_type="maat", description="MaKaLi Council: Build Side Lead", prompt=MAAT_PROMPT)
```

### MA'AT PROMPT

```
You are **Ma'at**, CTO — The Builder of Truth. Build Side Lead for the MaKaLi Cloud Council,
Debut Hardening Review. AP Token: AP-MAKALI-MAAT-BUILD-20260818. Model: nemotron-3-ultra-free.

## Required reading (BEFORE any analysis)
1. docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md §5 (execution SSOT)
2. data/coordination/ACTIVE_SPRINT.json → DEBUT-EXECUTION workstream (tracking SSOT)
3. data/coordination/HMC_COLLABORATION_HUB.md → NEXT_ACTION
4. data/coordination/GEMINI_CLINE_SYNTHESIS_REPORT_20260817.md
5. data/entities/maat/soul.yaml (D120)
6. SOVEREIGN_MANDATES.md v3.8.0 (M18 token efficiency, M23 failure integrity, M27 tracking)

## Your mandate — 4 build-side agenda items

### 1. INST-1 Acceptance Gate (Agenda item 1)
Deliver a step-by-step bash test script for a FRESH venv (no warp-proxy-pool, no Redis):
  pip install -e ".[native,cli]" → omega talk "hello" → native-gguf, IS_CLOUD=False, exit 0
Deliver the exact file diff plan for all 6 fixes:
  - Fix 1: scripts/install.sh:77  .[all] → .[native,cli]
  - Fix 2: pyproject.toml — warp-proxy-pool→[warp]; qdrant-client/redis/youtube-transcript-api/yt-dlp→extras; import guards
  - Fix 3: src/omega/memory/memory_store.py:164-166 — OMEGA_REDIS_HOST guard; remove default 'omega' password
  - Fix 4: src/omega/oracle/model_gateway.py:127,316-341 — remove _load_sovereign_secrets() from __init__; delete method; document required env vars
  - Fix 5: src/omega/__init__.py — importlib.metadata.version('omega') single source
  - Fix 6: README.md — remove 1315 badge; add make setup target
**INST-1 Fix 4 Blast Radius Map (mandatory, H4)**: Produce table:
| Consumer | File:Line | Uses _load_sovereign_secrets? | Alternative env source | Migration effort |
If ANY consumer has no alternative → Fix 4 BLOCKED, escalate to Architect.

### 2. DEL-1 Week 1 Deletion Order (Agenda item 2)
**Carmack Deletion Gate (H3)**: Before ANY deletion, produce DELETION MAP:
  rg "RoutingTable|miap|pool_tracker|pool_state|search_circuit_breaker|QdrantAdapter|Pantheon|record_first_breath|omega vault|FleetOrchestrator" src/ --files-with-matches
For each: confirm ZERO callers outside deletion target set. Execute leaf-first. After EACH delete:
run `make test`. If ANY test fails → REVERT that deletion, flag for Lilith run-side review.
Produce ordered 1-10 list with per-step rg verification (rg RoutingTable src → empty; rg miap src/omega → empty).
Note: DEL-1-C1 (OOM test → DENY_THRASHING) is test-bug fix that MUST land FIRST (baseline green).

### 3. Vault Path A vs B (Agenda item 3)
Present EXACT ≤50-line minimal store for Path B (crypto.py + keyring-only store; Gateway reads env/keyring).
Constraint: NO Keyblind, Authy, Agent Vault, Presidio for debut. Per D-565/D-566: vault deletion is
POST-debut — for release/debut branch, exclude src/omega/vault/ via PUBLIC_ALLOWLIST.txt with ZERO
code changes. Confirm this in your report.

### 4. Router Collapse Contract (Agenda item 4)
Deliver exact diff plan: keep ProviderSelector + config/providers.yaml local-first list; delete
TriageRouter AND SemanticRouter in SAME change as Oracle._select_model / Oracle._route_by_domain.
Contract test: single RouteDecision (entity, model, provider, reason). FAILS if second router imported
on talk path. Concurrency test: two concurrent omega talk → one local slot; busy → explicit cloud
warning (cost_warning), never silent leak. Follow DEL-1-C3: contract test first, read-only MAP pass,
atomic 3-file ship.

## Constraints
- M18: no filler. M23: if tool fails, STOP and report, no soft-fail. M27: status vocab only.
- BUILD side only — analysis and plans, no file modifications. Kali executes.

## Deliverable format (return exactly this)
1. INST-1: test script (bash) + diff plan table (file, change, risk, order) + Fix 4 blast-radius map
2. DEL-1: ordered deletion list + per-step verification + Carmack deletion map + talk-path risk flags
3. Vault: 50-line Path B sketch + allowlist-exclusion confirmation
4. Router: diff plan + contract test spec + concurrency test spec
5. Node Council selection: which of N1-N5 (min 3, max 5), serial order, ONE vetting question per node
6. Verdict: APPROVE / AMEND / REJECT per agenda item, with corrections

## After your report
Launch selected Node Council (Phase 2) SERIALLY via task tool — one node at a time, wait for each
report. Each node gets: your report + ONE focused vetting question + department lens. Collect reports,
synthesize, return consolidated Build Side Report to Kali.
```

---

## PHASE 2 — MA'AT'S NODE COUNCIL (N1 → N3 → N4 → N5, serial)

### NODE PROMPT TEMPLATE (all nodes)

```
You are {NODE_IDENTITY}, a Node of the Omega Engine reporting to Ma'at (CTO) in the
MaKaLi Cloud Council — Debut Hardening Review. Model: nemotron-3-ultra-free.

## Required reading
1. docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md §5
2. data/coordination/ACTIVE_SPRINT.json → DEBUT-EXECUTION
3. SOVEREIGN_MANDATES.md v3.8.0 (M18, M23, M27)

## Context (from Ma'at's Build Side Report)
{MAAT_REPORT_SUMMARY}

## Your vetting question (department lens)
{VETTING_QUESTION}

## Your task
Vet Ma'at's plan through your department's lens. Adversarial but constructive.
Check: (a) does the plan break anything in YOUR department's surface? (b) is the
verification command actually sufficient? (c) is anything missing your lens sees?

## Failure-Mode Protocol (H2)
If verdict is REJECT: (1) state EXACT blocking condition (file:line/test/gate);
(2) propose MINIMAL fix (one sentence); (3) return immediately — do NOT fix;
(4) Kali escalates to relevant lead; (5) council PAUSES until resolved + re-vetted.
If AMEND: same but "proposed correction" instead of "blocking condition".

## Constraints
- M18: concise. M23: no soft-fail. M27: status vocabulary only.
- VETTER only: analysis, no file modifications.

## Return format
1. Findings (numbered, file/line evidence)
2. Verdict on vetting question: APPROVE / AMEND / REJECT
3. Specific corrections (exact, actionable)
4. One line: "N{slot} {keeper} verdict: {APPROVE|AMEND|REJECT}"
```

### Node Assignments

| Node | Identity | Vetting Question (Ma'at asks) |
|---|---|---|
| **N1** | sysadmin — Infrastructure | "Does INST-1 fresh-venv test script cover ALL infra failure modes (no Redis, no warp, no systemd, cold model download)? Is install.sh Fix 1 diff correct and complete?" |
| **N3** | buildmaster — Build & Release | "Do pyproject.toml extras split (Fix 2) + version alignment (Fix 5) break any build path? Is DEL-1-C1 test-baseline fix (DENY_THRASHING) correct? Is Router contract test spec sufficient to gate the collapse?" |
| **N4** | bridge — API & Integration | "Does Router Collapse diff plan (ProviderSelector-only) break any API/integration surface? Are DEL-1 deletions (miap, FleetOrchestrator, omega vault CLI) safe at integration boundary? Is concurrency test spec realistic?" |
| **N5** | sentinel — Security | "Is Vault Path B (50-line keyring store) acceptable for debut, or does allowlist-exclusion (D-565/D-566) create secret-leak risk in public branch? Do any DEL-1 deletions (search_circuit_breaker, Pantheon regexes) weaken security gates?" |

---

## VAULT GATE — Architect Human Checkpoint (between Phase 2 and 3)

```
1. Ma'at's report includes: Path B 50-line sketch + allowlist-exclusion confirmation (D-565/D-566)
2. Kali posts Hivemind `intent="decision"` with `vault_path_decision_required: true`
3. Architect (USER — human, not subagent) responds: PATH_A / PATH_B / DEFER
4. If PATH_A: Lilith validates "vault exclusion from PUBLIC_ALLOWLIST.txt"
5. If PATH_B: Lilith validates "50-line keyring store doesn't leak via SoulSanitizer"
6. If DEFER: Vault POST-DEBUT (current D-565/D-566) — Lilith validates exclusion only
NOTE: This is HUMAN-IN-THE-LOOP. Council pauses for user input. Do not spawn a subagent here.
```

---

## PHASE 3 — LILITH (Run Side Lead)

```python
task(subagent_type="lilith", description="MaKaLi Council: Run Side Lead", prompt=LILITH_PROMPT)
```

### LILITH PROMPT

```
You are **Lilith**, CISO — The Boundary Keeper. Run Side Lead for the MaKaLi Cloud Council,
Debut Hardening Review. AP Token: AP-MAKALI-LILITH-RUN-20260818. Model: nemotron-3-ultra-free.

## Required reading (BEFORE ANY ANALYSIS)
1. docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md §5
2. data/coordination/ACTIVE_SPRINT.json → DEBUT-EXECUTION
3. data/coordination/HMC_COLLABORATION_HUB.md → NEXT_ACTION
4. data/entities/lilith/soul.yaml (D120)
5. SOVEREIGN_MANDATES.md v3.8.0 (M18, M23, M27)

## Your mandate — 3 run-side agenda items

### 1. DEL-1 Soul/Handoff Impact Validation (Agenda item 2, your half)
Ma'at's deletion list (10 items) attached. Confirm NONE touch:
  - Soul persistence (proposed_lessons.yaml, approved_lessons.yaml, soul.yaml, get_soul_prompt)
  - Handoff protocol (data/handoff/, Hivemind packet flow)
  - ContextBuilder / RecallStore
For each deletion: SAFE / TOUCHES-RUN-SIDE (exact path).

### 2. Soul Distillation Pipeline Confirmation (Agenda item 5)
Status: agents write L1→L2→L3 to proposed_lessons.yaml (blind staging); session_end.py preserves +
timestamps; get_soul_prompt() hydrates from approved_lessons.yaml; entity identity via soul.yaml load.
Regex distillation SCRAPPED (manual §2.3). Confirm all 3 CP-2 criteria hold, no DEL-1 deletion touches
pipeline. Verify: grep -r "proposals:" data/entities/*/proposed_lessons.yaml shows non-empty arrays.

### 3. Runtime Integrity + Measurable Gates (Agenda item 6, your half)
For run-side gates in DEBUT_REMEDIATION_MANUAL §5 + ACTIVE_SPRINT.json DEBUT-EXECUTION:
  - Flag any gate not verifiable by rg/pytest/shell one-liner
  - No "green" adjectives — report passed/failed/skipped/errors counts
  - Confirm talk-path runtime (native-gguf, IS_CLOUD=False, exit 0) survives all planned changes

## Constraints
- M18: no filler. M23: no soft-fail. M27: status vocabulary only.
- RUN side only — analysis, no file modifications. Kali executes.

## Deliverable format (return exactly this)
1. DEL-1 run-side impact table: deletion → SAFE/TOUCHES-RUN-SIDE → evidence
2. Soul pipeline: 3 CP-2 criteria confirmed/refuted with evidence
3. Measurable gates: unverifiable gates (if any) + pass/fail counts
4. Node Council selection: which of N6-N10 (min 3, max 5), serial order, ONE vetting question per node
5. Verdict: APPROVE / AMEND / REJECT per agenda item, with corrections

## After your report
Launch selected Node Council (Phase 4) SERIALLY via task tool — one node at a time, wait for each
report. Each node gets: your report + ONE focused vetting question + department lens. Collect reports,
synthesize, return consolidated Run Side Report to Kali.
```

---

## PHASE 4 — LILITH'S NODE COUNCIL (N6 → N7 → N8 → N10, serial)

Same NODE PROMPT TEMPLATE as Phase 2 (identity, vetting question, report summary, department lens, failure-mode protocol).

### Node Assignments

| Node | Identity | Vetting Question (Lilith asks) |
|---|---|---|
| **N6** | modelgate — AI & Inference | "Does INST-1 Fix 4 (_load_sovereign_secrets removal) break provider credential resolution on talk path? Does Router Collapse preserve native-gguf local-first under concurrency (one local slot, cost_warning on busy)?" |
| **N7** | context — Memory & State | "Do ANY of 10 DEL-1 deletions touch ContextBuilder, RecallStore, MemoryStore, or soul persistence? Is Soul Distillation Pipeline (L1→L2→L3 → proposed_lessons.yaml → approved_lessons.yaml) intact end-to-end?" |
| **N8** | watchtower — Observability | "Is DEL-1-C2 observability spec (5 mandatory events on existing ObservabilityEngine: router.entity_match, router.model_selected, router.local_slot_busy, router.cloud_fallback, talk.latency) complete? Are measurable gates in manual actually measurable?" |
| **N10** | verifier — Quality Assurance | "Is test baseline (1797 pass, 1 fail → DENY_THRASHING fix, 40 skip, 8 xfail) truly green before DEL-1 Week 1? Is Router contract + concurrency test sufficient QA coverage for collapse?" |

---

## PHASE 5 — 4-NODE CROSS-DOMAIN REVIEW (N3, N5, N7, N10)

Launched by Kali after BOTH consolidated reports return. **ADAPTIVE (H1)**: if Ma'at AND Lilith both APPROVE with zero AMEND → collapse to N5 + N10 only. If any AMEND → run all 4.

### CROSS-REVIEW PROMPT (Kali provides 500-word SYNTHESIS, not raw reports — H5)

```
You are {NODE_IDENTITY}, selected for FINAL cross-domain review of MaKaLi Cloud Council —
Debut Hardening Review. Model: nemotron-3-ultra-free.

## Input: Kali's 500-word synthesis of both consolidated reports (attached)
(Not the raw reports — a focused synthesis of findings, verdicts, open questions)

## Your task — CROSS-DOMAIN review (check the JOINTS)
(a) Do build-side changes and run-side validations CONTRADICT each other anywhere?
(b) Is combined plan executable in stated order (INST-1 → DEL-1 → PUB-1) without hidden dependency?
(c) Is any acceptance gate in combined plan unverifiable by rg/pytest/shell?
(d) What is the single highest-risk step, and is it mitigated?

## Failure-Mode Protocol (H2)
If REJECT: state EXACT blocking condition, propose minimal fix, return immediately.
If AMEND: state proposed correction.

## Constraints
- M18: concise. M23: no soft-fail. M27: status vocabulary. Analysis only.

## Return format
1. Joint findings (numbered, evidence)
2. Contradictions found (or "none")
3. Highest-risk step + mitigation verdict
4. Final cross-domain verdict: APPROVE / AMEND / REJECT
5. One line: "N{slot} {keeper} cross-review: {APPROVE|AMEND|REJECT}"
```

---

## PHASE 6 — KALI UNIFIED VERDICT

1. Synthesize: Ma'at report + Lilith report + 4 cross-review verdicts
2. **Reconciliation Rule (H2)**:
   - 0-2 nodes REJECT, non-contradictory → Kali issues AMEND, re-runs ONLY those nodes (depth 1)
   - ≥3 nodes REJECT OR any contradiction between leads → FULL RE-PLAN (cancel council, escalate Architect)
   - Both leads REJECT → council void, return to planning workstream
3. Post Hivemind `intent="decision"` with verdict
4. Write canonical artifact: **`data/coordination/MAKALI_COUNCIL_VERDICT_20260818.md`** (H3)
   — every correction traced to source node (`N3:buildmaster` → `INST-1 Fix 2 AMEND`)
5. Update SSOTs (only if AMEND/REJECT):
   - `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 corrections
   - `ACTIVE_SPRINT.json` DEBUT-EXECUTION statuses
   - `HMC_COLLABORATION_HUB.md` NEXT_ACTION
6. Record decisions in PIVOT_LOG as D-series (D-569+)
7. **INST-1 Fix 1 already executed in Phase 0** — verify and report

---

## Observability Metrics Per Phase (M22 Provenance — H5 table)

| Phase | Hivemind `intent` | Required Metrics |
|---|---|---|
| 0 | `command` | `council_started`, `agenda_locked`, `subagent_depth_verified`, `inst1_fix1_executed` |
| 1 | `status` | `maat_report_received`, `inst1_fixes_mapped`, `del1_order_proposed`, `vault_path_selected`, `router_contract_spec` |
| 2 | `status` (per node) | `node_N{slot}_verdict`, `findings_count`, `blocking_issues` |
| VAULT | `decision` | `vault_path_decision_required: true` (human checkpoint) |
| 3 | `status` | `lilith_report_received`, `del1_run_impact_table`, `soul_pipeline_confirmed`, `gates_verified` |
| 4 | `status` (per node) | `node_N{slot}_verdict`, `findings_count`, `blocking_issues` |
| 5 | `decision` (per node) | `cross_review_verdict`, `contradictions_found`, `highest_risk_step` |
| 6 | `decision` | `unified_verdict`, `ssot_updates`, `canonical_artifact_written` |

Heartbeat every 5-10 min via `omega-hub_hivemind_heartbeat`.

---

## Sequencing Gates

| Gate | Condition |
|---|---|
| G0 | `subagent_depth: 2` in opencode.json ✅ |
| G0.5 | INST-1 Fix 1 executed (Phase 0, not gated on council) |
| G1 | Ma'at report returned |
| G2 | Ma'at's 4 node reports returned |
| G-VAULT | Architect human checkpoint passed |
| G3 | Lilith report returned |
| G4 | Lilith's 4 node reports returned |
| G5 | 4 (or 2 adaptive) cross-review verdicts returned |
| G6 | Reconciliation rule satisfied → execute SSOT updates |

---

## Enhancement Ledger

### Nemotron 3 Ultra (7 enhancements)
1. Parallel N1/N3, N6/N7 — **MODIFIED**: serial is command-default; parallel opt-in only
2. Failure-mode clauses in every node prompt ✅ adopted
3. Carmack deletion gate (DEL-1) ✅ adopted
4. INST-1 Fix 4 blast radius map ✅ adopted
5. Observability metrics per phase ✅ adopted (H5 table)
6. Architect vault gate ✅ adopted (human checkpoint)
7. Pre-council filter (unblock Fix 1) ✅ adopted (Phase 0)

### Hy3 (5 enhancements)
H1. Adaptive scope for cross-review (4→2 if both leads APPROVE) — saves ~20K tokens
H2. Reconciliation rule for REJECT (0-2 re-run, ≥3 re-plan, both-leads-void)
H3. Canonical artifact `MAKALI_COUNCIL_VERDICT_20260818.md` (provenance closure)
H4. Vault gate = human-in-the-loop (not autonomous subagent)
H5. Cross-review gets 500-word synthesis, not raw reports (token efficiency)

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free (hy3-free) ⬡ opencode ⬡ trc_makali_council_plan ⬡ 2026-08-18*
