#!/usr/bin/env python3
"""
🔱 Omega Engine — Intake Digestor
AP: AP-INTAKE-DIGESTOR-v1.0.0

The Intake Digestor is the second stage of the OIRS pipeline. It extracts raw
text content from files detected by the Intake Sentinel and prepares them
for the Curation Pipeline.
"""

import sys
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Try to import extraction libraries; fallback to stubs if missing
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import docx
except ImportError:
    docx = None

try:
    from pdfminer.high_level import extract_text as pdf_extract
except ImportError:
    pdf_extract = None

# --- Configuration ---
PROCESSED_DIR = Path("data/processed")
REJECTED_DIR = Path("data/rejected")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("IntakeDigestor")

class ContentExtractor:
    """Handles extraction of raw text from various file formats."""
    
    @staticmethod
    def extract_text(filepath: Path) -> Optional[str]:
        ext = filepath.suffix.lower()
        logger.info(f"Extracting content from {filepath.name} ({ext})")
        
        try:
            if ext in {".txt", ".md", ".json", ".yaml", ".yml"}:
                return ContentExtractor._extract_plain(filepath)
            elif ext == ".html":
                return ContentExtractor._extract_html(filepath)
            elif ext == ".pdf":
                return ContentExtractor._extract_pdf(filepath)
            elif ext == ".docx":
                return ContentExtractor._extract_docx(filepath)
            else:
                logger.warning(f"Unsupported file extension: {ext}")
                return None
        except Exception as e:
            logger.error(f"Failed to extract text from {filepath.name}: {e}")
            return None

    @staticmethod
    def _extract_plain(filepath: Path) -> str:
        return filepath.read_text(encoding="utf-8", errors="ignore").strip()

    @staticmethod
    def _extract_html(filepath: Path) -> Optional[str]:
        if BeautifulSoup is None:
            logger.error("BeautifulSoup not installed; cannot extract HTML")
            return None
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator=" ", strip=True)

    @staticmethod
    def _extract_pdf(filepath: Path) -> Optional[str]:
        if pdf_extract is None:
            logger.error("pdfminer.six not installed; cannot extract PDF")
            return None
        return pdf_extract(filepath).strip()

    @staticmethod
    def _extract_docx(filepath: Path) -> Optional[str]:
        if docx is None:
            logger.error("python-docx not installed; cannot extract DOCX")
            return None
        doc = docx.Document(filepath)
        return "\\n".join([para.text for para in doc.paragraphs]).strip()

def calculate_hash(text: str) -> str:
    """Generates a SHA-256 hash of the content for deduplication."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def main(filepath_str: str):
    filepath = Path(filepath_str)
    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        sys.exit(1)

    # 1. Extract Content
    text = ContentExtractor.extract_text(filepath)
    if not text:
        logger.error(f"Extraction failed or returned empty content for {filepath.name}")
        sys.exit(1)

    # 2. Create Digest Metadata
    digest = {
        "source_path": str(filepath),
        "filename": filepath.name,
        "content_hash": calculate_hash(text),
        "extracted_at": datetime.now().isoformat(),
        "raw_text": text,
        "metadata": {
            "size": filepath.stat().st_size,
            "extension": filepath.suffix
        }
    }

    # 3. Save Digest for Curation Pipeline
    # We save a .json digest file in data/processed/ so the Curation Pipeline 
    # doesn't have to re-extract the raw text.
    portal_name = "inbox" # Default
    # In a real scenario, we'd derive the portal from the source path
    # e.g., if "mining_queue" in str(filepath) -> portal_name = "mining_queue"
    
    output_dir = PROCESSED_DIR / portal_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{filepath.stem}.digest.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=2)

    logger.info(f"✅ Successfully digested {filepath.name} -> {output_path}")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python intake_digestor.py <filepath>")
        sys.exit(1)
    
    main(sys.argv[1])
