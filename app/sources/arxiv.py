"""arXiv academic literature adapter."""
from __future__ import annotations

import logging
import re
from typing import Any
import xml.etree.ElementTree as ET
import httpx
from app.models.schemas import Paper, QualityTier
from app.sources.base import AcademicSource

logger = logging.getLogger(__name__)

# Atom namespace
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivSource(AcademicSource):
    """Adapter for arXiv Atom/XML export API."""

    name: str = "arxiv"
    default_tier: QualityTier = QualityTier.TIER_2  # Preprint repository
    BASE_URL: str = "https://export.arxiv.org/api/query"

    def search(
        self,
        query: str,
        limit: int = 10,
        year_start: int | None = None,
        year_end: int | None = None,
    ) -> list[Paper]:
        # Clean query: strip quotes/special syntax that causes arXiv 400
        clean_q = re.sub(r"[^\w\s\-\.]", " ", query).strip()
        formatted_query = f"all:{clean_q}"

        params: dict[str, Any] = {
            "search_query": formatted_query,
            "start": 0,
            "max_results": min(limit, 50),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(self.BASE_URL, params=params)
                if resp.status_code != 200:
                    logger.warning(f"arXiv returned status {resp.status_code}")
                    return []
                return self._parse_atom_feed(resp.text, year_start, year_end)
        except Exception as e:
            logger.warning(f"arXiv search error: {e}")
            return []

    def get_paper(self, identifier: str) -> Paper | None:
        clean_id = identifier.replace("arXiv:", "").strip()
        params = {"id_list": clean_id}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(self.BASE_URL, params=params)
                if resp.status_code != 200:
                    return None
                papers = self._parse_atom_feed(resp.text)
                return papers[0] if papers else None
        except Exception:
            return None

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(self.BASE_URL, params={"search_query": "all:electron", "max_results": 1})
                return resp.status_code == 200
        except Exception:
            return False

    def _parse_atom_feed(
        self,
        xml_text: str,
        year_start: int | None = None,
        year_end: int | None = None,
    ) -> list[Paper]:
        papers: list[Paper] = []
        try:
            root = ET.fromstring(xml_text)
        except Exception:
            return []

        for entry in root.findall("atom:entry", ATOM_NS):
            title_el = entry.find("atom:title", ATOM_NS)
            if title_el is None or not title_el.text:
                continue
            title = " ".join(title_el.text.split())

            summary_el = entry.find("atom:summary", ATOM_NS)
            abstract = " ".join(summary_el.text.split()) if summary_el is not None and summary_el.text else None

            authors: list[str] = []
            for author in entry.findall("atom:author", ATOM_NS):
                name_el = author.find("atom:name", ATOM_NS)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())

            year = None
            published_el = entry.find("atom:published", ATOM_NS)
            if published_el is not None and published_el.text:
                m = re.match(r"^(\d{4})", published_el.text)
                if m:
                    year = int(m.group(1))

            # Apply date filters
            if year:
                if year_start and year < year_start:
                    continue
                if year_end and year > year_end:
                    continue

            id_el = entry.find("atom:id", ATOM_NS)
            entry_id = id_el.text.strip() if id_el is not None and id_el.text else ""
            arxiv_id = None
            m = re.search(r"arxiv\.org/abs/([^/]+)$", entry_id)
            if m:
                arxiv_id = m.group(1)

            pdf_url = None
            for link in entry.findall("atom:link", ATOM_NS):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href")

            doi_el = entry.find("arxiv:doi", ATOM_NS)
            doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None

            journal_el = entry.find("arxiv:journal_ref", ATOM_NS)
            venue = journal_el.text.strip() if journal_el is not None and journal_el.text else "arXiv"

            paper = self.build_paper(
                title=title,
                authors=authors,
                year=year,
                venue=venue,
                abstract=abstract,
                doi=doi,
                arxiv_id=arxiv_id,
                url=entry_id or None,
                pdf_url=pdf_url,
                is_open_access=True,
                publication_type="preprint",
                quality_tier=QualityTier.TIER_2,
            )
            papers.append(paper)

        return papers

