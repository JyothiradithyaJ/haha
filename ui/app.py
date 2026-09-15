"""Streamlit UI for the real academic research pipeline."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Streamlit executes this file with `ui/` as the script directory. Put the
# repository root first so `app` always means this project's package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
project_root_str = str(PROJECT_ROOT)
if project_root_str in sys.path:
    sys.path.remove(project_root_str)
sys.path.insert(0, project_root_str)

import streamlit as st

from app.agent.ollama_client import OllamaError
from app.agent.researcher import ResearcherAgent
from app.reports.generator import ReportGenerator

st.set_page_config(page_title="Academic Research Agent", page_icon="📚", layout="wide")
st.title("Academic Research Agent")
st.caption("Evidence-grounded multi-pass literature research. Comparative phrasing triggers table mode.")

question = st.text_area(
    "Research question",
    placeholder="What is AI and how is it different about ML? Provide me a table of distinction",
    height=120,
)

if question:
    try:
        from app.agent.planner import ResearchPlanner

        preview_planner = ResearchPlanner()
        understanding = preview_planner.understand_question(question)
        st.session_state["planner_preview"] = understanding
        with st.expander("What I understood", expanded=True):
            st.write("**Entities:**", ", ".join(understanding.entities))
            st.write("**Comparative mode:**", "Yes" if understanding.comparative else "No")
            st.write("**Output format:**", understanding.output_format)
            st.write(
                "**Instructions stripped:**",
                ", ".join(preview_planner.last_stripped_instructions) or "None",
            )
    except Exception as exc:
        st.error(f"Query understanding failed: {exc}")

run = st.button("Run research", type="primary", disabled=not bool(question))

if run:
    progress = st.empty()
    messages = []

    def on_progress(message: str):
        messages.append(message)
        progress.info("\n".join(messages[-8:]))

    try:
        agent = ResearcherAgent(progress_callback=on_progress)
        report = agent.run(question)
        generator = ReportGenerator()
        md_path, json_path = generator.save_report(report)
        st.session_state["report"] = report
        st.session_state["md_path"] = md_path
        st.session_state["json_path"] = json_path
        progress.success("Research complete.")
    except OllamaError as exc:
        st.error(f"Ollama error: {exc}. Start Ollama and ensure the configured model is available.")
    except Exception as exc:
        st.error(f"Research pipeline failed: {exc}")

report = st.session_state.get("report")
if report:
    tabs = st.tabs(["Summary", "Comparison", "Evidence", "Gaps & Limitations", "Full Report", "References"])
    with tabs[0]:
        st.markdown(report.executive_summary)
        st.metric("Relevant papers", len(report.papers))
        st.metric("Claims", len(report.claims))
        st.metric("Research gaps", len(report.research_gaps))
    with tabs[1]:
        if report.comparative:
            if report.comparison_table:
                st.dataframe(report.comparison_table, use_container_width=True, hide_index=True)
            else:
                st.warning("Insufficient evidence retrieved for a fully evidenced comparison table.")
        else:
            st.info("Comparison mode is shown only when the query explicitly requests comparison/distinction.")
    with tabs[2]:
        st.dataframe([e.model_dump() for e in report.evidence_records], use_container_width=True, hide_index=True)
    with tabs[3]:
        st.subheader("Research gaps")
        for gap in report.research_gaps:
            st.markdown(f"**{gap.gap_id} — {gap.category.value}**\n\n{gap.description}")
        st.subheader("Limitations")
        for item in report.limitations_in_existing_research:
            st.markdown(f"- {item}")
    with tabs[4]:
        md_path = st.session_state["md_path"]
        st.markdown(Path(md_path).read_text(encoding="utf-8"))
    with tabs[5]:
        for p in report.papers:
            st.markdown(f"**[{p.internal_id}]** {p.title} — {p.year or 'N/A'}")
