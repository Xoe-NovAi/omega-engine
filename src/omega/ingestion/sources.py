"""
Sovereign Source Loaders — Loading primary material for ingestion.
"""
from pathlib import Path
from typing import AsyncGenerator, Tuple

class FileSource:
    """Loads text from local files."""
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name

    async def read(self) -> Tuple[str, str]:
        """Returns (source_name, content)."""
        content = Path(self.path).read_text(encoding="utf-8")
        # Strip frontmatter if present
        import re
        content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)
        return self.name, content

async def discover_sources(directory: Path, pattern: str = "**/*.txt") -> AsyncGenerator[FileSource, None]:
    """Discovers files matching a pattern in a directory."""
    for path in directory.glob(pattern):
        yield FileSource(path)
