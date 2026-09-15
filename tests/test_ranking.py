"""Unit tests for transparent multi-factor ranking."""
from app.models.schemas import Paper, QualityTier
from app.retrieval.ranking import rank_papers, compute_overlap


def test_compute_overlap():
    tokens = {"defect", "detection", "transformer"}
    text = "A novel vision transformer architecture for real-time defect detection"
    overlap = compute_overlap(tokens, text)
    assert overlap == 1.0


def test_ranking_relevance_ordering():
    # p1 matches query strongly
    p1 = Paper(
        title="Deep Learning Methods for Industrial Defect Detection: A Comprehensive Survey",
        abstract="We review deep learning architectures for defect detection in manufacturing.",
        year=2024,
        quality_tier=QualityTier.TIER_1,
        citation_count=50,
    )
    # p2 is unrelated
    p2 = Paper(
        title="Quantum Computing Algorithms for Financial Portfolio Optimization",
        abstract="Analysis of quantum annealing in financial risk models.",
        year=2021,
        quality_tier=QualityTier.TIER_2,
        citation_count=10,
    )

    ranked = rank_papers([p2, p1], query_text="industrial defect detection deep learning")
    assert ranked[0].title == p1.title
    assert ranked[0].internal_id == "P01"
    assert ranked[1].internal_id == "P02"
    assert ranked[0].relevance_score > ranked[1].relevance_score


def test_ranking_inspectable_breakdown():
    paper = Paper(
        title="Industrial Defect Detection",
        abstract="Empirical evaluation of detection models.",
        year=2024,
        quality_tier=QualityTier.TIER_1,
    )
    ranked = rank_papers([paper], query_text="industrial defect detection")
    assert "title_match" in ranked[0].score_breakdown
    assert "abstract_match" in ranked[0].score_breakdown
    assert "quality_tier" in ranked[0].score_breakdown
    assert "recency" in ranked[0].score_breakdown


def test_recent_vs_foundational_priority():
    recent_paper = Paper(
        title="Defect Detection",
        year=2025,
        citation_count=5,
    )
    older_seminal = Paper(
        title="Defect Detection",
        year=2018,
        citation_count=800,
    )

    ranked_recent = rank_papers([older_seminal, recent_paper], query_text="defect detection", recent_priority=True)
    assert ranked_recent[0].year == 2025

    ranked_foundational = rank_papers([recent_paper, older_seminal], query_text="defect detection", foundational_priority=True)
    assert ranked_foundational[0].year == 2018

