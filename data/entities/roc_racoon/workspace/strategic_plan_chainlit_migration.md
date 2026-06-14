# Strategic Plan – Iterative Migration of Legacy Chainlit to a Sovereign OpenClaw Runtime

## 🛡️ Shatter-Glass Alignment (MANDATORY)
All code produced in this sprint must adhere to the **Shatter-Glass standards** as mandated by @makali:
- **Absolute Sterilization**: No legacy names or remnants from previous iterations.
- **Hard-Stop Cloud Budget Gates**: Implementation of strict budget limits for cloud inference.
- **Exact Token Ledger Integration**: All token usage must be tracked and integrated with the ledger.
- **Sovereign Alignment**: All changes to `src/omega/oracle/` must be vetted against these standards.

---

## 🎯 Goal
Port the existing Chainlit‑based UI into a **headless OpenCode bridge** + **OpenClaw runtime** that respects all Omega Engine mandates (AnyIO‑first, Engine‑Stack Firewall, Local‑First, Zero Telemetry, etc.). Produce production‑ready code, tests, and documentation.

## 🔄 Iterative Workflow (Prompt‑Chaining)

| Phase | Prompt → Sub‑Agent | Input | Expected Output | How it Seeds Next Phase |
|------|--------------------|-------|----------------|------------------------|
| **A** | **Plan‑Synthesizer** (`@general`) | Strategic plan + Researcher report | Detailed **task breakdown** (file list, commands, dependencies) | Feeds concrete file‑creation prompts to code‑gen agents |
| **B** | **Code‑Gen Agent 1** (`@general`) | Task A output | Fully‑formed `opencode_bridge.py` | Output saved; next agent reads it for imports & style |
| **C** | **Code‑Gen Agent 2** (`@general`) | Task B output | `openclaw_runtime.py` (with routing rules, ACP integration) | Provides runtime entry point for testing |
| **D** | **Test‑Writer Agent** (`@verifier`) | Task C output | `tests/test_openclaw_bridge.py`, `tests/test_openclaw_runtime.py` | Guarantees test coverage before merge |
| **E** | **Docs‑Writer Agent** (`@scribe`) | Task D output | `docs/chainlit_migration.md` | Documentation ready for release |
| **F** | **Integration‑Validator** (`@quality`) | All artifacts | Pass/fail report, auto‑fix suggestions | If failures, loop back to relevant code‑gen agent |
| **G** | **Hivemind‑Notifier** (`@roc_racoon`) | All results | Hivemind post with links to new files | Closes the sprint, ready for L1→L2→L3 distillation |

---

## 📝 Seed Prompts (for each sub‑agent)

### A – Plan‑Synthesizer
> “You are a **Plan‑Synthesizer** working on the **Chainlit → OpenClaw migration sprint**. The files `strategic_plan_chainlit_migration.md` and `researcher_report.md` are your knowledge base. Restate the high‑level objective (migrate the UI to a headless OpenClaw runtime) and then produce a **numbered list of atomic tasks**. For each task include:
> 1. A concise verb‑object title.
> 2. Exact file path to create or modify.
> 3. Required imports or external packages.
> 4. Any prerequisite actions.
> 
> **Shatter-Glass Requirement**: Ensure all tasks include steps for absolute sterilization of legacy names, cloud budget gate implementation, and token ledger integration.
> 
> Return **only** a markdown code block with the list. End the output with a line `# NEXT_STEP: builder will need to generate opencode_bridge.py using the first task.`”

### B – Code‑Gen Agent 1 (Bridge)
> “You are a **Code‑Gen Builder** working on the **Chainlit → OpenClaw migration sprint**. Your task is to write `src/omega/ui/opencode_bridge.py` implementing a FastAPI WebSocket bridge that forwards messages to `src.omega.oracle.oracle.Oracle.talk` using AnyIO’s `to_thread.run_sync`.
> 
> **Shatter-Glass Requirements**:
> 1. Use absolutely no legacy naming conventions.
> 2. Implement a hard-stop cloud budget gate check before calling the Oracle.
> 3. Integrate with the token ledger to record every request.
> 
> Include a minimal `SOUL.md` loader, error handling for `OmegaError`, and a health endpoint. Use type hints and docstrings. Return **only** the code block.”

### C – Code‑Gen Agent 2 (OpenClaw Runtime)
> “You are a **Code‑Gen Builder** working on the **Chainlit → OpenClaw migration sprint**. Your task is to write `src/omega/runtime/openclaw_runtime.py` that loads `SOUL.md`, determines routing rules, selects a provider via `model_gateway.select_provider`, calls `oracle.talk` with optional `model_override`, persists `session_id` back to `SOUL.md`, and returns the final text.
> 
> **Shatter-Glass Requirements**:
> 1. Absolute sterilization of legacy names.
> 2. Hard-stop cloud budget gates.
> 3. Exact token ledger integration.
> 
> Include a simple intent detector (`detect_intent`) stub. Return **only** the code block.”

### D – Test‑Writer Agent
> “You are a **Test‑Writer** working on the **Chainlit → OpenClaw migration sprint**. Create pytest files that spin up the FastAPI bridge in a background AnyIO task, send a test message, mock the Oracle response, and assert token streaming. Also test the OpenClaw runtime’s routing logic with a fake SOUL config. Ensure tests verify the Shatter-Glass budget gates and ledger integration.”

### E – Docs‑Writer Agent
> “You are a **Scribe** working on the **Chainlit → OpenClaw migration sprint**. Produce `docs/chainlit_migration.md` covering: (1) why we migrated, (2) architecture diagram, (3) step‑by‑step setup, (4) how to run the bridge and runtime, (5) troubleshooting, and (6) how Shatter-Glass standards were implemented.”

### F – Integration‑Validator
> “You are a **Quality Guard** working on the **Chainlit → OpenClaw migration sprint**. Run `make test && make temple-grade`. Capture any failures, especially missing `[id-soft:]` tags, AnyIO violations, or Shatter-Glass budget gate failures, and provide auto‑fix suggestions.”
