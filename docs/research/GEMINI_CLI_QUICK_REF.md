# ⚡ Gemini CLI Quick Reference

## 📂 Configuration Paths
| Layer | Path | Purpose |
|---|---|---|
| **System Defaults** | `/etc/gemini-cli/system-defaults.json` | Base system defaults |
| **User Settings** | `~/.gemini/settings.json` | Global user preferences |
| **Project Settings** | `.gemini/settings.json` | Project-specific overrides |
| **System Overrides** | `/etc/gemini-cli/settings.json` | Global admin overrides |
| **Project Context** | `GEMINI.md` or `CONTEXT.md` | Hierarchical project instructions |

## 🛠️ Key Settings (`settings.json`)
- `context.fileName`: Defines the name of the project context file.
- `context.includeDirectories`: Directories to be automatically ingested as context.
- `model.maxSessionTurns`: Limit on session history length.
- `general.plan.enabled`: Toggles read-only safety "Plan Mode".
- `general.checkpointing.enabled`: Enables session recovery.
- `experimental.modelSteering`: Enables user hints for tool execution.

## 🚩 Critical CLI Flags
- `--yolo` / `--approval-mode=yolo`: Auto-approve all tool executions.
- `-f <file>`: (Proposed/FR) Specify a per-session memory file.
- `--headless`: Run without interactive UI.

## 🔄 Memory Flow
`User Input` $\rightarrow$ `System Prompt` $\rightarrow$ `Project Context (GEMINI.md)` $\rightarrow$ `Session History` $\rightarrow$ `Model` $\rightarrow$ `Auto-Memory Distillation` $\rightarrow$ `Updated GEMINI.md`
