import streamlit as st
from pathlib import Path
import tempfile
import json

# backend imports
from backend.resume_parser import ResumeParser
from backend.skill_extractor import SkillExtractor
from backend.skill_normalizer import SkillNormalizer

def render():
    st.header("Upload Resume")
    uploaded = st.file_uploader("Upload PDF or DOCX resume", type=["pdf", "docx", "doc"])
    parser = ResumeParser()
    extractor = SkillExtractor()
    normalizer = SkillNormalizer()

    if uploaded:
        # Save to temporary file because parser expects a path
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
            tmp.write(uploaded.getbuffer())
            tmp_path = tmp.name

        try:
            parsed = parser.parse_resume(tmp_path)
            raw_text = parsed.get("raw_text", "")
            st.success(f"Parsed resume: {uploaded.name}")
            st.session_state.resume_data = parsed

            # Extract skills
            try:
                extracted = extractor.extract_skills(raw_text)
            except Exception:
                extracted = []

            # Normalize skills
            normalized = normalizer.normalize_skills_list(extracted)
            st.session_state.extracted_skills = normalized

            st.subheader("Extracted skills")
            if normalized:
                st.write(", ".join(normalized))
            else:
                st.info("No skills automatically extracted. You can add skills manually below.")

            # manual edit/add
            manual = st.text_input("Add/Update skills (comma separated)", value="")
            if st.button("Save skills"):
                manual_list = [s.strip() for s in manual.split(",") if s.strip()]
                combined = list(dict.fromkeys(normalized + manual_list))
                st.session_state.extracted_skills = combined
                st.success("Skills saved to session.")
        except Exception as e:
            st.error(f"Error parsing resume: {e}")