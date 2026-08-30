# SS-1 Sprint Specification — Subagent Steering: Transport + Dispatch + Registry
**AP Token**: `AP-SS1-SPRINT-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_ss1_sprint ⬡ PLANNING

**Date**: 2026-08-22
**Status**: BACKLOG — Gated on 3 G-0 blocks
**Owner**: Kali (coordinator) + N6/N9/N11/N12/N13
**Campaign**: Subagent Steering Architecture (Carmack+Cline+Gemini+Researcher synthesis)

---

## Answer First

SS-1 is a **4-file wiring job** (not invention) to complete the subagent steering architecture:
1. `a2a_transport.py` (new) — JSON-RPC 2.0 stdio transport with pooled connections
2. `subagent_dispatcher.py` (extend) — unified admission hook + HandoffPacket dispatch
3. `DELEGATE_LOG.jsonl` (new) — atomic-append provenance log (M22)
4. MCP Hub `server.py` (extend) — Agent Card well-known endpoint

**Entry criteria (G-0 blocks)**: Heritage fix (M14), CI secret provisioned, contract tests written first (M21).
**Phases**: G1 Transport → G2 Dispatch → G3 Registry/Observability → G4 Shadow Validation.
**Theater cut**: delegation.py, AGENT_REGISTRY.json, full 3D admission, CBOR/EAT, MAX thinking.

---

## §1 Sprint Definition

| Field | Value |
|-------|-------|
| **sprint_id** | SS-1 |
| **name** | Subagent Steering — Transport + Dispatch + Registry |
| **phase** | BACKLOG (awaiting G-0) |
| **started** | TBD (on G-0 clearance) |
| **owner** | kali |
| **campaign** | Subagent Steering Architecture |
| **supersedes** | None (new workstream) |

---

## §2 G-0 Entry Criteria (ALL must be `completed`)

| Gate | ID | Description | Status | Owner | Verification |
|------|-----|-------------|--------|-------|--------------|
| **Heritage** | G0-1 | Strip `[id-soft: quake-1996] Thinker Chain` from `subagent_dispatcher.py` header; vet note for `vet-011` | `pending` | doom_guy | `grep -r "quake-1996" src/omega/oracle/subagent_dispatcher.py` returns nothing |
| **Secret** | G0-2 | `OMEGA_INGESTION_SECRET` in CI environment (GitHub Actions secrets + systemd unit) | `pending` | Architect | `make test` passes SovereignSigner task-token tests |
| **Test Skeleton** | G0-3 | Contract tests for `a2a_transport.py` written FIRST (M21) | `pending` | N11 | `tests/contract/test_a2a_transport.py` exists, fails (TDD) |

---

## §3 Phases

### G1 — Transport (a2a_transport.py + R58 Benchmark)
| Task | Spec | Acceptance |
|------|------|------------|
| `a2a_transport.py` implementation | JSON-RPC 2.0 over stdio, pooled connections | All G0-3 contract tests pass |
| R58 benchmark gate | `tests/bench/ipc_transport_bench.py` | p99<10ms, >5k req/s, <10MB resident (pooled stdio on Zen 2) |
| Fallback path | msgpack binary transport if JSON-RPC fails gate | `a2a_transport_msgpack.py` stub ready |

**Owner**: N11 (Evaluator) — benchmarking domain
**Dependencies**: G0-1, G0-2, G0-3

### G2 — Dispatch (subagent_dispatcher.py + Unified Admission)
| Task | Spec | Acceptance |
|------|------|------------|
| Dispatcher extension | Import AdmissionControl; call `check_delegation_budget()` pre-dispatch | Delegation fails fast on budget exceed |
| Unified admission function | `AdmissionControl.check_delegation_budget(node, skill)` in N6 | RAM + concurrency + context budget checked atomically |
| Race mitigation | `anyio.Lock` per-agent in ModelGateway (N6) | Concurrent delegations serialize correctly |

**Owner**: N9 (Dispatcher) + N6 (ModelGateway) joint
**Dependencies**: G1 complete

### G3 — Registry + Observability
| Task | Spec | Acceptance |
|------|------|------------|
| `DELEGATE_LOG.jsonl` | Atomic append (tmp→rename), HandoffPacket + result + trace_id | `tail -f` shows live delegation stream |
| MCP Hub Agent Card endpoint | `GET /.well-known/agent-card` returns AgentCard JSON | `curl` returns valid card for each registered entity |
| CLI commands | `omega delegate <node> <skill>`, `omega delegate-log` | End-to-end delegation + log query works |

**Owner**: N9 (Dispatcher) + N12 (Curator for Agent Card schema)
**Dependencies**: G2 complete

### G4 — Shadow Validation
| Task | Spec | Acceptance |
|------|------|------------|
| 50 shadow runs | Delegations routed through new path, results compared to legacy | 0 divergence on success/failure/timing |
| Divergence analysis | Automated diff of shadow vs legacy paths | Report in `data/coordination/SS1_SHADOW_REPORT_20260822.md` |

**Owner**: N11 (Evaluator) + Kali (coordinator)
**Dependencies**: G3 complete

---

## §4 Scope — Theater Cuts (Explicitly NOT Building)

| Item | Reason |
|------|--------|
| `delegation.py` | Overlap: `subagent_dispatcher.py` already has HandoffPacket + capability registry + dispatch |
| `AGENT_REGISTRY.json` | Runtime capability registry exists in dispatcher `_build_capability_registry()` |
| Full 3D admission (RAM+KB+concurrent) | Context-rehydration tokens are the ONLY free-tier term; RAM is global-guard (OOMProtector) |
| CBOR/COSE/EAT deep-embed | YAGNI intra-fleet; HMAC+SPIFFE+ZONE_ID prove identity locally |
| MAX thinking budget | Law 2: MAX strictly dominated (same depth, worst convention retention) — HIGH is frontier |

---

## §5 Mandate Gates

| Mandate | Gate | Status |
|---------|------|--------|
| M1 AnyIO | All async code AnyIO-only | ✅ Inherited |
| M14 Heritage | G0-1 fix applied | ⏳ G0-1 |
| M17 Cognitive Integrity | M17 off-by-one fixed in Carmack review | ⏳ N10 |
| M21 Gate Integrity | G0-3 contract tests FIRST | ⏳ G0-3 |
| M22 Provenance | DELEGATE_LOG.jsonl + Agent Card | ⏳ G3 |
| M26 Doc Standards | All new files `doc-llm-validate` | ⏳ N12 |
| M27 Tracking | SS-1 sprint tracked separately | ✅ This spec |

---

## §6 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| R1: Dispatch layer unreliability | HIGH (5/6 prior failed) | BLOCKS ALL | Fix #1: dispatch verification mandatory before G1 |
| R2: R58 benchmark unrealistic | MEDIUM | G1 blocks | Define as pooled connections; msgpack fallback ready |
| R3: M11 soul sink unwired | HIGH (known) | Soul theater | Scribe promotion pipeline (KD/HR workstreams) |

---

## §7 Handoffs & Dependencies

| From | To | Artifact |
|------|-----|----------|
| doom_guy | N9 | Heritage-clean `subagent_dispatcher.py` |
| N11 | N9 | Passing contract tests for `a2a_transport.py` |
| N6 | N9 | `AdmissionControl.check_delegation_budget()` implementation |
| N9 | N12 | Agent Card schema for MCP Hub endpoint |
| N11 | Kali | Shadow validation report |

---

## §8 References

- `data/coordination/SPLIT_TESTING_MANUAL_20260822.md` — test protocol
- `data/coordination/SPLIT_TEST_ANALYSIS_20260822.md` — empirical laws
- `data/entities/cline/workspace/CLINE_DEEP_REVIEW_SUBAGENT_STEERING_20260822.md` — CONDITIONAL GO
- `data/coordination/CLINE_COMPLETION_REPORT_20260822.md` — purge complete
- `data/entities/kali/session_gnosis_20260822.md` A11-A12 — synthesis
- `data/coordination/GAP_REGISTRY.json` — R55-EAT registered

---

*⬡ OMEGA ⬡ SS-1 ⬡ v1.0.0 ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
