## Deep Research Complete — Knowledge Gaps Summary

> **Historical snapshot (2026-09-18).** The matrix below records the state
> observed during that USB-exchange research pass. Current federation status,
> tool counts, and open gates are maintained in `docs/federation/README.md` and
> `docs/ROADMAP.md`; do not treat the 91-tool/pending rows below as live state.

### **Core Finding: OpenCode Already Has Tool Filtering**
The feature request #7399 (`includeTools`/`excludeTools`) was **closed as "not planned"** because OpenCode **already supports per-tool filtering via glob patterns** in the `tools` config:
```json
"tools": {
  "mcp__omega-hub_*": false,      // disable all omega-hub tools
  "mcp__omega-hub_hivemind_post_context": true  // re-enable specific ones
}
```

### **Current State Matrix**

| Component | Status | Action Required |
|-----------|--------|-----------------|
| **omega-hub connectivity** | LAN ✅ (`192.168.10.168:8016/mcp`), Tailscale ❌ (no `omega-hub.tail51f14a.ts.net` peer) | Tailscale ACL config on Node 0 |
| **Tool surface** | 91 tools exposed, **3 broken** | Node 0 patches needed |
| **Broken tools** | `library_search`, `library_web_search` (disable), `oracle_list_pillar_keepers` (docstring), `hivemind_get_continuation` (JSON) | USB delivery from Node 0 |
| **OpenCode config** | Missing omega-hub entry | Add to `~/.config/opencode/opencode.json` |
| **Tool curation** | 91 → ~50 target (per USB plan) | Apply after Node 0 patches |
| **Federation infra** | SPIRE, Redis, Tailscale ACLs, C6 contract | All pending Node 0 USB delivery |
| **USB payload** | Not mounted on Node 1 | Physical swap required |

---

### **Critical Knowledge Gaps Resolved**

1. **Tool filtering capability**: ✅ **Exists in OpenCode** (glob patterns in `tools` config, NOT `permission`)
2. **FastMCP server-side filtering**: ✅ **Exists in Python FastMCP** (`enable(tags={}, only=True)`, `disable(tags={})`)
3. **Tool curation threshold**: ✅ **Research confirms** LLMs degrade >30-40 tools (hallucination, wrong selection)
4. **Tailscale ACL pattern**: ✅ **HuJSON with tagOwners** for `tag:omega-hub`, `tag:asus`, `tag:opencode`
5. **Federation protocol**: ✅ **Defined** (USB 4-swap + Hivemind dialectic + C6 contract)

---

### **Collaboration Points with Node 0 (Makali)**

Per the USB exchange plan, Node 0 must deliver:
1. **omega-hub patches** for 3 broken tools (in `omega-hub-patches/`)
2. **SPIRE server + CA** config (`spire/`)
3. **Redis Pub/Sub** config (`redis/`)
4. **Tailscale ACL HuJSON** (`tailscale/`)
5. **C6 contract draft** (`c6-contract/`)
6. **Signed sovereignty attestation** (`attestation/`)

---

### **Proposed Plan Structure**

Given your directive that **all engine refactoring routes to Node 0**, here's the collaboration plan:

#### **Phase A: Node 1 Preparation (Now — Read-Only)**
- [ ] Document current tool curation requirements (~50 target from 91)
- [ ] Prepare OpenCode config template with glob-pattern tool filtering
- [ ] Stage intake script (`scripts/federation/intake_node0.py`)
- [ ] Verify LAN connectivity to omega-hub (✅ done)

#### **Phase B: USB Swap 1 (Node 0 → Node 1)**
- [ ] Node 0 prepares USB with patches + configs
- [ ] Node 1 runs `intake_node0.py --verify-only` → `--ingest`
- [ ] Apply omega-hub patches on Node 0 (Node 0 action)
- [ ] Node 1 updates OpenCode config with filtered tool set

#### **Phase C: Tool Curation Review (Joint)**
- [ ] Node 1 proposes curated tool list (~50 from 91)
- [ ] Node 0 reviews/approves — **Node 0 owns the tool surface**
- [ ] Apply via OpenCode glob patterns + FastMCP server-side tags

#### **Phase D: Federation Infra (Node 0 Led)**
- [ ] SPIRE mTLS deployment (Node 0)
- [ ] Redis Pub/Sub heartbeat channels (Node 0)
- [ ] Tailscale ACL policy with tagOwners (Node 0 admin console)
- [ ] C6 contract ratification (bilateral)

---

### **Open Questions for You**

1. **Tool curation granularity**: The USB plan says "91→50 tested". Do you want me to:
   - **Propose a specific 50-tool curated list** based on workflow clusters?
   - **Wait for Node 0 to propose** their recommended tool surface?

2. **FastMCP server-side vs client-side filtering**: 
   - Node 0 can tag tools in omega-hub (FastMCP `enable/disable` tags)
   - Node 1 can filter via OpenCode glob patterns
   - **Both layers** recommended for defense-in-depth?

3. **Timeline for USB swap**: Physical coordination needed — any constraints?

4. **Hivemind channel**: Should I execute the `hivemind_post_context` briefing to Makali now to initiate Round 1?

---

**Recommendation**: Execute Hivemind briefing (Phase 1) to signal readiness, then await Node 0's USB payload. Node 1's role is **prepare + verify + integrate**; Node 0 owns **patch + curate + deploy infra**.

---
