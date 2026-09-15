"""Unit tests for Pydantic data models and schemas."""
import pytest
from app.models.schemas import (
    Paper,
    QualityTier,
    SearchQuery,
    PassType,
    ResearchObjective,
    ResearchPlan,
    Claim,
    EvidenceType,
    EvidenceStrength,
    EvidenceRecord,
    ContradictionRecord,
    ResearchGap,
    GapCategory,
    ResearchReport,
)


def test_paper_schema_defaults():
    paper = Paper(
        title="Attention Is All You Need",
        authors=["Vaswani, A.", "Shazeer, N."],
        year=2017,
        venue="NeurIPS",
    )
    assert paper.title == "Attention Is All You Need"
    assert paper.quality_tier == QualityTier.TIER_2
    assert paper.relevance_score == 0.0
    assert len(paper.authors) == 2
    assert paper.doi is None


def test_claim_schema_validation():
    claim = Claim(
        claim_id="C01",
        claim_text="Transformer models outperform RNNs in sequence transduction tasks.",
        paper_id="P01",
        evidence_type=EvidenceType.EMPIRICAL_RESULT,
        evidence_strength=EvidenceStrength.VERY_STRONG,
        confidence=0.95,
    )
    assert claim.claim_id == "C01"
    assert claim.evidence_type == EvidenceType.EMPIRICAL_RESULT
    assert claim.confidence == 0.95


def test_contradiction_record_schema():
    rec = ContradictionRecord(
        claim="Zero-shot prompt tuning generalizes across all industrial textures",
        supporting_papers=["P01", "P02"],
        contradicting_papers=["P03"],
        overall_assessment="Severe degradation observed on metallic micro-textures",
    )
    assert len(rec.supporting_papers) == 2
    assert len(rec.contradicting_papers) == 1
    assert "metallic micro-textures" in rec.overall_assessment


def test_research_gap_schema():
    gap = ResearchGap(
        gap_id="GAP-01",
        category=GapCategory.ROBUSTNESS_GAP,
        description="Models fail under unseen illumination shifts.",
        supporting_evidence=["P02"],
        proposed_directions=["Invariant self-supervised learning"],
    )
    assert gap.category == GapCategory.ROBUSTNESS_GAP
    assert len(gap.proposed_directions) == 1


def test_research_report_serialization():
    report = ResearchReport(
        research_question="What are the trade-offs of vision transformers in defect detection?",
        executive_summary="Vision transformers achieve higher accuracy at the cost of latency.",
        research_methodology="Multi-pass systematic retrieval",
        academic_sources_searched=["openalex", "arxiv"],
        search_strategy_summary="Executed 4 queries",
        key_findings=["Finding 1"],
        evidence_strength_summary="Moderate evidence overall",
        conclusion="ViTs require quantization for edge deployment.",
    )
    dumped = report.model_dump()
    assert dumped["research_question"].startswith("What are the trade-offs")
    assert "openalex" in dumped["academic_sources_searched"]

