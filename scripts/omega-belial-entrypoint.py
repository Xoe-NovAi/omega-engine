#!/usr/bin/env python3
"""Belial Legacy Deep Mining entrypoint — invoked by Quadlet container."""

import sys
import os
import json
import anyio
import httpx

sys.path.insert(0, '/engine')
from src.omega.entity_belial import BelialMiner, LEGACY_MINES


async def run():
    miner = BelialMiner()
    total = 0
    for mine_name, mine_path in LEGACY_MINES:
        container_path = '/mines/' + mine_name.split('-')[0]
        candidates = miner.scan_mine(mine_name, mine_path)
        miner.submit_to_queue(candidates)
        total += len(candidates)
    print(f'Belial: Scan complete. {total} candidates queued.')

    api_key = os.environ.get('GOOGLE_API_KEY')
    if api_key:
        async def gemma_call(prompt):
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b:generateContent?key={api_key}'
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, json={'contents': [{'parts': [{'text': prompt}]}]})
                return resp.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response')
        report = await miner.deep_analyze(gemma_call)
        report_path = '/engine/data/mining_queue/belial_report.json'
        with open(report_path, 'w') as f:
            f.write(report)
        print(f'Belial: Deep analysis complete. Report at {report_path}')
    else:
        print('Belial: No GOOGLE_API_KEY — surface scan only.')


anyio.run(run)
