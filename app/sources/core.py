"""CORE academic literature adapter."""
from __future__ import annotations

import logging
from typing import Any
import httpx
from app.models.schemas import Paper, QualityTier
from app.sources.base import AcademicSource
from app.config import config

logger = logging.getLogger(__name__)


class CoreSource(AcademicSource):
    """Adapter for the CORE API v3."""

    name: str = "core"
    default_tier: QualityTier = QualityTier.TIER_2
    BASE_URL: str = "https://api.core.ac.uk/v3"

    def _get_headers(self) -> dict[str, str]:
        headers = {"User-Agent": "AcademicResearchAgent/1.0"}
        if config.CORE_API_KEY:
            headers["Authorization"] = f"Bearer {config.CORE_API_KEY}"
        return headers

    def search(
        self,
        query: str,
        limit: int = 10,
        year_start: int | None = None,
        year_end: int | None = None,
    ) -> list[Paper]:
        # Graceful degradation if no API key
        if not config.CORE_API_KEY:
            return []

        url = f"{self.BASE_URL}/search/works"
        params: dict[str, Any] = {
            "q": query,
            "limit": min(limit, 50),
        }
        if year_start and year_end:
            params["q"] += f" AND yearPublished:[{year_start} TO {year_end}]"

        try:
            with httpx.Client(timeout=self.timeout, headers=self._get_headers()) as client:
                resp = client.get(url, params=params)
                if resp.status_code != 200:
                    logger.warning(f"CORE returned status {resp.status_code}")
                    return []
                data = resp.json()
        except Exception as e:
            logger.warning(f"CORE search error: {e}")
            return []

        results: list[Paper] = []
        for item in data.get("results", []):
            paper = self._parse_item(item)
            if paper:
                results.append(paper)
        return results

    def get_paper(self, identifier: str) -> Paper | None:
        if not config.CORE_API_KEY:
            return None
        url = f"{self.BASE_URL}/works/{identifier}"
        try:
            with httpx.Client(timeout=self.timeout, headers=self._get_headers()) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    return None
                return self._parse_item(resp.json())
        except Exception:
            return None

    def health_check(self) -> bool:
        if not config.CORE_API_KEY:
            return False
        try:
            with httpx.Client(timeout=5.0, headers=self._get_headers()) as client:
                resp = client.get(f"{self.BASE_URL}/search/works", params={"q": "test", "limit": 1})
                return resp.status_code == 200
        except Exception:
            return False

    def _parse_item(self, item: dict[str, Any]) -> Paper | None:
        title = item.get("title")
        if not title:
            return None

        authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
        year = item.get("yearPublished")
        abstract = item.get("abstract")
        doi = item.get("doi")
        url = item.get("downloadUrl") or item.get("sourceFulltextUrls", [None])[0]
        pdf_url = item.get("downloadUrl")

        return self.build_paper(
            title=title,
            authors=authors,
            year=year,
            abstract=abstract,
            doi=doi,
            url=url,
            pdf_url=pdf_url,
            is_open_access=True,
            quality_tier=QualityTier.TIER_2,
        )

