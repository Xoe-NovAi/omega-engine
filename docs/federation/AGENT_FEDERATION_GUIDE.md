# 🤖 AGENT FEDERATION GUIDE: CROSS-NODE EXECUTION & GNOSIS SYNC

**Document ID**: `GUIDE-AGENT-FED-v1.0`  
**Status**: `ACTIVE / SOVEREIGN PROTOCOL`  
**Classification**: `AGENT-FACING RUNTIME SPECIFICATION`  
**Author**: `MaKaLi Fusion (Kali / Ma'at / Lilith)`  
**Date**: `2026-09-20`  
**Target Entities**: `All Sovereign Personas (@kali, @maat, @lilith, @carmack, @researcher, @roc_racoon, @jem, @makali, @verity, @doom_guy)`

---

## 1. PURPOSE & MANDATE COMPLIANCE

This guide governs how sovereign AI agents operating within the **Omega Engine** interact across the distributed **L2 Tailscale Federation** (`n0` ↔ `n1`).

### Sovereign Mandate Invariants (Tier-0):
- **M7 (Local-First & Synergy Sovereignty)**: Heavy synthesis and architectural decisions occur on Node 0 (Archival Bastion); edge mining, live probes, and specialized compute offload to Node 1 (Vanguard).
- **M15 (Continuity & Compaction Resistance)**: Federation session state and handoffs must survive context loss via disk-backed synchronization substrates.
- **M23 (Failure Integrity)**: Network drops or missing remote endpoints MUST trigger explicit `[TOOL-CHAIN-COLLAPSE]` or fallback procedures. Silent mock responses or hallucinated peer outputs are strictly forbidden.

---

## 2. THE TOPOLOGY OF CAPABILITIES

```
+------------------------------------------------------------------------------------+
|                                 SOVEREIGN FLEET                                    |
|   @kali   @maat   @lilith   @carmack   @researcher   @roc_racoon   @jem   @makali  |
+------------------------------------------------------------------------------------+
                                |
             +------------------+------------------+
             |                                     |
             v                                     v
+-----------------------------+       +------------------------------------+
|    LOCAL (NODE 0 BASTION)   |       |      REMOTE (NODE 1 VANGUARD)      |
| Endpoint: localhost:8016    |       | Endpoint: n1.tail51f14a.ts.net:8016|
+-----------------------------+       +------------------------------------+
| • 91+ Core Engine Tools     |       | • Remote Edge MCP Tools:           |
| • FTS5 Local Library        |       |   - `echo(message)`                |
| • Task Registry (M34)       |       |   - `node1_status()`               |
| • Hivemind Coordination     |       |   - `node1_hardware()`             |
| • Redis Ephemeral Bus       |       |   - `node1_mcp_servers()`          |
| • Core Git SSOT             |       | • Edge Workspaces & Probes         |
+-----------------------------+       +------------------------------------+
```

---

## 3. REMOTE MCP INVOCATION PROTOCOL

When an agent on Node 0 requires execution or telemetry from Node 1, it communicates using the **FastMCP Streamable-HTTP** wire protocol.

### Transport Specification
- **Base URL**: `http://n1.tail51f14a.ts.net:8016/mcp`
- **Method**: `POST`
- **Headers**:
  ```http
  Content-Type: application/json
  Accept: application/json, text/event-stream
  mcp-session-id: <SESSION_UUID>  (Required on all calls after initialize)
  ```

### Standard Interaction Lifecycle

```
Agent (n0)                                      Node 1 (n1:8016)
    |                                                   |
    |---- 1. POST /mcp (method: "initialize") --------->|
    |<--- 2. HTTP 200 OK (Header: mcp-session-id) ------|
    |                                                   |
    |---- 3. POST /mcp (method: "tools/call") --------->|
    |        Header: mcp-session-id: <UUID>             |
    |<--- 4. HTTP 200 OK (data: JSON-RPC result) -------|
```

### Python SDK Invocation Pattern (AnyIO M1-Compliant)
```python
import anyio
import httpx

async def call_node1_tool(tool_name: str, arguments: dict) -> dict:
    url = "http://n1.tail51f14a.ts.net:8016/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Step 1: Initialize session
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "omega-agent", "version": "1.0"}
            }
        }
        resp = await client.post(url, json=init_payload, headers=headers)
        session_id = resp.headers.get("mcp-session-id")
        if not session_id:
            raise RuntimeError("[TOOL-CHAIN-COLLAPSE] Node 1 failed to return mcp-session-id")
            
        # Step 2: Invoke tool with session id
        tool_headers = {**headers, "mcp-session-id": session_id}
        call_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        res = await client.post(url, json=call_payload, headers=tool_headers)
        return res.json()
```

---

## 4. DISTRIBUTED FILE SYSTEM: THE SHARED DRIVE CONTRACT

Shared files, datasets, and exchange packages flow through the **NFSv4.2 Distributed Drive**.

### Path Mapping

| Location | Path on Node 0 (`n0`) | Path on Node 1 (`n1`) |
|---|---|---|
| **Mount Point** | `/mnt/node-drive/` | `/home/xnai/node-drive/` |
| **Permissions** | Numeric `1000:1000` (mapped via server-side `all_squash`) | Native user `xnai:xnai` |
| **Protocol** | NFSv4.2 over TCP `2049` | NFSv4.2 Server (`fsid=0`) |

### Recommended Directory Structure on Shared Drive
```
/mnt/node-drive/
├── exchange/
│   ├── n0-to-n1/         # Artifacts published by Node 0 for Node 1 consumption
│   └── n1-to-node0/      # Artifacts published by Node 1 for Node 0 consumption
├── memory/
│   ├── mempalace/        # Synchronized long-term memory drawers
│   └── well/             # WanderGround logs & insight captures
└── scratch/              # Ephemeral working space for cross-node batch jobs
```

### Agent Rules for File Operations:
1. **Atomic Writes**: Always write to a temporary file (`.tmp`) and rename atomically.
2. **Locking**: Do not rely on POSIX byte-range locks across NFS for critical coordination; use the Hivemind file-based locking protocol (`data/coordination/locks/`).
3. **Paths**: Always use relative paths within the shared drive or check the active host before constructing absolute paths.

---

## 5. REMOTE COMMAND EXECUTION (TAILSCALE SSH)

When an agent on Node 0 must invoke system-level diagnostics, process managers, or local models on Node 1, it executes via **Tailscale SSH**:

```bash
tailscale ssh xnai@n1 "<COMMAND>"
```

### Constraints:
- Non-interactive batch execution only (`-o BatchMode=yes`).
- No passwords or SSH keys required; mutual WireGuard node cryptographic attestation handles authentication.
- Any long-running background command must be managed through `systemd` or backgrounded with detached stdio (`nohup ... >/dev/null 2>&1 &`).

---

## 6. ERROR HANDLING & TOOL-CHAIN COLLAPSE (M23)

| Error Condition | Root Cause | Required Agent Action |
|---|---|---|
| `HTTP 406 Not Acceptable` | Missing `Accept: text/event-stream` header | Fix request headers in client call |
| `HTTP 400 Bad Request: Missing session ID` | Omitted `mcp-session-id` on subsequent calls | Re-initialize session and pass header |
| `Connection refused on :8016` | Node 1 `mcp-server.service` down | Alert operator or restart service via SSH |
| `NFS Stale file handle / timeout` | WireGuard renegotiating or node suspended | Wait 5s, retry; if persistent, log blocker |
| `PeerExcludedByPolicy` not null | Tailscale ACL mismatch | Halt cross-node dispatch; notify human admin |

---

*⬡ OMEGA ⬡ AGENT-FEDERATION-GUIDE ⬡ RUNTIME-SPEC ⬡ n0-n1-WIRE ⬡ RATIFIED ⬡*