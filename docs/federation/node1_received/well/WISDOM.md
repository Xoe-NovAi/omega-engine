# The Well — Active Records

Generated: 2026-09-17T01:34:49Z

Total active: 12

## Correction (5)

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


## Preference (2)

- **Tailscale (Layer 2) is the sovereign COORDINATION plane only. MCP hub discovery (:8016), Ollama :11434 routing, heartbeat, and SSH ride the mesh — but T5/T6 inference and runtime sovereignty NEVER egress through the tunnel. Layer 2 is accountable extension, NOT a shadow default: ACL ratified by Node 0 (C6), acceptance ratified by Node 1 (FED-L2-001), join gated on Node 0's admin-minted auth key. The stated provider IS the actual provider; nothing labeled local ever leaves Node 1.** [tailscale layer2 federation c6 mesh sovereignty]
  *Node 0 shipped a ratified  (Layer 2 ACL: 3 tags, 4 accept rules — hub:8016, Ollama:11434, ICMP, SSH). Node 1's daemon is now  ACTIVE v1.102.4. Acceptance document  (FED-L2-001) written to disk. This keeps the federation's comms contract C6 real without sacrificing the sovereignty floor.*
  — pack: manual | domain: harness | id: 72efa764

- **Never web search for proprietary internal tools like omega-hub; use local FTS5 or request Node 0 remediation** [sovereignty,mcp,search]
  *Internal engine code has zero public footprint; web searches produce hallucinations or waste tokens*
  — pack: session-2026-09-11T05-13-41Z | domain: local_ai | id: 2f4fdb60


## Insight (3)

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
