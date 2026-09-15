"""Core Pydantic models for papers, searches, claims, contradictions, and reports."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class Author(BaseModel):
    name: str
    affiliation: str | None = None
    orcid: str | None = None


class QualityTier(str, Enum):
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"
    TIER_4 = "TIER_4"


class Paper(BaseModel):
    internal_id: str = Field(default="", description="Internal traceable ID like P01, P02")
    title: str
    normalized_title: str = ""
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    pubmed_id: str | None = None
    semantic_scholar_id: str | None = None
    openalex_id: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    sources: list[str] = Field(default_factory=list)
    citation_count: int | None = None
    publication_type: str | None = None
    is_open_access: bool | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quality_tier: QualityTier = QualityTier.TIER_2
    relevance_score: float = 0.0
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    matched_passes: list[str] = Field(default_factory=list)
    full_text_status: str = "not_attempted"  # available | unavailable | failed | not_attempted
    full_text_source: str | None = None
    full_text_error: str | None = None


class PassType(str, Enum):
    PASS_A_BROAD = "broad"
    PASS_B_EXPANSION = "expansion"
    PASS_C_SUPPORTING = "supporting"
    PASS_D_CONTRADICTION = "contradiction"
    PASS_E_RECENT = "recent"
    PASS_F_FOUNDATIONAL = "foundational"


class SearchQuery(BaseModel):
    query: str
    pass_type: PassType
    target_concept: str
    year_start: int | None = None
    year_end: int | None = None
    rationale: str = ""


class SearchResult(BaseModel):
    query: SearchQuery
    papers: list[Paper] = Field(default_factory=list)
    total_found: int = 0
    source_name: str = ""


class ResearchObjective(BaseModel):
    objective_id: str
    description: str


class ResearchPlan(BaseModel):
    main_question: str
    research_objectives: list[ResearchObjective] = Field(default_factory=list)
    sub_questions: list[str] = Field(default_factory=list)
    important_concepts: list[str] = Field(default_factory=list)
    synonyms: dict[str, list[str]] = Field(default_factory=dict)
    related_terminology: list[str] = Field(default_factory=list)
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    search_queries: list[SearchQuery] = Field(default_factory=list)
    recent_literature_strategy: str = ""
    foundational_literature_strategy: str = ""
    supporting_evidence_strategy: str = ""
    contradiction_falsification_strategy: str = ""


class EvidenceType(str, Enum):
    EMPIRICAL_RESULT = "empirical result"
    METHODOLOGICAL_CLAIM = "methodological claim"
    THEORETICAL_CLAIM = "theoretical claim"
    LIMITATION = "limitation"
    COMPARISON = "comparison"
    SURVEY_FINDING = "survey finding"
    DATASET_OBSERVATION = "dataset observation"


class EvidenceStrength(str, Enum):
    VERY_STRONG = "VERY STRONG"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    INSUFFICIENT = "INSUFFICIENT"


class Claim(BaseModel):
    claim_id: str
    claim_text: str
    paper_id: str
    evidence_type: EvidenceType
    evidence_strength: EvidenceStrength = EvidenceStrength.MODERATE
    supporting_sources: list[str] = Field(default_factory=list)
    contradicting_sources: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    notes: str = ""
    evidence_id: str | None = None
    section: str = "abstract"
    page_start: int | None = None
    page_end: int | None = None
    source_excerpt: str | None = None
    source_url: str | None = None


class EvidenceRecord(BaseModel):
    evidence_id: str
    claim_id: str
    paper_id: str
    quote_or_excerpt: str
    evidence_type: EvidenceType
    strength: EvidenceStrength
    source_adapter: str
    section: str = "abstract"
    page_start: int | None = None
    page_end: int | None = None
    source_url: str | None = None
    full_text_grounded: bool = False


class ContradictionRecord(BaseModel):
    claim: str
    supporting_papers: list[str] = Field(default_factory=list)
    contradicting_papers: list[str] = Field(default_factory=list)
    overall_assessment: str
    evidence_discrepancy: str = ""
    notes: str = ""


class GapCategory(str, Enum):
    DATASET_GAP = "dataset gap"
    METHODOLOGICAL_GAP = "methodological gap"
    EVALUATION_GAP = "evaluation gap"
    GENERALIZATION_GAP = "generalization gap"
    ROBUSTNESS_GAP = "robustness gap"
    REPRODUCIBILITY_GAP = "reproducibility gap"
    DEPLOYMENT_GAP = "deployment gap"
    COMPUTATIONAL_EFFICIENCY_GAP = "computational-efficiency gap"
    THEORETICAL_GAP = "theoretical gap"
    DOMAIN_GAP = "domain gap"
    MULTIMODAL_GAP = "multimodal gap"
    BENCHMARK_GAP = "benchmark gap"
    EXPLAINABILITY_GAP = "explainability gap"


class ResearchGap(BaseModel):
    gap_id: str
    category: GapCategory
    description: str
    supporting_evidence: list[str] = Field(default_factory=list)
    proposed_directions: list[str] = Field(default_factory=list)


class BibliographicVerificationRecord(BaseModel):
    paper_id: str
    doi: str | None = None
    title_matches: bool = True
    verified_sources: list[str] = Field(default_factory=list)
    discrepancies: list[str] = Field(default_factory=list)
    confidence: float = 1.0


class ResearchReport(BaseModel):
    research_question: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executive_summary: str
    research_methodology: str
    academic_sources_searched: list[str]
    search_strategy_summary: str
    key_findings: list[str]
    evidence_records: list[EvidenceRecord] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    contradictions: list[ContradictionRecord] = Field(default_factory=list)
    method_comparisons: list[dict[str, Any]] = Field(default_factory=list)
    limitations_in_existing_research: list[str] = Field(default_factory=list)
    research_gaps: list[ResearchGap] = Field(default_factory=list)
    open_research_questions: list[str] = Field(default_factory=list)
    evidence_strength_summary: str
    conclusion: str
    papers: list[Paper] = Field(default_factory=list)
    verification_records: list[BibliographicVerificationRecord] = Field(default_factory=list)
