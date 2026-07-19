# 🔱 HG-001: MaKaLi Digestion Layer "Zero Cost" Boundary
**AP Token**: `AP-CARMACK-HG001-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19

---

## 🎯 Research Target
Define exact boundary: what distillation can be purely syntactic (regex, counting, structural) vs. semantic (requires LLM)?

---

## 📋 Current Architecture Analysis

### ReportDigestionLayer (Current Implementation)
```python
# src/omega/council/digestion.py (hypothetical current state)
class ReportDigestionLayer:
    def digest(self, reports: list[PillarReport]) -> DigestedReport:
        # CROSS-REFERENCE: O(n²) string comparison
        conflicts = self.detect_conflicts(reports)
        
        # MANDATE MAPPING: keyword search
        mandate_refs = self.map_mandates(reports)
        
        # SEMANTIC CONFLICT DETECTION: **LLM CALL HERE**
        semantic_conflicts = self.llm_detect_semantic_conflicts(reports)
        
        # SYNTHESIS: **LLM CALL HERE**
        synthesis = self.llm_synthesize(reports, conflicts, mandate_refs)
        
        return DigestedReport(...)
```

**Problem**: Claims "zero inference cost" but makes 2+ LLM calls per council session.

---

## 🔬 Zero-Cost Boundary Definition

### ✅ ZERO COST (Pure Python — No LLM Calls)

| Operation | Technique | Complexity | Example |
|-----------|-----------|------------|---------|
| **Exact duplicate detection** | Hash comparison (SHA256) | O(n) | `hash(report.content) in seen_hashes` |
| **Near-duplicate detection** | MinHash + LSH (datasketch) | O(n) | 3-gram Jaccard > 0.9 |
| **Keyword/phrase counting** | Regex + Counter | O(n) | `len(re.findall(r"M13|Temple-Grade", text))` |
| **Structural validation** | Schema check (pydantic) | O(1) | `DigestedReport.model_validate(obj)` |
| **Mandate reference extraction** | Regex pattern matching | O(n) | `re.findall(r"M\d{1,2}", text)` |
| **Citation/reference linking** | Exact string match on IDs | O(n) | `ref_id in all_known_ids` |
| **Section header parsing** | Markdown AST parsing | O(n) | `markdown_it.parse(text).get_headers()` |
| **Word/token counting** | `tiktoken` or `split()` | O(n) | `len(encoding.encode(text))` |
| **Conflict detection (explicit)** | Regex for "disagree", "contradict", "conflict" | O(n) | `re.search(r"\b(disagree|contradict)\b", text, re.I)` |
| **Action item extraction** | Regex for "- [ ]", "TODO:", "ACTION:" | O(n) | `re.findall(r"^[-*]\s+\[ \]\s+(.+)$", text, re.M)` |

### ⚠️ REQUIRES LLM (Semantic — "LLM Work in Python Clothing")

| Operation | Why LLM Required | Cost |
|-----------|------------------|------|
| **Implicit conflict detection** | "P3 says optimize for speed, P4 says add validation" — no shared keywords | 1 call |
| **Nuanced mandate interpretation** | "Does this violate M19?" requires understanding intent | 1 call |
| **Synthesis/narrative generation** | Writing coherent summary from 8 pillar reports | 1 call |
| **Priority arbitration** | "Which pillar's concern wins?" requires judgment | 1 call |
| **Cross-report entity resolution** | "The 'cache' in P2 vs 'memory' in P7 — same thing?" | 1 call |

---

## 🎯 Exact Boundary Specification

```python
# src/omega/council/digestion_boundary.py
"""
ZERO-COST BOUNDARY — Enforced by architecture.
Any function crossing this boundary MUST be marked @requires_llm
and routed through the ModelGateway with budget tracking.
"""

from functools import wraps
from typing import Callable, TypeVar

F = TypeVar('F', bound=Callable)

# ============================================================
# ZERO-COST OPERATIONS (Pure Python, No LLM)
# ============================================================

def hash_deduplicate(reports: list[Report]) -> list[Report]:
    """O(n) exact duplicate removal via content hash."""
    seen = set()
    unique = []
    for r in reports:
        h = hashlib.sha256(r.content.encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(r)
    return unique

def minhash_deduplicate(reports: list[Report], threshold: float = 0.9) -> list[Report]:
    """O(n) near-duplicate detection via MinHash LSH."""
    from datasketch import MinHash, MinHashLSH
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    unique = []
    for i, r in enumerate(reports):
        m = MinHash(num_perm=128)
        for shingle in get_shingles(r.content, k=3):
            m.update(shingle.encode())
        if not lsh.query(m):
            lsh.insert(str(i), m)
            unique.append(r)
    return unique

def extract_mandate_refs(text: str) -> set[str]:
    """Regex extraction of M## mandate references."""
    return set(re.findall(r"\bM\d{1,2}\b", text))

def extract_action_items(text: str) -> list[str]:
    """Regex extraction of action items."""
    patterns = [
        r"^[-*]\s+\[ \]\s+(.+)$",      # - [ ] task
        r"^TODO:\s*(.+)$",              # TODO: task
        r"^ACTION:\s*(.+)$",            # ACTION: task
    ]
    items = []
    for pat in patterns:
        items.extend(re.findall(pat, text, re.MULTILINE | re.IGNORECASE))
    return items

def detect_explicit_conflicts(text: str) -> list[Conflict]:
    """Regex detection of explicit disagreement language."""
    conflict_patterns = [
        r"\b(disagree|contradict|conflict with|oppose)\b",
        r"\b(inconsistent with|at odds with)\b",
    ]
    conflicts = []
    for pat in conflict_patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            conflicts.append(Conflict(
                type="explicit",
                span=text[max(0,match.start()-100):match.end()+100],
                confidence=0.9
            ))
    return conflicts

def validate_structure(obj: dict, schema: type[BaseModel]) -> ValidationResult:
    """Pydantic schema validation — zero cost."""
    try:
        schema.model_validate(obj)
        return ValidationResult(valid=True)
    except ValidationError as e:
        return ValidationResult(valid=False, errors=e.errors())

# ============================================================
# LLM-REQUIRED OPERATIONS (Cross boundary — budget tracked)
# ============================================================

def requires_llm(func: F) -> F:
    """Decorator marking functions that cross the zero-cost boundary."""
    func._requires_llm = True
    func._llm_budget_tokens = getattr(func, '_llm_budget_tokens', 2000)
    return func

@requires_llm
async def detect_semantic_conflicts(reports: list[Report]) -> list[Conflict]:
    """LLM call: Detect implicit semantic conflicts."""
    prompt = build_conflict_detection_prompt(reports)
    response = await model_gateway.generate(prompt, max_tokens=1000)
    return parse_conflicts(response)

@requires_llm
async def synthesize_digested_report(reports: list[Report], conflicts: list[Conflict]) -> DigestedReport:
    """LLM call: Synthesize coherent narrative from pillar reports."""
    prompt = build_synthesis_prompt(reports, conflicts)
    response = await model_gateway.generate(prompt, max_tokens=3000)
    return parse_digested_report(response)

@requires_llm
async def arbitrate_priorities(conflicts: list[Conflict], mandates: set[str]) -> ArbitrationResult:
    """LLM call: Resolve priority between conflicting pillar concerns."""
    prompt = build_arbitration_prompt(conflicts, mandates)
    response = await model_gateway.generate(prompt, max_tokens=1500)
    return parse_arbitration(response)

# ============================================================
# ORCHESTRATOR (Enforces boundary)
# ============================================================

class DigestionOrchestrator:
    """Enforces zero-cost boundary — tracks LLM budget."""
    
    def __init__(self, max_llm_calls: int = 3, max_llm_tokens: int = 6000):
        self.max_llm_calls = max_llm_calls
        self.max_llm_tokens = max_llm_tokens
        self.llm_calls = 0
        self.llm_tokens = 0
    
    async def digest(self, reports: list[PillarReport]) -> DigestedReport:
        # PHASE 1: Zero-cost preprocessing (unlimited)
        reports = hash_deduplicate(reports)
        reports = minhash_deduplicate(reports)
        
        all_mandates = set()
        all_actions = []
        explicit_conflicts = []
        
        for r in reports:
            all_mandates.update(extract_mandate_refs(r.content))
            all_actions.extend(extract_action_items(r.content))
            explicit_conflicts.extend(detect_explicit_conflicts(r.content))
        
        # PHASE 2: LLM-required operations (BUDGET ENFORCED)
        semantic_conflicts = []
        if self.llm_calls < self.max_llm_calls:
            semantic_conflicts = await detect_semantic_conflicts(reports)
            self.llm_calls += 1
        
        arbitration = None
        if explicit_conflicts or semantic_conflicts:
            if self.llm_calls < self.max_llm_calls:
                arbitration = await arbitrate_priorities(
                    explicit_conflicts + semantic_conflicts, all_mandates
                )
                self.llm_calls += 1
        
        synthesis = None
        if self.llm_calls < self.max_llm_calls:
            synthesis = await synthesize_digested_report(reports, explicit_conflicts + semantic_conflicts)
            self.llm_calls += 1
        
        return DigestedReport(
            reports=reports,
            mandates=sorted(all_mandates),
            actions=all_actions,
            explicit_conflicts=explicit_conflicts,
            semantic_conflicts=semantic_conflicts,
            arbitration=arbitration,
            synthesis=synthesis,
            llm_budget_used={"calls": self.llm_calls, "tokens": self.llm_tokens}
        )
```

---

## 📊 Cost Analysis

| Council Session | Zero-Cost Ops | LLM Calls | Est. Tokens | Est. Cost (Nemotron) |
|-----------------|---------------|-----------|-------------|---------------------|
| **Before (claimed zero)** | 0 | 3-4 | ~8,000 | $0 (local) but latency |
| **After (enforced boundary)** | 5-8 | 2-3 | ~5,500 | $0 (local) + tracked |

**Key Insight**: Local inference is "free" in dollars but NOT free in latency (30s+ for Nemotron). The boundary matters for **council latency**, not cost.

---

## 🔬 id Software Qualification Gate

| Aspect | id Software Analog | Digestion Boundary |
|--------|-------------------|-------------------|
| **Constraint** | 486 CPU, no FPU | Nemotron 30s+ latency per call |
| **Technique** | Fixed-point math (integer only) | Pure Python ops only (no LLM) |
| **Justification** | FPU emulation too slow | LLM call = 30s stall |
| **Scope** | Renderer math only | Digestion preprocessing only |

**Verdict**: **PASSES** — Latency constraint is real; boundary prevents unbounded LLM calls.

---

## 📝 Implementation Checklist

- [ ] Create `digestion_boundary.py` with zero-cost functions
- [ ] Add `@requires_llm` decorator with budget tracking
- [ ] Refactor `ReportDigestionLayer` to use `DigestionOrchestrator`
- [ ] Add `max_llm_calls=3` config to `config/council.yaml`
- [ ] Write tests: `tests/test_digestion_boundary.py`
- [ ] Document: "Zero cost = zero LLM calls in preprocessing phase"

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_research ⬡ 2026-07-19*