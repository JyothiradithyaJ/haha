"""Semantic Scholar API adapter."""
from __future__ import annotations

import logging
from typing import Any
import httpx
from app.models.schemas import Paper, QualityTier
from app.sources.base import AcademicSource
from app.config import config

logger = logging.getLogger(__name__)


class SemanticScholarSource(AcademicSource):
    """Adapter for Semantic Scholar Graph API."""

    name: str = "semantic_scholar"
    default_tier: QualityTier = QualityTier.TIER_2
    BASE_URL: str = "https://api.semanticscholar.org/graph/v1/paper"
    FIELDS: str = "paperId,title,abstract,year,venue,authors,externalIds,citationCount,isOpenAccess,openAccessPdf,url,publicationTypes"

    def _get_headers(self) -> dict[str, str]:
        headers = {"User-Agent": "AcademicResearchAgent/1.0"}
        if config.SEMANTIC_SCHOLAR_API_KEY:
            headers["x-api-key"] = config.SEMANTIC_SCHOLAR_API_KEY
        return headers

    def search(
        self,
        query: str,
        limit: int = 10,
        year_start: int | None = None,
        year_end: int | None = None,
    ) -> list[Paper]:
        params: dict[str, Any] = {
            "query": query,
            "limit": min(limit, 50),
            "fields": self.FIELDS,
        }
        if year_start and year_end:
            params["year"] = f"{year_start}-{year_end}"
        elif year_start:
            params["year"] = f"{year_start}-"
        elif year_end:
            params["year"] = f"-{year_end}"

        url = f"{self.BASE_URL}/search"
        try:
            with httpx.Client(timeout=self.timeout, headers=self._get_headers()) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 429:
                    logger.warning("Semantic Scholar rate limit hit (429).")
                    return []
                if resp.status_code != 200:
                    logger.warning(f"Semantic Scholar returned status {resp.status_code}")
                    return []
                data = resp.json()
        except Exception as e:
            logger.warning(f"Semantic Scholar search error: {e}")
            return []

        results: list[Paper] = []
        for item in data.get("data", []):
            paper = self._parse_item(item)
            if paper:
                results.append(paper)
        return results

    def get_paper(self, identifier: str) -> Paper | None:
        url = f"{self.BASE_URL}/{identifier}"
        try:
            with httpx.Client(timeout=self.timeout, headers=self._get_headers()) as client:
                resp = client.get(url, params={"fields": self.FIELDS})
                if resp.status_code != 200:
                    return None
                return self._parse_item(resp.json())
        except Exception:
            return None

    def health_check(self) -> bool:
        url = f"{self.BASE_URL}/search"
        try:
            with httpx.Client(timeout=5.0, headers=self._get_headers()) as client:
                resp = client.get(url, params={"query": "machine learning", "limit": 1})
                return resp.status_code == 200
        except Exception:
            return False

    def _parse_item(self, item: dict[str, Any]) -> Paper | None:
        title = item.get("title")
        if not title:
            return None

        authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
        year = item.get("year")
        venue = item.get("venue")
        abstract = item.get("abstract")

        ext_ids = item.get("externalIds") or {}
        doi = ext_ids.get("DOI")
        arxiv_id = ext_ids.get("ArXiv")
        pubmed_id = ext_ids.get("PubMed") or ext_ids.get("PubMedCentral")
        s2_id = item.get("paperId")

        url = item.get("url")
        pdf_url = (item.get("openAccessPdf") or {}).get("url")
        citation_count = item.get("citationCount")
        pub_types = item.get("publicationTypes")
        publication_type = pub_types[0] if pub_types else None
        is_oa = item.get("isOpenAccess")

        return self.build_paper(
            title=title,
            authors=authors,
            year=year,
            venue=venue,
            abstract=abstract,
            doi=doi,
            arxiv_id=arxiv_id,
            pubmed_id=pubmed_id,
            semantic_scholar_id=s2_id,
            url=url,
            pdf_url=pdf_url,
            citation_count=citation_count,
            publication_type=publication_type,
            is_open_access=is_oa,
        )

