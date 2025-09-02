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

# No explicit login rerun for now; simple sidebar login fields
def sidebar_login():
    st.sidebar.header("User Login")
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    email = st.sidebar.text_input("Enter your email", value=st.session_state.user_email)
    login_button = st.sidebar.button("Login")
    logout_button = st.sidebar.button("Logout")

    if login_button and email:
        st.session_state.user_email = email
        st.success(f"Logged in as {email}")
    if logout_button:
        st.session_state.user_email = ""
        st.experimental_rerun()

sidebar_login()

if not st.session_state.user_email:
    st.info("Please login using the sidebar to continue.")
    st.stop()

user_id = st.session_state.user_email  # Using email as user id for simplicity

# CSS palette for styling (same as before)
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: #ede7f6;
    color: #37474f;
    border-right: 3px solid #80cbc4;
    padding: 20px 25px 50px 25px !important;
    font-weight: 600;
    min-width: 320px !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select {
    border-radius: 10px !important;
    border: 1.5px solid #b2dfdb !important;
    padding: 10px 14px !important;
    margin-bottom: 16px !important;
    font-size: 15px !important;
    color: #37474f !important;
}
.stButton > button {
    background-color: #4db6ac;
    color: white !important;
    border-radius: 14px;
    padding: 14px 40px;
    margin-top: 18px !important;
}
.css-1d391kg {
    max-width: 900px !important;
    margin: 0 auto !important;
    padding: 32px 24px !important;
}
[role="tabpanel"] {
    border: 1.5px solid #b2dfdb;
    border-radius: 14px;
    padding: 20px;
    background-color: #f9fdfa;
    margin-bottom: 30px;
}
textarea {
    background-color: #f1fafe;
    border-radius: 14px;
    border: 1.5px solid #b2dfdb;
    padding: 14px 20px;
    min-height: 280px;
    resize: vertical;
    box-shadow: inset 0 0 10px rgba(128, 203, 196, 0.2);
}
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
    st.subheader("Career Suggestions")
    st.text_area("Suggestions", sections["career"], height=300)

with tabs[1]:
    st.subheader("Roadmap")
    st.text_area("Roadmap JSON", sections["roadmap"], height=300)

with tabs[2]:
    st.subheader("Skill Gap Analysis & Practice Plan")
    st.text_area("Practice Plan", sections["skill_gap"], height=300)

with tabs[3]:
    st.subheader("Learning Resources")
    st.text_area("Learning Resources", sections["learning"], height=300)

with tabs[4]:
    st.subheader("Practice Websites")
    st.markdown(sections["practice_websites"], unsafe_allow_html=True)

with tabs[5]:
    st.subheader("Job Search Platforms")
    job_links = get_job_platform_links(skills_text, location)
    for platform, url in job_links.items():
        st.markdown(f"- [{platform}]({url})", unsafe_allow_html=True)
