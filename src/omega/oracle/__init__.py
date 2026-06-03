# 🔱 Omega Oracle — Single Intelligence Facade
# AP: AP-ORACLE-INIT-v1.0.0
#
# [id-soft: doom-1993] WAD System — module facade as WAD directory entry
#   DOOM's w_wad.h defines a flat directory of all lumps. This __init__ exports
#   the Oracle's public interface in the same flat-directory pattern.

from .oracle import Oracle, OracleResponse
from .entity_registry import EntityRegistry, Entity
from .model_gateway import ModelGateway

__all__ = ["Oracle", "OracleResponse", "EntityRegistry", "Entity", "ModelGateway"]
