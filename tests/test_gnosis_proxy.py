"""Tests for GnosisProxy (Invisible RAG middleware)."""

import pytest

from omega.oracle.gnosis_proxy import GnosisProxy, DescriptorRef
from omega.oracle.entity_registry import EntityRegistry


@pytest.fixture
def registry():
    return EntityRegistry()


@pytest.fixture
def proxy(registry):
    return GnosisProxy(registry=registry)


def test_create_transfer_descriptor(proxy):
    """Creating a transfer descriptor should store data and return a reference."""
    data = {"secret": "the universe is a simulation", "score": 42}
    desc = proxy.create_transfer_descriptor(data, resource_type="state")

    assert isinstance(desc, DescriptorRef)
    assert desc.resource_type == "state"
    assert desc.uri.startswith("omega://transfer/")
    assert desc.descriptor_id in proxy.transfer_store
    assert proxy.transfer_store[desc.descriptor_id] is data


def test_resolve_descriptor(proxy):
    """Resolving a descriptor should return the original data."""
    data = [1, 2, 3, "four"]
    desc = proxy.create_transfer_descriptor(data)
    resolved = proxy.resolve_descriptor(desc.descriptor_id)
    assert resolved == data
    assert resolved[3] == "four"


def test_resolve_nonexistent_descriptor(proxy):
    """Resolving a non-existent descriptor should raise KeyError."""
    with pytest.raises(KeyError, match="not found or expired"):
        proxy.resolve_descriptor("nonexistent_id")


def test_create_descriptor_unique_ids(proxy):
    """Each descriptor should have a unique ID."""
    desc1 = proxy.create_transfer_descriptor("data1")
    desc2 = proxy.create_transfer_descriptor("data2")
    assert desc1.descriptor_id != desc2.descriptor_id


def test_descriptor_metadata_tracks_size(proxy):
    """Descriptor metadata should include the size of the original data."""
    data = "x" * 100
    desc = proxy.create_transfer_descriptor(data)
    assert desc.metadata["size"] == 100


def test_descriptor_metadata_large_data(proxy):
    """Descriptor metadata size should reflect large payloads."""
    data = {"big": "x" * 1000}
    desc = proxy.create_transfer_descriptor(data)
    assert isinstance(desc.metadata["size"], int)
    assert desc.metadata["size"] > 1000


def test_discover_tools_empty_query(proxy):
    """Empty query should return no tools."""
    tools = proxy.discover_tools("", "Sophia", top_k=3)
    assert isinstance(tools, list)


def test_discover_tools_structure(proxy):
    """discover_tools should return a list of dicts."""
    tools = proxy.discover_tools("wisdom", "Sophia", top_k=3)
    assert isinstance(tools, list)
    if tools:
        assert "name" in tools[0] or "description" in tools[0]


def test_discover_tools_invalid_entity(proxy):
    """Invalid entity name should not raise."""
    tools = proxy.discover_tools("test", "NonExistentEntity12345", top_k=3)
    assert isinstance(tools, list)


@pytest.mark.asyncio
async def test_wrap_tool_call_no_descriptors(proxy):
    """wrap_tool_call with regular args should pass them through unchanged."""
    result = await proxy.wrap_tool_call("my_tool", {"arg1": "hello", "arg2": 42})
    assert result["tool"] == "my_tool"
    assert result["arguments"] == {"arg1": "hello", "arg2": 42}


@pytest.mark.asyncio
async def test_wrap_tool_call_with_descriptor(proxy):
    """wrap_tool_call should resolve omega://transfer/ URIs."""
    data = {"resolved": "payload"}
    desc = proxy.create_transfer_descriptor(data)
    result = await proxy.wrap_tool_call("my_tool", {"payload": desc.uri, "other": "value"})
    assert result["arguments"]["payload"] == data
    assert result["arguments"]["other"] == "value"


@pytest.mark.asyncio
async def test_wrap_tool_call_partial_descriptors(proxy):
    """wrap_tool_call should handle mixed descriptor/non-descriptor args."""
    desc = proxy.create_transfer_descriptor("secret_data")
    result = await proxy.wrap_tool_call("tool", {
        "normal": "plain",
        "transfer": desc.uri,
        "number": 99,
    })
    assert result["arguments"]["normal"] == "plain"
    assert result["arguments"]["transfer"] == "secret_data"
    assert result["arguments"]["number"] == 99


def test_gnosis_proxy_fifo_eviction(proxy):
    """Verify that the transfer store evicts the oldest descriptors when full."""
    # Fill the store to its limit
    for i in range(GnosisProxy.MAX_TRANSFER_STORE_SIZE):
        proxy.create_transfer_descriptor(f"data_{i}")
    
    # The first one created should be 'data_0'
    first_id = list(proxy._store_keys)[0]
    
    # Add one more to trigger eviction
    proxy.create_transfer_descriptor("overflow_data")
    
    # The first one should now be gone
    with pytest.raises(KeyError):
        proxy.resolve_descriptor(first_id)
    
    assert len(proxy.transfer_store) == GnosisProxy.MAX_TRANSFER_STORE_SIZE
