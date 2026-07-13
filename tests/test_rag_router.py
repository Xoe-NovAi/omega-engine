# 🔱 Omega Engine — RAG Router Tests (M21 Contract Tests)
# AP: AP-TEST-RAG-ROUTER-v1.0.0
# ⬡ OMEGA ⬡ LILITH ⬡ test_rag_router ⬡ S3
"""Contract tests for the Tiny-Critic RAG Router and RAG answer paths."""

import pytest

from omega.rag.router import RAGRouter
from omega.rag.simple_rag import SimpleRAG
from omega.rag.iterative_rag import IterativeRAG


@pytest.mark.asyncio
async def test_router_classifies_simple_query():
    router = RAGRouter(mode="tfidf_svm")
    result = await router.classify("What time is it?")
    assert result == "simple"
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_router_classifies_complex_query():
    router = RAGRouter(mode="tfidf_svm")
    result = await router.classify(
        "Compare the 23 Sovereign Mandates across all pillars and identify contradictions"
    )
    assert result == "complex"


@pytest.mark.asyncio
async def test_router_heuristic_mode():
    router = RAGRouter(mode="heuristic")
    assert await router.classify("Who is the current president?") == "simple"
    assert await router.classify("Analyze the trade-offs between local and cloud inference") == "complex"


@pytest.mark.asyncio
async def test_router_unknown_mode_raises():
    with pytest.raises(ValueError):
        RAGRouter(mode="not_a_mode")


@pytest.mark.asyncio
async def test_simple_rag_instantiable_and_answers():
    rag = SimpleRAG()
    assert isinstance(rag, SimpleRAG)
    # No gateway → graceful offline fallback (returns str, never raises)
    out = await rag.answer("What time is it?")
    assert isinstance(out, str)


@pytest.mark.asyncio
async def test_iterative_rag_instantiable_and_answers():
    rag = IterativeRAG()
    assert isinstance(rag, IterativeRAG)
    out = await rag.answer("Compare the mandates and synthesize a report")
    assert isinstance(out, str)
