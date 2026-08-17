# 🔱 Omega Engine — Coordination Package
# ⬡ OMEGA ⬡ MIAP ⬡ src/omega/coordination/__init__.py

"""
Coordination primitives for multi-instance agent orchestration.

Exports:
- MIAP (Multi-Instance Agent Protocol) core
"""

from .miap import (
    # Instance Registry
    register_instance,
    deregister_instance,
    update_instance_heartbeat,
    get_active_instances,
    get_all_instances,
    InstanceRecord,
    # Event Log
    append_event,
    read_events,
    get_latest_event,
    Event,
    # Projections
    project_anchored_summary,
    project_session_gnosis,
    write_projections,
    # Convenience Writers
    write_anchored_event,
    write_gnosis_entry,
    write_distillation,
    # CLI
    miap_cli,
)

__all__ = [
    "register_instance",
    "deregister_instance",
    "update_instance_heartbeat",
    "get_active_instances",
    "get_all_instances",
    "InstanceRecord",
    "append_event",
    "read_events",
    "get_latest_event",
    "Event",
    "project_anchored_summary",
    "project_session_gnosis",
    "write_projections",
    "write_anchored_event",
    "write_gnosis_entry",
    "write_distillation",
    "miap_cli",
]
