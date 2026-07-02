import pytest
import asyncio
from src.omega.oracle.context_builder import ContextBuilder, Message, ObservationMaskingStrategy

@pytest.mark.asyncio
async def test_observation_masking_culls_keywords():
    # Setup messages with repetitive "logged" lines
    messages = [
        Message(role="user", content="Run the scan"),
        Message(role="tool", content="Starting scan...\nAction logged: checking file 1\nAction logged: checking file 2\nAction logged: checking file 3\nScan complete.")
    ]
    
    strategy = ObservationMaskingStrategy(preserve_first_n=1)
    await strategy(messages, budget=1000)
    
    # "Starting scan..." should be preserved
    # "Action logged..." lines should be culled
    # "Scan complete." should be preserved
    content = messages[1].content
    assert "Starting scan..." in content
    assert "Scan complete." in content
    assert "Action logged" not in content

@pytest.mark.asyncio
async def test_observation_masking_preserves_non_keywords():
    messages = [
        Message(role="tool", content="Header\nImportant data: 123\nAction logged: skip\nCritical error: failure\nFooter")
    ]
    
    strategy = ObservationMaskingStrategy(preserve_first_n=1)
    await strategy(messages, budget=1000)
    
    content = messages[0].content
    assert "Header" in content
    assert "Important data: 123" in content
    assert "Critical error: failure" in content
    assert "Footer" in content
    assert "Action logged" not in content

@pytest.mark.asyncio
async def test_observation_masking_preserves_first_n():
    messages = [
        Message(role="tool", content="Line 1: logged\nLine 2: logged\nLine 3: logged\nLine 4: data")
    ]
    
    strategy = ObservationMaskingStrategy(preserve_first_n=2)
    await strategy(messages, budget=1000)
    
    content = messages[0].content
    # First two lines should be preserved regardless of content
    assert "Line 1: logged" in content
    assert "Line 2: logged" in content
    # Third line should be culled
    assert "Line 3: logged" not in content
    # Fourth line should be preserved
    assert "Line 4: data" in content
