#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Curate_packs.py — Context Packer v3 diagnostic curator CLI.

AP Token: AP-PACKER-V3-CURATOR-20260808
SSOT:     docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md §2, §3 Phase 2

The v3 doctrine: **Curate at config-time. Validate at pack-time. Never silently
delete themes to fit a budget.** This tool is the "curate at config-time" half:

  * Loads a profile from ``packer-config.yaml``.
  * Expands the profile's explicit theme file lists via ``GitIgnoreSpec``
    (community substitution for the deleted v2 hand-rolled globber).
  * Counts tokens with the SHARED ``TokenEstimator`` (single source of truth
    for curator + packer — zero drift, manual §1.5) using the profile's
    platform ``tokenizer_encoding`` and ``token_margin_multiplier``.
  * Renders a colour-coded ``rich.Table``:
      Theme | Files | Tokens | Budget | Headroom | Required | Status
  * FAILS the build (non-zero exit) on over-budget / missing / empty /
    injection-in-required theme — naming the exact bloat files.
  * ``--write-lock`` archives ``context_packs/<profile>/theme_lock.json`` with
    per-file tokens + SHA256 for reproducibility / change detection (§1.8).

Usage:
    python curate_packs.py <profile_name> [--config PATH] [--write-lock]

Exit codes:
    0  success (every theme within budget, required files present)
    1  [PACK-FAIL] budget / required / missing / empty theme
    2  unknown profile or config/CLI error
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import typer
import yaml
from rich.console import Console
from rich.table import Table

# Ensure the context-packer skill dir is importable (resides outside src/).
_SKILL_DIR = Path(__file__).resolve().parent
_SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
for _p in (_SKILL_DIR, _SRC_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import packer
from omega.oracle.token_estimator import tokens_for_file
from platform_adapters import PlatformConfig

app = typer.Typer(help="Context Packer v3 curator — diagnose profile budgets.")
console = Console()

DEFAULT_CONFIG = ".opencode/skills/context-packer/packer-config.yaml"


class CurateError(Exception):
    """Raised when curation cannot proceed (config/profile/CLI errors)."""


def _sha256(path: os.PathLike) -> str:
    h = hashlib.sha256()
    with open(os.fspath(path), "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def _load_profile(config_path: Path, profile_name: str) -> Dict[str, Any]:
    if not config_path.exists():
        raise CurateError(f"[CONFIG-ERROR] config not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    profiles = (data or {}).get("profiles", {})
    if profile_name not in profiles:
        raise CurateError(
            f"[CONFIG-ERROR] unknown profile '{profile_name}'. "
            f"Available: {sorted(profiles)}"
        )
    return profiles[profile_name]


def _resolve_profile(profile_data: Dict[str, Any]):
    """Wrap a raw config profile dict into a namespace for resolve_theme_files."""
    themes = profile_data.get("themes", {})
    return SimpleNamespace(
        name=profile_data.get("name", "?"),
        max_slots=int(profile_data.get("max_slots", 12)),
        include=profile_data.get("include", []),
        exclude=profile_data.get("exclude", []),
        themes=themes,
        platform=PlatformConfig.from_profile_config(profile_data),
    )


def _estimate_bundle(
    theme: str, file_infos: List[Dict[str, Any]], cfg: PlatformConfig, base: Path
) -> List[Dict[str, Any]]:
    """Count tokens for each resolved file + compute SHA256 (for the lock)."""
    results: List[Dict[str, Any]] = []
    for fi in file_infos:
        rel = fi["path"]
        full = Path(fi["full_path"])
        exists = full.is_file()
        if not exists:
            results.append({
                "theme": theme, "path": rel, "exists": False,
                "token_count": 0, "sha256": None,
            })
            continue
        token_count = tokens_for_file(
            full, model=cfg.tokenizer_encoding, margin=cfg.token_margin_multiplier
        )
        results.append({
            "theme": theme, "path": rel, "exists": True,
            "token_count": token_count, "sha256": _sha256(full),
        })
    return results


def _status_for(total: int, budget: int) -> str:
    if total > budget:
        return "OVER"
    if total > int(budget * 0.9):
        return "WARN"
    return "OK"


def _render_table(rows: List[Dict[str, Any]]) -> None:
    table = Table(title="Context Packer v3 — Profile Curation")
    for col in ("Theme", "Files", "Tokens", "Budget", "Headroom", "Required", "Status"):
        just = "right" if col in ("Files", "Tokens", "Budget", "Headroom") else "left"
        table.add_column(col, justify=just)
    for r in rows:
        headroom = (r["budget"] - r["total"]) if r["budget"] is not None else None
        headroom_s = f"{headroom:+}" if headroom is not None else "-"
        mark = {
            "OK": "[green]OK[/green]",
            "WARN": "[yellow]WARN[/yellow]",
            "OVER": "[red]OVER[/red]",
            "EMPTY": "[red]EMPTY[/red]",
            "MISSING": "[red]MISSING[/red]",
        }.get(r["status"], r["status"])
        table.add_row(
            r["theme"], str(r["files"]), f"{r['total']:,}",
            f"{r['budget']:,}" if r["budget"] is not None else "-",
            headroom_s, "yes" if r["required"] else "no", mark,
        )
    console.print(table)


def _top3_largest(theme: str, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    present = [f for f in files if f.get("exists") and f.get("token_count", 0) > 0]
    return sorted(present, key=lambda f: -f["token_count"])[:3]


def _scan_injection(text: str) -> Optional[str]:
    """Reuse the packer's injection scanner (pre-upload security gate)."""
    for pattern, rx in zip(packer.INJECTION_PATTERNS, packer.INJECTION_REGEXES):
        if rx.search(text):
            return pattern
    return None


@app.command()
def curate(
    profile_name: str,
    config: str = typer.Option(DEFAULT_CONFIG, "--config", "-c",
                               help="Path to packer-config.yaml"),
    write_lock: bool = typer.Option(False, "--write-lock",
                                    help="Write context_packs/<profile>/theme_lock.json"),
    scan_injection: bool = typer.Option(False, "--scan-injection",
                                        help="Scan required-theme files for injection patterns"),
    emit_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
) -> int:
    """Curate a single profile against its budgets."""
    try:
        profile_data = _load_profile(Path(config), profile_name)
        cfg = PlatformConfig.from_profile_config(profile_data)
    except CurateError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(2)

    base = Path.cwd()
    profile = _resolve_profile(profile_data)
    if not profile.themes:
        console.print(f"[red][PACK-FAIL] profile '{profile_name}' has no themes[/red]")
        raise typer.Exit(1)

    # step 1 — resolve explicit theme file lists (GitIgnoreSpec).
    try:
        resolved = packer.resolve_theme_files(profile, base)
    except Exception as e:  # noqa: BLE001 - convert glob failures to hard stop
        console.print(f"[red][PACK-FAIL] resolve failed: {e}[/red]")
        raise typer.Exit(1)

    # step 2 — count tokens via the SHARED TokenEstimator.
    bundles: Dict[str, List[Dict[str, Any]]] = {}
    for theme, infos in resolved.items():
        bundles[theme] = _estimate_bundle(theme, infos, cfg, base)

    required_themes = set(bundles.keys())  # fail-closed (M23)

    # step 3 — FAIL-CLOSED validation.
    rows: List[Dict[str, Any]] = []
    failures: List[str] = []
    for theme, files in bundles.items():
        total = sum(int(f["token_count"]) for f in files if f.get("exists"))
        present_files = [f for f in files if f.get("exists")]
        missing = [f for f in files if not f.get("exists")]
        per_limit = int(cfg.token_budget_per_bundle)
        if not present_files:
            status = "MISSING" if missing else "EMPTY"
            failures.append(f"[{status}] theme '{theme}' has no files")
        elif total > per_limit:
            status = "OVER"
            top3 = _top3_largest(theme, files)
            bloat = "; ".join(f"{f['path']}~{f['token_count']}" for f in top3)
            failures.append(f"theme '{theme}' over budget: {total} > {per_limit} "
                            f"(largest: {bloat or 'n/a'})")
        else:
            status = _status_for(total, per_limit)
        rows.append({"theme": theme, "files": len(present_files), "total": total,
                     "budget": per_limit, "required": theme in required_themes,
                     "status": status})

    total_all = sum(int(r["total"]) for r in rows)
    if total_all > int(cfg.token_budget_total):
        failures.append(f"total budget exceeded: {total_all} > {int(cfg.token_budget_total)}")
    slot_count = len(rows) + 1
    if slot_count > int(cfg.max_slots):
        failures.append(f"max_slots exceeded: {slot_count} (incl. manifest) > {int(cfg.max_slots)}")

    # injection scan on required themes (DoD P0-9).
    if scan_injection:
        for theme, files in bundles.items():
            if theme not in required_themes:
                continue
            for fi in files:
                if not fi.get("exists"):
                    continue
                with open(Path(fi["full_path"]), "r", encoding="utf-8",
                          errors="replace") as fh:
                    hit = _scan_injection(fh.read())
                if hit:
                    failures.append(f"theme '{theme}' file '{fi['path']}' matches injection: {hit}")

    _render_table(rows)

    if failures:
        console.print(f"\n[yellow][PACK-FAIL][/yellow] {len(failures)} problem(s):")
        for msg in failures[:40]:
            console.print(f"  [red]- {msg}[/red]")
        if write_lock:
            console.print("[yellow]NOT writing theme_lock.json — curation failed[/yellow]")
        raise typer.Exit(1)

    console.print(f"\n[green]Curate OK[/green] — '{profile_name}': "
                  f"{sum(r['files'] for r in rows)} files, {total_all:,} tokens, "
                  f"within {cfg.max_slots} slots.")

    if write_lock:
        from datetime import datetime
        out_dir = Path("context_packs") / profile_name
        out_dir.mkdir(parents=True, exist_ok=True)
        lock = {
            "profile": profile_name,
            "generated_at": datetime.now().astimezone().isoformat(),
            "tokenizer_encoding": cfg.tokenizer_encoding,
            "token_margin_multiplier": cfg.token_margin_multiplier,
            "themes": {
                theme: [
                    {"file": f["path"], "tokens": f["token_count"], "sha256": f["sha256"]}
                    for f in files if f.get("exists")
                ]
                for theme, files in bundles.items()
            },
        }
        lock_path = out_dir / "theme_lock.json"
        tmp = out_dir / "theme_lock.json.tmp"
        tmp.write_text(json.dumps(lock, indent=2), encoding="utf-8")
        os.replace(tmp, lock_path)
        console.print(f"[green]Wrote {lock_path} "
                      f"({sum(len(v) for v in lock['themes'].values())} files)[/green]")

    if emit_json:
        console.print(json.dumps({
            "profile": profile_name, "ok": True,
            "total_files": sum(r["files"] for r in rows),
            "total_tokens": total_all, "max_slots": cfg.max_slots, "rows": rows,
        }, indent=2))
    raise typer.Exit(0)


def main() -> int:
    return app()


if __name__ == "__main__":
    sys.exit(main())
