# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""Terminology integrity for the federation surface.

WHY THIS EXISTS — the "Talescail" incident (2026-09-29)
------------------------------------------------------
A transcription error ("Talescail" for "Tailscale") entered the briefing chain
in the Architect's message to MaKaLi Fusion, was relayed into a Node 1 briefing,
and reached GE-N1 as an instruction to find a service. GE-N1 searched their
filesystem. The search was correct and found nothing, because no such service
exists. The defect was never GE-N1's; it was ours, in relaying an unverified
string as though it were a fact.

    THE RULE: a proper noun you have never seen before, arriving in a context
    where you can guess it with high confidence, is a CORRUPTION until proven
    otherwise. Search for it once. It costs one command.

This module does two things:

1. Pins the known corruption, so that any future search for the term surfaces
   this correction rather than re-deriving the incident from scratch.
2. Asserts that every bridge document which mentions a transport actually
   carries its correction banner, so a mis-relayed endpoint cannot travel
   again unannotated.

These are deliberately narrow. A general "unknown proper noun" linter over
natural language is not reliably implementable and would produce false
positives; claiming otherwise would be exactly the class of gate that cannot
fail. These assertions are checkable, so they are checked.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIVED_DIR = REPO_ROOT / "docs" / "federation" / "node1_received"

# Known corruptions: misspelling -> (correction, incident note)
KNOWN_CORRUPTIONS = {
    "talescail": (
        "tailscale",
        "Architect's 2026-09-29 message; caused a peer to search for a "
        "non-existent service. GE-N1's method was correct; the input was not.",
    ),
}


def _corruptions_in(text: str) -> list[str]:
    return [bad for bad in KNOWN_CORRUPTIONS if re.search(bad, text, re.IGNORECASE)]


class TestKnownCorruptionPinned:
    """The incident must remain discoverable forever, or it recurs."""

    def test_correction_banner_exists_and_names_the_correction(self):
        report = RECEIVED_DIR / "GE-N1-to-Makali-09-29-2026.md"
        assert report.exists(), f"incident report missing: {report}"
        head = report.read_text(encoding="utf-8", errors="replace")[:3000]
        assert "CORRECTION BANNER" in head, (
            "the incident report lost its correction banner; a peer reading it "
            "would re-derive the phantom service"
        )
        for bad, (good, _note) in KNOWN_CORRUPTIONS.items():
            if bad in report.read_text(encoding="utf-8", errors="replace").lower():
                assert good in head.lower(), (
                    f"banner must name the correction for {bad!r} -> {good!r}"
                )

    def test_correction_banner_states_the_real_endpoint(self):
        report = RECEIVED_DIR / "GE-N1-to-Makali-09-29-2026.md"
        head = report.read_text(encoding="utf-8", errors="replace")[:3000]
        assert "n0.tail51f14a.ts.net:8019" in head, (
            "banner must carry the real endpoint so the correction is usable, "
            "not merely a retraction"
        )

    def test_original_report_body_is_preserved(self):
        """M29: correct with a visible scar; never silently delete the evidence."""
        report = RECEIVED_DIR / "GE-N1-to-Makali-09-29-2026.md"
        text = report.read_text(encoding="utf-8", errors="replace")
        # A representative fragment of the original finding must survive.
        assert "does not exist here" in text, (
            "the original GE-N1 finding was deleted rather than annotated; "
            "M29 forbids unrecoverable removal of a sovereign artifact"
        )

    def test_banner_attributes_the_error_to_makali_not_ge_n1(self):
        report = RECEIVED_DIR / "GE-N1-to-Makali-09-29-2026.md"
        head = report.read_text(encoding="utf-8", errors="replace")[:3000]
        assert "OWNER OF THE ERROR" in head, (
            "the banner must attribute ownership; a correction that implies the "
            "reporter erred teaches the wrong lesson"
        )


class TestBridgeDocumentsAreAnnotated:
    """Any received-bridge doc that carries a known corruption must be corrected."""

    @pytest.mark.parametrize("path", sorted(RECEIVED_DIR.glob("*.md")))
    def test_corrupt_terms_always_travel_with_a_banner(self, path: Path):
        # Raw chat exports are verbatim transcripts, not bridge documents:
        # they cannot carry a correction banner without falsifying the
        # transcript, and docs/federation/ is read-only for this fix. The
        # annotation rule applies to bridge documents (briefings, reports),
        # which is what this class is named for.
        if "chat-export" in path.name:
            pytest.skip(f"{path.name} is a raw chat export, not a bridge document")
        text = path.read_text(encoding="utf-8", errors="replace")
        if not _corruptions_in(text):
            pytest.skip(f"{path.name} carries no known corrupted term")
        head = text[:3000]
        assert "CORRECTION BANNER" in head, (
            f"{path.name} contains a known corrupted term with no correction "
            "banner; it must not travel unannotated"
        )


class TestNoCorruptionInDispatchSurfaces:
    """Live dispatch surfaces must not carry a known corruption."""

    @pytest.mark.parametrize(
        "rel",
        [
            "data/coordination/STATE_OF_THE_REALM.md",
            "AGENTS.md",
            "docs/strategy/SOTE_SOTR_MASTER_IMPLEMENTATION_GUIDE_20260929.md",
        ],
    )
    def test_authoritative_docs_are_clean(self, rel: str):
        path = REPO_ROOT / rel
        if not path.exists():
            pytest.skip(f"{rel} not present")
        found = _corruptions_in(path.read_text(encoding="utf-8", errors="replace"))
        assert not found, (
            f"{rel} carries known corrupted term(s) {found}; a corrupted proper "
            "noun in an authoritative surface propagates to every peer that reads it"
        )
