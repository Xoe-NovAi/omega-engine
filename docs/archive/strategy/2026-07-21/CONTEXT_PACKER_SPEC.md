# 🔱 Omega Engine — Context Packer Specification
**AP Token**: `AP-CP-SPEC-v1.0.0`
**Status**: PROPOSED
**Entity**: roc_racoon (Sovereign Miner)
**Date**: 2026-06-29

---

## 1. Executive Summary
The **Context Packer** is a specialized skill designed to solve the "Context-to-Slot" problem when interfacing with high-context LLM platforms (specifically Claude Projects). While Claude supports massive context windows, it limits the number of uploaded files (e.g., 12 files). 

The Context Packer transforms a sprawling codebase into a set of **High-Density Context Packs**—consolidated, themed documents that maximize signal and minimize slot usage, ensuring the AI has a complete architectural map without hitting file limits.

---

## 2. Architectural Heritage
This specification is a synthesis of three legacy patterns:
1. **`stack-cat` (v0.1.5)**: Config-driven collection, metadata injection, and themed grouping.
2. **`create_notebooklm_pack.sh`**: Segmented architecture and high-density concatenation.
3. **`R52c_notebooklm_ingestion_strategy.md`**: Signal enhancement and "bundle" logic for small files.

---

## 3. Functional Specification

### 3.1 The Packing Pipeline
The packer operates in four distinct phases: **Selection $\rightarrow$ Consolidation $\rightarrow$ Pruning $\rightarrow$ Packaging**.

#### Phase 1: Selection (The Filter)
The packer uses a `packer-config.yaml` to define "Context Profiles".
- **Include Patterns**: Glob patterns for files to include (e.g., `src/omega/**/*.py`).
- **Exclude Patterns**: Patterns to ignore (e.g., `**/__pycache__/**`, `*.log`).
- **Priority Files**: A list of "Must-Have" files that are always included regardless of patterns (e.g., `SOVEREIGN_MANDATES.md`).
- **Domain Mapping**: Maps file paths to "Themes" (e.g., `src/omega/oracle/*` $\rightarrow$ `Cognition`).

#### Phase 2: Consolidation (The Merge)
Files are merged into themed documents to save slots.
- **Themed Bundling**: All files mapped to the same theme are concatenated into one `.md` file.
- **Metadata Header**: Every file within a bundle is prepended with:
  ```markdown
  ---
  FILE: {relative_path}
  TYPE: {language}
  PURPOSE: {extracted_from_docstring_or_config}
  ---
  ```
- **Separator**: A clear visual boundary is placed between files to prevent semantic bleeding.

#### Phase 3: Pruning (The Compression)
If the resulting number of themed files exceeds the platform limit (e.g., 12), the packer applies pruning:
- **Theme Merging**: Low-priority themes are merged into a `General` or `Misc` bundle.
- **Surgical Pruning**: For oversized files, the packer removes:
  - Redundant boilerplate comments.
  - Triple+ newlines (collapsed to double).
  - Trailing whitespace.
- **Small-File Bundling**: Files < 1KB are automatically bundled by directory to prevent slot waste.

#### Phase 4: Packaging (The Export)
The final output is a structured directory: `context_packs/{profile_name}/`.
- **The Manifest**: A `00_PROJECT_MANIFEST.md` is generated as the primary entry point. It contains:
  - Project version and timestamp.
  - A map of all included files and their corresponding bundles.
  - High-level architectural goals for the current session.
- **The Packs**: Up to 11 themed `.md` files.

---

## 4. Technical Requirements

### 4.1 Configuration Schema (`packer-config.yaml`)
```yaml
profiles:
  engineering-p3:
    description: "Full context for P3 Engineering Pillar"
    max_slots: 12
    include:
      - "src/omega/oracle/orchestrator.py"
      - "src/omega/oracle/model_gateway.py"
      - "tests/test_orchestrator.py"
    exclude:
      - "**/__pycache__/**"
    themes:
      core_logic: ["src/omega/oracle/orchestrator.py", "src/omega/oracle/model_gateway.py"]
      validation: ["tests/**"]
      docs: ["docs/strategy/**"]
```

### 4.2 Implementation Details
- **Language**: Python 3.12+
- **I/O**: Must use `anyio` for all file operations (Mandate M1).
- **Atomic Writes**: Use `.tmp` $\rightarrow$ `.md` rename pattern (Mandate M12).
- **Complexity**: O(N) where N is the number of files in the selection set.

---

## 5. Success Metrics
- **Slot Efficiency**: $\frac{\text{Total Files Included}}{\text{Total Files Uploaded}} > 5.0$ (Average).
- **Semantic Integrity**: AI can correctly identify the original path of any code snippet using the injected headers.
- **Limit Compliance**: Total output files $\le 12$ for any given profile.

---

## 6. Roadmap
- [ ] **v0.1**: Basic concatenation based on hardcoded lists.
- [ ] **v0.2**: YAML configuration and themed bundling.
- [ ] **v0.3**: Automatic pruning and manifest generation.
- [ ] **v1.0**: Integration as an OpenCode Skill.
