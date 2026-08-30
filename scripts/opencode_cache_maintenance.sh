#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# opencode_cache_maintenance.sh — report + clean OpenCode derived caches
# Truth-ledger item: explorer caches rebuild from opencode.db; NEVER touch the db itself.
# Usage: --report (default) | --clean
set -euo pipefail

DB="$HOME/.local/share/opencode/opencode.db"
EXPLORER="$HOME/.local/share/opencode-sessions-explorer"
declare -a CLEAN_TARGETS=(
  "$EXPLORER/by-channel"
  "$EXPLORER/by-session"
  "$HOME/.cache/pip"
  "$HOME/.cache/tracker3"
)

size() { du -sh "$1" 2>/dev/null | cut -f1 || echo "0"; }

report() {
  echo "=== OpenCode Cache Report $(date -Iseconds) ==="
  echo "opencode.db (SSOT — never auto-clean): $(size "$DB")"
  echo "explorer indexes: by-channel=$(size "$EXPLORER/by-channel" 2>/dev/null || echo '-') by-session=$(size "$EXPLORER/by-session" 2>/dev/null || echo '-')"
  echo "pip cache: $(size "$HOME/.cache/pip" 2>/dev/null || echo '0')"
  echo "tracker3:  $(size "$HOME/.cache/tracker3" 2>/dev/null || echo '0')"
  echo "disk: $(df -h / | awk 'NR==2{print $4" free ("$5" used)"}')"
  # Alert threshold: warn under 10G free
  local free_kb; free_kb=$(df --output=avail -k / | tail -1 | tr -d ' ')
  if [ "$free_kb" -lt $((10*1024*1024)) ]; then
    echo "⚠️  ALERT: <10G free on / — run with --clean"
    exit 3   # nonzero so systemd timer/cron alerting can catch it
  fi
}

clean() {
  for t in "${CLEAN_TARGETS[@]}"; do
    [ -e "$t" ] && echo "cleaning: $t ($(size "$t"))" && rm -rf "$t"
  done
  find "$HOME/.local/share/opencode/log" -name "*.log" -mtime +1 -delete 2>/dev/null || true
  echo "done."; report
}

case "${1:---report}" in
  --report) report ;;
  --clean)  clean ;;
  *) echo "usage: $0 [--report|--clean]"; exit 1 ;;
esac
