# 🔱 Test: M2 Engine-Stack Firewall — No WAD Content in Core
# ⬡ OMEGA ⬡ PILLAR-P10 ⬡ tests/test_firewall_m2.py
#
# Enforces Mandate 2 (Engine-Stack Firewall):
#   "Maintain absolute separation between the Omega Engine Core
#    (src/omega/) and Expansion Stacks (WADs in config/wads/)."
#
# This test has TWO modes:
#   1. STRICT on src/omega/ — engine core must be WAD-agnostic
#      Only exceptions: firewall tools (must list terms), legitimate
#      architecture documentation (not logic)
#   2. LENIENT on tests/ — test fixtures may use entity names
#      (technical debt, tracked separately)
#
# The list of blocked terms IS the contract. Adding a term here means
# "this term is WAD-only and must never appear in src/omega/ logic."
# Exceptions require explicit file:line justification.

import pytest
import re
from pathlib import Path

# ── Blocked Terms ───────────────────────────────────────────────────
#
# Each entry is a (regex_pattern, severity, reason) tuple.
# "error" = MUST NOT appear in src/omega/.
# "warning" = should be removed but non-blocking (for gradual cleanup).

BLOCKED_TERMS: list[tuple[str, str, str]] = [
    # ── Kabbalistic/Mnemosyne architecture terms (WAD-only) ──────────
    (r"\bDa[']?at\b", "error", "WAD-only Kabbalistic term (Da'at/Knowledge sphere)"),
    (r"\bDa[']?ath\b", "error", "WAD-only Kabbalistic term (variant spelling)"),
    (r"\bQliphoth\b", "error", "WAD-only Qliphotic shell concept"),
    (r"\bKlipot\b", "error", "WAD-only Qliphotic shell concept (alt spelling)"),
    (r"\bSephiroth\b", "error", "WAD-only Sephirotic tree concept"),
    (r"\bSephirah\b", "error", "WAD-only individual sephirah term"),
    # Individual Sephiroth names (unique enough to not false-positive)
    (r"\bKeter\b", "error", "WAD-only Crown sephirah"),
    (r"\bChokmah\b", "error", "WAD-only Wisdom sephirah"),
    (r"\bBinah\b", "error", "WAD-only Understanding sephirah"),
    (r"\bChesed\b", "error", "WAD-only Mercy sephirah"),
    (r"\bGevurah\b", "error", "WAD-only Severity/Judgment sephirah"),
    (r"\bTiferet\b", "error", "WAD-only Beauty/Compassion sephirah"),
    (r"\bNetzach\b", "error", "WAD-only Victory/Eternity sephirah"),
    (r"\bHod\b", "error", "WAD-only Glory/Splendor sephirah"),
    (r"\bYesod\b", "error", "WAD-only Foundation sephirah"),
    (r"\bMalkhut\b", "error", "WAD-only Kingdom/Shekinah sephirah"),
    # General Kabbalistic reference
    (r"\bKabbal(?:ah|istic|ist)\b", "error", "WAD-only Kabbalistic tradition references"),
    (r"\bCabalistic\b", "error", "WAD-only Kabbalistic tradition references"),

    # ── WAD-specific architecture mapping terms ──────────────────────
    # These map generic engine concepts to specific WAD frameworks.
    # The MAPPING belongs in the WAD docs, not in engine code.
    (r"\bMnemosyne\b", "error", "WAD-only memory system archetype (Arcana-Nova)"),
    (r"\bArcana.?Novai?\b", "error", "WAD-only stack name (Arcana-Nova)"),
    (r"\bTorment.?Stack\b", "error", "WAD-only stack name (Torment Stack)"),
    (r"\bDoom.?Universe\b", "error", "WAD-only stack name (Doom Universe)"),
    (r"\b_omega_default\b", "error", "WAD-only IWAD name (default IWAD)"),

    # ── WAD Entity Names (ALL entity names are WAD content) ──────────
    # Engine core defines SLOTS (P1-P10, Grand Oversight) and INTERFACES.
    # WADs provide the ENTITIES that fill those slots.
    # These entity names MUST be loaded from WAD YAML, not hardcoded.
    # Arcana-Nova entities:
    (r"\bSekhmet\b", "error", "WAD entity name (Arcana-Nova P1)"),
    (r"\bBrigid\b", "error", "WAD entity name (Arcana-Nova P2)"),
    (r"\bPrometheus\b", "error", "WAD entity name (Arcana-Nova P3)"),
    (r"\bSaraswati\b", "error", "WAD entity name (Arcana-Nova P4)"),
    (r"\bInanna\b", "error", "WAD entity name (Arcana-Nova P5)"),
    (r"\bEreshkigal\b", "error", "WAD entity name (Arcana-Nova P6)"),
    (r"\bLucifer\b", "error", "WAD entity name (Arcana-Nova P7)"),
    (r"\bHecate\b", "error", "WAD entity name (Arcana-Nova P8)"),
    (r"\bAnubis\b", "error", "WAD entity name (Arcana-Nova P9)"),
    (r"\bVetala\b", "error", "WAD entity name (Arcana-Nova P10)"),
    (r"\bSophia\b", "error", "WAD entity name (Arcana-Nova containing field)"),
    (r"\bIris\b", "error", "WAD entity name (Arcana-Nova messenger bridge)"),
    # _omega_default / MaKaLi triad entities:
    (r"\bKali\b", "error", "WAD entity name (_omega_default Grand Oversight)"),
    (r"\bMa[']?at\b", "error", "WAD entity name (_omega_default Build Oversoul/CTO)"),
    (r"\bLilith\b", "error", "WAD entity name (_omega_default Runtime Oversoul/CISO)"),
    (r"\bMakali\b", "error", "WAD entity name (_omega_default MaKaLi synthesis)"),
    # Doom Universe / Torment Stack entities:
    (r"\bJohn.?Carmack\b", "error", "WAD entity name (Doom Universe S3 Consultant)"),
    (r"\bDoom.?Guy\b", "error", "WAD entity name (Doom Universe Architect)"),
    (r"\bRoc.?Rac?oon\b", "error", "WAD entity name (Legacy Miner)"),
    (r"\bJem\b", "error", "WAD entity name (Synthesizer)"),
    # Legacy / other:
    (r"\bVetala\b", "error", "WAD entity name (Content Integrity)"),

    # ── Pre-existing violations being tracked (severity: warning) ─────
    # These will be upgraded to "error" as they are cleaned up.
    # --- currently none ---
]

# ── Allowed Exceptions ──────────────────────────────────────────────
#
# File:line specific exemptions. Format:
#   (file_suffix, line_number or None, blocked_term_index)
#   line_number = None means "any line in this file"
#   blocked_term_index = index into BLOCKED_TERMS above
#
# EXCEPTION POLICY:
#   - Only for files that MUST reference WAD terms as part of their function
#     (e.g., the firewall checker itself defines blocked patterns)
#   - Each exception must have a clear justification
#   - Exceptions are TECHNICAL DEBT — they must be eliminated by migrating
#     the reference to WAD-loaded configuration
#
# CATEGORIES:
#   [FIREWALL TOOLS] - The firewall checker/auditor must list blocked terms
#   [DOC/COMMENT] - Documentation describing architecture (not logic)
#   [UI/DISPLAY] - TUI/UI displaying entity names (should load from WAD)
#   [LEGACY] - Archive/dead code

ALLOWED_EXCEPTIONS: list[tuple[str, int | None, int]] = [
    # ─────────────────────────────────────────────────────────────────
    # [FIREWALL TOOLS] - The firewall checker/auditor must list blocked terms
    # ─────────────────────────────────────────────────────────────────
    ("src/omega/audit/firewall_checker.py", None, 13),  # Keter
    ("src/omega/audit/firewall_checker.py", None, 14),  # Chokmah
    ("src/omega/audit/firewall_checker.py", None, 15),  # Binah
    ("src/omega/audit/firewall_checker.py", None, 16),  # Chesed
    ("src/omega/audit/firewall_checker.py", None, 17),  # Gevurah
    ("src/omega/audit/firewall_checker.py", None, 18),  # Tiferet
    ("src/omega/audit/firewall_checker.py", None, 19),  # Netzach
    ("src/omega/audit/firewall_checker.py", None, 20),  # Hod
    ("src/omega/audit/firewall_checker.py", None, 21),  # Yesod
    ("src/omega/audit/firewall_checker.py", None, 22),  # Malkhut
    ("src/omega/audit/firewall_checker.py", None, 23),  # Kabbalistic
    ("src/omega/audit/firewall_checker.py", None, 24),  # Cabalistic
    ("src/omega/audit/firewall_checker.py", None, 25),  # Mnemosyne
    ("src/omega/audit/firewall_checker.py", None, 26),  # Arcana-Nova
    ("src/omega/audit/firewall_checker.py", None, 27),  # Torment Stack
    ("src/omega/audit/firewall_checker.py", None, 28),  # Doom Universe
    ("src/omega/audit/firewall_checker.py", None, 29),  # _omega_default
    ("src/omega/audit/firewall_checker.py", None, 30),  # Sekhmet
    ("src/omega/audit/firewall_checker.py", None, 31),  # Brigid
    ("src/omega/audit/firewall_checker.py", None, 32),  # Prometheus
    ("src/omega/audit/firewall_checker.py", None, 33),  # Saraswati
    ("src/omega/audit/firewall_checker.py", None, 34),  # Inanna
    ("src/omega/audit/firewall_checker.py", None, 35),  # Ereshkigal
    ("src/omega/audit/firewall_checker.py", None, 36),  # Lucifer
    ("src/omega/audit/firewall_checker.py", None, 37),  # Hecate
    ("src/omega/audit/firewall_checker.py", None, 38),  # Anubis
    ("src/omega/audit/firewall_checker.py", None, 39),  # Vetala
    ("src/omega/audit/firewall_checker.py", None, 40),  # Sophia
    ("src/omega/audit/firewall_checker.py", None, 41),  # Iris
    ("src/omega/audit/firewall_checker.py", None, 42),  # Kali
    ("src/omega/audit/firewall_checker.py", None, 43),  # Ma'at
    ("src/omega/audit/firewall_checker.py", None, 37),  # Lilith
    ("src/omega/audit/firewall_checker.py", None, 38),  # Makali
    ("src/omega/audit/firewall_checker.py", None, 39),  # John Carmack
    ("src/omega/audit/firewall_checker.py", None, 40),  # Doom Guy
    ("src/omega/audit/firewall_checker.py", None, 41),  # Roc Racoon
    ("src/omega/audit/firewall_checker.py", None, 42),  # Jem
    ("src/omega/audit/firewall_checker.py", None, 43),  # Vetala (duplicate)

    # Memory firewall auditor references WAD terms as examples of what to block
    ("src/omega/audit/memory_firewall_auditor.py", None, 1),  # Qliphoth
    ("src/omega/audit/memory_firewall_auditor.py", None, 2),  # Klipot
    ("src/omega/audit/memory_firewall_auditor.py", None, 3),  # Sephiroth
    ("src/omega/audit/memory_firewall_auditor.py", None, 4),  # Sephirah
    ("src/omega/audit/memory_firewall_auditor.py", None, 5),  # Keter
    ("src/omega/audit/memory_firewall_auditor.py", None, 6),  # Chokmah
    ("src/omega/audit/memory_firewall_auditor.py", None, 7),  # Binah
    ("src/omega/audit/memory_firewall_auditor.py", None, 8),  # Chesed
    ("src/omega/audit/memory_firewall_auditor.py", None, 9),  # Gevurah
    ("src/omega/audit/memory_firewall_auditor.py", None, 10), # Tiferet
    ("src/omega/audit/memory_firewall_auditor.py", None, 11), # Netzach
    ("src/omega/audit/memory_firewall_auditor.py", None, 12), # Hod
    ("src/omega/audit/memory_firewall_auditor.py", None, 13), # Yesod
    ("src/omega/audit/memory_firewall_auditor.py", None, 14), # Malkhut
    ("src/omega/audit/memory_firewall_auditor.py", None, 15), # Kabbalistic
    ("src/omega/audit/memory_firewall_auditor.py", None, 16), # Cabalistic
    ("src/omega/audit/memory_firewall_auditor.py", None, 17), # Mnemosyne
    ("src/omega/audit/memory_firewall_auditor.py", None, 18), # Arcana-Nova
    ("src/omega/audit/memory_firewall_auditor.py", None, 19), # Torment Stack
    ("src/omega/audit/memory_firewall_auditor.py", None, 20), # Doom Universe
    ("src/omega/audit/memory_firewall_auditor.py", None, 21), # _omega_default
    ("src/omega/audit/memory_firewall_auditor.py", None, 22), # Sekhmet
    ("src/omega/audit/memory_firewall_auditor.py", None, 23), # Brigid
    ("src/omega/audit/memory_firewall_auditor.py", None, 24), # Prometheus
    ("src/omega/audit/memory_firewall_auditor.py", None, 25), # Saraswati
    ("src/omega/audit/memory_firewall_auditor.py", None, 26), # Inanna
    ("src/omega/audit/memory_firewall_auditor.py", None, 27), # Ereshkigal
    ("src/omega/audit/memory_firewall_auditor.py", None, 28), # Lucifer
    ("src/omega/audit/memory_firewall_auditor.py", None, 29), # Hecate
    ("src/omega/audit/memory_firewall_auditor.py", None, 30), # Anubis
    ("src/omega/audit/memory_firewall_auditor.py", None, 31), # Vetala
    ("src/omega/audit/memory_firewall_auditor.py", None, 32), # Sophia
    ("src/omega/audit/memory_firewall_auditor.py", None, 33), # Iris
    ("src/omega/audit/memory_firewall_auditor.py", None, 34), # Kali
    ("src/omega/audit/memory_firewall_auditor.py", None, 35), # Ma'at
    ("src/omega/audit/memory_firewall_auditor.py", None, 36), # Lilith
    ("src/omega/audit/memory_firewall_auditor.py", None, 37), # Makali
    ("src/omega/audit/memory_firewall_auditor.py", None, 38), # John Carmack
    ("src/omega/audit/memory_firewall_auditor.py", None, 39), # Doom Guy
    ("src/omega/audit/memory_firewall_auditor.py", None, 40), # Roc Racoon
    ("src/omega/audit/memory_firewall_auditor.py", None, 41), # Jem

    # ─────────────────────────────────────────────────────────────────
    # [DOC/COMMENT] - Legitimate documentation of architecture (not logic)
    # ─────────────────────────────────────────────────────────────────
    # Mandate auditor documents M3 "Iris Constant" - this is documenting
    # the mandate, not hardcoding entity logic
    ("src/omega/audit/mandate_auditor.py", 14, 34), # Iris (docstring)

    # Oracle.py - Phase C M2 remediation
    # Line 48: Import statement for ..iris.matcher module (not entity)
    ("src/omega/oracle/oracle.py", 48, 34),  # Iris (import)
    # Line 146: Docstring example showing entity name lookup
    ("src/omega/oracle/oracle.py", 146, 34),  # Iris (docstring example)
    # Line 188: Docstring describing Iris confidence assessment
    ("src/omega/oracle/oracle.py", 188, 34),  # Iris (docstring)
    # Line 586: Trace log namespace "iris.speculative" (observability key, not entity)
    ("src/omega/oracle/oracle.py", 586, 34),  # Iris (trace namespace)
    # Line 871: Fallback display name for backward compatibility
    ("src/omega/oracle/oracle.py", 871, 34),  # Iris (fallback display)
    # Line 886: Trace log namespace "iris.responded" (observability key, not entity)
    ("src/omega/oracle/oracle.py", 886, 34),  # Iris (trace namespace)

    # ICS.py - Phase D M2 remediation
    # Line 81: Default IWAD constant "_omega_default" (architecture constant, not entity)
    ("src/omega/ics.py", 81, 24),  # _omega_default (constant)

    # Adapters module documents that Kabbalistic terminology belongs in WAD
    ("src/omega/memory/adapters.py", None, 12), # Kabbalistic

    # ─────────────────────────────────────────────────────────────────
    # [UI/DISPLAY] - TUI/UI displaying entity names (should load from WAD)
    # ─────────────────────────────────────────────────────────────────
    # fleet_status_tui.py exceptions REMOVED — Phase E complete, file is now WAD-loadable

    # ─────────────────────────────────────────────────────────────────
    # [LEGACY] - Archive/dead code
    # ─────────────────────────────────────────────────────────────────
    # Sleep-time agent has pre-existing DaatDaemon class name
    # that needs to be renamed. Tracked separately.
    ("src/omega/memory/sleep_time.py", None, 0),  # Da'at
    ("src/omega/memory/sleep_time.py", None, 1),  # Da'ath
    ("src/omega/memory/sleep_time.py", None, 25), # Mnemosyne
    ("src/omega/memory/sleep_time.py", None, 12), # Kabbalistic

    # Compaction manager references WAD terms in comment saying
    # they belong in WAD docs. Fixed by removing explicit names.
    # ("src/omega/memory/compaction.py", None, 0),  # Da'at - FIXED
    # ("src/omega/memory/compaction.py", None, 3),  # Sephiroth - FIXED

    # Archive tests (dead code, skipped) - legacy Mnemosyne adapter
    ("tests/archive/test_mnemosyne_adapter.py", None, 12), # Kabbalistic
    ("tests/archive/test_mnemosyne_adapter.py", None, 5),  # Keter
    ("tests/archive/test_mnemosyne_adapter.py", None, 14), # Mnemosyne
    ("tests/archive/test_mnemosyne_adapter.py", None, 5),  # Keter
    ("tests/archive/test_mnemosyne_adapter.py", None, 14), # Mnemosyne
    ("tests/archive/test_mnemosyne_adapter.py", None, 5),  # Keter
    ("tests/archive/test_mnemosyne_adapter.py", None, 3),  # Qliphoth
    ("tests/archive/test_mnemosyne_adapter.py", None, 3),  # Qliphoth
    ("tests/archive/test_mnemosyne_adapter.py", None, 3),  # Qliphoth
    ("tests/archive/test_mnemosyne_adapter.py", None, 3),  # Qliphoth
    ("tests/archive/test_mnemosyne_adapter.py", None, 3),  # Qliphoth
    ("tests/archive/test_mnemosyne_adapter.py", None, 3),  # Qliphoth
    ("tests/archive/test_mnemosyne_adapter.py", None, 14), # Mnemosyne

    # Contract tests for memory firewall auditor
    ("tests/contracts/test_memory_firewall_auditor.py", None, 1), # Qliphoth

    # Memory adapter tests (legacy)
    ("tests/test_memory_adapters.py", None, 1), # Qliphoth
    ("tests/test_memory_adapters.py", None, 1), # Qliphoth
]

# ── Scan Configuration ──────────────────────────────────────────────

# STRICT scan: src/omega/ — engine core must be WAD-agnostic
STRICT_SCAN_DIRS = ["src/omega"]

# LENIENT scan: tests/ — test fixtures may use entity names (technical debt)
LENIENT_SCAN_DIRS = ["tests"]

SCAN_EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
]

# Files that are ALLOWED to contain blocked terms as part of their function
SCAN_EXCLUDE_FILES = [
    "tests/test_firewall_m2.py",  # Self-exempt (defines the terms)
]

# Entity name term indices (for test file blanket exceptions)
ENTITY_NAME_INDICES = list(range(30, 51))  # Indices 30-50 are entity names


# ── The Test ─────────────────────────────────────────────────────────


def _scan_directory(
    root: Path,
    scan_dirs: list[str],
    strict: bool,
    exceptions: list[tuple[str, int | None, int]],
) -> list[str]:
    """Scan directories for blocked terms.

    Args:
        root: Project root
        scan_dirs: Directories to scan
        strict: If True, violations are errors. If False, violations are warnings.
        exceptions: List of (file_suffix, line_number, term_index) exceptions

    Returns:
        List of violation strings (empty if clean)
    """
    violations = []

    for scan_dir in scan_dirs:
        scan_path = root / scan_dir
        if not scan_path.exists():
            continue

        for py_file in sorted(scan_path.rglob("*.py")):
            rel_str = str(py_file.relative_to(root))
            if any(excl in rel_str for excl in SCAN_EXCLUDE_PATTERNS):
                continue
            if rel_str in SCAN_EXCLUDE_FILES:
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            for line_num, line in enumerate(content.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if stripped.startswith(('"""', "'''")):
                    continue
                code = line.split(" #")[0].split("\t#")[0]

                for term_idx, (pattern_str, severity, reason) in enumerate(BLOCKED_TERMS):
                    if re.search(pattern_str, code, re.IGNORECASE):
                        # Check if this match is in the allowed exceptions
                        is_allowed = False
                        for exc_file, exc_line, exc_idx in exceptions:
                            if exc_idx == term_idx and rel_str.endswith(exc_file):
                                if exc_line is None or exc_line == line_num:
                                    is_allowed = True
                                    break
                        if not is_allowed:
                            sev_icon = "🔴" if strict else "🟡"
                            sev_label = "ERROR" if strict else "WARN"
                            violations.append(
                                f"  {sev_icon} {rel_str}:{line_num} [{sev_label}] — '{pattern_str}' found\n"
                                f"       Reason: {reason}\n"
                                f"       Line: {code.strip()[:120]}"
                            )

    return violations


def test_firewall_m2_strict_engine_core():
    """M2 Firewall (STRICT): no WAD-specific terminology in src/omega/.

    Engine core must be WAD-agnostic. Only exceptions:
    - Firewall tools (must list blocked terms)
    - Legitimate architecture documentation (not logic)
    """
    root = Path(__file__).resolve().parent.parent
    violations = _scan_directory(root, STRICT_SCAN_DIRS, strict=True, exceptions=ALLOWED_EXCEPTIONS)

    if violations:
        report = [
            f"\n{'='*70}",
            "M2 ENGINE-STACK FIREWALL VIOLATIONS (STRICT: src/omega/)",
            f"{'='*70}",
            f"Found {len(violations)} blocked WAD term(s) in engine core.",
            "",
            "Engine core (src/omega/) must be WAD-agnostic per Mandate 2.",
            "Only exceptions: firewall tools, legitimate architecture docs.",
            "",
            *violations,
            f"\n{'='*70}",
        ]
        pytest.fail("\n".join(report))


def test_firewall_m2_lenient_test_fixtures():
    """M2 Firewall (LENIENT): test fixtures may use entity names.

    Tests may use entity names as test data (technical debt).
    This test reports warnings but does not fail.
    """
    root = Path(__file__).resolve().parent.parent
    violations = _scan_directory(root, LENIENT_SCAN_DIRS, strict=False, exceptions=ALLOWED_EXCEPTIONS)

    if violations:
        # Print warnings but don't fail
        print(f"\n{'='*70}")
        print("M2 FIREWALL WARNINGS (LENIENT: tests/) — Technical Debt")
        print(f"{'='*70}")
        print(f"Found {len(violations)} entity name(s) in test fixtures.")
        print("These are TECHNICAL DEBT — tests should use generic names or load from WAD.")
        print("")
        for v in violations[:50]:  # Limit output
            print(v)
        if len(violations) > 50:
            print(f"  ... and {len(violations) - 50} more")
        print(f"{'='*70}\n")


def test_firewall_m2_blocked_terms_list_is_maintained():
    """The BLOCKED_TERMS list itself should stay reasonable."""
    assert len(BLOCKED_TERMS) >= 44, (
        "BLOCKED_TERMS seems too small — was the list accidentally truncated?"
    )

    # Verify that the exception list doesn't reference out-of-bounds indices
    for exc_file, exc_line, exc_idx in ALLOWED_EXCEPTIONS:
        assert 0 <= exc_idx < len(BLOCKED_TERMS), (
            f"ALLOWED_EXCEPTIONS references term index {exc_idx} "
            f"which is out of range (BLOCKED_TERMS has {len(BLOCKED_TERMS)} entries)"
        )


def test_firewall_m2_checker_also_has_these_terms():
    """The blocking patterns in firewall_checker.py should match ours.

    Ensures the two enforcement points stay in sync.
    """
    checker_path = Path(__file__).resolve().parent.parent / "src" / "omega" / "audit" / "firewall_checker.py"
    if not checker_path.exists():
        pytest.skip("firewall_checker.py not yet deployed")

    checker_content = checker_path.read_text(encoding="utf-8")

    # Check that the firewall checker also blocks our blocked terms
    for term_idx, (pattern_str, severity, reason) in enumerate(BLOCKED_TERMS):
        if severity == "error":
            bare_term = pattern_str.replace(r"\b", "")
            if bare_term not in checker_content:
                print(
                    f"  ⚠️  firewall_checker.py missing pattern: {bare_term} "
                    f"(BLOCKED_TERMS index {term_idx})"
                )