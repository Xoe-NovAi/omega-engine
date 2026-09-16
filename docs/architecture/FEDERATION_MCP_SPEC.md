# 🔱 SPECIFICATION: FEDERATION MCP TOOLS
**Doc ID**: `SPEC-FEDERATION-MCP-v1.0`  
**Status**: **IMPLEMENTED** (registered on omega-hub :8016, verified 2026-09-16)  
**Module**: `mcp_servers/omega_hub/hub_tools/federation.py`  
**Author**: MaKaLi Fusion (Kali / Ma'at / Lilith)  
**Date**: 2026-09-16  

---

## 1. Overview & Objective

To ensure that both human operators and autonomous agents can observe and diagnose the multi-node mesh without dropping into raw shell scripts, the Omega Core Hub (`:8016`) provides native MCP tools for federation governance.

These tools query local Tailscale daemon state, test WireGuard peer connectivity, verify transport security headers, and return structured telemetry to OpenCode and the agent fleet.

---

## 2. Tool Interfaces

### 2.1 `omega_federation_status`

Returns a comprehensive snapshot of the local node's connection to the tailnet, its identity tags, and the reachability status of known federation peers.

#### Parameters:
* None (Zero-argument inspector)

#### Response Schema:
```json
{
  "self": {
    "hostname": "omega-hub",
    "tailscale_ip": "100.123.51.67",
    "magicdns": "omega-hub.tail51f14a.ts.net",
    "tags": ["tag:omega-hub"],
    "backend_state": "Running"
  },
  "peers": [
    {
      "hostname": "kali-n1",
      "tailscale_ip": "100.x.x.x",
      "magicdns": "kali-n1.tail51f14a.ts.net",
      "tags": ["tag:asus"],
      "online": true,
      "direct": true,
      "last_seen": "2026-09-16T12:00:00Z"
    }
  ],
  "invariants": {
    "zero_inference_egress": true,
    "magicdns_active": true,
    "direct_wireguard": true
  }
}
```

---

### 2.2 `omega_federation_diagnose`

Runs an end-to-end diagnostic battery probing connectivity, DNS resolution, and application-layer transport headers.

#### Parameters:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `target_peer` | string | No | Specific peer to probe (default: probes all known peers) |

#### Diagnostic Checks Executed:
1. **Daemon Health**: Verifies `tailscaled` socket responsiveness.
2. **Ping / Latency**: Issues WireGuard-level ICMP echo and measures round-trip time.
3. **MCP Endpoint Probe**: Probes `http://<peer-magicdns>:8016/mcp` with an `initialize` JSON-RPC payload.
4. **Transport Security Audit**: Validates that incoming requests contain valid Host headers matching `allowed_hosts`.
5. **Relay Check**: Inspects whether the connection is Direct UDP or degraded DERP relay.

#### Response Output:
Returns a structured diagnostic report with PASS/WARN/FAIL status and exact corrective actions for any detected anomalies.

---

## 3. Architecture & Implementation Guidelines

* **M1 AnyIO Compliance**: All subprocess calls to `tailscale` or network socket probes must be wrapped in `anyio.to_thread.run_sync` or execute using non-blocking asynchronous clients.
* **M2 Firewall**: Implementation lives strictly in `mcp_servers/omega_hub/` (core services); no stack-specific WAD logic.
* **M23 Failure Integrity**: If `tailscaled` is dead or unreachable, return a structured `error` JSON with explicit error codes (`TAILSCALE_DAEMON_OFFLINE`), never throwing unhandled tracebacks.

*⬡ OMEGA ⬡ SPEC-FEDERATION-MCP-v1.0 ⬡ 2026-09-16*
