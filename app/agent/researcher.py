"""Academic research loop orchestrator with explicit query understanding."""
from __future__ import annotations

import logging
from typing import Callable

from app.config import config
from app.models.schemas import Paper, ResearchReport
from app.agent.ollama_client import OllamaClient
from app.agent.planner import ResearchPlanner
from app.agent.synthesizer import ReportSynthesizer
from app.retrieval.search import SearchCoordinator
from app.retrieval.deduplication import deduplicate_papers
from app.retrieval.ranking import rank_papers
from app.evidence.claims import ClaimExtractor
from app.evidence.evidence import EvidenceManager
from app.evidence.contradictions import ContradictionAnalyzer
from app.verification.bibliography import BibliographicVerifier

logger = logging.getLogger(__name__)


class ResearcherAgent:
    def __init__(
        self,
        ollama_client: OllamaClient | None = None,
        search_coordinator: SearchCoordinator | None = None,
        progress_callback: Callable[[str], None] | None = None,
        verify_bibliography: bool = True,
    ):
        self.ollama_client = ollama_client or OllamaClient()
        self.search_coordinator = search_coordinator or SearchCoordinator()
        self.planner = ResearchPlanner(self.ollama_client)
        self.claim_extractor = ClaimExtractor(self.ollama_client)
        self.evidence_manager = EvidenceManager()
        self.contradiction_analyzer = ContradictionAnalyzer(self.ollama_client)
        self.verifier = BibliographicVerifier(verify_remote=verify_bibliography)
        self.synthesizer = ReportSynthesizer(self.ollama_client)
        self.progress_callback = progress_callback or (lambda msg: None)

    def log_progress(self, msg: str) -> None:
        logger.info(msg)
        self.progress_callback(msg)

    def run(
        self,
        question: str,
        max_iterations: int | None = None,
        max_papers: int | None = None,
    ) -> ResearchReport:
        limit_iterations = config.MAX_RESEARCH_ITERATIONS if max_iterations is None else max_iterations
        limit_papers = config.MAX_PAPERS_TOTAL if max_papers is None else max_papers
        if limit_iterations < 1 or limit_papers < 1:
            raise ValueError("max_iterations and max_papers must both be at least 1")

        self.log_progress("Phase 1/6: Understanding research entities and generating structured plan...")
        plan = self.planner.create_plan(question)
        self.log_progress(f"Understood entities: {', '.join(plan.entities)}")
        if plan.stripped_instructions:
            self.log_progress(f"Stripped output instructions: {', '.join(plan.stripped_instructions)}")
        self.log_progress(f"Plan formulated with {len(plan.search_queries)} planned queries.")

        self.log_progress("Phase 2/6: Executing multi-pass academic source searches...")
        all_raw_papers: list[Paper] = []
        executed_queries: set[str] = set()
        iteration = 0
        for sq in plan.search_queries:
            if iteration >= limit_iterations:
                self.log_progress(f"Reached maximum iteration limit ({limit_iterations}). Halting search passes.")
                break
            norm_q = sq.query.strip().lower()
            if norm_q in executed_queries:
                continue
            executed_queries.add(norm_q)
            iteration += 1
            self.log_progress(f"  [Pass {sq.pass_type.value.upper()}] Querying: '{sq.query}'...")
            pass_results = self.search_coordinator.search_query(sq)
            for paper in pass_results:
                paper.matched_passes = list(dict.fromkeys([*paper.matched_passes, sq.pass_type.value]))
                if sq.entity:
                    paper.matched_entities = list(dict.fromkeys([*paper.matched_entities, sq.entity]))
            all_raw_papers.extend(pass_results)
            if len(all_raw_papers) >= limit_papers * 2:
                self.log_progress("Search candidate saturation threshold reached; terminating additional queries.")
                break
        self.log_progress(f"Retrieved {len(all_raw_papers)} raw paper records across sources.")

        self.log_progress("Phase 3/6: Performing deterministic paper deduplication...")
        unique_papers = deduplicate_papers(all_raw_papers)
        self.log_progress(f"Deduplicated to {len(unique_papers)} unique academic paper records.")

        self.log_progress("Phase 4/6: Ranking papers using extracted entity vocabulary...")
        ranked_papers = rank_papers(
            unique_papers,
            query_text=self.planner.last_cleaned_question or " ".join(plan.entities),
            target_concept=" ".join(plan.entities),
            concept_vocabulary=plan.entities,
            assign_ids=True,
            enforce_concept_floor=True,
        )
        selected_papers = ranked_papers[:limit_papers]
        self.log_progress(f"Selected top {len(selected_papers)} relevant papers; concept floor enforced.")

        self.log_progress("Phase 5/6: Extracting claims, contradictions, and bibliography verification...")
        self.evidence_manager.register_papers(selected_papers)
        claims = self.claim_extractor.extract_claims(selected_papers, max_papers=15)
        evidence_records = self.evidence_manager.build_evidence_records(claims)
        contradictions = self.contradiction_analyzer.analyze_contradictions(claims, selected_papers)
        verifications = self.verifier.verify_papers(selected_papers, max_papers=15)
        research_gaps = self.synthesizer.detect_research_gaps(selected_papers, claims)

        self.log_progress("Phase 6/6: Synthesizing final structured academic report...")
        report = self.synthesizer.synthesize_report(
            plan=plan,
            papers=selected_papers,
            claims=claims,
            evidence_records=evidence_records,
            contradictions=contradictions,
            gaps=research_gaps,
            verifications=verifications,
        )
        self.log_progress("Academic research process complete.")
        return report
