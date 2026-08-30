#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Model Registry Index Builder
⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-07-18
"""

import sys
sys.path.insert(0, 'src')

from omega.model_registry import ModelRegistry

def main():
    registry = ModelRegistry('config/model_registry')
    registry.load_all()
    registry.build_index()
    print(f"Loaded {len(registry._model_cards)} models")
    print(f"Loaded {len(registry._providers)} providers")
    print(f"Loaded {len(registry._research_profiles)} research profiles")

if __name__ == "__main__":
    main()