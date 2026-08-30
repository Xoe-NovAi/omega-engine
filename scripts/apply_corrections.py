#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Apply Reality Engine Corrections to Model Cards
⬡ OMEGA ⬡ CLINE ⬡ APPLY-CORRECTIONS ⬡ 2026-07-19
"""
import sys, json, yaml
from pathlib import Path
from datetime import datetime, timezone
import argparse

REGISTRY_DIR = Path("config/model_registry/models")
CORRECTIONS_FILE = Path("data/reality_corrections.json")


def load_corrections() -> dict:
    if not CORRECTIONS_FILE.exists():
        print(f"❌ {CORRECTIONS_FILE} not found. Run reality_engine.py first.")
        sys.exit(1)
    return json.loads(CORRECTIONS_FILE.read_text())


def apply_patch(content: str, fields: dict) -> str:
    if not content.startswith("---"):
        return content
    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1])
    if "context_window" in fields:
        fm["context_window"] = fields["context_window"]
    if "max_output_tokens" in fields:
        fm["max_output_tokens"] = fields["max_output_tokens"]
    if "pricing" in fields:
        fm.setdefault("pricing", {}).update(fields["pricing"])
    fm["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fm["schema_version"] = max(fm.get("schema_version", "1.0.0"), "1.1.0")
    fm.setdefault("live_api_state", {})
    fm["live_api_state"]["source"] = "openrouter-api-2026-07-19"
    fm["live_api_state"]["last_verified"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fm["live_api_state"]["confidence"] = "high"
    new_fm = "---\n" + yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True) + "---\n"
    return new_fm + parts[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually write changes")
    args = parser.parse_args()
    
    corrections = load_corrections()
    print(f"📋 Loaded {len(corrections['corrections'])} corrections")
    print(f"{'🟢 APPLY MODE' if args.apply else '🔴 DRY RUN'}\n")
    
    applied = 0
    for cor in corrections["corrections"]:
        model_id = cor["model_id"]
        filepath = Path(cor["file"])
        if not filepath.exists():
            continue
        content = filepath.read_text()
        new_content = apply_patch(content, cor["fields"])
        if new_content != content and args.apply:
            filepath.write_text(new_content)
            print(f"   ✅ {model_id} — patched")
            applied += 1
    
    print(f"\n{'='*72}")
    print(f"{'✅' if args.apply else '🔴'} Applied: {applied}")
    if not args.apply:
        print("💡 Run with --apply to write changes")
    return 0


if __name__ == "__main__":
    main()
