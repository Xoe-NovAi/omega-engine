# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Contract Tests for YouTube Researcher V2 (L1-L8)
⬡ OMEGA ⬡ VERITY ⬡ TEST ⬡ YOUTUBE_V2
AP Token: AP-YOUTUBE-TESTS-v2.0.0

M21 Gate Integrity: Every code path returning a typed result MUST be exercised by at least one test that validates the return type.
"""

import pytest
import anyio
from pathlib import Path
from datetime import datetime, timezone

from src.omega_youtube_research.transcriber import Transcriber, CheckpointingTranscriber, TranscriptFidelity
from src.omega_youtube_research.proxy_identity import YouTubeIdentity, AdaptiveRateLimiter
from src.omega_youtube_research.chunker import TemporalChunk, semantic_chunk
from src.omega_youtube_research.cas_archiver import CASArchiver, CASRecord, CASConfig
from src.omega_youtube_research.gnosis_bridge import (
    emit_gnosis_edges, GnosisEdge, GnosisEdgeType, GnosisEpisode,
    assert_gnosis_edge_type, assert_emit_gnosis_edges_signature
)
from src.omega_youtube_research.faithfulness import (
    verify_provenance, CalibratedJudge, FaithfulnessResult,
    assert_calibrated_judge_type, assert_faithfulness_result_type
)
from src.omega_youtube_research.freshness import (
    freshness_score, detect_drift, check_retrievability, MemoryType,
    assert_freshness_score_range, assert_decay_monotonicity, assert_access_boost_monotonicity
)
from src.omega_youtube_research.steering import (
    inject_steering, BackgroundResearcherQueue, ResearchTask, 
    SteeringTaskType, TaskPriority, TaskStatus,
    assert_research_task_type, assert_background_queue_type
)

# ── L1/L9: Transcriber Tests ──────────────────────────────────────────────────

@pytest.mark.anyio
async def test_transcriber_fidelity_type():
    """M21: Verify TranscriptFidelity return type."""
    # TranscriptFidelity computes score from other fields
    # Score = 0.4*confidence + 0.2*punct + 0.2*speaker + 0.2*technical
    # = 0.4*0.85 + 0.2*1 + 0.2*1 + 0.2*1 = 0.34 + 0.2 + 0.2 + 0.2 = 0.94
    fidelity = TranscriptFidelity(
        confidence_avg=0.85,
        has_punctuation=True,
        speaker_labeled=True,
        technical_correct=True
    )
    assert isinstance(fidelity, TranscriptFidelity)
    assert fidelity.score == pytest.approx(0.94, rel=0.01)

@pytest.mark.anyio
async def test_checkpointing_transcriber_type():
    """M21: Verify CheckpointingTranscriber initialization."""
    # Skip if faster-whisper not available
    try:
        transcriber = Transcriber()
        cp = CheckpointingTranscriber(
            transcriber=transcriber,
            checkpoint_path=Path("tests/tmp_checkpoint.json"),
            save_every=10
        )
        assert isinstance(cp, CheckpointingTranscriber)
    except RuntimeError as e:
        if "faster-whisper not installed" in str(e):
            pytest.skip("faster-whisper not installed")
        raise


# ── L2: Proxy & Rate Limiter Tests ───────────────────────────────────────────

def test_youtube_identity_type():
    """M21: Verify YouTubeIdentity return type."""
    identity = YouTubeIdentity(session_id="test-session", proxy_base="http://proxy:8080")
    assert isinstance(identity, YouTubeIdentity)
    assert identity.session_id == "test-session"

def test_adaptive_rate_limiter_type():
    """M21: Verify AdaptiveRateLimiter return type."""
    identity = YouTubeIdentity(session_id="test-session", proxy_base="http://proxy:8080")
    limiter = AdaptiveRateLimiter(identity=identity, base_rate=1.0, max_tokens=10)
    assert isinstance(limiter, AdaptiveRateLimiter)
    assert limiter.base_rate == 1.0


# ── L3: Chunker Tests ─────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_semantic_chunk_type():
    """M21: Verify semantic_chunk return type."""
    segments = [{"text": "This is a test sentence.", "start": 0.0, "end": 10.0}]
    chunks = await semantic_chunk(segments)
    assert isinstance(chunks, list)
    if chunks:
        assert isinstance(chunks[0], TemporalChunk)


# ── L4: CAS Archiver Tests ─────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_cas_archiver_type():
    """M21: Verify CASArchiver return type."""
    config = CASConfig(store_path=Path("tests/tmp_cas"))
    cas = CASArchiver(config)
    assert isinstance(cas, CASArchiver)
    
    text = "Sovereign AI is the future."
    chunk = TemporalChunk(text=text, t_start=0.0, t_end=10.0)
    cas_hash = await cas.archive(chunk)
    assert isinstance(cas_hash, str)
    
    record = cas.get_chunk(cas_hash)
    assert isinstance(record, CASRecord)
    assert record.text == text


# ── L5: Gnosis Bridge Tests ───────────────────────────────────────────────────

def test_gnosis_edge_type():
    """M21: Verify GnosisEdge return type."""
    edge = GnosisEdge(
        source_id="vid123",
        target_id="paper456",
        edge_type=GnosisEdgeType.IMPLEMENTS,
        confidence=0.9
    )
    assert_gnosis_edge_type(edge)

def test_emit_gnosis_edges_type():
    """M21: Verify emit_gnosis_edges return type."""
    chunks = [TemporalChunk(text="This video implements arXiv:2301.0001", cas_hash="h1", t_start=0.0, t_end=10.0)]
    edges = emit_gnosis_edges("vid123", chunks)
    assert isinstance(edges, list)
    if edges:
        assert isinstance(edges[0], GnosisEdge)
    assert_emit_gnosis_edges_signature()


# ── L6: Faithfulness Tests ─────────────────────────────────────────────────────

def test_calibrated_judge_type():
    """M21: Verify CalibratedJudge return type."""
    judge = CalibratedJudge()
    assert_calibrated_judge_type(judge)

@pytest.mark.anyio
async def test_verify_provenance_type():
    """M21: Verify verify_provenance return type."""
    chunks = [TemporalChunk(text="Sovereign AI is local.", cas_hash="h1", t_start=0.0, t_end=10.0)]
    # Use mock NLI scorer to avoid downloading model
    class MockNLI:
        def score_entailment(self, premise, hypothesis):
            return 0.9
    
    result = await verify_provenance(
        synthesis="Sovereign AI is local.",
        chunks=chunks,
        question="What is Sovereign AI?",
        nli_scorer=MockNLI()
    )
    assert_faithfulness_result_type(result)
    assert isinstance(result.passed, bool)


# ── L7: Freshness Tests ───────────────────────────────────────────────────────

def test_freshness_score_type():
    """M21: Verify freshness_score return type."""
    pub_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    score = freshness_score(pub_date, MemoryType.FACT, access_count=5)
    assert isinstance(score, float)
    assert_freshness_score_range(score)

def test_freshness_decay_monotonicity():
    """M21: Verify freshness decreases as date gets older."""
    dates = [
        datetime(2026, 7, 1, tzinfo=timezone.utc),
        datetime(2026, 6, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    ]
    assert_decay_monotonicity(dates, MemoryType.FACT)

def test_access_boost_monotonicity():
    """M21: Verify access boost increases with access count."""
    assert_access_boost_monotonicity()

def test_retrievability_check_type():
    """M21: Verify check_retrievability return type."""
    chunk = TemporalChunk(text="test", t_start=0.0, t_end=10.0)
    # Use extremely old age (2000 days) to ensure freshness well below 0.1 floor
    # FACT half-life = 180 days, so at 2000 days: 2^(-2000/180) ≈ 0.00044
    # With access_count=0: boost = 1.0, effective = 0.00044 < 0.1 floor
    res = check_retrievability(
        chunk=chunk,
        age_days=2000,
        last_accessed_days=200,
        access_count=0,
        has_active_relations=False,
        superseded_age_days=400
    )
    assert res.retrievable is False
    assert "age > 365 days" in res.reasons
    assert "raw freshness" in " ".join(res.reasons)


# ── L8: Steering Tests ─────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_steering_queue_type():
    """M21: Verify BackgroundResearcherQueue return type."""
    queue = BackgroundResearcherQueue(Path("tests/tmp_queue"))
    assert_background_queue_type(queue)
    
    task = ResearchTask(
        task_type=SteeringTaskType.YOUTUBE_DEEP_DIVE,
        topic_filter="AI Sovereignty",
        human_prompt="Deep dive into AI sovereignty"
    )
    assert_research_task_type(task)
    
    task_id = await queue.push(task)
    assert isinstance(task_id, str)
    
    popped = await queue.pop()
    assert popped.task_id == task_id
    assert popped.status == TaskStatus.RUNNING
    
    await queue.complete(popped, {"result": "success"})
    task = await queue.get_task(task_id)
    assert task.status == TaskStatus.COMPLETED


@pytest.mark.anyio
async def test_inject_steering_type():
    """M21: Verify inject_steering return type."""
    queue = BackgroundResearcherQueue(Path("tests/tmp_queue_inject"))
    task_id = await inject_steering(
        prompt="Deep dive into AI",
        queue=queue
    )
    assert isinstance(task_id, str)
    
    task = await queue.get_task(task_id)
    assert isinstance(task, ResearchTask)
    assert task.task_type == SteeringTaskType.YOUTUBE_DEEP_DIVE