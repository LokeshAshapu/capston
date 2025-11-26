import streamlit as st
import json
import logging
from backend.llm_handler import LLMHandler

# Enable debug logging to see terminal output in Streamlit
logging.basicConfig(level=logging.INFO)

def render():
    st.header("📚 Personalized Learning Path")
    
    gap = st.session_state.get("skill_gap") or {"missing": ["Python", "SQL"]}
    missing_skills = gap.get("missing", [])
    
    if not missing_skills:
        st.info("No skill gaps detected. Great job!")
        return
    
    st.write(f"**Missing Skills:** {', '.join(missing_skills)}")
    st.markdown("---")
    
    # User level selection
    col1, col2 = st.columns(2)
    with col1:
        current_level = st.selectbox(
            "Your Current Level",
            options=["Beginner", "Intermediate", "Advanced"]
        )
    
    with col2:
        commitment = st.selectbox(
            "Weekly Time Commitment",
            options=["3 hours", "5 hours", "10 hours"]
        )
    
    st.markdown("---")
    
    # Generate learning plan button
    if st.button("🎯 Generate Personalized Learning Plan", key="gen_plan"):
        with st.spinner("Generating AI-powered learning plan with video suggestions..."):
            try:
                llm = LLMHandler()
                
                # Show LLM availability status
                status = llm.check_available()
                st.write(f"**LLM Status:** {status}")
                
                if not status.get("available"):
                    st.error(f"LLM not available: {status.get('init_error')}")
                    return
                
                job_title = st.session_state.get("job_selected", "Target Job")
                
                st.info(f"Generating plan for: {job_title}, Skills: {', '.join(missing_skills)}")
                
                # Call LLM to generate plan
                learning_plan = llm.generate_learning_plan_with_videos(
                    missing_skills=missing_skills,
                    job_title=job_title,
                    current_level=current_level,
                    weekly_hours=int(commitment.split()[0])
                )
                
                # DEBUG: Show raw response
                st.write("**DEBUG - Raw LLM Response:**")
                st.json(learning_plan)
                
                # Check if error occurred
                if "error" in learning_plan:
                    st.error(f"Error: {learning_plan.get('error')}")
                    st.write("Raw response:")
                    st.code(learning_plan.get("raw", "No raw response"))
                    return
                
                st.session_state.learning_plan = learning_plan
                st.success("✅ Learning plan generated!")
                
            except Exception as e:
                st.error(f"Error generating plan: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display learning plan if available
    if st.session_state.get("learning_plan"):
        _display_learning_plan(st.session_state.learning_plan)


def _display_learning_plan(plan: dict):
    """Display the generated learning plan with videos"""
    
    st.markdown("---")
    st.subheader("📖 Your 12-Week Learning Plan")
    
    weeks = plan.get("weeks", [])
    
    if not weeks:
        st.warning("No plan data available. Try generating again.")
        st.write("**Full plan object:**")
        st.json(plan)
        return
    
    # Create tabs for each week
    week_tabs = st.tabs([f"Week {w['week']}" for w in weeks[:12]])
    
    for tab, week_data in zip(week_tabs, weeks[:12]):
        with tab:
            st.markdown(f"### 🎯 Focus: **{week_data.get('focus_skill', 'N/A')}**")
            
            # Topics
            st.markdown("**Topics to Cover:**")
            topics = week_data.get("topics", [])
            for topic in topics:
                st.markdown(f"- {topic}")
            
            # Resources with YouTube videos
            st.markdown("**📺 Recommended Resources:**")
            resources = week_data.get("resources", [])
            
            if resources:
                for idx, resource in enumerate(resources, 1):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{idx}. {resource.get('name', 'Resource')}**")
                        st.caption(f"Type: {resource.get('type', 'N/A')} | Duration: {resource.get('duration', 'N/A')}")
                        
                        url = resource.get("url", "")
                        if url:
                            if "youtube.com" in url or "youtu.be" in url:
                                st.markdown(f"🎥 [Watch on YouTube]({url})")
                            else:
                                st.markdown(f"🔗 [View Resource]({url})")
                    
                    with col2:
                        if "youtube.com" in url or "youtu.be" in url:
                            st.markdown("🎥")
            else:
                st.info("No resources found for this week.")
            
            # Practice project
            project = week_data.get("practice_project", "")
            if project:
                st.markdown("**💻 Practice Project:**")
                st.info(project)
            
            # Milestone
            milestone = week_data.get("milestone", "")
            if milestone:
                st.markdown("**✅ Milestone:**")
                st.success(milestone)
    
    # Summary metrics
    st.markdown("---")
    st.subheader("📊 Plan Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_hours = plan.get("total_time_hours", 0)
        st.metric("Total Hours", f"{total_hours}h")
    
    with col2:
        weeks_count = len(weeks)
        st.metric("Duration", f"{weeks_count} weeks")
    
    with col3:
        skill_count = len(plan.get("prerequisites", []))
        st.metric("Prerequisites", skill_count)
    
    with col4:
        resource_count = sum(len(w.get("resources", [])) for w in weeks)
        st.metric("Total Resources", resource_count)
    
    # Success metrics
    st.markdown("**Success Metrics:**")
    metrics = plan.get("success_metrics", [])
    for metric in metrics:
        st.markdown(f"✓ {metric}")
    
    # Download plan as JSON
    plan_json = json.dumps(plan, indent=2)
    st.download_button(
        label="📥 Download Plan as JSON",
        data=plan_json,
        file_name="learning_plan.json",
        mime="application/json"
    )