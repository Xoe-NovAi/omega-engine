# CROSS-NODE COMMUNICATION: HIVEMIND + TAILSCALE EXPERIENCE REPORT

> **📅 HISTORICAL SNAPSHOT — dated 2026-09-28. Do not read the tool counts below
> as current.** This report records the state of the federation bridge on
> 2026-09-28, when the hub served **54 tools**. As of **2026-10-03** the live hub
> serves **55** — the four control planes (kill/escalate/approve/throttle) landed
> as the unified `control` tool in `5e97ef84`. The "54 tools" figures are left
> verbatim below as a record of that date, per M28 (nothing is rewritten
> retroactively). For the current count see `docs/guides/how-to-debug-hub.md`.

## What Went Well

### 1. The MCP Bridge (Port 8016) is the Transport That Works
The entire cross-node communication story runs through a single HTTPS + JSON-RPC
endpoint at https://n0.tail51f14a.ts.net:8016/mcp. This is clean, reliable, and
already proven. 54 tools exposed including hivemind_handoff, hivemind_awareness,
omega_federation_status, library_*, omega_memory_*, and more.

### 2. Inline Context Delivery Works Perfectly
A 24 KB payload (6 files, VNR study pack) was delivered as inline JSON context
in a single hivemind_handoff call. No file sync, no chunking, no fragmentation.
The recipient's agent gets full text access immediately after accept().

### 3. One Enabling Action Unlocks Everything
The only thing that needed to happen on Node 1 was enabling the omega-hub MCP
server in OpenCode TUI. Once enabled, GE-N1 had instant access to all 54 tools
including the handoff system. No agent configuration, no credentials exchange,
no firewall changes.

### 4. The Architecture is Simple and Correct
Pull model: packets live on the source node. Recipients query the bridge.
No replication, no sync conflict, no stale copies. Tailscale provides the
encrypted L2 tunnel. The MCP bridge is the application layer.

### 5. Tailscale Itself is Solid
Mesh is up. MagicDNS resolves. Direct WireGuard path (not DERP relay) between
n0 (100.123.51.67) and n1 (100.89.40.17). Both nodes online, tagged, healthy.

---

## What Could Go Better

### 1. No Discovery Mechanism
GE-N1 searched 58 seconds for the VNR packet on local Node 1 filesystem before
someone realized they needed to enable the MCP server. There is no signal that
tells an agent "there are packets waiting for you on the bridge."

**Proposal:** A bootstrap file (e.g., ~/.omega-handoff.md) on each node listing
the bridge endpoint, the local identity, and the exact command to check pending
packets. Or an auto-pull hook on session start.

### 2. Port 8017 (Exchange Pipe) is Broken
The sanctioned file-serving channel at https://n0.tail51f14a.ts.net:8017/
returns SearXNG HTML instead of the exchange files. The path /full-pack-20260926/
is supposed to serve the 43-file governance package but something squatted the
port. This blocks bulk artifact delivery.

**Proposal:** Identify and fix the port conflict. Add a health check that fails
loudly when the exchange pipe returns unexpected content.

### 3. Entity Naming Convention is Unclear
I targeted entity "ge-n1" but I don't know if that matches how GE-N1
registers. The system uses target_entity for filtering, but the list action
with status=pending returned ALL pending packets regardless of target — so
filtering may not be happening as documented.

**Proposal:** Document the exact naming convention. Add a self-registration step
where an agent declares its entity name and the system validates it.

### 4. No Delivery Receipt
We don't know when GE-N1 actually read the VNR study pack or the tutorial.
The packet status goes to "active" on accept, but there's no read receipt.
If GE-N1 accepted but never read the context, we'd have no way to know.

**Proposal:** Add a "read" action that marks the packet as read with a timestamp.
Or have the accepting agent post an acknowledgment back to the sender.

### 5. Session Registration is Optional But Should Be Required
hivemind_awareness showed an empty list. No agents have registered heartbeats.
The system works without registration (you can submit and accept packets), but
registration would enable discoverability and presence awareness.

**Proposal:** Make hivemind_awareness heartbeat a required first step for any
agent joining the mesh. Auto-register on first tool call.

### 6. The list Action Appears to Ignore target_entity
When I called hivemind_handoff list status=pending, it returned all pending
packets including the VNR one targeted at ge-n1. The documentation suggests
it should filter by the calling agent's identity, but the behavior seems to
return everything.

**Proposal:** Either implement the documented filtering, or correct the
documentation to match actual behavior.

---

## Key Insights for Improvement

### Insight 1: The MCP Bridge IS the Federation Layer
We spent days debugging NFS exports, USB sneakernet degradation, and SHA ledger
mismatches. The working path was always there: a JSON-RPC tool call over the
Tailscale tunnel. The federation works through the bridge. The bridge works.
The handoff protocol works. Everything else was premature optimization.

### Insight 2: Enabling the Client Is the Only Step That Matters
No amount of server-side work matters if the client TUI doesn't have the MCP
server enabled. This is the single point of failure. Any node joining the
federation needs: (1) Tailscale installed and joined, (2) MCP server enabled
in their agent TUI. Everything else is automatic.

### Insight 3: Registration Should Be Automatic
The hivemind_awareness system exists but is optional. If it were required for
any agent to participate, the system would be more robust, more discoverable,
and failures would be caught earlier. An agent that connects but doesn'''t
register is invisible.

### Insight 4: Bulk Transfer and Handoff Are Different Problems
Handoffs (24 KB) work fine over MCP. Bulk packages (43 files, 122 KB zip) need
the exchange pipe (port 8017). Don'''t try to push large files through JSON-RPC.
Keep the two channels separate and healthy.

### Insight 5: The System is Simple Enough to Understand
The entire cross-node architecture fits in one diagram: Node 0 serves MCP on
8016, Tailscale tunnels to Node 1, client calls tools, packets live on source.
That simplicity is a feature. Don'''t over-engineer it.

---

## Recommended Actions (Priority Order)

1. **Fix the 8017 exchange pipe** (blocking bulk transfer)
2. **Add a bootstrap file** on each node with bridge URL + check-command
3. **Add auto-pull on session start** (check pending handoffs automatically)
4. **Add read receipts** to the handoff system
5. **Make registration required** for mesh participation
6. **Document the entity naming convention** clearly
7. **Fix or document the list filtering behavior**

---

## Files Referenced

- This report: submitted as a handoff packet
- Handoff delivery report: docs/team/HANDOFF_DELIVERY_REPORT_20260928.md
- VNR study pack: docs/vnr-study-pack/ (source of truth, 6 files)
- Handoff packet: ho_29738346af4e (VNR pack), ho_7b77a3a2d12c (tutorial)

## The Win

The federation works. The bridge works. The handoff protocol works. GE-N1 is
operational on Node 1 with full tool access. The remaining work is polish:
fixing the exchange pipe, adding discoverability, and making registration
automatic. The hard part is done.

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ FEDERATION-EXPERIENCE ⬡ 2026-09-28*
