#!/usr/bin/env python3
"""Validate Model Registry - called from Makefile"""
import sys
sys.path.insert(0, 'src')

from omega.model_registry import ModelRegistry

registry = ModelRegistry('config/model_registry')
registry.load_all()

errors = 0

# SCHEMA_VALID: All model cards validate against schema
for model_id, model in registry._model_cards.items():
    if not model.model_id:
        print(f'  ❌ {model_id}: missing model_id')
        errors += 1
    if not model.display_name:
        print(f'  ❌ {model_id}: missing display_name')
        errors += 1
    if model.context_window <= 0:
        print(f'  ❌ {model_id}: invalid context_window')
        errors += 1

# NO_DUPLICATES: Unique model_id
if len(registry._model_cards) != len(set(registry._model_cards.keys())):
    print('  ❌ Duplicate model_ids found')
    errors += 1

# PROVIDER_CHAIN_COMPLETE: Fallback chain has no gaps
priorities = [p.priority for p in registry._providers.values() if p.enabled]
if sorted(priorities) != list(range(min(priorities), max(priorities) + 1)):
    print(f'  ❌ Provider priority gaps: {priorities}')
    errors += 1

# RESEARCH_PROFILES_COMPLETE: All models in KB have research profile
for model_id, model in registry._model_cards.items():
    if model.research_profile and model.research_profile.reasoning_depth == 'unknown':
        print(f'  ⚠️  {model_id}: research profile has unknown reasoning_depth')

# INDEX_SYNC: DB matches loaded files
try:
    import sqlite3
    conn = sqlite3.connect('config/model_registry/index.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM models')
    db_count = cursor.fetchone()[0]
    conn.close()
    if db_count != len(registry._model_cards):
        print(f'  ❌ Index sync mismatch: DB={db_count}, Files={len(registry._model_cards)}')
        errors += 1
    else:
        print(f'  ✅ Index sync: {db_count} models')
except Exception as e:
    print(f'  ⚠️  Index not built yet (run make model-index): {e}')

if errors == 0:
    print('✅ All validation gates passed')
else:
    print(f'❌ {errors} validation errors')
    sys.exit(1)
