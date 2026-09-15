"""Evidence extraction, strength evaluation, and contradiction analysis package."""
from app.evidence.claims import ClaimExtractor
from app.evidence.evidence import EvidenceManager, evaluate_evidence_strength
from app.evidence.contradictions import ContradictionAnalyzer

__all__ = [
    "ClaimExtractor",
    "EvidenceManager",
    "evaluate_evidence_strength",
    "ContradictionAnalyzer",
]

