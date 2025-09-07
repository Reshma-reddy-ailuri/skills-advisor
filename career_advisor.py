import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os
from dotenv import load_dotenv
import graphviz

# ------------------------------------------------
# Page config
# ------------------------------------------------
st.set_page_config(page_title="AI Skills Career Advisor", layout="wide")

# ------------------------------------------------
# Load API keys and Firebase credentials
# ------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# Firestore init (expects FIREBASE_SERVICE_ACCOUNT in st.secrets)
if not firebase_admin._apps:
    firebase_creds_str = st.secrets["FIREBASE_SERVICE_ACCOUNT"]
    firebase_creds_dict = json.loads(firebase_creds_str)
    cred = credentials.Certificate(firebase_creds_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ------------------------------------------------
# Helpers: backgrounds & theme
# ------------------------------------------------
def set_background(image_url: str):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("{image_url}") no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def inject_global_theme():
    st.markdown(
        """
        <style>
        /* Main content card feel */
        .block-container {
            background-color: rgba(249, 253, 250, 0.92);
            padding: 32px 48px 48px 48px !important;
            max-width: 1000px;
            margin: 32px auto;
            border-radius: 16px;
            box-shadow: 0px 8px 24px rgba(0,0,0,0.15);
        }
        h1, h2, h3 {
            color: #4db6ac;
            font-weight: 700;
        }
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #f3e5f5;
            color: #37474f;
            padding: 24px 20px 40px 20px !important;
            min-width: 320px !important;
            border: none !important;
        }
        /* Inputs & buttons */
        .stTextInput>div>div>input,
        .stSelectbox>div>div>div>input,
        .stNumberInput>div>div>input {
            border-radius: 10px;
            border: 1px solid #cfd8dc;
            padding: 0.55em 0.7em;
        }
        .stSlider {
            padding-top: 4px;
        }
        .stButton>button {
            background-color: #4db6ac;
            color: #fff;
            border-radius: 10px;
            padding: 0.65em 1.2em;
            font-size: 1rem;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #009688;
            transform: translateY(-1px);
        }
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 18px;
            border-radius: 12px 12px 0 0;
            background-color: #e0f7fa;
            font-weight: 600;
            color: #37474f;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4db6ac !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True
    )

# Profile menu CSS (hover dropdown)
PROFILE_MENU_CSS = """
<style>
.profile-menu {
    position: fixed;
    top: 16px;
    right: 24px;
    display: inline-block;
    z-index: 9999;
}
.profile-btn {
    background: linear-gradient(135deg, #6a11cb, #2575fc);
    color: #fff;
    padding: 10px 16px;
    border: none;
    border-radius: 30px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.profile-dropdown {
    display: none;
    position: absolute;
    right: 0;
    background: #fff;
    min-width: 220px;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    margin-top: 10px;
    padding: 10px;
}
.profile-dropdown a, .profile-dropdown button {
    width: 100%;
    display: block;
    background: transparent;
    border: none;
    text-align: left;
    padding: 10px 12px;
    border-radius: 8px;
    font-weight: 600;
    color: #37474f;
    cursor: pointer;
    text-decoration: none;
}
.profile-dropdown a:hover, .profile-dropdown button:hover {
    background: #f5f5f5;
}
.profile-menu:hover .profile-dropdown {
    display: block;
}
.logout {
    color: #fff !important;
    background: #ff4b5c !important;
    text-align: center !important;
}
.logout:hover {
    background: #d90429 !important;
}
.profile-meta {
    font-size: 12px; color: #546e7a; padding: 0 12px 6px 12px;
}
</style>
"""

# ------------------------------------------------
# AI (Gemini) function
# ------------------------------------------------
def get_ai_response(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1600, "topP": 1, "topK": 1},
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=45)
    except Exception as e:
        return f"API error: {e}"
    if response.status_code == 200:
        resp = response.json()
        try:
            return resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Could not parse AI response: {e}"
    else:
        return f"API error: {response.status_code}"

# ------------------------------------------------
# Parsing & UI helpers
# ------------------------------------------------
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
        dot = graphviz.Digraph(node_attr={"style": "filled", "fillcolor": "#ade8f4", "fontname": "Segoe UI"})
        dot.attr(rankdir="TB", size="8,5")
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

# ------------------------------------------------
# Login Page (username + email)
# ------------------------------------------------
def login_page():
    set_background("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1650&q=80")
    st.markdown(
        """
        <div style="height: 14vh;"></div>
        <h2 style="text-align:center; color:white; text-shadow:0 2px 8px rgba(0,0,0,0.5);">
            Welcome to AI Skills Career Advisor
        </h2>
        """, unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style='
            background-color: rgba(255, 255, 255, 0.94);
            padding: 30px;
            border-radius: 16px;
            width: 380px;
            margin: 24px auto 0 auto;
            box-shadow: 0 12px 32px rgba(0,0,0,0.35);
            border: 2px solid #4db6ac;
        '>
        """, unsafe_allow_html=True
    )
    username = st.text_input("👤 Username", key="login_username")
    email = st.text_input("📧 Email", key="login_email")
    if st.button("Login", use_container_width=True):
        if username and email:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_email = email
            if "practice_states" not in st.session_state:
                st.session_state.practice_states = {}
            st.rerun()
        else:
            st.warning("⚠️ Please enter both username and email!")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------
# Profile dropdown (hover) + query-param actions
# ------------------------------------------------
def profile_menu():
    st.markdown(PROFILE_MENU_CSS, unsafe_allow_html=True)
    username = st.session_state.get("username", "User")
    email = st.session_state.get("user_email", "")

    st.markdown(
        f"""
        <div class="profile-menu">
            <button class="profile-btn">👤 {username}</button>
            <div class="profile-dropdown">
                <div class="profile-meta"><b>{username}</b><br>{email}</div>
                <a href="?edit=1">✏️ Edit Profile</a>
                <a href="?about=1">ℹ️ About</a>
                <a class="logout" href="?logout=1">🚪 Logout</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Handle dropdown actions via query params
    qp = st.query_params
    if "logout" in qp:
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

    if "about" in qp:
        st.info("AI Skills Career Advisor • v1.0 — Personalize skills, discover roadmaps, and track practice progress.")
        # Clear only 'about'
        st.query_params["about"] = None

    if "edit" in qp:
        with st.expander("Edit Profile", expanded=True):
            new_username = st.text_input("Username", value=username, key="edit_username")
            new_email = st.text_input("Email", value=email, key="edit_email")
            cols = st.columns(2)
            with cols[0]:
                if st.button("Save Changes"):
                    st.session_state.username = new_username.strip() or username
                    st.session_state.user_email = new_email.strip() or email
                    if "edit" in st.query_params:
                        st.query_params["edit"] = None
                    st.success("Profile updated.")
                    st.rerun()
            with cols[1]:
                if st.button("Cancel"):
                    if "edit" in st.query_params:
                        st.query_params["edit"] = None
                    st.rerun()

# ------------------------------------------------
# Main App (after login)
# ------------------------------------------------
def main_app():
    set_background("https://images.unsplash.com/photo-1508780709619-79562169bc64?auto=format&fit=crop&w=1650&q=80")
    inject_global_theme()
    profile_menu()

    st.title("🎓 AI Skills & Career Advisor")

    # Sidebar inputs (profile for AI prompt)
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
        submit = st.button("Get Career Advice", use_container_width=True)

    user_id = st.session_state.get("user_email", "")

    if submit:
        # Build prompt for Gemini
        skills_text = ", ".join([f"{s} (level {l})" for s, l in skills.items()])
        prompt = f"""
I am a {age}-year-old student from {location}, India.
My education background: {education}.
My skills with proficiency levels: {skills_text}.
My interests include: {interests}.
My career goals are: {goals}.
Please provide the output in the following exact sections:
===Career Suggestions===
Provide exactly 3 career suggestions, each as a bullet point like:
Career Name: brief explanation.
===Roadmap===
[ {{ "step_number": 1, "title": "Foundational Math & Statistics", "description": "Strengthen linear algebra, calculus, probability, and statistics.", "expected_duration_weeks": 8 }},
  {{ "step_number": 2, "title": "Python Programming for Data Science", "description": "Master NumPy, Pandas, Matplotlib, Seaborn, and Scikit-learn.", "expected_duration_weeks": 12 }},
  {{ "step_number": 3, "title": "Machine Learning Fundamentals", "description": "Learn various ML algorithms (regression, classification, clustering).", "expected_duration_weeks": 16 }},
  {{ "step_number": 4, "title": "Deep Learning (Optional but Recommended)", "description": "Understand neural networks, CNNs, RNNs, and TensorFlow/PyTorch.", "expected_duration_weeks": 12 }},
  {{ "step_number": 5, "title": "Data Visualization & Communication", "description": "Improve data storytelling and presentation skills.", "expected_duration_weeks": 4 }},
  {{ "step_number": 6, "title": "Capstone Project", "description": "Work on a real-world data science project to showcase skills.", "expected_duration_weeks": 12 }},
  {{ "step_number": 7, "title": "Job Search & Networking", "description": "Prepare resume, portfolio, and network with professionals.", "expected_duration_weeks": 8 }} ]
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
===Learning Resources===
List relevant courses, books, or tutorials as bullet points.
===Practice Websites===
List practice websites with markdown links like [site](https://www.notion.so/url).
No extra text outside these sections.
"""
        ai_response = get_ai_response(prompt)
        sections = split_sections(ai_response)

        # Main outputs
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
            st.subheader("Career Suggestions")
            career_text = sections.get("career", "").strip()
            if career_text:
                render_career_suggestions(career_text)
            else:
                st.info("No career suggestions available.")

        with tabs[1]:
            st.subheader("Career Roadmap")
            roadmap_text = sections.get("roadmap", "").strip()
            if roadmap_text:
                render_graphviz_roadmap(roadmap_text)
            else:
                st.info("No roadmap data available.")

        with tabs[2]:
            st.subheader("Skill Gap Analysis & Practice Plan")
            skill_gap_text = sections.get("skill_gap", "").strip()
            if skill_gap_text:
                # Split skills and checklist text
                if "Practice Plan Checklist:" in skill_gap_text:
                    skills_part, checklist_part = skill_gap_text.split("Practice Plan Checklist:", 1)
                else:
                    skills_part, checklist_part = skill_gap_text, ""

                if skills_part.strip():
                    st.markdown(skills_part)

                # Checklist with persistence
                checklist_items = get_checklist_items("Practice Plan Checklist:" + checklist_part)
                if checklist_items:
                    st.write("Practice Plan Checklist:")
                    checklist_with_persistence(checklist_items)

                # Save / Load progress
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Practice Progress"):
                        save_progress(user_id, st.session_state.practice_states)
                with col2:
                    if st.button("Load Practice Progress"):
                        loaded_states = load_progress(user_id)
                        if loaded_states:
                            st.session_state.practice_states = loaded_states
                            st.rerun()
                        else:
                            st.warning("No saved progress found.")
            else:
                st.info("No skill gap analysis available.")

        with tabs[3]:
            st.subheader("Learning Resources")
            learning_text = sections.get("learning", "").strip()
            if learning_text:
                render_learning_resources(learning_text)
            else:
                st.info("No learning resources provided.")

        with tabs[4]:
            st.subheader("Practice Websites")
            practice_websites_text = sections.get("practice_websites", "").strip()
            if practice_websites_text:
                st.markdown(practice_websites_text, unsafe_allow_html=True)
            else:
                st.info("No practice websites listed.")

        with tabs[5]:
            st.subheader("Job Search Platforms")
            if skills and location:
                job_links = get_job_platform_links(", ".join([f"{s} (level {l})" for s, l in skills.items()]), location)
                for platform, url in job_links.items():
                    st.markdown(f"- [{platform}]({url})", unsafe_allow_html=True)
            else:
                st.info("Enter skills and location to view job search platforms.")
    else:
        st.info("Fill profile on the left and click **Get Career Advice** to generate suggestions.")

# ------------------------------------------------
# App entry
# ------------------------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    login_page()
    st.stop()
else:
    main_app()
