import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load local .env if available
load_dotenv()

# Prefer Streamlit secrets, else fallback to .env
API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def generate_gemini_response(prompt: str) -> str:
    """Send prompt to Gemini API and return safe text output"""
    if not API_KEY:
        return "❌ API key not found. Please set GEMINI_API_KEY."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    body = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=body, timeout=30)

        if response.status_code != 200:
            return f"❌ API Error {response.status_code}: {response.text}"

        data = response.json()
        # Safely extract response text
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        if not text.strip():
            return f"⚠️ Empty response. Raw: {data}"

        return text

    except Exception as e:
        return f"⚠️ Exception: {str(e)}"
def build_prompts(user_data):
    return {
        "career_suggestions": f"Based on this profile: {user_data}, suggest 3 possible career paths with explanations.",
        "roadmap": f"Create a step-by-step learning roadmap for this user: {user_data}.",
        "skill_gap": f"Identify skill gaps for this profile and how to close them: {user_data}.",
        "resources": f"List online resources, courses, and certifications useful for this profile: {user_data}.",
        "practice": f"Suggest practice websites, coding platforms, or exercises for this profile: {user_data}.",
        "jobs": f"Suggest job search platforms and networking strategies for this profile: {user_data}.",
    }
st.title("AI-Powered Career Advisor Results")

user_data = {"name": "reshma_ailuri"}  # <-- replace with form data
prompts = build_prompts(user_data)

# Initialize session state
if "sections" not in st.session_state:
    st.session_state.sections = {}

tabs = st.tabs([
    "Career Suggestions", "Roadmap", "Skill Gap Analysis",
    "Learning Resources", "Practice Websites", "Job Search Platforms"
])

tab_keys = ["career_suggestions", "roadmap", "skill_gap", "resources", "practice", "jobs"]

for tab, key in zip(tabs, tab_keys):
    with tab:
        st.subheader(key.replace("_", " ").title())

        if key not in st.session_state.sections:
            with st.spinner(f"Generating {key.replace('_',' ')}..."):
                st.session_state.sections[key] = generate_gemini_response(prompts[key])

        st.write(st.session_state.sections[key])
