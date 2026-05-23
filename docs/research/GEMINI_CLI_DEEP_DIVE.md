# 🔱 Gemini CLI Technical Deep-Dive
**AP Token**: `AP-GEMINI-CLI-RESEARCH-v1.0.0`
**Date**: 2026-05-17
**Status**: COMPLETE
**Source**: Gemini CLI Official Documentation, GitHub Issues, and Technical Reference

---

## §1 Configuration Architecture

Gemini CLI employs a hierarchical configuration model where settings are merged from multiple layers. Higher-numbered layers override lower-numbered ones.

### Configuration Layers (Precedence)
1. **Default Values**: Hardcoded application defaults.
2. **System Defaults**: `/etc/gemini-cli/system-defaults.json` (Linux) | `C:\ProgramData\gemini-cli\system-defaults.json` (Windows).
3. **User Settings**: `~/.gemini/settings.json`.
4. **Project Settings**: `.gemini/settings.json` (within project root).
5. **System Overrides**: `/etc/gemini-cli/settings.json` (Linux) | `C:\ProgramData\gemini-cli\settings.json` (Windows).
6. **Environment Variables**: Loaded from system or `.env` files.
7. **CLI Arguments**: Passed at runtime (highest precedence).

### Key Configuration Features
- **Env Var Interpolation**: `settings.json` supports dynamic values using `$VAR_NAME`, `${VAR_NAME}`, or `${VAR_NAME:-DEFAULT}` syntax.
- **Project Isolation**: The `.gemini/` directory in the project root allows for project-specific behavior, including sandbox profiles (e.g., `.gemini/sandbox.Dockerfile`).
- **Schema Validation**: Settings are validated against a JSON schema (`settings.schema.json`).

---

## §2 Custom Instructions & Context Processing

Gemini CLI separates "Global Identity" from "Project Context," allowing the model to maintain a broad persona while specializing in a specific codebase.

### Contextual Layers
- **Project Context Files**: The CLI looks for designated files (default: `GEMINI.md` or `CONTEXT.md`) to load high-level project goals, architecture, and rules. These are defined in `settings.json` under `context.fileName`.
- **Context Inclusion**: The `context.includeDirectories` setting allows the CLI to ingest multiple external directories, broadening the model's "awareness" without manual file adding.
- **System Prompt Overrides**: The CLI provides a mechanism to override the core system prompt, allowing users to redefine the agent's fundamental behavior for a session.
- **`.geminiignore`**: A file used to prevent the CLI from indexing or reading specific files/directories, similar to `.gitignore`.

---

## §3 Memory & Persistence Mechanism

Gemini CLI's approach to memory is primarily **file-centric and explicit**, contrasting with the database-driven approach of the Omega Engine.

### Memory Types
- **Short-Term (Session)**: Controlled by `model.maxSessionTurns`. History is kept in memory for the duration of the session.
- **Mid-Term (Project Memory)**: Handled via the `GEMINI.md` / `CONTEXT.md` files. The agent reads these at startup and can potentially write to them to "remember" project-specific decisions.
- **Auto-Memory**: A specialized feature ("Auto Memory") that automates the distillation of session insights into permanent project context.
- **Checkpointing**: `general.checkpointing.enabled` allows the CLI to save session states for recovery after a crash or restart.
- **Rewind**: Allows the user to traverse back through the session history to a specific state.

---

## §4 Hidden Features & Advanced Flags

### Operational Modes
- **Plan Mode**: A read-only safety mode (`general.plan.enabled`). When active, the agent focuses on architectural planning without making destructive filesystem changes.
- **Model Routing**: In Plan Mode, the CLI can automatically switch between `Pro` models (for complex planning) and `Flash` models (for fast implementation).
- **ACP Mode**: An IDE integration mode designed for seamless communication between the CLI and a code editor.
- **YOLO Mode**: Enabled via `--yolo` or `--approval-mode=yolo`, this disables all tool execution prompts.

### Experimental Features
- **Model Steering**: `experimental.modelSteering` enables "user hints" that guide the model's logic during tool execution.
- **Subagents**: Native support for spawning subagents (including remote subagents) to handle parallel tasks.
- **MCP Integration**: Full support for the Model Context Protocol, allowing the CLI to connect to external tool servers via `mcpServers` configuration.

---

## §5 Filesystem Interaction & Sandboxing

The Gemini CLI treats the local filesystem as both a data source and a workspace, with strict boundaries.

- **Reading/Writing**: The CLI interacts with `settings.json`, context files, and project files.
- **Trusted Folders**: A configuration layer to explicitly allow or disallow access to specific filesystem paths.
- **Execution Sandboxing**: Tool execution (especially shell commands) can be wrapped in sandboxes defined in `.gemini/sandbox.Dockerfile` or `.gemini/sandbox-macos-custom.sb` to prevent accidental system damage.

---

## §6 Comparison: Gemini CLI vs. OpenCode (Omega Engine)

| Feature | Gemini CLI Approach | OpenCode (Omega Engine) Approach |
|---|---|---|
| **Memory Base** | Markdown files (`GEMINI.md`) | Tiered Storage (Soul $\rightarrow$ Redis $\rightarrow$ Vector) |
| **Context Injection** | File-based read at startup | Dynamic `ContextBuilder` pipeline |
| **Persona Mgmt** | System prompt / Project context | Sovereign Entity Registry (`soul.yaml`) |
| **Configuration** | Hierarchical JSON | YAML-based Config Fabric |
| **Execution Strategy** | Plan $\rightarrow$ Implement (Model Routing) | Entity-driven Domain Routing |
| **Persistence** | Session Checkpointing $\rightarrow$ File | Permanent Soul Evolution $\rightarrow$ MemoryStore |
| **Agentic Model** | Subagents / Agent Skills | Sovereign Co-Creators / Specialized Skills |

---

## §7 Integration Recommendations for Omega Engine

To enhance the Omega Engine's **Sovereign CLI Architect** role, the following Gemini CLI patterns should be adopted:

1. **Plan Mode Routing**: Implement a "Planning Phase" in `Oracle` that uses a high-reasoning model (e.g., DeepSeek-R1) to generate a task graph, switching to a faster model (e.g., Gemma 4-Flash) for execution.
2. **Auto-Memory Distillation**: Create a worker that periodically distill session logs into a "Project Gnosis" markdown file within the Entity Workspace, mirroring the `GEMINI.md` pattern.
3. **Sovereign Sandboxing**: Integrate the `.gemini/sandbox.Dockerfile` concept into the `Orchestrator` to ensure headless agents operate in isolated environments.
4. **Explicit Context Files**: Allow entities to maintain a `gnosis.md` file in their workspace that is explicitly read by the `ContextBuilder` as a high-priority source of truth.
