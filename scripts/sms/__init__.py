#!/usr/bin/env python3
"""SMS — Small-model Specialist gauntlet package (Omega Engine Alpha).

See docs/research/P7_SMS_GAUNTLET_BLUEPRINT_20261008.md for design.
Package layout:
  gauntlet.py      main runner (Ollama /api/chat)
  roles.py         per-role prompts, gold accessors, scorers
  scoring/         json_schema, span_f1, provenance, latency helpers
  schemas/         versioned JSON Schemas (Draft 2020-12) per role
  datasets/       smoke dataset JSONL (synthetic, sanitized)
"""
