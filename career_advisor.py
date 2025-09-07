# skills_advisor.py
import streamlit as st
import os
from dotenv import load_dotenv
from graphviz import Digraph
from openai import OpenAI
import json

# -------------------- Load .env --------------------
load_dotenv()
API_KEY = os.getenv("REACT_APP_GEMINI_API_KEY")

# -------------------- CSS Styling --------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.login-card {
    background: rgba(255,255,255,0.95);
    max-width: 500px;
    margin: 100px auto;
    padding: 40px 30px;
    border-radius: 15px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
    text-align: center;
    position: relative;
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
.stTextInput>div>div>input, .stNumberInput>div>div>input {
    border-radius: 8px;
    border: 1px solid #ccc;
    padding: 12px;
    font-size: 15px;
}
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
.stTabs [role="tab"] { font-weight: 600; font-size: 15px; }
.stTabs [role="tabpanel"] {
    background: rgba(255,255,255,0.95);
    border-radius: 12px;
    padding: 20px;
    margin-top: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.badge { display: inline-block; background-color: #4a90e2; color: white; padding: 4px 10px; margin: 2px 2px 2px 0; border-radius: 12px; font-size: 14px; }
.badge.completed { background-color: #50e3c2 !important; }
.checklist-badge { display: inline-block; background-color: #50e3c2; color: white; padding: 4px 10px; margin: 2px 2px 2px 0; border-radius: 12px; font-size: 14px; }
.link-badge { display: inline-block; background-color: #f0f0f0; color: #333; padding: 4px 10px; margin: 2px 2px 2px 0; border-radius: 12px; font-size: 14px; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# -------------------- Session State --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "practice_states" not in st.session_state:
    st.session_state.practice_states = {}
if "roadmap_states" not in st.session_state:
    st.session_state.roadmap_states = {}
if "sections" not in st.session_state:
    st.session_state.sections = {}

# -------------------- Helper Functions --------------------
def render_badges(items, badge_class="badge"):
    badges_html = ""
    for i, item in enumerate(items):
        completed = st.session_state.roadmap_states.get(item, False)
        cls = badge_class + (" completed" if completed else "")
        badges_html += f"<span class='{cls}'>{item}</span>"
    st.markdown(badges_html, unsafe_allow_html=True)

def roadmap_with_checkboxes(items):
    for item in items:
        checked = st.checkbox(item, value=st.session_state.roadmap_states.get(item, False))
        st.session_state.roadmap_states[item] = checked

def checklist_with_persistence(items):
    for i, item in enumerate(items):
        key = f"checklist_{i}"
        checked = st.session_state.practice_states.get(key, False)
        st.session_state.practice_states[key] = st.checkbox(item, value=checked)

def generate_gemini_response(prompt):
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gemini-pro",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_graphviz_roadmap(steps):
    dot = Digraph(comment="Career Roadmap")
    for i, step in enumerate(steps):
        dot.node(str(i), step)
        if i > 0:
            dot.edge(str(i-1), str(i))
    return dot

# -------------------- Login Page --------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>Login to Career Advisor</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    email = st.text_input("Email")
    if st.button("Login"):
        if username.strip() and email.strip():
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.warning("Please fill in all fields")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Main App --------------------
else:
    st.markdown(f'<div class="profile-icon">{st.session_state.username[0].upper()}</div>', unsafe_allow_html=True)
    st.title(f"Welcome {st.session_state.username} 👋")
    st.write("Fill in your details to get personalized career advice.")

    if not st.session_state.form_submitted:
        with st.form("user_input_form"):
            age = st.number_input("Age", min_value=12, max_value=100, step=1)
            skills_input = st.text_input("Skills (comma separated)")
            target_role = st.text_input("Target Role / Career Goal")
            education = st.text_input("Education Background")
            experience = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
            current_role = st.text_input("Current Role")
            interests = st.text_input("Interests / Hobbies")
            location = st.text_input("Preferred Job Location")
            submitted = st.form_submit_button("Get Career Advice")

            if submitted:
                if all([skills_input.strip(), target_role.strip(), education.strip(), location.strip()]):
                    st.session_state.age = age
                    st.session_state.skills_input = skills_input
                    st.session_state.target_role = target_role
                    st.session_state.education = education
                    st.session_state.experience = experience
                    st.session_state.current_role = current_role
                    st.session_state.interests = interests
                    st.session_state.location = location
                    st.session_state.form_submitted = True

                    # -------------------- Generate Sections from Gemini --------------------
                    prompt = f"""
                    Based on the following user info, provide:
                    1. Career suggestions with details
                    2. Roadmap steps to achieve target role
                    3. Skill gap analysis
                    4. Learning resources
                    5. Practice websites
                    6. Job search platforms
                    
                    User Info:
                    Skills: {skills_input}
                    Target Role: {target_role}
                    Education: {education}
                    Experience: {experience} years
                    Current Role: {current_role}
                    Interests: {interests}
                    Location: {location}
                    
                    Format output as JSON with keys: career, roadmap, skill_gap, learning, practice_websites, job_platforms
                    """
                    try:
                        response_text = generate_gemini_response(prompt)
                        st.session_state.sections = json.loads(response_text)
                    except Exception as e:
                        st.error(f"Error fetching Gemini response: {e}")
                        st.session_state.sections = {}
                    st.rerun()
                else:
                    st.warning("Please fill all required fields.")

    # -------------------- Tabs --------------------
    if st.session_state.form_submitted:
        sections = st.session_state.sections
        st.header("AI-Powered Career Advisor Results")
        tabs = st.tabs(["Career Suggestions", "Roadmap", "Skill Gap Analysis", "Learning Resources", "Practice Websites", "Job Search Platforms"])

        with tabs[0]:  # Career Suggestions
            st.header("Career Suggestions")
            career_text = sections.get("career", "")
            if career_text:
                st.markdown(career_text)
            else:
                st.info("No career suggestions available.")

        with tabs[1]:  # Roadmap
            st.header("Career Roadmap")
            roadmap_text = sections.get("roadmap", "")
            if roadmap_text:
                roadmap_steps = [s.strip() for s in roadmap_text.split(",")]
                roadmap_with_checkboxes(roadmap_steps)
                render_badges(roadmap_steps)
                st.graphviz_chart(generate_graphviz_roadmap(roadmap_steps))
            else:
                st.info("No roadmap data available.")

        with tabs[2]:  # Skill Gap
            st.header("Skill Gap Analysis & Practice Plan")
            skill_gap_text = sections.get("skill_gap", "")
            if skill_gap_text:
                st.markdown(skill_gap_text)
                checklist_items = ["Complete Python project", "Solve 50 SQL problems", "Deploy a cloud app"]
                st.write("Practice Plan Checklist:")
                checklist_with_persistence(checklist_items)
            else:
                st.info("No skill gap analysis available.")

        with tabs[3]:  # Learning Resources
            st.header("Learning Resources")
            learning_text = sections.get("learning", "")
            if learning_text:
                resources = [r.strip() for r in learning_text.split(",")]
                render_badges(resources, badge_class="badge")
            else:
                st.info("No learning resources provided.")

        with tabs[4]:  # Practice Websites
            st.header("Practice Websites")
            practice_websites_text = sections.get("practice_websites", "")
            if practice_websites_text:
                links = [l.strip() for l in practice_websites_text.split(",")]
                render_badges(links, badge_class="link-badge")
            else:
                st.info("No practice websites listed.")

        with tabs[5]:  # Job Search Platforms
            st.header("Job Search Platforms")
            job_platforms_text = sections.get("job_platforms", "")
            if job_platforms_text:
                links = [l.strip() for l in job_platforms_text.split(",")]
                render_badges(links, badge_class="link-badge")
            else:
                st.info("No job search platforms listed.")
