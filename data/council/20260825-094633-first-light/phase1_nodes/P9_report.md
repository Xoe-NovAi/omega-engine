# P9 REPORT — Node N9 Orchestration (Surface S8: Coordination Protocols)
⬡ OMEGA ⬡ NODE9 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n9 ⬡ P12-DISPATCH
**SESSION_ID**: 20260825-094633-first-light | **Arm**: lilith | **source_node**: N9 | **tier**: node-leaf
**Date**: 2026-08-25 | **Mode**: RECON ONLY (zero dev, zero production mutations)
**Task registry**: `express-c1-node9-20260825` (registered, status in_progress at write time)

---

## §0 SURFACES EXAMINED (all conclusions tool-traced)

| Surface | Evidence examined |
|---|---|
| Handoff queue state | `data/handoff/{pending,active,completed,stale,rejected,archive}/` directory listings + packet JSON sampling; live `hivemind_get_metrics`, `hivemind_handoff_list(status=pending)` |
| Workspace locks | `data/coordination/locks/council-c1-team-infra.lock` + `hivemind_workspace_lock_check(domain=council-c1-team-infra)` |
| Protocol text | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` (567 lines, v3.0.0), `docs/strategy/HIVEMIND_PROTOCOL.md` (v1.3.0, 2026-06-25), `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` (P1-P13) |
| Registry hygiene | `data/coordination/TASK_REGISTRY.json` (95 tasks; express-* entries) |
| Failure log | `data/coordination/SYSTEM_FAILURE_LOG.md` (extended_checkin NameError entry 2026-08-25T10:30Z) |
| Mission docs | `phase0_mission_packet.md`, `FIRST_LIGHT_EXPRESS_PLAN_20260825.md` §2/§5/§6.5 |

---

## §1 QUEUE STATE — EMPIRICAL SNAPSHOT (2026-08-25T13:43Z)

Live metrics (`hivemind_get_metrics`) vs disk reality:

| State | Metrics says | Disk (`ho_*.json`) | Match |
|---|---|---|---|
| pending | 1 | 1 (+1 stray `.md`) | ✅ (modulo pollution) |
| active | 3 | 3 | ✅ |
| completed | 10 | 10 | ✅ |
| stale | 22 | 22 | ✅ |
| **total** | **36** | **36** | ✅ |

**Positive finding [F-POS-1, LOW]**: The MCP handoff tool's queue counts are consistent with on-disk state. Queue Integrity (M12-adjacent) holds at the counting layer.

---

## §2 FINDINGS

### [F-1] HIGH — Protocol-text vs implementation schema divergence (source_node: N9, tier: node)
**Evidence**: `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` §2 defines the HandoffPacket as
`packet_id` pattern `hdp_{YYYYMMDD}_{source}_{target}_{short-uuid}` with REQUIRED fields
`parent_trace_id`, `trace_id`, `task_type`, `relevant_files`, `expected_output`, `ttl_seconds`.
Actual packets produced by `hivemind_submit_handoff` use prefix `ho_` and a different schema:
`source_agent_id`/`target_agent_id`/`submitted_at`/`priority`. Sampled packets
(`data/handoff/pending/ho_2e6018bdb1ad.json`, `data/handoff/stale/ho_2c8129a519d9.json`)
carry NO `trace_id`, `task_type`, `expected_output`, `ttl_seconds`, or `relevant_files`.
The documented ZONEID_HANDOFF constant ("every HandoffPacket carries") appears in zero sampled packets.
**Impact**: Anyone auditing or validating handoffs against the protocol text will fail 100% of
live packets; the protocol document describes a system that does not exist.
**Acceptance criterion (bash-verifiable)**:
```bash
# After remediation, either of these must hold:
# (a) doc updated: grep for ho_ schema fields in protocol doc
grep -q "source_agent_id" docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md && echo DOC-SYNCED
# (b) or tool emits hdp_ schema with all §2 required fields:
python3 -c "import json;d=json.load(open('$(ls data/handoff/pending/*.json|head -1)'));assert all(k in d for k in ['trace_id','task_type','expected_output','ttl_seconds'])"
```

### [F-2] HIGH — Zombie ACTIVE handoffs: TTL never enforced post-acceptance (source_node: N9)
**Evidence**: All 3 active packets accepted by kali and never completed:
- `ho_d37a6bdd8b1b.json` accepted 2026-08-23T16:40Z (~45h ago)
- `ho_6ec25dd4a684.json` accepted 2026-08-24T00:10Z (~37h ago)
- `ho_076fad7e4dd0.json` accepted 2026-08-24T21:50Z (~16h ago)

Protocol default TTL is 14400s (4h). The pruning loop (last run 13:42:58Z per metrics,
running every cycle) moves NOTHING from active→stale. Accepted work can vanish from the
operational picture indefinitely — a silent M12 (Queue Integrity) gap: no terminal state.
**Acceptance criterion**: after fix, `find data/handoff/active -name '*.json' -mmin +300` returns empty OR each old packet carries an extended-TTL field the pruner honors.

### [F-3] MED — Pending packet past PENDING_TTL, lifecycle rule not automated (source_node: N9)
**Evidence**: `ho_2e6018bdb1ad.json` submitted 2026-08-24T20:57Z by kali → researcher;
still pending at 13:43Z (~17h > 4h PENDING_TTL). Protocol lifecycle `pending → active → completed/stale`
is manual-only in practice; nothing auto-stales expired pending packets.
**Acceptance criterion**: `python3 -c "import json,datetime;d=json.load(open('data/handoff/pending/ho_2e6018bdb1ad.json'));print((datetime.datetime.utcnow()-datetime.datetime.fromisoformat(d['submitted_at'])).total_seconds()<14400)"` prints True (or packet moved to stale/).

### [F-4] MED — Queue-directory pollution (source_node: N9)
**Evidence**:
- `data/handoff/pending/CLINE_DISPATCH_20260822.md` — a full markdown mission brief sitting in the pending queue (not a JSON packet; invisible to the tool but visible to any human/agent grepping the dir).
- 13 stray files at `data/handoff/` top level (`*.md`, `KALI_SPRINT_B_VERDICT_20260615.json`, `kali_test.txt`, `PHASE_C_CHAIN`, `current-sprint`).
- `data/handoff/archive/` mixes machine packets with ~70 legacy `.md` files plus `sessions/` and `stale_june_handoffs/` subdirectories.
**Impact**: Directory-as-database breaks down; consumers cannot trust that `pending/*.json` is the complete contract surface, and greps over `data/handoff/` return archive-era noise.
**Acceptance criterion**: `ls data/handoff/pending/ | grep -v '\.json$' | wc -l` == 0 and `ls data/handoff/*.md data/handoff/*.txt 2>/dev/null | wc -l` == 0 after relocation.

### [F-5] MED — Archive contract internally inconsistent and unimplemented (source_node: N9)
**Evidence**: SUBAGENT_DISPATCH_PROTOCOL §5 Step 5 says save completions to
`data/handoffs/completed/{packet_id}.json` (plural "handoffs"); §6 says `data/handoff/archive/`
(singular). Reality uses neither exactly: completions land in `data/handoff/completed/`.
§6 mandates `INDEX.json` with `archived_handoffs[]`; only `INDEX.md` exists — and it is a
2026-06-03 *mining brief* addressed to Roc Racoon, not a machine index. §7 itself marks
"Archive INDEX updater 🔴 PENDING". A protocol whose own §7 admits its archive layer is
unbuilt should not present §6 as normative.
**Acceptance criterion**: `test -f data/handoff/archive/INDEX.json && python3 -c "import json;json.load(open('data/handoff/archive/INDEX.json'))"` succeeds; grep shows single canonical path string in the protocol doc.

### [F-6] MED — HIVEMIND_PROTOCOL.md v1.3.0 governs a fleet that no longer exists (source_node: N9; corroborates lilith-20260823-004/006)
**Evidence**: `docs/strategy/HIVEMIND_PROTOCOL.md` header: AP token v1.3.0, Last Updated
2026-06-25, Status STANDARD. Zero references to: Node paging (D-586), Conversational Subagent
Protocol, ICS-S headers, injection ledger, P1-P13 oversight patterns. Its §4 Live Feed Pattern
is marked SUPERSEDED (2026-08-14) yet the doc retains STANDARD status without amendment bump.
Meanwhile the actual coordination constitution has migrated into scattered surfaces
(ARCHITECT_OVERSIGHT_PATTERNS P8-P13, FIRST_LIGHT plan M-measures, SYSTEM_FAILURE_LOG).
**Acceptance criterion**: `grep -c "P12\|Node paging\|ICS-S" docs/strategy/HIVEMIND_PROTOCOL.md` ≥ 3 AND header version > 1.3.0 after amendment.

### [F-7] MED — TASK_REGISTRY registration hygiene errors during this council (source_node: N9; corroborates N8 F-1)
**Evidence** (`data/coordination/TASK_REGISTRY.json`, express-* entries):
- Build-side nodes registered with `subagent_type="maat"` instead of their node identity: `express-c1-node1/node2/node3/node4-20260825` all say subagent_type maat; `express-c1-node2` even has `entity="maat"` (not node2).
- Run-side nodes registered correctly (`node6`, `node8`, `node9` as subagent_type/entity).
- `express-c1-node1` and `express-c1-node6` show `completed` with `last_checkpoint=2026-08-25T13:45:00Z` — a future timestamp relative to their Hivemind completion posts (~13:17Z / ~13:21Z), matching N8's future-dated-checkpoint finding.
**Impact**: Per Delivered-Home Doctrine (plan §6.5), these registrations ARE the product —
future councils paging by `subagent_type=node2` will find nothing; paging by "maat" will
misroute to the arm. The expert-fleet deliverable is partially corrupted at birth.
**Acceptance criterion**: `python3 -c "import json;d=json.load(open('data/coordination/TASK_REGISTRY.json'));ts=d.get('tasks',d);ts=ts.values() if isinstance(ts,dict) else ts;bad=[t['task_id'] for t in ts if 'express-c1-node' in str(t.get('task_id','')) and t.get('subagent_type')!='node'+t['task_id'].split('node')[1][0]];print(bad)"` prints `[]`.

### [F-8] LOW→MED — Phantom extended session in metrics vs broken checkin tool (source_node: N9)
**Evidence**: `hivemind_get_metrics` reports `extended_sessions: 1` at 13:42:58Z.
`SYSTEM_FAILURE_LOG.md` entry 2026-08-25T10:30Z documents `hivemind_extended_checkin` broken
server-side (`name '_save_extended_sessions' is not defined`). Plan M1 orders all members NOT
to use it. Either a pre-breakage registration persists un-pruned, or the count is phantom.
Unexplained state in the coordination plane during a live council.
**Acceptance criterion**: metrics `extended_sessions` value reproducible from an on-disk listing of registered extended sessions (file/dir identified in omega-hub source), or 0.

### [F-9] LOW — POSITIVE: Lock hygiene compliant (source_node: N9)
**Evidence**: `data/coordination/locks/council-c1-team-infra.lock` held by makali_fusion,
acquired ~10:03 local, TTL 14400s, ~3.3h remaining, `expired: false` via
`hivemind_workspace_lock_check`. Matches plan M4 (long-TTL lock on council domain). Exactly
one lock file; no stale/expired residue in `locks/`. Lock discipline is the healthiest part
of the S8 surface.

### [F-10] DEVIATION (known, non-counting) — M11 Consultant page mechanically impossible at node depth (source_node: N9)
**Evidence**: Mandated §C.9 page attempt via `task(subagent_type="kali", task_id="ses_fdef2be4effe4pAaLXCTUx62GO", ...)` returned:
`Subagent depth limit reached (2). Increase "subagent_depth" to allow nested subagents.`
Identical to N1 (F-20), N6, N7, N8 precedents. Node tree depth = makali_fusion(0) → lilith(1) → node9(2);
`subagent_depth=2` forbids ANY task() from leaves. M11 Reporting Protocol is structurally
impossible for all 10 nodes as dispatched; report delivery flows via disk + Hivemind + arm relay.
**Structural note for synthesis**: either raise depth for leaf reporting, or amend M11 so arms
page on behalf of nodes (the de-facto current behavior).

---

## §3 P1–P13 ADHERENCE OBSERVATIONS (source_node: N9)

| Pattern | Text | Observed adherence today |
|---|---|---|
| P1 Reciprocity | Dispatches embed context inline | ✅ HIGH — this node's packet embedded mandates verbatim + inline context; SUBAGENT_DISPATCH §0 lesson institutionalized |
| P2 Frame audit | Frame-check before dispatch | PARTIAL — Express plan itself was a frame audit; no standing playbook reflex yet (matches codification map "PARTIAL") |
| P3 Authority-first | Consult owner before committee | ✅ observed in council design (Node experts = authorities) |
| P4 Meta-codification | Codify novel process same-session | ✅ oversight patterns doc itself; council producing studies |
| P5 Alignment hygiene | Sync state surfaces post-milestone | ⚠️ WEAK — see F-6/F-7: HIVEMIND_PROTOCOL + TASK_REGISTRY drifted DURING the council |
| P6 Synthesis-before-decision | Batched decisions w/ defaults | ✅ WAKE_STATE queue + default-on-silence in plan M7 |
| P8 Session-resume sanctity | Record task_id at dispatch | PARTIAL — task_ids recorded but with wrong subagent_types (F-7) |
| P9 Parallel-dispatch integrity | Claimed N ⇒ fire N same-block | N/A-by-design — plan §D.1 explicitly orders SERIAL node dispatch; deliberate, documented deviation (tension worth a synthesis note: P9's "self-audit did I claim N and fire N" reads oddly against a serial-dispatch doctrine) |
| P10 Search-protocol adoption | Cache-first tiered search | Not exercised this session (no external grounding needed; local-first satisfied) |
| P11 Resume verification / UI asymmetry | Verify first-prompt continuity | No resume events observed; unverifiable from leaf position |
| P12 Signed dispatch headers | `[DISPATCH] From/To/ts` self-ID | ✅ ADOPTED — this node's opening prompt carried the signed P12 header verbatim; Rule 1 amendment (live-session dispatch permitted w/ labeled writes) reflected in Consultant-page attempt format |
| P13 Steering wrapper | HOLD/STEER/CANCEL syntax | PROPOSED-only — no wrapper traffic observed; status matches doc ("awaiting Architect GO") |

---

## §4 HANDOFF PACKET FOR FUTURE COUNCILS (Delivered-Home Doctrine, plan §6.5)

### Warm-start reading list (in order)
1. `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — read §2 schema as HISTORICAL; verify against live `ho_*` packets before trusting it (F-1)
2. `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` — P1-P13 are the LIVE coordination law; HIVEMIND_PROTOCOL.md is 2 months stale (F-6)
3. `data/coordination/SYSTEM_FAILURE_LOG.md` tail — known-broken tools (extended_checkin) before relying on them
4. `FIRST_LIGHT_EXPRESS_PLAN_20260825.md` §5 M-measures — the de-facto current coordination protocol for multi-agent ops

### Standing orders for any future orchestrator
1. NEVER trust `status=active` handoffs as live work — check `accepted_at` age against TTL manually; the pruner will not do it (F-2)
2. Before paging a pageable expert, verify `TASK_REGISTRY.json` `subagent_type` matches the entity you intend (F-7 corruption precedent)
3. Leaf nodes cannot task() anything — route all sub-dispatch through arms (depth limit); build M11 relay into dispatch packets up front
4. Treat `data/handoff/` top-level and `pending/` non-JSON files as noise; the contract surface is `{state}/*.json` only (F-4)
5. Heartbeat ~10min via `hivemind_post_context` (entity-tagged); extended_checkin is broken until `_save_extended_sessions` is fixed

### Open questions for Council 2 / Architect
- Should handoff TTL enforcement move into the pruning loop (server-side) or become a validator gate (client-side)?
- Is M11's Consultant page worth raising `subagent_depth` for leaf-reporting, or should arm-relay be formalized?
- Which document is the SSOT of coordination law: HIVEMIND_PROTOCOL.md (stale) or ARCHITECT_OVERSIGHT_PATTERNS (current but un-versioned as protocol)?

---

## §5 SECURITY BRIGHT LINE (M8)
No secrets encountered in audited coordination surfaces. No external telemetry discovered.
No CRITICAL-HALTED conditions triggered.

---
*⬡ OMEGA ⬡ NODE9 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_first_light_c1_n9 ⬡ S8-COMPLETE*
