#!/bin/bash
# collect_node0.sh — Node 0 OpenCode/Zen/OpenRouter diagnostic collector.
#
# Carried by USB to Node 0, run there, bundle carried back. Collects configs,
# provider state, DNS evidence, key VALIDITY (HTTP codes only) and optional
# repro transcripts. NEVER writes secret values into the bundle: .env/JSON
# values are replaced by shape markers, auth.json by structure-only inventory,
# API-keys.md is never copied (keys are tested in-memory, only codes recorded).
#
# Usage:
#   bash collect_node0.sh [--out DIR] [--project DIR] [--keys PATH]
#                         [--repro] [--spark-id ID] [--or-model ID]
#   Defaults: --project ~/Documents/Xoe-NovAi/omega-engine
#             --keys    ~/Desktop/API-keys.md
#             --spark-id opencode/muse-spark-1.2-contributor-free
#   --repro runs live `opencode run` captures (tiny quota spend). Without it,
#   collection only (zero spend). --or-model additionally repros OpenRouter
#   with API-keys.md key#1 (implies --repro).
#
#   Copy the resulting directory (or .tar.gz) onto the USB stick.
set -u
# NOTE: no `set -e`, no `set -x` (trace would leak secrets). Every section
# is guarded and failures are recorded, not fatal.

OUT=""; PROJECT="$HOME/Documents/Xoe-NovAi/omega-engine"
KEYS="$HOME/Desktop/API-keys.md"; REPRO=0
SPARK_ID="opencode/muse-spark-1.2-contributor-free"; OR_MODEL=""
while [[ $# -gt 0 ]]; do case "$1" in
  --out) OUT="$2"; shift 2 ;;
  --project) PROJECT="$2"; shift 2 ;;
  --keys) KEYS="$2"; shift 2 ;;
  --repro) REPRO=1; shift ;;
  --spark-id) SPARK_ID="$2"; shift 2 ;;
  --or-model) OR_MODEL="$2"; REPRO=1; shift 2 ;;
  *) echo "unknown arg: $1" >&2; exit 1 ;;
esac; done
[[ -z "$OUT" ]] && OUT="./node0-collect-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT"

# ── helpers ──────────────────────────────────────────────────────────
# sec <nn> <file> <description> — runs stdin-script body, captures all output.
have() { command -v "$1" > /dev/null 2>&1; }
TIMO() { if have timeout; then timeout "$@"; else "${@:2}"; fi; }

# scrub_json: stdin JSON -> stdout JSON with secret values replaced by shapes.
scrub_json() {
  if have python3; then python3 -c '
import json,sys,re
SENS=re.compile(r"key|token|secret|passwd|password|auth|bearer|credential|apikey|api_key",re.I)
VAL =re.compile(r"sk-(or|ant)-|ctx7sk-|^fc-|pk_(live|test)|xox[bap]-|ghp_|gsk_|Bearer |eyJ[A-Za-z0-9_-]{10,}")
def shape(v):
    s=str(v); return "<redacted len=%d head=%s>"%(len(s),s[:4])
def walk(o,k=""):
    if isinstance(o,dict): return {kk:walk(v,kk) for kk,v in o.items()}
    if isinstance(o,list): return [walk(v,k) for v in o]
    if isinstance(o,str) and (SENS.search(k or "") or VAL.search(o)): return shape(o)
    return o
try: print(json.dumps(walk(json.load(sys.stdin)),indent=1))
except Exception as e: print("<unparsable json: %s>"%e)'
  else
    echo "<no python3 — sed fallback, verify before trusting>";
    sed -E 's/((key|token|secret|passwd|password|auth)[^":]*["'\'']?\s*[:=]\s*["'\'']?)[^"'\'',}]+/\1<redacted>/gI'
  fi
}

# env_shape: stdin KEY=val lines -> KEY=<redacted len=N> (names only).
env_shape() { awk -F= '{v=substr($0,length($1)+2); gsub(/.*/,"",v); print $1"=<redacted len="length(substr($0,length($1)+2))">"}' | grep -v "^#"; }

sec() { # sec <file> <title> ; body on stdin via heredoc arg is awkward — use: sec file title <<'EOF' ... EOF
  local f="$OUT/$1"; shift; local title="$1"; shift
  { echo "### $title"; echo "### collected $(date -u +%FT%TZ) on $(hostname)"; echo; cat; } > "$f" 2>&1
  echo "wrote $f"
}

# ── 00 meta ──────────────────────────────────────────────────────────
sec "00_meta.txt" "host identity + tool versions" <<EOF
user=$(id -un) home=$HOME
hostname=$(hostname)
os=$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d= -f2)
opencode_bin=$(command -v opencode || echo MISSING)
opencode_version=$({ opencode --version 2>&1 | head -1; } || echo UNKNOWN)
python3=$({ python3 --version 2>&1; } || echo MISSING)
node=$({ node --version 2>&1; } || echo MISSING)
tailscale=$({ tailscale version 2>&1 | head -1; } || echo MISSING)
EOF

# ── 01 env (shapes only) ─────────────────────────────────────────────
sec "01_env.txt" "effective-path + provider/proxy env (NAMES only, values redacted)" <<EOF
XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-<unset>} XDG_DATA_HOME=${XDG_DATA_HOME:-<unset>}
OPENCODE_CONFIG=${OPENCODE_CONFIG:-<unset>} OPENCODE_CONFIG_DIR=${OPENCODE_CONFIG_DIR:-<unset>}
--- provider/proxy-ish vars (name=<redacted len>) ---
$(env | grep -iE "proxy|openai|anthropic|openrouter|zen|exa|firecrawl|parallel|context7|api[_-]?key|token|auth" | env_shape || echo "<none set>")
EOF

# ── 02 config inventory ──────────────────────────────────────────────
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/opencode"
sec "02_config_inventory.txt" "config dirs + project dir listings" <<EOF
CONF_DIR=$CONF_DIR DATA_DIR=$DATA_DIR PROJECT=$PROJECT
--- global --- $(ls -la "$CONF_DIR" 2>&1)
--- global plugins --- $(ls "$CONF_DIR/plugins" 2>&1 || echo "<none>")
--- data dir --- $(ls -la "$DATA_DIR" 2>&1 || echo "<missing>")
--- project root --- $(ls -la "$PROJECT" 2>&1 || echo "<PROJECT DIR MISSING>")
--- project .opencode --- $(ls -la "$PROJECT/.opencode" 2>&1 || echo "<none>")
--- log files --- $(find "$DATA_DIR" -name "*.log" 2>/dev/null | head || echo "<none found>")
EOF

# ── 03 configs scrubbed ──────────────────────────────────────────────
{
  echo "### scrubbed config copies (values -> shape markers)"
  for f in "$CONF_DIR/opencode.json" "$CONF_DIR/opencode.jsonc" "$CONF_DIR/tui.json" \
           "$PROJECT/opencode.json" "$PROJECT/opencode.jsonc" "$PROJECT/tui.json" \
           "${OPENCODE_CONFIG:-/nonexistent}"; do
    echo; echo "===== FILE: $f ====="
    if [[ -f "$f" ]]; then scrub_json < "$f"; else echo "<absent>"; fi
  done
} > "$OUT/03_configs_scrubbed.txt" 2>&1
echo "wrote $OUT/03_configs_scrubbed.txt"
{ echo "### .env NAMES + shapes (values never copied)";
  if [[ -f "$CONF_DIR/.env" ]]; then grep -v "^#" "$CONF_DIR/.env" | env_shape; else echo "<no .env>"; fi; } > "$OUT/04_env_shapes.txt" 2>&1
echo "wrote $OUT/04_env_shapes.txt"

# ── 05 auth structure only ───────────────────────────────────────────
{
  echo "### auth.json STRUCTURE (provider names + field names + value shapes; no values)"
  if [[ -f "$CONF_DIR/auth.json" ]]; then
    if have python3; then
      python3 - "$CONF_DIR/auth.json" <<'PYEOF'
import json,sys
a=json.load(open(sys.argv[1]))
def shape(v):
    s=str(v); return "len=%d head=%s"%(len(s),s[:4]) if len(s)>8 else "<present>"
def walk(o):
    if isinstance(o,dict): return {k:walk(v) for k,v in o.items()}
    if isinstance(o,list): return [walk(v) for v in o]
    return shape(o) if isinstance(o,str) else o
print(json.dumps(walk(a),indent=1))
PYEOF
    else
      echo "<no python3 — cannot inventory safely; skipping>"
    fi
  else
    echo "<no auth.json>"
  fi
} > "$OUT/05_auth_structure.txt" 2>&1
echo "wrote $OUT/05_auth_structure.txt"

# ── 06 models catalog ────────────────────────────────────────────────
{ echo "### opencode models (IDs, not display names)";
  if have opencode; then TIMO 60 opencode models 2>&1 | head -80; else echo "<no opencode>"; fi
  echo; echo "### spark entries:"; TIMO 60 opencode models 2>/dev/null | grep -i spark || echo "<none>"
  echo; echo "### providers state:"; TIMO 60 opencode providers list 2>&1 | scrub_json | head -40 || echo "<providers list unavailable>"
} > "$OUT/06_models.txt" 2>&1
echo "wrote $OUT/06_models.txt"

# ── 07 DNS ───────────────────────────────────────────────────────────
sec "07_dns.txt" "name resolution evidence" <<EOF
resolver: $(grep -v "^#" /etc/resolv.conf 2>/dev/null | head -3 | tr '\n' ' ')
$(for h in api.openrouter.ai openrouter.ai api.exa.ai mcp.context7.com mcp.firecrawl.dev; do
  printf "%s: " "$h"
  if have getent && TIMO 8 getent hosts "$h" > /dev/null 2>&1; then echo resolves; else echo FAILS; fi
done)
--- via 1.1.1.1: api.openrouter.ai ---
$(have nslookup && TIMO 10 nslookup api.openrouter.ai 1.1.1.1 2>&1 | grep -E "Address|NXDOMAIN|can't" | head -3 || echo "<no nslookup>")
EOF

# ── 08 openrouter keys: validity codes only ──────────────────────────
{
  echo "### API-keys.md OpenRouter key validity (HTTP codes ONLY — values never recorded)"
  echo "### keys file: $KEYS (NOT copied into bundle)"
  if [[ -f "$KEYS" ]]; then
    n=$(grep -o "sk-or-v1-[A-Za-z0-9_.-]*" "$KEYS" | wc -l); echo "sk-or-v1 keys found: $n"
    grep -o "sk-or-v1-[A-Za-z0-9_.-]*" "$KEYS" | nl -ba | while read -r idx key; do
      code=$(TIMO 20 curl -sS -m 15 -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $key" https://openrouter.ai/api/v1/models 2>/dev/null || echo "000")
      echo "key#$idx: HTTP $code"; unset key
    done
    echo "--- unauthenticated apex probe:"; TIMO 20 curl -sS -m 15 -o /dev/null -w "models endpoint: %{http_code}\n" https://openrouter.ai/api/v1/models 2>&1
  else echo "<keys file absent: $KEYS>"
  fi
} > "$OUT/08_openrouter_keys.txt" 2>&1
echo "wrote $OUT/08_openrouter_keys.txt"

# ── 09 tailscale ─────────────────────────────────────────────────────
sec "09_tailscale.txt" "tailnet + exit-node state (Zen pool evidence)" <<EOF
$(have tailscale && TIMO 30 tailscale status 2>&1 | head -12 || echo "<no tailscale>")
$(have tailscale && echo "--- exit-node prefs:" && TIMO 20 tailscale debug prefs 2>&1 | grep -iE "exit|runssh" | head -5 || true)
EOF

# ── 10 repro (opt-in spend) ──────────────────────────────────────────
{
  echo "### live repro transcripts (REPRO=$REPRO)"
  if [[ "$REPRO" == "1" ]] && have opencode; then
    echo "===== SPARK: opencode run -m $SPARK_ID ====="
    TIMO 150 opencode run -m "$SPARK_ID" "reply with exactly: PONG" 2>&1 | head -30
    echo; echo "===== exit: $? ====="
    if [[ -n "$OR_MODEL" ]]; then echo; echo "===== OPENROUTER: -m $OR_MODEL (key#1) ====="
      K1=$(grep -o "sk-or-v1-[A-Za-z0-9_.-]*" "$KEYS" 2>/dev/null | head -1)
      if [[ -n "${K1:-}" ]]; then OPENROUTER_API_KEY="$K1" TIMO 150 opencode run -m "$OR_MODEL" "reply with exactly: PONG" 2>&1 | head -30; unset K1; else echo "<no key#1>"; fi
    fi
  else echo "<repro skipped (run with --repro to enable; tiny quota spend)>"
  fi
} > "$OUT/10_repro.txt" 2>&1
echo "wrote $OUT/10_repro.txt"

# ── 11 self-audit: no full secrets in bundle ─────────────────────────
{
  echo "### self-audit: full-length secret patterns must NOT appear in bundle"
  if grep -rE -e "sk-or-v1-[A-Za-z0-9_.-]{20,}" -e "sk-ant-[A-Za-z0-9_.-]{20,}" -e "ctx7sk-[A-Za-z0-9_.-]{20,}" -e "fc-[a-f0-9]{30,}" -e "BEGIN PRIVATE KEY" "$OUT" 2>/dev/null; then
    echo "RESULT: FLAG — full secret present, DO NOT TRANSPORT, rerun after fixing scrub"
  else echo "RESULT: CLEAN — no full-length secrets in bundle"
  fi
} > "$OUT/11_audit.txt" 2>&1
cat "$OUT/11_audit.txt"

# ── 12 manifest + tarball ────────────────────────────────────────────
sec "12_manifest.txt" "bundle manifest" <<EOF
flags used: project=$PROJECT keys=$KEYS repro=$REPRO spark=$SPARK_ID or_model=${OR_MODEL:-<none>}
redaction policy: config values -> shape markers; auth.json -> structure only;
API-keys.md never copied (codes only); repro transcripts may contain model chatter only.
files: $(ls "$OUT" | tr '\n' ' ')
size: $(du -sh "$OUT" | cut -f1)
deliver: copy this directory (or the .tar.gz) onto the USB stick.
EOF
tar czf "$OUT.tar.gz" -C "$(dirname "$OUT")" "$(basename "$OUT")" 2>/dev/null && echo "tarball: $OUT.tar.gz ($(du -h "$OUT.tar.gz" | cut -f1))"
echo "DONE: bundle at $OUT"
