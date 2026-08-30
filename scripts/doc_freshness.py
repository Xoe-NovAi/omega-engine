#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Check documentation freshness — flag docs >30 days stale."""
import re
import os
from datetime import datetime

now = datetime.now()
stale = []
total = 0

for root, dirs, files in os.walk('docs'):
    dirs[:] = [d for d in dirs if d != 'archive']
    for f in files:
        if not f.endswith('.md'):
            continue
        total += 1
        path = os.path.join(root, f)
        try:
            content = open(path).read()
        except Exception:
            continue
        m = re.search(r'\*\*Date\*\*:\s(\d{4}-\d{2}-\d{2})', content)
        if m:
            try:
                age = (now - datetime.strptime(m.group(1), '%Y-%m-%d')).days
                if age > 30:
                    stale.append((path, age))
            except ValueError:
                pass

stale.sort(key=lambda x: -x[1])
print(f'\nDocs checked: {total}')
print(f'Stale (>30 days): {len(stale)}')
print()

for path, age in stale[:30]:
    icon = '🔴' if age > 60 else '⚠️ '
    print(f'  {icon} {path} ({age} days old)')

if len(stale) > 30:
    print(f'  ... and {len(stale) - 30} more')
