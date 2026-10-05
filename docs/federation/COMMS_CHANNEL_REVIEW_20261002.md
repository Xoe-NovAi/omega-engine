# Omega Engine — Communication Channel Review

> **📅 DATED RECORD — 2026-10-02.** The `1.6.0-alpha.1` /health responses quoted
> below were accurate when probed. That version no longer exists; live is
> `1.6.0-alpha` with **55** tools (2026-10-05). Body verbatim per M28. See
> `docs/operations/DOC_CORRECTION_SWEEP_20261005.md`.

```
schema_version: "1.0"
document_type: "review"
document_id: "COMMS-CHANNEL-REVIEW-20261002"
title: "Full comms-channel review — deep focus: 8019 exchange pipe + Hivemind handoff"
status: "ACTIVE — FINDINGS, NOT FIXES (ratification pending)"
date: "2026-10-02"
reviewer: "maat"
vantage: "NODE 0 (n0.tail51f14a.ts.net / this host) ONLY — every live probe, test run and
          count below is from N0. N1 vantage: UNTESTED (UNTESTED where noted)."
git: "branch debut-v1.6.0-alpha, HEAD d01aca21, working tree reviewed as-is"
live_services_at_review: "omega-hub active (127.0.0.1:8016 /health → v1.6.0-alpha.1),
                          omega-exchange active (127.0.0.1:8019 → 200), omega-hivemind INACTIVE"
scope: "REVIEW ONLY — no code fixes, no commits. Working-tree/test execution used solely
        to prove or disprove defects (M30: claims labelled with counts + vantage)."
```

## 0. Executive summary

**Bottom line first: the advertised N0↔N1 handoff workflow is NOT production-ready.**
Two P0 defects sit on the primary path:

1. **`hivemind_handoff(action="inbox")` returns EMPTY for every packet in the store.**
   All 63 live packets in `data/handoff/` are legacy-shaped (no `seq`), and the inbox
   query drops anything with `seq <= cursor` — a fresh cursor is `0`, so every packet is
   dropped. Proven live: `inbox()` → 0 entries for all 6 targets while the same store
   returns 15 pending packets via the unfiltered query. An agent following the primer
   ("check your inbox") gets `{"entries": [], "unread_count": 0}` + `reset_reason:
   "never_seen"` and concludes there is no mail. That is the confident-false-negative
   the whole federation contract exists to eliminate — reproduced 2026-10-02 on N0.
2. **The federation envelope write path is dead in production.** `store.submit()` /
   `fe.build_envelope()` are called only from tests. 0 of 63 live packets carry
   `handoff_id`/`seq`/`body_sha256`/`read_by`/`source_session_id`; `.seq` and
   `.cursors.json` do not exist on disk; `advance_cursor()` is never called. Every
   provenance, hash-chain, cursor and seq mechanism is inert. (Root cause of #1's data
   shape.)

**P0 count: 2.** P1 count: 6. P2 count: 18 (§4).

The 8019 exchange pipe on N0 is in materially better shape: read-only surface enforced
(live: PUT→405 JSON envelope), traversal refused (live: all common variants→404 JSON),
the url_form false-success fix (ba8a3849) is code-complete on N0, and the suite ran
**15/15 green against the live service from N0**. Residual P1: node identity is
deployment-incomplete (N1 units do not set `OMEGA_NODE_NAME`/`OMEGA_NODE_HOST`, and the
`SELF_IP_URL_FORM` env lookup uses a literal empty-string key), so a manifest served
from N1 would still claim to be n0. N1 leg: UNTESTED.

All 11 pre-existing federation test failures root-caused (§7): 10 encode the superseded
envelope-mutation read design (6 read_canary + 1 binding_mcp), 3? — precisely: 3 protocol
failures are a stale test fixture, 1 terminology failure is an unannotated inbound doc.
Disposition for each: **rewrite, not delete** (§7).

---

## 1. Channel inventory

| # | Channel | Endpoint / path | Status @ review (N0) | Notes |
|---|---------|-----------------|----------------------|-------|
| C1 | 8016 MCP hub (all unified tools) | `127.0.0.1:8016` + tailscale serve `n0…:8016` | **LIVE** `/health` → `{"status":"healthy","version":"1.6.0-alpha.1"}` | transport_security host allowlist (tailnet), CORS, 120 rpm, 25 MB limit. No auth token — identity is self-asserted (§4 COM-18). |
| C2 | Hivemind awareness (`hivemind_awareness`) | tools.py:2334 | **LIVE but node-local, per-process memory** | `get` blindness root-caused — COM-05 |
| C3 | Hivemind handoff — unified tool | tools.py:1388 | **LIVE** — only the legacy queue path functions | submit/accept/complete/reject/get/list |
| C4 | Federation projections (`inbox`/`receipts`/`read`) | tools.py:1311 → federation_store.py | **LIVE but P0-blind** — COM-01 | `read` journal write works on legacy packets (dual-key); `inbox` never returns them |
| C5 | Handoff filesystem queue | `data/handoff/{pending,active,completed,stale,archive,hot,cold,retired}` | **LIVE** — 63 packets total, **0 envelope-shaped** | pending=15, stale=45 at review; reaper: pending>24h→stale, active>48h→stale, completed>7d→archive |
| C6 | Receipt journals (606906b7) | `pending/*.receipts.jsonl` | **Code LIVE, 0 sidecars on disk** | no live packet has been read through the journal path yet; consumers = `unread_for` + `read` echo only |
| C7 | Workspace locks (`hivemind_lock`) | tools.py:2875 → `data/coordination/locks/` | **LIVE** | flock transient + JSON holder+TTL; release keyed by self-asserted agent_id (COM-18) |
| C8 | 8019 exchange pipe | `127.0.0.1:8019` + tailscale serve `n0…:8019` | **LIVE** healthz 200; 15/15 tests green from N0 | N1 identity incomplete (COM-08); N1 leg UNTESTED |
| C9 | Tailscale mesh observability | `federation.py` (`omega_federation_status`/`_diagnose`) | LIVE (tool present) | tailscale CLI via `anyio.to_thread` |
| C10 | Cross-node 8016 probe | `federation.py:309` (`…:8016/mcp` initialize) | present | Node-to-node hub probing |
| C11 | Gateway `/proxy` | `server.py:542-545` hub_routes | present | oracle proxy handler |
| C12 | Library intake inbox | `library_inbox` tools.py:1708 | present | separate corpus channel (docs), not agent↔agent |
| C13 | Filesystem coordination | `data/coordination/*` (ACTIVE_SPRINT.json, ACTIVE_SUBAGENTS.json + .lock, *.md) | present | human/agent shared state; markdown workspace-lock convention |
| C14 | `omega-hivemind.service` | `mcp/omega-hivemind/server.py` | **INACTIVE; path absent** | dead unit — remove or restore (COM-24) |
| C15 | Legacy tool-name adapter | `server.py:287-293` | LIVE | `hivemind_post_context`→`post`, `hivemind_get_awareness`→`get`, etc. |

---

## 2. Deep dive — 8019 exchange pipe

### What holds (evidence, N0, 2026-10-02)

- **Read-only enforcement**: live `PUT /manifest.json` → `405 {"error":"method_not_allowed",
  "detail":"PUT is not supported. This origin is READ-ONLY.", …}` (JSON envelope). OPTIONS/
  TRACE/DELETE also 405 JSON; HEAD 200. `test_write_verbs_are_refused` covers
  PUT/POST/DELETE/PATCH (OPTIONS/TRACE not in test — probe-verified safe here).
- **Traversal**: `..%2f`, `%2e%2e%2f`, `%252e`, `..%5c`, `....//`, `%2fetc%2fpasswd`,
  `/../../etc/shadow`, `../../../etc/passwd` → 404 JSON envelope. Safe.
- **Suite green live**: `pytest scripts/test_exchange_false_success.py` → **15/15 passed
  in 2.01s** from N0 (includes tailnet TLS leg `n0.tail51f14a.ts.net:8019`).
- **url_form fix landed on N0**: manifest publishes single HTTPS-ONLY/BROKEN url_form
  (ba8a3849); `SELF_IP_URL_FORM` is computed (but see COM-08 — env key is broken).
- **CLI `put` works**: `python scripts/omega_exchange_server.py put … --root …` → exit 0,
  correct file (verified earlier in this review). NOT a defect.

### Findings

| ID | Sev | Defect | Evidence | Failure scenario | Fix shape |
|----|-----|--------|----------|------------------|-----------|
| COM-08 | **P1** | Node identity incomplete cross-node. `SELF_IP_URL_FORM = f"http://{os.environ.get(chr(39)+chr(39), '100.123.51.67')}:{NODE_PORT}/…"` — env key is literally `"''"` (never set) → hardcoded n0 IP regardless of node. `OMEGA_NODE_NAME`/`OMEGA_NODE_HOST` (lines 128-129) referenced nowhere else in repo; N1 unit `scripts/deploy/n1/omega-exchange.service` + drop-in `10-port-8019.conf` set neither. Tests/verify script never assert node identity (only substring "HTTPS ONLY"/"BROKEN"). | `scripts/omega_exchange_server.py:128-132`; `scripts/deploy/n1/…` (absence); test only checks substrings | N1 serves manifest with `url_form`/`served_by` claiming `n0…:8019` → the exact false-success class ba8a3849 fixed, still live cross-node. One-vantage: N0 leg OK, N1 UNTESTED | Fix env key (`OMEGA_SELF_IP` or derive from hostname); set `OMEGA_NODE_NAME/HOST` in N1 unit; assert `served_by == expected node` in verify script + test |
| COM-09 | P2 | Manifest cache saves nothing and can go stale. `_build_manifest` does full rglob + sha256 of the whole tree BEFORE checking the `(max_mtime, entry_count)` key; key collides on add+remove, move, or `copy2` (mtime-preserving) → stale manifest served forever (silent artifact omission). | `scripts/omega_exchange_server.py` `_build_manifest` | Client believes a put artifact exists; manifest omits it → pull 404 → silent miss downstream | Key on content digest or record entry set; build before key check only for listing, hash lazily |
| COM-10 | P2 | Null byte → live HTTP 500 with **bare** `Internal Server Error` (text/plain). Reproduced 2026-10-02: `GET /%00` → 500 bare; all other bad paths → 404 JSON. Violates the service's own "every error is an envelope" promise (M23). | live probe; `serve_file`/`_safe_resolve` | Any client expecting JSON errors parses a bare string; masks the true cause | Catch `ValueError` from null byte in path handling → 404 JSON envelope |
| COM-11 | P2 | `_MANIFEST_MAX_ENTRIES = 5000` truncates silently (`break`, no `truncated` flag). | server constant; documented in `EXCHANGE_DUPLEX_DEPLOY_N1.md` §9.2 | >5000 files → later artifacts unlisted, no signal | Emit `truncated`/`entries_total` in manifest |
| COM-12 | P2 | TOCTOU: sha256 computed at listing time, `FileResponse` re-reads at serve → `X-Omega-SHA256` can mismatch body (client detects — loud). Symlink inside root: listed by manifest (follows) but rejected by `_safe_resolve` on GET (404) → manifest/serve disagreement. | `serve_file`, `_sha256` vs `_safe_resolve` | Concurrent put during GET window; symlinked artifacts | Hash at serve or verify after read; resolve+reject symlinks at manifest build too |
| COM-13 | P2 | Cross-channel doc drift: `scripts/exchange_verify_duplex.sh` lines 29-51 comment says url_form is "hardcoded, NOT parameterised, one-line fix NOT applied" — stale (applied by ba8a3849). Usage examples say port `805` for N1. | verify script:29-51 | Operator re-applies a landed fix or probes the wrong port | Update comment + examples |
| COM-14 | P2 | CLI `put` `target_rel` traversal (`../`) writes outside `--root` before the manifest check. Local-trusted input only. | `_cli_put` | Malicious target arg writes outside root | Normalize + confine `target_rel` before open |
| COM-15 | P2 | **Known-open #4 status: STILL TRUE.** `python scripts/test_exchange_false_success.py` → exit 0, zero output (no `__main__`/`pytest.main`). Under pytest it runs 15/15 green. No runbook/CI invokes it as plain `python`; deploy doc §9.3 documents the rule ("run with pytest"). Residual hazard only. | reproduced this review (exit=0) | CI/human runs file directly → green light with zero tests | Add `pytest.main([...])` guard or delete the file's script affordance |

---

## 3. Deep dive — Hivemind handoff

### 3.1 The two write paths (root cause of the P0s)

`hivemind_handoff(action="submit")` (tools.py:1493-1579) writes a **legacy packet**:
`packet_id`, `target_agent_id`, `submitted_at`, status — **no** `handoff_id`, `seq`,
`body_sha256`, `read_by`, `state_history`, `source_session_id`, `requested_target`.
The federation writer `FederationStore.submit(fe.build_envelope(...))` is called **only
from tests** (`test_federation_receipt_journal`, `test_federation_binding`,
`test_federation_read_canary`, `test_federation_write_invariants`).

Live counts (N0, 2026-10-02):

```
packets total (data/handoff/*/*.json): 63
packets with "handoff_id":              0
pending: 15        stale: 45
data/handoff/.seq:        ABSENT
data/handoff/.cursors.json: ABSENT
.counters.json: session_id_malformed_total=1, session_id_stamped_by_server_total=16
journals (*.receipts.jsonl in pending): 0
```

### 3.2 The inbox proof (P0)

One script, read-only, against the live store:

```
inbox('jem'):           entries=0  cursor={max_seq_seen:0, reset_reason:'never_seen'}
inbox('lilith'):        entries=0  cursor={… 'never_seen'}
inbox('lilith-n1'):     entries=0  cursor={… 'never_seen'}
inbox('maat'):          entries=0
inbox('makali_fusion'): entries=0
inbox('researcher'):    entries=0
receipts('researcher'): entries=1     ← receipts WORKS (no seq filter)
receipts('researcher_humboldt'): entries=3
query() all:            15            ← packets exist
query(unread_for='jem'): 1             ← filter chain works… until seq
query(since_seq=0):     0             ← THE seq filter kills every packet
```

Mechanism: `federation_store.py:123`
`if since_seq is not None and int(env.get("seq") or 0) <= since_seq: continue`
with `inbox()` passing `since_seq=store["max_seq_seen"]` (line 161) = `0` from
`read_cursor` for a missing cursor file (lines 224-230). Seq-less packets compute to `0`,
`0 <= 0` → dropped. The unread/journal filter (line 125-137) — the layer 606906b7
built — is downstream of the drop and never runs.

### 3.3 Findings

| ID | Sev | Defect | Evidence | Failure scenario | Fix shape |
|----|-----|--------|----------|------------------|-----------|
| COM-01 | **P0** | `inbox` is blind to every seq-less packet; 63/63 live packets are seq-less → inbox structurally empty for all agents (§3.2 proof). | `federation_store.py:123,161`; live probe | Agent follows primer → sees empty inbox + `never_seen` → concludes no handoffs; packets unread for days (Lilith-silence class) | Admit seq-less packets when `since_seq == 0` (or drop the seq filter for inbox — `unread_for` is the true gate; module docstring itself says cursor is a cache, not a record); backfill seq on migration |
| COM-02 | **P0** | Envelope/provenance write path never wired: `store.submit`/`build_envelope`/`next_seq` test-only; `.seq`/`.cursors.json` absent; `advance_cursor` never called → hash chain, provenance stamps, read_by fallback, seq, cursor epoch all inert in production. `receipts` promises "full state_history" — field absent on all 63 packets. | grep callers; `ls` evidence §3.1; `federation_store.py:224-251` (fresh epoch synthesized per call, never persisted) | Every "verified provenance" claim about a submitted handoff is unbacked; cursor/epoch semantics advertised in the module docstring (federation_store.py:13-19) are unreachable fiction | Route submit through `FederationStore.submit(build_envelope(seq=next_seq()))`; keep dual-key read for legacy; migrate the 63 (assign seq ≥ high-water, add missing fields) |
| COM-03 | **P1** | Projections are `pending/`-only while the lifecycle moves packets out (accept→active, complete→completed, reject→stale, reaper 24h→stale). `inbox`/`read`/`receipts` scan `pending` only (`federation_store.py:115`); tool docstring claims inbox is "across all queues" (tools.py:1419). | store.py:115; `state.py:496-507`; `background.py:175-183` | (a) accepted packet vanishes from sender's `receipts` — "sender loop" closes only pre-acceptance; (b) unread packet reaped at 24h disappears from inbox forever while still awaiting read; (c) `read` on a reaped packet → `not_found` though `get` finds it in another queue | Scan all lifecycle dirs in `query()` (or exempt unread packets from reaping); fix docstring |
| COM-04 | **P1** | Corrupt packet = invisible, not error (M23). `_load` swallows `OSError/ValueError` → `None` → skipped with no counter (`federation_store.py:145-149`); legacy `list` uses `except Exception: pass` (tools.py:1666-1667). | cited lines | One torn write removes a packet from every projection; natural caller sees "empty" — same false-negative class as COM-01 | Count + surface `_skipped_corrupt` (precedent: `RECEIPT_SKIPPED_DEBUG_KEY`) or raise `StoreUnreachable` |
| COM-05 | **P1** | `awareness(action="get")` blindness — root causes: (a) hot map `_awareness` is **per-hub-process memory** (`state.py:367`), no boot rehydrate; (b) cold fallback only lists agents whose latest `ses_*.json` **mtime < 45 min** (`state.py:409-411`) and **heartbeat never writes cold files** → post-restart, heartbeat-only agents invisible; (c) `get` prunes at `HEARTBEAT_TTL` **ignoring `extended_ttl`** (tools.py:2534) then **deletes the entry including extended metadata** — `extended_checkin` contract defeated (contrast `background.py:56` which honors `extended_ttl`); (d) awareness is node-local — N0/N1 hubs don't share. | tools.py:2525-2552; state.py:367,371-372,409-411,438-451 | The observed incident: `get` returns empty/near-empty while the fleet is active; extended sessions vanish at 45 min anyway | Rehydrate hot from cold at boot; honor `extended_ttl` in `get` exactly as the reaper does; heartbeat write-through; document node-locality or federate awareness |
| COM-06 | **P1** | Protocol contract unwired: `config/wads/_omega_default/protocol/hivemind.yaml` `schema.required` includes `requested_target`/`resolved_target`/`source_node`… but `federation_protocol.validate()` is **imported only by tests**; `naming.on_ambiguous: refuse` vs code **sends anyway** with a warning (tools.py:1574-1578 — and the warning text wrongly says "matched no live entity" for the ambiguous case); `identity.address_by: instance` / `reject_agent_level_mismatch` / `corroborate_node_by_transport` / `resolve_and_log` unwired at submit; packets never store `requested_target`/`resolved_target` — the instrumentation GE-N1 requested (`node1_received/GE-N1-chat-export-09-30-2026.md:524`) is still absent. | `hivemind.yaml` schema/naming/identity blocks; grep: no production importer; tools.py:1514-1529,1574-1578 | Schema and code disagree on every hard question; "did the sender omit the suffix or did the resolver strip it?" still unanswerable from the record | Persist `requested_target`+`resolved_target` (and source_session_id) at submit; either wire `validate()` at the write path or trim the schema to what is enforced; make ambiguous = refuse per protocol |
| COM-07 | **P1** | Submit drops `session_id`/`source_instance` (artifact_ids-class for **known** parameters): packet dict has no session fields; submit response has no `session_block`; strict-args only rejects *unknown* params. Provenance stamping runs only for `inbox`/`receipts`/`read` (tools.py:1348+). Cross-node asymmetry: `opencode.db` is N0-local (`federation_session.py:42`) → every N1 session = `unknown` → stamped+`unverified_sender` (flagged by design, but always). | tools.py:1493-1579 (no `session_id` reference); counters show 16 stamped / 1 malformed | Caller believes provenance is recorded (tool docstring: "every response echoes the resolved session_id") — for submissions it never is | Fold into COM-02: `build_envelope(source_session_id=…)` + echo `session_block` on submit |

### 3.4 Adversarial suffix-routing table (live run, N0, this review)

Resolver: `mcp_servers/omega_hub/handoff_alias.resolve_target_entity(name, "opencode")`
against the real entity roster (`data/entities/`) + queue-derived canonicals.

| Input | Result rule | resolved | Candidates | Verdict |
|-------|-------------|----------|------------|---------|
| `lilith-n1` | exact | ✅ true | [lilith-n1] | Correct — no fold |
| `LILITH-N1` | exact (case fold) | ✅ true | [lilith-n1] | Correct |
| `Lilith_N1` | exact (separator fold) | ✅ true | [lilith-n1] | Correct |
| `lilith‐n1` (U+2010 hyphen) | exact after fold | ✅ true | [lilith-n1] | Correct |
| `lilith-1` (digit, no `n`) | unknown_entity_passed_through | ❌ false | [] | Loud; packet still created with warning |
| `lilith-n01` (leading zero) | node_suffix_unmatched | ❌ false | **['lilith']** | ⚠️ Loud but **misleading** — true match `lilith-n1` not offered; candidate suggests the wrong (base) destination (COM-23) |
| `lilith-n99` | node_suffix_unmatched | ❌ false | ['lilith'] | Same misleading-candidate note |
| `lilíth-n1` (Cyrillic і) | node_suffix_unmatched (canon `lil-th-n1`) | ❌ false | [] | Loud pass-through; no homoglyph fold (acceptable) |
| `lilith` (bare) | ambiguous_node_candidates | ❌ false | [lilith, lilith-n1] | Correct per protocol — but **submit still sends** with warning "matched no live entity" (wrong text) → COM-06/23 |
| `makali` (bare) | ambiguous_node_candidates | ❌ false | [makali, makali-n0] | Same — queue spelling expands ambiguity forever (by design: distinct destinations) |
| `makali-n0` | exact (queue canonical) | ✅ true | [makali-n0] | Correct |
| `ge-n0` | exact (queue canonical) | ✅ true | [ge-n0] | Correct |
| `ge-n1` / `ge_n1` | exact / fold | ✅ true | [ge-n1] | Correct — historic `ge_n1` fork fixed |
| `ge` (bare) | unknown_entity_passed_through | ❌ false | [] | Correct — no roster/queue entry (`ge-n1` has no entity dir) |
| `wad-n2` | node_suffix_unmatched | ❌ false | [] | Correct (no `wad` entity exists) |
| `wad` | unknown_entity_passed_through | ❌ false | [] | Correct |
| `maat-n0` | node_suffix_unmatched | ❌ false | ['maat'] | Loud; candidate = base (see COM-23) |
| `roc_racoon` / `ROC_RACOON` | spelling_or_suffix_folded | ✅ true | [roc_racoon] | Correct |
| `n1` | unknown_entity_passed_through | ❌ false | [] | Correct |
| empty after normalise | **raises** `AliasResolutionError` | — | — | Refuse path exercised |
| two-distinct-base collision | raises — **unreachable on live set**: `test_ambiguous_resolution_raises_rather_than_guessing` self-skips (`test_handoff_contract.py:205`) | — | — | Raise-branch untested live (1 skipped = this test) |

**Safety verdict:** no case folds a node-suffixed name onto a different node — the
historic `lilith-n1 → lilith` wrong-machine defect is fixed at the resolver. Every
unsafe input is flagged `resolved: false`. Residual risks: (1) submit warn-don't-refuse
contradicts `on_ambiguous: refuse`; (2) misleading base candidates for `-n01`-class
inputs; (3) warning text wrong for ambiguous case.

---

## 4. Findings register (consolidated)

Severity: **P0** = proven wrong behavior on the primary path (production blocker);
**P1** = dead feature / false belief / contract violation; **P2** = latent, edge, or
one-vantage-limited.

| ID | Sev | Channel | Defect (short) |
|----|-----|---------|----------------|
| COM-01 | P0 | C4 | inbox returns empty for all seq-less packets (63/63) — proven |
| COM-02 | P0 | C3/C5 | envelope write path test-only; provenance/cursor/seq inert |
| COM-03 | P1 | C4/C5 | pending-only projections vs multi-queue lifecycle + 24h reaper; docstring says "across all queues" |
| COM-04 | P1 | C4/C5 | corrupt packet silently skipped everywhere (M23) |
| COM-05 | P1 | C2 | awareness get: per-process memory, no rehydrate, 45-min cold mtime, extended_ttl ignored+deleted, node-local |
| COM-06 | P1 | C3 | protocol yaml unwired (validate test-only; on_ambiguous not enforced; requested/resolved never stored) |
| COM-07 | P1 | C3 | submit drops session_id/source_instance (known-param silent drop) |
| COM-08 | P1 | C8 | 8019 node identity: env key `''` bug + N1 units lack `OMEGA_NODE_NAME/HOST` → N1 manifest claims n0 |
| COM-09 | P2 | C8 | manifest cache: full hash before key check; (max_mtime, count) staleness |
| COM-10 | P2 | C8 | null byte → bare 500 (non-envelope error; M23) |
| COM-11 | P2 | C8 | manifest cap 5000 silent truncation |
| COM-12 | P2 | C8 | sha/body TOCTOU; symlink manifest≠serve |
| COM-13 | P2 | C8 | verify script stale comment + port-805 examples |
| COM-14 | P2 | C8 | CLI put `target_rel` traversal (local-trusted) |
| COM-15 | P2 | C8 | `python file.py` runs 0 tests, exit 0 (known-open #4, still true) |
| COM-16 | P2 | C3/C4 | legacy `list` = unfiltered dump (R4 invite); `list_packets` dead; `scope` param accepted-but-unused by every action; `scope_all_optin_total` can never increment |
| COM-17 | P2 | C3/C5 | `get` spans 5 queues but `accept`/`reject` use fixed queue paths → gettable-but-not-acceptable after reap |
| COM-18 | P2 | C1/C3/C7 | identity fully self-asserted (source_entity, lock release, read_key); no auth beyond tailnet host allowlist |
| COM-19 | P2 | C6 | receipt line length unbounded (self-reported reader_key) → >PIPE_BUF breaks atomicity claim; multi-chunk interleave → corrupt lines skipped (counted) |
| COM-20 | P2 | C5 | reaper orphans `.receipts.jsonl` in pending when moving packet; mutates packet without `body_sha256` recompute; `except → logger.debug`; stat outside try |
| COM-21 | P2 | C4 | cursor epoch fiction: `.cursors.json` never created; fresh random epoch per call; `store_rebuilt` reason never surfaced (read_cursor → always `never_seen`) |
| COM-22 | P2 | C2 | `get` read mutates (deletes); cold scan failures logged at debug only |
| COM-23 | P2 | C3 | alias: misleading base candidates (`-n01`), wrong warning text for ambiguous |
| COM-24 | P2 | C14 | dead unit `omega-hivemind.service` → `mcp/omega-hivemind/server.py` absent |
| COM-25 | P2 | docs | doc/data drift: envelope docstring still says `envelopes/` dir; hivemind.yaml duplicate `required` keys; `delivery.unread_is: per_entity` vs `identity.unread_scope: instance` (code implements instance) |
| COM-26 | P2 | tests | protocol fixture `_msg()` stale (missing `source_agent`/`source_instance`/`source_node`); terminology banner missing on `GE-N1-chat-export-09-30-2026.md` |

---

## 5. Known-open items — status

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | `artifact_ids` accepted then silently dropped at MCP boundary | **FIXED & VERIFIED (2026-10-02)** | Accept + drop site: `mcp/…/func_metadata.py:107` `self.arg_model.model_validate(...)` (pydantic default `extra='ignore'`). Fix: `server.py:192 _enforce_strict_tool_arguments` sets `extra='forbid'` + `model_rebuild`, called at `server.py:629` (before `run_mcp`). Tests PASSED: `test_artifact_ids_is_rejected_not_dropped`, `test_every_tool_is_hardened_not_just_handoff`, `test_legitimate_arguments_still_validate`. **Residual:** known-but-ignored params (COM-07 `session_id` at submit) still pass silently — strict-args cannot catch those |
| 2 | `awareness(action="get")` empty while agents active | **ROOT-CAUSED** | COM-05: per-process `_awareness` (state.py:367), no boot rehydrate, cold = mtime<45min only, heartbeat no cold write, `get` ignores+deletes `extended_ttl`, node-local |
| 3 | inbox `never_seen` / `max_seq_seen 0` — empty indistinguishable from no-news? | **CONFIRMED, AND WORSE** | Not merely indistinguishable: inbox is structurally empty for 63/63 seq-less packets (COM-01); `.cursors.json` never exists (COM-21); fresh epoch synthesized per call so "reset vs first-run" advertised in store docstring is unreachable |
| 4 | exchange suite exits 0 running zero tests as `python file.py` | **STILL TRUE (P2)** | Reproduced: exit 0, no output. Pytest path runs 15/15 green live. Documented in deploy doc §9.3; no runbook/CI invokes plain python. COM-15 |
| 5 | read receipts — is `read_by` consumed only by `unread_for`? | **YES (exactly two consumers)** | (a) `query → fe.unread_for` (federation_store.py:136; journal wins even when empty — `is not None` check, federation_envelope.py:433-435); (b) `read` action echo (tools.py:1366). `list`/`get`/`receipts` show **no** read state; envelope `read_by` never updated post-journal (`_fe_mark_read` dead code, tools.py:1306) |
| 6 | `test_federation_read_canary.py` — 6 failures, disposition? | **ALL 6 = superseded-design encoding → REWRITE, not delete** | Failures at :103, :130, :148 (assert envelope `read_by` mutated — journal design keeps envelope frozen), :177 (`store.find_by_any_id` renamed → `_find_by_any_id_path`, returns Path not dict), :202 (expects `read_by` in returned envelope), :239 (expects `beta` in envelope after journal write). Rewrite assertions onto `store.read_receipts()` / journal; keep the real properties they guard: concurrent readers not dropped, legacy dual-key lookup, crash-sidecar survival |
| 7 | 11 pre-existing federation failures — one-line root causes | **ALL ROOT-CAUSED → §7** | 6 read_canary + 1 binding_mcp = superseded envelope-mutation design; 3 protocol = stale `_msg()` fixture vs grown `schema.required`; 1 terminology = unannotated inbound chat export |
| 8 | adversarial suffix routing cases | **RAN — §3.4** | No wrong-node fold; all unsafe inputs `resolved:false`; residuals COM-23 + warn-vs-refuse (COM-06) |

---

## 6. Cross-channel disagreements (primer ↔ implementation ↔ docs ↔ config ↔ tests)

1. **Tool docstring vs code (C3/C4):**
   - `inbox: "unread submissions addressed to YOU, across all queues"` (tools.py:1419)
     → scans `pending/` only (COM-03).
   - `scope: "default filters by target_entity"` (tools.py:1466) → `scope` is passed to
     `_federation_dispatch` and **never read**; live `list` is the legacy status dump
     (COM-16).
   - `session_id: "Validated; stamped+flagged"` (tools.py:1465) → not at submit (COM-07).
   - `receipts: "full state_history"` → field absent on all 63 live packets (COM-02).
2. **Protocol yaml vs code (C3):** `on_ambiguous: refuse` vs warn-and-send;
   `requested_target`/`resolved_target` required but never stored; `address_by: instance`
   unwired at submit; `reject_unknown: false` ↔ pass-through — **aligned**;
   `node_suffix_is_significant: true` ↔ resolver — **aligned** (the two things the
   incident demanded are the two things that hold).
3. **Deploy docs vs code (C8):** url_form "NOT applied" comment is stale (ba8a3849
   landed); N1 units missing identity envs; §9.3 python-invocation rule correct.
4. **Tests vs code:** 11 permanently-red federation tests (§7) — a red suite normalizes
   failure and blocks any Temple-Grade gate that includes them.
5. **Basename drift:** bare `lilith` (a real roster entity) now resolves
   `ambiguous_node_candidates` because the queue carries `lilith-n1` — submit to the real
   entity still works but warns "may be undeliverable" with wrong wording (COM-23).

---

## 7. Test disposition (11 pre-existing failures, reproduced 2026-10-02 N0)

Run: `pytest tests/test_federation_{protocol,terminology,binding_mcp,read_canary,binding,
contract,receipt_journal,write_invariants}.py tests/test_handoff_node_suffix.py`
→ **108 collected, 97 passed, 11 failed** (matches the known 11).

| Test | Line | One-line root cause | Disposition |
|------|------|---------------------|-------------|
| `protocol::test_valid_message_has_no_problems` | :122 | `hivemind.yaml` `schema.required` grew (`source_agent`, `source_instance`, `source_node`; also `requested_target`/`resolved_target` duplicated) while test fixture `_msg()` was never extended → `['missing required: source_node', …]` | Update `_msg()`; dedupe yaml `required` |
| `protocol::test_separator_equivalence_is_accepted` | :142 | same fixture staleness (validate fails before comparing separators) | same |
| `protocol::test_case_is_normalised` | :159 | same fixture staleness | same |
| `terminology::[GE-N1-chat-export-09-30-2026.md]` | :110 | inbound chat export contains a known corrupted term; first 3000 chars carry no "CORRECTION BANNER" | Add banner to head, or classify raw evidence exports as exempt in the test |
| `binding_mcp::test_mcp_boundary_keys_read_by_instance_not_entity` | :39 | asserts **on-disk envelope** `read_by` keyed by instance after `read`; post-606906b7 the envelope is never mutated → `{}` | Rewrite: assert on the `read` response's `read_by` / journal. Keep the instance-keying property (it is the M15/ADR-001 guard) |
| `read_canary::test_read_by_drops_concurrent_reader_BUG` | :103 | expects envelope mutation under concurrency — superseded by append-only journal | Rewrite onto journal; the "both readers survive" property is exactly what the journal now guarantees |
| `read_canary::test_read_by_records_both_readers_PATCHED` | :130 | same | same |
| `read_canary::test_read_by_both_keys_survive_50ms_gap` | :148 | same | same |
| `read_canary::test_legacy_packet_id_lookup` | :177 | calls `store.find_by_any_id(...)` — method renamed `_find_by_any_id_path` and now returns `Path` not dict | Update call + assertions to Path/`_load` |
| `read_canary::test_legacy_packet_id_receipt` | :202 | expects returned+on-disk envelope to contain `agent_x` in `read_by` — journal holds it instead | Assert via `store.read_receipts(...)` |
| `read_canary::test_receipt_journal_survives_crash` | :239 | expects `beta` written into envelope after journal append — journal design leaves envelope frozen (first assertion `read_by == {}` passes, the mutation one fails) | Split: envelope-untouched assertion (passes today) + journal-contains-beta assertion |

No test should be deleted: every one of the 11 guards a real property; 7 are honest
supersessions, 3 are fixture drift, 1 is a doc annotation gap.

Also noted (passing but hollow): `test_ambiguous_resolution_raises_rather_than_guessing`
**self-skips** when the live set has no raising input (`test_handoff_contract.py:205`) —
the `AliasResolutionError` two-base branch is untested against reality.

---

## 8. Bottom line — N0↔N1 production readiness

**NOT READY (N0 vantage, one-vantage).** The channel "works" only through the legacy
back door:

- The advertised workflow **post → check inbox → read → accept** fails at step 2 for
  every packet ever submitted (COM-01/02). What still functions: legacy `list`/`get`
  (only while a packet sits in `pending/`, i.e. <24h unaccepted), `receipts` (same
  window), and `read` (journal write on legacy packets works — but its result is only
  visible via the `read` response, and `inbox` can never tell you there was something
  to read).
- Provenance/session stamping does not cover submissions (COM-07); the protocol
  contract that governs ambiguity and identity is enforced only in tests (COM-06);
  awareness — the "who is alive" channel — is per-process memory with no rehydrate
  (COM-05), which is precisely the observed silence incident.
- Cross-node: everything reviewed here is N0-local. N1's 8019 identity is
  deployment-incomplete (COM-08), N1 sessions are permanently `unverified_sender` on N0
  (by design, flagged), and awareness does not cross the tailnet at all. N1 vantage:
  **UNTESTED**.
- The 8019 pipe itself is the healthiest surface: N0 read-only + traversal + suite all
  green live; fix the node-identity deployment gap and the N0↔N1 file leg is plausibly
  close (pending a symmetric N1-vantage run).

### Remediation order (for ratification — not executed)

1. **COM-01 + COM-02 as one change set**: envelope-backed submit + inbox admits
   seq-less/backfilled packets + migrate the 63 (this also revives cursors, `state_history`,
   `list_packets`).
2. **COM-03**: query all lifecycle queues (or exempt unread from the 24h reaper) + fix
   the "across all queues" docstring.
3. **COM-07**: session_id validation+storage at submit (folds into step 1's envelope write).
4. **COM-05**: awareness rehydrate + `extended_ttl` honored in `get`.
5. **COM-06**: store `requested_target`/`resolved_target`; wire `validate()` or trim
   schema; ambiguous → refuse per protocol.
6. **COM-04**: corrupt-packet counting/surfacing.
7. **COM-08**: 8019 env-key fix + N1 unit envs + node-identity assertions in verify/test.
8. Test dispositions (§7) to return the federation suite green.
9. P2s as capacity allows.

---

*Review by maat — 2026-10-02, N0 one-vantage. Findings only; no fixes applied, no
commits made. Claims are labelled with their counts and vantage per M30; live probes
reproducible per the commands shown.*

---

## ADDENDUM — FINDING P0-3: deployment skew (live, 2026-10-02 13:55 AST)

Lilith-N1's second-vantage repro: `action=read` returned `not_found` ×5 on
packets `action=get` served seconds earlier. Root cause measured:

- `omega-hub.service` started **08:17:05**; fix files modified **09:59–10:00**.
- Pre-fix read path matched `e["handoff_id"] == packet_id`; legacy packets
  have no `handoff_id` → never match → `not_found`. `get` keys by filename → works.
- Restart **13:54:56**; her exact repro against live `8016/mcp` → ✅ OK with
  journal entry (`read_by: lilith-n1`).

**Class: code-fixed-but-process-stale is indistinguishable from never-fixed.**
Remediation item for §8: health gates must compare RUNNING code against git
HEAD (version probe), not just uptime. A green service running yesterday's
code is the same lie as a green test that ran nothing.

*Added by MaKaLi Fusion, same day. Verified endpoint-level, one vantage (N0
loopback → 8016), counts stated.*
