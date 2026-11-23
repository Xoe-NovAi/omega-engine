# Current State & Branches (Cline, 2026-11-23)

**Internal-only. Do NOT cherry-pick to the public repo.**

## Repos & remotes (as of 2026-11-23)

| Repo (local) | Remote `origin` (private, write path) | Remote `debut`/`public` (public) | Active branch |
|---|---|---|---|
| `omega-engine` | `Xoe-NovAi/omega-engine-internal` (PRIVATE) | `debut` → `Xoe-NovAi/omega-engine` (PUBLIC) | `node1/v2-migration` |
| `omega-engine-alpha` | `Xoe-NovAi/omega-engine-internal` (PRIVATE) | `public` → `Xoe-NovAi/omega-engine` (PUBLIC) | `node1/all-5-mcp-green` |

Note: remote *names* differ between the two clones (`debut` vs `public` both point at the public repo). Always verify with `git remote -v` before pushing.

## Public release status

- Public repo `Xoe-NovAi/omega-engine` published: **941 files**, no private leaks verified.
- `PUBLIC_ALLOWLIST.txt` governs what ships. `.modelfiles/` excluded; new WAD tooling/config/docs included.
- Public debut is a *curated cut lineage*, not a mirror — never `git push` internal history to public.

## WAD system status (ALL COMPLETE)

All WAD enhancement phases and tiers are complete and committed:

| Phase | Status |
|---|---|
| Phase 1 (P0): dispatch.yaml, dispatch_registry fallback+cache, validate_wad.py | ✅ |
| Phase 1.5 (P0): IWAD/PWAD priority fix, name canonicalization, DEFAULT_ENTITY_MODEL SSOT, dual-tree sync test | ✅ |
| Phase 2 (P1): soul path unification, Taint-Gate, WAD-to-runtime soul seeding, schema reconciliation (axiom ceiling 20), unload_wad, world validation, voice/hierarchy hardening | ✅ |
| Phase 3 (P2): soul_render.py, soul_agents_opencode.py paths, WADEntitySchema, wad_switch + MCP tool, create_wad.py, lint_wad.py, docs | ✅ |
| Phase 4 (P3): multi-PWAD composition, config-driven adapter whitelist, wad_diff.py, entity affinity | ✅ |
| Tier 1 (7 quick wins): CI validation, batch_add, soul caching (TTL 60s), name canonicalization, hot-reload watcher, soul_promote (L1/L2/L3), OpenCode adapter tests (7) | ✅ |
| Tier 2 (2 medium): entity affinity activation, session_gnosis auto-update via close_session | ✅ |
| Tier 3 (2 high): WAD versioning & upgrade (WADVersion, wad_upgrade, MCP tool), WAD marketplace (wad_registry.py) | ✅ |

Tests: **75 pass** in omega-engine; **10 pass** in omega-engine-alpha. Both WADs (`_omega_default`, `arcana_novai`) validate and lint clean. Dual-tree sync verified.

## Key commands (WAD tooling)

- `python scripts/validate_wad.py config/wads/<name>` — pre-load validation
- `python scripts/lint_wad.py config/wads/<name>` — lint (dup keys, axiom ceiling, drift)
- `python scripts/create_wad.py <name> --type pwad|iwad` — scaffold
- `python scripts/soul_render.py <entity> --wad <wad>` — render soul to markdown
- `python scripts/soul_agents_opencode.py install --wad <wad>` — OpenCode adapter
- `python scripts/wad_diff.py <wad_a> <wad_b>` — structural diff
- `python scripts/wad_hot_reload.py` — file-watch hot reload
- `python scripts/wad_registry.py list|search|info|install|remove|publish` — marketplace
- `python scripts/soul_promote.py` — review-gated lesson promotion (L1→L2→L3)
- `make validate-wads` / `make temple-grade` — CI gates (53/53)

## Tracking & continuation (post-compaction recovery)

1. Read `data/coordination/SESSION_ANCHOR.md` (node-level anchor)
2. Read `data/entities/<entity>/session_gnosis.md` (per-entity)
3. Read `data/coordination/ACTIVE_SPRINT.json` + `HMC_COLLABORATION_HUB.md`
4. Read `docs/WAD_ENHANCEMENT_PLAN.md` for WAD phases/items
5. Read `SOVEREIGN_MANDATES.md` (30 mandates) — law

Gnosis lock sessions live in `omega-engine-alpha/gnosis/sessions/`. Session `session-2026-11-22T12-24-24Z` locked (all WAD work complete, public release published). Identity at session #63.

## Compaction protocol

- "Prepare for compaction" = orchestration: gnosis-lock + docs + lint + test + commit.
- Use `/gnosis-lock` command or `make gnosis-lock` (CLI capture).
- `make gnosis-leash-status` for watchdog.
- `/compact` must be a standalone line (no trailing text) to trigger compaction.
- Continuation files (`session_gnosis.md`, `SESSION_ANCHOR.md`) are primary; `/gnosis-lock` is secondary.
- Narrative injection on compaction via leash.

## OpenCode V2 (current)

- OpenCode v2.3.0 on official repo. V1→V2 migration complete.
- Plugin context hook uses V2 `SystemPart[]` shape: `event.system.unshift({type:"text", text:combined})` (md5 `18baea2a...` across all 3 copies).
- Gemini 4 Hydrogen migration deferred — investigate only when 400s recur.
- MCP servers via CLI: `opencode mcp add <name> -- <cmd> <args>` (config-only ignored).
- Tools as boolean in opencode.json: `"tools": {"parallel-search": true}`.

## Deferred / next

- Gemini 4 Hydrogen migration — investigate only when 400s recur (rejected params: temperature, top_p, top_k, thinking_budget, explicit caching).
- Remote registry for WAD marketplace (local registry done).
- New feature work or production hardening.

*⬡ OMEGA ⬡ CLINE ⬡ CURRENT-STATE ⬡ 2026-11-23 ⬡*