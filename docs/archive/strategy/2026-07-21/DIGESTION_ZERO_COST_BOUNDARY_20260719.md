# 🔱 MaKaLi Digestion Layer — Zero-Cost Boundary Definition
**AP Token**: `AP-DIGESTION-ZERO-COST-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_digestion_boundary ⬡ 2026-07-19

---

## 🎯 The Core Problem

The MaKaLi Council architecture claims the **Report Digestion Layer** operates at "zero inference cost" — but the current implementation does semantic conflict detection, mandate compliance mapping, and cross-reference indexing in Python. This is **LLM work in Python clothing**.

---

## 🔪 Zero-Cost Boundary Definition (CARMACK RULING)

### ✅ ZERO-COST OPERATIONS (Allowed in Digestion Layer)
*These are purely syntactic/structural — no semantic understanding required*

| Operation | Example | Cost |
|-----------|---------|------|
| **Regex extraction** | `re.findall(r"L3-[A-Z][a-z]+", text)` | ~0.1ms |
| **Line/word counting** | `len(text.split())` | ~0.01ms |
| **Section header parsing** | `re.findall(r"^##\s+(.+)$", text, re.M)` | ~0.1ms |
| **Mandate tag detection** | `re.findall(r"M\d+", text)` | ~0.05ms |
| **File size / hash** | `hashlib.sha256(content).hexdigest()` | ~0.5ms |
| **Structural validation** | YAML/JSON syntax check | ~1ms |
| **Cross-reference by ID** | `if "R_CARMACK_REVIEW" in text` | ~0.01ms |
| **Token estimation** | `len(text) // 4` | ~0.01ms |

### ❌ LLM-COST OPERATIONS (Forbidden in Digestion Layer)
*These require semantic understanding — MUST be done by oversouls (Ma'at/Lilith) or Kali*

| Operation | Why It's LLM Work | Where It Belongs |
|-----------|-------------------|------------------|
| **Conflict detection** | "These two pillars contradict on M2" | Ma'at/Lilith synthesis |
| **Semantic synthesis** | "The core insight is X" | Kali final synthesis |
| **Mandate compliance judgment** | "This violates M2 because..." | Ma'at (build side) / Lilith (run side) |
| **Gap identification** | "Missing research on X" | Kali research gap list |
| **Priority ranking** | "This is more important than that" | Kali prioritization |
| **Cross-pillar correlation** | "P3's finding relates to P7's" | Oversouls |
| **Insight generation** | "What this means is..." | Oversouls/Kali |

---

## 🏗️ Minimal Viable Digestion Layer (Ships This Week)

```python
# src/omega/council/digestion.py — ~100 lines TOTAL

import re
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Set
from pathlib import Path

@dataclass
class DigestedReport:
    """Zero-cost structural digest of a pillar report."""
    pillar_id: str                    # "P3", "P7", etc.
    report_path: str
    sha256: str                       # Content hash for deduplication
    word_count: int
    sections: List[str]               # ["## Findings", "## Recommendations", ...]
    mandate_refs: List[str]           # ["M1", "M2", "M14", ...]
    research_gaps: List[str]          # Extracted from "## Research Gaps" section
    key_findings: List[str]           # First sentence of each finding paragraph
    timestamp: str

class ZeroCostDigester:
    """Purely syntactic report digestion — NO LLM CALLS."""
    
    SECTION_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    MANDATE_RE = re.compile(r"\bM(\d+)\b")
    GAP_SECTION_RE = re.compile(r"##\s*Research Gaps\s*\n(.*?)(?=\n##|\Z)", re.DOTALL | re.IGNORECASE)
    FINDING_RE = re.compile(r"^\s*[-*]\s*(.+?)(?:\n|$)", re.MULTILINE)
    
    def digest(self, report_path: Path) -> DigestedReport:
        content = report_path.read_text(encoding="utf-8")
        
        return DigestedReport(
            pillar_id=self._extract_pillar_id(report_path),
            report_path=str(report_path),
            sha256=hashlib.sha256(content.encode()).hexdigest()[:16],
            word_count=len(content.split()),
            sections=self.SECTION_RE.findall(content),
            mandate_refs=sorted(set(self.MANDATE_RE.findall(content))),
            research_gaps=self._extract_gaps(content),
            key_findings=self._extract_findings(content),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _extract_pillar_id(self, path: Path) -> str:
        # From path like "data/coordination/P3_REPORT_20260719.md"
        match = re.search(r"(P\d+)", path.name)
        return match.group(1) if match else "UNKNOWN"
    
    def _extract_gaps(self, content: str) -> List[str]:
        match = self.GAP_SECTION_RE.search(content)
        if not match:
            return []
        gap_text = match.group(1)
        return [g.strip() for g in self.FINDING_RE.findall(gap_text) if g.strip()]
    
    def _extract_findings(self, content: str) -> List[str]:
        # First sentence of each bullet in "## Key Findings" section
        findings_section = re.search(r"##\s*Key Findings\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
        if not findings_section:
            return []
        bullets = self.FINDING_RE.findall(findings_section.group(1))
        return [b.split(".")[0].strip() + "." for b in bullets if b.strip()][:10]
```

---

## 📊 What the Oversouls Get (Structured, Not Synthesized)

| Input to Ma'at/Lilith | Format | Purpose |
|----------------------|--------|---------|
| `DigestedReport` per pillar | JSON/dataclass | Structural index |
| `mandate_refs` | `["M1", "M2", "M14"]` | Quick compliance scan |
| `research_gaps` | `["Need M25 test", "Verify CG-004"]` | Kali research queue |
| `key_findings` | `["Gemma 4 works via Cline...", "Streaming fixed..."]` | Oversoul synthesis seed |
| `sha256` | `"a1b2c3d4..."` | Deduplication across runs |

---

## 🚫 What We Explicitly DO NOT Do

1. **No cross-pillar comparison** — Ma'at/Lilith do this
2. **No conflict resolution** — Kali does this
3. **No "this means that" interpretation** — Oversouls do this
4. **No priority scoring** — Kali does this
5. **No mandate violation judgment** — Ma'at/Lilith do this

---

## ✅ Validation Test (Zero-Cost Proof)

```python
def test_zero_cost():
    """Digestion must complete in <10ms per report, zero LLM calls."""
    import time
    digester = ZeroCostDigester()
    
    start = time.perf_counter()
    result = digester.digest(Path("data/coordination/P3_REPORT.md"))
    elapsed = (time.perf_counter() - start) * 1000
    
    assert elapsed < 10, f"Digestion took {elapsed:.1f}ms (max 10ms)"
    assert result.mandate_refs == ["M1", "M2", "M14", "M25"]
    assert "Gemma 4" in " ".join(result.key_findings)
    print(f"✅ Zero-cost digestion: {elapsed:.2f}ms")
```

---

## 🎯 Integration with MaKaLi T0

```
PHASE 1 (Parallel): 9 Pillars → 9 DigestedReports (ZeroCostDigester)
         ↓
PHASE 2 (Ma'at):     Read 5 DigestedReports → Write Ma'at_Synthesis.md
         ↓
PHASE 3 (Lilith):    Read 5 DigestedReports → Write Lilith_Synthesis.md
         ↓
PHASE 4 (Kali):      Read 2 Syntheses → Write FINAL_SYNTHESIS.md + RESEARCH_GAPS.md
```

**Total digestion time for 9 pillars**: ~50ms (not 9 × LLM calls)

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_digestion_boundary ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
