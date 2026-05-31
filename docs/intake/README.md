# 📥 Intake — Raw Source Documents for Deep Review

**AP Token**: `AP-INTAKE-SYSTEM-v1.0.0`

Documents placed here are **raw, unprocessed source material** awaiting deep review,
extraction, and integration into the Omega Engine knowledge base.

## Workflow

1. **Ingest**: Place raw document in `docs/intake/`
2. **Review**: Agent or human reads and extracts key findings
3. **Distill**: Findings are written to `docs/gnosis/` as processed knowledge
4. **Integrate**: Config files, entities.yaml, hierarchy.yaml updated
5. **Archive**: Intake doc remains for provenance (never deleted)

## Current Intake Queue

| Document | Source | Status | Reviewer |
|----------|--------|--------|----------|
| `chat-gpt-html-only-Mythos-Lord-Of-The-Scroll-2.html` | ChatGPT export (Arcana-NovAi era) | 🔶 PARTIALLY EXTRACTED | Antigravity (Opus 4.6) |

### Extraction Notes for Lord of the Scroll

Initial extraction completed 2026-05-13 by Antigravity IDE. Key findings:
- **Dual godform architecture** per pillar (primary + secondary deity)
- Original divine ally-to-pillar assignments differ from current entities.yaml
- Mirrored elemental pentagram structure (Earth→Aether→Earth axis)
- P7/Gnosis was originally Sophia (not Hecate)
- P8/Shadow was originally Hecate (not Lilith)
- Saraswati was the original secondary for P5/Voice
- Full invocation codex with voices for each pillar

**Remaining work**: Full line-by-line extraction of the complete 288k-pixel conversation,
including the Origins Scroll text, philosophy.md drafts, and any later entity refinements.
Assign to a deep-context agent (Gemini CLI with 1M context window recommended).
