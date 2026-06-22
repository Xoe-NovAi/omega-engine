# AP: AP-PR-READINESS-v1.0.0
import anyio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from omega.oracle.oracle import Oracle
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.health_monitor import get_health_monitor

logger = logging.getLogger("omega.runtime.openclaw")

class OpenClawRuntime:
    """
    OpenClaw Runtime - coordinates sovereign inference with budget gates
    and session persistence in SOUL.md.
    
    Respects Mandate 2 (Engine-Stack Firewall) by remaining agnostic to 
    specific IWAD/PWAD content.
    """

    def __init__(self, oracle: Oracle, gateway: ModelGateway):
        """Initialize the runtime with core engine components.
        
        Args:
            oracle: The Omega Oracle instance for routing and summoning.
            gateway: The ModelGateway instance for provider selection.
        """
        self.oracle = oracle
        self.gateway = gateway
        self.health_monitor = get_health_monitor()

    async def _load_soul(self, soul_path: Path) -> Dict[str, Any]:
        """Load the entity's SOUL.md file.
        
        Args:
            soul_path: Absolute path to the SOUL.md file.
            
        Returns:
            A dictionary of key-value pairs parsed from the soul file.
        """
        if not soul_path.exists():
            return {}
        
        try:
            # Use a lambda to ensure encoding is passed to read_text, not run_sync
            content = await anyio.to_thread.run_sync(lambda: soul_path.read_text(encoding="utf-8"))
            soul = {}
            for line in content.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    soul[k.strip()] = v.strip()
            return soul
        except Exception as e:
            logger.error(f"Failed to load soul file {soul_path}: {e}")
            return {}

    async def _persist_session(self, soul_path: Path, session_id: str) -> None:
        """Persist the current session_id back to SOUL.md.
        
        Args:
            soul_path: Absolute path to the SOUL.md file.
            session_id: The session identifier to record.
        """
        soul = await self._load_soul(soul_path)
        soul["last_session_id"] = session_id
        
        content = "\n".join([f"{k}: {v}" for k, v in soul.items()])
        try:
            # Use a lambda to ensure encoding is passed to write_text, not run_sync
            await anyio.to_thread.run_sync(lambda: soul_path.write_text(content, encoding="utf-8"))
        except Exception as e:
            logger.error(f"Failed to persist session to {soul_path}: {e}")

    def _detect_intent(self, query: str) -> str:
        """Stub for intent detection.
        
        Args:
            query: The user's input query.
            
        Returns:
            The detected intent category.
        """
        query_lower = query.lower()
        if any(kw in query_lower for kw in ["code", "api", "fix", "implement", "debug"]):
            return "technical"
        if any(kw in query_lower for kw in ["write", "story", "poem", "creative", "imagine"]):
            return "creative"
        return "general"

    async def _check_budget(self, entity_name: str, provider_name: str) -> bool:
        """Enforce hard-stop cloud budget gates before inference.
        
        Args:
            entity_name: Name of the entity making the request.
            provider_name: Name of the selected provider.
            
        Returns:
            True if budget is available or provider is local, False otherwise.
        """
        # Local providers are exempt from budget gates per Mandate 7
        if provider_name not in self.gateway._cloud_providers:
            return True
            
        usage = self.health_monitor.get_quota_usage(provider_name)
        if usage >= 1.0:
            logger.warning(f"Sovereign Budget Gate: Cloud budget exceeded for {provider_name} (Entity: {entity_name})")
            return False
        return True

    async def execute(self, entity_name: str, query: str, soul_path_str: str) -> str:
        """
        Coordinates the full inference lifecycle: soul loading, routing, 
        budget verification, execution, and persistence.
        
        Args:
            entity_name: Name of the entity acting.
            query: User input.
            soul_path_str: Absolute path to the entity's SOUL.md.
            
        Returns:
            The final response text from the Oracle.
        """
        soul_path = Path(soul_path_str)
        soul = await self._load_soul(soul_path)
        
        # 1. Determine routing rules based on intent and soul markers
        intent = self._detect_intent(query)
        routing_rule = soul.get("routing_rule", "default")
        
        # 2. Select provider via ModelGateway (utilizing select_provider pattern)
        try:
            provider_name = await self.gateway.select_provider(entity_name, intent)
        except AttributeError:
            # Fallback to preferred backend if select_provider is not yet implemented in ModelGateway
            provider_name = await self.gateway.get_preferred_backend()
        
        # 3. Hard-stop Cloud Budget Gate
        if not await self._check_budget(entity_name, provider_name):
            return "Error: Sovereign cloud budget exceeded. Please use a local model."

        # 4. Call Oracle.talk with optional model_override from SOUL.md
        model_override = soul.get("preferred_model")
        
        if model_override:
            # Use summon for direct model override control
            response = await self.oracle.summon(
                entity_name=entity_name,
                query=query,
                model_override=model_override
            )
        else:
            # Standard routed talk
            response = await self.oracle.talk(query)

        # 5. Exact Token Ledger Integration
        # Record usage in the HealthMonitor ledger. 
        # Using a linear approximation for token count (len // 4) as per Right Approximation principle.
        estimated_tokens = (len(query) + len(response.text)) // 4
        self.health_monitor.record_token_usage(provider_name, estimated_tokens)
        
        # 6. Persist session_id back to SOUL.md for cognitive continuity
        if response.session_id:
            await self._persist_session(soul_path, response.session_id)
            
        return response.text
