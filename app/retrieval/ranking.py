"""Transparent multi-factor relevance ranking for academic papers."""
from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from app.models.schemas import Paper, QualityTier


def _tokenize(text: str) -> set[str]:
    """Extract lowercase alphabetic tokens of length >= 3."""
    if not text:
        return set()
    tokens = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    # Exclude basic stopwords
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "using", "based",
        "method", "paper", "study", "approach", "results", "which", "are", "were"
    }
    return {t for t in tokens if t not in stopwords}


def compute_overlap(tokens: set[str], text: str | None) -> float:
    """Compute normalized token coverage in text."""
    if not tokens or not text:
        return 0.0
    text_tokens = _tokenize(text)
    if not text_tokens:
        return 0.0
    overlap = len(tokens.intersection(text_tokens))
    return overlap / len(tokens)


def compute_recency_score(
    year: int | None,
    recent_priority: bool = False,
    foundational_priority: bool = False,
    citation_count: int | None = None,
) -> float:
    """Compute recency vs foundational score based on publication year."""
    current_year = datetime.now(timezone.utc).year
    if year is None:
        return 0.4

    if recent_priority:
        # Prioritize 2024-2026
        if year >= current_year - 2:
            return 1.0
        elif year >= current_year - 4:
            return 0.7
        elif year >= current_year - 8:
            return 0.4
        else:
            return 0.2

    if foundational_priority:
        # Prioritize older well-cited papers
        citations = citation_count or 0
        if year <= current_year - 5 and citations >= 50:
            return 1.0
        elif year <= current_year - 3 and citations >= 20:
            return 0.8
        elif citations >= 10:
            return 0.6
        else:
            return 0.4

    # Balanced default
    age = max(0, current_year - year)
    if age <= 3:
        return 0.9
    elif age <= 6:
        return 0.75
    elif age <= 10:
        return 0.6
    else:
        return 0.45


def compute_citation_score(citation_count: int | None) -> float:
    """Log-scale citation score capped at ~1000 citations."""
    if not citation_count or citation_count <= 0:
        return 0.1
    # log10(1) = 0, log10(1001) ~ 3.0
    return min(1.0, math.log10(citation_count + 1) / 3.0)


def compute_quality_score(tier: QualityTier) -> float:
    """Numeric score for peer-reviewed / official status."""
    tiers = {
        QualityTier.TIER_1: 1.0,
        QualityTier.TIER_2: 0.8,
        QualityTier.TIER_3: 0.5,
        QualityTier.TIER_4: 0.2,
    }
    return tiers.get(tier, 0.7)


def rank_papers(
    papers: list[Paper],
    query_text: str,
    target_concept: str = "",
    recent_priority: bool = False,
    foundational_priority: bool = False,
    assign_ids: bool = True,
) -> list[Paper]:
    """Rank papers using transparent multi-factor scoring.

    Weights:
    - Title match: 0.35
    - Abstract match: 0.25
    - Concept match: 0.15
    - Recency / Foundational: 0.10
    - Quality tier: 0.10
    - Citation count: 0.05
    """
    query_tokens = _tokenize(query_text)
    concept_tokens = _tokenize(target_concept)

    for paper in papers:
        # 1. Title match
        title_score = compute_overlap(query_tokens, paper.title)

        # 2. Abstract match
        abstract_score = compute_overlap(query_tokens, paper.abstract)

        # 3. Concept match (if specified)
        if concept_tokens:
            concept_in_title = compute_overlap(concept_tokens, paper.title)
            concept_in_abstract = compute_overlap(concept_tokens, paper.abstract)
            concept_score = max(concept_in_title, concept_in_abstract)
        else:
            concept_score = 0.5

        # 4. Recency score
        recency_score = compute_recency_score(
            paper.year,
            recent_priority=recent_priority,
            foundational_priority=foundational_priority,
            citation_count=paper.citation_count,
        )

        # 5. Quality tier
        quality_score = compute_quality_score(paper.quality_tier)

        # 6. Citation score
        citation_score = compute_citation_score(paper.citation_count)

        # Composite score
        total_score = (
            0.35 * title_score
            + 0.25 * abstract_score
            + 0.15 * concept_score
            + 0.10 * recency_score
            + 0.10 * quality_score
            + 0.05 * citation_score
        )

        paper.relevance_score = round(total_score, 4)
        paper.score_breakdown = {
            "title_match": round(title_score, 3),
            "abstract_match": round(abstract_score, 3),
            "concept_match": round(concept_score, 3),
            "recency": round(recency_score, 3),
            "quality_tier": round(quality_score, 3),
            "citations": round(citation_score, 3),
        }

    # Sort descending by relevance score
    ranked = sorted(papers, key=lambda p: p.relevance_score, reverse=True)

    if assign_ids:
        for idx, p in enumerate(ranked, start=1):
            p.internal_id = f"P{idx:02d}"

    return ranked

