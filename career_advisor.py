import os
import streamlit as st
import requests
from dotenv import load_dotenv
from graphviz import Digraph
import json

# ------------------- Load API Key --------------------
load_dotenv()

# 🔑 Look for API_KEY in both st.secrets and .env
API_KEY = st.secrets.get("API_KEY", os.getenv("API_KEY"))
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"
st.write("🔍 Debug - API_KEY from secrets:", st.secrets.get("API_KEY"))
st.write("🔍 Debug - API_KEY from env:", os.getenv("API_KEY"))

# ------------------- CSS Styling --------------------
st.markdown("""
<style>
body { background: linear-gradient(135deg, #f0f4f8, #d9e2ec); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.login-card { background: rgba(255,255,255,0.95); max-width: 500px; margin: 100px auto; padding: 40px 30px; border-radius: 15px; box-shadow: 0px 8px 20px rgba(0,0,0,0.15); text-align: center; position: relative; }
.login-card::before { content: "💡"; font-size: 120px; color: rgba(74,144,226,0.08); position: absolute; top: 10px; right: 10px; z-index: 0; pointer-events: none; }
.login-card h2 { margin-bottom: 25px; font-size: 24px; color: #333; position: relative; z-index: 1; }
.stTextInput>div>div>input, .stNumberInput>div>div>input, select { border-radius: 8px; border: 1px solid #ccc; padding: 12px; font-size: 15px; }
.stButton>button { width: 100%; padding: 12px; border-radius: 8px; background: #4a90e2; color: white; font-size: 16px; border: none; margin-top: 10px; }
.stButton>button:hover { background: #357abd; }
.profile-icon { position: fixed; top: 15px; right: 25px; font-size: 18px; background: #4a90e2; width: 45px; height: 45px; border-radius: 50%; text-align: center; line-height: 45px; font-weight: bold; color: white; z-index: 9999; box-shadow: 0 3px 8px rgba(0,0,0,0.2); }
.stTabs [role="tab"] { font-weight: 600; font-size: 15px; }
.stTabs [role="tabpanel"] { background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px; margin-top: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.badge { display: inline-block; background-color: #4a90e2; color: white; padding: 4px 10px; margin: 2px 2px 2px 0; border-radius: 12px; font-size: 14px; }
.link-badge { display: inline-block; background-color: #f0f0f0; color: #333; padding: 4px 10px; margin: 2px 2px 2px 0; border-radius: 12px; font-size: 14px; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ------------------- Session State --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "sections" not in st.session_state:
    st.session_state.sections = {}

# ------------------- Helper Functions --------------------
def render_badges(items, badge_class="badge"):
    badges_html = "".join([f"<span class='{badge_class}'>{item}</span>" for item in items])
    st.markdown(badges_html, unsafe_allow_html=True)

def roadmap_with_checkboxes(items):
    for item in items:
        st.checkbox(item)

def generate_graphviz_roadmap(steps):
    dot = Digraph(comment="Career Roadmap", format='png')
    colors = ["#4a90e2", "#50e3c2", "#f5a623", "#9013fe", "#d0021b", "#7ed321"]
    for i, step in enumerate(steps):
        color = colors[i % len(colors)]
        dot.node(str(i), step, style="filled", fillcolor=color, fontcolor="white", shape="box", fontsize="14")
        if i > 0:
            dot.edge(str(i-1), str(i), color="#333333", arrowsize="1.0")
    return dot

def generate_gemini_response(prompt):
    """Call Gemini REST API and return structured sections."""
    url = f"{GEMINI_URL}?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        res.raise_for_status()
        data = res.json()

        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        if not text:
            st.warning("⚠️ Gemini returned an empty response.")
            return {}

        sections = {
            "career": "",
            "roadmap": "",
            "skill_gap": "",
            "learning": "",
            "practice_websites": "",
            "job_platforms": "",
        }
        lines = text.split("\n")
        current_section = "career"

        for line in lines:
            line = line.strip()
            if not line:
                continue
            l_lower = line.lower()
            if "roadmap" in l_lower:
                current_section = "roadmap"; continue
            elif "skill gap" in l_lower:
                current_section = "skill_gap"; continue
            elif "learning" in l_lower:
                current_section = "learning"; continue
            elif "practice" in l_lower:
                current_section = "practice_websites"; continue
            elif "job" in l_lower:
                current_section = "job_platforms"; continue
            sections[current_section] += line + "\n"

        return sections

    except Exception as e:
        st.error(f"Error calling Gemini API: {e}")
        return {}

# ------------------- Login Page --------------------
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

# ------------------- Main App --------------------
else:
    st.markdown(f'<div class="profile-icon">{st.session_state.username[0].upper()}</div>', unsafe_allow_html=True)
    st.title(f"Welcome {st.session_state.username} 👋")
    st.write("Fill in your details to get personalized career advice.")

    if not st.session_state.form_submitted:
        with st.form("user_input_form"):
            age = st.number_input("Age", min_value=12, max_value=100, step=1)
            experience = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)

            st.write("### Skills and Proficiency")
            skill_1 = st.text_input("Skill 1 Name")
            prof_1 = st.selectbox("Skill 1 Level", ["Beginner", "Intermediate", "Expert"])
            skill_2 = st.text_input("Skill 2 Name")
            prof_2 = st.selectbox("Skill 2 Level", ["Beginner", "Intermediate", "Expert"])
            skill_3 = st.text_input("Skill 3 Name")
            prof_3 = st.selectbox("Skill 3 Level", ["Beginner", "Intermediate", "Expert"])

            target_role = st.text_input("Target Role / Career Goal")
            education = st.text_input("Education Background")
            location = st.text_input("Preferred Job Location")

            submitted = st.form_submit_button("Get Career Advice")

            if submitted:
                if all([target_role.strip(), education.strip(), location.strip()]):
                    st.session_state.age = age
                    st.session_state.experience = experience
                    st.session_state.target_role = target_role
                    st.session_state.education = education
                    st.session_state.location = location
                    st.session_state.skills_input = f"{skill_1} ({prof_1}), {skill_2} ({prof_2}), {skill_3} ({prof_3})"
                    st.session_state.form_submitted = True

                    prompt = f"""
Provide career advice in labeled sections: Career Suggestions, Roadmap, Skill Gap, Learning Resources, Practice Websites, Job Search Platforms.

User Info:
- Age: {age}
- Experience: {experience} years
- Skills: {st.session_state.skills_input}
- Target Role: {target_role}
- Education: {education}
- Location: {location}
"""
                    with st.spinner("Generating your personalized career advice..."):
                        st.session_state.sections = generate_gemini_response(prompt)
                    st.rerun()

    if st.session_state.form_submitted:
        sections = st.session_state.sections
        st.header("AI-Powered Career Advisor Results")

        tabs = st.tabs([
            "Career Suggestions",
            "Roadmap",
            "Skill Gap Analysis",
            "Learning Resources",
            "Practice Websites",
            "Job Search Platforms"
        ])

        with tabs[0]:
            st.header("Career Suggestions")
            st.markdown(sections.get("career", "No career suggestions available."))

        with tabs[1]:
            st.header("Career Roadmap")
            roadmap_text = sections.get("roadmap", "")
            if roadmap_text:
                steps = [s.strip() for s in roadmap_text.replace("\\n", ",").split(",") if s.strip()]
                roadmap_with_checkboxes(steps)
                st.graphviz_chart(generate_graphviz_roadmap(steps))
            else:
                st.info("No roadmap data available.")

        with tabs[2]:
            st.header("Skill Gap Analysis")
            st.markdown(sections.get("skill_gap", "No skill gap analysis available."))

        with tabs[3]:
            st.header("Learning Resources")
            learning_text = sections.get("learning", "")
            if learning_text:
                render_badges([r.strip() for r in learning_text.split(",")])
            else:
                st.info("No learning resources provided.")

        with tabs[4]:
            st.header("Practice Websites")
            practice_text = sections.get("practice_websites", "")
            if practice_text:
                render_badges([l.strip() for l in practice_text.split(",")], badge_class="link-badge")
            else:
                st.info("No practice websites listed.")

        with tabs[5]:
            st.header("Job Search Platforms")
            jobs_text = sections.get("job_platforms", "")
            if jobs_text:
                render_badges([l.strip() for l in jobs_text.split(",")], badge_class="link-badge")
            else:
                st.info("No job search platforms listed.")
