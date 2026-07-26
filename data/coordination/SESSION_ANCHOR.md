# 🔱 Session Anchor — Phase D Gate (10/11 Required Pass)
**Last Updated**: 2026-07-25T23:00Z  
**Engine**: v1.8.1  
**Phase**: ⬡ PHASE D GATE — 10/11 required pass; C-3 restic timer only remaining failure  
**AP Token**: `AP-PHASE-D-GATE-v1.1.0`  
**Channel**: opencode / kali

---

## 📋 Session Objective

Strategy doc audit + knowledge gap research + C-0.5 hook architecture correction.

---

## ✅ Delivered This Session

| Deliverable | Path |
|-------------|------|
| **C-0.5 CORRECTED** — Plugin API (NOT hooks key) | `.opencode/plugins/soul_distiller.js` + `.opencode/hooks/session_end.py` |
| **Gate script updated** — checks plugin, not hooks key | `scripts/verify_phase_d_gate.py` |
| **opencode.json cleaned** — hooks key removed (was breaking OpenCode) | `.opencode/opencode.json` |
| **Strategy doc audit** — 8 docs reviewed, 9 fixes applied | See findings below |
| **Ark §4 reconciled** — completed items marked ✅, C-6' honesty | `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` |
| **OMEGA_ENGINE.md C-6' honesty** — 2 unmigrated clones noted | `OMEGA_ENGINE.md` |
| **Deprecation markers** — 2 breaker clones marked DEPRECATED | `search_fleet.py`, `distiller.py` |
| **Web research** — circuit breakers, MCP Streamable HTTP, soul/state persistence | 2026 best practices validated |

---

## 🔍 Critical Discovery: C-0.5 Architecture Was Wrong

**The `hooks` key in `opencode.json` was NEVER valid.** OpenCode's schema has `additionalProperties: false` — any unrecognized key causes `ConfigInvalidError`.

**Correct mechanism**: OpenCode Plugin API (`.opencode/plugins/*.js`)
- Plugin listens for `session.compacted` events via the `event` hook
- Uses Bun's `$` shell API to invoke the Python distillation script
- No config changes needed — plugins in `.opencode/plugins/` are auto-discovered

**This is why Copilot CLI kept removing the hooks key** — it wasn't being malicious, it was correctly validating against the schema.

---

## 🚀 Next Actions

### 🔴 P0
1. **Enable restic timer** — `sudo systemctl enable --now restic-check.timer` ← fixes C-3, gates Phase D
2. **Reinstall mcp v1** — `pip install "mcp>=1.27,<2"` (venv has 1.28.1 v2 beta)
3. **Restart OpenCode** — loads the new `soul_distiller.js` plugin

### 🟠 P1
4. **Verify plugin fires** — compact a session, check logs for "Soul distillation completed"
5. **Kill remaining C-6' breaker clones** — P-5 ticket
6. **Consolidate SQLite DBs** — P-2 ticket (11→3)

---

## 📁 Read Order for Next Agent

1. This file (SESSION_ANCHOR.md)
2. `docs/sprints/current/AGENT_SPRINT_CARD.md`
3. `scripts/verify_phase_d_gate.py` output
4. `git status`

---

## 🔄 Compaction Recovery

On restart: read this anchor → AGENT_SPRINT_CARD → run probes → do not re-research closed domains.

---

*⬡ OMEGA ⬡ KALI ⬡ PHASE-D-GATE-v1.1 ⬡ 2026-07-25*
