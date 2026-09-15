"""Research planner decomposing user questions into structured multi-pass plans."""
from __future__ import annotations

import logging
import re
from typing import Any
from app.models.schemas import (
    ResearchPlan,
    ResearchObjective,
    SearchQuery,
    PassType,
)
from app.agent.ollama_client import OllamaClient, OllamaError
from app.agent.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE

logger = logging.getLogger(__name__)


class ResearchPlanner:
    """Creates structured research plans using Qwen3.5 4B validated by deterministic schemas."""

    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def create_plan(self, question: str) -> ResearchPlan:
        """Generate and validate a comprehensive research plan for the question."""
        user_prompt = PLANNER_USER_TEMPLATE.format(question=question)

        try:
            raw_json = self.client.generate_json(
                prompt=user_prompt,
                system_prompt=PLANNER_SYSTEM_PROMPT,
                temperature=0.1,
            )
            if isinstance(raw_json, dict):
                return self._coerce_to_plan(question, raw_json)
            else:
                logger.warning("LLM planner returned non-dict JSON; using fallback plan.")
                return self._generate_deterministic_fallback(question)
        except Exception as e:
            logger.warning(f"Ollama planning failed or unavailable ({e}); utilizing deterministic fallback planner.")
            return self._generate_deterministic_fallback(question)

    def _coerce_to_plan(self, question: str, data: dict[str, Any]) -> ResearchPlan:
        """Deterministically validate and coerce parsed dictionary into ResearchPlan."""
        objectives: list[ResearchObjective] = []
        for obj in data.get("research_objectives", []):
            if isinstance(obj, dict) and obj.get("description"):
                objectives.append(
                    ResearchObjective(
                        objective_id=obj.get("objective_id", f"OBJ-{len(objectives)+1}"),
                        description=obj["description"],
                    )
                )

        # Fallback if objectives empty
        if not objectives:
            objectives = [
                ResearchObjective(objective_id="OBJ-1", description=f"Analyze core methods for: {question}"),
                ResearchObjective(objective_id="OBJ-2", description="Identify empirical limitations and research gaps"),
            ]

        # Queries
        queries: list[SearchQuery] = []
        for q in data.get("search_queries", []):
            if isinstance(q, dict) and q.get("query"):
                pass_type_str = str(q.get("pass_type", "broad")).lower()
                # Map to PassType
                matched_type = PassType.PASS_A_BROAD
                for pt in PassType:
                    if pt.value == pass_type_str:
                        matched_type = pt
                        break

                queries.append(
                    SearchQuery(
                        query=q["query"].strip(),
                        pass_type=matched_type,
                        target_concept=q.get("target_concept", "general"),
                        year_start=q.get("year_start"),
                        year_end=q.get("year_end"),
                        rationale=q.get("rationale", ""),
                    )
                )

        # Ensure the plan covers every pass A through F even if the model
        # returns a partial (but otherwise valid) plan.
        if not queries:
            return self._generate_deterministic_fallback(question)

        fallback_by_pass = {
            query.pass_type: query
            for query in self._generate_deterministic_fallback(question).search_queries
        }
        present_passes = {query.pass_type for query in queries}
        for pass_type in PassType:
            if pass_type not in present_passes:
                queries.append(fallback_by_pass[pass_type])

        return ResearchPlan(
            main_question=question,
            research_objectives=objectives,
            sub_questions=[str(sq) for sq in data.get("sub_questions", []) if sq],
            important_concepts=[str(c) for c in data.get("important_concepts", []) if c],
            synonyms=data.get("synonyms", {}) if isinstance(data.get("synonyms"), dict) else {},
            related_terminology=[str(t) for t in data.get("related_terminology", []) if t],
            inclusion_criteria=[str(c) for c in data.get("inclusion_criteria", []) if c],
            exclusion_criteria=[str(c) for c in data.get("exclusion_criteria", []) if c],
            search_queries=queries,
            recent_literature_strategy=data.get("recent_literature_strategy", "Prioritize 2024-2026 works."),
            foundational_literature_strategy=data.get("foundational_literature_strategy", "Analyze foundational works."),
            supporting_evidence_strategy=data.get("supporting_evidence_strategy", "Verify empirical benchmarks."),
            contradiction_falsification_strategy=data.get("contradiction_falsification_strategy", "Search for limitations."),
        )

    def _generate_deterministic_fallback(self, question: str) -> ResearchPlan:
        """Deterministic heuristic plan generator when Ollama is unavailable."""
        # Clean question
        cleaned = re.sub(r"[^\w\s]", " ", question)
        tokens = [w for w in cleaned.split() if len(w) > 2]
        core_phrase = " ".join(tokens[:8]) if tokens else question

        queries = [
            SearchQuery(
                query=core_phrase,
                pass_type=PassType.PASS_A_BROAD,
                target_concept="core methodology",
                rationale="Pass A: Broad discovery across literature",
            ),
            SearchQuery(
                query=f"{core_phrase} deep learning architecture",
                pass_type=PassType.PASS_B_EXPANSION,
                target_concept="architectures",
                rationale="Pass B: Query expansion on algorithmic variants",
            ),
            SearchQuery(
                query=f"{core_phrase} benchmark dataset performance",
                pass_type=PassType.PASS_C_SUPPORTING,
                target_concept="empirical benchmarks",
                rationale="Pass C: Supporting empirical results and metrics",
            ),
            SearchQuery(
                query=f"{core_phrase} limitations challenge failure false positive",
                pass_type=PassType.PASS_D_CONTRADICTION,
                target_concept="limitations and negative results",
                rationale="Pass D: Contradictions, failure modes, and trade-offs",
            ),
            SearchQuery(
                query=core_phrase,
                pass_type=PassType.PASS_E_RECENT,
                target_concept="recent breakthroughs",
                year_start=2024,
                year_end=2026,
                rationale="Pass E: Recent literature 2024-2026",
            ),
            SearchQuery(
                query=core_phrase,
                pass_type=PassType.PASS_F_FOUNDATIONAL,
                target_concept="seminal baselines",
                year_start=2015,
                year_end=2021,
                rationale="Pass F: Foundational seminal baseline works",
            ),
        ]

        return ResearchPlan(
            main_question=question,
            research_objectives=[
                ResearchObjective(objective_id="OBJ-1", description=f"Investigate core methods and architectures for: {question}"),
                ResearchObjective(objective_id="OBJ-2", description="Synthesize empirical comparative benchmarks and identify trade-offs"),
                ResearchObjective(objective_id="OBJ-3", description="Determine unresolved research gaps, failure modes, and future directions"),
            ],
            sub_questions=[
                f"What are the leading architectures and methods proposed for {question}?",
                "What empirical benchmarks and performance metrics characterize these methods?",
                "What are the primary failure cases, domain-shift limitations, and unresolved research gaps?",
            ],
            important_concepts=tokens[:6],
            synonyms={t: [f"{t} methods", f"{t} systems"] for t in tokens[:3]},
            related_terminology=["deep learning", "empirical benchmark", "evaluation metric"],
            inclusion_criteria=[
                "Peer-reviewed journal/conference publications or preprints proposing or evaluating methods for this topic",
                "Articles reporting concrete empirical findings or architectural specifications",
            ],
            exclusion_criteria=[
                "Pure marketing materials, non-technical surveys without depth, or papers with zero empirical evaluation",
            ],
            search_queries=queries,
            recent_literature_strategy="Target 2024-2026 peer-reviewed and preprint advances.",
            foundational_literature_strategy="Trace seminal foundational benchmarks from 2015-2021.",
            supporting_evidence_strategy="Verify quantitative comparative metrics and datasets.",
            contradiction_falsification_strategy="Actively seek negative results, failure modes, and trade-offs.",
        )
