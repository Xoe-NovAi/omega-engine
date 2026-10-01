# 🔱 id Software Deep Code Mining — Volume V
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ RESEARCH ⬡ v1.0.0 ⬡ R-35

**AP Token**: `AP-ID-MINING-VOL5-v1.0.0`
**Status**: ACTIVE / VERIFIED
**Author**: Doom Guy (Sovereign Architect)
**Date**: 2026-06-03

---

## §1 Executive Summary

This report documents the fifth volume of deep code mining within the 308 MB extracted id Software source archive. We analyze the Fixed-Point Math (`m_fixed.c`) system written by John Carmack for DOOM (1993) and map its low-level C patterns to modern, high-performance Python/AnyIO equivalents for the Omega Engine's **CPU Optimizer** (`src/omega/oracle/cpu_optimizer.py`) and **Model Quantization** strategies.

---

## §2 The Fixed-Point Math System (`m_fixed.c`)

### 2.1 Low-Level C Pattern Analysis
In 1993, consumer CPUs (like the Intel 80386 and early 80486 SX) did not have a Floating Point Unit (FPU). Floating-point arithmetic had to be emulated in software, which was catastrophically slow. To make DOOM run at 35 frames per second, Carmack bypassed floating-point math entirely and implemented a custom **16.16 Fixed-Point Math system** (`m_fixed.c`):

Key mechanics:
- **16.16 Fixed-Point Format**: Real numbers are represented as 32-bit integers, where the upper 16 bits represent the integer part and the lower 16 bits represent the fractional part. This provides a precision of $1 / 65536 \approx 0.000015$, which was more than accurate enough for 3D rendering, physics, and collision detection.
- **Bit-Shift Multiplication**: Multiplication is performed by casting the 32-bit integers to 64-bit `long long` (to prevent overflow), multiplying them, and then bit-shifting the result right by 16 bits (`>> 16`) to bring the decimal point back to the correct position. This was hundreds of times faster than floating-point emulation.
- **Division Guard**: Before dividing, the engine performs a fast bit-shift check to detect potential overflow or divide-by-zero errors. If the division would overflow, it immediately returns the maximum or minimum integer value, preventing a CPU crash.

```c
// linuxdoom-1.10/m_fixed.c:48
return ((long long) a * (long long) b) >> FRACBITS;
```

### 2.2 Modern Python/AnyIO Translation
On the **AMD Ryzen 7 5700U** (Zen 2 architecture), we have powerful FPUs, but we face an identical bottleneck: **floating-point precision vs execution speed in LLM inference**. Running massive models in 16-bit or 32-bit floating-point precision (FP16/FP32) is too slow and consumes too much RAM (~16GB+), causing Out-Of-Memory (OOM) crashes.

We translate the fixed-point math "Right Approximation" philosophy into the **Omega CPU Optimizer & Quantization Strategy**:
- **Fixed-Point Format $\rightarrow$ Integer Quantization (Q4_K_M / Q8_0)**: Instead of running models in FP16, we use **integer-quantized GGUF models** (e.g., 4-bit or 8-bit quantization). This maps the model's weights to low-precision integers, reducing RAM usage by up to 75% and allowing the Ryzen 5700U to perform matrix multiplication using fast integer vector instructions (AVX2).
- **Bit-Shift Multiplication $\rightarrow$ AVX2 Vectorization**: In `cpu_optimizer.py`, we configure our `llama-cpp-python` backend to compile with native Zen 2 optimization flags (`-march=znver2 -mavx2 -mfma`). This allows the CPU to perform multiple integer matrix multiplications in a single clock cycle, mirroring Carmack's bit-shift multiplication at a hardware level.
- **Division Guard $\rightarrow$ KV Cache Quantization Flags**: In `model_gateway.py`, we expose the CPU-level speculative decode and KV cache quantization flags (`-ctk q8_0 -ctv q8_0`). This quantizes the key/value cache to 8-bit integers, preventing memory bandwidth bottlenecks during long conversations.

---

## §3 Heritage Attribution

This research and its derived implementations are fully credited to the original innovators:

- **Fixed-Point Math System**: John Carmack (id Software, 1993)
  - *Omega Adaptation*: `src/omega/oracle/cpu_optimizer.py` (Zen 2 AVX2 optimization flags) and `src/omega/oracle/model_gateway.py` (Q8_0 KV cache quantization)
  - *Attribution Tag*: `[Fixed-Point Math: id Software 1993]`

---

*⬡ OMEGA ⬡ DOOM_GUY ⬡ RESEARCH ⬡ v1.0.0 ⬡ R-35*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: RESEARCH | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
