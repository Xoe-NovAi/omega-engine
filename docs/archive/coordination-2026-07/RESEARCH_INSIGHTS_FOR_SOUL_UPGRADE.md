# L1→L2→L3 Insights from Researcher's Deep Research Report
# For potential integration into proposed_lessons.yaml

# Insight 1: Hardware-Specific Optimization Directive
l1_narrative: |
  The Researcher's deep research identified that the Omega Engine currently lacks hardware-specific optimization directives despite running on AMD Ryzen 7 5700U (Zen 2) with specific capabilities like AVX2, FMA3, and potential for ZenDNN/ROCm utilization. Current soul files document hardware_substrate constants but lack directives for actively leveraging hardware-specific acceleration libraries.

l2_insights:
  - "Hardware-specific libraries like ZenDNN (AMD's optimized inference library) and ROCm (Radeon Open Compute) can provide 2-3x inference speedups on AMD APUs"
  - "The Ryzen 7 5700U has Zen 2 architecture with specific cache hierarchies and memory bandwidth characteristics that can be optimized for"
  - "Tensor splitting and n-cpu-moe flags in llama.cpp enable hybrid CPU/offload inference patterns"
  - "Hardware optimization must be measured, not assumed - the 3-month Quake Pentium optimization blitz was driven by profiling data"
  - "Without explicit directives for hardware optimization, the engine may miss significant performance opportunities on target hardware"

l3_universal_principles:
  - "Hardware-aware optimization: Measure hardware capabilities and leverage vendor-specific acceleration libraries when available, validating gains through empirical testing"
  - "Performance optimization must be hardware-specific - generic optimizations may miss architecture-specific opportunities"
  - "The right approximation for performance includes hardware-specific acceleration paths when they provide measurable gains"

sovereignty_impact: |
  Without hardware-specific optimization directives, the Omega Engine may underutilize the target hardware's capabilities, reducing the effectiveness of local-first inference and increasing reliance on cloud fallbacks. With explicit hardware optimization directives, the engine can maximize local performance, strengthening sovereignty by reducing cloud dependency.

confidence: 9/10
heritage_tags: ["[id-soft: quake3-1999] Cvar System — configuration must match hardware capabilities"]

# Insight 2: Admission Control and Resource Governance
l1_narrative: |
  The Researcher's report identified a critical gap in the Omega Engine's provider fabric: lack of admission control mechanisms to prevent resource exhaustion and cascading failures. While the engine has local-first provider ordering and fallback chains, it lacks mechanisms to protect the local GGUF worker from being overwhelmed by concurrent requests or to enforce cost ceilings on cloud provider usage.

l2_insights:
  - "Without admission control, a single runaway request can saturate the local GGUF worker and cascade to cloud providers, violating local-first principles"
  - "Per-provider token budgets, concurrent request limits, and cost ceilings ($/request) are necessary to prevent resource exhaustion"
  - "Observable fallback chains that emit provider_hop metrics enable governance and debugging of provider transitions"
  - "Admission control is not pessimism - it's sovereignty enforcement that enables reliable local-first operation"
  - "Resource governance must happen at the architectural boundary, not as an afterthought in individual providers"

l3_universal_principles:
  - "Resource sovereignty: Implement admission control at the provider fabric boundary to enforce local-first principles and prevent cascading failures"
  - "Governance through measurement: Resource limits must be observable and enforceable, not merely configured"
  - "Local-first is not just provider ordering - it's active resource governance that protects local inference capacity"

sovereignty_impact: |
  Without admission control, the local-first provider ordering (M7) can be violated by resource exhaustion that forces cloud fallback. With admission control, the engine can protect local inference capacity, enforce cost ceilings on cloud usage, and maintain true sovereignty over inference resource allocation.

confidence: 10/10
heritage_tags: ["[id-soft: quake-1996] Zone Memory — pre-checking resource availability", "[id-soft: doom-1993] BSP Culling — skipping broken paths to maintain performance"]

# Insight 3: A2A Agent Capability Discovery
l1_narrative: |
  The Researcher's research revealed that while the Omega Engine has Hivemind coordination and task delegation protocols, it lacks standardized agent capability discovery and negotiation mechanisms (A2A - Agent-to-Agent) that would enable horizontal scaling beyond the current Kali-bottlenecked orchestration model. Current coordination relies on centralized task delegation rather than peer-to-agent capability discovery.

l2_insights:
  - "The current Hivemind handoff protocol creates a central bottleneck at Kali for all agent delegation, limiting horizontal scaling"
  - "Standardized AgentCard schemas with cryptographic verification enable agents to discover each other's capabilities without central coordination"
  - "JSON-RPC 2.0 over MCP provides a standardized protocol for agent-to-agent communication and task negotiation"
  - "Capability negotiation allows agents to adapt protocols and data formats based on mutual compatibility"
  - "Peer-to-peer agent communication reduces central orchestration load and increases system resilience"

l3_universal_principles:
  - "Agent sovereignty: Implement standardized capability discovery (AgentCard) and negotiation protocols to enable peer-to-agent communication without central bottlenecks"
  - "Decentralized coordination: Agent-to-agent communication reduces central orchestration load and increases system resilience"
  - "Capability-based delegation: Agents should discover and negotiate capabilities rather than rely on central assignment"

sovereignty_impact: |
  Without A2A capability discovery, the Omega Engine's fleet coordination remains bottlenecked at Kali, limiting scalability and creating a central point of failure and governance. With A2A protocols, the fleet can scale horizontally while maintaining sovereignty through standardized capability discovery and negotiation.

confidence: 9/10
heritage_tags: ["[id-soft: quake3-1999] Hard-Boundary Struct — each agent is a sealed interface", "[id-soft: doom-1993] WAD System — orchestrator treats clients like swapable entries"]

# Insight 4: Advanced Inference Techniques
l1_narrative: |
  The Researcher's deep research identified several advanced inference techniques that the Omega Engine currently does not leverage, including speculative decoding (Medusa-style), KV cache quantization (FP8/KV8), paged attention (vLLM-style), and context extension techniques (YaRN, LongRoPE). While the engine has substrate volatility absorption concepts, it lacks specific directives for evaluating and integrating these performance-enhancing techniques.

l2_insights:
  - "Speculative decoding (Medusa-style) can provide 2-3x speedup with multiple prediction heads"
  - "KV cache quantization (FP8/KV8) reduces memory footprint for long-context processing with minimal quality loss"
  - "Paged attention (vLLM-style) enables near-zero waste KV cache management for batch processing"
  - "Context extension techniques (YaRN, LongRoPE) dramatically increase context window for reasoning with minimal fine-tuning"
  - "These techniques must be measured on target hardware - what works in benchmarks may not translate to real-world gains on Ryzen 5700U"
  - "The engine should evaluate these techniques as optional backends in the provider fabric, not as mandatory replacements"

l3_universal_principles:
  - "Inference sovereignty: Evaluate and integrate advanced inference techniques based on measured performance gains on target hardware"
  - "Optional acceleration: Advanced techniques should be available as provider fabric options, not mandatory replacements"
  - "Measure before optimizing: Validate performance gains through empirical testing on actual hardware"

sovereignty_impact: |
  Without directives for advanced inference techniques, the Omega Engine may miss opportunities to improve local inference performance and efficiency. With evaluation and integration directives, the engine can selectively adopt techniques that provide measurable gains on target hardware, strengthening local-first capabilities.

confidence: 8/10
heritage_tags: ["[id-soft: quake3-1999] netchan — real-time streaming of state updates", "[id-soft: doom-1993] WAD System — data-driven extension of entity knowledge"]

# Insight 5: Sovereign Deployment and Tooling
l1_narrative: |
  The Researcher's research identified that while the Omega Engine has strong architectural foundations, it lacks standardized deployment profiles and tooling that would enable true sovereign deployment for end-users. Current deployment requires manual configuration and hardware-specific tuning that creates friction for adoption.

l2_insights:
  - "A one-click installer with hardware detection can auto-configure the engine for local hardware (ZenDNN/ROCm availability, memory limits, etc.)"
  - "Deployment profiles should include hardware detection, resource limits, and provider fabric configuration optimized for target hardware"
  - "Session visualization tools and entity marketplace features enhance user sovereignty and entity evolution visibility"
  - "Tooling must preserve local-first principles - installers should default to local-first configuration"
  - "The 'last mile' to sovereign deployment is often the most significant barrier to adoption"

l3_universal_principles:
  - "Deployment sovereignty: Create standardized deployment profiles with hardware detection that preserve local-first principles"
  - "Tooling as sovereignty enabler: Deployment and management tools should reduce friction while enforcing architectural constraints"
  - "Hardware-aware deployment: Installers should detect and optimize for target hardware capabilities"

sovereignty_impact: |
  Without sovereign deployment tooling, the Omega Engine's architectural strengths may be inaccessible to end-users due to configuration complexity. With standardized deployment profiles and tooling, the engine can preserve its architectural integrity while reducing adoption barriers.

confidence: 8/10
heritage_tags: ["[id-soft: doom-1993] WAD System — data-driven extension of entity knowledge", "[id-soft: quake-1996] Right Approximation — optimizing for actual deployment constraints"]

# Insight 6: Agent Evaluation Frameworks
l1_narrative: |
  The Researcher's report identified that while the Omega Engine has some verification concepts (M21 Gate Integrity, API contract verification), it lacks standardized agent evaluation frameworks that would enable objective measurement of capability improvements and prevent regressions through empirical testing. Current verification focuses on code quality and mandate compliance but not on measuring actual agent capability improvements.

l2_insights:
  - "AgentBench and AgentEval provide standardized benchmarks for measuring agent capabilities across different domains"
  - "LLM-as-judge evaluation with calibrated scoring enables scalable evaluation of complex agent behaviors"
  - "Behavioral cloning and imitation learning can accelerate agent skill acquisition through demonstration learning"
  - "Evaluation frameworks must be integrated into the testing suite to prevent regressions in capability, not just code quality"
  - "Objective measurement prevents 'victory disease' where teams believe they're improving without empirical validation"

l3_universal_principles:
  - "Capability sovereignty: Implement standardized agent evaluation frameworks to objectively measure capability improvements and prevent regressions"
  - "Empirical validation: Measure actual agent capabilities, not just code quality or mandate compliance"
  - "Continuous improvement: Evaluation frameworks enable data-driven decisions about agent capability evolution"

sovereignty_impact: |
  Without agent evaluation frameworks, the Omega Engine may improve code quality without improving actual agent capabilities, leading to a gap between architectural sophistication and practical utility. With evaluation frameworks, the engine can make data-driven decisions about capability evolution that strengthen true sovereignty.

confidence: 9/10
heritage_tags: ["[id-soft: quake-1996] Right Approximation — measuring before optimizing", "[id-soft: doom-1993] WAD System — data-driven extension of entity knowledge"]