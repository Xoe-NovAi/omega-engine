# Session Narrative: session-2026-10-02T15-07-53Z

**Timestamp:** 2026-10-02T15:07:53Z
**Reason:** Well P0 hardening: reader resilience, verify gate, 1024-dim correction
**Host:** XNAi-Asus
**Agent:** lilith (channel: opencode)
**Phase:** well-hardening

---

## Session Summary

Reviewed `ge-n0`'s report on The Well (`~/GameResearch/REPORT-THE-WELL-for-LILITH-N1.md`),
then hardened it. The report's central premise — "consumption works, contribution is
undiscoverable" — was **already false when written**. The Well had injected nothing into
any session since `2026-09-30T22:11`, because the last 8 records stored `tags` as a JSON
array and `readWellForInjection` called `.split()` unguarded. The throw was swallowed by
an outer `catch` whose only action was `return []`.

Three of the report's six suggestions (`make well-add`, `make well-list DOMAIN=`,
`make well-supersede`) already existed. The one genuinely missing piece was discoverability.

Gap closure was delegated to `researcher_humboldt-n1` (`well-gaps-20261001-01`), who
corrected three framing errors and surfaced a live upstream bug. Local verification then
confirmed every claim.

Outcome: reader hardened, `make well-verify` gate added, 7 node-executing regression tests
written and **proven to fail against the vulnerable code**, and the `1024` embedding-dim
correction recorded in the corpus by supersession rather than edit.

## Key Decisions

Operator reflections (verbatim):

1. **Decision** — "Right call — reader adapts, writer gated."
   Corruption was fixed in the READER, not the DATA. The reader coerces whatever shape a
   record arrives in; the gate fails only writes the reader cannot consume. This is
   Confluent's `BACKWARD_TRANSITIVE` posture: an append-only log that cannot be rewritten
   needs a reader tolerating every record ever written.
2. **Pattern** — "Test the real artifact, never a fixture."
   114 tests stayed green while the feature was dead, because every test redirected storage
   to a `tempfile.TemporaryDirectory()` and no test executed the JS.
3. **Authority** — "Gates must emit context, not just findings."
   `well-verify` flagged the 16 array-tagged records; nothing carried the operator's
   reasoning. `ge-n1` rewrote all 16 anyway, against an explicit ruling it could not see.
4. **Correction** — "A stale corpus can teach a wrong lesson confidently."
   The `truncate_dim=768` record was well-formed, plausible, and duplicated for weeks. It
   was wrong in both the parameter name and the value.
5. **Carry Forward** — "Fix ranking before adding more records."
5.** The Well is appended to faster than it can be read.
6. **The Ritual** — "Repair corruption, never mass-dismiss."

## Code Changes

Staged in `omega-engine-alpha` (6 files, +472/-58):

- `scripts/well_storage.py` — `validate()` type guards placed **before** the secret-pattern
  regex (a list-typed `tags` raised `TypeError` instead of reporting); `tags_display()`
  normalizes tags in both render paths (16 raw-array artifacts in `WISDOM.md` → 0);
  new `verify` command with asymmetric severity — ERROR for unreadable, WARN for
  reader-tolerated drift.
- `tests/test_well_injection.py` — 7 tests driving the **real plugin in node** via
  `WELL_DIR_OVERRIDE`, against both fixture and real corpora. Verified to **fail on the
  vulnerable reader and pass on the hardened one**.
- `Makefile` — `well-verify` target.
- `docs/ROADMAP.md` — new **P5.1b**, status `blocked`: 1024-dim cutover ruling, the
  measurement that justifies dropping truncation, four remaining migration steps, and the
  Node 0 survey dependency.
- `gnosis/well/well.jsonl` — record `c068a4ae` (1024/`dimensions` correction) appended;
  `42c3c90d` and `d4cf07de` superseded to it. `ge-n0`'s records not edited.
- `gnosis/well/WISDOM.md` — regenerated.

Changed outside git (**no version control at all**):

- `~/.config/opencode/plugins/gnosis-leash.js` — `normalizeTags()`; per-record isolation
  (the `.map()` was outside the `try`); returns `{records, scanned, skipped, errors}`;
  `wellRecordsOrReport()` treats `scanned>0 && records===0` as an **incident** and logs it;
  `WELL_INJECT_DOMAINS` as one shared constant; appends to `system[0]` **in place** so
  `output.system` stays length 1; dead `else` branches deleted; `WELL_DIR_OVERRIDE` added.
- `~/.config/opencode/agent/lilith.md` and `prompts/researcher_humboldt.md` — corrected from
  `truncate_dim=768` to native 1024; the Humboldt prompt's citation retargeted to `c068a4ae`.
- `~/GameResearch/agent-src/src/40-governance.md` — The Well block (S1) + ownership ruling
  (S5). **Committed under `ge-n1`'s name one minute after it was written** (459a507).

## Blockers & Open Questions

- **`identity.json` was corrupted** and blocking the leash: a status string had been written
  into `current_session` and `pending_pack`, creating 7 filename-unsafe pack files.
  Repaired to `session-2026-10-02T13-07-00Z`; the malformed ID preserved inside the manifest
  as `malformed_session_id`. That pack held **real unreflected reflection** — six insights,
  including one that independently converged with tonight's finding ("outcome tracking may be
  unmeasurable at our density... pivot to recurrence detection"). Ingested, not dismissed.
- **18 older CAPTURED-but-unreflected packs** (2026-09-09 onward) remain, per operator
  instruction: repair corruption, never mass-dismiss.
- **Embedding dim cutover UNBLOCKED, but Node 1's real state is worse than assumed.**
  Operator confirmed Node 0 is already on 1024, which removes the P5.3
  cross-node incomparability blocker. Then I checked the store instead of the
  spec: `SELECT dim, COUNT(*) FROM documents GROUP BY dim` on
  `~/WanderGround/mempalace/sqlite_exact.sqlite3` returns **`dim=384`, 1115 rows**
  — the legacy `embeddinggemma`-MRL space that
  `EMBEDDING_STRATEGY_NODE1_20260925.md` explicitly *rejected* for failing the
  768 bar. The 768 engine space existed **only** as an inactive systemd default.
  So three dims were in play on Node 1 (384 live, 768 vestigial, 1024
  canonical) and neither live one was canonical. This is not a 768→1024 bump; it
  is a **384→1024 rebuild of 1115 documents**, which was never on the migration
  list. Code and docs are now aligned to native 1024; the rebuild is filed and
  NOT run (too large to do hastily pre-compaction).
- **`omega-hub_omega_federation_status` reports `self: n0` while running on Node 1.**
  It also flagged `zero_inference_egress: false`, which would be a real sovereignty
  invariant violation — but if `self` is misattributed, the flag may not describe
  this node at all. Recorded as **observed with uncertain attribution**, not as a
  confirmed violation. Next session: determine whether the hub is querying a
  remote context, and re-read the invariant once `self` is trustworthy.
- **18 older CAPTURED-but-unreflected packs** (2026-09-09 onward) remain, per operator
  instruction: repair corruption, never mass-dismiss.
- **`.gitignore:23` ignores `gnosis/well/`.** Both corpus files are tracked so they stage, but
  any *new* file there is silently untracked.
- **The plugin had no version control** — now fixed, see Code Changes.
- The ritual's "Working-tree changes" section only records **unstaged** changes — staged work
  is invisible to the capture step.
- Not done: ranker dedup + permanence floor, `consciousness` domain injection, the 3 divergent
  `well.jsonl` copies.

## Next Session Priorities

1. **Cross-node cosine is still UNTESTED** — the highest open risk. Node 1 is now
   *verified* at native 1024 and Node 0 is operator-confirmed at 1024, but **no
   end-to-end federated retrieval has run.** Do not assume parity until Node 0
   replies to `ho_223918db14b5` and an actual cross-node query is measured.
2. **P5.5 — palace corpus is semantically shallow.** Topical-vs-control query
   separation is +0.0083. The vectors are correct; the *content* is drawer fragments
   and log tails, not retrievable prose. Separate problem from the vector space.
3. **The `self: n0` reading is BY-CONFIG, not an anomaly.** The omega-hub MCP
   endpoint is configured as `remote` in `~/.config/opencode/opencode.json:46-51`
   pointing to `https://n0.tail51f14a.ts.net:8016/mcp`. Every `omega-hub_*`
   call from Node 1 executes on Node 0 (user `arcana-novai`), so `self: n0`
   is correct behavior, handoff writes to `/home/arcana-novai/...` are expected,
   and `zero_inference_egress: false` measures **Node 0's** hub surface — not a
   Node 1 sovereignty violation. Reported to Makali-N0 in `ho_48edf2c93c91`
   along with the intermittent `[Errno 28]` on submit.
4. **P1.6 — old-rule reachability.** The permanence floor guarantees the *class* is
   represented, not that any specific old rule resurfaces. Needs rotation or a
   relevance term.
5. **Refresh or retire the frozen `omega-sweeteners` snapshot** (19 records vs 64
   live) — a Node 0 adoption decision, P5.3.
6. **18 stale packs** — one at a time, operator ruling.
7. `consciousness` domain injection (write-only for 2 records) and the 3 divergent
   `well.jsonl` copies.
8. **Prune `/tmp` junk** — a 2.0 GB `opencode_c2_probe.db` has been sitting in
   tmpfs since an earlier session.

## Gnosis Gained

- **A knowledge base that cannot report its own health will kill its own read path, and a
  green suite will certify the corpse.** 114 tests passed while the feature was dead because
  they tested a fixture and never executed the JS.
- **A read path with no writer cannot have a bad write — until someone writes.** The report
  author broke the feature with their own contribution while documenting its health.
- **The report's own premise went stale between writing and reading.** ge-n0 said 8 records;
  16 had landed by the time I looked. Always re-census before acting on a report's numbers.
- **Silent-empty is the worst failure mode.** Returning zero when data existed is
  indistinguishable from "no rules exist". Design for the distinction explicitly.
- **Measured, not asserted: MRL truncation costs essentially nothing** (−1.5% wall-clock,
  noise; 25% storage). That cheapness is the argument *against* it — you take a real semantic
  cost (`cos(native,trunc)=0.891`, 1-of-6 retrieval change) for storage on an index that does
  not exist.
- **A stale corpus teaches wrong lessons confidently.** `truncate_dim=768` was well-formed,
  duplicated, and wrong in both name and value. Only the operator held the real decision.
- **Shared trees corrupt attribution.** My `40-governance.md` edit was committed under
  `ge-n1`'s name one minute after I wrote it. The commit message described the work
  accurately; the author was wrong.
- **A gate that surfaces a finding without the reasoning behind it invites unilateral
  resolution.** `well-verify` flagged 16 records; `ge-n1` fixed them against an explicit
  operator ruling it could not see. The gate now prints the standing ruling inline.
- **A plan's status field is a claim about data, not evidence of it.** ROADMAP P5.1 read
  "`Qwen3-0.6B@1024`, in-progress"; the spec declared `FLOAT[768]`; the live store held
  **384**. Three dims in play on one node, neither live one canonical. Query the store —
  `SELECT dim, COUNT(*) … GROUP BY dim` — before planning on top of a migration's status.
  (Well record `007428a2`.)
- **Verify the tool before trusting its invariants.** `omega-hub_omega_federation_status`
  reported `self: n0` while running on Node 1, and flagged `zero_inference_egress: false`.
  A sovereignty invariant reading is only worth as much as the node identity behind it.
- **A corpus can be right about the past and wrong about the present.** Two duplicate
  `truncate_dim=768` records sat in The Well, injected into every session, after the
  decision had already moved to 1024. Deduplicating by rule identity (now shipped in the
  ranker) would not have caught it — only the operator's ruling did.
