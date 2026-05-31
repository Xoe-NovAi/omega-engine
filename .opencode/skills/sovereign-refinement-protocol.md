# 🔱 Sovereign Refinement & Hardening Protocol (SR-HP)
## Template Grade: Temple Standard | Version: 1.0.0 | Status: ACTIVE
## ⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}

### 📖 How to Use This Protocol
When an agent is invoked with this protocol, it must execute the following **four phases** sequentially. The agent is forbidden from skipping to implementation without completing the preceding forensic and preservation gates.

---

## 🔍 Phase 1: The Forensic & Physical Audit Gate

Before making any software or configuration changes, the agent must audit the physical and state layers of the system to prevent resource-collision failures.

### 1.1 Physical Layer Audit
The agent must run the following commands and analyze the output:
- [ ] **Disk Space**: \`df -h /\` (Verify root partition has $>15\%$ headroom).
- [ ] **Memory**: \`free -h\` (Verify RAM has $>2\text{GB}$ available).
- [ ] **Containers**: \`podman pod ls\` and \`podman ps\` (Verify infrastructure health).

### 1.2 State Layer Audit
If a database or tool is failing (e.g., SQLite \`FOREIGN KEY\` errors), the agent must:
- [ ] Check if the failure correlates with a physical constraint (e.g., disk full preventing journal writes).
- [ ] Query the database schema and last 5 records using Python's native \`sqlite3\` to check for corruption or desynchronization.
- [ ] Verify file permissions using \`ls -la\` (especially in container-mapped directories).

---

## 🛡️ Phase 2: The Inviolable Data Preservation Gate

The agent is strictly forbidden from modifying files or upgrading binaries until a verified backup is secured.

### 2.1 The Backup Sequence
The agent must execute and verify:
\`\`\`bash
# 1. Create timestamped backup directory
BACKUP_DIR="\$HOME/omega_state_backups/\$(date +%Y%m%d_%H%M%S)"
mkdir -p "\$BACKUP_DIR"

# 2. Copy state and config directories
cp -r ~/.opencode "\$BACKUP_DIR/"
cp -r ~/.config/opencode "\$BACKUP_DIR/"

# 3. Compress and verify
tar -czf "\$HOME/omega_sovereign_backup_\$(date +%Y%m%d).tar.gz" -C "\$HOME/omega_state_backups" "\$(basename "\$BACKUP_DIR")"
ls -lh "\$HOME/omega_sovereign_backup_\$(date +%Y%m%d).tar.gz"
\`\`\`

### 2.2 Emergency Space Recovery (If Backup Fails with \`No space left\`)
If the backup fails due to disk space, the agent must execute this safe cleanup sequence:
1. Purge tool output caches: \`rm -rf ~/.local/share/opencode/tool-output/*\`
2. Prune old debug logs: \`rm -f ~/.config/opencode/antigravity-logs/*.log\`
3. Identify large non-critical files for migration to \`/media/arcana-novai/omega_library/\`.

---

## 📝 Phase 3: The Alignment & Tracker Sync Gate

The agent must synchronize the "Sovereign Truth" across all project trackers before starting any technical work.

### 3.1 Tracker Updates
- [ ] **\`docs/MASTER_LEDGER.md\`**: Append a milestone entry detailing the current state, fixes, and decisions.
- [ ] **\`data/handoff/handoff_builder_execution_card.md\`**: Update the active Sprint status, Ground Truth metrics, and current focus.
- [ ] **\`data/workbench/workbench.db\`**: Run SQL inserts to record architectural decisions and update artifact mining statuses.

---

## 🔬 Phase 4: The R&D-to-Sprint Cycle (The Core Engine)

For every technical objective, the agent must split the work into two distinct, sequential phases: **Research & Discovery (R&D)** and **Implementation (Sprint)**.

\`\`\`
┌─────────────────────────────────────────────────────────┐
│              RESEARCH & DISCOVERY (R&D)                 │
│                                                         │
│  1. Audit: Map existing code and touchpoints.           │
│  2. Research: Benchmark and analyze optimal patterns.   │
│  3. Design: Draft fallback and schema specifications.   │
│  4. Output: Write docs/research/R_{TOPIC}_SPEC.md.      │
└────────────────────────────────────┬────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                 IMPLEMENTATION (SPRINT)                 │
│                                                         │
│  1. Implement: Write clean, AnyIO-compliant code.       │
│  2. Test: Run make test and verify all gates.           │
│  3. Verify: Confirm graceful degradation on failure.    │
└─────────────────────────────────────────────────────────┘
\`\`\`

### 4.1 R&D Phase Requirements
The agent must author a formal specification file at \`docs/research/R_{TOPIC}_SPEC.md\` answering:
1.  **Fallback**: How does this system gracefully degrade if its dependencies (Redis, Qdrant, Postgres) are offline?
2.  **Performance**: What is the latency/RAM footprint of this design on the Zen 2 CPU?
3.  **Sovereignty**: Does this design introduce any external cloud dependencies or telemetry?

### 4.2 Sprint Phase Requirements
The agent must implement the design following these **Inviolable Sovereign Constraints**:
- [ ] **AnyIO Absolute**: No synchronous blocking I/O or raw \`asyncio\` in \`src/omega/\`. Wrap blocking calls in \`anyio.to_thread.run_sync\`.
- [ ] **Engine-Stack Firewall**: Keep \`src/omega/\` completely generic. No stack-specific or entity-specific logic in the core.
- [ ] **Zero Telemetry**: All logs, metrics, and audits must remain strictly local.
- [ ] **No Performance Tax**: Heavy operations (like logging or vector generation) must run asynchronously out-of-band.

---

## 🏁 Verification & Sign-Off
Before completing the session, the agent must run:
\`\`\`bash
make test
\`\`\`
**All 259+ tests must pass.** The agent must output a final summary containing the updated metrics, reclaimed resources, and the path to the newly authored R&D specifications.
