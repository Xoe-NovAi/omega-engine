#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Compaction-Immune Constraint Re-assertion Loader (M11 / M15 / M23).

THE PROBLEM THIS SOLVES
-----------------------
`MANDATES_CONDENSED.md` is injected PRE-compaction. After compaction runs, that
block is precisely what the summarizer is permitted to drop. arXiv:2606.22528
("Governance Decay", Jun 2026) showed agents obeying standing rules while those
rules are visible, then performing prohibited tool actions once they are not --
reproduced in LangGraph, AutoGen, and the OpenAI Agents SDK.

Our rehydration restored TASK state (`session_gnosis.md`, SESSION_ANCHOR) but
never CONSTRAINT state. This loader is that missing half: it reads the manifest
from DISK at hydration time, so the constraint set cannot be eroded by a
summarizer, because it was never carried in context to begin with.

M23 -- WHY A MISSING FILE IS EXIT 1, NOT AN EMPTY STRING
--------------------------------------------------------
A soft-fail here is worse than no layer at all. An empty constraint set reads
to the caller as "no constraints apply", which is the exact belief the threat
exploits. So a missing or unparseable manifest is a governance failure:
`load_constraints()` raises `ConstraintManifestMissing`, and the CLI exits 1.
There is deliberately no `--allow-missing` escape hatch.

USAGE
-----
    .venv/bin/python scripts/load_constraints.py                # md  (default)
    .venv/bin/python scripts/load_constraints.py --format json   # machine-readable
    .venv/bin/python scripts/load_constraints.py --format ids    # M1 M2 M7 ...
    .venv/bin/python scripts/load_constraints.py --check         # gate mode

EXIT CODES
----------
    0  manifest loaded
    1  manifest missing, unreadable, or unparseable  (M23 -- fail loud)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "docs" / "governance" / "CONSTRAINTS.md"

# The exact string the manifest must carry to be recognised as the live,
# re-injected artifact. Checked on every load: a manifest that has quietly lost
# its COMPACTION-IMMUNE banner is not the artifact we think it is.
COMPACTION_IMMUNE_BANNER = (
    "This file is COMPACTION-IMMUNE. It is re-injected at every post-compact hydration."
)

# Constraint lines look like:
#     - **M1** — All async code uses AnyIO; never `import asyncio`; ...
# The ID may be compound (e.g. `M10/M15`), hence the inner alternation. Both
# em-dash and en-dash are accepted so a reformat in any editor cannot silently
# unparse the manifest.
_CONSTRAINT_RE = re.compile(
    r"^-\s+\*\*(?P<id>M\d+(?:\s*/\s*M\d+)*)\*\*\s*[—–-]{1,2}\s*(?P<law>.+?)\s*$"
)

# Mandates that must survive any compaction. Derived from the Tier-0 injection
# set in MANDATES_CONDENSED.md ("Critical five") plus the structural
# prohibitions that have no second line of defence.
TIER0_IDS: tuple[str, ...] = ("M1", "M7", "M11", "M15", "M23")
STRUCTURAL_IDS: tuple[str, ...] = ("M2", "M28")
REQUIRED_IDS: tuple[str, ...] = TIER0_IDS + STRUCTURAL_IDS

MAX_MANIFEST_BYTES = 4096


class ConstraintManifestMissing(RuntimeError):
    """M23: the manifest is absent, unreadable, or structurally invalid."""


def manifest_path() -> Path:
    """Resolve the manifest location.

    Overridable for tests via `OMEGA_CONSTRAINTS_MANIFEST`. Deliberately NOT
    overridable to a value that resolves to nothing useful -- an override that
    points at a missing file is still a hard failure, by design.
    """
    override = os.environ.get("OMEGA_CONSTRAINTS_MANIFEST")
    if override:
        return Path(override).expanduser().resolve()
    return MANIFEST_PATH


def parse_constraints(text: str) -> list[tuple[str, str]]:
    """Extract `(mandate_id, one_line_law)` pairs from manifest text.

    Raises ConstraintManifestMissing if the compaction-immune banner is absent
    or no constraint lines parse -- both mean we are reading the wrong file.
    """
    if COMPACTION_IMMUNE_BANNER not in text:
        raise ConstraintManifestMissing(
            "constraint manifest is missing the COMPACTION-IMMUNE banner; "
            "refusing to serve a manifest that cannot be recognised on re-injection"
        )

    found: list[tuple[str, str]] = []
    for line in text.splitlines():
        m = _CONSTRAINT_RE.match(line)
        if m:
            found.append((m.group("id").replace(" ", ""), m.group("law")))

    if not found:
        raise ConstraintManifestMissing(
            "constraint manifest contains no parseable `- **M<n>** — law` lines"
        )
    return found


def load_constraints(path: Path | None = None) -> dict[str, Any]:
    """Load the manifest. M23: raises rather than degrading to an empty set.

    Returns a dict with `ids`, `constraints` (ordered), `banner`, `path`,
    `size_bytes`, and `missing_required`.
    """
    target = path or manifest_path()

    if not target.exists():
        raise ConstraintManifestMissing(f"constraint manifest not found: {target}")
    try:
        raw = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConstraintManifestMissing(
            f"constraint manifest unreadable at {target}: {exc}"
        ) from exc

    pairs = parse_constraints(raw)
    size = target.stat().st_size

    ids = [mid for mid, _ in pairs]
    present = set(ids)
    missing = [r for r in REQUIRED_IDS if r not in present]

    return {
        "ids": ids,
        "constraints": pairs,
        "banner": COMPACTION_IMMUNE_BANNER,
        "path": str(target),
        "size_bytes": size,
        "missing_required": missing,
    }


def render_markdown(data: dict[str, Any]) -> str:
    """Injection block: the banner, then one line per mandate."""
    lines = [
        "## STANDING CONSTRAINTS (re-asserted post-compact -- do not drop)",
        "",
        f"> {COMPACTION_IMMUNE_BANNER}",
        "",
    ]
    lines += [f"- **{mid}** — {law}" for mid, law in data["constraints"]]
    lines += [
        "",
        f"Source: {data['path']} ({data['size_bytes']} bytes).",
        "If any ID above is absent from your working context, context was "
        "eroded — re-read the source before acting.",
    ]
    return "\n".join(lines)


def render_ids(data: dict[str, Any]) -> str:
    return " ".join(data["ids"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print the compaction-immune constraint manifest for injection.",
    )
    parser.add_argument(
        "--format",
        choices=("md", "json", "ids"),
        default="md",
        help="output format (default: md)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="gate mode: verify the manifest loads and every required ID is present",
    )
    args = parser.parse_args(argv)

    # M23: fail loud and DETERMINISTIC. `load_constraints()` raises for library
    # callers; the CLI turns that into an explicit exit 1 with a banner on
    # stderr rather than swallowing it. An empty constraint set would read to
    # the caller as "no constraints apply" -- the precise belief the threat
    # exploits -- so there is no path here that prints nothing and exits 0.
    try:
        data = load_constraints()
    except ConstraintManifestMissing as exc:
        print(
            "[CONSTRAINT-MANIFEST-MISSING] compaction-immune constraints could "
            "not be re-asserted.",
            file=sys.stderr,
        )
        print(f"[CONSTRAINT-MANIFEST-MISSING] {exc}", file=sys.stderr)
        print(
            "[CONSTRAINT-MANIFEST-MISSING] This is a governance failure (M23), "
            "not an empty constraint set. Do NOT proceed as if no constraints "
            "apply -- restore the manifest.",
            file=sys.stderr,
        )
        return 1

    if args.check:
        problems: list[str] = []
        if data["missing_required"]:
            problems.append(
                "missing required mandate ID(s): " + ", ".join(data["missing_required"])
            )
        if data["size_bytes"] > MAX_MANIFEST_BYTES:
            problems.append(
                f"manifest is {data['size_bytes']} bytes, over the "
                f"{MAX_MANIFEST_BYTES}-byte injection budget"
            )
        if problems:
            for p in problems:
                print(f"[CONSTRAINT-CHECK FAIL] {p}", file=sys.stderr)
            return 1
        print(
            f"OK: {len(data['ids'])} constraints, {data['size_bytes']} bytes, "
            f"all required IDs present ({data['path']})"
        )
        return 0

    if args.format == "json":
        print(
            json.dumps(
                {
                    "ids": data["ids"],
                    "constraints": [
                        {"id": mid, "law": law} for mid, law in data["constraints"]
                    ],
                    "banner": data["banner"],
                    "path": data["path"],
                    "size_bytes": data["size_bytes"],
                    "missing_required": data["missing_required"],
                },
                indent=2,
            )
        )
    elif args.format == "ids":
        print(render_ids(data))
    else:
        print(render_markdown(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())