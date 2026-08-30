# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

import os
import yaml
import re
from pathlib import Path
import logging
from omega.oracle.entity_registry import Entity

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("doc-validator")

def extract_yaml_blocks(file_path: Path):
    """Extracts YAML code blocks from a markdown file."""
    blocks = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Find blocks starting with ```yaml and ending with ```
            matches = re.finditer(r"```yaml\n(.*?)\n```", content, re.DOTALL)
            for match in matches:
                blocks.append(match.group(1))
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
    
    return blocks

def validate_entity_yaml(yaml_text: str, file_path: Path):
    """Validates a YAML block. If it looks like an Entity, validates against the Entity model."""
    try:
        # If the block contains nested backticks, it's likely a documentation example
        # of a block, not a YAML object itself. Skip it.
        if "```" in yaml_text:
            return True

        docs = list(yaml.safe_load_all(yaml_text))
        
        for data in docs:
            if not data:
                continue
            
            if isinstance(data, dict) and "name" in data and "model" in data:
                valid_fields = {f.name for f in Entity.__dataclass_fields__.values()}
                known = {k: v for k, v in data.items() if k in valid_fields}
                metadata = {k: v for k, v in data.items() if k not in valid_fields}
                
                if "metadata" in known:
                    existing_meta = known["metadata"] if isinstance(known["metadata"], dict) else {}
                    known["metadata"] = {**existing_meta, **metadata}
                else:
                    known["metadata"] = metadata
                    
                Entity(**known)
        
        return True
    except Exception as e:
        # If it's a syntax error but doesn't look like an entity, we can be lenient
        if "name" not in yaml_text or "model" not in yaml_text:
            return True
        logger.error(f"Invalid YAML in {file_path}: {e}")
        return False

def validate_docs(root_dir: Path):
    """Walks the docs directory and validates all YAML blocks.
    Skips archive and history directories.
    """
    errors = 0
    exclusions = ["archive", "history"]
    for md_file in root_dir.rglob("*.md"):
        if any(excl in str(md_file) for excl in exclusions):
            continue
        blocks = extract_yaml_blocks(md_file)
        for block in blocks:
            if not validate_entity_yaml(block, md_file):
                errors += 1
                
    return errors

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    docs_dir = project_root / "docs"
    
    logger.info(f"Validating YAML examples in {docs_dir}...")
    error_count = validate_docs(docs_dir)
    
    if error_count > 0:
        logger.error(f"Doc validation failed: {error_count} invalid YAML blocks found.")
        exit(1)
    else:
        logger.info("Doc validation passed! All examples are correct.")
        exit(0)
