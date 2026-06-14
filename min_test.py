import anyio
from omega.oracle.entity_registry import EntityRegistry
print("Registry loaded")
anyio.run(lambda: print("AnyIO works"))
