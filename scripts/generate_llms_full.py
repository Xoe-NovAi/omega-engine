import os
from pathlib import Path
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("llms-full-gen")

def clean_markdown(text: str) -> str:
    """Removes conversational fluff and redundant markers to maximize token efficiency."""
    # Remove common conversational filler phrases
    fillers = [
        r"In this guide, we will look at.*?\.",
        r"Welcome to the .*? documentation\.",
        r"Let's dive in\!",
        r"I hope this helps\!",
        r"Please note that.*?\.",
    ]
    for filler in fillers:
        text = re.sub(filler, "", text, flags=re.IGNORECASE)
    
    # Remove redundant headers (e.g., "Introduction", "Overview")
    text = re.sub(r"^#\s*(Introduction|Overview|Welcome)\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()

def generate_llms_full(root_dir: Path, output_file: Path):
    """Aggregates all relevant documentation into a high-density llms-full.txt."""
    # Define priority order for documents
    priority_files = [
        "OMEGA_ENGINE.md",
        "ORACLE_STACK.md",
        "SOVEREIGN_MANDATES.md",
        "docs/llms.txt",
        "docs/USER_MANUAL.md",
    ]
    
    processed_files = set()
    aggregated_content = []
    
    # 1. Add priority files first
    for rel_path in priority_files:
        full_path = root_dir / rel_path
        if full_path.exists():
            logger.info(f"Processing priority file: {rel_path}")
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                aggregated_content.append(f"--- FILE: {rel_path} ---\n{clean_markdown(content)}\n")
                processed_files.add(full_path)
    
    # 2. Add all other .md files in docs/ recursively
    docs_dir = root_dir / "docs"
    if docs_dir.exists():
        for md_file in sorted(docs_dir.rglob("*.md")):
            if md_file in processed_files:
                continue
            
            # Skip archive files
            if "archive" in str(md_file):
                continue
                
            logger.info(f"Processing doc: {md_file.relative_to(root_dir)}")
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                aggregated_content.append(f"--- FILE: {md_file.relative_to(root_dir)} ---\n{clean_markdown(content)}\n")
                processed_files.add(md_file)
    
    # Write to output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(aggregated_content))
    
    logger.info(f"Successfully generated {output_file} with {len(processed_files)} files.")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "docs" / "llms-full.txt"
    
    generate_llms_full(project_root, output_path)
