# Session Narrative: onboarding + researcher-humboldt entity + makali-n0 corrections + well entity-ontology

**Timestamp:** 2026-09-24T22:37:15Z  
**Reason:** End of session  
**Host:** XNAi-Asus  
**Agent:** build (channel: cli)  
**Phase:** unset  

---

## Session Summary

**Machine-generated continuity record** (entity build, channel cli, phase unset).
Reason: End of session

Commit: `35ff0438` on `node1/all-5-mcp-green` — 35ff04388ce44069bd0d8f195729df5a5c80b5ac
Delta: 40 files, +1142/-682 lines, 106 new files.

## Key Decisions

- **Decision (operator reflection): most consequential were (2) the entity-class correction + (3) the Well filings.** The operator's ruling — Researchers hold no card seats; Card Keeper seats are pantheon-based — repaired the ontology before it fossilized into the Node 0 package. Filing both corrections into the Well (not docs-only) makes them injectable operating rules.
- **Humboldt chosen over Lovelace** for categorical rigor and polymath span; full candidate list (Sacks, Lovelace, Curie, Feynman, McClintock, Rubin, Librarian, Seldon, Scully, Arroway, Archivist) preserved in MemPalace `wanderground/entity_candidates` for future entities.
- **Future entity vetting: factory schema change.** `entity_class` (Researcher vs Keeper) should be encoded in the WAD manifest schema so the factory enforces the separation structurally. → ROADMAP item filed this session.

## Code Changes

Recent commits:
- `35ff0438 feat(continuity): harden durable state recovery and SQLite adapter`
- `adbcc9fb docs(opencode): lock dynamic free-model foundation`
- `28fd643e docs(federation): add Node 0 intake request for Lilith/Arcana-NovAi materials`
- `9908a9ef feat(wad): scaffold Arcana-NovAi WAD (manifest V2, Entity+Card schema)`
- `ecce1415 chore: pre-compaction complete — gnosis locked, lint 6/6, test 54/54`

Working-tree changes:
-  M .env.ollama.example
-  M .opencode/opencode_node0_hardened.json
-  M .opencode/opencode_node1_hardened.json
-  M Makefile
-  M README.md
-  M docs/AGENT_RUNBOOK.md
-  M docs/ARCHITECTURAL_REVIEW_20260912.md
-  M docs/ARCHITECTURE.md
-  M docs/BENCHMARKS.md
-  M docs/CONTINUITY_KERNEL.md
-  M docs/CPU_PERFORMANCE_TUNING_GUIDE.md
-  M docs/DEVELOPER_GUIDE.md
-  M docs/FEDERATION_DIALECTIC_PLAN.md
-  M docs/FIRST_RUN_EXPERIENCE.md
-  M docs/GETTING_STARTED.md
-  M docs/GNOSIS_USAGE.md
-  M docs/HARDWARE.md
-  M docs/IMPLEMENTATION_MANUAL_HARDENED.md
-  M docs/OPENCODE_FOUNDATION.md
-  M docs/ROADMAP.md
-  M docs/SYSTEM_GUIDE.md
-  M docs/WANDERGROUND_SPEC.md
-  D docs/entities/LILITH_N1_GENESIS_PLAN.md
-  D docs/entities/LILITH_STRATEGY_FINAL.md
-  M docs/federation/NODE0_ACTION_BRIEFING_FAST_DOWNLOAD_LAYER.md
-  M docs/federation/NODE0_INTAKE_REQUEST_LILITH.md
-  M docs/federation/README.md
-  M docs/models/gemma4-12b-qat.md
-  M docs/research/EMBEDDING_MODEL_DECISION.md
-  M docs/research/KNOWLEDGE_GAPS_IMPLEMENTATION_GUIDE.md
-  M gnosis/identity/identity.json
-  M gnosis/well/WISDOM.md
-  M gnosis/well/well.jsonl
-  M scripts/compaction/pre_compaction_ritual.sh
-  M scripts/continuity_sqlite.py
-  M scripts/screening.py
-  M tests/test_continuity_sqlite.py
-  M tests/test_leash_status.py
-  M wads/arcana_novai/entities/lilith/card_assignment_empress.yaml
-  M wads/arcana_novai/entities/lilith/soul.yaml
- ?? ANTIGRAVITY_REVIEW_BRIEFING_LILITH.md
- ?? benchmarking/screening/gemma4-12b-qat_lite_screening.json
- ?? docs/INSTALLATION.md
- ?? docs/PRIVACY_SECURITY.md
- ?? docs/TROUBLESHOOTING.md
- ?? docs/USER_GUIDE.md
- ?? docs/benchmarking/
- ?? docs/entities/lilith/
- ?? docs/federation/MAKALI_N0_SYSTEM_BRIEFING.md
- ?? docs/federation/MAKALI_N0_SYSTEM_BRIEFING_CONSOLIDATED.md
- ?? docs/federation/N1-to-N0_omega-hub-tailscale-remediation.md
- ?? docs/federation/NODE0_USB_HANDOFF_REPORT.md
- ?? docs/federation/makali_n0_onboarding/
- ?? docs/research/Deep-Dive-Hardening-Research-Report.md
- ?? docs/research/ENGINEERING-BRIEF_Integrating-Rust-nom-PyO3.md
- ?? gcca_context.md
- ?? gcca_final_ack.md
- ?? gcca_response.md
- ?? gsca_response_2.md
- ?? models/
- ?? omega-sweeteners/
- ?? package-lock.json
- ?? scripts/check_docs.py
- ?? scripts/continuity_mempalace.py
- ?? scripts/embedding_server.py
- ?? tests/test_continuity_mempalace.py
- ?? tests/test_screening.py
- ?? wads/arcana_novai/entities/researcher_humboldt/


## Blockers & Open Questions

- WAD manifest schema does not yet carry `entity_class` — filed as ROADMAP item, implementation pending.
- Mesh still 0 peers; event bus untested cross-node; embedding migration (384→768-D) unexecuted — all pre-existing gaps, untouched this session.
- Pre-existing uncommitted working-tree changes (40+ files from prior sessions) were NOT committed by this session — only this session's files were staged.

## Next Session Priorities

1. Implement `entity_class` in WAD manifest V2 schema + factory validation (ROADMAP item).
2. Restart OpenCode to load `researcher_humboldt` subagent; run first expedition task.
3. Continue Makali-N0 federation join (mesh peering, first task.request → task.reply).

## Gnosis Gained

- **Pattern (operator reflection): the corpus-grounding rule.** Both entities ground in source corpora, not Q&A alone — Lilith in ancient/modern Lilith sources, Humboldt in Humboldt's corpus. Entity souls must name their corpora.
- **Gnosis (operator reflection): ontology is load-bearing.** The Entity-vs-Card split plus the Researcher-vs-Keeper class separation structure everything downstream — wings, KG namespaces, card seats, factory validation.
- **Lilith provenance lesson (operator verbatim): "To ask the human architect questions before assuming."** The briefing understated Lilith's historical grounding; durable fix is to ask before assuming — encoded in briefing §3 and Well `2e2c0041`.
- Well records filed: `4bb0b17f` (Researchers hold no card seats) + `2e2c0041` (Lilith axioms fuse operator answers with historical corpus). KG `guides` triples for Fool/Star/World invalidated; `entity_class_is → Researcher` triple added.


