#!/usr/bin/env python3
"""Check M22 SSOT: is_cloud only appears in inference.fallback_chain"""
import yaml
import sys

with open('config/providers.yaml') as f:
    data = yaml.safe_load(f)

def find_is_cloud(obj, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'is_cloud':
                if not path.startswith('inference.fallback_chain'):
                    print(f'FAIL: is_cloud found outside fallback_chain at {path}')
                    sys.exit(1)
            else:
                find_is_cloud(v, f'{path}.{k}' if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_is_cloud(v, f'{path}[{i}]')

find_is_cloud(data)
print('M22 passed: is_cloud SSOT intact')
