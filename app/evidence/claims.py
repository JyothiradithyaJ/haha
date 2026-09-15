"""Extract verifiable scientific and methodological claims from papers."""
from __future__ import annotations

import logging
import re
from typing import Any
from app.models.schemas import Paper, Claim, EvidenceType, EvidenceStrength
from app.agent.ollama_client import OllamaClient, OllamaError
from app.agent.prompts import CLAIM_EXTRACTION_SYSTEM_PROMPT, CLAIM_EXTRACTION_USER_TEMPLATE

logger = logging.getLogger(__name__)


class ClaimExtractor:
    """Extracts verifiable claims from papers with LLM support and deterministic fallbacks."""

    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def extract_claims(self, papers: list[Paper], max_papers: int = 15) -> list[Claim]:
        """Extract substantive claims from the top-ranked papers with abstracts."""
        claims: list[Claim] = []
        counter = 1

        for paper in papers[:max_papers]:
            if not paper.abstract or len(paper.abstract) < 40:
                continue

            extracted = self._extract_paper_claims(paper, start_id=counter)
            for c in extracted:
                c.claim_id = f"C{counter:02d}"
                claims.append(c)
                counter += 1

        return claims

    def _extract_paper_claims(self, paper: Paper, start_id: int) -> list[Claim]:
        """Extract claims using Ollama or fallback to deterministic NLP."""
        prompt = CLAIM_EXTRACTION_USER_TEMPLATE.format(
            paper_id=paper.internal_id,
            title=paper.title,
            abstract=paper.abstract,
        )

        try:
            raw_json = self.client.generate_json(
                prompt=prompt,
                system_prompt=CLAIM_EXTRACTION_SYSTEM_PROMPT,
                temperature=0.1,
            )
            if isinstance(raw_json, list) and len(raw_json) > 0:
                claims: list[Claim] = []
                for item in raw_json:
                    if isinstance(item, dict) and item.get("claim_text"):
                        etype = self._parse_evidence_type(item.get("evidence_type", ""))
                        claims.append(
                            Claim(
                                claim_id=f"C{start_id:02d}",
                                claim_text=item["claim_text"].strip(),
                                paper_id=paper.internal_id,
                                evidence_type=etype,
                                supporting_sources=[paper.internal_id],
                                confidence=float(item.get("confidence", 0.8)),
                                notes=str(item.get("notes", "")),
                            )
                        )
                if claims:
                    return claims
        except Exception as err:
            logger.debug(f"LLM claim extraction failed for {paper.internal_id}: {err}")

        # Deterministic rule-based extraction fallback
        return self._extract_deterministic_claims(paper, start_id)

    def _extract_deterministic_claims(self, paper: Paper, start_id: int) -> list[Claim]:
        """Extract claims by scanning abstract for key scientific result indicators."""
        abstract = paper.abstract or ""
        # Split into sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", abstract) if len(s.strip()) > 20]

        patterns = [
            (r"\b(achieves?|outperforms?|improves?|superior|state-of-the-art|accuracy|performance|mAP|AUC)\b", EvidenceType.EMPIRICAL_RESULT),
            (r"\b(we propose|we introduce|our method|novel framework|architecture|algorithm)\b", EvidenceType.METHODOLOGICAL_CLAIM),
            (r"\b(however|limitation|challenge|fail|overhead|latency|bottleneck|trade-off)\b", EvidenceType.LIMITATION),
            (r"\b(compared to|evaluat|benchmark|dataset|empirical)\b", EvidenceType.COMPARISON),
        ]

        extracted: list[Claim] = []
        for s in sentences:
            for pat, etype in patterns:
                if re.search(pat, s, re.IGNORECASE):
                    extracted.append(
                        Claim(
                            claim_id=f"C{start_id:02d}",
                            claim_text=s,
                            paper_id=paper.internal_id,
                            evidence_type=etype,
                            supporting_sources=[paper.internal_id],
                            confidence=0.75,
                            notes=f"Directly extracted from {paper.internal_id} abstract",
                        )
                    )
                    break
            if len(extracted) >= 2:
                break

        # Fallback if no specific pattern matched: take the first sentence
        if not extracted and sentences:
            extracted.append(
                Claim(
                    claim_id=f"C{start_id:02d}",
                    claim_text=sentences[0],
                    paper_id=paper.internal_id,
                    evidence_type=EvidenceType.METHODOLOGICAL_CLAIM,
                    supporting_sources=[paper.internal_id],
                    confidence=0.7,
                    notes=f"Core proposition from {paper.internal_id}",
                )
            )

        return extracted

    def _parse_evidence_type(self, raw_type: str) -> EvidenceType:
        """Parse raw string into EvidenceType enum."""
        raw = raw_type.lower().strip()
        for et in EvidenceType:
            if et.value == raw or raw in et.value:
                return et
        return EvidenceType.EMPIRICAL_RESULT
