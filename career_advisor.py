import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os
from dotenv import load_dotenv

# Soothing color palette with soft pastels and comfortable contrasts
st.markdown("""
<style>
/* Background with soft pastel gradient */
.reportview-container {
    background: linear-gradient(135deg, #e3f2fd 0%, #fce4ec 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Primary heading with soft teal */
h1 {
    color: #4db6ac; /* soft teal */
    font-weight: 700;
    font-size: 2.8rem;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 1px 1px 3px rgba(77, 182, 172, 0.4);
}

/* Sidebar with calming lavender background and gentle border */
[data-testid="stSidebar"] {
    background: #ede7f6; /* lavender */
    color: #37474f; /* blue gray */
    border-right: 3px solid #80cbc4; /* soft teal */
    padding: 20px 25px 50px 25px !important;
    font-weight: 600;
}

/* Sidebar headers with deeper teal */
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #00796b; /* dark teal */
    margin-top: 1rem;
    margin-bottom: 0.6rem;
}

/* Sidebar input fields with soft shadows and rounded corners */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select {
    border-radius: 12px;
    border: 1.8px solid #80cbc4; /* soft teal border */
    padding: 10px 16px;
    margin-bottom: 16px;
    font-size: 1rem;
    box-shadow: 2px 2px 6px rgba(128, 203, 196, 0.25);
    color: #37474f;
    background-color: #ffffff;
}

/* Buttons with soft teal background and smooth hover */
.stButton>button {
    background-color: #4db6ac; /* soft teal */
    color: white !important;
    border-radius: 14px;
    font-weight: 700;
    padding: 14px 40px;
    margin-top: 18px !important;
    box-shadow: 0 5px 15px rgba(77, 182, 172, 0.4);
    transition: background-color 0.3s ease, box-shadow 0.3s ease;
}
.stButton>button:hover {
    background-color: #80cbc4; /* lighter teal */
    box-shadow: 0 7px 20px rgba(128, 203, 196, 0.6);
}

/* Tabs background with soft pastel */
[role="tablist"] {
    background-color: #f3e5f5; /* lavender light */
    border-radius: 16px;
    padding: 8px 20px;
    margin-bottom: 20px;
}

/* Tabs labels soft teal with rounded corners */
[role="tab"] {
    color: #4db6ac; /* soft teal */
    font-weight: 600;
    border-radius: 16px;
    padding: 10px 26px;
    margin: 4px 10px;
    min-width: 160px;
    text-align: center;
    transition: all 0.3s ease;
}

/* Selected tab styling */
[role="tab"][aria-selected="true"] {
    background: #4db6ac;
    color: #fff !important;
    font-weight: 700;
    box-shadow: 0 6px 20px rgba(77, 182, 172, 0.45);
}

/* Text areas with soft background and smooth shadow */
textarea {
    background-color: #f1fafe; /* very light blue */
    color: #37474f;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 1rem;
    border-radius: 14px;
    border: 1.5px solid #b2dfdb;
    padding: 14px 20px;
    min-height: 280px;
    resize: vertical;
    box-shadow: inset 0 0 10px rgba(128, 203, 196, 0.2);
}

/* Main content padding */
.css-1d391kg {
    padding: 32px !important;
}

/* Scrollbar styling for textareas */
textarea::-webkit-scrollbar {
    width: 12px;
}
textarea::-webkit-scrollbar-track {
    background: #ede7f6;
    border-radius: 12px;
}
textarea::-webkit-scrollbar-thumb {
    background-color: #4db6ac;
    border-radius: 12px;
    border: 3px solid #ede7f6;
}

/* Practice checklist text */
.css-1r6slb0 span {
    color: #00796b; /* darker teal */
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)

# Load Gemini API Key from environment variable or Streamlit secrets
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# Initialize Firebase Admin SDK using service account from Streamlit secrets
firebase_creds_str = st.secrets["FIREBASE_SERVICE_ACCOUNT"]
firebase_creds_dict = json.loads(firebase_creds_str)

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_ai_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
            "topP": 1,
            "topK": 1
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        resp = response.json()
        try:
            return resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error parsing AI response: {e}\nFull response: {resp}"
    else:
        return f"API Error: {response.status_code} - {response.text}"

def split_sections(text):
    sections = {"career": "", "roadmap": "", "skill_gap": "", "learning": ""}
    current_section = None
    for line in text.splitlines():
        line_strip = line.strip()
        if line_strip == "===Career Suggestions===":
            current_section = "career"
        elif line_strip == "===Roadmap===":
            current_section = "roadmap"
        elif line_strip == "===Skill Gap Analysis & Practice Plan===":
            current_section = "skill_gap"
        elif line_strip == "===Learning Resources===":
            current_section = "learning"
        elif current_section:
            sections[current_section] += line + "\n"
    return sections

def parse_roadmap_json(raw_json):
    try:
        start_idx = raw_json.find('[')
        end_idx = raw_json.rfind(']') + 1
        json_str = raw_json[start_idx:end_idx]
        roadmap = json.loads(json_str)
        return roadmap
    except Exception as e:
        st.error(f"Error decoding roadmap JSON: {e}")
        st.text_area("Raw Roadmap JSON:", raw_json, height=200)
        return None

def render_graphviz_roadmap(roadmap):
    if not roadmap:
        st.warning("Roadmap data unavailable or invalid.")
        return
    from graphviz import Digraph
    dot = Digraph(comment="Career Roadmap")
    for step in roadmap:
        label = f"Step {step.get('step_number', '?')}\n{step.get('title', 'No title')}\n({step.get('expected_duration_weeks', '?')} weeks)"
        dot.node(str(step.get('step_number', '?')), label)
    for i in range(len(roadmap)-1):
        dot.edge(str(roadmap[i].get('step_number', '?')), str(roadmap[i+1].get('step_number', '?')))
    st.graphviz_chart(dot)

def get_checklist_items(text):
    items = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
    return items

def init_checklist_states(num_items):
    if "practice_states" not in st.session_state:
        st.session_state.practice_states = {}
    for idx in range(num_items):
        key = f"practice_{idx}"
        if key not in st.session_state.practice_states:
            st.session_state.practice_states[key] = False

def display_practice_checklist(practice_text):
    st.write("### Practice Plan Checklist")
    checklist_items = get_checklist_items(practice_text)
    if not checklist_items:
        st.write("No checklist items found; showing full practice plan below:")
        st.text_area("Practice Plan", practice_text, height=250)
        return

    init_checklist_states(len(checklist_items))

    for idx, item in enumerate(checklist_items):
        key = f"practice_{idx}"
        checked = st.checkbox(item, value=st.session_state.practice_states[key], key=key)
        st.session_state.practice_states[key] = checked

# Firestore save/load functions
def save_progress(user_id, practice_states):
    doc_ref = db.collection("users").document(user_id)
    doc_ref.set({"practice_progress": practice_states}, merge=True)
    st.success("Practice progress saved to Firestore!")

def load_progress(user_id):
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("practice_progress", {})
    return {}

# Simple login simulation for demo (replace with real login later)
def simple_login():
    st.sidebar.header("User Authentication")
    email = st.sidebar.text_input("Email")
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if st.sidebar.button("Login"):
        if email:
            st.session_state.user_email = email
            st.success(f"Logged in as {email}")
        else:
            st.error("Enter an email to login.")
    if st.session_state.user_email:
        st.sidebar.write(f"Logged in: {st.session_state.user_email}")
        if st.sidebar.button("Logout"):
            st.session_state.user_email = None
            st.experimental_rerun()

simple_login()

if not st.session_state.get("user_email"):
    st.warning("Please login from the sidebar to continue.")
    st.stop()

user_id = st.session_state.user_email  # use email as user_id for demo

# Main app UI
st.set_page_config(page_title="AI Career Advisor with Firestore", layout="wide")
st.title("AI-Powered Career Advisor with Firestore Persistence")

with st.sidebar:
    st.header("Profile Information")
    age = st.number_input("Age", 10, 60)
    location = st.text_input("City or State")
    education = st.text_input("Education Background")

    st.write("Enter skills and your proficiency (1-5):")
    skills = {}
    for i in range(3):
        skill = st.text_input(f"Skill {i+1}", key=f"skill{i}")
        level = st.slider(f"Proficiency Level {i+1}", 1, 5, 3, key=f"level{i}")
        if skill:
            skills[skill] = level
    skills_text = ", ".join([f"{s} (level {l})" for s, l in skills.items()])

    interests = st.text_input("Interests (comma-separated)")
    goals = st.text_input("Career Goals")

    submit = st.button("Get Career Advice")
    if submit:
        st.session_state.generated = True
        st.session_state.age = age
        st.session_state.location = location
        st.session_state.education = education
        st.session_state.skills_text = skills_text
        st.session_state.interests = interests
        st.session_state.goals = goals

if not st.session_state.get("generated", False):
    st.info("Please fill in your profile and click 'Get Career Advice' to begin.")
    st.stop()

prompt = f"""
I am a {st.session_state.age}-year-old student from {st.session_state.location}, India.
My education background: {st.session_state.education}.
My skills with proficiency levels: {st.session_state.skills_text}.
My interests include: {st.session_state.interests}.
My career goals are: {st.session_state.goals}.

Please respond with the following sections with EXACT headers:

===Career Suggestions===
[List 3 career paths with explanations.]

===Roadmap===
[Provide ONLY a valid JSON array with steps like:
[
  {{
    "step_number": 1,
    "title": "Step title",
    "description": "Step description",
    "expected_duration_weeks": 4
  }},
  ...
]
Do NOT add extra text outside JSON in this section.]

===Skill Gap Analysis & Practice Plan===
[Describe skills to develop and provide a bullet-pointed practice plan starting each point exactly with a dash and a space ("- ").]

===Learning Resources===
[List relevant courses, books, or tutorials.]

Include only these sections with headers, no extra text.
"""

with st.spinner("Generating career advice..."):
    ai_response = get_ai_response(prompt)

sections = split_sections(ai_response)
roadmap_raw = sections.get("roadmap", "").strip()
roadmap = parse_roadmap_json(roadmap_raw)

tabs = st.tabs(["Career Suggestions", "Visual Roadmap", "Skill Gap Analysis & Practice Plan", "Learning Resources"])

with tabs[0]:
    st.markdown("### Career Suggestions")
    st.text_area("Career Suggestions", sections.get("career", "No suggestions available."), height=300, key="career_suggestions")

with tabs[1]:
    st.markdown("### Career Roadmap")
    render_graphviz_roadmap(roadmap)

with tabs[2]:
    st.markdown("### Skill Gap Analysis & Practice Plan")
    practice_text = sections.get("skill_gap", "No practice plan found.")
    display_practice_checklist(practice_text)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Practice Progress"):
            save_progress(user_id, st.session_state.practice_states)
    with col2:
        if st.button("Load Practice Progress"):
            loaded = load_progress(user_id)
            if loaded:
                st.session_state.practice_states = loaded
                st.experimental_rerun()
            else:
                st.warning("No saved progress found.")

with tabs[3]:
    st.markdown("### Learning Resources")
    st.text_area("Learning Resources", sections.get("learning", "No learning resources found."), height=300)
