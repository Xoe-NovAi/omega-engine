# WAD Contract Brief — Node 1 study of the Engine's stack contract

**Date**: 2026-09-18 · **Sources**: read-only from `origin/main`
(`Xoe-NovAi/omega-engine`): `src/omega/oracle/wad_loader.py`,
`docs/architecture/SOVEREIGN_WAD_PROTOCOL.md`, `docs/tutorials/first-wad.md`,
`config/wads/{_omega_default,arcana_novai}/`, `tests/test_wad_{loader,auto_loading}.py`.
**Status**: contract mapped; validation questions for Node 0 (not verdicts).

## 1. What a WAD is

**WAD = "Where's All the Data?"** (Doom Bible, 1993). A directory under
`config/wads/<name>/` (overridable via `OMEGA_WADS_DIR`), discovered by the
presence of `manifest.yaml`. The loader registers its entities + voices into the
`EntityRegistry`; the tutorial path is `entities.yaml` + `ingestion/domains.yaml`
→ load → ingest.

## 2. Manifest schema (enforced by `wad_loader.py`)

- **V1 required** (typed): `name: str`, `version: str`, `entities: list|dict`,
  `adapters: list|dict`.
- **V2 optional** (explicit allow-list, `extra=forbid` — unknown keys REJECT):
  `author`, `description`, `license`, `type` (iwad|pwad), `mode`,
  `requires_engine`, `startup: dict` (startup message), `voices`, `vr_scenes`,
  `dependencies`, `hierarchy` (path override).
- **Entity fields** (typed): `name`, `domains` (list, ≤20), `model`,
  `personality`, `temperature`, `context_window`, `slots`.
- **Hardening**: YAML ≤1 MB, entity names ≤128 chars, adapter imports whitelisted
  (`omega.memory.adapters*` only).

## 3. Override semantics (Doom-faithful)

- **Backward scan**: later WAD entity definitions override earlier ones (PWAD
  patches beat IWAD base — `w_wad.c:376`).
- **4-path VFS**: active stack → `_omega_default` (`files.c:39-75` pattern).

## 4. The firewall (M2 — `SOVEREIGN_WAD_PROTOCOL.md` §§1–5)

WADs are **data, not code** (§3.1): sanitization (§3.2), resource quarantine
(§3.3), review gate (§3.4), prompt-injection mitigation (§4), 3-tier governance
hierarchy (§5). WADs modify **runtime state only** — never engine internals.

## 5. The two IWADs today

| | `_omega_default` ("The Company") | `arcana_novai` ("Personal AI OS") |
|---|---|---|
| version | 1.0.0, requires `>=0.5.0` | **0.1.0, requires `>=0.4.0`** |
| mode | production | personal |
| shape | manifest lists 15 entity files; `entities/`, `voices/`, `meditate/`, ethics/audience/hierarchy/roles | `entities.yaml` dict (default + 12 deities on `qwen3-1.7b-q6_k`, full esoteric metadata); `agents/*.md` (13 deity cards incl. Lilith); `axioms`/`qliphoth`/`spheres`/`vault_schema`; `world/{core/physics,metaphysics/laws}`; `adapters/`, `plugins/entity_roc_racoon.py` |
| manifest `entities:` | file list | **empty list** (entities live in `entities.yaml` instead) |

## 6. Validation questions for Node 0 (defer, don't decree)

1. `arcana_novai` manifest `entities: []` vs populated `entities.yaml` — which does
   the loader consume? (Both shapes are schema-legal.)
2. `voices.primary: jem.yaml` — no `voices/` dir in `arcana_novai`; resolved from
   `_omega_default` via VFS fallback, or missing?
3. Python inside the WAD (`adapters/__init__.py`, `plugins/entity_roc_racoon.py`)
   vs §3.1 "data, not code" — covered by review gate + adapter whitelist? Precedent
   exists; confirm the rule.
4. Committed `tmpfzhu8kz4.tmp` (+`.license`) — junk or load-bearing?
5. `requires_engine >=0.4.0` vs current engine version — still accurate at v0.1.0?

## 7. Node 1 triage (preliminary — WAD payload vs engine-core)

- **WAD payload candidates** (`arcana_novai`): `parallel_bridge.py` + `exa_search.py`
  (ingestion/bridge tools — cf. `plugins/entity_roc_racoon.py` precedent);
  thermal bench + CPU guide (ModelGate/sysadmin knowledge); gnosis-lock ritual +
  Well (Context-pillar memory patterns); §11 transport lessons (bridge knowledge);
  portable `{env:}` MCP wiring (fixes the `arcana-novai` absolute-path leak).
- **Engine-core candidates**: placeholder-key detector hygiene test; sysctl/ZRAM/THP
  deploy tuning; `AllowedCPUs` + thread policy.
- **Rule**: nothing custom in the engine tree, nothing engine in the WAD.
