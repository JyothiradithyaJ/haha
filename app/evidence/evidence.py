"""Evidence mapping and heuristic strength evaluation."""
from __future__ import annotations

from app.models.schemas import (
    Paper,
    Claim,
    EvidenceRecord,
    EvidenceStrength,
    QualityTier,
)


def evaluate_evidence_strength(
    supporting_papers: list[Paper],
    contradicting_papers: list[Paper] | None = None,
) -> EvidenceStrength:
    """Evaluate evidence strength based on multi-source support, peer review tiers, and conflict.

    Heuristic scale:
    - VERY STRONG: >= 3 independent sources, with >= 2 Tier 1 peer-reviewed, no contradiction
    - STRONG: 2 independent sources or 1 high-tier peer-reviewed with citations, minimal contradiction
    - MODERATE: 1-2 preprint/aggregator sources, or strong sources with minor contradiction
    - WEAK: single unverified preprint or heavily contested claim
    - INSUFFICIENT: zero concrete supporting papers or severe unresolvable conflict
    """
    contradicting = contradicting_papers or []
    num_supporting = len(supporting_papers)
    num_contradicting = len(contradicting)

    if num_supporting == 0:
        return EvidenceStrength.INSUFFICIENT

    tier1_count = sum(1 for p in supporting_papers if p.quality_tier == QualityTier.TIER_1)
    has_contradiction = num_contradicting > 0

    if num_supporting >= 3 and tier1_count >= 2 and not has_contradiction:
        return EvidenceStrength.VERY_STRONG

    if (num_supporting >= 2 and not has_contradiction) or (tier1_count >= 1 and not has_contradiction):
        return EvidenceStrength.STRONG

    if has_contradiction:
        if num_supporting > num_contradicting and num_supporting >= 2:
            return EvidenceStrength.MODERATE
        return EvidenceStrength.WEAK

    if num_supporting == 1:
        return EvidenceStrength.MODERATE

    return EvidenceStrength.WEAK


class EvidenceManager:
    """Maintains traceable bidirectional mappings: claim -> evidence -> paper -> source."""

    def __init__(self):
        self.evidence_records: list[EvidenceRecord] = []
        self.paper_lookup: dict[str, Paper] = {}

    def register_papers(self, papers: list[Paper]) -> None:
        """Index papers by internal_id."""
        for p in papers:
            if p.internal_id:
                self.paper_lookup[p.internal_id] = p

    def build_evidence_records(self, claims: list[Claim]) -> list[EvidenceRecord]:
        """Convert extracted claims into formal traceable EvidenceRecords."""
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
                evidence_id=f"EV-{len(records)+1:03d}",
                claim_id=claim.claim_id,
                paper_id=claim.paper_id,
                quote_or_excerpt=claim.claim_text,
                evidence_type=claim.evidence_type,
                strength=strength,
                source_adapter=(paper.sources[0] if paper.sources else "unknown"),
            )
            records.append(record)

        self.evidence_records = records
        return records
