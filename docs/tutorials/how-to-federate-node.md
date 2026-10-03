# 🔱 Tutorial: How to Federate a Node
**AP Token**: `AP-TUTORIAL-FEDERATE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_user ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Step-by-step tutorial for federating a new node into the Omega Engine mesh network.
**Prerequisites**: Two machines (Node 0 + Node 1), Tailscale, Docker/Podman, `omega-engine` repo on both
**Tags**: tutorial, federation, node, tailscale, mesh, distributed

---

## Overview

This tutorial walks through **federating a new node (Node 1)** into an existing Omega Engine mesh (Node 0). The federation uses Tailscale for secure mesh networking and the Omega Exchange (port 8019) for file transfer.

**What you'll achieve**: A two-node Omega federation with working handoff, exchange, and health checks.

**Time estimate**: 45-60 minutes

---

## Prerequisites

### Node 0 (Existing - Controller)
- Machine with Omega Engine running
- Tailscale installed and authenticated
- `omega-engine` repo at `~/Documents/Xoe-NovAi/omega-engine`
- Port 8016 (MCP Hub) and 8019 (Exchange) available

### Node 1 (New - Worker)
- Second machine (can be VM, laptop, or cloud instance)
- Tailscale installed and authenticated **on same tailnet**
- Docker/Podman installed
- `omega-engine` repo cloned
- Ports 8016, 8019 available

### Network
- Both nodes on same Tailscale tailnet
- Tailscale MagicDNS enabled
- Direct WireGuard connectivity (verify with `tailscale ping`)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Omega Federation Mesh                     │
├─────────────────────────────────────────────────────────────┤
│  Node 0 (Controller)          Node 1 (Worker)               │
│  ┌─────────────────────┐      ┌─────────────────────┐       │
│  │ Omega Hub :8016     │◄────►│ Omega Hub :8016     │       │
│  │ Omega Exchange :8019│◄────►│ Omega Exchange :8019│       │
│  │ Hivemind            │      │ Hivemind            │       │
│  │ Entities: Kali,     │      │ Entities: Lilith,   │       │
│  │   Maat, Prometheus  │      │   Roc Racoon, etc.  │       │
│  └─────────────────────┘      └─────────────────────┘       │
│         ▲                             ▲                      │
│         │      Tailscale Mesh         │                      │
│         │    (MagicDNS + WireGuard)   │                      │
│         ▼                             ▼                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Prepare Node 0 (Controller)

### 1.1 Verify Node 0 Services

```bash
# On Node 0
cd ~/Documents/Xoe-NovAi/omega-engine

# Check hub health
curl http://localhost:8016/health
# {"status":"healthy","version":"1.6.0-alpha.1"}

# Check exchange health
curl http://localhost:8019/healthz
# 200 OK
```

### 1.2 Configure Node 0 Identity

```bash
# Set Node 0 identity (run once)
export OMEGA_NODE_NAME="n0"
export OMEGA_NODE_HOST="n0.tail51f14a.ts.net"  # Your Tailscale MagicDNS name
export OMEGA_SELF_IP="100.123.51.67"  # Your Tailscale IP

# Add to ~/.bashrc or ~/.profile for persistence
echo 'export OMEGA_NODE_NAME="n0"' >> ~/.bashrc
echo 'export OMEGA_NODE_HOST="n0.tail51f14a.ts.net"' >> ~/.bashrc
echo 'export OMEGA_SELF_IP="100.123.51.67"' >> ~/.bashrc
```

### 1.3 Start Node 0 Services

```bash
# Start hub (MCP server)
cd ~/Documents/Xoe-NovAi/omega-engine
python -m mcp_servers.omega_hub.server &
HUB_PID=$!

# Start exchange server
python scripts/omega_exchange_server.py --root ~/omega-exchange --port 8019 &
EXCHANGE_PID=$!

# Verify both running
curl http://localhost:8016/health
curl http://localhost:8019/healthz
```

---

## Step 2: Prepare Node 1 (Worker)

### 2.1 Clone Repository

```bash
# On Node 1
cd ~/Documents
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
```

### 2.2 Configure Node 1 Identity

```bash
# Set Node 1 identity (CRITICAL - must be unique)
export OMEGA_NODE_NAME="n1"
export OMEGA_NODE_HOST="n1.tail51f14a.ts.net"  # Your Tailscale MagicDNS name
export OMEGA_SELF_IP="100.98.76.54"  # Your Tailscale IP

# Add to ~/.bashrc for persistence
echo 'export OMEGA_NODE_NAME="n1"' >> ~/.bashrc
echo 'export OMEGA_NODE_HOST="n1.tail51f14a.ts.net"' >> ~/.bashrc
echo 'export OMEGA_SELF_IP="100.98.76.54"' >> ~/.bashrc

# Verify
echo "Node: $OMEGA_NODE_NAME"
echo "Host: $OMEGA_NODE_HOST"
echo "IP: $OMEGA_SELF_IP"
```

### 2.2 Configure Tailscale

```bash
# Ensure Tailscale is running
sudo tailscale up

# Verify MagicDNS works
tailscale status
# Should show both nodes

# Test connectivity
tailscale ping n0.tail51f14a.ts.net
# Should succeed with direct WireGuard
```

### 2.3 Start Node 1 Services

```bash
cd ~/Documents/omega-engine

# Start hub
python -m mcp_servers.omega_hub.server &
HUB_PID=$!

# Start exchange server (CRITICAL: use the fixed server from ba8a3849)
python scripts/omega_exchange_server.py --root ~/omega-exchange --port 8019 &
EXCHANGE_PID=$!

# Verify
curl http://localhost:8016/health
curl http://localhost:8019/healthz
```

---

## Step 3: Verify Cross-Node Connectivity

### 3.1 Test Exchange Connectivity

```bash
# From Node 1, test Node 0 exchange
curl https://n0.tail51f14a.ts.net:8019/healthz
# Should return 200 OK

# From Node 0, test Node 1 exchange
curl https://n1.tail51f14a.ts.net:8019/healthz
# Should return 200 OK
```

### 3.2 Test MCP Hub Connectivity

```bash
# From Node 1, test Node 0 hub
curl https://n0.tail51f14a.ts.net:8016/health
# {"status":"healthy","version":"1.6.0-alpha.1"}

# From Node 0, test Node 1 hub
curl https://n1.tail51f14a.ts.net:8016/health
# {"status":"healthy","version":"1.6.0-alpha.1"}
```

### 3.3 Run Federation Diagnostics

```bash
# From Node 0, run full diagnostic
python -c "
import asyncio
from omega.federation import diagnose
result = asyncio.run(diagnose('n1.tail51f14a.ts.net'))
print(result)
"
```

**Expected**: All checks PASS (daemon health, ping/latency, MCP endpoint, transport security, relay status)

---

## Step 4: Test Handoff Federation

### 4.1 Send Test Handoff (Node 0 → Node 1)

```bash
# On Node 0, send handoff to Lilith on Node 1
python -c "
import asyncio
from mcp_servers.omega_hub.hub_tools.hivemind_handoff import hivemind_handoff

async def send():
    result = await hivemind_handoff(
        action='submit',
        target_entity='lilith-n1',  # Node-qualified!
        target_channel='opencode',
        source_entity='kali',
        source_channel='opencode',
        task='Federation test from Node 0',
        context='Testing cross-node handoff',
        priority=2
    )
    print(result)

asyncio.run(send())
"
```

### 4.2 Verify Receipt (Node 1)

```bash
# On Node 1, check handoff received
python -c "
import asyncio
from mcp_servers.omega_hub.hub_tools.hivemind_handoff import hivemind_handoff

async def check():
    # Check inbox for lilith-n1
    result = await hivemind_handoff(
        action='inbox',
        target_entity='lilith-n1',
        target_channel='opencode'
    )
    print('Inbox:', result)
    
    # Check direct store (authoritative)
    import json, glob
    for f in glob.glob('data/handoff/pending/*.json'):
        with open(f) as fp:
            data = json.load(fp)
            if data.get('target_entity') == 'lilith-n1':
                print('Found in store:', data['packet_id'], data['task'])

asyncio.run(check())
"
```

**Critical**: Always use **node-qualified names** (`lilith-n1`, not `lilith`) — the node suffix is the address, not a spelling variant.

---

## Step 5: Test File Exchange

### 5.1 Node 0 Publishes File

```bash
# On Node 0, create test file
echo "Hello from Node 0 at $(date)" > ~/omega-exchange/federation_test.txt

# Verify it appears in manifest
curl https://n0.tail51f14a.ts.net:8019/manifest.json | jq '.entries[] | select(.name=="federation_test.txt")'
```

### 5.2 Node 1 Pulls File

```bash
# On Node 1, pull the file
curl -o federation_test.txt https://n0.tail51f14a.ts.net:8019/federation_test.txt

# Verify SHA256 matches manifest
sha256sum federation_test.txt
curl -s https://n0.tail51f14a.ts.net:8019/manifest.json | jq -r '.entries[] | select(.name=="federation_test.txt") | .sha256'
# Should match!
```

### 5.3 Verify Read-Only Enforcement

```bash
# This should fail with 405
curl -X PUT https://n0.tail51f14a.ts.net:8019/test.txt -d "data"
# {"error":"method_not_allowed","detail":"PUT is not supported. This origin is READ-ONLY."}
```

---

## Step 6: Configure Entities for Federation

### 6.1 Node 0 Entities (Controller Side)

```bash
# Entities that run on Node 0
# kali, maat, prometheus, kali-n0, maat-n0, etc.
# These are the "controller" entities
```

### 6.2 Node 1 Entities (Worker Side)

```bash
# Entities that run on Node 1
# lilith-n1, roc_racoon, jem, etc.
# These are the "worker" entities
```

### 6.3 Configure Hivemind for Cross-Node

```bash
# On both nodes, ensure hivemind config allows cross-node
# The handoff system automatically routes based on node suffix
# No additional config needed if node suffixes are correct
```

---

## Step 7: Run Federation Health Check

```bash
# From Node 0, run comprehensive check
python -c "
import asyncio
from omega.hub import get_hardware_stats
from mcp_servers.omega_hub.hub_tools.omega_federation_status import omega_federation_status
from mcp_servers.omega_hub.hub_tools.omega_federation_diagnose import omega_federation_diagnose

async def health_check():
    # Local hardware
    hw = await get_hardware_stats()
    print('Local HW:', hw['cpu']['avg_percent'], 'CPU,', hw['memory']['available_mb'], 'MB avail')
    
    # Federation status
    status = await omega_federation_status()
    print('Federation:', status)
    
    # Full diagnose
    diag = await omega_federation_diagnose('n1.tail51f14a.ts.net')
    print('Diagnose:', diag)

asyncio.run(health_check())
"
```

---

## Step 8: Automate with Systemd (Production)

### 8.1 Node 0 Service

```ini
# /etc/systemd/user/omega-hub.service
[Unit]
Description=Omega Hub (Node 0)
After=network-online.target tailscale.service
Wants=tailscale.service

[Service]
Type=simple
WorkingDirectory=/home/user/Documents/Xoe-NovAi/omega-engine
Environment=OMEGA_NODE_NAME=n0
Environment=OMEGA_NODE_HOST=n0.tail51f14a.ts.net
Environment=OMEGA_SELF_IP=100.123.51.67
ExecStart=/home/user/.venv/bin/python -m mcp_servers.omega_hub.server
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```ini
# /etc/systemd/user/omega-exchange.service
[Unit]
Description=Omega Exchange (Node 0)
After=network-online.target tailscale.service
Wants=tailscale.service

[Service]
Type=simple
WorkingDirectory=/home/user/Documents/Xoe-NovAi/omega-engine
Environment=OMEGA_NODE_NAME=n0
Environment=OMEGA_NODE_HOST=n0.tail51f14a.ts.net
Environment=OMEGA_SELF_IP=100.123.51.67
ExecStart=/home/user/.venv/bin/python scripts/omega_exchange_server.py --root /home/user/omega-exchange --port 8019
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

### 8.2 Node 1 Service (adjust paths/names)

```ini
# Same as above but:
Environment=OMEGA_NODE_NAME=n1
Environment=OMEGA_NODE_HOST=n1.tail51f14a.ts.net
Environment=OMEGA_SELF_IP=100.98.76.54
```

### 8.3 Enable and Start

```bash
# On both nodes
systemctl --user daemon-reload
systemctl --user enable --now omega-hub.service omega-exchange.service

# Check status
systemctl --user status omega-hub.service omega-exchange.service
```

---

## Troubleshooting

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| `curl` to peer fails | Tailscale not connected | `tailscale up`; check `tailscale status` |
| Exchange returns 404 | Wrong path | Use `/healthz` not `/health` for exchange |
| Handoff not received | Wrong entity name | Use `lilith-n1` not `lilith` |
| Exchange manifest shows wrong node | `OMEGA_SELF_IP` not set | Set env vars before starting exchange |
| MCP hub not reachable | Port 8016 blocked | Check firewall; Tailscale allows all ports by default |
| `tailscale ping` fails | Different tailnets | Ensure both nodes on same tailnet |

---

## Verification Checklist

```bash
# Run this on both nodes to verify federation
cat << 'EOF' > verify_federation.sh
#!/bin/bash
set -e

echo "=== Federation Verification ==="
echo "Node: $(hostname) ($OMEGA_NODE_NAME)"

echo "1. Local services:"
curl -sf http://localhost:8016/health | jq -r '.status'
curl -sf http://localhost:8019/healthz

echo "2. Peer services:"
PEER="n0.tail51f14a.ts.net"
if [ "$OMEGA_NODE_NAME" = "n0" ]; then PEER="n1.tail51f14a.ts.net"; fi
curl -sf https://$PEER:8016/health | jq -r '.status'
curl -sf https://$PEER:8019/healthz

echo "3. Handoff test:"
python -c "
import asyncio, json
from mcp_servers.omega_hub.hub_tools.hivemind_handoff import hivemind_handoff
async def test():
    r = await hivemind_handoff(action='submit', target_entity='lilith-n1', target_channel='opencode', source_entity='kali', source_channel='opencode', task='verify', context='test', priority=2)
    print('Submit:', json.loads(r).get('packet_id'))
asyncio.run(test())
"

echo "4. File exchange:"
echo "test" > ~/omega-exchange/verify.txt
curl -sf https://$PEER:8019/verify.txt -o /tmp/verify.txt
cat /tmp/verify.txt

echo "=== All checks passed ==="
EOF
chmod +x verify_federation.sh
./verify_federation.sh
```

---

## Next Steps

1. **Add more nodes** — Repeat for n2, n3, etc.
2. **Configure entity distribution** — Assign entities to nodes based on workload
3. **Set up monitoring** — Federation health dashboards
4. **Implement backup** — Exchange replication for disaster recovery
5. **Add authentication** — Beyond Tailscale (M18)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ TUTORIAL-FEDERATE-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

