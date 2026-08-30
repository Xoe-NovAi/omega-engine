<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# N13 Arcana — Mining Brief (T2 Format)

## Mission
Mine the staged corpus seeds for N13 arcana genesis, producing a KB with PD-provenance discipline. Output: KB draft at `data/entities/jem/workspace/N13_ARCANA_KB_20260822.md` (appending to existing G-phase).

## Output Contract
- Source Inventory (P0/P1/P2 with file:line citations)
- Per-Source Digests (measured claims only)
- PD-Provenance Table (standing section: | Source | Edition/Year | PD Basis | Confidence |)
- Gotchas (measured discrepancies)
- Open Questions (for pager ruling)
- L2/L3 Insights (SO-10a format)

## Source Inventory
### P0
1. `config/wads/arcana_novai/` — pantheon.yaml, spheres.yaml, qliphoth.yaml, axioms.yaml, hierarchy.yaml (schema + wad_loader wiring)
2. `data_archive/mnemosyne/` — 13-sphere Kabbalistic corpus (Kether→Malkuth)
3. omega_library tarot intake — "First 5 Cards Grok Chat" (99KB), "Lilith Tarot Deck Design Guide"
4. `src/omega/astrology.py` + `src/omega/meditate.py` (lens registry)
5. Book T c.1890s — PD confirmation (US pre-1929)
6. Tarotoo dataset — external P0, MIT, CI-validated, MCP server

### P1
7. `NODE_GAP_WEB_RESEARCH_JEM_20260822.md` §W4 (structured esoterica sources)
8. `NODE_GAP_LOCAL_DISCOVERY_ROC_20260822.md` §L7 (N13 corpus P0-grade)
9. `N12_CURATOR_KB_20260822.md` (esoteric KB stewardship domain)
10. `N12_DOMAIN_INDEX.md` (hazard register incl. heritage vetting boundary)

### P2
11. Heritage/id-soft vetting docs (doom_guy domain)
12. notebooklm-py/Gemini Notebook monitoring (N12 liaison)
13. yt-dlp anti-blocking playbook (N12)
14. PD esoteric corpora (Project Gutenberg, Sacred Texts Archive, etc.)

## Extraction Questions
1. arcana_novai YAML schema + wad_loader wiring details
2. Mnemosyne 13-sphere mapping to engine memory architecture
3. Tarot structured data format + Lilith Deck design specifications
4. Book T PD basis + edition verification methodology
5. Tarotoo dataset structure + MCP server interface
6. Heritage vetting boundary (doom_guy vs N13)
7. PD-primary sourcing methodology for sovereign correspondence DB

## Constraints
- Read-only except KB + brief paths
- Cite file:line for every claim
- PD-primary sourcing discipline mandatory
- Disk-proof: glob-verify after each write