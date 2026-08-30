# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import anyio
from pathlib import Path
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.wad_loader import WADLoader
from omega.oracle.world_state import world_state

@pytest.mark.anyio
async def test_first_breath_world_query():
    # Setup
    registry = EntityRegistry()
    # Use the actual arcana_novai WAD path
    wads_dir = Path("config/wads")
    loader = WADLoader(registry, wads_dir=wads_dir)
    
    # Load the WAD
    success, _ = await loader.load_wad("arcana_novai")
    assert success is True
    
    # Test Lattice-Culling: Core -> Physics
    physics = world_state.lattice_query("core", "physics")
    assert physics is not None
    assert physics["gravity"] == 9.81
    assert physics["substrate"] == "etheric_lattice"
    
    # Test Lattice-Culling: Metaphysics -> Laws
    laws = world_state.lattice_query("metaphysics", "laws")
    assert laws is not None
    assert laws["soul_resonance"] == "active"
    
    # Test Culling: Invalid sector
    void = world_state.lattice_query("void", "something")
    assert void is None
    
    # Test Culling: Valid sector, invalid lump
    missing = world_state.lattice_query("core", "missing")
    assert missing is None

@pytest.mark.anyio
async def test_world_state_global():
    world_state.set_global("world_name", "Omegaverse")
    assert world_state.get_global("world_name") == "Omegaverse"
    assert world_state.get_global("non_existent", "default") == "default"
