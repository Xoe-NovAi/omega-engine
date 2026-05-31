import json
import anyio
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

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
            except Exception as e:
                logger.error(f"Failed to load capability registry: {e}")

    async def _save(self):
        """Save capabilities to disk."""
        try:
            import yaml
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            def _write():
                with open(self.storage_path, "w") as f:
                    yaml.dump(self._registry, f)
            await anyio.to_thread.run_sync(_write)
        except Exception as e:
            logger.error(f"Failed to save capability registry: {e}")

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
