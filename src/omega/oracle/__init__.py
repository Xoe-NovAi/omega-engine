# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Omega Oracle — Single Intelligence Facade
# AP: AP-ORACLE-INIT-v1.0.0
#
# [id-soft: vet-043] WAD System — module facade as WAD directory entry
#   DOOM's w_wad.h defines a flat directory of all lumps. This __init__ exports
#   the Oracle's public interface in the same flat-directory pattern.

from .oracle import Oracle, OracleResponse
from .entity_registry import EntityRegistry, Entity
from .model_gateway import ModelGateway, GenerateResult
from .entity_affinity import EntityAffinityResolver, AffinityResult
from .orchestrator import Orchestrator
from .axiom_registry import AxiomRegistry

__all__ = [
    "Oracle",
    "OracleResponse",
    "EntityRegistry",
    "Entity",
    "ModelGateway",
    "GenerateResult",
    "EntityAffinityResolver",
    "AffinityResult",
    "Orchestrator",
    "AxiomRegistry",
]
