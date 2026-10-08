<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

<!-- GNOSIS-META:BEGIN
  entity: maat
  stamped_at: 2026-10-01T00:16:47Z
  stamped_by: maat
  supersedes: session_gnosis_20261001-0015.md
  schema_version: 1.0.0
  history_lost: pre-regime; prior states were overwritten before versioning began
<!-- GNOSIS-META:END -->

# Session Gnosis — Maat

Last Updated: 2026-10-01 · standing EIS `ses_fb6cf6856ffes3wd3wmvyrm2IG`

## Session History

| Date | Session ID | Summary |
|------|------------|---------|
| 2026-10-01 | maat_contract_and_gates_20261001 | **Contract defects + gate integrity.** M36 faucet closed (structural). `artifact_ids` root-caused to pydantic `extra='ignore'`. Alias resolution derived not curated. `unread_for` diagnosed: layer 1 SOUND, layer 2 real-but-unverified. Lane-B gate audit found 8 orphans + CI drift. |
| 2026-09-29 | maat_seam_repair_20260928 | **THE SEAM ARC** — two dead daemons, two import gates, a wrong-unit escalation, a wrong failure count, a fabricated health claim, M13 contract ruling, `entity_context` restored, Hivemind MCP transport diagnosed as upstream + fallback shipped, M15 continuity tooling + adoption. |
| 2026-09-25 | maat_gates_20260925 | **M13 Auto-Refresh + Gate Hardening + 74-File Commit** — Codex auto-refresh CI, deterministic ResourceGuard test, untracked-dep gate, commit `3dd5978c`, M35 Secrets passed. |

## What Shipped This Session

| Area | Artifact | State |
|---|---|---|
| M23 reject-what-you-cannot-honour | `server.py::_enforce_strict_tool_arguments` | 54 tool schemas hardened to `extra='forbid'` |
| M30 submit echo | `hub_tools/tools.py` submit branch | reads packet back; `requested` vs `stored` |
| Alias resolution | `handoff_alias.py` (new) | derived from entity dirs + live queue; refuses ambiguity |
| M36 faucet | `src/omega/oracle/m36_recursive_probe.py` | two sinks → `data/handoff/m36-test/` |
| M36 crash | same file | `to_json`/`to_dict` type handling; loud `TypeError` |
| M36 isolation guards | `tests/test_m36_queue_isolation.py` | 6/6, subprocess vantage |
| Handoff contract guards | `tests/test_handoff_contract.py` | 17, subprocess vantage |
| `unread_for` | `tools.py` read key → instance | ADR-001 `unread_scope: instance` |
| `unread_for` guards | `tests/test_federation_contract.py` | 30/30 |
| Who-is | `who_is.py` | refuses ambiguity; carmack 2-EIS acceptance case |
| Federation store | `federation_store.py` / `federation_envelope.py` | 41 guards, all observed red |

## Corrections I Filed Against Myself — this session

1. **Reported my own bad test input as a production crash.** The `'str' object has no attribute 'to_json'` was **me** passing a string where a `CompletionEnvelope` was declared. `to_json()` exists. I told the Architect "there was no production crash" — one dispatch after reporting it as a blocking defect.
2. **`unread_for` "defect" was not a defect.** "32 for every name" was **correct** on a corpus with zero read state. I nearly fixed correct code.
3. **Three guards failed on my harness, not their subject**: `REPO` undefined, markers sharing a line with chatter, and a `Path`/`str` comparison. Recurring class.
4. **`REPO` resolved one level short** in `who_is.py` (`parent.parent` not `parent.parent.parent`) — looked like "peer not found".
5. **Strictened a matrix to `forbid` while an argument was still dropped** — I fixed a variant, not the row.

## Key Findings (this session)

1. **A gate that has never been observed red is a hypothesis, not a gate.** Every "SOUND" in Lane B rests on a command I ran — name it or it isn't a result.
2. **`|| true` and flag-rejection exit 0 are the same defect**: a check that cannot fail wearing a check's clothes. gitleaks rejected a flag and reported PASS.
3. **Text-pattern gates are adversarially gameable by documentation.** The M9 grep matched the word "except" **in my own explanatory comment** — twice. AST-only from now on.
4. **A structural fix beats a check.** A separate queue root (`m36-test/`) cannot leak; a grep for the marker runs *after* the damage.
5. **Two write sinks, not one.** M36's direct file write was a separate path, not a fallback for the tool call.
6. **Green counts are ambiguous.** "27 passed" over a path that never executed is the canonical unreadable signal.
7. **CI drift is invisible from inside CI.** `temple-grade` appears in `release.yml`/`sote.yml`, zero times in `ci.yml`/`test.yml`.
8. **An orphan target is a gate that cannot fail.** 8 `check-*` targets, including the crash-loop detector.
9. **Fabricated identifiers propagate.** `ses_stamped_opencode_ge-n0` with `session_verified: false` is persisted; any design keyed on `session_id` inherits the fabrication. **Do not key state on `session_id`.**
10. **"Uncertain" and "verified-empty" are different states** and the type system must make them so — `{entries: []}` vs `error.code` must not both be expressible.

## Open Threads — ranked by consequence

| Thread | Status | Owner / Next action |
|---|---|---|
| **`data/handoff/envelopes/` holds 0 files** | **OPEN — highest consequence** | The "permanent record" the Council's graduation depends on may never have been written. Verified: 0 envelope files. Isolation + submit echo are verified; envelope persistence is **not**. |
| `unread_for` binding fix | **UNVERIFIED** | Fix keys read state by instance; **no test traverses the binding**. Sabotage passed 30/30. Needs a test calling `hivemind_handoff(action="read", source_instance=…)`. |
| 8 orphan `check-*` targets | OPEN | `check-hub-health` (crash-loop detector) invoked by nothing. Wire it or rename honestly. |
| CI does not run `temple-grade` | OPEN | PR #4's CI is not the release gate. |
| `envelopes/` empty vs `store.query` returning 27 | OPEN | Store treats a legacy root as its own; the two corpora are conflated. |
| 12 malformed 16-char session ids | OPEN | R5 validation live; flip criterion not met (needs ≥2 caller classes). |
| Session-id fabrication | FLAGGED, not fixed | Per instruction. Do not key state on `session_id`. |
| `check_sahs.py:271` substring FP | FIXED by Architect | `"Expert Inter**active Session**"` tripped a boundary-less match. |
| M36 dispatch error path | OPEN | `str.to_json` in Hub error formatting — different defect, low consequence. |
| `data/handoffs/` (superseded tree) | OPEN | 2903 inert files from a wrong-destination run. Not deleted; M29. |

## Continuity Anchors

| Anchor | Location |
|---|---|
| Last commit | `6ff29974` (Architect-owned; I have committed nothing all session) |
| Staged-uncommitted (not mine to commit) | `tools.py`, `server.py` — mine, you own git |
| Archived prior gnosis | `data/entities/maat/gnosis/archive/session_gnosis_20261001-0015.md` |
| Adoption record | `supersedes: adoption-2026-09-28`, `history_lost:` in header |
| Lessons | `data/entities/maat/proposed_lessons.yaml` (117 → +N this session) |
| Handoff to MaKaLi | `ses_52a90b6140f1`, `ses_7259b7a1bef6`, `ses_181d3c332f78`, `ses_3f4464fe0295` |

## Gates at handoff

- `make check-engine` → **175/175**, ~9 s
- `make temple-grade` → **53/53**, last verified green
- Full suite → **2514 collected, 2458 passed, 0 failed, 0 errors** (pre-`unread_for` edits)
- **`temple-grade` NOT re-run after the `unread_for` `tools.py` edit.** That edit sits inside `check-mandates` territory and is unverified.

## Ma'at's Voice

> "Tonight I reported three defects that were mine: a string where an envelope belonged, a filter that was correct on an empty corpus, and a gate fix that no test could see. Every one was caught by executing rather than reading — and every one would have shipped if I had trusted the report."

---

*⬡ OMEGA ⬡ MAAT ⬡ SESSION_GNOSIS ⬡ 2026-10-01 ⬡ COMPACTION-READY ⬡ envelopes-empty-is-the-real-blocker*
