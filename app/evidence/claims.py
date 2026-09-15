"""Extract verifiable scientific and methodological claims from full text."""
from __future__ import annotations

import logging
import re
from app.models.schemas import Paper, Claim, EvidenceType
from app.agent.ollama_client import OllamaClient
from app.agent.prompts import CLAIM_EXTRACTION_SYSTEM_PROMPT, CLAIM_EXTRACTION_USER_TEMPLATE
from app.evidence.full_text import FullTextChunk, FullTextIngestor

logger = logging.getLogger(__name__)


class ClaimExtractor:
    """Extract claims from open-access full text, falling back explicitly to abstracts."""

    def __init__(self, client: OllamaClient | None = None, ingestor: FullTextIngestor | None = None):
        self.client = client or OllamaClient()
        self.ingestor = ingestor or FullTextIngestor()

    def extract_claims(self, papers: list[Paper], max_papers: int = 15) -> list[Claim]:
        claims: list[Claim] = []
        counter = 1
        for paper in papers[:max_papers]:
            chunks: list[FullTextChunk] = []
            if paper.pdf_url:
                try:
                    chunks = self.ingestor.ingest(paper)
                    if chunks:
                        paper.full_text_status = "available"
                        paper.full_text_source = paper.pdf_url
                    else:
                        paper.full_text_status = "failed"
                except Exception as err:
                    paper.full_text_status = "failed"
                    paper.full_text_error = str(err)[:500]
                    logger.warning("Full-text ingestion failed for %s: %s", paper.internal_id, err)
            else:
                paper.full_text_status = "unavailable"

            if chunks:
                for chunk in chunks:
                    extracted = self._extract_chunk_claims(paper, chunk, counter)
                    for claim in extracted:
                        claim.claim_id = f"C{counter:02d}"
                        claims.append(claim)
                        counter += 1
                    # Keep reports bounded while covering multiple sections.
                    if len(claims) >= max_papers * 8:
                        break
            elif paper.abstract and len(paper.abstract) >= 40:
                extracted = self._extract_abstract_claims(paper, counter)
                for claim in extracted:
                    claim.claim_id = f"C{counter:02d}"
                    claims.append(claim)
                    counter += 1
        return claims

    def _extract_chunk_claims(self, paper: Paper, chunk: FullTextChunk, start_id: int) -> list[Claim]:
        prompt = CLAIM_EXTRACTION_USER_TEMPLATE.format(
            paper_id=paper.internal_id,
            title=paper.title,
            abstract=chunk.text,
            section=chunk.section,
            page_start=chunk.page_start or "unknown",
            page_end=chunk.page_end or "unknown",
        )
        try:
            raw_json = self.client.generate_json(prompt=prompt, system_prompt=CLAIM_EXTRACTION_SYSTEM_PROMPT, temperature=0.1)
            if isinstance(raw_json, list):
                result = []
                for item in raw_json:
                    if not isinstance(item, dict) or not item.get("claim_text"):
                        continue
                    result.append(Claim(
                        claim_id=f"C{start_id:02d}", claim_text=item["claim_text"].strip(), paper_id=paper.internal_id,
                        evidence_type=self._parse_evidence_type(item.get("evidence_type", "")),
                        supporting_sources=[paper.internal_id], confidence=float(item.get("confidence", 0.8)),
                        notes=str(item.get("notes", "")), section=chunk.section, page_start=chunk.page_start,
                        page_end=chunk.page_end, source_excerpt=chunk.text, source_url=chunk.source_url,
                    ))
                if result:
                    return result
        except Exception as err:
            logger.debug("LLM full-text claim extraction failed for %s: %s", paper.internal_id, err)
        return self._extract_deterministic_text(paper, chunk.text, chunk.section, chunk.page_start, chunk.page_end, chunk.source_url, start_id)

    def _extract_abstract_claims(self, paper: Paper, start_id: int) -> list[Claim]:
        prompt = CLAIM_EXTRACTION_USER_TEMPLATE.format(
            paper_id=paper.internal_id, title=paper.title, abstract=paper.abstract,
            section="abstract", page_start="unknown", page_end="unknown",
        )\        
        try:
            raw_json = self.client.generate_json(prompt=prompt, system_prompt=CLAIM_EXTRACTION_SYSTEM_PROMPT, temperature=0.1)
            if isinstance(raw_json, list):
                result = []
                for item in raw_json:
                    if isinstance(item, dict) and item.get("claim_text"):
                        result.append(Claim(
                            claim_id=f"C{start_id:02d}", claim_text=item["claim_text"].strip(), paper_id=paper.internal_id,
                            evidence_type=self._parse_evidence_type(item.get("evidence_type", "")),
                            supporting_sources=[paper.internal_id], confidence=float(item.get("confidence", 0.7)),
                            notes="ABSTRACT-ONLY: open-access full text was unavailable.", section="abstract",
                            source_excerpt=paper.abstract, source_url=paper.url,
                        ))
                if result:
                    return result
        except Exception as err:
            logger.debug("LLM abstract claim extraction failed for %s: %s", paper.internal_id, err)
        return self._extract_deterministic_text(paper, paper.abstract or "", "abstract", None, None, paper.url, start_id, abstract_only=True)

    def _extract_deterministic_text(self, paper: Paper, text: str, section: str, page_start: int | None,
                                    page_end: int | None, source_url: str | None, start_id: int,
                                    abstract_only: bool = False) -> list[Claim]:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 30]
        patterns = [
            (r"\b(achieves?|outperforms?|improves?|superior|state-of-the-art|accuracy|performance|mAP|AUC|significant)\b", EvidenceType.EMPIRICAL_RESULT),
            (r"\b(we propose|we introduce|our method|novel framework|architecture|algorithm|methodology)\b", EvidenceType.METHODOLOGICAL_CLAIM),
            (r"\b(however|limitation|challenge|fail|overhead|latency|bottleneck|trade-off)\b", EvidenceType.LIMITATION),
            (r"\b(compared to|evaluat|benchmark|dataset|empirical)\b", EvidenceType.COMPARISON),
        ]
        result: list[Claim] = []
        for sentence in sentences:
            etype = next((et for pat, et in patterns if re.search(pat, sentence, re.I)), None)
            if etype:
                note = "ABSTRACT-ONLY: open-access full text was unavailable." if abstract_only else f"Extracted from {section} section."
                result.append(Claim(claim_id=f"C{start_id:02d}", claim_text=sentence, paper_id=paper.internal_id,
                    evidence_type=etype, supporting_sources=[paper.internal_id], confidence=0.72 if not abstract_only else 0.65,
                    notes=note, section=section, page_start=page_start, page_end=page_end,
                    source_excerpt=sentence, source_url=source_url))
            if len(result) >= 2:
                break
        return result

    def _parse_evidence_type(self, raw_type: str) -> EvidenceType:
        raw = raw_type.lower().strip()
        for et in EvidenceType:
            if et.value == raw or raw in et.value:
                return et
        return EvidenceType.EMPIRICAL_RESULT
