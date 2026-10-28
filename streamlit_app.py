import streamlit as st
from pypdf import PdfReader
from io import BytesIO
import re
import ollama


# ---------- CAREERMATE AI: NEW WEBSITE STYLE ----------
import streamlit as st

st.markdown("""
<style>
/* Main application */
.stApp {
    background: #f4f7fc;
    color: #172033;
    font-family: 'Segoe UI', sans-serif;
}

/* Main content area */
.main .block-container {
    max-width: 1200px;
    padding: 2.5rem 2rem 7rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e3e8f2;
}

[data-testid="stSidebar"] * {
    color: #26334d !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #4f46e5 !important;
    font-weight: 700;
}

/* Headings */
h1, h2, h3 {
    color: #172554 !important;
    font-weight: 700 !important;
}

/* Paragraphs and regular text */
p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
    color: #334155;
}

/* Input boxes and text areas */
.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"],
.stNumberInput input {
    background: #ffffff !important;
    color: #172033 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #c7d2fe !important;
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea {
    color: #172033 !important;
    background: #ffffff !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.1rem;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #4338ca;
    color: white !important;
    border: none;
    box-shadow: 0 4px 14px #4f46e533;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #e5eaf3;
    border-radius: 15px;
    padding: 1rem;
    margin-bottom: 12px;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
}

/* Dashboard cards */
.cm-card {
    background: #ffffff;
    border: 1px solid #e5eaf3;
    border-radius: 16px;
    padding: 22px;
    margin: 8px 0;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
}

.cm-card h3 {
    color: #4f46e5 !important;
    margin-top: 0;
}

.cm-card p {
    color: #475569;
    line-height: 1.6;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Dividers */
hr {
    border-color: #e2e8f0;
}

/* Footer spacing */
footer {
    visibility: hidden;
}

/* Mobile-friendly layout */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1.2rem 1rem 5rem;
    }
}
</style>
""", unsafe_allow_html=True)
# ---------- END OF STYLE ----------


st.set_page_config(
    page_title="CareerMate AI",
    page_icon="🎯",
    layout="wide"
)

# ---------- Styling ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020, #152442);
    color: #f1f5f9;
}
[data-testid="stSidebar"] {
    background: #10182b;
}
.hero {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(120deg, #274690, #6741a5);
    margin-bottom: 20px;
}
.card {
    background: #182640;
    border: 1px solid #344969;
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Theme ----------
theme_palettes = {
    "Light": {
        "background": "#f4f7fc",
        "sidebar": "#ffffff",
        "surface": "#ffffff",
        "surface_alt": "#f8fafc",
        "text": "#172033",
        "muted": "#475569",
        "border": "#dbe3ee",
        "accent": "#c2410c",
        "accent_soft": "#ffedd5",
        "accent_text": "#9a3412",
    },
    "Dark": {
        "background": "#0b1220",
        "sidebar": "#101c2d",
        "surface": "#16243a",
        "surface_alt": "#1d2d44",
        "text": "#ecf2f8",
        "muted": "#b5c3d6",
        "border": "#34465d",
        "accent": "#d97706",
        "accent_soft": "#4c3314",
        "accent_text": "#f7bd4d",
    },
}
selected_theme = st.session_state.get("theme", "Light")
palette = theme_palettes[selected_theme]
st.markdown(
    "<style>"
    ":root {"
    f"--app-background: {palette['background']};"
    f"--sidebar-background: {palette['sidebar']};"
    f"--surface: {palette['surface']};"
    f"--surface-alt: {palette['surface_alt']};"
    f"--text: {palette['text']};"
    f"--muted: {palette['muted']};"
    f"--border: {palette['border']};"
    f"--accent: {palette['accent']};"
    f"--accent-soft: {palette['accent_soft']};"
    f"--accent-text: {palette['accent_text']};"
    "}"
    ".stApp {background: var(--app-background) !important; color: var(--text) !important;}"
    ".main, .main .block-container {background: transparent !important; color: var(--text) !important;}"
    '[data-testid="stSidebar"] {background: var(--sidebar-background) !important; border-right: 1px solid var(--border) !important;}'
    '[data-testid="stSidebar"] * {color: var(--text) !important;}'
    "h1, h2, h3, h4, p, label, li, .stMarkdown, [data-testid='stCaptionContainer'] {color: var(--text) !important;}"
    ".hero {background: linear-gradient(120deg, var(--accent-soft), var(--surface)) !important; color: var(--text) !important;}"
    ".card, .cm-card, [data-testid='stChatMessage'] {background: var(--surface) !important; border: 1px solid var(--border) !important; color: var(--text) !important;}"
    ".card h3, .cm-card h3 {color: var(--accent-text) !important;}"
    ".card p, .cm-card p {color: var(--muted) !important;}"
    "hr {border-color: var(--border) !important;}"
    "input, textarea, [role='combobox'], [data-testid='stChatInput'] {background: var(--surface-alt) !important; color: var(--text) !important; border-color: var(--border) !important;}"
    "input::placeholder, textarea::placeholder {color: var(--muted) !important;}"
    ".stButton > button {background: var(--accent) !important; color: #ffffff !important; border: 1px solid var(--accent) !important;}"
    ".stButton > button:hover {filter: brightness(0.92);}"
    "[role='radiogroup'][aria-label='Theme'] [role='radio'] {background: var(--surface-alt) !important; color: var(--text) !important; border-color: var(--border) !important;}"
    "[role='radiogroup'][aria-label='Theme'] [role='radio'][aria-checked='true'] {background: var(--accent) !important; color: #ffffff !important;}"
    "[data-testid='stAlert'] {background: var(--surface) !important; color: var(--text) !important;}"
    "[data-testid='stFileUploader'] {background: var(--surface-alt) !important; color: var(--text) !important;}"
    "</style>",
    unsafe_allow_html=True,
)

# ---------- Local AI chatbot using Ollama ----------

OLLAMA_MODEL = "llama3.2:3b"


def ask_ai(prompt, chat_history=None):
    """
    Generate answers using a local Ollama model.
    No Hugging Face token or external API key is required.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are CareerMate AI, a helpful assistant for college "
                "students. Answer the user's actual question, not just "
                "career questions. Help with programming, studies, "
                "careers, internships, resumes, projects, and interviews. "
                "Use simple English, clear explanations, and practical "
                "examples. If you don't know something, say so."
            ),
        }
    ]

    if chat_history:
        messages.extend(chat_history[-10:])

    messages.append({
        "role": "user",
        "content": prompt
    })

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages
        )

        return response["message"]["content"]

    except Exception as e:
        return (
            "I couldn't connect to the local AI model.\n\n"
            "Please make sure Ollama is running and the model is installed.\n\n"
            "Run this command in PowerShell:\n"
            "`ollama pull llama3.2:3b`\n\n"
            f"Error details: {e}"
        )

# ---------- Career knowledge base ----------
CAREERS = {
    "AI / ML Engineer": {
        "keywords": ["python", "machine learning", "ai", "deep learning",
                     "statistics", "tensorflow", "pytorch"],
        "skills": ["Python", "Statistics", "NumPy", "Pandas",
                   "Machine Learning", "Deep Learning", "Model Evaluation"],
        "project": "Build an image classification or prediction project."
    },
    "Data Analyst": {
        "keywords": ["sql", "excel", "data", "statistics", "python",
                     "power bi", "visualization"],
        "skills": ["Excel", "SQL", "Python", "Data Cleaning",
                   "Statistics", "Power BI or Tableau"],
        "project": "Analyze a dataset and create an interactive dashboard."
    },
    "Web Developer": {
        "keywords": ["html", "css", "javascript", "web", "flask",
                     "django", "react"],
        "skills": ["HTML", "CSS", "JavaScript", "Git",
                   "Responsive Design", "Backend Basics", "Databases"],
        "project": "Build and deploy a responsive personal portfolio."
    },
    "Cybersecurity Analyst": {
        "keywords": ["security", "network", "linux", "cybersecurity",
                     "ethical hacking", "python"],
        "skills": ["Networking", "Linux", "Security Fundamentals",
                   "Python", "Log Analysis", "Incident Response"],
        "project": "Create a basic log-analysis tool using sample logs."
    },
    "Cloud Engineer": {
        "keywords": ["cloud", "aws", "azure", "linux", "docker",
                     "network", "devops"],
        "skills": ["Linux", "Networking", "Cloud Fundamentals",
                   "Git", "Docker", "Deployment", "Security Basics"],
        "project": "Deploy a small web application to a cloud platform."
    },
    "Software Developer": {
        "keywords": ["python", "java", "c++", "programming",
                     "algorithms", "software", "git"],
        "skills": ["Programming", "Data Structures", "Algorithms",
                   "OOP", "Git", "Testing", "Problem Solving"],
        "project": "Build a task manager with persistent data storage."
    }
}

def recommend_careers(interests, current_skills):
    text = " ".join(interests + current_skills).lower()
    results = []

    for name, info in CAREERS.items():
        score = sum(
            1 for keyword in info["keywords"] if keyword in text
        )
        results.append((name, score, info))

    return sorted(results, key=lambda item: item[1], reverse=True)

def analyze_skill_gap(role, current_skills):
    required = CAREERS[role]["skills"]
    current = {skill.strip().lower() for skill in current_skills}
    missing = [
        skill for skill in required if skill.lower() not in current
    ]
    return required, missing

def build_roadmap(goal, weeks):
    topics = [
        "Learn the fundamentals",
        "Practice core concepts",
        "Complete guided exercises",
        "Build a small practical project",
        "Improve the project and test it",
        "Create a portfolio-ready project",
        "Review concepts and solve problems",
        "Document your work and prepare your portfolio"
    ]

    st.write(f"### Your {weeks}-week roadmap for {goal}")
    for week in range(weeks):
        topic = topics[week % len(topics)]
        st.markdown(
            f'<div class="card"><b>Week {week + 1}</b><br>{topic} '
            f'for {goal}</div>',
            unsafe_allow_html=True
        )

# ---------- Sidebar ----------
st.sidebar.title("🎯 CareerMate AI")
st.sidebar.caption("Your personal career companion")
st.sidebar.segmented_control("Theme", ["Light", "Dark"], default="Light", key="theme")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "AI Career Chat",
        "Career Recommendations",
        "Skill Gap Analysis",
        "Learning Roadmap",
        "Resume Analysis",
        "Interview Preparation",
        "Job Search"
    ]
)

st.sidebar.info("Works locally with Python logic. No API token required.")

# ---------- Dashboard ----------
if page == "Dashboard":
    st.markdown("""
    <div class="hero">
        <h1>Welcome to CareerMate AI 👋</h1>
        <p>Discover careers, improve skills and prepare for your future.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Career Paths", len(CAREERS))
    c2.metric("Career Tools", 6)
    c3.metric("API Tokens Needed", 0)

    st.subheader("Explore your career")
    st.write("Choose a feature from the sidebar to get started.")

    st.markdown("""
    <div class="card">💼 <b>Career Recommendations</b><br>
    Explore possible career paths based on your interests.</div>
    <div class="card">🧠 <b>Skill Gap Analysis</b><br>
    Compare your current skills with a target role.</div>
    <div class="card">🗺️ <b>Learning Roadmap</b><br>
    Create a structured study plan.</div>
    """, unsafe_allow_html=True)

# ---------- AI Career Chat ----------
elif page == "AI Career Chat":

    st.title("💬 AI Career Assistant")

    st.write(
        "Ask questions about careers, internships, programming, "
        "college, projects, or any other topic."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    # Display previous messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    prompt = st.chat_input("Ask anything...")

    if prompt:

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("CareerMate is thinking..."):

                answer = ask_ai(
                    prompt,
                    st.session_state.chat_history
                )

                st.markdown(answer)

        st.session_state.chat_history.extend([
            {
                "role": "user",
                "content": prompt
            },
            {
                "role": "assistant",
                "content": answer
            }
        ])
# ---------- Career recommendations ----------
elif page == "Career Recommendations":
    st.title("💼 Career Recommendations")
    interests = st.multiselect(
        "Select your interests",
        ["Artificial Intelligence", "Machine Learning", "Data",
         "Web Development", "Cybersecurity", "Cloud Computing",
         "Programming", "Software Development"]
    )
    skills = st.text_input(
        "Current skills, separated by commas",
        placeholder="Python, SQL, HTML"
    )

    if st.button("Recommend Careers", type="primary"):
        if not interests and not skills.strip():
            st.warning("Select interests or enter your skills.")
        else:
            skill_list = [x.strip() for x in skills.split(",") if x.strip()]
            results = recommend_careers(interests, skill_list)

            st.caption(
                "These are rule-based suggestions, not a validated "
                "prediction of career success."
            )
            for name, score, info in results[:4]:
                st.markdown(f"### {name}")
                st.write(f"Matching keywords: {score}")
                st.write(f"Suggested project: {info['project']}")
                st.divider()

# ---------- Skill gap ----------
elif page == "Skill Gap Analysis":
    st.title("🧠 Skill Gap Analysis")
    role = st.selectbox("Target role", list(CAREERS.keys()))
    current = st.text_area(
        "Enter skills you already know, separated by commas",
        placeholder="Python, SQL, Git"
    )

    if st.button("Analyze Skill Gaps", type="primary"):
        skills = [x.strip() for x in current.split(",") if x.strip()]
        required, missing = analyze_skill_gap(role, skills)

        st.subheader("Skills for your target role")
        st.write(", ".join(required))
        st.subheader("Skills to learn")
        if missing:
            for skill in missing:
                st.write(f"📌 {skill}")
        else:
            st.success("All listed skills match the checklist.")

        st.caption(
            "This is a simple checklist comparison. Similar skill names "
            "may need to be entered in the same wording."
        )

# ---------- Roadmap ----------
elif page == "Learning Roadmap":
    st.title("🗺️ Learning Roadmap")
    goal = st.text_input(
        "Your learning goal",
        placeholder="e.g. Python for Data Science"
    )
    weeks = st.slider("Duration in weeks", 2, 24, 8)

    if st.button("Create Roadmap", type="primary"):
        if goal.strip():
            build_roadmap(goal.strip(), weeks)
        else:
            st.warning("Enter a learning goal.")

# ---------- Resume analysis ----------
elif page == "Resume Analysis":
    st.title("📄 Resume Analysis")
    uploaded = st.file_uploader(
        "Upload your resume",
        type=["pdf", "txt"]
    )

    if uploaded:
        try:
            if uploaded.name.lower().endswith(".pdf"):
                reader = PdfReader(BytesIO(uploaded.getvalue()))
                resume = "\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
            else:
                resume = uploaded.getvalue().decode(
                    "utf-8", errors="replace"
                )

            if not resume.strip():
                st.warning(
                    "No readable text was found. The PDF may be scanned."
                )
            else:
                words = re.findall(r"\b[\w+#.]+\b", resume)
                lower = resume.lower()
                keywords = [
                    "python", "sql", "machine learning", "project",
                    "internship", "education", "experience", "skills",
                    "github", "communication"
                ]
                found = [k for k in keywords if k in lower]
                missing = [k for k in keywords if k not in lower]

                st.metric("Approximate word count", len(words))
                st.subheader("Detected resume keywords")
                st.write(", ".join(found) if found else "None detected")
                st.subheader("Potential areas to review")
                st.write(", ".join(missing) if missing else "Checklist covered")

                st.info(
                    "These are keyword checks, not a full AI review or "
                    "a guarantee of ATS performance."
                )
                with st.expander("View extracted resume text"):
                    st.text(resume[:15000])

        except Exception as exc:
            st.error(f"Unable to read the resume: {exc}")

# ---------- Interview preparation ----------
elif page == "Interview Preparation":
    st.title("🎤 Interview Preparation")
    role = st.selectbox("Choose a role", list(CAREERS.keys()))
    level = st.selectbox(
        "Difficulty", ["Beginner", "Intermediate", "Advanced"]
    )

    questions = {
        "AI / ML Engineer": [
            "What is machine learning?",
            "Explain supervised and unsupervised learning.",
            "What is overfitting?",
            "Why do we split data into training and testing sets?",
            "What is a confusion matrix?"
        ],
        "Data Analyst": [
            "What is data cleaning?",
            "Explain primary and foreign keys.",
            "What is the difference between WHERE and HAVING?",
            "What is a dashboard?",
            "How would you handle missing data?"
        ],
        "Web Developer": [
            "What is the purpose of HTML?",
            "Explain CSS selectors.",
            "What is the difference between frontend and backend?",
            "What is an HTTP request?",
            "Why is responsive design important?"
        ],
        "Cybersecurity Analyst": [
            "What is phishing?",
            "What is multi-factor authentication?",
            "What is a firewall?",
            "Why are software updates important?",
            "What is the principle of least privilege?"
        ],
        "Cloud Engineer": [
            "What is cloud computing?",
            "Explain virtual machines.",
            "What is the difference between scalability and elasticity?",
            "Why is identity and access management important?",
            "What is a container?"
        ],
        "Software Developer": [
            "What is object-oriented programming?",
            "What is the difference between a list and a tuple in Python?",
            "What is a data structure?",
            "Why do we use version control?",
            "How do you debug a program?"
        ]
    }

    if st.button("Generate Practice Questions", type="primary"):
        st.subheader(f"{role} — {level}")
        for i, question in enumerate(questions[role], start=1):
            with st.expander(f"Question {i}: {question}"):
                st.write(
                    "Try answering in your own words, then verify "
                    "your answer using reliable learning resources."
                )

# ---------- Job search ----------
elif page == "Job Search":
    st.title("🔎 Find Jobs & Internships")
    st.write("Search current listings on external job websites.")

    role = st.text_input("Job title", "AI Intern")
    location = st.text_input("Location", "Bengaluru")

    if st.button("Find Opportunities", type="primary"):
        from urllib.parse import quote_plus

        if role.strip():
            q = quote_plus(f"{role} {location}".strip())
            st.markdown(
                f"[Search LinkedIn Jobs](https://www.linkedin.com/jobs/search/?keywords={q})"
            )
            st.markdown(
                f"[Search Indeed India](https://in.indeed.com/jobs?q={quote_plus(role)}&l={quote_plus(location)})"
            )
            st.markdown(
                f"[Search Google Jobs](https://www.google.com/search?q={q}+jobs)"
            )
        else:
            st.warning("Enter a job title.")

st.sidebar.divider()
st.sidebar.caption("CareerMate AI • Local Edition")
