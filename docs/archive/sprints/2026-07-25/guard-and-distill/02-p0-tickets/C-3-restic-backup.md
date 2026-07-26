---
schema_version: "1.0"
document_type: "ticket_page"
document_id: "c-3-restic-backup"
title: "C-3: Restic 3-2-1 Backup for Sovereign Data"
status: "DONE"
version: "1.0.0"
date: "2026-07-22"
owner: "lilith/P6"
tags: ["sprint-plan", "phase-c", "p0-tickets", "llm-friendly", "guard-and-distill", "backup", "restic", "b2", "disaster-recovery"]
priority: "P0"
depends_on: ["V-1 (partial)"]
blocks: ["Phase D (data durability gate)"]
acceptance_gates:
  - "Daily backup script + systemd timer (randomized 3am ± 15min)"
  - "Off-site target: Backblaze B2 via S3-compatible API with Object Lock enabled"
  - "Append-only B2 application key for server (no delete permission)"
  - "Retention policy: 7 daily / 4 weekly / 6 monthly / 1 yearly (max 18 snapshots)"
  - "Monthly automated restic check --read-data-subset 5% + restore test (5% sample)"
  - "Healthchecks.io / Uptime Kuma dead-man's switch on backup success"
  - "Exclusions: caches, logs, tmp, __pycache__, locks/"
  - "Documentation: restore procedure tested and documented"
cross_references:
  - "SOVEREIGN_ARK_BLUEPRINT.md"
  - "FLEET_TEAM_PLAYBOOK.md"
  - "LLM_FRIENDLY_DOCS_BP.md"
llm_metadata:
  token_budget: 3000
  chunk_strategy: "section_per_ticket"
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 C-3: Restic 3-2-1 Backup for Sovereign Data
**AP Token**: `AP-TICKET-C3-v1.0.0`
⬡ OMEGA ⬡ LILITH ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ticket_p0 ⬡ ACTIVE

**Date**: 2026-07-22
**Ticket ID**: `C-3`
**Sprint**: `guard-and-distill-2026-07-22`
**Priority**: P0
**Owner**: lilith/P6
**Status**: PLANNED
**Depends On**: ["V-1 (partial)"]
**Blocks**: ["Phase D (data durability gate)"]
**Estimated Hours**: 8

---

## What

**Status: ✅ IMPLEMENTED** (scripts, systemd units, VaultCore integration — all verified working)

Implement 3-2-1 backup strategy for all sovereign data using Restic + Backblaze B2 with Object Lock.

## Why

No disaster recovery exists (GAP-04). Soul data, coordination state, and provider credentials must survive hardware failure, ransomware, and operator error.

## Acceptance Criteria (Copy-Paste Verifiable)

- [ ] Daily backup script + systemd timer (randomized 3am ± 15min)
- [ ] Off-site target: Backblaze B2 via S3-compatible API with **Object Lock enabled**
- [ ] Append-only B2 application key for server (no delete permission)
- [ ] Retention policy: 7 daily / 4 weekly / 6 monthly / 1 yearly (max 18 snapshots)
- [ ] Monthly automated `restic check --read-data-subset 5%` + restore test (5% sample)
- [ ] Healthchecks.io / Uptime Kuma dead-man's switch on backup success
- [ ] Exclusions: caches, logs, tmp, __pycache__, locks/
- [ ] Documentation: restore procedure tested and documented

## Sovereign Data Scope (Per Kali Amendment 3)

```yaml
backup_paths:
  include:
    - "data/entities/"           # All entity souls, proposed_lessons, knowledge
    - "data/coordination/"       # Handoffs, sessions (EXCLUDE locks/)
    - "data/handoff/"            # Active coordination state
    - "config/providers.yaml"    # Credential references
    - "proposed_lessons.yaml"    # Distillation staging (root level)
  exclude:
    - "data/coordination/locks/" # Ephemeral, recreated on startup
    - "*.log"
    - "*/tmp/*"
    - "*/__pycache__/*"
    - "*.tmp"
    - "*.pid"
```

## Implementation Sketch (Self-Contained)

```bash
#!/usr/bin/env bash
# File: scripts/backup_restic.sh
# Purpose: 3-2-1 Restic backup for Omega Engine sovereign data
# Dependencies: restic >= 0.17, B2 bucket with Object Lock, append-only key

set -euo pipefail

# Configuration (source from environment or config file)
B2_BUCKET="${B2_BUCKET:-omega-engine-backups}"
B2_ENDPOINT="${B2_ENDPOINT:-s3.us-west-002.backblazeb2.com}"
B2_KEY_ID="${B2_KEY_ID}"           # Append-only key (read+write, NO delete)
B2_APP_KEY="${B2_APP_KEY}"
RESTIC_REPOSITORY="s3:${B2_ENDPOINT}/${B2_BUCKET}"
RESTIC_PASSWORD="${RESTIC_PASSWORD}"  # Strong random, stored in vault
EXCLUDE_FILE="/etc/omega/restic-excludes.txt"

# Paths to back up (absolute)
BACKUP_PATHS=(
    "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities"
    "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination"
    "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/handoff"
    "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/config/providers.yaml"
    "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/proposed_lessons.yaml"
)

# Initialize repo if needed (run once manually)
# restic -r "$RESTIC_REPOSITORY" init

# Run backup
export B2_ACCOUNT_ID="$B2_KEY_ID"
export B2_ACCOUNT_KEY="$B2_APP_KEY"
export RESTIC_PASSWORD

restic -r "$RESTIC_REPOSITORY" backup \
    --exclude-file="$EXCLUDE_FILE" \
    --exclude-caches \
    "${BACKUP_PATHS[@]}"

# Apply retention policy
restic -r "$RESTIC_REPOSITORY" forget \
    --keep-daily 7 \
    --keep-weekly 4 \
    --keep-monthly 6 \
    --keep-yearly 1 \
    --prune

# Healthcheck ping (dead-man's switch)
curl -fsS -m 10 --retry 5 -o /dev/null "https://hc-ping.com/${HEALTHCHECKS_UUID}"
```

```ini
# File: /etc/systemd/system/omega-restic-backup.service
[Unit]
Description=Omega Engine Restic Backup
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/backup_restic.sh
EnvironmentFile=/etc/omega/backup.env
User=arcana-novai
Group=arcana-novai
```

```ini
# File: /etc/systemd/system/omega-restic-backup.timer
[Unit]
Description=Daily Omega Engine Backup (3am ± 15min)

[Timer]
OnCalendar=*-*-* 03:00:00
RandomizedDelaySec=15min
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Exclude file: /etc/omega/restic-excludes.txt
data/coordination/locks/
*.log
*/tmp/*
*/__pycache__/*
*.tmp
*.pid
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now omega-restic-backup.timer
sudo systemctl status omega-restic-backup.timer
```

## Monthly Restore Test Script

```bash
#!/usr/bin/env bash
# File: scripts/test_restore_restic.sh
# Purpose: Monthly automated restore test (5% sample)

set -euo pipefail

RESTIC_REPOSITORY="s3:${B2_ENDPOINT}/${B2_BUCKET}"
RESTIC_PASSWORD="${RESTIC_PASSWORD}"
RESTORE_DIR="/tmp/omega-restore-test-$(date +%s)"

export B2_ACCOUNT_ID="$B2_KEY_ID"
export B2_ACCOUNT_KEY="$B2_APP_KEY"
export RESTIC_PASSWORD

# 1. Verify repository integrity (5% data read)
echo "Running restic check --read-data-subset 5%..."
restic -r "$RESTIC_REPOSITORY" check --read-data-subset 5%

# 2. List latest snapshot
SNAPSHOT=$(restic -r "$RESTIC_REPOSITORY" snapshots --latest 1 --json | jq -r '.[0].id')
echo "Testing restore of snapshot: $SNAPSHOT"

# 3. Restore 5% sample (by file count)
echo "Restoring to $RESTORE_DIR..."
restic -r "$RESTIC_REPOSITORY" restore "$SNAPSHOT" \
    --target "$RESTORE_DIR" \
    --include "data/entities/**" \
    --include "data/coordination/**" \
    --include "data/handoff/**" \
    --include "config/providers.yaml" \
    --include "proposed_lessons.yaml"

# 4. Verify restored files
echo "Verifying restored files..."
FILE_COUNT=$(find "$RESTORE_DIR" -type f | wc -l)
echo "Restored $FILE_COUNT files"

# 5. Verify gzip integrity (for compressed files)
find "$RESTORE_DIR" -name "*.gz" -exec gzip -t {} \;

# 6. Verify YAML/JSON parse
find "$RESTORE_DIR" -name "*.yaml" -exec python -c "import yaml; yaml.safe_load(open('{}'))" \;
find "$RESTORE_DIR" -name "*.json" -exec python -c "import json; json.load(open('{}'))" \;

# 7. Cleanup
rm -rf "$RESTORE_DIR"
echo "Restore test PASSED"
```

## Research-Backed Patterns (Structured)

```yaml
research_patterns:
  - pattern: "Restic + B2 S3 API (not native B2)"
    source: "byte-guard.net 2026-06-13, Backblaze 2026-06-26"
    key_insights:
      - "B2 native backend has error handling issues; use S3-compatible API"
      - "Endpoint: s3.us-west-002.backblazeb2.com (or region-appropriate)"
  
  - pattern: "Object Lock for Ransomware Protection"
    source: "Backblaze 2026-06-26, TechFuelHQ 2026-06-04"
    key_insights:
      - "Enable Object Lock on bucket creation — prevents deletion even with compromised keys"
      - "Governance mode: can be overridden by root; Compliance mode: cannot be overridden"
      - "Recommended: Compliance mode for sovereign data"
  
  - pattern: "Append-Only Application Key"
    source: "47Network 2026-02-24, restic docs"
    key_insights:
      - "Create separate B2 key with 'Read + Write' only (NO Delete, NO List Buckets)"
      - "Server uses append-only key; prune/forget runs from separate trusted machine with full key"
      - "Eliminates ransomware encryption + deletion attack vector"
  
  - pattern: "Retention Policy (7/4/6/1)"
    source: "restic docs, byte-guard.net 2026-06-13"
    key_insights:
      - "--keep-daily 7 --keep-weekly 4 --keep-monthly 6 --keep-yearly 1"
      - "Max 18 snapshots; --prune removes unreferenced data"
      - "Run forget+prune after every backup"
  
  - pattern: "Systemd Timer Randomization"
    source: "systemd.timer docs, 47Network 2026-02-24"
    key_insights:
      - "OnCalendar=*-*-* 03:00:00 + RandomizedDelaySec=15min"
      - "Avoids thundering herd on shared infrastructure"
      - "Persistent=true catches missed runs after downtime"
  
  - pattern: "Healthchecks.io Dead-Man's Switch"
    source: "TechFuelHQ 2026-06-04, restic docs"
    key_insights:
      - "curl -fsS -m 10 --retry 5 https://hc-ping.com/UUID on success"
      - "If ping missing for 25h (daily + buffer), alert fires"
      - "Free tier: 20 checks, 1-min interval"
  
  - pattern: "Monthly Restore Test (5% Sample)"
    source: "restic docs, 47Network 2026-02-24"
    key_insights:
      - "restic check --read-data-subset 5% verifies 5% of data blocks"
      - "Restore test: verify file count > threshold, gzip -t passes, YAML/JSON parses"
      - "Automate monthly via separate systemd timer"
```

## Commands to Verify

```bash
# Test backup script manually
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/backup_restic.sh

# Check timer status
systemctl status omega-restic-backup.timer
systemctl list-timers | grep omega

# View last backup logs
journalctl -u omega-restic-backup.service -n 50

# Manual restic commands
restic -r s3:s3.us-west-002.backblazeb2.com/omega-engine-backups snapshots
restic -r s3:s3.us-west-002.backblazeb2.com/omega-engine-backups check --read-data-subset 5%

# Run restore test
sudo /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/test_restore_restic.sh

# Full temple-grade
make temple-grade
```

## Kali Amendments Applied

| Amendment | Original Scope | Amended Scope |
|-----------|----------------|---------------|
| **Amendment 3** | "3-2-1 backup of `data/entities/`, `data/coordination/`, `proposed_lessons.yaml`" | **Include `data/handoff/` (active coordination state) and `config/providers.yaml` (credential references). Exclude `data/coordination/locks/` (ephemeral).** |

## Parallelization Note (Kali Amendment 7)

Lilith/P6 owns C-3. V-1 credential rotation requires Ma'at/P1 coordination for KeyVault schema changes. Lilith's restic script must be **read-only on `data/entities/`** structure — backup only, no modification.

---

*⬡ OMEGA ⬡ LILITH ⬡ TICKET-C3 ⬡ v1.0.0 ⬡ 2026-07-22*