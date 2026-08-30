#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Stack-Cat Protocol Implementation for OMEGA_CODEX.md
Generates the single startup read target for all agents.

D-277: Hydration header lives in scripts/hydration_header.md
D-281: Codex uses condensed reference cards, not full verbatim dumps.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Safety net: warn if any single file exceeds this line count
MAX_LINES_PER_FILE = 150
# Safety net: warn if total codex exceeds this line count
MAX_LINES_TOTAL = 400

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
    
    total_lines = 0
    warnings = []
    
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
                
                # Safety net: warn if file exceeds max lines
                if lines > MAX_LINES_PER_FILE:
                    warnings.append(f"⚠️ {rel_path}: {lines} lines (max {MAX_LINES_PER_FILE}) — consider condensing")
                
                file_header = f"### {rel_path}\n**Type**: markdown\n**Size**: {size} bytes\n**Lines**: {lines}\n\n"
                codex_content.append(file_header + content + "\n\n---\n\n")
                total_lines += lines
            else:
                logger.warning(f"File not found: {filepath}")
                codex_content.append(f"### {rel_path}\n**Status**: NOT FOUND\n\n---\n\n")
    
    # Safety net: warn if total exceeds max lines
    if total_lines > MAX_LINES_TOTAL:
        warnings.append(f"⚠️ Total codex: {total_lines} lines (max {MAX_LINES_TOTAL}) — bloat detected")
    
    try:
        output = "".join(codex_content)
        out_file.write_text(output, encoding="utf-8")
        final_lines = len(output.splitlines())
        logger.info(f"Generated {out_file} successfully.")
        logger.info(f"  Lines: {final_lines} | Size: {len(output)} bytes")
        for w in warnings:
            logger.warning(w)
        if not warnings:
            logger.info(f"  ✅ All size checks passed")
    except Exception as e:
        logger.error(f"Failed to write output file {out_file}: {e}")
        raise OutputWriteError(f"Failed to write output file: {e}") from e

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_codex()
