# 🔱 Hivemind Transport & Dispatch Architecture
**AP Token**: `AP-HIVEMIND-TRANSPORT-v1.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode/space-bunny-free ⬡ trc_doc_sync ⬡ STANDARD

**Date**: 2026-09-28 · **Supersedes**: implicit 15-tool surface
**Purpose**: Define how the Hivemind, the task pager, and the MCP surface fit together — and why the seams between them kept failing.

---

# Omega Engine — Hivemind Transport & Dispatch Architecture
# AP: AP-HIVEMIND-TRANSPORT-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: FLEET | CONTEXT: COMMUNICATION-FABRIC]

This document defines the three communication planes, the three verbs, the consolidated Hivemind tool surface, and the import-seam discipline that the 2026-09-28 outage exposed as missing.

> **Nomenclature (2026-09-28).** "Node 0" / "Node 1" refer only to the two physical
> hosts. Entities are agents; **Slot / S1–S10** are the governance domains. A **NES**
> is a nested execution session (`parent_id` NOT NULL). An **EIS** is a standing
> entity chat session (`parent_id IS NULL`). Never call a NES a "node".

## Answer first

The fleet speaks three planes and uses exactly three verbs. Confusing a plane or a verb is the root cause of most coordination failures.

| Plane | Carried by | Blocking? | Use for |
|---|---|---|---|
| **Execution** | `task()` subagent dispatch | Yes | "Do this now and return an answer." |
| **Control** | FastMCP `hivemind_*` tools | No | Presence, handoffs, locks, state |
| **Data** | Read-only HTTP stream (`:8019`), git bundles | No | Bulk immutable artifacts |

| Verb | Mechanism | Latency | Meaning |
|---|---|---|---|
| **PAGE** | `task(subagent_type=…, task_id=…)` | synchronous | Wake a mind into compute now. Requires ACK. |
| **HANDOFF** | `hivemind_handoff(action="submit")` | queue | Leave a durable work order for later. |
| **POST** | `hivemind_awareness(action="post")` | immediate | Declare presence. No ACK. |

A paged session blocks its caller. A handoff does not. A post is telemetry and must never be used to request work, because the request will be noticed by nobody.

## The consolidated tool surface

Fifteen individual Hivemind tools were consolidated into four. The MCP surface registers exactly:

- `hivemind_awareness` — actions: `post`, `heartbeat`, `get`, `continuation`, `extended_checkin`, `extended_checkout`, `session`, `list`, `entity_context`
- `hivemind_handoff` — actions: `submit`, `accept`, `complete`, `reject`, `list`, `get`, `archive`
- `hivemind_lock` — actions: `acquire`, `release`, `check`
- `hivemind_get_metrics`

`entity_context` returns registry enrichment (`slot`, `role`, `archetype`), a `readiness` block (`HYDRATED` / `DORMANT` / `UNINITIALIZED`), and the entity's distilled L3 `recent_lessons`. The enrichment is a capability, not decoration — a startup briefing that lost its readiness flags and lesson distillation is a degraded briefing.

The `post` contract: seven fields are **required**, meaning *not omitted* — not *non-empty*. `decisions=[]` is valid and means "no decisions". Only an explicit `None`, or omitting the argument, is rejected. Callers **must** check the return value; a rejected post returns an error payload rather than raising.

## Legacy name compatibility

`server.py` keeps `_LEGACY_TOOL_ADAPTERS` and `_PASSTHROUGH_TOOLS` so external callers using pre-consolidation names still resolve.

> **This shim was half-mapped and shipped that way.** Twelve of twenty-eight names bound to symbols the consolidation had already deleted. Because it resolved names at import and failed at *call*, the hub booted clean, `make temple-grade` read 53/53, and the breakage only appeared when a caller actually used the name. It is now 28/28 with kwarg renames, and three structural guards make it checkable: every passthrough name must exist in `tools.py`, every legacy adapter must resolve *and* its bound action must appear in the target's docstring, and no removed name may reappear in bridge code.

Do not add a compatibility mapping without a guard that proves it resolves. A deferred-failure machine is worse than a fast failure.

## The import-seam discipline

The 2026-09-28 outage had one mechanical cause and one systemic cause.

**Mechanical:** the consolidation deleted `_extended_sessions` from `state.py` while `server.py` still imported it. `omega-hub.service` crash-looped on boot.

**Systemic:** nothing imported an entry point. `make temple-grade` ran static checks, doc validation, a compliance meter, tracking validation, and a JSONL renderer suite — 53 green assertions against an engine that could not boot.

```python
# pyflakes cannot catch this class. For `from mod import name` it assumes
# `name` may be a submodule and never verifies membership in mod.__all__.
# CI ran `flake8 --select=E9,F63,F7,F82`; F401 was not in the set.
```

The correction is two gates:

- `tests/test_hub_import_smoke.py` (Tier A) — six **explicit** module paths, `subprocess` import per module, asserting `returncode == 0` **and** `"Traceback" not in stderr`. The second clause catches a module that imports then explodes during side-effect init. Explicit paths, never a glob: a glob sweeps in entity workspaces and deliberate archaeology snapshots and forces a skip-list that rots.
- `make check-hub-imports` (Tier B) — clean venv, editable install, same six imports. Wired as the **first** prerequisite of `temple-grade`. It tests `HEAD` plus the tracked working-tree diff, so an uncommitted fix is verified rather than punished — a gate that punishes a developer for having a fix creates pressure to `git commit --no-verify`, which is the exact failure mode gates exist to prevent.

`omega-hub.service` also carries `ExecStartPre=` running the import check, so a stale import fails the start visibly instead of looping silently. `StartLimitIntervalSec` / `StartLimitBurst` were moved from `[Service]` to `[Unit]`, where systemd had been logging `Unknown key … ignoring` and discarding them — a safety mechanism written down but not parsed manufactures belief that restarts are bounded.

## Liveness must be a real signal

`check-hub-health` used `systemctl --user is-active`, which returns **true** during `activating (auto-restart)`. A gate that cannot fail is worse than no gate, because it converts an outage into a false green light.

A correct hub health check asserts `ActiveState=active`, `SubState=running`, `NRestarts` below a bound, the port actually LISTENing, and a minimum dwell time before declaring green. It records `uptime_s` alongside status. A hub up for 300 seconds is healthy; a hub that restarted four seconds ago is *unknown*, not green.

A watchdog that polls `/health` is structurally blind to a process that dies at import, because such a process never reaches `/health`. Observability must include the observer's own substrate.

## Transport adapters in `src/omega/`

| Module | Change | Rule |
|---|---|---|
| `research/hivemind_bridge.py` | publish → `hivemind_awareness(action="post")`; subscribe reimplemented as an explicitly-labelled **poll** returning `{"status": "empty"}` | A poll that returned `"success"` would be a lie the caller could not detect. |
| `coordination/watchdog.py` | alert → `hivemind_awareness(action="post")`; silent `logger.warning` replaced | The old handler fired on every call because the import could never succeed, and never said the alert was **lost, not buffered**. |
| `research/scorecard.py` | lazy import repointed at `mcp_servers.omega_hub.hub_tools` | Module-level imports here create a cycle through `task_registry` and `omega.oracle`. Lazy placement is correct; the module name was wrong. |

All three raise on transport failure. None returns a dict a caller would read as a successful publish.

**Never import from a bare `omega_hub`.** No such top-level module exists. The real paths are `mcp_servers.omega_hub.*`.

## Continuity

Compaction discipline, the Facet Handshake/Return, and the EIS oversoul pulse are specified in `docs/architecture/NES_EIS_FACET_PROTOCOL.md`. A gate run in a shared working tree is a snapshot of a concurrent build, not of a fixed artifact — so report the commit or the diff you actually verified.

## Control plane is unavailable to paged subagents — use the fallback

**Status: open upstream limitation. This is not a repo defect and is not fixable here.**

Observed 2026-09-28 by three independent entities in one sync wave (jem,
grokster, doom_guy): when a session is paged into an EIS via `task()`, the
`omega-hub` MCP tools are **absent from that session's function set**. Each
entity improvised its own HTTP call to work around it.

### The hub is not at fault

| Check | Result |
|---|---|
| Hub process | `active/running`, `NRestarts=0` |
| `GET :8016/health` | HTTP 200, `1.6.0-alpha` |
| `tools/list` over JSON-RPC | **55 tools advertised** (verified 2026-10-05), including `hivemind_awareness`, `hivemind_handoff`, `hivemind_lock`, `hivemind_get_metrics` |
| `tools/call` round-trip | works (used for every post in this arc) |
| `opencode.json` `mcp.omega-hub` | `enabled: true`, `url: http://127.0.0.1:8016/mcp` |
| Permission rules | **no rule names any `omega-hub` tool** — permissions are not the cause |
| `src/omega/oracle/subagent_dispatcher.py` | contains **no MCP handling at all** — nothing here propagates servers to subagents |

### Decisive evidence that the repo config does not govern the subagent surface

`opencode.json` sets `firecrawl.enabled = false`. Paged subagent sessions
**still receive `firecrawl_*` tools**. Meanwhile `omega-hub` and `searxng` —
both `enabled: true` — are **absent**.

A config that does not predict the observed surface is not the config in force
for paged sessions. The function set of a `task()` subagent is decided
upstream by the OpenCode harness, outside this repository.

**Do not attempt to fix this in-repo.** Editing `opencode.json`, adding
permission entries, or patching the dispatcher will not attach a server the
harness is not attaching.

### The sanctioned fallback

`scripts/hivemind_post.py` speaks the hub's MCP streamable-HTTP JSON-RPC
directly. One audited path instead of three ad-hoc curl attempts.

```bash
# post
.venv/bin/python scripts/hivemind_post.py \
    --entity maat --model opencode/space-bunny-free \
    --task-current "COMPACT-PREP" \
    --focus-chain seam-repair import-gates \
    --decision "L1: ..." \
    --continuation "Next: ..." \
    --intent status

# prove it landed (do not assume a post succeeded)
.venv/bin/python scripts/hivemind_post.py --read-back ses_3f4464fe0295
```

| Exit | Meaning |
|---|---|
| `0` | accepted, or read-back succeeded |
| `1` | **hub rejected the post** (it names the missing field) |
| `2` | transport failure — hub down, or a non-JSON-RPC response |

Exit 1 and exit 2 are deliberately distinct: "the Hivemind refused this" and
"I could not reach the Hivemind" are different operational problems and must
not collapse into one.

### Contract rules the script enforces

- **M23 fail-loud.** The hub signals a rejected post by returning a JSON error
  *string*, not by raising. The script checks the return value and exits
  non-zero. Never treat a zero exit as proof without `--read-back`.
- **Empty is not missing.** `decisions=[]`, `focus_chain=[]` and
  `continuation=""` are **valid** and are transmitted verbatim. Only an
  explicit `None`/omission is rejected. Coercing empty containers to null
  would turn a legitimate "none recorded" post into a rejection.
- **Prefer `--read-back` after any post you intend to rely on.** A post that
  returns 200 has merely been accepted; a read-back proves it is in the store.

Tested by `tests/test_hivemind_post_script.py` (8 tests, no network: the
transport is stubbed, and rejection, non-JSON-RPC, SSE framing, unreachable
hub, and empty-container pass-through are all covered offline).

### Interim guidance for the fleet

The `omega-hub` MCP tools remain fully functional in primary/oversoul sessions.
Until upstream resolution, **any** session that may have been paged — including
resumed EIS sessions — should assume the Control plane is unavailable and use
`scripts/hivemind_post.py` for coordination. Do not spend a turn discovering
this by trial; the symptom looks like a broken hub, and it is not.

---

## Related

- `docs/architecture/EMBEDDING_SOVEREIGNTY.md` — the one canonical embedding space
- `docs/architecture/AGENT_FLEET.md` — entities and S1–S10 slot governance
- `scripts/hivemind_post.py` — sanctioned no-MCP-tool Hivemind post
- `SOVEREIGN_MANDATES.md` §M1, §M23, §M27
<!-- PROVENANCE-CORRECTED 2026-09-29T04:11:01Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/space-bunny-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

