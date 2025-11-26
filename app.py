# import streamlit as st
# from streamlit_option_menu import option_menu
# import sys
# from pathlib import Path

# # Add project root to path
# sys.path.insert(0, str(Path(__file__).parent))

# from config.settings import APP_CONFIG
# from frontend.pages import home, upload_resume, select_job, gap_analysis, learning_path

# # Page config
# st.set_page_config(
#     page_title=APP_CONFIG["app_name"],
#     page_icon="🎯",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
#     <style>
#     .main { padding: 0rem 1rem; }
#     .stMetric { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; }
#     </style>
# """, unsafe_allow_html=True)

# # Session state initialization
# if "resume_data" not in st.session_state:
#     st.session_state.resume_data = None
# if "extracted_skills" not in st.session_state:
#     st.session_state.extracted_skills = []
# if "job_selected" not in st.session_state:
#     st.session_state.job_selected = None
# if "skill_gap" not in st.session_state:
#     st.session_state.skill_gap = None
# if "learning_plan" not in st.session_state:
#     st.session_state.learning_plan = None

# # Sidebar Navigation
# with st.sidebar:
#     st.title("🎯 SkillGuide AI")
#     st.markdown("---")
    
#     selected = option_menu(
#         menu_title="Navigation",
#         options=["Home", "Upload Resume", "Select Job", "Gap Analysis", "Learning Path"],
#         icons=["house", "file-earmark-pdf", "briefcase", "bar-chart", "book"],
#         menu_icon="cast",
#         default_index=0,
#         styles={
#             "container": {"padding": "0!important", "background-color": "#fafafa"},
#             "icon": {"color": "orange", "font-size": "25px"},
#             "nav-link": {"font-size": "16px", "text-align": "left"},
#         }
#     )
    
#     st.markdown("---")
#     st.markdown(f"**Version:** {APP_CONFIG['version']}")

# # Route to pages
# if selected == "Home":
#     home.render()
# elif selected == "Upload Resume":
#     upload_resume.render()
# elif selected == "Select Job":
#     select_job.render()
# elif selected == "Gap Analysis":
#     gap_analysis.render()
# elif selected == "Learning Path":
#     learning_path.render()




# # ...existing code...
# import streamlit as st
# from streamlit_option_menu import option_menu
# import streamlit as st
# # removed streamlit_option_menu dependency; using st.sidebar.radio instead
# import sys
# from pathlib import Path
 
#  # Add project root to path
# sys.path.insert(0, str(Path(__file__).parent))
 
# from config.settings import APP_CONFIG
# from frontend.pages import home, upload_resume, select_job, gap_analysis, learning_path
#  # ...existing code...
 

# st.set_page_config(
#     page_title=APP_CONFIG["app_name"],
#     page_icon="🎯",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
#     <style>
#     .main { padding: 0rem 1rem; }
#     .stMetric { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; }
#     </style>
# """, unsafe_allow_html=True)

# # Session state initialization
# if "resume_data" not in st.session_state:
#     st.session_state.resume_data = None
# if "extracted_skills" not in st.session_state:
#     st.session_state.extracted_skills = []
# if "job_selected" not in st.session_state:
#     st.session_state.job_selected = None
# if "skill_gap" not in st.session_state:
#     st.session_state.skill_gap = None
# if "learning_plan" not in st.session_state:
#     st.session_state.learning_plan = None

#  # Sidebar Navigation
# with st.sidebar:
#     st.title("🎯 SkillGuide AI")
#     st.markdown("---")
#     selected = option_menu(
#         menu_title="Navigation",
#         options=["Home", "Upload Resume", "Select Job", "Gap Analysis", "Learning Path"],
#         icons=["house", "file-earmark-pdf", "briefcase", "bar-chart", "book"],
#         menu_icon="cast",
#         default_index=0,
#         styles={
#             "container": {"padding": "0!important", "background-color": "#fafafa"},
#             "icon": {"color": "orange", "font-size": "25px"},
#             "nav-link": {"font-size": "16px", "text-align": "left"},
#         }
#     )
#     selected = st.radio(
#         "Navigation",
#         options=["Home", "Upload Resume", "Select Job", "Gap Analysis", "Learning Path"]
#     )
    
#     st.markdown("---")
#     st.markdown(f"**Version:** {APP_CONFIG['version']}")

# # Route to pages
# if selected == "Home":
#     home.render()
# elif selected == "Upload Resume":
#     upload_resume.render()
# elif selected == "Select Job":
#     select_job.render()
# elif selected == "Gap Analysis":
#     gap_analysis.render()
# elif selected == "Learning Path":
#     learning_path.render()
# # ...existing code...


# ...existing code...
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import APP_CONFIG
from frontend.pages import home, upload_resume, select_job, gap_analysis, learning_path
# ...existing code...

st.set_page_config(
    page_title=APP_CONFIG["app_name"],
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stMetric { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "resume_data" not in st.session_state:
    st.session_state.resume_data = None
if "extracted_skills" not in st.session_state:
    st.session_state.extracted_skills = []
if "job_selected" not in st.session_state:
    st.session_state.job_selected = None
if "skill_gap" not in st.session_state:
    st.session_state.skill_gap = None
if "learning_plan" not in st.session_state:
    st.session_state.learning_plan = None

# Sidebar Navigation (using built-in radio to avoid extra dependency)
with st.sidebar:
    st.title("🎯 SkillGuide AI")
    st.markdown("---")
    selected = st.radio(
        "Navigation",
        options=["Home", "Upload Resume", "Select Job", "Gap Analysis", "Learning Path"],
        index=0
    )
    st.markdown("---")
    st.markdown(f"**Version:** {APP_CONFIG['version']}")

# Route to pages
if selected == "Home":
    home.render()
elif selected == "Upload Resume":
    upload_resume.render()
elif selected == "Select Job":
    select_job.render()
elif selected == "Gap Analysis":
    gap_analysis.render()
elif selected == "Learning Path":
    learning_path.render()
# ...existing code...