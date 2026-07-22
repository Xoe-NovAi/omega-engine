"""M21 Contract Tests: Admission decisions correct (5 tests)."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os

@pytest.mark.contract
@pytest.mark.anyio
async def test_admission_acquire_success():
    """Admission acquire succeeds when slot is free."""
    from omega.oracle.admission_controller import LocalInferenceAdmission
    
    admission = LocalInferenceAdmission()
    acquired = await admission.acquire("model-a")
    assert acquired is True
    assert admission.is_available is False
    admission.release()
    assert admission.is_available is True

@pytest.mark.contract
@pytest.mark.anyio
async def test_admission_acquire_fails_when_busy():
    """Admission acquire fails when slot is occupied."""
    from omega.oracle.admission_controller import LocalInferenceAdmission
    
    admission = LocalInferenceAdmission()
    # Acquire first model
    acquired1 = await admission.acquire("model-a")
    assert acquired1 is True
    
    # Try to acquire second model
    acquired2 = await admission.acquire("model-b")
    assert acquired2 is False
    
    admission.release()

@pytest.mark.contract
@pytest.mark.anyio
async def test_admission_release_clears_model():
    """Admission release clears current model."""
    from omega.oracle.admission_controller import LocalInferenceAdmission
    
    admission = LocalInferenceAdmission()
    await admission.acquire("model-a")
    assert admission._current_model == "model-a"
    
    admission.release()
    assert admission._current_model is None
    assert admission.is_available is True

@pytest.mark.contract
@pytest.mark.anyio
async def test_admission_is_available_property():
    """Admission is_available property reflects semaphore state."""
    from omega.oracle.admission_controller import LocalInferenceAdmission
    
    admission = LocalInferenceAdmission()
    assert admission.is_available is True  # Initially available
    
    await admission.acquire("model")
    assert admission.is_available is False  # Now busy
    
    admission.release()
    assert admission.is_available is True  # Available again

@pytest.mark.contract
@pytest.mark.anyio
async def test_admission_concurrent_acquire():
    """Only one concurrent acquire should succeed."""
    import anyio
    from omega.oracle.admission_controller import LocalInferenceAdmission
    
    admission = LocalInferenceAdmission()
    results = []
    
    async def try_acquire(model_name):
        acquired = await admission.acquire(model_name)
        results.append(acquired)
        if acquired:
            await anyio.sleep(0.01)  # Simulate work
            admission.release()
    
    # Launch two concurrent acquires
    async with anyio.create_task_group() as tg:
        tg.start_soon(try_acquire, "model-a")
        tg.start_soon(try_acquire, "model-b")
    
    # Only one should succeed
    assert sum(results) == 1, f"Expected 1 success, got {sum(results)}"
