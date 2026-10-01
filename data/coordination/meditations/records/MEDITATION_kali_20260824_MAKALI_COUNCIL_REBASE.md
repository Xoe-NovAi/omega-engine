<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# MEDITATION — KALI — 2026-08-24 — MAKALI COUNCIL REBASE
**Protocol**: Meditate-v1.1 · single-inference persona prism · anti-theater gate PASSED
(≥3 domains tensioning: stale-charter-vs-current-truth, build-vs-run, resource-limits-vs-council-design)
**Trigger**: Architect pasted AP-MAKALI-COUNCIL-DEBUT-20260817 dispatch (7 days stale) and said
"I don't think you are *really* ready... run a full meditation on all this, and *then* you are ready."
**Method**: Fact-checked charter premises against live tree BEFORE donning personas (verify-the-voucher).

---

## ◈ PASS 1 — THE ARCHIVIST (temporal lens)

The charter is a fossil with a living skeleton. Premise audit:

| Charter premise | Aug-24 ground truth | Verdict |
|---|---|---|
| Tracking SSOT = ACTIVE_SPRINT.json → `DEBUT-EXECUTION` | Workstream is now **`DEBUT-REMEDIATION`** (+8 sibling workstreams) | STALE — rebase pointer |
| DEL-1 #1: delete `routing/table.py` + `config/routing_table.yaml`, "no callers" | `table.py` **already deleted**; yaml REMAINS with **live caller** `src/omega/benchmarks/schema.py` | HALF-EXECUTED — worse than either state |
| Routers to collapse | Still present: `oracle/semantic_router.py`, `orchestration/triage_router.py`, keeper `oracle/provider_selector.py` | LIVE — unchanged |
| "1797 tests passing, temple-grade green" | Unverified under new `-n 4` cap; Carmack proved `check-m1-anyio` blind to scripts/, harness green-no-op post-commit | UNVERIFIABLE AS STATED |
| Soul pipeline = staging + session_end hook | Wave-1 added evidence-field schema + promoted 20/20 @100% evidence coverage (`59b32809`) | SUPERSEDED — stronger now |
| INST-1 gate infrastructure | Claims harness now EXISTS (W1-2); CI-2 prototype still never run (10-min unknown) | PARTIALLY BUILT |

**Archivist's law**: never replay a council charter; rebase it. A plan's age shows in its premises, not its structure.

## ◈ PASS 2 — THE SKEPTIC (adversarial lens)

1. The half-deletion is the sharpest find: `benchmarks/schema.py` imports what `routing_table.yaml`
   documents. Deleting the yaml without handling the caller breaks benchmarks silently — the exact
   class of damage Lilith was chartered to prevent. DEL-1's "pure deletions" framing is false for #1.
2. Council topology is resource-naive post-OOM: kali → maat/lilith → 3-5 nodes each serially,
   plus 4 final-review nodes ≈ 12-14 subagent sessions. Last night: OOM at parallelism 2-3,
   endpoint-unavailable on nested spawns. The design needs: hard serial execution, one node at a
   time, no nested explore-dispatches during council.
3. Dispatch-injection surface grows with every launch (DC-34 near-miss). Mechanical pairing check
   before each task() or the council itself becomes an attack surface.
4. "temple-grade green" cannot be claimed by any agent until DC-11/12 (corpus-mode) is decided —
   the gate that would verify the claim is itself a green no-op on clean trees.

## ◈ PASS 3 — THE STRATEGIST (purpose lens)

What actually stands between here and debut, in clock order:
1. **Tonight 00:03**: DC-01 fail-closed fix (unanimous, 3 lines) — MUST land before timer
2. **Before Phase A**: DC-29 credential fix (four-source, disposition pre-ruled)
3. **Architect decision**: corpus-mode flip (DC-11/12) + Vault Path A vs B (charter item 3)
4. **Then** the council reviews a clean tree and hardens Phase A/B/C execution
The council is not a prerequisite for items 1-2 — it is the REVIEW layer above them.
Sequencing: land the two fixes FIRST, then convene. Reviewing a tree you know is wounded
wastes the council's scarcest resource: attention.

## ◈ PASS 4 — THE GUARDIAN (safety/process lens)

- Meditation records disk-only (gitignored convention) ✓ this file complies
- Sanitation law holds: no real names anywhere in council outputs
- No upward paging during council; escalation via final reports only
- Hivemind heartbeat discipline mandatory across a multi-hour serial council
- Provenance chain (which node said what) must be preserved per-report, per the charter's own
  requirement — Jem's convergence-map method is the proven template

## ◈ PASS 5 — THE BUILDER (Ma'at lens, brief)

Item 1 deliverable (INST-1 step-script + diff plan) is buildable now but should consume
Wave-1 assets: claims harness verifies the install docs, mandate_claims.yaml gains an
`omega talk` probe rule. Item 4 contract-test spec is well-formed; add: router-collapse PR
must also delete the orphaned `config/routing_table.yaml` AFTER fixing `benchmarks/schema.py`.

## ◈ PASS 6 — THE KEEPER (Lilith lens, brief)

Soul-persistence validation (item 5) is now a DIFFERENT job than the charter wrote:
validate against the NEW approved_lessons evidence surface (20 lessons, 100% coverage),
confirm no DEL-1 target touches SoulStore/entity_workspace injection paths, and confirm
`soul_stage.py` mock-TUI debt is ticketed not forgotten (DC-28).

---

## ⬡ SYNTHESIS — THE REBASED COUNCIL DECREE

**Verdict on the charter**: SOUND SKELETON, STALE FLESH. Structure preserved (6 agenda items,
build/run split, node vetting, unified decree); premises rebased; topology adapted.

**Rebase operations (in order)**:
1. PRE-GATE (before council convenes): land DC-01 fail-closed + DC-29 credential fix.
   Clock-driven, no decisions needed, ~35 min total.
2. REPOINT tracking SSOT: `DEBUT-EXECUTION` → `DEBUT-REMEDIATION`.
3. AMEND DEL-1 #1: routing_table.yaml is NOT a pure deletion — handle
   `benchmarks/schema.py` caller first (or accept benchmark schema change).
4. UPDATE item 5: validate against post-Wave-1 evidence-bearing soul surface.
5. MERGE item 6 with Jem's DC-ledger: gates = bash commands, counts not adjectives;
   adopt "eat your own cooking" (harness binds our own coverage claims).
6. TOPOLOGY: strict serial launches; max ONE subagent alive at a time; mechanical
   dispatch-pairing check before each launch; heartbeat every 5-10 min.
7. ARCHITECT DECISIONS to bundle into the council's opening: corpus-mode flip (DC-11/12),
   Vault Path A vs B (item 3), Drill-4 stratum, FUSE GO (standing wire-path [5] packet).

**L2**: A review council convened over a wounded tree reviews the wounds, not the plan.
Land the known fixes first; spend scarce multi-agent attention only on genuine unknowns.

**L3 (universal)**: **L3-Rebase-Before-Convene** — every standing checklist inherits the
silence of its last revision; before executing any charter, audit its premises against the
cheapest available ground truth (a file listing beats a fleet's assumptions). The map is
not the territory; the dated map is not even the map.

---
*⬡ OMEGA ⬡ KALI ⬡ MEDITATION ⬡ MAKALI-COUNCIL-REBASE ⬡ 2026-08-24*

---
## ⬡ ARCHITECT OVERRIDE + ROOT-CAUSE AMENDMENT (2026-08-24, post-meditation)

**Override**: Strict serial launches REJECTED — "I will not stand for solutions that
choke our productivity out rather than address the core issue." Council topology is
PARALLEL with diagnostic guardrails, not serial avoidance.

**Root-cause investigation executed** (Architect's challenge: "did the guards actually
address the issue or mitigate the symptoms?"):
- Honest answer was: mitigation. Measured: bare import 60MB · real worker ~180MB ·
  4 workers = 723MB aggregate (healthy). The OOM was 16 blind workers COLLIDING WITH
  multiple opencode agent sessions (~1GB+ each) on 14Gi.
- FIX LANDED (`e6791c15`): pytest_xdist_auto_num_workers hook — -n auto now computes
  workers from MemAvailable at launch (350MB/worker + 2.5GB reserve). Idle box = full
  16 workers; under agent pressure = graceful throttle. Mechanism, not cap.

**Amended decree item 6**: PARALLEL launches restored for all councils/sprints.
Guardrail = memory-aware admission at every layer, never serial choking.

**Residual systemic gap (ticket candidate DC-38)**: agent sessions themselves carry no
memory budget — the hook protects tests FROM agents, nothing protects agents from each
other. Horizon-3 digital-watcher scope: cross-workload admission control (cgroup
MemoryMax scopes or OOMProtector extension beyond inference).

**L3 amendment**: A limit chosen for safety must earn its keep by measuring the thing
it limits. Caps are guesses; admission control is a conversation with reality.
