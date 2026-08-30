#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
⬡ AUTONOMOUS MEDITATION PIPELINE — Omega Engine Core
Fully autonomous Problem → Prompt Crafting → Meditation → Synthesis → Research → Grounded Update pipeline.

This is the ENGINE CORE (src/omega/) — zero platform dependencies.
Platform integration goes through the MCP Hub or CLI abstraction layer (M16).
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════════════════
# PLATFORM ABSTRACTION LAYER (M16: Modularization & Portability)
# ═══════════════════════════════════════════════════════════════════════════


class OracleClient(Protocol):
    """Protocol for oracle/LLM calls. Implementations provided by platform."""

    async def talk(self, prompt: str) -> str: ...


class SearchClient(Protocol):
    """Protocol for web search. Implementations provided by platform."""

    async def search(self, query: str, limit: int = 5) -> str: ...
    async def fetch(self, url: str) -> str: ...
    async def searxng(self, query: str, limit: int = 5) -> str: ...


class PlatformClients:
    """Container for platform-specific clients. Injected at runtime."""

    def __init__(
        self,
        oracle: Optional[OracleClient] = None,
        search: Optional[SearchClient] = None,
    ):
        self.oracle = oracle
        self.search = search

    @classmethod
    def from_opencode(cls, mcp_endpoint: str = "http://127.0.0.1:8016/mcp") -> "PlatformClients":
        """Factory for OpenCode environment (uses local MCP Hub via SovereignMCPClient)."""
        try:
            from src.omega.skills.opencode_client import OpenCodePlatformClients

            opencode_clients = OpenCodePlatformClients(mcp_endpoint)

            class OpenCodeOracle:
                def __init__(self, oracle_client):
                    self._oracle = oracle_client

                async def talk(self, prompt: str) -> str:
                    return await self._oracle.talk(prompt)

            class OpenCodeSearch:
                def __init__(self, search_client):
                    self._search = search_client

                async def search(self, query: str, limit: int = 5) -> str:
                    return await self._search.search(query, limit)

                async def fetch(self, url: str) -> str:
                    return await self._search.fetch(url)

                async def searxng(self, query: str, limit: int = 5) -> str:
                    return await self._search.searxng(query, limit)

            return cls(
                oracle=OpenCodeOracle(opencode_clients.get_oracle()),
                search=OpenCodeSearch(opencode_clients.get_search()),
            )
        except ImportError:
            return cls()  # No clients available

    @classmethod
    def from_cli(
        cls, oracle_cmd: str = "opencode", search_cmd: str = "websearch"
    ) -> "PlatformClients":
        """Factory for CLI environment (subprocess calls)."""
        # Implementation would use subprocess to call CLI tools
        return cls()

    @classmethod
    def null(cls) -> "PlatformClients":
        """Null implementation for testing/dry-run."""
        return cls()


# ════════════════════════════════════════════════════════════════════════════
# PIPELINE CORE (Pure Engine Logic — No Platform Dependencies)
# ═══════════════════════════════════════════════════════════════════════════


class AutonomousMeditationPipeline:
    """
    Core pipeline logic. Platform-agnostic.
    Receives clients via dependency injection (M16).
    """

    def __init__(
        self,
        problem_statement: str,
        clients: Optional[PlatformClients] = None,
        resume_from: int = 0,
        dry_run: bool = False,
        output_dir: Optional[Path] = None,
    ):
        self.problem = problem_statement
        self.clients = clients or PlatformClients.null()
        self.resume_from = resume_from
        self.dry_run = dry_run
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_id = f"{self.timestamp}"
        self.output_dir = output_dir or (PROJECT_ROOT / "data" / "autonomous")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stage_outputs: Dict[int, str] = {}

    # ─── Stage I/O ────────────────────────────────────────────────────────

    def _write_stage(self, stage: int, name: str, content: str) -> Path:
        filename = f"{self.run_id}_{stage:02d}_{name}.md"
        filepath = self.output_dir / filename
        filepath.write_text(content)
        self.stage_outputs[stage] = str(filepath)
        print(f"  📝 Stage {stage} ({name}) → {filepath}")
        return filepath

    def _read_stage(self, stage: int) -> Optional[str]:
        if stage in self.stage_outputs:
            return Path(self.stage_outputs[stage]).read_text()
        for f in self.output_dir.glob(f"{self.run_id}_{stage:02d}_*.md"):
            return f.read_text()
        return None

    # ─── Platform Calls (Delegated to Injected Clients) ──────────────────

    async def _call_oracle(self, prompt: str) -> str:
        if self.dry_run or not self.clients.oracle:
            return f"[DRY RUN] Would call oracle with: {prompt[:200]}..."
        return await self.clients.oracle.talk(prompt)

    async def _call_websearch(self, query: str, limit: int = 5) -> str:
        if self.dry_run or not self.clients.search:
            return f"[DRY RUN] Would search: {query}"
        return await self.clients.search.search(query, limit)

    async def _call_webfetch(self, url: str) -> str:
        if self.dry_run or not self.clients.search:
            return f"[DRY RUN] Would fetch: {url}"
        return await self.clients.search.fetch(url)

    async def _call_searxng(self, query: str, limit: int = 5) -> str:
        if self.dry_run or not self.clients.search:
            return f"[DRY RUN] Would SearXNG search: {query}"
        return await self.clients.search.searxng(query, limit)

    # ─── Stage 0: Prompt Crafting ────────────────────────────────────────

    async def stage_0_prompt_crafting(self) -> str:
        print("\n🎯 STAGE 0: Prompt Crafting (Agent → Self)")
        lens_set, mode, rationale = self._analyze_problem_for_meditation()
        prompt = f"""/meditate {self.problem} --lenses {lens_set} --mode {mode}"""
        content = f"""# CRAFTED MEDITATE PROMPT
**Generated by**: autonomous-meditation-pipeline at {datetime.now().isoformat()}
**Run ID**: {self.run_id}
**Problem**: {self.problem}

## Prompt for /meditate:
```
{prompt}
```

## Rationale:
- **Lens set**: {lens_set} — {rationale["lens_set"]}
- **Output mode**: {mode} — {rationale["mode"]}
- **Context injected**: M2, M7, M8, M11, M13, M16, M23 mandates; Heritage refs; Constraints

## Anti-Collapse Contract: ACTIVE
> "Each voice speaks from its domain only. No summarizing others. No agreement without unique constraint. Persona collapse = protocol violation."
"""
        self._write_stage(0, "prompt_crafted", content)
        return prompt

    def _analyze_problem_for_meditation(self) -> tuple:
        problem_lower = self.problem.lower()
        lens_set = "infrastructure,persistence,engineering,integration,governance,cognition,context,observability,orchestration,validation"
        mode = "STRATEGIC"
        rationale = {
            "lens_set": "Full Omega Pantheon (10 lenses) — systemic cross-cutting problem",
            "mode": "STRATEGIC — production architecture with measurable metrics",
        }
        if any(kw in problem_lower for kw in ["bug", "error", "fail", "broken", "crash"]):
            lens_set = "engineering,validation,observability,infrastructure"
            mode = "DIAGNOSTIC"
            rationale = {"lens_set": "Diagnostic triad", "mode": "DIAGNOSTIC — identify root cause"}
        elif any(kw in problem_lower for kw in ["creative", "explore", "future", "what if"]):
            lens_set = "Architect,Skeptic,Pragmatist,Ethicist"
            mode = "CREATIVE"
            rationale = {
                "lens_set": "Creative personas",
                "mode": "CREATIVE — explore possibilities",
            }
        elif any(kw in problem_lower for kw in ["audit", "compliance", "verify"]):
            lens_set = "governance,validation,observability,infrastructure"
            mode = "AUDIT"
            rationale = {"lens_set": "Compliance-focused", "mode": "AUDIT — verify standards"}
        return lens_set, mode, rationale

    # ─── Stage 1: Meditation Execution ──────────────────────────────────

    async def stage_1_meditate_execution(self, prompt: str) -> str:
        print("\n🧘 STAGE 1: Meditation Execution (Agent → Self via /meditate)")
        if self.dry_run:
            content = f"# MEDITATION RAW OUTPUT (DRY RUN)\n**Prompt**: {prompt}"
            self._write_stage(1, "meditation_raw", content)
            return content
        result = await self._call_oracle(prompt)
        content = f"""# MEDITATION RAW OUTPUT
**Executed**: {datetime.now().isoformat()} | **Run**: {self.run_id}
**Prompt**: {prompt}
## Raw Output:
{result}
"""
        self._write_stage(1, "meditation_raw", content)
        return content

    # ─── Stage 2: Synthesis ──────────────────────────────────────────────

    async def stage_2_synthesis(self, meditation_raw: str) -> str:
        print("\n📋 STAGE 2: Intuitive Synthesis (Kali Verdict)")
        synthesis_prompt = f"""Produce INTUITIVE SYNTHESIS from this meditation:
{meditation_raw[:8000]}
Include: 1) Architecture diagram (ASCII), 2) Non-negotiables, 3) MVP scope, 4) Integration points, 5) Success metrics, 6) 3 commands that change everything."""
        result = await self._call_oracle(synthesis_prompt)
        content = f"""# INTUITIVE SYNTHESIS (Kali Verdict)
**Generated**: {datetime.now().isoformat()} | **Run**: {self.run_id}
{result}
"""
        self._write_stage(2, "synthesis", content)
        return content

    # ─── Stage 3: Research Prompt Crafting ──────────────────────────────

    async def stage_3_research_prompt_crafting(self, synthesis: str, meditation_raw: str) -> str:
        print("\n🔍 STAGE 3: Research Prompt Crafting (Agent → Self)")
        queries = [
            "SQLite event sourcing CQRS pattern implementation 2026 best practices",
            "Python keyring library libsecret Keychain Credential Manager cross-platform 2026",
            "Model Context Protocol MCP server credential management 2025-2026",
            "AWS Secrets Manager rotation Lambda pattern vs HashiCorp Vault rotation 2026",
            "fanotify vs inotify recursive directory monitoring Linux 2026",
            "watchdog Python file monitoring cross-platform 2026",
            "credential vault local-first zero-telemetry architecture patterns",
            "distributed transaction credential rotation across heterogeneous consumers",
            "OS keyring hardware-backed encryption TPM Secure Enclave 2026",
        ]
        content = f"""# RESEARCH PROMPT
**Generated**: {datetime.now().isoformat()} | **Run**: {self.run_id}
## Queries:
{chr(10).join(f"{i + 1}. {q}" for i, q in enumerate(queries))}
## Search Strategy: T0(local) → T1(websearch) → T2(webfetch) → T3(SearXNG) → T4(Exa) → T5(Firecrawl)
## Success Criteria: Prior art, benchmarks, security advisories, impl refs, failure modes
"""
        self._write_stage(3, "research_prompt", content)
        return "\n".join(queries)

    # ─── Stage 4: Research Execution ────────────────────────────────────

    async def stage_4_research_execution(self, queries: List[str]) -> str:
        print("\n📚 STAGE 4: Research Execution (Agent → Sovereign Search)")
        if self.dry_run:
            content = "# RESEARCH FINDINGS (DRY RUN)\n[Would execute tiered searches]"
            self._write_stage(4, "research_raw", content)
            return content
        all_findings = []
        for i, query in enumerate(queries):
            print(f"  Query {i + 1}/{len(queries)}: {query[:80]}...")
            findings = await self._execute_tiered_search(query)
            all_findings.append(
                {"query": query, "findings": findings, "timestamp": datetime.now().isoformat()}
            )
        content = f"""# RESEARCH RAW OUTPUT
**Executed**: {datetime.now().isoformat()} | **Run**: {self.run_id}
{json.dumps(all_findings, indent=2)}
"""
        self._write_stage(4, "research_raw", content)
        return content

    async def _execute_tiered_search(self, query: str) -> Dict[str, Any]:
        findings = {
            "query": query,
            "tier_1_websearch": [],
            "tier_2_webfetch": [],
            "tier_3_searxng": [],
        }
        try:
            result = await self._call_websearch(query, limit=5)
            findings["tier_1_websearch"] = json.loads(result) if isinstance(result, str) else result
        except Exception as e:
            findings["tier_1_websearch"] = {"error": str(e)}
        try:
            if isinstance(findings["tier_1_websearch"], dict) and findings["tier_1_websearch"].get(
                "results"
            ):
                top_url = findings["tier_1_websearch"]["results"][0].get("url")
                if top_url:
                    result = await self._call_webfetch(top_url)
                    findings["tier_2_webfetch"] = {"url": top_url, "content": result[:5000]}
        except Exception as e:
            findings["tier_2_webfetch"] = {"error": str(e)}
        try:
            result = await self._call_searxng(query, limit=5)
            findings["tier_3_searxng"] = json.loads(result) if isinstance(result, str) else result
        except Exception as e:
            findings["tier_3_searxng"] = {"error": str(e)}
        return findings

    # ─── Stage 5: Grounded Report ────────────────────────────────────────

    async def stage_5_grounded_report(self, meditation_raw: str, research_raw: str) -> str:
        print("\n📄 STAGE 5: Grounded Report (Agent → Self)")
        content = f"""# GROUNDED MEDITATION REPORT
**Generated**: {datetime.now().isoformat()} | **Run**: {self.run_id}
## Updated Architecture (Research-Backed): [citations]
## Verified Claims: [with citations]
## Corrected Assumptions: [evidence-based]
## New Insights from Prior Art: [research findings]
## Risk Adjustments: [failure modes from research]
"""
        self._write_stage(5, "grounded_report", content)
        return content

    # ─── Stage 6: Gnosis Distillation ────────────────────────────────────

    async def stage_6_gnosis_distillation(self, grounded_report: str) -> str:
        print("\n💎 STAGE 6: Gnosis Distillation (Agent → Verity)")
        content = f"""# GNOSIS DISTILLATION (L1→L2→L3)
**Generated**: {datetime.now().isoformat()} | **Run**: {self.run_id}
## Proposals (→ proposed_lessons.yaml):
```yaml
proposals:
  - id: "gnosis-[topic]-001"
    l1_narrative: "What happened..."
    l2_insight: "What this means..."
    l3_principle: "L3-[Name]: [Universal principle]"
    confidence: 9
    sources: ["meditation", "research:query1"]
    tags: ["tag1", "tag2"]
```
"""
        self._write_stage(6, "gnosis", content)
        return content

    # ─── Stage 7: Integration ────────────────────────────────────────────

    async def stage_7_integration(self, gnosis: str, grounded_report: str) -> str:
        print("\n🔗 STAGE 7: Integration (Agent → Ma'at)")
        content = f"""# INTEGRATION RECORD
**Generated**: {datetime.now().isoformat()} | **Run**: {self.run_id}
## PIVOT_LOG Entry: D-[next] — {self.problem[:80]}
## Workbench Items: [VaultCore, CAP Adapters, Policy Engine, Provider Registry, Watcher+MCP, Context Bundle, Chaos CLI, omega-vault release]
## Temple-Grade Gates: [temple-grade, heritage-map, sovereignty, test]
"""
        self._write_stage(7, "integration", content)
        return content

    # ─── Main Run Loop ──────────────────────────────────────────────────

    async def run(self) -> Dict[int, str]:
        print(
            f"\n{'=' * 60}\n🚀 AUTONOMOUS MEDITATION PIPELINE\nRun ID: {self.run_id}\nProblem: {self.problem}\n{'=' * 60}"
        )

        stages = [
            (0, "Prompt Crafting", lambda: self.stage_0_prompt_crafting()),
            (1, "Meditation", lambda: self.stage_1_meditate_execution(self._read_stage(0) or "")),
            (2, "Synthesis", lambda: self.stage_2_synthesis(self._read_stage(1) or "")),
            (
                3,
                "Research Prompt",
                lambda: self.stage_3_research_prompt_crafting(
                    self._read_stage(2) or "", self._read_stage(1) or ""
                ),
            ),
            (4, "Research", lambda: self.stage_4_research_execution(self._read_stage(3) or [])),
            (
                5,
                "Grounded Report",
                lambda: self.stage_5_grounded_report(
                    self._read_stage(1) or "", self._read_stage(4) or ""
                ),
            ),
            (6, "Gnosis", lambda: self.stage_6_gnosis_distillation(self._read_stage(5) or "")),
            (
                7,
                "Integration",
                lambda: self.stage_7_integration(
                    self._read_stage(6) or "", self._read_stage(5) or ""
                ),
            ),
        ]

        for stage_num, name, func in stages:
            if stage_num < self.resume_from:
                print(f"\n⏭️  Skipping Stage {stage_num} ({name})")
                continue
            print(f"\n{'─' * 60}")
            try:
                await func()
                print(f"  ✅ Stage {stage_num} complete")
            except Exception as e:
                print(f"  ❌ Stage {stage_num} failed: {e}")
                if not self.dry_run:
                    raise

        print(
            f"\n{'=' * 60}\n✅ PIPELINE COMPLETE: {self.run_id}\nOutputs: {self.output_dir}\n{'=' * 60}"
        )
        return self.stage_outputs


# ════════════════════════════════════════════════════════════════════════════
# ENTRY POINTS (Platform-Specific Factories)
# ════════════════════════════════════════════════════════════════════════════


def create_pipeline_opencode(problem: str, **kwargs) -> AutonomousMeditationPipeline:
    """Factory for OpenCode environment."""
    return AutonomousMeditationPipeline(
        problem_statement=problem, clients=PlatformClients.from_opencode(), **kwargs
    )


def create_pipeline_cli(problem: str, **kwargs) -> AutonomousMeditationPipeline:
    """Factory for CLI environment."""
    return AutonomousMeditationPipeline(
        problem_statement=problem, clients=PlatformClients.from_cli(), **kwargs
    )


def create_pipeline_standalone(problem: str, **kwargs) -> AutonomousMeditationPipeline:
    """Factory for standalone/testing (no platform clients)."""
    # dry_run defaults to True for standalone; allow override via kwargs
    kwargs.setdefault("dry_run", True)
    return AutonomousMeditationPipeline(
        problem_statement=problem, clients=PlatformClients.null(), **kwargs
    )


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Autonomous Meditation Pipeline")
    parser.add_argument("problem", help="Problem statement")
    parser.add_argument(
        "--platform", choices=["opencode", "cli", "standalone"], default="standalone"
    )
    parser.add_argument("--resume-from", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    factories = {
        "opencode": create_pipeline_opencode,
        "cli": create_pipeline_cli,
        "standalone": create_pipeline_standalone,
    }

    pipeline = factories[args.platform](
        args.problem,
        resume_from=args.resume_from,
        dry_run=args.dry_run,
        output_dir=args.output_dir,
    )
    await pipeline.run()


if __name__ == "__main__":
    import anyio

    anyio.run(main)
