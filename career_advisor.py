import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os
from dotenv import load_dotenv
import graphviz  # Added import

# Load API keys and Firebase credentials
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

sidebar_login()
if not st.session_state.user_email:
    st.info("Please login using the sidebar to continue.")
    st.stop()
user_id = st.session_state.user_email

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f3e5f5; color: #37474f; padding: 24px 20px 40px 20px !important; font-weight: 600; min-width: 320px !important; border: none !important; }
    .block-container { background-color: #f9fdfa; padding: 32px 48px 48px 48px !important; max-width: 900px; margin: auto; font-size: 1.1rem; color: #37474f; }
    h2, h3 { color: #4db6ac; padding-bottom: 8px; }
    ul { padding-left: 1.5rem; }
    li { margin-bottom: 12px; }
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
            return resp["candidates"]["content"]["parts"]["text"]
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

def extract_json_block(text):
    text = text.strip()
    # Remove 'json' prefix if present
    if text.startswith("json"):
        text = text[len("json"):].strip()
    return text

def render_graphviz_roadmap(roadmap_json):
    roadmap_json = extract_json_block(roadmap_json)
    if not roadmap_json:
        st.info("No roadmap data available yet.")
        return
    try:
        data = json.loads(roadmap_json)
        if not data:
            st.info("Roadmap JSON is empty.")
            return
        dot = graphviz.Digraph(node_attr={'style': 'filled', 'fillcolor': '#ade8f4', 'fontname': 'Segoe UI'})
        dot.attr(rankdir='LR', size='8,5')
        # Add nodes and labels
        for step in data:
            num = str(step.get("step_number", "?"))
            label = f"{step.get('title', '')}\n({step.get('expected_duration_weeks', '?')} weeks)"
            dot.node(num, label)
        # Add edges
        for i in range(len(data)-1):
            from_node = str(data[i].get("step_number", "?"))
            to_node = str(data[i+1].get("step_number", "?"))
            dot.edge(from_node, to_node)
        st.graphviz_chart(dot)  # This renders the chart
    except Exception as e:
        st.error(f"Could not draw roadmap: {e}")
        st.text_area("Raw roadmap data (please verify format):", roadmap_json, height=200)

def get_checklist_items(practice_text):
    return [line[2:].strip() for line in practice_text.split('\n') if line.strip().startswith("- ")]

def checklist_with_persistence(items):
    for i, item in enumerate(items):
        key = f"practice_{i}"
        st.checkbox(item, key=key)

def render_learning_resources(text):
    lines = text.strip().split("\n")
    md_lines = []
    for line in lines:
        line = line.strip()
        if line:
            if line.startswith("- ") or line.startswith("* "):
                md_lines.append(line)
            else:
                md_lines.append(f"- {line}")
    st.markdown("\n".join(md_lines))

def render_career_suggestions(text):
    lines = [line.lstrip("-* \t").strip() for line in text.splitlines() if line.strip()]
    st.markdown("\n".join(f"- {line}" for line in lines))

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
I am a {age}-year-old student from {location}, India. My education background: {education}. My skills with proficiency levels: {skills_text}. My interests include: {interests}. My career goals are: {goals}.
Please provide the output in the following exact sections:
===Career Suggestions=== Provide exactly 3 career suggestions, each as a bullet point like:
Career Name: brief explanation.
===Roadmap=== Provide ONLY a valid JSON array (no extra text) for the roadmap steps as below:
[ {{ "step_number": 1, "title": "Step title", "description": "Step description", "expected_duration_weeks": 4 }}, ... ]
===Skill Gap Analysis & Practice Plan=== List skills to develop and provide a bullet point practice plan.
===Learning Resources=== List relevant courses, books, or tutorials as bullet points.
===Practice Websites=== List practice websites with markdown links like [site](https://www.notion.so/url).
No extra text outside these sections.
"""
ai_response = get_ai_response(prompt)
sections = split_sections(ai_response)

tabs = st.tabs(["Career Suggestions", "Roadmap", "Skill Gap Analysis", "Learning Resources", "Practice Websites", "Job Search Platforms"])
with tabs:
    st.header("Career Suggestions")
    render_career_suggestions(sections["career"].strip())
with tabs[15]:
    st.header("Roadmap")
    render_graphviz_roadmap(sections["roadmap"])
with tabs[16]:
    st.header("Skill Gap Analysis & Practice Plan")
    checklist_items = get_checklist_items(sections["skill_gap"])
    if checklist_items:
        st.write("Practice Plan Checklist:")
        checklist_with_persistence(checklist_items)
    extra_options = sections["skill_gap"].split("\n")
    extras = [line for line in extra_options if not line.strip().startswith("- ")]
    if extras:
        st.markdown("\n".join(extras))
    else:
        st.markdown(sections["skill_gap"].strip())
with tabs[17]:
    st.header("Learning Resources")
    if sections["learning"].strip():
        render_learning_resources(sections["learning"])
    else:
        st.info("No learning resources found.")
with tabs[18]:
    st.header("Practice Websites")
    st.markdown(sections["practice_websites"], unsafe_allow_html=True)
with tabs[19]:
    st.header("Job Search Platforms")
    job_links = get_job_platform_links(skills_text, location)
    for platform, url in job_links.items():
        st.markdown(f"- [{platform}]({url})", unsafe_allow_html=True)
