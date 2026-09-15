from app.models.schemas import Paper, QualityTier, ResearchPlan, ResearchObjective, Claim, EvidenceType
from app.retrieval.ranking import rank_papers
from app.agent.synthesizer import ReportSynthesizer
from app.reports.generator import ReportGenerator


def paper(title, abstract):
    return Paper(title=title, abstract=abstract, year=2025, quality_tier=QualityTier.TIER_1)


def test_off_topic_records_are_excluded_by_concept_floor():
    papers = [
        paper("Table of Contents", "A table of contents for a physics book."),
        paper("Statehood in Congo", "A political science analysis of statehood in Congo."),
        paper("Artificial Intelligence and Machine Learning", "Artificial intelligence and machine learning methods are compared in this survey."),
    ]
    ranked = rank_papers(
        papers,
        "What is AI and how is it different about ML",
        concept_vocabulary=["AI", "ML"],
        enforce_concept_floor=True,
    )
    assert len(ranked) == 1
    assert ranked[0].title == "Artificial Intelligence and Machine Learning"


def test_comparison_table_is_emitted_only_for_comparative_plan():
    papers = [
        paper("AI methods", "Artificial intelligence methods use learning and reasoning."),
        paper("ML methods", "Machine learning methods train predictive models with data."),
    ]
    papers[0].internal_id = "P01"
    papers[1].internal_id = "P02"
    claims = [
        Claim(
            claim_id="C01",
            claim_text="Artificial intelligence uses learning and reasoning.",
            paper_id="P01",
            evidence_type=EvidenceType.METHODOLOGICAL_CLAIM,
        ),
        Claim(
            claim_id="C02",
            claim_text="Machine learning trains predictive models with data.",
            paper_id="P02",
            evidence_type=EvidenceType.METHODOLOGICAL_CLAIM,
        ),
    ]
    plan = ResearchPlan(
        main_question="AI vs ML",
        entities=["AI", "ML"],
        important_concepts=["AI", "ML"],
        comparative=True,
        output_format="comparison_table",
        research_objectives=[ResearchObjective(objective_id="OBJ-1", description="compare")],
    )
    table = ReportSynthesizer._comparison_table(plan, papers, claims)
    assert table
    assert "AI" in table[0] and "ML" in table[0]
    md = ReportGenerator().render_markdown(
        __import__("app.models.schemas", fromlist=["ResearchReport"]).ResearchReport(
            research_question="AI vs ML",
            executive_summary="x",
            research_methodology="x",
            academic_sources_searched=[],
            search_strategy_summary="x",
            key_findings=[],
            evidence_strength_summary="x",
            conclusion="x",
            papers=papers,
            claims=claims,
            comparison_table=table,
            entities=["AI", "ML"],
            comparative=True,
        )
    )
    assert "## Comparison" in md
    assert "[P01]" in md and "[P02]" in md


def test_comparison_rows_do_not_reuse_unrelated_claims():
    papers = [
        paper("AI methods", "Artificial intelligence methods use learning and reasoning."),
        paper("ML methods", "Machine learning methods train predictive models with data."),
    ]
    papers[0].internal_id = "P01"
    papers[1].internal_id = "P02"
    claims = [
        Claim(
            claim_id="C01",
            claim_text="Artificial intelligence has a methodological framework.",
            paper_id="P01",
            evidence_type=EvidenceType.METHODOLOGICAL_CLAIM,
        ),
        Claim(
            claim_id="C02",
            claim_text="Machine learning achieves 95 percent accuracy on the benchmark.",
            paper_id="P02",
            evidence_type=EvidenceType.EMPIRICAL_RESULT,
        ),
    ]
    plan = ResearchPlan(
        main_question="AI vs ML",
        entities=["AI", "ML"],
        important_concepts=["AI", "ML"],
        comparative=True,
        output_format="comparison_table",
    )
    table = ReportSynthesizer._comparison_table(plan, papers, claims)
    performance_rows = [row for row in table if row["Dimension"] == "Performance / benchmarks"]
    assert performance_rows
    assert "insufficient evidence retrieved" in performance_rows[0]["AI"]
    assert "95 percent accuracy" in performance_rows[0]["ML"]


def test_non_comparative_plan_has_no_comparison_table():
    plan = ResearchPlan(main_question="Explain AI", entities=["AI"], important_concepts=["AI"], comparative=False)
    assert ReportSynthesizer._comparison_table(plan, [paper("AI", "Artificial intelligence")], []) == []
