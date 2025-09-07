import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os
from dotenv import load_dotenv
import graphviz

# ------------------ SETUP ------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

firebase_creds_str = st.secrets["FIREBASE_SERVICE_ACCOUNT"]
firebase_creds_dict = json.loads(firebase_creds_str)

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="AI Career Advisor", layout="wide")

# ------------------ CSS & BACKGROUND ------------------
page_bg = """
<style>
/* Full page background */
.stApp {
    background: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e") no-repeat center center fixed;
    background-size: cover;
}

/* Overlay for blur effect */
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(6px);
    z-index: -1;
}

/* Login box */
.login-container {
    background: rgba(255, 255, 255, 0.95);
    padding: 40px 50px;
    border-radius: 20px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.2);
    width: 400px;
    margin: auto;
    text-align: center;
}

/* Input styling */
div[data-baseweb="input"] input {
    background-color: #ffffff !important;
    border: 1px solid #ddd !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-size: 16px !important;
}

/* Slider styling */
.stSlider > div {
    background: #f1f5f9 !important;
    border-radius: 12px !important;
    padding: 6px 12px;
}

/* Button styling */
.stButton>button {
    width: 100%;
    background: linear-gradient(90deg, #4db6ac, #2196f3);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    padding: 12px;
    font-size: 16px;
    transition: 0.3s ease;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #2196f3, #4db6ac);
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
}
.stTabs [data-baseweb="tab"] {
    padding: 12px 24px;
    font-size: 16px;
    border-radius: 10px 10px 0 0;
    background: #e3f2fd;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #4db6ac !important;
    color: white !important;
}

/* Profile top bar */
.top-bar {
    display: flex; 
    justify-content: flex-end; 
    align-items: center;
    padding: 10px 20px;
}
.profile-circle {
    width: 42px; height: 42px;
    border-radius: 50%;
    background: #4db6ac;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: bold;
    font-size: 18px;
    margin-left: 10px;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)


# ------------------ FUNCTIONS ------------------
def get_ai_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1600, "topP": 1, "topK": 1},
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        resp = response.json()
        try:
            return resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Could not parse AI response: {e}"
    else:
        return f"API error: {response.status_code}"


def split_sections(text):
    sections = {"career": "", "roadmap": "", "skill_gap": "", "learning": "", "practice_websites": ""}
    current = None
    for line in text.splitlines():
        if line.strip() == "===Career Suggestions===":
            current = "career"
        elif line.strip() == "===Roadmap===":
            current = "roadmap"
        elif line.strip() == "===Skill Gap Analysis & Practice Plan===":
            current = "skill_gap"
        elif line.strip() == "===Learning Resources===":
            current = "learning"
        elif line.strip() == "===Practice Websites===":
            current = "practice_websites"
        elif current is not None:
            sections[current] += line + "\n"
    return sections


def render_graphviz_roadmap(roadmap_json):
    try:
        data = json.loads(roadmap_json)
        dot = graphviz.Digraph(
            node_attr={"style": "filled", "fillcolor": "#ade8f4", "fontname": "Segoe UI"}
        )
        dot.attr(rankdir="TB", size="8,5")
        for step in data:
            num = str(step.get("step_number", "?"))
            label = f"{step.get('title', '')}\n({step.get('expected_duration_weeks', '?')} weeks)"
            dot.node(num, label)
        for i in range(len(data) - 1):
            dot.edge(str(data[i]["step_number"]), str(data[i + 1]["step_number"]))
        st.graphviz_chart(dot)
    except Exception as e:
        st.error(f"Could not draw roadmap: {e}")


# ------------------ LOGIN PAGE ------------------
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.user_email:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("## 🔑 Login to Career Advisor")
    username = st.text_input("Username")
    email = st.text_input("Email")
    if st.button("Login"):
        if email and username:
            st.session_state.user_email = email
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.warning("Please enter both username and email.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ------------------ MAIN APP ------------------
# Profile icon bar
with st.container():
    st.markdown('<div class="top-bar">', unsafe_allow_html=True)
    initials = st.session_state.username[:2].upper()
    st.markdown(f'<div class="profile-circle">{initials}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.title("🎯 AI-Powered Career Advisor")

st.write("### Enter your details:")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", 10, 60)
    location = st.text_input("City or State")
with col2:
    education = st.text_input("Education Background")

st.write("#### Skills & Proficiency (1-5):")
skills = {}
for i in range(3):
    skill = st.text_input(f"Skill {i+1}", key=f"skill{i}")
    level = st.slider(f"Proficiency {i+1}", 1, 5, 3, key=f"level{i}")
    if skill:
        skills[skill] = level

interests = st.text_input("Interests (comma-separated)")
goals = st.text_input("Career Goals")

if st.button("🚀 Get Career Advice"):
    skills_text = ", ".join([f"{s} (level {l})" for s, l in skills.items()])
    prompt = f"""
    I am a {age}-year-old student from {location}, India. My education background: {education}.
    My skills with proficiency levels: {skills_text}. My interests include: {interests}.
    My career goals are: {goals}.
    Please provide the output in the following exact sections:
    ===Career Suggestions=== ...
    """
    ai_response = get_ai_response(prompt)
    sections = split_sections(ai_response)

    tabs = st.tabs(
        ["Career Suggestions", "Roadmap", "Skill Gap Analysis", "Learning Resources", "Practice Websites"]
    )

    with tabs[0]:
        st.subheader("Career Suggestions")
        st.markdown(sections.get("career", "No data."))

    with tabs[1]:
        st.subheader("Career Roadmap")
        if sections.get("roadmap"):
            render_graphviz_roadmap(sections["roadmap"])
        else:
            st.info("No roadmap found.")

    with tabs[2]:
        st.subheader("Skill Gap Analysis & Practice Plan")
        st.markdown(sections.get("skill_gap", "No data."))

    with tabs[3]:
        st.subheader("Learning Resources")
        st.markdown(sections.get("learning", "No data."))

    with tabs[4]:
        st.subheader("Practice Websites")
        st.markdown(sections.get("practice_websites", "No data."))

