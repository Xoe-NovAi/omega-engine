#!/usr/bin/env python3
"""Generate CURRENT_MODELS.md from the model_db snapshot."""
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
MODEL_DB = PROJECT_ROOT / "docs" / "research" / "model_db"
SNAPSHOT_FILE = MODEL_DB / ".last_state.json"
REPORT_FILE = MODEL_DB / "CURRENT_MODELS.md"

if not SNAPSHOT_FILE.exists():
    print(f"No snapshot found at {SNAPSHOT_FILE}")
    print("Run scripts/check_free_models.sh first to generate a snapshot.")
    sys.exit(1)

snap = json.loads(SNAPSHOT_FILE.read_text())
lines = []

lines.append("# 🔱 Omega Engine \u2014 Current Free Model Catalog")
lines.append("")
lines.append(f"**Auto-generated:** {snap['timestamp']}")
lines.append(f"**Source:** Live API queries to OpenRouter, Google AI Studio, OpenCode Zen")
lines.append("")

# ── OpenRouter Free Models ─────────────────────────────────────────────
lines.append("---")
lines.append("## OpenRouter Free Models")
lines.append(f"**{snap['openrouter']['free_count']} free models** \u2014 live from openrouter.ai/api/v1/models")
lines.append("")
lines.append("| # | Model ID | Context |")
lines.append("|---|----------|-------:|")
for i, m in enumerate(sorted(snap['openrouter']['free'], key=lambda x: x['id']), 1):
    ctx = m.get('context', '?')
    lines.append(f"| {i} | {m['id']} | {ctx} |")

lines.append("")
lines.append("**Rate limits:** 20 RPM / 200 RPD (no credits), 1,000 RPD (with $10+)")
lines.append("")

# ── Google Gemma Models ────────────────────────────────────────────────
lines.append("---")
lines.append("## Google Gemma Models (Free Tier)")
lines.append(f"**{snap['google']['gemma_count']} Gemma models** \u2014 live from Google AI Studio API")
lines.append("")
lines.append("| Model ID | Methods |")
lines.append("|----------|---------|")
for m in snap['google']['gemma']:
    methods = ", ".join(m.get('methods', []))
    lines.append(f"| {m['id']} | {methods} |")

lines.append("")
lines.append("**Free tier limits:** ~30 RPM, 1,500 RPD, 1M TPM. No credit card required.")
lines.append("**Warning:** Free tier data may be used for model training.")
lines.append("")

# ── OpenCode Zen ───────────────────────────────────────────────────────
lines.append("---")
lines.append("## OpenCode Zen Models")
total = snap['opencode_zen']['total']
free_count = snap['opencode_zen']['free']
lines.append(f"**{total} models** ({free_count} free, {total - free_count} premium) \u2014 live from opencode.ai/zen/v1/models")
lines.append("")
lines.append("| Tier | Models |")
lines.append("|------|--------|")
free_ids = " | ".join(snap['opencode_zen'].get('free_ids', []))
lines.append(f"| **Free ({free_count})** | {free_ids} |")
lines.append(f"| **Premium ({total - free_count})** | (see OPENCODE_ZEN_MODEL_REFERENCE.md) |")
lines.append("")

# ── Footer ─────────────────────────────────────────────────────────────
lines.append("---")
lines.append("*Run `scripts/check_free_models.sh --report` to regenerate this report.*")
lines.append("*Run `scripts/check_free_models.sh --diff` to check for changes since last run.*")
lines.append("")
lines.append("## Quick-Reference by Use Case")
lines.append("")
lines.append("| Omega Task | Best Free Model (OpenRouter ID) | Why |")
lines.append("|------------|--------------------------------|-----|")
lines.append("| **High-volume entity responses** | `google/gemma-4-31b-it:free` (256K ctx) | Fast, available on Google + OpenRouter |")
lines.append("| **Coding / blocker remediation** | `minimax/minimax-m2.5:free` (200K ctx) | 80.2% SWE-bench, best free coder |")
lines.append("| **Long-context RAG / analysis** | `deepseek/deepseek-v4-flash:free` (1M ctx) | Massive context, good reasoning |")
lines.append("| **Open-weight deployment** | `nvidia/nemotron-3-super-120b-a12b:free` (1M ctx) | 60.47% SWE-bench, opensource |")
lines.append("| **Lightweight fallback** | `qwen/qwen3-coder:free` (1M ctx) | Strong coder, 1M ctx free |")
lines.append("| **Local sovereign inference** | GGUF models via lmster (1-8B) | Zero cloud, unlimited usage |")
lines.append("")

# Write report
REPORT_FILE.write_text("\n".join(lines))
print(f"Report written to {REPORT_FILE}")
