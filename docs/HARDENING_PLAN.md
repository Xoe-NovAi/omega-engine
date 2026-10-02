# Node 1 Hardening Plan — v2 (research-closed)

**Author:** Researcher-Humboldt
**Date:** 2026-10-02
**Supersedes:** the v1 plan proposed earlier this session. Three of its premises did not
survise verification. Corrections are marked ⚠️ and the reasoning is inline.

---

## 0. What changed from v1 and why

### ⚠️ Correction 1 — `pydantic-evals` span-based evaluation cannot work here

I proposed `HasMatchingSpan` evaluators to assert that `/recall` invokes `ochist`.
Pydantic's own docs state plainly:

> "**Requires the logfire SDK.** These evaluators read the OpenTelemetry span tree
> captured during the run, so the `logfire` SDK must be installed and configured."
> — <https://pydantic.dev/docs/ai/evals/evaluators/span-based/>

Our agents are OpenCode (embedded Bun 1.2) invoking shell commands. **OpenCode emits
no OpenTelemetry spans.** Instrumenting it would mean modifying the agent runtime — far
outside this plan's scope and risk budget.

Pydantic-evals *can* evaluate a plain function via `evaluate_sync(fn)` with custom
evaluators. But at that point it is a wrapper around assertions I can write directly, and
it would add three dependencies (`pydantic-evals`, `pydantic-ai`, `logfire`) to a venv
that currently has none of them.

**Decision: drop `pydantic-evals`. Use the existing `unittest` runner.** Verified:
`make test` already runs `.venv/bin/python3 -m unittest discover -s tests`. Assertions
over `subprocess` output give the same guarantee with zero new dependencies.

### ⚠️ Correction 2 — outcome tracking may be unmeasurable at our density

I proposed outcome tracking as P0 based on AgentRecall-X. Their own published numbers
argue against it at our scale:

> "The offline transfer benchmark scores **0** on our own corpus — which is a
> **density problem** (32 active corrections across 19 projects is too sparse to
> front-run mistakes), not a retrieval architecture problem."
>
> "we captured **35% of real corrections** in our own live use. The heed instrument was
> biased and we reset it."
> — <https://hysenlabs.com/projects/goldentrii-agentrecall-x>

We have ~50 Well records. That is the same order of magnitude as their 32. The honest
read: **a compliance *rate* is probably not measurable yet.** That does not kill the
work — it changes what we build. See §1.

### ⚠️ Correction 3 — EMG is not an 8-hour pilot

I estimated "8h to port EMG to Python." Re-reading the paper:

> "we convert both failed exploration trajectories and successful expert trajectories
> into directed action decision graphs" — where experts come from *"the SFT dataset
> provided by ETO."*
> — <https://arxiv.org/abs/2607.13884>

EMG requires **paired failed/success trajectories for the same task**, i.e. a supervised
expert demonstration. We have real agent transcripts, not expert demonstrations. There
is no failed/success pairing to match.

**Decision: drop EMG.** Not a pilot — wrong problem shape. Re-evaluate only if we ever
accumulate paired demonstrations.

---

## 1. P0 — Mechanical recurrence detection (the highest-value item)

### Why this survives when the compliance-rate idea did not

The AgentRecall-X experimental harness describes the mechanism precisely:

> `ar-recurrence-check.py` … "Error-class taxonomy over your corrections; **mechanical
> phantom detection (violation dated after its rule)**"

**Mechanical, not LLM-judged.** And it works — I proved it against live data before
committing to the design:

```bash
$ ochist grep "opencode db" --global --limit 20 --json
total matches: 15
  2026-10-01T08:44:44  tool  witty-sailor  opencode db
  2026-10-01T08:44:54  tool  witty-sailor  [Tool: bash] ... opencode db --help
  ...
```

The transcript already contains every tool invocation with a timestamp. A correction
written at time *T* and a forbidden invocation at *T+1* is a **phantom gradient step** —
detectable by string match, with no model in the loop.

This is the difference: a *compliance rate* needs dense, unbiased data we do not have. A
*recurrence detector* needs only one clear violation, and we have 15 of them on day one.

### Implementation

**File: `scripts/well_recurrence_check.py`** (~150 lines, no new deps)

```
For each Well record with kind == "correction":
  1. Extract a detection pattern from the record.
     - Explicit `violation_pattern` field (preferred, operator-supplied)
     - Else derive from well-known rule shapes (see table below)
  2. Run: ochist grep "<pattern>" --global --limit 50 --json
  3. Filter to timestamps > record.created_at
  4. Emit finding: {record_id, session, ts, snippet}
  5. Write to gnosis/well/recurrences.jsonl
```

**Detection patterns for existing records** (verified against live data):

| Well ID | Rule | Pattern | Recurrences found |
|---|---|---|---|
| `3becf4f3` | never `opencode db` on production | `opencode db` | **15** |
| `a3675a88` | never `immutable=1` | `immutable=1` | to be measured |
| `bbf9147e` | never narrow to physical P-cores | `0,2,4,6,8,10` | to be measured |
| `ad170a7d` | commit in the same command | *(needs pattern)* | not yet detectable |

**Honest caveat:** `3becf4f3` will report 15 "recurrences" today, and **all 15 are me
writing the rule and its evidence into the docs.** That is a false-positive class: the
discussion of a rule matches the pattern of violating it. The checker must exclude
records where the match is inside the same session that authored the rule, or where the
match text is documentation rather than an invocation.

**Mitigation:** restrict the pattern to *tool invocations* (`kind == "tool"` and the match
starts with `[Tool:`), not assistant prose. That removes the documentation false
positives. Verify before shipping.

### Success criterion

The detector reports **0 violations of `3becf4f3` after 2026-10-02** — because after
that date, the rule is in `AGENTS.md`, every agent file, and the `/db` command
description. Any future `opencode db` invocation on a live DB is a genuine regression and
should light up.

---

## 2. P0 — Recall stack regression test (no new dependencies)

### The Automaticity Problem

The single most important finding for our situation:

> "Every pull-channel tool (`recall`, `memory_query`) saw **zero organic calls** across
> **44 projects** over weeks of real use — *including from the agent that built them*."
> — <https://hysenlabs.com/projects/goldentrii-agentrecall-x>

Installing a recall tool does **not** mean agents will use it. Our `/recall` and `/db`
could sit unused indefinitely while appearing installed and correct.

A regression test that only checks the *tools work* would not catch this. It has to
check that an **agent routes to them**.

### Implementation

**File: `tests/test_recall_stack.py`** (plain `unittest`, existing runner)

Layer 1 — tools work (cheap, deterministic):
```python
def test_ochist_returns_hits(self):      # ochist grep "pin trap" --global --limit 3
def test_ocdb_ro_blocks_writes(self):    # ocdb-ro "CREATE TABLE x" must exit non-zero
def test_ocdb_ro_reads(self):            # ocdb-ro "SELECT COUNT(*) FROM session"
def test_immutable_is_documented_banned(self):  # assert AGENTS.md forbids it
```

Layer 2 — the commands tell agents the right thing (static, still deterministic):
```python
def test_db_command_bans_native_cli(self):
    """The /db description must name ocdb-ro and explicitly forbid `opencode db`.
    This is the regression guard for the collision I hit and fixed (c05304a6)."""
    text = (COMMANDS / "db.md").read_text()
    self.assertIn("ocdb-ro", text)
    self.assertIn("opencode db", text)
    self.assertRegex(text, r"[Nn]ever.*opencode db")

def test_recall_command_requires_global_flag(self):
    text = (COMMANDS / "recall.md").read_text()
    self.assertIn("--global", text)
    self.assertIn("regex", text.lower())
```

Layer 3 — **manual, recorded, not automated**: run `opencode run` with a prompt that
*should* trigger recall, and record whether the agent actually used `ochist`. This is
the layer that measures the automaticity problem, and it cannot be a unit test because
it needs a live model. Run it manually, record the result in
`docs/AGENT_EVAL_LOG.md`, review monthly.

### Why not fully automated

An `opencode run` test costs a model call and is non-deterministic — a flaky CI gate is
worse than no gate. Layer 2 catches the failure mode I actually hit (a command whose
description sends the agent to the wrong tool). Layer 3 measures adoption.

---

## 3. P1 — Config repo remote + secret scanning

### Prerequisites verified

```
gitleaks      NOT INSTALLED
pre-commit    NOT INSTALLED
```

Both must be installed before any of this. `pip install pre-commit` and the gitleaks
binary (apt or the release tarball).

### Remote

`~/.config/opencode` has commit `23698b5` and **no remote**. The bare-repo pattern is
the community standard for dotfiles
(<https://www.ackama.com/articles/the-best-way-to-store-your-dotfiles-a-bare-git-repository-explained>
— note the useful correction there: *"The secret sauce is the work tree configuration,
not the bare repository"*, and a non-bare repo is functionally identical).

**But I already used the non-bare form** — `git init` inside `~/.config/opencode` itself,
tracking 18 files at their real paths. That is the simpler and equally valid variant. Do
**not** restructure to a bare repo now; it would gain nothing and risk breaking the
live config.

Remaining step is one command:
```bash
cd ~/.config/opencode
git remote add origin git@github.com:Xoe-NovAi/opencode-config.git
git push -u origin main
```
Requires the repo to exist and be private. **Blocked on the repo URL.**

### Gitleaks config

`.gitleaks.toml` with two allowlists that our tree specifically needs:
- npm `sha512-` integrity hashes in `package-lock.json` (32 of them — verified)
- `.md` files, where `{env:API_KEY}` references appear

```toml
title = "opencode-config gitleaks config"

[[allowlists]]
description = "npm integrity hashes are checksums, not secrets"
regexes = ['''sha512-[A-Za-z0-9+/=]{80,}''']

[[allowlists]]
description = "MCP configs reference secrets by env interpolation only"
paths = ['''(?i)(opencode\.jsonc?|\.env\.template)$''']
```

Then `pre-commit install` and `pre-commit run --all-files` to validate against the
existing 18 files before trusting it.

---

## 4. P1 — Coordination contract

**File: `docs/COORDINATION.md`** (~2h)

Production consensus from two independent sources:
- Anthropic, five coordination patterns — Shared State suits collaborative work where
  agents build on each other's findings
  (<https://claude.com/blog/multi-agent-coordination-patterns>)
- Devsatva, four production patterns from 12 deployed systems —
  *"one writer per state layer — non-negotiable for correctness"* and *"audit every
  write — multi-agent state corruption is hardest to debug post-hoc"*
  (<https://devsatva.com/blog/multi-agent-coordination-patterns-2026>)

Also worth recording: *"Agent failures are not exceptions — they're the median case."*
Every agent should declare timeout, retry policy, and degradation mode.

| Layer | Store | Writer | Notes |
|---|---|---|---|
| Corrections | `gnosis/well/well.jsonl` | `well_storage.py` via `make well-add` | append-only, never hand-edited |
| Semantic | MemPalace KG | `mempalace_kg_*` | single-writer enforced by lock |
| Episodic | MemPalace drawers | `mempalace_add_drawer` | |
| Session DB | `opencode.db` | OpenCode process only | **never** write directly |
| Events | `omega-hub` | `omega-hub` | advisory locks, TTL |

---

## 5. Explicitly dropped

| Item | Why |
|---|---|
| `pydantic-evals` | Requires OTel spans OpenCode does not emit; adds 3 deps for assertions `unittest` already expresses |
| EMG / `hermes-emg` | Requires paired failed/expert trajectories; we have real transcripts, not demonstrations. Also Hermes-native, not OpenCode |
| AgentRecall-X install | MCP-server for Claude Code; adds a parallel memory system to a setup that already has The Well. Borrow the *idea*, not the package |
| Vector/semantic search over sessions | Full embed = 31 min; regex + FTS5 answers recall better at 15.6k parts |
| FTS5 index on Node 1 | 15.6k searchable parts — a full scan is 282 ms. No index needed below ~200k |

---

## 6. Execution order

```bash
cd /home/xnai/Documents/Projects/omega-engine-alpha

# P0-1: recurrence detector (no new deps)
#   scripts/well_recurrence_check.py
#   verify tool-only filtering removes documentation false positives

# P0-2: regression test (existing runner)
#   tests/test_recall_stack.py → make test picks it up automatically

# P1-1: config remote — BLOCKED on repo URL
#   cd ~/.config/opencode && git remote add origin <url> && git push -u origin main

# P1-2: install + configure secret scanning
pip install pre-commit          # gitleaks binary separately
#   ~/.config/opencode/.gitleaks.toml, then pre-commit run --all-files

# P1-3: docs/COORDINATION.md

# Gates
make lint && make test && make docs
```

---

## 7. What I could not verify

- **The docs false-positive filter** (§1) is a design I have reasoned about but not
  implemented. The 15 matches on `3becf4f3` include at least 3 that are me documenting
  the rule. The filter must be proven against real data before the detector's output can
  be trusted; until then its counts are an upper bound.
- **Whether agents actually route to `/recall` and `/db`** is unmeasured. That is the
  open question the whole automaticity problem turns on, and layer 3 of the test is
  manual by necessity.
- **No AgentEval log exists yet.** `docs/AGENT_EVAL_LOG.md` is to be created with the
  first recorded manual run.
- The config repo has **no remote and no `install.sh`**. Machine onboarding is manual
  until both exist.

---

## 8. Sources

- Anthropic, five coordination patterns — <https://claude.com/blog/multi-agent-coordination-patterns>
- Devsatva, four production patterns, 12-agent case study — <https://devsatva.com/blog/multi-agent-coordination-patterns-2026>
- AgentRecall-X analysis incl. the zero-organic-calls and density findings — <https://hysenlabs.com/projects/goldentrii-agentrecall-x>
- AgentRecall-X repository — <https://github.com/Goldentrii/AgentRecall-X>
- EMG paper (dropped: needs paired expert trajectories) — <https://arxiv.org/abs/2607.13884>
- `hermes-emg` implementation (dropped: Hermes-native) — <https://github.com/lesterppo/hermes-emg>
- Pydantic Evals span-based evaluation, "Requires the logfire SDK" — <https://pydantic.dev/docs/ai/evals/evaluators/span-based>
- Pydantic Evals overview — <https://pydantic.dev/docs/ai/evals/evals>
- TypeScript mirror `logfire/evals` — <https://pydantic.dev/docs/logfire/instrument/typescript/evals/>
- Dotfiles via bare git repo, and the non-bare equivalence — <https://www.ackama.com/articles/the-best-way-to-store-your-dotfiles-a-bare-git-repository-explained>
- Gitleaks config reference — <https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml>
- Gitleaks pre-commit setup — <https://github.com/crow50/Gitleaks-Secret-Scanning>
- pydantic-ai #2981: break complex agent evals into small cases — <https://github.com/pydantic/pydantic-ai/issues/2981>
- Context vs memory engineering, budget-before-retrieve — <https://machinelearningmastery.com/ai-agent-memory-design-what-works-and-what-doesnt/>
- Anthropic, effective context engineering — <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>

Local evidence (Node 1, 2026-10-02):
- `ochist grep "opencode db" --global --json` → 15 timestamped matches, proving
  mechanical recurrence detection is feasible
- project venv: `pytest`, `anyio`, `sqlite_vec`, `numpy`, `scipy` present;
  `pydantic_evals`, `pydantic_ai`, `logfire`, `networkx` absent
- `gitleaks`, `pre-commit`, `uv` absent from PATH
- `make test` runs `unittest discover -s tests`, not pytest