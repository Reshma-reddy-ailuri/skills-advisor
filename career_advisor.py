import streamlit as st

# -------------------- CSS Styling --------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Login card */
.login-card {
    background: rgba(255,255,255,0.95);
    max-width: 450px;
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
.stTextInput>div>div>input, .stNumberInput>div>div>input {
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

.badge.completed {
    background-color: #50e3c2 !important;
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

.link-badge {
    display: inline-block;
    background-color: #f0f0f0;
    color: #333;
    padding: 4px 10px;
    margin: 2px 2px 2px 0;
    border-radius: 12px;
    font-size: 14px;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# -------------------- Session State --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "practice_states" not in st.session_state:
    st.session_state.practice_states = {}
if "roadmap_states" not in st.session_state:
    st.session_state.roadmap_states = {}

# -------------------- Helper Functions --------------------
def render_badges(items, badge_class="badge"):
    badges_html = ""
    for i, item in enumerate(items):
        completed = st.session_state.roadmap_states.get(item, False)
        cls = badge_class + (" completed" if completed else "")
        badges_html += f"<span class='{cls}'>{item}</span>"
    st.markdown(badges_html, unsafe_allow_html=True)

def roadmap_with_checkboxes(items):
    """Roadmap badges with checkboxes for completion"""
    for item in items:
        checked = st.checkbox(item, value=st.session_state.roadmap_states.get(item, False))
        st.session_state.roadmap_states[item] = checked

def checklist_with_persistence(items):
    for i, item in enumerate(items):
        key = f"checklist_{i}"
        checked = st.session_state.practice_states.get(key, False)
        st.session_state.practice_states[key] = st.checkbox(item, value=checked)

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
            st.rerun()
        else:
            st.warning("Please fill in all fields")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Main App --------------------
else:
    st.markdown(
        f'<div class="profile-icon">{st.session_state.username[0].upper()}</div>',
        unsafe_allow_html=True,
    )
    st.title(f"Welcome {st.session_state.username} 👋")
    st.write("Fill in your details to get personalized career advice.")

    # -------------------- Input Form --------------------
    if not st.session_state.form_submitted:
        with st.form("user_input_form"):
            age = st.number_input("Age", min_value=12, max_value=100, step=1)
            skills_input = st.text_input("Skills (comma separated)")
            target_role = st.text_input("Target Role / Career Goal")
            education = st.text_input("Education Background")
            location = st.text_input("Preferred Job Location")
            submitted = st.form_submit_button("Get Career Advice")

            if submitted:
                if all([skills_input.strip(), target_role.strip(), education.strip(), location.strip()]):
                    st.session_state.age = age
                    st.session_state.skills_input = skills_input
                    st.session_state.target_role = target_role
                    st.session_state.education = education
                    st.session_state.location = location
                    st.session_state.form_submitted = True
                    st.rerun()
                else:
                    st.warning("Please fill all fields.")

    # -------------------- Tabs --------------------
    if st.session_state.form_submitted:
        st.header("AI-Powered Career Advisor Results")
        tabs = st.tabs([
            "Career Suggestions",
            "Roadmap",
            "Skill Gap Analysis",
            "Learning Resources",
            "Practice Websites",
            "Job Search Platforms",
        ])

        # Career Suggestions
        with tabs[0]:
            st.header("Career Suggestions")
            skills_list = st.session_state.skills_input.split(",")
            st.info(f"Based on your skills ({st.session_state.skills_input}):")
            render_badges(["Data Scientist", "Software Engineer", "AI/ML Engineer"])

        # Roadmap
        with tabs[1]:
            st.header("Career Roadmap")
            st.info(f"Steps to become a {st.session_state.target_role}:")
            roadmap_steps = ["Learn Python", "Master SQL", "Work on Projects", "Understand Cloud Computing", "Build Portfolio"]
            roadmap_with_checkboxes(roadmap_steps)
            render_badges(roadmap_steps)

        # Skill Gap Analysis
        with tabs[2]:
            st.header("Skill Gap Analysis & Practice Plan")
            st.info(f"Missing skills for {st.session_state.target_role}:")
            render_badges(["Python", "SQL", "Cloud Computing"])
            checklist_items = ["Complete Python project", "Solve 50 SQL problems", "Deploy a cloud app"]
            st.write("Practice Plan Checklist:")
            checklist_with_persistence(checklist_items)

        # Learning Resources
        with tabs[3]:
            st.header("Learning Resources")
            render_badges([
                "📘 Coursera – Machine Learning",
                "📘 Udemy – Data Science Bootcamp",
                "📘 Kaggle – Hands-on Projects"
            ])

        # Practice Websites
        with tabs[4]:
            st.header("Practice Websites")
            render_badges([
                "https://leetcode.com",
                "https://hackerrank.com",
                "https://kaggle.com"
            ], badge_class="link-badge")

        # Job Search Platforms
        with tabs[5]:
            st.header("Job Search Platforms")
            render_badges(["LinkedIn", "Indeed", "Naukri"], badge_class="link-badge")
