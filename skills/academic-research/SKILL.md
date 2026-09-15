---
name: academic-research
description: Methodology, protocols, and epistemic principles for rigorous, evidence-grounded academic research and literature synthesis.
---

# Academic Research Methodology & Protocol

This skill codifies the core scientific principles, retrieval standards, epistemic safeguards, and anti-hallucination protocols governing the Academic Research Agent.

## Core Epistemic Principles

### 1. Evidence Over Intuition

- The local language model (Qwen3.5 4B) must **never** be treated as the ground truth of scientific facts, empirical metrics, or bibliographic records.
- All factual claims in final research outputs must derive strictly from retrieved and verified literature artifacts.
- If a specific metric, hyperparameter, or dataset is not found in the retrieved literature, explicitly state that it is unavailable rather than generating a plausible approximation.

### 2. Source Traceability & Bracketed Identifiers

- Every substantive claim must be traceable to one or more retrieved paper identifiers (e.g., `[P01]`, `[P02]`).
- The internal pipeline maintains an unbroken provenance graph:
  $$\text{Claim} \longrightarrow \text{Evidence Record} \longrightarrow \text{Paper} \longrightarrow \text{Source API}$$
- Citations must match the retrieved literature set exactly. Never cite an unretrieved or imagined paper.

### 3. Multi-Source Independent Confirmation

- A single preprint or isolated conference abstract is considered provisional (`MODERATE` or `WEAK` strength).
- Scientific findings require corroboration across multiple independent publication venues and registries (e.g., Crossref, OpenAlex, Semantic Scholar, PubMed, arXiv).
- When available, preference is given to Tier 1 records (peer-reviewed journal and proceedings with registered DOIs).

### 4. Active Contradiction & Falsification (Pass D)

- Scientific research is inherently falsification-driven. Never search exclusively for confirmatory evidence.
- Every research cycle must execute an explicit contradiction search pass targeting:
  - Negative results and failure cases
  - Scalability, latency, and memory bottlenecks
  - Performance degradation under domain shift and out-of-distribution textures
  - Direct disagreements or disputed baselines
- Construct a dedicated contradiction matrix rather than forcing false consensus.

### 5. Uncertainty & Epistemic Humility

- Explicitly categorize evidence strength:
  - **VERY STRONG**: Multi-source empirical consensus across peer-reviewed publications without significant contradiction.
  - **STRONG**: Independent corroboration across verified sources with minor caveats.
  - **MODERATE**: Single verified publication or preprints with consistent findings.
  - **WEAK**: Heavily contested findings, preliminary preprints, or narrow evaluation scopes.
  - **INSUFFICIENT**: Incomplete metadata, unverified claims, or severe conflicting evidence.
- Clearly communicate limitations, sample size constraints, and domain boundaries.

### 6. Bibliographic Verification & Anti-Hallucination

- Never fabricate:
  - DOIs
  - Author lists
  - Journal/conference venues
  - Empirical benchmarks or tables
- Normalization rules:
  - DOIs must be normalized by removing URI prefixes (`https://doi.org/`) and converted to lowercase.
  - Titles must be normalized by stripping punctuation and whitespace before duplicate resolution.
- When independent registries disagree on minor metadata (e.g., preprint year vs journal publication year), preserve the discrepancy transparently.

### 7. Distinguishing Key Epistemic Categories

- **Evidence vs. Interpretation**: Clearly distinguish raw empirical results reported by authors from higher-level survey interpretations.
- **Correlation vs. Causation**: Do not frame statistical correlations observed in benchmark evaluations as causal mechanisms without theoretical justification.
- **Established vs. Emerging Findings**: Maintain a deliberate balance between foundational seminal works (2015–2021) and cutting-edge recent breakthroughs (2024–2026).

### 8. Rigorous Research Gap Classification

- Reject platitudes such as "more research is needed".
- Classify unresolved research gaps into concrete taxonomies:
  - `robustness gap`
  - `deployment gap`
  - `generalization gap`
  - `dataset gap`
  - `computational-efficiency gap`
  - `evaluation gap`
  - `benchmark gap`
  - `reproducibility gap`
- Every identified gap must cite specific papers demonstrating the limitation and specify concrete future research directions.
