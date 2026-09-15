# Lightweight Academic Research Agent

An evidence-grounded academic research agent that transforms complex research questions into rigorous, verified literature reviews and contradiction-aware research reports.

Built with **pure Python**, **local Ollama (`qwen3.5:4b`)**, and **deterministic academic API retrieval**.

---

## Key Features

1. **Strict Anti-Hallucination & Provenance**:
   - The local LLM is **never** the source of truth for citations, DOIs, paper records, or empirical metrics.
   - Deterministic Python code controls all API calls, paper normalization, deduplication, citation mapping (`[P01]`, `[P02]`), and source verification.
   - Citations in the final report map directly to actual retrieved literature records.
2. **Deterministic Academic Sources**:
   - **OpenAlex Works REST API** (with inverted-index abstract reconstruction)
   - **Semantic Scholar Graph API**
   - **Crossref Works API** (official DOI registry)
   - **PubMed / NCBI E-utilities** (biomedical literature)
   - **arXiv Atom API** (preprints)
   - **CORE API v3** (open access repositories)
3. **Multi-Pass Search & Active Contradiction Falsification**:
   - **Pass A**: Broad discovery across key concepts
   - **Pass B**: Query expansion covering methodology, acronyms, and synonyms
   - **Pass C**: Supporting empirical evidence and benchmark verification
   - **Pass D**: Contradiction, failure modes, limitations, and negative results
   - **Pass E**: Recent literature (2024–2026)
   - **Pass F**: Foundational seminal baselines (2015–2021)
4. **Deterministic Deduplication & Transparent Multi-Factor Ranking**:
   - Multi-tier deduplication priority: `DOI > PubMed ID > arXiv ID > Semantic Scholar ID > OpenAlex ID > Normalized Title + Author + Year`.
   - Inspectable scoring breakdown across title match, abstract match, concept coverage, recency, quality tier (Tier 1 peer-reviewed vs Tier 2 preprint), and citation count.
5. **Classified Research Gap Detection**:
   - Unresolved research gaps categorized into standard scientific taxonomies (`robustness gap`, `deployment gap`, `generalization gap`, `benchmark gap`, `computational-efficiency gap`, etc.) supported by cited literature.
6. **Zero Heavy Infrastructure**:
   - No vector databases, no Docker, no Redis, no Celery, no bloated UI frameworks. Pure Python with `httpx`, `pydantic`, and `pytest`.

---

## Architecture Overview

```
academic-research-agent/
│
├── app/
│   ├── agent/
│   │   ├── ollama_client.py     # Local Ollama client (qwen3.5:4b) with health checks & fallback
│   │   ├── planner.py           # Multi-pass research planner (Passes A–F)
│   │   ├── prompts.py           # Structured prompt templates for local LLM
│   │   ├── researcher.py        # Autonomous research loop orchestrator with stop conditions
│   │   └── synthesizer.py       # Synthesis engine, research gap classifier, report builder
│   │
│   ├── sources/
│   │   ├── base.py              # AcademicSource base class & normalizers (DOI, arXiv, title)
│   │   ├── openalex.py          # OpenAlex Works API client
│   │   ├── semantic_scholar.py  # Semantic Scholar Graph API client
│   │   ├── crossref.py          # Crossref Works API client
│   │   ├── pubmed.py            # NCBI E-utilities (esearch + efetch) client
│   │   ├── arxiv.py             # arXiv Atom XML API client
│   │   └── core.py              # CORE API v3 client
│   │
│   ├── retrieval/
│   │   ├── deduplication.py     # Deterministic 6-tier paper deduplication & metadata fusion
│   │   ├── ranking.py           # Multi-factor transparent scoring & ID assignment ([P01]...)
│   │   └── search.py            # Concurrent multi-source search dispatcher with rate limits
│   │
│   ├── evidence/
│   │   ├── claims.py            # Claim extractor (empirical, methodological, limitation)
│   │   ├── evidence.py          # Traceable evidence mapping (claim -> evidence -> paper -> source)
│   │   └── contradictions.py    # Contradiction matrix & trade-off analysis
│   │
│   ├── verification/
│   │   └── bibliography.py      # Cross-registry bibliographic verification
│   │
│   ├── reports/
│   │   └── generator.py         # 16-section Markdown & JSON report generator
│   │
│   ├── models/
│   │   └── schemas.py           # Comprehensive Pydantic data models
│   │
│   └── config.py                # Environment configuration loader (.env)
│
├── skills/
│   └── academic-research/
│       └── SKILL.md             # Epistemic research methodology and protocol
│
├── tests/
│   ├── test_schemas.py          # Pydantic schema validation tests
│   ├── test_deduplication.py    # Identity matching & metadata fusion tests
│   ├── test_ranking.py          # Scoring factors, recency vs foundational tests
│   ├── test_sources.py          # Mocked HTTP tests for all academic sources
│   ├── test_ollama.py           # Ollama health, errors, & JSON extraction tests
│   └── test_research_pipeline.py# End-to-end integration test
│
├── .env.example
├── requirements.txt
├── README.md
└── main.py                      # Interactive CLI entrypoint
```

---

## Installation & Setup

### 1. Python Environment

Ensure Python 3.10+ is installed (tested on Python 3.14):

```bash
# Clone or navigate to the repository
cd my_agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Ollama & Qwen3.5 4B Setup

This project uses **Ollama** as the local LLM runtime with `qwen3.5:4b`.

1. Download and install Ollama from [https://ollama.com](https://ollama.com).
2. Start the Ollama server:
   ```bash
   ollama serve
   ```
3. Pull the required model:

   ```bash
   ollama pull qwen3.5:4b
   ```

   _(Note: As an intentional safety guard, the application will **never** automatically download models)._

4. Verify your local Ollama connection:
   ```bash
   python main.py --verify-ollama
   ```

### 3. Environment Configuration

Copy the example configuration:

```bash
cp .env.example .env
```

Edit `.env` as needed:

```ini
# Local Ollama LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b

# Academic API Configuration (Optional keys for higher rate limits)
SEMANTIC_SCHOLAR_API_KEY=
CORE_API_KEY=
NCBI_API_KEY=

# OpenAlex email identification (recommended for faster polite pool response)
OPENALEX_EMAIL=user@example.com

# Agent Search & Execution Controls
SEARCH_TIMEOUT_SECONDS=15
MAX_SEARCH_RESULTS_PER_SOURCE=10
MAX_RESEARCH_ITERATIONS=6
MAX_PAPERS_TOTAL=30
```

---

## Usage

### Run an Academic Research Question

Run the CLI with a research question enclosed in quotes:

```bash
python main.py "Compare recent deep-learning methods for industrial defect detection and identify the major unresolved research gaps."
```

### Interactive Mode

Simply run without arguments to enter interactive mode:

```bash
python main.py
```

### Fast Offline Verification Mode

Test the complete end-to-end pipeline offline without external network dependency using realistic fixtures:

```bash
python main.py "Compare recent deep-learning methods for industrial defect detection" --mock
```

### CLI Options

| Option             | Description                                  | Default                       |
| :----------------- | :------------------------------------------- | :---------------------------- |
| `question`         | Positional research question string          | Interactive prompt if omitted |
| `--verify-ollama`  | Diagnostic check of Ollama and model         | —                             |
| `--mock`           | Run offline with synthetic academic fixtures | `False`                       |
| `--iterations <N>` | Maximum search iterations                    | `6`                           |
| `--max-papers <N>` | Maximum ranked papers to analyze             | `30`                          |

---

## Final Report Structure

Every generated report contains the complete 16 required sections:

1. **Research Question**: The exact decomposed query.
2. **Executive Summary**: High-level synthesis of findings and current paradigms.
3. **Research Methodology**: Epistemic protocol and search procedure.
4. **Academic Sources Searched**: Exhaustive list of queried registries.
5. **Search Strategy**: Breakdown of executed queries across Passes A–F.
6. **Key Findings**: Core substantive findings with traceable citations `[Pxx]`.
7. **Evidence Table**: Traceable mapping connecting Evidence ID, Claim ID, Paper ID, and verbatim excerpts.
8. **Supporting Evidence**: Corroborated claims with strength heuristics (`VERY STRONG`, `STRONG`, `MODERATE`, etc.).
9. **Contradictory Evidence & Scientific Disagreements**: Detailed matrix of conflicting results and trade-offs.
10. **Method / Approach Comparison**: Comprehensive table of architectures, venues, citations, and quality tiers.
11. **Limitations in Existing Research**: Concrete constraints identified by authors.
12. **Classified Research Gaps**: Gaps classified by taxonomy (`robustness gap`, `deployment gap`, etc.) with future directions.
13. **Open Research Questions**: Unresolved sub-questions.
14. **Evidence Strength & Uncertainty Evaluation**: Epistemic confidence and uncertainty assessment.
15. **Conclusion**: Strategic perspective on the domain.
16. **References**: Authoritative bibliography of all retrieved papers with clickable DOIs and source registry tags.

Reports are saved automatically to `reports/`:

- Markdown report: `reports/research_<timestamp>.md`
- Structured JSON data: `reports/research_<timestamp>.json`

---

## Running the Test Suite

Run all unit and integration tests:

```bash
python -m pytest tests/ -v -p no:cacheprovider
```

The test suite includes:

- `test_schemas.py`: Pydantic validation and serialization.
- `test_deduplication.py`: DOI, arXiv, title, and multi-source fusion.
- `test_ranking.py`: Multi-factor transparent scoring and recency balancing.
- `test_sources.py`: Mocked HTTP responses for OpenAlex, Semantic Scholar, Crossref, PubMed, arXiv, CORE.
- `test_ollama.py`: Connection error handling, missing model diagnostics, and JSON extraction.
- `test_research_pipeline.py`: Full end-to-end integration pipeline verification.

---

## Anti-Hallucination Guarantees

1. **Zero Citation Invention**: Every `[Pxx]` citation maps strictly to a paper in the retrieved evidence set.
2. **Deterministic Metadata**: Authors, titles, venues, DOIs, and citations are parsed directly from official API responses.
3. **Deterministic Deduplication**: Multiple database records of the same paper are merged preserving all source references.
4. **Active Falsification**: The agent explicitly executes counter-evidence and limitation queries (Pass D) to prevent confirmation bias.

---

## Limitations & Future Extensions

- **Full PDF Parsing**: V1 focuses on abstracts, metadata, and structured API summaries. Modular PDF full-text extraction can be added as a future layer.
- **Optional Embeddings**: Designed to integrate local embeddings (such as `nomic-embed-text`) in V2 without modifying the source abstraction layer.
