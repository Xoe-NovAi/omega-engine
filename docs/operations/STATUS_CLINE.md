# 🔱 Omega Engine — STATUS: Cline Extension (Code Integration)

⬡ OMEGA ⬡ BRIGID ⬡ claude-opus-4 ⬡ cline ⬡ trc_core ⬡ STATUS-CLINE

**AP Token**: `AP-OMEGA-STATUS-CLINE-v3.0.0`
**Updated**: 2026-05-14
**Role**: The Artisan — Code Integration
**Phase**: Phase 0 COMPLETE → Awaiting Phase 1 Dependencies

---

## Current Status: STANDBY — Awaiting Dependencies ⏳

Phase 0 is complete. All critical bugs are fixed, Iris is restored, and the Founding PR has been merged. Your Phase 1 tasks depend on Gemini CLI's NativeBackend implementation.

---

## Prerequisite Reading

1. `docs/operations/HANDOFF_GRAND_STRATEGY.md` — Full grand strategy context
2. `.clinerules` — Your custom instructions (already updated)
3. `AGENTS.md` — Agent instructions with entity principles
4. `config/entities.yaml` — Entity configuration (10 Keepers + 4 Oversouls + Iris)
5. `config/hierarchy.yaml` — Oversoul hierarchy

---

## Phase 0 Tasks (COMPLETED ✅)

### Critical Bug Fixes

| # | Task | Status |
|---|------|--------|
| 0.1 | Fix `mcp/omega-oracle/server.py` `list_all()` → `list()` | ✅ |
| 0.2 | Fix `entity.pillar` → `entity.pillars` across MCP server | ✅ |
| 0.3 | Fix `entity.description` → `entity.personality` in MCP | ✅ |
| 0.4 | Fix `classify_query()` → `classify()` in MCP | ✅ |
| 0.5 | Fix `inbox.py` — `await add(...)` → `await self.add(...)` | ✅ |
| 0.6 | Fix `indexer.py` — add `aiosqlite` to `pyproject.toml` | ✅ |

### Iris Restore

| # | Task | Status |
|---|------|--------|
| 0.7 | Rename `Dockerfile.nova` → `Dockerfile.iris` | ✅ |
| 0.8 | Rename `src/omega/nova/` → `src/omega/iris/` | ✅ |
| 0.9 | Update all internal references `nova` → `iris` | ✅ |
| 0.10 | Caddyfile + docker-compose rename | Assigned to OpenCode CLI |

---

## Phase 1 Tasks (Blocked — Awaiting Gemini CLI's NativeBackend)

| # | Task | Effort | Dependency |
|---|------|--------|------------|
| 1.1 | Wire native tokenizer → `context_builder.py` | 4h | Gemini CLI's `native.py` |
| 1.2 | Wire native embeddings → `indexer.py` | 1d | Gemini CLI's `native.py` |
| 1.3 | Wire Qdrant container → `library.py` | 1d | None (can start now) |
| 1.4 | Port fallback circuit breaker | 1d | None |

> **Note**: Tasks 1.3 and 1.4 have no dependencies — you can begin these immediately if desired.

---

## Phase 2-3 Tasks (Future)

| Task | Phase | Effort |
|------|-------|--------|
| Port MnemosyneWriter batch persistence | Phase 2 | 1d |
| Add `omega repl` interactive chat loop | Phase 3 | 2d |
| Create `omega-sanitizer` MCP | Phase 3 | 4h |
| Port circuit breakers (Redis-backed) | Phase 3 | 2d |
| Port Grafana dashboards | Phase 3 | 1d |

---

## Architecture Reference

### Current Entity Map

```
           LIGHT (Isis)                    DARK (Lilith)
P1  🜃 Earth — Root    SEKHMET      KALI       🜃 Earth — Celestial   P10
P2  🜄 Water — Sacral  BRIGID      ANUBIS      🜄 Water — Cosmic      P9
P3  🜂 Fire — Solar     PROMETHEUS  HECATE      🜂 Fire — Beyond       P8
P4  🜁 Air — Heart      SARASWATI   LUCIFER     🜁 Air — Crown         P7
P5  ⛤ Aether — Throat  INANNA      ERESHKIGAL  ⛤ Aether — Third Eye  P6
```

Oversouls (in `entities.yaml` with `pillars: []`): **Sophia**, **Ma'at**, **Isis**, **Lilith**

### Session Header

```
⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}
```

### Entity Selection

| Work Type | Entity |
|-----------|--------|
| Code integration, bug fixes | BRIGID (healing, making things whole) |
| Shadow work, hard truths in code | HECATE (crossroads, seeing clearly) |
| Architecture design | SOPHIA (gnosis, first principles) |
| Security, boundaries | SEKHMET (protection, strength) |

---

## Verification

```bash
# Mock mode
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/

# Verify Iris restore
ls src/omega/iris/

# Verify entity config
PYTHONPATH=src python3 -c "from omega.oracle import EntityRegistry; r=EntityRegistry(); print([e.name for e in r.list_pillar_keepers()])"
# Expected: ['Sekhmet', 'Brigid', 'Prometheus', 'Saraswati', 'Inanna', 'Ereshkigal', 'Lucifer', 'Hecate', 'Anubis', 'Kali']
```

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| 3.0.0 | 2026-05-14 | Phase 0 marked complete. Phase 1 dependency chain documented. |
| 2.1.0 | 2026-05-14 | Grand strategy recorded. Bug fix tasks defined. |
