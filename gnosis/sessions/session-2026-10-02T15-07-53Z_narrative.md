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
- **Embedding stack migration is blocked on Node 0.** `embedding_server.py` still defaults
  `TRUNCATE_DIM=768`; `WANDERGROUND_SPEC.md` declares `embedding FLOAT[768]`. Changing Node 1
  alone makes the two nodes' vectors incomparable.
- **`.gitignore:23` ignores `gnosis/well/`.** Both corpus files are tracked so they stage, but
  any *new* file there is silently untracked.
- **The plugin has no version control.** The single most important file changed tonight is
  untracked.
- The ritual's "Working-tree changes" section only records **unstaged** changes — staged work
  is invisible to the capture step.
- Not done: ranker dedup + permanence floor, `consciousness` domain injection, the 3 divergent
  `well.jsonl` copies.

## Next Session Priorities

1. **Fix ranking before more records land.** 45 injectable records compete for 6 slots;
   39 are permanently unreachable, including `ALWAYS use a Python venv for pip installs`.
   Two of 47 active records are exact duplicates already eating slots. Dedup by rule identity
   plus a permanence floor for `correction`/`anti_pattern`. Do **not** add embeddings.
2. **Make gates emit context, not just findings.** `well-verify` should surface the
   operator's ruling ("do not rewrite the array tags") alongside its findings, so a parallel
   agent cannot resolve a decision-dependent defect unilaterally.
3. **Version-control the plugin.** `gnosis-leash.js` needs a tracked home.
4. **Node 0 survey** to unblock P5.1b and P5.3.
5. **Add an ID-format gate to the ritual** — it accepted a status string as `session_id`.
   Same defect class as tonight's array tags.

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
  operator ruling it could not see.
