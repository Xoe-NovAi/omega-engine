<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Decision Workspace Tools — Consolidated Implementation Specification
## Canonical T0+T1 Specification (Cross-Validated: Grok CLI + Web Claude)

**AP Token**: `AP-DECISION-TOOLS-IMPL-SPEC-v1.0.0`  
**Date**: 2026-07-19  
**Status**: **CANONICAL — Supersedes all prior scattered manuals for implementation purposes**  
**Authority Stack**:  
1. `SOVEREIGN_MANDATES.md` (non-negotiable law)  
2. **This specification** (what to build, in what order, how to know done)  
3. `docs/strategy/GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` (Conditional GO)  
4. `docs/research/WEB_RESEARCH_KNOWLEDGE_GAPS_20260719.md` (verified web claims)  
5. `docs/strategy/GROUNDED_MEDITATE_DECISION_WORKSPACE_20260718.md` (research background — do not over-build Corrections 3–6)  

**Source Documents Preserved (Historical Trail — Do Not Delete)**:
| Document | Role | Location |
|---|---|---|
| Grok CLI Decision Tools Review | Architecture review + Conditional GO | `docs/strategy/GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` |
| Web Claude V1 Manual (pre-Grok) | First implementation pass | `context_packs/decision-tools-review/pack-results/DECISION_TOOLS_MANUAL_20260719-WEB_CLAUDE-V1_BEFORE_GROK_REVIEW.md` |
| Web Claude V2 Manual (cross-validated) | Second pass with Grok convergence | `context_packs/decision-tools-review/pack-results/DECISION_TOOLS_MANUAL_20260719-WEB_CLAUDE-V2_AFTER_GROK_REVIEW.md` |
| Grok CLI Agent Implementation Manual | Sprint execution plan (5 workstreams) | `docs/strategy/AGENT_IMPLEMENTATION_MANUAL_20260719.md` |
| Dual-Review Retrospective | Process analysis + protocol fixes | `context_packs/decision-tools-review/pack-results/DUAL_REVIEW_RETROSPECTIVE_20260719.md` |
| Grok CLI Web Research | Claim verification + live codebase delta | `data/coordination/grok_cli/WEB_RESEARCH_KNOWLEDGE_GAPS_20260719.md` |

**Scope Guardrail**: Builds the *tools* that manage decisions. Does NOT ratify, review, or touch the 23 open content decisions (D-297, Tests vs WAL, etc.) — those are separate, out of scope.

---

## 0. EXECUTIVE SUMMARY — WHAT CHANGED FROM THE ORIGINAL SPEC

The original proposal (`GROUNDED_MEDITATE_DECISION_WORKSPACE_20260718.md`) had two hard blockers fixed in this spec:

1. **M2 Firewall violation, fixed.** The original schema embedded ANAi persona names (`Sekhmet`, `Brigid`, `Kali`, etc.) with numeric Belief-Engine parameters directly into engine-core code (`src/omega/governance/`). Per Mandate 2 and the M2 migration pattern in `HMC_QUAD_FORGE_IMPLEMENTATION_MANUAL_20260718.md` §2: "Engine defines Slots. WADs fill Slots. Engine never references WAD entities." This spec keys everything on `Slot` values (`P1`–`P10`, `LIGHT_OVERSOUL`, `DARK_OVERSOUL`, `GRAND_OVERSIGHT`) and resolves mythic names only at render time via the active WAD's overlay. **Do not write persona names into `src/omega/governance/decisions.py` or the decision schema.**

2. **7h estimate corrected to 9–11h honest.** The original T0 estimate (3h) bundled engine+schema+migration of 23 decisions into one number. Migration is its own effort. This spec splits T0 into T0a/T0b and gives each phase its own acceptance gate.

**Cross-Validation**: Two independent reviews (Grok CLI with native repo access + Web Claude with curated context pack + web search) converged on every load-bearing conclusion. Where they diverged, the divergence was a legitimate design-taste question (file format: frontmatter+body vs pure YAML) — both defensible. The asymmetric catches (Grok: algorithmic bugs; Web Claude: empirical library verification) are complementary and both folded into this spec.

---

## 1. FILE LAYOUT (Create Exactly This)

```
src/omega/governance/
  decisions.py              # DecisionEngine class — the only writer of decision files
  decision_schema.json      # JSON Schema (Draft 2020-12), single source of truth for validation

src/omega/cli/
  decision_cli.py           # Typer sub-app: omega decision {list,show,decide,graph,validate}

docs/decisions/
  schema/decision_v1.json   # Copy of decision_schema.json for reference
  catalog/                  # One file per decision: D0001.md, D0002.md, ...
    .locks/                 # Per-decision lock files (portalocker), gitignored
  SCHEMA_GUIDE.md           # Human-readable field reference generated from decision_schema.json

tests/
  test_decision_schema.py   # Schema validates against its own meta-schema + fixture round-trips
  test_decision_engine.py   # CRUD, atomic write, supersession, concurrent-lock contract tests
  test_decision_cli.py      # CLI contract tests (exit codes, --json output, --human-confirmed gating)

config/wads/_omega_default/decisions/
  slot_overlay.yaml         # Slot -> qualitative stance descriptor (IWAD default, no numeric params)

config/wads/arcana_novai/decisions/
  slot_overlay.yaml         # Slot -> {Sekhmet, Brigid, ...} display name mapping (PWAD, mythic names live HERE only)

Makefile
  # add target: decision-schema-check
```

**Rule that must never be violated**: Nothing under `src/omega/` may contain a WAD-specific proper noun (mythic entity name). If a name like "Sekhmet" needs to appear anywhere in engine-core code, tests, or the JSON Schema, that is an M2 violation — stop and route it through the WAD overlay files instead.

---

## 2. THE SCHEMA (T0a — Engine + Schema)

### 2.1 File Format: YAML Frontmatter + Markdown Body

Follow the `structured-madr` precedent validated in `grounding_part1.xml` §1: each decision is a single `.md` file, YAML frontmatter between `---` fences, free-text rationale/narrative below.

```markdown
---
schema_version: "1.0.0"
id: D0001
title: "Use sqlite-vec for unified session-state WAL"
type: adr
category: architecture
status: proposed
tags: [database, persistence, wal]
created: "2026-07-19"
updated: "2026-07-19"
proposer: kali
authority: human
drivers:
  primary: "Need a single durable store for handoffs, gnosis, lessons, checkpoints"
  secondary: ["Reduce write-path complexity", "Reuse existing sqlite-vec adapter"]
options:
  - id: sqlite_vec_unified
    label: "Single sqlite-vec WAL database"
    risk_assessment: { technical: low, schedule: low, ecosystem: low }
    consequences:
      positive: ["Single writer simplifies durability", "Reuses D-282 PRAGMA SSOT"]
      negative: ["Write serialization bottleneck at N concurrent agents"]
      neutral: ["Requires partition_key per entity"]
  - id: per_domain_files
    label: "Keep per-domain JSON files (status quo)"
    risk_assessment: { technical: low, schedule: low, ecosystem: medium }
    consequences:
      positive: ["No migration needed"]
      negative: ["No cross-domain query, split-brain risk"]
      neutral: []
chosen_option: null
decided_at: null
decided_by: null
rationale: null
decision_by: "2026-08-01"
supersedes: null
superseded_by: null
relationships:
  - type: blocks
    target: D0010
  - type: depends_on
    target: D0002
meditate_scaffold_ready: true
slot_ref: P2
evidence_refs:
  - "grounding_part2.xml#P2-BRIGID"
  - "research.xml#structured-madr"
---

## Context

Free-text narrative. This is where the human/agent writes the reasoning that doesn't
fit structured fields. Not validated by JSON Schema — validated only for presence
(non-empty) if `status != proposed`.

## Notes

Anything else.
```

**Why frontmatter + body, not pure YAML**: Pure-YAML decision files lose the ability to hold rich prose rationale without awkward multi-line YAML block scalars, and every ADR precedent surveyed (`adr-tools`, `structured-madr`, MADR) uses this exact split. Parse with `python-frontmatter` (`pip install python-frontmatter`) since it round-trips cleanly and handles edge cases (BOM, CRLF) that a manual `str.split('---', 2)` will not.

**Note for builders**: Grok CLI's review independently proposed pure YAML (`docs/decisions/catalog/D001.yaml`, no frontmatter split, no markdown body) instead. Both are defensible — pure YAML is simpler to parse and matches the project's existing config-file culture (`entities.yaml`, `lenses.yaml`); frontmatter+body matches the actual ADR tooling the research cites as precedent, and gives free-text rationale a natural home instead of forcing it into a YAML block scalar. **This spec's recommendation stands (frontmatter + `.md`)** because it's what the cited precedent actually does, but if the implementing agent finds `python-frontmatter` adds friction, switching to pure `.yaml` with a `body: |` block-scalar field is a same-day, low-risk substitution — it does not change the schema's field semantics, only the file's outer envelope. Pick one before T0a starts; don't let both formats coexist in the catalog.

### 2.2 Fields — What Changed from the Original Draft, Field by Field

| Field | Status | Note |
|---|---|---|
| `schema_version` | **NEW — required** | String, semver. Every decision file declares which schema version it was written against. Without this, you cannot safely migrate the format later. Bump this file's version in lockstep with `decision_schema.json`. |
| `id` | keep | Pattern `^D[0-9]{4}$`. Zero-padded to 4 digits from the start — 23 decisions today, but don't hardcode a 2-digit assumption. |
| `title`, `created`, `updated` | keep | `created`/`updated` are ISO 8601 dates (`YYYY-MM-DD`), not datetimes — this project's own docs use date-only stamps throughout. |
| `type`, `category`, `tags` | keep | `type` is a fixed const `"adr"` for now (future-proofs against non-ADR decision types later). |
| `status` | keep, enum extended | `proposed \| deliberating \| accepted \| superseded \| deprecated`. Added `deliberating` because MEDITATE T1-scaffold needs a state to mark "a `meditate` prompt has been rendered for this decision" distinct from `proposed`. |
| `authority` | keep | `human \| agent \| human_review`. Flat enum only — do **not** implement the full MAD-framework role structure (proposer/deliberator/decider/auditor) from the original doc's "Correction 6." That's T2 scope; building it now is scope creep the 9–11h budget cannot absorb. |
| `criteria` (weighted scoring) | **REMOVED from required schema** | Make this an optional, freeform `object` with no enforced sub-schema. Do not validate weights sum to 1.0, do not enforce a fixed criteria vocabulary. If nobody uses it, it costs nothing; if the schema enforces it, it becomes exactly the kind of stale, unmaintained ceremony that `grounding_part1.xml` Source 7 ("ADRs go stale") warns against. |
| `options[]` | keep, required if `status != proposed` is not enforced (options can be empty for early proposals) | `risk_assessment` and `consequences` sub-objects unchanged from the original draft — this part was already well-designed and matches `structured-madr` directly. |
| `chosen_option` | **NEW** | Nullable string, must match one of `options[].id`. Required non-null when `status == accepted`. This was missing from the original schema — without it, nothing records *which* option won. |
| `decided_at` | **NEW** | Nullable ISO date. Required non-null when `status in (accepted, deprecated)`. |
| `decided_by` | **NEW — [Grok catch]** | Nullable string, `agent_id` or `"human"`. Distinct from `proposer`: `proposer` is who *wrote the decision file*, `decided_by` is who *executed the accept*. These are frequently different agents in a 12+-agent fleet and collapsing them into one field loses provenance. |
| `rationale` | **NEW — [Grok catch]** | Nullable short string (not the full markdown body). A one-line "why this option won" that's cheap to scan in `list`/`show` output without opening the full narrative section. Required non-null when `status == accepted`. |
| `relationships[]` | keep | `type` enum: `blocks \| blocked_by \| supersedes \| complements \| depends_on`. |
| `supersedes` / `superseded_by` | **PROMOTED to top-level scalar fields**, in addition to appearing in `relationships[]` if desired | Nullable `D####` string. This is the one structural change from the original draft that matters most for CLI performance: `show D0024` needs O(1) access to walk the chain back to D0001, not a linear scan of a `relationships` array. Keep them redundant with `relationships[]` entries of type `supersedes`/`superseded_by` for graph rendering, but the CLI's chain-walk reads the scalar fields. |
| `meditate_scaffold_ready` | renamed from `meditate_ready` | Boolean. Renamed for clarity — this only means "a static MEDITATE prompt template can be rendered," not "MEDITATE has run" or "a verdict exists." |
| `slot_ref` | **replaces `persona_parameters` entirely** | Single nullable enum value: `GRAND_OVERSIGHT \| LIGHT_OVERSOUL \| DARK_OVERSOUL \| P1 \| P2 \| ... \| P10`. This is the M2-compliant replacement — see §5. |
| `persona_parameters` | **DELETED** | Do not implement this field in the engine schema. If T1-scaffold needs per-slot framing, it comes from the WAD overlay file (§5), never from the decision file itself. |
| `evidence_refs` | **NEW** | Array of strings, freeform (`"bundle_name.xml#section"` convention recommended but not enforced). Lets a decision point back at the research that justified it — matches the citation discipline already used throughout this project's own docs. |
| `proposer` | **NEW** | String, agent/entity name that created the file. Free text, not validated against a WAD entity list (that would itself be an M2 coupling — the engine schema shouldn't need to know what entities exist in any given WAD). |
| `decision_by` | keep | Nullable ISO date. **Display-only** in T0/T1 — see §6, no enforcement daemon. |

### 2.3 JSON Schema Meta-Rules

- Use **Draft 2020-12** (`jsonschema.Draft202012Validator`, package `jsonschema`, current on PyPI). Declare `"$schema": "https://json-schema.org/draft/2020-12/schema"` at the top of `decision_schema.json` explicitly — don't rely on the library's default-draft fallback, since an unpinned `$schema` means a future `jsonschema` upgrade could silently change which draft rules apply to your validation.
- Set `"additionalProperties": false` at the top level and on every nested object (`options[]` items, `consequences`, `risk_assessment`, `relationships[]` items). This is the "forbid-unknown" requirement from the review brief — it's what catches a typo'd field name (`autority` vs `authority`) at validation time instead of silently ignoring it forever.
- `required` at top level: `["schema_version", "id", "title", "status", "created", "authority"]`. Everything else is conditionally required via `if/then` (JSON Schema 2020-12 supports this natively):

```json
{
  "if": { "properties": { "status": { "const": "accepted" } } },
  "then": { "required": ["chosen_option", "decided_at", "decided_by", "rationale"] }
}
```

- Validate the schema file itself in CI: `Draft202012Validator.check_schema(json.load(open("decision_schema.json")))`. This catches a malformed schema before it silently stops validating anything.

---

## 3. THE DECISIONENGINE CLASS (T0a)

### 3.1 Location and Shape

`src/omega/governance/decisions.py`. A plain class, not a singleton, not a WAD-aware service — it takes a `catalog_dir: Path` in its constructor and knows nothing about entities, WADs, or slots beyond the `slot_ref` string it validates against the fixed `Slot` enum already defined in `src/omega/governance/slots.py`.

```python
import json
import anyio
import frontmatter          # pip install python-frontmatter
import portalocker          # pip install portalocker>=3.2
from pathlib import Path
from jsonschema import Draft202012Validator
from omega.governance.slots import Slot

class DecisionValidationError(Exception):
    """Typed error per Mandate 9 (Error Integrity) — never raise bare ValueError."""

class DecisionNotFoundError(Exception):
    pass

class DecisionEngine:
    def __init__(self, catalog_dir: Path, schema_path: Path):
        self.catalog_dir = catalog_dir
        self.locks_dir = catalog_dir / ".locks"
        self.locks_dir.mkdir(parents=True, exist_ok=True)
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)   # fail fast if schema itself is broken
        self._validator = Draft202012Validator(schema)

    async def read(self, decision_id: str) -> "Decision": ...
    async def list(self, status: str | None = None, tag: str | None = None) -> list["Decision"]: ...
    async def create(self, fields: dict, body: str) -> "Decision": ...
    async def decide(self, decision_id: str, option_id: str, human_confirmed: bool) -> "Decision": ...
    def _validate(self, fields: dict) -> None: ...
    def _atomic_write(self, path: Path, content: bytes) -> None: ...
    def _allocate_id(self) -> str: ...
    def _actor_id(self) -> str: ...
    def _today(self) -> str: ...
    def _path_for(self, decision_id: str) -> Path: ...
    def _read_sync(self, decision_id: str) -> "Decision": ...
    def _serialize(self, fields: dict, body: str) -> bytes: ...
```

### 3.2 Atomic Writes — Exact Pattern to Use

`atomicwrites` (the PyPI package once suggested for this kind of thing) was **archived by its upstream author in 2022** and formally deprecated from downstream package repositories in 2025, with upstream's own guidance being "use `os.replace`/`os.rename` instead." **Do not add `atomicwrites` as a dependency.** Roll the four-line pattern yourself:

```python
import os
import tempfile

def _atomic_write(self, path: Path, content: bytes) -> None:
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent,          # MUST be same directory as target — same filesystem is required for os.replace to be atomic
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())   # forces kernel to write to disk before the rename is visible
        os.replace(tmp_path, path)  # atomic on POSIX; MoveFileEx-based on Windows via os.replace's ctypes fallback
    except Exception:
        os.unlink(tmp_path)        # clean up the temp file if anything above failed
        raise
```

Three things that matter and are easy to get wrong:
1. **The temp file must be created in the same directory as the target**, not `/tmp` — `os.replace` is only atomic when source and destination are on the same filesystem, and a container's `/tmp` may be a different mount than `docs/decisions/catalog/`.
2. **Call `f.flush()` then `os.fsync(f.fileno())` before `os.replace`** — without the fsync, the rename can complete while the actual file content is still sitting in a kernel buffer, so a crash between rename and buffer-flush can leave you with a zero-length or truncated file even though the rename itself succeeded.
3. Because this is Mandate-1 (AnyIO Absolute) territory, wrap the actual call site in `anyio.to_thread.run_sync(self._atomic_write, path, content)` from the `async def create()`/`decide()` methods — `_atomic_write` itself stays a plain synchronous function (blocking file I/O has no business being `async def`), and AnyIO pushes it off the event loop.

### 3.3 Locking — Exact Library and Pattern to Use

Do not hand-roll `fcntl`/`msvcrt` branching. Use **`portalocker`** (`pip install portalocker`, current major version 3.x, actively maintained, explicitly cross-platform for Windows/Linux/BSD/macOS — unlike raw `fcntl` which is POSIX-only and would silently break if this ever runs on a contributor's Windows machine). Portalocker's `Lock` context manager takes a `timeout` directly, which gives you a clean way to fail fast instead of hanging:

```python
async def decide(self, decision_id: str, option_id: str, human_confirmed: bool) -> "Decision":
    decision = await self.read(decision_id)
    if decision.authority == "human" and not human_confirmed:
        raise DecisionValidationError(f"{decision_id} requires --human-confirmed")

    lock_path = self.locks_dir / f"{decision_id}.lock"

    def _do_decide():
        with portalocker.Lock(str(lock_path), timeout=5, mode="w") as _:
            # re-read inside the lock — another agent may have superseded it
            # while we were waiting for the lock
            current = self._read_sync(decision_id)
            # [Grok catch] Idempotency: decide() is only valid on a HEAD-of-chain
            # record. Reject anything that isn't proposed/deliberating explicitly
            # — don't just special-case "superseded". An already-accepted decision
            # must be re-opened via an explicit new supersession, not silently
            # re-decided, or you get two "accepted" records for one question.
            if current.status not in ("proposed", "deliberating"):
                raise DecisionValidationError(
                    f"{decision_id} has status={current.status!r}; decide() only "
                    f"operates on proposed/deliberating records. To change an "
                    f"accepted decision, supersede its current head instead."
                )
            if option_id not in {o["id"] for o in current.fields.get("options", [])}:
                raise DecisionValidationError(f"option {option_id!r} not found in {decision_id}.options")
            new_id = self._allocate_id()   # see id-allocation note below — locked separately
            new_fields = {**current.fields, "id": new_id, "supersedes": decision_id,
                          "status": "accepted", "chosen_option": option_id,
                          "decided_by": self._actor_id(), "decided_at": self._today()}
            self._atomic_write(self._path_for(new_id), self._serialize(new_fields, ""))
            updated_current = {**current.fields, "status": "superseded", "superseded_by": new_id}
            self._atomic_write(self._path_for(decision_id), self._serialize(updated_current, current.body))
            return new_id

    new_id = await anyio.to_thread.run_sync(_do_decide)
    return await self.read(new_id)
```

**Re-read inside the lock, not before it.** This is the one concurrency bug that will actually happen with 12+ agents in the fleet (`engine_state.xml` §2): agent A reads D0001 as `proposed`, agent B acquires the lock first and supersedes it to D0024, then agent A acquires the lock and — if it trusted its stale pre-lock read — would supersede an already-superseded decision, creating two competing successors. The fix is cheap: re-read the file *after* acquiring the lock, immediately before mutating.

**ID allocation has its own race condition — separate from the per-decision lock above.** `_allocate_id()` (reading the catalog directory for the current max `D####` and returning max+1) must **not** just scan the directory unlocked: two agents calling `decide()` on two *different* source decisions at the same moment can both scan the catalog, both see the same max id, and both write `D0025`, silently clobbering one of them via `os.replace`. Guard allocation with its own lock file, separate from the per-decision locks, e.g. `docs/decisions/catalog/.locks/_id_allocator.lock`, and hold it only for the scan-and-reserve step (not the whole `decide()` call):

```python
def _allocate_id(self) -> str:
    alloc_lock = self.locks_dir / "_id_allocator.lock"
    with portalocker.Lock(str(alloc_lock), timeout=5, mode="w"):
        existing = [int(p.stem[1:]) for p in self.catalog_dir.glob("D[0-9][0-9][0-9][0-9].*")]
        next_n = (max(existing) if existing else 0) + 1
        return f"D{next_n:04d}"
```

This is cheap (a directory glob + a lock acquire/release, not a full write), and it's the difference between "23 decisions" and "23 decisions, one of which silently vanished because two agents raced the allocator." Write a contract test for this specifically: spawn two concurrent `decide()` calls on two different source decisions and assert both successor ids are distinct and both files exist.

### 3.4 Supersession Is the Only Mutation Path

Never open an existing decision file and rewrite fields in place except for the two specific, narrow cases above: (a) `status: proposed → superseded` + setting `superseded_by`, and (b) creating the new successor file. Every other field change — editing a typo in `title`, adding an `evidence_refs` entry — should also go through `decide`-style supersession once a decision has left `status: proposed`. While `status == proposed`, direct in-place edits (still via `_atomic_write`, still through the lock) are fine, since nothing has been decided yet and there's nothing to preserve immutably.

---

## 4. CLI (T1-core + T1-graph)

### 4.1 Typer Wiring

Follow the exact pattern the project's own `oracle_cli.py` already uses (per `engine_state.xml` §3, "Typer CLI"). Register as a sub-Typer, not a flat top-level command list:

```python
# src/omega/cli/decision_cli.py
import typer
decision_app = typer.Typer(help="Manage decision records")

@decision_app.command("list")
def list_decisions(
    tier: str = typer.Option(None, help="Filter by slot_ref, e.g. P0-P10"),
    status: str = typer.Option(None, help="proposed | deliberating | accepted | superseded | deprecated"),
    tag: str = typer.Option(None, help="Filter by tag"),
    overdue: bool = typer.Option(False, "--overdue", help="Filter to decision_by < today AND status == proposed"),
    meditate_ready: bool = typer.Option(False, "--meditate-ready", help="Filter to meditate_scaffold_ready: true"),
    json_out: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
): ...

@decision_app.command("show")
def show_decision(decision_id: str, json_out: bool = typer.Option(False, "--json")): ...

@decision_app.command("decide")
def decide_decision(
    decision_id: str,
    option: str = typer.Option(..., "--option"),
    human_confirmed: bool = typer.Option(False, "--human-confirmed"),
): ...

@decision_app.command("validate")
def validate_decisions(
    decision_id: str = typer.Argument(None, help="Specific decision to validate, or all if omitted"),
    json_out: bool = typer.Option(False, "--json"),
): ...

@decision_app.command("graph")
def graph_decisions(
    focus: str = typer.Option(None, "--focus"),
    depth: int = typer.Option(2, "--depth"),
    color: bool = typer.Option(False, "--color"),
): ...

# src/omega/cli/oracle_cli.py  (wherever the root Typer app is assembled)
from omega.cli.decision_cli import decision_app
app.add_typer(decision_app, name="decision")
```

This gives you `omega decision list`, `omega decision show D0001`, etc. for free — no custom argument-parsing needed, and it matches the existing `app.add_typer(sub.app, name="...")` idiom the project already uses elsewhere for `db`/`items`-style command groups.

### 4.2 Command-by-Command Spec

**`omega decision list [--tier PX] [--status S] [--tag T] [--overdue] [--meditate-ready] [--json]`**  
Default output: a plain table (id, title, status, slot_ref, decision_by). `--json` emits an array of full decision objects. Exit code 0 always (empty result is not an error — print "No decisions match." to stderr, empty array to stdout if `--json`). `--overdue` (**[Grok catch]**) filters to `decision_by < today AND status == proposed` — this is the cheap, correct substitute for a deadline-enforcement daemon: same information, no background process, no Hivemind alert plumbing to build and maintain. `--meditate-ready` filters to `meditate_scaffold_ready: true`, useful for an agent scanning "what's ready for a MEDITATE pass."

**`omega decision validate [--all | DECISION_ID]`** — **[Grok catch, add this]**  
Runs the JSON Schema over one decision or the whole catalog and reports pass/fail per file, without mutating anything. This is a ~30-minute addition on top of the validator you already built for `create`/`decide`, and it's the single highest-ROI command for T0b migration: run `omega decision validate --all` after every migration batch instead of discovering a malformed file only when `list`/`show` chokes on it later. Exit code 0 if all pass, 1 if any fail (with per-file error detail to stderr).

**`omega decision show D0001 [--json]`**  
Prints the full decision, including a rendered supersession chain if `supersedes`/`superseded_by` is non-null: `D0001 (superseded) → D0024 (accepted)`. Walks the scalar fields (§2.2), not the `relationships[]` array. Exit code 1 if the id doesn't exist, with a message to stderr — never print a Python traceback to a human-facing CLI.

**`omega decision decide D0001 --option amend [--human-confirmed]`**  
Per §3.3. If `authority: human` and `--human-confirmed` is absent, exit code 2 (distinct from the "not found" exit code 1, so scripts/handoffs can distinguish "you didn't confirm" from "the id is wrong") with a clear stderr message. On success, print the new decision's id to stdout (so it can be captured: `NEW_ID=$(omega decision decide D0001 --option amend --human-confirmed)`).

**`omega decision graph [--focus D0001] [--depth 2] [--color]`**  
Renders all five relationship types (`blocks`, `blocked_by`, `supersedes`, `complements`, `depends_on`) as ASCII, not just blocking edges — this was explicit in the original spec's Correction 4 and is worth keeping. Plain ASCII by default (per the review: this output gets embedded in Hivemind handoff packets and CI logs, where ANSI color codes just show up as garbage `\x1b[...]` sequences). `--color` opts into ANSI for interactive terminal use. **Detect cycles before rendering** (`depends_on`/`blocks` edges that loop back on themselves via a hand-authored decision file are a real possibility once >20 files exist) — a plain DFS visited-set check is enough; on detection, print the cycle path to stderr and exit non-zero rather than looping forever or silently truncating the graph.

### 4.3 Exit Codes (Contract, Not Suggestion)

Agents and CI scripts branch on these — treat them as part of the API, not an afterthought:

| Code | Meaning | Commands |
|---|---|---|
| `0` | Success (including "list returned zero rows") | all |
| `1` | Decision id not found, or `validate` found ≥1 schema failure | `show`, `decide`, `validate` |
| `2` | `authority: human` decision missing `--human-confirmed` | `decide` |
| `3` | Schema/engine failure — malformed `decision_schema.json` itself, lock timeout, or attempted `decide` on a non-`proposed`/`deliberating` record (§3.4 idempotency fix) | `decide`, engine startup |

Never let an unhandled Python exception surface as a raw traceback to stdout/stderr in the CLI layer — catch `DecisionValidationError`/`DecisionNotFoundError` at the Typer command boundary and map to the codes above (this is also Mandate 9, Error Integrity, in practice, not just UX polish).

### 4.4 What NOT to Build in T1

- No `--watch` / live-reload mode.
- No deadline-enforcement daemon reading `decision_by` and firing alerts — `decision_by` is a **read-only "days remaining" column** in `list`/`show` output for T0/T1, nothing more. A real enforcer belongs with the Anubis TTL-enforcer pattern already scoped as its own phase in `grounding_part2.xml` P9 — don't duplicate that infrastructure inside the decision CLI.
- No interactive `decide` wizard (prompt-driven option selection). Flags only for T1; a TUI wizard is a T2+ nicety.

---

## 5. MEDITATE T1-SCAFFOLD (Static Template Only — No BE Math)

### 5.1 Why the Original Design Doesn't Work as Specified

The Belief Engine paper (`arXiv:2605.15343v1`, verified in `grounding_part2.xml`) validates numeric `uptake`/`anchoring` parameters inside an **iterative, multi-turn belief-update loop**: extract arguments → judge evidence → update structured memory → update belief state (this is where the log-odds math with `u`/`a` actually executes) → compose response. Omega's MEDITATE, by the project's own architecture (`grounding_part1.xml`'s Belief-Engine-to-MEDITATE mapping table), is a **single-inference, sequential persona immersion inside one oracle call**. There is no loop in which a numeric float gets iteratively applied. Handing the model a JSON blob of `{uptake: 0.4, anchoring: 0.7}` in a single-shot prompt doesn't invoke belief-engine math — it's a number the model reads once and can only use as a vague qualitative hint, which is what a plain adjective would have done just as well, without borrowing false rigor from a paper whose actual mechanism isn't present.

### 5.2 What T1-Scaffold Actually Builds

A static Jinja2 (or plain f-string, no need for a templating engine at this scale) prompt template that:

1. Reads `slot_ref` from the decision file.
2. Looks up that slot in the **active WAD's** `config/wads/<iwad>/decisions/slot_overlay.yaml` — not in the decision file itself — to get a qualitative stance descriptor and (for a PWAD like `arcana_novai`) a display name.
3. Renders the decision's title, drivers, options, and consequences into a prompt, with the slot's qualitative framing prepended.
4. Prints the rendered prompt to stdout (or writes it to a file) for a human/agent to paste into an actual MEDITATE session. **T1-scaffold does not call the oracle. It does not run inference.** That's explicitly deferred — building the auto-invocation now means building against an integration point (`Oracle.talk()`/`summon()`) that isn't part of this review's scope and risks scope-creeping a 1h task into a multi-day one.

`config/wads/_omega_default/decisions/slot_overlay.yaml` (IWAD default — engine-native, no mythic names):
```yaml
P1: { stance: "anchored in infrastructure reality, evidence-responsive on deployment risk" }
P2: { stance: "anchored on data-integrity concerns, receptive to durability evidence" }
# ... P3-P10, LIGHT_OVERSOUL, DARK_OVERSOUL, GRAND_OVERSIGHT
```

`config/wads/arcana_novai/decisions/slot_overlay.yaml` (PWAD overlay — mythic names live HERE, never in engine code):
```yaml
P1: { display_name: "Sekhmet", stance: "anchored in infrastructure reality, evidence-responsive on deployment risk" }
P2: { display_name: "Brigid", stance: "anchored on data-integrity concerns, receptive to durability evidence" }
# ...
```

This is the direct, correct application of the M2 pattern already proven in `HMC_QUAD_FORGE_IMPLEMENTATION_MANUAL_20260718.md` §3 for meditate lenses generally (`_omega_default/meditate/lenses.yaml` base + `arcana_novai/meditate/overlay.yaml` mapping) — decision-tools T1-scaffold should reuse that exact base+overlay resolution mechanism, not invent a parallel one.

### 5.3 Deferred to T2 (Do Not Build Now)

Full Belief-Engine-parameterized iterative deliberation, automatic oracle invocation, and verdict extraction back into `chosen_option`. T2 is already gated in the original doc behind "decision count > 50 or stalled > 2 weeks" — leave it there.

---

## 6. MIGRATION (T0b)

### 6.1 Two-PR Strategy — Do Not Combine

**PR 1**: `DecisionEngine` + `decision_schema.json` + CLI + tests, with **zero decision files migrated**. Merge this first, fully tested, fully gated by `make decision-schema-check` (§7), before touching a single one of the 23 existing decisions.

**PR 2**: Migration of the 23 decisions currently described in prose across `engine_state.xml`, `implementation.xml` (`SOVEREIGN_ARK_BLUEPRINT.md`), and `PIVOT_LOG.md` into the new format.

Reasons to split, not bundle: (1) PR 1 is independently testable and revertable without touching content; (2) migrating 23 real decisions surfaces schema gaps (a decision that doesn't cleanly fit `options[]`, a status that doesn't map cleanly to the five-value enum) that are much cheaper to fix *before* the schema is locked than after; (3) it matches the "build from pain, not speculation" principle the source docs already invoke — don't guess what the schema needs to hold before you've tried pouring the real data in.

### 6.2 Migration Mechanics

- During PR 2, set `"additionalProperties": true` temporarily on the schema (or run a `--lenient` validation mode) so imperfect first-pass migrations don't block on cosmetic mismatches. Tighten back to `false` once all 23 decisions validate cleanly under the strict schema, as a final step of PR 2 before merge.
- Every migrated decision gets `evidence_refs` pointing back at the source document it was extracted from (e.g., `evidence_refs: ["engine_state.xml#section-D-298"]`) — this preserves the citation trail instead of losing it in the migration.
- Do not hand-write all 23 by hand from scratch. Write one small one-off script (not part of the shipped `DecisionEngine` API) that parses the existing markdown tables in `engine_state.xml`/`implementation.xml` and pre-fills a first-draft frontmatter block per decision; a human/agent then reviews and fills in `options`/`consequences` where the source prose didn't already structure them clearly. Delete the one-off script after migration — it's not a maintained tool.

---

## 7. VALIDATION GATE (Makefile Target)

Add to the `Makefile`, matching the existing gate pattern (`firewall-check`, `mandate-amendment-check`, `kernel-import-check` per `engine_state.xml` §2):

```makefile
decision-schema-check:
	@echo "🔱 Decision Schema Gate"
	python -c "import json; from jsonschema import Draft202012Validator; \
		Draft202012Validator.check_schema(json.load(open('src/omega/governance/decision_schema.json')))"
	pytest tests/test_decision_schema.py tests/test_decision_engine.py tests/test_decision_cli.py -v
```

And wire it into `temple-grade` alongside the other gates already listed in `engine_state.xml` §2's ratified-protocol table.

---

## 8. CORRECTED SCHEDULE AND AGENT ASSIGNMENT

| Phase | Scope | Hours | Suggested Owner | Acceptance Gate | Priority |
|---|---|---|---|---|---|
| **T0a** | `decision_schema.json` + `DecisionEngine` (read/list/create/decide) + atomic writes + portalocker locking + id-allocator lock (§3.4) | 2h | Roc (established the M2-pattern template in Phase A of the HMC manual — reuse that muscle memory) | `pytest tests/test_decision_engine.py` green; concurrent-decide contract test (two threads racing `decide` on the same id) passes without producing two successors; concurrent-`decide`-on-different-ids test proves no id collision | **Definition of done — non-negotiable** |
| **T0b** | Migrate 23 decisions, two-PR strategy per §6, validated via `omega decision validate --all` | 2.5h | Researcher (already owns Phases B–E of the M2 migration — same "extract from prose, restructure to schema" skill) | All 23 files validate under strict schema (`additionalProperties: false`); `evidence_refs` populated for each | **Definition of done — non-negotiable** |
| **T1-core** | CLI `list/show/decide/validate` + supersession-chain display | 3h | Researcher or Roc (whichever finishes T0 first) | `pytest tests/test_decision_cli.py`; exit codes 0/1/2/3 verified per §4.3's table | **Definition of done — non-negotiable** |
| **T1-graph** | `graph` command, all 5 relationship types, plain-ASCII default, cycle detection | 0.5–1.5h (deadline enforcer explicitly cut, see §4.4 — use `list --overdue` instead) | same | Manual smoke test: 5-node graph with mixed relationship types renders without truncation; cycle test triggers non-zero exit, not a hang | **Stretch — cut first if the sprint is running long** |
| **T1-scaffold** | Static MEDITATE prompt template, slot-keyed, no numeric BE params | 1–2h | Whoever built the `arcana_novai/meditate/overlay.yaml` resolver in HMC Phase A (same resolution logic, new overlay file) | Rendered prompt contains zero numeric `uptake`/`anchoring` values; `grep -r "Sekhmet\|Brigid\|Prometheus" src/omega/` returns nothing | **Stretch — cut second, or push to next sprint** |
| **Total** | | **9h target, 9–11h realistic range** | | | |

**Stretch-goal framing is deliberate, not padding.** Both independent reviews (§0.1) agree T0+T1-core is the actual definition of done for this sprint; T1-graph and T1-scaffold are valuable but should not be allowed to compress T0a/T0b's quality bar to fit the clock. If the sprint is running long at the T1-core checkpoint, ship T0+T1-core alone and open T1-graph/T1-scaffold as a fast-follow — don't rush the schema/migration to make room for the graph command.

**Hard stop, unchanged from the original doc**: do not begin T2 (full BE verdict extraction, automatic oracle invocation) until decision count exceeds 50 or the T1 workflow has stalled for 2+ weeks. This spec only covers T0+T1.

---

## 9. MANDATE COMPLIANCE CHECKLIST (Verify Before Merge)

| Mandate | Check |
|---|---|
| **M1 AnyIO Absolute** | `grep -rn "asyncio" src/omega/governance/decisions.py src/omega/cli/decision_cli.py` returns nothing; all blocking I/O wrapped in `anyio.to_thread.run_sync` |
| **M2 Engine-Stack Firewall** | `grep -rEn "Sekhmet\|Brigid\|Prometheus\|Saraswati\|Inanna\|Ereshkigal\|Lucifer\|Hecate\|Anubis" src/omega/` returns nothing. Mythic names exist only under `config/wads/arcana_novai/` |
| **M9 Error Integrity** | No bare `except:`; `DecisionValidationError`/`DecisionNotFoundError` are typed subclasses, tests cover each raise path with `pytest.raises(...)` |
| **M13 Temple-Grade** | `decision-schema-check` wired into `make temple-grade` |
| **M16 Modularization** | No hardcoded absolute paths in `decisions.py` — `catalog_dir` passed in via `config_resolver`, not literal strings |
| **M21 Gate Integrity** | Contract test asserts `isinstance(engine.read(...), Decision)` — not a mock returning a dict/tuple |
| **M23 Failure Integrity** | If `decision_schema.json` fails `check_schema()` at engine startup, raise immediately — do not silently fall back to unvalidated writes |

---

## 10. SECONDARY RISKS FROM CROSS-REVIEW (Now Closed)

Grok's review flagged three secondary risks it didn't have room to fully spec mitigations for. All three are now closed with concrete fixes in this spec — listed here so builders can verify each is actually implemented, not just acknowledged:

| Risk (Grok's framing) | Status | Where it's fixed in this spec |
|---|---|---|
| "id collision without allocator" | **Closed** | §3.4, `_allocate_id()` under its own `_id_allocator.lock`, with a required contract test for concurrent cross-decision `decide()` calls |
| "relationship cycles in graph without cycle detection" | **Closed** | §4.2, DFS visited-set check before rendering, non-zero exit on detection |
| "docs-tree write friction (pre-commit doc rules)" | **Open — verify locally** | Not addressed here because it's environment-specific. Before T0b migration, run a throwaway `git commit` of one migrated decision file through the existing pre-commit hooks (secret detection, doc-format linters per `git-filter-repo`/pre-commit tooling referenced in the project's tool list) to confirm the frontmatter+`.md` format doesn't trip a doc-format rule expecting pure prose. Cheap to check, expensive to discover mid-migration. |

---

## 11. ONE-LINE SUMMARY FOR HANDOFF PACKETS

> Build T0a (schema + engine, Roc) and T0b (migration, Researcher) in parallel where possible, then T1-core is the real finish line — T1-graph/T1-scaffold are stretch, cut first if time runs short. Slot-keyed, not persona-keyed — mythic names live only in the `arcana_novai` overlay file, never in `src/omega/`. No numeric Belief-Engine math in T1-scaffold — static template only. `decide()` only operates on proposed/deliberating records, with its own id-allocator lock separate from the per-decision lock. Budget 9h target, 9–11h realistic — this range is now confirmed by two independent reviews (Web Claude + Grok CLI), not just one. Two-PR migration, not one.

---

⬡ OMEGA ⬡ CONSOLIDATED SPEC ⬡ CROSS-VALIDATED GROK+WEB CLAUDE ⬡ 2026-07-19