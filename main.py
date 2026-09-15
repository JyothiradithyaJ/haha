"""CLI entrypoint for the Lightweight Academic Research Agent."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from app.config import config
from app.agent.ollama_client import OllamaClient, OllamaError
from app.agent.researcher import ResearcherAgent
from app.reports.generator import ReportGenerator
from app.sources.base import AcademicSource
from app.models.schemas import Paper, QualityTier


def positive_int(value: str) -> int:
    """Parse a strictly positive command-line integer."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


class MockAcademicSource(AcademicSource):
    """Offline mock source for rapid local testing and integration demos."""

    name: str = "mock_source"
    default_tier: QualityTier = QualityTier.TIER_1

    def search(self, query: str, limit: int = 10, year_start: int | None = None, year_end: int | None = None) -> list[Paper]:
        return [
            self.build_paper(
                title="PromptAD: Learning Prompts with Finding Anomaly for Industrial Inspection",
                authors=["Li, J.", "Wu, Z.", "Zhang, H."],
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
                authors=["Chen, X.", "Kumar, S.", "Mueller, T."],
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
        ]

    def get_paper(self, identifier: str) -> Paper | None:
        return self.search("test")[0]

    def health_check(self) -> bool:
        return True


def verify_ollama(client: OllamaClient) -> None:
    """Verify local Ollama service status and print diagnostic details."""
    print("=" * 60)
    print("Checking Local Ollama Runtime...")
    print(f"Base URL: {client.base_url}")
    print(f"Required Model: {client.model}")
    print("=" * 60)

    try:
        status = client.check_health()
        print(" [SUCCESS] Ollama server is running and reachable.")
        print(f" [SUCCESS] Target model '{client.model}' is available locally.")
        print(f" Installed local models: {', '.join(status['models'])}")
    except OllamaError as err:
        print("! [ERROR] Ollama diagnostic check failed:")
        print(f"  {err}")
        print("\nTroubleshooting:")
        print("  1. Ensure Ollama is installed and running: 'ollama serve'")
        print(f"  2. Pull the required model: 'ollama pull {client.model}'")
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Lightweight Academic Research Agent: Evidence-grounded academic report generator."
    )
    parser.add_argument(
        "question",
        nargs="?",
        default=None,
        help="Research question to analyze (e.g. 'Compare recent deep-learning methods for industrial defect detection...')"
    )
    parser.add_argument(
        "--verify-ollama",
        action="store_true",
        help="Check connection to local Ollama runtime and verify qwen3.5:4b availability."
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in offline mock mode using synthetic academic fixtures for verification."
    )
    parser.add_argument(
        "--iterations",
        type=positive_int,
        default=config.MAX_RESEARCH_ITERATIONS,
        help=f"Maximum number of search iterations (default: {config.MAX_RESEARCH_ITERATIONS})"
    )
    parser.add_argument(
        "--max-papers",
        type=positive_int,
        default=config.MAX_PAPERS_TOTAL,
        help=f"Maximum papers to retrieve and rank (default: {config.MAX_PAPERS_TOTAL})"
    )
    return parser.parse_args()


def main() -> None:
    """CLI execution entrypoint."""
    args = parse_args()
    ollama_client = OllamaClient()

    if args.verify_ollama:
        verify_ollama(ollama_client)
        return

    question = args.question
    if not question:
        print("\nAcademic Research Agent")
        print("-" * 40)
        try:
            question = input("Enter your academic research question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)

    if not question:
        print("Error: No research question provided.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("LIGHTWEIGHT ACADEMIC RESEARCH AGENT")
    print(f"Research Question: \"{question}\"")
    print(f"Local Model: {config.OLLAMA_MODEL} ({config.OLLAMA_BASE_URL})")
    print(f"Mode: {'OFFLINE MOCK' if args.mock else 'LIVE ACADEMIC APIS'}")
    print("=" * 70 + "\n")

    # Progress printer
    def on_progress(message: str) -> None:
        print(f"-> {message}")

    search_coord = None
    if args.mock:
        from app.retrieval.search import SearchCoordinator
        search_coord = SearchCoordinator(sources=[MockAcademicSource()])

    agent = ResearcherAgent(
        ollama_client=ollama_client,
        search_coordinator=search_coord,
        progress_callback=on_progress,
        verify_bibliography=not args.mock,
    )

    try:
        report = agent.run(
            question=question,
            max_iterations=args.iterations,
            max_papers=args.max_papers,
        )
    except Exception as err:
        print(f"\n[FATAL ERROR] Research pipeline encountered an error: {err}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    generator = ReportGenerator()
    md_path, json_path = generator.save_report(report)

    print("\n" + "=" * 70)
    print("RESEARCH REPORT GENERATED SUCCESSFULLY")
    print("=" * 70)
    print(f"Markdown Report: {md_path}")
    print(f"Structured Data: {json_path}")
    print(f"Total Unique Papers Analyzed: {len(report.papers)}")
    print(f"Substantive Claims Extracted: {len(report.claims)}")
    print(f"Scientific Contradictions Identified: {len(report.contradictions)}")
    print(f"Classified Research Gaps: {len(report.research_gaps)}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
