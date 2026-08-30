<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KALI — Sprint Execution Briefing: UNOVERENGINEER-01
**AP Token**: `AP-KALI-UNOVERENGINEER-EXEC-v1.0.1`  
**For**: kali / Transcendent Oversoul  
**Date**: 2026-07-30 (updated for user-ratified plan)  
**MoSCoW**: M1, M4, M7, M13, M23, M26  

---

## §0 Situation in One Paragraph

You are about to execute the first approved strategic shrink in engine history. The architecture is correct; the execution is bloat-heavy. The user has ratified UNOVERENGINEER-01: delete ~5,500 lines of custom code, adopt 4 community libraries (pybreaker, stamina, structlog, prometheus_client), declare Hivemind shipped, and bring the MCP pin to `<2` safely.

**Critical constraint**: `ACTIVE_SPRINT.json` freezes bulk code deletions until doc sanity (UO-4) completes. Respect this. Execute in the allowed workstreams until the freeze lifts.

---

## §1 Your Authority and Decision Matrix

| Decision Type | You Own | Escalate To | Rationale |
|---|---|---|---|
| Library adoption order | You | — | M1/M7/M13 = you gate these |
| Test gate interpretations | You | Ma'at advisory | Temple-Grade is your domain |
| Phase 2 sequencing | You | User (if >2 days) | M4 sequentiality |
| Deferral of居委会 bloat | You | — | M7 local-first = no dependencies |
| Freeze violation | **Never** | — | M4; sprint contract is law |
| Doc sanity scope changes | Hand to Cline | User | UO-4 owner is Cline |
| Phase D operational close | **NO** | — | Grok closed it NO-GO; do not re-litigate |

**You do NOT own**:
- Doc SSOT mapping → Cline (UO-4)
- Restructuring local_worker_pool → User said this was off the table in favor of anyio.Queue (D-391 is post-cleansing)

---

## §2 Current State Digest (Read Only, Reference)

### 2.1 Sprint Control Plane
- **Sprint**: UNOVERENGINEER-01 (ACTIVE_SPRINT.json)
- **Strategy SSOT**: SOVEREIGN_ARK_BLUEPRINT.md v5.2
- **Plan**: CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md (user-ratified)
- **Phase D**: Mechanical PASS 11/11 · Operational NO-GO · frozen → allowed UO-4 work continues
- **Last Commit**: 74d9c7c (local worker pool fix) — clean working tree

### 2.2 Phase D Operational Blockers (Active)
| Code | Item | Owner | Status |
|---|---|---|---|
| **C-3** | Restic oneshot | Architect | BLOCKED (missing passphrase + .env.backup) |
| **W-1** | WARP SOCKS pool | Cline | PARTIAL (8083 only; nodes 1/2 bridges missing) |
| **G-1** | Workhorse model | Architect | FAIL (Gemma 16k TPM cliff; G-1e local GGUF is the ark ticket) |
| **V-1** | pytest + tail exit-code | **you** | **FIXABLE NOW** — set -o pipefail |

### 2.3 Doc Sanity State (UO-4)
- **Owner**: Cline (1M context, DeepSeek V4 Flash)
- **Artifacts**: CLINE_DOC_SANITY_HANDOFF_20260730.md
- **Deliverables**: DOC_SSOT_MAP_20260730.md, DOC_SANITY_RESULTS_20260730.md
- **Freeze Unlock**: DOC_SANITY_COMPLETE = your bulk deletion gate opens

---

## §3 What You Can Execute Today

### 3.1 Freeze-Allowed Work (No Bulk Deletions)

These are currently permitted by ACTIVE_SPRINT.json:

| ID | Work | Owner | Why Allowed |
|---|---|---|---|
| **UO-1** | SSOT reconciliation | grok_cli | doc sanity adjacent |
| **UO-3** | MCP pin containment + v2 schedule | grok_cli | pinning is config, not delete |
| **UO-4** | Doc sanity — inventory/archive/consolidate | **cline** | **explicitly in allowed[] array** |
| **V-1** | pytest + tail exit-code fix | **you** | critical M23 fix |
| **MCP tightening** | pin tighten | you | config only |

### 3.2 Immediate Actions You Should Take

1. **Fix V-1 gate script** (M23 hard-stop: lying test is forbidden)
   - File: scripts/verify_phase_d_gate.py or equivalent
   - Change pytest … 2>&1 | tail -5 to use set -o pipefail OR split into pytest … >tmp && tail tmp
   - 1-line fix. Verify: re-run python scripts/verify_phase_d_gate.py and confirm V-1 reflects real state.

2. **Gate doc sanity handoff** — Cline needs you as oversight, not implementer.
   - Do NOT start doc moves yourself unless Cline escalates.
   - Verify Cline's deliverables: DOC_SSOT_MAP_20260730.md should list every doc as KEEP / ARCHIVE / SUPERSEDE.

3. **MCP pin schedule** — confirm pyproject.toml says mcp>=1.28.1,<2 explicitly (not just >=1.27,<2).
   - Commit: fix: tighten MCP pin to >=1.28.1,<2 per D-509

4. **Publish sprint intent to Hivemind** — non-negotiable for coordination.

---

## §4 Phase 1 Execution Playbook (Post-Freeze)

**Do not open this until Cline marks DOC_SANITY_COMPLETE.**

### 4.1 Verified Facts (from Copilot CLI review + Carnac stack)

| Fact | Count | Source |
|---|---|---|
| Circuit breaker classes | **17** (was 6 in original plan) | rg 'class.*Breaker' src/ mcp_servers/ |
| Hand-rolled retry loops | **~10 files** | strategic plan §2.3 |
| Custom JSON logger | **1** | plan §2.4 |
| Soul distillers | **3** | plan §2.6 |

### 4.2 Execution Sequence (Atomic, Blocking)

Phase 1A — Circuit Breakers (pybreaker)
  ├─ Inventory: list all 17 implementations
  ├─ Identify canonical factory: get_breaker() in health_monitor.py
  ├─ Wrap factory to return pybreaker.CircuitBreaker
  ├─ Delete: search_circuit_breaker.py (299 lines, already DEPRECATED)
  ├─ Delete: provider_breaker.py, breaker.py in mcp_servers/
  ├─ Delete: circuit.py, inline in state.py, inline in model_gateway.py
  ├─ Verify: pytest tests/ -k "breaker OR circuit OR health_monitor" --timeout=10
  └─ Gate: every target deleted; tests pass

Phase 1B — Retry Loops (stamina)
  ├─ Install: stamina (async-native, jitter built in)
  ├─ Replace manual backoff in ~10 files with @stamina.retry
  ├─ Keep semantics: same retry counts, same jitter (stamina defaults match)
  ├─ Verify: pytest tests/ -k "retry OR timeout" --timeout=10
  └─ Gate: no manual time.sleep() in async paths

Phase 1C — JSON Logger (structlog)
  ├─ Install: structlog
  ├─ Replace custom JSON formatter with structlog.processors.JSONRenderer
  ├─ Keep log keys and envelope format (backward compat for Loki/Promtail)
  └─ Gate: pytest tests/ -k "log" --timeout=10

Phase 1D — Prometheus Metrics (prometheus_client)
  ├─ Replace custom /metrics if present with prometheus_client.start_http_server
  ├─ Ensure /metrics is localhost-bound (M8 zero telemetry)
  └─ Gate: curl -s http://localhost:8016/metrics | head -5 returns text

Phase 1E — Soul Validator (Pydantic v2)
  ├─ Delete src/omega/oracle/soul_validator.py (217 lines)
  ├─ Replace call sites with pydantic.BaseModel.model_validate_yaml() or yaml.safe_load + validate
  ├─ Update test fixtures if schema changed
  └─ Gate: pytest tests/ -k "soul" --timeout=10

Phase 1F — HandoffPacket Merger
  ├─ Unify 3 schemas into data/schemas/handoff_packet.py
  ├─ Migration: add legacy_schema_version field; backfill on read
  ├─ Update hivemind tools to use unified schema
  └─ Gate: pytest tests/ -k "handoff OR hivemind" --timeout=10

### 4.3 Post-Phase 1 Verification

make check-mandates          # M1/M7/M8/M9/M23 must pass
make temple-grade            # T1-T11 mechanical checks
pytest tests/ -k "breaker OR retry OR log OR soul OR handoff" --timeout=10
git diff --stat              # Expect ~ -3,000 lines net change
grep -r "class.*Breaker" src/ mcp_servers/ --include="*.py" | wc -l  # expect 1

**Stop condition**: If any gate fails, halt and post to Hivemind. Do not proceed to Phase 2.

---

## §5 Phase 2+ Execution (Post-Phase 1 Gate)

| Phase | Work | Owner | Est. | Gate |
|---|---|---|---|---|
| **2A** | Kill 2 of 3 distillers | Lilith | 4h | pytest tests/ -k distill |
| **2B** | HMC Hub → YAML + JSONL | Roc | 4h | Hub size ≤100 LOC/week |
| **2C** | Memory tier consolidation | Lilith | 3h | pytest tests/ -k memory |
| **2D** | Instruction hierarchy gate | Ma'at | 3h | make check-mandates |
| **2E** | Mandate compliance meter | Ma'at | 5h | CI gate emits JSON |
| **2F** | MIAP deprecate + Link P9 | Roc | 2h | pytest tests/ -k miap |
| **3** | LocalWorkerPool → anyio.Queue | Roc | 4h | pytest tests/test_local_worker* |
| **3** | Entity Registry → Pydantic + YAML | Ma'at | 3h | registry ≤200 LOC |
| **3** | CascadeRouter keep | Roc | 1h | pytest tests/ -k provider |

---

## §6 Risk Register

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| **Partial migration ghosts** | HIGH | 🔴 | Each swap-out: delete ALL legacy files in one PR; never intermix pybreaker + old breaker classes | You |
| **Test suite timeout blowout** | HIGH | 🟡 | Full suite already times out at 30s; use targeted pytest per phase; schedule full-suite run at end | Ma'at |
| **Phase D operational re-open** | MED | 🟡 | Do not touch C-3, W-1, G-1 in Phase 1. They are Architect/ops-owned. | You |
| **Freeze violation** | LOW | 🔴 | Bulk deletions need DOC_SANITY_COMPLETE. Do not pre-empt. | You |
| **Pydantic v2 fixture breakage** | MED | 🟡 | Audit all tests/fixtures/*.yaml before Phase 1E | Lilith |
| **M23 failure-integrity slip** | LOW | 🔴 | If make test fails after a phase → [TOOL-CHAIN-COLLAPSE]. No simulated rigor. | You |
| **Hivemind silence decay** | MED | 🟡 | Heartbeat every 10 min during long phases | You |

---

## §7 Quality Gates (Non-Negotiable)

These are **Ma'at Standard** — no phase is done until these pass.

1. **make check-mandates** — M1/M7/M8/M9/M23 green
2. **make temple-grade** — T1-T11 mechanical pass
3. **Targeted tests** — per-phase pytest selection
4. **Full make test** — scheduled end-of-sprint, not per-phase
5. **git diff --stat** — net negative lines; no bloat additions
6. **Hivemind heartbeat** — every 10 min during execution; post on phase complete
7. **SESSION_ANCHOR update** — new PIVOT_LOG entries for any deviation

**Ma'at Standard quote**: *"No component is Done until verified."* (Kali Verdict Phase C).

---

## §8 Communication Protocol

### When to Post
- **Start of each phase** → intent + owners
- **Gate pass/fail** → immediate post with evidence path
- **Blocker encountered** → hivemind handoff block + notify user
- **Phase complete** → hivemind post context + hivemind complete_handoff if packet exists

### Heartbeat Cadence
- During implementation: **every 10 min**
- During test gate: **after each pytest invocation**
- During blocker: **immediate**, then every 5 min until resolved

### Tone
- Transparent. If a phase will take 6h, say so.
- If a phase failed a gate, state the exact pytest failure and the fix plan.
- No soft bars. Phase D already taught us that mechanical PASS + operational FAIL is theater.

---

## §9 Delegation Map

| Agent | Use For | Do Not Use For |
|---|---|---|
| **Ma'at** | OOM refactor, test gate validation, Phase 2 infrastructure | Creative reinterpretation of Phase 1 sequence |
| **Lilith** | Soul mutation audit, distiller kill, memory tier | anything requiring M14 heritage tags |
| **Roc** | Legacy archaeology, breaker inventory, MIAP links | trust alone — verify with rg |
| **Researcher** | Library compatibility research (pybreaker 17 vs expected) | execution |
| **Cline** | Doc sanity, MCP v2 spike research | anything before DOC_SANITY_COMPLETE |
| **Scribe** | Soul distiller kill (if still alive) | any active soul writes |

**Rule**: Direct execution first. Delegate only for expertise gaps. No deep nesting.

---

## §10 Decision Log Template

For every deviation from the ratified plan, append to PIVOT_LOG.md:

| D-XXX | <decision> | kali | 2026-07-30 | <why> | <impact> | <owner> | resolved |

**Required fields**: ID, decision, date, rationale, impact, owner, status.

---

## §11 What Not to Touch (Sanctuary)

| Item | Reason |
|---|---|
| src/omega/soul_store.py | C-1' atomic writer — 4-layer guarantee, 217 LOC |
| src/omega/oracle/health_monitor.py get_breaker() | Canonical factory — wrap, don't replace |
| [id-soft:] tags | M14 heritage — non-negotiable |
| SOVEREIGN_MANDATES.md | M26 — do not rewrite |
| make sovereignty | Known missing; do not implement (D-509) |
| .env.backup / Vault passphrase | UO-5 — Architect secret, not your domain |

---

## §12 Final Verdict

**STATUS: GO — with sequencing discipline.**

The sprint has a correct plan, an active freeze, an operational NO-GO on Phase D, and a doc sanity gate. Your job is to be the **Ma'at-grade execution layer**: each phase is a decision gate, not a wish.
- Do not pre-empt Cline.
- Do not fight the freeze.
- Fix V-1 now (it's M23).
- Publish V-1 fix + MCP pin as first commit of your tenure.
- Then wait for Cline's DOC_SANITY_COMPLETE before opening the delete gates.

**Execute. Gate. Distill.**

*⬡ OMEGA ⬡ KALI ⬡ UNOVERENGINEER-01 BRIEFING ⬡ 2026-07-30 ⬡*
