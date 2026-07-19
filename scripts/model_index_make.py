#!/usr/bin/env python3
"""Build Model Registry Index - called from Makefile"""
import sys
sys.path.insert(0, 'src')

from omega.model_registry import ModelRegistry

registry = ModelRegistry('config/model_registry')
registry.load_all()
registry.build_index()
print(f'Loaded {len(registry._model_cards)} models')
print(f'Loaded {len(registry._providers)} providers')
print(f'Loaded {len(registry._research_profiles)} research profiles')
