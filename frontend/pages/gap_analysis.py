import streamlit as st
import json
from pathlib import Path
import traceback
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

from backend.skill_matcher import SkillMatcher
from backend.gap_analyzer import GapAnalyzer

TEMPLATES_PATH = Path("config/job_templates.json")


def _load_job_skills(template_key: str) -> List[str]:
    """Load required skills for a job template from config"""
    if not TEMPLATES_PATH.exists():
        logger.warning(f"Templates file not found: {TEMPLATES_PATH}")
        return []
    try:
        templates = json.loads(TEMPLATES_PATH.read_text())
        tpl = templates.get(template_key, {})
        required = tpl.get("required_skills", []) or tpl.get("required", [])
        return required if required else []
    except Exception as e:
        logger.exception(f"Error loading job skills for {template_key}")
        return []


def _run_analysis_and_store(extracted_skills: List[str], selected_job: str) -> Dict[str, Any]:
    """Run skill matching and gap analysis, store results in session state"""
    matcher = SkillMatcher()
    analyzer = GapAnalyzer()
    job_skills = _load_job_skills(selected_job)
    
    if not job_skills:
        st.warning(f"No job skills found for template: {selected_job}")
        return {}
    
    # Match skills
    match_result = matcher.match_all_skills(extracted_skills, job_skills)
    
    # Analyze gaps
    gap = analyzer.analyze_gaps(
        match_result.get("matched", []),
        match_result.get("missing", []),
        match_result.get("weak_matches", [])
    )
    
    # Store in session
    st.session_state.skill_gap = {
        "matched": match_result.get("matched", []),
        "missing": match_result.get("missing", []),
        "weak": match_result.get("weak_matches", []),
        "summary": gap.get("summary", {})
    }
    return st.session_state.skill_gap


def render():
    st.header("Gap Analysis")

    # Debug: display current session values
    st.subheader("Debug — session state")
    st.write({
        "has_resume": bool(st.session_state.get("resume_data")),
        "extracted_skills": st.session_state.get("extracted_skills"),
        "job_selected": st.session_state.get("job_selected"),
        "skill_gap_exists": "skill_gap" in st.session_state
    })

    resume = st.session_state.get("resume_data")
    extracted_skills = st.session_state.get("extracted_skills", [])
    selected_job = st.session_state.get("job_selected")

    if not resume:
        st.info("Please upload a resume first (Upload Resume).")
        return
    if not selected_job:
        st.info("Please select a job template (Select Job).")
        return

    job_skills = _load_job_skills(selected_job)
    st.write(f"Target role: **{selected_job}**")
    st.write(f"Job skills ({len(job_skills)}): {', '.join(job_skills)}")
    st.write(f"Resume skills ({len(extracted_skills)}): {', '.join(extracted_skills) if extracted_skills else 'None'}")

    # If analysis already exists, show button to re-run
    if "skill_gap" in st.session_state:
        if st.button("Re-run Gap Analysis"):
            try:
                with st.spinner("Re-running analysis..."):
                    _run_analysis_and_store(extracted_skills, selected_job)
                    st.success("Gap analysis updated.")
            except Exception as e:
                st.error("Error during analysis — see details below.")
                st.text(traceback.format_exc())
    else:
        # Auto-run if skills and job present to avoid manual click
        if extracted_skills:
            if st.button("Run Gap Analysis"):
                try:
                    with st.spinner("Analyzing skills..."):
                        _run_analysis_and_store(extracted_skills, selected_job)
                        st.success("Gap analysis complete.")
                except Exception as e:
                    st.error("Error during analysis — see details below.")
                    st.text(traceback.format_exc())
        else:
            st.info("No extracted skills found. Add skills in Upload Resume or use 'Save skills' there.")

    # If analysis exists, render results
    skill_gap = st.session_state.get("skill_gap")
    if skill_gap:
        st.subheader("Summary")
        summary = skill_gap.get("summary", {})
        st.write(f"Matched: {summary.get('matched', 0)} • Missing: {summary.get('missing', 0)} • Weak: {summary.get('weak', 0)}")
        st.markdown("---")
        
        st.subheader("Matched skills")
        if skill_gap.get("matched"):
            for m in skill_gap.get("matched"):
                st.write(f"- {m.get('skill')}  → {m.get('matched_to','')}  ({m.get('method','')}, score: {m.get('score','')})")
        else:
            st.write("No exact matches found.")

        st.subheader("Weak matches")
        if skill_gap.get("weak"):
            for w in skill_gap.get("weak"):
                st.write(f"- {w.get('skill')} (fuzzy {w.get('fuzzy_score', w.get('semantic_score',''))})")
        else:
            st.write("None")

        st.subheader("Missing skills (ranked)")
        missing = skill_gap.get("missing", [])
        if missing:
            analyzer = GapAnalyzer()
            ranked = analyzer._rank_missing_skills(missing)
            for r in ranked:
                st.write(f"- {r['skill']} — Priority: {r['priority']} — Importance: {r['importance']}")
        else:
            st.write("No missing skills. Great!")
    else:
        st.info("Run the analysis to see results.")