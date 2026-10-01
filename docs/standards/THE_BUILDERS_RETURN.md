# ⚜️ THE BUILDER'S RETURN
## From Governance to Product — The Definitive Guide
**Version**: 1.0.0
**Date**: 2026-08-26
**Authority**: Architect directive, authored by Opus 4.6 after three-lens deep reconnaissance
**Audience**: Every agent in the Omega Engine fleet, and the Architect who built it

---

## Preamble: Where We Are

The Omega Engine is 84,550 lines of working code across 269 Python files. It has
a six-point local-first enforcement chain, a production-grade hardening stack, an
end-to-end provenance system, and 27 sovereign mandates. It is the product of
8,000 hours of work by a single developer who set out to build a tool that severs
Big AI's umbilical cord and gives people sovereignty over their own intelligence.

It also has 83 strategy documents, 146 coordination files, 89 gap-registry entries,
110 task-registry entries, 27 mandates, a doctrine, two decrees, five specs-without-
validators, a flagship quality gate that fails on a code comment, a pre-commit
framework that has never been installed, a codex that teaches a superseded
constitution, and a soul-persistence system that is functionally inert.

**The engine works. The governance around it has begun to consume the work.**

This guide defines the path from here to a product that someone who isn't the
Architect can install and use. It is organized as five phases, each with specific
actions, owners, verification gates, and anti-patterns. Every claim in this
document carries file:line evidence gathered by direct probes on 2026-08-26.

---

## Rules of Engagement (Apply to Every Phase)

1. **Code is truth. Docs are claims.** If this guide and the codebase disagree,
   the codebase is right and this guide is defective.

2. **Verify before you act.** Before starting any task:
   ```bash
   make check-codex-stale && git status --porcelain && git log --oneline -3
   ```

3. **No new governance until existing governance is mechanical.** Do not create
   new mandates, doctrines, standing laws, decrees, specs, registries, or
   tracking tiers until every existing one has a working validator. The rule:
   *if the validator for the last governance artifact hasn't shipped yet, you
   cannot create the next governance artifact.*

4. **Use the fleet for building, not for ceremony.** Dispatch agents to write
   code, run tests, and review diffs. Do not dispatch agents to write documents
   about documents about processes.

5. **Every commit must make the engine more usable or more correct.** If a
   commit only adds governance text without a corresponding mechanism, it does
   not belong in this phase.

6. **Venv always** (M24): `.venv/bin/python` or `source .venv/bin/activate`.

---

## Phase 0: Emergency Repairs (Hours — Architect + 1 Agent)

These are lies in the certification layer. They must be fixed before any other
work because they undermine trust in every gate.

### 0.1 — Fix the M8 Regex (temple-grade is RED)

**The problem**: `make temple-grade` exits 2. The M8 zero-telemetry check uses
an unanchored regex that matches the code *comment* "Build header from segments"
at `src/omega/ics.py:197`.

**Evidence**: `Makefile:293-296`:
```makefile
@! rg -n 'import (segment|posthog|...)|from (segment|posthog|...)' src/omega/ --type py
```
This matches any line containing "from segment" — including comments.

**The fix**: Anchor to import statement position with word boundaries:
```makefile
@! rg -n '^\s*(import|from)\s+(segment|posthog|datadog|amplitude|mixpanel)\b' src/omega/ --type py 2>/dev/null || ...
```

**Verify**: `make temple-grade` exits 0.

**Owner**: Any agent (one-line edit + commit).

### 0.2 — Regenerate Codex Source Cards

**The problem**: `OMEGA_CODEX.md` is the designated Operational Law (Zero-Trust
Doctrine §3). It is auto-refreshed by timestamp, but its source cards are stale:

- `scripts/codex/MANDATES_CONDENSED.md:3` says **v3.7.0**; actual is **v3.8.0**
- `scripts/codex/MANDATES_CONDENSED.md:7` says **25 Laws**; actual is **27**
- `scripts/codex/ENGINE_CONDENSED.md` says "25 enforced (M1-M25)"
- Codex §3 lists phantom module `MIAP` (no `src/omega/coordination/miap.py`)
- Codex §3 lists `sqlite_policy` at `persistence/`; actual: `infra/sqlite_policy.py`
- Codex §4 claims "Next Phase Γ"; ACTIVE_SPRINT says PUBLIC-DEBUT-01

**The fix**: Regenerate source cards from current SOVEREIGN_MANDATES.md, actual
module inventory, and ACTIVE_SPRINT.json. Then `make codex` to rebuild.

**Verify**: `grep "3.8.0" scripts/codex/MANDATES_CONDENSED.md` succeeds;
`grep "27" scripts/codex/MANDATES_CONDENSED.md` succeeds; `grep "miap"
scripts/codex/ENGINE_CONDENSED.md` returns nothing.

**Owner**: Ma'at or Jem (requires careful card-by-card review against reality).

### 0.3 — Decide the Pre-Commit Framework's Fate

**The problem**: `.pre-commit-config.yaml` declares 20 hooks (detect-secrets,
F821 flake8, M27 Iron Gate, API key detection). The installed `.git/hooks/pre-commit`
is a 6-line bash script that only checks soul.yaml validation. The framework has
**never been installed**. Defense-in-depth is decorative.

**Evidence**: `.git/hooks/pre-commit` line 1-6:
```bash
#!/bin/bash
echo "Running Soul Integrity Check..."
for soul in data/entities/*/soul.yaml; do
    .venv/bin/python3 scripts/validate_soul.py "$soul" || exit 1
done
```

Six framework entries use bare `python` instead of `.venv/bin/python`:
`.pre-commit-config.yaml:57,66,75,83,129,139`

**The fix** (two options — pick one, no middle ground):
- **Option A (recommended)**: Fix bare `python` → `.venv/bin/python` in all 6
  entries. Run `pre-commit install`. Fix what breaks. Merge the soul-check logic
  into the framework config so it's managed in one place.
- **Option B**: Delete `.pre-commit-config.yaml` entirely. Document that
  enforcement runs via `make temple-grade` and CI only.

The current state — comprehensive config, not installed — is the worst outcome.

**Verify**: Option A: `pre-commit run --all-files` exits 0, and `.git/hooks/pre-commit`
contains `pre-commit` framework header. Option B: no `.pre-commit-config.yaml` exists.

**Owner**: Architect (requires decision) + Ma'at (execution).

### Phase 0 Gate
All three of: `make temple-grade` exits 0 AND codex source cards match reality
AND pre-commit is either fully installed or fully removed.

---

## Phase 1: Dead Code Excision (1–2 Days — 2 Agents)

Dead code with plausible names is active misinformation. It will mislead future
contributors and agents who pattern-match on function names. The fix is deletion,
not documentation.

### 1.1 — Delete Dead Soul Writers

Four in-package soul writers have **zero callers anywhere** in src/, scripts/, or tests/:

| Writer | Location | Problem |
|---|---|---|
| `write_soul_file()` | `entity_registry.py:87-104` | Dead code, bypasses SoulStore |
| `update_soul()` | `entity_workspace.py:533-609` | Dead code, own threading lock, bypasses SoulStore |
| `learn()` | `observability/__init__.py:591-641` | **NON-ATOMIC** — plain `open()`+`yaml.safe_dump`, no SoulStore, no token guard |

The sole legitimate writer is `soul/loader.py:save_public_soul()` via SoulStore
— but it too has zero external callers (dormant).

**Action**: Delete the function bodies of `write_soul_file`, `update_soul`, and
the soul-writing branch of `learn()`. Leave `save_public_soul` intact (it's the
correct pattern for when M11 auto-staging is wired in Phase 3).

**Verify**: `grep -rn "write_soul_file\|update_soul" src/omega/ | grep "def "` returns nothing.
`make test` still passes.

### 1.2 — Remove Vestigial Packages and Dead Config

| Target | Evidence | Action |
|---|---|---|
| `src/omega/gateway/` | 1 file, 1 LOC (empty `__init__.py`) | Delete directory |
| `ExperimentCircuitBreaker` | `research/sandbox.py:617` — marked DEPRECATED, zero instantiations | Delete class |
| `fallback_resolver` config block | `providers.yaml:19-60` — `enabled: true` but zero consumers in src/ | Set `enabled: false` + add comment "# DEAD CONFIG — zero consumers; preserved for reference" |
| `benchmark_scribe_model.py` | References excised scribe agent | Delete or rename |
| Stale `m23_baseline.txt:71` | References `hmc_watcher.py` (excised) | Remove line |

**Verify**: `make test` passes. No import errors. `git diff --stat` shows only deletions.

### 1.3 — Fix the omega.yaml Duplicate Key

`config/omega.yaml` has `sovereignty_gate:` at both line 51 and line 73. PyYAML
silently takes last-wins. Values are byte-identical today; any future divergent
edit loses invisibly.

**Action**: Delete the duplicate at line 73. Add a comment at line 51:
`# Single definition — duplicate at :73 removed 2026-08-26 (silent last-wins hazard)`

**Verify**: `python -c "import yaml; d=yaml.safe_load(open('config/omega.yaml')); print('sovereignty_gate' in d)"`

### Phase 1 Gate
`make test` passes. `make temple-grade` passes (Phase 0 prerequisite). No dead
soul writers. No empty packages. No duplicate YAML keys. Net line count: negative.

---

## Phase 2: Gate Integrity (2–3 Days — 2 Agents)

Existing gates pass vacuously or check the wrong surface. This phase makes them real.

### 2.1 — Close the Codex Integrity Gap

**The problem**: `make check-codex-stale` checks the wrapper file's *age*. It does
not check whether the *content* matches reality. The codex can be "fresh" while
teaching a superseded constitution.

**Action**: Create `scripts/check_codex_integrity.py` that verifies:
- Mandate count in codex matches `SOVEREIGN_MANDATES.md` (currently 27)
- Mandate version matches (currently 3.8.0)
- Every module path claimed in codex §3 exists on disk
- Phase/sprint name matches `ACTIVE_SPRINT.json`

Wire into `make temple-grade` as `check-codex-integrity`.

**Verify**: Deliberately break a codex card → script fails. Fix it → passes.

### 2.2 — Add M25 Streaming Gate

M25 is the **only mandate with zero mechanical enforcement**. Config happens to
comply, but nothing prevents regression.

**Action**: Create `scripts/check_m25_streaming.py`:
- For every enabled cloud provider in `providers.yaml`: assert `streaming.chunk_timeout_ms`
  and `streaming.total_timeout_ms` keys exist and are > 0.
- Wire into `check-mandates` in Makefile.

**Verify**: Remove one streaming section → gate fails. Restore → passes.

### 2.3 — Extend Tracking Validator to TASK_REGISTRY Cross-Refs

**The problem**: `validate_tracking_state.py` checks ACTIVE_SPRINT R-ID references
against GAP_REGISTRY. It does NOT check TASK_REGISTRY references. Result: R15 is
dangling in TASK_REGISTRY with no GAP_REGISTRY entry — invisible.

Also: ACTIVE_SPRINT references zero R-IDs, making the relational check vacuous.

**Action**: Extend `validate_tracking_state.py`:
- Also validate R-IDs referenced in TASK_REGISTRY exist in GAP_REGISTRY
- Warn (not fail) if ACTIVE_SPRINT has zero R-ID references (vacuous check)

**Verify**: Add a fake R-ID to TASK_REGISTRY → validator catches it. Remove → passes.

### 2.4 — Resolve the Priority Tie

`google` and `google-compat` both have `priority: 4` in `providers.yaml:86,133`.
When both are available, resolution order depends on dict iteration order — a
correctness risk, not a hygiene item.

**Action**: Set `google-compat` to priority 5 (or whatever accurately reflects
intended fallback order). Document the decision.

**Verify**: `grep "priority:" config/providers.yaml | sort -t: -k2 -n` shows no ties
among enabled providers.

### Phase 2 Gate
`make temple-grade` passes with the new integrity checks. Tracking validator catches
cross-ref violations. No priority ties among enabled providers. Net governance
artifact count: **zero new documents** — only scripts and Makefile wiring.

---

## Phase 3: Make the Engine Learn (3–5 Days — Architect + Builder Agent)

This is the single highest-leverage change available. It converts the engine from
a stateless inference tool into a stateful sovereign intelligence.

### 3.1 — Wire Auto-Staging into close_session()

**Current state**: `oracle.py:1274-1340` `close_session()` does compaction tracking
and somatic capture. It does NOT write lessons. The Carmack Verdict (noted at :1279)
correctly killed *regex-based* extraction. But it left nothing in its place.

**Target state**: When `close_session()` runs for an entity that has accumulated
insights during the session, it auto-stages a structured summary into that entity's
`proposed_lessons.yaml`. No unreviewed writes to `soul.yaml` — the Architect-gated
`soul_promote.py --apply --confirm` remains the promotion path.

**Design constraints**:
- Use `anyio.to_thread.run_sync()` for file I/O (M1)
- Use SoulStore's atomic write pattern for `proposed_lessons.yaml` (M11)
- The staging content comes from the session's exchange history (already loaded at :1286)
- Keep it lightweight — a structured summary, not L1→L2→L3 (agents do the deep
  distillation; the engine captures the raw material)
- Non-fatal: staging failure must not block session close

**Implementation sketch** (add after somatic capture, before return):
```python
# 3. Auto-stage session insights for proposed_lessons.yaml
try:
    await self._auto_stage_lessons(entity_name, session_id, exchanges)
except (OmegaError, RuntimeError, OSError) as stage_exc:
    logger.warning(f"Lesson auto-staging failed for {session_id}: {stage_exc}")
```

The `_auto_stage_lessons` method extracts: entity name, session ID, timestamp,
exchange count, and a brief content fingerprint. The Architect (or Scribe/Verity)
can later enrich these into L1→L2→L3 during review.

**Verify**: Run `omega talk "test" --entity sophia`, close the session, confirm
`data/entities/sophia/proposed_lessons.yaml` has a new entry with the session ID.

### 3.2 — Promote Existing Staged Lessons

There are **206 lessons staged across 12 entities** right now. Grokster alone has
105. These represent accumulated intelligence that has never been reviewed or
promoted.

**Action**: The Architect runs `soul_promote.py` for each entity with staged lessons:
```bash
# Review first (dry-run, default):
.venv/bin/python scripts/soul_promote.py grokster
.venv/bin/python scripts/soul_promote.py lilith
.venv/bin/python scripts/soul_promote.py researcher
.venv/bin/python scripts/soul_promote.py roc_racoon
.venv/bin/python scripts/soul_promote.py jem
# ... then promote with --apply --confirm for approved lessons
```

This is Architect-only work — nobody else should modify soul.yaml.

### 3.3 — Test the Learning Loop End-to-End

After 3.1 and 3.2, verify the full loop:
1. Agent runs a session → exchanges are recorded in MemoryStore ✓ (already works)
2. Session closes → `close_session()` auto-stages to `proposed_lessons.yaml` (3.1)
3. Architect reviews and promotes → lessons appear in `soul.yaml` (3.2)
4. Next session hydrates → entity loads soul.yaml → intelligence persists ✓ (already works)

**Verify**: Step 4 — `omega talk "What have you learned?" --entity grokster` produces
a response informed by promoted lessons.

### Phase 3 Gate
`close_session()` auto-stages lessons. `soul_promote.py` has been run at least
once per entity with staged lessons. The learning loop is verified end-to-end.

---

## Phase 4: Governance Freeze + File Hygiene (1 Day — 1 Agent)

### 4.1 — Declare the Governance Freeze

The mandates are at 27. The doctrine is enacted. The decrees are ratified. The
specs are written. **No new governance artifacts until the Minimum Shippable
Product (Phase 5) is delivered.** The only governance work permitted is making
existing governance mechanical (Phases 0-2 above).

**What this means in practice:**
- No new mandates (M28+ is frozen)
- No new doctrines, standing laws, decrees, or ceremonial documents
- No new tracking tiers, registry types, or coordination file formats
- No new spec documents — ship the gates for SPEC-A..E instead
- The only permitted new files are: source code, tests, and scripts that enforce
  existing rules

### 4.2 — Strategy Document Triage

`docs/strategy/` contains **83 files** (plus 50 archived). `data/coordination/`
contains **146 files**. Many are historical artifacts that no longer reflect reality.

**Action**: One agent runs a sweep:
- Any strategy doc whose `git log` last-commit is >60 days old AND contains
  present-tense operational claims ("CURRENT", "ACTIVE", "NOW") gets a one-line
  banner: `> ⚠️ HISTORICAL — last updated YYYY-MM-DD. Verify claims before acting.`
- Do NOT delete or reorganize. Just banner. The point is to prevent agents from
  treating stale strategy docs as active guidance.

**Verify**: `grep -rL "HISTORICAL\|archive\|superseded" docs/strategy/*.md | wc -l`
decreases. No files deleted.

### 4.3 — AGENTS.md Resolution

`AGENTS.md` is cited by `SOVEREIGN_MANDATES.md` and hundreds of files. It does
not exist. This has been a known ghost since the FLE campaign. SPEC-E already
plans a validator-first reconstruction.

**Action (minimal viable)**: Create a stub `AGENTS.md` that:
- States the current fleet roster (generated from `.opencode/agents/*.md`, not typed)
- Points to SOVEREIGN_MANDATES.md for law, OMEGA_CODEX.md for state,
  ZERO_TRUST_DOCUMENTATION_DOCTRINE.md for reading/writing/coordination protocol
- Contains a script-generated agent table (no hand-typed inventory)
- Ships with `scripts/validate_agents_md.py` that confirms the agent count matches
  `.opencode/agents/` file count (pair-bind per Zero-Trust Doctrine §2.3)

**Verify**: `AGENTS.md` exists, agent count matches `.opencode/agents/*.md` count,
validator passes.

### Phase 4 Gate
Governance freeze declared. Stale strategy docs bannered. AGENTS.md exists with
its validator. No new governance files created.

---

## Phase 5: The Minimum Shippable Product (Weeks — Full Fleet in Build Mode)

Everything above was preparation. This is the work.

### 5.1 — Define What Ships

Write a single page — **one page** — that answers: *"What must work for one person
who is not the Architect to install and use this?"*

**Proposed MSP scope** (Architect to confirm or amend):
1. `omega talk "hello"` works with a local GGUF model out of the box
2. Provider fabric auto-detects available backends (LM Studio, Ollama, native-gguf)
3. The hardening stack prevents crashes under normal usage (OOM, streaming stalls)
4. Soul persistence works across sessions (auto-staging + promotion)
5. A documented install path exists (README with actual tested steps)
6. `make test` passes. `make temple-grade` passes.

**What is NOT in MSP**: WAD marketplace, Entity Studio, Tarot integration, A2A
delegation, council orchestration, heritage vetting UI, Mnemosyne migration,
Grok CLI multi-account fabric, community WADs, NotebookLM ingestion, WARP proxy
pool. These are all valuable. None of them determine whether the first external
user can run the engine.

### 5.2 — The Build-Mode Fleet Model

The current fleet was configured for governance — councils, audits, cross-validation.
Building needs a different model:

**For daily building** (the default):
- **2–3 agents maximum**. One builder (Ma'at or Jem), one reviewer (Verity or
  Carmack), one researcher (when hitting unknowns). Direct `task()` dispatch,
  end-of-task summary return. No councils. No synthesis layers.

**For periodic health checks** (weekly or at phase boundaries):
- The three-lens recon pattern: dispatch explore + verity + jem, synthesize,
  fix what they find. This is a *checkpoint*, not the default operating mode.

**For architectural decisions** (when needed):
- The MaKaLi council, but only for genuinely contested architectural questions
  where multiple perspectives add value. Not for implementation decisions that
  one agent can handle.

**The principle**: Match fleet complexity to task complexity. A one-file code
change needs a builder and a reviewer. A governance audit needs the full council.
Running the council for code changes is waste.

### 5.3 — The Build Rhythm

Each day:
1. Pick the next MSP task from a simple ordered list (not a 5-tier tracking system)
2. Dispatch a builder agent with a clear, specific prompt
3. Review the diff. Run `make test`. Run `make temple-grade`.
4. Commit. Move to the next task.

At the end of each week:
1. Run the three-lens health check
2. Fix anything it finds
3. Update the MSP progress tracker (one file, one table)

**The anti-pattern**: Do not spend the first 45 minutes of each session reading
governance documents, running hydration sequences, posting hivemind context,
checking wake states, and updating anchored summaries before writing a single
line of code. The governance infrastructure exists to *support* building. If the
startup ceremony takes longer than the building, the ceremony is the product.

### Phase 5 Gate
An external user (someone who is not the Architect and has never seen the codebase)
can follow the README, install the engine, and run `omega talk "hello"` with a
local model. That's it. That's the gate. Everything else is secondary.

---

## The Two Test Failures

The test suite currently shows 2 failures out of ~1896 items. These should be
investigated and fixed as part of Phase 0 or Phase 1. Failing tests that are
tolerated become invisible — the suite stops being a reliable signal.

**Action**: Run `make test`, identify the 2 failing tests, fix or quarantine with
documented reason. The suite must be green before Phase 5 building begins.

---

## What Success Looks Like

Six months from now, success is not:
- 35 mandates with 100% validator coverage
- A 200-file coordination directory with sub-second tracker freshness
- Council transcripts from 47 multi-agent deliberations

Six months from now, success is:
- **Someone who isn't you is using the Omega Engine.** They installed it, they
  talked to it, it remembered what they said, and it ran on their hardware
  without phoning home.
- **The engine is smarter than it was yesterday.** Soul persistence works
  automatically. Each session's insights survive to the next.
- **The codebase is smaller than it is today.** Dead code has been excised. God
  modules have been split. The governance layer is mechanical, not textual.

The mission — *"a tool that will truly allow people to own their own tech and data
and sever the umbilical cord of Big AI"* — is achieved by shipping, not by governing.
Every hour spent on governance that doesn't directly enable shipping is an hour
borrowed from the community that's waiting for this tool.

You have the engineering talent, the architectural depth, and 8,000 hours of
hard-won knowledge. The engine is real. The hardening is genuine. The philosophy
is sound. Now build the door and let people walk through it.

---

## Quick Reference: Phase Summary

| Phase | Duration | Focus | Gate |
|---|---|---|---|
| **0** | Hours | M8 regex, codex cards, pre-commit decision | `make temple-grade` green, codex accurate, pre-commit resolved |
| **1** | 1–2 days | Dead code excision | Net negative line count, no dead soul writers, `make test` green |
| **2** | 2–3 days | Gate integrity | New integrity checks wired + passing, no priority ties |
| **3** | 3–5 days | M11 auto-staging | `close_session()` stages lessons, learning loop verified E2E |
| **4** | 1 day | Governance freeze, file hygiene | Freeze declared, AGENTS.md exists with validator |
| **5** | Weeks | Minimum Shippable Product | External user installs and talks to the engine |

**Total time to Phase 4 gate**: ~2 weeks.
**Total time to Phase 5 gate**: ~6–8 weeks from today.

---

*The engine is built. It's time to open the door.*
