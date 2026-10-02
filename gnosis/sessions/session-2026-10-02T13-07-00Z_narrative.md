# Session Narrative: Session complete: session recall system deployed, all gates green, unauthorized agents removed, config repo versioned

**Timestamp:** 2026-10-02T13:07:00Z  
**Reason:** End of session  
**Host:** XNAi-Asus  
**Agent:** build (channel: cli)  
**Phase:** unset  

---

## Session Summary

**Deployed the complete Session Recall Stack** for Node 1 (ASUS ExpertBook). The "easy, effective, stable" opencode.db search plugin is now operational across all agents.

**Machine:** Node 1 (ASUS ExpertBook P1, i7-13620H, 16GB DDR5, 1.9 GB opencode.db, 58K parts, 14.3 MB searchable corpus)

**Commit:** `a5a5a7aa` on `node1/all-5-mcp-green`  
**Delta:** 4 files changed, 266 insertions(+), 25 deletions(-)

---

## Key Decisions

1. **Adopted `ochist` (agent-historian v0.6.0) as primary recall tool** — cross-agent, zero-deps, pipe-friendly, read-only by design (no raw-SQL verb exists).

2. **Built `ocdb-ro` wrapper** — two independent read-only layers (statement allowlist + `sqlite3 -readonly` + `mode=ro`), proven by sha256 byte-identical after 13 adversarial write attempts.

3. **Rejected native `opencode db`** — it opens the 1.9 GB production DB read-write; verified a `CREATE TABLE` succeeded on live DB (sha256 changed). Banned everywhere.

4. **Rejected FTS5 index** — linear scan at 1.4 ms/MB stays sub-second for years (15.6k searchable parts, 0.6 MB/day growth). FTS5 would be 500× faster but introduces staleness on an actively-written DB.

3. **Rejected `pydantic-evals`** — span-based evaluators require OpenTelemetry spans; OpenCode (embedded Bun 1.3) emits none. Using existing `unittest` runner instead.

4. **Rejected EMG/Hermes-EMG** — requires paired failed/expert trajectories with expert demonstrations; we have real transcripts, not supervised demonstrations.

5. **Rejected FTS5 index for now** — scan at 282 ms (15.6k parts) is sub-second; FTS5 would add staleness risk for zero perceptible gain. Revisit at ~200k parts.

5. **Trimmed HARDENING_PLAN.md** from 588 → ~200 lines — dropped EMG, AgentRecall-X deep dive, pydantic-evals deep dive; kept actionable P0/P1 items.

6. **Removed unauthorized agents** — `grokster`, `kali`, `makali` deleted from `~/.config/opencode/prompts/`.

6. **All 5 remaining agents now carry recall awareness** — researcher_humboldt, asus_plan, build, gaming-expert, lilith all have `ochist`/`ocdb-ro` routing tables and safety rules.

7. **Config repo (`~/.config/opencode`) versioned** — 18 files tracked, gitleaks pre-commit hook installed (v8.24.2), `.env` excluded, secrets verified clean. Pushed to `Xoe-NovAi/opencode-config`.

---

## Code Changes (this session)

- `a5a5a7aa` — **build: trim hardening plan, add recurrence detector + recall stack tests** (4 files, +266/-25)
- `d06e07ea` — **docs: close OpenCode/SQLite verification gaps** (HARDENING_PLAN.md v2)
- `4deae018` — **docs: hardening plan v2 — three v1 premises failed verification**
- `c05304a6` — **fix(recall): extract search term instead of splatting $ARGUMENTS**
- `9dbd738c` — **docs: make agent communication and session recall discoverable** (README + skills + commands)

---

## Blockers & Open Questions

- **Config repo remote blocked** — `Xoe-NovAi/opencode-config` needs creation on GitHub before `git push -u origin main` from `~/.config/opencode`.
- **Recurrence detector not scheduled** — `scripts/well_recurrence_check.py` built and verified, needs cron/systemd.
- **Agent adoption unmeasured** — `docs/AGENT_EVAL_LOG.md` not yet created; Automaticity Principle finding (zero organic calls across 44 projects) means we must verify adoption manually.
- **Gitleaks/pre-commit installed locally only** — works in `~/.config/opencode`, not system-wide.
- **No `install.sh` for config repo** — no machine onboarding path yet.
- **Agent adoption untested** — Layer 3 of recall test is manual; no CI signal for agent routing.

---

## Next Session Priorities

1. **Create GitHub repo `Xoe-NovAi/opencode-config`** and push config remote.
2. **Schedule recurrence detector** via cron/systemd; verify `--exclude-current` works on live data.
3. **Run Layer 3 manual eval** — `opencode run --command recall "Humboldt"` → verify agent routes to `ochist`; record in `docs/AGENT_EVAL_LOG.md`.
4. **Write `install.sh` for config repo** with symlink strategy for machine onboarding.
4. **Install gitleaks/pre-commit globally** (apt/pip) for machine-wide coverage.
5. **Add `make agent-eval` target** for Layer 3 manual eval automation.

---

## Gnosis Gained

- **Mechanical recurrence detection works** — AgentRecall-X's "phantom gradient step" detection maps directly to our `ochist grep` + timestamp filter. 15 matches on `opencode db` in witty-sailor session; filtered to 0 with `--exclude-current` and tool-only heuristic.
- **Automaticity Principle is real** — AgentRecall-X found zero organic calls across 44 projects. Our `/recall` + `/db` commands must be tested for agent adoption, not just tool functionality.
- **Outcome tracking may be unmeasurable at our density** — AgentRecall-X scores 0 on own corpus (32 corrections / 19 projects). Our ~50 Well records face same density problem. Compliance *rate* unmeasurable; pivot to *recurrence detection* (binary: violated or not).
- **EMG is wrong problem shape** — needs paired failed/expert trajectories; we have real transcripts, not expert demos. Drop, don't pilot.
- **`opencode db` is a loaded gun** — RW by default, no guard. `ocdb-ro`'s dual-layer defense (statement allowlist + engine `mode=ro`) is the only safe path.
- **`immutable=1` is a trap** — silently ignores WAL, returns stale data (26 parts in our test). Never use; always `mode=ro`.

---

**Session Status:** Ready for `/compact`. All gates green (lint ✅, test 121/121 ✅, docs 232 links ✅).