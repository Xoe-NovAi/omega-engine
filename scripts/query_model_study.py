#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Model Study KB Query Interface
Usage: python3 query_model_study.py [command] [args]
"""

import sqlite3
import json
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "model_study" / "model_study.db"

def connect():
    return sqlite3.connect(DB_PATH)

def list_models():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name, tier, platform, context_window, pricing_input, pricing_output FROM models ORDER BY tier, platform, name")
    for row in cursor.fetchall():
        ctx = f"{row[3]:,}" if row[3] else "N/A"
        pin = f"${row[4]:.2f}" if row[4] is not None else "N/A"
        pout = f"${row[5]:.2f}" if row[5] is not None else "N/A"
        print(f"  {row[0]}")
        print(f"    Tier: {row[1]} | Platform: {row[2]} | Context: {ctx} | ${pin}/${pout}/MTok")
    conn.close()

def model_details(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM models WHERE name LIKE ?", (f"%{name}%",))
    row = cursor.fetchone()
    if row:
        cols = [d[0] for d in cursor.description]
        for col, val in zip(cols, row):
            if col in ('capabilities', 'weaknesses', 'best_for'):
                try:
                    val = json.loads(val)
                    val = ", ".join(val)
                except:
                    pass
            print(f"  {col}: {val}")
    else:
        print(f"No model found matching '{name}'")
    conn.close()

def list_test_runs():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, test_name, date, description FROM test_runs")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]} ({row[2]})")
        print(f"      {row[3]}")
    conn.close()

def test_results(test_run_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT model_name, metric, value, notes 
        FROM test_results 
        WHERE test_run_id = ? 
        ORDER BY model_name, metric
    """, (test_run_id,))
    for row in cursor.fetchall():
        print(f"  {row[0]} | {row[1]}: {row[2]}")
        if row[3]:
            print(f"    Note: {row[3]}")
    conn.close()

def findings(test_run_id=None, severity=None):
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT f.*, tr.test_name FROM findings f JOIN test_runs tr ON f.test_run_id = tr.id"
    params = []
    conditions = []
    if test_run_id:
        conditions.append("f.test_run_id = ?")
        params.append(test_run_id)
    if severity:
        conditions.append("f.severity = ?")
        params.append(severity)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY f.severity, f.category"
    cursor.execute(query, params)
    for row in cursor.fetchall():
        print(f"  [{row[3]}] {row[4]} | {row[2]} | {row[5]}")
        if row[6]:
            print(f"    Evidence: {row[6]}")
    conn.close()

def synergies():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name, pattern, models_involved, use_case, evidence, confidence FROM synergies ORDER BY confidence DESC")
    for row in cursor.fetchall():
        print(f"  {row[0]} (confidence: {row[5]:.0%})")
        print(f"    Pattern: {row[1]}")
        print(f"    Models: {row[2]}")
        print(f"    Use Case: {row[3]}")
        print(f"    Evidence: {row[4]}")
        print()
    conn.close()

def best_for(task):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name, tier, platform, best_for FROM models")
    print(f"Models suited for '{task}':")
    for row in cursor.fetchall():
        try:
            best_for = json.loads(row[3])
            if any(task.lower() in bf.lower() for bf in best_for):
                print(f"  {row[0]} ({row[1]}/{row[2]})")
                print(f"    Best for: {', '.join(best_for)}")
        except:
            pass
    conn.close()

def cognitive_mode(mode):
    """Find models by cognitive mode"""
    mode_map = {
        "diagnostic": ["deep_reasoning", "root_cause_analysis", "surgical_bug_finding", "architectural_reasoning"],
        "generation": ["high_throughput_generation", "documentation_factory", "test_suite_generation"],
        "synthesis": ["consolidation", "roadmap_sequencing", "big_picture_synthesis"],
        "research": ["realtime_x_search", "parallel_web_search", "source_grounding", "live_research"],
        "verification": ["code_execution", "parallel_verification", "empirical_verification"],
        "orchestration": ["fleet_orchestration", "mandate_enforcement", "gnosis_distillation"],
    }
    keywords = mode_map.get(mode.lower(), [mode.lower()])
    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name, tier, platform, capabilities, best_for FROM models")
    print(f"Models with '{mode}' cognitive mode:")
    for row in cursor.fetchall():
        try:
            caps = json.loads(row[3])
            if any(kw in caps for kw in keywords):
                print(f"  {row[0]} ({row[1]}/{row[2]})")
                print(f"    Capabilities: {', '.join(caps)}")
        except:
            pass
    conn.close()

def token_economics():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, tier, platform, context_window, pricing_input, pricing_output, free_tier_limit
        FROM models 
        WHERE pricing_input IS NOT NULL
        ORDER BY pricing_input
    """)
    print("Token Economics (per MTok):")
    print(f"  {'Model':<35} {'Tier':<6} {'Platform':<12} {'Context':>10} {'In':>6} {'Out':>6} {'Free Tier'}")
    print("  " + "-"*90)
    for row in cursor.fetchall():
        ctx = f"{row[3]:,}" if row[3] else "N/A"
        inp = f"${row[4]:.2f}" if row[4] is not None else "N/A"
        out = f"${row[5]:.2f}" if row[5] is not None else "N/A"
        print(f"  {row[0]:<35} {row[1]:<6} {row[2]:<12} {ctx:>10} {inp:>6} {out:>6} {row[6]}")
    conn.close()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCommands:")
        print("  models                    - List all models")
        print("  model <name>              - Show model details")
        print("  tests                     - List test runs")
        print("  results <test_id>         - Show test results")
        print("  findings [test_id] [sev]  - Show findings (filter by test_id and/or severity)")
        print("  synergies                 - Show synergy patterns")
        print("  best_for <task>           - Find models for a task")
        print("  mode <cognitive_mode>     - Find models by cognitive mode")
        print("  economics                 - Show token economics table")
        return

    cmd = sys.argv[1]
    
    if cmd == "models":
        list_models()
    elif cmd == "model" and len(sys.argv) > 2:
        model_details(" ".join(sys.argv[2:]))
    elif cmd == "tests":
        list_test_runs()
    elif cmd == "results" and len(sys.argv) > 2:
        test_results(int(sys.argv[2]))
    elif cmd == "findings":
        test_id = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
        sev = sys.argv[3] if len(sys.argv) > 3 else None
        findings(test_id, sev)
    elif cmd == "synergies":
        synergies()
    elif cmd == "best_for" and len(sys.argv) > 2:
        best_for(" ".join(sys.argv[2:]))
    elif cmd == "mode" and len(sys.argv) > 2:
        cognitive_mode(sys.argv[2])
    elif cmd == "economics":
        token_economics()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()