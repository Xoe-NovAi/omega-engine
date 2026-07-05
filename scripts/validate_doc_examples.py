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
    """Validates a YAML block against the Entity Pydantic model."""
    try:
        data = yaml.safe_load(yaml_text)
        if not data:
            return True
        
        # If it's a list of entities, validate each one
        if isinstance(data, list):
            for item in data:
                Entity(**item)
        elif isinstance(data, dict):
            # If it's a single entity, validate it
            Entity(**data)
        
        return True
    except Exception as e:
        logger.error(f"Invalid Entity YAML in {file_path}: {e}")
        return False

def validate_docs(root_dir: Path):
    """Walks the docs directory and validates all YAML blocks."""
    errors = 0
    for md_file in root_dir.rglob("*.md"):
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
