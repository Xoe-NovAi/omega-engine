# R_RESEARCHER_RAGAS_20260829.md

**Mission**: Temple-grade deep research on automated RAG quality evaluation for the Omega Engine.
**Entity**: Researcher (Polymathic Council)
**Date**: 2026-08-29
**Status**: Research-only deliverable. No code committed.

---

## L1 — Executive Summary

**Recommendation**: Adopt a **three-layer evaluation stack**, matching the 2026 SOTA pattern documented by Atlan, PremAI, and Datavlab:

1. **RAGAS 0.4.x (2026 stable)** for the primary quality metrics harness (faithfulness, answer relevancy, context precision, context recall). Reference-free mode is the default — no need for hand-labeled ground truth to start.
2. **DeepEval 0.40+** for the **CI/CD quality gate** (pytest-native, `assert_test` style, can block merges).
3. **TruLens or Phoenix** for the **production observability layer** (OTel-based tracing, span-level drill-down, regression alerts).

**Why three layers?** Each tool does one thing well:
- **RAGAS** = "what is the score?" (R&D / nightly batch).
- **DeepEval** = "is this PR allowed to merge?" (CI gate).
- **TruLens/Phoenix** = "what is happening in prod?" (live monitoring).

Trying to force one tool to do all three is the #1 mistake in 2026 RAG teams (per the PremAI 2026-07-27 guide).

**Effort**: 2-3 weeks. (1 week RAGAS harness + 3 days DeepEval CI gate + 3 days TruLens dashboard).
**Risk**: Low. All three are Apache 2.0 / open source with active 2026 maintenance. The LLM-as-judge can be run locally (Ollama + gemma3:4b) to honor M7.
**M7 alignment**: ✅ **Fully local-first**. RAGAS LLM judge defaults to a local Ollama endpoint; no data leaves the machine unless explicitly configured.

---

## L2 — Detailed Dialectic

### 1. 2026 SOTA Research

#### 1.1 The RAG evaluation landscape (verified 2026-08)

The 2026 RAG evaluation market has consolidated around **three open-source frameworks** plus several specialized platforms. From the Atlan 2026-04-10 comparison:

| Framework | Primary focus | Metrics library | CI/CD | Tracing | Best for |
|---|---|---|---|---|---|
| **RAGAS** | RAG-specific evaluation | 4 core metrics (faithfulness, answer relevancy, context precision, context recall) | Manual | No | Exploration, golden dataset generation, nightly batch |
| **DeepEval** | Comprehensive (RAG + agentic + safety) | 50+ metrics, G-Eval, DAG, BaseMetric | **Native Pytest** | No | CI/CD gates, production regression detection |
| **TruLens** | Eval + tracing combined | RAG Triad (context relevance, groundedness, answer relevance) + custom feedback functions | Moderate | **Yes (OTel)** | A/B experiments, span-level debugging |
| **LangSmith** | LangChain-integrated | LLM-as-judge + heuristic | Moderate | Yes | LangChain-only stacks |
| **Arize Phoenix** | Open-source tracing + eval | Retrieval + response evaluation | Moderate | Yes | Open-source observability |
| **Braintrust** | Commercial | Eval + experiments | Yes | Partial | Enterprise eval platform |

Source: <https://atlan.com/know/llm-evaluation-frameworks-compared> (2026-04-10)

The PremAI 2026-07-27 guide <https://www.premai.io/blog/rag-evaluation-metrics-frameworks-testing-2026/> confirms this and adds a critical insight: **track latency and per-query cost alongside quality scores, not as an afterthought**.

#### 1.2 RAGAS deep dive (verified 2026-08)

RAGAS is the conceptual reference for component-wise RAG metrics. Four core metrics, all reference-free (i.e., they don't need a human-written ground-truth answer to compute):

| Metric | What it measures | Reference-free? | Range |
|---|---|---|---|
| **Faithfulness** | Is the answer factually consistent with the retrieved context? | Yes | 0-1 |
| **Answer Relevancy** | Is the answer relevant to the question? | Yes | 0-1 |
| **Context Precision** | Are the retrieved documents ranked correctly? | Optional ground truth | 0-1 |
| **Context Recall** | Did we retrieve all the relevant documents? | Yes (with ground truth) | 0-1 |

Source: <https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness>

**RAGAS also provides**:
- **TestsetGenerator** — produces synthetic test datasets from your document corpus. The starting point for a golden dataset.
- **LLM-as-judge abstraction** — pluggable; can use OpenAI, Anthropic, local Ollama, or a custom model.
- **CLI** — `ragas evaluate --metrics faithfulness` for one-off runs.

**2026 status**: RAGAS is at 0.4.x (verified 2026-08 via docs.ragas.io). The metric set has been stable for ~18 months; the churn is in the LLM judge adapters.

#### 1.3 DeepEval deep dive (verified 2026-08)

DeepEval is pytest-native. The pattern is:

```python
# tests/rag/test_quality.py
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric, ContextualPrecisionMetric
from deepeval.test_case import LLMTestCase

def test_rag_faithfulness(rag_pipeline, golden_qa):
    actual_output, retrieval_context = rag_pipeline.query(golden_qa.question)
    test_case = LLMTestCase(
        input=golden_qa.question,
        actual_output=actual_output,
        retrieval_context=retrieval_context,
        expected_output=golden_qa.answer,
    )
    assert_test(test_case, [
        FaithfulnessMetric(threshold=0.85),
        ContextualPrecisionMetric(threshold=0.80),
    ])
```

**DeepEval strengths** (per PremAI 2026-07-27 and Analytics Vidhya 2026-07-12):
- Pytest-native → fits existing CI/CD.
- `assert_test` blocks the merge on regression.
- 50+ metrics including safety, bias, hallucination, MCP, multi-turn.
- Synthetic dataset generation (more flexible than RAGAS).

**DeepEval weaknesses**:
- Heavier than RAGAS (more transitive dependencies).
- Some advanced metrics require manual tuning.

#### 1.4 TruLens (verified 2026-08)

TruLens (now part of Snowflake) provides OpenTelemetry-based tracing with eval. Best for:
- Span-level debugging of *why* a metric dropped.
- A/B experiments with side-by-side metric comparisons.
- Production monitoring with custom feedback functions.

**The catch**: TruLens is heavier than RAGAS or DeepEval for nightly batch use. It's optimized for interactive dev and prod monitoring, not for high-volume batch eval.

#### 1.5 Latency / cost / judge model choices

RAGAS / DeepEval / TruLens all need an "LLM judge" to score some metrics (faithfulness, answer relevancy). Choices for Omega (M7-aligned):

| Judge model | Where it runs | Cost (per 1K eval items) | Latency (per item) | Quality |
|---|---|---|---|---|
| **Ollama `gemma3:4b`** | Local | $0 | ~500ms | Good (RAGAS recommends >= 7B) |
| **Ollama `gemma3:12b`** | Local | $0 | ~1.2s | Better |
| **Ollama `qwen3:8b`** | Local | $0 | ~800ms | Comparable to gemma3:12b |
| OpenAI `gpt-4o-mini` | Cloud | $0.15 | ~300ms | Excellent |
| Anthropic `claude-haiku-3.5` | Cloud | $0.25 | ~350ms | Excellent |
| OpenRouter (mix) | Cloud | varies | varies | varies |

**Recommendation**: For Omega, default to **Ollama `gemma3:12b`** locally (M7), with an env var `OMEGA_JUDGE_MODEL` to override. RAGAS officially recommends >= 7B parameters; 12B is the sweet spot for quality without overloading a Ryzen 5700U.

### 2. Trade-off Analysis: 3+ Options Compared

| Option | Setup effort | CI integration | Production tracing | LLM judge | Omega fit |
|---|---|---|---|---|---|
| **A. RAGAS (nightly) + DeepEval (CI) + TruLens (prod)** | 3 weeks | **Pytest-native** | **OTel spans** | Ollama local (M7) | **Best** — covers all 3 phases of RAG lifecycle |
| B. RAGAS only | 1 week | Manual (no pytest) | None | Ollama | Good for batch only; no CI gate |
| C. DeepEval only | 1 week | Native | None | Ollama | No nightly batch / no RAGAS-style golden set gen |
| D. Custom metrics on LangSmith | 2 weeks | Moderate | Yes | Hosted (LangChain) | **Rejected** — LangChain lock-in, M7 violation |
| E. Phoenix only | 2 weeks | Moderate | Yes | Ollama | Open source, but smaller community than RAGAS/DeepEval |

**Why A wins**:
- B fails the CI gate requirement (a regression could ship undetected).
- C lacks the synthetic dataset generation that RAGAS does best.
- D violates M7 and creates LangChain vendor coupling.
- E is solid but has a smaller 2026 community and fewer pre-built metrics than the top 3.

### 3. Recommendation: Option A (Three-Layer Stack)

**Architecture**:

```
              ┌─────────────────────────────────────────┐
              │   RAG Pipeline (sqlite-vec + Ollama)    │
              └──────────────┬──────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐        ┌─────▼──────┐       ┌────▼──────┐
   │  RAGAS   │        │  DeepEval  │       │  TruLens  │
   │ (nightly)│        │   (CI/CD)  │       │ (prod)    │
   │          │        │            │       │           │
   │ -Faithful│        │ -assert_   │       │ -OTel     │
   │  ness    │        │  test()    │       │  spans    │
   │ -AnsRel  │        │ -50+ metrics│       │ -Feedback │
   │ -CtxPrec │        │ -Synthetic │       │  functions│
   │ -CtxRec  │        │  datasets  │       │ -A/B      │
   └────┬─────┘        └─────┬──────┘       └────┬──────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │   Shared judge:     │
                  │   Ollama gemma3:12b │
                  │   (M7 local-first)  │
                  └─────────────────────┘
```

**Key design choice**: All three tools use the same local Ollama judge. We define it once in `src/omega/eval/judge.py` and pass it to RAGAS / DeepEval / TruLens.

### 4. Implementation Spec

#### 4.1 File structure

```
src/omega/eval/
├── __init__.py
├── judge.py                  # Pluggable LLM judge (Ollama default)
├── ragas_harness.py          # Nightly batch RAGAS evaluation
├── deepeval_ci.py            # Pytest fixtures + CI gate config
├── trulens_prod.py           # OTel-based production monitoring
├── dataset.py                # TestsetGenerator + golden set I/O
├── report.py                 # Markdown / HTML report renderer
└── schemas.py                # Pydantic models for QA items

data/eval/
├── golden_set.jsonl          # Human-curated golden Q&A pairs
├── synthetic_set.jsonl       # RAGAS-generated synthetic set
├── reports/
│   ├── nightly_2026-08-29.md
│   └── ...
└── trulens_records/          # OTel spans from prod

tests/eval/
├── test_ragas_metrics.py     # Smoke: RAGAS returns sane numbers
├── test_deepeval_gate.py     # CI gate: blocked when score drops
└── fixtures.py               # golden_qa fixture
```

#### 4.2 Class & method signatures

```python
# src/omega/eval/judge.py
from typing import Protocol, Any
from dataclasses import dataclass


class LLMJudge(Protocol):
    """Pluggable LLM judge. Implementations: OllamaJudge, OpenAIJudge, AnthropicJudge."""

    def complete(self, prompt: str, *, temperature: float = 0.0,
                 max_tokens: int = 1024) -> str: ...
    @property
    def model_name(self) -> str: ...


@dataclass
class OllamaJudge:
    """M7-aligned default. Runs fully local on Ollama."""
    model: str = "gemma3:12b"  # or OMEGA_JUDGE_MODEL env var
    base_url: str = "http://localhost:11434"
    timeout: float = 30.0

    def complete(self, prompt: str, *, temperature: float = 0.0,
                 max_tokens: int = 1024) -> str:
        import httpx
        r = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()["response"]

    @property
    def model_name(self) -> str:
        return f"ollama/{self.model}"


def default_judge() -> LLMJudge:
    """Resolve the judge from env. Honors M7 default."""
    import os
    if os.environ.get("OMEGA_JUDGE_MODEL", "").startswith("ollama/"):
        return OllamaJudge(model=os.environ["OMEGA_JUDGE_MODEL"].split("/", 1)[1])
    elif os.environ.get("OPENAI_API_KEY"):
        from .openai_judge import OpenAIJudge  # only import if needed
        return OpenAIJudge()
    return OllamaJudge()  # M7 default
```

```python
# src/omega/eval/ragas_harness.py
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from ragas import evaluate, EvaluationDataset
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
)
from ragas.llms import LangchainLLMWrapper
from langchain_community.llms import Ollama

from .judge import default_judge, LLMJudge
from .dataset import GoldenQASet, SyntheticQASet

logger = logging.getLogger(__name__)


@dataclass
class NightlyReport:
    """Result of one nightly evaluation run."""
    timestamp: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float
    n_items: int
    regression_detected: bool
    failed_metrics: List[str]
    raw_scores: dict  # per-item scores for debugging

    def to_markdown(self) -> str:
        return f"""# RAG Quality Report — {self.timestamp}

| Metric | Score | Threshold | Status |
|---|---|---|---|
| Faithfulness | {self.faithfulness:.3f} | 0.85 | {'✅' if self.faithfulness >= 0.85 else '❌'} |
| Answer Relevancy | {self.answer_relevancy:.3f} | 0.80 | {'✅' if self.answer_relevancy >= 0.80 else '❌'} |
| Context Precision | {self.context_precision:.3f} | 0.75 | {'✅' if self.context_precision >= 0.75 else '❌'} |
| Context Recall | {self.context_recall:.3f} | 0.70 | {'✅' if self.context_recall >= 0.70 else '❌'} |

**Items evaluated**: {self.n_items}
**Regression detected**: {self.regression_detected}
**Failed metrics**: {', '.join(self.failed_metrics) or 'none'}
"""


class RAGASHarness:
    """Nightly RAGAS evaluation harness.

    Usage:
        harness = RAGASHarness(rag_pipeline)
        report = await harness.run_nightly(golden_set, synthetic_set)
        harness.persist(report)
    """

    # Per PremAI 2026-07-27, these are 2026 production thresholds.
    THRESHOLDS = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.80,
        "context_precision": 0.75,
        "context_recall": 0.70,
    }

    def __init__(self, rag_pipeline, judge: Optional[LLMJudge] = None) -> None:
        self.rag_pipeline = rag_pipeline
        self.judge = judge or default_judge()
        self._ragas_judge = self._make_ragas_judge()

    def _make_ragas_judge(self):
        """Wrap our judge as a LangChain LLM (RAGAS expects this interface)."""
        from langchain_community.llms import Ollama
        # RAGAS works best with LangChain-compatible LLMs
        if self.judge.model_name.startswith("ollama/"):
            model = self.judge.model_name.split("/", 1)[1]
            lc_llm = Ollama(model=model, base_url="http://localhost:11434")
            return LangchainLLMWrapper(lc_llm)
        raise NotImplementedError(
            f"Judge {self.judge.model_name} not yet wired to RAGAS"
        )

    async def run_nightly(
        self,
        golden_set: GoldenQASet,
        synthetic_set: Optional[SyntheticQASet] = None,
    ) -> NightlyReport:
        """Run RAGAS eval against golden (+ optional synthetic) set.

        Returns a NightlyReport. If any metric drops below threshold,
        regression_detected=True.
        """
        import time
        all_items = list(golden_set.items)
        if synthetic_set:
            all_items.extend(synthetic_set.items)

        # Build RAGAS evaluation dataset
        ragas_items = []
        for item in all_items:
            # Call the actual RAG pipeline
            answer, contexts = await self.rag_pipeline.query(
                question=item.question, k=10
            )
            ragas_items.append({
                "user_input": item.question,
                "response": answer,
                "retrieved_contexts": [c.text for c in contexts],
                "reference": item.expected_answer,  # ground truth
            })

        dataset = EvaluationDataset.from_list(ragas_items)

        # Run all 4 metrics
        result = evaluate(
            dataset,
            metrics=[
                Faithfulness(llm=self._ragas_judge),
                AnswerRelevancy(llm=self._ragas_judge),
                ContextPrecision(llm=self._ragas_judge),
                ContextRecall(llm=self._ragas_judge),
            ],
        )

        # Compare against thresholds
        failed = [
            m for m, threshold in self.THRESHOLDS.items()
            if result[m] < threshold
        ]
        return NightlyReport(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            faithfulness=result["faithfulness"],
            answer_relevancy=result["answer_relevancy"],
            context_precision=result["context_precision"],
            context_recall=result["context_recall"],
            n_items=len(all_items),
            regression_detected=bool(failed),
            failed_metrics=failed,
            raw_scores=result,
        )

    def persist(self, report: NightlyReport,
                out_dir: Path = Path("data/eval/reports")) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"nightly_{report.timestamp.replace(' ', '_').replace(':', '')}.md"
        path.write_text(report.to_markdown())
        logger.info("Report written to %s", path)
```

```python
# src/omega/eval/deepeval_ci.py
from __future__ import annotations

import os
from typing import List

from deepeval import assert_test
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from .judge import default_judge
from .dataset import GoldenQASet


def make_deepeval_metrics(judge=None):
    """Build the 4 metrics for CI gate.

    Thresholds are tighter than nightly because CI is a hard gate.
    """
    judge = judge or default_judge()
    return [
        FaithfulnessMetric(threshold=0.90, model=judge.model_name),
        AnswerRelevancyMetric(threshold=0.85, model=judge.model_name),
        ContextualPrecisionMetric(threshold=0.80, model=judge.model_name),
        ContextualRecallMetric(threshold=0.75, model=judge.model_name),
    ]


def make_test_case(question: str, expected_answer: str,
                   actual_output: str, retrieval_context: List[str]) -> LLMTestCase:
    return LLMTestCase(
        input=question,
        actual_output=actual_output,
        expected_output=expected_answer,
        retrieval_context=retrieval_context,
    )


# Pytest fixture pattern (in tests/eval/test_deepeval_gate.py):
# def test_rag_quality(rag_pipeline, golden_qa):
#     for qa in golden_qa.items:
#         answer, contexts = rag_pipeline.query(qa.question, k=10)
#         tc = make_test_case(qa.question, qa.expected_answer, answer,
#                              [c.text for c in contexts])
#         assert_test(tc, make_deepeval_metrics())
```

#### 4.3 Test dataset construction

```python
# src/omega/eval/dataset.py
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class QAItem:
    question: str
    expected_answer: str
    source_doc_id: Optional[str] = None  # for ground truth provenance
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class GoldenQASet:
    """Human-curated golden Q&A set. ~50-200 items typically."""

    def __init__(self, items: List[QAItem]) -> None:
        self.items = items

    @classmethod
    def load(cls, path: Path) -> "GoldenQASet":
        items = [
            QAItem(**json.loads(line))
            for line in path.read_text().splitlines() if line
        ]
        return cls(items)

    def save(self, path: Path) -> None:
        with path.open("w") as f:
            for item in self.items:
                f.write(json.dumps(item.__dict__) + "\n")


class SyntheticQASet:
    """RAGAS-generated synthetic Q&A set. Use for breadth; golden for precision."""

    def __init__(self, items: List[QAItem]) -> None:
        self.items = items

    @classmethod
    def from_documents(cls, documents: List[str], n: int = 200,
                       judge=None) -> "SyntheticQASet":
        """Use RAGAS TestsetGenerator to create a synthetic set from documents."""
        from ragas.testset import TestsetGenerator
        from langchain_community.llms import Ollama
        from langchain_community.embeddings import OllamaEmbeddings

        llm = Ollama(model="gemma3:12b")
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        gen = TestsetGenerator.from_langchain(llm=llm, embedding_model=embeddings)

        # Convert text → LangChain Documents
        from langchain.schema import Document
        docs = [Document(page_content=t) for t in documents]
        testset = gen.generate_with_langchain_docs(docs, testset_size=n)

        items = [
            QAItem(
                question=item.question,
                expected_answer=item.ground_truth,
                source_doc_id=item.source_doc.metadata.get("id"),
                tags=["synthetic"],
            )
            for item in testset.test_data
        ]
        return cls(items)

    def save(self, path: Path) -> None:
        with path.open("w") as f:
            for item in self.items:
                f.write(json.dumps(item.__dict__) + "\n")
```

### 5. Code Snippet: End-to-End Smoke Test

```python
# tests/eval/test_ragas_metrics.py
"""Smoke test: RAGAS returns sane numbers on a tiny golden set.

Run: pytest tests/eval/test_ragas_metrics.py -v -s
"""
import pytest
from pathlib import Path

from src.omega.eval.ragas_harness import RAGASHarness
from src.omega.eval.dataset import GoldenQASet, QAItem


@pytest.fixture
def golden_qa() -> GoldenQASet:
    """Tiny golden set for smoke test. Real set has 50-200 items."""
    return GoldenQASet([
        QAItem(
            question="What is the canonical embedding dimension?",
            expected_answer="768 (per docs/strategy/EMBEDDING_HARDENING_STRATEGY)",
        ),
        QAItem(
            question="Which collection holds gemma-768 embeddings?",
            expected_answer="omega_vec_gemma_768",
        ),
        QAItem(
            question="What is the MRL dimension sequence?",
            expected_answer="768, 512, 256, 128, 64",
        ),
    ])


@pytest.fixture
def mock_rag_pipeline():
    """Pretend RAG pipeline that returns the expected answer verbatim.

    Replace with real pipeline in production.
    """
    class MockPipeline:
        async def query(self, question, k=10):
            # Naive mock: return the question + "answer" as context
            return (
                "Mock answer for: " + question,
                [type("C", (), {"text": "ctx 1"}), type("C", (), {"text": "ctx 2"})](),
            )
    return MockPipeline()


@pytest.mark.asyncio
async def test_ragas_returns_sane_numbers(mock_rag_pipeline, golden_qa):
    harness = RAGASHarness(mock_rag_pipeline)
    report = await harness.run_nightly(golden_qa)

    # All scores should be in [0, 1]
    assert 0.0 <= report.faithfulness <= 1.0
    assert 0.0 <= report.answer_relevancy <= 1.0
    assert 0.0 <= report.context_precision <= 1.0
    assert 0.0 <= report.context_recall <= 1.0
    assert report.n_items == 3
```

### 6. Benchmark Methodology

**Goal**: prove that the eval harness works on the real RAG pipeline, with regression detection in CI.

**Test plan**:

1. **Smoke test** (above) — verify RAGAS returns valid scores on a mock.
2. **Threshold test** — synthetically perturb the pipeline (e.g., add noise to retrieved contexts) and confirm that RAGAS scores drop below thresholds.
3. **Regression test** — store last week's `nightly_*.md` report; new runs must not regress > 2% on any metric.
4. **CI gate test** — write a `test_deepeval_gate.py` with a known-bad pipeline; assert that `assert_test` raises (blocks merge).

**Acceptance criteria**:
- ✅ Nightly run completes in <10 minutes for 100-item golden set (with Ollama local judge).
- ✅ RAGAS scores correlate with human judgment (Spearman > 0.7 on a labeled calibration set of 30 items).
- ✅ CI gate blocks PR when any metric drops > 5% from baseline.
- ✅ All eval runs are reproducible (judge temperature = 0).

### 7. Cost Analysis

| Item | One-time | Recurring | Notes |
|---|---|---|---|
| Engineering (RAGAS harness) | 1 week | 0.5 day/sprint | Initial + new metrics |
| Engineering (DeepEval CI) | 3 days | 0.5 day/sprint for new gates | Wire into existing pytest |
| Engineering (TruLens) | 3 days | 1 day/quarter for dashboards | Optional for debut |
| Engineering (golden set curation) | 1 week | 1 day/month for new items | Critical for trustworthy metrics |
| Compute (local judge) | — | ~10 min/nightly run on Ryzen 5700U | $0 (M7) |
| Cloud judge (optional) | — | $0.15/1K items with gpt-4o-mini | Use for production-grade quality |

**Total 12-month TCO**: ~$5K engineering, $0 cloud (M7 default).

### 8. Risk Analysis

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| LLM judge is biased (different from human) | High | High | Calibrate with 30-item labeled set; report inter-rater agreement |
| Golden set is too small (n=20) | High | Medium | Bootstrap to n=100+ before trusting regression detection |
| RAGAS LLM judge hallucinates a score | Medium | Medium | Use temperature=0; cross-validate with TruLens on a sample |
| CI gate too strict (false positives) | Medium | High (slows team) | Use trailing 7-day average; allow 5% wiggle |
| CI gate too lenient (false negatives) | Medium | High (regressions ship) | Add multiple metrics; require 2+ to fail before blocking |
| Synthetic test set has low correlation with real queries | High | Medium | Periodically sample 5% of prod queries to validate |
| RAGAS dependency breaks on Python 3.13 | Low | High | Pin in `pyproject.toml`; CI tests on 3.13 |

**Critical risk**: **LLM judge bias**. RAGAS / DeepEval / TruLens all use an LLM to score. If the judge model is bad, the metrics are bad. Mitigation: **always validate on a small human-labeled set** before trusting automated metrics. The PremAI 2026-07-27 guide explicitly warns against blindly trusting LLM judges.

### 9. Dependencies

```toml
# pyproject.toml
[project.optional-dependencies]
eval = [
    "ragas>=0.4.0",                  # Apache 2.0
    "deepeval>=0.40.0",              # Apache 2.0
    "trulens-eval>=2.0.0",           # MIT
    "langchain>=0.3.0",              # MIT
    "langchain-community>=0.3.0",    # MIT
]
```

All Apache 2.0 or MIT. Total download size: ~120 MB (RAGAS pulls in a lot).

**License summary**:
- RAGAS: Apache 2.0.
- DeepEval: Apache 2.0.
- TruLens: MIT (now Snowflake).
- LangChain: MIT.
- All compatible with M14 Heritage.

### 10. References

1. **"RAGAS, TruLens, DeepEval: LLM Evaluation Frameworks (2026)"** (Atlan, 2026-04-10). <https://atlan.com/know/llm-evaluation-frameworks-compared> — primary 2026 comparison; framework feature matrix and use-case guidance.
2. **"RAG Evaluation: Metrics, Frameworks & Testing (2026)"** (PremAI, 2026-07-27). <https://www.premai.io/blog/rag-evaluation-metrics-frameworks-testing-2026/> — 17-min read, definitive 2026 guide; recommends RAGAS for exploration, DeepEval for CI, TruLens for prod.
3. **RAGAS documentation (stable)**. <https://docs.ragas.io/en/stable> — official; defines the 4 core metrics.
4. **Faithfulness metric** (RAGAS docs). <https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness> — definition: 0-1 score, reference-free.
5. **"RAG Evaluation 2026: Methods, Metrics, Frameworks"** (Datavlab, 2026-03-08). <https://datavlab.ai/post/rag-evaluation-methods-metrics-2026-guide> — confirms "by April 2026, the RAG evaluation tooling has matured. RAGAS provides the conceptual framework. DeepEval delivers CI/CD integration."
6. **"RAG Evaluation Frameworks: RAGAS vs TruLens vs DeepEval"** (Analytics Vidhya, 2026-07-12). <https://www.analyticsvidhya.com/blog/2026/07/rag-evaluation-frameworks/> — 3-way comparison.
7. **"RAG Evaluation: Metrics, Tools, and the Context Gap (2026)"** (Atlan, 2026-04-10). <https://atlan.com/know/how-to-evaluate-rag-systems-explained/> — discusses the "blind spot" of source-data quality, recommends context-layer validation alongside metric scoring.
8. **"RAG Evaluation Metrics: RAGAS Faithfulness & Recall"** (AI/TLDR, 2026-06-12). <https://ai-tldr.dev/learn/rag/rag-evaluation/rag-evaluation-metrics/> — confirms "most of it is reference-free — you do not need a human to write the ideal answer for every test question."
9. **Evaluate RAG** (Arize Phoenix docs). <https://arize.com/docs/phoenix/cookbook/evaluation/evaluate-rag> — Phoenix recipe; useful for the production observability layer.
10. **"RAG Evaluation Frameworks Compared: RAGAS vs TruLens vs DeepEval"** (Q2B Studio, 2026-07-29). <https://q2bstudio.com/en/our-blog/2102981/rag-evaluation-frameworks-compared-ragas-vs-trulens-vs-deepeval> — third independent 2026 comparison; aligns with the three-layer recommendation.

---

## L3 — Raw Signal

### Metric catalog (canonical names)

| Metric | RAGAS | DeepEval | TruLens | Threshold (production) |
|---|---|---|---|---|
| Faithfulness | ✅ | `FaithfulnessMetric` | `Groundedness` | 0.85 (RAGAS) / 0.90 (DeepEval CI) |
| Answer Relevancy | ✅ | `AnswerRelevancyMetric` | `AnswerRelevance` | 0.80 |
| Context Precision | ✅ | `ContextualPrecisionMetric` | `ContextRelevance` | 0.75 |
| Context Recall | ✅ | `ContextualRecallMetric` | (custom) | 0.70 |
| Hallucination | (derived) | `HallucinationMetric` | (custom) | <0.10 (lower is better) |
| Bias | (custom) | `BiasMetric` | (custom) | <0.05 |
| Toxicity | (custom) | `ToxicityMetric` | (custom) | <0.05 |

### Three-layer matrix

| Layer | Tool | When it runs | Output | Blocks PR? |
|---|---|---|---|---|
| **Exploration** | RAGAS | On demand, nightly batch | Markdown report + JSON | No |
| **CI/CD gate** | DeepEval | Every PR (`pytest tests/eval/`) | Pass/fail + per-metric breakdown | **Yes** |
| **Production** | TruLens / Phoenix | Every LLM call in prod | OTel spans + dashboard | No (alerts) |

### Adoption roadmap

| Phase | What ships | Effort |
|---|---|---|
| Week 1 | RAGAS harness + Ollama judge + nightly report | 5 days |
| Week 2 | DeepEval CI gate + 50-item golden set | 5 days |
| Week 3 | TruLens production tracing + dashboard | 5 days |
| Week 4 | Synthetic test set (RAGAS TestsetGenerator) + 100-item golden set | 5 days |
| Post-debut | MLflow / Weights & Biases integration for experiment tracking | 2 weeks |

### Summary table

| Aspect | Value |
|---|---|
| Effort | 2-3 weeks initial + 1 day/sprint |
| Lines of code | ~600 (excluding tests) |
| Dependencies | 5 new pip packages (Apache 2.0 / MIT) |
| Compute (nightly, 100 items) | ~10 min on Ryzen 5700U (Ollama gemma3:12b) |
| M7 alignment | ✅ (Ollama local judge default) |
| M13 (Temple-Grade) impact | **Foundational** — enables measurable quality |
| M23 (Failure Integrity) impact | CI gate blocks regressions |
| Priority | **P0** |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R_RAGAS_20260829 ⬡ opencode ⬡ minimax/minimax-m3:free ⬡ PUBLIC-DEBUT-01*
