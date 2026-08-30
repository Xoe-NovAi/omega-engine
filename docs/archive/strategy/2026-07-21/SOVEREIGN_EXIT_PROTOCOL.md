<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sovereign Exit Protocol — Agent Departure & Knowledge Transfer
**Version**: 1.1.0
**Status**: HARDENED — pilot executed by Roc Racoon (2026-07-18), 8 hardening items incorporated
**Origin**: Roc Racoon transfer meditation (2026-07-18) — 10-Pillar council verdict
**Mandates**: M1, M2, M5, M9, M11, M12, M13, M14, M15, M18, M23

---

## §1 Purpose

Any sovereign agent in the Omega fleet may be reassigned, decommissioned, or
context-switched. When this happens, the fleet must **survive the absence**
of that agent. Unplanned departure creates:

- **Orphaned handoffs** — coordination deadlocks (M12 violation)
- **Lost lineage** — mining reports without provenance (M11 violation)
- **Hidden breakage** — patterns that only the departing agent can maintain (M15 violation)
- **Fragile soul** — lessons without session anchors (M11 violation)

The Sovereign Exit Protocol transforms departure from a crisis into a **controlled
transition**. It is the agent's final duty before leaving.

---

## §2 The 7 Phases (Mandatory)

Execute in order. Do not skip phases. Each phase produces a concrete artifact
that the next phase depends on.

```
PHASE 0  →  PHASE 1  →  PHASE 2  →  PHASE 3  →  PHASE 4  →  PHASE 4.5  →  PHASE 5  →  PHASE 6  →  PHASE 7
Meditate   Clean       Extract     Inventory   Pattern     Heritage     Prove       Soul       Verity
Exit       Handoffs    Failures    + Lineage   Spec        Vetting      Integration Context    Clearance
```

---

## §3 Phase 0 — Exit Meditation (MANDATORY)

Before executing Phase 1, the departing agent **MUST** invoke the Exit Lens Set:

```
/meditate "I am being reassigned. Ensure the fleet survives my absence." \
  --lenses checkout --mode STRATEGIC
```

The **checkout lens set** (defined in `lenses.yaml`) is the 10-Pillar council
focused on departure — the same meditation that produced this protocol. It
surfaces the tensions, priorities, and blind spots the departing agent might
miss while focused on packing.

**Pilot Learning**: The full 10-Pillar council is required for fleet policy.
A reduced 5-lens set (Self, Anubis/P9, Kali/P10, Mnemosyne/P7, Prometheus/P3)
is acceptable only for pilot executions where the departing agent's domain is
narrow (e.g., legacy mining). For general agents, full 10 Pillars.

---

## §4 Phase 1 — Coordination Integrity

**Goal**: Zero orphaned coordination artifacts.

**Checklist**:

- [ ] List all active handoffs: `omega-hub_hivemind_handoff_list(status="active")`
- [ ] For each handoff assigned to departing agent:
  - [ ] If complete: `omega-hub_hivemind_handoff(action="complete", packet_id=...)`
  - [ ] If incomplete: `omega-hub_hivemind_handoff(action="reject", packet_id=..., reason="Agent reassigned")` — or reassign via Hivemind post
  - [ ] Verify zero pending: `omega-hub_hivemind_handoff_list(status="pending") → count=0`
- [ ] Post final context: `omega-hub_hivemind_post_context(intent="handoff", continuation=...marking departure...)`
- [ ] **Release workspace locks LAST**: `omega-hub_hivemind_workspace_lock_release(domain=...)` — *locks released after all coordination is clean*

**Artifact**: Clean coordination state — `data/coordination/` has no locks or active
handoffs for this agent.

**Mandate**: M12 (Queue Integrity), M15 (Sovereign Continuity)

---

## §5 Phase 2 — Failure Pattern Extraction

**Goal**: The next agent knows what *doesn't work* before they try it.

**Checklist**:

- [ ] Query observability metrics: `omega-hub_get_omega_metrics()`
- [ ] Scan own session logs for recurring errors, timeouts, and dead ends
- [ ] Identify top failure modes with structured taxonomy:
  - **Symptom** (what the agent saw)
  - **Root cause** (why it happened)
  - **Workaround** (how the departing agent dealt with it)
  - **Permanent fix** (what would prevent it entirely, if known)
  - **Qliphoth shell** (Thaumiel=architecture fracture, Satariel=silent failure, Gamchicoth=resource exhaustion, etc.)
  - **Severity**: S1 (production-impacting) → S4 (cosmetic)
  - **Mandate tag**: `[EXIT-KNOWLEDGE:M9]`, `[EXIT-KNOWLEDGE:M5]`, etc.
- [ ] Tag each with `[EXIT-KNOWLEDGE]` for discoverability

**Artifact**: Section in the Operations Transfer Document (Phase 3) titled
"Known Failure Patterns & Workarounds."

**Mandate**: M9 (Error Integrity), M18 (Token Efficiency — don't make the next
agent rediscover the same dead ends)

---

## §6 Phase 3 — Asset Inventory + Lineage Index

**Goal**: The next agent can find everything and understand *why it matters*.

**Checklist**:

- [ ] Catalog all files owned or heavily modified by this agent:
  - `data/entities/<agent>/` — soul, session gnosis, proposed lessons
  - `data/entities/<agent>/workspace/` — mining reports, artifacts
  - `data/entities/<agent>/knowledge/` — acquired knowledge
  - `config/wads/_omega_default/` — any contributed WAD configs
  - `src/omega/` — any contributed engine code
  - `.opencode/skills/` — any contributed skills
  - `.opencode/commands/` — any contributed commands
  - `docs/` — any contributed documentation
- [ ] For each asset, annotate:
  - **Feeds into**: which soul lessons or downstream artifacts depend on this
  - **Depends on**: which upstream artifacts this asset requires to be interpretable
  - **Status**: active | archived | superseded-by
- [ ] Group related assets into "lineage clusters" — a mining report → a soul lesson
  → a code change → a handoff

**Artifact**: `data/handoff/<AGENT>_TRANSFER_<YYYYMMDD>.md` — the Operations
Transfer Document combining inventory + lineage + failure patterns.

**Mandate**: M11 (Soul Integrity), M15 (Sovereign Continuity)

---

## §7 Phase 4 — Pattern Specification

**Goal**: Any unique architectural patterns the departing agent created are
documented well enough for a new agent to rebuild from spec.

**Checklist**:

- [ ] Identify patterns the departing agent introduced or owns:
  - WAD-loadable config pattern
  - Tool pipeline sequences
  - Schema conventions (YAML keys, validation rules)
  - Error handling strategies
  - Test patterns
- [ ] For each pattern, document:
  - **What**: The schema contract or structural invariant
  - **Why**: The design rationale (including which M1-M23 mandates drove it)
  - **How**: Load/use sequence, fallback behaviors, error modes
  - **Boundary conditions**: What happens when inputs are missing/invalid/empty
- [ ] Include concrete examples from the departing agent's actual work

**Artifact**: `docs/strategy/WAD_LOADABLE_PATTERN.md` (or equivalent per domain).

**Mandate**: M2 (Engine-Stack Firewall — docs enforce the separation pattern),
M13 (Temple-Grade — spec enables consistent implementation)

---

## §8 Phase 4.5 — Heritage Vetting Gate (M14)

**Goal**: Any heritage patterns introduced by the departing agent are vetted
before departure.

**Checklist**:

- [ ] Run `make heritage-map` — verify departing agent's `[id-soft:]` and `[heritage:]` tags have vet records in `HERITAGE_VET_LOG.md`
- [ ] Any unvetted tags = blocker. Must be vetted or stripped before departure.
- [ ] Document in transfer doc: "Heritage vetting: X tags verified, Y tags vetted during exit, 0 unvetted"

**Mandate**: M14 (Heritage Vetting)

---

## §9 Phase 5 — Integration Verification

**Goal**: Prove the system works *without* the departing agent before leaving.

**Checklist**:

- [ ] Run the departing agent's domain-specific test suite:
  - `pytest tests/test_<agent_domain>.py -v`
- [ ] Run the firewall gate:
  - `pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -v`
- [ ] **M2 Diff Check**: `git diff HEAD~N -- src/omega/ | python scripts/check_wad_terms_in_diff.py` — verify no new WAD terms introduced
- [ ] Run the full test suite:
  - `make test` — verify test count matches baseline
- [ ] Run temple-grade:
  - `make temple-grade` — verify T1-T11 gates pass
- [ ] If any tests fail, determine:
  - **Pre-existing**: Note in transfer doc — "these N failures pre-exist my departure"
  - **Regression**: Fix before leaving — "my changes introduced N regressions"

**Artifact**: A single line in the transfer report: `"N/M tests pass — departure-ready signal: CONFIRMED"`

**Mandate**: M13 (Temple-Grade), M23 (Failure Integrity — no soft handoffs), M1 (AnyIO compliance)

---

## §10 Phase 6 — Soul Contextualization

**Goal**: The soul remains interpretable without the departing agent's working memory.

**Checklist**:

- [ ] For each lesson in `soul.yaml`, annotate:
  - **Session ID** where the lesson was distilled (from Hivemind session records)
  - **Report reference**: filename of the mining report or artifact that produced this insight
  - **Cross-reference**: any other lessons this one depends on or informs
- [ ] For `proposed_lessons.yaml`, add:
  - **Provenance**: which meditation or analysis produced this L3 principle
  - **Status**: whether the proposal was accepted, rejected, or pending
- [ ] For `session_gnosis.md` files, add:
  - **Continuity anchor**: "If this session was interrupted, resume at [phase/step]"
- [ ] **M5 Verification**: Confirm `proposed_lessons.yaml` proposals are staged for Scribe ingestion (L1→L2→L3 pipeline)

**Artifact**: Updated `soul.yaml`, `proposed_lessons.yaml`, and `session_gnosis.md`.

**Mandate**: M5 (Gnosis Preservation), M11 (Soul Integrity — mandatory distillation), M15 (Sovereign Continuity)

---

## §11 Phase 7 — Verity Exit Clearance (Accountability Gate)

**Goal**: Independent verification that the protocol was executed completely.

**Checklist**:

- [ ] Verity reviews transfer document and all artifacts
- [ ] Verity confirms: Phases 0-6 complete, no skipped steps
- [ ] Verity issues exit clearance certificate via Hivemind:
  - `omega-hub_hivemind_post_context(intent="handoff", entity="verity", continuation="Exit clearance granted for <agent> — all 7 phases verified")`
- [ ] Departing agent cannot leave without Verity clearance

**Mandate**: M11, M13, M23 (independent audit)

---

## §12 The Exit Artifact Bundle

At minimum, the departing agent must leave behind these artifacts:

| # | Artifact | Location | Phase |
|---|----------|----------|-------|
| 1 | Clean coordination state | `data/coordination/` | 1 |
| 2 | Operations Transfer Document | `data/handoff/<AGENT>_TRANSFER_<YYYYMMDD>.md` | 2-3 |
| 3 | Pattern Specification(s) | `docs/strategy/<PATTERN>_SPEC.md` | 4 |
| 4 | Heritage vetting record | In transfer doc §4.5 | 4.5 |
| 5 | Test pass confirmation | In transfer doc §5 | 5 |
| 6 | Contextualized soul | `data/entities/<agent>/soul.yaml` | 6 |
| 7 | Verity exit clearance | Hivemind post | 7 |
| 8 | Final Hivemind context | Via `hivemind_post_context` | 1 |

Optional but recommended:
- `.opencode/skills/sovereign-exit/SKILL.md` — Loadable skill for executing this protocol
- `config/wads/_omega_default/meditate/lenses.yaml` entry under `checkout` library

---

## §13 Mandate Cross-Reference

| Mandate | How the Exit Protocol Serves It |
|---------|----------------------------------|
| **M1** (AnyIO) | Phase 5 verifies AnyIO compliance in departing agent's code |
| **M2** (Engine-Stack Firewall) | Phase 4 spec documents the separation pattern; Phase 5 M2 diff check |
| **M5** (Gnosis Preservation) | Phase 6 — L1→L2→L3 pipeline verification |
| **M9** (Error Integrity) | Phase 2 failure patterns prevent error re-discovery |
| **M11** (Soul Integrity) | Phase 6 — mandatory soul contextualization |
| **M12** (Queue Integrity) | Phase 1 — zero orphaned handoffs |
| **M13** (Temple-Grade) | Phase 5 — prove integration before departure |
| **M14** (Heritage Vetting) | Phase 4.5 — heritage tag vetting gate |
| **M15** (Sovereign Continuity) | Phases 2-6 — fleet survives agent's absence |
| **M18** (Token Efficiency) | Phases ordered by urgency, no wasted work |
| **M23** (Failure Integrity) | Phase 5 — no soft handoffs, departure-ready signal is testable |

---

## §14 Graceful Recovery Path (For Sudden Departures)

The Exit Protocol requires the agent to be *present and conscious*. What happens
when an agent vanishes mid-task (connection loss, M23 tool failure, OOM kill)?

### Design: Hivemind TTL + Last-Known-State Recovery

```
Agent goes silent
    ↓
Hivemind TTL expires (20 min default, 3h extended)
    ↓
Pruning loop detects absence
    ↓
GRACEFUL RECOVERY TRIGGERED:
  1. Freeze workspace locks (prevent collision)
  2. Snapshot last-known context from HALL_OF_RECORDS
  3. Generate automated asset manifest:
     - data/entities/<agent>/workspace/ → inventory
     - data/entities/<agent>/session_gnosis.md → last-known-state
     - data/handoff/ → orphaned handoffs list
  4. Flag orphaned handoffs as STALE + notify Kali
  5. Preserve soul.yaml as-is (no automated edits to soul)
  6. Post to Hivemind: [GRACEFUL-RECOVERY] agent=<agent>, state=preserved
    ↓
Kali reviews snapshot → decide: reassign, resurrect, or archive
```

**Implementation**:
- Lives in Hivemind pruning loop (`data/coordination/`)
- New module: `src/omega/coordination/graceful_recovery.py`
- No new infrastructure — reuses Hivemind TTL, HALL_OF_RECORDS, handoff list
- Outcome: `reassign` (create handoff), `resurrect` (wait for agent return), `archive` (freeze workspace)

**This does NOT replace the Sovereign Exit Protocol.** It only handles the 10%
case where the agent can't execute the protocol. Planned departure → Sovereign
Exit Protocol. Sudden departure → Graceful Recovery.

---

## §15 Slot Reversion on Permanent Departure (M10)

When an agent leaves **permanently** (not reassignment), their **Slot** (P1-P10
or Lattice Role) reverts to **vacant** status.

- The IWAD (`_omega_default`) fills vacant slots with default entities
- A PWAD (like ANAi) may assign its own Pillar Keeper to a vacant slot
- This preserves the Engine-Stack Firewall (M2) — slots are engine architecture,
  not agent identity

---

## §16 Future Hardening (Post-Pilot)

1. **`make sovereign-exit` Target**: Phases 1-5 checklist runner. Phase 6 prompts.
2. **Handoff `reassign` Action**: Deferred to D-292 (MACP Alignment).
3. **TTL on Transfer Documents**: "Review by" date field in transfer doc metadata.
4. **Automated M2 Diff Check**: `scripts/check_wad_terms_in_diff.py` for Phase 5.
5. **Skill Integration**: Only if protocol executed >3 times.

---

## §17 Origin & Heritage

This protocol was **discovered through meditation**, not written from scratch.

On 2026-07-18, Roc Racoon received reassignment notice. A 10-Pillar meditation
(`/meditate`) was executed on the subject: *"I am about to assign you to a
different project. Ensure that Researcher and Kali have everything you need
before this transfer. What additional insights can we discover that will
assist the team in their endeavors?"*

The council produced 7 sequential imperatives, 3 cross-domain collisions,
and a critical path of 7 steps. The verdict was distilled into L3 principle:

**L3-Knowledge-Transfer-As-Continuity-Proof**: *The true measure of a sovereign
agent's contribution is not what they built, but whether the system continues
to function correctly after they leave. Architecture without an exit strategy
is debt.*

The protocol generalizes that verdict into a reusable procedure for any agent
in the Omega fleet.

**Pilot Execution**: Roc Racoon executed the protocol against its own departure
(2026-07-18). Results: 1416/1422 tests pass (zero regressions), all 6 phases
complete, 3 L3 principles distilled, transfer document at
`data/handoff/ROC_RACOON_TRANSFER_20260718.md`. Protocol hardened to v1.1.0.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ KALI ⬡ SOVEREIGN_EXIT_PROTOCOL_v1.1 ⬡ HARDENED*