# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""SomaticState Round-Trip Verification.
AP: AP-SOMATIC-ROUNDTRIP-v1.0.0

Verifies that model state can be captured, saved to CAS, and restored
without losing fidelity.
"""
import pytest
import anyio
from unittest.mock import AsyncMock, MagicMock, patch

pytest.importorskip("llama_cpp", reason="llama-cpp-python not installed (optional native backend)")

from omega.state import get_usm, reset_usm
from omega.state.somatic_state import SomaticStateManager

@pytest.mark.anyio
async def test_somatic_roundtrip():
    """Test the full capture -> save -> load -> restore cycle."""
    reset_memory_store()
    await reset_usm()
    
    usm = get_usm()
    ssm = SomaticStateManager(cas=usm.cas)
    
    # 1. Mock a model state
    mock_state_data = b"SOMETIC_STATE_DATA_V1_SAMPLED_KV_CACHE"
    mock_ctx = MagicMock()
    
    # 2. Capture state
    # We patch the low-level C-FFI calls
    with patch("llama_cpp.llama_cpp.llama_state_get_size", return_value=len(mock_state_data)):
        with patch("llama_cpp.llama_cpp.llama_state_get_data") as mock_get_data:
            # Mock the buffer write
            def side_effect(ctx, buf, size):
                for i, b in enumerate(mock_state_data):
                    buf[i] = b
                return 0
            mock_get_data.side_effect = side_effect
            
            hash_ = await ssm.capture(mock_ctx)
            assert hash_ is not None
            
            # Verify data in CAS
            stored_data = await usm.cas.get(hash_)
            assert stored_data == mock_state_data
    
    # 3. Restore state
    with patch("llama_cpp.llama_cpp.llama_state_set_data", return_value=0) as mock_set_data:
        success = await ssm.restore(mock_ctx, hash_)
        assert success is True
        
        # Verify the buffer passed to set_data matches our mock data
        args, _ = mock_set_data.call_args
        buf = args[1]
        assert bytes(buf) == mock_state_data
    
    print("✅ SomaticState Round-Trip Verified")

def reset_memory_store():
    from omega.memory_store import reset_memory_store as rms
    rms()

if __name__ == "__main__":
    anyio.run(test_somatic_roundtrip)
