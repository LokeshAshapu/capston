import streamlit as st
import json
from pathlib import Path

def _load_templates():
    p = Path("config/job_templates.json")
    if p.exists():
        return list(json.loads(p.read_text()).keys())
    return ["software_engineer", "data_scientist", "product_manager", "devops_engineer"]

def render():
    st.header("Select Job Template")
    templates = _load_templates()
    choice = st.selectbox("Job template", options=templates)
    if st.button("Select"):
        st.session_state.job_selected = choice
        st.success(f"Selected: {choice}")