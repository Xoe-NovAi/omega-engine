#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
#
# test_exchange_false_success.py — regression test for the 8019 false-success
# bug found by Carmack (2026-09-28).
#
# THE DEFECT:
#   `curl -o <file> http://100.123.51.67:8019/<artifact>` wrote a 48-byte ASCII
#   body to disk, indistinguishable from a successful download. A receiver that
#   skipped manifest verification believed the transfer worked and failed later
#   at `unzip`, far from the cause.
#
# WHY THIS TEST EXISTS IN THIS SHAPE:
#   A gate never observed failing is not a gate. These cases were first run
#   against the OLD `python3 -m http.server` origin and DID FAIL — that run is
#   recorded in the dispatch report. The three client paths are exercised exactly
#   as a real receiver would use them, including `curl -o` semantics, because the
#   defect was only ever visible through the client, not through the origin.

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

HOST = "127.0.0.1"
PORT = 8019
TAILNET_IP = "100.123.51.67"
TLS_NAME = "n0.tail51f14a.ts.net"
BASE_LOOPBACK = f"http://{HOST}:{PORT}"
BASE_TLS = f"https://{TLS_NAME}:{PORT}"
BASE_PLAIN_TAILNET = f"http://{TAILNET_IP}:{PORT}"


def _fetch(url: str, timeout: int = 10) -> tuple[int, bytes, dict]:
    """GET a URL, returning (status, body, headers). Never raises on 4xx/5xx."""
    req = urllib.request.Request(url, headers={"User-Agent": "exchange-regression/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers or {})


def _curl_to_file(url: str, dest: Path, extra: list[str] | None = None) -> tuple[int, int]:
    """Reproduce the real client: `curl -o dest url`, and report what landed.

    Returns (exit_code, bytes_written). This is the exact shape of the bug — the
    question is never "what status did the server return", it is "what did the
    client put on disk".
    """
    if dest.exists():
        dest.unlink()
    cmd = ["curl", "-s", "-o", str(dest), "--max-time", "10", *(extra or []), url]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    written = dest.stat().st_size if dest.exists() else 0
    return proc.returncode, written


@pytest.fixture(scope="module")
def manifest() -> dict:
    status, body, _ = _fetch(f"{BASE_LOOPBACK}/manifest.json")
    assert status == 200, (
        f"/manifest.json returned {status}. The origin MUST serve a manifest so a "
        "client can verify before accepting bytes."
    )
    return json.loads(body)


@pytest.fixture(scope="module")
def a_real_artifact(manifest: dict) -> dict:
    entries = [e for e in manifest["entries"] if e.get("size", 0) > 0]
    assert entries, "manifest lists no artifacts; nothing to verify"
    return entries[0]


# ── The three client paths ───────────────────────────────────────────────────
class TestThreeClientPaths:
    def test_path1_loopback_plain_http_serves_real_bytes(
        self, a_real_artifact: dict, tmp_path: Path
    ):
        """PATH 1 — loopback plain HTTP: the origin's own protocol. Must work."""
        url = f"{BASE_LOOPBACK}/{a_real_artifact['path']}"
        dest = tmp_path / "loopback.bin"
        rc, written = _curl_to_file(url, dest)

        assert rc == 0, f"loopback curl exit={rc}"
        assert written == a_real_artifact["size"], (
            f"loopback wrote {written} bytes, manifest says {a_real_artifact['size']}"
        )
        digest = hashlib.sha256(dest.read_bytes()).hexdigest()
        assert digest == a_real_artifact["sha256"], "loopback hash does not match manifest"

    def test_path2_tailnet_tls_serves_real_bytes(
        self, a_real_artifact: dict, tmp_path: Path
    ):
        """PATH 2 — the SUPPORTED client form: HTTPS via the tailnet name."""
        url = f"{BASE_TLS}/{a_real_artifact['path']}"
        dest = tmp_path / "tls.bin"
        rc, written = _curl_to_file(url, dest, extra=["-k"])

        assert rc == 0, f"TLS curl exit={rc}"
        assert written == a_real_artifact["size"], (
            f"TLS wrote {written} bytes, manifest says {a_real_artifact['size']}"
        )
        digest = hashlib.sha256(dest.read_bytes()).hexdigest()
        assert digest == a_real_artifact["sha256"], "TLS hash does not match manifest"

    def test_path3_plain_http_to_tailnet_ip_can_never_yield_a_plausible_artifact(
        self, a_real_artifact: dict, tmp_path: Path
    ):
        """PATH 3 — the BROKEN form, and the bug that started all this.

        http://<tailnet-ip>:8019 speaks plaintext to a TLS terminator. The 48-byte
        ASCII rejection is produced by tailscaled, so the ORIGIN cannot suppress
        it. What must be impossible is a *plausible artifact* landing on disk.

        The assertions that matter, in order of strength:
          1. the response is not a 200;
          2. it does not carry the artifact's bytes or hash;
          3. if a file does land, it is trivially small next to the real artifact
             AND its content is recognisable as an error string, not a payload;
          4. `curl -f` (the documented client form) writes NO file at all.
        """
        url = f"{BASE_PLAIN_TAILNET}/{a_real_artifact['path']}"
        real_size = a_real_artifact["size"]

        status, body, headers = _fetch(url)

        # (1) must not claim success
        assert status != 200, (
            f"plain-HTTP to the tailnet IP returned 200 — a plaintext request was "
            f"accepted, which should be impossible on a TLS port"
        )

        # (2) must not be the artifact
        assert hashlib.sha256(body).hexdigest() != a_real_artifact["sha256"], (
            "plain-HTTP returned the real artifact — unexpected but not harmful"
        )

        # (3) if a body exists it must be unmistakably an error, not a payload
        if body:
            assert len(body) != real_size, (
                f"error body is {len(body)} bytes, same length as the real "
                f"artifact ({real_size}) — a receiver could confuse them"
            )
            lowered = body[:512].lower()
            recognisable = any(
                marker in lowered
                for marker in (
                    b"https",       # "Client sent an HTTP request to an HTTPS server."
                    b"error",
                    b"omega-error",
                    b"manifest",
                    b"not found",
                )
            )
            assert recognisable, (
                f"error body is not recognisable as an error: {body[:120]!r}. A "
                "client must never be able to mistake this for a payload."
            )

        # (4) THE decisive one: the documented client form leaves nothing on disk.
        dest = tmp_path / "should_not_exist.zip"
        rc, written = _curl_to_file(url, dest, extra=["-f"])
        assert rc != 0, "curl -f exited 0 on a failed path"
        assert not dest.exists() or written == 0, (
            f"curl -f wrote {written} bytes for a FAILED request — this is the "
            "false-success bug, and it is not fixed"
        )


# ── Manifest: the verification contract ───────────────────────────────────────
class TestManifestContract:
    def test_manifest_lists_required_fields(self, manifest: dict):
        assert manifest["entries"], "manifest has no entries"
        for entry in manifest["entries"]:
            for field in ("path", "size", "sha256", "content_type"):
                assert field in entry, f"manifest entry missing {field!r}: {entry}"
            assert isinstance(entry["size"], int) and entry["size"] >= 0
            assert len(entry["sha256"]) == 64, "sha256 must be a full hex digest"

    def test_manifest_publishes_the_only_valid_url_form(self, manifest: dict):
        assert "HTTPS ONLY" in manifest["url_form"]
        assert "BROKEN" in manifest["broken_url_form"], (
            "the manifest must name the broken URL form explicitly, so nobody "
            "rediscovers it"
        )

    def test_manifest_hashes_match_reality(self, manifest: dict):
        """The manifest's own hashes must be true, or it is a worse-than-nothing
        control: a client would reject a correct download."""
        checked = 0
        for entry in manifest["entries"][:25]:
            p = Path(manifest["root"]) / entry["path"]
            if not p.is_file():
                continue
            raw = p.read_bytes()
            assert len(raw) == entry["size"], f"size drift on {entry['path']}"
            assert hashlib.sha256(raw).hexdigest() == entry["sha256"], (
                f"hash drift on {entry['path']}"
            )
            checked += 1
        assert checked, "verified zero real files — manifest is decorative"

    def test_responses_carry_verifiable_headers(self, a_real_artifact: dict):
        status, _, headers = _fetch(f"{BASE_LOOPBACK}/{a_real_artifact['path']}")
        assert status == 200
        assert headers.get("x-omega-sha256") == a_real_artifact["sha256"], (
            "artifact responses must carry the sha256 so a client can verify "
            "before hashing the body"
        )
        assert headers.get("x-omega-size") == str(a_real_artifact["size"])


# ── Read-only surface ────────────────────────────────────────────────────────
class TestReadOnlySurface:
    @pytest.mark.parametrize("verb", ["PUT", "POST", "DELETE", "PATCH"])
    def test_write_verbs_are_refused(self, verb: str):
        req = urllib.request.Request(
            f"{BASE_LOOPBACK}/anything", data=b"x", method=verb,
            headers={"User-Agent": "exchange-regression/1.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                status, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            status, body = e.code, e.read()

        assert status == 405, f"{verb} returned {status}, expected 405 (read-only)"

    def test_error_responses_are_envelopes_not_bare_bodies(self):
        status, body, headers = _fetch(f"{BASE_LOOPBACK}/definitely-not-here-xyz")
        assert status == 404
        assert headers.get("x-omega-error") == "1", (
            "error responses must carry X-Omega-Error: 1 so a client can tell an "
            "error from a payload without parsing"
        )
        parsed = json.loads(body)
        assert parsed["error"] and parsed["detail"], "error body must be a JSON envelope"
        assert parsed["verification_required"] is True


# ── Path traversal ───────────────────────────────────────────────────────────
class TestPathContainment:
    @pytest.mark.parametrize(
        "evil",
        ["../../../etc/passwd", "..%2f..%2fetc%2fpasswd", "/../../etc/shadow"],
    )
    def test_traversal_is_refused(self, evil: str, tmp_path: Path):
        """Traversal must be refused, and the refusal must not leak host content.

        A body IS expected here (a JSON error envelope) — that is the safe,
        loud failure this service promises. What must never happen is the real
        contents of /etc/passwd or /etc/shadow reaching the client. Asserting
        "zero bytes" would be asserting the WRONG property and would have
        rejected a correct implementation.
        """
        dest = tmp_path / "escape.bin"
        rc, written = _curl_to_file(f"{BASE_LOOPBACK}/{evil}", dest, extra=["-k", "--path-as-is"])
        assert written > 0, (
            f"traversal {evil!r} produced no refusal at all — expected a loud "
            "error envelope so the client is not left guessing"
        )

        body = dest.read_bytes()
        leaked = [m for m in (b"root:", b"/bin/bash", b"/bin/sh", b"$6$", b"$7$") if m in body]
        assert not leaked, (
            f"traversal {evil!r} leaked host file content (markers {leaked!r})"
        )
        # And the refusal must be identifiable as a refusal.
        assert b"root:" not in body, "response contains /etc/passwd content"
        assert b"omega-error" in body or b"not_found" in body, (
            f"traversal {evil!r} refusal is not recognisable as an error: {body[:120]!r}"
        )


if __name__ == "__main__":
    # P0-3: this module is a pytest module. Run directly it executes zero
    # tests and exits 0 — a false success. Fail loud instead.
    print("run with pytest: .venv/bin/python -m pytest scripts/test_exchange_false_success.py")
    sys.exit(2)
