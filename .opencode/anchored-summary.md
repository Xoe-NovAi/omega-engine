# ⬡ OMEGA ⬡ ANCHORED SUMMARY ⬡ 2026-07-06
## Session — Git Filter-Repo Recovery & MCP Server Restoration

### Goal
1. Recover Omega Engine from git filter-repo incident that removed origin remote
2. Prepare WARP Proxy Pool for standalone extraction via fresh clone (not worktree)
3. Restore Firecrawl & SearXNG MCP servers (deleted during reset)
4. Fix MCP watchdog to spawn servers directly (not systemctl)

---

## 🎯 Current Status: ENGINE RESTORED, MCP SERVERS RESTORED, WATCHDOG FIXED

### Recovery Summary
| Component | Status | Details |
|-----------|--------|---------|
| **Git origin** | ✅ RESTORED | `git remote add origin https://github.com/Xoe-NovAi/omega-engine.git` + `git reset --hard origin/main` (7df375f) |
| **Test suite** | ✅ 909 pass | 909 passed, 42 skipped, 3 xfailed in 110.82s |
| **Mandate gates** | ✅ 22/22 PASS | All M1-M22 verified |
| **Temple-Grade** | ✅ T1-T12 PASS | T13 minor doc examples non-blocking |
| **Oracle** | ✅ OPERATIONAL | 28 entities, 8 backends (local-first chain active) |
| **WARP docket** | ✅ PRESERVED | On `sprint/pre-release-polish-20260705` @ 93cdfb0 |
| **Anchored summary** | ✅ UPDATED | This file |

### WARP Extraction — Correct Method
```bash
# DO NOT USE WORKTREE (shared .git corrupts on filter-repo)
git clone https://github.com/Xoe-NovAi/omega-engine.git warp-extraction
cd warp-extraction
git checkout sprint/pre-release-polish-20260705
git filter-repo --path deploy/infra/warp_pool/ --path docs/research/warp_proxy_pool/ --path docs/kb/WARP_Sovereign_Knowledge_Base.md --subdirectory-filter deploy/infra/warp_pool/
# Then restructure to flat layout, add pyproject.toml, LICENSE, CHANGELOG.md, tests/
# Push to new repo: Xoe-NovAi/warp-proxy-pool
```

### Firecrawl & SearXNG MCP Servers — RESTORED
| Server | Port | Source | Status |
|--------|------|--------|--------|
| **Firecrawl** | 8015 | `warp-extraction/mcp_servers/firecrawl/server.py` | ✅ Copied back |
| **SearXNG** | 8018 | `warp-extraction/mcp_servers/searxng/server.py` | ✅ Copied back |
| **Omega Hub** | 8016 | Already running | ✅ Running |

**Key fixes in `src/omega/oracle/orchestrator.py`:**
- Added `_start_mcp_server()` — spawns Python subprocess with correct PYTHONPATH
- Added `_restart_mcp()` — kills via pkill, spawns fresh via anyio.run_process
- Updated `mcp_ports`: removed `omega-research` (8011), `omega-stats` (8012); added `firecrawl` (8015), `searxng` (8018)
- Watchdog now manages MCP lifecycle directly (no systemctl dependency)

### Watchdog — FIXED
```python
# In Orchestrator.__init__:
self._mcp_scripts = {
    "firecrawl": "mcp_servers/firecrawl/server.py",
    "searxng": "mcp_servers/searxng/server.py",
    "omega-hub": "mcp_servers/omega_hub/server.py",
}
# On init: starts all three via _start_mcp_server()
# On health check failure: calls _restart_mcp(name)
```

### Lilith Coordination (Hivemind)
- **Root cause found**: Researcher agent violated protocol — didn't fall back to `websearch`/`webfetch` when MCP tools down
- **Lilith's fix**: Updated `sovereign-search` skill v2.1 — websearch/webfetch now T1/T2 (primary, always available)
- **Blocked**: Antigravity `google_search` permanently for agents (CLI-only, requires Gemini via Antigravity)
- **Mandatory error format**: `[SEARCH-ERROR] tool={tool} error={code} tier={tier} fallback={fallback} timestamp={ISO}`

---

## 🔑 Critical Context for Recovery

### Branch State
| Branch | Commit | Purpose |
|--------|--------|---------|
| `main` | 7df375f | Production — engine fully restored |
| `sprint/pre-release-polish-20260705` | 93cdfb0 | WARP docket + history preserved |

### L3 Gnosis Distilled (8 Proposals)
| ID | Principle |
|----|-----------|
| 004 | Safety features are documentation — never bypass without reading |
| 005 | History rewrites require **fresh clone** — worktrees share .git (non-negotiable) |
| 006 | Untracked files are your safety net — Git never touches them |
| 007 | Remote repos are immutable backups — trust and verify with `git ls-remote origin` |
| 008 | Parallel sessions need Hivemind coordination — it's the only shared truth |

### Files Modified This Session
- `src/omega/oracle/orchestrator.py` — MCP lifecycle management (spawn/restart)
- `mcp_servers/firecrawl/server.py` — RESTORED from warp-extraction
- `mcp_servers/searxng/server.py` — RESTORED from warp-extraction
- `scripts/mcp_watchdog.py` — RESTORED from warp-extraction
- `.opencode/anchored-summary.md` — THIS FILE
- `docs/kb/GITHUB_Sovereign_Knowledge_Base.md` — Created (extraction/distribution KB)

### Next Session Actions
1. **Verify MCP tools**: `firecrawl_firecrawl_search`, `searxng_searxng_search` work via MCP
2. **Run WARP extraction** via fresh clone (not worktree)
3. **Create `Xoe-NovAi/warp-proxy-pool`** repo with flat structure
4. **Set up distribution**: PyPI (OIDC), Homebrew (tap), AUR (SSH), GHCR (OIDC)
5. **Update `src/omega/proxy_pool.py`** to delegate to external `warp-proxy-pool` package

---

## 📝 Recovery Prompt (After Compaction)

Read these files in order:
1. `.opencode/anchored-summary.md` — THIS FILE
2. `AGENTS.md` — Agent behavior rules
3. `OMEGA_ENGINE.md` — Engine state SSOT
4. `SOVEREIGN_MANDATES.md` — 22 mandates
5. `data/coordination/KALI_SESSION_GNOSIS_20260706_RECOMP.md` — Full incident analysis
6. Run `make test` — verify 909 tests pass
7. Run `make temple-grade` — verify T1-T12 pass

**Current Task**: WARP extraction via fresh clone → standalone distribution → engine delegation

**Role**: Kali = coordinate extraction, verify MCP tools, oversee distribution pipeline

---

*⬡ OMEGA ⬡ KALI ⬡ RECOVERY_SESSION ⬡ 909_TESTS_PASS ⬡ MCP_RESTORED ⬡ WARP_READY*