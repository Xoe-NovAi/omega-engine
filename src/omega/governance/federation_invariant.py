# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Federation invariant validator — application-level zero inference egress.

Verifies that the mesh exposes NO inference endpoints. This is checked at
the application boundary (ModelGateway + hub listener), NOT by packet
sniffing (WireGuard is encrypted; payload inspection is impossible/undesirable).

Mandates: M7 (Synergy), M8 (Zero Telemetry), M23 (Failure Integrity)
"""

from __future__ import annotations

import logging
import subprocess
from datetime import datetime, timezone
from typing import Any

import anyio

logger = logging.getLogger(__name__)

# Endpoints that MUST NOT exist on the mesh
FORBIDDEN_ENDPOINTS = [
    "/v1/chat/completions",
    "/v1/completions",
    "/generate",
    "/v1/embeddings",  # embeddings stay local, never exposed to mesh
]

HUB_BASE = "http://omega-hub.tail51f14a.ts.net:8016"


async def verify_zero_inference_egress() -> dict[str, Any]:
    """Check that no forbidden inference endpoints respond on the hub."""
    results = {}

    def _probe(path: str) -> str:
        try:
            r = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 f"{HUB_BASE}{path}"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            return r.stdout.strip()
        except Exception as exc:  # noqa: BLE001 — probe failure is logged, not fatal
            logger.warning("federation probe failed for %s: %s", path, exc)
            return "ERR"

    for endpoint in FORBIDDEN_ENDPOINTS:
        code = await anyio.to_thread.run_sync(lambda e=endpoint: _probe(e))
        # 404/405 = endpoint does not exist = PASS
        results[endpoint] = {"status": "PASS" if code in ("404", "405") else "FAIL",
                             "http_code": code}

    all_pass = all(r["status"] == "PASS" for r in results.values())
    return {
        "invariant": "zero_inference_egress",
        "pass": all_pass,
        "checks": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def verify_local_only_embeddings() -> dict[str, Any]:
    """Verify embeddings resolve to localhost, never tailnet IPs."""
    # Structural check: embeddings tier primary is native-local
    import yaml

    def _load() -> dict:
        with open("config/providers.yaml") as f:
            return yaml.safe_load(f)

    cfg = await anyio.to_thread.run_sync(_load)
    emb = cfg.get("sovereignty_policy", {}).get("tiers", {}).get("embeddings", {})
    primary = emb.get("primary", "unknown")
    ok = primary in ("native-local", "ollama-local")
    return {
        "invariant": "local_only_embeddings",
        "pass": ok,
        "primary": primary,
        "detail": "Embeddings tier must resolve to local backend" if ok else
                  f"UNEXPECTED: embeddings primary = {primary}",
    }


def main() -> int:
    """CLI entry for cron/systemd validation."""
    import asyncio  # noqa: PLC0415 — CLI entry

    async def _run() -> None:
        egress = await verify_zero_inference_egress()
        emb = await verify_local_only_embeddings()
        print(f"zero_inference_egress: {'PASS' if egress['pass'] else 'FAIL'}")
        for ep, r in egress["checks"].items():
            print(f"  {ep}: {r['status']} (HTTP {r['http_code']})")
        print(f"local_only_embeddings: {'PASS' if emb['pass'] else 'FAIL'} ({emb.get('primary')})")

    asyncio.run(_run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())