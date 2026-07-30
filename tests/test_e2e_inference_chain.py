# AP: AP-E2E-TEST-v1.0.0
# ⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ E2E-VERIFICATION
#
# End-to-End Inference Chain Test
# Verifies the full loop: Query -> Router -> Gateway -> Response -> Memory -> Distiller

import os
import pytest
import anyio
from unittest.mock import MagicMock, patch

# Force test environment
os.environ["OMEGA_ENV"] = "test"

from omega.oracle.oracle import Oracle
from omega.oracle.model_gateway import ModelGateway
from omega.memory_store import MemoryStore

@pytest.mark.anyio
async def test_e2e_inference_chain():
    """
    Verifies the complete cognitive run-loop of the Omega Engine.
    
    Chain:
    1. User Query -> Oracle.talk()
    2. Oracle -> SemanticRouter (Entity Selection)
    3. Oracle -> ModelGateway (Inference via MockBackend)
    4. ModelGateway -> OracleResponse (Result)
    5. Oracle -> MemoryStore (Persistence)
    """
    
    # 1. Setup
    oracle = Oracle()
    from omega.memory_store import get_memory_store
    memory = get_memory_store()
    
    oracle = Oracle()
    await oracle.bootstrap()

    # 2. Execution
    query = "I need to store some data in the vector store"
    response = await oracle.talk(query)
    
    # 3. Verifications
    
    # A. Response Integrity
    assert response is not None
    assert hasattr(response, "text")
    assert len(response.text) > 0
    
    # B. Routing Verification
    assert response.backend is not None

    # C. Memory Persistence
    exchanges = await memory.search_fts(query, entity_name=response.entity)
    assert len(exchanges) > 0
    assert any(query in e.get("content", "") for e in exchanges)
        
    print("\n✅ E2E Inference Chain Verified: Query -> Router -> Gateway -> Response -> Memory")

if __name__ == "__main__":
    # Allow running the test directly via python
    anyio.run(test_e2e_inference_chain)
