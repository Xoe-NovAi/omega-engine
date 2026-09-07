"""Tests for the Curation Pipeline — domain classification, quality scoring, and curation."""
import pytest
from omega.library.curator import CurationExtractor, DomainType


class TestCurationExtractor:
    @pytest.fixture
    def extractor(self):
        return CurationExtractor()

    def test_classify_domain_code(self, extractor):
        """Code content with GitHub URLs and code blocks."""
        url = "https://github.com/user/repo"
        content = """def hello():
            print("hello world")
        import os
        ```python
        x = 1
        ```
        """
        domain = extractor.classify_domain(content, url)
        assert domain == DomainType.CODE

    def test_classify_domain_science(self, extractor):
        """Content with DOI and academic structure."""
        url = "https://arxiv.org/abs/2301.12345"
        content = """Abstract: This paper presents a novel method.
        Introduction: Previous work has shown...
        Methodology: We used a transformer-based approach.
        DOI: 10.1234/zenodo.1234567
        """
        domain = extractor.classify_domain(content, url)
        assert domain == DomainType.SCIENCE

    def test_classify_domain_general(self, extractor):
        """Generic content without strong signals."""
        url = "https://blog.example.com/post"
        content = "Today I woke up and had breakfast. Then I went for a walk."
        domain = extractor.classify_domain(content, url)
        assert domain == DomainType.GENERAL

    def test_classify_domain_data(self, extractor):
        """Dataset content with CSV references."""
        url = "https://data.gov/dataset/123"
        content = """SELECT * FROM users
        SELECT name, email FROM contacts
        dataset contains 1000 rows
        <table><tr><td>data</td></tr></table>
        """
        domain = extractor.classify_domain(content, url)
        assert domain == DomainType.DATA

    def test_calculate_quality_factors(self, extractor):
        """Quality factors should have expected shape."""
        content = """# Title
        ## Section 1
        This is a sample document with enough text to calculate quality factors.
        It contains multiple paragraphs and should produce reasonable quality scores.
        DOI: 10.1234/test.5678
        
        ## Section 2
        More content here for completeness.
        <table><tr><td>Cell</td></tr></table>
        """
        url = "https://arxiv.org/abs/2301.12345"
        domain = DomainType.SCIENCE
        factors = extractor.calculate_quality_factors(content, url, domain)

        assert "freshness" in factors
        assert "completeness" in factors
        assert "authority" in factors
        assert "structure" in factors
        assert "accessibility" in factors
        assert all(0.0 <= v <= 1.0 for v in factors.values())

    def test_extract_citations(self, extractor):
        content = """
        DOI: 10.1234/zenodo.1234567
        DOI: 10.5678/another.90123
        ArXiv: 2301.12345
        ArXiv: 2402.67890
        """
        citations = extractor.extract_citations(content)
        assert citations["doi"] == 2
        assert citations["arxiv"] == 2
        assert citations["total"] == 4

    def test_heading_structure_score_no_headings(self, extractor):
        score = extractor.calculate_heading_structure_score("Plain text with no HTML headings")
        assert score == 0.0

    def test_heading_structure_score_with_h1(self, extractor):
        content = "<h1>Title</h1><p>Content</p><h2>Sub</h2><p>More</p>"
        score = extractor.calculate_heading_structure_score(content)
        assert score > 0.0


class TestCurationPipeline:
    @pytest.fixture
    def mock_extractor(self):
        """Mock ContentExtractor to return known content without HTTP calls."""
        from unittest.mock import AsyncMock
        from omega.library.extractor import ExtractedContent

        extractor = AsyncMock()
        extractor.extract = AsyncMock(return_value=ExtractedContent(
            source="https://example.com/test.txt",
            source_type="url",
            title="Test Document",
            body="""
                This is a comprehensive test document with plenty of content
                to generate a reasonable quality score. It includes multiple
                paragraphs that should contribute to completeness and structure
                quality factors. The content is well-organized with headings
                and should pass basic quality thresholds.
                DOI: 10.1234/test.56789
            """,
            summary="A test document for curation pipeline testing.",
            author="Test Author",
            language="en",
            headings=["Title"],
            links=[],
            word_count=50,
            published_date="2024-01-01",
        ))
        return extractor

    @pytest.mark.anyio
    async def test_process_returns_curated_document(self, mock_extractor):
        from omega.library.curator import CurationPipeline
        pipeline = CurationPipeline()
        pipeline.extractor = mock_extractor

        doc = await pipeline.process(
            source="https://example.com/test.txt",
            source_type="url",
            title="Test Document",
            tags=["test", "example"],
            metadata={"custom": "value"},
        )

        assert doc.doc_id.startswith("doc_")
        assert doc.title == "Test Document"
        assert doc.quality_score > 0
        assert "test" in doc.tags
        assert doc.metadata.get("custom") == "value"

    @pytest.mark.anyio
    async def test_quality_threshold(self, mock_extractor):
        from omega.library.curator import CurationPipeline
        pipeline = CurationPipeline()
        pipeline.extractor = mock_extractor

        doc = await pipeline.process(
            source="https://example.com/minimal.md",
            source_type="url",
            title="Minimal",
        )

        # With mocked 50-word document, quality should be low but above 0.1
        assert pipeline.is_above_threshold(doc, 0.1) == True
        # But below 0.3 (50 words, no HTML structure = low completeness)
        assert pipeline.is_above_threshold(doc, 0.3) == False
