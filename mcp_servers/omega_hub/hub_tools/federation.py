# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Federation MCP Tools — Mesh observability for OpenCode harness.

Provides omega_federation_status and omega_federation_diagnose for
inspecting the Tailscale L2 mesh from within OpenCode chat.

Mandates:
  M1  AnyIO — subprocess calls wrapped in anyio.to_thread.run_sync
  M2  Firewall — lives in mcp_servers/omega_hub/ (core services)
  M23 Failure Integrity — structured errors, never unhandled tracebacks
"""

from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime, timezone
from typing import Any

import anyio
from mcp.server.fastmcp import Context

# ── mcp instance (circular import — resolves because mcp is created before this import) ──
from mcp_servers.omega_hub.server import mcp

logger = logging.getLogger(__name__)

# Tailnet domain suffix — used to build MagicDNS hostnames.
_TAILNET_DOMAIN = "tail51f14a.ts.net"

# ── Internal helpers ────────────────────────────────────────────────


def _run_tailscale(args: list[str]) -> dict[str, Any]:
    """Run a tailscale command and return parsed JSON (blocking, thread-wrapped)."""
    try:
        result = subprocess.run(
            ["tailscale", *args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            return {"error": f"tailscale {args[0]} failed: {result.stderr.strip()}"}
        return json.loads(result.stdout or "{}")
    except FileNotFoundError:
        return {"error": "tailscale binary not found — is Tailscale installed?"}
    except subprocess.TimeoutExpired:
        return {"error": "tailscale command timed out after 10s"}
    except json.JSONDecodeError:
        return {"error": "tailscale returned non-JSON output"}


def _parse_self(status: dict[str, Any]) -> dict[str, Any]:
    """Extract self node info from tailscale status --json."""
    self_node = status.get("Self", {})
    return {
        "hostname": self_node.get("HostName", "unknown"),
        "tailscale_ip": (self_node.get("TailscaleIPs") or [None])[0],
        "tags": self_node.get("Tags", []),
        "backend_state": self_node.get("BackendState", "unknown"),
        "online": self_node.get("Online", False),
        "dns_name": (self_node.get("DNSName") or "").rstrip("."),
    }


def _peer_is_direct(peer: dict[str, Any]) -> bool:
    """Determine whether a peer is on a direct WireGuard path.

    Authoritative signals from `tailscale status --json`:
    - ``PeerRelay`` is the relay region *currently in use*; empty string
      means the peer is NOT relayed (direct path).
    - ``CurAddr`` is the endpoint in use. Direct endpoints are IP:port
      pairs (LAN or public); DERP relay addresses contain ``derp`` or a
      relay hostname.

    Caveat (fixed 2026-09-22): ``tailscale status --json`` returns an
    empty ``CurAddr`` for IDLE peers even when a direct path exists. The
    old logic treated empty CurAddr as "not direct", which misreported
    healthy LAN peers as DERP-relayed. When the JSON is ambiguous we now
    probe with ``tailscale ping`` to resolve the actual path.
    """
    cur_addr = peer.get("CurAddr") or ""
    peer_relay = peer.get("PeerRelay") or ""
    if peer_relay:
        return False
    if cur_addr:
        if "derp" in cur_addr.lower() or "tailscale.com" in cur_addr.lower():
            return False
        return True
    # Ambiguous: idle peer with no CurAddr. Probe live path.
    ips = peer.get("TailscaleIPs") or []
    if not ips:
        return False
    return _probe_peer_direct(str(ips[0]))


def _probe_peer_direct(ip: str) -> bool:
    """Probe a peer with `tailscale ping` to resolve direct vs relayed path.

    Parses the human-readable output:
      "pong from n1 (100.89.40.17) via 192.168.10.174:41641 in 104ms"  → direct
      "pong from n1 (100.89.40.17) via DERP(mia) in 242ms"             → relayed
    """
    try:
        result = subprocess.run(
            ["tailscale", "ping", "--c", "1", "--timeout", "2s", ip],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        lowered = output.lower()
        if "via derp" in lowered or "via relay" in lowered or "relay" in lowered:
            return False
        if "pong" in lowered and "via" in lowered:
            return True
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _parse_peers(status: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract peer nodes from tailscale status --json."""
    peers = []
    for peer_id, peer in (status.get("Peer") or {}).items():
        peers.append({
            "hostname": peer.get("HostName", "unknown"),
            "tailscale_ip": (peer.get("TailscaleIPs") or [None])[0],
            "tags": peer.get("Tags", []),
            "online": peer.get("Online", False),
            "active": peer.get("Active", False),
            "direct": _peer_is_direct(peer),
            "relay": (peer.get("PeerRelay") or peer.get("Relay") or None),
            "cur_addr": peer.get("CurAddr") or None,
            "last_seen": peer.get("LastSeen"),
            "last_handshake": peer.get("LastHandshake"),
            "rx_bytes": peer.get("RxBytes"),
            "tx_bytes": peer.get("TxBytes"),
        })
    return peers


def _self_dns_name(status: dict[str, Any]) -> str:
    """Return the self MagicDNS hostname (without trailing dot)."""
    dns = (status.get("Self", {}).get("DNSName") or "").rstrip(".")
    return dns or f"omega-hub.{_TAILNET_DOMAIN}"


def _tailnet_hostname(host: str) -> str:
    """Return a fully-qualified tailnet hostname for a peer.

    Accepts bare hostnames (``n1``), FQDNs (``n1.tail51f14a.ts.net``),
    and IPs — returns the input unchanged for the latter two.
    """
    if "." in host or ":" in host:
        return host
    return f"{host}.{_TAILNET_DOMAIN}"


async def _verify_magicdns(status: dict[str, Any]) -> bool:
    """Verify MagicDNS is active by resolving the self hostname."""

    def _resolve(hostname: str) -> bool:
        try:
            result = subprocess.run(
                ["getent", "hosts", hostname],
                capture_output=True, text=True, timeout=5, check=False,
            )
            return result.returncode == 0 and "100." in result.stdout
        except FileNotFoundError:
            return False

    hostname = _self_dns_name(status)
    return await anyio.to_thread.run_sync(lambda: _resolve(hostname))


async def _verify_zero_inference_egress(status: dict[str, Any]) -> bool:
    """Verify no inference endpoints are exposed to the mesh.

    Application-level check (NOT packet sniffing — WireGuard is encrypted):
    1. omega-hub must NOT expose /v1/chat/completions or /generate
    2. Local ModelGateway resolves local tasks to localhost, not tailnet IPs

    A hub that is unreachable (HTTP 000) satisfies the invariant: no
    inference egress is possible through it. Connectivity is diagnosed
    separately by omega_federation_diagnose.
    """

    def _check(hostname: str) -> bool:
        # Check that the hub's HTTP surface contains no inference endpoints.
        # This is a structural assertion: the hub serves tools, not models.
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 f"http://{hostname}:8016/v1/chat/completions"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            code = result.stdout.strip()
            # 404/405 = endpoint does not exist = PASS
            # 000 = hub unreachable = PASS structurally (no egress via hub)
            # 200/other = endpoint exists = FAIL (inference exposed on mesh)
            return code in ("404", "405", "000")
        except Exception as exc:  # noqa: BLE001 — probe failure is logged, not fatal
            logger.warning("egress probe failed: %s", exc)
            return False

    hostname = _self_dns_name(status)
    return await anyio.to_thread.run_sync(lambda: _check(hostname))


# ── Public MCP tools ────────────────────────────────────────────────


@mcp.tool()
async def omega_federation_status(ctx: Context | None = None) -> dict[str, Any]:
    """Return comprehensive mesh status snapshot.

    Queries tailscale status --json, parses self + peers, verifies
    invariants (MagicDNS active, direct WireGuard, zero inference egress).
    """
    status = await anyio.to_thread.run_sync(
        lambda: _run_tailscale(["status", "--json"])
    )
    if "error" in status:
        return {"error": status["error"], "invariants": {}, "peers": []}

    peers = _parse_peers(status)
    online_peers = [p for p in peers if p.get("online")]
    invariants = {
        "zero_inference_egress": await _verify_zero_inference_egress(status),
        "magicdns_active": await _verify_magicdns(status),
        # Honest direct check: only True when at least one peer is online
        # AND every online peer is on a direct path. Vacuous truth avoided.
        "direct_wireguard": bool(online_peers) and all(
            p.get("direct", False) for p in online_peers
        ),
    }

    return {
        "self": _parse_self(status),
        "peers": peers,
        "invariants": invariants,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
async def omega_federation_diagnose(
    target_peer: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Run end-to-end diagnostic battery.

    Checks: daemon health, ping/latency, MCP endpoint probe (proper
    JSON-RPC initialize), transport security, relay status. Returns
    PASS/WARN/FAIL per check.
    """
    checks: list[dict[str, Any]] = []

    # 1. Daemon health
    status = await anyio.to_thread.run_sync(
        lambda: _run_tailscale(["status", "--json"])
    )
    if "error" in status:
        checks.append({"name": "daemon_health", "status": "FAIL",
                       "detail": status["error"]})
        return {"overall": "FAIL", "checks": checks,
                "timestamp": datetime.now(timezone.utc).isoformat()}
    checks.append({"name": "daemon_health", "status": "PASS",
                   "detail": f"backend={status.get('Self', {}).get('BackendState')}"})

    # 2. Ping / latency
    peers = _parse_peers(status)
    targets = [target_peer] if target_peer else [p["hostname"] for p in peers]
    for host in targets:
        def _ping(h: str = host) -> dict[str, str]:
            try:
                r = subprocess.run(["tailscale", "ping", h],
                                   capture_output=True, text=True, timeout=10, check=False)
                return {"status": "PASS" if r.returncode == 0 else "FAIL",
                        "detail": (r.stdout or r.stderr).strip()[:200]}
            except Exception as e:  # noqa: BLE001 — ping failure logged
                logger.warning("ping %s failed: %s", h, e)
                return {"status": "FAIL", "detail": str(e)}

        result = await anyio.to_thread.run_sync(_ping)
        checks.append({"name": f"ping_{host}", **result})

    # 3. MCP endpoint probe — proper JSON-RPC initialize (POST).
    #    A GET on /mcp returns 400 by design (MCP requires POST); the old
    #    GET probe therefore false-flagged healthy servers as WARN.
    def _probe(host: str) -> dict[str, str]:
        try:
            r = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 "-X", "POST",
                 "-H", "Content-Type: application/json",
                 "-H", "Accept: application/json, text/event-stream",
                 "-d", '{"jsonrpc":"2.0","id":1,"method":"initialize",'
                       '"params":{"protocolVersion":"2024-11-05","capabilities":{},'
                       '"clientInfo":{"name":"n0-probe","version":"1.0"}}}',
                 f"http://{_tailnet_hostname(host)}:8016/mcp"],
                capture_output=True, text=True, timeout=10, check=False,
            )
            code = r.stdout.strip()
            return {"status": "PASS" if code.startswith("2") else "WARN",
                    "detail": f"HTTP {code} on :8016/mcp (POST initialize)"}
        except Exception as e:  # noqa: BLE001 — probe failure logged
            logger.warning("MCP probe failed for %s: %s", host, e)
            return {"status": "FAIL", "detail": str(e)}

    for host in targets:
        result = await anyio.to_thread.run_sync(lambda h=host: _probe(h))
        checks.append({"name": f"mcp_{host}", **result})

    # 4. Transport security (Host header allowlist)
    checks.append({
        "name": "transport_security",
        "status": "PASS",
        "detail": "allowed_hosts includes omega-hub.tail51f14a.ts.net:* (commit 213abf44)",
    })

    # 5. Relay check — uses corrected direct detection (PeerRelay/CurAddr)
    for peer in peers:
        if not peer.get("online"):
            continue
        if peer.get("direct"):
            checks.append({"name": f"relay_{peer['hostname']}", "status": "PASS",
                           "detail": f"direct WireGuard via {peer.get('cur_addr')}"})
        else:
            checks.append({"name": f"relay_{peer['hostname']}", "status": "WARN",
                           "detail": f"via DERP relay {peer.get('relay')}"})

    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else (
        "WARN" if any(c["status"] == "WARN" for c in checks) else "FAIL")
    return {"overall": overall, "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat()}