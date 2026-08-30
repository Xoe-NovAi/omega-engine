import os

# 1. Trim C-11 Scope
c11_path = "docs/sprints/guard-and-distill/02-p0-tickets/C-11-property-tests.md"
if os.path.exists(c11_path):
    with open(c11_path, "r") as f:
        c11 = f.read()
    
    # Add Carmack's note
    if "CARMACK AUDIT" not in c11:
        c11 = c11.replace("## What", "## What\n\n> ⚠️ **CARMACK AUDIT (2026-07-22)**: Scope trimmed. Start strictly with OOMProtector and SoulStore invariants. Do NOT build a massive chaos testing suite or benchmarks until core invariants are proven.\n\nImplement Hypothesis `RuleBasedStateMachine` property tests for:")
        with open(c11_path, "w") as f:
            f.write(c11)
        print("Trimmed C-11 scope")

# 2. Trim C-0.5 Scope
c05_path = "docs/sprints/guard-and-distill/02-p0-tickets/C-0.5-scribe-agent.md"
if os.path.exists(c05_path):
    with open(c05_path, "r") as f:
        c05 = f.read()
    
    # Add Carmack's note
    if "CARMACK AUDIT" not in c05:
        c05 = c05.replace("## What", "## What\n\n> ⚠️ **CARMACK AUDIT (2026-07-22)**: Scope phased. Build L1→L2 first using JSON Schema and LLM-as-Judge. Push L3 extraction to Phase D if it threatens the sprint timeline.\n\nCreate **Scribe agent**")
        with open(c05_path, "w") as f:
            f.write(c05)
        print("Trimmed C-0.5 scope")

