#!/usr/bin/env bash
# ==============================================================================
# OMEGA ENGINE — PRE-COMPACTION RITUAL
# ==============================================================================
# Captures full session state, evolution delta, and gnosis before context compaction.
# Run at end of every session, before /compact, or on shutdown.
#
# Usage: ./pre_compaction_ritual.sh [--session-id <id>] [--reason "..."] [--entity <name>] [--channel <name>] [--phase <phase>]
#   Entity attrs default to env (ENTITY, CHANNEL, PHASE) or sensible constants.
# ==============================================================================

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────
PROJECT_ROOT="/home/xnai/Documents/Projects/omega-engine-alpha"
GNSSIS_ROOT="${PROJECT_ROOT}/gnosis"
SESSIONS_DIR="${GNSSIS_ROOT}/sessions"
EVOLUTION_DIR="${GNSSIS_ROOT}/evolution"
IDENTITY_DIR="${GNSSIS_ROOT}/identity"
# File-safe session id uses dashes in the time section to avoid ':' in names;
# metadata timestamps must be strict ISO-8601 (parseable) — see CODE_QUALITY §2.
TIMESTAMP_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FILE_TS=$(date -u +"%Y-%m-%dT%H-%M-%SZ")
TIMESTAMP="${TIMESTAMP_ISO}"
# Entity attribution: every artifact records WHO ran the lock. Defaults come
# from env (ENTITY/CHANNEL/PHASE) so agents can set them per-run; a bare CLI
# call still records a useful, queryable identity instead of 'unknown'.
ENTITY="${ENTITY:-build}"
CHANNEL="${CHANNEL:-cli}"
PHASE="${PHASE:-unset}"

SESSION_ID="${1:-session-${FILE_TS}}"
REASON="${2:-End of session}"

# ─── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() { echo -e "${CYAN}[PRE-COMPACT]${NC} $*"; }
ok() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err() { echo -e "${RED}[ERR]${NC} $*"; }

# ─── Banner ───────────────────────────────────────────────────────────────────
echo
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║           🔱 OMEGA ENGINE — PRE-COMPACTION RITUAL                         ║"
echo "║                    Gnosis Lock Protocol v1.0                               ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo
log "Session ID: ${SESSION_ID}"
log "Timestamp:  ${TIMESTAMP}"
log "Reason:     ${REASON}"
log "Entity:     ${ENTITY} (channel: ${CHANNEL}, phase: ${PHASE})"
echo

# ─── Step 1: Capture Git State ────────────────────────────────────────────────
log "Step 1/8: Capturing Git state..."
GIT_STATE_FILE="${SESSIONS_DIR}/${SESSION_ID}_git_state.json"
{
  echo "{"
  echo "  \"timestamp\": \"${TIMESTAMP}\","
  echo "  \"session_id\": \"${SESSION_ID}\","
  echo "  \"entity\": \"${ENTITY}\","
  echo "  \"channel\": \"${CHANNEL}\","
  echo "  \"phase\": \"${PHASE}\","
  echo "  \"git\": {"
  if git -C "${PROJECT_ROOT}" rev-parse --git-dir >/dev/null 2>&1; then
    echo "    \"repo\": \"omega-engine-alpha\","
    echo "    \"branch\": \"$(git -C "${PROJECT_ROOT}" branch --show-current)\","
    echo "    \"commit\": \"$(git -C "${PROJECT_ROOT}" rev-parse HEAD)\","
    echo "    \"short_commit\": \"$(git -C "${PROJECT_ROOT}" rev-parse --short HEAD)\","
    echo "    \"dirty\": $(git -C "${PROJECT_ROOT}" status --porcelain | grep -q . && echo true || echo false),"
    echo "    \"status\": $(git -C "${PROJECT_ROOT}" status --porcelain | jq -R . | jq -s .),"
    echo "    \"recent_commits\": $(git -C "${PROJECT_ROOT}" log --oneline -10 | jq -R . | jq -s .)"
  else
    echo "    \"repo\": \"none\""
  fi
  echo "  }"
  echo "}"
} > "${GIT_STATE_FILE}"
ok "Git state saved to ${GIT_STATE_FILE}"

# ─── Step 2: Capture OpenCode Config ──────────────────────────────────────────
log "Step 2/8: Capturing OpenCode configuration..."
CONFIG_FILE="${SESSIONS_DIR}/${SESSION_ID}_opencode_config.json"
cp ~/.config/opencode/opencode.json "${CONFIG_FILE}.bak" 2>/dev/null || true
jq '.' ~/.config/opencode/opencode.json > "${CONFIG_FILE}" 2>/dev/null || cp ~/.config/opencode/opencode.json "${CONFIG_FILE}"
ok "OpenCode config saved to ${CONFIG_FILE}"

# ─── Step 3: Capture MCP Server Status ────────────────────────────────────────
log "Step 3/8: Capturing MCP server status..."
MCP_FILE="${SESSIONS_DIR}/${SESSION_ID}_mcp_status.json"
{
  echo "{"
  echo "  \"timestamp\": \"${TIMESTAMP}\","
  echo "  \"mcp_servers\": ["
  # Try to get MCP list via opencode if available (with 5s timeout)
  if command -v opencode >/dev/null 2>&1; then
    timeout 5 opencode mcp list --json 2>/dev/null | jq -c '.[] | {name: .name, type: .type, url: .url, enabled: .enabled, status: .status}' | paste -sd, - || echo "    {\"note\": \"opencode mcp list timed out or failed\"}"
  else
    echo "    {\"note\": \"opencode CLI not available\"}"
  fi
  echo "  ]"
  echo "}"
} > "${MCP_FILE}"
ok "MCP status saved to ${MCP_FILE}"

# ─── Step 4: Capture System State ─────────────────────────────────────────────
log "Step 4/8: Capturing system state..."
SYS_FILE="${SESSIONS_DIR}/${SESSION_ID}_system_state.json"
# Build JSON via python3 (robust escaping; no shell-quoting/array defects).
# zramctl/curl failures degrade to sane JSON instead of leaking shell output.
python3 - "${SYS_FILE}" "${TIMESTAMP}" <<'PYEOF'
import json, os, subprocess, sys

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=10).stdout.strip()
    except Exception:
        return "unknown"

out, ts = sys.argv[1], sys.argv[2]

mem = {"total": "unknown", "used": "unknown", "free": "unknown", "available": "unknown"}
swap = {"total": "unknown", "used": "unknown", "free": "unknown"}
models = []

zram_lines = sh("zramctl --output NAME,SIZE,ALGORITHM,PRIORITY --noheadings 2>/dev/null")
zram = [w.split() for w in zram_lines.splitlines() if w.strip()] or []

free_out = sh("free -h")
for line in free_out.splitlines():
    parts = line.split()
    if parts and parts[0] == "Mem:":
        mem = {"total": parts[1], "used": parts[2], "free": parts[3], "available": parts[4] if len(parts) > 4 else "unknown"}
    elif parts and parts[0] == "Swap:":
        swap = {"total": parts[1], "used": parts[2], "free": parts[3] if len(parts) > 3 else "unknown"}

try:
    import urllib.request
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
        data = json.load(r)
    models = [{"name": m.get("name"), "size": m.get("size")} for m in data.get("models", [])]
except Exception:
    models = []

state = {
    "timestamp": ts,
    "hostname": sh("hostname"),
    "kernel": sh("uname -r"),
    "uptime": sh("uptime -p"),
    "cpu": {
        "model": sh("lscpu | grep 'Model name' | cut -d: -f2 | xargs"),
        "governor": sh("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo unknown"),
        "epp": sh("cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference 2>/dev/null || echo unknown")
    },
    "memory": mem,
    "swap": swap,
    "zram": [{"name": z[0], "size": z[1] if len(z) > 1 else "unknown",
              "algorithm": z[2] if len(z) > 2 else "unknown",
              "priority": z[3] if len(z) > 3 else "unknown"} for z in zram],
    "ollama": {
        "active": sh("systemctl is-active ollama 2>/dev/null") == "active",
        "models": models
    }
}

with open(out, "w") as f:
    json.dump(state, f, indent=2)
PYEOF
if jq -e . "${SYS_FILE}" >/dev/null 2>&1; then
  ok "System state saved to ${SYS_FILE}"
else
  err "System state JSON INVALID: ${SYS_FILE}"
fi

# ─── Step 5: Capture Session Narrative (Markdown) ─────────────────────────────
log "Step 5/8: Capturing session narrative..."
NARRATIVE_FILE="${SESSIONS_DIR}/${SESSION_ID}_narrative.md"
{
  echo "# Session Narrative: ${SESSION_ID}"
  echo
  echo "**Timestamp:** ${TIMESTAMP}  "
  echo "**Reason:** ${REASON}  "
  echo "**Host:** $(hostname)  "
  echo "**Agent:** ${ENTITY} (channel: ${CHANNEL})  "
  echo "**Phase:** ${PHASE}  "
  echo
  echo "---"
  echo
  echo "## Session Summary"
  echo
  echo "TODO: Fill in manually or via LLM summary of conversation"
  echo
  echo "## Key Decisions"
  echo
  echo "- "
  echo
  echo "## Code Changes"
  echo
  echo "- "
  echo
  echo "## Blockers & Open Questions"
  echo
  echo "- "
  echo
  echo "## Next Session Priorities"
  echo
  echo "1. "
  echo "2. "
  echo "3. "
  echo
  echo "## Gnosis Gained"
  echo
  echo "- "
  echo
} > "${NARRATIVE_FILE}"
ok "Session narrative template saved to ${NARRATIVE_FILE}"

# ─── Step 6: Compute Evolution Delta ──────────────────────────────────────────
log "Step 6/8: Computing evolution delta..."
LATEST_EVOLUTION=$(ls -1t "${EVOLUTION_DIR}"/evolution_*.json 2>/dev/null | head -1 || echo "")
EVOLUTION_FILE="${EVOLUTION_DIR}/evolution_${TIMESTAMP}.json"
{
  echo "{"
  echo "  \"timestamp\": \"${TIMESTAMP}\","
  echo "  \"session_id\": \"${SESSION_ID}\","
  echo "  \"entity\": \"${ENTITY}\","
  echo "  \"channel\": \"${CHANNEL}\","
  echo "  \"phase\": \"${PHASE}\","
  echo "  \"previous_evolution\": \"${LATEST_EVOLUTION}\","
  echo "  \"delta\": {"
  echo "    \"files_changed\": $(git -C "${PROJECT_ROOT}" diff --name-only 2>/dev/null | wc -l),"
  echo "    \"lines_added\": $(git -C "${PROJECT_ROOT}" diff --numstat 2>/dev/null | awk '{sum+=$1} END {print sum+0}'),"
  echo "    \"lines_removed\": $(git -C "${PROJECT_ROOT}" diff --numstat 2>/dev/null | awk '{sum+=$2} END {print sum+0}'),"
  echo "    \"new_files\": $(git -C "${PROJECT_ROOT}" ls-files --others --exclude-standard 2>/dev/null | wc -l),"
  echo "    \"config_changes\": $(git -C "${PROJECT_ROOT}" diff --name-only 2>/dev/null | grep -E '\.(json|md|sh|py|yaml|yml)$' | wc -l)"
  echo "  },"
  echo "  \"insights\": ["
  echo "    \"Session ${SESSION_ID} completed with reason: ${REASON}\""
  echo "  ]"
  echo "}"
} > "${EVOLUTION_FILE}"
ok "Evolution delta saved to ${EVOLUTION_FILE}"

# ─── Step 6b: Machine-generate narrative summary from captured state ──────────
# CLI locks (make gnosis-lock) cannot run the interactive question tool, so the
# narrative template ends up all-TODO. Reuse the captured git/evolution state to
# auto-fill Session Summary + Code Changes so even a CLI lock is a useful
# continuity record. Human-reflection fields (Decisions/Gnosis) stay TODO for
# the skill run or the next session.
log "Step 6.5: Auto-generating narrative summary from state..."
python3 - "${NARRATIVE_FILE}" "${GIT_STATE_FILE}" "${EVOLUTION_FILE}" "${ENTITY}" "${CHANNEL}" "${PHASE}" "${SESSION_ID}" "${TIMESTAMP}" "${REASON}" <<'PYEOF'
import json, sys

narr_path, git_path, evo_path = sys.argv[1], sys.argv[2], sys.argv[3]
entity, channel, phase = sys.argv[4], sys.argv[5], sys.argv[6]
sid, ts, reason = sys.argv[7], sys.argv[8], sys.argv[9]

def load(p, default):
    try:
        return json.load(open(p))
    except Exception:
        return default

git = load(git_path, {})
evo = load(evo_path, {})
git_inner = git.get("git", {})
delta = evo.get("delta", {})

commits = git_inner.get("recent_commits", [])
changes = git_inner.get("status", [])
summary_lines = [
    f"**Machine-generated continuity record** (entity {entity}, channel {channel}, phase {phase}).",
    f"Reason: {reason}",
    "",
    f"Commit: `{git_inner.get('short_commit', 'unknown')}` on `{git_inner.get('branch', 'unknown')}`"
    + (f" — {git_inner['commit']}" if git_inner.get("commit") else ""),
]
if delta:
    summary_lines.append(
        f"Delta: {delta.get('files_changed', 0)} files, "
        f"+{delta.get('lines_added', 0)}/-{delta.get('lines_removed', 0)} lines, "
        f"{delta.get('new_files', 0)} new files."
    )
code_lines = []
if commits:
    code_lines.append("Recent commits:")
    for c in commits[:5]:
        code_lines.append(f"- `{c}`")
if changes:
    code_lines.append("")
    code_lines.append("Working-tree changes:")
    for ch in changes:
        code_lines.append(f"- {ch}")

narr = open(narr_path).read()
narr = narr.replace(
    "TODO: Fill in manually or via LLM summary of conversation",
    "\n".join(summary_lines),
    1,
)
if code_lines:
    # Replace the "- " under Code Changes with auto-captured entries.
    narr = narr.replace("## Code Changes\n\n- ", "## Code Changes\n\n" + "\n".join(code_lines) + "\n", 1)
open(narr_path, "w").write(narr)
print(f"    narrative summary auto-filled ({len(summary_lines)+len(code_lines)} lines)")
PYEOF
ok "Narrative summary auto-generated"

# ─── Step 7: Update Persistent Identity ───────────────────────────────────────
log "Step 7/8: Updating persistent identity..."
IDENTITY_FILE="${IDENTITY_DIR}/identity.json"
CURRENT_SESSIONS=$(jq -r '.session_count // 0' "${IDENTITY_FILE}" 2>/dev/null || echo 0)
NEW_SESSION_COUNT=$((CURRENT_SESSIONS + 1))
# Per-entity continuity: update the entity's own entry (session_count,
# last_session, last_phase) inside the global identity, preserving others.
# Keeps the flat storage layout; entity views are queries, not folders.
ENTITY_KEY=$(jq -r --arg e "${ENTITY}" '.entities[$e] // {}' "${IDENTITY_FILE}" 2>/dev/null || echo '{}')
ENTITY_COUNT=$(jq -r '.session_count // 0' <<<"${ENTITY_KEY}" 2>/dev/null || echo 0)
NEW_ENTITY_COUNT=$((ENTITY_COUNT + 1))
{
  echo "{"
  echo "  \"entity\": \"Omega Engine Alpha Build Agent\","
  echo "  \"inception\": \"2026-09-08T00:00:00Z\","
  echo "  \"last_updated\": \"${TIMESTAMP}\","
  echo "  \"session_count\": ${NEW_SESSION_COUNT},"
  echo "  \"current_session\": \"${SESSION_ID}\","
  echo "  \"current_entity\": \"${ENTITY}\","
  echo "  \"current_machine\": \"ASUS ExpertBook P1503CVA (i7-13620H)\","
  echo "  \"federation_role\": \"Node 1 - Compute Vanguard\","
  echo "  \"partner_node\": \"HP Pavilion (Node 0 - Archival Bastion)\","
  echo "  \"core_principles\": ["
  echo "    \"Measure, don't guess\","
  echo "    \"Document the trap\","
  echo "    \"Single-channel reality\","
  echo "    \"Hybrid CPU respect\","
  echo "    \"Living document\""
  echo "  ],"
  echo "  \"key_achievements\": ["
  echo "    \"P-core pin trap documented (0.5 t/s disaster)\","
  echo "    \"Ollama tuned: 13.4 t/s on phi4-mini\","
  echo "    \"MAX_LOADED_MODELS=1 for 16GB single-channel\","
  echo "    \"Dynamic Big Pickle: 1M context ceiling\","
  echo "    \"P2P Omegaverse Federation architected\""
  echo "  ],"
  echo "  \"open_quests\": ["
  echo "    \"HP Node 0 federation live\","
  echo "    \"Tailscale mesh operational\","
  echo "    \"Secure key management pattern\","
  echo "    \"Agent team migration complete\""
  echo "  ],"
  echo "  \"entities\": {"
  # Merge existing per-entity entries, updating THIS entity's record.
  jq -r --arg e "${ENTITY}" --arg s "${SESSION_ID}" --arg p "${PHASE}" --argjson n "${NEW_ENTITY_COUNT}" '
    .entities // {} | .[$e] = {session_count: $n, last_session: $s, last_phase: $p} |
    to_entries | sort_by(.key) | map("    \"" + .key + "\": " + (.value | tostring)) | join(",\n")
  ' "${IDENTITY_FILE}" 2>/dev/null || echo "    \"${ENTITY}\": {\"session_count\": ${NEW_ENTITY_COUNT}, \"last_session\": \"${SESSION_ID}\", \"last_phase\": \"${PHASE}\"}"
  echo "  }"
  echo "}"
} > "${IDENTITY_FILE}"
ok "Identity updated: ${NEW_SESSION_COUNT} sessions logged (entity ${ENTITY} → #${NEW_ENTITY_COUNT})"

# ─── Step 8: Create Session Manifest ──────────────────────────────────────────
log "Step 8/8: Creating session manifest..."
MANIFEST_FILE="${SESSIONS_DIR}/${SESSION_ID}_manifest.json"
{
  echo "{"
  echo "  \"session_id\": \"${SESSION_ID}\","
  echo "  \"timestamp\": \"${TIMESTAMP}\","
  echo "  \"reason\": \"${REASON}\","
  echo "  \"entity\": \"${ENTITY}\","
  echo "  \"channel\": \"${CHANNEL}\","
  echo "  \"phase\": \"${PHASE}\","
  echo "  \"artifacts\": {"
  echo "    \"git_state\": \"${GIT_STATE_FILE}\","
  echo "    \"opencode_config\": \"${CONFIG_FILE}\","
  echo "    \"mcp_status\": \"${MCP_FILE}\","
  echo "    \"system_state\": \"${SYS_FILE}\","
  echo "    \"narrative\": \"${NARRATIVE_FILE}\","
  echo "    \"evolution\": \"${EVOLUTION_FILE}\""
  echo "  },"
  echo "  \"identity_updated\": true,"
  echo "  \"ready_for_compaction\": true"
  echo "}"
} > "${MANIFEST_FILE}"
ok "Manifest saved to ${MANIFEST_FILE}"

# ─── Step 9: Log SESSION_END to the evolution log ────────────────────────────
log "Logging SESSION_END evolution event..."
EVOLUTION_SCRIPT="${PROJECT_ROOT}/scripts/compaction/evolution_log.py"
if python3 "${EVOLUTION_SCRIPT}" log SESSION_END "${SESSION_ID}" \
    "Pre-compaction ritual: ${REASON}" \
    --metadata "{\"manifest\": \"${MANIFEST_FILE}\", \"sessions\": ${NEW_SESSION_COUNT}, \"entity\": \"${ENTITY}\", \"channel\": \"${CHANNEL}\", \"phase\": \"${PHASE}\"}" \
    --tags ritual session-end >/dev/null 2>&1; then
  ok "Evolution event logged"
else
  warn "Could not log evolution event (evolution log may be degraded)"
fi

# ─── Completion ───────────────────────────────────────────────────────────────
echo
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ PRE-COMPACTION RITUAL COMPLETE                                         ║"
echo "║                                                                            ║"
echo "║  Session ${SESSION_ID} fully captured.                                     ║"
echo "║  All gnosis locked to disk. Identity evolved to session #${NEW_SESSION_COUNT}.      ║"
echo "║  Safe to run /compact or shutdown.                                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo
log "Manifest: ${MANIFEST_FILE}"
log "Next: Review ${NARRATIVE_FILE} and fill narrative, then compact."