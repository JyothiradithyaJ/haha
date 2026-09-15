"""Transparent multi-factor relevance ranking for academic papers."""
from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from app.models.schemas import Paper, QualityTier


def _tokenize(text: str) -> set[str]:
    if not text:
        return set()
    tokens = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "using", "based",
        "method", "paper", "study", "approach", "results", "which", "are", "were",
        "what", "how", "different", "difference", "distinction", "table", "provide",
        "compare", "comparison", "explain", "summarize", "list",
    }
    return {t for t in tokens if t not in stopwords}


def _concept_tokens(concepts: str | list[str]) -> set[str]:
    values = [concepts] if isinstance(concepts, str) else concepts
    return set().union(*(_tokenize(value) for value in values)) if values else set()


def compute_overlap(tokens: set[str], text: str | None) -> float:
    if not tokens or not text:
        return 0.0
    text_tokens = _tokenize(text)
    if not text_tokens:
        return 0.0
    return len(tokens.intersection(text_tokens)) / len(tokens)


def compute_recency_score(year: int | None, recent_priority: bool = False, foundational_priority: bool = False, citation_count: int | None = None) -> float:
    current_year = datetime.now(timezone.utc).year
    if year is None:
        return 0.4
    if recent_priority:
        if year >= current_year - 2: return 1.0
        if year >= current_year - 4: return 0.7
        if year >= current_year - 8: return 0.4
        return 0.2
    if foundational_priority:
        citations = citation_count or 0
        if year <= current_year - 5 and citations >= 50: return 1.0
        if year <= current_year - 3 and citations >= 20: return 0.8
        if citations >= 10: return 0.6
        return 0.4
    age = max(0, current_year - year)
    if age <= 3: return 0.9
    if age <= 6: return 0.75
    if age <= 10: return 0.6
    return 0.45


def compute_citation_score(citation_count: int | None) -> float:
    if not citation_count or citation_count <= 0:
        return 0.1
    return min(1.0, math.log10(citation_count + 1) / 3.0)


def compute_quality_score(tier: QualityTier) -> float:
    return {
        QualityTier.TIER_1: 1.0,
        QualityTier.TIER_2: 0.8,
        QualityTier.TIER_3: 0.5,
        QualityTier.TIER_4: 0.2,
    }.get(tier, 0.7)


def rank_papers(
    papers: list[Paper],
    query_text: str,
    target_concept: str = "",
    recent_priority: bool = False,
    foundational_priority: bool = False,
    assign_ids: bool = True,
    concept_vocabulary: list[str] | None = None,
    enforce_concept_floor: bool = True,
) -> list[Paper]:
    """Rank papers with a configurable hard floor on substantive concept relevance."""
    query_tokens = _tokenize(query_text)
    concept_tokens = _concept_tokens(concept_vocabulary or target_concept)
    ranked_candidates: list[Paper] = []

    for paper in papers:
        title_score = compute_overlap(query_tokens, paper.title)
        abstract_score = compute_overlap(query_tokens, paper.abstract)
        if concept_tokens:
            concept_score = max(
                compute_overlap(concept_tokens, paper.title),
                compute_overlap(concept_tokens, paper.abstract),
            )
        else:
            concept_score = 0.0

        recency_score = compute_recency_score(paper.year, recent_priority, foundational_priority, paper.citation_count)
        quality_score = compute_quality_score(paper.quality_tier)
        citation_score = compute_citation_score(paper.citation_count)
        total_score = 0.35 * title_score + 0.25 * abstract_score + 0.15 * concept_score + 0.10 * recency_score + 0.10 * quality_score + 0.05 * citation_score

        paper.relevance_score = round(total_score, 4)
        paper.score_breakdown = {
            "title_match": round(title_score, 3),
            "abstract_match": round(abstract_score, 3),
            "concept_match": round(concept_score, 3),
            "recency": round(recency_score, 3),
            "quality_tier": round(quality_score, 3),
            "citations": round(citation_score, 3),
        }
        if concept_tokens and concept_score <= 0.0 and enforce_concept_floor:
            logger_message = f"Excluding off-topic paper from ranked set: {paper.title!r}"
            # Keep diagnostics in the score metadata without admitting the paper.
            paper.score_breakdown["excluded_by_concept_floor"] = 1.0
            continue
        ranked_candidates.append(paper)

    ranked = sorted(ranked_candidates, key=lambda p: p.relevance_score, reverse=True)
    if assign_ids:
        for idx, paper in enumerate(ranked, start=1):
            paper.internal_id = f"P{idx:02d}"
    return ranked
