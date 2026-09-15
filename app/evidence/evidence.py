"""Evidence mapping and heuristic strength evaluation."""
from __future__ import annotations

from app.models.schemas import Paper, Claim, EvidenceRecord, EvidenceStrength, QualityTier


def evaluate_evidence_strength(supporting_papers: list[Paper], contradicting_papers: list[Paper] | None = None) -> EvidenceStrength:
    contradicting = contradicting_papers or []
    num_supporting = len(supporting_papers)
    num_contradicting = len(contradicting)
    if num_supporting == 0:
        return EvidenceStrength.INSUFFICIENT
    tier1_count = sum(1 for p in supporting_papers if p.quality_tier == QualityTier.TIER_1)
    if num_supporting >= 3 and tier1_count >= 2 and not num_contradicting:
        return EvidenceStrength.VERY_STRONG
    if (num_supporting >= 2 or tier1_count >= 1) and not num_contradicting:
        return EvidenceStrength.STRONG
    if num_contradicting:
        return EvidenceStrength.MODERATE if num_supporting > num_contradicting and num_supporting >= 2 else EvidenceStrength.WEAK
    return EvidenceStrength.MODERATE if num_supporting == 1 else EvidenceStrength.WEAK


class EvidenceManager:
    """Maintains traceable claim -> evidence -> paper -> source mappings."""

    def __init__(self):
        self.evidence_records: list[EvidenceRecord] = []
        self.paper_lookup: dict[str, Paper] = {}

    def register_papers(self, papers: list[Paper]) -> None:
        for paper in papers:
            if paper.internal_id:
                self.paper_lookup[paper.internal_id] = paper

    def build_evidence_records(self, claims: list[Claim]) -> list[EvidenceRecord]:
        records: list[EvidenceRecord] = []
        for claim in claims:
            paper = self.paper_lookup.get(claim.paper_id)
            if not paper:
                continue
            supporting = [self.paper_lookup[pid] for pid in claim.supporting_sources if pid in self.paper_lookup]
            contradicting = [self.paper_lookup[pid] for pid in claim.contradicting_sources if pid in self.paper_lookup]
            strength = evaluate_evidence_strength(supporting, contradicting)
            claim.evidence_strength = strength
            record = EvidenceRecord(
                evidence_id=f"EV-{len(records)+1:03d}", claim_id=claim.claim_id, paper_id=claim.paper_id,
                quote_or_excerpt=claim.source_excerpt or claim.claim_text, evidence_type=claim.evidence_type,
                strength=strength, source_adapter=(paper.sources[0] if paper.sources else "unknown"),
                section=claim.section, page_start=claim.page_start, page_end=claim.page_end,
                source_url=claim.source_url or paper.pdf_url or paper.url,
                full_text_grounded=claim.section != "abstract",
            )
            records.append(record)
        self.evidence_records = records
        return records
