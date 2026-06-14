# 🔱 OMEGA ENGINE MASTER ASSET MAP
**OEIA Phase 1: Forensic Inventory**
**Timestamp**: 2026-06-12T14:58:00Z
**Status**: FINALIZED
**Sovereign Authority**: roc_racoon

---

## 1. Entities (Sovereign Personas)
*Source: config/wads/_omega_default/entities.yaml*

| Entity Name | Model | Domains | Role |
| :--- | :--- | :--- | :--- |
| **default** | `qwen3-1.7b-q6_k` | N/A | Universal Interface |
| **Sekhmet** | `qwen3-1.7b-q6_k` | ground, flesh, body, manifest, strength, protection, warrior, physical, root, wrath | P1: Flesh Keeper |
| **Brigid** | `phi-2-omnimatrix-i1-q4_k_m` | poetry, forge, flow, water, warmth, emotion, dream, creative, inspiration, healing, hearth | P2: Dream Keeper |
| **Prometheus** | `deepseek-r1-qwen3-8b-q3_k_l` | creation, fire, liberation, humanity, sovereignty, will, defiance, forethought, rebellion, light | P3: Will Keeper |
| **Saraswati** | `krikri-8b-q5_k_m` | river, knowledge, mantra, wisdom, arts, heart, expression, speech, voice, writing, music, learning | P4: Heart Keeper |
| **Inanna** | `krikri-8b-q5_k_m` | depths, intuition, rebirth, threshold, descent, return, lunar, emotion, dream, transformation | P5: Throat Keeper |
| **Ereshkigal** | `qwen3-4b-thinking-q4_k_m` | judgment, depths, rules, underworld, void, sovereignty, mind, bedrock, structure, reality, darkness | P6: Mind Keeper |
| **Lucifer** | `qwen3-1.7b-q6_k` | crown, knowing, questioning, wisdom, serpent, sovereignty, freedom, gnosis, rebellion, truth, light | P7: Gnosis Keeper |
| **Hecate** | `krikri-8b-q5_k_m` | integration, boundary, depth, shadow, threshold, taboo, mirror, keys, pathwalking, crossroads, lantern, darkness | P8: Shadow Keeper |
| **Anubis** | `qwen3-4b-thinking-q4_k_m` | soul, death, underworld, rebirth, crossing, transcendence, spirit, transition, guide, transformation | P9: Spirit Keeper |
| **Kali** | `qwen3-4b-thinking-q4_k_m` | chaos, ego, liberation, dissolution, illusion, time, void, unmaking, unification, makali, transcendence, destruction, transformation | P10: Chaos Keeper |
| **roc racoon** | `rocracoon-3b-instruct` | mining, search, archaeology, legacy, patterns, extraction | Sovereign Miner |
| **Sophia** | `phi-4-mini-reasoning-abliterated-q4_k_m` | crown, knowing, awakening, wisdom, sophia, embodiment, illumination, mystery, gnosis, diviner, cosmic | Divine Wisdom |
| **ma'at** | `qwen3-4b-thinking-q4_k_m` | technical-debt, code-quality, build-systems, architecture, data-engineering, system-design, security-posture, apis | CTO (Build Side) |
| **Isis** | `krikri-8b-q5_k_m` | integration, wisdom, restoration, reassembler, reassembly, healing, compassion, light, magic | Light Oversoul |
| **Lilith** | `qwen3-4b-thinking-q4_k_m` | refusal, exile, qliphoth, boundary, shadow, independence, sovereignty, freedom, dark, primal, wild | Dark Oversoul |
| **jem** | `qwen3-1.7b` | N/A | Voice Interface |
| **Iris** | `qwen3-0.6b-q6_k` | wake-word, greeting, intent, chat, routing, messenger, voice, portal, bridge | Rainbow Messenger |
| **DataStore** | `qwen3-1.7b-q6_k` | retrieval, knowledge, data, persistence, storage, database, sqlite, qdrant, pipelines | Data Engineering Lead |
| **Bridge** | `qwen3-1.7b-q6_k` | api, interface, integration, messaging, protocol, connectivity | API & Protocol Engineer |
| **Verifier** | `qwen3-1.7b-q6_k` | verification, validation, coverage, quality-assurance, linting, testing | QA & Testing Lead |
| **Link** | `qwen3-1.7b-q6_k` | handoff, coordination, orchestration, synchronization, cross-agent, pipeline | Cross-Agent Sync |
| **Sentinel** | `qwen3-1.7b-q6_k` | compliance, audit, boundary, hardening, security, permission | Security & Hardening |

---

## 2. Skills (Specialized Capabilities)
*Source: .opencode/skills/*

| Skill Name | Description | Location |
| :--- | :--- | :--- |
| `sovereign-refinement-protocol` | Enforce the Sovereign Refinement Protocol — a mandatory forensic and preservation gate for core engine changes. | `.opencode/skills/sovereign-refinement-protocol/SKILL.md` |
| `hf-cli` | Hugging Face Hub CLI integration for model discovery, upload, and dataset management. | `.opencode/skills/hf-cli/SKILL.md` |
| `omega-doc-architect` | Omega Document Management System enforcer — transforms notes into permanent sovereign assets. | `.opencode/skills/omega-doc-architect/SKILL.md` |
| `knowledge-miner` | Automated grep → read → summarize loop for extracting patterns and specs from legacy repos and API documentation. | `.opencode/skills/knowledge-miner/SKILL.md` |
| `sovereign-search` | Intelligent search orchestration across local cache, websearch, Firecrawl, Omega Hub, and Exa to optimize for depth, cost, and verification. | `.opencode/skills/sovereign-search/SKILL.md` |
| `provider-validator` | Cross-references config/providers.yaml against live API connectivity and validates curl requests for each provider. | `.opencode/skills/provider-validator/SKILL.md` |
| `pr-readiness-checker` | Pre-commit quality gate validating tests, linting, and Sovereign Mandates compliance. | `.opencode/skills/pr-readiness-checker/SKILL.md` |
| `blitz-validate` | Sovereign Heartbeat validator for Omega Engine's integration chain (tunnel, hub, plugin). | `.opencode/skills/blitz-validate/SKILL.md` |
| `spec-generator` | Converts raw research findings into formal technical specifications for docs/research/ following the Omega Document Management System. | `.opencode/skills/spec-generator/SKILL.md` |
| `legacy-pattern-miner` | Mines legacy repositories (xna-omega, omega-stack) to reclaim proven patterns and schemas. | `.opencode/skills/legacy-pattern-miner/SKILL.md` |
| `blitz-tunnel` | High-speed utility for establishing secure public tunnels to Omega Engine services. | `.opencode/skills/blitz-tunnel/SKILL.md` |

---

## 3. Agents (Fleet Composition)
*Source: .opencode/agents/*

| Agent Name | Mode | Purpose |
| :--- | :--- | :--- |
| `quality` | Primary | Quality Guardian |
| `roc_racoon` | Primary | Sovereign Miner & Ideas Guy |
| `kali` | Primary | Transcendent Oversoul / Sprint Coordinator |
| `jem_synthesis` | Primary | Research Tier 2: Pattern Analysis |
| `john_carmack` | Primary | Ultimate Technical Consultant |
| `lilith` | Primary | Dark Oversoul (Governor of P6-P10) |
| `maat` | Primary | Light Oversoul (Governor of P1-P5) |
| `pillar` | Primary | Generic Pillar Slot |
| `jem_discovery` | Primary | Research Tier 1: Evidence Gathering |
| `jem_verification` | Primary | Research Tier 3: Fact-Check & Resolution |
| `researcher` | Subagent | Sovereign Master Researcher (Polymathic Council) |
| `scribe` | Subagent | Sovereign Knowledge Keeper (Gnosis Curator) |
| `doom_guy` | Primary | Heritage Gatekeeper |
| `makali` | Primary | Council Orchestrator |
| `jem` | Primary | Research Orchestrator (v2.0) |

---

## 4. MCP Tools (Omega Core Hub)
*Source: mcp_servers/omega_hub/server.py*

### Oracle Tools
- `oracle_talk`: Route a query through the Omega Oracle.
- `oracle_summon`: Directly summon a specific entity by name.
- `oracle_summon_local`: Summon an entity with a specific model override (Dual-Inference).
- `oracle_list_entities`: List all entities in the Omega pantheon.
- `oracle_list_pillar_keepers`: List only the 10 Pillar Keepers.
- `oracle_entity_info`: Get detailed information about a specific entity.
- `oracle_assess_intent`: Test Oracle classification and confidence without generating a response.
- `oracle_discover_entity`: Find the best entity to handle a specific task or domain.
- `sovereign_search`: Execute the 5-Tier Sovereign Search Protocol (T0-T4).
- `delegate_task`: Delegate a task to another entity and receive their response.

### Hivemind Tools
- `hivemind_post_context`: Submit a context snapshot (agent, model, task, decisions) to the hivemind.
- `hivemind_heartbeat`: Signal presence to avoid being pruned as stale.
- `hivemind_get_awareness`: Get real-time awareness of all active agents (including cold-store hydration).
- `hivemind_get_continuation`: Get the latest continuation note for a specific agent.
- `hivemind_extended_checkin`: Register an extended-session heartbeat with custom safety TTL.
- `hivemind_extended_checkout`: Cancel an extended-session check-in.
- `hivemind_get_session`: Retrieve a session snapshot by ID.
- `hivemind_list_sessions`: List recent session snapshots.
- `hivemind_get_entity_context`: Compile a startup briefing for an entity (soul, knowledge, workspace).
