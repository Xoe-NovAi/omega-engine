#!/usr/bin/env python3
"""
Retroactive Verification Audit — Uses v1.0 verifier logic to audit historical subagent completions.
Outputs CSV + JSONL with all specified columns.
"""

import json
import sqlite3
import csv
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

# Paths
TASK_REGISTRY_PATH = Path("data/coordination/TASK_REGISTRY.json")
OPENCODE_DB_PATH = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

# Verification logic (v1.0 - matches production verifier)
VERIFICATION_SQL = """
WITH child_session AS (
  SELECT 
    s.id AS session_id,
    s.parent_id,
    s.title,
    s.agent,
    s.time_updated,
    s.time_archived,
    m.id AS last_msg_id,
    m.data AS last_msg_data,
    json_extract(m.data, '$.finish') AS finish_reason
  FROM session s
  LEFT JOIN message m ON m.session_id = s.id
  WHERE s.id = ?
  ORDER BY m.time_created DESC
  LIMIT 1
),
tool_errors AS (
  SELECT COUNT(*) AS error_count
  FROM part p
  WHERE p.session_id = ?
    AND json_extract(p.data, '$.type') = 'tool'
    AND json_extract(p.data, '$.state.status') = 'error'
),
silent_failures AS (
  SELECT COUNT(*) AS failure_count
  FROM part p
  WHERE p.session_id = ?
    AND json_extract(p.data, '$.type') = 'tool'
    AND json_extract(p.data, '$.state.status') = 'completed'
    AND (
      -- Actual HTTP 504 errors
      json_extract(p.data, '$.state.output') LIKE '%"status":504%'
      OR json_extract(p.data, '$.state.output') LIKE '%"statusCode":504%'
      OR json_extract(p.data, '$.state.output') LIKE '%HTTP/1.1 504%'
      OR json_extract(p.data, '$.state.output') LIKE '%HTTP/2 504%'
      -- Actual timeout errors (not just the word "timeout")
      OR json_extract(p.data, '$.state.output') LIKE '%"error":"timeout"%'
      OR json_extract(p.data, '$.state.output') LIKE '%"error":"ETIMEDOUT"%'
      OR json_extract(p.data, '$.state.output') LIKE '%"code":"ETIMEDOUT"%'
      OR json_extract(p.data, '$.state.output') LIKE '%TimeoutError%'
      OR json_extract(p.data, '$.state.output') LIKE '%asyncio.TimeoutError%'
      -- Connection refused
      OR json_extract(p.data, '$.state.output') LIKE '%"error":"ECONNREFUSED"%'
      OR json_extract(p.data, '$.state.output') LIKE '%Connection refused%'
      OR json_extract(p.data, '$.state.output') LIKE '%ECONNREFUSED%'
    )
),
result_data AS (
  SELECT 
    json_extract(m.data, '$.tokens.total') AS total_tokens,
    json_extract(m.data, '$.cost') AS cost,
    m.data AS full_message
  FROM message m
  WHERE m.session_id = ?
    AND json_extract(m.data, '$.role') = 'assistant'
  ORDER BY m.time_created DESC
  LIMIT 1
),
genealogy_check AS (
  SELECT 
    CASE 
      WHEN s.parent_id IS NULL THEN 1
      WHEN EXISTS (SELECT 1 FROM session WHERE id = s.parent_id) THEN 1
      ELSE 0
    END AS genealogy_valid
  FROM session s
  WHERE s.id = ?
)
SELECT 
  cs.session_id,
  cs.parent_id,
  cs.title,
  cs.agent,
  cs.time_updated,
  cs.time_archived,
  cs.finish_reason,
  te.error_count,
  sf.failure_count AS silent_failure_count,
  rd.total_tokens,
  rd.full_message IS NOT NULL AS has_result_data,
  gc.genealogy_valid
FROM child_session cs
CROSS JOIN tool_errors te
CROSS JOIN silent_failures sf
CROSS JOIN result_data rd
CROSS JOIN genealogy_check gc;
"""

def classify_failure(result: Dict) -> str:
    """Classify the failure category for a verification result."""
    if result.get('error_count', 0) > 0:
        return 'tool_error'
    if result.get('silent_failure_count', 0) > 0:
        return 'silent_failure'
    if result.get('finish_reason') == 'length':
        return 'token_limit'
    if result.get('finish_reason') == 'content_filter':
        return 'content_filter'
    if not result.get('has_result_data', False):
        return 'no_result_data'
    if not result.get('genealogy_valid', False):
        return 'genealogy_broken'
    if result.get('time_archived') is not None and result.get('time_archived', 0) > 0:
        return 'archived_stale'
    if result.get('finish_reason') not in ('tool-calls', 'stop', 'function_call', 'error', 'length', 'content_filter'):
        return 'unknown_finish_reason'
    return 'unknown'

def run_verification(session_id: str, db_path: Path) -> Dict:
    """Run verification for a single session using the v1.0 SQL."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5.0)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(VERIFICATION_SQL, (session_id,) * 5)
        row = cursor.fetchone()
        if not row:
            return {
                'session_id': session_id,
                'VERIFIED_COMPLETE': 0,
                'error': 'No data returned from DB'
            }
        result = dict(row)
        
        # Compute verification flags
        result['not_archived'] = result.get('time_archived') is None or result.get('time_archived', 0) == 0
        result['clean_finish'] = result.get('finish_reason') in ('tool-calls', 'stop', 'function_call')
        result['no_hard_failure'] = result.get('finish_reason') not in ('error', 'content_filter')
        result['zero_tool_errors'] = result.get('error_count', 0) == 0
        result['zero_silent_failures'] = result.get('silent_failure_count', 0) == 0
        result['has_token_data'] = (result.get('total_tokens', 0) or 0) > 0
        result['has_result_data'] = result.get('has_result_data', False)
        
        # Overall verification
        result['VERIFIED_COMPLETE'] = int(
            result['not_archived']
            and result['clean_finish']
            and result['zero_tool_errors']
            and result['zero_silent_failures']
            and result['has_result_data']
            and result['genealogy_valid']
        )
        
        return result
    finally:
        conn.close()

def main():
    print("🔱 Retroactive Verification Audit — v1.0 Verifier")
    print(f"OpenCode DB: {OPENCODE_DB_PATH}")
    print(f"Task Registry: {TASK_REGISTRY_PATH}")
    
    # Load task registry
    with open(TASK_REGISTRY_PATH) as f:
        registry = json.load(f)
    
    tasks = registry.get('tasks', [])
    print(f"Loaded {len(tasks)} tasks from registry")
    
    # Filter to last 30 days
    cutoff = datetime.now(timezone.utc).timestamp() - (30 * 86400)
    recent_tasks = []
    for task in tasks:
        try:
            created = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
            if created.timestamp() >= cutoff:
                recent_tasks.append(task)
        except:
            pass
    
    print(f"Tasks in last 30 days: {len(recent_tasks)}")
    
    # Run verification for each task
    results = []
    for task in recent_tasks:
        task_id = task['task_id']
        entity = task.get('entity', 'unknown')
        agent = task.get('subagent_type', 'unknown')
        
        session_id = task_id
        
        print(f"Verifying {session_id} ({entity}/{agent})...")
        result = run_verification(session_id, OPENCODE_DB_PATH)
        result['entity'] = entity
        result['agent'] = agent
        result['task_id'] = task_id
        
        # Classify failure
        if result.get('VERIFIED_COMPLETE') == 1:
            result['failure_category'] = ''
        else:
            result['failure_category'] = classify_failure(result)
        
        result['verification_timestamp'] = int(datetime.now(timezone.utc).timestamp() * 1000)
        result['verifier_version'] = '1.0.0'
        
        results.append(result)
    
    # Output CSV
    csv_path = Path("data/coordination/RETROACTIVE_VERIFICATION_AUDIT_20260831.csv")
    jsonl_path = Path("data/coordination/RETROACTIVE_VERIFICATION_AUDIT_20260831.jsonl")
    
    csv_columns = [
        'session_id', 'parent_session_id', 'entity', 'agent', 'finish_reason',
        'tool_error_count', 'silent_failure_count', 'total_tokens', 'has_result_data',
        'genealogy_valid', 'verified_complete', 'failure_category',
        'verification_timestamp', 'verifier_version'
    ]
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        for r in results:
            row = {col: r.get(col, '') for col in csv_columns}
            writer.writerow(row)
    
    # Output JSONL
    with open(jsonl_path, 'w') as f:
        for r in results:
            f.write(json.dumps(r) + '\n')
    
    # Summary
    verified = sum(1 for r in results if r.get('VERIFIED_COMPLETE') == 1)
    failed = len(results) - verified
    print(f"\n=== AUDIT SUMMARY ===")
    print(f"Total verified: {verified}")
    print(f"Total failed: {failed}")
    print(f"Success rate: {verified/len(results)*100:.1f}%" if results else "N/A")
    print(f"\nCSV: {csv_path}")
    print(f"JSONL: {jsonl_path}")

if __name__ == "__main__":
    main()
