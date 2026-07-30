#!/usr/bin/env python3
# 🔱 Omega Engine — Session End Hook (Phase 1: Oracle Pipeline)
# AP Token: AP-SESSION-END-HOOK-v2.1.0
# ⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ session_end ⬡ ACTIVE
#
# Purpose: Soul Distillation (L1→L2→L3) + Codex Refresh on session end.
#          Called by .opencode/wrapper.sh AFTER OpenCode process exits.
#          Guaranteed execution via shell EXIT trap — not plugin events.
#
# Phase 1: Uses Oracle SoulDistillationPipeline with regex-based extraction.
# Phase 2 (planned): Replace regex extraction with local LLM call via
#          Roc's Local Worker Pool for true semantic distillation.
#
# M5 (Gnosis Preservation): Every session MUST produce proposed_lessons.yaml
# M11 (Soul Integrity): L1→L2→L3 → blind staging (NOT soul.yaml)
# M22 (Response Provenance): model_used recorded from OPENCODE_MODEL env
# M23 (Failure Integrity): Hard timeout, never crashes wrapper, logs to stderr
# M1 (AnyIO): Uses anyio, never asyncio directly
#
# Environment (set by wrapper):
#   OPENCODE_ENTITY     — entity name (e.g., "kali", "john_carmack")
#   OPENCODE_SESSION_ID — session ID (e.g., "ses_20260730_kali_001")
#   OPENCODE_MODEL      — model used (e.g., "nemotron-3-ultra-free")

import json
import logging
import os
import subprocess
import sys
import traceback
from pathlib import Path

# Add src to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import anyio

# Logging to stderr (captured by wrapper log)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Paths
CODEX_CAT_PATH = PROJECT_ROOT / "scripts" / "codex_cat.py"
OPENCODE_SESSION_DIR = Path.home() / ".local" / "share" / "opencode"

# Hard timeout for entire distillation (M23 Failure Integrity)
DISTILL_TIMEOUT = 30.0  # seconds
EXPORT_TIMEOUT = 10.0   # seconds for opencode export


async def _export_session_transcript(session_id: str) -> str:
    """Export session transcript via opencode export CLI.
    
    Returns the JSON transcript string, or empty string on failure.
    
    Phase 1: Uses opencode export <session_id>
    Phase 2 (planned): Will also query DB for subagent tree via SQL
    """
    logger.info(f"[Session] Exporting transcript for {session_id}")
    
    try:
        # Build command: opencode export <session_id>
        cmd = ["opencode", "export", session_id]
        
        def _run_export() -> tuple[int, str, str]:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=EXPORT_TIMEOUT,
                env={**os.environ},
            )
            return result.returncode, result.stdout, result.stderr
        
        returncode, stdout, stderr = await anyio.to_thread.run_sync(_run_export)
        
        if returncode == 0 and stdout:
            # Validate it's parseable JSON
            try:
                json.loads(stdout)
                logger.info(f"[Session] Transcript exported successfully ({len(stdout)} bytes)")
                return stdout
            except json.JSONDecodeError as e:
                logger.warning(f"[Session] Export returned invalid JSON: {e}")
                return ""
        else:
            logger.warning(f"[Session] Export failed (exit {returncode}): {stderr[:200]}")
            return ""
            
    except subprocess.TimeoutExpired:
        logger.warning(f"[Session] Export timed out after {EXPORT_TIMEOUT}s")
        return ""
    except Exception as e:
        logger.warning(f"[Session] Export error: {e}")
        return ""


async def _regenerate_codex() -> None:
    """Regenerate OMEGA_CODEX.md via codex_cat.py (non-blocking, timeout)."""
    if not CODEX_CAT_PATH.exists():
        logger.debug("[Codex] Script not found, skipping")
        return
    
    try:
        def _run_codex() -> tuple[int, str, str]:
            result = subprocess.run(
                [sys.executable, str(CODEX_CAT_PATH)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(PROJECT_ROOT),
            )
            return result.returncode, result.stdout, result.stderr

        returncode, stdout, stderr = await anyio.to_thread.run_sync(_run_codex)

        if returncode == 0:
            for line in stdout.strip().split("\n"):
                if "Lines:" in line or "successfully" in line:
                    logger.info(f"[Codex] {line.strip()}")
            logger.info("[Codex] OMEGA_CODEX.md refreshed for next session")
        else:
            logger.warning(f"[Codex] Refresh failed (exit {returncode}): {stderr.strip()}")

    except Exception as e:
        logger.warning(f"[Codex] Refresh error: {e}")


async def _run_oracle_distillation(entity: str, session_id: str, model: str) -> int:
    """Run Oracle SoulDistillationPipeline with exported transcript.
    
    Phase 1: Uses regex-based SoulDistiller (better than Scribe, still not LLM).
    Phase 2: Will use local LLM via Roc's Local Worker Pool.
    
    Returns 0 on success, 1 on timeout/failure.
    """
    try:
        # Step 1: Export transcript from OpenCode DB
        transcript_json = await _export_session_transcript(session_id)
        if not transcript_json:
            logger.warning(f"[Distill] No transcript available for {session_id}, skipping")
            return 0  # Not a failure — no transcript to distill
        
        # Step 2: Import Oracle SoulDistillationPipeline
        from omega.oracle.soul_distiller import (
            SoulDistillationPipeline,
            SoulDistiller,
            SessionClassifier,
            SovereigntyScorer,
        )
        
        # Build pipeline with default components
        classifier = SessionClassifier(min_events=8, novelty_threshold=0.3)
        scorer = SovereigntyScorer(min_pass_threshold=0.6)
        distiller = SoulDistiller(entities_dir=str(PROJECT_ROOT / "data" / "entities"))
        pipeline = SoulDistillationPipeline(
            classifier=classifier,
            scorer=scorer,
            distiller=distiller,
        )
        
        # Step 3: Run pipeline with hard timeout (M23)
        logger.info(f"[Distill] Running Oracle pipeline for {entity} / {session_id}")
        
        async def _run_with_timeout():
            with anyio.fail_after(DISTILL_TIMEOUT):
                result = await pipeline.run(
                    session_transcript=transcript_json,
                    entity_name=entity if entity != "unknown" else "sophia",
                    source_trace_id=session_id,
                )
                return result
        
        try:
            result = await _run_with_timeout()
        except TimeoutError:
            logger.error(f"[Distill] Pipeline timed out after {DISTILL_TIMEOUT}s (M23)")
            return 1
        
        if result:
            logger.info(
                f"[Distill] Pipeline produced L1/L2/L3 for {entity} "
                f"(L1: {result['L1'].content[:60]}...)"
            )
        else:
            logger.info(f"[Distill] Pipeline classified session as routine — no distillation needed")
        
        return 0
        
    except ImportError as e:
        logger.warning(f"[Distill] Oracle pipeline not available: {e}")
        logger.warning("[Distill] Falling back to direct proposed_lessons.yaml write")
        
        # Fallback: write minimal proposed_lessons.yaml placeholder
        return await _write_fallback_proposed_lessons(entity, session_id, model)
        
    except Exception as e:
        logger.error(f"[Distill] Pipeline failed: {e}")
        logger.debug(traceback.format_exc())
        return 1


async def _write_fallback_proposed_lessons(entity: str, session_id: str, model: str) -> int:
    """Write minimal placeholder to proposed_lessons.yaml as fallback.
    
    Used when Oracle pipeline is not available. Ensures M5/M11 compliance
    even if the full pipeline can't load.
    """
    try:
        import yaml
        
        entity_name = entity if entity != "unknown" else "sophia"
        proposed_path = PROJECT_ROOT / "data" / "entities" / entity_name / "proposed_lessons.yaml"
        proposed_path.parent.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime, timezone
        data = {
            "proposals": [],
            "metadata": {
                "entity": entity_name,
                "session_id": session_id,
                "model_used": model,
                "distilled_at": datetime.now(timezone.utc).isoformat(),
                "note": "Fallback: Oracle pipeline not available. Install opencode-sessions-explorer for full distillation.",
                "tier_counts": {"L1": 0, "L2": 0, "L3": 0},
            },
        }
        
        # Atomic write
        tmp_path = proposed_path.with_suffix(".yaml.tmp")
        with open(tmp_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp_path), str(proposed_path))
        
        logger.info(f"[Distill] Fallback proposed_lessons.yaml written for {entity_name}")
        return 0
        
    except Exception as e:
        logger.warning(f"[Distill] Fallback write failed: {e}")
        return 1


async def main() -> int:
    """Main entry point. Returns exit code (0=success, 1=timeout/failure)."""
    # Read environment (set by wrapper)
    entity = os.environ.get("OPENCODE_ENTITY", "unknown")
    session_id = os.environ.get("OPENCODE_SESSION_ID", "unknown")
    model = os.environ.get("OPENCODE_MODEL", "unknown")

    logger.info(f"[Session] Session end hook triggered for {entity} / {session_id} / {model}")

    # Validate required fields
    if entity == "unknown" or session_id == "unknown":
        logger.warning("[Session] Missing entity or session_id, writing fallback")
        await _write_fallback_proposed_lessons("sophia", session_id, model)
        await _regenerate_codex()
        return 0  # Don't fail wrapper

    # Step 1: Soul Distillation via Oracle Pipeline (M5/M11/M22)
    distill_result = await _run_oracle_distillation(entity, session_id, model)

    # Step 2: Codex Refresh (always attempt, never fails wrapper)
    await _regenerate_codex()

    return distill_result


if __name__ == "__main__":
    try:
        exit_code = anyio.run(main)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("[Session] Interrupted by signal")
        sys.exit(130)
    except Exception as e:
        logger.error(f"[Session] Fatal error: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)