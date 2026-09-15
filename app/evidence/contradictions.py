"""Contradiction analysis and scientific disagreement detection."""
from __future__ import annotations

import logging
import re
from typing import Any
from app.models.schemas import Paper, Claim, ContradictionRecord, EvidenceType
from app.agent.ollama_client import OllamaClient, OllamaError
from app.agent.prompts import CONTRADICTION_ANALYSIS_SYSTEM_PROMPT, CONTRADICTION_USER_TEMPLATE

logger = logging.getLogger(__name__)


class ContradictionAnalyzer:
    """Identifies conflicting empirical results, limitations, and performance trade-offs."""

    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def analyze_contradictions(
        self,
        claims: list[Claim],
        papers: list[Paper],
    ) -> list[ContradictionRecord]:
        """Build contradiction matrix by analyzing claims against literature."""
        if not claims or not papers:
            return []

        paper_map = {p.internal_id: p for p in papers if p.internal_id}

        # Format context for analysis
        context_lines = []
        for c in claims[:12]:
            context_lines.append(f"[{c.paper_id}] ({c.evidence_type.value}): {c.claim_text}")

        context_str = "\n".join(context_lines)

        try:
            raw_json = self.client.generate_json(
                prompt=CONTRADICTION_USER_TEMPLATE.format(claims_context=context_str),
                system_prompt=CONTRADICTION_ANALYSIS_SYSTEM_PROMPT,
                temperature=0.1,
            )
            if isinstance(raw_json, list) and len(raw_json) > 0:
                records: list[ContradictionRecord] = []
                for item in raw_json:
                    if isinstance(item, dict) and item.get("claim"):
                        # Validate paper IDs exist
                        supp = [pid for pid in item.get("supporting_papers", []) if pid in paper_map]
                        contra = [pid for pid in item.get("contradicting_papers", []) if pid in paper_map]
                        if supp or contra:
                            records.append(
                                ContradictionRecord(
                                    claim=str(item["claim"]).strip(),
                                    supporting_papers=supp,
                                    contradicting_papers=contra,
                                    overall_assessment=str(item.get("overall_assessment", "")).strip(),
                                    evidence_discrepancy=str(item.get("evidence_discrepancy", "")).strip(),
                                    notes=str(item.get("notes", "")).strip(),
                                )
                            )
                if records:
                    return records
        except (OllamaError, ValueError, Exception) as err:
            logger.debug(f"LLM contradiction analysis failed: {err}")

        # Deterministic fallback: cross-examine limitation claims vs empirical claims
        return self._detect_deterministic_contradictions(claims, papers)

    def _detect_deterministic_contradictions(
        self,
        claims: list[Claim],
        papers: list[Paper],
    ) -> list[ContradictionRecord]:
        """Deterministic contradiction detection based on limitation keywords and Pass D papers."""
        records: list[ContradictionRecord] = []
        limitation_claims = [c for c in claims if c.evidence_type == EvidenceType.LIMITATION]
        empirical_claims = [c for c in claims if c.evidence_type == EvidenceType.EMPIRICAL_RESULT]

        # Check for pass D papers (contradiction pass)
        pass_d_papers = [p.internal_id for p in papers if "contradiction" in p.matched_passes]

        # Trade-off 1: Accuracy vs Inference Latency / Computational Overhead
        overhead_papers = [
            p.internal_id for p in papers
            if p.abstract and re.search(r"\b(overhead|latency|computation|slow|memory|cost)\b", p.abstract, re.I)
        ]
        high_acc_papers = [
            p.internal_id for p in papers
            if p.abstract and re.search(r"\b(accuracy|state-of-the-art|outperform|high precision)\b", p.abstract, re.I)
        ]
        if overhead_papers and high_acc_papers:
            records.append(
                ContradictionRecord(
                    claim="Reported performance versus computational cost or latency",
                    supporting_papers=high_acc_papers[:2],
                    contradicting_papers=overhead_papers[:2],
                    overall_assessment="The retrieved literature indicates a trade-off between reported performance and computational-resource requirements.",
                    evidence_discrepancy="Performance metrics and resource requirements are reported under different evaluation conditions.",
                )
            )

        # Trade-off 2: Zero-shot Generalization vs Domain Shift & Novel Defect Variance
        domain_papers = [
            p.internal_id for p in papers
            if p.abstract and re.search(r"\b(domain shift|unseen|generaliz|texture|variance|false positive)\b", p.abstract, re.I)
        ]
        if domain_papers and len(domain_papers) >= 2:
            records.append(
                ContradictionRecord(
                    claim="Generalization across settings, datasets, or domains",
                    supporting_papers=[domain_papers[0]],
                    contradicting_papers=[domain_papers[1]],
                    overall_assessment="The retrieved papers report differing outcomes when methods are applied beyond their original evaluation setting.",
                    evidence_discrepancy="Differences in data, setting, or evaluation protocol may explain the divergent results.",
                )
            )

        # If limitation claims exist, build records from them
        for lim in limitation_claims[:2]:
            matching_emp = [ec.paper_id for ec in empirical_claims if ec.paper_id != lim.paper_id]
            if matching_emp:
                records.append(
                    ContradictionRecord(
                        claim=lim.claim_text[:120] + ("..." if len(lim.claim_text) > 120 else ""),
                        supporting_papers=matching_emp[:2],
                        contradicting_papers=[lim.paper_id],
                        overall_assessment=f"Disagreement between baseline claims and specific limitations identified in [{lim.paper_id}].",
                        evidence_discrepancy="Method reported to suffer under specific edge cases or constrained conditions.",
                    )
                )

        return records
