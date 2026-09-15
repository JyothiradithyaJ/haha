"""Deterministic academic paper deduplication and metadata fusion."""
from __future__ import annotations

import re
from app.models.schemas import Paper, QualityTier
from app.sources.base import normalize_doi, normalize_arxiv_id, normalize_title


def _extract_first_author_surname(authors: list[str]) -> str:
    """Extract lowercase normalized surname of the first author."""
    if not authors:
        return ""
    first = authors[0].strip()
    # If formatted as "Last, First"
    if "," in first:
        return first.split(",")[0].strip().lower()
    # If formatted as "First Last"
    parts = first.split()
    return parts[-1].strip().lower() if parts else ""


def _tier_rank(tier: QualityTier) -> int:
    """Higher rank is higher quality."""
    ranks = {
        QualityTier.TIER_1: 4,
        QualityTier.TIER_2: 3,
        QualityTier.TIER_3: 2,
        QualityTier.TIER_4: 1,
    }
    return ranks.get(tier, 0)


def merge_paper_records(primary: Paper, incoming: Paper) -> Paper:
    """Deterministic merge of two duplicate paper records to preserve all metadata."""
    # Combine sources
    combined_sources = list(dict.fromkeys(primary.sources + incoming.sources))
    
    # Combined matched passes
    combined_passes = list(dict.fromkeys(primary.matched_passes + incoming.matched_passes))

    # Abstract: choose longer/more informative
    abs1 = primary.abstract or ""
    abs2 = incoming.abstract or ""
    best_abstract = abs1 if len(abs1) >= len(abs2) else abs2

    # Authors: choose longer list or non-empty
    best_authors = primary.authors if len(primary.authors) >= len(incoming.authors) else incoming.authors

    # Citations: max non-null
    c1 = primary.citation_count
    c2 = incoming.citation_count
    best_citations = max(c for c in [c1, c2] if c is not None) if (c1 is not None or c2 is not None) else None

    # Quality tier: keep highest quality
    best_tier = primary.quality_tier if _tier_rank(primary.quality_tier) >= _tier_rank(incoming.quality_tier) else incoming.quality_tier

    # Open access
    best_oa = (primary.is_open_access is True) or (incoming.is_open_access is True)

    return Paper(
        internal_id=primary.internal_id or incoming.internal_id,
        title=primary.title if len(primary.title) >= len(incoming.title) else incoming.title,
        normalized_title=primary.normalized_title or incoming.normalized_title or normalize_title(primary.title),
        authors=best_authors,
        year=primary.year or incoming.year,
        venue=primary.venue or incoming.venue,
        abstract=best_abstract if best_abstract else None,
        doi=primary.doi or incoming.doi,
        arxiv_id=primary.arxiv_id or incoming.arxiv_id,
        pubmed_id=primary.pubmed_id or incoming.pubmed_id,
        semantic_scholar_id=primary.semantic_scholar_id or incoming.semantic_scholar_id,
        openalex_id=primary.openalex_id or incoming.openalex_id,
        url=primary.url or incoming.url,
        pdf_url=primary.pdf_url or incoming.pdf_url,
        sources=combined_sources,
        citation_count=best_citations,
        publication_type=primary.publication_type or incoming.publication_type,
        is_open_access=best_oa,
        retrieved_at=min(primary.retrieved_at, incoming.retrieved_at),
        quality_tier=best_tier,
        relevance_score=max(primary.relevance_score, incoming.relevance_score),
        matched_passes=combined_passes,
    )


def deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    """Deterministic deduplication with strict 6-tier identity matching priority:

    1. DOI
    2. PubMed ID
    3. arXiv ID
    4. Semantic Scholar ID
    5. OpenAlex ID
    6. Normalized title + First Author surname + Year
    """
    unique_papers: list[Paper] = []
    
    # Fast lookup indexes
    doi_map: dict[str, int] = {}
    pubmed_map: dict[str, int] = {}
    arxiv_map: dict[str, int] = {}
    s2_map: dict[str, int] = {}
    openalex_map: dict[str, int] = {}
    title_author_year_map: dict[tuple[str, str, int | None], int] = {}
    title_only_map: dict[str, int] = {}  # Exact normalized title fallback if length >= 20

    for incoming in papers:
        # Normalize fields
        doi = normalize_doi(incoming.doi)
        arxiv = normalize_arxiv_id(incoming.arxiv_id)
        pmid = incoming.pubmed_id.strip() if incoming.pubmed_id else None
        s2_id = incoming.semantic_scholar_id.strip() if incoming.semantic_scholar_id else None
        oa_id = incoming.openalex_id.strip() if incoming.openalex_id else None
        norm_title = normalize_title(incoming.title)
        first_author = _extract_first_author_surname(incoming.authors)
        year = incoming.year

        incoming.doi = doi
        incoming.arxiv_id = arxiv
        incoming.normalized_title = norm_title

        match_idx: int | None = None

        # 1. DOI
        if doi and doi in doi_map:
            match_idx = doi_map[doi]
        # 2. PubMed ID
        elif pmid and pmid in pubmed_map:
            match_idx = pubmed_map[pmid]
        # 3. arXiv ID
        elif arxiv and arxiv in arxiv_map:
            match_idx = arxiv_map[arxiv]
        # 4. Semantic Scholar ID
        elif s2_id and s2_id in s2_map:
            match_idx = s2_map[s2_id]
        # 5. OpenAlex ID
        elif oa_id and oa_id in openalex_map:
            match_idx = openalex_map[oa_id]
        # 6. Normalized Title + Author + Year
        elif norm_title and (first_author, year) != ("", None):
            key = (norm_title, first_author, year)
            if key in title_author_year_map:
                match_idx = title_author_year_map[key]
        # 7. Exact Title fallback if long enough (>= 25 chars) and author/year missing
        elif norm_title and len(norm_title) >= 25 and norm_title in title_only_map:
            match_idx = title_only_map[norm_title]

        if match_idx is not None:
            # Merge existing record
            existing = unique_papers[match_idx]
            merged = merge_paper_records(existing, incoming)
            unique_papers[match_idx] = merged
            target_idx = match_idx
        else:
            # New unique record
            target_idx = len(unique_papers)
            unique_papers.append(incoming)

        # Update index mappings for target_idx
        if doi:
            doi_map[doi] = target_idx
        if pmid:
            pubmed_map[pmid] = target_idx
        if arxiv:
            arxiv_map[arxiv] = target_idx
        if s2_id:
            s2_map[s2_id] = target_idx
        if oa_id:
            openalex_map[oa_id] = target_idx
        if norm_title:
            title_author_year_map[(norm_title, first_author, year)] = target_idx
            title_only_map[norm_title] = target_idx

    return unique_papers

