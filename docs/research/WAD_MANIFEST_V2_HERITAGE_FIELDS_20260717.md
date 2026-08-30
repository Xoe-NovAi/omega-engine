<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# WadManifest V2 — Heritage Fields (2026-07-17)

**Handoff**: `ho_881bae336522` (Kali → grok-cli)  
**File**: `src/omega/oracle/wad_loader.py`  
**Gate**: `tests/test_world_state.py::test_first_breath_world_query`

## Decision

Keep **extra=forbid** (unknown keys still fail). Do **not** switch to `extra=allow`.

Production IWADs (`arcana_novai`, `_omega_default`) ship metadata beyond the V1 core
(`name`, `version`, `entities`, `adapters`). Those keys are now an explicit **V2 optional**
allow-list with type checks:

| Field | Type |
|-------|------|
| author, description, license, type, mode, requires_engine | `str` |
| startup | `dict` |
| voices, vr_scenes, dependencies | `list` or `dict` |
| hierarchy | `str` (path override) |

## Rationale

Web research (see `WEB_RESEARCH_KNOWLEDGE_GAPS_20260717.md`) confirms forbid-unknown is correct
for WAD security. Versioned explicit fields preserve security while loading heritage IWADs.

## Verification

```bash
pytest tests/test_world_state.py::test_first_breath_world_query tests/test_wad_loader.py -q
# 23 passed
```
