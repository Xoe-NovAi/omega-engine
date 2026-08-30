#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# alert_state_change.sh — Detect provider state changes and post to Hivemind
# Version: v1.0 (probe-report-actions-20260827 — Action 5)
#
# Compares the most recent probe for each model against the saved state.
# Posts to Hivemind via omega-hub (MCP) on:
#   - new model appears (never seen before)
#   - state transition: working (200+valid) ↔ rate-limited (429)
#   - quality regression: was valid, now returning 200+error body
#   - full outage: 3+ consecutive failures (escalates to "critical")
#
# Mandate compliance:
#   M8 (zero telemetry): only calls Hivemind MCP, no external analytics
#   M23 (failure integrity): Hivemind failure → local log + non-zero exit
#   M27 (tracking integrity): all transitions logged in JSON state file
#
# Usage:
#   bash scripts/alert_state_change.sh            # check + alert
#   bash scripts/alert_state_change.sh --dry-run  # log only, no Hivemind post

set -uo pipefail

LOG_DIR="${HOME}/Documents/Xoe-NovAi/omega-engine/data/metrics"
PROBE_FILE="${LOG_DIR}/free_model_probes.jsonl"
STATE_FILE="${LOG_DIR}/model_state.json"
ALERT_LOG="${LOG_DIR}/alert_state_change.log"
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $*" | tee -a "$ALERT_LOG"
}

if [[ ! -f "$PROBE_FILE" ]]; then
    log "FATAL: $PROBE_FILE not found"
    exit 2
fi

# === Compute current state (most recent probe per model) ====================
CURRENT=$(python3 << 'PYEOF'
import json, sys
from pathlib import Path
from collections import defaultdict

PROBE_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/free_model_probes.jsonl"

# Track most recent probe per model, plus last 3 for outage detection
latest = {}
recent3 = defaultdict(list)  # model -> list of last 3 http_status

with PROBE_FILE.open() as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = d.get("model")
        if not m:
            continue
        latest[m] = d
        recent3[m].append(d.get("http_status"))

# Compute state
def classify(d):
    """Classify a probe entry into one of: working, rate_limited, auth_error, server_error, unknown"""
    s = d.get("http_status")
    qc = d.get("quality_check") or {}
    if s == 200 and qc.get("valid_json") and qc.get("has_completion"):
        return "working"
    if s == 200:
        return "degraded"  # 200 but no valid completion (or-key bug)
    if s == 429:
        return "rate_limited"
    if s in (401, 403):
        return "auth_error"
    if s in (500, 502, 503, 504):
        return "server_error"
    if s in (400, 404, 422):
        return "client_error"
    if s == "NO_KEY":
        return "no_key"
    return f"other_{s}"

state = {}
for m, d in latest.items():
    s = classify(d)
    last3 = recent3[m][-3:]
    consecutive_failures = 0
    for st in reversed(last3):
        if st in (429, 500, 502, 503, 504) or st == "NO_KEY":
            consecutive_failures += 1
        else:
            break
    state[m] = {
        "label": d.get("label"),
        "state": s,
        "http_status": d.get("http_status"),
        "ts": d.get("ts"),
        "key_source": d.get("key_source"),
        "latency_ms": d.get("latency_ms"),
        "window": d.get("window"),
        "consecutive_failures": consecutive_failures,
    }

print(json.dumps(state, ensure_ascii=False))
PYEOF
)

# === Load previous state ====================================================
PREVIOUS="{}"
if [[ -f "$STATE_FILE" ]]; then
    PREVIOUS=$(cat "$STATE_FILE")
fi

# === Diff + generate alerts =================================================
ALERTS=$(python3 << PYEOF
import json
import sys

current = json.loads('''$CURRENT''')
previous = json.loads('''$PREVIOUS''')

alerts = []
STATE_RANK = {
    "working": 0,
    "degraded": 1,
    "client_error": 2,
    "server_error": 3,
    "auth_error": 4,
    "rate_limited": 5,
    "no_key": 6,
    "other_0": 7,  # network failure
}

# 1. New models
for m in current:
    if m not in previous:
        c = current[m]
        alerts.append({
            "model": m,
            "label": c.get("label"),
            "type": "new_model",
            "old_state": None,
            "new_state": c["state"],
            "http_status": c["http_status"],
            "key_source": c.get("key_source"),
            "ts": c["ts"],
            "severity": "info",
            "message": f"New model observed: {m} (state={c['state']})",
        })

# 2. State transitions
for m in current:
    if m not in previous:
        continue
    c = current[m]
    p = previous[m]
    if c["state"] != p["state"]:
        # Determine severity
        old_rank = STATE_RANK.get(p["state"], 99)
        new_rank = STATE_RANK.get(c["state"], 99)
        if new_rank < old_rank:
            severity = "recovery"  # was bad, now good
        elif new_rank > old_rank:
            severity = "degradation"  # was good, now bad
        else:
            severity = "change"
        # Promote to critical if 3+ consecutive failures
        if c.get("consecutive_failures", 0) >= 3:
            severity = "critical"
        # Demote "degraded" → "working" to info (likely transient)
        if p["state"] == "degraded" and c["state"] == "working":
            severity = "info"
        alerts.append({
            "model": m,
            "label": c.get("label"),
            "type": "state_change",
            "old_state": p["state"],
            "new_state": c["state"],
            "http_status": c["http_status"],
            "key_source": c.get("key_source"),
            "ts": c["ts"],
            "consecutive_failures": c.get("consecutive_failures", 0),
            "severity": severity,
            "message": f"{m}: {p['state']} → {c['state']} (HTTP {c['http_status']}, key={c.get('key_source')})",
        })

# 3. Models that disappeared (in previous but not current)
for m in previous:
    if m not in current:
        p = previous[m]
        alerts.append({
            "model": m,
            "label": p.get("label"),
            "type": "model_disappeared",
            "old_state": p["state"],
            "new_state": None,
            "ts": p["ts"],
            "severity": "warning",
            "message": f"Model {m} no longer probed (was {p['state']})",
        })

print(json.dumps(alerts, ensure_ascii=False))
PYEOF
)

# === Save current state (atomic write) ======================================
echo "$CURRENT" > "${STATE_FILE}.tmp"
mv "${STATE_FILE}.tmp" "$STATE_FILE"

# === Process alerts =========================================================
ALERT_COUNT=$(echo "$ALERTS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
if [[ "$ALERT_COUNT" == "0" ]]; then
    log "No state changes detected across $(echo "$CURRENT" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))') models"
    exit 0
fi

log "Detected $ALERT_COUNT state change(s)"

# Format alerts for Hivemind
HIVEMIND_PAYLOAD=$(python3 << PYEOF
import json
alerts = json.loads('''$ALERTS''')
# Group by severity
by_sev = {}
for a in alerts:
    by_sev.setdefault(a["severity"], []).append(a)

summary_lines = []
for sev in ["critical", "degradation", "recovery", "change", "warning", "info"]:
    items = by_sev.get(sev, [])
    if not items:
        continue
    summary_lines.append(f"**{sev.upper()}** ({len(items)}):")
    for a in items:
        summary_lines.append(f"  - {a['message']}")

body = "## Provider State Change Alert\n\n"
body += f"Detected **{len(alerts)}** state change(s) at $(date -u '+%Y-%m-%d %H:%M:%S UTC')\n\n"
body += "\n".join(summary_lines)
body += "\n\n---\n*Triggered by: scripts/alert_state_change.sh v1.0*\n*Source: data/metrics/free_model_probes.jsonl*"
print(json.dumps({
    "body": body,
    "alerts": alerts,
}))
PYEOF
)

BODY=$(echo "$HIVEMIND_PAYLOAD" | python3 -c "import json,sys; print(json.load(sys.stdin)['body'])")

if [[ "$DRY_RUN" == "true" ]]; then
    log "[DRY-RUN] Would post to Hivemind:"
    echo "$BODY" | tee -a "$ALERT_LOG"
    log "Alerts not sent (dry-run mode)"
    exit 0
fi

# === Post to Hivemind ======================================================
# Per M23 (failure integrity) + M8 (zero telemetry): no external HTTP calls.
# Use file-based handoff packets — the canonical Hivemind transport.
# The Hivemind server (omega-hub) auto-processes data/handoff/pending/*.json.

log "Writing handoff packet for Hivemind"

PKT_ID="alert-state-$(date -u +%Y%m%d%H%M%S)-$(printf '%04x' $RANDOM)"
PKT_FILE="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/handoff/pending/${PKT_ID}.json"
mkdir -p "$(dirname "$PKT_FILE")"

# Build payload: alerts JSON + body markdown
PAYLOAD_JSON=$(python3 << PYEOF
import json, os
alerts = $(echo "$ALERTS" | /usr/bin/python3 -c "import json,sys; print(repr(json.load(sys.stdin)))")
body = '''$BODY'''
packet = {
    "packet_id": "$PKT_ID",
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)",
    "source_channel": "opencode",
    "source_entity": "maat",
    "target_channel": "opencode",
    "target_entity": "maat",
    "task": "Provider state-change alert (probe-report-actions-20260827)",
    "context": body[:4000],
    "priority": 1,
    "intent": "alert",
    "alerts": alerts,
}
print(json.dumps(packet, ensure_ascii=False, indent=2))
PYEOF
)

echo "$PAYLOAD_JSON" > "$PKT_FILE"

if [[ -f "$PKT_FILE" && -s "$PKT_FILE" ]]; then
    log "Wrote handoff packet: $PKT_FILE ($(wc -c < "$PKT_FILE") bytes)"
    log "Hivemind server will process this packet on next sweep"
else
    log "ERROR: failed to write handoff packet"
    exit 1
fi

log "Alert processing complete ($ALERT_COUNT alert(s))"
