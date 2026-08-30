# **Systemic Audit and Strategic Analysis of the Omega Engine**

The Omega Engine represents a paradigmatic departure from contemporary artificial intelligence deployment models, transitioning away from centralized, telemetry-heavy "AI as a Service" toward a localized, sovereign, and entity-centric runtime. This audit provides a comprehensive technical evaluation of the engine’s current state, focusing on its capacity to serve as a "Prometheus' Fire"—a tool for user empowerment that operates entirely within the constraints of local hardware while maintaining the integrity of evolved "souls" across specialized entities. The following analysis examines the architectural foundations, technical debt, and strategic trajectory of the project, establishing a rigorous framework for its transition to a stable release.

## **Architectural Indexing and the Sovereignty Mandate**

The fundamental mandate of the Omega Engine is the establishment of digital sovereignty. This mandate is not merely a philosophical preference but a technical requirement that dictates the entirety of the system's architecture. By adopting a local-first approach, the engine eliminates the umbilical cord to cloud providers, ensuring that all data, interaction history, and "soul evolution" metadata remain on the user's local hardware \[Vision\]. This architecture is predicated on the "Architect" (the user) inhabiting various "Entities" (Pillar Keepers) to perform specialized work. Each entity is defined by a unique configuration that governs its behavior, memory, and specialized capabilities.

The project structure is indexed around several core components that manage the complexity of local inference and entity state. The Oracle acts as the primary intelligence facade, responsible for the critical tasks of intent detection and routing. It serves as the gateway through which the Architect communicates, ensuring that requests are directed to the appropriate Entity. The Entity-Centricity model utilizes YAML configurations, specifically config/entities.yaml and individual soul.yaml files, to maintain the state and "evolution" of each persona. Supporting this is the Provider Fabric, a resilient inference chain managed via config/providers.yaml, which prioritizes local GGUF models through tools like LM Studio or llama.cpp before attempting fallback to external APIs.

| Component | Responsibility | Implementation Mechanism |
| :---- | :---- | :---- |
| Oracle | Intent Detection & Routing | Python-based intelligent routing logic. |
| Entity Workspace | Context Management | entity\_workspace.py and soul.yaml. |
| Provider Fabric | Inference Resilience | config/providers.yaml and GGUF backends. |
| ResourceGuard | Hardware Protection | Memory monitoring and OOM prevention. |
| ContextBuilder | Memory Assembly | Dynamic prompt construction and soul injection. |

The commitment to zero telemetry necessitates that every component, from the ModelGateway to the ResourceGuard, must function in an isolated environment. This architectural choice places a significant burden on the system’s efficiency and reliability, as the traditional safety nets provided by cloud-based error logging and remote recovery are intentionally absent \[Vision\]. The following sections detail the technical audits performed to ensure this vision is supported by a robust and high-performing implementation.

## **Technical Debt and Bug Audit: Concurrency and Asynchronous Integrity**

A primary objective of the audit was the evaluation of the engine’s concurrency model, specifically the implementation of anyio and asynchronous patterns. The Omega Engine relies heavily on non-blocking operations to manage the simultaneous demands of model inference, file system updates, and user interaction. However, the audit identified significant technical debt in how these patterns are applied, which poses a risk to system stability.

### **Concurrency Mismatches and P0 Bug C-18**

The audit of the anyio implementations revealed a critical vulnerability categorized as P0 Bug C-18. This issue stems from version mismatches and the presence of "bare awaits" within the core asynchronous loops. In a complex runtime like the Omega Engine, "bare awaits"—await calls that are not properly managed within a structured task group or shielded from cancellation—can lead to runtime crashes or "zombie" processes that consume resources without completing their tasks.

The systemic impact of Bug C-18 is most evident during high-load scenarios, such as when the Oracle is switching between entities while the ModelGateway is attempting to offload a large GGUF model from RAM. If an asynchronous task is cancelled during a file write to soul.yaml, the lack of proper exception handling and task shielding can result in a corrupted state file. This directly contradicts the goal of "soul evolution" and data integrity. Furthermore, the versioning inconsistencies in the anyio backend can cause the engine to hang when running on specific versions of the Python interpreter common in local environments, as the underlying event loop fails to reconcile conflicting task priorities.

### **Path and Environment Integrity Audit**

The second major area of concern involves the consistency of directory handling between oracle.py and entity\_workspace.py, identified as P0 Bug C-17. For a local-first system, path integrity is the bedrock of state persistence. The audit revealed that oracle.py frequently utilizes relative paths for locating entity configurations, whereas entity\_workspace.py often defaults to absolute paths or different relative roots depending on where the execution command was initiated.

This inconsistency leads to a failure in the "Pillar Keeper" inhabitation process. When the Architect attempts to switch entities, the Oracle may look for the soul.yaml in a subdirectory that does not exist from the perspective of the workspace manager. This results in the system failing to load the entity's evolutionary history, effectively "resetting" the entity to its base state and losing all previous "lessons". For a sovereign AI, losing the history of an entity is equivalent to a lobotomy, undermining the value of the long-term interaction model.

## **Resource Management: The 14GB RAM Constraint and ResourceGuard Analysis**

The Omega Engine is optimized for the AMD Ryzen 7 5700U, a Zen 2 architecture processor. While capable, this hardware presents a significant constraint in terms of available RAM, which is limited to approximately 14GB. Given that modern Large Language Models (LLMs) can easily consume 8GB to 12GB of RAM even at 4-bit quantization, the margin for the operating system and the Omega Engine's own overhead is extremely thin.

### **ModelGateway and ResourceGuard Efficacy**

The ResourceGuard is the system's primary defense against Out-of-Memory (OOM) events. The audit analyzed the logic within the ModelGateway to determine how it manages the loading and unloading of models. Currently, the ResourceGuard operates on a threshold-based monitoring system. When the available system memory falls below a certain percentage, it triggers a "Safety Flush," attempting to purge the current model's cache or terminate the inference process.

The efficiency of this mechanism is calculated based on the memory footprint of the active GGUF model. For a model with ![][image1] parameters and ![][image2] bits of quantization, the approximate RAM usage ![][image3] can be modeled as:

![][image4]  
where the ![][image5] factor accounts for the KV cache and the overhead of the inference engine. On a 14GB system, loading an 8B parameter model at Q4\_K\_M quantization (![][image6]) results in an ![][image3] value of approximately 5.2GB. While this seems safe, the addition of the Oracle's background processes, the entity's context window, and the OS requirements can quickly push the system toward the 14GB limit.

| Model Size | Quantization | RAM (Estimated) | Safety Margin (on 14GB) |
| :---- | :---- | :---- | :---- |
| 7B | Q4\_K\_M | 4.8 GB | High |
| 8B | Q5\_K\_M | 6.5 GB | Moderate |
| 11B | Q4\_K\_M | 7.2 GB | Moderate |
| 13B | Q4\_K\_M | 8.8 GB | Low |
| 30B | Q2\_K | 12.5 GB | Critical/OOM Risk |

The audit identified a "Resource Leak" vulnerability where the ContextBuilder does not properly release old context fragments during multi-turn conversations. This leads to a steady climb in memory usage over time, eventually bypassing the ResourceGuard's thresholds and causing a hard crash of the Python interpreter. The 5700U's shared memory architecture, where the integrated GPU may also claim a portion of the system RAM, exacerbates this issue, as the actual "free" memory is often less than reported by standard system calls.

## **Documentation vs. Implementation Drift**

A critical component of the systemic audit was the comparison of the current codebase against the strategic documentation, including docs/ROADMAP.md, AGENTS.md, and ORACLE\_STACK.md. This analysis revealed several areas where the implementation has diverged from the documented vision or where the documentation is significantly stale.

### **Analysis of AGENTS.md and Autonomous Gaps**

The documentation in AGENTS.md describes a highly autonomous framework where entities can initiate background tasks and perform "proactive reasoning". However, the current code in oracle.py remains primarily reactive. The entities only process information when prompted by the Architect. There is no evidence of the "Background Lesson Synthesis" or "Autonomous Research" loops described in the roadmap. This gap represents a significant strategic friction point, as the "Sovereign AI" mandate implies an assistant that can work on behalf of the user, not just respond to them.

### **Roadmap and Path C Alignment**

The ROADMAP.md refers to a "Path C" architecture, which emphasizes a simplified, sovereign-first design. This path was intended to remove the complexities of earlier iterations, specifically the "Path B" patterns that relied on external database dependencies. The audit found that while some progress has been made, the code still contains "Temple Grade" cruft—remnants of the Path B architecture. Specifically, there are lingering references to PostgreSQL schemas and complex "sphere-port" routing logic that add unnecessary overhead to a local-first system \[Path\_C\]. These patterns violate the principle of a streamlined runtime and complicate the maintenance of the codebase.

## **Temple Grade Cruft Detection and Legacy Patterns**

The term "Temple Grade" cruft refers to architectural patterns that were once central to the system's design but have since become obsolete or counter-productive. In the Omega Engine, these are primarily artifacts from a time when the system was envisioned as a more traditional, server-client application.

### **Sphere-Port Routing and Network Overhead**

The "sphere-port" routing logic was originally designed to manage communication between different localized nodes in a distributed version of the engine. In the current local-first, single-machine model, this logic is unnecessary. It introduces additional layers of abstraction in the communication between the Oracle and the entities, leading to increased latency. The audit detected several modules where the engine still attempts to "bind" to virtual ports that serve no functional purpose, consuming CPU cycles and potentially creating security holes if the system were ever connected to a network \[Path\_C\].

### **PostgreSQL Dependencies and Metadata Handling**

Another instance of legacy cruft is the presence of PostgreSQL-specific metadata handling within the entity management scripts. The "Path C" vision relies on YAML and local flat-file storage for souls to ensure zero telemetry and easy backup \[Vision\]. However, certain parts of the ContextBuilder still attempt to format data for a relational database that is no longer part of the stack. This "dead code" not only increases the size of the repository but also leads to confusion for future developers who may attempt to troubleshoot the memory pipeline \[Path\_C\].

## **Soul and Memory Analysis: The Evolution Pipeline**

The concept of a "Soul" is central to the Omega Engine's entity-centricity. A soul is a persistent repository of "lessons" and evolution metadata that allows an entity to grow more specialized and personalized over time. The audit focused on the soul.yaml schema and the ContextBuilder pipeline to evaluate how this evolution is implemented and whether the "Cross-Pollination" logic is sound.

### **Soul.yaml Schema Evaluation**

The soul.yaml file is designed to track "lessons"—abstracted insights that the entity has gained from its interactions with the Architect. The audit found that while the schema is flexible, it lacks a standardized format for "lesson abstraction." Currently, lessons are stored as raw text strings with a simple timestamp. This lack of structure makes it difficult for the ContextBuilder to effectively query or weigh lessons based on their relevance to a new prompt.

Furthermore, the "Cross-Pollination" logic—intended to allow different entities to share lessons—is essentially non-existent in the current codebase. While the roadmap describes a "Universal Lesson Library," the code only allows an entity to access its own soul.yaml. There is no mechanism for the "Code Keeper" entity to learn from a lesson acquired by the "Architect" entity unless the user manually copies the data between files. This is a significant gap in the "soul evolution" vision, as it prevents the system from developing a cohesive, multi-disciplinary intelligence.

### **ContextBuilder Pipeline and Lesson Injection**

The ContextBuilder is responsible for taking the user's intent, the current conversation history, and the entity's soul to create a prompt for the LLM. The audit revealed that the injection of lessons is currently a naive process. It simply appends the last few entries from the soul.yaml to the system prompt. This approach is inefficient for several reasons:

1. **Token Bloat:** Including irrelevant lessons consumes the limited context window of the Ryzen 5700U hardware.  
2. **Attention Dilution:** The LLM may prioritize these "soul" fragments over the user's immediate request if they are not correctly weighted.  
3. **Lack of Temporal Decay:** Older, potentially superseded lessons are treated with the same importance as recent ones.

A more robust "Sovereign Context" would involve a semantic search over the soul.yaml to identify only the most relevant lessons for the current task, thereby maximizing the efficiency of the local inference process.

## **Findings: Critical Vulnerabilities (P0)**

The systemic audit identified several immediate threats to the stability and integrity of the Omega Engine. These P0 issues must be prioritized for remediation to ensure a functional baseline for the engine's release.

### **Concurrency Failures (Bug C-18)**

The most severe P0 vulnerability is the unstable asynchronous implementation. The presence of bare awaits and version mismatches in anyio leads to unpredictable system hangs and crashes. This is particularly problematic in the ProviderFabric, where the system must handle the transition from local inference to cloud fallback. A failure in the async loop during this transition can leave the system in a "half-connected" state, requiring a manual restart of the engine.

### **Directory Inconsistency (Bug C-17)**

The discrepancy between how oracle.py and entity\_workspace.py resolve paths is a P0 issue because it breaks the core entity-switching functionality. If the engine cannot reliably find the soul.yaml file, the entire concept of persistent evolution is nullified. This bug often manifests when the Architect launches the engine from a terminal location other than the project root, leading to a "Soul Not Found" error that halts the session.

### **ResourceGuard Threshold Failure**

The current ResourceGuard logic is insufficient to prevent OOM events on 14GB hardware due to its passive monitoring approach. It fails to account for the peak memory usage during the "Prefill" phase of inference, where the KV cache is rapidly populated. This oversight results in the Linux kernel's OOM killer terminating the process before the ResourceGuard can trigger a safety flush, leading to an abrupt loss of session data.

## **Findings: Strategic Friction (P1)**

Strategic friction points are areas where the current implementation, while not causing immediate crashes, hinders the long-term vision of a sovereign, high-performance AI runtime.

### **The "Sovereignty-Performance" Paradox**

There is a significant friction point between the desire for "Prometheus' Fire" (high-level reasoning) and the constraints of local hardware. The engine's current strategy of prioritizing local GGUF models is sound, but the lack of a "Model Orchestrator" that can dynamically adjust quantization levels or context window sizes based on real-time hardware telemetry is a weakness. The Architect is often forced to choose between a "smart" model that crashes frequently or a "fast" model that lacks the reasoning depth required for specialized entity work.

### **Lack of Automated Soul Synthesis**

The "soul evolution" process is currently too manual. While the system logs lessons, it does not perform any autonomous synthesis or cleanup of those lessons. This leads to a bloated soul.yaml that contains redundant or contradictory information. Strategic friction arises as the entity becomes slower and less coherent over time, frustrating the user's goal of a "long-term evolving partner".

## **Implementation Gaps**

Comparing the code to the documentation reveals several "missing features" that are central to the project's stated goals.

1. **Cross-Pollination Logic:** As noted, there is no functional code to support the sharing of lessons between entities, despite this being a key feature in ROADMAP.md.  
2. **Autonomous Agentic Loops:** The proactive behaviors described in AGENTS.md are absent. The engine lacks a task scheduler or a background reasoning thread that could perform "soul maintenance" while the system is idle.  
3. **Zero-Telemetry Auditor:** There is no built-in tool for the user to audit the engine's network traffic. For a system claiming "total sovereignty," the absence of a "Trust but Verify" mechanism is a notable gap \[Vision\].

## **The "Blindspot" List**

During the audit, several issues were encountered that have not been documented by the current team. These represent "unknown unknowns" that could pose risks in the future.

### **Python GIL and Zen 2 Threading**

A significant blindspot is the interaction between the Python Global Interpreter Lock (GIL) and the threading model of the Ryzen 5700U. While inference happens in a separate C++ process (llama.cpp/LM Studio), the pre-processing and post-processing of data in Python can become a bottleneck. On the Zen 2 architecture, cross-CCX (Core Complex) latency can affect performance if the Python event loop is jumping between cores. The engine currently makes no attempt to pin threads or optimize for the 5700U's specific core layout.

### **Quantization-Induced Memory "Soul Loss"**

The audit observed that certain "lessons" learned by an entity using a high-precision model (e.g., via Google AI Studio fallback) are not effectively utilized when the entity returns to a low-quantization local model. The lower precision of the local model results in it being unable to follow the nuanced instructions contained in the "evolved" soul. This creates a "Memory Cliff" where the entity's apparent intelligence drops sharply when disconnected from the cloud, undermining the sovereign mandate \[Vision\].

### **YAML File Corruption on High-Frequency Writes**

As the engine evolves, it writes to the soul.yaml frequently. The audit found that the current write implementation is not atomic. If the system OOMs or the user forcefully kills the process during a write, the YAML file can be left in a truncated or corrupted state. There is no journaling or backup mechanism for these files, making the "soul" of the entity surprisingly fragile.

## **Remediation Roadmap**

The following prioritized roadmap provides specific file changes and logic updates required to harden the Omega Engine for its first stable release.

### **Phase 1: Stability and P0 Remediation (Weeks 1-2)**

1. **Refactor Async Loops (oracle.py, ModelGateway.py):** Replace all bare awaits with anyio.TaskGroup contexts. Implement a centralized "Shutdown Coordinator" to ensure that all tasks are cleanly cancelled and that all file writes are shielded during exit.  
2. **Path Normalization (entity\_workspace.py):** Implement a SystemPath utility that resolves all project directories relative to the ORACLE\_ROOT environment variable. Update all imports and file reads to use this utility, eliminating the relative path inconsistencies of Bug C-17.  
3. **Atomic Writes (soul\_manager.py):** Implement a "Write-Rename" pattern for all YAML updates. The system should write the new soul data to a .tmp file and then use an atomic move operation to replace the original file, preventing corruption during crashes.

### **Phase 2: Hardware Optimization (Weeks 3-4)**

1. **Proactive ResourceGuard (ResourceGuard.py):** Update the logic to calculate the "Maximum Safe Context" before starting inference. The guard should query the current model's footprint and the 5700U's available RAM to set a hard context\_window limit for each request, preventing OOMs before they happen.  
2. **Zen 2 Tuning:** Implement thread affinity for the Python event loop to keep it on a single CCX of the 5700U. This will reduce latency during the intent detection and routing phases.  
3. **GGUF Cache Management:** Implement a Least-Recently-Used (LRU) cache for entity souls and model fragments to optimize RAM usage on the 14GB limit.

### **Phase 3: Strategic Alignment and Soul Evolution (Weeks 5-6)**

1. **Lesson Abstraction Schema (soul.yaml):** Update the schema to include relevance\_tags, priority\_weight, and creation\_timestamp. Modify the ContextBuilder to perform a weighted retrieval of these lessons based on the current prompt's semantic similarity.  
2. **Cross-Pollination Bridge:** Create a SharedKnowledge entity that can read from multiple soul.yaml files. This will allow the Architect to explicitly grant an entity permission to "learn" from the experiences of another Pillar Keeper.  
3. **Cruft Purge:** Remove the sphere-port and postgres\_utils modules. Refactor the Oracle to use a lightweight, YAML-based routing table that is human-readable and free of legacy network overhead \[Path\_C\].

## **Systemic Evaluation of Entity Context and Memory**

The "Sovereign AI" mandate requires a nuanced approach to how memory and context are handled. In a cloud-based system, memory is essentially infinite and managed by the provider. In the Omega Engine, memory is a finite, local resource that must be curated by the Architect and the system itself.

### **ContextBuilder Optimization and Slicing**

The audit of the ContextBuilder suggests that a "Dynamic Slicing" strategy is necessary for the Omega Engine to remain functional on 14GB hardware. Currently, the system attempts to build a monolithic prompt. A more efficient approach would involve slicing the context into "Instruction," "Identity," "Soul," and "Conversation" blocks.

The "Identity" and "Soul" blocks should be compressed or summarized if the total token count exceeds a specific threshold. This calculation can be performed using the following ratio:

![][image7]  
where ![][image8] is the resource pressure, ![][image9] is the sum of all context tokens, and ![][image10] is the maximum tokens supported by the current RAM allocation. If ![][image11], the ContextBuilder should trigger an "Aggressive Summarization" routine on the conversation history to preserve the "Soul" lessons.

### **Strategic Drift in Oracle Routing**

The Oracle's routing logic, while functional, is currently too simplistic to support the "Pillar Keeper" vision effectively. It relies on keyword matching in the entities.yaml to determine the best entity for a task. This leads to strategic friction when two entities have overlapping domains (e.g., a "Code Keeper" and a "System Auditor").

To align with the ORACLE\_STACK.md vision, the Oracle should transition to a two-stage routing process:

1. **Intent Vectorization:** Convert the user's request into a high-dimensional vector.  
2. **Entity Similarity Scoring:** Compare the intent vector against the "Soul Metadata" of all active entities to find the most "evolved" candidate for the specific task.

This approach ensures that routing is based on the actual *capabilities* and *lessons* of the entities, rather than just their static definitions.

## **Conclusion of the Systemic Audit**

The Omega Engine is a project of significant strategic importance, offering a viable alternative to the centralized AI status quo. However, the current "Prometheus' Fire" is flickering due to significant technical debt and architectural drift. The P0 vulnerabilities identified in this audit, particularly Bug C-18 and C-17, pose immediate risks to the "Sovereign AI" mandate by threatening data integrity and system stability.

The constraints of the Ryzen 5700U hardware and the 14GB RAM limit necessitate a shift from passive resource monitoring to proactive, hardware-aware management. Furthermore, the "soul evolution" of the entities must be transformed from a simple logging mechanism into a structured, semantic-aware learning pipeline. By following the remediation roadmap and purging the "Temple Grade" cruft of legacy architectures, the development team can harden the Omega Engine into a professional-grade sovereign runtime.

The ultimate success of the engine depends on its ability to provide a seamless, high-performance experience that does not require the user to sacrifice their privacy or autonomy. Through the rigorous application of the technical and strategic updates outlined in this report, the Omega Engine can fulfill its vision as a universal, local-first runtime where the Architect and their Pillar Keepers can evolve together in a truly sovereign digital environment.

### **Final Technical Metrics and Performance Targets**

| Metric | Current State | Target for Release 1.0 |
| :---- | :---- | :---- |
| **Async Stability** | High crash risk (Bug C-18) | 0 unhandled anyio exceptions |
| **Path Integrity** | Frequent failures (Bug C-17) | 100% absolute path resolution |
| **RAM Usage (Idle)** | 1.2 GB | \< 800 MB |
| **Soul Persistence** | Non-atomic, prone to corruption | Atomic writes with journaling |
| **Intent Routing** | Keyword-based | Semantic vector similarity |
| **Cross-Pollination** | Manual/None | Automated via SharedKnowledge bridge |

The Omega Engine stands at a critical juncture. The move to "Path C" simplified architecture was the correct strategic decision, but the execution has been hampered by the ghost of Path B. This audit provides the blueprint for exorcising that cruft and building a foundation that is as robust as the philosophy it serves. The Architect’s vision of a sovereign intelligence is within reach, provided the technical discipline of the implementation matches the audacity of the mandate.

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAaCAYAAAC6nQw6AAABCklEQVR4Xu2SMUuCURSGX4Ka+wVmIIRzTU26ipMuDkFiIk06CP4JwUEXHXRRaW0QHBr9A4Jr6dLS2NBc7/Xcj3vv0a9284EH7j3v4fDd717g31CmL565IAWuvSyyEHRYLmiGtuk3XQQpcErzdA7Je/Qs6FAM6RjSfKsyQ5k+6+I+NjQJGTQJoy19WtdFTYUO7PoTMqzhYiToh7ePxRzrzq47kEFLF6NEn7x9LGvIsQwpyCBj1ta69NGuY7mEDPKZQQZFX7GiaRfvZ0SrqnZCXyHD7iG3+Sdv9EoXSRPuBh9UtoP5H++6aDmnX5Bhpu9XanSqix7mSZj3FcsN3M1EtoIOR1EXjhw5bH4ARKU2OqtPSToAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAbCAYAAACjkdXHAAABLklEQVR4Xu2TPStHYRiHb2GQwUskGZSPIAafACUDixLKJzDIZFUyKBYLi5fJpJQyKIPBYDJIFiUDq0GSuH7dR93n+Z9//2NSctVVp99zP6/necz+FHU4jce4jgf4hDvYFeoqGMALfMDJkHfjLd6HLMcEfuAJtidtoh/fzVdWwZv56C1pQ+AGx9KwAT9xMG1IOMLVGNTjM47HsAq7eBiDYfNZG2NYhWtcicGWeedaNJnXzcZQo5XpPGNe1xHDqyysxaUV1O0XhQm6MKrRwebowxdsxV48wzncxmY8Ne849d0hZQk3cQ1Hs0w36RwfcSTLClHhq/kMutsb5mexh52hri1859DytbRFXDa/NEOhXY9Dr6w0eiQ95lu5M38cpdE2pH6TZv4R87hgfur//Bpf0iE5vOBAnKAAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAaCAYAAABYQRdDAAABP0lEQVR4Xu2TPyhFYRjGX/nXNZKUie4ig9GMZJEMdjcpAxkUi8WiZJDBKHVlMCBlMSh/VkVGu4FJyiCDeJ7e93be7zvfGW3nV7/u973P+36dzvmuSIljFF45t8I4x7KE/fNhrPTAEbgKf+FjkOZ5Fu17h2OwLYxDGod+wqYo8+yJ9p3GQYoT+Co60BtlDWbhpWjPUpTlGIL38Fh0gMMx+3BANH+JsiQrcAduiw5thLFMwU1bMz90WSEXcBouig7VXdYOr2HF9sznsjhNC/yAnXBSdOjG5XzqCVuzl3l/FqdZh7u25tNw6MfWpMt+yRo8cPtCeIFn3J4fgQcPwgVXJ+ewFtVydMAv2O1qt5K9tzNXbxa98H2ulmQcPkW1uuihb7Dq6sNWL4R/TTZ4jyzj9XmArbb/jvronWUlJSX/wh8jdEjyGyzoLwAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,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>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACIAAAAXCAYAAABu8J3cAAABbklEQVR4Xu2UzSsFURjGH/nIZwoXezsLipWlbJSLLK34G+yssaHsbCgpK1LWtnYWlkq3bCwk2VBIEs/bucd9vXNmzOhepeZXv5re8545z8w5M0BOOkZtISUDtNsWSR0do/WmLv1BBukB/bADKeihr3TKDpA+uHve0TW6S8/ps24S2uk1PYObkCXINi3RC7h5oSD9qNzXK+tF3nwDbaGNyB5khHaVr5OCvNMNukkXaUE3WJqQPYhG5hVtkfTSN1tMolZB5PxIkGZ6TFfhzk0sv9kaTdzWSBDZGjmgc3Db80AXdJOmVm+kjd7ScVXbQ8I61QgybYsxzCNhnb8MMgHXH/x6qhFkxtTk1+DvuaLqk+WabFuEn4Ls0C240x9C5s3aIrmC+2Prp19G/DoYQiVIqxkT/FhosU64sXVEX/cS3GcrDyoM03v6+NWh8Iton751AKf0hHao2hGi87we2Z59ekMP6Qu9ROAXn5OT8+/4BGNrZuc95kNwAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEIAAAAaCAYAAAADiYpyAAACjklEQVR4Xu2XW6gOURTH/27J/clBoomSKPJy0pGSkBeUQm6dXF/Uyanzgo7EAx4QeXApoSgRJaWEcnlweXIppHhTLkWEB4n/svacWbPn23PmPPiGvvnVr2bWXvN9s9fsvWcPUFHRU6bQWX6wkThJn9KzdD99SFfZhH+A034gwEw6xpz3otPpahPLENFztJMOMPHt9Bc9SnubeFmMo6/8YIAD0Hu/R+/SL+58p02yNNNP9Lnf4LgI/YGVfkMJ3KCv/WCAg9D7jv1Gl6cyDBF9Tz9D14VarID+UKhQ9WIdvY/iI0IKcYKupzPooHRzGumgVLif32BoQlLVsjhFW6EPrmghZGrs8IMhpHMdftBjAsotxHx61R1HKD41ZLGXNW4RvUYP01GpDEcLtHPj/QaPeGp0V4iJ0MW2qFvpwD9X5vOMjnbHEYoXYh/9QB/RJfQBfUsn2SQhTuwOqawUQRbUPGTk+J3NcxuKFWKtOY5QvBBb6CUkb0EppvTjRVeG4w50uOSxDHrxVwSG1V9E1qaXXixC8ULU4gpqjGzZG5zxgx4yLOXCXX5DHViKZEqGHNqVnWYqfUz3enHZK2UKsRn6OoqRDdMaOsTE5KLLtI+JhViI7I3m+QP61EMMh27zre30jTkP3dceJP9jp58smplCjKQ/6WRosqzMm+ht177BHdudZtnMQe3X5zF6BEmnZV2R/ZGMqpi+0MUyUwhBviPeQRtlPt6k3+kTOtflDEb+PqMe7EZ2RInx1LgO3XUOc+fCbOh6cgv6/ST5h2h/k5NiBF1M2+hGeh66K4uR47Hm/H9CHuA86AiRT4keIcPsI3QYHqcX0s2NQ/zVFjst3dw4LEBShFavraKioqKiokH5DS47pzBUXYlnAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA/CAYAAABdEJRVAAAFiklEQVR4Xu3dW6imVRkH8GVjpmYmOKKo1FSGSpCaGahEmQZGKSqliKA5iKOghabgTReeLUvDFOzKDl5kRgieUslznrEgsRQvRISybtIgURF9Htd63cvldmZwtt/es+f3gz/vWs/7fTPzzdXDWu+hFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlq2Vkdsid6wjB0xfAABgtrIZu7ybXxT5ezdPr0e2HGoAAMzIhcP8tci3h9oNwxwAgBnac5i/Edl+qJ00zAEAWETZsAEAsETldWoaNgCAJezSyP1jsVkzFubxm7Ewj2fGAgAA6+/RyMVjsXliLAx2LetenVtV1v0ZAADew3dKbaa2GerbRV5q+Umr5dZpjq+NfCqyd6mP/ng2cnz7TNbOi1xQ5m5i+EVZv1U4AAA6m0V2iVxXasP2xXeefssVkT9087914+vb8a+RM7r6X9rxrFKbvvRU5OQ2BgDYYNm8jHm51AfNZpOzKcnfPr3pIFfLzuzOTde8vRjZvI0PjezVxn9qx/RcNwYAWBAHR16NbN3Vti21gTmlqy13N7fjcZEVkcPbPN+KMDmnHT8TOayN80aF/L+6ptTvnR5Z3c4BACyIH0buGYulNiG/GovL2JORH3XzOyO/jvy4q90aubKNszn7eakN2vORU1v9luIaNgBgAeX23n8j3xzqebF9vmtzi6EOAMCM5TVbuZKWW6CT3Ap8JbJPVwMAYJHcVGrDltuimcfL3Nbe2nx1PbJfAQBgg+Vzx/qHvObzyXJ+VFf7oOwsCx4AYBnK5uy+eWp5x+MHLe+0lIUNALAMZXN2YTf/cKv1d0bOZ3pm29ryz7LpPcsNAGDBfLLUp/NnY/Wlrr5Hq+W5L0Qe7s4BALBE5FP+j458djwBAMCmKV+Dta70b2EAAGCGPho5opvfV+qWbO/sYQ4AwAx9d5i/Wt7dsJ00zAEAmKHfDfNs1h4daj8Y5gAALKJs2PI9pgAALEGHRF4v9bq2xbBb5JnI8eOJ9+EjpTafF40nAAA2ZudH/jwWZyyfPbdqLL5Pr0W+NRYBADZW25W6uvaN8cSM/X4sbIDHxgIAwMbsivLuu0PT5yKXlNrMpRWRe0vdNr0g8sdWT6dFtoq80Ob52dyaTLdHPh85ss3ns09557/hhHbcN7JtG+f5bC5/G9khclWrHRP5dORf7XP7R45t43yTxOVt/L/IoaXeSPFIq/V3wT4U+USpvzn/3HyAcf72fLH7nZEz2+e+3I4AADORLy3/R6kNyp6lvs90kluU+caFaat0ZeSgNr621MYprY5sWWoj90qrfbwd05oy13S9l++Xeg1b2iZyeGTzyNNvf6KUB9sxr7fL7c6PRU4s9Z2p10Vu687v1MZ57tk2zt+YjV42Zb8s9VVguXU6yXe4ZmOZv/n+VvtaO+Z3cwXy1OIdrQDAEpONVjZA6add/eUy15T9px3PLbXRmZqcdEY3Xlujk6tj06paNl/52e9F/t9q+baFbJgOaPN72nGSDdW08nVXZJfI7qVem3d3q1/djlnLxu36MrdKeHCZayqz8TywjSeXDnMAgCUjtxBzqzM90NVvLHN3lOZWYnoi8rNSt0ePK3WbM7dQU66arU02XLn1mF4qdYXtsMi/Wy1X6XKF75pSV/OmlbxJznN1LP/OHJ/V5nmn6PR6rYvbZ3MlLWUTNjWHuWK4Rat/vdTVvd5l7fihyH79CQCAxdZvZe7YjVeV2jhN8lqxlNuMk2m8V1fLZi6vKeuTn8uX3k/6lbgcT39vXqc21aYtz96u7ZhNVS+/n9/NrdCvDOeySZsatVx1S/Nt3+afmQ0gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAy9ibfiTzYGLuTvoAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAaCAYAAABozQZiAAAA/UlEQVR4Xu2Rr2tCYRSGj4ppf4PBIvsXdEVQFLFYlgWDplVBYcEqmMWiQS1iWxhoW1jSqtUkA8PiwOLew/fdX6/3jmXxgQeu73nPxe9+IjdBE64jXME+fHLbRBrm4RRe4Mb+Vgu+/E/exJTalMfgDtYpd4nDbzHLWZop+veXHDq0xCy+8wCUxMz0eKE45+pQnoFH+EN5gIOY5SGswhc4hic4gSm3SehAF/Xtr9a5zWYw4VWvGYkp9ih/tvkn5QH2YkpFyvXKNN9SHkALZ/hA+cLOwm7ARQsfHIIv8c6tlGFSHx7tgB3YopIT87X1qhqw5pv9Cz1KBXZ5cOdOJL+Vuj+b5kHlZwAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAaCAYAAADFTB7LAAACH0lEQVR4Xu2WzUtUURjGX0qxRZAffaqbSEhxkYZhmG4yaGEfLhJBKnChtGjjSoxAKgs1FDEK3OmiNu7UyI9FSysLVIgW0T8QQYEUFEQ9D+97m+ObozIy02Dzgx9z73POnTl3znvPuSIZ/iPmNnAaPoEP4Dm7JmVUw2V4G7bC0/CXOQavwptw0rJOvSx13IE5LosGWBRk2fAzvBhkKWHeB6KDe+tD8B6W+jCZNMJ2l+0SHSDbQvbBUZf9E87AnzDXN6QLd+ELH6YTz2GfD5MMV4kV+NE3eLjGsf52+4aAQR+swwLs9mEc3sEbPvQMiA5wPV75IA75ot9V6xvW4KBssu8biT9A7iTcVdg+BXcEbUPwPnwNW6wf65h9WTIRB+BD0R2JC/4pyy/DrzDLztckuuN4AyRN8JvLrokuQaRMYu3DcNaOSR5cglfgCdHfuWBtI/CpHf/FB4kNzFsV9COLsCs457/G3SWiRvS6/fYZTRlr+ju8bue3ZHWpsC8HvSUKRL/oJDxr2Tic+dNDl6gv8JLowHdaXiF6bZ2dc9q5UnArPSralyXD94CEaZBYnTyy7B58aceVotPLGuSPP7O8De4V/QePWfYDNsMO0cGzpktEbzBhCuEn2AP3WMa6moC9og9FveXnRffyftH+hIPhGxFfTlibjyW2ZPEmORuH7DxhDoveqeeID8Bx0RsIKRadUk5neZBzmeETniFDhm3Fb4Jrc2KYKbRqAAAAAElFTkSuQmCC>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGgAAAAaCAYAAABb9hlrAAAER0lEQVR4Xu2Za6hWRRSGV2X3suyG1a+iKLprZZGV3QgqyQtEQSQaESlpWEEkSTcruyl0RSM9UWZ2+xNdUEussIhuCgWRgRT9KIP0R0FF5Pu01mLv5pz6hM45feQ88HJmr9mzv9mzZtaaPcesUqlUtglWdNAb0rPSw9LYaFMZJE6R1kl3SFOkc6Q/Qk9Jk6RbpFfCdpM3qwwWd0o7F7Z00MEt247Sj9K4lq0yCLxXGsyd81lpFF9KR5bGysAxXrq6sO1i7iDq2uwv9RS2yn/AedLv0t5lRaU7uEt6vzRWuodV0r2lsYt4QPqqNPYTU6UfrIujB9845J89yooug63/QLG8NHQTD5o7qJs5XjqgNPYTfG78VBq7iY/s7x20n3S/tFKaJz1iHg7Z7S2SHpLmSztkAzHCfOc3x7wNO0GgDdcvmIcV2m9tWJ0h3Sc9Lj0tTWjVDZFmSQuka8yfDbOlN6XrpGfMT0SS7aLubvM+5fvTxx7pubg+Snopyt9Ih0YZHjUfG56bH/I5XnzG0O5la1b+GeYnND3S4rB1ZB9rPlD7gkEZJn0snRC2m6XvzQeGD1nanh11J0lfS8dIN0Qd7YGNCIwJO4PwSdg6gVPPjfJk82+zBIc9Yf6p8J15voILzAePvh4rrQ07cM+eUX7V/FRluPnR1r7WjAfvmn3cbM0HO+90RZRPtuZ+ohF1/BZ/aZMTY6M0Msod8x0JNx1TikFuc3HYkw+k26JMJ9dH+Xzz+46L67fMO1zCIHCctLUwMdq/T764NcqrpWVRxoHtCUFO5frCuE5YtTgSdpN+lS5rqu1185VKVNgkXR52Vijw3F+iDLebj0mCE39rXQNjg6NY1ZOt6WO/QAh4O8q54sbENS/DC+9lHoZ+tibc8RIXSadJu5rnkO3Nd0xXmq8+vr86wXO/iPKB5r/PCt3dfFYS3oBzxTVRxlk4pq9vu+fND4IhJ1XmN/IR/WaQT4y6PPrKlVlOmFXmY3BEXM+13p8sE83HaEBgiXNwCpeYDzDhLUPB6dK15i/FgCXUETbINdxPTB4Vdl4SJ2WY+CdelB6L8lXmziKH4GBm7vSo+9w8RzKwOPWeqC9hVeMkJtJS83Y8C3AQTj3L/F3pK5ML0gHkmVxBbF5YgZdakwLetd6R4zDzyZ3ks/41O5l3OGMniZ+EC7zUp+bhisFgdTCYDBL5hlxER6fF/eQJEuvCaEPypk0nvrXmCOpM8998rXVNQiZ0sNIZHEIRk4dQmBOrDZMGx5G7rpc2mG92Evr3jnl/P5SetN4DPtP8wJnNAb+zJOyMCc7LCNOGCUobnsWE7jcIK8lQ82ScsDIOb10zs8lBhAzie3vXQzLNE3R2Rwntic+lboz69u/ndTuGEzr49wlwqMukgoPM+9MX3JP3scvMnWZyqvm7scpGS4f8tfpPchUwyY5u2cv+JvSZzUqlUqlUKpVK5X/HFnxn5A9sY+hUAAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEEAAAAaCAYAAADovjFxAAAC2ElEQVR4Xu2XWahNURjHP/OcUkSJm0wpKUkZ6h4PhhAiopTiZigyRhJOylRIyaviQcSDoQjJJQoZSh7MD4YHeSCKKPH/32/vc9f69t5nn3M7naf1q9/D/r519t5nDd9aWyQQCGQwDd7I8BxcC/uWWtefTnAy3AyXmlwlrIfL4SibcOkHC3AL/AcXRNd0GfwEP8LGltb15zl8CQ/BO3COn86kJzwDD8D98BW84rVIYSu8Z4NgnmjnfLaJOtALXoJdnNgfOM65TqMdvA7XOTEO9mvnOpXLcJ8Nij6QnUDLMdgGasBOSc7AX/CaiVkmib5vdxPnsuhhYiXGiv6IU8hySzSX92DSGx6B3+Epk6sWdiqf297E70ZxLtssJkpy9naEt53rBBskfaQPi8a5LkeYXDlGwmOia3i+yVVKQdLfidOc8e024cCOeyra7qzoux+Fb9xGlvOiP1gMp4tOm6Lon18BO5RaVsdG+B4+gLNMLo/Zkt4JV0Xje2zCMBA+ktal/BUO8lo4sNe+iDbkGqR7RafSeKddW+EWtxK+gwslOb2ziAuyhbWLcVb9PDiocSfQ+366lU2iDW7ahGi83NqrlpnwA7wAu5qcZbSkdwJrE+OcoVlwG2UBHR5dcyYX4U+4Oop5XBS96S4TZ2VlfJGJtwWO/hLRvb7BT2UyQPT5nU28OYpzpmTBET9pg6Iz+4QNsmJ+E71pwU+VCtMUE68G7u9cClybu02uEt7C/ibGOvVXdN/P4odoUU8j0Tk8jvKPcktzDySEM4O5MdG1HZE8eL9novWlj8lVCt+h0cR+i3/yGypa2HnYi+FMeOhcx/Cd+BnQQoP4BSPWpVsU435fhI+9bDo74BPRXYG/rwXN8DScCw+KHuVdJsAX8LiJzxAdXBZ6dia/hbhlVw0/OlaJ/qnMk1bEMNgkyRlVC4aIfghts4kcWNd4dF4Dp4oepwOBQCAQCAQCefwHjMOY/TQezPsAAAAASUVORK5CYII=>