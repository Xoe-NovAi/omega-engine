# 🔱 Omega Engine — External AI Integrations
**AP Token**: `AP-EXTERNAL-AI-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ R-52

---

## Executive Summary

To maximize the reasoning capabilities of the Omega Engine, we must leverage high-context external AI tools (NotebookLM, Gemini Deep Research, and Claude) while maintaining local sovereignty. This document defines the strategy for "Knowledge Export" — the process of preparing and syncing the Omega codebase for external analysis without violating security boundaries.

---

## 📓 R-52c: NotebookLM Strategy

NotebookLM is a powerful tool for grounding LLMs in a specific corpus, but it has strict limits: **50 sources** and **50MB per source**. Uploading the Omega Engine file-by-file would quickly exceed the source limit and create fragmented context.

### 1. Categorization Framework
We will group the repository into "Knowledge Pillars" to maximize context density per source:

| Pillar | Source Path | Consolidation Strategy | Target File |
|---|---|---|---|
| **Core Engine** | `src/omega/` | Group by module (Oracle, Memory, Provider) | `engine_core.txt` |
| **Sovereign Gnosis** | `docs/research/` | Group by research family (R-00, R-50, etc.) | `research_vault.txt` |
| **Strategic Intent** | `docs/strategy/`, `docs/ROADMAP.md` | Linear concatenation of all strategy docs | `strategy_roadmap.txt` |
| **System Identity** | `config/`, `AGENTS.md`, `ORACLE_STACK.md` | All YAMLs + core identity markdown | `system_identity.txt` |
| **Validation Suite** | `tests/` | Key test cases and failure patterns | `test_suite_summary.txt` |

### 2. The `prepare_notebooklm.py` Design
The script will perform the following logic:
1.  **Filter**: Exclude `.git`, `__pycache__`, `.venv`, and binary files.
2.  **Consolidate**: Iterate through the defined pillars, reading each file and appending it to a consolidated text file with a header: `--- FILE: [path] ---`.
3.  **Chunk**: If a consolidated file exceeds 40MB, split it into `pillar_part1.txt`, `pillar_part2.txt`.
4.  **Export**: Place all consolidated files in `data/export/notebooklm/`.

**Pseudo-code for consolidation**:
```python
def consolidate(paths, output_file):
    with open(output_file, 'w') as out:
        for path in paths:
            out.write(f"\\n--- FILE: {path} ---\\n")
            out.write(read_file(path))
```

---

## 🚀 R-52d: Gemini Deep Research Sync

Gemini Deep Research requires access to a comprehensive dataset, ideally hosted on Google Drive for seamless integration with the Gemini ecosystem.

### 1. Sync Architecture
We will use `rclone` as the primary synchronization engine due to its robustness and support for filtered syncs.

**Sync Command**:
```bash
rclone sync /home/arcana-novai/Documents/Xoe-NovAi/omega-engine \
  gdrive:OmegaEngineRepo \
  --exclude ".git/**" \
  --exclude "__pycache__/**" \
  --exclude ".venv/**" \
  --exclude "data/sessions/**"
```

### 2. CLI Wrapper: `omega-sync-drive`
A Bash wrapper will be implemented to automate the sync and provide the user with a "Deep Research Trigger" prompt.

**Workflow**:
1.  **Verification**: Check if `rclone` is configured.
2.  **Execution**: Run the filtered sync command.
3.  **Instruction**: Output a prompt for the user to copy into Gemini:
    > "I have synced the latest Omega Engine codebase to my Google Drive folder 'OmegaEngineRepo'. Please perform a Deep Research analysis on the current architecture, specifically focusing on [Insert Focus Area]."

---

## 🔑 R-52e: Claude Hybrid Cloud Access (PAT)

To enable Claude (or other external agents) to read the repository via GitHub without granting full administrative access, we utilize **Fine-Grained Personal Access Tokens (PATs)**.

### 1. Minimal Scope Definition
To maintain the principle of least privilege, the PAT must be configured with the following specific scopes:

| Scope | Access Level | Purpose |
|---|---|---|
| **Contents** | `Read-only` | Allows the agent to read the source code, markdown files, and configurations. |
| **Metadata** | `Read-only` | Allows the agent to read commit history, PR descriptions, and issue labels for context. |

**Crucial Exclusion**: No `Write` access to contents, no access to `Secrets`, and no `Administration` permissions.

### 2. Implementation Flow
1.  **Generate**: Create a Fine-Grained PAT in GitHub $\rightarrow$ Settings $\rightarrow$ Developer Settings $\rightarrow$ Personal Access Tokens $\rightarrow$ Fine-grained tokens.
2.  **Target**: Select only the `omega-engine` repository.
3.  **Apply**: Add the token to the `.env` file as `CLAUDE_REPO_PAT`.
4.  **Verify**: Use a simple `curl` request to ensure the token can read `README.md` but cannot push a change.

---

## 🛠️ Implementation Roadmap

| Task | Component | Effort | Priority |
|---|---|---|---|
| **C-1** | `prepare_notebooklm.py` script | 3h | High |
| **D-1** | `omega-sync-drive` Bash wrapper | 1h | Medium |
| **E-1** | PAT Configuration & .env update | 15min | High |
