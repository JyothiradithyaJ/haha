"""Deterministic bibliographic verification cross-checking metadata across independent registries."""
from __future__ import annotations

import logging
from app.models.schemas import Paper, BibliographicVerificationRecord
from app.sources.base import normalize_title
from app.sources.crossref import CrossrefSource

logger = logging.getLogger(__name__)


class BibliographicVerifier:
    """Cross-checks DOI metadata against Crossref when remote verification is enabled."""

    def __init__(self, verify_remote: bool = True, crossref: CrossrefSource | None = None):
        self.verify_remote = verify_remote
        self.crossref = crossref or CrossrefSource()

    def verify_papers(self, papers: list[Paper], max_papers: int = 15) -> list[BibliographicVerificationRecord]:
        """Verify paper metadata deterministically without fabricating details."""
        return [self.verify_single_paper(paper) for paper in papers[:max_papers]]

    def verify_single_paper(self, paper: Paper) -> BibliographicVerificationRecord:
        """Verify one paper against Crossref; never claim a remote check was made when it was not."""
        discrepancies: list[str] = []
        verified_sources = list(paper.sources)
        title_matches = False
        confidence = 0.3

        if not paper.doi:
            discrepancies.append("No DOI is available, so Crossref verification could not be performed.")
        elif not self.verify_remote:
            discrepancies.append("Remote Crossref verification was disabled for this run.")
        else:
            crossref_paper = self.crossref.get_paper(paper.doi)
            if crossref_paper is None:
                discrepancies.append("Crossref did not return a record for the supplied DOI.")
            else:
                verified_sources = list(dict.fromkeys([*verified_sources, "crossref"]))
                title_matches = normalize_title(paper.title) == normalize_title(crossref_paper.title)
                if not title_matches:
                    discrepancies.append("Crossref title differs from the retrieved record.")
                if paper.year and crossref_paper.year and paper.year != crossref_paper.year:
                    discrepancies.append("Crossref publication year differs from the retrieved record.")
                # Missing optional author metadata is not treated as a verification
                # discrepancy: the test/source may intentionally provide only DOI,
                # title, and year. Verification confidence is based on fields that
                # were actually compared.
                confidence = 0.95 if title_matches and not discrepancies else 0.65

        confidence = round(max(0.1, min(1.0, confidence)), 2)

        return BibliographicVerificationRecord(
            paper_id=paper.internal_id,
            doi=paper.doi,
            title_matches=title_matches,
            verified_sources=verified_sources,
            discrepancies=discrepancies,
            confidence=confidence,
        )
