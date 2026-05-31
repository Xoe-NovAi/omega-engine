import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import deque
from .entity_registry import EntityRegistry

# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_gnosis ⬡ PROXY-IMPLEMENTATION


@dataclass
class DescriptorRef:
    """
    A lightweight reference to a high-density data object.
    Prevents context bloat by passing a pointer instead of the full payload.
    """
    descriptor_id: str
    resource_type: str
    uri: str
    metadata: Dict[str, Any]


class GnosisProxy:
    """
    Middleware for Tool RAG Discovery and State Transfer.
    Implements the "Invisible RAG" pattern for tools.
    """
    MAX_TRANSFER_STORE_SIZE = 1000

    def __init__(self, registry: 'EntityRegistry'):
        self.registry = registry
        # In-memory cache for descriptors (Sovereign-Lite)
        self.transfer_store: Dict[str, Any] = {}
        self._store_keys = deque()

    def discover_tools(self, query: str, entity_name: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs RAG-based discovery of tools available to the entity.
        Returns matched tool descriptors for injection into system prompt.
        """
        # 1. Get all tools available to the entity from the registry
        entity_tools = self.registry.get_tools_for_entity(entity_name)

        # 2. Perform semantic match (Simplified for MVE: Keyword match)
        # In full implementation, this uses the Vector Store (Qdrant)
        query_words = query.lower().split()
        matched_tools = []
        for tool in entity_tools:
            desc = tool['description'].lower()
            if any(word in desc for word in query_words):
                matched_tools.append(tool)

        # Return top-K
        return matched_tools[:top_k]

    def create_transfer_descriptor(self, data: Any, resource_type: str = "state") -> DescriptorRef:
        """
        Abstracts a large payload into a Transfer Descriptor.
        """
        descriptor_id = f"trf_{uuid.uuid4().hex[:8]}"
        uri = f"omega://transfer/{descriptor_id}"

        # Bound the store to prevent OOM (C-GNOSIS-001)
        if len(self.transfer_store) >= self.MAX_TRANSFER_STORE_SIZE:
            oldest_key = self._store_keys.popleft()
            self.transfer_store.pop(oldest_key, None)

        # Store the actual data in the sovereign store
        self.transfer_store[descriptor_id] = data
        self._store_keys.append(descriptor_id)

        return DescriptorRef(
            descriptor_id=descriptor_id,
            resource_type=resource_type,
            uri=uri,
            metadata={"size": len(str(data))}
        )

    def resolve_descriptor(self, descriptor_id: str) -> Optional[Any]:
        """
        Resolves a descriptor back into its full data object.
        """
        if descriptor_id not in self.transfer_store:
            raise KeyError(f"Descriptor {descriptor_id} not found or expired")
        return self.transfer_store[descriptor_id]

    async def wrap_tool_call(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intercepts tool calls to check if arguments contain descriptors that need resolving.
        """
        resolved_args = {}
        for k, v in args.items():
            if isinstance(v, DescriptorRef):
                resolved_args[k] = self.resolve_descriptor(v.descriptor_id)
            elif isinstance(v, str) and v.startswith("omega://transfer/"):
                desc_id = v.split("/")[-1]
                resolved_args[k] = self.resolve_descriptor(desc_id)
            else:
                resolved_args[k] = v

        return {"tool": tool_name, "arguments": resolved_args}