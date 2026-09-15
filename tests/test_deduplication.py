"""Unit tests for deterministic paper deduplication and metadata fusion."""
from app.models.schemas import Paper, QualityTier
from app.sources.base import normalize_doi, normalize_arxiv_id, normalize_title
from app.retrieval.deduplication import deduplicate_papers


def test_normalizers():
    assert normalize_doi("https://doi.org/10.1109/CVPR.2023.00123") == "10.1109/cvpr.2023.00123"
    assert normalize_doi("DOI: 10.1016/J.PATCOG.2022.108920") == "10.1016/j.patcog.2022.108920"
    assert normalize_doi(None) is None

    assert normalize_arxiv_id("arXiv:2305.18273v2") == "2305.18273"
    assert normalize_arxiv_id("https://arxiv.org/abs/2104.08821v1.pdf") == "2104.08821"

    assert normalize_title("PromptAD: Learning Prompts with Finding Anomaly!") == "promptad learning prompts with finding anomaly"


def test_deduplication_by_doi():
    p1 = Paper(
        title="PromptAD: Learning Prompts for Anomaly Detection",
        doi="10.1109/TII.2024.3312345",
        sources=["openalex"],
        citation_count=10,
    )
    p2 = Paper(
        title="PromptAD: Learning Prompts for Anomaly Detection (IEEE)",
        doi="https://doi.org/10.1109/tii.2024.3312345",
        sources=["semantic_scholar"],
        citation_count=25,
        venue="IEEE TII",
    )

    deduped = deduplicate_papers([p1, p2])
    assert len(deduped) == 1
    merged = deduped[0]
    assert "openalex" in merged.sources
    assert "semantic_scholar" in merged.sources
    assert merged.citation_count == 25
    assert merged.venue == "IEEE TII"


def test_deduplication_by_arxiv_id():
    p1 = Paper(
        title="Edge-Guided Vision Transformers",
        arxiv_id="arXiv:2305.18273v1",
        sources=["arxiv"],
    )
    p2 = Paper(
        title="Edge-Guided Vision Transformers for Production",
        arxiv_id="2305.18273v2",
        sources=["semantic_scholar"],
    )

    deduped = deduplicate_papers([p1, p2])
    assert len(deduped) == 1
    assert deduped[0].arxiv_id == "2305.18273"
    assert set(deduped[0].sources) == {"arxiv", "semantic_scholar"}


def test_deduplication_by_title_author_year():
    p1 = Paper(
        title="Deep Defect Inspection on Metallic Surfaces",
        authors=["Chen, Xiaoming", "Smith, John"],
        year=2023,
        sources=["crossref"],
    )
    p2 = Paper(
        title="Deep Defect Inspection on Metallic Surfaces!",
        authors=["X. Chen", "J. Smith"],
        year=2023,
        sources=["openalex"],
    )

    deduped = deduplicate_papers([p1, p2])
    assert len(deduped) == 1
    assert "crossref" in deduped[0].sources
    assert "openalex" in deduped[0].sources


def test_distinct_papers_preserved():
    p1 = Paper(title="Method A for Defect Detection", year=2023, authors=["Author One"])
    p2 = Paper(title="Method B for Quality Inspection", year=2024, authors=["Author Two"])

    deduped = deduplicate_papers([p1, p2])
    assert len(deduped) == 2

