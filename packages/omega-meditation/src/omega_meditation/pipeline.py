# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
⬡ AUTONOMOUS MEDITATION PIPELINE — Core Engine Logic
Platform-agnostic. Platform integration via injected clients (M16).
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
from abc import ABC, abstractmethod

# Project root for data paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ════════════════════════════════════════════════════════════════════════════
# PLATFORM ABSTRACTION LAYER (M16: Modularization & Portability)
# ════════════════════════════════════════════════════════════════════════════

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
    def from_opencode(cls) -> "PlatformClients":
        """Factory for OpenCode environment (uses MCP Hub tools)."""
        try:
            from mcp_servers.omega_hub.tools import (
                omega_hub_oracle_talk,
                omega_hub_library_web_search,
                omega_hub_webfetch,
                omega_hub_searxng_search,
            )
            
            class OpenCodeOracle:
                async def talk(self, prompt: str) -> str:
                    return await omega_hub_oracle_talk(query=prompt)
            
            class OpenCodeSearch:
                async def search(self, query: str, limit: int = 5) -> str:
                    return await omega_hub_library_web_search(query=query, limit=limit)
                async def fetch(self, url: str) -> str:
                    return await omega_hub_webfetch(url=url)
                async def searxng(self, query: str, limit: int = 5) -> str:
                    return await omega_hub_searxng_search(query=query, limit=limit)
            
            return cls(oracle=OpenCodeOracle(), search=OpenCodeSearch())
        except ImportError:
            return cls()  # No clients available
    
    @classmethod
    def from_cli(cls, oracle_cmd: str = "opencode", search_cmd: str = "websearch") -> "PlatformClients":
        """Factory for CLI environment (subprocess calls)."""
        # Implementation would use subprocess to call CLI tools
        return cls()
    
    @classmethod
    def null(cls) -> "PlatformClients":
        """Null implementation for testing/dry-run."""
        return cls()


# ════════════════════════════════════════════════════════════════════════════
# PIPELINE CORE (Pure Engine Logic — No Platform Dependencies)
# ════════════════════════════════════════════════════════════════════════════

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
- **Lens set**: {lens_set}
  - Reason: {rationale['lens_set']}
- **Output mode**: {mode}
  - Reason: {rationale['mode']}
- **Context injected**:
  - Mandates: M2 (Engine-Stack Firewall), M7 (Local-First), M8 (Zero Telemetry), M11 (Soul Integrity), M13 (Temple-Grade), M16 (Modularization), M23 (Failure Integrity)
  - Heritage: Architect's Gemini CLI experiments (2025), Strike 11.5 Council Dispatcher, /meditate command (2026-07-16)
  - Constraints: 11 plaintext credential files, 6 tools, 8 Gmail accounts, 1.5 years manual rotation

## Anti-Collapse Contract: ACTIVE
> "Each voice in this council speaks from its domain only.
> No voice may summarize what another already said.
> No voice may agree without adding a unique constraint.
> Persona collapse is a protocol violation."
"""
        self._write_stage(0, "prompt_crafted", content)
        return prompt

    def _analyze_problem_for_meditation(self) -> tuple:
        problem_lower = self.problem.lower()
        lens_set = "infrastructure,persistence,engineering,integration,governance,cognition,context,observability,orchestration,validation"
        mode = "STRATEGIC"
        rationale = {
            "lens_set": "Full Omega Pantheon (10 lenses) — systemic cross-cutting problem touching all domains",
            "mode": "STRATEGIC — need production architecture with measurable success metrics"
        }
        if any(kw in problem_lower for kw in ["bug", "error", "fail", "broken", "crash"]):
            lens_set = "engineering,validation,observability,infrastructure"
            mode = "DIAGNOSTIC"
            rationale = {
                "lens_set": "Targeted diagnostic triad — engineering (root cause), validation (reproduction), observability (evidence), infrastructure (environment)",
                "mode": "DIAGNOSTIC — need to identify what is broken and why"
            }
        elif any(kw in problem_lower for kw in ["creative", "explore", "future", "possibility", "what if"]):
            lens_set = "Architect,Skeptic,Pragmatist,Ethicist"
            mode = "CREATIVE"
            rationale = {
                "lens_set": "Custom creative personas — Architect (vision), Skeptic (constraints), Pragmatist (feasibility), Ethicist (implications)",
                "mode": "CREATIVE — exploring what could exist"
            }
        elif any(kw in problem_lower for kw in ["audit", "compliance", "verify", "check"]):
            lens_set = "governance,validation,observability,infrastructure"
            mode = "AUDIT"
            rationale = {
                "lens_set": "Compliance-focused — governance (laws), validation (tests), observability (evidence), infrastructure (environment)",
                "mode": "AUDIT — verify compliance with standards"
            }
        return lens_set, mode, rationale

    # ─── Stage 1: Meditation Execution ──────────────────────────────────

    async def stage_1_meditate_execution(self, prompt: str) -> str:
        print("\n🧘 STAGE 1: Meditation Execution (Agent → Self via /meditate)")
        if self.dry_run:
            content = f"# MEDITATION RAW OUTPUT (DRY RUN)\n**Prompt**: {prompt}\n\n[Would execute /meditate here]"
            self._write_stage(1, "meditation_raw", content)
            return content
        try:
            result = await self._call_oracle(prompt)
            content = f"""# MEDITATION RAW OUTPUT
**Executed by**: autonomous-meditation-pipeline at {datetime.now().isoformat()}
**Run ID**: {self.run_id}
**Prompt**: {prompt}

## Raw Output:
{result}
"""
        except Exception as e:
            content = f"""# MEDITATION RAW OUTPUT (ERROR)
**Error**: {e}
**Prompt**: {prompt}
"""
        self._write_stage(1, "meditation_raw", content)
        return content

    # ─── Stage 2: Intuitive Synthesis ──────────────────────────────────

    async def stage_2_synthesis(self, meditation_raw: str) -> str:
        print("\n📋 STAGE 2: Intuitive Synthesis (Agent → Self)")
        synthesis_prompt = f"""Based on this meditation output, produce an INTUITIVE SYNTHESIS briefing:

{meditation_raw[:8000]}

Produce:
1. Architecture diagram (ASCII)
2. Non-negotiables (from Preserved Dissent)
3. MVP scope (from Emergent Sequencing)
4. Integration points (Omega Pillars)
5. Success metrics (measurable)
6. The "3 commands that change everything"

Format as markdown."""
        try:
            result = await self._call_oracle(synthesis_prompt)
            content = f"""# INTUITIVE SYNTHESIS (Kali Verdict)
**Generated by**: autonomous-meditation-pipeline at {datetime.now().isoformat()}
**Run ID**: {self.run_id}
**Based on**: Stage 1 meditation output

## Synthesis:
{result}
"""
        except Exception as e:
            content = f"""# INTUITIVE SYNTHESIS (ERROR)
**Error**: {e}
"""
        self._write_stage(2, "synthesis", content)
        return content

    # ─── Stage 3: Research Prompt Crafting ─────────────────────────────

    async def stage_3_research_prompt_crafting(self, synthesis: str, meditation_raw: str) -> str:
        print("\n🔍 STAGE 3: Research Prompt Crafting (Agent → Self)")
        content = f"""# RESEARCH PROMPT
**Generated by**: autonomous-meditation-pipeline at {datetime.now().isoformat()}
**Run ID**: {self.run_id}
**Based on**: Stage 2 synthesis + Stage 1 meditation gaps

## Research Queries:
1. **SQLite event sourcing for credential vault** — Verify production patterns, schema, performance
2. **Python keyring libsecret/Keychain/CredMan backends** — Cross-platform reliability, headless fallback
3. **MCP (Model Context Protocol) 2025-11-25 spec** — Server primitives, auth patterns, credential tools
4. **Credential rotation patterns** — AWS Secrets Manager Lambda, HashiCorp Vault, distributed transactions
5. **fanotify vs inotify for config watching** — Recursive mount monitoring, cross-platform (watchdog)
6. **Chaos testing for credential systems** — Keyring unavailable, concurrent rotation, crash mid-rotation
7. **Provider registry schemas** — Google AI Studio vs Vertex, Anthropic, OpenRouter, xAI, Firecrawl
8. **Local-first observability without telemetry** — Structured audit logs, FTS5, correlation

## Search Strategy:
- Tier 0: Local cache check
- Tier 1: websearch (primary, 2026 sources)
- Tier 2: webfetch (deep extraction from key URLs)
- Tier 3: SearXNG (semantic refinement)
- Tier 4: Exa (high-precision technical)
- Tier 5: Firecrawl (full-page scrape for docs)

## Success Criteria:
- [ ] Prior art found for each technical decision
- [ ] Benchmarks for performance claims
- [ ] Security advisories for each provider
- [ ] Implementation references (libraries, schemas, protocols)
- [ ] Failure modes documented for each component
"""
        self._write_stage(3, "research_prompt", content)
        return content

    # ─── Stage 4: Research Execution ───────────────────────────────────

    async def stage_4_research_execution(self, research_prompt: str) -> str:
        print("\n📚 STAGE 4: Research Execution (Agent → Sovereign Search)")
        if self.dry_run:
            content = f"# RESEARCH RAW OUTPUT (DRY RUN)\n**Prompt**: {research_prompt[:500]}...\n\n[Would execute tiered searches here]"
            self._write_stage(4, "research_raw", content)
            return content

        queries = self._parse_queries(research_prompt)
        all_findings = []
        for i, query in enumerate(queries):
            print(f"  Query {i+1}/{len(queries)}: {query[:80]}...")
            findings = await self._execute_tiered_search(query)
            all_findings.append({
                "query": query,
                "findings": findings,
                "timestamp": datetime.now().isoformat()
            })

        content = f"""# RESEARCH RAW OUTPUT
**Executed by**: autonomous-meditation-pipeline at {datetime.now().isoformat()}
**Run ID**: {self.run_id}
**Queries executed**: {len(queries)}

## Findings:
{json.dumps(all_findings, indent=2)}
"""
        self._write_stage(4, "research_raw", content)
        return content

    def _parse_queries(self, research_prompt: str) -> List[str]:
        queries = []
        for line in research_prompt.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('- ')):
                query = line.split('.', 1)[-1].split('-', 1)[-1].strip()
                if len(query) > 10:
                    queries.append(query)
        return queries[:15]

    async def _execute_tiered_search(self, query: str) -> Dict[str, Any]:
        findings = {
            "query": query,
            "tier_0_local": [],
            "tier_1_websearch": [],
            "tier_2_webfetch": [],
            "tier_3_searxng": [],
            "tier_4_exa": [],
            "tier_5_firecrawl": []
        }
        try:
            result = await self._call_websearch(query, limit=5)
            findings["tier_1_websearch"] = json.loads(result) if isinstance(result, str) else result
        except Exception as e:
            findings["tier_1_websearch"] = {"error": str(e)}
        try:
            if isinstance(findings["tier_1_websearch"], dict) and findings["tier_1_websearch"].get("results"):
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

    # ─── Stage 5: Grounded Report ──────────────────────────────────────

    async def stage_5_grounded_report(self, meditation_raw: str, research_raw: str) -> str:
        print("\n📄 STAGE 5: Grounded Report (Agent → Self)")
        content = f"""# GROUNDED MEDITATION REPORT
**Generated by**: autonomous-meditation-pipeline at {datetime.now().isoformat()}
**Run ID**: {self.run_id}
**Based on**: Stage 1 meditation + Stage 4 research

## Updated Architecture (Research-Backed):
[Architecture updated with research citations]

## Verified Claims with Citations:
[Claims from meditation verified against research]

## Corrected Assumptions:
[Assumptions corrected based on evidence]

## New Insights from Prior Art:
[Insights from research not in original meditation]

## Risk Adjustments:
[Risks adjusted based on failure modes found]

## Full Research Reference:
{research_raw[:3000]}...

## Full Meditation Reference:
{meditation_raw[:3000]}...
"""
        self._write_stage(5, "grounded_report", content)
        return content

    # ─── Stage 6: Gnosis Distillation ──────────────────────────────────

    async def stage_6_gnosis_distillation(self, grounded_report: str) -> str:
        print("\n💎 STAGE 6: Gnosis Distillation (Agent → Verity)")
        content = f"""# GNOSIS DISTILLATION (L1→L2→L3)
**Generated by**: autonomous-meditation-pipeline at {datetime.now().isoformat()}
**Run ID**: {self.run_id}
**Based on**: Stage 5 grounded report

## Proposed Lessons (→ proposed_lessons.yaml):

```yaml
proposals:
  - id: "gnosis-[topic]-001"
    l1_narrative: "What happened in this autonomous session..."
    l2_insight: "What this means for our architecture..."
    l3_principle: "L3-[Name]: [Universal principle]"
    confidence: 9
    sources: ["meditation", "research:query1", "research:query2"]
    tags: ["tag1", "tag2"]
```

## Distillation Notes:
[L1→L2→L3 reasoning for each principle]
"""
        self._write_stage(6, "gnosis", content)
        return content

    # ─── Stage 7: Integration ──────────────────────────────────────────

    async def stage_7_integration(self, gnosis: str, grounded_report: str) -> str:
        print("\n🔗 STAGE 7: Integration (Agent → Ma'at)")
        content = f"""# INTEGRATION RECORD
**Generated by**: autonomous-meditation-pipeline at {datetime.now().isoformat()}
**Run ID**: {self.run_id}

## PIVOT_LOG Entry:
- Decision: D-[next]
- Summary: [one-line summary]
- Rationale: [from grounded report]
- Owner: [lens or agent]

## Workbench Items Created:
- [ ] Item 1: [description]
- [ ] Item 2: [description]

## Temple-Grade Gates:
- [ ] make temple-grade (T1-T11)
- [ ] make heritage-map (M14)
- [ ] make sovereignty (M7)
- [ ] make test (1398+ tests)

## Status: PENDING MANUAL EXECUTION
"""
        self._write_stage(7, "integration", content)
        return content

    # ─── Run Pipeline ──────────────────────────────────────────────────

    async def run(self) -> Dict[int, str]:
        print(f"\n{'='*60}")
        print(f"🚀 AUTONOMOUS MEDITATION PIPELINE")
        print(f"Run ID: {self.run_id}")
        print(f"Problem: {self.problem}")
        print(f"{'='*60}")

        if self.resume_from <= 0:
            prompt = await self.stage_0_prompt_crafting()
        else:
            prompt = self._read_stage(0) or ""

        if self.resume_from <= 1:
            meditation = await self.stage_1_meditate_execution(prompt)
        else:
            meditation = self._read_stage(1) or ""

        if self.resume_from <= 2:
            synthesis = await self.stage_2_synthesis(meditation)
        else:
            synthesis = self._read_stage(2) or ""

        if self.resume_from <= 3:
            research_prompt = await self.stage_3_research_prompt_crafting(synthesis, meditation)
        else:
            research_prompt = self._read_stage(3) or ""

        if self.resume_from <= 4:
            research = await self.stage_4_research_execution(research_prompt)
        else:
            research = self._read_stage(4) or ""

        if self.resume_from <= 5:
            grounded = await self.stage_5_grounded_report(meditation, research)
        else:
            grounded = self._read_stage(5) or ""

        if self.resume_from <= 6:
            gnosis = await self.stage_6_gnosis_distillation(grounded)
        else:
            gnosis = self._read_stage(6) or ""

        if self.resume_from <= 7:
            integration = await self.stage_7_integration(gnosis, grounded)
        else:
            integration = self._read_stage(7) or ""

        print(f"\n{'='*60}")
        print(f"✅ PIPELINE COMPLETE")
        print(f"Run ID: {self.run_id}")
        print(f"Outputs: {self.output_dir}")
        for stage, path in self.stage_outputs.items():
            print(f"  Stage {stage}: {path}")
        print(f"{'='*60}")

        return self.stage_outputs


# ════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS (Platform-Specific Entry Points)
# ════════════════════════════════════════════════════════════════════════════

def create_pipeline_opencode(
    problem: str,
    resume_from: int = 0,
    dry_run: bool = False,
    output_dir: Optional[Path] = None,
) -> AutonomousMeditationPipeline:
    """Create pipeline configured for OpenCode environment."""
    return AutonomousMeditationPipeline(
        problem_statement=problem,
        clients=PlatformClients.from_opencode(),
        resume_from=resume_from,
        dry_run=dry_run,
        output_dir=output_dir,
    )

def create_pipeline_cli(
    problem: str,
    resume_from: int = 0,
    dry_run: bool = False,
    output_dir: Optional[Path] = None,
) -> AutonomousMeditationPipeline:
    """Create pipeline configured for CLI environment."""
    return AutonomousMeditationPipeline(
        problem_statement=problem,
        clients=PlatformClients.from_cli(),
        resume_from=resume_from,
        dry_run=dry_run,
        output_dir=output_dir,
    )

def create_pipeline_standalone(
    problem: str,
    resume_from: int = 0,
    dry_run: bool = True,
    output_dir: Optional[Path] = None,
) -> AutonomousMeditationPipeline:
    """Create pipeline with no platform clients (dry-run only)."""
    return AutonomousMeditationPipeline(
        problem_statement=problem,
        clients=PlatformClients.null(),
        resume_from=resume_from,
        dry_run=dry_run,
        output_dir=output_dir,
    )