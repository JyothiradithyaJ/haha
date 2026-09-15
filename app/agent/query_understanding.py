"""Explicit query-understanding stage for separating research entities from output instructions."""
from __future__ import annotations

import logging
import re

from pydantic import ValidationError

from app.agent.ollama_client import OllamaClient
from app.models.schemas import QueryUnderstanding

logger = logging.getLogger(__name__)

INSTRUCTION_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bprovide\s+(?:me\s+)?a\s+table\s+of\s+distinction\b", "provide a table of distinction"),
    (r"\bprovide\s+(?:me\s+)?a\s+table\b", "provide a table"),
    (r"\bin\s+a\s+tabular\s+(?:column|format)\b", "use tabular format"),
    (r"\bcompare\b", "compare"),
    (r"\bcomparison\b", "comparison"),
    (r"\bdistinguish\b", "distinguish"),
    (r"\bdistinction\b", "distinction"),
    (r"\bexplain\b", "explain"),
    (r"\bsummar(?:ize|ise)\b", "summarize"),
    (r"\blist\b", "list"),
    (r"\btable\b", "table"),
)

COMMON_ENTITY_ALIASES: dict[str, tuple[str, ...]] = {
    "ai": ("AI", "Artificial Intelligence"),
    "artificial intelligence": ("AI", "Artificial Intelligence"),
    "ml": ("ML", "Machine Learning"),
    "machine learning": ("ML", "Machine Learning"),
}

# Words that describe the question/task rather than the research subject.
FALLBACK_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "being", "been",
    "how", "what", "why", "when", "where", "which", "who", "does", "do", "did",
    "can", "could", "should", "would", "will", "about", "for", "to", "of", "in",
    "on", "with", "and", "or", "as", "by", "from", "into", "than", "that",
    "this", "these", "those", "it", "its", "their", "them", "me", "you", "we",
    "recent", "latest", "major", "unresolved", "identify", "discuss", "describe",
    "research", "gap", "gaps", "work", "methods", "method", "approach", "approaches",
}

SYSTEM_PROMPT = """You are a strict academic query-understanding component. Extract only substantive research entities from the user's question. Ignore formatting and answer instructions. Never treat words such as table, explain, compare, list, what, how, distinction, or summarize as research entities. Return only valid JSON matching the requested schema."""

USER_TEMPLATE = """Understand this academic research request.

Raw question:
{question}

Return exactly this JSON shape:
{{"entities": ["entity 1", "entity 2"], "comparative": true, "output_format": "comparison_table"}}

Rules:
- entities are the actual topics/entities to research, not instruction words.
- comparative is true only when the user explicitly asks to compare, distinguish, contrast, or produce a distinction/comparison table.
- output_format should be one of: report, comparison_table, list, summary.
"""


class QueryUnderstandingError(RuntimeError):
    """Raised when query understanding cannot be validated."""


class QueryUnderstandingService:
    def __init__(self, client: OllamaClient | None = None, max_retries: int = 2):
        self.client = client or OllamaClient()
        self.max_retries = max_retries

    @staticmethod
    def strip_instructions(question: str) -> tuple[str, list[str]]:
        cleaned = question
        stripped: list[str] = []
        for pattern, label in INSTRUCTION_PATTERNS:
            if re.search(pattern, cleaned, flags=re.IGNORECASE):
                stripped.append(label)
                cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,:;?!")
        return cleaned, list(dict.fromkeys(stripped))

    @staticmethod
    def _normalize_entities(entities: list[str]) -> list[str]:
        normalized: list[str] = []
        for entity in entities:
            value = entity.strip()
            if not value:
                continue
            low = value.lower()
            canonical = COMMON_ENTITY_ALIASES.get(low, (value,))[0]
            if canonical not in normalized:
                normalized.append(canonical)
        return normalized

    def _deterministic_entity_aliases(self, cleaned: str) -> list[str]:
        found: list[str] = []
        lower = cleaned.lower()
        # Longer aliases first so "machine learning" is recognized before "ml".
        for key in sorted(COMMON_ENTITY_ALIASES, key=len, reverse=True):
            aliases = COMMON_ENTITY_ALIASES[key]
            if re.search(rf"\b{re.escape(key)}\b", lower):
                canonical = aliases[0]
                if canonical not in found:
                    found.append(canonical)
        return found

    @staticmethod
    def _deterministic_generic_entity(cleaned: str) -> list[str]:
        """Recover a conservative topic when the LLM is unavailable or returns the wrong schema."""
        text = re.sub(r"[-_/]", " ", cleaned.lower())
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = [token for token in text.split() if token not in FALLBACK_STOPWORDS]
        if not tokens:
            return []

        # Keep a short, search-friendly noun/topic phrase rather than using the raw question.
        phrase = " ".join(tokens[:8]).strip()
        return [phrase] if phrase else []

    def understand(self, question: str) -> tuple[QueryUnderstanding, list[str], str]:
        if not question or not question.strip():
            raise QueryUnderstandingError("Research question is empty")
        cleaned, instructions = self.strip_instructions(question)
        if not cleaned:
            raise QueryUnderstandingError("No research subject remains after instruction stripping")
        logger.info("Query understanding stripped instructions: %s", instructions)

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                raw = self.client.generate_json(
                    prompt=USER_TEMPLATE.format(question=question),
                    system_prompt=SYSTEM_PROMPT,
                    temperature=0.0,
                )
                result = QueryUnderstanding.model_validate(raw)
                result.entities = self._normalize_entities(result.entities)
                if not result.entities:
                    raise QueryUnderstandingError("LLM returned no substantive research entities")
                return result, instructions, cleaned
            except (ValidationError, QueryUnderstandingError, Exception) as exc:
                last_error = exc
                logger.warning("Query understanding validation attempt %d failed: %s", attempt + 1, exc)

        aliases = self._deterministic_entity_aliases(cleaned)
        entities = aliases or self._deterministic_generic_entity(cleaned)
        if entities:
            lower_question = question.lower()
            comparative = any(
                re.search(rf"\b{re.escape(word)}\b", lower_question)
                for word in ("compare", "comparison", "distinction", "distinguish", "contrast")
            )
            output_format = "comparison_table" if comparative else "report"
            return QueryUnderstanding(
                entities=entities,
                comparative=comparative,
                output_format=output_format,
            ), instructions, cleaned

        raise QueryUnderstandingError(f"Unable to validate query understanding: {last_error}")

    def search_terms(self, understanding: QueryUnderstanding) -> list[str]:
        terms: list[str] = []
        for entity in understanding.entities:
            low = entity.lower()
            aliases = COMMON_ENTITY_ALIASES.get(low, (entity,))
            for term in aliases:
                if term not in terms:
                    terms.append(term)
        return terms
