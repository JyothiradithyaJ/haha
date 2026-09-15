"""Base abstraction for academic source clients."""
from __future__ import annotations

import abc
import re
from typing import Any
from app.models.schemas import Paper, QualityTier
from app.config import config


def normalize_doi(doi: str | None) -> str | None:
    """Deterministic DOI normalization (lowercase, stripped prefix)."""
    if not doi:
        return None
    cleaned = doi.strip().lower()
    cleaned = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", cleaned)
    cleaned = re.sub(r"^doi:\s*", "", cleaned)
    cleaned = cleaned.strip("/")
    return cleaned if cleaned else None


def normalize_arxiv_id(arxiv_id: str | None) -> str | None:
    """Deterministic arXiv ID normalization (strips prefix and version numbers)."""
    if not arxiv_id:
        return None
    cleaned = arxiv_id.strip()
    cleaned = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", cleaned)
    cleaned = re.sub(r"^arxiv:\s*", "", cleaned, flags=re.IGNORECASE)
    # Strip trailing .pdf
    cleaned = re.sub(r"\.pdf$", "", cleaned, flags=re.IGNORECASE)
    # Strip version suffix (e.g. 2104.08821v2 -> 2104.08821)
    cleaned = re.sub(r"v\d+$", "", cleaned)
    return cleaned.strip() if cleaned else None


def normalize_title(title: str | None) -> str:
    """Deterministic title normalization: lowercase, strip punctuation and excess whitespace."""
    if not title:
        return ""
    # Remove punctuation
    cleaned = re.sub(r"[^\w\s]", " ", title.lower())
    # Collapse multiple whitespaces
    cleaned = " ".join(cleaned.split())
    return cleaned


class AcademicSource(abc.ABC):
    """Abstract base class for academic literature sources."""

    name: str = "base_source"
    default_tier: QualityTier = QualityTier.TIER_2

    def __init__(self, timeout: float | None = None):
        self.timeout = timeout or config.SEARCH_TIMEOUT_SECONDS

    @abc.abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
        year_start: int | None = None,
        year_end: int | None = None,
    ) -> list[Paper]:
        """Search academic source and return normalized Paper records."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_paper(self, identifier: str) -> Paper | None:
        """Fetch a specific paper record by its native identifier or DOI."""
        raise NotImplementedError

    @abc.abstractmethod
    def health_check(self) -> bool:
        """Verify API connectivity and responsiveness."""
        raise NotImplementedError

    def build_paper(
        self,
        title: str,
        authors: list[str] | None = None,
        year: int | None = None,
        venue: str | None = None,
        abstract: str | None = None,
        doi: str | None = None,
        arxiv_id: str | None = None,
        pubmed_id: str | None = None,
        semantic_scholar_id: str | None = None,
        openalex_id: str | None = None,
        url: str | None = None,
        pdf_url: str | None = None,
        citation_count: int | None = None,
        publication_type: str | None = None,
        is_open_access: bool | None = None,
        quality_tier: QualityTier | None = None,
    ) -> Paper:
        """Helper to build a validated, normalized Paper model."""
        clean_title = title.strip()
        norm_title = normalize_title(clean_title)
        clean_doi = normalize_doi(doi)
        clean_arxiv = normalize_arxiv_id(arxiv_id)

        tier = quality_tier or self.default_tier
        # If paper has a peer-reviewed DOI or official venue, tier can be upgraded
        if clean_doi and tier == QualityTier.TIER_2:
            tier = QualityTier.TIER_1

        return Paper(
            title=clean_title,
            normalized_title=norm_title,
            authors=[a.strip() for a in (authors or []) if a and a.strip()],
            year=year,
            venue=venue.strip() if venue else None,
            abstract=abstract.strip() if abstract else None,
            doi=clean_doi,
            arxiv_id=clean_arxiv,
            pubmed_id=pubmed_id.strip() if pubmed_id else None,
            semantic_scholar_id=semantic_scholar_id.strip() if semantic_scholar_id else None,
            openalex_id=openalex_id.strip() if openalex_id else None,
            url=url.strip() if url else None,
            pdf_url=pdf_url.strip() if pdf_url else None,
            sources=[self.name],
            citation_count=citation_count,
            publication_type=publication_type,
            is_open_access=is_open_access,
            quality_tier=tier,
        )

