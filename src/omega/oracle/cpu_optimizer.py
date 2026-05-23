"""Zen 2 CPU Optimizer — llama.cpp compilation flags, KV cache, speculative decoding tuning.

AP: AP-CPU-OPTIMIZER-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | MODEL: DEEPSEEK-V4-FLASH | CONTEXT: CPU-OPTIMIZATION]

Target: AMD Ryzen 7 5700U (Zen 2, 8C/16T, 14Gi RAM)

Architecture-specific optimizations:
  - AVX2, FMA3, F16C — all 256-bit (no AVX-512)
  - L2: 512KB/core, L3: 8MB shared across 2 CCX (4 cores each)
  - Core pinning: compute on cores 0,2,4,6; I/O on SMT (1,3,5,7,9,11)
  - NUMA: single die, no NUMA penalty

Compilation flags for llama.cpp on Zen 2:
  CMAKE_FLAGS="-DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON \
    -DLLAMA_NO_AVX512=ON -DLLAMA_BLAS=OFF -DLLAMA_CUDA=OFF -DLLAMA_METAL=OFF \
    -DCMAKE_C_FLAGS='-march=znver2' -DCMAKE_CXX_FLAGS='-march=znver2'"

KV cache quantization (llama-server flags):
  -ctk q8_0   — key cache in 8-bit (reduces memory ~2x vs f16)
  -ctv q8_0   — value cache in 8-bit
  -mli 1      — mul matq input (enables Q8_0 input optimization)

Speculative decoding (Oracle already implements this):
  Draft: Nova (qwen3-1.7b-270m, always-on, ~300MB)
  Target: Pillar Keeper (loaded on demand)
  Acceptance: heuristic-based confidence check
  
  Can be enhanced with dynamic speculation:
  - Track acceptance rate per entity
  - Adjust speculation length (target tokens per draft)
  - Switch draft strategy if acceptance drops below 50%
"""

import logging
import platform
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Zen 2 Constants ──────────────────────────────────────────────────────
ZEN2_L1_CACHE = 32  # KB per core
ZEN2_L2_CACHE = 512  # KB per core
ZEN2_L3_CACHE = 8192  # KB shared (2x 4MB CCX)
ZEN2_CORES = 8
ZEN2_THREADS = 16
ZEN2_COMPUTE_CORES = [0, 2, 4, 6]
ZEN2_IO_THREADS = [1, 3, 5, 7, 9, 11]
ZEN2_RECOMMENDED_THREADS = 6

# Expected RAM breakdown on 14Gi system
RAM_TOTAL_MB = 14 * 1024  # ~14336
RAM_OS_OVERHEAD_MB = 2000
RAM_AVAILABLE_AI_MB = RAM_TOTAL_MB - RAM_OS_OVERHEAD_MB  # ~12336
RAM_NOVA_RESIDENT_MB = 300

# Model RAM with KV cache at various context lengths
KV_CACHE_BYTES_PER_TOKEN = {
    "f16": 4,  # 2 bytes key + 2 bytes value per layer * 2 (K+V)
    "q8_0": 2,  # 1 byte key + 1 byte value per layer
    "q4_0": 1,  # 0.5 byte key + 0.5 byte value per layer
}

# Speculative decoding defaults
DEFAULT_SPEC_ACCEPTANCE_THRESHOLD = 0.4  # Nova confidence threshold
MIN_DRAFT_TOKENS = 1
MAX_DRAFT_TOKENS = 5
TARGET_ACCEPTANCE_RATE = 0.6  # Aim for 60% draft acceptance


@dataclass
class CompilationFlags:
    """llama.cpp compilation flags for Zen 2 optimization."""
    march: str = "znver2"
    avx2: bool = True
    fma: bool = True
    f16c: bool = True
    no_avx512: bool = True
    blas: bool = False
    cuda: bool = False
    metal: bool = False

    def to_cmake_flags(self) -> List[str]:
        flags = [
            f"-DLLAMA_AVX2={'ON' if self.avx2 else 'OFF'}",
            f"-DLLAMA_FMA={'ON' if self.fma else 'OFF'}",
            f"-DLLAMA_F16C={'ON' if self.f16c else 'OFF'}",
            f"-DLLAMA_NO_AVX512={'ON' if self.no_avx512 else 'OFF'}",
            f"-DLLAMA_BLAS={'ON' if self.blas else 'OFF'}",
            f"-DLLAMA_CUDA={'ON' if self.cuda else 'OFF'}",
            f"-DLLAMA_METAL={'ON' if self.metal else 'OFF'}",
            f"-DCMAKE_C_FLAGS='-march={self.march}'",
            f"-DCMAKE_CXX_FLAGS='-march={self.march}'",
        ]
        return flags

    def to_bash_export(self) -> str:
        flags = " ".join(self.to_cmake_flags())
        return (
            f"export LLAMA_AVX2={'ON' if self.avx2 else 'OFF'}\n"
            f"export LLAMA_FMA={'ON' if self.fma else 'OFF'}\n"
            f"export LLAMA_F16C={'ON' if self.f16c else 'OFF'}\n"
            f"export LLAMA_NO_AVX512={'ON' if self.no_avx512 else 'OFF'}\n"
            f"cmake -B build {flags}"
        )


@dataclass
class KVCacheConfig:
    """KV cache quantization configuration for llama-server."""
    key_cache_type: str = "q8_0"   # q8_0, q4_0, f16
    value_cache_type: str = "q8_0" # q8_0, q4_0, f16
    mul_matq_input: bool = True     # Enable Q8_0 input optimization

    def to_llama_server_flags(self) -> List[str]:
        flags = [
            "-ctk", self.key_cache_type,
            "-ctv", self.value_cache_type,
        ]
        if self.mul_matq_input:
            flags.extend(["-mli", "1"])
        return flags


@dataclass
class SpeculativeDecodeConfig:
    """Configuration for the speculative decoder (Nova → Pillar Keeper)."""
    draft_model: str = "qwen3-1.7b"
    target_acceptance_rate: float = TARGET_ACCEPTANCE_RATE
    min_draft_tokens: int = MIN_DRAFT_TOKENS
    max_draft_tokens: int = MAX_DRAFT_TOKENS
    acceptance_threshold: float = DEFAULT_SPEC_ACCEPTANCE_THRESHOLD

    # Adaptive tuning (updated during runtime)
    entity_acceptance_rates: Dict[str, float] = field(default_factory=dict)
    total_attempts: int = 0
    total_accepted: int = 0


class Zen2Optimizer:
    """Comprehensive Zen 2 optimization for the Omega stack.

    Provides:
      - Compilation flags for llama.cpp targeting Zen 2
      - KV cache quantization recommendations based on available RAM
      - Speculative decoding acceptance tracking and tuning
      - Thread pool and batch size recommendations
      - Memory pressure monitoring
    """

    def __init__(self):
        self.spec_decode = SpeculativeDecodeConfig()
        self.kv_cache = KVCacheConfig()
        self._memory_log: List[Dict[str, Any]] = []

    # ── Compilation ────────────────────────────────────────────────────

    def get_compilation_flags(self) -> CompilationFlags:
        """Get recommended llama.cpp compilation flags for Zen 2."""
        return CompilationFlags(
            march="znver2",
            avx2=True,
            fma=True,
            f16c=True,
            no_avx512=True,
            blas=False,
            cuda=False,
            metal=False,
        )

    def get_build_instructions(self) -> str:
        """Get full build instructions for llama.cpp on Zen 2."""
        flags = self.get_compilation_flags()
        return (
            "git clone https://github.com/ggerganov/llama.cpp\n"
            "cd llama.cpp\n"
            f"cmake -B build {' '.join(flags.to_cmake_flags())}\n"
            "cmake --build build --config Release -j$(nproc)\n"
            "# Install binaries:\n"
            "cp build/bin/llama-server /home/arcana-novai/.local/bin/\n"
            "cp build/bin/llama-cli /home/arcana-novai/.local/bin/\n\n"
            "# Environment variables for runtime:\n"
            "export OMP_NUM_THREADS=6\n"
            "export OMP_PROC_BIND=close\n"
            "export OMP_PLACES=cores\n"
            "export OPENBLAS_CORETYPE=ZEN\n"
            "export LLAMA_CPU_HINT=1  # AMD optimization hint"
        )

    # ── KV Cache ───────────────────────────────────────────────────────

    def recommend_kv_cache(
        self,
        model_size_b: float,
        context_window: int,
        layers: int = 32,
        num_heads: int = 32,
        head_dim: int = 128,
        available_ram_mb: Optional[int] = None,
    ) -> KVCacheConfig:
        """Recommend KV cache quantization based on available RAM and model.

        Formula: KV_cache_size = 2 * layers * num_heads * head_dim * context_window * bytes_per_element

        Args:
            model_size_b: Model size in billions of parameters
            context_window: Maximum context length
            layers: Number of transformer layers
            num_heads: Number of attention heads
            head_dim: Dimension per head
            available_ram_mb: Available RAM (default: 12Gi minus estimated model load)

        Returns:
            KVCacheConfig optimized for available RAM
        """
        model_ram_estimate_mb = model_size_b * 700  # ~700MB per billion params at Q4
        if available_ram_mb is None:
            available_ram_mb = RAM_AVAILABLE_AI_MB

        remaining_ram_mb = available_ram_mb - model_ram_estimate_mb - RAM_NOVA_RESIDENT_MB

        # KV cache size per token (bytes) = 2 * layers * num_heads * head_dim * 2 (K+V)
        kv_per_token_bytes = 2 * layers * num_heads * head_dim * 2  # *2 for both K and V
        kv_full_context_mb = (kv_per_token_bytes * context_window) / (1024 * 1024)

        # f16: full precision
        f16_total_mb = kv_full_context_mb * 2
        # q8_0: half precision
        q8_0_total_mb = kv_full_context_mb
        # q4_0: quarter precision
        q4_0_total_mb = kv_full_context_mb * 0.5

        logger.info(
            f"KV cache analysis for {model_size_b}B model @ {context_window} ctx:\n"
            f"  f16:  {f16_total_mb:.0f} MB  (remaining RAM: {remaining_ram_mb:.0f} MB)\n"
            f"  q8_0: {q8_0_total_mb:.0f} MB  (remaining RAM: {remaining_ram_mb:.0f} MB)\n"
            f"  q4_0: {q4_0_total_mb:.0f} MB  (remaining RAM: {remaining_ram_mb:.0f} MB)"
        )

        if remaining_ram_mb > f16_total_mb * 2:
            return KVCacheConfig(key_cache_type="f16", value_cache_type="f16")
        elif remaining_ram_mb > q8_0_total_mb * 1.5:
            return KVCacheConfig(key_cache_type="q8_0", value_cache_type="q8_0")
        elif remaining_ram_mb > q4_0_total_mb * 1.5:
            return KVCacheConfig(key_cache_type="q4_0", value_cache_type="q4_0")
        else:
            logger.warning(f"Limited RAM: {remaining_ram_mb:.0f}MB for KV cache of {context_window} tokens")
            # Need to reduce context or use aggressive quantization
            return KVCacheConfig(key_cache_type="q4_0", value_cache_type="q4_0")

    def get_kv_cache_flags(self) -> List[str]:
        """Get llama-server CLI flags for configured KV cache quantization."""
        return self.kv_cache.to_llama_server_flags()

    # ── Speculative Decoding ──────────────────────────────────────────

    def record_speculative_attempt(self, entity_name: str, accepted: bool) -> None:
        """Record a speculative decoding attempt for acceptance tracking.

        Args:
            entity_name: The entity that was the target
            accepted: Whether the draft was accepted
        """
        self.spec_decode.total_attempts += 1
        if accepted:
            self.spec_decode.total_accepted += 1

        rate = self.spec_decode.entity_acceptance_rates.get(entity_name, 0.5)
        # Exponential moving average
        alpha = 0.3
        new_rate = rate * (1 - alpha) + (1.0 if accepted else 0.0) * alpha
        self.spec_decode.entity_acceptance_rates[entity_name] = new_rate

    def get_speculative_acceptance_rate(self, entity_name: Optional[str] = None) -> float:
        """Get the current speculative decoding acceptance rate.

        Args:
            entity_name: If provided, get entity-specific rate, else overall

        Returns:
            Acceptance rate 0.0-1.0
        """
        if entity_name and entity_name in self.spec_decode.entity_acceptance_rates:
            return self.spec_decode.entity_acceptance_rates[entity_name]

        if self.spec_decode.total_attempts == 0:
            return 0.0
        return self.spec_decode.total_accepted / self.spec_decode.total_attempts

    def suggest_speculation_length(self, entity_name: Optional[str] = None) -> int:
        """Suggest the number of draft tokens for speculative decoding.

        Adaptive: if acceptance rate is high, speculate more tokens.
        If low, be conservative.

        Args:
            entity_name: Optional entity for history-based tuning

        Returns:
            Number of draft tokens to generate
        """
        rate = self.get_speculative_acceptance_rate(entity_name)
        if rate >= 0.8:
            return MAX_DRAFT_TOKENS
        elif rate >= 0.6:
            return 3
        elif rate >= 0.4:
            return 2
        else:
            return MIN_DRAFT_TOKENS

    # ── Thread Pool ────────────────────────────────────────────────────

    def get_recommended_threads(self, model_size_b: Optional[float] = None) -> int:
        """Recommend thread count for model inference.

        On Zen 2, 6 threads is optimal for most models:
        - Uses 3 of 4 CCX cores (leaves 1 for OS + Nova)
        - Avoids SMT contention on compute-bound workloads
        - Scales well up to 8B param models

        For tiny models (< 1B), 4 threads is sufficient.

        Args:
            model_size_b: Model size in billions of parameters

        Returns:
            Recommended thread count
        """
        if model_size_b and model_size_b < 1.0:
            return 4
        return ZEN2_RECOMMENDED_THREADS

    def get_recommended_batch_sizes(self, model_size_b: float) -> Dict[str, int]:
        """Recommend batch sizes for llama-server based on model size.

        Zen 2 has 512KB L2/core — batch processing should fit in L2.

        Args:
            model_size_b: Model size in billions

        Returns:
            Dict with 'batch_size' and 'ubatch_size'
        """
        if model_size_b < 1.0:
            return {"batch_size": 512, "ubatch_size": 64}
        elif model_size_b < 3.0:
            return {"batch_size": 256, "ubatch_size": 32}
        elif model_size_b < 7.0:
            return {"batch_size": 128, "ubatch_size": 32}
        else:
            return {"batch_size": 64, "ubatch_size": 16}

    # ── Memory Monitoring ──────────────────────────────────────────────

    async def get_memory_pressure(self) -> Dict[str, Any]:
        """Check current memory pressure.

        Returns:
            Dict with available_mb, pressure_level, recommendations
        """
        pressure = {
            "available_mb": 0,
            "total_mb": RAM_TOTAL_MB,
            "pressure_level": "unknown",
            "can_load_model": False,
            "can_keep_nova": True,
            "kv_recommendation": "q8_0",
        }

        try:
            import anyio
            result = await anyio.run_process(
                ["awk", "/MemAvailable/{print $2}", "/proc/meminfo"],
                capture_output=True,
                check=False,
            )
            available_kb = int(result.stdout.decode().strip())
            pressure["available_mb"] = available_kb // 1024
        except Exception:
            pressure["available_mb"] = RAM_AVAILABLE_AI_MB

        avail = pressure["available_mb"]
        if avail > 8000:
            pressure["pressure_level"] = "low"
            pressure["can_load_model"] = True
            pressure["kv_recommendation"] = "f16"
        elif avail > 4000:
            pressure["pressure_level"] = "moderate"
            pressure["can_load_model"] = True
            pressure["kv_recommendation"] = "q8_0"
        elif avail > 2000:
            pressure["pressure_level"] = "high"
            pressure["can_load_model"] = avail > 3000
            pressure["kv_recommendation"] = "q4_0"
            pressure["can_keep_nova"] = avail > 500
        else:
            pressure["pressure_level"] = "critical"
            pressure["can_load_model"] = False
            pressure["kv_recommendation"] = "q4_0"
            pressure["can_keep_nova"] = False

        self._memory_log.append({
            "timestamp": time.time(),
            "available_mb": avail,
            "pressure_level": pressure["pressure_level"],
        })
        self._memory_log = self._memory_log[-100:]

        return pressure

    def estimate_model_ram(
        self,
        model_size_b: float,
        quantization: str = "q4_k_m",
        context_window: int = 8192,
        kv_quant: str = "q8_0",
    ) -> Dict[str, float]:
        """Estimate RAM usage for a model with KV cache.

        Args:
            model_size_b: Model parameter count in billions
            quantization: GGUF quantization type
            context_window: Max context in tokens
            kv_quant: KV cache quantization (f16, q8_0, q4_0)

        Returns:
            Dict with model_mb, kv_cache_mb, total_mb
        """
        # Model RAM: rough estimates per quantization
        quant_factors = {
            "q2_k": 300, "q3_k_m": 400, "q4_0": 450, "q4_k_m": 500,
            "q5_k_m": 600, "q6_k": 700, "q8_0": 800, "f16": 1400,
        }
        factor = quant_factors.get(quantization, 500)
        model_mb = model_size_b * factor

        # KV cache: ~2 bytes per token per parameter (for K+V at q8_0)
        kv_bytes_per_b_param = 2 * context_window * (model_size_b / 8)  # rough
        kv_scale = {"f16": 2.0, "q8_0": 1.0, "q4_0": 0.5}
        kv_mb = kv_bytes_per_b_param * kv_scale.get(kv_quant, 1.0) / (1024 * 1024)

        return {
            "model_mb": round(model_mb, 0),
            "kv_cache_mb": round(kv_mb, 0),
            "total_mb": round(model_mb + kv_mb, 0),
            "fits_in_ram": (model_mb + kv_mb + RAM_NOVA_RESIDENT_MB) < RAM_AVAILABLE_AI_MB,
        }

    # ── Diagnostics ────────────────────────────────────────────────────

    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU architecture information."""
        info: Dict[str, Any] = {
            "architecture": platform.machine(),
            "processor": platform.processor(),
        }

        try:
            with open("/proc/cpuinfo") as f:
                text = f.read()

            # Model name
            m = re.search(r"model name\s+:\s+(.+)", text)
            if m:
                info["model_name"] = m.group(1)

            # Core count
            cores = text.count("processor")
            info["logical_cores"] = cores

            # Flags
            m = re.search(r"flags\s+:\s+(.+)", text)
            if m:
                flags = m.group(1).split()
                info["has_avx2"] = "avx2" in flags
                info["has_avx512"] = "avx512f" in flags
                info["has_fma"] = "fma" in flags
                info["has_f16c"] = "f16c" in flags
                info["has_sse4_2"] = "sse4_2" in flags

            # AMD specific
            info["is_amd"] = "AMD" in text
            info["is_intel"] = "GenuineIntel" in text
            info["is_zen"] = "Ryzen 7" in text or "AMD Ryzen" in text

        except Exception as e:
            info["error"] = str(e)

        return info

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all optimization recommendations."""
        cpu_info = self.get_cpu_info()
        compilation = self.get_compilation_flags()

        return {
            "cpu": {
                "model": cpu_info.get("model_name", "Unknown"),
                "has_avx2": cpu_info.get("has_avx2", False),
                "has_avx512": cpu_info.get("has_avx512", False),
                "has_fma": cpu_info.get("has_fma", False),
                "recommended_threads": ZEN2_RECOMMENDED_THREADS,
                "compute_cores": ZEN2_COMPUTE_CORES,
                "io_threads": ZEN2_IO_THREADS,
                "is_optimal_for_local_ai": (
                    cpu_info.get("has_avx2", False) and
                    not cpu_info.get("has_avx512", False)  # no wasted AVX-512 codegen
                ),
            },
            "compilation": {
                "march": compilation.march,
                "cmake_flags": compilation.to_cmake_flags(),
            },
            "kv_cache": {
                "key_type": self.kv_cache.key_cache_type,
                "value_type": self.kv_cache.value_cache_type,
                "memory_saving_vs_f16": self._kv_memory_saving(),
            },
            "speculative_decoding": {
                "draft_model": self.spec_decode.draft_model,
                "overall_acceptance_rate": round(
                    self.get_speculative_acceptance_rate(), 3
                ),
                "entity_rates": self.spec_decode.entity_acceptance_rates,
                "suggested_draft_tokens": self.suggest_speculation_length(),
            },
            "memory": {
                "total_mb": RAM_TOTAL_MB,
                "available_ai_mb": RAM_AVAILABLE_AI_MB,
                "nova_resident_mb": RAM_NOVA_RESIDENT_MB,
            },
        }

    def _kv_memory_saving(self) -> float:
        scale = {"f16": 1.0, "q8_0": 0.5, "q4_0": 0.25}
        current = scale.get(self.kv_cache.key_cache_type, 1.0)
        return 1.0 - current  # 0.0 = no saving, 0.5 = 50% saving, etc.

    def get_environment_variables(self) -> Dict[str, str]:
        """Get recommended environment variables for Zen 2 optimization."""
        return {
            "OMP_NUM_THREADS": str(ZEN2_RECOMMENDED_THREADS),
            "OMP_PROC_BIND": "close",
            "OMP_PLACES": "cores",
            "OPENBLAS_CORETYPE": "ZEN",
            "LLAMA_CPU_HINT": "1",
        }
