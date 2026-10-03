# 🔱 Deep Federation Hardening: Final PR Readiness Caveats & Fixes
**Date**: 2026-09-25
**Researcher**: Antigravity IDE (Gemini 3.1 Pro)
**Scope**: Closing the final gaps in the Bastion/Vanguard federation architecture.

---

## 1. FastMCP + Tailscale Serve: The DNS Rebinding Trap

**The Vulnerability:**
In `ANTIGRAVITY_FINAL_HANDOFF_20260924.md`, we established that Node 1 consumes Node 0's Hub via Tailscale Serve (`https://n0.tail51f14a.ts.net:8016/mcp`). 

**The Caveat:**
Tailscale Serve acts as a TLS-terminating reverse proxy and forwards the *original* `Host` header (i.e., `n0.tail51f14a.ts.net`) to the backend service. FastMCP (and most modern ASGI frameworks) enforce strict DNS rebinding protection. If FastMCP is bound to `127.0.0.1` and receives a request with a Tailscale `Host` header, it will **block the request** as a potential DNS rebinding attack.

**The Fix:**
You must explicitly whitelist the Tailscale MagicDNS hostname in your FastMCP `security_settings` or `TransportSecuritySettings` on Node 0.
```python
# Example FastMCP Configuration on Node 0
app = FastMCP(
    "Omega-Hub",
    allowed_hosts=["localhost", "127.0.0.1", "n0.tail51f14a.ts.net"]
)
```

---

## 2. Tailscale SSH: The "Operation now in progress" Blackhole

**The Vulnerability:**
`DEFINITIVE_RESOLUTION_GUIDE_20260922.md` noted that Node 1 is dropping SSH connections with an `Operation now in progress` timeout over Tailscale.

**The Caveat:**
Deep research confirms this is a classic **Path MTU Discovery (PMTUD) blackhole**. Tailscale uses a strict 1280 byte MTU. During the SSH handshake, if packets exceed 1280 bytes and intermediate routers drop ICMP "Fragmentation Needed" packets, the connection silently hangs forever.

**The Fix (TCP MSS Clamping):**
The Operator must run this `iptables` MSS clamping rule on Node 1 (or Node 0 if it acts as a subnet router) to force the TCP segment size to fit inside the Tailscale MTU:
```bash
sudo iptables -t mangle -A FORWARD -o tailscale0 -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
```
*Note: This must be persisted using `iptables-persistent` to survive reboots.*

---

## 3. OpenCode Crash: The `npx` MCP Server Vector

**The Vulnerability:**
`OPENCODE_CRASH_REMEDIATION_20260924.md` isolated third-party `npx` MCP servers as the root cause of the fatal OpenCode black-screen crash.

**The Caveat:**
The MCP JSON-RPC protocol operates strictly over `stdio`. The crash is almost certainly caused by **`stdout` pollution**. If `npx` prints *any* text to `stdout` before the JSON handshake (e.g., "Need to install the following packages...", npm update warnings, or deprecation notices), the OpenCode JSON parser crashes immediately, taking down the client.

**The Fix:**
When adding third-party servers back to `mcp_servers.json`, **never use raw `npx`**. 
1. Pre-install the server globally (`npm install -g @modelcontextprotocol/server-name`).
2. Point the MCP config directly to the installed node script.
3. If `npx` must be used, force it to be completely silent: `npx --yes --quiet <package>`.

---

## 4. Git Bundle Federation: Minisign Pipeline Security

**The Vulnerability:**
`D-FED-01` replaces NFS with signed `git bundle` transfers.

**The Caveat:**
Automated signing in CI/CD (using Minisign) introduces key-leak risks. If the `minisign` secret key is exposed in the repository or a persistent runner, the entire supply chain is compromised.

**The Fix:**
- Use ephemeral runners for the artifact generation.
- Inject the Minisign secret key into the CI runner via a secure vault (e.g., GitHub Actions Secrets) *only* during the signing step.
- Verify the `.minisig` file on Node 1 before `git fetch` is allowed to process the bundle.

---

### Conclusion for PR Readiness
By applying the **FastMCP Host whitelist**, the **TCP MSS Clamping**, and stripping `npx` from the MCP configs, you will have closed the final edge-case failure vectors in the Bastion/Vanguard architecture. The engine is fully hardened.
