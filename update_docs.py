import os
import re

def update_file(path, replacements):
    if not os.path.exists(path):
        print(f"Skipping {path} - not found")
        return
    with open(path, "r") as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(path, "w") as f:
        f.write(content)
    print(f"Updated {path}")

# 1. SOVEREIGN_ARK_BLUEPRINT.md
update_file("docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md", [
    ("├── C-3 Restic 3-2-1 Backup for Sovereign Data (lilith/P6) — 8h", 
     "├── V-1 VaultCore MVP (maat/P1) — 8h (MOVED TO P0 - Blocks C-3)\n├── C-3 Restic 3-2-1 Backup for Sovereign Data (lilith/P6) — 8h (Depends on V-1)"),
    ("└── P1 Gates: C-9, D-1, V-1, M21, C-4a.5", 
     "└── P1 Gates: C-9, D-1, M21, C-4a.5"),
    ("├── C-0.5 Scribe Agent L1→L2→L3 Distillation Pipeline (scribe/new) — 16h", 
     "├── C-0.5 Scribe Agent L1→L2→L3 Distillation + Crash Recovery Sweeper (scribe/new) — 16h")
])

# 2. LLM_FRIENDLY_DOCS_BP.md
bp_path = "docs/standards/LLM_FRIENDLY_DOCS_BP.md"
if os.path.exists(bp_path):
    with open(bp_path, "r") as f:
        content = f.read()
    if "M8 (Zero Telemetry)" not in content:
        addition = """
## 🛡️ Sovereign Mandate Compliance (The Centered Path)

### M8 (Zero Telemetry) in Analytics
All agent behavior analytics, success tracking, and feedback loops MUST be stored locally (e.g., `data/coordination/agent_doc_analytics/` as SQLite/JSONL). External telemetry platforms (Datadog, Exabeam) are strictly forbidden. The feedback loop must be entirely self-contained within the user's hardware.

### M18 (Token Efficiency) in Document Consumption
Do not force local agents (especially 8K context limits) to ingest monolithic `llms-full.txt` files. Agents must be instructed to read `llms.txt` (the index) first, then use targeted reads/greps for specific sections to prevent OOM and context truncation.
"""
        with open(bp_path, "a") as f:
            f.write(addition)
        print(f"Appended mandates to {bp_path}")

# 3. Sprint Index
idx_path = "docs/sprints/guard-and-distill/index.md"
if os.path.exists(idx_path):
    with open(idx_path, "r") as f:
        content = f.read()
    
    content = content.replace("4 P0 tickets", "5 P0 tickets")
    content = content.replace("- **V-1** — VaultCore credential rotation (3h)", "")
    
    if "5. **V-1**" not in content:
        content = content.replace("### P0 Tickets (Must Complete Before Phase D)", 
                                  "### P0 Tickets (Must Complete Before Phase D)\n5. **V-1** — VaultCore credential rotation (Moved from P1 - Blocks C-3)")
        
    content = content.replace("3. **C-3** — Restic backup script for sovereign data", 
                              "3. **C-3** — Restic backup script for sovereign data (Depends on V-1 for secure credential storage)")
    content = content.replace("4. **C-0.5** — Scribe agent for automated L1→L2→L3 soul distillation", 
                              "4. **C-0.5** — Scribe agent for automated L1→L2→L3 soul distillation + Startup Sweeper for crash recovery")
    
    with open(idx_path, "w") as f:
        f.write(content)
    print(f"Updated {idx_path}")

# 4. C-0.5 Ticket
c05_path = "docs/sprints/guard-and-distill/02-p0-tickets/C-0.5-scribe-agent.md"
if os.path.exists(c05_path):
    with open(c05_path, "r") as f:
        content = f.read()
    if "Startup Sweeper" not in content:
        content = content.replace("## Acceptance Criteria (Copy-Paste Verifiable)", 
                                  "## Acceptance Criteria (Copy-Paste Verifiable)\n- [ ] **Startup Sweeper**: Engine boot process checks `data/coordination/` for orphaned session logs and triggers Scribe retroactively (Crash Recovery).")
        with open(c05_path, "w") as f:
            f.write(content)
        print(f"Updated {c05_path}")

# 5. C-3 Ticket
c3_path = "docs/sprints/guard-and-distill/02-p0-tickets/C-3-restic-backup.md"
if os.path.exists(c3_path):
    with open(c3_path, "r") as f:
        content = f.read()
    if "V-1 (VaultCore)" not in content:
        content = content.replace("## Dependencies", 
                                  "## Dependencies\n- **Requires**: V-1 (VaultCore) for secure storage of B2 Application Keys and repository passwords. NO HARDCODING.")
        with open(c3_path, "w") as f:
            f.write(content)
        print(f"Updated {c3_path}")
        
# 6. Research Synthesis
rs_path = "docs/research/R_LLM_FRIENDLY_DOCS_RESEARCH_SYNTHESIS_20260722.md"
if os.path.exists(rs_path):
    with open(rs_path, "r") as f:
        content = f.read()
    content = content.replace("Research Need: Standardized agent telemetry schema, success/failure attribution, automated documentation improvement triggers",
                              "Research Need: Standardized agent telemetry schema, success/failure attribution, automated documentation improvement triggers **(Must be 100% Local-Only per M8 - No external telemetry)**")
    with open(rs_path, "w") as f:
        f.write(content)
    print(f"Updated {rs_path}")

