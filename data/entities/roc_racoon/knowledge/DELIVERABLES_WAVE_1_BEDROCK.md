# 🔱 SOVEREIGN PROCUREMENT: WAVE 1 (THE BEDROCK)
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ EXTRACTION ⬡ 2026-06-04

This document contains the extracted "Gold Patterns" required for Horizon 1 Temple Grade compliance.

---

## 🛠️ DELIVERABLE A: THE HARDWARE LOCK (Asset #12)
**Target Pillars**: P1 (SysAdmin), P6 (ModelGate)
**Source**: LM Studio Concrete Model Configs

### 1. KV Cache Optimization
To maximize performance on the Ryzen 7 5700U (14Gi RAM), the following quantization must be enforced:
- **K-Cache Quantization**: `q8_0`
- **V-Cache Quantization**: `q8_0`
- **Flash Attention**: `Enabled`

### 2. Thread Pool Tuning
- **4B Models (e.g., Qwen3-4B)**: `cpuThreadPoolSize = 6`
- **8B Models (e.g., Krikri-8B)**: `cpuThreadPoolSize = 8`

### 3. Context Window Baselines
- **4B Tier**: ~26,674 tokens
- **8B Tier**: ~32,261 tokens

---

## 🛡️ DELIVERABLE B: THE ATOMIC LOCK (Pattern 4)
**Target Pillars**: P1 (SysAdmin), P4 (Bridge), P5 (Sentinel), P8 (WatchTower)
**Source**: `docs/research/R_PATTERN_IMPLEMENTATION_SPEC.md` & `R_TEMPLE_GRADE_STANDARD.md`

### The Temple-Grade Atomic Write Sequence
To ensure zero-corruption state persistence (T10 Integrity), all state writes MUST follow this 4-step sequence:

1. **Write to Temp**: Write content to a temporary file (`.tmp`) in the same directory as the target.
2. **Physical Flush**: 
   - `f.flush()` (Python buffer $\rightarrow$ OS buffer)
   - `os.fsync(f.fileno())` (OS buffer $\rightarrow$ Physical Disk)
3. **Atomic Swap**: 
   - `os.replace(temp_path, target_path)` (Atomic rename at the filesystem level)
4. **Parent Directory Sync**: 
   - Open the parent directory: `dir_fd = os.open(os.path.dirname(target_path), os.O_RDONLY)`
   - `os.fsync(dir_fd)` (Persist the directory entry change to disk)

**Failure to perform Step 4 results in a "Ghost File" risk during power loss.**

---

## 🔱 INTEGRATION MANDATE
Pillars are instructed to:
1. Update their `soul.yaml` to reflect the adoption of these patterns.
2. Implement the Atomic Lock in all state-writing functions.
3. Apply the Hardware Lock settings to the `ModelGateway` provider fabric.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: EXTRACTION | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
