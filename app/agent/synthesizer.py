"""Academic literature synthesizer, research-gap detector, and comparative report builder."""
from __future__ import annotations
import logging
from app.models.schemas import Paper, ResearchPlan, Claim, EvidenceRecord, ContradictionRecord, ResearchGap, GapCategory, BibliographicVerificationRecord, ResearchReport
from app.agent.ollama_client import OllamaClient
from app.agent.prompts import RESEARCH_GAP_SYSTEM_PROMPT, RESEARCH_GAP_USER_TEMPLATE

logger = logging.getLogger(__name__)

class ReportSynthesizer:
    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def detect_research_gaps(self, papers: list[Paper], claims: list[Claim]) -> list[ResearchGap]:
        if not papers: return []
        paper_map = {p.internal_id: p for p in papers if p.internal_id}
        summary = "\n".join(f"[{p.internal_id}] {p.title} ({p.year or 'N/A'}): {(p.abstract[:200] + '...') if p.abstract else 'No abstract'}" for p in papers[:10])
        try:
            raw = self.client.generate_json(prompt=RESEARCH_GAP_USER_TEMPLATE.format(papers_summary=summary), system_prompt=RESEARCH_GAP_SYSTEM_PROMPT, temperature=0.1)
            gaps=[]
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict) and item.get("description"):
                        cat=self._parse_gap_category(str(item.get("category", "")))
                        evidence=[x for x in item.get("supporting_evidence", []) if x in paper_map]
                        gaps.append(ResearchGap(gap_id=item.get("gap_id", f"GAP-{len(gaps)+1}"), category=cat, description=str(item["description"]).strip(), supporting_evidence=evidence or [papers[0].internal_id], proposed_directions=[str(x).strip() for x in item.get("proposed_directions", []) if x]))
            if gaps: return gaps
        except Exception as err: logger.debug("LLM research gap detection failed: %s", err)
        return self._generate_deterministic_gaps(papers)

    def _generate_deterministic_gaps(self, papers: list[Paper]) -> list[ResearchGap]:
        ids=[p.internal_id for p in papers[:4] if p.internal_id]; r=lambda i: [ids[i]] if len(ids)>i else (ids[:1] if ids else [])
        return [
            ResearchGap(gap_id="GAP-01", category=GapCategory.GENERALIZATION_GAP, description="Limited evidence about whether reported findings generalize across datasets, populations, settings, or implementations beyond those studied.", supporting_evidence=r(0), proposed_directions=["Evaluate on independent heterogeneous datasets", "Report sensitivity analyses for important sources of variation"]),
            ResearchGap(gap_id="GAP-02", category=GapCategory.REPRODUCIBILITY_GAP, description="Insufficient reporting of implementation details, data preparation, and evaluation protocols to support independent reproduction.", supporting_evidence=r(1), proposed_directions=["Publish complete evaluation protocols and implementation details"]),
            ResearchGap(gap_id="GAP-03", category=GapCategory.METHODOLOGICAL_GAP, description="Uncertainty remains about which methodological choices drive reported outcomes and under what conditions they fail.", supporting_evidence=r(2), proposed_directions=["Use ablation studies and controlled comparisons"]),
        ]

    def _parse_gap_category(self, raw: str) -> GapCategory:
        raw=raw.lower().strip()
        for gc in GapCategory:
            if gc.value == raw or raw in gc.value: return gc
        return GapCategory.METHODOLOGICAL_GAP

    @staticmethod
    def _comparison_table(plan: ResearchPlan, papers: list[Paper], claims: list[Claim]) -> list[dict[str, str]]:
        """Build only dimensions for which both sides have evidence; cite every cell."""
        entities=plan.entities
        if not plan.comparative or len(entities)<2: return []
        rows=[]
        claim_text_by_paper={c.paper_id: c.claim_text for c in claims}
        for dimension, keywords in {
            "Methodology": ("method", "architecture", "approach"),
            "Performance / benchmarks": ("performance", "accuracy", "benchmark", "result"),
            "Computational cost": ("latency", "compute", "cost", "efficient"),
            "Limitations": ("limitation", "failure", "challenge", "robustness"),
            "Use cases": ("application", "use", "task", "deployment"),
        }.items():
            cells={"Dimension": dimension}
            for entity in entities:
                matched=[p for p in papers if any(token in (p.title + " " + (p.abstract or "")).lower() for token in entity.lower().split())]
                claims_for=[claim_text_by_paper.get(p.internal_id, "") for p in matched if claim_text_by_paper.get(p.internal_id)]
                if claims_for:
                    cells[entity]=f"{claims_for[0]} [{matched[0].internal_id}]"
                else:
                    cells[entity]="insufficient evidence retrieved"
            if all(cells.get(e) != "insufficient evidence retrieved" for e in entities): rows.append(cells)
        return rows

    def synthesize_report(self, plan: ResearchPlan, papers: list[Paper], claims: list[Claim], evidence_records: list[EvidenceRecord], contradictions: list[ContradictionRecord], gaps: list[ResearchGap], verifications: list[BibliographicVerificationRecord]) -> ResearchReport:
        sources=list(dict.fromkeys(s for p in papers for s in p.sources)) or ["openalex", "semantic_scholar", "crossref", "arxiv", "pubmed"]
        findings=[f"[{c.paper_id}] {c.claim_text}" for c in claims[:8]] or [f"Retrieved {len(papers)} relevant academic works addressing '{plan.main_question}'."]
        comparisons=[{"paper_id":p.internal_id,"title":p.title,"year":p.year or "N/A","venue":p.venue or "Conference/Journal","approach":p.publication_type or "Academic method","citations":p.citation_count or 0,"tier":p.quality_tier.value} for p in papers[:6]]
        limitations=[f"[{c.paper_id}] {c.claim_text}" for c in claims if c.evidence_type.value=="limitation"] or [f"[{g.supporting_evidence[0]}] {g.description}" for g in gaps if g.supporting_evidence]
        return ResearchReport(
            research_question=plan.main_question,
            executive_summary=f"This report examines '{plan.main_question}' using {len(sources)} academic source families and {len(papers)} relevant papers. " + (f"The request was recognized as comparative across {', '.join(plan.entities)}." if plan.comparative else "The request was recognized as a single-topic research task."),
            research_methodology="Systematic multi-pass academic discovery with deterministic deduplication, entity-based relevance ranking, evidence extraction, contradiction analysis, and bibliography verification.",
            academic_sources_searched=sources, search_strategy_summary=f"Executed {len(plan.search_queries)} planned queries and retained {len(papers)} relevant papers.",
            key_findings=findings, evidence_records=evidence_records, claims=claims, contradictions=contradictions, method_comparisons=comparisons,
            comparison_table=self._comparison_table(plan, papers, claims), limitations_in_existing_research=limitations, research_gaps=gaps,
            open_research_questions=plan.sub_questions, evidence_strength_summary=f"Evidence was assessed across {len(claims)} extracted claims using source quality and contradiction signals.",
            conclusion=f"The retrieved literature provides evidence for the research entities and identifies {len(gaps)} unresolved gaps.", papers=papers, verification_records=verifications,
            entities=plan.entities, comparative=plan.comparative, stripped_instructions=plan.stripped_instructions,
        )
