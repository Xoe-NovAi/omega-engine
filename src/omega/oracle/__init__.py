# 🔱 Omega Oracle — Single Intelligence Facade
# AP: AP-ORACLE-INIT-v1.0.0

from .oracle import Oracle, OracleResponse
from .entity_registry import EntityRegistry, Entity
from .model_gateway import ModelGateway

__all__ = ["Oracle", "OracleResponse", "EntityRegistry", "Entity", "ModelGateway"]
