# Project Knowledge Index — Tech Architecture Research

## Files in This Project (≤12 for direct context)

| # | File | Purpose | Lines |
|---|------|---------|-------|
| 1 | `CLAUDE_PROJECT_SYSTEM_PROMPT.md` | System instructions (pasted into Custom Instructions) | 288 |
| 2 | `CHAT_INITIATION_PROMPT.md` | Starting prompt for each research session | ~60 |
| 3 | `RESEARCH_BRIEF.md` | Full research brief (8 areas, ground truth, constraints) | 478 |
| 4 | `RESEARCH_REPORT.md` | Existing researcher findings (28 sources) | 446 |
| 5 | `UNOVERENGINEERING_PLAN.md` | Current implementation plan with corrections | 305 |
| 6 | `KEY_MANDATES.md` | Sovereign Mandates M1-M25 (excerpt) | ~50 |
| 7 | `GROUNDED_TRUTH.md` | Verified dependency and import state | ~80 |
| 8 | `DECISION_MATRIX_TEMPLATE.md` | Template for final recommendations | ~30 |

## File Update Protocol
1. Delete old file from Project Knowledge
2. Wait for confirmation
3. Upload new version with versioned filename (e.g., `RESEARCH_REPORT-v2.md`)
4. Start a new conversation
5. Clear browser cache before starting

## RAG Threshold
- ≤12 files: direct context (guaranteed)
- 13+ files: RAG mode (retrieval may be partial)
- Current: 8 files (safe)

## Research Evergreen Sources
- PyPI pages for all candidate libraries
- GitHub repos for source code inspection
- Official documentation (modelcontextprotocol.io, ai.google.dev, etc.)
- Community benchmarks (SWE-bench, GPQA, etc.)
