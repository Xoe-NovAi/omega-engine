#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
#
# test_lan_exposure_audit.py — negative tests for `make check-lan-exposure`.
#
# WHY A NEGATIVE TEST IS MANDATORY:
#   A gate that has never been observed failing is not a gate. The first run of
#   this audit on real hardware produced 15 genuine findings, which is evidence
#   the parser works — but that is a live accident, not a test. These cases pin
#   the behaviour so a future refactor cannot silently turn the gate into a
#   no-op that always prints PASS.
#
# Every case below is synthetic: it feeds `classify()` a constructed Listener and
# asserts the verdict. No socket is opened, no service is touched, nothing on the
# host is mutated.

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lan_exposure_audit as lea  # noqa: E402

PASS = "\033[0;32m"
FAIL = "\033[0;31m"
NC = "\033[0m"

ALLOW = lea.load_allowlist()


def L(addr: str, port: int, ifname: str | None = None, proc: str | None = None):
    return lea.Listener(addr, port, ifname, proc)


# (name, listener, should_be_clean)
CASES = [
    # --- must be CLEAN: loopback and link-local are never exposures ---
    ("loopback v4 ignored", L("127.0.0.1", 8016, None, "python"), True),
    ("loopback v4 alt ignored", L("127.0.0.54", 53, None, None), True),
    ("loopback v6 ::1 ignored", L("::1", 631, None, None), True),
    (
        "link-local fe80 ignored (the bug this caught)",
        L("fe80::70ed:3d61:6fe7:a202", 44348, "wlo1", "rygel"),
        True,
    ),
    (
        "link-local fe80 veth ignored",
        L("fe80::2c96:56ff:fe1e:8555", 58532, "veth_host_3", "rygel"),
        True,
    ),
    # --- must be CLEAN: explicitly approved tailnet binds ---
    ("approved tailnet 8016 v4", L("100.123.51.67", 8016, None, None), True),
    ("approved tailnet 8019 v4", L("100.123.51.67", 8019, None, None), True),
    ("approved tailnet 8016 v6", L("fd7a:115c:a1e0::d835:3344", 8016, None, None), True),
    ("approved tailnet 8019 v6", L("fd7a:115c:a1e0::d835:3344", 8019, None, None), True),
    # --- must be FLAGGED: the exact regressions this gate was built to catch ---
    ("WILDCARD nfsd 2049 caught", L("0.0.0.0", 2049, None, None), False),
    ("WILDCARD mountd 20048 caught", L("0.0.0.0", 20048, None, None), False),
    ("WILDCARD lockd 32803 caught", L("0.0.0.0", 32803, None, None), False),
    ("WILDCARD redis 6379 caught", L("0.0.0.0", 6379, None, "pasta.avx2"), False),
    ("WILDCARD rpcbind 111 caught", L("0.0.0.0", 111, None, None), False),
    ("WILDCARD v6 rpcbind :: caught", L("::", 111, None, None), False),
    ("LAN deluged wlo1 caught", L("192.168.10.168", 51372, "wlo1", "deluged"), False),
    ("TAILNET deluged caught", L("100.123.51.67", 51372, "tailscale0", "deluged"), False),
    ("LAN docker veth caught", L("10.0.3.1", 51372, "veth_host_3", "deluged"), False),
    ("LAN rygel caught", L("10.0.1.1", 50158, "veth_host_1", "rygel"), False),
    ("bridge 172.17.0.1 caught", L("172.17.0.1", 45907, None, "rygel"), False),
    # --- boundary: approved PORT but different PORT must still be caught ---
    ("8016 approved but 9999 is not", L("100.123.51.67", 9999, None, None), False),
    # --- boundary: an approved port owned by a DIFFERENT process is a takeover ---
    (
        "approved addr+port, foreign process still caught",
        L("100.123.51.67", 8016, None, "evil-daemon"),
        False,
    ),
]


def main() -> int:
    failures = []
    print("LAN EXPOSURE AUDIT — negative tests")
    print("=" * 62)
    for name, listener, expect_clean in CASES:
        verdict = lea.classify(listener, ALLOW)
        is_clean = verdict is None
        ok = is_clean == expect_clean
        status = f"{PASS}PASS{NC}" if ok else f"{FAIL}FAIL{NC}"
        expect = "clean" if expect_clean else "FLAGGED"
        got = "clean" if is_clean else f"flagged({verdict[0]})"
        print(f"  [{status}] {name:<48} expected={expect:<8} got={got}")
        if not ok:
            failures.append(name)

    print("=" * 62)
    total = len(CASES)
    if failures:
        print(f"{FAIL}RESULT: FAIL{NC} — {len(failures)}/{total} negative tests failed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"{PASS}RESULT: PASS{NC} — {total}/{total} negative tests green.")
    print()
    print("The gate has now been observed BOTH failing (on live host) and")
    print("passing these assertions. It is a gate, not a no-op.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
