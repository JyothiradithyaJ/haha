"""OpenAlex academic literature adapter."""
from __future__ import annotations

import logging
from typing import Any
import httpx
from app.models.schemas import Paper, QualityTier
from app.sources.base import AcademicSource
from app.config import config

logger = logging.getLogger(__name__)


def reconstruct_inverted_index(inv_index: dict[str, list[int]] | None) -> str | None:
    """Reconstruct plain abstract text from OpenAlex inverted index."""
    if not inv_index:
        return None
    pos_map: dict[int, str] = {}
    for word, positions in inv_index.items():
        for pos in positions:
            pos_map[pos] = word
    if not pos_map:
        return None
    sorted_positions = sorted(pos_map.keys())
    return " ".join(pos_map[p] for p in sorted_positions)


class OpenAlexSource(AcademicSource):
    """Adapter for the OpenAlex Works API."""

    name: str = "openalex"
    default_tier: QualityTier = QualityTier.TIER_2
    BASE_URL: str = "https://api.openalex.org/works"

    def _get_headers(self) -> dict[str, str]:
        headers = {"User-Agent": "AcademicResearchAgent/1.0 (academic-research-bot)"}
        if config.OPENALEX_EMAIL:
            headers["User-Agent"] += f" (mailto:{config.OPENALEX_EMAIL})"
        return headers

    def search(
        self,
        query: str,
        limit: int = 10,
        year_start: int | None = None,
        year_end: int | None = None,
    ) -> list[Paper]:
        params: dict[str, Any] = {
            "search": query,
            "per-page": min(limit, 50),
        }
        filters = []
        if year_start and year_end:
            filters.append(f"publication_year:{year_start}-{year_end}")
        elif year_start:
            filters.append(f"from_publication_date:{year_start}-01-01")
        elif year_end:
            filters.append(f"to_publication_date:{year_end}-12-31")

        if filters:
            params["filter"] = ",".join(filters)

        try:
            with httpx.Client(timeout=self.timeout, headers=self._get_headers()) as client:
                resp = client.get(self.BASE_URL, params=params)
                if resp.status_code != 200:
                    logger.warning(f"OpenAlex returned status {resp.status_code} for query: {query}")
                    return []
                data = resp.json()
        except Exception as e:
            logger.warning(f"OpenAlex query error: {e}")
            return []

        results: list[Paper] = []
        for item in data.get("results", []):
            paper = self._parse_work(item)
            if paper:
                results.append(paper)
        return results

    def get_paper(self, identifier: str) -> Paper | None:
        url = f"{self.BASE_URL}/{identifier}"
        try:
            with httpx.Client(timeout=self.timeout, headers=self._get_headers()) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    return None
                return self._parse_work(resp.json())
        except Exception:
            return None

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5.0, headers=self._get_headers()) as client:
                resp = client.get(self.BASE_URL, params={"per-page": 1})
                return resp.status_code == 200
        except Exception:
            return False

    def _parse_work(self, item: dict[str, Any]) -> Paper | None:
        title = item.get("title")
        if not title:
            return None

        authors: list[str] = []
        for authorship in item.get("authorships", []):
            author_obj = authorship.get("author", {})
            name = author_obj.get("display_name")
            if name:
                authors.append(name)

        year = item.get("publication_year")
        doi = item.get("doi")
        openalex_id = item.get("id")

        primary_loc = item.get("primary_location") or {}
        source_obj = primary_loc.get("source") or {}
        venue = source_obj.get("display_name")
        pdf_url = primary_loc.get("pdf_url")
        url = primary_loc.get("landing_page_url") or doi or openalex_id

        # Abstract reconstruction
        abstract = reconstruct_inverted_index(item.get("abstract_inverted_index"))

        citation_count = item.get("cited_by_count")
        publication_type = item.get("type")
        is_oa = item.get("open_access", {}).get("is_oa")

        return self.build_paper(
            title=title,
            authors=authors,
            year=year,
            venue=venue,
            abstract=abstract,
            doi=doi,
            openalex_id=openalex_id,
            url=url,
            pdf_url=pdf_url,
            citation_count=citation_count,
            publication_type=publication_type,
            is_open_access=is_oa,
        )

