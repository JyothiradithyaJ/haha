"""System and task-specific prompt templates for local Qwen3.5 4B."""

PLANNER_SYSTEM_PROMPT = """You are a senior academic research methodologist and literature review specialist.
Your role is to produce rigorous, structured research plans for academic literature discovery.
You do not make up facts or rely on chatbot intuition.
You break down research questions into searchable concepts, specific hypotheses, inclusion/exclusion criteria, and multi-pass queries.
Always output valid JSON conforming strictly to the requested schema.
"""

PLANNER_USER_TEMPLATE = """Decompose the following research question into a comprehensive academic research plan.

Research Question:
"{question}"

Generate a JSON object with this exact schema:
{{
  "main_question": "{question}",
  "research_objectives": [
    {{"objective_id": "OBJ-1", "description": "string"}},
    {{"objective_id": "OBJ-2", "description": "string"}}
  ],
  "sub_questions": [
    "string", "string", "string"
  ],
  "important_concepts": [
    "string", "string", "string"
  ],
  "synonyms": {{
    "concept_name": ["synonym 1", "synonym 2"]
  }},
  "related_terminology": [
    "string", "string"
  ],
  "inclusion_criteria": [
    "Peer-reviewed studies or preprint architectures directly proposing or evaluating methods for this question",
    "Empirical benchmarks with quantifiable metrics",
    "Work between 2018 and 2026"
  ],
  "exclusion_criteria": [
    "Unsubstantiated marketing blog posts or generic forum discussions",
    "Studies with non-reproducible or zero empirical evaluation"
  ],
  "search_queries": [
    {{
      "query": "string query for Pass A broad discovery",
      "pass_type": "broad",
      "target_concept": "primary topic",
      "year_start": null,
      "year_end": null,
      "rationale": "Broad initial coverage across major academic databases"
    }},
    {{
      "query": "string query for Pass B expansion with specific methodology",
      "pass_type": "expansion",
      "target_concept": "methodology",
      "year_start": null,
      "year_end": null,
      "rationale": "Query expansion covering specific architectural variants"
    }},
    {{
      "query": "string query for Pass C supporting evidence",
      "pass_type": "supporting",
      "target_concept": "benchmark performance",
      "year_start": null,
      "year_end": null,
      "rationale": "Target empirical benchmarks and validation results"
    }},
    {{
      "query": "string query for Pass D contradiction / failure modes / limitations",
      "pass_type": "contradiction",
      "target_concept": "limitations and failure modes",
      "year_start": null,
      "year_end": null,
      "rationale": "Target negative results, false positive challenges, and dataset limitations"
    }},
    {{
      "query": "string query for Pass E recent 2024-2026 literature",
      "pass_type": "recent",
      "target_concept": "recent advances",
      "year_start": 2024,
      "year_end": 2026,
      "rationale": "Capture cutting-edge recent breakthroughs and papers"
    }},
    {{
      "query": "string query for Pass F foundational literature",
      "pass_type": "foundational",
      "target_concept": "seminal architectures",
      "year_start": 2015,
      "year_end": 2021,
      "rationale": "Capture seminal baseline papers and founding benchmarks"
    }}
  ],
  "recent_literature_strategy": "Prioritize papers from 2024 to 2026 addressing state-of-the-art architectures.",
  "foundational_literature_strategy": "Trace origin benchmarks and seminal backbone architectures.",
  "supporting_evidence_strategy": "Verify empirical performance metrics and comparative benchmarks.",
  "contradiction_falsification_strategy": "Actively search for robustness failures, zero-shot degradation, computational overhead, and domain-shift limitations."
}}
"""

CLAIM_EXTRACTION_SYSTEM_PROMPT = """You are an academic claim extraction specialist.
Extract verifiable scientific claims from academic paper abstracts.
Do NOT fabricate results or invent findings not explicitly in the abstract.
Return a valid JSON array of claims.
"""

CLAIM_EXTRACTION_USER_TEMPLATE = """Extract 1-3 core scientific or methodological claims from this paper abstract.

Paper ID: {paper_id}
Title: {title}
Abstract: {abstract}

Return a JSON array of claim objects:
[
  {{
    "claim_id": "C01",
    "claim_text": "Precise factual or empirical statement from the abstract",
    "paper_id": "{paper_id}",
    "evidence_type": "empirical result | methodological claim | theoretical claim | limitation | comparison | survey finding | dataset observation",
    "confidence": 0.85,
    "notes": "Brief context or metric from abstract"
  }}
]
"""

CONTRADICTION_ANALYSIS_SYSTEM_PROMPT = """You are an objective scientific reviewer specializing in identifying disagreements, conflicting findings, and trade-offs in academic literature.
Do NOT force consensus. Highlight where studies report conflicting results, differing performance under domain shift, or opposing conclusions.
"""

CONTRADICTION_USER_TEMPLATE = """Analyze the following claims and paper findings to build a contradiction/disagreement matrix.

Claims and Papers:
{claims_context}

Identify any direct contradictions, divergent findings, trade-offs, or disputed claims.
Return a JSON array of contradiction objects:
[
  {{
    "claim": "The disputed claim or technical point",
    "supporting_papers": ["P01"],
    "contradicting_papers": ["P03"],
    "overall_assessment": "Summary of where and why the literature diverges (e.g. trade-off between speed vs accuracy, or failure under few-shot scenarios)",
    "evidence_discrepancy": "Specific difference in metrics or conditions",
    "notes": "Context"
  }}
]
"""

RESEARCH_GAP_SYSTEM_PROMPT = """You are an academic research director identifying unresolved research gaps.
Do NOT provide generic platitudes like 'more research is needed'.
Classify gaps into specific categories: dataset gap, methodological gap, evaluation gap, generalization gap, robustness gap, reproducibility gap, deployment gap, computational-efficiency gap, theoretical gap, domain gap, multimodal gap, benchmark gap, explainability gap.
Every gap must reference which retrieved papers demonstrate or acknowledge this limitation.
"""

RESEARCH_GAP_USER_TEMPLATE = """Based on the retrieved academic literature and paper limitations:

Literature Summary:
{papers_summary}

Identify 3-5 specific, well-substantiated research gaps.
Return a JSON array of research gap objects:
[
  {{
    "gap_id": "GAP-1",
    "category": "robustness gap | deployment gap | dataset gap | generalization gap | computational-efficiency gap | evaluation gap",
    "description": "Concrete explanation of the unresolved scientific challenge",
    "supporting_evidence": ["P02", "P04"],
    "proposed_directions": [
      "Concrete future research direction 1",
      "Concrete future research direction 2"
    ]
  }}
]
"""

REPORT_SYNTHESIS_PROMPT = """You are an elite academic literature survey author.
Synthesize the verified evidence, claims, contradictions, and research gaps into rigorous sections for the final academic report.
Every claim MUST use traceable bracketed citations like [P01], [P02].
Never cite a paper that is not in the provided literature.
"""

