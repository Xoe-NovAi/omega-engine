# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Provider Configuration Data Classes
⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-07-18
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProviderConfig:
    provider: str
    priority: int
    enabled: bool = True
    description: str = ""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    endpoint: Optional[str] = None
    model_dir: Optional[str] = None
    model_overrides: dict = field(default_factory=dict)
    supported_models: list[str] = field(default_factory=list)

    # Native GGUF specific
    model_path: Optional[str] = None
    n_ctx: int = 8192
    n_ctx_max: int = 32768
    cores: list[int] = field(default_factory=list)
    n_threads: int = 4
    n_threads_batch: int = 4
    type_k: int = 8
    type_v: int = 1
    kv_cache_type: str = "f16"
    n_batch: int = 512
    n_ubatch: int = 32
    use_mmap: bool = True
    use_mlock: bool = False
    n_gpu_layers: int = 0
