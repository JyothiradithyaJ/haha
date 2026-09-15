"""Evidence extraction, strength evaluation, contradiction analysis, and full-text ingestion."""
from app.evidence.claims import ClaimExtractor
from app.evidence.evidence import EvidenceManager, evaluate_evidence_strength
from app.evidence.contradictions import ContradictionAnalyzer
from app.evidence.full_text import FullTextChunk, FullTextIngestor, PdfTextParser

__all__ = ["ClaimExtractor", "EvidenceManager", "evaluate_evidence_strength", "ContradictionAnalyzer", "FullTextChunk", "FullTextIngestor", "PdfTextParser"]
