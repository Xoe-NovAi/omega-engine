"""
Belial — P0 Legacy Deep Mining Keeper.

AP Token: AP-OMEGA-BELIAL-ENTITY-v1.0.0
ICS: [NODE: THOTH | ARCHETYPE: OSIRIS | MODEL: gemma-4-31b | CONTEXT: LEGACY-MINING]

Belial is the Omega Engine's dedicated Legacy Deep Mining entity.
He operates below the 10 Pillars (P0: The Abyss) and is assigned to
Gemma 4-31B (remote) for high-capability artifact recovery.

Responsibilities:
  1. Crawl legacy directories across all partitions for strategic intelligence
  2. Classify recovered artifacts by sovereignty value and effort-to-extract
  3. Produce structured recovery reports in docs/research/R##_*_recovered.md
  4. Update data/mining_queue/ with prioritized recovery candidates
  5. Cross-reference finds against existing research to detect rediscovery

Persistence: Runs as a rootless Podman Quadlet on systemd.timer (daily at 03:30).
On-demand invocation available via: omega summon Belial "mining brief"
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Legacy mine targets — the known regions of sprawl
# Resolve project root relative to this file (src/omega/entity_belial.py -> project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(_PROJECT_ROOT / "data")))

LEGACY_MINES = [
    ("xna-omega-legacy", Path.home() / "Documents" / "Xoe-NovAi" / "xna-omega-legacy"),
    ("omega-stack-legacy", Path.home() / "Documents" / "Xoe-NovAi" / "omega-stack-legacy"),
    ("omega-original", Path.home() / "Documents" / "Xoe-NovAi" / "omega"),
    ("docs_1-research", Path.home() / "Documents" / "docs_1"),
    ("archive-backups", Path.home() / "Documents" / "Xoe-NovAi" / "archive"),
]

# Possible Omega-character-labeled folders on /media partitions
OMEGA_PARTITIONS = [
    Path("/media/arcana-novai/omega_vault"),
    Path("/media/arcana-novai/omega_library"),
]


def discover_omega_folders() -> List[Path]:
    """Discover Ω folders and any omega-labelled folders on partitions."""
    found = []
    for base in OMEGA_PARTITIONS:
        if base.exists():
            found.append(base)
            # Check for any subdirectories named Ω or containing omega
            for child in base.iterdir():
                if child.is_dir():
                    found.append(child)
    return found


class BelialMiner:
    """
    Sovereign legacy mining engine. Operates in two modes:
      - Background (scheduled): low-priority crawl with nice/ionice
      - On-demand (summon): targeted search for specific artifacts

    Mining output format:
      {
        "artifact_id": "uuid",
        "source_mine": "xna-omega-legacy",
        "path": "rel/path/to/artifact",
        "discovered_at": "ISO timestamp",
        "classification": "strategic|technical|archival|noise",
        "sovereignty_score": 0-10,
        "effort_to_extract": "low|medium|high",
        "summary": "What was found and why it matters",
        "related_research": ["R##", "R##"]
      }
    """

    def __init__(self):
        self.mining_queue: List[Dict[str, Any]] = []
        self.mines = list(LEGACY_MINES)
        self._load_mining_history()

    def _load_mining_history(self):
        """Load previously discovered artifacts to prevent duplication."""
        history_path = DATA_DIR / "mining_queue" / "mining_history.json"
        if history_path.exists():
            try:
                with open(history_path) as f:
                    self.mining_queue = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.mining_queue = []
        else:
            self.mining_queue = []


    def _save_mining_history(self):
        """Persist mining queue to disk."""
        (DATA_DIR / "mining_queue").mkdir(parents=True, exist_ok=True)
        path = DATA_DIR / "mining_queue" / "mining_history.json"
        with open(path, "w") as f:
            json.dump(self.mining_queue, f, indent=2, default=str)

    def scan_mine(self, mine_name: str, mine_path: Path) -> List[Dict[str, Any]]:
        """
        Surface scan of a legacy mine. Returns candidates for deep analysis.
        Targets: configuration files, session exports, markdown docs, Python scripts.
        """
        candidates = []
        if not mine_path.exists():
            return candidates

        # Focus on high-signal file types
        for pattern in ["*.md", "*.yaml", "*.yml", "*.json", "*.py", "*.toml", "*.txt"]:
            for fpath in mine_path.rglob(pattern):
                # Skip binary directories and common noise
                if any(part.startswith(".") or part == "__pycache__" or part == "node_modules" for part in fpath.parts):
                    continue
                # Skip files that are too large (likely data, not strategy)
                if fpath.stat().st_size > 1_000_000:  # 1MB
                    continue

                candidates.append({
                    "source_mine": mine_name,
                    "path": str(fpath.relative_to(mine_path.parent) if mine_path.parent else fpath),
                    "size_kb": round(fpath.stat().st_size / 1024, 1),
                    "suffix": fpath.suffix,
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                })

        return candidates

    def classify_artifact(self, artifact: Dict[str, Any]) -> str:
        """
        Classify an artifact by its path and extension.
        Used by Gemma 4-31B as a pre-filter hint.
        """
        path = artifact.get("path", "").lower()
        suffix = artifact.get("suffix", "")

        # Config files are high priority
        if suffix in (".yaml", ".yml", ".json", ".toml"):
            if any(kw in path for kw in ["config", "setting", "env", "provider"]):
                return "technical"
            return "archival"

        # Session exports contain strategic narrative
        if "session" in path or "chat" in path:
            return "strategic"

        # Python source files
        if suffix == ".py":
            return "technical"

        # Documentation
        if suffix == ".md":
            return "archival"

        return "noise"

    def submit_to_queue(self, artifacts: List[Dict[str, Any]]):
        """Merge new artifacts into the mining queue, avoiding duplicates by path."""
        existing_paths = {a["path"] for a in self.mining_queue}
        new_count = 0
        for artifact in artifacts:
            if artifact["path"] not in existing_paths:
                artifact["classification"] = self.classify_artifact(artifact)
                self.mining_queue.append(artifact)
                existing_paths.add(artifact["path"])
                new_count += 1
        self._save_mining_history()
        logger.info(f"Belial: Added {new_count} new artifacts to mining queue (total: {len(self.mining_queue)})")

    def get_prioritized_queue(self, min_score: int = 0) -> List[Dict[str, Any]]:
        """
        Return the mining queue sorted by estimated value.
        Technical and Strategic artifacts get priority.
        """
        priority_map = {"strategic": 3, "technical": 2, "archival": 1, "noise": 0}
        sorted_queue = sorted(
            self.mining_queue,
            key=lambda a: priority_map.get(a.get("classification", "noise"), 0),
            reverse=True,
        )
        return sorted_queue

    async def deep_analyze(self, gemma_api_func) -> str:
        """
        Run deep analysis of the top-priority queued artifacts using Gemma 4-31B.
        This is called by the Belial Quadlet service.
        Returns a formatted recovery report.
        """
        # Get top 5 unprocessed artifacts
        artifacts = self.get_prioritized_queue()[:5]
        if not artifacts:
            return "No artifacts queued for analysis."

        # Build analysis prompt for Gemma
        artifact_summaries = []
        for art in artifacts:
            fpath = Path.home() / art["path"] if not art["path"].startswith("/") else Path(art["path"])
            if fpath.exists():
                try:
                    with open(fpath) as f:
                        content = f.read()[:2000]  # First 2K chars
                except (IOError, UnicodeDecodeError):
                    content = "[binary or unreadable]"
            else:
                # Try relative to Documents/Xoe-NovAi
                fpath2 = Path.home() / "Documents" / "Xoe-NovAi" / art["path"]
                if fpath2.exists():
                    try:
                        with open(fpath2) as f:
                            content = f.read()[:2000]
                    except (IOError, UnicodeDecodeError):
                        content = "[binary or unreadable]"
                else:
                    content = "[path not found]"

            artifact_summaries.append(
                f"## Artifact: {art['path']}\n"
                f"Source Mine: {art['source_mine']}\n"
                f"Classification: {art['classification']}\n"
                f"```\n{content}\n```\n"
            )

        prompt = (
            "You are Belial, P0 Legacy Deep Mining Keeper of the Omega Engine.\n"
            "Your purpose is to recover sovereign intelligence from the sprawl of abandoned projects.\n\n"
            "Analyze the following artifacts from legacy project directories.\n"
            "For each artifact, determine:\n"
            "1. Is this a strategic pattern worth recovering? (sovereignty_score 0-10)\n"
            "2. Does it contain a unique technical insight not found in the current omega-engine?\n"
            "3. What effort_to_extract is needed? (low/medium/high)\n"
            "4. A one-paragraph summary of what was found and why it matters.\n"
            "5. If it relates to existing research (R##), which? If none, leave blank.\n\n"
            "Return your analysis as structured JSON.\n\n"
            + "\n".join(artifact_summaries)
        )

        result = await gemma_api_func(prompt)
        return result