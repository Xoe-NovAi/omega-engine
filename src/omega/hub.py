# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Omega Hub — Hardware stats bridge for degradation management.

Provides get_hardware_stats() used by Oracle.talk() for graceful
degradation under system pressure.

AP: AP-OMEGA-HUB-v1.0.0
[M2/M16: Engine-Stack Firewall] Uses omega.monitoring directly — no
cross-boundary import from mcp_servers.
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import logging
from typing import Any, Dict

import anyio

logger = logging.getLogger(__name__)


async def get_hardware_stats() -> Dict[str, Any]:
    """Get hardware stats dict for degradation management.

    Returns keys: cpu_usage, memory_available_mb, memory_total_mb, temperature_c.
    Falls back to safe defaults on any error.
    """
    try:
        from omega.monitoring import HardwareMonitor

        def _collect() -> Dict[str, Any]:
            hm = HardwareMonitor()
            stats = hm.collect_all()
            cpu = stats.get("cpu", {})
            mem = stats.get("memory", {})
            return {
                "cpu_usage": cpu.get("avg_percent", 0.0),
                "memory_available_mb": mem.get("available_mb", 1024),
                "memory_total_mb": mem.get("total_mb", 0),
                "temperature_c": stats.get("thermal", {}).get("cpu_temp_c", 0.0),
            }

        return await anyio.to_thread.run_sync(_collect)
    except ImportError:
        logger.debug("get_hardware_stats: omega.monitoring not available")
        return {"cpu_usage": 0.0, "memory_available_mb": 1024}
    except (RuntimeError, OSError) as e:
        logger.warning("get_hardware_stats failed: %s", e)
        return {"cpu_usage": 0.0, "memory_available_mb": 1024}
