"""Research planner driven by the explicit query-understanding stage."""
from __future__ import annotations

import logging
import re
from typing import Any

from app.models.schemas import ResearchPlan, ResearchObjective, SearchQuery, PassType, QueryUnderstanding
from app.agent.ollama_client import OllamaClient
from app.agent.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE
from app.agent.query_understanding import QueryUnderstandingService

logger = logging.getLogger(__name__)


class ResearchPlanner:
    """Create validated plans from substantive entities, never from formatting instructions."""

    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()
        self.query_understanding = QueryUnderstandingService(self.client)
        self.last_understanding: QueryUnderstanding | None = None
        self.last_stripped_instructions: list[str] = []
        self.last_cleaned_question: str = ""

    def understand_question(self, question: str) -> QueryUnderstanding:
        understanding, instructions, cleaned = self.query_understanding.understand(question)
        self.last_understanding = understanding
        self.last_stripped_instructions = instructions
        self.last_cleaned_question = cleaned
        logger.info("Understood entities=%s comparative=%s output=%s", understanding.entities, understanding.comparative, understanding.output_format)
        return understanding

    def create_plan(self, question: str) -> ResearchPlan:
        understanding = self.understand_question(question)
        entity_text = " AND ".join(understanding.entities)
        user_prompt = PLANNER_USER_TEMPLATE.format(question=entity_text)
        try:
            raw_json = self.client.generate_json(prompt=user_prompt, system_prompt=PLANNER_SYSTEM_PROMPT, temperature=0.1)
            if not isinstance(raw_json, dict):
                raise ValueError("Planner returned non-object JSON")
            plan = self._coerce_to_plan(question, raw_json, understanding)
        except Exception as exc:
            logger.warning("LLM planning failed after query understanding: %s", exc)
            plan = self._generate_deterministic_fallback(question, understanding)
        return plan

    def _coerce_to_plan(self, question: str, data: dict[str, Any], understanding: QueryUnderstanding) -> ResearchPlan:
        objectives = [
            ResearchObjective(objective_id=o.get("objective_id", f"OBJ-{i+1}"), description=o["description"])
            for i, o in enumerate(data.get("research_objectives", []))
            if isinstance(o, dict) and o.get("description")
        ] or [ResearchObjective(objective_id="OBJ-1", description=f"Investigate {', '.join(understanding.entities)}")]

        queries: list[SearchQuery] = []
        for item in data.get("search_queries", []):
            if not isinstance(item, dict) or not item.get("query"):
                continue
            try:
                pt = PassType(str(item.get("pass_type", "broad")).lower())
            except ValueError:
                pt = PassType.PASS_A_BROAD
            queries.append(SearchQuery(
                query=item["query"].strip(), pass_type=pt,
                target_concept=str(item.get("target_concept", "general")),
                year_start=item.get("year_start"), year_end=item.get("year_end"),
                rationale=str(item.get("rationale", "")),
            ))

        if not queries:
            return self._generate_deterministic_fallback(question, understanding)

        # Ensure every research pass is represented. This keeps partial LLM plans
        # compatible with the full A-G retrieval strategy.
        fallback = self._generate_deterministic_fallback(question, understanding).search_queries
        by_pass = {q.pass_type: q for q in fallback}
        present = {q.pass_type for q in queries}
        for pt in PassType:
            if pt not in present and pt in by_pass:
                queries.append(by_pass[pt])

        return ResearchPlan(
            main_question=question,
            research_objectives=objectives,
            sub_questions=[str(x) for x in data.get("sub_questions", []) if x],
            important_concepts=understanding.entities,
            synonyms={e: self.query_understanding.search_terms(understanding) for e in understanding.entities},
            related_terminology=[str(x) for x in data.get("related_terminology", []) if x],
            inclusion_criteria=[str(x) for x in data.get("inclusion_criteria", []) if x],
            exclusion_criteria=[str(x) for x in data.get("exclusion_criteria", []) if x],
            search_queries=queries,
            recent_literature_strategy=data.get("recent_literature_strategy", "Prioritize recent literature."),
            foundational_literature_strategy=data.get("foundational_literature_strategy", "Trace foundational literature."),
            supporting_evidence_strategy=data.get("supporting_evidence_strategy", "Verify empirical evidence."),
            contradiction_falsification_strategy=data.get("contradiction_falsification_strategy", "Seek limitations and negative findings."),
            entities=understanding.entities,
            comparative=understanding.comparative,
            output_format=understanding.output_format,
            stripped_instructions=self.last_stripped_instructions,
        )

    @staticmethod
    def _comparison_entities(entities: list[str], cleaned_question: str) -> list[str]:
        """Return two conservative comparison subjects when the LLM gives one broad entity."""
        if len(entities) >= 2:
            return entities

        topic = entities[0] if entities else cleaned_question.strip()
        text = re.sub(r"\s+", " ", cleaned_question).strip()

        # Common comparative constructions: X vs Y / X versus Y / between X and Y.
        match = re.search(r"\b(.+?)\s+(?:vs\.?|versus|against)\s+(.+)$", text, re.IGNORECASE)
        if match:
            parts = [match.group(1).strip(" ,.:;"), match.group(2).strip(" ,.:;")]
            if all(parts):
                return parts

        match = re.search(r"\bbetween\s+(.+?)\s+and\s+(.+?)(?:\s+(?:for|to|that|which)\b|$)", text, re.IGNORECASE)
        if match:
            parts = [match.group(1).strip(" ,.:;"), match.group(2).strip(" ,.:;")]
            if all(parts):
                return parts

        # For "compare X methods for Y", separate the method family from its domain.
        match = re.search(r"^(.+?\bmethods?)\s+for\s+(.+)$", text, re.IGNORECASE)
        if match:
            left = match.group(1).strip(" ,.:;")
            right = match.group(2).strip(" ,.:;")
            right = re.sub(r"\b(?:and|identify)\b.*$", "", right, flags=re.IGNORECASE).strip(" ,.:;")
            if left and right:
                return [left, right]

        # Safe fallback: preserve the single topic instead of indexing into a
        # nonexistent second entity. The planner can still execute all passes.
        return [topic]

    def _generate_deterministic_fallback(self, question: str, understanding: QueryUnderstanding) -> ResearchPlan:
        entities = self._comparison_entities(understanding.entities, self.last_cleaned_question or question)
        topic = " AND ".join(entities)
        queries: list[SearchQuery] = []
        templates = [
            (PassType.PASS_A_BROAD, topic, "core literature"),
            (PassType.PASS_B_EXPANSION, f"{topic} methods architectures", "methodology"),
            (PassType.PASS_C_SUPPORTING, f"{topic} benchmark performance evaluation", "empirical evidence"),
            (PassType.PASS_D_CONTRADICTION, f"{topic} limitations failure modes robustness", "limitations"),
            (PassType.PASS_E_RECENT, topic, "recent advances"),
            (PassType.PASS_F_FOUNDATIONAL, topic, "foundational literature"),
        ]
        for pt, query, concept in templates:
            queries.append(SearchQuery(
                query=query,
                pass_type=pt,
                target_concept=concept,
                year_start=2024 if pt == PassType.PASS_E_RECENT else (2015 if pt == PassType.PASS_F_FOUNDATIONAL else None),
                year_end=2026 if pt == PassType.PASS_E_RECENT else (2021 if pt == PassType.PASS_F_FOUNDATIONAL else None),
                rationale=f"{pt.value} search for substantive entities.",
            ))

        # Pass G is part of the complete A-G planner contract. When the query is
        # not comparative, it still provides a neutral comparative/alternatives
        # search rather than being omitted from a partial plan.
        if understanding.comparative and len(entities) >= 2:
            comparative_query = f'"{entities[0]}" "{entities[1]}" comparison'
        else:
            comparative_query = f"{topic} alternatives comparison"
        queries.append(SearchQuery(
            query=comparative_query,
            pass_type=PassType.PASS_G_COMPARATIVE,
            target_concept="direct comparison" if understanding.comparative else "comparative alternatives",
            rationale="Comparative evidence pass in the complete A-G retrieval strategy.",
        ))

        return ResearchPlan(
            main_question=question,
            research_objectives=[
                ResearchObjective(objective_id="OBJ-1", description=f"Investigate {topic}"),
                ResearchObjective(objective_id="OBJ-2", description="Identify evidence, trade-offs, and gaps"),
            ],
            sub_questions=[f"What are the defining characteristics of {topic}?", f"What evidence distinguishes the entities?"],
            important_concepts=understanding.entities,
            synonyms={e: self.query_understanding.search_terms(understanding) for e in understanding.entities},
            related_terminology=[],
            inclusion_criteria=["Academic publications directly relevant to the extracted entities"],
            exclusion_criteria=["Records with no substantive relevance to the extracted entities"],
            search_queries=queries,
            recent_literature_strategy="Target recent evidence.",
            foundational_literature_strategy="Trace foundational evidence.",
            supporting_evidence_strategy="Verify empirical evidence.",
            contradiction_falsification_strategy="Seek contradictory evidence and failure modes.",
            entities=understanding.entities,
            comparative=understanding.comparative,
            output_format=understanding.output_format,
            stripped_instructions=self.last_stripped_instructions,
        )
