"""
Unit tests for OMER M1 Schema Validation (scripts/validate_model_cards.py)
"""

import tempfile
import unittest
from pathlib import Path
import sys

# Add scripts directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_model_cards


class TestOmerValidation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_card(self, filename: str, content: str) -> Path:
        p = self.test_dir / filename
        p.write_text(content, encoding="utf-8")
        return p

    def test_valid_minimal_card(self):
        content = """---
card_version: "1.0"
model_id: "test/model:v1"
provider: "Test Provider"
research_status: "candidate"
deployment: "hosted_trial"
last_verified: "2026-09-11"
confidence: "metadata:high,performance:low"
license: "Apache-2.0"
context_length: 8192
modalities_in: ["text"]
modalities_out: ["text"]
---

# Test Model

## Provider Claims
| Benchmark | Score | Evidence |
|---|---|---|
| MMLU | 75.0 | **Provider claim** |

## Local Measurement
No local measurements.

## Omega Verdict
Candidate for testing.
"""
        card_path = self._write_card("test_model.md", content)
        errors = validate_model_cards.validate_model_card(card_path)
        self.assertEqual(errors, [])

    def test_missing_frontmatter(self):
        content = "# No frontmatter\n\n## Provider Claims\n## Local Measurement\n## Omega Verdict\n"
        card_path = self._write_card("no_fm.md", content)
        errors = validate_model_cards.validate_model_card(card_path)
        self.assertTrue(any("No YAML frontmatter found" in e for e in errors))

    def test_pcore_trap_detection(self):
        content = """---
card_version: "1.0"
model_id: "local/test:v1"
provider: "Local"
research_status: "active"
deployment: "local"
last_verified: "2026-09-11"
confidence: "metadata:high,performance:high"
license: "Apache-2.0"
context_length: 8192
modalities_in: ["text"]
modalities_out: ["text"]
local_hardware_profile:
  cpu: "i7-13620H"
  cpu_cores: 10
  cpu_threads: 16
  allowed_cpus: "0,2,4,6,8,10"
  threads: 8
  ram_gb: 16
  ram_type: "DDR5"
  kv_cache_type: "q8_0"
  flash_attention: true
  max_loaded_models: 1
  quantization: "Q4_K_M"
---

# Local Trap Model

## Provider Claims
## Local Measurement
## Omega Verdict
"""
        card_path = self._write_card("trap_model.md", content)
        errors = validate_model_cards.validate_model_card(card_path)
        self.assertTrue(any("P-core trap" in e for e in errors))

    def test_invalid_evidence_label(self):
        content = """---
card_version: "1.0"
model_id: "test/model:v2"
provider: "Test"
research_status: "candidate"
deployment: "hosted_trial"
last_verified: "2026-09-11"
confidence: "metadata:high,performance:low"
license: "MIT"
context_length: 4096
modalities_in: ["text"]
modalities_out: ["text"]
---

# Invalid Evidence Model

## Provider Claims
| Benchmark | Score | Evidence |
|---|---|---|
| MMLU | 75.0 | **Unverified rumor** |

## Local Measurement
## Omega Verdict
"""
        card_path = self._write_card("invalid_evidence.md", content)
        errors = validate_model_cards.validate_model_card(card_path)
        self.assertTrue(any("Invalid evidence label" in e for e in errors))

    def test_missing_required_section(self):
        content = """---
card_version: "1.0"
model_id: "test/model:v3"
provider: "Test"
research_status: "candidate"
deployment: "hosted_trial"
last_verified: "2026-09-11"
confidence: "metadata:high,performance:low"
license: "MIT"
context_length: 4096
modalities_in: ["text"]
modalities_out: ["text"]
---

# Incomplete Model

## Provider Claims
## Omega Verdict
"""
        card_path = self._write_card("incomplete_sections.md", content)
        errors = validate_model_cards.validate_model_card(card_path)
        self.assertTrue(any("Missing required section '## Local Measurement'" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
