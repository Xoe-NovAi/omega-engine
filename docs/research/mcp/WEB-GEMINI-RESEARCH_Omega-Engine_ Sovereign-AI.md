# **Omega Engine: Sovereign Orchestration & Memory Fabric Deep Research**

The architecture of local-first artificial intelligence has undergone a fundamental transformation leading into 2026\. This shift is characterized by the move away from centralized, cloud-monolithic models toward sovereign, orchestrated systems that prioritize local hardware optimization and data privacy. The Omega Engine Control Plane represents the pinnacle of this evolution, specifically designed to leverage the unique microarchitectural characteristics of the AMD Ryzen 7 5700U. By integrating low-level Linux primitives for process supervision, a multi-tiered memory fabric for state persistence, and adaptive orchestration topologies grounded in graph theory, the Omega Engine defines the frontier of autonomous, resilient AI operating environments.

## **Sovereign Lifecycle and Supervision Architecture**

The management of agentic microservices within a sovereign environment requires a departure from traditional container-heavy orchestration. On mobile-class hardware like the Ryzen 7 5700U, the overhead of Docker or Kubernetes runtimes significantly encroaches upon the limited memory and thermal envelope available for LLM inference. Consequently, the Omega Engine adopts a native supervision model based on systemd and its advanced socket activation capabilities.

### **Advanced Socket Activation and Dynamic Microservices**

The primary mechanism for managing dynamic microservices in the Omega Engine is systemd socket activation. This pattern allows the system manager to create and listen on IPC or network sockets on behalf of a service before that service is actually executed.1 When a request is received—for instance, an agent invoking a specific tool via the Model Context Protocol (MCP)—systemd transparently spawns the required service and passes the pre-opened file descriptor (FD) to it.3

This "on-demand" spawning is essential for the 5700U’s 15W–25W thermal design power (TDP), as it facilitates a resource-conscious mode where processes consume RAM and CPU cycles only when active.4 The technical implementation relies on the standard protocol where systemd passes the socket as file descriptor number 3\.4 Services integrated into the Omega Engine utilize the sd\_listen\_fds() interface to retrieve these descriptors, enabling a sub-50ms response time from the moment of activation.1

The transition to socket activation also provides superior network bandwidth compared to traditional container networking (like slirp4netns), as the socket is opened directly in the host's network namespace.6 This reduces the latency of cross-agent communication, which is a critical bottleneck in multi-round reasoning tasks.

### **Stateful Handover via the File Descriptor Store**

A significant challenge in on-demand service spawning is the preservation of internal state. The Omega Engine utilizes the systemd File Descriptor Store (fdstore) to handle stateful handovers without the latency penalties of persistent disk writes.1 By configuring the FileDescriptorStoreMax= property in the service unit, a microservice can upload file descriptors to the service manager during its runtime.1

For the Omega Engine, the most sophisticated implementation of this involves the use of memfd (memory-backed file descriptors).1 An agent process can serialize its current context, focus chain, or KV-cache metadata into a memfd, upload it to the fdstore via sd\_pid\_notify\_with\_fds(), and then safely exit.1 Upon subsequent activation by a new request, systemd re-injects these descriptors into the process environment, allowing the new instance to recover its state in memory.1

| Feature | Implementation Mechanism | System Impact |
| :---- | :---- | :---- |
| FD Upload | sd\_pid\_notify\_with\_fds() | Asynchronous persistence without I/O wait.1 |
| FD Tracking | FDNAME= metadata | Granular state recovery for multi-agent chains.1 |
| Persistence | FileDescriptorStorePreserve=yes | State survives full service stops, not just restarts.1 |
| Inspection | systemd-analyze fdstore | Real-time debugging of persistent memory segments.1 |

### **Supervision Logic and Recovery Performance**

Comparing systemd socket activation against supervisord and AnyIO native process monitoring reveals distinct trade-offs for sovereign systems. While supervisord provides a user-friendly INI-based configuration and web interface, it introduces an extra Python-based dependency that adds to the system's baseline memory footprint.7 In contrast, systemd provides kernel-level integration via cgroups, offering the most robust recovery and resource isolation.7

The Omega Engine prioritizes systemd because it handles the "socket buffering" problem: while a service is recovering from a crash or being spawned on-demand, the kernel buffers incoming requests in the socket queue.4 This ensures that the control plane does not experience dropped messages or "connection refused" errors during sub-50ms recovery cycles. Furthermore, the use of Restart=always with StartLimitIntervalSec= allows for intelligent back-off strategies that prevent "thundering herd" issues when multiple local agents crash simultaneously.7

### **Idle-Reclaim Algorithms and Model Hibernation**

To maintain the efficiency of the 5700U, the Omega Engine implements an aggressive idle-reclaim strategy. This is not a simple "kill" command but a choreographed hibernation. When a model server (like a local instance of Lemonade Server) detects that it has been idle for a predefined period (e.g., 300 seconds), it executes a three-step sequence.10

First, the server quantizes its current KV-cache to Q4\_0 and serializes it into a memfd.11 Second, it uploads the memfd to the systemd fdstore.1 Third, it terminates its own process, triggering the kernel to reclaim several gigabytes of RAM previously occupied by the model weights.11 The socket remains open and supervised by systemd, so any subsequent call to the agent’s API will instantaneously re-spawn the process and re-load the weights and context.1

## **Tiered Memory and Vector Sovereignty**

The Omega Engine's memory fabric is designed to mirror the cognitive tiers of human memory: a HOT tier for immediate focus, a WARM tier for associative retrieval, and a COLD tier for permanent relational knowledge.

### **HOT Tier: Redis JSON and the Red Phone Kill Switch**

The HOT tier provides the sub-millisecond responsiveness required for the "Red Phone" kill switch and active reasoning chains. By using Redis with the RedisJSON module, the Omega Engine stores agent "focus chains" as structured documents.1 This allows the control plane to update specific sub-fields (such as an agent's current task status or last-seen token) without the overhead of full JSON serialization/deserialization.

The "Red Phone" kill switch is implemented via Redis Streams and Pub/Sub. Because Redis operates as a high-performance, single-threaded event loop, it can broadcast an emergency halt signal to all active agent processes with near-zero latency. This is a critical sovereign safety requirement, ensuring that an autonomous agent can be instantly restrained if it attempts an unauthorized action, such as an external network request during a "private-only" reasoning phase.

### **WARM Tier: Qdrant Optimization for AVX2**

Vector sovereignty on the Ryzen 5700U is constrained by the CPU's lack of AVX-512, necessitating a highly optimized Qdrant configuration for the AVX2 instruction set.12 The Hierarchical Navigable Small World (HNSW) index is the core of this tier, and its parameters must be meticulously tuned to balance search precision with the limited RAM available on a mobile chipset.

| Parameter | Recommended Value | Rationale for Zen 2 (AVX2) |
| :---- | :---- | :---- |
| m | 8 \- 12 | Minimizes the number of edges per node, reducing RAM footprint by \~30%.12 |
| ef\_construct | 64 \- 100 | Balances build speed and retrieval accuracy; higher values exceed L3 cache efficiency.12 |
| full\_scan\_threshold | 10,000 KB | Below this size, linear scan is faster on Zen 2 than graph traversal.12 |
| on\_disk\_payload | true | Moves metadata to NVMe, preserving precious RAM for the vector index.12 |

The research indicates that for 1536-dimensional vectors (standard for models like text-embedding-3-small), reducing the m parameter is the single most effective way to minimize the memory footprint of the index.12 On the 5700U, this prevents the HNSW graph from thrashing the 8MB L3 cache, which is split into two 4MB segments across the dual-CCX topology.

### **COLD Tier: Relational Anchoring in PostgreSQL**

While vector databases excel at semantic similarity, they often struggle with relational integrity and complex filtering. The Omega Engine uses PostgreSQL as its COLD tier to provide "relational anchoring." Every vector point in Qdrant is linked to a unique PostgreSQL UUID. This ensures that the "semantic memory" (the vector) is always grounded in "factual memory" (the relational record).

To maintain consistency during high-concurrency ingestion, the Omega Engine employs a Write-Ahead Log (WAL) pattern. The process is as follows:

1. The agent's output is first written to a PostgreSQL table, generating a UUID and a timestamp.  
2. The vector embedding is then generated and written to Qdrant, using the PostgreSQL UUID as the Qdrant point ID.  
3. If the Qdrant write fails, the Postgres record is marked as "unanchored" and is eventually reconciled by a background worker. This prevents the emergence of "phantom memories" where an agent retrieves a vector but cannot find the associated source document or metadata.

### **TLS/SSL Sovereignty and Zero-Trust Communication**

In a local-first environment, the assumption that local traffic is "safe" is a vulnerability. The Omega Engine implements a zero-trust architecture where all inter-process communication is encrypted. For the HOT tier, rediss:// is used to enforce TLS for Redis connections. For the WARM tier, Qdrant’s gRPC interface is configured for TLS termination.12

Since the system is sovereign and may be air-gapped, it cannot rely on external Certificate Authorities. Instead, the control plane acts as a local Root CA, issuing short-lived, self-signed certificates to each microservice. These certificates are passed to the services via the systemd LoadCredential mechanism, ensuring that private keys never touch the persistent disk in an unencrypted state.

## **Adaptive Orchestration Topologies**

The orchestration layer of the Omega Engine is governed by the AdaptOrch framework, which moves beyond static "agent chains" to dynamic, task-aware topologies.13

### **Topology Selection Algorithms and Coupling Density**

The core of AdaptOrch is the calculation of "Coupling Density" (![][image1]) from a natural language prompt. Before execution, a high-speed "Routing Model" decomposes the user's request into a Directed Acyclic Graph (DAG) of subtasks ![][image2].13

![][image3]  
In this formula, ![][image4] represents the coupling strength between subtasks, which is categorized during decomposition:

* **0.0 (None):** Fully independent subtasks.13  
* **0.3 (Weak):** Shared context is helpful but not mandatory.13  
* **0.7 (Strong):** The output of one task is the direct input of the next.13  
* **1.0 (Critical):** Semantic coherence between subtasks is mandatory for a valid result.13

Based on the calculated ![][image1] and the "Antichain Width" ![][image5] (representing maximum parallelism), the system selects one of four canonical topologies.13

| Topology | Selection Criteria | Operational Mode |
| :---- | :---- | :---- |
| **Parallel (![][image6])** | $ | E |
| **Sequential (![][image7])** | **![][image8]** | Strict topological order with context forward-passing.13 |
| **Hierarchical (![][image9])** | High ![][image1] and High $ | V |
| **Hybrid (![][image10])** | Complex DAG with mixed ![][image1] | Partitioned groups connected sequentially.13 |

### **Blackboard Architectures for Multi-Round Debate**

For adversarial or iterative reasoning (e.g., the Debate mode), the Omega Engine implements a "Blackboard" architecture using Redis Streams. Unlike a simple queue, a Redis Stream allows multiple agents to subscribe to a persistent, append-only log of the conversation state.

In a Debate mode, the "Lead Agent" posts the initial problem to the stream. Two or more "Debater" agents then contribute perspectives, reading the entire history from the stream before appending their own thoughts. A final "Arbiter" agent monitors the Consistency Score (![][image11]) of the debate.14 If the ![][image11] remains below a target threshold ![][image12], the system can programmatically re-route the task by increasing the coupling density and escalating to a more capable model, ensuring that the final synthesis is logically sound.14

## **Hardware-Centric Performance: Ryzen 7 5700U**

The AMD Ryzen 7 5700U is an 8-core, 16-thread processor based on the Zen 2 Lucienne architecture.15 To achieve peak AI performance, the Omega Engine must account for the 5700U’s specific CCX (Core Complex) topology and memory bandwidth limitations.

### **KV-Cache Management and 2026 Quantization Standards**

By 2026, the management of the Key-Value (KV) cache has become as critical as the quantization of the model weights themselves. In previous eras, the KV cache was stored in FP16, which consumed massive amounts of memory at large context windows—often leading to "deadlocks" when context exceeded 24,000 tokens.11

The breakthrough lies in Q4\_0 and Q8\_0 KV-cache quantization. On the 5700U, Q4\_0 quantization reduces the memory footprint of the context from \~400 MiB per 1,000 tokens (FP16) to just \~45 MiB.11 This allows the Omega Engine to support a context ceiling of 128,000 tokens for a 14B parameter model while remaining within the 5700U's typical RAM constraints.11

| KV Quantization | Speed (tok/s) | Context Ceiling (14B) | VRAM/RAM Usage @ 32K |
| :---- | :---- | :---- | :---- |
| FP16 | 27.2 | 24K | \~12.8 GiB 11 |
| Q8\_0 | 27.3 | 64K+ | \~6.4 GiB 11 |
| Q4\_0 | 27.3 | 128K | \~1.4 GiB 11 |

For the Zen 2 architecture, the use of Q4\_0 is particularly advantageous because the reduced memory throughput required for the KV cache prevents the dual-channel DDR4-3200 memory controller from becoming a total bottleneck during high-context generation.11

### **Process Steering and CCX Pinning Strategies**

The 5700U is composed of two CCXs, each containing 4 cores and a shared 4MB L3 cache.17 Cross-CCX communication (via the Infinity Fabric) is significantly slower than intra-CCX communication. To optimize for this, the Omega Engine employs a strict CPU pinning strategy.

The heavy LLM inference engine (e.g., llama.cpp) is pinned to Cores 0-3 (CCX0). This ensures that the model weights and active KV cache remain local to a single L3 cache pool, avoiding the latency penalty of cross-CCX cache misses.17 The secondary, lighter-weight processes—including the Redis HOT tier, the Qdrant WARM tier, and the various socket-activated MCP servers—are pinned to Cores 4-7 (CCX1).10

This strategy ensures that the intensive "prefill" and "generation" phases of the LLM do not starve the orchestration control plane of CPU cycles. Furthermore, the 5700U's simultaneous multithreading (SMT) is utilized by pinning each physical core to two threads: one for the primary task and one for background telemetry and safety monitoring, ensuring that the "Red Phone" kill switch is always responsive even when the LLM is at 100% utilization.

## **Synthesis: The Sovereign AI OS Implementation Roadmap**

The research presented here culminates in a clear implementation roadmap for the Omega Engine on Zen 2 hardware. This roadmap is designed to move from foundational process management to a fully autonomous, topology-aware agentic system.

### **Phase 1: Substrate Initialization (Month 1\)**

The first priority is the establishment of the systemd user-session environment and the native memory tiers.

* **Microservice Layer:** Implement the omega-agent@.socket and omega-agent@.service templates. Configure the FileDescriptorStoreMax=100 setting and the sd\_listen\_fds() logic in the core agent wrapper.1  
* **Memory Tiers:** Deploy Redis with the JSON module for the HOT tier and PostgreSQL for the COLD tier. Initialize the Qdrant WARM tier with the AVX2-optimized m=10 parameter.12  
* **Security:** Establish the local Root CA and implement TLS termination for the rediss:// and gRPC endpoints using systemd credentials.

### **Phase 2: Orchestration and Topology Logic (Month 2\)**

Once the substrate is stable, the system's "intelligence" about its own structure is implemented.

* **AdaptOrch Deployment:** Integrate the AdaptOrch framework. Develop the "Routing Model" (using a quantized 7B parameter model) to perform DAG decomposition and ![][image1] calculation from user prompts.13  
* **Blackboard Integration:** Implement the Redis Stream-based Blackboard for adversarial agent modes, ensuring all agents are configured for cross-stream state transparency.  
* **MCP Expansion:** Connect tool-calling agents via the Model Context Protocol using the socket-activation pattern, allowing the system to scale its capabilities without a permanent RAM penalty.10

### **Phase 3: Hardware Tuning and Optimization (Month 3\)**

The final phase involves refining the system's interaction with the Zen 2 silicon.

* **KV-Cache Transition:** Migrate all model configurations to Q4\_0 KV-cache quantization, enabling 128K context support.11  
* **CCX Pinning:** Apply the Core 0-3 (Inference) and Core 4-7 (Orchestration) pinning policy using AllowedCPUs= in systemd unit files.17  
* **Hibernation Tuning:** Fine-tune the idle-reclaim algorithms. Establish benchmarks for "cold start" latency (from socket activation to first token) and ensure they remain below 50ms for sub-7B models.

## **Conclusion: The Performance Convergence Paradigm**

The development of the Omega Engine is grounded in the "Performance Convergence Scaling Law." As of 2026, the industry has recognized that as model capabilities reach a plateau of ![][image13]\-convergence, the primary driver of system performance is no longer the model itself, but the "harness" that orchestrates it.19 The variance in quality attributable to the orchestration topology (![][image14]) now exceeds that of model selection (![][image15]) by a factor of ![][image16].19

For the user of the Ryzen 7 5700U, this means that a sophisticated, topology-aware control plane like the Omega Engine—which understands when to parallelize, when to debate, and how to hibernate—is far more effective than trying to run a single, monolithic 70B parameter model at 0.5 tokens per second. The frontier of AI is no longer just about the size of the neural network; it is about the sovereignty of the environment, the efficiency of the memory fabric, and the intelligence of the orchestration logic. In this new paradigm, the Omega Engine transforms the 5700U from a mobile processor into a world-class, autonomous AI command center.

#### **Works cited**

1. File Descriptor Store \- Systemd, accessed May 14, 2026, [https://systemd.io/FILE\_DESCRIPTOR\_STORE/](https://systemd.io/FILE_DESCRIPTOR_STORE/)  
2. systemd.socket \- Freedesktop.org, accessed May 14, 2026, [https://www.freedesktop.org/software/systemd/man/systemd.socket.html](https://www.freedesktop.org/software/systemd/man/systemd.socket.html)  
3. systemd.socket(5) — Arch manual pages, accessed May 14, 2026, [https://man.archlinux.org/man/systemd.socket.5.en](https://man.archlinux.org/man/systemd.socket.5.en)  
4. Unravelling systemd socket activation | by Radu Zaharia | Medium, accessed May 14, 2026, [https://blog.raduzaharia.com/unravelling-systemd-socket-activation-f930562453b4](https://blog.raduzaharia.com/unravelling-systemd-socket-activation-f930562453b4)  
5. Oxy: the journey of graceful restarts \- The Cloudflare Blog, accessed May 14, 2026, [https://blog.cloudflare.com/oxy-the-journey-of-graceful-restarts/](https://blog.cloudflare.com/oxy-the-journey-of-graceful-restarts/)  
6. Does "containerized socket activation" improve network performance? · containers podman · Discussion \#14068 \- GitHub, accessed May 14, 2026, [https://github.com/containers/podman/discussions/14068](https://github.com/containers/podman/discussions/14068)  
7. Systemd vs Supervisor \- ege.dev, accessed May 14, 2026, [https://ege.dev/posts/systemd-vs-supervisor/](https://ege.dev/posts/systemd-vs-supervisor/)  
8. Supervisor Configuration for Process Management: Complete Application Monitoring Guide \- CubePath Docs, accessed May 14, 2026, [https://cubepath.com/docs/application-deployment/supervisor-configuration-for-process-management](https://cubepath.com/docs/application-deployment/supervisor-configuration-for-process-management)  
9. Supervisor vs systemd \- ERPNext \- Frappe Forum, accessed May 14, 2026, [https://discuss.frappe.io/t/supervisor-vs-systemd/80551](https://discuss.frappe.io/t/supervisor-vs-systemd/80551)  
10. Local Tiny Agents: MCP Agents on Ryzen AI with Lemonade Server \- AMD, accessed May 14, 2026, [https://www.amd.com/en/developer/resources/technical-articles/2025/local-tiny-agents--mcp-agents-on-ryzen-ai-with-lemonade-server.html](https://www.amd.com/en/developer/resources/technical-articles/2025/local-tiny-agents--mcp-agents-on-ryzen-ai-with-lemonade-server.html)  
11. akandr/bc250: AMD BC-250 (PS5 APU) setup guide — Ollama \+ Vulkan inference, poor man's AI assistant via Signal, stable-diffusion.cpp image generation · GitHub, accessed May 14, 2026, [https://github.com/akandr/bc250](https://github.com/akandr/bc250)  
12. Indexing \- Qdrant, accessed May 14, 2026, [https://qdrant.tech/documentation/concepts/indexing/](https://qdrant.tech/documentation/concepts/indexing/)  
13. AdaptOrch: Task-Adaptive Multi-Agent Orchestration in the Era of LLM Performance Convergence \- arXiv, accessed May 14, 2026, [https://arxiv.org/pdf/2602.16873](https://arxiv.org/pdf/2602.16873)  
14. AdaptOrch: Task-Adaptive Multi-Agent Orchestration in the Era of LLM Performance Convergence \- arXiv, accessed May 14, 2026, [https://arxiv.org/html/2602.16873v1](https://arxiv.org/html/2602.16873v1)  
15. AMD Ryzen 7 5700U (Lucienne: Zen 2\) Benchmarks Surface: 15% Faster than the 4700U, accessed May 14, 2026, [https://www.reddit.com/r/AMDLaptops/comments/jsxvd2/amd\_ryzen\_7\_5700u\_lucienne\_zen\_2\_benchmarks/](https://www.reddit.com/r/AMDLaptops/comments/jsxvd2/amd_ryzen_7_5700u_lucienne_zen_2_benchmarks/)  
16. AMD Ryzen CPUs for LLM (and AI in general) \- X or X3D (big cache)? \- Reddit, accessed May 14, 2026, [https://www.reddit.com/r/LocalLLaMA/comments/1izo4zu/amd\_ryzen\_cpus\_for\_llm\_and\_ai\_in\_general\_x\_or\_x3d/](https://www.reddit.com/r/LocalLLaMA/comments/1izo4zu/amd_ryzen_cpus_for_llm_and_ai_in_general_x_or_x3d/)  
17. Why did AMD choose a 2x 4-core CCX die design for Ryzen 7, instead of a single 8 core die with one big cache? \- Reddit, accessed May 14, 2026, [https://www.reddit.com/r/Amd/comments/605aow/why\_did\_amd\_choose\_a\_2x\_4core\_ccx\_die\_design\_for/](https://www.reddit.com/r/Amd/comments/605aow/why_did_amd_choose_a_2x_4core_ccx_die_design_for/)  
18. So I just realized how AMD is going to double the core count for Zen 2 \- Reddit, accessed May 14, 2026, [https://www.reddit.com/r/Amd/comments/954h43/so\_i\_just\_realized\_how\_amd\_is\_going\_to\_double\_the/](https://www.reddit.com/r/Amd/comments/954h43/so_i_just_realized_how_amd_is_going_to_double_the/)  
19. Agent Harness for Large Language Model Agents: A Survey\[v3\] | Preprints.org, accessed May 14, 2026, [https://www.preprints.org/manuscript/202604.0428](https://www.preprints.org/manuscript/202604.0428)  
20. Punctuated Equilibria in Artificial Intelligence: The Institutional Scaling Law and the Speciation of Sovereign AI \- arXiv, accessed May 14, 2026, [https://arxiv.org/pdf/2603.14664](https://arxiv.org/pdf/2603.14664)  
21. Agent Harness for Large Language Model Agents: A Survey\[v1\] | Preprints.org, accessed May 14, 2026, [https://www.preprints.org/manuscript/202604.0428/v1?ref=observability.how](https://www.preprints.org/manuscript/202604.0428/v1?ref=observability.how)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAbCAYAAACqenW9AAAApElEQVR4XmNgGAX0BglA/B+Ku5DE2YD4HJQGgzwGiKJjQPwLyg6HysUDcRWUzaAKxD+BuAzKlwDibQwQjSBwCoiFoWyGmQwIhTDAA8QvgFgOiCcgS+gCMTuyABRMAuJYIFZGl8AGkoB4GbogLuAAxB/QBXEBJyBejC6IC1QAcTm6IC6wG4iD0QWxAW4GSOQooIljBTVAPBFdEBcAhbEBuuAoQAYAHYcZKT1EKVMAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJIAAAAaCAYAAABcmAU7AAAFbUlEQVR4Xu2aB4hkRRCGS1HMOeKpJ5gjJsynZ85ZT4ycWYwgYlZQUVQwcuaAAQMmzIHDhIqCOSKeCbPeYURFj0Prm+re6amZeWFm9maWfR/87HRVT88L/bqq661IRUVFxUhhftXKqnGqWZxvpLC16l3V3N5RUYotVW95Yx5MmldV/6lmqN5Xfag6Ovjj30FnOdVXqlVDe1bVg6rJTicHf+TwxIcmNboL43+nnfaMXxhwzlHN7o3tWET1hOpx1WaquYJ9WdUrqrvFJthI4APV2c62ueoY1XTVI6qtVEs39BBZQXWx2BN4nGqNRndhJqq+F7te96rGq3ZSHaQ6XvVl8B1Q6z348CCe5Y2tIIx9qvrLOwKriK1QI2Ui/aJa0BsDnOdF3pjAZOuWeVT/iF2v3Z0P1hXzbeQdA8yvqsW9MWV51Y9iJ7af86W8rfrdGweQOVQXeGPCc6o7vTEwRvWDN3bAdmLXE7HSt+I3aV4RB5lPVNd5Ywony0q0mHc4HlKd5o0DyMPe4DhPLLR49lF9LDYRuyXmmZcnNlKEz8JnfuOaxFeE+VSbSH6uwsMwrzcWZDbVhlLPLVP2Ejunbb0D5hRzFjmp/SV/sg0C07zBQUJNmE5vCBee5Jw8qheQh3FddwttfuumoE7YWGxykm9NFcvvIqy+U8LnXVV/iyXyZblULOpcpbpBtX6juxbWOKcLnb0GCSDO9MBmBmzJSd7YDRTVmrVvZkNelJfHxbDDChG5UnVr0u6WGNZeErup5Gy0D0w7lYDNDg8xmyDG4XiBCUq6EVOOw4KfsFkGcuTXpB6Gt1A9UHcP8adYZGqCm8nTw8pUBibCk9K8nY1iVmfBjvBMaZ4sWVqr9s1sVpT8ibSaWJ909flJ2ucyncD4L4vt1nYQW0mwLZn0KcOp4S/XgXFiisFKRfup0IZ7pB5CizBWbIeZ5mv3q65N2pFvVC96I7wgdpKtiBMlPl3fST1J5e9S4TO1Jfxrh/am0r9ciuJZ3kQC+pwePp+YOnoAE5LxxyU2Qs4VSfsdKV9aYIfHuOmNpFyDjWseOVea62PtYGLPkGLXDF4X2/U2cb3YwWTBj/DEkogBVe/L6u7a7P1ZrNYALN9cuH6wjhS7KPQhL+QpZMfaS/YW2/pnrfKd5DBsEjjuOPEJa3+IhbV4b+B51UpJOwvuFWNSdyvCFLE8qokTxFaarNcg/BBV4XYQ/+/zxhx4amOdpagOqX0zG/Ie+uZBn0fFiq9ZpYJOIKxzM9tBWN/XGwvwtNhxrx7a64V2uhAwgd5I2nnEaHKXd7SBe93y3BYVG2iis0fIhfCf4h0J+I/0xj5BIbDoRCJxZLsfK/hZLKG6Q2xnk1ce4LXS+d4YYBXhDUG6gsDBYit71qYnTqSYZ20f2rcP9bAJMSFpQxy7FYRfxiCv8lDZT2Gxoe/Nzj7EGKm//nhTLKG7ROwdGwkXO48svvCGPkPYzaujcK5pjSePhVXPiOUHtzW6anADGbOIWhV12W19LZb08pqmFYRKJs3nYnkQOddRqn/FQhPns8BQ7zpx7Hbjkqo8JnavKda+pzqpoYfBxOL4x3qHh+3ljqo9xHY/WeEuQl50ozf2mW1UO3ujg4el1UXPYxexlWm4oFaUl9+w6qavVogq45N2O/LGpdhJuGwH6UurkkBP2EB1qDf2GSZ30ZhfFlbqY72xR7CKfivFHuCyMHa34/L2Iyv0dgTLKDuPj8SWQj6zkg0K0yX/CSzLQmJ1lGW8o0ecIcXeMHQCY3cLJYtRx9WqZ6VekugFt8jw1ceoLPNSlDDVa+LY3UAR178yGTWw4+Qf04ZrBRktHCH2frKioqKioqKioqKiYmbyPx+cPOfXbPeXAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAaCAYAAAAXHBSTAAACsUlEQVR4Xu2WWYhOYRjHH1uWEEOWoialiEwZS5YQIksULlBj5kZyM+HGki1ruUG5oGRwo6wXLpCiREjZLhQlF1KWC1uSJP5/z3vyfM/3zsx3zsgpnV/9+s7zf9/zne1933NECv5vtvkgB7b4oC0sgg99mAPt4S4fZmEU/AKn+Iac+A4n+jAtd+F1H+ZIE7ztwzRMgD/hbN+QI0NFn9Zy3xBjJOzmsk/wvMss/XzQBrqInoOFcyjGQfhNdJ8y2sGV8AE8Du/DFaadT2m9qRM6wMPwJTzi2q7CSy5rjQb4SHSo9wlZR3gDTgu1pU5aGEGX4VtYG2r+MesE7rjY1Al74GbRk2efXiHnosL6YqgrgcfmcQfCDXBhyHlRz+C6UFsmiR5nrW/go/0BZ5mMHR+7eoapCYfoC9hZdFXkEOU2WSO6z8ZQVwKH97ywfQ3WmDbepKWmThghepwdvoHvnSU+dHBH/nFzsH26qd+JXmQnk1XKJtH/s3QVnSKe3qJ9j9pwcAj72zAC+0z1YaA7fC86vxLYP+18Srgj5Re1zNUJQ0T77rfh8BC2Bvss8GFgJjzlMvbnHSdzYU/T1hJ8IpwKb1zOOR9jjOixttuQS+FnGwR4ErtNzR3rTW3hAsIFw8L+k8P2PdFhOACehPvkz9zzcJ5y31sm49M4Z2oLbyj7cxUs4wM8DS+ITv6+pc2/T+ymyyy8u03wTPjljTobTJ5SFbwCn4u+NppjLHwCD8HXcHxpcwkcIewbhSvgaNG7G5vcO0Xf3pw/MYaJzrnk3dJD9LssNuzmwxM+jDBOyj8CPLzoRh9WSjX8Cle5PAscfqt9mIE58KPoDczMXvhU9GWYFQ7BV3CQb8gAV8kDPkwLVyZO4K2+IQXHJP65lQV+ZfA99VeolviL8F/CD9mCgoKCbPwCbXx/CaQeolgAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADYAAAAaCAYAAAD8K6+QAAACs0lEQVR4Xu2XS6hOURiGX7dyyzV3chSSUoqSUK4ZMTMxQxHFGVBi4JbIAJm4lRSRkii3JLklI0kGSBm4DoikSBLv17fXOd95z97/+f9ztjPxP/V2/vV+q73Wt/da61sHqPN/sph6pGYOo6jp1FxqQPAnU6NDuxqGUy/VLJOJ1FtqvAYC1ucI9Yf6RN2nPlDj4Am9gCdXK/NQ+wupin7Uc2qLBgLLqa/wRMYGvwv8Kz+h3ge/Vm6oUQb7qC9UXw1k7IV/pfNUf4kZl+Dxsxqogd/wrVAqn6ntagZs0g+pnhrIWAnvs04DNXCGekp100BimBpCHzXgieXRi3oH/6KVmA/fnx1hKPzlFL7gg2oEbPM/UxO+lPJohA82UgOCHThlLCM7fG6paUyjRqgZsLhNNG7+wdSB0I48gPfvLK7DD6dWXFAjB5torD2TqG2hnehK/UD7EltN3WxDeZyjfsHHbmIJfANG7lADxTsq7YXUWvGMRfCk8hJbgeYJ2mn2k7pLzc7i+7O/hk1S51W09A/Bx2tR03bD90TC6sv30E7oXrAbRF79socXJRb5CD8VI3abSNjz9bQ8Le3EKfh4VlebOEntCu0haD0pOzwUuzUUnXo2aX1GZAo8Xum2sgm+3KvhMnwFtMAOgFfZ7zHUbfig3TNvFvU6+x2xt3NMzYzN8GfklQhjByonblxUowJ2RbNa1gJLIN0A7lEN8P1lbXsLtn51vyVsjxQVX8OuSnY3vEbtoa7AC/ZMamfop9gybCvxxFR432UaSMyB76/EBPiRXgl74AI1Az3gk1xFrUfxF1Q2ovrENlBv0LzCSsE+/wk1S+Aq8i8EeTymtqrZUZbCl2OD+O0llQKrSd9Q3eXYxh+kZhkch1f+uIw7i97UGjXLxP5tOazmP2YGiq90derUqdM+/gKX0IdHa2rVxAAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAWCAYAAAAmaHdCAAAAxUlEQVR4XmNgGAWjgDRwF4j/48CvkNThBAlAfBaIdwPxQSD+BWXDcANMIS6gCsSPkPj+QHwCiY8MkA0G4V1A3IKiAgiYgfgJEBegS0BBPRB/B2IuJLEGJDYYODFAwsARXQIKdkIxMtiCxmeYyAAxhA9dAgo+MqDabALE35D4YHAfiC+iCyIBkAVLgLgWiq8AsQuyglioomhkQTSAzwIwYAJiQ3RBJAAK9KnogqQCZyAOQxckFigxQNLEPSA+DsQVqNLDDgAARgQr4XB2OmoAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAWCAYAAADJqhx8AAAA4ElEQVR4Xu2RPw4BQRTGH6FU6TT+NA4gCtXqtaJxAuEERMUBNKKyncYNBGdQkYhEReIKKr7nmd2ZFxs6zf6SX7LzfbOzbzNEMTEuR/iI8G7t+0gb7uAabkhe4mfjLNz6IguTZlGEl7AjD56ttU0ZLuCU5OCWWwsHONIhWMKJyvi3Haok4zd1AU5wrrKBWtOY5ICCyhkembst7KsuYA9vOnyTJ+nNzfTcWsbmoqMLkNYByV6+gIAErNiBRV0H4ApTOoxiSPIBQwY2rPVX+Ap9kkm6cOW0P5CDJZIDauRO82eexp8r6uxPMxUAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAE4AAAAWCAYAAABud6qHAAAC20lEQVR4Xu2YW6gNYRTHl1uS3O/kfkspkTdEQhJePIl0iqM8IKQIDyJCKJGIJ0pJIsmDUEjyIinlElIuRYQkJP5/a8Zee52Z2d9hn2lP7V/92vtba/Zc1p7vMiNSp04RmQU7+GACA+BEOA12N/EesKdph9AWNvhgkRgJX/igYxQ8DH/Bd/AmfA2Hw77wARz/d+twnsEZPlgEOsOHcJNPGBbCj/ANHOxydyPfwjYuF0KD6H55HoViN/wAu/pExE7Ru+yslHfNmNOi+TM+EQi76yPR4xSG9qLdbqtPGFiU25I+/i0W3WaVTzSD5fArHOLiudHHBxxdXPu8aOGSYKFewl0+4ZgqOtb9L+zu13wwLw75gGEYfOxiLNpFF4tZLXon9fcJB/e7yAf/gSPwmw/mAWe0rFltnGghhpoY2wdM23JLNJ8XGyTseKPhlmaYNen9IWRw5onZSYDtbaYd01p0zAm5EE8jvJziOTiotGkZKyTseFwW+eJkmVm4+fCCi12FvV3sqGunDeozRXNJF7JESoX4Ab/D63B6lN8bfZJW8JRpZ7FAko/XomyHa0ybJ/zZtGPmujZPlP+Kh3dFWuEsnBQ4I1r6me98wkj6Y5JYJpWPV3WOiRYvho8+/iRGiHZBC7fZ52Ix76XpPixjRPPsOmmsg2N9MIX1kn28mHlS+lND/Kk/S4YX/zT6PlB0WuePuLgkk+Dz6LuF2xz3wYiNovluPhGxWSpfKBfNoeyQyvurOiwQ12Q88A3RhSQvOK74QdGHcM9+0XGqk08YXonu5x7cI7p8uQMnS/bAy24aWgj2BD6yZS2nWpQpouNbDLtnUsFi+EaEFzfbJwzt4AS4FK6EHcvTqayV8MJxGcVt2f0LAR/K78MTPlEF2AOe+GAKvJMv+WCtM0e0u/LVUjWwS5Uvoi8BsuC68pM0nfELAZ8ervhgTpyU8LVeTcKxq9JzabXhO7hePlinxvkNoHmkgXQmg6cAAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAWCAYAAAAinad/AAAA4klEQVR4XmNgGAWjgL7gERD/x4E3IKkjCNKB+DgQ7wbiE0D8AcqG4XCEUvxAHYgfIPFzgHglEh8ZbGZAWNAEFZuGJIYCOIH4GxAHoEsggSXoAkBwBF0ABCIZIGGkjC4BBRJAnIYmJgbE9WhiYLAUiN+gCyKBYCDWRBMLAmInNDEGZiB+B8Rb0SWQQA8DasSA8GMGSPCggHwGiBcd0SWggBeIf6OJcQDxTzQxMGAFYl10QSTgzwCxDBmAvIcuRhSYAsSv0cRaGUg0zJcBEjbfgfgTA8T19lCxjwwQb9rAVQ9/AACuQzIzdG8DxAAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAWCAYAAAAinad/AAAA50lEQVR4Xu2SvwtBURiGP8mvRVYzZfIvEKvFoDCapJTVv2KzGGwMJCYTi9UiJSvJRCnx6jvXOffrXkwWnnrqnvc9dU7fPUR//nyXLby52DP2vaUKZ3AC5/Covi2LeutrEnBjrOuwa6xNWqQPqKisaWQ2QvAE87IwmMIV9MAwHNtrTZl4RjFZGJSI9+TgEKbttaYD9zIUBOGOeK4F0T3xwgMcyMKBEbzAqCwsGsTXz8hC0Cae1wIu7ZXGB5MyFMRhQH3XiA/P6vpzHoPuG+sI8Z93e0aOPB70mvgWZ5X5id/VVeUplf8Cd7C4Mf2ypyy3AAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAaCAYAAABGiCfwAAABq0lEQVR4Xu2UPShHYRSHfz7LV8JiYKJIDExKEpGMFoksPiJmExZZlEEZZJJiMaAYZFHylSSbko+FMkkWg8TvdFzO/9x7B7P/U89wz3nfe+49970H+K8U0mraRCtMPJs2mGtLLa1xMbs3RCYdo5/0jZ7SG9pC0+kmHfxZraTSIbpM5+genaI5tN6sS6CUHkEL1dEMk7uFFpJcpYln0e3vfEAaXaRP0AcMIS14pM+0y+WEUWihBxdfoB8Iv4G0W+4VQvr8Qt9pq8sFlECLrZpYMXTProlZTnxAkJvcQ18/jhToG9gW9kP3SgvzTTygxwdyoRvGfcIhDzLiYlXQvYETtDlhhaMT4Y/+F+aRWFCUAxP1ppimrz74B6S93fQQiQW37KKAC7rkgxGc+UAM8lnk4aVgo8thh274YATSAUu5u7bsQ4uF1gxDT6JMgTiKoEffIicxCmnrHb30CaEA+hR9PvGN5A98kKzQPB8kvdBfRMZbJB30Glr0nM7SK7qGiFZAh6sMAWm/TIl1OkOPabtZF4vMwTboQJ2ETv04yvA7nuQQDED/sSRJkvwXvgAjPVV6+okMiQAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAaCAYAAABLlle3AAABzklEQVR4Xu2VTShEURTHDyEiCx9FiPIRRRaSlJhSFpKFlZUopcTCRiyQlSTlcyOKhSIlKVZSJAuRZMFCsbBhQbKwEv8z5703590ZheZtmF/96p5zT3Pm3TnvDtF/Jxq2w0Qj7xmN8BLewA1jzxNa4RusgnXwA9a6KsJMFnyCo1acQtJ01qnwgF34COOtOJWk6ZZT4QHcoEbFfNSc21O5sFIKH0im1maCpOmMyoWVQXgNh5RXJE07VZ1JNYy11vxzaKJgBYyz4gy15+cIrpO7KTdk8wJlfvjDR+AJnIY7MB8eGDX7cAqewn64qvapkOTDY3TSynWr2AdfYJvK2fCwjVnrPnis9phNWKATdlNNMnwm95G9wmUVa+ZhvbVegWcUOHaGn9RFAgU37YG9Ro5ryo2cTTMFfjt+z7n2AjY4FSG4V2s+5jtyTzJzbsRfwQ+xTYGZWCQZqiCSSN7HNZIB4NtJU0IyXKHogpXWukVvgCKSxk1G3qGM5M4N9a04t2QmSa7KORUfqjWTA99htpH/NjxIuUaOjzFdxVyTpuIFOKDiHzMJb0mOuYNkYjNdFUTjJK8HDxBfo8Pu7d9RTPK+snwhhIKf1Efy1xghwh/jE5XaUf3JpDmQAAAAAElFTkSuQmCC>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAZCAYAAAAMhW+1AAAAX0lEQVR4XmNgGAXogA2I04F4DxB/BOKryJJcQPwfiN2RBZFBLRAfAWIHJIwCLjNATEDGcMAExL+AWBFZEB3sBmJVdEFk4ALEE9DENNH4DE8ZIG6ZCMRngVgbVXoU4AUAbeYRSyPvD0sAAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAaCAYAAACHD21cAAAAs0lEQVR4XmNgGHKAEYh3E4E3AXEXEPNBtDEwOAPxcSCuAeIYIHYE4lYg/g/EVUDsDcTZQNwMxL+AmAWijYGhD4iZYRwoKAbic2hiIHARmXMFmQMF6xkgBqKD1TBGCBDHI0mAgAkDxJk8aOIg4IkugAxKGSAaSQZbGMjU+I6BDI0wZ55AlyAEYM7sQZfAB0AR+5UBotEPTQ4vsGSAaPoLxNxocljBMwaIBnT8GFnRKBgFlAMAohAqqsZAuBYAAAAASUVORK5CYII=>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAaCAYAAABYQRdDAAABP0lEQVR4Xu2TPyhFYRjGX/nXNZKUie4ig9GMZJEMdjcpAxkUi8WiZJDBKHVlMCBlMSh/VkVGu4FJyiCDeJ7e93be7zvfGW3nV7/u973P+36dzvmuSIljFF45t8I4x7KE/fNhrPTAEbgKf+FjkOZ5Fu17h2OwLYxDGod+wqYo8+yJ9p3GQYoT+Co60BtlDWbhpWjPUpTlGIL38Fh0gMMx+3BANH+JsiQrcAduiw5thLFMwU1bMz90WSEXcBouig7VXdYOr2HF9sznsjhNC/yAnXBSdOjG5XzqCVuzl3l/FqdZh7u25tNw6MfWpMt+yRo8cPtCeIFn3J4fgQcPwgVXJ+ewFtVydMAv2O1qt5K9tzNXbxa98H2ulmQcPkW1uuihb7Dq6sNWL4R/TTZ4jyzj9XmArbb/jvronWUlJSX/wh8jdEjyGyzoLwAAAABJRU5ErkJggg==>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAaCAYAAADi4p8jAAACz0lEQVR4Xu2XS+hNURjFPyJK3uQ1kEIKIRMUIiWUQomSd38jJjIwkAExICkk5J1HFEp5GzAgj5lIzORNxERIrOU7p/Zd9jn/fe/9M9D91ere1jrn3P3du7+99zVr8H/SFhoDddSghAtQk5p1MFONAlpBl9WMwaLmQRehN9AW6Ar0CDoSXFfEcTWEAWqU0MN8PKl0h2aoqVyDfkK3oa6B3w96CO2x4g+dD3VRM4P+BmiRBiWsUiOB91A3NUNY3AOokwagl3l+QAPzafxJTXDT/J6n0DOrrsC7aiTwBNqmZs4w88Es1SCAOTVK/NXQZ/GU85Ze4BDosZoJcOzfoMEakJPmg++vQUBe4JnAG515awIvRmqBraHnUF8NErkH3VKTbDcf6HANAvICdwTeiswbH3gxUgucZr6wxegNrYfuQF+hnZXxb3ZB3y3SixPMB7pQg4C8wMmBtzXz+OFlpBZ4FFqiZgYXkfvmeTvJctguHM9YDQiDvWoGMOcUCDmc+e3FV1jgYjWFDtDb7FUZYV5gHw2EZebjma4BOWvF1bPXLqlpvrV8UDMCCyxbwMhVaKqa5kXlsydUDO6FzKIHDjb2R2ijBuZzf5Ca4JT5A7k4lJFS4AuLP4f9XVSQssD8Wu7LFXD/I1w0dBoSbv6EzcuTTc5u8wfyJFEGC+T0KWOzGhnjLL3AlebXcrGq4GD22gZ6BfUMMg7+XfZ+FnQsyPhr84EDAy8GC1yupsD9LwYPEs3tsznrzMfzx2ybkgW5ZgcZ+yLMwm+nM/TD/NyqnLDK+0LNCa4jPAaWwan7xbxP95nPuNgfgZfQfjXr5br53lQrXIG5ejYHj5ATrfiXHmr+5Y3UoF7mmj+4Vnj/aTVrYBN0Q82WIl+EaoHbU9gStcIdgF/WX4FNPUnNBPi37LUV/w2rhnMW32ZaDB73uIpVw1or7qlU2JuH1GzQoEGDf8IvvMubecjzhykAAAAASUVORK5CYII=>
