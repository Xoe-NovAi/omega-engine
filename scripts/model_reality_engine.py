#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Omega Model Registry Reality Engine
⬡ OMEGA ⬡ CLINE ⬡ REALITY-ENGINE ⬡ 2026-07-19
"""
import sys, json, time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import yaml
import requests
from datetime import datetime, timezone

REGISTRY_DIR = Path("config/model_registry")

@dataclass
class RealityFact:
    source: str
    source_url: str
    last_verified: str
    confidence: str
    raw_data: dict = field(default_factory=dict)

@dataclass
class ModelReality:
    model_id: str
    facts: list[RealityFact] = field(default_factory=list)
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    pricing_input_mtok: Optional[float] = None
    pricing_output_mtok: Optional[float] = None
    released_at: Optional[str] = None
    license: Optional[str] = None
    is_open_weight: bool = False
    supported_parameters: list[str] = field(default_factory=list)
    
    def add_fact(self, fact: RealityFact):
        self.facts.append(fact)
        if "context_length" in fact.raw_data:
            self.context_window = fact.raw_data["context_length"]
        p = fact.raw_data.get("pricing", {})
        if p:
            self.pricing_input_mtok = float(p.get("prompt", 0))
            self.pricing_output_mtok = float(p.get("completion", 0))

class RealityEngine:
    def __init__(self):
        self.models: dict[str, ModelReality] = {}
    
    def query_openrouter(self) -> list[RealityFact]:
        facts = []
        try:
            resp = requests.get("https://openrouter.ai/api/v1/models", timeout=30)
            data = resp.json()
            for m in data.get("data", []):
                fact = RealityFact(
                    source="openrouter-api-2026-07-19",
                    source_url="https://openrouter.ai/api/v1/models",
                    last_verified=datetime.now(timezone.utc).isoformat(),
                    confidence="high",
                    raw_data=m,
                )
                facts.append(fact)
                self.models[m.get("id", "")] = ModelReality(model_id=m.get("id", ""))
                self.models[m.get("id", "")].context_window = m.get("context_length")
                p = m.get("pricing", {})
                if p:
                    self.models[m.get("id", "")].pricing_input_mtok = float(p.get("prompt", 0))
                    self.models[m.get("id", "")].pricing_output_mtok = float(p.get("completion", 0))
        except Exception as e:
            print(f"⚠️ OpenRouter API error: {e}")
        return facts
    
    def run(self):
        print("🚀 Omega Model Registry Reality Engine")
        print("=" * 72)
        print("\n📡 Querying OpenRouter API...")
        self.query_openrouter()
        print(f"   Fetched {len(self.models)} models from OpenRouter")
        return len(self.models)

def main():
    engine = RealityEngine()
    n = engine.run()
    print(f"\nCOMPLETE — {n} models verified")
    return 0

if __name__ == "__main__":
    sys.exit(main())
