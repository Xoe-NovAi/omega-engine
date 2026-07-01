# 🔱 Context Packer Skill

The **Context Packer** is a sovereign tool designed to optimize codebase ingestion for high-context LLM platforms (like Claude Projects) by consolidating sprawling files into a limited number of high-density "Context Packs".

## 🎯 Purpose
Maximize signal-to-noise ratio and adhere to platform file limits (e.g., 12 slots) while preserving architectural mapping and file provenance.

## 🛠️ Usage
The packer is driven by `packer-config.yaml`. You can define multiple "Profiles" based on the task at hand.

### Execution
Run the packer via the CLI:
```bash
python .opencode/skills/context-packer/packer.py <profile_name>
```

### Configuration (`packer-config.yaml`)
Define profiles with:
- `include`: Glob patterns for files to capture.
- `exclude`: Glob patterns for noise reduction.
- `themes`: Mapping of patterns to themed bundles (e.g., `core_logic`, `docs`).
- `max_slots`: The hard limit for output files (default: 12).

## 🛡️ Sovereign Mandates Compliance
- **M1 (AnyIO Absolute)**: Fully AnyIO-native. No `asyncio` used.
- **M12 (Queue Integrity)**: Implements atomic writes (`.tmp` $\rightarrow$ `.md`) for all output packs.
- **Provenance**: Every bundled file is prepended with a metadata header containing `FILE`, `SIZE`, `LANG`, `SHA256`, and `PURPOSE`.

## ⚙️ Pipeline
1. **Selection**: Filters files based on include/exclude patterns.
2. **Consolidation**: Groups files into themed bundles.
3. **Pruning**: 
   - Collapses excessive whitespace.
   - Merges low-priority themes if `max_slots` is exceeded.
4. **Packaging**: Exports to `context_packs/{profile}/` with a `00_PROJECT_MANIFEST.md`.
