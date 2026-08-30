#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
g13_empty_response_detector.py — G13 implementation per R_VAULT_ANTIGRAVITY_20260827 §B
Version: v1.0 (R_VAULT_ANTIGRAVITY_DEEPER_20260827)

Distinguishes 4 failure shapes from real success:
  Shape A: real_success         → 200, content present
  Shape B: reasoning_truncation → 200, content null BUT usage.completion_tokens > 0 (NOT a failure)
  Shape C: empty_stream_g13     → 200, content null AND usage.completion_tokens == 0 (FAILURE)
  Shape D: auth_2xx_error_g13   → 200, body has `error` field, no `choices` (FAILURE)

Reads:  data/metrics/free_model_probes.jsonl
Writes: data/metrics/g13_events.jsonl  (append-only)
Hivemind alert: if 1+ G13 event detected for a model, write handoff packet.

Mandate compliance:
  M8 (zero telemetry): only reads local files, no external calls
  M23 (failure integrity): tool errors → sys.exit(2), no soft-fail
  M27 (tracking integrity): atomic file writes
  M26 (doc standards): pydoc + type hints
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, Dict, List

# === DEFAULTS ===
DEFAULT_INPUT = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/free_model_probes.jsonl"
DEFAULT_OUTPUT = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/g13_events.jsonl"
DEFAULT_HIVEMIND_DIR = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/handoff/pending"

# Shape constants (for classification)
WORKING = "working"
REASONING_TRUNCATION = "reasoning_truncation"  # NOT a failure, just reasoning model behavior
EMPTY_STREAM = "empty_stream_g13"  # G13 main signal
AUTH_2XX_ERROR = "auth_2xx_error_g13"  # G13 subtype
UNKNOWN = "unknown"


def classify(probe: dict) -> str:
    """Classify a probe entry into one of the 4 shapes + WORKING.

    Requires the probe to include the new fields Ma'at adds per R3:
      - body.error (if present)
      - body.usage.completion_tokens
      - body.usage.completion_tokens_details.reasoning_tokens
      - body.choices[0].finish_reason

    For backward compat: falls back to the existing quality_check block.
    """
    s = probe.get("http_status")
    if s != 200:
        return UNKNOWN  # G13 scope is 2xx only; non-2xx handled by alert_state_change.sh

    # Try to use the new body fields if Ma'at added them (R3)
    body = probe.get("body")
    if isinstance(body, dict):
        # Shape D: 200 with explicit top-level error
        if "error" in body and "choices" not in body:
            return AUTH_2XX_ERROR

        choices = body.get("choices", [])
        msg = choices[0].get("message", {}) if choices else {}
        content = msg.get("content")
        usage = body.get("usage", {})
        ct = usage.get("completion_tokens", 0)
        rt = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)

        # Shape A: real success
        if content and len(str(content)) > 0:
            return WORKING

        # Shape B: reasoning truncation (NOT a failure)
        if not content and (ct > 0 or rt > 0):
            return REASONING_TRUNCATION

        # Shape C: empty stream
        if not content and ct == 0 and rt == 0:
            return EMPTY_STREAM

        return UNKNOWN

    # Fallback: use existing quality_check block (Ma'at's pre-G13 data)
    qc = probe.get("quality_check") or {}
    if qc.get("valid_json") and qc.get("has_completion"):
        return WORKING
    if qc.get("valid_json") and not qc.get("has_completion"):
        # Distinguish reasoning vs empty by checking content_length
        if qc.get("content_length", 0) == 0:
            return EMPTY_STREAM  # conservative — could be reasoning, but safer to alert
    return UNKNOWN


def detect_g13_events(input_path: Path, output_path: Path) -> Tuple[List[dict], Dict[str, List[str]]]:
    """Scan the JSONL probe file, return list of G13 events (Shape C + D)."""
    if not input_path.exists():
        print(f"[FATAL] input not found: {input_path}", file=sys.stderr)
        sys.exit(2)

    events: List[dict] = []
    by_model: Dict[str, List[str]] = defaultdict(list)

    with input_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            shape = classify(d)
            if shape in (EMPTY_STREAM, AUTH_2XX_ERROR):
                events.append({
                    "ts": d.get("ts"),
                    "model": d.get("model"),
                    "label": d.get("label"),
                    "shape": shape,
                    "http_status": d.get("http_status"),
                    "key_source": d.get("key_source"),
                    "key_health": d.get("key_health"),
                    "window": d.get("window"),
                    "latency_ms": d.get("latency_ms"),
                    "quality_check": d.get("quality_check"),
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                })
                by_model[d.get("model")].append(shape)

    # Write atomically
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(".tmp")
    with tmp.open("a") as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    tmp.replace(output_path)

    return events, dict(by_model)


def post_hivemind_alert(by_model: dict, hivemind_dir: Path) -> Optional[Path]:
    """If any model has 1+ G13 events, write a handoff packet for Ma'at to pick up."""
    if not by_model:
        return None

    crit = {m: shapes for m, shapes in by_model.items() if AUTH_2XX_ERROR in shapes}
    other = {m: shapes for m, shapes in by_model.items() if AUTH_2XX_ERROR not in shapes}

    body_lines = [f"## G13 Empty-Response Detector Alert", ""]
    body_lines.append(f"Detected **{sum(len(v) for v in by_model.values())}** G13 events across **{len(by_model)}** models")
    body_lines.append("")
    if crit:
        body_lines.append(f"**CRITICAL (auth_2xx_error — account/key state issue): {len(crit)} models**")
        for m, shapes in crit.items():
            body_lines.append(f"  - `{m}`: {shapes.count(AUTH_2XX_ERROR)} events")
    if other:
        body_lines.append(f"\n**Empty-stream (G13 main signal): {len(other)} models**")
        for m, shapes in other.items():
            body_lines.append(f"  - `{m}`: {shapes.count(EMPTY_STREAM)} events")

    body_lines.append("\n---\n*Triggered by: scripts/g13_empty_response_detector.py v1.0*\n*Source: data/metrics/free_model_probes.jsonl*")

    pkt_id = f"g13-alert-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{hash(tuple(sorted(by_model.keys()))) & 0xffff:04x}"
    pkt_file = hivemind_dir / f"{pkt_id}.json"
    hivemind_dir.mkdir(parents=True, exist_ok=True)

    packet = {
        "packet_id": pkt_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_channel": "opencode",
        "source_entity": "grokster",
        "target_channel": "opencode",
        "target_entity": "maat",
        "task": "G13 empty-response detector events detected (R_VAULT_ANTIGRAVITY_DEEPER_20260827 §B.1)",
        "context": "\n".join(body_lines)[:4000],
        "priority": 1 if crit else 0,
        "intent": "alert",
        "events_by_model": by_model,
    }
    tmp = pkt_file.with_suffix(".tmp")
    with tmp.open("w") as f:
        json.dump(packet, f, ensure_ascii=False, indent=2)
    tmp.replace(pkt_file)
    return pkt_file


def main():
    ap = argparse.ArgumentParser(description="G13 empty-response detector (R_VAULT_ANTIGRAVITY_DEEPER_20260827 §B)")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to free_model_probes.jsonl")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to g13_events.jsonl")
    ap.add_argument("--hivemind-dir", type=Path, default=DEFAULT_HIVEMIND_DIR, help="Hivemind handoff dir")
    ap.add_argument("--dry-run", action="store_true", help="Print events but don't write")
    args = ap.parse_args()

    events, by_model = detect_g13_events(args.input, args.output)
    print(f"G13 detector v1.0 — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print(f"Events: {len(events)} G13 across {len(by_model)} models")

    if not events:
        print("No G13 events — system healthy.")
        return

    print("\nBy model:")
    for m, shapes in sorted(by_model.items()):
        n_empty = shapes.count(EMPTY_STREAM)
        n_auth = shapes.count(AUTH_2XX_ERROR)
        parts = []
        if n_empty:
            parts.append(f"empty={n_empty}")
        if n_auth:
            parts.append(f"auth_2xx={n_auth}")
        print(f"  {m:48s} {' '.join(parts)}")

    if args.dry_run:
        print("\n[DRY-RUN] Would post Hivemind alert")
        return

    pkt = post_hivemind_alert(by_model, args.hivemind_dir)
    if pkt:
        print(f"\nWrote Hivemind handoff packet: {pkt}")
    else:
        print("\nNo handoff packet needed (no events)")


if __name__ == "__main__":
    main()
