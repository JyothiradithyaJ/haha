"""Search coordinator dispatching queries across multiple academic sources."""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.models.schemas import Paper, SearchQuery, PassType
from app.sources.base import AcademicSource
from app.sources.openalex import OpenAlexSource
from app.sources.semantic_scholar import SemanticScholarSource
from app.sources.crossref import CrossrefSource
from app.sources.pubmed import PubMedSource
from app.sources.arxiv import ArxivSource
from app.sources.core import CoreSource
from app.config import config

logger = logging.getLogger(__name__)


class SearchCoordinator:
    """Coordinates concurrent queries across enabled academic sources with bounded concurrency."""

    def __init__(self, sources: list[AcademicSource] | None = None):
        if sources is not None:
            self.sources = sources
        else:
            self.sources = [
                OpenAlexSource(),
                SemanticScholarSource(),
                CrossrefSource(),
                PubMedSource(),
                ArxivSource(),
                CoreSource(),
            ]

    def search_query(
        self,
        query: SearchQuery,
        limit_per_source: int | None = None,
    ) -> list[Paper]:
        """Execute a SearchQuery across all sources concurrently and tag matched_passes."""
        limit = limit_per_source or config.MAX_SEARCH_RESULTS_PER_SOURCE
        collected: list[Paper] = []

        def _execute_source(source: AcademicSource) -> list[Paper]:
            try:
                # Some sources (e.g. PubMed) are biomedical-focused. If query is clearly non-biomedical and fails, it returns [].
                return source.search(
                    query=query.query,
                    limit=limit,
                    year_start=query.year_start,
                    year_end=query.year_end,
                )
            except Exception as err:
                logger.warning(f"Error querying source {source.name}: {err}")
                return []

        # Concurrently query sources
        with ThreadPoolExecutor(max_workers=min(len(self.sources), 6)) as executor:
            future_to_source = {
                executor.submit(_execute_source, src): src for src in self.sources
            }
            for future in as_completed(future_to_source):
                src = future_to_source[future]
                try:
                    results = future.result()
                    for p in results:
                        if query.pass_type.value not in p.matched_passes:
                            p.matched_passes.append(query.pass_type.value)
                    collected.extend(results)
                except Exception as err:
                    logger.warning(f"Future error for {src.name}: {err}")

        return collected

    def health_check_all(self) -> dict[str, bool]:
        """Check status of each source adapter."""
        status = {}
        for src in self.sources:
            try:
                status[src.name] = src.health_check()
            except Exception:
                status[src.name] = False
        return status

