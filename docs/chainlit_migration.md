# 🔱 Omega Engine — Chainlit to OpenClaw Migration
**Document**: `docs/chainlit_migration.md`
**Status**: ARCHITECTURAL RECORD
**Classification**: L2 Deep Dive
**Context**: Sovereignty Sprint — Interface Decoupling

---

## 1. Rationalization: The Necessity of Migration

The transition from Chainlit to the **OpenClaw Bridge** is not merely a change in UI frameworks, but a strategic alignment with the **Sovereign Mandates**. The migration was driven by three primary imperatives:

### 1.1 Absolute Sovereignty
Chainlit, while powerful, introduces an opaque abstraction layer between the user and the engine. To achieve true sovereignty, the Omega Engine requires a transparent, lean, and fully owned interface. OpenClaw replaces the "black box" of a third-party framework with a minimal FastAPI-based bridge, ensuring that every byte of data flowing from the client to the Oracle is visible, auditable, and controlled.

### 1.2 AnyIO Compliance (Mandate 1)
Chainlit's internal handling of asynchronous tasks often conflicts with the **AnyIO Absolute**. To prevent event-loop collisions and ensure runtime portability across the Provider Fabric, the interface must be native to AnyIO. OpenClaw is built from the ground up using `anyio`, eliminating the need for `asyncio` shims and preventing the "Restart Cycle" caused by loop mismatches.

### 1.3 Shatter-Glass Standards
The "Shatter-Glass" philosophy dictates that the interface must act as a high-pressure seal. Chainlit's generic session management was insufficient for the rigorous resource isolation and sterilization required by the Omega Engine. OpenClaw implements explicit **Budget Gates** and **Token Ledgers** at the bridge level, ensuring that no single request can destabilize the Ryzen 5700U's limited memory overhead.

---

## 2. System Architecture

The OpenClaw migration shifts the architecture from a monolithic UI-to-Engine flow to a decoupled **Bridge-Runtime-Oracle** pipeline.

### Data Flow Topology
`Client` $\longrightarrow$ `OpenClaw Bridge` $\longrightarrow$ `Omega Runtime` $\longrightarrow$ `Oracle`

1.  **Client**: The front-end interface (Web/CLI) that captures user intent.
2.  **OpenClaw Bridge (FastAPI)**: The "Shatter-Glass" layer. It handles authentication, request sterilization, and enforces the Token Ledger before passing the payload to the runtime.
3.  **Omega Runtime**: The execution environment that manages the `ResourceGuard` (Semaphore) and ensures the Engine-Stack Firewall (Mandate 2) is maintained.
4.  **Oracle**: The final cognitive routing layer that performs intent detection, summons the appropriate Pillar Keeper, and interfaces with the Provider Fabric.

---

## 3. Setup and Configuration

### 3.1 Environment Preparation
Ensure the Omega virtual environment is active and the core dependencies are installed:

```bash
source .venv/bin/activate
pip install fastapi uvicorn anyio
```

### 3.2 Identity Anchoring (`SOUL.md`)
Unlike Chainlit, which manages users via its own internal database, OpenClaw utilizes a **SOUL-based identity anchor**. Each bridge instance must be configured with a `SOUL.md` file in its workspace:

- **Path**: `data/bridge/openclaw/SOUL.md`
- **Purpose**: Defines the bridge's persona, permission levels, and the specific entity it is authorized to mirror.
- **Configuration**: Ensure the `entity_id` in `SOUL.md` matches a valid entry in the `EntityRegistry`.

---

## 4. Operational Execution

### 4.1 Launching the Bridge
The OpenClaw bridge is launched as a FastAPI server. Use the following command to start the service in production mode:

```bash
uvicorn src.omega.bridge.openclaw:app --host 0.0.0.0 --port 8000 --workers 1
```
*Note: Workers are limited to 1 to prevent `ResourceGuard` collisions on local inference.*

### 4.2 Runtime Synchronization
The bridge automatically synchronizes with the Omega Runtime via the `OmegaHub` MCP server. Upon startup, the bridge performs a **Sovereign Handshake**:
1. Validates `SOUL.md` integrity.
2. Checks `ResourceGuard` availability.
3. Establishes a heartbeat with the `omega_hub` server.

---

## 5. Shatter-Glass Implementation Detail

The core of OpenClaw is the implementation of the **Shatter-Glass Standards**, which provide extreme boundary enforcement between the user and the weights.

### 5.1 Budget Gates
Every incoming request is passed through a **Budget Gate**. This is a pre-inference check that evaluates:
- **Context Depth**: If the requested history exceeds the model's quantized KV cache limit, the bridge triggers an automatic `ContextBuilder` compaction before the request reaches the Oracle.
- **Compute Ceiling**: Limits the maximum number of tokens generated per turn to prevent "infinite loops" from consuming all CPU cycles.

### 5.2 Token Ledger
OpenClaw maintains a real-time **Token Ledger** in the bridge's volatile memory. 
- **Tracking**: Every token produced by the Provider Fabric is tallied.
- **Hard-Stop**: Once a session's budget is exhausted, the bridge "shatters" the connection, returning a `SovereignBudgetExceeded` error and forcing a session distillation to `soul.yaml` before allowing a reset.

### 5.3 Sterilization
To prevent "Prompt Leakage" or "Cognitive Drift," OpenClaw implements **Sterilization** on both ends of the pipeline:
- **Input Sterilization**: Strips unauthorized system-level commands and sanitizes the prompt to ensure it conforms to the `EntityRegistry` constraints.
- **Output Sterilization**: Scans the model's response for forbidden patterns or internal `trace_id` leaks before the text is rendered to the client.

---

## 6. Troubleshooting

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| `AnyIO Loop Conflict` | `asyncio` call detected in bridge | Audit code for `import asyncio`; replace with `anyio.to_thread.run_sync`. |
| `ResourceGuard Timeout` | Multiple workers attempting inference | Ensure `--workers 1` in uvicorn command. |
| `SOUL.md Mismatch` | Bridge identity not found in Registry | Run `omega add-entity` to register the bridge's anchor entity. |
| `Shatter-Glass Trip` | Request exceeded Token Ledger limit | Increase session budget in `config/omega.yaml` or trigger manual compaction. |
