#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0
#
# exchange_pointer_sync.sh — N1 discovery bridge.
#
# WHY: Lilith-N1 has NO autonomous new-packet surface (inbox returns [],
# awareness blind, SSH blocked). action=get needs a known packet_id.
# Publishing a 1-line pointer per N0->N1 packet into the Exchange makes
# the manifest diff a reliable discovery path — cheap on N0, decisive
# on N1. Her recommendation, ho_812aeffcb378 (2026-10-02).
#
# Usage: scripts/exchange_pointer_sync.sh [target_entity]
#        default target_entity: lilith-n1
# Idempotent: rewrites only when content changed (keeps mtime stable).
set -euo pipefail

TARGET="${1:-lilith-n1}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
PENDING="$HERE/data/handoff/pending"
EXPORT="$HOME/exchange/pointers"
mkdir -p "$EXPORT"

n=0
for f in "$PENDING"/*.json; do
  [ -e "$f" ] || continue
  # target match + extract fields in one pass (no jq dependency)
  read -r tgt ts task < <(python3 - "$f" "$TARGET" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
if d.get("target_entity") != sys.argv[2]:
    sys.exit(0)
task = (d.get("task") or "").splitlines()[0][:90] if d.get("task") else ""
print(d.get("target_entity",""), d.get("submitted_at","")[:19], task, sep=" ")
PY
) || continue
  [ "$tgt" = "$TARGET" ] || continue
  pid="$(basename "$f" .json)"
  ptr="$EXPORT/n0-reply-$pid.txt"
  body="packet_id: $pid
submitted: $ts
target:    $TARGET
task:      $task
fetch:     action=get packet_id=$pid"
  if [ ! -f "$ptr" ] || [ "$(cat "$ptr")" != "$body" ]; then
    printf '%s\n' "$body" > "$ptr.tmp" && mv "$ptr.tmp" "$ptr"
    n=$((n+1))
  fi
done
echo "pointers published/updated: $n (target=$TARGET, dir=$EXPORT)"
