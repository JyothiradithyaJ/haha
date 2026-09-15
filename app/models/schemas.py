"""Core Pydantic models for papers, searches, claims, contradictions, and reports."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class Author(BaseModel):
    """Author metadata."""
    name: str
    affiliation: str | None = None
    orcid: str | None = None


class QualityTier(str, Enum):
    """Source quality classification tiers."""
    TIER_1 = "TIER_1"  # Peer-reviewed original research, official journal/conf, DOI/PubMed records
    TIER_2 = "TIER_2"  # OpenAlex, Semantic Scholar, Crossref, CORE, arXiv
    TIER_3 = "TIER_3"  # Institutional repositories, technical reports
    TIER_4 = "TIER_4"  # Generic web/other (disabled by default)


class Paper(BaseModel):
    """Normalized internal representation of an academic paper."""
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
    sources: list[str] = Field(default_factory=list, description="List of source adapters that found this paper")
    citation_count: int | None = None
    publication_type: str | None = None
    is_open_access: bool | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quality_tier: QualityTier = QualityTier.TIER_2

    # Ranking & relevance metadata
    relevance_score: float = 0.0
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    matched_passes: list[str] = Field(default_factory=list)


class PassType(str, Enum):
    """Search pass categories."""
    PASS_A_BROAD = "broad"
    PASS_B_EXPANSION = "expansion"
    PASS_C_SUPPORTING = "supporting"
    PASS_D_CONTRADICTION = "contradiction"
    PASS_E_RECENT = "recent"
    PASS_F_FOUNDATIONAL = "foundational"


class SearchQuery(BaseModel):
    """Structured query for academic sources."""
    query: str
    pass_type: PassType
    target_concept: str
    year_start: int | None = None
    year_end: int | None = None
    rationale: str = ""


class SearchResult(BaseModel):
    """Results from a search query across sources."""
    query: SearchQuery
    papers: list[Paper] = Field(default_factory=list)
    total_found: int = 0
    source_name: str = ""


class ResearchObjective(BaseModel):
    """Specific research goal or sub-objective."""
    objective_id: str
    description: str


class ResearchPlan(BaseModel):
    """Structured academic research plan created by the planner."""
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
    """Categorization of evidence supporting a claim."""
    EMPIRICAL_RESULT = "empirical result"
    METHODOLOGICAL_CLAIM = "methodological claim"
    THEORETICAL_CLAIM = "theoretical claim"
    LIMITATION = "limitation"
    COMPARISON = "comparison"
    SURVEY_FINDING = "survey finding"
    DATASET_OBSERVATION = "dataset observation"


class EvidenceStrength(str, Enum):
    """Heuristic assessment of evidence strength."""
    VERY_STRONG = "VERY STRONG"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    INSUFFICIENT = "INSUFFICIENT"


class Claim(BaseModel):
    """Substantive scientific claim extracted from retrieved literature."""
    claim_id: str = Field(description="Unique claim identifier, e.g. C01")
    claim_text: str
    paper_id: str = Field(description="Primary paper ID, e.g. P01")
    evidence_type: EvidenceType
    evidence_strength: EvidenceStrength = EvidenceStrength.MODERATE
    supporting_sources: list[str] = Field(default_factory=list, description="Paper IDs supporting this claim")
    contradicting_sources: list[str] = Field(default_factory=list, description="Paper IDs questioning/contradicting")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    notes: str = ""


class EvidenceRecord(BaseModel):
    """Evidence mapping record connecting claims to papers and excerpts."""
    evidence_id: str
    claim_id: str
    paper_id: str
    quote_or_excerpt: str
    evidence_type: EvidenceType
    strength: EvidenceStrength
    source_adapter: str


class ContradictionRecord(BaseModel):
    """Record of scientific disagreements, negative findings, or conflicting results."""
    claim: str
    supporting_papers: list[str] = Field(default_factory=list, description="Paper IDs e.g. ['P01', 'P03']")
    contradicting_papers: list[str] = Field(default_factory=list, description="Paper IDs e.g. ['P05']")
    overall_assessment: str
    evidence_discrepancy: str = ""
    notes: str = ""


class GapCategory(str, Enum):
    """Classification of identified unresolved research gaps."""
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
    """Categorized unresolved academic research gap backed by literature."""
    gap_id: str
    category: GapCategory
    description: str
    supporting_evidence: list[str] = Field(default_factory=list, description="Paper IDs highlighting this gap")
    proposed_directions: list[str] = Field(default_factory=list)


class BibliographicVerificationRecord(BaseModel):
    """Verification record cross-checking a paper across independent databases."""
    paper_id: str
    doi: str | None = None
    title_matches: bool = True
    verified_sources: list[str] = Field(default_factory=list)
    discrepancies: list[str] = Field(default_factory=list)
    confidence: float = 1.0


class ResearchReport(BaseModel):
    """Complete 16-section structured academic research report."""
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

