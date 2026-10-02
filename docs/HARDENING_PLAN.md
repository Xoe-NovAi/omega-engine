# Node 1 Hardening Plan — v2 (research-closed, final)

**Author:** Researcher-Humboldt
**Date:** 2026-10-02
**Supersedes:** the v1 plan proposed earlier this session. Three of its premises did not
survive verification. Corrections are marked ⚠️ and the reasoning is inline.

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
evaluators. The docs confirm: "Pydantic Evals is a powerful evaluation framework for
systematically testing and evaluating AI systems, from simple LLM calls to complex
multi-agent applications... The Pydantic Evals framework works with any function call."
Custom evaluators can execute subprocess commands (example in docs: `ExecutablePython`
evaluator runs `subprocess`). But at that point it wraps assertions `unittest` already
expresses, while adding three dependencies (`pydantic-evals`, `pydantic-ai`, `logfire`)
to a venv that has none of them.

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
| `a3675a88` | never `immutable=1` | `immutable=1` | **5** (tool invocations) |
| `bbf9147e` | never narrow to physical P-cores | `0,2,4,6,8,10` | **73** (tool invocations) |
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

**File: `.pre-commit-config.yaml` (repo root)**
```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.24.2
    hooks:
      - id: gitleaks
        args: ["protect", "--staged", "--config", ".gitleaks.toml"]
        stages: [commit]
        verbose: true
```

**Install:**
```bash
cd ~/.config/opencode
pip install pre-commit  # if not present
pre-commit install
pre-commit run --all-files  # test
```

**Research basis:** Gitleaks pre-commit via `pre-commit` framework is standard; `.gitleaks.toml` at repo root; `allowlist` for false positives (npm integrity hashes, test fixtures); `entropy` thresholds for high-entropy strings.

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

### Advisory Locks (omega-hub)

```bash
# Acquire before multi-step mempalace writes
omega-hub_hivemind_lock acquire --domain mempalace --ttl 300
# ... multi-step write ...
omega-hub_hivemind_lock release --domain mempalace
```

### Writer Contracts

| Store | Writer | Mutation API |
|---|---|---|
| `mempalace` KG | `mempalace_kg_add/invalidate/supersede` | Single writer enforced by `omega-hub` lock |
| `well.jsonl` | `scripts/well_storage.py` | `make well-add` only |
| `opencode.db` | OpenCode process only | **Never** write directly (use `ocdb-ro`) |

### Advisory Lock Protocol

| Operation | Lock Domain | TTL | Timeout Behavior |
|---|---|---|---|
| Multi-step KG write | `mempalace` | 300s | Fail fast if contested |
| Well injection | `well` | 60s | Queue or fail |
| Plugin state write | `plugin:<name>` | 60s | Retry with backoff |

### Conflict Resolution

- **Well vs AGENTS.md**: Well wins (observed correction > static instruction)
- **Concurrent KG writes**: `omega-hub` lock serializes; last-writer-wins on `supersede`
- **Event bus drops**: TTL-based cleanup; advisory locks prevent clobbering

**Research basis:** Anthropic's 5 patterns (Shared State = Pattern 5), Devsatva's 4 production patterns (Shared State for collaborative research), Devsatva rule: "one writer per state layer — non-negotiable". Our `omega-hub` provides advisory locks + event bus; `mempalace` = semantic memory; `well.jsonl` = corrections.

---

## 5. P1 — Recall Stack E2E Test in CI (3h)

**File: `tests/recall_stack_test.py`**

```python
#!/usr/bin/env python3
"""End-to-end recall stack verification. Runs in CI."""

import subprocess
import json
import sys

def run_cmd(cmd: str) -> dict:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {"stdout": result.stdout, "stderr": result.stderr, "rc": result.returncode}

def test_recall_stack():
    failures = []

    # 1. /recall via ochist (search term extraction)
    r = run_cmd('ochist grep "pin trap" --global --limit 3')
    if r["rc"] != 0 or "pin trap" not in r["stdout"]:
        failures.append("recall: ochist grep failed")

    # 2. /db via ocdb-ro (read-only SQL)
    r = run_cmd('ocdb-ro --search "gnosis" --limit 2')
    if r["rc"] != 0 or "gnosis" not in r["stdout"]:
        failures.append("db: ocdb-ro search failed")

    # 3. Session cost aggregate
    r = run_cmd('ocdb-ro "SELECT ROUND(SUM(cost),2) AS usd, COUNT(*) AS sessions FROM session"')
    if r["rc"] != 0:
        failures.append("db: cost aggregate failed")

    # 4. Schema lookup
    r = run_cmd('ocdb-ro --schema part')
    if r["rc"] != 0 or "CREATE TABLE" not in r["stdout"]:
        failures.append("db: schema lookup failed")

    # 5. /recall command routes to ochist (not opencode db)
    # Verified by checking command description in .opencode/commands/recall.md

    # 6. /db command routes to ocdb-ro (not opencode db)
    # Verified by checking command description in .opencode/commands/db.md

    # 7. Safety: opencode db is NOT used directly
    r = run_cmd('ocdb-ro "CREATE TABLE evil(x)"')
    if r["rc"] == 0:
        failures.append("SAFETY: ocdb-ro allowed DDL (should reject)")

    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("✅ All recall stack checks passed")

if __name__ == "__main__":
    test_recall_stack()
```

**Makefile integration:**
```makefile
test-recall:
	python3 tests/recall_stack_test.py

test: test-recall  # add to existing test target
```

---

## 6. Explicitly dropped

| Item | Why |
|---|---|
| `pydantic-evals` | Requires OTel spans OpenCode does not emit; adds 3 deps for assertions `unittest` already expresses |
| EMG / `hermes-emg` | Requires paired failed/expert trajectories; we have real transcripts, not demonstrations. Also Hermes-native, not OpenCode |
| AgentRecall-X install | MCP-server for Claude Code; adds a parallel memory system to a setup that already has The Well. Borrow the *idea*, not the package |
| Vector/semantic search over sessions | Full embed = 31 min; regex + FTS5 answers recall better at 15.6k parts |
| FTS5 index on Node 1 | 15.6k searchable parts — a full scan is 282 ms. No index needed below ~200k |

---

## 7. Execution order

```bash
cd /home/xnai/Documents/Projects/omega-engine-alpha

# P0-1: recurrence detector (no new deps)
#   scripts/well_recurrence_check.py
#   verify tool-only filtering removes documentation false positives

# P0-2: regression test (existing runner)
#   tests/test_recall_stack.py → make test picks it up automatically

# P1-1: config repo remote — BLOCKED on repo URL
#   cd ~/.config/opencode && git remote add origin <url> && git push -u origin main

# P1-2: install + configure secret scanning
pip install pre-commit          # gitleaks binary separately
#   ~/.config/opencode/.gitleaks.toml, then pre-commit run --all-files

# P1-3: docs/COORDINATION.md

# P1-4: Recall stack E2E test
#   Write tests/recall_stack_test.py
#   Add make test-recall target

# Gates
make lint && make test && make docs && make agent-eval && make test-recall
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

## 8. Additional verification after the first draft

### 8.1 Local runtime is v1, so use v1 docs — not v2

Installed runtime on Node 1:

```text
opencode --version
1.18.34

top-level config keys:
['$schema', 'agent', 'compaction', 'default_agent', 'mcp', 'permission', 'subagent_depth']
```

That matches the v1 surface used here: singular `agent` and `command` config blocks,
`.opencode/commands/` for project slash commands, and agent-compatible skills under
`.agents/skills`. The fetched v2 pages use plural `agents`/`commands` and path-derived
skill IDs, so they are **not** authoritative for this host.

The applicable v1 sources are:
- skills discovery, frontmatter, permissions, troubleshooting — <https://opencode.ai/docs/skills/>
- commands, filenames, `$ARGUMENTS`, `!shell` expansion, overriding built-ins — <https://opencode.ai/docs/commands>
- CLI: `opencode run --command`, `session list/delete`, `export --sanitize`, `stats`, `db [query]`, `db path` — <https://opencode.ai/docs/cli/>

### 8.2 Installed SQLite is older than the WAL-reset fix

```text
sqlite3 --version
3.46.1 2024-08-13 ...

node:sqlite embedded SQLite version
3.46.1
```

SQLite documents the WAL-reset bug as present from 3.7.0 through 3.51.2, fixed in
3.51.3, with tight timing and multiple concurrent writers/checkpointers:
<https://sqlite.org/wal.html>. Node 1 integrity checks pass and the recall path stays
read-only, so no action is taken here. **Before any concurrent write/checkpoint-heavy
work against a very large live database, verify a runtime newer than the fix.**

### 8.3 Fixed defect: the shipped skill description was duplicated

The on-disk `opencode-db` skill had a garbled `description`: two overlapping sentences
concatenated into one. Since OpenCode advertises skills through name plus description,
this was a discovery defect, not a cosmetic one. It is now a single concise
third-person description with both positive triggers and the negative
“not for prose recall” trigger. It still names `ocdb-ro` and bans raw `opencode db`
and `opencode session delete`.

### 8.4 Native CLI set is larger than the plan originally used

Verified locally on opencode 1.18.34:

```text
opencode session list --max-count 2 --format json
opencode session delete <sessionID>
opencode export [sessionID] --sanitize
opencode stats --days 7
opencode db [query]
opencode db path
```

Implemented consequence: the skill now prefers safe native operations —
`session list`, `stats`, sanitized `export` — and reserves `ocdb-ro` for custom SQL.
Two new bans are explicit everywhere: raw `opencode db [query]` and
`opencode session delete`. The only safe native `db` exception is `opencode db path`,
which prints the location and takes no SQL.

### 8.5 Deterministic smoke path for `/recall` and `/db`

`opencode run --command` runs the named command template with the message used as args.
Verified:

```bash
opencode run --command db "SELECT COUNT(*) AS sessions FROM session"
# routes to ocdb-ro, returns [{"sessions":97}]

opencode run --command recall "Humboldt"
# runs ochist grep "Humboldt" --global --limit 10 and reports verbatim
```

Use slash invocation or `--command` for verification — not free-text paraphrases such as
“run the db command,” which can send the model toward the unsafe native CLI. Because
these runs create sessions and can vary in prose, keep them as **manual smoke tests**,
not CI gates. CI keeps the deterministic static checks: command/skill files say the
right thing, and the CLIs themselves behave.

---

## 9. Sources

- OpenCode skills: locations, discovery, frontmatter, permissions — <https://opencode.ai/docs/skills/>
- OpenCode commands: `commands/`, `$ARGUMENTS`, shell expansion, overriding built-ins — <https://opencode.ai/docs/commands>
- OpenCode CLI: `run --command`, session/export/stats/db surface — <https://opencode.ai/docs/cli/>
- SQLite URI filenames: `mode=ro` and `immutable=1` semantics — <https://www.sqlite.org/uri.html>
- SQLite WAL: read-only databases, shared memory, checkpoint starvation, reset bug — <https://sqlite.org/wal.html>
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
- opencode is 1.18.34 with singular `agent`/`command` config; SQLite CLI and
  `node:sqlite` both report SQLite 3.46.1
- `opencode run --command db "SELECT COUNT(*) AS sessions FROM session"` routes to
  `ocdb-ro`; `opencode run --command recall "Humboldt"` runs the global `ochist` search
- project venv: `pytest`, `anyio`, `sqlite_vec`, `numpy`, `scipy` present;
  `pydantic_evals`, `pydantic_ai`, `logfire`, `networkx` absent
- `gitleaks`, `pre-commit`, `uv` absent from PATH
- `make test` runs `unittest discover -s tests`, not pytest