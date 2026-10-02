# 🔱 How-to: Configure the Omega Exchange
**AP Token**: `AP-GUIDE-CONFIGURE-EXCHANGE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_proc ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Step-by-step guide for configuring the Omega Exchange (port 8019) for file distribution across federated nodes.
**Tags**: how-to, exchange, configuration, federation, file-transfer
**Cross-references**: scripts/omega_exchange_server.py, docs/federation/HIVE_SYNC_GUIDE_20261002.md, docs/federation/COMMS_CHANNEL_REVIEW_20261002.md

---

## Overview

The **Omega Exchange** is a read-only HTTP file server (port 8019) that enables secure file distribution across federated Omega nodes. It serves manifests and files with SHA256 verification, enforces read-only access, and prevents path traversal.

**What you'll configure**: A production-ready Exchange server with proper identity, TLS, and federation settings.

**Time estimate**: 15-20 minutes

---

## Prerequisites

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate

# Verify exchange script exists
ls scripts/omega_exchange_server.py
```

---

## Step 1: Prepare Exchange Root Directory

```bash
# Create exchange root
mkdir -p ~/omega-exchange

# Set permissions (readable by exchange process)
chmod 755 ~/omega-exchange
```

---

## Step 2: Configure Node Identity (CRITICAL)

**Each node MUST have unique identity** for the manifest to correctly identify the serving node.

```bash
# Set environment variables (add to ~/.bashrc for persistence)
export OMEGA_NODE_NAME="n0"           # Unique: n0, n1, n2, etc.
export OMEGA_NODE_HOST="n0.tail51f14a.ts.net"  # Tailscale MagicDNS name
export OMEGA_SELF_IP="100.123.51.67"  # Your Tailscale IP

# Verify
echo "Node: $OMEGA_NODE_NAME"
echo "Host: $OMEGA_NODE_HOST"
echo "IP: $OMEGA_SELF_IP"
```

**Why this matters**: The exchange manifest includes `served_by` and `url_form` fields. Without correct identity, Node 1's manifest would claim to be Node 0 (the COM-08 defect).

---

## Step 3: Configure Exchange Root Content

```bash
# Add files to serve
echo "Hello from Node 0" > ~/omega-exchange/hello.txt
mkdir -p ~/omega-exchange/configs
cp config/providers.yaml ~/omega-exchange/configs/
mkdir -p ~/omega-exchange/wads
cp config/wads/_omega_default.wad ~/omega-exchange/wads/ 2>/dev/null || true

# Verify structure
find ~/omega-exchange -type f | head -20
```

---

## Step 4: Start Exchange Server

```bash
# Development mode
cd ~/Documents/Xoe-NovAi/omega-engine
python scripts/omega_exchange_server.py --root ~/omega-exchange --port 8019

# Production: use systemd (see Step 7)
```

**Verify**:
```bash
# Health check
curl http://localhost:8019/healthz
# 200 OK

# Manifest
curl http://localhost:8019/manifest.json | jq .
```

**Expected manifest structure**:
```json
{
  "served_by": "n0",
  "url_form": "https://n0.tail51f14a.ts.net:8019",
  "entries": [
    {"name": "hello.txt", "size": 18, "sha256": "..."},
    {"name": "configs/providers.yaml", "size": 2048, "sha256": "..."}
  ],
  "entry_count": 2,
  "cache_key": "1727890123.45:2"
}
```

---

## Step 5: Verify Read-Only Enforcement

```bash
# These should ALL return 405 Method Not Allowed
curl -X PUT http://localhost:8019/test.txt -d "data"
curl -X POST http://localhost:8019/test.txt -d "data"
curl -X DELETE http://localhost:8019/test.txt
curl -X PATCH http://localhost:8019/test.txt -d "data"

# Expected response:
# {"error":"method_not_allowed","detail":"PUT is not supported. This origin is READ-ONLY."}
```

---

## Step 6: Verify Path Traversal Protection

```bash
# These should ALL return 404 (not 500, not file contents)
curl "http://localhost:8019/..%2fetc%2fpasswd"
curl "http://localhost:8019/%2e%2e%2fetc%2fpasswd"
curl "http://localhost:8019/../../etc/passwd"
curl "http://localhost:8019/%252e%252e%252fetc%252fpasswd"

# Expected: 404 with JSON error envelope
# {"error":"not_found","detail":"File not found"}
```

---

## Step 7: Verify SHA256 Integrity

```bash
# Get file with SHA256 header
curl -I http://localhost:8019/hello.txt
# Should include: X-Omega-SHA256: <sha256>

# Verify content matches hash
curl -s http://localhost:8019/hello.txt | sha256sum
# Should match X-Omega-SHA256 header
```

---

## Step 8: Production Deployment (systemd)

### 8.1 Create Service Files

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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

### 8.2 Port Configuration (if not 8019)

```ini
# /etc/systemd/user/omega-exchange.service.d/10-port-8019.conf
[Service]
Environment=OMEGA_EXCHANGE_PORT=8019
```

### 8.3 Enable and Start

```bash
systemctl --user daemon-reload
systemctl --user enable --now omega-exchange.service

# Check status
systemctl --user status omega-exchange.service

# View logs
journalctl --user -u omega-exchange.service -f
```

---

## Step 9: Federation Configuration

### 9.1 Node 0 to Node 1 Connectivity

```bash
# From Node 0, test Node 1 exchange
curl https://n1.tail51f14a.ts.net:8019/healthz
curl https://n1.tail51f14a.ts.net:8019/manifest.json | jq .

# From Node 1, test Node 0 exchange
curl https://n0.tail51f14a.ts.net:8019/healthz
curl https://n0.tail51f14a.ts.net:8019/manifest.json | jq .
```

### 9.2 Verify Manifest Identity

```bash
# Each node's manifest MUST show its own identity
curl -s https://n0.tail51f14a.ts.net:8019/manifest.json | jq '.served_by, .url_form'
# "n0"
# "https://n0.tail51f14a.ts.net:8019"

curl -s https://n1.tail51f14a.ts.net:8019/manifest.json | jq '.served_by, .url_form'
# "n1"
# "https://n1.tail51f14a.ts.net:8019"
```

**If both show "n0"**: Node 1's `OMEGA_NODE_NAME`/`OMEGA_NODE_HOST`/`OMEGA_SELF_IP` not set correctly.

---

## Step 10: Cache Configuration

The exchange uses a manifest cache keyed on `(max_mtime, entry_count)`.

```bash
# Cache behavior:
# - Cache invalidates when directory mtime changes OR entry count changes
# - Cache key: (max_mtime, entry_count)
# - Stale cache possible if: add+remove same time, or copy preserving mtime

# To force refresh:
touch ~/omega-exchange/  # Updates directory mtime
# Or restart exchange service
systemctl --user restart omega-exchange.service
```

---

## Step 11: Monitoring & Health Checks

### 11.1 Health Endpoint

```bash
# Basic health
curl http://localhost:8019/healthz
# 200 OK

# With JSON
curl -H "Accept: application/json" http://localhost:8019/healthz
```

### 11.2 Metrics (if enabled)

```bash
# Exchange logs to journal
journalctl --user -u omega-exchange.service -f

# Key log lines:
# "Serving manifest with N entries"
# "Serving file: hello.txt (sha256: ...)"
# "405 Method Not Allowed: PUT /test.txt"
```

---

## Troubleshooting

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| `curl` returns 000 | Service not running | `systemctl --user status omega-exchange.service` |
| Manifest shows wrong node | Identity env vars not set | Set `OMEGA_NODE_NAME`, `OMEGA_NODE_HOST`, `OMEGA_SELF_IP` |
| 404 for existing file | Path mismatch | Check file exists in `--root` directory |
| SHA256 mismatch | File changed after manifest | Touch directory or restart service |
| TLS errors | Certificates missing | Use Tailscale HTTPS (MagicDNS provides certs) |
| Cache stale | mtime/entry_count unchanged | `touch <root>` or restart |

---

## Security Checklist

| Item | Verified |
|------|----------|
| Read-only enforcement (405 on write) | ☐ |
| Path traversal protection (404 on `..`) | ☐ |
| SHA256 headers on all files | ☐ |
| Manifest identity correct | ☐ |
| Tailscale HTTPS only | ☐ |
| No symlinks in exchange root | ☐ |
| Cache invalidation works | ☐ |
| systemd service configured | ☐ |
| Logs accessible | ☐ |

---

## Related Guides

- [How to Federate a Node](../tutorials/how-to-federate-node.md)
- [Hive Sync Guide](../federation/HIVE_SYNC_GUIDE_20261002.md)
- [Comms Channel Review](../federation/COMMS_CHANNEL_REVIEW_20261002.md)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ GUIDE-CONFIGURE-EXCHANGE-v1.0.0 ⬡ 2026-10-02 ⬡*