# 🔱 Ryzen 7 5700U Hardware Substrate Spec Sheet
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ HARDWARE-SUBSTRATE ⬡ 2026-07-01

## §1 Silicon Specifications

| Component | Specification | Details |
|-----------|---------------|---------|
| **CPU** | AMD Ryzen 7 5700U | Zen 2 Architecture (Lucienne), TSMC 7nm FinFET |
| **Cores / Threads** | 8 Cores / 16 Threads | SMT Enabled |
| **Clock Speed** | 1.8 GHz Base / 4.3 GHz Boost | Dynamic scaling based on thermal headroom |
| **L1 Data Cache** | 32 KB per core | 8-way associative, 64-byte line size |
| **L1 Instruction Cache** | 32 KB per core | 4-way associative, 64-byte line size |
| **L1 Total** | 64 KB per core | 512 KB total across 8 cores |
| **L2 Cache** | 512 KB per core | 8-way associative, write-back |
| **L3 Cache** | 8 MB shared | 16-way associative, **Victim Cache** architecture |
| **TDP** | 15W | Configurable TDP (cTDP) 10-25W |
| **Memory Support** | DDR4-3200 / LPDDR4-4266 | Dual-channel support |
| **ISA Extensions** | SSE4a, SSE4.1, SSE4.2, AVX2, FMA3 | No AVX-512 support |

---

## §2 Architectural Implications for AI Inference

### 2.1 L3 Victim Cache Behavior
Unlike traditional inclusive caches where L3 duplicates the contents of L1 and L2, Zen 2 uses a **victim cache** design. 
- When a cache line is evicted from L2, it is written to L3.
- L3 does not proactively mirror L1/L2.
- **Implication**: Memory access patterns must be highly sequential. Random jumps across large context windows will cause frequent L3 misses, dropping execution directly to DDR4-3200 memory bus speeds (~25.6 GB/s), which is the primary bottleneck for local LLM generation.

### 2.2 AVX2 Vector Execution
The Ryzen 5700U lacks AVX-512 but has full AVX2 support.
- AVX2 registers are 256-bit wide, allowing execution of **8 single-precision floats (32-bit)** or **16 half-precision floats (16-bit)** per instruction.
- FMA3 (Fused Multiply-Add) allows calculating $A \times B + C$ in a single clock cycle.
- **Implication**: Local quantization formats (like Q4_K_M or Q8_0) must align matrix blocks to 32-byte boundaries to maximize AVX2 register utilization.

### 2.3 Thermal & Power Constraints (15W TDP)
Running concurrent local models (e.g., an 8B reasoning model and a 1.7B speculative decoder) will quickly saturate the 15W TDP envelope, triggering thermal throttling down to base clock speeds (1.8 GHz).
- **Implication**: The engine must enforce a strict `ResourceGuard` semaphore to ensure only one model executes matrix math at any given millisecond.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: HARDWARE-SUBSTRATE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
