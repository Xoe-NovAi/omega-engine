# OpenCode V2 Migration — Review Guide for Node 0

> **Branch:** `node1/all-5-mcp-green` (private repo: `omega-engine-internal`)
> **Commits:** `efc12a77` → `40e7808b` (8 migration commits + gnosis lock)
> **Date:** 2026-11-17
> **Status:** Ready for review

## Summary

Migrated Omega Engine from OpenCode CLI v1.9.5 to v2.3.0. All config, plugin, adapter, tests, and docs updated to native V2 shapes. Privacy scrub applied. Remote strategy corrected (origin → private repo).

## What Changed

### 1. Plugin Port (`efc12a77`)
**File:** `.opencode/plugins/gnosis-leash.js`
- V1 `export const` → V2 `Plugin.define({ id, setup })`
- Event subscription via `ctx.event.subscribe()`
- Compaction hook via `ctx.session.hook("compaction", ...)`
- Context hook via `ctx.session.hook("context", ...)`
- Added `@opencode/plugin@^2.3.0` dependency

**File:** `scripts/compaction/leash_status.py`
- Updated watchdog to recognize V2 hook patterns

### 2. Soul Adapter Native V2 (`8b080318`)
**File:** `scripts/soul_agents_opencode.py`
- `agents` array (not `agent` object)
- `permissions` array (not `permission` object)
- `system` field for system prompts
- `experimental` flags for experimental features
- Self-migration: detects V1 shapes and converts

### 3. Tests Updated (`c040aef6`)
**Files:** `tests/test_gnosis_leash.py`, `tests/test_well_injection.py`
- V2 hook patterns (`session.created`, `session.idle`, `session.compacted`)
- V2 plugin harness (Plugin.define, setup function)
- Well injection verify gate (domain allowlist expanded)

### 4. Docs Updated (`03dc3d09`)
**Files:** `docs/AGENT_RUNBOOK.md`, `docs/SYSTEM_GUIDE.md`, `docs/OPENCODE_FOUNDATION.md`, `docs/OPENCODE_AGENT_SYSTEM_GUIDE.md`, `docs/ROADMAP.md`
- V2 keybind: Shift+Tab cycles agents (not Tab)
- V2 MCP: Code Mode default, tools behind `execute()`
- V2 defaults: todos off, subagent depth 1
- V2 permission array shape

### 5. Privacy Scrub (`3e6d073b`)
**39 tracked files** — real tailnet names → placeholders, IPs → 100.x.x.x
- Matches official main's privacy commit (`5a0bc047`)
- Placeholders: `n0.tailnet.ts.net`, `n1.tailnet.ts.net`, `100.x.x.x`

### 6. Remote Strategy Correction (`e984ddbb`)
- `origin` → `omega-engine-internal` (private)
- `public` → `omega-engine` (public)
- Renegade branch deleted from public repo
- `REPO_TOPOLOGY.md` untracked (internal-only)

### 7. Windows Port + Well Fix (`40e7808b`)
- Plugin: `os.homedir()` preferred over `process.env.HOME`
- leash_status: `Path.home()` preferred
- Well VALID_DOMAINS expanded (7 new domains)

### 8. Modelfile Tracking (`081bdbc5`)
- `.modelfiles/Modelfile.phi4-mini` — CPU-only config

## Migration Steps for Official Repo

1. **Apply V2 config shapes** to official `opencode.json`:
   - `agents` array with `permissions` array
   - `mcp.servers` shape
   - `experimental` flags
   - `model` default: `opencode/big-pickle`

2. **Port plugin** (`.opencode/plugins/gnosis-leash.js`):
   - Copy V2 Plugin.define version
   - Ensure `@opencode/plugin@^2.3.0` in dependencies

3. **Update adapter** (`scripts/soul_agents_opencode.py`):
   - Use native V2 shapes
   - Self-migration for V1 → V2

4. **Run gates:**
   ```bash
   make lint && make test && make docs
   ```

5. **Verify privacy:**
   - Confirm 39 files match official's privacy commit
   - `REPO_TOPOLOGY.md` stays untracked (internal-only)

## Key Discoveries

1. **Tab no longer cycles agents** — Shift+Tab in V2. Tab = autocomplete.
2. **MCP tools are Code-Mode-gated** — behind `execute()` as `tools.<server>.<tool>`.
3. **V1 compat masks silent losses** — `subagent_depth`, `compaction.prune`, `doom_loop`, `lsp`, `tools` accepted but ignored.
4. **Three repos exist** — `omega-engine` (public), `omega-engine-internal` (private), `omega-engine-retired` (private).
5. **subagent_depth default is 1** (not 2) in V2.

## Files to Review

| File | Change | Review Priority |
|------|--------|-----------------|
| `.opencode/plugins/gnosis-leash.js` | V2 Plugin.define port | High |
| `scripts/soul_agents_opencode.py` | Native V2 shapes | High |
| `scripts/compaction/leash_status.py` | V2 hook patterns | Medium |
| `tests/test_gnosis_leash.py` | V2 test updates | Medium |
| `tests/test_well_injection.py` | Well verify gate | Medium |
| `docs/OPENCODE_V2_MIGRATION_PLAN.md` | Full migration plan | Low (reference) |
| `docs/AGENT_RUNBOOK.md` | V2 keybind docs | Low |

## Gate Status (Node 1)

| Gate | Result |
|------|--------|
| `make lint` | ✅ PASS |
| `make docs` | ✅ PASS (233 links) |
| `make test` | ✅ 166/166 (2 skipped) |

## Notes for Node 0

- `REPO_TOPOLOGY.md` is internal-only and must NOT be committed to the public repo.
- The `node1/all-5-mcp-green` branch contains 234 commits (renegade lineage + migration). Only the last ~8 commits are V2-migration-relevant.
- The private repo (`omega-engine-internal`) is where all internal work lives.
- The public repo (`omega-engine`) receives filtered cuts only.