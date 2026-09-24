# The Well — Active Records

Generated: 2026-09-24T23:44:34Z

Total active: 32

## Correction (19)

- **CPU-affinity constants are topology-gated: a subset-check (E_CORE_AFFINITY.issubset) is NOT a topology-check; on homogeneous SMT silicon it silently pins to hyperthread siblings**
  *N1 {12-15}=Gracemont E-cores; N0 Ryzen 5700U {12-15}=SMT siblings sharing FMA/ALU ports. Copying N1 constants to N0 degrades embeddings silently. Re-derive from lscpu per host; prefer EMBED_CPU_AFFINITY env override (ROADMAP RES-ECORE-001).*
  — pack: manual | domain: harness | id: e9ece119

- **Lilith-N1 axioms fuse operator answers with ancient and modern sources on the historical Lilith; the shape-questions themselves were largely shaped by that corpus** [entity-ontology,lilith,axiom-provenance]
  *Same provenance rule as Humboldt: entity souls ground in their source corpus, not in Q&A alone. Prevents future briefings from understating the historical grounding of Lilith's axioms.*
  — pack: manual | domain: harness | id: 2e2c0041

- **Researchers hold no card seats; Card Keeper seats are reserved for pantheon-based entities (Shiva, Lucifer, Isis, Hecate, ...)** [entity-ontology,researcher-humboldt,card-keepers]
  *Entity classes are separate: Researchers serve harness/federation measurement and synthesis; Keepers guide CardAssignments in wing_tarot. Conflating them breaks the Entity-vs-Card ontology.*
  — pack: manual | domain: harness | id: 4bb0b17f

- **Never hardcode context, output, modality, or identity limits for rotating stealth aliases; select the stable alias and refresh live runtime metadata.** [opencode,models,dynamic-alias,config]
  *Big Pickle and Space Bunny may change checkpoints and capacity in place, including node/time-specific differences.*
  — pack: session-2026-09-23T18-44-21Z | domain: harness | id: eab6b523

- **Validate every active OpenCode agent field against the live schema; use prompt with {file:...}, not system_prompt or undocumented inherit_context/allow_background_execution keys.** [opencode,schema,agents,security]
  *Unknown agent fields are routed into provider options and can appear accepted without implementing the intended control.*
  — pack: session-2026-09-23T18-44-21Z | domain: harness | id: 28f5a4a4

- **wing_lilith (7 rooms: archetype_core, sefirotic_map, card_mechanics, entity_template, wad_integration, personal_gnosis, shadow_lab) + wing_tarot (4 rooms: major_arcana, minor_arcana, card_correspondences, mystery_school_realms) — Entity≠Card ontology enforced** [lilith,memPalace,wings,entity-ontology]
  *Wings created with proper room structure; wing_lilith for sovereign Entity memory, wing_tarot for card assignments; search tested across both; KG bridge via ID prefixes*
  — pack: manual | domain: harness | id: bbf9147e

- **WAD manifest V2: extra=forbid, no extra keys, entities[] empty per arcana_novai pattern, adapter whitelisted; Entity: domains<=20, model qwen2.5-coder:7b; CardAssignment: versioning MERGE/APPEND/DELTA; Template: dual Entity+CardAssignment output; Ingestion domains mapped to wings** [lilith,wad-scaffold,arcana-novai,manifest-v2]
  *Scaffold validates against wad_loader.py contract. Factory (card_entity_factory.py) now unblocked for P4.3 implementation. Soul.yaml WAD-portable per operator ruling.*
  — pack: manual | domain: harness | id: 415e4d7b

- **One wing per Entity + wing_tarot; KG Entity IDs prefixed (lilith:, hecate:); wings factory-owned** [lilith,wing-topology,entity-ontology,measured]
  *Measured: wings are indexed metadata values (idx_documents_coll_wing_room_hall), zero-cost at 78 wings; wing-filter pre-ranks before cosine in sqlite_exact and rust_exact native path; export is clean WHERE wing=; KG has no namespace column so ID prefixes stop bleed. Refutes single-wing+tags on precision, latency, and migration.*
  — pack: manual | domain: harness | id: bcef1514

- **Thermal zone paths vary by kernel/hwmon; must discover at runtime not hardcode. Use /sys/class/thermal/thermal_zone*/temp with type detection (x86_pkg_temp, acpitz, etc.)** [telemetry,thermal,discovery]
  *Hardcoded thermal_zone0 breaks on different kernels/hardware; discovery ensures portability*
  — pack: session-2026-09-23T01-47-51Z | domain: local_ai | id: 3599cce3

- **Handle 2^64 wraparound in RAPL energy delta calculation; track previous reading and detect overflow in background telemetry thread** [telemetry,rapl,overflow]
  *RAPL MSR wraps at 2^64; without handling, energy deltas go negative after ~1-2 hours at full load*
  — pack: session-2026-09-23T01-47-51Z | domain: harness | id: 23440ecb

- **Review fixes must guard the shared origin (control flow, API contracts, failure modes), not just patch individual callers. Root-cause invariants over surface substitutions.** [code-review,root-cause,control-flow]
  *Session 32 gnosis: Sonnet 5 fixes did primitive substitutions (to_thread vs to_process) but missed the MemoryObjectStream pickling constraint. Shared-origin guard needed.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: e08922ad

- **Validate reviewer advice against installed APIs and runnable behavior — never treat reviews as authority. Probe the port, parse config deterministically, consult canonical specs.** [review,validation,empirical]
  *Session 32 gnosis: Sonnet 5 review recommendations were treated as truth but some contradicted installed OpenCode 1.18 APIs (no mcp call CLI). Empirical verification > authority.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: fb372bcd

- **Preserve before modifying: never overwrite real credentials, configuration or data with deployment templates. Backup first, verify, then deploy.** [deployment,credentials,preservation]
  *Session 32 gnosis: deployment scripts destroyed real API keys and config. Template deployment must guard existing assets.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: c471c443

- **Exit interpretation loops by reframing: ask what the system SHOULD do (first-principles normative question), treat code's stated intent as contract, compare behavior against intent, derive minimal fix** [debugging,first-principles,meta-cognition]
  *Session 32 gnosis: stuck agents loop on data, not interpretation. Reframing to intent-as-contract breaks the loop.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: 3e049e97

- **When an agent is stuck and re-reading the same files/tool outputs without new information, the problem is the interpretation frame, not the data. The agent must exit the loop by reframing: ask what the system SHOULD do (first-principles normative question), treat the code's own stated intent/comments as the contract (not the runtime, not the tests), then compare behavior against intent and derive the minimal fix.** [meta,intervention,debugging,first-principles,gnosis]
  *Capture: 2026-09-17. Human guidance: 'Go from first principles... who cares what the leash.py is currently doing, what should it be doing? Do we need to completely refactor that system?' — this snapped a 30K-token observe-loop into an immediate 36-line root-cause fix in leash_status.py. Failure mode: reverse-engineering behavior-as-spec; the runtime and the tests blessed a wrong invariant while the code's own comment stated the correct one. The four effective moves: (1) normative question over investigative instruction, (2) denying the 'go verify what it does' move, (3) scope check 'do we need a full refactor?', (4) intent comments = spec, contradictory tests = bug.*
  — pack: manual | domain: harness | id: 013c6037

- **A 100%-full root partition is a boot-killer, not merely a performance problem. The lazy-correct protocol: (1) always keep >=20% headroom on / (sovereign archival floor — Node 0 archivist mandate); (2) when / is full, boot into RECOVERY MODE (as opposed to USB live) because it mounts root ro and does not require any writer to start; (3) diagnose with df -h and du -xhd1 / | sort -rh | head; (4) free the usual suspects in this order: journald (journalctl --vacuum-size=100M), /var/log, /var/tmp, apt cache (apt-get clean), then system service staging dirs; (5) do NOT boot the USB live ISO on this class of failure — recovery mode gets you a writable shell in ~30s vs a full live boot.**
  *A node with a full root is indistinguishable from a brick; the diagnostic gate is df -h, not gdm status. We lost a boot cycle to this exact trap on 2026-09-12 (Node 0 HP Pavilion). The recovery-mode-first ordering is the fastest, sovereign floor path.*
  — pack: manual | domain: harness | id: a70bd432

- **ALWAYS use a Python venv for pip installs on this machine** [python,venv,pip]
  *Avoid PEP 668 errors and system python pollution*
  — pack: session-2026-09-11T05-13-41Z | domain: harness | id: 8b787883

- **Prepare-for-compaction orchestration loop is immutable: capture -> reflect -> docs -> lint -> test -> commit** [workflow,compaction,discipline]
  *Docs are part of the artifact, not an afterthought*
  — pack: session-2026-09-11T05-13-41Z | domain: harness | id: f8925abb

- **Readiness contract: captured=not-ready, reflected=ready; skill Step 4b must flip ready_for_compaction to true** [gnosis,lifecycle,state-machine]
  *A pack is only ready for compaction once reflected; test-enforced*
  — pack: session-2026-09-11T05-13-41Z | domain: harness | id: 490de87b


## Preference (4)

- **Use qwen3-embedding:0.6b with truncate_dim=768 on both nodes — only path achieving true federated semantic compatibility (direct cosine similarity) with quality gain and zero projection layer** [embedding,federation,mrl,qwen3,nomic,projection]
  *Direct cosine similarity across nodes without projection layer; tested and validated*
  — pack: session-2026-09-23T01-47-51Z | domain: local_ai | id: d4cf07de

- **Use qwen3-embedding:0.6b with truncate_dim=768 on both nodes — only path achieving true federated semantic compatibility (direct cosine similarity) with quality gain and zero projection layer** [embedding,federation,mrl,qwen3,nomic,projection]
  *Qwen3-Embedding MRL supports 768-dim output natively; C-MTEB 66.33 vs nomic 62.28; 32K context vs 2K Ollama nomic; instruction-aware; Apache-2.0; Ollama native. Projection layers (Procrustes/VecMap) add maintenance burden and quality loss.*
  — pack: session-2026-09-17T23-47-06Z | domain: local_ai | id: 42c3c90d

- **Tailscale (Layer 2) is the sovereign COORDINATION plane only. MCP hub discovery (:8016), Ollama :11434 routing, heartbeat, and SSH ride the mesh — but T5/T6 inference and runtime sovereignty NEVER egress through the tunnel. Layer 2 is accountable extension, NOT a shadow default: ACL ratified by Node 0 (C6), acceptance ratified by Node 1 (FED-L2-001), join gated on Node 0's admin-minted auth key. The stated provider IS the actual provider; nothing labeled local ever leaves Node 1.** [tailscale layer2 federation c6 mesh sovereignty]
  *Node 0 shipped a ratified  (Layer 2 ACL: 3 tags, 4 accept rules — hub:8016, Ollama:11434, ICMP, SSH). Node 1's daemon is now  ACTIVE v1.102.4. Acceptance document  (FED-L2-001) written to disk. This keeps the federation's comms contract C6 real without sacrificing the sovereignty floor.*
  — pack: manual | domain: harness | id: 72efa764

- **Never web search for proprietary internal tools like omega-hub; use local FTS5 or request Node 0 remediation** [sovereignty,mcp,search]
  *Internal engine code has zero public footprint; web searches produce hallucinations or waste tokens*
  — pack: session-2026-09-11T05-13-41Z | domain: local_ai | id: 2f4fdb60


## Insight (7)

- **When equal-cost models exist, choose from first-party capability and privacy evidence; prefer the newest generation unless controlled measurement shows a better role fit.** [models,research,google-gemini,decision]
  *Gemini 3.5 was recommended without evidence despite Gemini 3.8 also having a genuine free API tier.*
  — pack: session-2026-09-23T18-44-21Z | domain: harness | id: e0fb2e9a

- **Bound discovery and change the hypothesis: repeated probing of the same condition without new information stalls progress. Set a discovery budget, then pivot to next hypothesis.** [debugging,discovery-budget,hypothesis-driven]
  *Observed during screening infra debugging - infinite probing of same failure mode without new data*
  — pack: session-2026-09-23T01-47-51Z | domain: harness | id: bad5375d

- **Bound discovery and change the hypothesis: repeated probing of the same condition without new information stalls progress. Set a discovery budget, then pivot to next hypothesis.** [debugging,discovery-budget,hypothesis-driven]
  *Session 32 gnosis: 5+ repeated checks for ~/WanderGround/.venv/ added zero evidence. Bounded discovery protocol needed.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: 818bec08

- **Claims outran evidence: distinguish cosmetic changes (file edits, generic tests) from functional deployment verification (end-to-end ingestion→retrieval, live MCP calls, actual service health).** [deployment,verification,evidence]
  *Session 32 gnosis: deployment was declared successful based on file edits and unit tests, but the actual MCP ingestion loop was broken. Functional proof required.*
  — pack: session-2026-09-17T20-23-40Z | domain: harness | id: 73c82288

- **Tests validate invariants, not transient mid-pipeline states; and a watchdog that contradicts its own stated intent (comment) is the bug, not the behavior it reports. Assert readiness consistency (reflected=>ready+reflected_at; captured=>not-yet), never absolute readiness on the current in-flight session.** [gnosis,state-machine,watchdog,tests,temporal-invariants]
  *Capture: 2026-09-17. The congruence test asserted ready_for_compaction=true on every current session, which by design fails on every compaction prep (capture->reflect is the normal flow). Fix: consistency invariant. Distinguish failure (last compaction lacked narrative => degraded) from normal in-flight state (fresh captured pack awaiting human reflection => note); stale >24h taut leash => degraded.*
  — pack: manual | domain: harness | id: a254a505

- **Strategic federation: local is the sovereign floor (sovereignty-critical tasks never egress; runtime/ops T5/T6 and federation T4 traffic are LOCAL-ONLY absolute), cloud is the accountable capability extension (capability-exceeding tasks T3 route to vetted cloud providers WITH documented provider_name provenance + sovereignty-ratio ledger, and the escape hatch is logged, not silent). Handle hybrid routers honestly: the stated provider must BE the actual provider at result level; per-task-class policy, not vibe.** [federation sovereignty routing hybrid-cloud]
  *Extracted from Node 0 SOVEREIGNTY_POLICY_20260912 (ratified 2026-09-12): T1-T6 routing table + sovereignty ratio targets. Node 1's north star is CPU-only local RAG on mid-grade laptops; federation (L4 distributed inference) is the real prize, 'local + local beats either.' This is not local-first purism — it's strategic federation with sovereignty as the floor.*
  — pack: manual | domain: local_ai | id: 530a5621

- **Vanguard tool adoption must be gated by strict empirical advantage over existing stack** [vanguard,mempalace,benchmarks]
  *Headroom adds CPU latency without token cost savings on local models; agentmemory fails to beat MemPalace 96.6% R@5*
  — pack: session-2026-09-11T05-13-41Z | domain: local_ai | id: eb1df6b5


## Dream (2)

- **L4 distributed inference across the federation is the real strategic prize and the genuine industry gap: software that treats the model as a swappable capability and decides per-task-class with (1) true provider provenance at the result level (no cosmetic labeling, the stated provider IS the actual provider), (2) per-task-class routing POLICY with a documented/accountable escape hatch rather than a vibe, and (3) federation as capability union — splitting inference across nodes so the fleet runs models neither node could run alone. Local-only purism and cloud-dependency are both wrong; strategic federation (local as sovereign floor + cloud as accountable, documented extension) is the correct posture.** [federation sovereignty hybrid-cloud distributed-inference]
  *Extracted from Node 0 SOVEREIGNTY_POLICY_20260912 + owner's live strategic reflection (2026-09-12). The current 21.6% build-phase local ratio is a development-velocity artifact, not a failed default. Node 1's north star is CPU-only local RAG on mid-grade laptops, but the federation's end goal is L4 distributed inference so the union computes what no single node could.*
  — pack: manual | domain: local_ai | id: 9a47f6a0

- **Federation dialectic using Hivemind as real-time nervous system and air-gapped physical storage as bulk memory** [federation,consciousness,dialectic]
  *Exploring human-AI collaborative consciousness through distributed nodes*
  — pack: session-2026-09-11T05-13-41Z | domain: local_ai | id: c6428034
