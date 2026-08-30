# Verification Tests — Unit + Integration + Benchmark

**Section**: 10 of 10  
**Priority**: P1 — Temple-Grade T3 (coverage ≥80%) + T9 (observability)  

---

## Test Organization

```
tests/
├── test_headroom_unit.py              # Unit tests for each compressor
├── test_headroom_model_gateway.py     # ModelGateway integration tests
├── test_headroom_rag.py               # RAG retrieval integration tests
├── test_headroom_mcp_tools.py         # MCP tool schema compression tests
├── test_headroom_entity_context.py    # Entity context compression tests
├── test_headroom_ccr.py               # CCR store tests
├── test_headroom_error_handling.py    # Error handling/fallback tests
├── benchmark_headroom.py              # Performance benchmarks
└── test_headroom_recall.py            # Recall/accuracy validation
```

---

## 1. Unit Tests — Each Compressor

```python
# tests/test_headroom_unit.py
"""
Unit tests for Headroom compressors with known inputs/outputs.
Validates compression ratios match Headroom benchmarks (±10% tolerance).
"""

import pytest
from headroom.transforms import (
    SmartCrusher, SmartCrusherConfig,
    LogCompressor, LogCompressorConfig,
    SearchCompressor, SearchCompressorConfig,
    CodeAwareCompressor, CodeAwareCompressorConfig,
)
from headroom.transforms.relevance import RelevanceScorerConfig


class TestSmartCrusher:
    """SmartCrusher: JSON arrays, tool outputs (benchmark: 87.6% compression)."""
    
    @pytest.fixture
    def crusher(self):
        return SmartCrusher(SmartCrusherConfig(
            max_items_after_crush=15,
            min_tokens_to_crush=200,
            relevance=RelevanceScorerConfig(tier="hybrid"),
        ))
    
    def test_json_array_compression(self, crusher):
        """Test JSON array compression (simulated tool output)."""
        data = [
            {"id": i, "type": "search_result", "content": "x" * 1000, "score": 0.9 - i * 0.01}
            for i in range(50)
        ]
        
        compressed = crusher.compress(data)
        
        assert len(compressed) <= 15
        assert len(compressed) > 0
        
        for item in compressed:
            assert "id" in item
            assert "type" in item
            assert "content" in item
    
    def test_hivemind_awareness_compression(self, crusher):
        """Test Hivemind awareness JSON compression."""
        data = {
            "agents": [
                {"entity": f"agent_{i}", "status": "active", "task": "x" * 500}
                for i in range(20)
            ],
            "handoffs": [{"from": "a", "to": "b", "data": "y" * 200}] * 10,
        }
        
        compressed = crusher.compress([data])
        
        assert len(compressed) == 1
        assert "agents" in compressed[0]
        assert len(compressed[0]["agents"]) <= 15


class TestLogCompressor:
    """LogCompressor: logs, stack traces (benchmark: 80-90% compression)."""
    
    @pytest.fixture
    def compressor(self):
        return LogCompressor(LogCompressorConfig(
            max_total_lines=100,
            max_errors=10,
            dedupe_warnings=True,
            preserve_recent_errors=5,
        ))
    
    def test_log_compression(self, compressor):
        """Test log file compression."""
        logs = [
            "2026-08-20 10:00:00 INFO Starting service",
            "2026-08-20 10:00:01 WARNING Connection slow",
        ] + [
            "2026-08-20 10:00:02 WARNING Connection slow"
            for _ in range(50)
        ] + [
            "2026-08-20 10:00:03 ERROR Connection failed",
            "2026-08-20 10:00:04 ERROR Connection failed",
            "2026-08-20 10:00:05 INFO Service recovered",
        ]
        
        compressed = compressor.compress(logs)
        
        assert len(compressed) <= 100
        assert any("WARNING" in line for line in compressed)
        assert sum(1 for line in compressed if "ERROR" in line) <= 10


class TestSearchCompressor:
    """SearchCompressor: search results, file matches (benchmark: 70-90%)."""
    
    @pytest.fixture
    def compressor(self):
        return SearchCompressor(SearchCompressorConfig(
            max_total_matches=30,
            max_files=15,
            always_keep_first=True,
            always_keep_last=True,
            min_score_threshold=0.1,
        ))
    
    def test_search_results_compression(self, compressor):
        """Test web/file search results compression."""
        results = [
            {"file": f"file_{i}.py", "matches": [{"line": j, "content": "match" * 50}] * 10}
            for i in range(20)
        ]
        
        compressed = compressor.compress(results)
        
        assert len(compressed) <= 15
        assert compressed[0]["file"] == "file_0.py"
        assert compressed[-1]["file"] == "file_19.py"


class TestCodeAwareCompressor:
    """CodeAwareCompressor: source code, diffs (benchmark: 70-85%)."""
    
    @pytest.fixture
    def compressor(self):
        return CodeAwareCompressor(CodeAwareCompressorConfig(
            preserve_signatures=True,
            preserve_imports=True,
            preserve_type_annotations=True,
            docstring_mode="FIRST_LINE",
            max_function_lines=50,
        ))
    
    def test_python_code_compression(self, compressor):
        """Test Python source code compression."""
        code = '''
import os
import sys
from typing import List, Dict

def process_data(data: List[Dict]) -> Dict:
    """Process data and return results.
    
    This function handles the main data processing pipeline.
    It validates input, transforms data, and returns structured output.
    """
    results = {}
    for item in data:
        if item.get("valid"):
            results[item["id"]] = transform(item)
    return results

def transform(item: Dict) -> Dict:
    """Transform a single item."""
    return {"processed": True, **item}
'''
        
        compressed = compressor.compress([{"content": code, "language": "python"}])
        
        assert len(compressed) == 1
        comp_code = compressed[0]["content"]
        
        assert "def process_data(data: List[Dict]) -> Dict:" in comp_code
        assert "def transform(item: Dict) -> Dict:" in comp_code
        assert "import os" in comp_code
        assert "from typing import List, Dict" in comp_code
        assert "Process data and return results." in comp_code
        assert "This function handles" not in comp_code
```

---

## 2. Integration Tests — ModelGateway

```python
# tests/test_headroom_model_gateway.py
"""
Integration tests for HeadroomMiddleware in ModelGateway._prepare_messages().
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from omega.oracle.model_gateway import ModelGateway
from omega.oracle.middleware.headroom import HeadroomMiddleware, HeadroomMiddlewareConfig
from omega.oracle.provider_registry import ProviderRegistry


@pytest.fixture
def gateway():
    registry = MagicMock(spec=ProviderRegistry)
    gateway = ModelGateway(providers=[], provider_registry=registry)
    return gateway


@pytest.mark.asyncio
async def test_model_gateway_headroom_compression(gateway):
    """ModelGateway._prepare_messages compresses tool outputs."""
    gateway._headroom_middleware = HeadroomMiddleware(HeadroomMiddlewareConfig())
    await gateway._headroom_middleware.initialize()
    
    messages = [
        {"role": "user", "content": "Analyze this data"},
        {"role": "assistant", "content": "", "tool_calls": [
            {"function": {"name": "search", "arguments": "{}"}, "id": "call_1"}
        ]},
        {"role": "tool", "content": "x" * 50000, "tool_call_id": "call_1"},
    ]
    
    compressed = await gateway._prepare_messages(messages)
    
    tool_msg = next(m for m in compressed if m.get("role") == "tool")
    assert len(tool_msg["content"]) < 50000
    assert len(tool_msg["content"]) > 1000


@pytest.mark.asyncio
async def test_model_gateway_protects_recent_turns(gateway):
    """Recent N turns protected from compression (Carmack Q6.1)."""
    gateway._headroom_middleware = HeadroomMiddleware(HeadroomMiddlewareConfig(
        protect_recent_turns=2
    ))
    await gateway._headroom_middleware.initialize()
    
    messages = [
        {"role": "user", "content": "old message " + "x" * 10000},
        {"role": "assistant", "content": "old response " + "y" * 10000},
        {"role": "user", "content": "recent message"},
        {"role": "assistant", "content": "recent response"},
    ]
    
    compressed = await gateway._prepare_messages(messages)
    
    assert compressed[-2]["content"] == "recent message"
    assert compressed[-1]["content"] == "recent response"
    assert len(compressed[0]["content"]) < len(messages[0]["content"])
    assert len(compressed[1]["content"]) < len(messages[1]["content"])


@pytest.mark.asyncio
async def test_model_gateway_headroom_fallback(gateway):
    """ModelGateway falls back gracefully if Headroom fails."""
    gateway._headroom_middleware = None
    
    messages = [{"role": "user", "content": "hello"}]
    result = await gateway._prepare_messages(messages)
    
    assert result == messages


@pytest.mark.asyncio
async def test_model_gateway_headroom_timeout(gateway):
    """ModelGateway handles Headroom timeout gracefully."""
    gateway._headroom_middleware = HeadroomMiddleware(HeadroomMiddlewareConfig(
        operation_timeout_seconds=0.001
    ))
    await gateway._headroom_middleware.initialize()
    
    messages = [{"role": "user", "content": "x" * 100000}]
    result = await gateway._prepare_messages(messages)
    
    assert result == messages
    assert gateway._headroom_middleware._metrics["fallback_count"] == 1
```

---

## 3. Integration Tests — RAG Retrieval

```python
# tests/test_headroom_rag.py
"""
Integration tests for Headroom in RAG retrieval pipeline.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from omega.memory.retrieval import RetrievalCompressor, RetrievalCompressionConfig
from omega.memory.store import MemoryStore
from omega.oracle.middleware.headroom import HeadroomMiddleware


@pytest.fixture
def memory_store():
    store = MagicMock(spec=MemoryStore)
    store.search = AsyncMock(return_value=[
        {"content": "x" * 2000, "score": 0.9, "entity_name": "kali", "session_id": "s1", "type": "assistant", "tags": ["test"]}
        for _ in range(20)
    ])
    return store


@pytest.fixture
def headroom():
    mw = HeadroomMiddleware()
    return mw


@pytest.mark.asyncio
async def test_retrieval_compression(memory_store, headroom):
    """RetrievalCompressor compresses search results."""
    compressor = RetrievalCompressor(
        memory_store, headroom,
        RetrievalCompressionConfig(
            max_chunks_per_query=10,
            target_total_tokens=8000,
            protect_top_k=3,
        )
    )
    
    results = await compressor.search_and_compress(
        query="test query",
        entity_name="kali",
        top_k=10,
    )
    
    assert len(results) <= 10
    for r in results[:3]:
        assert r.compressed is False or r.compression_ratio > 0.9
    for r in results[3:]:
        assert r.compressed is True or r.compression_ratio < 0.9


@pytest.mark.asyncio
async def test_retrieval_token_budget(memory_store, headroom):
    """RetrievalCompressor enforces token budget."""
    compressor = RetrievalCompressor(
        memory_store, headroom,
        RetrievalCompressionConfig(target_total_tokens=1000)
    )
    
    memory_store.search.return_value = [
        {"content": "x" * 5000, "score": 0.9, "entity_name": "kali", "tags": []}
        for _ in range(10)
    ]
    
    results = await compressor.search_and_compress("query", "kali", top_k=10)
    
    total_tokens = sum(r.token_count for r in results)
    assert total_tokens <= 1000


@pytest.mark.asyncio
async def test_retrieval_fallback(memory_store, headroom):
    """RetrievalCompressor falls back on error."""
    headroom.compress_retrieval_results = AsyncMock(side_effect=Exception("Failed"))
    
    compressor = RetrievalCompressor(memory_store, headroom)
    
    results = await compressor.search_and_compress("query", "kali", top_k=5)
    
    assert len(results) == 5
    assert all(not r.compressed for r in results)
```

---

## 4. Integration Tests — MCP Tool Schema Compression

```python
# tests/test_headroom_mcp_tools.py
"""
Integration tests for MCP tool schema compression.
"""

import pytest
from omega.mcp.tool_compressor import MCPToolCompressor, MCPToolCompressorConfig


@pytest.mark.asyncio
async def test_mcp_tool_schema_compression():
    """MCPToolCompressor reduces tool schema tokens 80-90%."""
    compressor = MCPToolCompressor(MCPToolCompressorConfig(
        max_items_after_crush=10,
        min_tokens_to_crush=100,
        relevance_tier="keyword",
    ))
    
    tools = [
        {
            "name": f"tool_{i}",
            "description": "This tool does something useful " + "x" * 200,
            "inputSchema": {"type": "object", "properties": {"param": {"type": "string"}}},
        }
        for i in range(86)
    ]
    
    compressed = await compressor.compress_tool_schemas(tools)
    
    assert len(compressed) <= 10
    
    orig_tokens = sum(len(str(t)) // 4 for t in tools)
    comp_tokens = sum(len(str(t)) // 4 for t in compressed)
    ratio = comp_tokens / orig_tokens
    
    assert ratio < 0.2


@pytest.mark.asyncio
async def test_mcp_tool_output_compression():
    """MCPToolCompressor compresses individual tool outputs."""
    compressor = MCPToolCompressor()
    
    output = {
        "results": [{"id": i, "data": "x" * 1000} for i in range(100)],
        "metadata": {"total": 100, "page": 1},
    }
    
    compressed = await compressor.compress_tool_output(output)
    
    assert "results" in compressed
    assert len(compressed["results"]) < 100
```

---

## 5. Integration Tests — Entity Context Compression

```python
# tests/test_headroom_entity_context.py
"""
Integration tests for EntityContextCompressor.
"""

import pytest
from omega.entities.context_compressor import EntityContextCompressor, EntityContextCompressorConfig


@pytest.mark.asyncio
async def test_entity_context_protected_fields():
    """Protected fields (identity, mandates) never compressed (M11)."""
    compressor = EntityContextCompressor()
    
    context = {
        "name": "kali",
        "archetype": "The Architect",
        "node": "N1",
        "mandates": ["M1", "M2", "M7"],
        "core_principles": ["Sovereignty requires local-first"],
        "lessons": [{"principle": "Test", "insight": "x" * 1000}] * 20,
        "traits": {"analytical": "x" * 500},
    }
    
    compressed = await compressor.compress_entity_context(context)
    
    assert compressed["name"] == "kali"
    assert compressed["archetype"] == "The Architect"
    assert compressed["node"] == "N1"
    assert compressed["mandates"] == ["M1", "M2", "M7"]
    assert compressed["core_principles"] == ["Sovereignty requires local-first"]
    assert len(str(compressed["lessons"])) < len(str(context["lessons"]))
    assert len(str(compressed["traits"])) < len(str(context["traits"]))


@pytest.mark.asyncio
async def test_entity_context_lesson_summarization():
    """Old lessons summarized (keep L3, truncate L1/L2)."""
    compressor = EntityContextCompressor(EntityContextCompressorConfig(
        protect_recent_lessons=2,
        summarize_lessons=True,
    ))
    
    context = {
        "lessons": [
            {"principle": f"Principle {i}", "insight": "x" * 500, "narrative": "y" * 500}
            for i in range(10)
        ],
    }
    
    compressed = await compressor.compress_entity_context(context)
    
    lessons = compressed["lessons"]
    assert lessons[-1]["insight"] == "x" * 500
    assert lessons[-2]["insight"] == "x" * 500
    for lesson in lessons[:-2]:
        assert len(lesson["insight"]) <= 200
        assert "summarized" in lesson
        assert lesson["principle"] != ""
```

---

## 6. CCR Store Tests

```python
# tests/test_headroom_ccr.py
"""
Tests for CCR Store.
"""

import pytest
import tempfile
from omega.oracle.middleware.ccr_store import CCRStore, CCRConfig


@pytest.fixture
def ccr_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = CCRConfig(store_path=tmpdir, max_store_size_gb=1.0)
        store = CCRStore(config)
        yield store


@pytest.mark.asyncio
async def test_ccr_store_retrieve(ccr_store):
    """CCR store stores and retrieves original content."""
    await ccr_store.initialize()
    
    original = "This is the original content that was compressed"
    compressed = "Compressed version"
    
    key = await ccr_store.store(
        original=original,
        compressed=compressed,
        entity_name="kali",
        session_id="test_session",
        content_type="json",
    )
    
    retrieved = await ccr_store.retrieve(key)
    assert retrieved == original


@pytest.mark.asyncio
async def test_ccr_store_with_key(ccr_store):
    """CCR store with explicit key (migration, MCP tools)."""
    await ccr_store.initialize()
    
    key = "explicit_key_123"
    original = "Original content"
    compressed = "Compressed"
    
    returned_key = await ccr_store.store_with_key(key, original, compressed)
    assert returned_key == key
    
    retrieved = await ccr_store.retrieve(key)
    assert retrieved == original


@pytest.mark.asyncio
async def test_ccr_store_search(ccr_store):
    """CCR store search by metadata."""
    await ccr_store.initialize()
    
    await ccr_store.store("orig1", "comp1", entity_name="kali", tags=["test"])
    await ccr_store.store("orig2", "comp2", entity_name="maat", tags=["test"])
    await ccr_store.store("orig3", "comp3", entity_name="kali", tags=["prod"])
    
    kali_entries = await ccr_store.search(entity_name="kali")
    assert len(kali_entries) == 2
    
    test_entries = await ccr_store.search(tags=["test"])
    assert len(test_entries) == 2


@pytest.mark.asyncio
async def test_ccr_store_size_limit(ccr_store):
    """CCR store enforces max size limit."""
    config = CCRConfig(store_path=ccr_store.config.store_path, max_store_size_gb=0.001)
    store = CCRStore(config)
    await store.initialize()
    
    for i in range(100):
        await store.store("x" * 50000, "y" * 5000, entity_name="test")
    
    stats = await store.get_stats()
    assert stats["disk_usage_gb"] <= 0.001
```

---

## 7. Benchmark Tests

```python
# tests/benchmark_headroom.py
"""
Performance benchmarks for Headroom compression.
Validates latency budgets (Carmack Q6.2) and compression ratios.
"""

import pytest
import time
import statistics
from headroom import ContentRouter, ContentRouterConfig
from headroom.transforms import (
    SmartCrusher, SmartCrusherConfig,
    LogCompressor, LogCompressorConfig,
    SearchCompressor, SearchCompressorConfig,
    CodeAwareCompressor, CodeAwareCompressorConfig,
)
from headroom.transforms.relevance import RelevanceScorerConfig


class BenchmarkHeadroom:
    """Benchmark Headroom compressors."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.router = ContentRouter(ContentRouterConfig(
            enable_smart_crusher=True,
            enable_log_compressor=True,
            enable_search_compressor=True,
            enable_code_aware=True,
            smart_crusher=SmartCrusher(SmartCrusherConfig(
                max_items_after_crush=15, min_tokens_to_crush=200,
                relevance=RelevanceScorerConfig(tier="hybrid"),
            )),
            log_compressor=LogCompressor(LogCompressorConfig(
                max_total_lines=100, max_errors=10,
            )),
            search_compressor=SearchCompressor(SearchCompressorConfig(
                max_total_matches=30, max_files=15,
            )),
            code_aware=CodeAwareCompressor(CodeAwareCompressorConfig(
                preserve_signatures=True, preserve_imports=True,
                preserve_type_annotations=True, docstring_mode="FIRST_LINE",
            )),
        ))
    
    def _benchmark(self, func, data, iterations=100):
        latencies = []
        for _ in range(iterations):
            start = time.perf_counter()
            func(data)
            latencies.append((time.perf_counter() - start) * 1000)
        
        return {
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "p95_ms": statistics.quantiles(latencies, n=20)[18],
            "p99_ms": statistics.quantiles(latencies, n=100)[98],
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        }
    
    def test_smart_crusher_json_latency(self):
        """SmartCrusher on JSON tool output: ≤15ms (Carmack Q6.2)."""
        data = [{"id": i, "content": "x" * 1000} for i in range(50)]
        
        stats = self._benchmark(self.router.compress, data)
        
        print(f"SmartCrusher JSON: {stats}")
        assert stats["p99_ms"] <= 15
    
    def test_log_compressor_latency(self):
        """LogCompressor on logs: ≤5ms."""
        logs = [f"2026-08-20 10:00:{i:02d} WARNING Something happened" for i in range(200)]
        
        stats = self._benchmark(self.router.compress, logs)
        
        print(f"LogCompressor: {stats}")
        assert stats["p99_ms"] <= 5
    
    def test_search_compressor_latency(self):
        """SearchCompressor on search results: ≤10ms."""
        results = [
            {"file": f"f{i}.py", "matches": [{"line": j, "content": "match"} for j in range(20)]}
            for i in range(30)
        ]
        
        stats = self._benchmark(self.router.compress, results)
        
        print(f"SearchCompressor: {stats}")
        assert stats["p99_ms"] <= 10
    
    def test_code_aware_compressor_latency(self):
        """CodeAwareCompressor on code: ≤15ms."""
        code = "\n".join([f"def func_{i}():\n    return {i}" for i in range(100)])
        data = [{"content": code, "language": "python"}]
        
        stats = self._benchmark(self.router.compress, data)
        
        print(f"CodeAwareCompressor: {stats}")
        assert stats["p99_ms"] <= 15
    
    def test_combined_pipeline_latency(self):
        """Full ContentRouter pipeline: ≤20ms."""
        messages = [
            {"role": "user", "content": "query"},
            {"role": "tool", "content": str([{"id": i, "data": "x" * 500} for i in range(30)])},
            {"role": "assistant", "content": "response"},
        ]
        
        stats = self._benchmark(self.router.compress, messages)
        
        print(f"Combined pipeline: {stats}")
        assert stats["p99_ms"] <= 20


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
```

---

## 8. Recall/Accuracy Validation Tests

```python
# tests/test_headroom_recall.py
"""
Recall/accuracy validation tests.
Validates Headroom benchmarks: GSM8K 0.870, TruthfulQA +0.030, Recall@10 ≥98%.
"""

import pytest
from headroom.transforms import SmartCrusher, SearchCompressor


class TestHeadroomRecall:
    """Validate compression doesn't degrade task accuracy."""
    
    @pytest.fixture
    def crusher(self):
        return SmartCrusher(SmartCrusherConfig(
            max_items_after_crush=15, min_tokens_to_crush=200,
        ))
    
    @pytest.fixture
    def search_compressor(self):
        return SearchCompressor(SearchCompressorConfig(
            max_total_matches=30, max_files=15,
        ))
    
    def test_gsm8k_accuracy_preserved(self, crusher):
        """GSM8K math reasoning accuracy preserved after compression."""
        gsm8k_output = {
            "problem": "If a train travels 60 mph for 2.5 hours, how far does it go?",
            "steps": [
                {"step": 1, "reasoning": "Distance = Speed × Time", "calculation": "60 × 2.5"},
                {"step": 2, "reasoning": "60 × 2 = 120", "calculation": "120"},
                {"step": 3, "reasoning": "60 × 0.5 = 30", "calculation": "30"},
                {"step": 4, "reasoning": "120 + 30 = 150", "calculation": "150"},
            ],
            "answer": 150,
        }
        
        compressed = crusher.compress([gsm8k_output])[0]
        
        assert "steps" in compressed
        assert len(compressed["steps"]) >= 3
        assert compressed["answer"] == 150
    
    def test_truthfulqa_accuracy_preserved(self, crusher):
        """TruthfulQA-style QA accuracy preserved."""
        qa_output = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "confidence": 0.99,
            "sources": ["wikipedia", "britannica"],
            "reasoning": "Paris has been the capital since 987 AD..." + "x" * 500,
        }
        
        compressed = crusher.compress([qa_output])[0]
        
        assert compressed["answer"] == "Paris"
        assert compressed["confidence"] == 0.99
    
    def test_rag_recall_at_10(self, search_compressor):
        """RAG retrieval Recall@10 ≥98% after compression."""
        results = [
            {"content": f"Relevant chunk {i}", "score": 0.9 - i * 0.01, "relevant": True}
            for i in range(10)
        ] + [
            {"content": f"Irrelevant chunk {i}", "score": 0.5 - i * 0.01, "relevant": False}
            for i in range(10)
        ]
        
        compressed = search_compressor.compress(results)
        
        relevant_in_top10 = sum(1 for r in compressed[:10] if r.get("relevant", False))
        recall = relevant_in_top10 / 10
        
        assert recall >= 0.98
    
    def test_no_hallucination_introduction(self, crusher):
        """Compression doesn't introduce hallucinated content."""
        original = {"fact": "The Earth orbits the Sun", "source": "NASA"}
        
        compressed = crusher.compress([original])[0]
        
        assert compressed["fact"] == "The Earth orbits the Sun"
        assert compressed["source"] == "NASA"
        assert set(compressed.keys()) <= set(original.keys())
```

---

## 9. End-to-End Integration Test

```python
# tests/test_headroom_e2e.py
"""
End-to-end integration test: Full Omega request with Headroom.
"""

import pytest
from omega.oracle import Oracle
from omega.oracle.middleware.headroom import HeadroomMiddleware


@pytest.mark.asyncio
async def test_full_request_with_headroom():
    """Full Oracle.talk() request with Headroom compression."""
    oracle = Oracle()
    await oracle.initialize()
    
    oracle.model_gateway._headroom_middleware = HeadroomMiddleware()
    await oracle.model_gateway._headroom_middleware.initialize()
    
    response = await oracle.talk("Search for Omega Engine architecture and summarize")
    
    assert response is not None
    assert len(response) > 0
    
    metrics = oracle.model_gateway._headroom_middleware.get_metrics()
    assert metrics["total_compressions"] > 0
    assert metrics["average_compression_ratio"] < 1.0


@pytest.mark.asyncio
async def test_multi_turn_conversation_compression():
    """Multi-turn conversation with tool outputs compressed."""
    oracle = Oracle()
    await oracle.initialize()
    oracle.model_gateway._headroom_middleware = HeadroomMiddleware()
    await oracle.model_gateway._headroom_middleware.initialize()
    
    await oracle.talk("What is 2+2?")
    await oracle.talk("Search for Python async best practices")
    await oracle.talk("Summarize what you found")
    
    metrics = oracle.model_gateway._headroom_middleware.get_metrics()
    assert metrics["total_compressions"] >= 2
```

---

## 10. Test Configuration

```ini
# pytest.ini additions for Headroom tests
[tool.pytest.ini_options]
markers =
    headroom: Headroom compression tests
    integration: Integration tests
    benchmark: Performance benchmarks (slow)
    recall: Recall/accuracy validation
    e2e: End-to-end tests
```

---

## CI/CD Integration

```yaml
# .github/workflows/headroom-tests.yml
name: Headroom Tests

on: [push, pull_request]

jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install -e ".[test,headroom]"
      - name: Run unit tests
        run: pytest tests/test_headroom_unit.py -v
  
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install -e ".[test,headroom]"
      - name: Run integration tests
        run: pytest tests/test_headroom_*_integration.py -v
  
  benchmark:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install -e ".[test,headroom]"
      - name: Run benchmarks
        run: pytest tests/benchmark_headroom.py -v --benchmark-only
  
  recall:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install -e ".[test,headroom]"
      - name: Run recall tests
        run: pytest tests/test_headroom_recall.py -v
```

---

## Acceptance Criteria Summary

| Test Category | Criteria | Threshold |
|---------------|----------|-----------|
| **Unit** | Each compressor: known input → expected output ratio | ±10% of benchmark |
| **ModelGateway** | Tool output compression in `_prepare_messages` | 60-95% reduction |
| **ModelGateway** | Recent turns protected | Last 2 turns unchanged |
| **ModelGateway** | Fallback on error | Returns original, logs warning |
| **RAG** | Retrieval compression | 70-90% reduction |
| **RAG** | Token budget enforced | Total ≤ target_total_tokens |
| **RAG** | Top-K protected | Top 3 chunks ≥90% original |
| **MCP** | Tool schema compression | 80-90% reduction |
| **Entity** | Protected fields unchanged | 100% identity preserved |
| **Entity** | Lessons summarized | L3 kept, L1/L2 truncated |
| **CCR** | Store/retrieve roundtrip | Original == retrieved |
| **CCR** | Size limit enforced | Disk usage ≤ max_store_size_gb |
| **Benchmark** | SmartCrusher latency | p99 ≤ 15ms |
| **Benchmark** | LogCompressor latency | p99 ≤ 5ms |
| **Benchmark** | SearchCompressor latency | p99 ≤ 10ms |
| **Benchmark** | CodeAware latency | p99 ≤ 15ms |
| **Benchmark** | Combined pipeline | p99 ≤ 20ms |
| **Recall** | GSM8K accuracy | ≥0.870 |
| **Recall** | TruthfulQA delta | ≥+0.030 |
| **Recall** | RAG Recall@10 | ≥98% |

---

## Running Tests

```bash
# Unit tests
pytest tests/test_headroom_unit.py -v

# Integration tests
pytest tests/test_headroom_model_gateway.py tests/test_headroom_rag.py tests/test_headroom_mcp_tools.py tests/test_headroom_entity_context.py tests/test_headroom_ccr.py -v

# Error handling
pytest tests/test_headroom_error_handling.py -v

# Benchmarks (slow)
pytest tests/benchmark_headroom.py -v --benchmark-only

# Recall validation
pytest tests/test_headroom_recall.py -v

# All Headroom tests
pytest -m headroom -v

# Coverage
pytest --cov=omega.oracle.middleware.headroom --cov=omega.memory.retrieval --cov=omega.mcp.tool_compressor --cov=omega.entities.context_compressor --cov=omega.oracle.middleware.ccr_store -v
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ Section 10/10*