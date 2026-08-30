#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Chunk sprint plan for RAG/vector storage.
Splits markdown into optimal chunks for embedding.
"""

import argparse
import sys
import re
from pathlib import Path
import tiktoken
import json

ENCODING = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))

def chunk_markdown(content: str, max_tokens: int = 2000, overlap: int = 100) -> list:
    """Split markdown into chunks by sections, respecting token limits."""
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    # Split by headings
    sections = re.split(r'(^## .+$)', content, flags=re.MULTILINE)
    
    # Reconstruct with headings
    reconstructed = []
    for i, section in enumerate(sections):
        if i == 0:
            reconstructed.append(section)
        elif i % 2 == 1:  # Heading
            reconstructed.append(section)
        else:  # Content
            reconstructed.append(section)
    
    # Now chunk
    for section in reconstructed:
        section_tokens = count_tokens(section)
        
        if current_tokens + section_tokens > max_tokens and current_chunk:
            # Save current chunk
            chunks.append({
                "content": current_chunk.strip(),
                "tokens": current_tokens
            })
            # Start new with overlap
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + "\n" + section
            current_tokens = count_tokens(current_chunk)
        else:
            current_chunk += "\n" + section
            current_tokens += section_tokens
    
    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),
            "tokens": current_tokens
        })
    
    return chunks

def extract_metadata(chunk: str) -> dict:
    """Extract metadata from chunk (first heading, etc.)."""
    lines = chunk.split('\n')
    heading = ""
    for line in lines:
        if line.startswith('# '):
            heading = line[2:].strip()
            break
        elif line.startswith('## '):
            heading = line[3:].strip()
            break
    
    return {
        "heading": heading,
        "preview": chunk[:200] + "..." if len(chunk) > 200 else chunk
    }

def main():
    parser = argparse.ArgumentParser(description="Chunk sprint plan for RAG")
    parser.add_argument("input_file", help="Markdown file to chunk")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Max tokens per chunk")
    parser.add_argument("--overlap", type=int, default=100, help="Overlap tokens between chunks")
    parser.add_argument("--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    content = Path(args.input_file).read_text()
    chunks = chunk_markdown(content, args.max_tokens, args.overlap)
    
    # Add metadata
    result = {
        "source": args.input_file,
        "total_chunks": len(chunks),
        "total_tokens": sum(c["tokens"] for c in chunks),
        "chunks": []
    }
    
    for i, chunk in enumerate(chunks):
        meta = extract_metadata(chunk["content"])
        result["chunks"].append({
            "id": f"chunk_{i:03d}",
            "tokens": chunk["tokens"],
            "content": chunk["content"],
            "metadata": meta
        })
    
    output = json.dumps(result, indent=2)
    
    if args.output:
        Path(args.output).write_text(output)
        print(f"Wrote {len(chunks)} chunks to {args.output}")
    else:
        print(output)
    
    print(f"Total chunks: {len(chunks)}, Total tokens: {result['total_tokens']}")

if __name__ == "__main__":
    main()