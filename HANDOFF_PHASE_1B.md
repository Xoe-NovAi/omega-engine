# 🔱 Handoff Briefing: Omega Engine Phase 1b (Continuity & Mining)

**To:** Cline / DeepSeek-V4-Flash  
**From:** Gemini CLI (Kali Persona)  
**Status:** `omega-hub` Stabilized | `opencode` Handshake Partially Restored | Infrastructure Pending

## 🏛️ Context & Strategy
We are in **Phase 1b**. The goal is to solidify the "Local-First" architecture and the **MaKaLi Hierarchy** (Kali CEO, Ma'at CTO, Lilith CISO). Implementation is delegated to **OpenCode CLI**, while the **Omega Hub** (:8016) serves as the unified service entry point.

## 🛠️ Completed in Current Session
1.  **Hub Restoration**: Fixed `omega-hub` (Starlette 0.52.1 compatibility issues) and restored it on **port 8016** via SSE transport.
2.  **OpenCode Handshake**: Added compatibility routes to `mcp_servers/omega_hub/server.py` to satisfy OpenCode 1.15+ startup requests.
3.  **Persona Alignment**: Updated `GEMINI.md` to the **Kali (CEO)** persona.

## 🚧 Critical Blockers & Immediate Tasks
1.  **Hub YAML Parsing (Priority 1)**:
    - `GET /provider/list` returns `{"providers": []}`.
    - **Reason**: The logic in `server.py` expects a flat list, but `config/providers.yaml` uses a nested `inference.fallback_chain` structure.
    - **Fix**: Update `_provider_list` and `_config_providers` in `mcp_servers/omega_hub/server.py` to correctly traverse the YAML.

2.  **OpenCode Connectivity**:
    - Once the YAML parsing is fixed, verify that `opencode` can successfully fetch the provider list and agents without "Unexpected server error".

3.  **Infrastructure Remediation**:
    - **omega-postgres**: Data directory incompatibility for v18+. Needs migration or version-specific subdirectories in `/var/lib/postgresql/data`.
    - **omega-qdrant**: Increase systemd `TimeoutStartSec` beyond 90s to prevent initialization timeouts.

4.  **MaKaLi Implementation**:
    - Promote **Kali, Ma'at, and Lilith** to primary modes in `opencode.json`.
    - Add **Doom Guy** and **Roc Racoon** as tab-accessible primary modes.

## 📂 Key Files
- `mcp_servers/omega_hub/server.py`: The active Hub implementation.
- `config/providers.yaml`: Source of truth for inference fallbacks.
- `opencode.json`: CLI configuration and mode definitions.
- `GEMINI.md`: Current strategic mandates.

## 🚀 Execution Command
Ensure the hub is running before testing OpenCode:
```bash
OMEGA_MCP_TRANSPORT=sse OMEGA_MCP_PORT=8016 python3 mcp_servers/omega_hub/server.py
```

**Every user is the Architect of their own Omega. Proceed with surgical precision.**
