#!/usr/bin/env bash
# ==============================================================================
# OMEGA ENGINE — HARNESS BACKUP
# ==============================================================================
# Snapshots the ASUS OpenCode harness: SSOT docs, scripts, gnosis protocol,
# identity, configs, shell functions. Run manually or via cron.
#
# Usage: scripts/backup_harness.sh            (writes /home/xnai/backups/)
#        scripts/backup_harness.sh --usb     (also copies to USB if mounted)
# ==============================================================================
set -euo pipefail

PROJECT_ROOT="/home/xnai/Documents/Projects/omega-engine-alpha"
BACKUP_DIR="/home/xnai/backups"
STAMP="$(date -u +%Y%m%d-%H%M%SZ)"
ARCHIVE="${BACKUP_DIR}/omega-harness-${STAMP}.tar.gz"
KEEP=14
LOG="${BACKUP_DIR}/backup.log"

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  $*" >> "${LOG}"; }

mkdir -p "${BACKUP_DIR}"

# ─── Build archive (excludes real secrets, sessions, venv) ───────────────────
tar czf "${ARCHIVE}" \
  --exclude='.env.ollama' \
  --exclude='.env.docker' \
  --exclude='session-*.md' \
  --exclude='gnosis/sessions' \
  --exclude='gnosis/evolution' \
  --exclude='.venv' \
  -C "$(dirname "${PROJECT_ROOT}")" \
    "$(basename "${PROJECT_ROOT}")/AGENTS.md" \
    "$(basename "${PROJECT_ROOT}")/Makefile" \
    "$(basename "${PROJECT_ROOT}")/docker-compose.yml" \
    "$(basename "${PROJECT_ROOT}")/.env.ollama.example" \
    "$(basename "${PROJECT_ROOT}")/.env.docker.example" \
    "$(basename "${PROJECT_ROOT}")/.gitignore" \
    "$(basename "${PROJECT_ROOT}")/docs" \
    "$(basename "${PROJECT_ROOT}")/scripts" \
    "$(basename "${PROJECT_ROOT}")/gnosis/GNOSIS_LOCK_PROTOCOL.md" \
    "$(basename "${PROJECT_ROOT}")/gnosis/OPENCODE_HOOKS.md" \
    "$(basename "${PROJECT_ROOT}")/gnosis/identity" \
    "$(basename "${PROJECT_ROOT}")/.modelfiles" \
  -C /home/xnai \
    .config/opencode/opencode.json \
    .config/opencode/opencode.jsonc \
    .config/opencode/AGENTS.md \
    .config/opencode/agent \
    .config/opencode/prompts \
    .bash_aliases

# ─── Prune old archives ───────────────────────────────────────────────────────
ls -1t "${BACKUP_DIR}"/omega-harness-*.tar.gz 2>/dev/null | tail -n +$((KEEP+1)) | while read -r old; do
  rm -f "${old}"
  log "pruned ${old}"
done

# ─── Optional USB copy ────────────────────────────────────────────────────────
USB="/run/media/xnai/D5D5-0B76"
if [[ "${1:-}" == "--usb" ]] && mountpoint -q "${USB}"; then
  mkdir -p "${USB}/backups"
  cp -f "${ARCHIVE}" "${USB}/backups/"
  log "usb copy: ${USB}/backups/$(basename "${ARCHIVE}")"
fi

log "archive: ${ARCHIVE} ($(du -h "${ARCHIVE}" | cut -f1))"
echo "✅ Backup: ${ARCHIVE}"
echo "   size:  $(du -h "${ARCHIVE}" | cut -f1)   keep: ${KEEP}"