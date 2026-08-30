<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 ENTITIES_DATA_DIR Fix: Forensic Pipeline Impact Assessment
**Date**: 2026-06-18
**Assessor**: Ma'at (P1-P5 Oversight)

## Summary
The `ENTITIES_DATA_DIR` module-level → call-time fix (`_get_entities_data_dir()`) has **zero impact** on the forensic pipeline infrastructure built by Roc Racoon. The forensic pipeline operates entirely via hardcoded SQL path descriptions and its own `forensics.db` database. It does not import, reference, or depend on `entity_workspace.py`'s path resolution. The fix is architecturally orthogonal.

## Direct Impact

- **Does the forensic code use ENTITIES_DATA_DIR?**
  **No.** The forensic extraction tool (`extract_handoffs.py`) references only its own database at `data/entities/roc_racoon/workspace/forensics/forensics.db`. No import of `entity_workspace` or its path constants exists in the forensic codebase.

- **Does the fix change how sources are resolved?**
  **No.** The forensic pipeline registers 11 data sources via hardcoded seed SQL in `001_init_schema.sql`. Source #7 ("Entity Soul Files") is described as `data/entities/*/soul.yaml` — a literal path string, not a programmatic reference. This path matches both the old and new resolution behavior when `OMEGA_DATA_DIR` is unset (the production case).

- **Are the forensics.db paths still valid?**
  **Yes.** All 11 source paths in the seed schema are hardcoded strings pointing to real filesystem locations. None depend on the `ENTITIES_DATA_DIR` constant or `_get_entities_data_dir()` function. The OpenCode DB path (`~/.local/share/opencode/opencode.db`) is an absolute user-home path unaffected by any engine env vars.

## Indirect Impact

- **Cleaner OpenCode DB data going forward?**
  **Yes — indirectly beneficial.** The bug caused test runs to create 50 orphan entity directories (`ent_0`..`ent_49`) in `data/entities/`. These orphans:
  1. Added noise to the `data/entities/*/soul.yaml` glob — future forensic extractions would include null/empty entity soul files
  2. Inflated the entity count in any pipeline statistics that glob the directory
  3. Could have caused spurious cross-references if the extraction code picked up empty soul.yaml stubs

  With the fix, future OpenCode DB sessions will not generate these orphans, so Phases 2+ of the forensic pipeline will work with cleaner data.

- **INDEX.yaml now stable?**
  **Yes.** The INDEX.yaml could never be accurate with 50 orphans regenerating on every test run. With the fix applied and Sprint D orphans deleted, INDEX.yaml can now represent the true entity population.

- **Future extractions less noisy?**
  **Yes.** Any forensic tool that does `glob("data/entities/*/soul.yaml")` will no longer encounter the `ent_*` orphan stubs. This reduces false positives in:
  - Entity count statistics
  - Soul file parsing pipelines
  - Cross-reference correlation scans

## Recommendations

1. **No changes needed to the forensic pipeline.** The pipeline is properly decoupled from engine-level path resolution — this is good architectural hygiene. Preserve this independence.

2. **Phase 2 extraction scripts should use glob-based discovery** (`data/entities/*/soul.yaml`) rather than hardcoded paths, to remain resilient if the entities directory structure is later made configurable. The seed data's hardcoded `data/entities/*/soul.yaml` glob in `001_init_schema.sql` is already correct in this regard.

3. **Consider adding a note to forensics documentation** that the orphan issue was resolved, so future analysts understand why the entity count dropped from ~107 to ~57 after Sprint D.

4. **No change to EMP/IFL extraction scripts** — the OpenCode DB forensics source (#1) is read-only and its contents are now simply cleaner.

## Verdict

**GREEN** — No forensic pipeline impact. The fix is architecturally orthogonal.

The forensic pipeline sources are registered as hardcoded path strings in SQL seed data. The extraction tool references only its own `forensics.db`. The `ENTITIES_DATA_DIR` → `_get_entities_data_dir()` change lives entirely within `entity_workspace.py` and has zero coupling to any forensic code. **Indirect benefit**: future extractions will contain fewer noise entries from orphan entity stubs.
