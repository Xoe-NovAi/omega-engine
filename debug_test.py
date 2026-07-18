import re
from pathlib import Path

BLOCKED_TERMS = [
    (r"\bDa[']?at\b", "error", "WAD-only Kabbalistic term (Da'at/Knowledge sphere)"),
    (r"\bDa[']?ath\b", "error", "WAD-only Kabbalistic term (variant spelling)"),
    (r"\bQliphoth\b", "error", "WAD-only Qliphotic shell concept"),
    (r"\bKlipot\b", "error", "WAD-only Qliphotic shell concept (alt spelling)"),
    (r"\bSephiroth\b", "error", "WAD-only Sephirotic tree concept"),
    (r"\bSephirah\b", "error", "WAD-only individual sephirah term"),
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
    (r"\bKabbal(?:ah|istic|ist)\b", "error", "WAD-only Kabbalistic tradition references"),
    (r"\bCabalistic\b", "error", "WAD-only Kabbalistic tradition references"),
    (r"\bMnemosyne\b", "error", "WAD-only memory system archetype (Arcana-Nova)"),
    (r"\bArcana.?Novai?\b", "error", "WAD-only stack name (Arcana-Nova)"),
    (r"\bTorment.?Stack\b", "error", "WAD-only stack name (Torment Stack)"),
    (r"\bDoom.?Universe\b", "error", "WAD-only stack name (Doom Universe)"),
    (r"\b_omega_default\b", "error", "WAD-only IWAD name (default IWAD)"),
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
    (r"\bKali\b", "error", "WAD entity name (_omega_default Grand Oversight)"),
    (r"\bMa[']?at\b", "error", "WAD entity name (_omega_default Light Oversoul/CTO)"),
    (r"\bLilith\b", "error", "WAD entity name (_omega_default Dark Oversoul/CISO)"),
    (r"\bMakali\b", "error", "WAD entity name (_omega_default MaKaLi synthesis)"),
    (r"\bJohn.?Carmack\b", "error", "WAD entity name (Doom Universe S3 Consultant)"),
    (r"\bDoom.?Guy\b", "error", "WAD entity name (Doom Universe Architect)"),
    (r"\bRoc.?Rac?oon\b", "error", "WAD entity name (Legacy Miner)"),
    (r"\bJem\b", "error", "WAD entity name (Synthesizer)"),
    (r"\bVetala\b", "error", "WAD entity name (Content Integrity)"),
]

exceptions = [
    ("src/omega/audit/mandate_auditor.py", 14, 77), # Iris (docstring)
]

content = Path("src/omega/audit/mandate_auditor.py").read_text()
for line_num, line in enumerate(content.splitlines(), start=1):
    if line_num == 14:
        stripped = line.strip()
        if stripped.startswith("#"):
            print("SKIPPED: starts with #")
        elif stripped.startswith('"""') or stripped.startswith("'''"):
            print("SKIPPED: starts with docstring")
        else:
            code = line.split(" #")[0].split("\t#")[0]
            print(f"Line 14 code: '{code}'")
            for term_idx, (pattern_str, severity, reason) in enumerate(BLOCKED_TERMS):
                if re.search(pattern_str, code, re.IGNORECASE):
                    print(f"  Match: term_idx={term_idx}, pattern={pattern_str}")
                    for exc_file, exc_line, exc_idx in exceptions:
                        rel_str = "src/omega/audit/mandate_auditor.py"
                        if exc_idx == term_idx and rel_str.endswith(exc_file):
                            if exc_line is None or exc_line == line_num:
                                print(f"  EXCEPTION MATCHES!")
                            else:
                                print(f"  Exception line mismatch: {exc_line} != {line_num}")