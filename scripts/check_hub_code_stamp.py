#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""Probe: is the running hub executing the code on disk? (P0-5)

Exit 0 = CURRENT. Exit 1 = STALE PROCESS — restart required.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from mcp_servers.omega_hub import code_stamp  # noqa: E402


def main() -> int:
    current, stale = code_stamp.check_stamp(REPO)
    if current:
        print("CURRENT — running code matches disk")
        return 0
    print("STALE PROCESS — restart required")
    for rel in stale:
        print(f"  stale: {rel}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
