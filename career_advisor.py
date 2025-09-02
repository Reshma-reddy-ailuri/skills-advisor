import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os
from dotenv import load_dotenv

# Load Gemini API Key and initialize Firebase
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
firebase_creds_str = st.secrets["FIREBASE_SERVICE_ACCOUNT"]
firebase_creds_dict = json.loads(firebase_creds_str)

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()

def sidebar_login():
    st.sidebar.header("User Login")
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    email = st.sidebar.text_input("Enter your email", value=st.session_state.user_email)
    login_button = st.sidebar.button("Login")
    logout_button = st.sidebar.button("Logout")

    if login_button and email:
        st.session_state.user_email = email
        st.sidebar.success(f"Logged in as {email}")
    if logout_button:
        st.session_state.user_email = ""
        # Without experimental_rerun, page refresh is manual

sidebar_login()

if not st.session_state.user_email:
    st.info("Please login using the sidebar to continue.")
    st.stop()

user_id = st.session_state.user_email

# Styling for more spacing and web-like look
st.markdown("""
    <style>
    .block-container {padding-top: 2rem !important;}
    .stTabs { margin-bottom: 1.5rem !important;}
    section[data-testid="stHorizontalBlock"] > div { padding: 1.2rem 2rem;}
    h1, .stTabs [role="tab"] { font-size: 2rem; }
    .stMarkdown { font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

def get_ai_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1600,
            "topP": 1,
            "topK": 1
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        resp = response.json()
        try:
            return resp["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return "Could not parse AI response."
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
        elif current:
            sections[current] += line + "\n"
    return sections

def render_graphviz_roadmap(roadmap_json):
    try:
        data = json.loads(roadmap_json)
        from graphviz import Digraph
        dot = Digraph()
        for step in data:
            num = str(step["step_number"])
            label = f'''{step["title"]}\n({step["expected_duration_weeks"]} weeks)'''
            dot.node(num, label)
        for i in range(len(data)-1):
            dot.edge(str(data[i]["step_number"]), str(data[i+1]["step_number"]))
        st.graphviz_chart(dot)
    except Exception as e:
        st.error(f"Could not draw roadmap: {e}")

def get_checklist_items(practice_text):
    return [line[2:].strip() for line in practice_text.split('\n') if line.strip().startswith("- ")]

def generate_linkedin_job_url(keywords, location):
    base_url = "https://www.linkedin.com/jobs/search/"
    query = f"?keywords={keywords.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
    return base_url + query

def get_job_platform_links(keywords, location):
    return {
        "LinkedIn Jobs": generate_linkedin_job_url(keywords, location),
        "Unstop Jobs": f"https://unstop.com/jobs?search={keywords.replace(' ', '%20')}&location={location.replace(' ', '%20')}",
        "Hiring Cloud": f"https://hiringcloud.in/jobs?query={keywords.replace(' ', '%20')}"
    }

st.header("AI-Powered Career Advisor with Referrals")

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

if not submit:
    st.info("Fill profile and click 'Get Career Advice' to generate suggestions.")
    st.stop()

prompt = f"""
I am a {age}-year-old student from {location}, India.
My education background: {education}.
My skills with proficiency levels: {skills_text}.
My interests include: {interests}.
My career goals are: {goals}.

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

===Practice Websites===
[List relevant practice websites with markdown links like [site](url).]

Include only these sections with headers, no extra text.
"""

ai_response = get_ai_response(prompt)
sections = split_sections(ai_response)

tabs = st.tabs(["Career Suggestions", "Roadmap", "Skill Gap Analysis", "Learning Resources", "Practice Websites", "Job Search Platforms"])

with tabs[0]:
    st.header("Career Suggestions")
    st.markdown(sections["career"].strip())

with tabs[1]:
    st.header("Roadmap")
    render_graphviz_roadmap(sections["roadmap"].strip())

with tabs[2]:
    st.header("Skill Gap Analysis & Practice Plan")
    checklist_items = get_checklist_items(sections["skill_gap"])
    if checklist_items:
        st.write("Practice Plan Checklist:")
        for i, item in enumerate(checklist_items):
            st.checkbox(item, key=f"practice_{i}")
    else:
        st.markdown(sections["skill_gap"].strip())

with tabs[3]:
    st.header("Learning Resources")
    st.markdown(sections["learning"].strip())

with tabs[4]:
    st.header("Practice Websites")
    st.markdown(sections["practice_websites"], unsafe_allow_html=True)

with tabs[5]:
    st.header("Job Search Platforms")
    job_links = get_job_platform_links(skills_text, location)
    for platform, url in job_links.items():
        st.markdown(f"- [{platform}]({url})", unsafe_allow_html=True)
