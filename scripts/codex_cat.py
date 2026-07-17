#!/usr/bin/env python3
"""
Stack-Cat Protocol Implementation for OMEGA_CODEX.md
Generates the single startup read target for all agents.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class CodexGenerationError(Exception):
    """Base exception for codex generation."""
    pass

class GroupsFileError(CodexGenerationError):
    """Groups file not found or invalid."""
    pass

class FileReadError(CodexGenerationError):
    """Failed to read a source file."""
    pass

class OutputWriteError(CodexGenerationError):
    """Failed to write output file."""
    pass

def generate_codex(root: Path = None, out_file: Path = None) -> None:
    """
    Generate OMEGA_CODEX.md from groups.json.
    
    Args:
        root: Project root directory (defaults to script's parent parent)
        out_file: Output file path (defaults to root/OMEGA_CODEX.md)
        
    Raises:
        GroupsFileError: If groups.json not found or invalid
        FileReadError: If a source file cannot be read
        OutputWriteError: If output file cannot be written
    """
    if root is None:
        root = Path(__file__).parent.parent
    if out_file is None:
        out_file = root / "OMEGA_CODEX.md"
    
    groups_file = root / "scripts" / "groups.json"
    
    try:
        with open(groups_file) as f:
            groups = json.load(f)
    except FileNotFoundError:
        logger.error(f"Groups file not found: {groups_file}")
        raise GroupsFileError(f"Groups file not found: {groups_file}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in groups file: {e}")
        raise GroupsFileError(f"Invalid JSON in groups file: {e}")
        
    ts = datetime.now(timezone.utc).isoformat()
    codex_content = [f"# ⬡ OMEGA ⬡ CODEX ⬡ {ts} ⬡\n\n"]
    codex_content.append("> **Generated via Stack-Cat Protocol**. This is the single startup read target for all agents. It contains the concatenated active state of the engine, mandates, workflow, and refinement protocols.\n\n")
    
    # D-277 / D-281 Phase IV: hydration sequence lives in scripts/hydration_header.md
    header_path = Path(__file__).resolve().parent / "hydration_header.md"
    try:
        header = header_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logger.error(f"Hydration header not found: {header_path}")
        raise FileReadError(f"Hydration header not found: {header_path}") from e
    codex_content.append(header.replace("{{TIMESTAMP}}", ts))
    if not codex_content[-1].endswith("\n"):
        codex_content.append("\n")
    
    for group, files in groups.items():
        codex_content.append(f"## 📁 GROUP: {group.upper()}\n\n")
        for rel_path in files:
            filepath = root / rel_path
            if filepath.exists():
                try:
                    content = filepath.read_text(encoding="utf-8")
                except Exception as e:
                    logger.error(f"Failed to read {filepath}: {e}")
                    raise FileReadError(f"Failed to read {filepath}: {e}") from e
                    
                size = len(content.encode('utf-8'))
                lines = len(content.splitlines())
                header = f"### {rel_path}\n**Type**: markdown\n**Size**: {size} bytes\n**Lines**: {lines}\n\n"
                codex_content.append(header + content + "\n\n---\n\n")
            else:
                logger.warning(f"File not found: {filepath}")
                codex_content.append(f"### {rel_path}\n**Status**: NOT FOUND\n\n---\n\n")
                
    try:
        out_file.write_text("".join(codex_content), encoding="utf-8")
        logger.info(f"Generated {out_file} successfully. Size: {len(''.join(codex_content))} chars.")
    except Exception as e:
        logger.error(f"Failed to write output file {out_file}: {e}")
        raise OutputWriteError(f"Failed to write output file: {e}") from e

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_codex()
