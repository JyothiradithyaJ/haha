"""Crossref metadata API adapter."""
from __future__ import annotations

import logging
import re
from typing import Any
import httpx
from app.models.schemas import Paper, QualityTier
from app.sources.base import AcademicSource
from app.config import config

logger = logging.getLogger(__name__)


def strip_jats_tags(text: str | None) -> str | None:
    """Remove JATS XML tags such as <jats:p> from Crossref abstracts."""
    if not text:
        return None
    cleaned = re.sub(r"<[^>]+>", " ", text)
    return " ".join(cleaned.split())


class CrossrefSource(AcademicSource):
    """Adapter for the official Crossref Works REST API."""

    name: str = "crossref"
    default_tier: QualityTier = QualityTier.TIER_1  # Official DOI registry records
    BASE_URL: str = "https://api.crossref.org/works"

    def _get_headers(self) -> dict[str, str]:
        headers = {"User-Agent": "AcademicResearchAgent/1.0"}
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
            "query.bibliographic": query,
            "rows": min(limit, 50),
        }
        filters = []
        if year_start:
            filters.append(f"from-pub-date:{year_start}-01-01")
        if year_end:
            filters.append(f"until-pub-date:{year_end}-12-31")
        if filters:
            params["filter"] = ",".join(filters)

        try:
            with httpx.Client(timeout=self.timeout, headers=self._get_headers()) as client:
                resp = client.get(self.BASE_URL, params=params)
                if resp.status_code != 200:
                    logger.warning(f"Crossref returned status {resp.status_code}")
                    return []
                data = resp.json()
        except Exception as e:
            logger.warning(f"Crossref search error: {e}")
            return []

        items = data.get("message", {}).get("items", [])
        results: list[Paper] = []
        for item in items:
            paper = self._parse_item(item)
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
                item = resp.json().get("message", {})
                return self._parse_item(item)
        except Exception:
            return None

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5.0, headers=self._get_headers()) as client:
                resp = client.get(self.BASE_URL, params={"rows": 1})
                return resp.status_code == 200
        except Exception:
            return False

    def _parse_item(self, item: dict[str, Any]) -> Paper | None:
        titles = item.get("title", [])
        if not titles or not titles[0]:
            return None
        title = titles[0]

        authors: list[str] = []
        for author in item.get("author", []):
            family = author.get("family", "")
            given = author.get("given", "")
            if family and given:
                authors.append(f"{given} {family}")
            elif family:
                authors.append(family)
            elif author.get("name"):
                authors.append(author["name"])

        # Extract year from issued date-parts
        year = None
        date_parts = (
            item.get("issued", {}).get("date-parts")
            or item.get("published-print", {}).get("date-parts")
            or item.get("published-online", {}).get("date-parts")
        )
        if date_parts and len(date_parts[0]) > 0:
            year = date_parts[0][0]

        venues = item.get("container-title", [])
        venue = venues[0] if venues else None

        doi = item.get("DOI")
        url = item.get("URL") or (f"https://doi.org/{doi}" if doi else None)

        raw_abstract = item.get("abstract")
        abstract = strip_jats_tags(raw_abstract)

        citation_count = item.get("is-referenced-by-count")
        pub_type = item.get("type")

        pdf_url = None
        for link in item.get("link", []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL")
                break

        return self.build_paper(
            title=title,
            authors=authors,
            year=year,
            venue=venue,
            abstract=abstract,
            doi=doi,
            url=url,
            pdf_url=pdf_url,
            citation_count=citation_count,
            publication_type=pub_type,
            quality_tier=QualityTier.TIER_1,
        )

