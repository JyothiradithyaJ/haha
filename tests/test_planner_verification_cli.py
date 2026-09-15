"""Tests for planner pass coverage, Crossref verification, and CLI bounds."""
from __future__ import annotations

import sys

import pytest

from app.agent.planner import ResearchPlanner
from app.models.schemas import Paper, PassType
from app.verification.bibliography import BibliographicVerifier
from main import parse_args


class PartialPlanClient:
    def generate_json(self, **_kwargs):
        return {
            "research_objectives": [{"description": "Test objective"}],
            "search_queries": [
                {
                    "query": "test query",
                    "pass_type": "broad",
                    "target_concept": "test",
                }
            ],
        }


class FakeCrossref:
    def __init__(self, result: Paper | None):
        self.result = result
        self.requested_doi: str | None = None

    def get_paper(self, doi: str) -> Paper | None:
        self.requested_doi = doi
        return self.result


def test_partial_llm_plan_is_completed_with_all_research_passes():
    plan = ResearchPlanner(PartialPlanClient()).create_plan("How does testing work?")

    assert {query.pass_type for query in plan.search_queries} == set(PassType)


def test_crossref_verification_compares_returned_metadata():
    paper = Paper(internal_id="P01", title="A Verified Paper", doi="10.1000/example", year=2024)
    crossref_record = Paper(title="A Verified Paper", doi="10.1000/example", year=2024)
    source = FakeCrossref(crossref_record)

    record = BibliographicVerifier(crossref=source).verify_single_paper(paper)

    assert source.requested_doi == "10.1000/example"
    assert record.title_matches is True
    assert "crossref" in record.verified_sources
    assert record.confidence == 0.95


def test_disabled_remote_verification_is_explicit():
    paper = Paper(internal_id="P01", title="Offline paper", doi="10.1000/offline")
    record = BibliographicVerifier(verify_remote=False).verify_single_paper(paper)

    assert record.title_matches is False
    assert "disabled" in record.discrepancies[0].lower()


def test_cli_rejects_non_positive_limits(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "question", "--iterations", "0"])
    with pytest.raises(SystemExit):
        parse_args()

    monkeypatch.setattr(sys, "argv", ["main.py", "question", "--max-papers", "-1"])
    with pytest.raises(SystemExit):
        parse_args()
