import streamlit as st

# -------------------- CSS Styling --------------------
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Login card with watermark */
    .login-card {
        background: rgba(255,255,255,0.95);
        max-width: 400px;
        margin: 80px auto;
        padding: 40px 30px;
        border-radius: 15px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .login-card::before {
        content: "💡";
        font-size: 120px;
        color: rgba(74,144,226,0.08);
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 0;
        pointer-events: none;
    }
    .login-card h2 {
        margin-bottom: 25px;
        font-size: 24px;
        color: #333;
        position: relative;
        z-index: 1;
    }

    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 12px;
        font-size: 15px;
    }

    /* Button styling */
    .stButton>button {
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        background: #4a90e2;
        color: white;
        font-size: 16px;
        border: none;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background: #357abd;
    }

    /* Profile icon */
    .profile-icon {
        position: fixed;
        top: 15px;
        right: 25px;
        font-size: 18px;
        background: #4a90e2;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        text-align: center;
        line-height: 45px;
        font-weight: bold;
        color: white;
        z-index: 9999;
        box-shadow: 0 3px 8px rgba(0,0,0,0.2);
    }

    /* Tabs styling */
    .stTabs [role="tab"] {
        font-weight: 600;
        font-size: 15px;
    }

    /* Dashboard watermark */
    .stApp::before {
        content: "🧑‍💻";
        font-size: 150px;
        color: rgba(74,144,226,0.05);
        position: absolute;
        top: 50px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 0;
        pointer-events: none;
    }

    /* Subtle tab panel styling */
    .stTabs [role="tabpanel"] {
        background: rgba(255,255,255,0.95);
        border-radius: 12px;
        padding: 20px;
        margin-top: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* Scrollbar for overflow inside tabs if needed */
    .stTabs [role="tabpanel"]::-webkit-scrollbar {
        width: 8px;
    }
    .stTabs [role="tabpanel"]::-webkit-scrollbar-thumb {
        background-color: rgba(74,144,226,0.3);
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- Session State --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "practice_states" not in st.session_state:
    st.session_state.practice_states = {}

# -------------------- Login Page --------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>Login to Career Advisor</h2>", unsafe_allow_html=True)

    username = st.text_input("Username")
    email = st.text_input("Email")

    if st.button("Login"):
        if username and email:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Please fill in all fields")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Main App --------------------
else:
    # Profile icon
    st.markdown(
        f'<div class="profile-icon">{st.session_state.username[0].upper()}</div>',
        unsafe_allow_html=True,
    )

    st.title(f"Welcome {st.session_state.username} 👋")
    st.write("Explore your personalized AI-powered career advisor dashboard.")

    # -------------------- Tabs --------------------
    st.header("AI-Powered Career Advisor Results")

    tabs = st.tabs(
        [
            "Career Suggestions",
            "Roadmap",
            "Skill Gap Analysis",
            "Learning Resources",
            "Practice Websites",
            "Job Search Platforms",
        ]
    )

    # ---------------- Career Suggestions ----------------
    with tabs[0]:
        st.header("Career Suggestions")
        career_text = sections.get("career", "").strip() if 'sections' in locals() else ""
        if career_text:
            render_career_suggestions(career_text) if 'render_career_suggestions' in locals() else None
        else:
            st.info("No career suggestions available.")

    # ---------------- Roadmap ----------------
    with tabs[1]:
        st.header("Career Roadmap")
        roadmap_text = sections.get("roadmap", "").strip() if 'sections' in locals() else ""
        if roadmap_text:
            render_graphviz_roadmap(roadmap_text) if 'render_graphviz_roadmap' in locals() else None
        else:
            st.info("No roadmap data available.")

    # ---------------- Skill Gap Analysis ----------------
    with tabs[2]:
        st.header("Skill Gap Analysis & Practice Plan")
        skill_gap_text = sections.get("skill_gap", "").strip() if 'sections' in locals() else ""
        if skill_gap_text:
            if "Practice Plan Checklist:" in skill_gap_text:
                skills_part, checklist_part = skill_gap_text.split("Practice Plan Checklist:", 1)
            else:
                skills_part, checklist_part = skill_gap_text, ""

            if skills_part.strip():
                st.markdown(skills_part)

            checklist_items = get_checklist_items("Practice Plan Checklist:" + checklist_part) if 'get_checklist_items' in locals() else []
            if checklist_items:
                st.write("Practice Plan Checklist:")
                checklist_with_persistence(checklist_items) if 'checklist_with_persistence' in locals() else None

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Practice Progress"):
                    save_progress(user_id, st.session_state.practice_states) if 'save_progress' in locals() else None
            with col2:
                if st.button("Load Practice Progress"):
                    loaded_states = load_progress(user_id) if 'load_progress' in locals() else None
                    if loaded_states:
                        st.session_state.practice_states = loaded_states
                        st.experimental_rerun()
                    else:
                        st.warning("No saved progress found.")
        else:
            st.info("No skill gap analysis available.")

    # ---------------- Learning Resources ----------------
    with tabs[3]:
        st.header("Learning Resources")
        learning_text = sections.get("learning", "").strip() if 'sections' in locals() else ""
        if learning_text:
            render_learning_resources(learning_text) if 'render_learning_resources' in locals() else None
        else:
            st.info("No learning resources provided.")

    # ---------------- Practice Websites ----------------
    with tabs[4]:
        st.header("Practice Websites")
        practice_websites_text = sections.get("practice_websites", "").strip() if 'sections' in locals() else ""
        if practice_websites_text:
            st.markdown(practice_websites_text, unsafe_allow_html=True)
        else:
            st.info("No practice websites listed.")

    # ---------------- Job Search Platforms ----------------
    with tabs[5]:
        st.header("Job Search Platforms")
        skills = st.session_state.get('skills', None)
        location = st.session_state.get('location', None)
        if skills and location:
            job_links = get_job_platform_links(", ".join([f"{s} (level {l})" for s, l in skills.items()]), location) if 'get_job_platform_links' in locals() else {}
            for platform, url in job_links.items():
                st.markdown(f"- [{platform}]({url})", unsafe_allow_html=True)
        else:
            st.info("Enter skills and location to view job search platforms.")
