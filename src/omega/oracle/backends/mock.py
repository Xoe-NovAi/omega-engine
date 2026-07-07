# 🔱 Offline Mock Backend — CI/CD Accelerator
# AP: AP-OFFLINE-MOCK-BACKEND-v1.0.0

class OfflineMockBackend:
    """Mock backend for OMEGA_ENV=test.
    
    Returns deterministic responses to unblock CI/CD and avoid
    unnecessary inference overhead during testing.
    """

# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
    async def generate(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Return a static mock response."""
        return "Mock response"
