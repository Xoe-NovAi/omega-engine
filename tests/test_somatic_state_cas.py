# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for SomaticStateManager (CAS-backed).
M21: Gate Integrity — All core API boundaries must have contract tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
from omega.state import SomaticStateManager, CASManager


class TestSomaticStateManager:
    @pytest.fixture
    async def cas(self):
        with tempfile.TemporaryDirectory() as tmp:
            cas = CASManager(Path(tmp))
            await cas.initialize()
            yield cas
    
    @pytest.fixture
    def somatic(self, cas):
        return SomaticStateManager(cas)
    
    def test_is_available_without_llama_cpp(self, somatic):
        # Should return False when llama_cpp not installed or missing APIs
        with patch.dict('sys.modules', {'llama_cpp': None}):
            somatic._llama_cpp = None
            somatic._available = None
            assert somatic.is_available() is False
    
    @pytest.mark.anyio
    async def test_capture_raises_when_unavailable(self, somatic):
        with patch.object(somatic, '_load_llama_cpp', return_value=False):
            with pytest.raises(RuntimeError, match="SomaticState unavailable"):
                await somatic.capture(0x12345678)
    
    @pytest.mark.anyio
    async def test_capture_roundtrip(self, somatic):
        # Mock llama_cpp with state APIs
        mock_llama = MagicMock()
        mock_llama.llama_state_get_size.return_value = 4
        mock_llama.llama_state_get_data.return_value = 0
        mock_llama.llama_state_set_data.return_value = 0
        
        with patch.object(somatic, '_llama_cpp', mock_llama):
            somatic._available = True
            
            mock_ctx = Mock()
            hash_ = await somatic.capture(mock_ctx)
            
            assert hash_ is not None
            assert len(hash_) == 64  # SHA-256 hex
            mock_llama.llama_state_get_size.assert_called_once_with(mock_ctx)
            mock_llama.llama_state_get_data.assert_called_once()
    
    @pytest.mark.anyio
    async def test_restore_roundtrip(self, somatic, cas):
        mock_llama = MagicMock()
        mock_llama.llama_state_get_size.return_value = 4
        mock_llama.llama_state_get_data.return_value = 0
        mock_llama.llama_state_set_data.return_value = 0
        
        with patch.object(somatic, '_llama_cpp', mock_llama):
            somatic._available = True
            
            mock_ctx = Mock()
            hash_ = await somatic.capture(mock_ctx)
            
            # Now test restore
            result = await somatic.restore(mock_ctx, hash_)
            assert result is True
            mock_llama.llama_state_set_data.assert_called_once()
    
    @pytest.mark.anyio
    async def test_capture_async(self, somatic):
        mock_llama = MagicMock()
        mock_llama.llama_state_get_size.return_value = 4
        mock_llama.llama_state_get_data.return_value = 0
        
        with patch.object(somatic, '_llama_cpp', mock_llama):
            somatic._available = True
            
            mock_ctx = Mock()
            hash_ = await somatic.capture_async(mock_ctx)
            assert hash_ is not None