import streamlit as st

# -------------------- CSS Styling --------------------
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Login card with watermark */
    .login-card {
        background: rgba(255,255,255,0.95);
        max-width: 400px;
        margin: 100px auto;
        padding: 40px 30px;
        border-radius: 15px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
        text-align: center;
        position: relative;
        overflow: hidden;
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

    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 12px;
        font-size: 15px;
    }

    /* Button styling */
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

    /* Profile icon */
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

    /* Tabs styling */
    .stTabs [role="tab"] {
        font-weight: 600;
        font-size: 15px;
    }

    /* Dashboard watermark */
    .stApp::before {
        content: "🧑‍💻";
        font-size: 150px;
        color: rgba(74,144,226,0.05);
        position: absolute;
        top: 50px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 0;
        pointer-events: none;
    }

    /* Subtle tab panel styling */
    .stTabs [role="tabpanel"] {
        background: rgba(255,255,255,0.95);
        border-radius: 12px;
        padding: 20px;
        margin-top: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* Badge styling */
    .badge {
        display: inline-block;
        background-color: #4a90e2;
        color: white;
        padding: 4px 10px;
        margin: 2px 2px 2px 0;
        border-radius: 12px;
        font-size: 14px;
    }

    .checklist-badge {
        display: inline-block;
        background-color: #50e3c2;
        color: white;
        padding: 4px 10px;
        margin: 2px 2px 2px 0;
        border-radius: 12px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- Session State --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "practice_states" not in st.session_state:
    st.session_state.practice_states = {}

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# -------------------- Helper Functions --------------------
def render_badges(items, badge_class="badge"):
    """Render list of items as colored badges"""
    badges_html = "".join([f"<span class='{badge_class}'>{item.strip()}</span>" for item in items])
    st.markdown(badges_html, unsafe_allow_html=True)

def checklist_with_persistence(items):
    """Render checklist items with checkboxes and persist state"""
    for i, item in enumerate(items):
        key = f"checklist_{i}"
        checked = st.session_state.practice_states.get(key, False)
        st.session_state.practice_states[key] = st.checkbox(item, value=checked)

# Example: parse checklist items
def get_checklist_items(text):
    return [line.strip("- ").strip() for line in text.split("\n") if line.strip()]

# -------------------- Login Page --------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2>Login to Career Advisor</h2>", unsafe_allow_html=True)

    username = st.text_input("Username")
    email = st.text_input("Email")

    if st.button("Login"):
        if username and email:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.warning("Please fill in all fields")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Main App --------------------
else:
    # Profile icon
    st.markdown(
        f'<div class="profile-icon">{st.session_state.username[0].upper()}</div>',
        unsafe_allow_html=True,
    )

    st.title(f"Welcome {st.session_state.username} 👋")
    st.write("Fill in your details to get personalized career advice.")

    # -------------------- Input Form --------------------
    if not st.session_state.form_submitted:
        with st.form("user_input_form"):
            skills_input = st.text_input("Enter your skills (comma separated)")
            target_role = st.text_input("Enter your target career role")
            location = st.text_input("Enter your preferred job location")

            submitted = st.form_submit_button("Get Career Advice")

            if submitted:
                if skills_input.strip() and target_role.strip() and location.strip():
                    st.session_state.skills_input = skills_input
                    st.session_state.target_role = target_role
                    st.session_state.location = location
                    st.session_state.form_submitted = True
                    st.experimental_rerun()
                else:
                    st.warning("Please fill in all fields to continue.")

    # -------------------- Render Tabs Only After Form Submission --------------------
    if st.session_state.form_submitted:

        # -------------------- Tabs --------------------
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

        # ---------------- Career Suggestions ----------------
        with tabs[0]:
            st.header("Career Suggestions")
            skills_list = st.session_state.skills_input.split(",") if st.session_state.skills_input else []
            st.info("Based on your skills, here are some career suggestions:")
            render_badges(["Data Scientist", "Software Engineer", "AI/ML Engineer"])

        # ---------------- Roadmap ----------------
        with tabs[1]:
            st.header("Career Roadmap")
            st.info("Roadmap will be generated here for your target role.")

        # ---------------- Skill Gap Analysis ----------------
        with tabs[2]:
            st.header("Skill Gap Analysis & Practice Plan")
            st.info("Based on your target role, here are missing skills:")
            missing_skills = ["Python", "SQL", "Cloud Computing"]
            render_badges(missing_skills, badge_class="badge")

            # Example practice checklist
            checklist_items = ["Complete Python project", "Solve 50 SQL problems", "Deploy a cloud app"]
            st.write("Practice Plan Checklist:")
            checklist_with_persistence(checklist_items)

        # ---------------- Learning Resources ----------------
        with tabs[3]:
            st.header("Learning Resources")
            learning_resources = [
                "📘 Coursera – Machine Learning",
                "📘 Udemy – Data Science Bootcamp",
                "📘 Kaggle – Hands-on Projects"
            ]
            render_badges(learning_resources, badge_class="badge")

        # ---------------- Practice Websites ----------------
        with tabs[4]:
            st.header("Practice Websites")
            practice_websites = [
                "https://leetcode.com",
                "https://hackerrank.com",
                "https://kaggle.com"
            ]
            render_badges(practice_websites, badge_class="badge")

        # ---------------- Job Search Platforms ----------------
        with tabs[5]:
            st.header("Job Search Platforms")
            job_platforms = ["LinkedIn", "Indeed", "Naukri"]
            render_badges(job_platforms, badge_class="badge")
