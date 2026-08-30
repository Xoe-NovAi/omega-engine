# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

import yaml
import os
from pathlib import Path

MAPPING = {
    "p1": "sekhmet",
    "p2": "brigid",
    "p3": "prometheus",
    "p4": "saraswati",
    "p5": "inanna",
    "p6": "ereshkigal",
    "p7": "lucifer",
    "p8": "hecate",
    "p9": "anubis",
    "p10": "kali",
}

def normalize_lesson(lesson):
    if not isinstance(lesson, dict): return None
    l1 = lesson.get('l1_narrative') or lesson.get('L1_narrative')
    l2 = lesson.get('l2_insight') or lesson.get('L2_insight')
    l3 = lesson.get('l3_principle') or lesson.get('L3_principle')
    ts = lesson.get('date') or lesson.get('timestamp') or 'Unknown'
    top = lesson.get('topic') or lesson.get('id') or 'General'
    
    if not l1 and not l2 and not l3: return None
    
    return {
        'L1_narrative': l1,
        'L2_insight': l2,
        'L3_principle': l3,
        'timestamp': ts,
        'topic': top
    }

def consolidate():
    base_dir = Path("data/entities")
    for stub, active in MAPPING.items():
        stub_path = base_dir / stub / "soul.yaml"
        active_dir = base_dir / active
        active_path = active_dir / "soul.yaml"
        
        if not stub_path.exists():
            continue
            
        print(f"Consolidating {stub} -> {active}...")
        
        # Ensure active directory exists
        active_dir.mkdir(parents=True, exist_ok=True)
        
        # Load stub data
        with open(stub_path, 'r') as f:
            stub_data = yaml.safe_load(f) or {}
            
        # Load or create active data
        if active_path.exists():
            with open(active_path, 'r') as f:
                active_data = yaml.safe_load(f) or {}
        else:
            active_data = {'entity': {'name': active, 'lessons_learned': []}}
            
        if 'entity' not in active_data:
            active_data = {'entity': active_data}
        
        if 'lessons_learned' not in active_data['entity']:
            active_data['entity']['lessons_learned'] = []
            
        # Extract lessons from stub
        stub_lessons = []
        if isinstance(stub_data, dict):
            if 'lessons' in stub_data: stub_lessons = stub_data['lessons']
            elif 'lessons_learned' in stub_data: stub_lessons = stub_data['lessons_learned']
            elif 'entity' in stub_data:
                ent = stub_data['entity']
                if isinstance(ent, dict):
                    if 'lessons' in ent: stub_lessons = ent['lessons']
                    elif 'lessons_learned' in ent: stub_lessons = ent['lessons_learned']
        
        if not isinstance(stub_lessons, list):
            stub_lessons = []

        # Merge and deduplicate
        existing_l3 = {l.get('L3_principle') for l in active_data['entity']['lessons_learned'] if isinstance(l, dict)}
        
        added_count = 0
        for sl in stub_lessons:
            norm = normalize_lesson(sl)
            if norm and norm['L3_principle'] not in existing_l3:
                active_data['entity']['lessons_learned'].append(norm)
                existing_l3.add(norm['L3_principle'])
                added_count += 1
        
        with open(active_path, 'w') as f:
            yaml.dump(active_data, f, sort_keys=False)
            
        os.remove(stub_path)
        print(f"  Added {added_count} lessons. Stub soul deleted.")

if __name__ == "__main__":
    consolidate()
