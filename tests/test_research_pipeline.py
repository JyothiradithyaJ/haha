"""End-to-end integration test for the academic research agent pipeline."""
import re
import tempfile
from pathlib import Path
from app.models.schemas import Paper, QualityTier
from app.sources.base import AcademicSource
from app.retrieval.search import SearchCoordinator
from app.agent.researcher import ResearcherAgent
from app.reports.generator import ReportGenerator


class RealisticTestAcademicSource(AcademicSource):
    """Test source providing realistic papers for pipeline verification."""

    name: str = "mock_academic_db"
    default_tier: QualityTier = QualityTier.TIER_1

    def search(self, query: str, limit: int = 10, year_start: int | None = None, year_end: int | None = None) -> list[Paper]:
        return [
            self.build_paper(
                title="PromptAD: Learning Prompts with Finding Anomaly for Industrial Inspection",
                authors=["Li, Jing", "Wu, Zhaoxiang", "Zhang, Hao"],
                year=2024,
                venue="IEEE Transactions on Industrial Informatics",
                abstract="We propose PromptAD, a prompt-learning framework for zero-shot defect detection in industrial surfaces. Our method achieves 94.2% AUC on MVTec-AD with 1-shot setup. However, inference latency remains high due to large vision-language transformer backbones.",
                doi="10.1109/TII.2024.3312345",
                citation_count=42,
                is_open_access=True,
                quality_tier=QualityTier.TIER_1,
            ),
            self.build_paper(
                title="Industrial Defect Detection Under Severe Domain Shift: Failure Modes and Benchmarks",
                authors=["Chen, Xiaoming", "Kumar, Sanjeev", "Mueller, Thomas"],
                year=2025,
                venue="Computer Vision and Image Understanding",
                abstract="Deep learning defect detection models report significant false positive rates when deployed to noisy metallic textures. We show that state-of-the-art vision models suffer up to a 28% drop in precision under subtle illumination changes, demonstrating a severe robustness gap.",
                doi="10.1016/j.cviu.2025.103982",
                citation_count=18,
                is_open_access=True,
                quality_tier=QualityTier.TIER_1,
            ),
            self.build_paper(
                title="Real-Time Edge-Guided Vision Transformers for Production Line Inspection",
                authors=["Wang, Y.", "Zhao, B."],
                year=2023,
                venue="IEEE Robotics and Automation Letters",
                abstract="This paper introduces EdgeVit-Defect, an ultra-lightweight transformer for real-time edge detection operating at 65 FPS on embedded NVIDIA Jetson platforms. While achieving line-rate inference, fine-grained micro-scratch detection exhibits lower recall compared to heavy foundation models.",
                arxiv_id="2305.18273",
                citation_count=65,
                is_open_access=True,
                quality_tier=QualityTier.TIER_2,
            ),
            self.build_paper(
                title="Duplicate Paper from Alternate Database: Learning Prompts with Finding Anomaly",
                authors=["Li, Jing", "Wu, Z."],
                year=2024,
                abstract="We propose PromptAD, a prompt-learning framework for zero-shot defect detection in industrial surfaces.",
                doi="10.1109/tii.2024.3312345",  # Same DOI as P1, should be deduplicated
                citation_count=40,
                quality_tier=QualityTier.TIER_2,
            ),
        ]

    def get_paper(self, identifier: str) -> Paper | None:
        return self.search("")[0]

    def health_check(self) -> bool:
        return True


def test_end_to_end_research_pipeline():
    # 1. Setup mock search coordinator
    search_coord = SearchCoordinator(sources=[RealisticTestAcademicSource()])

    # 2. Instantiate agent (using deterministic fallback if Ollama is not running)
    agent = ResearcherAgent(search_coordinator=search_coord, verify_bibliography=False)

    # 3. Run pipeline
    question = "Compare recent deep-learning methods for industrial defect detection and identify major unresolved research gaps"
    report = agent.run(question, max_iterations=2, max_papers=10)

    # 4. Verify Deduplication
    assert len(report.papers) == 3  # The 4th duplicate paper with same DOI was merged!
    paper_ids = [p.internal_id for p in report.papers]
    assert paper_ids == ["P01", "P02", "P03"]

    # 5. Verify Claims & Evidence Mapping
    assert len(report.claims) > 0
    assert len(report.evidence_records) > 0
    for ev in report.evidence_records:
        assert ev.paper_id in paper_ids
        assert ev.claim_id.startswith("C")

    # 6. Verify Contradiction Analysis
    assert len(report.contradictions) > 0
    for contra in report.contradictions:
        for pid in contra.supporting_papers:
            assert pid in paper_ids
        for pid in contra.contradicting_papers:
            assert pid in paper_ids

    # 7. Verify Research Gaps
    assert len(report.research_gaps) > 0
    for gap in report.research_gaps:
        assert gap.gap_id.startswith("GAP")
        assert gap.category.value is not None
        assert len(gap.supporting_evidence) > 0
        for ev_id in gap.supporting_evidence:
            assert ev_id in paper_ids

    # 8. Verify Markdown Report and 16 Sections
    generator = ReportGenerator()
    md_output = generator.render_markdown(report)

    for section_num in range(1, 17):
        assert f"## {section_num}." in md_output, f"Missing section {section_num} in rendered report"

    # 9. Verify Strict Citation Traceability
    # Extract all [Pxx] matches from the report text
    cited_ids = set(re.findall(r"\[(P\d{2})\]", md_output))
    for cited in cited_ids:
        assert cited in paper_ids, f"Report hallucinated citation [{cited}] not present in retrieved papers!"

    # 10. Verify File Saving (Markdown + JSON)
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir)
        md_file, json_file = generator.save_report(report, output_dir=out_dir)
        assert md_file.exists()
        assert json_file.exists()
        assert md_file.stat().st_size > 500
        assert json_file.stat().st_size > 500
