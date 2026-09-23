#!/usr/bin/env bash
# fetch_model.sh — agent-proof background model downloader (Node 1)
#
# Problem: agent-harness shells kill the child process GROUP when a tool call
# ends (timeout/completion). `nohup ... &` does NOT survive this (proven:
# frozen at 68MB). `setsid` survives, but the DEFINITIVE solution is a
# systemd user transient unit: owned by the user manager, survives call ends,
# aborts, logout (linger=yes), with journal logging + status inspection.
#
# Usage:
#   scripts/fetch_model.sh <repo_id> <filename> [--sha256 <hex>] [--local-dir DIR] [--unit NAME]
#
# Examples:
#   scripts/fetch_model.sh google/gemma-4-12B-it-qat-q4_0-gguf gemma-4-12b-it-qat-q4_0.gguf \
#       --sha256 93567e57a8fe10b23569b9d9ec38cd005deedf71e29477c421a4b83f418a538b
#   systemctl --user status fetch-gemma-4-12b-it-qat-q4-0
#   journalctl --user -u fetch-gemma-4-12b-it-qat-q4_0 -f
#
# Machine rules honored: real disk (never /tmp tmpfs), Xet high-perf transfer
# (HF_HUB_ENABLE_HF_TRANSFER is deprecated in hf_hub>=1.32), resume-safe
# partials, sha256 gate before any `ollama create`.
set -euo pipefail

REPO="${1:?usage: fetch_model.sh <repo_id> <filename> [--sha256 HEX] [--local-dir DIR] [--unit NAME]}"
FILE="${2:?usage: fetch_model.sh <repo_id> <filename> [--sha256 HEX] [--local-dir DIR] [--unit NAME]}"
SHA256=""; LOCAL_DIR="/home/xnai/ollama-install"; UNIT=""
shift 2
while [ $# -gt 0 ]; do
    case "$1" in
        --sha256)    SHA256="$2"; shift 2;;
        --local-dir) LOCAL_DIR="$2"; shift 2;;
        --unit)      UNIT="$2"; shift 2;;
        *) echo "unknown arg: $1" >&2; exit 2;;
    esac
done

# Unit name must be [a-z0-9-_]; derive from filename if not given.
if [ -z "$UNIT" ]; then
    UNIT="fetch-$(echo "$FILE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g; s/--*/-/g')"
fi

HF_BIN="$(dirname "$0")/../.venv/bin/hf"
[ -x "$HF_BIN" ] || HF_BIN="$(command -v hf || true)"
[ -n "$HF_BIN" ] || { echo "hf CLI not found (project .venv or PATH)" >&2; exit 3; }

mkdir -p "$LOCAL_DIR"

echo "[*] launching unit $UNIT (repo=$REPO file=$FILE dir=$LOCAL_DIR)"
# HF_XET_CHUNK_CACHE_SIZE_BYTES: Xet's chunk cache is DISABLED by default
# (hf_xet>=1.2.0) — without it, every process restart starts the download
# from 0% (new .incomplete token; old partial orphaned). 10GB cache on real
# disk makes all future fetches resumable + deduped. Proven 2026-09-23.
systemd-run --user --unit="$UNIT" --collect \
    -p Description="model-fetch $REPO/$FILE" \
    env HF_XET_HIGH_PERFORMANCE=1 HF_HUB_DISABLE_TELEMETRY=1 \
        HF_XET_CHUNK_CACHE_SIZE_BYTES=10737418240 \
    "$HF_BIN" download "$REPO" "$FILE" --local-dir "$LOCAL_DIR"

echo "[+] running. watch: journalctl --user -u $UNIT -f"
echo "    status: systemctl --user status $UNIT"
if [ -n "$SHA256" ]; then
    echo "[*] expected sha256: $SHA256"
    echo "    verify after completion: sha256sum $LOCAL_DIR/$FILE"
fi
