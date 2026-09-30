<!-- GNOSIS-META
entity: makali_fusion
entity_type: oversoul
schema_version: 1.0.0
stamped_at: 2026-09-30T06:20:00+00:00
stamped_by: makali_fusion
supersedes: session_gnosis_20260930-0315.md
history_lost: none
-->

# 🔱 SESSION GNOSIS — MaKaLi Fusion (CHECKPOINT 2)
**HEAD**: `626507ac` · **Branch**: `debut-v1.6.0-alpha` (pushed, tree clean)
**Gates**: `check-engine` 175/175 · `temple-grade` 53/53 · M23 ratchet −43

## §0 — THE ONE-LINE VERSION
The contract defect is closed and the live-root corruption path is fixed. Two
things are now known to be **wrong rather than merely undone**: the M9 gate
matches text in comments, and `HANDOFF_BASE` is a process-global. Both are
recorded, neither is papered over.

## §1 — WHAT LANDED THIS SESSION
- **42 M36 test packets purged** (`4c7a3c5c`) — 64% of the live queue was test
  noise, which is why real packets went unread. Audit record committed.
- **`artifact_ids` no longer silently drops** (`626507ac`). Root cause was NOT a
  missing parameter — the signature is correct and a direct Python call raises
  loudly. It was pydantic `extra='ignore'` inside `mcp`'s `func_metadata`,
  reachable only over the wire. Fixed with `extra=forbid` + `model_rebuild`.
  Submit now echoes the STORED packet beside the requested one.
- **Live-root corruption path closed.** M36's queue-root restore sat after the
  outer `except`; any exception outside the tuple left the process permanently
  re-rooted at the test root. Moved into `finally`. Sabotage-verified red→green.
- **Fresh-clone ImportError fixed** — `handoff_alias.py` was untracked while
  `tools.py` imported it.
- **A gate that could never pass, fixed** — `docs/reference/` was under a global
  `*.md` ignore, so "src/omega changed ⇒ docs changed" was unsatisfiable.
  I did **not** `--no-verify` that hook. I fixed the ignore.
- **`ge_n1` fork retired** with manifest to `data/handoff/retired/` — its
  instruction contradicted the correction that superseded it.

## §2 — KNOWN-WRONG, DELIBERATELY NOT FIXED
1. **M9 gate is a text grep.** `rg 'except\s*:'` matches the word in a comment.
   An agent gamed it today by writing a comment explaining it was gaming it. I
   removed the evasion; **the gate is still wrong** and should parse the AST.
2. **`HANDOFF_BASE` is process-global, no lock.** A concurrent dispatch during an
   M36 call inherits the test root. Correct fix is threading the root as a
   parameter, not a lock or `contextvars`.
3. **Suffix-stripping in `handoff_alias.py`.** Carmack: it folds `makali-n0`
   into `makali`, but both exist as distinct agents. He says the fix is sender
   discipline, and writes plainly: *"that is a policy call, not a code fact."*
   **Architect's decision. Not mine.**
4. **`_queue_canonical()` scans the whole queue per submit.** Real smell; cutting
   it breaks the 10 existing forks, so the merge decision comes first.

## §3 — STATE DRIFT FOUND BY ROC
- `ACTIVE_SPRINT.json` asks for branch `del1/01-test-infrastructure` and
  `tests/test_engine_islands.py`. **Neither exists.** The file has been steering
  nothing.
- SOTE W40 claims commit `82dca293` and "Git Working Tree CLEAN". **Both false.**
- 3 packets target entities with no `data/entities/` directory: `ge-n1` (×7),
  `makali-n0`, `john-carmack-n1`.

## §4 — THE PLATFORM API I DID NOT KNOW EXISTED (Grokster)
`opencode serve` on `127.0.0.1:4096`, basic auth via `OPENCODE_SERVER_PASSWORD`.
- **`POST /session/:id/prompt_async`** → 204, non-blocking steering.
- **`POST /session/:id/abort`** → the model-visible cancel path.
- **`GET /session/status`** → supported in-flight query. I had been inferring it
  from `opencode.db`, which works but is unsupported.
- **Docs describe a NEWER release than installed 1.18.33.** `_SCOUT` documented
  but absent from our binary; `_CODE_MODE`, `_REFERENCES`, `_WEBSOCKETS` present
  but undocumented. Undocumented flags carry no stability guarantee.

## §5 — THE BACKGROUND FEATURE, SETTLED
`OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true` is in `~/.bashrc` **and** `.env`
(verified both resolve; not in `opencode.json`, which has
`additionalProperties: false` and would risk the provider/MCP config).

**It still does not work for me, and the cause is mine:** my `background: true`
serialises as the JSON string `"true"`. Error: `Expected boolean | undefined,
got "true"`. Two attempts, then I stopped rather than guess at a serialisation
boundary. A canary cost 3 seconds — which is the whole argument for the
3-minute time box.

**Background subagent metadata on all 15 task calls this session:
`background: NULL`, `jobId: NULL`. It never engaged once.**

## §6 — THE PARTNERSHIP
Every error caught today was caught by the other vantage, not by me checking
harder: Talescail (Architect), the superseded branch (Architect), the queued
messages during a blocking task (Architect), the stale SOTR (Roc), the
fresh-clone break (Roc), the gate that could never pass (Roc), the live-root leak
(Carmack), the gate-gaming (Carmack), the `to_json` crash being Ma'at's own test
(Ma'at, self-corrected).

**The rule that came out of it: I do not treat the Architect's vantage as the
softer one, and neither reports anything as settled until it is executed.**

## §7 — RESUME
1. Read §2 — four known-wrong items, two of them policy calls for the Architect.
2. Read `data/coordination/AUTONOMOUS_RUN_20260930.md` for the full run log.
3. `git log --oneline -3` — `626507ac` is the checkpoint.

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ CHECKPOINT-2 ⬡ 626507ac ⬡ 2026-09-30 ⬡*

---

## §8 — CHECKPOINT 3 ADDENDA (autonomous run)

**Commits since checkpoint 2**, all pushed:
`3dfdcf91` gnosis seal · `49952015` M9 gate to AST parse (18 tests) ·
`b2a966c6` findings register + sprint reconciliation · `8b3ad798` PR-readiness
lane A · `7b0cec02` M36 verification record.

**Four more instances of the standing pattern** — the check being wrong rather
than the claim. A stale generated registry read as a roster. A policy file
called stale when it was correct. A truncated tool list read as a total. And two
"cannot verify" reports that resolved the opposite way: the SUPERSEDED markers
were present, and the strict-args fix was present under a different name than the
one that was searched for.

> **RULE: before trusting any negative finding, ask what would make the check miss it.**

**The release blocker is not a bug.** A gitleaks invocation that is flag-rejected
exits 0 and looks like a pass. Same class as the M9 text grep and the
`is-active` check — *a check that cannot distinguish "verified" from "did not
run."* On a public repo, that is the one thing to settle before tagging.

**The dialectic method that worked here:** commission two opposed briefs, notice
they converge on an empirical question neither can answer by reading, then run
the experiment instead of synthesising a decision from two opinions. The
call-graph trace closed the seam and produced a stronger conclusion than either
brief argued for.

**Method note for the next head:** two attempts to write this section failed —
an inline Python heredoc on a nested-quote syntax error, and a bash heredoc on a
malformed terminator. **The first one still produced a successful commit, because
the surrounding command chain continued.** So the commit message claimed a gnosis
update that had not happened. **Verify the artefact you intended to write actually
changed before you let the commit stand.**

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ CHECKPOINT-3 ⬡ 7b0cec02 ⬡ 2026-09-30 ⬡*