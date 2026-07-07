# AP: AP-PR-READINESS-v1.0.0
# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Capability Registry — Agent Skill Discovery
#
# [id-soft: quake3-1999] VM System — capability-based dispatch
#   Q3A's virtual machine (vm.c) loads game code as a dynamic module with
#   exported function table. CapabilityRegistry mirrors this: agents publish
#   their skills as discoverable entries, enabling runtime dispatch.
# [id-soft: doom-1993] Multi-Index Entity — dual-index lookup
#   DOOM's mobj_t is simultaneously in sector (render) and blockmap (collision)
#   lists. CapabilityRegistry provides dual-index lookup: by skill name and
#   by agent name.


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import json
import anyio
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)

logger = logging.getLogger("omega.capabilities")

class CapabilityRegistry:
    """
    Sovereign Capability Registry for Agent Discovery.
    Allows agents to publish their specialized skills and tools, 
    and other agents to discover the best-suited peer for a task.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("data/capabilities.yaml")
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._lock = anyio.Lock()
        self._load()

    def _load(self):
        """Load capabilities from disk (synchronous during init)."""
        if self.storage_path.exists():
            try:
                import yaml
                with open(self.storage_path, "r") as f:
                    data = yaml.safe_load(f)
                    if data:
                        self._registry = data
            except OmegaError:
                pass
            except (OmegaError, RuntimeError, OSError) as e:
                logger.error(f"Failed to load capability registry: {e}", exc_info=True)
                pass

    async def _save(self):
        """Save capabilities to disk."""
        try:
            import yaml
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            def _write():
                with open(self.storage_path, "w") as f:
                    yaml.dump(self._registry, f)
            await anyio.to_thread.run_sync(_write)
        except OmegaError:
            pass
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to save capability registry: {e}", exc_info=True)
            pass

    async def publish(self, agent_id: str, capabilities: Dict[str, Any]) -> bool:
        """
        Publish or update capabilities for a specific agent.
        
        Args:
            agent_id: Unique identifier for the agent (e.g., 'opencode-builder').
            capabilities: Dictionary containing 'skills', 'domains', and 'tools'.
        """
        async with self._lock:
            self._registry[agent_id] = {
                "capabilities": capabilities,
                "updated_at": anyio.current_time() if hasattr(anyio, 'current_time') else None # simplified
            }
            await self._save()
            return True

    async def discover_expert(self, query: str) -> Optional[str]:
        """
        Discover the best-suited agent for a given task description.
        
        Scoring is based on keyword overlap in domains and skills, 
        weighted by the agent's reported confidence score.
        """
        async with self._lock:
            best_agent = None
            max_score = 0
            
            query_tokens = set(query.lower().split())
            
            for agent_id, data in self._registry.items():
                caps = data.get("capabilities", {})
                domains = set(" ".join(caps.get("domains", [])).lower().split())
                skills = set(" ".join(caps.get("skills", [])).lower().split())
                tools = set(" ".join(caps.get("tools", [])).lower().split())
                confidence = caps.get("confidence_score", 0.5)
                
                all_tokens = domains | skills | tools
                overlap = len(query_tokens & all_tokens)
                
                # Score = overlap * confidence
                score = overlap * confidence
                
                if score > max_score:
                    max_score = score
                    best_agent = agent_id
            
            return best_agent

    def list_all(self) -> Dict[str, Any]:
        """Return the full registry."""
        return self._registry
