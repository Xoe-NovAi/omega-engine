---
schema_version: "1.0"
document_type: "research_deliverable"
document_id: "RESEARCHER-GAP-FILL-PHASE-2-20260830"
title: "Sovereign Researcher — Phase 2 MEDIUM Gap Research"
status: "COMPLETE"
date: "2026-08-30"
entity: "researcher"
model: "mimo-v2.5-free"
sprint: "PUBLIC-DEBUT-01"
---

⬡ OMEGA ⬡ RESEARCHER ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

# Sovereign Researcher — Phase 2: MEDIUM Gap Research

> **Research Protocol**: Perspective Triangulation via Council of Four
> **M23 Compliance**: All findings grounded in live web research + codebase analysis (Aug 30, 2026)
> **Phase**: 2 of 3 — MEDIUM gaps (6 gaps)
> **Foundation**: Builds on `RESEARCHER_GAP_DEEP_DIVE_20260830.md` + `RESEARCHER_M33_M36_M37_20260830.md`
> **Tool Note**: Used `parallel-search_web_search` (initial) + codebase analysis (after rate limit). SearXNG/exa unavailable.

---

## §0 — Executive Summary

All 6 MEDIUM gaps researched. All have pre-existing partial implementations in `RESEARCHER_M33_M36_M37_20260830.md`; this report consolidates them and adds the latest API/benchmark data for production wiring.

| Gap ID | Gap Name | Confidence | Est. Time | Status |
|--------|----------|------------|-----------|--------|
| MED-1 | sqlite-vec + FTS5 + R-tree hybrid search | HIGH | 6h (benchmark) | Spec exists, needs 10K test |
| MED-2 | ScanCode Toolkit integration patterns | HIGH | 2h (CLI wire) | CLI pattern standard |
| MED-3 | REUSE v3.3 compliance patterns | HIGH | 1h (CI hook) | Pattern standard |
| MED-4 | SLSA v1.1 provenance generation | HIGH | 4h (spec only) | Spec designed, needs review |
| MED-5 | in-toto attestation layout | HIGH | 4h (spec only) | Spec designed, needs review |
| MED-6 | COHORT_REGISTRY.json schema validation | HIGH | 4h (code) | Schema defined, code in §6 of M33-M36-M37 |

**Total Phase 2 estimate**: ~21h

---

## §1 — MED-1: sqlite-vec + FTS5 + R-tree Hybrid Search Performance

### Research Findings

**State of the Art (Aug 2026)**:

1. **Alex Garcia's canonical hybrid search (Oct 2024)** — the reference implementation:
   - FTS5 + sqlite-vec + Reciprocal Rank Fusion (RRF)
   - Combines BM25 keyword scores with vector cosine/L2 distance
   - RRF formula: `score = 1/(k + rank_fts) + 1/(k + rank_vec)` where k=60
   - Configurable weights: `:weight_fts` and `:weight_vec`
   - Full SQL pattern with CTEs (vec_matches, fts_matches, final)

2. **sqlite-hybrid (tailorlite, npm)**:
   - Wraps `sqlite-vec` for vector ops + SQLite FTS5 for keyword search
   - Automates vec0 companion table + FTS5 virtual table sync
   - Intercept INSERT/UPDATE/DELETE on indexed tables via sync triggers
   - JSON column support via `json_extract()`
   - RRF fusion built in

3. **sqlite-vec KNN benchmarks (official, asg017/sqlite-vec)**:
   - Datasets: cohere1m (1M vectors, 768d), cohere10m (10M)
   - Index types: brute-force (float/int8/bit), rescore, IVF, DiskANN
   - Make targets: `bench-10k`, `bench-50k`, `bench-100k`, `bench-all`
   - Results DB: `runs/<dataset>/<subset_size>/results.db` (SQLite WAL mode)
   - Query KNN at 10K vectors: sub-50ms typical

4. **retrieval-skill (c-h-)**:
   - Vector (60% weight) + FTS5 (40% weight) + recency boost
   - Octen-Embedding-8B (4096-dim) + sqlite-vec + BM25
   - RRF fusion across text, keyword, vision lanes
   - Multi-vector ColQwen2.5 for PDF page embeddings

5. **Performance at scale**:
   - <100K vectors: brute-force KNN, <50ms
   - 100K-1M: IVF or scalar quantization rescore
   - >1M: DiskANN index type
   - 10K vectors: combined hybrid <100ms typical (FTS5 <10ms + KNN <50ms + RRF overhead)

**R-tree integration**: Per Alex Garcia's blog, R-tree is for spatial data (geographic coordinates). For Omega's text+embedding use case, R-tree is NOT needed. The vec0 metadata columns handle filtering without R-tree. R-tree is only relevant if Omega implements VR spatial navigation (Decision 28).

**Omega-specific data shape**:
- The codebase has `omega_memory_get_history()` (conversation retrieval)
- FTS5 index on `soul.yaml`, `proposed_lessons.yaml`, research reports
- vec0 on embeddings of same content
- Hybrid search for RAG retrieval

### Code Pattern (Production)

```sql
-- FTS5 results CTE
WITH fts_matches AS (
  SELECT rowid, rank 
  FROM fts_documents 
  WHERE content MATCH :query 
  LIMIT :k
),
-- vec0 KNN results CTE
vec_matches AS (
  SELECT rowid, distance 
  FROM vec_documents
  WHERE embedding MATCH lembed(:query) AND k = :k
  ORDER BY distance
),
-- RRF fusion
combined AS (
  SELECT 
    COALESCE(fts.rowid, vec.rowid) AS rowid,
    COALESCE(1.0 / (:rrf_k + fts.rank), 0.0) * :weight_fts +
    COALESCE(1.0 / (:rrf_k + vec.distance), 0.0) * :weight_vec AS score
  FROM fts_matches fts
  FULL OUTER JOIN vec_matches vec ON fts.rowid = vec.rowid
  JOIN documents ON documents.rowid = COALESCE(fts.rowid, vec.rowid)
  ORDER BY score DESC
)
SELECT * FROM combined LIMIT :k;
```

### Benchmarking Strategy

1. **Build test corpus**: 10K research reports, 10K heritage.yaml entries
2. **Ingest to both FTS5 and vec0** (using all-MiniLM-L6-v2 or similar 384-dim)
3. **Query benchmarks**:
   - Cold query latency: <100ms
   - Warm query (cached): <10ms
   - RRF overhead: <5ms
4. **Scaling test**: 10K → 50K → 100K → 1M vectors
5. **Edge cases**: Empty results, single-source matches, no-overlap

### Evidence
- Alex Garcia blog: https://alexgarcia.xyz/blog/2024/sqlite-vec-hybrid-search/
- sqlite-hybrid: https://github.com/tailorlite/sqlite-hybrid
- sqlite-vec benchmarks: https://github.com/asg017/sqlite-vec/tree/main/benchmarks-ann
- retrieval-skill: https://github.com/c-h-/retrieval-skill
- Simon Willison summary: https://simonwillison.net/2024/Oct/4/hybrid-full-text-search-and-vector-search-with-sqlite/

### Recommendation
**Implement the Alex Garcia RRF pattern in `src/omega/memory/hybrid_search.py`** with `weight_fts=0.4, weight_vec=0.6` (text + semantic, weighted toward semantic). Use the official `benchmarks-ann` framework for scaling tests. Skip R-tree — use vec0 metadata columns for filtering. Target <100ms p95 at 10K vectors.

**Estimated time**: 6h (4h code + 2h benchmark)
**Confidence**: HIGH — Pattern is standard, benchmark framework is ready-made

---

## §2 — MED-2: ScanCode Toolkit Integration Patterns

### Research Findings

**State of the Art (Aug 2026)**:

1. **ScanCode is dual-mode**: CLI tool AND Python library (importable)
2. **CLI flags** (per `scancode --help`):
   - `-c` copyrights, `-l` licenses, `-p` packages, `-e` emails, `-u` URLs, `-i` info
3. **Output formats**:
   - `--json` (compact)
   - `--json-pp` (pretty-printed, recommended)
   - `--json-lines` (one file per line)
   - `--yaml`
   - `--csv` (deprecated)
   - `--html` / `--html-app` (latter deprecated, use Workbench)
   - `--spdx-rdf` / `--spdx-tv` (SPDX 2.1)
   - `--cyclonedx` / `--cyclonedx-xml` (CycloneDX 1.3 BOM)
   - `--debian` (machine-readable Debian copyright format)
   - `--custom-output` with Jinja templates
4. **Performance controls**:
   - `--max-in-memory` (default 10000, use 0 for unlimited)
   - `--max-depth` (directory recursion)
5. **Scan pipeline**:
   1. Collect inventory + classify
   2. Extract archives (libarchive/bsdtar, 7zip)
   3. Extract text from binary
   4. Detect licenses (rule engine)
   5. Capture copyright statements
   6. Identify packaged code
   7. Report in chosen format

**Pre-existing implementation**: `RESEARCHER_M33_M36_M37_20260830.md` has `HeritageScanner` class in §3 (M37-HERITAGE-001) with `_create_pre_commit_config()` and `generate_github_action()` methods.

### Recommended Pattern for Omega

**Phase A: CLI subprocess wrapper** (initial deployment)
```python
# In scripts/heritage_scanner.py (already designed in M33-M36-M37)
import subprocess, json
from pathlib import Path

def scan_for_heritage(root: Path, output: Path) -> dict:
    result = subprocess.run([
        "scancode", 
        "--json-pp", str(output),
        "--copyright", "--license", "--package",
        "--info", str(root)
    ], capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise HeritageScanError(result.stderr)
    return json.loads(output.read_text())
```

**Phase B: Python API** (after CLI proven)
- ScanCode's internal modules: `scancode.api`, `scancode.scan`
- Direct import for tighter integration
- Faster than subprocess (no process spawn)
- Better error handling

**Phase C: CI integration**
- GitHub Action: `scancode-toolkit-action` (community) or custom
- Pre-commit: `pre-commit run --all-files` (M37 already creates config)
- GitHub Actions: `actions/checkout` → install ScanCode → `scancode --json-pp`
- Output to `data/heritage/scancode-omega-spdx.json`
- Generate `omega.spdx.json` for regulatory compliance

### Evidence
- ScanCode docs: https://scancode-toolkit.readthedocs.io/en/stable/
- Output formats: https://nexb-skeleton.readthedocs.io/en/stable/cli-reference/output-format.html
- CLI reference: https://scancode-toolkit.readthedocs.io/en/stable/reference/scancode-cli/index.html
- PyPI: https://pypi.org/project/scancode-toolkit/
- License detection: https://scancode-toolkit.readthedocs.io/en/stable/explanation/scancode-license-detection.html

### Recommendation
**Use CLI subprocess wrapper initially** (already designed in `M33-M36-M37` §3). Add GitHub Action step that runs ScanCode on every PR, archives SPDX document to `data/heritage/`. Use `--json-pp` for human-readable, `--spdx-tv` for regulatory SBOM. Pin ScanCode version in CI to ensure reproducibility.

**Estimated time**: 2h (CLI wire + CI step)
**Confidence**: HIGH

---

## §3 — MED-3: REUSE v3.3 Compliance Patterns

### Research Findings

**State of the Art (Aug 2026)**:

1. **REUSE tool v6.2.0** is the current release. Despite the spec being v3.3, the tool has moved to v6.x major versions.

2. **CLI commands**:
   - `reuse lint` — verify REUSE compliance (exit 0 = compliant)
   - `reuse annotate` — bulk add headers to files
   - `reuse download` — fetch license texts
   - `reuse spdx` — generate SPDX document
   - `reuse supported-licenses` — list all supported SPDX identifiers
   - `reuse convert-dep5` — convert old `.reuse/dep5` to `REUSE.toml`
   - `reuse lint-file` — lint individual files

3. **Pre-commit integration**:
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://codeberg.org/fsfe/reuse-tool
       rev: v6.2.0
       hooks:
         - id: reuse           # Lint whole project
         # OR per-file (faster on large repos):
         - id: reuse-lint-file
   ```

4. **GitHub Action**: `fsfe/reuse-action@v6`
   ```yaml
   - uses: fsfe/reuse-action@v6
     with:
       args: lint
   ```
   - `args: spdx` generates SBOM
   - `args: --include-submodules lint` includes git submodules

5. **Bulk annotation pattern**:
   ```bash
   reuse annotate --copyright="Arcana Novai" --license=Apache-2.0 src/omega/**/*.py
   ```
   - Auto-detects comment style per extension
   - Skips already-annotated files
   - `--skip-unrecognised` flag for non-annotated files
   - Jinja2 template support for custom header formats

6. **REUSE.toml** (modern config, replaces `.reuse/dep5`):
   ```toml
   version = 1
   [[annotations]]
   path = "src/**/*.py"
   SPDX-FileCopyrightText = "2026 Arcana Novai"
   SPDX-License-Identifier = "Apache-2.0"
   ```

7. **Docker**: `docker run --rm -v $(pwd):/data fsfe/reuse lint`

### Bulk Annotation for Omega

**Step 1: Check current state**
```bash
reuse lint
```
Expected output: List of non-compliant files.

**Step 2: Add REUSE.toml for project-level config**
```toml
# REUSE.toml
version = 1
[[annotations]]
path = "src/**/*.py"
SPDX-FileCopyrightText = "2026 Arcana Novai"
SPDX-License-Identifier = "Apache-2.0"

[[annotations]]
path = "config/**/*.yaml"
SPDX-FileCopyrightText = "2026 Arcana Novai"
SPDX-License-Identifier = "Apache-2.0"

[[annotations]]
path = "data/**/*.json"
SPDX-FileCopyrightText = "2026 Arcana Novai"
SPDX-License-Identifier = "Apache-2.0"

[[annotations]]
path = "scripts/**/*.py"
SPDX-FileCopyrightText = "2026 Arcana Novai"
SPDX-License-Identifier = "Apache-2.0"
```

**Step 3: Bulk annotate**
```bash
# All Python source files
reuse annotate --copyright="Arcana Novai" --license=Apache-2.0 \
  $(find src/omega -name "*.py" -type f)

# All YAML config files
reuse annotate --copyright="Arcana Novai" --license=Apache-2.0 \
  $(find config -name "*.yaml" -type f)
```

**Step 4: Verify compliance**
```bash
reuse lint
```

**Step 5: Add to CI**
```yaml
# .github/workflows/reuse-compliance.yml
name: REUSE Compliance
on: [push, pull_request]
jobs:
  reuse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: fsfe/reuse-action@v6
```

**Step 6: Generate SPDX SBOM**
```bash
reuse spdx -o data/heritage/omega-spdx.json
```

### Evidence
- REUSE docs: https://reuse.readthedocs.io/en/stable/
- annotate man: https://reuse.readthedocs.io/en/stable/man/reuse-annotate.html
- GitHub Action: https://github.com/fsfe/reuse-action
- Pre-commit setup: https://reuse.readthedocs.io/en/stable/readme.html

### Recommendation
**Use `REUSE.toml` for project-level config** + `reuse-action@v6` in CI. Bulk annotate all Python files first, then verify. Add to pre-commit for individual file lint. The pattern is well-standardized — minimal risk.

**Estimated time**: 1h (REUSE.toml + GitHub Action)
**Confidence**: HIGH

---

## §4 — MED-4: SLSA v1.1 Provenance Generation

### Research Findings

**State of the Art (Aug 2026)**:

1. **SLSA v1.1 is current** (v1.2 also released). The provenance format is `https://slsa.dev/provenance/v1`.

2. **Recommended Suite** (per SLSA spec):
   | Component | Recommendation |
   |-----------|---------------|
   | Envelope | **DSSE** (ECDSA NIST P-256 + SHA-256) |
   | Statement | **in-toto attestations** |
   | Predicate | SLSA Provenance, SPDX, or custom |
   | Bundle | JSON Lines |
   | Storage | TBD |

3. **Tool landscape**:
   - **slsa-github-generator**: DEPRECATED Feb 2025 — "no longer actively maintained"
   - **GitHub Artifact Attestations** (`actions/attest-build-provenance@v1`): official replacement, achieves SLSA Build L2 out of the box, uses Sigstore keyless signing
   - **sigstore** Python (v4.5.0, Jul 2026): full programmatic API for SLSA provenance via DSSE
   - **slsa-verifier** (`slsa-framework/slsa-verifier`): verification tool

4. **GitHub Action for Python packages** (the path of least resistance):
   ```yaml
   # .github/workflows/release.yml
   permissions:
     id-token: write       # OIDC for Sigstore
     attestations: write   # Store attestation
   jobs:
     release:
       steps:
         - run: poetry build
         - uses: actions/attest-build-provenance@v1
           with:
             subject-path: "dist/*"
         - uses: pypa/gh-action-pypi-publish@release/v1
   ```
   - Result: `github.com/<owner>/<repo>/attestations` page
   - Verification: `gh attestation verify <artifact>`

5. **For local builds (sovereign path)**: Use `sigstore` Python directly
   ```python
   from sigstore.sign import SigningContext
   
   ctx = SigningContext.production()
   signer = ctx.signer()
   with signer.sign_artifact(artifact_path) as bundle:
       # bundle is a sigstore.Bundle (DSSE envelope)
   ```

6. **Attestation format** (in-toto Statement):
   ```json
   {
     "_type": "https://in-toto.io/Statement/v1",
     "subject": [{"name": "dist/omega-1.2.0.tar.gz", "digest": {"sha256": "..."}}],
     "predicateType": "https://slsa.dev/provenance/v1",
     "predicate": {
       "buildDefinition": {
         "buildType": "https://slsa-framework.github.io/source-iterators/v0.1",
         "externalParameters": {"buildCommand": "python -m build"},
         "internalParameters": {...},
         "resolvedDependencies": [...]
       },
       "runDetails": {
         "builder": {"id": "https://github.com/actions/runner"},
         "metadata": {
           "buildInvocationId": "...",
           "buildStartedOn": "...",
           "buildFinishedOn": "...",
           "completeness": {"parameters": true, "environment": false, "materials": true},
           "reproducible": false
         }
       }
     }
   }
   ```

7. **For Omega (sovereign local-first)**: The `sigstore` Python package is the safest choice — no GitHub dependency. However, for OpenSSF Best Practices badge, GitHub Artifact Attestations is the path of least resistance.

**Pre-existing implementation**: `RESEARCHER_M33_M36_M37_20260830.md` §3 (M37-HERITAGE-001) has a detailed `HeritageScanner` class with:
- `_emit_slsa_provenance()` method
- `_sha256_file()` / `_sha256_dir()` methods
- `_git_rev_parse()` for git integration
- SLSA Build L2 compliance target
- GitHub Actions workflow generator

### Evidence
- SLSA spec v1.1: https://slsa.dev/spec/v1.0/about
- SLSA attestation model: https://github.com/slsa-framework/slsa/blob/releases/v1.0/spec/attestation-model.md
- GitHub Action: https://github.com/actions/attest-build-provenance
- sigstore Python: https://sigstore.github.io/sigstore-python
- Python example: https://browniebroke.com/blog/2024-08-08-attest-build-provenance-for-a-python-package-in-github-actions/

### Recommendation
**Two-pronged strategy**:
1. **GitHub Actions CI**: Use `actions/attest-build-provenance@v1` for SLSA L2 on release artifacts (low friction, free)
2. **Local sigstore**: Use `sigstore` Python for local builds, signing wheel/sdist with OIDC if available, or key-based for offline

The spec in `M33-M36-M37` §3 is well-designed. Add this to the 8h Phase 1 item (M37 SPDX Headers) — they're the same workstream.

**Estimated time**: 4h (review existing spec, add sigstore Python wrapper)
**Confidence**: HIGH

---

## §5 — MED-5: in-toto Attestation Layout

### Research Findings

**State of the Art (Aug 2026)**:

1. **in-toto** is CNCF graduated (April 2025). The Python reference implementation is `pip install in-toto` (v3.0.0+).

2. **Core concepts**:
   - **Layout**: Top-level metadata that defines the supply chain steps
   - **Step**: A single build step (e.g., compile, test, package)
   - **Inspection**: A checkpoint (e.g., QA, security review)
   - **Functionary**: Authorized identity that executes a step (key, Sigstore identity)
   - **Material rule**: Filter for input files (e.g., `ALLOW src/*`)
   - **Product rule**: Filter for output files (e.g., `CREATE dist/*`)
   - **Link**: Metadata file (.link) emitted by `in-toto-run` proving a step executed

3. **Production usage**:
   - Datadog (since 2019)
   - SolarWinds (post-SUNBURST adoption)
   - Bazel Central Registry (recent)

4. **Sub-projects**:
   - **Witness**: Attestation collector (reduces adoption friction)
   - **Archivista**: Attestation storage server
   - **in-toto-attestation**: Statement + Predicate framework

5. **Minimal layout pattern**:
   ```python
   from in_toto.models.layout import Layout, Step
   from in_toto.models.metadata import Metablock, Envelope
   
   layout = Layout()
   
   # Step 1: Build
   build_step = Step(name="build")
   build_step.set_expected_command_from_string("python -m build")
   build_step.add_material_rule_from_string("ALLOW src/*")
   build_step.add_product_rule_from_string("CREATE dist/*")
   
   # Step 2: Sign with heritage signature
   sign_step = Step(name="sign")
   sign_step.set_expected_command_from_string("sigstore sign dist/*.whl")
   sign_step.add_material_rule_from_string("ALLOW dist/*")
   sign_step.add_product_rule_from_string("ALLOW *.sig")
   
   layout.steps = [build_step, sign_step]
   
   # Serialize
   metadata = Metablock(signed=layout)
   ```

6. **`in-toto-run`** (most common entry point):
   ```bash
   in-toto-run --step-name build \
     --signing-key key.pub \
     --materials src/ \
     --products dist/ \
     -- python -m build
   ```
   This creates a `.link` file proving the step executed as expected.

7. **`in-toto-verify`**:
   ```bash
   in-toto-verify --layout root.layout \
     --verification-keys key.pub
   ```
   Walks the layout, verifies each link was signed by the authorized functionary, validates material/product rules.

8. **Attestation framework** (in-toto.io/Statement/v1):
   ```json
   {
     "_type": "https://in-toto.io/Statement/v1",
     "predicateType": "https://slsa.dev/provenance/v1",
     "subject": [...],
     "predicate": {...}
   }
   ```

**For Omega's heritage tracking**:

A heritage layout would define the following steps:
1. **fetch**: Git checkout of source (functionary: CI bot, Sigstore identity)
2. **scan**: ScanCode + REUSE lint (functionary: researcher entity)
3. **build**: `python -m build` (functionary: maat entity)
4. **heritage_attest**: Generate heritage.yaml with provenance (functionary: m37 heritage scanner)
5. **sign**: Sigstore sign the wheel + .link files (functionary: maat or build agent)
6. **inspect**: Heritage validation (functionary: verity or architect)

**Link chain**: `fetch.link → scan.link → build.link → heritage_attest.link → sign.link → inspect.link`

Each link is signed by the functionary's key (or Sigstore identity). The layout's `expires` field limits validity.

### Evidence
- in-toto docs: https://in-toto.readthedocs.io/en/latest/
- Layout example: https://in-toto.readthedocs.io/en/latest/layout-creation-example.html
- Production use: https://oneuptime.com/blog/post/2026-02-09-artifact-attestation-in-toto/view
- BCR discussion: https://github.com/bazelbuild/bazel-central-registry/discussions/2721

### Recommendation
**Use `in-toto-run` to wrap heritage build steps** (simplest entry point). Define a layout with 4-6 steps (fetch, scan, build, heritage_attest, sign, inspect). Use Sigstore identities as functionaries (no key management). Store the layout and all link files in `data/heritage/`.

The `M33-M36-M37` §3 spec already has the framework — this gap is about finalizing the layout, not designing from scratch.

**Estimated time**: 4h (layout definition + test run)
**Confidence**: HIGH

---

## §6 — MED-6: COHORT_REGISTRY.json Schema Validation

### Research Findings

**State of the Art (Aug 2026)**:

1. **Pydantic v2 dataclasses** — automatic JSON Schema generation:
   ```python
   from pydantic.dataclasses import dataclass
   from pydantic import TypeAdapter
   
   @dataclass
   class ActiveSubagent:
       session_id: str
       parent_session_id: Optional[str] = None
       status: SessionStatus = SessionStatus.ALIVE
       # ...
   
   # Generate JSON Schema
   schema = TypeAdapter(ActiveSubagent).json_schema()
   # Or: ActiveSubagent.__pydantic_json_schema__ if BaseModel
   ```

2. **Standard library dataclasses** work with `jsonschema` directly but need manual schema definition.

3. **M34 ActiveSubagent** is a standard library dataclass (not pydantic). Conversion path:
   - Add `@pydantic.dataclasses.dataclass` decorator (preserves stdlib behavior)
   - Use `TypeAdapter(ActiveSubagent).json_schema()` to generate schema
   - Validate with `jsonschema.validate(instance, schema)`

**Pre-existing implementation**: `RESEARCHER_M33_M36_M37_20260830.md` §6 (COHORT-REGISTRY-001) has a complete JSON Schema (v1.0) and a `CohortRegistry` class. Key design points:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://omega-engine/cohort_registry/v1",
  "title": "Omega Cohort Registry",
  "type": "object",
  "required": ["version", "updated", "cohorts"],
  "properties": {
    "version": {"const": "1.0"},
    "updated": {"type": "string", "format": "date-time"},
    "cohorts": {
      "type": "object",
      "additionalProperties": {"$ref": "#/$defs/cohort"}
    }
  },
  "$defs": {
    "cohort": {
      "type": "object",
      "required": ["cohort_id", "dispatched_by", "subagent_ids", "cohort_type", "created_at"],
      "properties": {
        "cohort_id": {"type": "string", "pattern": "^cohort_[a-z0-9]{8,}$"},
        "dispatched_by": {
          "type": "string",
          "enum": ["kali", "grokster", "lilith", "maat", "researcher", "roc_racoon", "node", "sophia", "verity"]
        },
        "subagent_ids": {
          "type": "array",
          "items": {"type": "string", "pattern": "^ses_[a-z0-9]+$"},
          "minItems": 1
        },
        "cohort_type": {
          "type": "string",
          "enum": ["EIS_BURST", "RESEARCH_PAIR", "IMPLEMENT_TRIO", "FLEET_DISPATCH", "PIPELINE"]
        },
        "status": {"type": "string", "enum": ["ALIVE", "COMPLETED", "FAILED", "ABANDONED", "DEAD_LETTER", "INTERRUPTED"]},
        "resumption_count": {"type": "integer", "minimum": 0, "default": 0},
        "m34_registry_ref": {"type": "const": "ACTIVE_SUBAGENTS.json"}
      }
    }
  }
}
```

**Validation against M34 ActiveSubagent**:
- The `subagent_ids` array in COHORT_REGISTRY must reference valid `session_id`s in `ACTIVE_SUBAGENTS.json`
- Cross-validation: for each cohort, check every `subagent_id` exists in M34 registry
- Use `jsonschema` library (already in pyproject.toml: `jsonschema==4.26.0`)

**Implementation path** (from M33-M36-M37 §6.3):
```python
# src/omega/oracle/cohort_registry.py
import jsonschema
import json
from pathlib import Path

class CohortRegistry:
    def __init__(self, registry_path: str = "data/coordination/COHORT_REGISTRY.json"):
        self.path = Path(registry_path)
        self.schema = self._load_schema()
    
    def _load_schema(self) -> dict:
        schema_path = Path("docs/coordination/cohort_registry_schema.json")
        return json.loads(schema_path.read_text())
    
    def validate(self, instance: dict) -> bool:
        jsonschema.validate(instance=instance, schema=self.schema)
        return True
    
    def cross_validate_against_m34(self, m34_registry_path: str) -> list[str]:
        """Return list of cross-validation errors."""
        errors = []
        instance = json.loads(self.path.read_text())
        m34 = json.loads(Path(m34_registry_path).read_text())
        m34_sessions = {e["session_id"] for e in m34.get("subagents", [])}
        
        for cohort_id, cohort in instance.get("cohorts", {}).items():
            for sub_id in cohort.get("subagent_ids", []):
                if sub_id not in m34_sessions:
                    errors.append(f"Cohort {cohort_id}: subagent {sub_id} not in M34 registry")
        return errors
```

**Pydantic v2 dataclass approach** (alternative, more typesafe):
```python
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from typing import Literal, Optional, List
from datetime import datetime

DispatchedBy = Literal["kali", "grokster", "lilith", "maat", "researcher", 
                       "roc_racoon", "node", "sophia", "verity"]
CohortType = Literal["EIS_BURST", "RESEARCH_PAIR", "IMPLEMENT_TRIO", 
                     "FLEET_DISPATCH", "PIPELINE"]
CohortStatus = Literal["ALIVE", "COMPLETED", "FAILED", "ABANDONED", 
                       "DEAD_LETTER", "INTERRUPTED"]

@dataclass(config=ConfigDict(extra="forbid"))
class Cohort:
    cohort_id: str  # pattern: ^cohort_[a-z0-9]{8,}$
    dispatched_by: DispatchedBy
    subagent_ids: List[str]  # pattern: ^ses_[a-z0-9]+$
    cohort_type: CohortType
    created_at: datetime
    # Optional fields...
    dispatched_by_session_id: Optional[str] = None
    task_brief: Optional[str] = None
    last_updated: Optional[datetime] = None
    status: CohortStatus = "ALIVE"
    resumption_count: int = 0
    m34_registry_ref: Literal["ACTIVE_SUBAGENTS.json"] = "ACTIVE_SUBAGENTS.json"
    tags: List[str] = field(default_factory=list)

# Auto-generated schema
from pydantic import TypeAdapter
schema = TypeAdapter(Cohort).json_schema()
# Also: validate instance
cohort = TypeAdapter(Cohort).validate_python(instance_dict)
```

### Evidence
- Pydantic JSON Schema: https://pydantic.dev/docs/validation/latest/concepts/json_schema/
- Pydantic dataclasses: https://pydantic.dev/docs/validation/latest/api/pydantic/dataclasses/
- M34 ActiveSubagent: `src/omega/oracle/m34_registry.py:120-216`
- COHORT_REGISTRY spec: `data/coordination/RESEARCHER_M33_M36_M37_20260830.md:1637-1788`
- jsonschema library: https://python-jsonschema.readthedocs.io/

### Recommendation
**Two-layer validation**:
1. **JSON Schema validation**: Use the v1.0 schema from `M33-M36-M37` §6.1, validate with `jsonschema` library on every read/write
2. **Pydantic dataclass**: Convert to `@pydantic.dataclasses.dataclass` for type safety in the `CohortRegistry` class methods
3. **Cross-validation**: After JSON schema validation, check `subagent_ids` against `ACTIVE_SUBAGENTS.json`

Store schema in `docs/coordination/cohort_registry_schema.json` (immutable reference). Store instance in `data/coordination/COHORT_REGISTRY.json` (mutable). Use atomic write (M34 pattern) for the instance.

**Estimated time**: 4h (1h code + 1h test + 2h integration with M34)
**Confidence**: HIGH — Schema is fully defined, code pattern is standard

---

## §7 — Council of Four Synthesis

### Architect (Systemic Logic)
The 6 MEDIUM gaps form a clear dependency chain: REUSE → ScanCode → SLSA/in-toto (all part of M37 heritage). COHORT_REGISTRY is independent of the heritage chain but depends on M34. Hybrid search is independent (memory subsystem). The critical path is M37 heritage chain (8h) + COHORT_REGISTRY (4h) = 12h. Hybrid search (6h) is parallel.

### Adversary (Critical Risks)
1. **ScanCode memory**: `--max-in-memory 10000` default can fail on large repos. Use `0` for unlimited or `--max-in-memory 100000`.
2. **REUSE annotation precision**: `reuse annotate` may add headers to test/fixture files that shouldn't have them. Use `--ignore-pattern` to exclude.
3. **SLSA deprecation risk**: `slsa-github-generator` is deprecated; GitHub Artifact Attestations is the path. Don't waste time on the deprecated tool.
4. **in-toto verbosity**: A full layout with 6+ steps creates many `.link` files. For Omega's debut, 2-3 steps (build, sign, inspect) is sufficient.
5. **COHORT_REGISTRY cross-validation cost**: For every cohort load, we must read the entire M34 registry. For 1000+ subagents, this is O(n). Use indexing.

### Alchemist (Creative Synthesis)
The convergence between in-toto's "layout/inspection" model and COHORT_REGISTRY's cohort lifecycle is striking. Both define "expected steps" with "authorized functionaries." A cohort could literally BE an in-toto inspection — verifying that all subagents in a cohort were dispatched by an authorized functionary. The heritage attestation graph IS the cohort graph, viewed from a different angle.

### Archivist (Historical Truth)
These are all mature standards: REUSE since 2018, ScanCode since 2017, SLSA v1.0 since 2021 (v1.1 since 2024), in-toto CNCF graduated 2025, pydantic JSON Schema generation since v1.0. None are experimental. The risk is in the tooling layer (scancode deprecations, slsa-github-generator deprecation), not the standards themselves. For local-first sovereign projects, the `sigstore` Python package is the most stable choice.

---

## §8 — Recommended Next Steps

1. **Day 1**: COHORT_REGISTRY code (4h) — finalize the schema and write the Python class
2. **Day 2**: Hybrid search benchmark (6h) — implement and test Alex Garcia RRF pattern at 10K vectors
3. **Day 3**: REUSE + ScanCode CI (3h) — REUSE.toml + GitHub Action for both
4. **Day 4**: in-toto layout (4h) — define 2-3 step layout, test with in-toto-run
5. **Day 5**: SLSA provenance review (4h) — review M33-M36-M37 spec, add sigstore wrapper

**Total: ~21h parallel/sequential**

**Phase 2 complete. Ready for Phase 3 (LOW gaps) upon confirmation.**

---

*⬡ RESEARCHER ⬡ PHASE-2-COMPLETE ⬡ 2026-08-30 ⬡ mimo-v2.5-free ⬡*
