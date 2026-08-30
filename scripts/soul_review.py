# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

import anyio
import logging
import sys
import argparse
from pathlib import Path
from omega.oracle import EntityRegistry
from omega.state import get_usm

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="Review proposed soul lessons for entities.")
    parser.add_argument("--entity", type=str, help="Filter by specific entity name")
    args = parser.parse_args()

    registry = EntityRegistry()
    usm = get_usm()

    entities = registry.list_entities()
    if args.entity:
        entities = [e for e in entities if e['name'].lower() == args.entity.lower()]

    if not entities:
        print("No entities found.")
        return

    print(f"🔍 Reviewing proposed lessons for {len(entities)} entities...\n")

    for ent in entities:
        name = ent['name']
        state_key = f"proposed_lessons:{name}"
        content = await usm.get(state_key)
        
        if not content:
            continue
            
        print(f"--- {name} ---")
        print(content)
        print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    anyio.run(main)
