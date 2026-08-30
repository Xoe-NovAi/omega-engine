# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from omega.oracle.security import tdp_wrap, TaintedData, TDPGate

@pytest.mark.anyio
async def test_tdp_wrap_string():
    @tdp_wrap(source="test_source", taint_level=2)
    async def mock_tool():
        return "some untrusted data"
    
    result = await mock_tool()
    
    assert "### [EXTERNAL DATA START]" in result
    assert "Source: test_source" in result
    assert "Taint Level: 2" in result
    assert "some untrusted data" in result
    assert "### [EXTERNAL DATA END]" in result

@pytest.mark.anyio
async def test_tdp_wrap_non_string():
    @tdp_wrap(source="test_source")
    async def mock_tool():
        return {"data": 123}
    
    result = await mock_tool()
    assert result == {"data": 123}
