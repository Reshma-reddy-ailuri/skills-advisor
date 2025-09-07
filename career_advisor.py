import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os
from dotenv import load_dotenv
import graphviz

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
if "practice_states" not in st.session_state:
    st.session_state.practice_states = {}


st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { background-color: #f3e5f5; color: #37474f; padding: 24px 20px 40px 20px !important; font-weight: 600; min-width: 320px !important; border: none !important; }
    .block-container { background-color: #f9fdfa; padding: 32px 48px 48px 48px !important; max-width: 900px; margin: auto; font-size: 1.1rem; color: #37474f; }
    h2, h3 { color: #4db6ac; padding-bottom: 8px; }
    ul { padding-left: 1.5rem; }
    li { margin-bottom: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- FUNCTION DEFINITIONS ---


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


def extract_json_block(text):
    text = text.strip()
    if text.startswith("json"):
        text = text[len("json") :].strip()
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
        dot = graphviz.Digraph(
            node_attr={"style": "filled", "fillcolor": "#ade8f4", "fontname": "Segoe UI"}
        )
        dot.attr(rankdir="TB", size="8,5")  # Vertical layout for better readability
        for step in data:
            num = str(step.get("step_number", "?"))
            label = f"{step.get('title', '')}\n({step.get('expected_duration_weeks', '?')} weeks)"
            dot.node(num, label)
        for i in range(len(data) - 1):
            from_node = str(data[i].get("step_number", "?"))
            to_node = str(data[i + 1].get("step_number", "?"))
            dot.edge(from_node, to_node)
        st.graphviz_chart(dot)
    except Exception as e:
        st.error(f"Could not draw roadmap: {e}")
        st.text_area("Raw roadmap data (please verify format):", roadmap_json, height=200)


def get_checklist_items(practice_text):
    if "Practice Plan Checklist:" in practice_text:
        checklist_part = practice_text.split("Practice Plan Checklist:")[1]
        return [line[2:].strip() for line in checklist_part.split("\n") if line.strip().startswith("- ")]
    return []


def checklist_with_persistence(items):
    if "practice_states" not in st.session_state:
        st.session_state.practice_states = {}
    for i, item in enumerate(items):
        key = f"practice_{i}"
        if key not in st.session_state.practice_states:
            st.session_state.practice_states[key] = False
        checked = st.checkbox(item, key=key, value=st.session_state.practice_states[key])
        st.session_state.practice_states[key] = checked


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
        "Hiring Cloud": f"https://hiringcloud.in/jobs?query={keywords.replace(' ', '%20')}",
    }


def save_progress(user_id, practice_states):
    if user_id and practice_states:
        db.collection("practice_progress").document(user_id).set({"states": practice_states})
        st.success("Practice progress saved successfully.")
    else:
        st.warning("No progress to save.")


def load_progress(user_id):
    if user_id:
        doc = db.collection("practice_progress").document(user_id).get()
        if doc.exists:
            return doc.to_dict().get("states", {})
    return None


# --- SIDEBAR INPUTS ---
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
    interests = st.text_input("Interests (comma-separated)")
    goals = st.text_input("Career Goals")

    submit = st.button("Get Career Advice")

if submit:
    # Build prompt
    skills_text = ", ".join([f"{s} (level {l})" for s, l in skills.items()])
    prompt = f"""
I am a {age}-year-old student from {location}, India. My education background: {education}. My skills with proficiency levels: {skills_text}. My interests include: {interests}. My career goals are: {goals}.
Please provide the output in the following exact sections:
===Career Suggestions=== Provide exactly 3 career suggestions, each as a bullet point like:
Career Name: brief explanation.
===Roadmap===
[
  {{
    "step_number": 1,
    "title": "Foundational Math & Statistics",
    "description": "Strengthen linear algebra, calculus, probability, and statistics.",
    "expected_duration_weeks": 8
  }},
  {{
    "step_number": 2,
    "title": "Python Programming for Data Science",
    "description": "Master NumPy, Pandas, Matplotlib, Seaborn, and Scikit-learn.",
    "expected_duration_weeks": 12
  }},
  {{
    "step_number": 3,
    "title": "Machine Learning Fundamentals",
    "description": "Learn various ML algorithms (regression, classification, clustering).",
    "expected_duration_weeks": 16
  }},
  {{
    "step_number": 4,
    "title": "Deep Learning (Optional but Recommended)",
    "description": "Understand neural networks, CNNs, RNNs, and TensorFlow/PyTorch.",
    "expected_duration_weeks": 12
  }},
  {{
    "step_number": 5,
    "title": "Data Visualization & Communication",
    "description": "Improve data storytelling and presentation skills.",
    "expected_duration_weeks": 4
  }},
  {{
    "step_number": 6,
    "title": "Capstone Project",
    "description": "Work on a real-world data science project to showcase skills.",
    "expected_duration_weeks": 12
  }},
  {{
    "step_number": 7,
    "title": "Job Search & Networking",
    "description": "Prepare resume, portfolio, and network with professionals.",
    "expected_duration_weeks": 8
  }}
]
===Skill Gap Analysis & Practice Plan===
Skills to Develop:
- Advanced Python libraries (e.g., scikit-learn, TensorFlow, PyTorch)
- Deep Learning techniques
- Database management (SQL)
- Big Data technologies (e.g., Spark, Hadoop - optional initially)
- Data cleaning and preprocessing techniques
- Model deployment and monitoring
- Strong communication and presentation skills

Practice Plan Checklist:
- Work on personal projects using publicly available datasets.
- Participate in Kaggle competitions to gain experience.
- Contribute to data science projects on GitHub.
- Showcase your projects and skills on a personal website or GitHub.
- Present your projects to friends, family, or online communities.
- Attend meetups and conferences related to data science.

===Learning Resources=== List relevant courses, books, or tutorials as bullet points.
===Practice Websites=== List practice websites with markdown links like [site](https://www.notion.so/url).

No extra text outside these sections.
"""
    ai_response = get_ai_response(prompt)
    sections = split_sections(ai_response)

    # Show outputs in main section
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

    with tabs[0]:
        st.header("Career Suggestions")
        career_text = sections.get("career", "").strip()
        if career_text:
            render_career_suggestions(career_text)
        else:
            st.info("No career suggestions available.")

    with tabs[1]:
        st.header("Career Roadmap")
        roadmap_text = sections.get("roadmap", "").strip()
        if roadmap_text:
            render_graphviz_roadmap(roadmap_text)
        else:
            st.info("No roadmap data available.")

    with tabs[2]:
        st.header("Skill Gap Analysis & Practice Plan")
        skill_gap_text = sections.get("skill_gap", "").strip()
        if skill_gap_text:
            # Separate skills and checklist parts to render properly
            if "Practice Plan Checklist:" in skill_gap_text:
                skills_part, checklist_part = skill_gap_text.split("Practice Plan Checklist:", 1)
            else:
                skills_part, checklist_part = skill_gap_text, ""

            # Show skills as markdown
            if skills_part.strip():
                st.markdown(skills_part)

            # Extract checklist items and render checkboxes with persistence
            checklist_items = get_checklist_items("Practice Plan Checklist:" + checklist_part)
            if checklist_items:
                st.write("Practice Plan Checklist:")
                checklist_with_persistence(checklist_items)

            # Save/load buttons side by side
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Practice Progress"):
                    save_progress(user_id, st.session_state.practice_states)
            with col2:
                if st.button("Load Practice Progress"):
                    loaded_states = load_progress(user_id)
                    if loaded_states:
                        st.session_state.practice_states = loaded_states
                        st.experimental_rerun()
                    else:
                        st.warning("No saved progress found.")
        else:
            st.info("No skill gap analysis available.")

    with tabs[3]:
        st.header("Learning Resources")
        learning_text = sections.get("learning", "").strip()
        if learning_text:
            render_learning_resources(learning_text)
        else:
            st.info("No learning resources provided.")

    with tabs[4]:
        st.header("Practice Websites")
        practice_websites_text = sections.get("practice_websites", "").strip()
        if practice_websites_text:
            st.markdown(practice_websites_text, unsafe_allow_html=True)
        else:
            st.info("No practice websites listed.")

    with tabs[5]:
        st.header("Job Search Platforms")
        if skills and location:
            job_links = get_job_platform_links(", ".join([f"{s} (level {l})" for s, l in skills.items()]), location)
            for platform, url in job_links.items():
                st.markdown(f"- [{platform}]({url})", unsafe_allow_html=True)
        else:
            st.info("Enter skills and location to view job search platforms.")
else:
    st.info("Fill profile and click 'Get Career Advice' to generate suggestions.")
