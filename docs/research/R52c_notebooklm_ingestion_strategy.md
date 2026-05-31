# 🔱 Omega Engine — NotebookLM Ingestion Strategy
**AP Token**: `AP-R52C-NL-STRAT-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ RESEARCH

---

## 1. Executive Summary
NotebookLM provides a powerful grounding mechanism for LLMs by treating a set of documents as a closed-world knowledge base. To maximize its utility for the Omega Engine while staying within its constraints (50 sources per notebook, 50MB per source), we will implement a **segmented notebook architecture**.

This strategy transforms the raw repository into high-density, cleaned "Source Packs" tailored for LLM ingestion, ensuring that architectural context is preserved without noise.

---

## 2. Categorization Schema (Notebook Mapping)

To prevent source overflow and optimize retrieval, the codebase and documentation are split into five specialized notebooks.

### Mapping Table

| Notebook ID | Notebook Name | Included Paths / Files | Purpose |
| :--- | :--- | :--- | :--- |
| **NB-01** | **Core Engine Architecture** | `src/omega/**/*`, `config/**/*`, `Makefile`, `README.md` | Technical implementation, config, and build logic. |
| **NB-02** | **Strategic Gnosis** | `docs/strategy/**/*`, `docs/ROADMAP.md`, `docs/decisions/PIVOT_LOG.md`, `AGENTS.md`, `ORACLE_STACK.md` | High-level vision, architectural decisions, and agent rules. |
| **NB-03** | **Research Archive** | `docs/research/**/*` | Detailed technical research, API specs, and audit reports. |
| **NB-04** | **Ops & Integration** | `docs/operations/**/*`, `docs/integration/**/*`, `docs/intake/**/*`, `docs/index.md` | Deployment, operational guides, and external integrations. |
| **NB-05** | **Validation Suite** | `tests/**/*`, `scripts/**/*` | Test cases, validation scripts, and utility tools. |

---

## 3. Ingestion Pipeline: `prepare_notebooklm.py`

A Python utility will be implemented to preprocess the repository. The goal is to maximize "signal" and minimize "noise" (e.g., `__pycache__`, `.git`, large binary files).

### Script Logic & Design

**A. File Discovery & Filtering**
- **Allowed Extensions**: `.py`, `.md`, `.yaml`, `.json`, `.sh`, `.sql`.
- **Exclusions**: `**/__pycache__/**`, `**/.pytest_cache/**`, `**/.git/**`, `**/.venv/**`.

**B. Content Cleaning (Signal Enhancement)**
- **Path Injection**: Every file's content is prepended with a standardized header:
  `--- FILE: {relative_path} ---`
- **Whitespace Normalization**: Remove trailing spaces and collapse triple+ newlines into double newlines.
- **Header Preservation**: Ensure Markdown headers (`#`, `##`) are maintained to help NotebookLM recognize document structure.
- **Code-to-Text Optimization**: For Python files, remove excessively long comment blocks that are redundant with documentation.

**C. Chunking Strategy**
- **Default**: One file = One source.
- **Large File Handling**: If a file exceeds 1MB (rare in this repo), it is split by top-level function or class definition to keep the context window focused.
- **Consolidation**: Very small files (<1KB) in the same directory are concatenated into a single `{directory}_bundle.txt` to save source slots.

**D. Export Structure**
The script will output to `notebooklm_export/{NB-ID}/{filename}`, allowing for simple drag-and-drop upload to the respective notebook.

---

## 4. Archive & Maintenance

### Naming Convention
To maintain version history and avoid mixing stale data, exports will follow this pattern:
`OMEGA_NL_{YYYYMMDD}_{VERSION}`
*Example: `OMEGA_NL_20260516_v1`*

### Refresh Schedule
| Trigger | Frequency | Action |
| :--- | :--- | :--- |
| **Routine Sync** | Weekly (Monday 09:00) | Full rebuild of all 5 notebooks. |
| **Strategic Pivot** | Per Major PR / Phase | Re-sync **NB-02** and **NB-03** immediately after design changes. |
| **Implementation Spike** | Per Feature Completion | Sync **NB-01** and **NB-05** after new modules are hardened. |

---

## 5. Implementation Note for MiniMax M2.5

The implementation agent should prioritize the following:
1. Use `pathlib` for robust cross-platform path handling.
2. Implement the cleaning logic as a set of modular functions (e.g., `clean_markdown()`, `clean_python()`).
3. Ensure the script can be run as a standalone utility: `python3 scripts/prepare_notebooklm.py --output ./export`.
4. Add a summary log at the end of execution showing the count of sources per notebook to verify they are under the 50-source limit.
