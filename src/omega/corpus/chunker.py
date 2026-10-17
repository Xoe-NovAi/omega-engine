# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Corpus chunking + text extraction.

Chunks are paragraph-aware with a character budget. 1500 chars with 200
overlap keeps each chunk well inside the Qwen3-Embedding context while
preserving whole thoughts (Qwen3-Embedding mean-pools; mid-sentence cuts
lose the clause). Overlap protects concepts that straddle a boundary.

TOKEN BUDGET (measured 2026-10-16 against the real Qwen3 tokenizer):
the canonical provider runs at n_ctx=512, and 1500 chars of markdown
tokenizes to ~357 tokens — a 43% margin. Code-dense files tokenize
~1.3x worse (~460 tokens), still inside the limit. Raising
CHUNK_CHARS past ~2000 would begin silently truncating the tail, which
would make the indexed text diverge from the stored text. Keep it here.
"""

from __future__ import annotations

import html as _html
import re
from dataclasses import dataclass
from typing import List

CHUNK_CHARS = 1500
CHUNK_OVERLAP = 200
MIN_CHUNK_CHARS = 120

_SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.I | re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t]+")
_MULTINL = re.compile(r"\n{3,}")


def extract_text(raw: str, suffix: str = "") -> str:
    """Strip markup/scripts down to readable prose. Best-effort, never fails."""
    if suffix.lower() in (".html", ".htm", ".xhtml"):
        s = _SCRIPT_STYLE.sub(" ", raw)
        s = _COMMENT.sub(" ", s)
        s = _TAG.sub(" ", s)
        s = _html.unescape(s)
    else:
        s = raw
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = _WS.sub(" ", s)
    s = _MULTINL.sub("\n\n", s)
    return s.strip()


@dataclass
class Chunk:
    """One embeddable unit."""

    ord: int
    text: str


def chunk_document(text: str, chunk_chars: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> List[Chunk]:
    """Split text into overlapping chunks on paragraph boundaries."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= chunk_chars:
        return [Chunk(0, text)]

    # Paragraph split keeps semantic units; whitespace split is the fallback
    # for minified content (logs, single-line blobs).
    paras = text.split("\n\n")
    units: List[str] = []
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if len(p) <= chunk_chars:
            units.append(p)
        else:
            # Hard-wrap long paragraphs on sentence-ish boundaries.
            for piece in _hard_wrap(p, chunk_chars):
                units.append(piece)

    chunks: List[Chunk] = []
    cur = ""
    for u in units:
        if not cur:
            cur = u
        elif len(cur) + 2 + len(u) <= chunk_chars:
            cur = cur + "\n\n" + u
        else:
            chunks.append(Chunk(len(chunks), cur))
            tail = cur[-overlap:] if overlap > 0 else ""
            # Avoid a chunk that starts mid-word on the overlap seam.
            if tail and " " in tail:
                tail = tail[tail.index(" ") + 1 :]
            cur = (tail + "\n\n" + u) if tail else u
    if cur.strip():
        chunks.append(Chunk(len(chunks), cur.strip()))

    return [c for c in chunks if len(c.text) >= MIN_CHUNK_CHARS] or (
        [Chunk(0, text[:chunk_chars])] if text else []
    )


def _hard_wrap(s: str, width: int) -> List[str]:
    """Wrap a long paragraph preferring sentence ends, then whitespace."""
    out: List[str] = []
    cur = ""
    for token in re.split(r"(?<=[.!?;:])\s+", s):
        while len(token) > width:
            cut = token.rfind(" ", 0, width)
            cut = cut if cut > width // 2 else width
            if cur:
                out.append(cur)
                cur = ""
            out.append(token[:cut])
            token = token[cut:].lstrip()
        if len(cur) + len(token) + 1 > width:
            out.append(cur)
            cur = token
        else:
            cur = (cur + " " + token).strip() if cur else token
    if cur:
        out.append(cur)
    return out


def title_from_text(text: str, fallback: str = "") -> str:
    """Derive a human title: first markdown heading, else first non-empty line."""
    for line in text.splitlines()[:40]:
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("#").strip()[:200]
    for line in text.splitlines()[:40]:
        s = line.strip()
        if s:
            return s[:200]
    return fallback
