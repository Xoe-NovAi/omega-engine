#!/usr/bin/env python3
"""Model Registry validation script - called from Makefile"""
import sys
sys.path.insert(0, 'src')

from omega.model_registry import ModelRegistry
from omega.model_registry.models import Parameters, Capabilities
import sqlite3

registry = ModelRegistry('config/model_registry')
registry.load_all()
errors = 0

# SCHEMA_VALID: All model cards validate against schema
for model_id, model in registry._model_cards.items():
    if not model.model_id:
        print(f'  ERROR: {model_id}: missing model_id')
        errors += 1
    if not model.display_name:
        print(f'  ERROR: {model_id}: missing display_name')
        errors += 1
    if model.context_window <= 0:
        print(f'  ERROR: {model_id}: invalid context_window')
        errors += 1
    if model.provider not in registry._providers:
        print(f'  ERROR: {model_id}: provider {model.provider} not in registry')
        errors += 1
    # T1: Verify parameters field exists
    if not hasattr(model, 'parameters') or model.parameters is None:
        print(f'  ERROR: {model_id}: missing parameters field')
        errors += 1
    elif not isinstance(model.parameters, Parameters):
        print(f'  ERROR: {model_id}: parameters is not Parameters dataclass')
        errors += 1
    elif model.parameters.temperature <= 0:
        print(f'  ERROR: {model_id}: invalid parameters.temperature={model.parameters.temperature}')
        errors += 1
    # T3: Verify extended capability fields
    if not hasattr(model.capabilities, 'code_execution'):
        print(f'  ERROR: {model_id}: missing capabilities.code_execution')
        errors += 1
    if not hasattr(model.capabilities, 'parallel_search'):
        print(f'  ERROR: {model_id}: missing capabilities.parallel_search')
        errors += 1
    if not hasattr(model.capabilities, 'workspace_integration'):
        print(f'  ERROR: {model_id}: missing capabilities.workspace_integration')
        errors += 1
    # P1: Verify benchmark_sources
    if not hasattr(model, 'benchmark_sources') or model.benchmark_sources is None:
        print(f'  ERROR: {model_id}: missing benchmark_sources field')
        errors += 1
    # Verify schema version >= 1.1.0
    if model.schema_version < "1.1.0":
        print(f'  WARNING: {model_id}: schema_version={model.schema_version} (expected >=1.1.0)')

# NO_DUPLICATES: Check for duplicate model_ids
seen = set()
for model_id in registry._model_cards:
    if model_id in seen:
        print(f'  ERROR: Duplicate model_id: {model_id}')
        errors += 1
    seen.add(model_id)

# PROVIDER_CHAIN_COMPLETE: Verify priority chain 0-99 (no gaps)
priorities = sorted([p.priority for p in registry._providers.values()])
expected = list(range(len(priorities)))
if priorities != expected:
    print(f'  ERROR: Provider priority chain incomplete: {priorities} (expected {expected})')
    errors += 1
else:
    print(f'  Provider priority chain: {priorities}')

# INDEX_SYNC: Verify DB matches loaded models
conn = sqlite3.connect('config/model_registry/index.sqlite')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM models')
db_count = cursor.fetchone()[0]
# Verify new columns exist
cursor.execute("PRAGMA table_info(models)")
columns = {row[1] for row in cursor.fetchall()}
conn.close()

required_columns = {'temperature', 'top_p', 'top_k', 'repetition_penalty',
                    'max_tokens', 'code_execution', 'parallel_search',
                    'workspace_integration'}
missing_columns = required_columns - columns
if missing_columns:
    print(f'  ERROR: Index missing columns: {missing_columns}')
    errors += 1
else:
    print(f'  Index has all required columns ({len(columns)} total)')

if db_count != len(registry._model_cards):
    print(f'  ERROR: Index sync mismatch: DB={db_count}, Files={len(registry._model_cards)}')
    errors += 1
else:
    print(f'  Index sync: {db_count} models')

if errors == 0:
    print('All validation gates passed')
    sys.exit(0)
else:
    print(f'{errors} validation errors')
    sys.exit(1)
