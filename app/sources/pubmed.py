"""PubMed / NCBI E-utilities academic adapter."""
from __future__ import annotations

import logging
import re
from typing import Any
import xml.etree.ElementTree as ET
import httpx
from app.models.schemas import Paper, QualityTier
from app.sources.base import AcademicSource
from app.config import config

logger = logging.getLogger(__name__)


class PubMedSource(AcademicSource):
    """Adapter for NCBI E-utilities (PubMed)."""

    name: str = "pubmed"
    default_tier: QualityTier = QualityTier.TIER_1  # Official peer-reviewed biomedical records
    BASE_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def _get_params(self, base_params: dict[str, Any]) -> dict[str, Any]:
        params = dict(base_params)
        if config.NCBI_API_KEY:
            params["api_key"] = config.NCBI_API_KEY
        return params

    def search(
        self,
        query: str,
        limit: int = 10,
        year_start: int | None = None,
        year_end: int | None = None,
    ) -> list[Paper]:
        # Step 1: ESearch to get PubMed IDs
        search_params: dict[str, Any] = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": min(limit, 25),
            "sort": "relevance",
        }
        if year_start and year_end:
            search_params["mindate"] = f"{year_start}/01/01"
            search_params["maxdate"] = f"{year_end}/12/31"
            search_params["datetype"] = "pdat"
        elif year_start:
            search_params["mindate"] = f"{year_start}/01/01"
            search_params["datetype"] = "pdat"

        search_url = f"{self.BASE_URL}/esearch.fcgi"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(search_url, params=self._get_params(search_params))
                if resp.status_code != 200:
                    return []
                data = resp.json()
        except Exception as e:
            logger.warning(f"PubMed search error: {e}")
            return []

        id_list = data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []

        # Step 2: EFetch or ESummary for the retrieved IDs
        return self._fetch_papers(id_list)

    def _fetch_papers(self, id_list: list[str]) -> list[Paper]:
        ids_str = ",".join(id_list)
        # Fetch abstracts using efetch XML
        fetch_url = f"{self.BASE_URL}/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ids_str,
            "retmode": "xml",
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(fetch_url, params=self._get_params(fetch_params))
                if resp.status_code != 200:
                    return []
                return self._parse_pubmed_xml(resp.text)
        except Exception as e:
            logger.warning(f"PubMed efetch error: {e}")
            return []

    def _parse_pubmed_xml(self, xml_text: str) -> list[Paper]:
        papers: list[Paper] = []
        try:
            root = ET.fromstring(xml_text)
        except Exception:
            return []

        for article in root.findall(".//PubmedArticle"):
            medline = article.find("MedlineCitation")
            if medline is None:
                continue
            pmid_el = medline.find("PMID")
            pmid = pmid_el.text if pmid_el is not None else None

            art_el = medline.find("Article")
            if art_el is None:
                continue

            title_el = art_el.find("ArticleTitle")
            title = "".join(title_el.itertext()).strip() if title_el is not None else None
            if not title:
                continue

            # Authors
            authors: list[str] = []
            author_list = art_el.find("AuthorList")
            if author_list is not None:
                for author in author_list.findall("Author"):
                    last = author.find("LastName")
                    fore = author.find("ForeName")
                    if last is not None and fore is not None:
                        authors.append(f"{fore.text} {last.text}")
                    elif last is not None:
                        authors.append(last.text or "")

            # Year
            year = None
            pub_date = art_el.find(".//JournalIssue/PubDate")
            if pub_date is not None:
                year_el = pub_date.find("Year")
                if year_el is not None and year_el.text:
                    try:
                        year = int(year_el.text)
                    except ValueError:
                        pass
                elif pub_date.find("MedlineDate") is not None:
                    m = re.search(r"\b(19\d\d|20\d\d)\b", pub_date.find("MedlineDate").text or "")
                    if m:
                        year = int(m.group(1))

            # Venue / Journal
            venue = None
            journal = art_el.find("Journal/Title")
            if journal is not None and journal.text:
                venue = journal.text

            # Abstract
            abstract = None
            abs_el = art_el.find("Abstract")
            if abs_el is not None:
                texts = [
                    "".join(t.itertext()).strip()
                    for t in abs_el.findall("AbstractText")
                    if "".join(t.itertext()).strip()
                ]
                if texts:
                    abstract = " ".join(texts)

            # DOI
            doi = None
            for id_el in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
                if id_el.attrib.get("IdType") == "doi" and id_el.text:
                    doi = id_el.text.strip()
                    break

            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None

            paper = self.build_paper(
                title=title,
                authors=authors,
                year=year,
                venue=venue,
                abstract=abstract,
                doi=doi,
                pubmed_id=pmid,
                url=url,
                quality_tier=QualityTier.TIER_1,
            )
            papers.append(paper)

        return papers

    def get_paper(self, identifier: str) -> Paper | None:
        papers = self._fetch_papers([identifier])
        return papers[0] if papers else None

    def health_check(self) -> bool:
        url = f"{self.BASE_URL}/esearch.fcgi"
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(url, params=self._get_params({"db": "pubmed", "term": "covid", "retmax": 1, "retmode": "json"}))
                return resp.status_code == 200
        except Exception:
            return False

