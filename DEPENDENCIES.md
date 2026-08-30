# 🔱 Omega Engine Dependency Manifest
**Status**: SOVEREIGN-LIST
**Date**: 2026-07-13

This document tracks the external software, libraries, and standards used by the Omega Engine. Unlike the Heritage Registry, this is a manifest of tools, not an attribution of architectural lineage.

---

## 🛠️ Runtime & Infrastructure
- **AnyIO**: Async runtime (Sovereign Mandate M1)
- **FastAPI / Starlette / Uvicorn**: Web framework stack for MCP servers and Iris
- **Typer**: CLI framework for `omega` CLI
- **Pydantic**: Data validation and schema definition
- **httpx**: Async HTTP client for provider API calls
- **redis-py**: Redis async client for hot-memory and coordination
- **qdrant-client**: Vector database for semantic search and Gnosis retrieval
- **llama-cpp-python**: Native GGUF inference backend
- **headroom-ai**: Semantic compression middleware
- **MCP Python SDK**: Model Context Protocol implementation
- **google.genai**: Google AI SDK for Gemini streaming
- **sse-starlette**: SSE transport for MCP hub streaming
- **onnxruntime**: Inference runtime for encoder/embedding models
- **Piper TTS**: ONNX-based speech synthesis
- **Silero VAD**: ONNX-based voice activity detection
- **SentencePiece**: BPE tokenization for ONNX models
- **tokenizers (HF)**: Fast tokenization for embedding models

## 📦 Deployment & OS
- **Podman**: Rootless container runtime (Sovereign Mandate M6)
- **systemd**: Service management and timers
- **Cloudflare WARP**: Privacy infrastructure and proxy pool
- **SearXNG**: Self-hosted metasearch engine
- **Exa.ai**: Neural search API
- **Firecrawl**: Web scraping and deep extraction API

## 📜 Standards & Protocols
- **MCP (Model Context Protocol)**: Tool-calling standard
- **A2A v1.0 (Agent-to-Agent)**: Agent discovery and delegation standard
- **SPIFFE / WIMSE**: Identity format and trust domains
- **OpenTelemetry**: Observability tracing and provenance
- **SSE (Server-Sent Events)**: W3C web standard for streaming
- **SPDX 3.1**: Software Bill of Materials format
- **SQLite FTS5**: Full-text search with BM25
- **RRF (Reciprocal Rank Fusion)**: Hybrid search fusion algorithm

---

**Note**: This list is a manifest of usage. For architectural patterns adopted from these sources, refer to the Heritage Registry in `CREDITS.md`.
