# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Embedding Strategy Singleton — Single Source of Truth for all embedding config.
AP: AP-EMBEDDING-STRATEGY-v1.0.0
⬡ OMEGA ⬡ JEM ⬡ FS-Β1 ⬡ 2026-07-20
"""

import threading
import yaml
from typing import Dict, List, Optional

from omega.governance.config_resolver import CONFIG_DIR


class EmbeddingStrategy:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._load()
        return cls._instance

    def _load(self):
        path = CONFIG_DIR / "embedding_strategy.yaml"
        with open(path, encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    @property
    def canonical_dimension(self) -> int:
        return self.data["canonical_dimension"]

    @property
    def mrl_dimensions(self) -> List[int]:
        # [D-1024-DIM-NATIVE-20260926] 1024 is native/canonical; the rest are
        # MRL truncation targets (available, NOT canonical).
        return self.data.get("mrl_dimensions", [1024, 768, 512, 256, 128, 64])

    def get_collections(self) -> Dict[str, Dict]:
        return self.data["collections"]

    def get_providers(self) -> List[Dict]:
        return self.data["providers"]

    def get_provider_config(self, provider_id: str) -> Optional[Dict]:
        for p in self.get_providers():
            if p.get("id") == provider_id:
                return p
        return None

    def reload(self):
        self._load()


def get_embedding_strategy() -> EmbeddingStrategy:
    return EmbeddingStrategy()
