# Node 1 Hardening Plan — v2 (trimmed)

**Author:** Researcher-Humboldt
**Date:** 2026-10-02

---

## 0. What the research corrected

### ⚠️ Correction 1 — `pydantic-evals` span evaluation requires OTel spans
OpenCode emits no OTel spans. `HasMatchingSpan` cannot work. Dropped `pydantic-evals`. Use `unittest` assertions over `subprocess` output instead (zero deps).

### ⚠️ Correction 2 — Outcome tracking unmeasurable at our density
AgentRecall-X scores 0 on their own corpus (32 corrections / 19 projects). We have ~50 Well records — same density problem. Compliance *rate* not measurable. Pivot to **mechanical recurrence detection** (see §1).

### ⚠️ Correction 3 — EMG is not a pilot
EMG requires paired failed/success trajectories with expert demonstrations. We have real transcripts, not expert demos. Dropped.

---

## 1. P0 — Mechanical recurrence detection (highest value)

### Why this survives
AgentRecall-X's experimental harness: *"mechanical phantom detection (violation dated after its rule)"*. Mechanical, not LLM-judged. Proven on live data:

```bash
$ ochist grep "opencode db" --global --limit 20 --json
total matches: 15
  2026-10-01T08:44:44  tool  witty-sailor  opencode db
  ...
```

The transcript holds every tool invocation with timestamp. A correction at *T* and forbidden invocation at *T+1* is a **phantom gradient step** — detectable by string match, no model needed.

### Implementation: `scripts/well_recurrence_check.py` (~150 lines, zero deps)

```python
# Algorithm:
# 1. Load gnosis/well/well.jsonl (JSONL)
# 2. Filter kind == "correction" with violation_pattern
# 3. For each: ochist grep "<pattern>" --global --limit 50 --json
# 4. Filter: kind == "tool" AND timestamp > record.created_at
# 5. Exclude same-session matches (documentation false positives)
# 6. Write gnosis/well/recurrences.jsonl
```

**Detection patterns (verified):**

| Well ID | Rule | Pattern | Tool invocations |
|---|---|---|---|
| `3becf4f3` | never `opencode db` | `opencode db` | 15 |
| `a3675a88` | never `immutable=1` | `immutable=1` | 5 |
| `bbf9147e` | never narrow to physical P-cores | `0,2,4,6,8,10` | 73 |

**Caveat:** `3becf4f3` shows 15 matches, but all 15 are documentation/prose, not invocations. Filter to `kind == "tool"` to remove documentation false positives.

**Success criterion:** Detector reports 0 violations of `3becf4f3` after 2026-10-02 (rule in AGENTS.md, agent files, `/db` command).

---

## 2. P0 — Recall stack regression test (no new deps)

### The Automaticity Problem
> "Every pull-channel tool (`recall`, `memory_query`) saw **zero organic calls** across **44 projects** over weeks of real use — *including from the agent that built them*."
> — AgentRecall-X analysis

Installing a recall tool ≠ agents use it. Test must verify agents *route* to tools.

### Implementation: `tests/test_recall_stack.py` (plain `unittest`, existing runner)

**Status: DONE.** The file is a real `unittest.TestCase` (Layer 1 live checks:
ochist grep, ocdb-ro search/aggregate/schema, DDL + writefile/load_extension
safety rejections, skill presence — with `skipUnless` guards for missing
binaries). Collected by the existing `make test`
(`python3 -m unittest discover -s tests`); a completeness meta-test in
`test_repo_hygiene.py` fails if any `test_*.py` ever yields zero collected
tests. Layer 1 below is historical sketch; see the file for what runs.

**Layer 2 — commands route agents correctly (static):**
```python
def test_db_command_bans_native_cli(self):
    text = (COMMANDS / "db.md").read_text()
    self.assertIn("ocdb-ro", text)
    self.assertIn("opencode db", text)
    self.assertRegex(text, r"[Nn]ever.*opencode db")

def test_recall_command_requires_global(self):
    text = (COMMANDS / "recall.md").read_text()
    self.assertIn("--global", text)
    self.assertIn("regex", text.lower())
```

**Layer 3 — manual, recorded:** Run `opencode run` with recall-triggering prompt; record in `docs/AGENT_EVAL_LOG.md`. Monthly review.

**Why not automated:** `opencode run` costs a model call, non-deterministic. Layer 2 catches the collision I hit; Layer 3 measures adoption.

**Makefile:** none needed — the existing target collects it:
```makefile
test:
	.venv/bin/python3 -m unittest discover -s tests -v   # includes test_recall_stack
```

---

## 3. P1 — Config repo remote + secret scanning (1h)

### Remote
```bash
cd ~/.config/opencode
git remote add origin git@github.com:Xoe-NovAi/opencode-config.git
git push -u origin main
```
**Blocked on repo URL.** Non-bare repo (18 files, real paths) — simpler than bare, equally valid.

### Gitleaks config (`.gitleaks.toml`)
```toml
title = "opencode-config gitleaks config"

[[allowlists]]
description = "npm integrity hashes are checksums, not secrets"
regexes = ['''sha512-[A-Za-z0-9+/=]{80,}''']

[[allowlists]]
description = "MCP configs reference secrets by env interpolation only"
paths = ['''(?i)(opencode\.jsonc?|\.env\.template)$''']
```

**File: `.pre-commit-config.yaml`**
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

**Install:** `pip install pre-commit gitleaks && pre-commit install && pre-commit run --all-files`

---

## 4. P1 — Coordination contract (condensed)

**File: `docs/COORDINATION.md`** (condensed from 2h to 30 min)

Production consensus: **Shared State** primary + **Event Bus** (omega-hub).

**One writer per layer — non-negotiable:**

| Layer | Store | Writer | Consistency |
|---|---|---|---|
| Corrections | `gnosis/well/well.jsonl` | `well_storage.py` | Strong |
| Semantic | MemPalace KG | `mempalace_kg_*` | Eventual |
| Episodic | MemPalace drawers | `mempalace_add_drawer` | Strong |
| Session DB | `opencode.db` | OpenCode only | **Never write directly** |
| Events | `omega-hub` | `omega-hub` | At-least-once |

**Advisory locks:** `omega-hub_hivemind_lock acquire --domain mempalace --ttl 300`

**Writer contracts:** Single writer per layer enforced by locks. Well wins over AGENTS.md.

---

## 5. P1 — Recall stack E2E test (3h)

**Superseded by §2 — DONE.** The E2E test landed as
`tests/test_recall_stack.py` (a `unittest.TestCase`, not the bare function
sketched here) and is collected by the existing `make test`; there is no
separate `test-recall` target. The bare-function sketch below would have been
invisible to `unittest discover` — see `TestDiscoveryCompleteness` in
`tests/test_repo_hygiene.py`, which fails any test file yielding zero
collected tests. Historical sketch retained for context:

~~File: `tests/recall_stack_test.py` (bare function + `test-recall` Makefile target)~~

---

## 6. Explicitly dropped

| Item | Why |
|---|---|
| `pydantic-evals` | Requires OTel spans; adds 3 deps for assertions `unittest` expresses |
| EMG / `hermes-emg` | Needs paired failed/expert trajectories; we have real transcripts |
| AgentRecall-X install | Adds parallel memory; borrow the *mechanical* idea only |
| Vector search | Full embed = 31 min; regex + FTS5 answers recall at 15.6k parts |
| FTS5 index on Node 1 | 15.6k searchable parts — scan 282 ms. No index below ~200k |

---

## 7. Execution order

```bash
cd /home/xnai/Documents/Projects/omega-engine-alpha

# P0-1: Recurrence detector (no new deps)
#   scripts/well_recurrence_check.py

# P0-2: Regression test (existing runner)
#   tests/test_recall_stack.py → TestCase, collected by make test
#   (enforced by test_repo_hygiene.TestDiscoveryCompleteness)

# P1-1: Config repo remote — BLOCKED on repo URL
#   cd ~/.config/opencode && git remote add origin <url> && git push -u origin main

# P1-2: Install + configure secret scanning
pip install pre-commit          # gitleaks binary separately
#   ~/.config/opencode/.gitleaks.toml, then pre-commit run --all-files

# P1-3: docs/COORDINATION.md (condensed)

# P1-4: Recall stack E2E test — DONE (tests/test_recall_stack.py, in make test)

# Gates
make lint && make test && make docs
```

---

## 8. What I could not verify

- **Docs false-positive filter** — 15 matches on `3becf4f3` include documentation; tool-only filter not yet proven.
- **Agent routing to `/recall`/`/db`** — unmeasured; Layer 3 manual.
- **No AgentEval log** — `docs/AGENT_EVAL_LOG.md` to be created first run.
- **Config repo** — no remote, no `install.sh`.

---

## 8. Sources

- OpenCode skills/commands/CLI v1 — <https://opencode.ai/docs/skills/>, <https://opencode.ai/docs/commands/>, <https://opencode.ai/docs/cli/>
- SQLite URI (`mode=ro`, `immutable=1`), WAL (read-only, checkpoint, reset bug) — <https://sqlite.org/uri.html>, <https://sqlite.org/wal.html>
- Anthropic coordination patterns — <https://claude.com/blog/multi-agent-coordination-patterns>
- Devsatva production patterns — <https://devsatva.com/blog/multi-agent-coordination-patterns-2026>
- AgentRecall-X analysis (zero organic calls, density problem) — <https://hysenlabs.com/projects/goldentrii-agentrecall-x>
- EMG paper (dropped) — <https://arxiv.org/abs/2607.13884>
- Pydantic Evals span-based requires logfire SDK — <https://pydantic.dev/docs/ai/evals/evaluators/span-based>
- Dotfiles bare repo equivalence — <https://www.ackama.com/articles/the-best-way-to-store-your-dotfiles-a-bare-git-repository-explained>
- Gitleaks config — <https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml>

Local evidence (Node 1, 2026-10-02):
- `ochist grep "opencode db" --global --json` → 15 timestamped matches
- opencode 1.18.34, singular `agent`/`command` config; SQLite 3.46.1
- `opencode run --command db "..."` routes to `ocdb-ro`; `--command recall` runs `ochist`
- venv: `pytest`, `anyio`, `sqlite_vec`, `numpy`, `scipy` present; `pydantic_evals`, `pydantic_ai`, `logfire`, `networkx` absent
- `gitleaks`, `pre-commit`, `uv` absent from PATH
- `make test` runs `unittest discover -s tests`