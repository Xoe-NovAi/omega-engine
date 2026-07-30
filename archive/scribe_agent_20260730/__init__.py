"""
Scribe Agent Package — Hub Master & Soul Distillation
"""
from src.omega.agents.scribe.parser import HubBroadcast, HubUpdatePlan
from src.omega.agents.scribe.lock import HubLock, HubLockError, managed_hub_lock, atomic_write
from src.omega.agents.scribe.hub_master import HubMaster
from src.omega.agents.scribe.agy_oauth_persistence import (
    AGYAuthPersistence,
    persist_oauth_tokens_async,
    create_refresh_hook,
)

__all__ = [
    "HubBroadcast",
    "HubUpdatePlan",
    "HubLock",
    "HubLockError",
    "managed_hub_lock",
    "atomic_write",
    "HubMaster",
    "AGYAuthPersistence",
    "persist_oauth_tokens_async",
    "create_refresh_hook",
]

__version__ = "1.0.0"