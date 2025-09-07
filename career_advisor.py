import streamlit as st
from graphviz import Digraph

# -------------------- CSS Styling --------------------
st.markdown("""
    <style>
    body { background: #f5f7fa; font-family: Arial, sans-serif; }
    .login-card {
        background: white;
        max-width: 500px;
        margin: 80px auto;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    .login-card h2 { text-align: center; margin-bottom: 20px; font-size: 24px; color: #333; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 8px; border: 1px solid #ccc; padding: 10px; font-size: 15px;
    }
    .stButton>button {
        width: 100%; padding: 10px; border-radius: 8px; background: #4CAF50;
        color: white; font-size: 16px; border: none;
    }
    .stButton>button:hover { background: #45a049; }
    .profile-icon {
        position: fixed; top: 15px; right: 25px; font-size: 18px; background: #ddd;
        width: 40px; height: 40px; border-radius: 50%; text-align: center;
        line-height: 40px; font-weight: bold; color: #333; z-index: 9999;
    }
    .badge { display: inline-block; padding: 6px 12px; margin: 3px; background-color: #e0f0ff; border-radius: 8px; color: #007acc; font-size: 14px; }
    .link-badge { display: inline-block; padding: 6px 12px; margin: 3px; background-color: #f0f0f0; border-radius: 8px; color: #0645AD; text-decoration: none; font-size: 14px; }
    .role-section { margin-bottom: 15px; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #4CAF50; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# -------------------- Session State --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "checklist_states" not in st.session_state:
    st.session_state.checklist_states = {}

# -------------------- Mock Data Function --------------------
def generate_mock_career_advice(user_data):
    return {
        "career": {
            "Data Scientist": {
                "Description": "Analyze and interpret complex data to help organizations make informed decisions.",
                "Required Skills": ["Python", "SQL", "Machine Learning", "Data Visualization"],
                "Next Steps": ["Build ML projects", "Complete Kaggle competitions", "Learn Cloud deployment"]
            },
            "Machine Learning Engineer": {
                "Description": "Design and deploy ML models into production systems.",
                "Required Skills": ["Python", "TensorFlow/PyTorch", "SQL", "Model Deployment"],
                "Next Steps": ["Work on end-to-end ML projects", "Learn Docker/Kubernetes"]
            },
            "AI Developer": {
                "Description": "Develop AI-powered applications and tools.",
                "Required Skills": ["Python", "NLP/Computer Vision", "Deep Learning", "APIs"],
                "Next Steps": ["Build AI apps", "Contribute to open-source AI projects"]
            }
        },
        "roadmap": [
            "Learn Python basics",
            "SQL fundamentals",
            "Data Analysis projects",
            "Machine Learning projects",
            "Advanced ML techniques",
            "Cloud deployment & portfolio building"
        ],
        "skill_gap": (
            "- Missing skills: Cloud Computing, Advanced ML, Data Visualization\n"
            "- Plan: Complete projects, take online courses, practice daily\n"
            "Practice Plan Checklist:\n- [ ] Python Intermediate\n- [ ] SQL Advanced\n- [ ] ML Projects\n- [ ] Cloud Basics"
        ),
        "learning": [
            ("Coursera – Machine Learning", "https://www.coursera.org/learn/machine-learning"),
            ("Udemy – Data Science Bootcamp", "https://www.udemy.com/course/data-science-bootcamp/"),
            ("Kaggle – Hands-on Projects", "https://www.kaggle.com/")
        ],
        "practice_websites": [
            ("LeetCode", "https://leetcode.com/"),
            ("HackerRank", "https://www.hackerrank.com/"),
            ("Kaggle", "https://www.kaggle.com/")
        ],
        "job_platforms": [
            ("LinkedIn Jobs", "https://www.linkedin.com/jobs/"),
            ("Naukri.com", "https://www.naukri.com/"),
            ("Indeed", "https://www.indeed.com/")
        ]
    }

# -------------------- Helper Functions --------------------
def render_badges(items, badge_class="badge", clickable=False):
    for item in items:
        if clickable and isinstance(item, tuple):
            label, url = item
            st.markdown(f'<a class="{badge_class}" href="{url}" target="_blank">{label}</a>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="{badge_class}">{item if not isinstance(item, tuple) else item[0]}</span>', unsafe_allow_html=True)

def render_checklist(checklist_text):
    for line in checklist_text.split("\n"):
        line = line.strip()
        if line.startswith("- [ ]"):
            label = line[5:].strip()
            checked = st.session_state.checklist_states.get(label, False)
            st.session_state.checklist_states[label] = st.checkbox(label, value=checked)

def render_graphviz_roadmap(roadmap_steps):
    dot = Digraph(comment="Career Roadmap", format="png")
    dot.attr(rankdir='LR', size='8')
    for i, step in enumerate(roadmap_steps):
        dot.node(str(i), step)
    for i in range(len(roadmap_steps)-1):
        dot.edge(str(i), str(i+1))
    st.graphviz_chart(dot)

def render_career_suggestions(career_dict):
    for role, details in career_dict.items():
        st.markdown(f'<div class="role-section">', unsafe_allow_html=True)
        st.subheader(role)
        st.markdown(f"**Description:** {details['Description']}")
        st.markdown("**Required Skills:** " + ", ".join(details["Required Skills"]))
        st.markdown("**Next Steps:** " + " | ".join(details["Next Steps"]))
        st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown(f'<div class="profile-icon">{st.session_state.username[0].upper()}</div>', unsafe_allow_html=True)
    st.title(f"Welcome {st.session_state.username} 👋")
    st.write("Explore your personalized career advisor dashboard.")

    # -------------------- Input Page --------------------
    if not st.session_state.show_results:
        st.header("Enter Your Profile Details")
        with st.form("user_input_form"):
            age = st.number_input("Age", min_value=10, max_value=100, value=25)
            location = st.text_input("Location")
            education = st.text_input("Education")
            years_exp = st.number_input("Years of Experience", min_value=0, max_value=50, value=2)
            target_role = st.text_input("Target Career Role")
            skill_1 = st.text_input("Skill 1 (Python / SQL / etc.)")
            skill_1_level = st.selectbox("Skill 1 Proficiency", ["Beginner", "Intermediate", "Advanced"])
            skill_2 = st.text_input("Skill 2")
            skill_2_level = st.selectbox("Skill 2 Proficiency", ["Beginner", "Intermediate", "Advanced"])
            skill_3 = st.text_input("Skill 3")
            skill_3_level = st.selectbox("Skill 3 Proficiency", ["Beginner", "Intermediate", "Advanced"])
            submit_btn = st.form_submit_button("Get Career Advice")

        if submit_btn:
            st.session_state.user_data = {
                "age": age,
                "location": location,
                "education": education,
                "experience": years_exp,
                "target_role": target_role,
                "skills": f"{skill_1} ({skill_1_level}), {skill_2} ({skill_2_level}), {skill_3} ({skill_3_level})"
            }
            st.session_state.show_results = True
            st.experimental_rerun()

    # -------------------- Results Page --------------------
    else:
        user_data = st.session_state.user_data
        sections = generate_mock_career_advice(user_data)
        st.header("AI-Powered Career Advisor Results")

        tabs = st.tabs([
            "Career Suggestions",
            "Roadmap",
            "Skill Gap Analysis",
            "Learning Resources",
            "Practice Websites",
            "Job Search Platforms"
        ])

        # Career Suggestions
        with tabs[0]:
            st.header("Career Suggestions")
            render_career_suggestions(sections["career"])

        # Roadmap
        with tabs[1]:
            st.header("Career Roadmap")
            render_graphviz_roadmap(sections["roadmap"])

        # Skill Gap Analysis
        with tabs[2]:
            st.header("Skill Gap Analysis & Practice Plan")
            skill_gap_text = sections["skill_gap"]
            if "Practice Plan Checklist:" in skill_gap_text:
                skills_part, checklist_part = skill_gap_text.split("Practice Plan Checklist:", 1)
            else:
                skills_part, checklist_part = skill_gap_text, ""
            if skills_part.strip():
                st.markdown(skills_part)
            render_checklist("Practice Plan Checklist:" + checklist_part)

        # Learning Resources
        with tabs[3]:
            st.header("Learning Resources")
            render_badges(sections["learning"], clickable=True)

        # Practice Websites
        with tabs[4]:
            st.header("Practice Websites")
            render_badges(sections["practice_websites"], badge_class="link-badge", clickable=True)

        # Job Search Platforms
        with tabs[5]:
            st.header("Job Search Platforms")
            render_badges(sections["job_platforms"], badge_class="link-badge", clickable=True)

        # Back Button
        if st.button("⬅ Back to Input Form"):
            st.session_state.show_results = False
            st.experimental_rerun()
