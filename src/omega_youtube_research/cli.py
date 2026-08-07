"""
L1-L9 YouTube Researcher CLI
⬡ OMEGA ⬡ RESEARCHER ⬡ CLI
AP Token: AP-YOUTUBE-CLI-v2.0.0

Commands:
  omega youtube ingest <video_id>          # Ingest transcript (P0 pipeline)
  omega youtube transcribe <video_id>      # T1→T2→T3 extraction with TFS
  omega youtube chunk <video_id>           # Semantic chunk + CAS archive
  omega youtube steer "prompt"             # L8 Oracle Steering Queue injection
  omega youtube status <task_id>           # Check steering task status
  omega youtube freshness <video_id>       # L7 Freshness audit
  omega youtube faithfulness <video_id>    # L6 Faithfulness audit
  omega youtube gnosis <video_id>          # L5 Gnosis Graph edges
  omega youtube cas-stats                  # L4 CAS storage stats
"""

import typer
import asyncio
import json
from pathlib import Path
from typing import Optional

from src.omega_youtube_research.module import YouTubeResearchModule
from src.omega_youtube_research.config import YouTubeResearchConfig
from src.omega_youtube_research.transcriber import Transcriber, CheckpointingTranscriber, TranscriptFidelity
from src.omega_youtube_research.chunker import TemporalChunk, semantic_chunk, hybrid_search
from src.omega_youtube_research.cas_archiver import CASArchiver
from src.omega_youtube_research.gnosis_bridge import emit_gnosis_edges, GnosisEdge, GnosisEdgeType
from src.omega_youtube_research.faithfulness import verify_provenance, CalibratedJudge, FaithfulnessResult
from src.omega_youtube_research.freshness import freshness_score, detect_drift, check_retrievability, MemoryType
from src.omega_youtube_research.steering import (
    inject_steering, 
    BackgroundResearcherQueue, 
    ResearchTask, 
    SteeringTaskType, 
    TaskPriority, 
    TaskStatus,
    OracleSteeringQueue,
)

app = typer.Typer(
    name="youtube",
    help="YouTube Researcher — Temporal Knowledge Observatory (9 Layers)",
    no_args_is_help=True,
)


def get_module() -> YouTubeResearchModule:
    """Get initialized YouTubeResearchModule."""
    config = YouTubeResearchConfig.load()
    module = YouTubeResearchModule(config)
    return module


@app.command()
def ingest(
    video_id: str = typer.Argument(..., help="YouTube video ID"),
    transcript: str = typer.Option("", "--transcript", "-t", help="Raw transcript text (or read from stdin)"),
    source_url: Optional[str] = typer.Option(None, "--url", "-u", help="Source URL"),
    chunk_size: Optional[int] = typer.Option(None, "--chunk-size", help="Override chunk size"),
):
    """Ingest transcript through P0 pipeline (Sieve → Sign → Chain → Persist)."""
    if not transcript:
        transcript = typer.prompt("Enter transcript (or pipe via stdin)")
    
    module = get_module()
    
    async def run():
        await module.init()
        result = await module.ingest_transcript(
            video_id=video_id,
            raw_transcript=transcript,
            source_url=source_url,
            chunk_size=chunk_size,
        )
        await module.close()
        
        typer.echo(f"✅ Ingested {video_id}")
        typer.echo(f"   Source ID: {result.source_id}")
        typer.echo(f"   Provenance Hash: {result.provenance_hash}")
        typer.echo(f"   Chunks: {result.chunk_count}")
        typer.echo(f"   Attestation: {result.attestation.provenance_hash[:16]}...")
    
    asyncio.run(run())


@app.command()
def transcribe(
    video_id: str = typer.Argument(..., help="YouTube video ID"),
    audio_path: str = typer.Argument(..., help="Path to audio file"),
    tier: int = typer.Option(2, "--tier", help="Extraction tier (1=API, 2=Whisper, 3=Firecrawl)"),
    lang: str = typer.Option("en", "--lang", help="Language code"),
    checkpoint: bool = typer.Option(True, "--checkpoint/--no-checkpoint", help="Enable somatic checkpoints"),
):
    """L1/L9: Three-tier extraction with TFS and somatic checkpoints."""
    
    async def run():
        transcriber = Transcriber(
            model_size="small",
            device="cpu",
            compute_type="int8",
            cpu_threads=8,
        )
        
        if checkpoint:
            cp = CheckpointingTranscriber(
                transcriber=transcriber,
                checkpoint_path=Path(f"data/youtube_checkpoints/{video_id}.json"),
                save_every=50,
            )
            text, fidelity = await cp.transcribe_with_checkpoint(audio_path, lang=lang)
        else:
            if tier == 1:
                text, fidelity = await transcriber.transcribe_t1(video_id, lang)
            elif tier == 2:
                text, fidelity = await transcriber.transcribe_t2(audio_path, lang)
            else:
                raise NotImplementedError("T3 requires Firecrawl integration")
        
        typer.echo(f"✅ Transcribed {video_id} (Tier {tier})")
        typer.echo(f"   Length: {len(text)} chars")
        typer.echo(f"   TFS: {fidelity.score:.3f}")
        typer.echo(f"   Confidence: {fidelity.confidence_avg:.3f}")
        typer.echo(f"   Has punctuation: {fidelity.has_punctuation}")
        typer.echo(f"   Speaker labeled: {fidelity.speaker_labeled}")
        typer.echo(f"   Technical correct: {fidelity.technical_correct}")
        
        if fidelity.should_escalate():
            typer.echo("   ⚠️  TFS < 0.7 — should escalate to next tier")
        if fidelity.should_quarantine():
            typer.echo("   🚨 TFS < 0.5 — QUARANTINE")
    
    asyncio.run(run())


@app.command()
def chunk(
    video_id: str = typer.Argument(..., help="YouTube video ID"),
    transcript: str = typer.Option("", "--transcript", "-t", help="Transcript text"),
    boundary_model: str = typer.Option("qwen2.5-0.5b", "--model", help="Boundary detection model"),
    cosine_threshold: float = typer.Option(0.7, "--threshold", help="Cosine similarity threshold"),
):
    """L3: Semantic chunking with temporal anchors."""
    
    async def run():
        if not transcript:
            transcript = typer.prompt("Enter transcript")
        
        # Parse into segments (simplified)
        segments = [{"text": transcript, "start": 0.0, "end": 3600.0}]
        
        chunks = await semantic_chunk(
            transcript_segments=segments,
            boundary_model=boundary_model,
            cosine_threshold=cosine_threshold,
        )
        
        # Set video_id on all chunks
        for chunk in chunks:
            chunk.source_video_id = video_id
        
        typer.echo(f"✅ Chunked {video_id} into {len(chunks)} semantic chunks")
        for i, chunk in enumerate(chunks[:5]):
            typer.echo(f"   [{i}] {chunk.t_start:.1f}s-{chunk.t_end:.1f}s: {chunk.text[:80]}... (CAS: {chunk.cas_hash})")
        if len(chunks) > 5:
            typer.echo(f"   ... and {len(chunks) - 5} more")
    
    asyncio.run(run())


@app.command()
def steer(
    prompt: str = typer.Argument(..., help="Natural language steering prompt"),
    node: str = typer.Option("N6", "--node", "-p", help="Target node (N1-N10)"),
    priority: str = typer.Option("normal", "--priority", help="Priority: low/normal/high/critical"),
    task_type: str = typer.Option("youtube_deep_dive", "--type", help="Task type"),
):
    """L8: Inject steering task into Oracle Steering Queue."""
    
    async def run():
        task_priority = TaskPriority[priority.upper()]
        task_type = SteeringTaskType(task_type)
        
        task_id = await inject_steering(
            prompt=prompt,
            node=node,
            priority=task_priority,
            task_type=task_type,
        )
        
        typer.echo(f"✅ Injected steering task: {task_id}")
        typer.echo(f"   Prompt: {prompt}")
        typer.echo(f"   Node: {node}")
        typer.echo(f"   Priority: {priority}")
        typer.echo(f"   Type: {task_type}")
    
    asyncio.run(run())


@app.command()
def status(
    task_id: str = typer.Argument(..., help="Task ID to check"),
):
    """Check steering task status."""
    
    async def run():
        queue = BackgroundResearcherQueue()
        status = await queue.get_status(task_id)
        
        if status:
            typer.echo(f"Task {task_id}: {status.value}")
        else:
            typer.echo(f"Task {task_id}: NOT FOUND")
    
    asyncio.run(run())


@app.command()
def freshness(
    video_id: str = typer.Argument(..., help="YouTube video ID"),
    publish_date: str = typer.Argument(..., help="Publish date (ISO format)"),
    domain: str = typer.Option("ai_research", "--domain", help="Domain for lambda selection"),
    access_count: int = typer.Option(0, "--access", help="Access count for boost"),
):
    """L7: Calculate freshness score with Arc Labs base-2 half-life."""
    
    pub_date = datetime.fromisoformat(publish_date.replace("Z", "+00:00"))
    mem_type = MemoryType[domain.upper()] if domain.upper() in MemoryType.__members__ else MemoryType.FACT
    
    score = freshness_score(pub_date, mem_type, access_count)
    
    typer.echo(f"Freshness for {video_id}:")
    typer.echo(f"  Domain: {domain} (τ={MemoryType[domain.upper()].value if domain.upper() in MemoryType.__members__ else 180} days)")
    typer.echo(f"  Access count: {access_count}")
    typer.echo(f"  Score: {score:.4f}")
    
    if score < 0.1:
        typer.echo("  ⚠️  Below floor (0.1) — may be suppressed from retrieval")


@app.command()
def faithfulness(
    video_id: str = typer.Argument(..., help="YouTube video ID"),
    synthesis: str = typer.Option("", "--synthesis", "-s", help="Synthesis text to verify"),
    threshold: float = typer.Option(0.85, "--threshold", help="Entailment threshold"),
):
    """L6: Faithfulness audit with CalibratedJudge (AutoCal-R)."""
    
    if not synthesis:
        synthesis = typer.prompt("Enter synthesis to verify")
    
    async def run():
        # Load chunks from CAS (simplified)
        chunks = []  # Would load from CAS
        
        result = await verify_provenance(
            synthesis=synthesis,
            chunks=chunks,
            threshold=threshold,
        )
        
        typer.echo(f"Faithfulness audit for {video_id}:")
        typer.echo(f"  Claims: {result.claim_count}")
        typer.echo(f"  Entailed: {result.entailed_count}")
        typer.echo(f"  Entailment ratio: {result.entailment_ratio:.3f}")
        typer.echo(f"  Calibrated score: {result.calibrated_score:.3f}")
        typer.echo(f"  Passed: {'✅' if result.passed else '❌'}")
        
        if result.unentailed_claims:
            typer.echo("  Unentailed claims:")
            for claim in result.unentailed_claims[:5]:
                typer.echo(f"    - {claim[:100]}...")
    
    asyncio.run(run())


@app.command()
def gnosis(
    video_id: str = typer.Argument(..., help="YouTube video ID"),
    transcript: str = typer.Option("", "--transcript", "-t", help="Transcript text"),
    publish_date: Optional[str] = typer.Option(None, "--date", help="Publish date (ISO)"),
):
    """L5: Emit Gnosis Graph edges from video chunks."""
    
    async def run():
        if not transcript:
            transcript = typer.prompt("Enter transcript")
        
        # Chunk first
        segments = [{"text": transcript, "start": 0.0, "end": 3600.0}]
        chunks = await semantic_chunk(segments)
        for chunk in chunks:
            chunk.source_video_id = video_id
        
        pub_date = datetime.fromisoformat(publish_date) if publish_date else None
        edges = emit_gnosis_edges(video_id, chunks, pub_date)
        
        typer.echo(f"✅ Emitted {len(edges)} Gnosis edges for {video_id}")
        for edge in edges[:10]:
            typer.echo(f"  {edge.edge_type.value}: {edge.source_id} → {edge.target_id} ({edge.confidence:.2f})")
            if edge.flagged:
                typer.echo(f"    ⚠️  FLAGGED: {edge.evidence[:80]}...")
        if len(edges) > 10:
            typer.echo(f"  ... and {len(edges) - 10} more")
    
    asyncio.run(run())


@app.command()
def cas_stats():
    """L4: Show CAS storage statistics."""
    
    cas = CASArchiver(Path("data/youtube_cas"))
    stats = cas.get_storage_stats()
    
    typer.echo("CAS Storage Statistics:")
    typer.echo(f"  Unique chunks: {stats['unique_chunks']}")
    typer.echo(f"  Video links: {stats['video_links']}")
    typer.echo(f"  Total size: {stats['total_size_mb']:.2f} MB")
    typer.echo(f"  Dedup ratio: {stats['dedup_ratio']:.2f}x")


if __name__ == "__main__":
    app()