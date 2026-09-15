"""Academic sources package."""
from app.sources.base import AcademicSource
from app.sources.openalex import OpenAlexSource
from app.sources.semantic_scholar import SemanticScholarSource
from app.sources.crossref import CrossrefSource
from app.sources.pubmed import PubMedSource
from app.sources.arxiv import ArxivSource
from app.sources.core import CoreSource

__all__ = [
    "AcademicSource",
    "OpenAlexSource",
    "SemanticScholarSource",
    "CrossrefSource",
    "PubMedSource",
    "ArxivSource",
    "CoreSource",
]

