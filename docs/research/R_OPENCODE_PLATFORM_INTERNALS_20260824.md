# R_OPENCODE_PLATFORM_INTERNALS_20260824

**AP Token**: AP-RESEARCHER-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_platform_internals ⬡ ACTIVE

**Date**: 2026-08-24 · **Task**: kg-resource-platform-research-20260824 (gaps G6–G9 + httpx2)
**Trigger**: 2026-08-24 incident record — dead CLI, nondeterministic `opencode db` pipe
truncation, compaction-threshold doctrine unverified.
**Protocol**: FP-04 T0 discipline — every claim tagged VERIFIED-MEASURED / VERIFIED-CITED / THEORY.
Companion doc: `R_RESOURCE_GOVERNANCE_20260824.md`.

---

## Executive Summary (L1)

`opencode db` **silently truncates piped output** — reproduced 5/5 runs: a 4.83MB query result
delivered complete via file redirect but cut at ~1.30MB ±20KB through a pipe, exit code 0,
empty stderr. This is silent data loss in a forensic tool and is upstream-bug-worthy. OpenCode
exposes **no session ID to wrapped processes** (only `OPENCODE_PID` + `OPENCODE=1`) — exact
wrapper attribution requires a feature request. The fleet's "85%-of-window auto-compact"
doctrine is **mechanically wrong but numerically coincidental**: official docs specify a
formula (`estimated > limit − max(output, buffer)`), not a percentage. Typer's lazy group
construction is confirmed at source level: `add_typer` only appends metadata; all Click
validation happens inside `app()` — so import-smoke gates MUST invoke `--help`. And `httpx2`
is not a mystery shim: it is Pydantic's maintained fork of httpx, pinned deliberately.

## Detailed Findings (L2)

### G6 — `opencode db` pipe truncation — behavior VERIFIED-MEASURED, mechanism THEORY

Environment: opencode 1.18.22, Ubuntu 25.10.

Reproduction matrix:

| Output path | Payload | Result |
|---|---|---|
| File redirect (`> file`) | 4,827,965 bytes | **complete**, exit 0 |
| Pipe (`| wc -c`) ×5 runs | same query | **1,290,203–1,315,259 bytes**, exit 0, stderr empty |
| Pipe, trivial output (14 bytes) ×10 | tiny | 10/10 intact |
| Redirect, trivial output ×10 | tiny | 10/10 intact |
| Pipe, larger payload (~≥4.8MB) | LIMIT 5000 | 3,319,695 bytes delivered |

Characterization:

1. **Silent**: exit 0, zero stderr on every truncated run. No warning distinguishes a cut
   stream from a complete one — the consumer cannot detect loss without external byte counts.
2. **Nondeterministic ceiling**: ~1.30MB ±20KB for one payload; 3.32MB for another. The cutoff
   scales with payload/runtime rather than sitting at a fixed buffer boundary (rules out a
   simple fixed-size buffer; consistent with an async pump cancelled near completion).
3. **Redirect-safe**: file-backed stdout receives full bytes — blocking fd writes flush;
   pipe backpressure interacts badly with whatever relay layer sits between sqlite and stdout.
4. Early transient: three rapid-fire redirected runs produced empty files once (later 10/10
   clean) — matches the incident record's "nondeterministic" framing; likely concurrent-DB-lock
   or startup race, distinct from the size-dependent truncation above.

Mechanism candidates (THEORY — source not inspected): (a) async copy goroutine/task cancelled
on process exit with pending buffered chunks dropped under pipe backpressure; (b) short-write /
EAGAIN handling bug in the relay when stdout is non-blocking. Distinguishing them requires
reading the opencode db command implementation.

**Verdict: upstream-bug-worthy = YES.** Silent data loss with exit 0 in a database inspection
tool is a correctness defect, not a UX quirk. Recommended report: minimal repro (any query
producing >2MB), version, "pipe delivers N of M bytes, redirect delivers M".

**Canonical rule until fixed** (codified from this incident): *never consume `opencode db`
output through a pipe*. Always stage to a temp file, then read/parse the file:

```bash
opencode db "SELECT ..." > /tmp/stage.json && python3 -c 'import json,sys; ...' < /tmp/stage.json
```

Byte-count verification (`wc -c` against expectation) is prudent for forensic-critical reads.

### G7 — Session-ID exposure to wrapped processes — VERIFIED-MEASURED (negative result)

Method: inspected the environment of a live opencode-wrapped bash process (this session's own
tool calls) — the most direct possible probe.

Findings:
- Present: `OPENCODE_PID=7129`, `OPENCODE=1`.
- Absent: any session ID variable (`OPENCODE_SESSION_ID`, etc.), IPC socket path, or hook
  payload carrying session identity into child processes.
- `opencode --help` / `opencode db --help`: no flag exposes current-session identity to
  subprocesses. (`opencode export [sessionID]` requires knowing the ID already.)

Consequence: our wrapper's set-diff attribution can only correlate via `OPENCODE_PID` → parent
process → DB heuristics ("most recently updated session owned by this PID"), which is exactly
the fragile inference FP-04 warns about. Exact attribution is impossible today.

**Feature-request case** (documented for filing): expose `OPENCODE_SESSION_ID` (and optionally
`OPENCODE_MESSAGE_ID`) to tool-subprocess environments. Precedent: CI systems expose
`GITHUB_RUN_ID`/`CI_JOB_ID` to build steps; the wrapper-attribution use case (provenance
forensics per mandate M22) is a strong consumer. Until shipped, PID+timestamp correlation stays
documented as APPROXIMATE, never cited as Tier-0 ground truth.

### G8 — Compaction threshold doctrine — MECHANISM VERIFIED-CITED; "85%" figure MYTH-PENDING-EVIDENCE

Official documentation (opencode.ai/v2/docs/compaction) states automatic compaction triggers
when:

```
estimated tokens > context limit − max(requested output tokens, buffer)
```

with defaults `buffer = 20000`, `keep.tokens = 15000`; estimation is heuristic
(JSON-serialize ÷ 4 chars/token). Source corroboration (sst/opencode `compaction.ts`,
`isOverflow`): `count > context − output` where output = min(model limit.output,
OUTPUT_TOKEN_MAX). Multiple community issues (#11314 et al.) describe a hardcoded percentage
variant historically and request configurable thresholds — indicating the mechanism has varied
across versions.

Assessment of our doctrine ("85% of window, ~160K/200K"):
- As a **mechanism claim** ("auto-compact fires at 85% of window"): **MYTH-PENDING-EVIDENCE**.
  No percentage threshold exists in current documented behavior.
- As an **arithmetic approximation**: for a 200K window with ~30–40K reserved for output+buffer,
  triggering lands near 160–170K ≈ 80–85%. The number was right for reasons we had wrong.

Doctrine correction to adopt: *"Auto-compaction fires when estimated request tokens exceed
context limit minus max(output allowance, 20K buffer) — approximately 80–85% on a 200K-class
window, but version- and model-dependent. Never plan around a fixed percentage."* Per FP-04,
sessions must not assume headroom past the formula's trigger point.

### G9 — typer/click lazy validation — VERIFIED-MEASURED + VERIFIED-CITED

Local repro (typer 0.25.1 installed in `.venv`):

```python
broken = typer.Typer()
@broken.command()
def vault_create(x: UndefinedModel): ...   # unresolvable annotation

app = typer.Typer()
app.add_typer(broken, name="vault")        # import + mount: SILENT success
app(["--help"])                            # NameError raised HERE
```

Source confirmation (typer/main.py, read via upstream mirror):
- `add_typer()` does nothing but `self.registered_groups.append(TyperInfo(...))` — pure
  metadata registration, zero construction.
- Click Group objects are built only by `get_group_from_info()`, reachable solely through
  `get_command()`, which is called only inside `Typer.__call__` — i.e., at `app()` invocation.
- Even `--help` forces full construction of every mounted group (help rendering needs the
  command tree).

Related upstream context: typer #243 / PR #1037 / PR #1052 document add_typer semantics
evolution (single-command flattening, name inference removal) — evidence the mount surface is
actively shifting, reinforcing that smoke tests must exercise real invocation, not import.

**Rule codified (validates the dead-CLI incident)**: an import-smoke gate of the form
`python -c "from omega.cli.oracle_cli import app"` catches module-level ImportErrors but NOT
group-construction errors. The gate MUST be `omega --help` (or `app(["--help"])` in-process),
which forces every registered sub-command group through Click construction. This is why council
step N1 specifies iterating `cli/*.py` imports AND the verdict separately demands the
`omega --help` tripwire — both are needed; neither substitutes for the other.

### httpx2 — identity resolved — VERIFIED-MEASURED (local metadata) + intentional

- Installed distribution: `httpx2 2.5.0` in `.venv`, METADATA shows Project-URL
  `https://github.com/pydantic/httpx2`, Author-email Tom Christie, Maintainer "Pydantic
  Services Inc.", BSD-3-Clause, depends on `httpcore2==2.5.0`.
- pyproject.toml:27 pins `"httpx2==2.5.0"` with comment "[Strike 7.1] Pydantic fork of httpx;
  API-compatible superset" (idna relaxed to ≥3.18 at line 29 specifically for it).
- Consumers: 5 test files (`test_providers.py`, `test_remote_provider_s3.py`,
  `test_hub_health.py`, `test_orchestrator.py`, `library/test_api_clients.py`) alias it as
  `import httpx2 as httpx`.

**Verdict: intentional dependency, not a local shim, not typosquatting-suspicious** — it is the
Pydantic-org-maintained continuation fork of encode/httpx. No action required; documenting here
so future audits don't re-litigate it.

## Sovereign Synthesis (L3)

> A platform is only as trustworthy as its failure honesty: opencode's db tool loses data
> silently (exit 0), its compaction folklore ran on a number whose reason was wrong, and its
> CLI framework defers every error to the moment you finally invoke — all three punish agents
> who trust surfaces instead of probing them. Stage outputs to files, verify doctrines against
> docs, and make smoke tests invoke, never merely import.

Priority order: (1) codify temp-file staging rule for all `opencode db` consumers, (2) upgrade
import-smoke gates to `--help` invocation (N1 alignment), (3) correct compaction doctrine
language in agent guidance, (4) file upstream issues: db pipe truncation + OPENCODE_SESSION_ID.

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ R_OPENCODE_PLATFORM_INTERNALS ⬡ 2026-08-24*
