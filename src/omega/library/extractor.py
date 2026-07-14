# AP: AP-ORACLE-RESTORE-v2.3.0
"""Content Extraction — Extract content from URLs, PDFs, RSS feeds, and files.

AP: AP-OMEGA-EXTRACTOR-v1.0.0
ICS: [NODE: KNOWLEDGE | ARCHETYPE: HERMES | CONTEXT: CONTENT-EXTRACTOR]

Parses and extracts structured content from multiple source types.
Graceful degradation: if a source fails, returns partial content.
All extraction is local-only — no cloud APIs.
"""
# DocRef: docs/architecture/KNOWLEDGE_LIBRARY.md

import json
import logging
import os
import re
import uuid
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
from omega.library.security import SSRFGuard, validate_path_scope, validate_download_size
from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)

logger = logging.getLogger(__name__)


@dataclass
class ExtractedContent:
    """Structured content extracted from a source."""

    source: str
    source_type: str  # "url", "pdf", "rss", "file", "note"
    title: str
    body: str
    summary: str = ""
    author: Optional[str] = None
    published_date: Optional[str] = None
    domain: Optional[str] = None
    language: str = "en"
    word_count: int = 0
    headings: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "source_type": self.source_type,
            "title": self.title,
            "body": self.body,
            "summary": self.summary,
            "author": self.author,
            "published_date": self.published_date,
            "domain": self.domain,
            "language": self.language,
            "word_count": self.word_count,
            "headings": self.headings,
            "links": self.links[:50],  # cap for storage
            "images": self.images[:20],
            "metadata": self.metadata,
            "extracted_at": self.extracted_at,
            "error": self.error,
        }


class ContentExtractor:
    """Extract content from various source types.

    Uses local tools only:
      - httpx for web pages (with basic HTML parsing)
      - pdfminer.six or PyMuPDF for PDFs
      - feedparser for RSS
      - Plain text extraction for files
    """

    def __init__(self):
        self._httpx: Optional[Any] = None
        self._feedparser: Optional[Any] = None

    async def extract(self, source: str, source_type: str = "url") -> ExtractedContent:
        """Extract content from any source type."""
        extractors = {
            "url": self._extract_url,
            "rss": self._extract_rss,
            "file": self._extract_file,
            "note": self._extract_note,
            "pdf": self._extract_pdf,
            "bookmark": self._extract_bookmark,
        }
        extractor = extractors.get(source_type, self._extract_url)
        try:
            return await extractor(source)
        except OmegaError as e:
            logger.error(f"Extraction OmegaError for {source}: {e}")
            return ExtractedContent(
                source=source,
                source_type=source_type,
                title=f"Extraction failed: {source[:60]}",
                body="",
                error=str(e),
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Extraction unexpected error for {source}: {e}", exc_info=True)
            return ExtractedContent(
                source=source,
                source_type=source_type,
                title=f"Extraction failed: {source[:60]}",
                body="",
                error=str(e),
            )

    async def _extract_url(self, url: str) -> ExtractedContent:
        """Extract content from a web URL.
        
        Security gates (Phase 1 H2-N):
          1. SSRFGuard — blocks internal/private IP ranges [id-soft: vet-033]
          2. DownloadSizeGuard — checks Content-Length before streaming [id-soft: vet-035]
        """
        # ── [id-soft: vet-030] SSRF Gate — O(1) cull of private IP ranges ──
        if not await SSRFGuard.validate(url):
            return ExtractedContent(
                source=url,
                source_type="url",
                title=f"SSRF blocked: {url[:60]}",
                body="",
                error="URL resolves to a private or internal IP range",
            )

        # ── [id-soft: vet-031] Size Gate — fixed-timestep pre-check on download size ──
        if not await validate_download_size(url):
            return ExtractedContent(
                source=url,
                source_type="url",
                title=f"Download blocked: {url[:60]}",
                body="",
                error="Content-Length exceeds maximum download size (50MB)",
            )

        # ── Surgical Path: arXiv PDF Fallback ──
        if "arxiv.org/abs/" in url:
            pdf_url = url.replace("/abs/", "/pdf/")
            # We attempt PDF extraction first for arXiv to get the full paper
            pdf_content = await self._extract_pdf_from_url(pdf_url)
            if pdf_content and pdf_content.body:
                return pdf_content

        if not self._httpx:
            import httpx2 as httpx
            self._httpx = httpx

        async with self._httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "OmegaLibrary/1.0 (research bot; local only)",
            })
            response.raise_for_status()
            html = response.text

        title = self._parse_title(html) or url
        body = self._parse_body(html)
        
        # ── Surgical Path: Project Gutenberg Stripping ──
        if "gutenberg.org" in url:
            body = self._apply_gutenberg_stripping(body)
            
        headings = self._parse_headings(html)
        links = self._parse_links(html, url)

        import urllib.parse
        domain = urllib.parse.urlparse(url).netloc

        content = ExtractedContent(
            source=url,
            source_type="url",
            title=title,
            body=body,
            domain=domain,
            headings=headings,
            links=links,
            word_count=len(body.split()),
            metadata={"status_code": response.status_code, "content_length": len(html)},
        )
        content.summary = self._generate_summary(body)
        return content

    async def _extract_pdf_from_url(self, url: str) -> Optional[ExtractedContent]:
        """Fetch and extract text from a remote PDF URL."""
        try:
            if not self._httpx:
                import httpx2 as httpx
                self._httpx = httpx
            
            async with self._httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Save temporarily to use the existing _extract_pdf logic
                temp_path = Path(tempfile.gettempdir()) / f"omega_pdf_{uuid.uuid4().hex}.pdf"
                async with await anyio.open_file(str(temp_path), "wb") as f:
                    await f.write(response.content)
                
                content = await self._extract_pdf(str(temp_path))
                # Cleanup
                if temp_path.exists():
                    temp_path.unlink()
                return content
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(f"Remote PDF extraction failed for {url}: {e}")
            return None

    def _apply_gutenberg_stripping(self, body: str) -> str:
        """Remove Project Gutenberg boilerplate using boundary markers."""
        start_marker = "*** START OF THIS PROJECT GUTENBERG EBOOK ***"
        end_marker = "*** END OF THIS PROJECT GUTENBERG EBOOK ***"
        
        start_idx = body.find(start_marker)
        if start_idx != -1:
            body = body[start_idx + len(start_marker):]
            
        end_idx = body.find(end_marker)
        if end_idx != -1:
            body = body[:end_idx]
            
        return body.strip()


    async def _extract_rss(self, url: str) -> ExtractedContent:
        """Extract content from an RSS/Atom feed."""
        if not self._feedparser:
            import feedparser
            self._feedparser = feedparser

        import httpx2 as httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            feed = self._feedparser.parse(response.text)

        entries = []
        for entry in feed.entries[:50]:
            entries.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", "")[:500],
            })

        body = "\n\n".join(
            f"## {e['title']}\n{e['summary']}\nSource: {e['link']}"
            for e in entries
        )

        return ExtractedContent(
            source=url,
            source_type="rss",
            title=feed.feed.get("title", url),
            body=body,
            domain=url,
            word_count=len(body.split()),
            metadata={"feed_title": feed.feed.get("title", ""), "entry_count": len(entries), "entries": entries},
        )

    async def _extract_file(self, path: str) -> ExtractedContent:
        """Extract content from a local file.

        Security gate:
          - PathScopeGuard — prevents directory traversal [id-soft: vet-034]
        """
        # ── [id-soft: vet-032] Path Scope Gate — zone boundary enforcement for file paths ──
        from omega.library.library import DATA_DIR as LIBRARY_BASE
        file_path = Path(path)
        if not validate_path_scope(file_path, LIBRARY_BASE):
            return ExtractedContent(
                source=path,
                source_type="file",
                title="Path traversal blocked",
                body="",
                error=f"Path {path} escapes the library data directory",
            )
        if not file_path.exists():
            return ExtractedContent(source=path, source_type="file", title="File not found", body="", error="File not found")

        suffix = file_path.suffix.lower()
        if suffix in (".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".csv", ".html", ".xml"):
            async with await anyio.open_file(str(file_path)) as f:
                body = await f.read()
        elif suffix == ".pdf":
            return await self._extract_pdf(path)
        else:
            body = f"[Binary file: {file_path.name}, size={file_path.stat().st_size} bytes]"

        return ExtractedContent(
            source=path,
            source_type="file",
            title=file_path.name,
            body=body,
            word_count=len(body.split()),
            metadata={"size_bytes": file_path.stat().st_size, "suffix": suffix},
        )

    async def _extract_note(self, text: str) -> ExtractedContent:
        """Treat raw text as content."""
        return ExtractedContent(
            source="inline_note",
            source_type="note",
            title=text[:80],
            body=text,
            word_count=len(text.split()),
        )

    async def _extract_pdf(self, path: str) -> ExtractedContent:
        """Extract text from a PDF file."""
        file_path = Path(path)
        if not file_path.exists():
            return ExtractedContent(source=path, source_type="pdf", title="PDF not found", body="", error="File not found")

        body = f"[PDF: {file_path.name}, size={file_path.stat().st_size} bytes]"
        try:
            import pdfminer.high_level
            body = pdfminer.high_level.extract_text(str(file_path))
        except ImportError:
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(str(file_path))
                body = "\n\n".join(page.get_text() for page in doc)
                doc.close()
            except ImportError:
                logger.warning("No PDF library available (install pdfminer.six or PyMuPDF)")
                body = f"[PDF metadata only: {file_path.name}]"

        return ExtractedContent(
            source=path,
            source_type="pdf",
            title=file_path.stem,
            body=body,
            word_count=len(body.split()),
            metadata={"size_bytes": file_path.stat().st_size},
        )

    async def _extract_bookmark(self, source: str) -> ExtractedContent:
        """Handle a bookmark (URL with bookmark hint)."""
        return await self._extract_url(source)

    def _parse_title(self, html: str) -> Optional[str]:
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        if match:
            return re.sub(r'<[^>]+>', '', match.group(1)).strip()
        return None

    def _parse_body(self, html: str) -> str:
        for tag in ["article", "main", ".content", "#content", ".post", ".entry"]:
            pattern = re.compile(rf'<{tag}[^>]*>(.*?)</{tag}>', re.IGNORECASE | re.DOTALL)
            match = pattern.search(html)
            if match:
                text = re.sub(r'<[^>]+>', ' ', match.group(1))
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 100:
                    return text

        body = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
        body = re.sub(r'<[^>]+>', ' ', body)
        body = re.sub(r'\s+', ' ', body).strip()
        return body[:50000]

    def _parse_headings(self, html: str) -> List[str]:
        headings = []
        for tag in ["h1", "h2", "h3"]:
            for match in re.finditer(rf'<{tag}[^>]*>(.*?)</{tag}>', html, re.IGNORECASE | re.DOTALL):
                text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if text:
                    headings.append(f"{tag}: {text}")
        return headings[:50]

    def _parse_links(self, html: str, base_url: str) -> List[str]:
        links = []
        for match in re.finditer(r'<a[^>]+href=["\'](.*?)["\']', html, re.IGNORECASE):
            url = match.group(1)
            if url.startswith("http") and url not in links:
                links.append(url)
        return links[:100]

    def _generate_summary(self, body: str, max_sentences: int = 3) -> str:
        sentences = re.split(r'(?<=[.!?])\s+', body.strip())
        summary_sentences = []
        for s in sentences:
            if len(s) > 20:
                summary_sentences.append(s)
            if len(summary_sentences) >= max_sentences:
                break
        return " ".join(summary_sentences) if summary_sentences else body[:200]
