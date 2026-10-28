import os
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pypdf import PdfReader

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "instance" / "careermate.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
DB_PATH.parent.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-development-secret")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "txt"}
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
HF_MODEL = os.getenv("HF_MODEL", "openai/gpt-oss-120b:fastest")


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


CAREERS = {
    "AI / Machine Learning Engineer": {
        "keywords": ["python", "machine learning", "ai", "artificial intelligence", "deep learning", "math", "tensorflow", "pytorch"],
        "skills": ["Python", "Statistics", "Machine Learning", "Deep Learning", "Git", "Model evaluation"],
        "projects": ["Build a spam classifier", "Create an image classification app", "Deploy a small ML API"]
    },
    "Data Analyst / Data Scientist": {
        "keywords": ["data", "analytics", "statistics", "sql", "excel", "visualization", "python", "power bi"],
        "skills": ["SQL", "Python", "Statistics", "Data cleaning", "Data visualization", "Portfolio projects"],
        "projects": ["Analyze a public dataset", "Build a dashboard", "Write a data insights report"]
    },
    "Web Developer": {
        "keywords": ["web", "html", "css", "javascript", "frontend", "backend", "flask", "react"],
        "skills": ["HTML", "CSS", "JavaScript", "Git", "APIs", "Responsive design"],
        "projects": ["Build a responsive portfolio", "Create a CRUD web app", "Deploy a website"]
    },
    "Cybersecurity Analyst": {
        "keywords": ["security", "cyber", "network", "linux", "ethical hacking", "privacy"],
        "skills": ["Networking", "Linux", "Security fundamentals", "Python basics", "Log analysis", "Incident reporting"],
        "projects": ["Set up a home lab", "Analyze sample security logs", "Document a threat model"]
    },
    "Software Engineer": {
        "keywords": ["programming", "software", "java", "c++", "python", "algorithms", "coding"],
        "skills": ["One programming language", "Data structures", "Algorithms", "Git", "Testing", "SQL"],
        "projects": ["Build a task manager", "Create a REST API", "Solve coding practice problems"]
    }
}

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS saved_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")

init_db()

def get_session_id():
    if "chat_id" not in session:
        import secrets
        session["chat_id"] = secrets.token_hex(16)
    return session["chat_id"]

def save_message(role, content):
    with db() as conn:
        conn.execute(
            "INSERT INTO messages(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (get_session_id(), role, content, datetime.now().isoformat(timespec="seconds"))
        )

def get_history(limit=12):
    with db() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
            (get_session_id(), limit)
        ).fetchall()
    return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

def demo_reply(message):
    text = message.lower()
    if any(w in text for w in ["career", "which job", "which role", "career path"]):
        return ("Start by comparing your interests, current skills, and preferred work style. "
                "For example, Python plus statistics may suit data roles; HTML, CSS, and JavaScript may suit web development. "
                "Use the Career Recommendations section to compare options, then build one small portfolio project.")
    if any(w in text for w in ["interview", "interview question"]):
        return ("Try these practice questions: 1) Tell me about yourself. 2) Explain a project you built. "
                "3) Describe a difficult bug and how you solved it. 4) What would you improve in your project? "
                "Answer with the situation, your actions, and the result. This is demo guidance, not a model-generated response.")
    if any(w in text for w in ["resume", "cv"]):
        return ("For a stronger resume, use clear project titles, explain what you personally built, list relevant tools, "
                "and include measurable results only when you can support them. Upload a PDF or TXT in Resume Analysis for a basic review.")
    if any(w in text for w in ["roadmap", "learn", "learning plan"]):
        return ("A simple roadmap: 1) learn the fundamentals, 2) practise with small exercises, "
                "3) build two projects, 4) publish your work, and 5) practise explaining your decisions. "
                "Choose the roadmap tool for a role-specific plan.")
    return ("I'm in demo mode, so I can only answer a few common career questions. "
            "To get answers to other questions, configure HF_TOKEN in your .env file as described in the README "
            "and restart the app. If you already configured it, the AI service may be unavailable right now.")

def ask_ai(message):
    if not HF_TOKEN:
        return demo_reply(message), "demo"
    try:
        client = InferenceClient(api_key=HF_TOKEN, provider="auto")
        history = get_history(limit=10)
        messages = [{
            "role": "system",
            "content": (
                "You are CareerMate AI, a practical career assistant for students and early-career job seekers. "
                "Be supportive, clear, and honest. Give actionable steps, realistic learning plans, and beginner-friendly explanations. "
                "Do not guarantee jobs, salaries, or hiring outcomes. Do not invent current vacancies. "
                "For job searches, point users to trusted job portals and tell them to verify listings. "
                "For resume feedback, do not ask for sensitive personal information. Use concise headings and bullet points."
            )
        }]
        messages.extend(history)
        messages.append({"role": "user", "content": message[:5000]})
        completion = client.chat.completions.create(
            model=HF_MODEL,
            messages=messages,
            max_tokens=700,
            temperature=0.5
        )
        answer = completion.choices[0].message.content
        return (answer or demo_reply(message)), "huggingface"
    except Exception as exc:
        app.logger.warning("Hugging Face request failed: %s", exc)
        return demo_reply(message) + "\n\nAI service note: the Hugging Face request did not complete. Check your token, model access, provider availability, and account limits.", "demo"

@app.route("/")
def index():
    history = get_history(limit=30)
    return render_template("index.html", history=history, ai_ready=bool(HF_TOKEN), model=HF_MODEL)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"error": "Please type a message first."}), 400
    if len(message) > 5000:
        return jsonify({"error": "Please keep messages under 5,000 characters."}), 400
    save_message("user", message)
    answer, source = ask_ai(message)
    save_message("assistant", answer)
    return jsonify({"reply": answer, "source": source})

@app.route("/api/careers", methods=["POST"])
def careers():
    data = request.get_json(silent=True) or {}
    interests = str(data.get("interests", ""))[:1000].lower()
    skills_text = str(data.get("skills", ""))[:1000]
    current_skills = {s.strip().lower() for s in skills_text.split(",") if s.strip()}
    results = []
    for name, info in CAREERS.items():
        score = sum(1 for word in info["keywords"] if word in interests or word in skills_text.lower())
        missing = [skill for skill in info["skills"] if skill.lower() not in current_skills]
        results.append({
            "name": name, "score": score, "skills": info["skills"],
            "missing": missing[:5], "projects": info["projects"]
        })
    results.sort(key=lambda item: item["score"], reverse=True)
    return jsonify({"results": results[:3]})

@app.route("/api/roadmap", methods=["POST"])
def roadmap():
    data = request.get_json(silent=True) or {}
    role = str(data.get("role", "Software Engineer"))[:100]
    level = str(data.get("level", "Beginner"))[:40]
    prompt = (
        f"Create a realistic 8-week learning roadmap for a student targeting {role}. "
        f"Current level: {level}. Give weekly goals, practice tasks, and one portfolio project. "
        "Avoid promising job placement. Make it concise and beginner-friendly."
    )
    answer, source = ask_ai(prompt)
    return jsonify({"roadmap": answer, "source": source})

@app.route("/api/interview", methods=["POST"])
def interview():
    data = request.get_json(silent=True) or {}
    role = str(data.get("role", "Software Engineer"))[:100]
    level = str(data.get("level", "Entry level"))[:40]
    prompt = (
        f"Create 8 interview practice questions for an entry-level candidate targeting {role} at {level} level. "
        "Include what a good answer should cover, but do not write fake personal experience for the candidate."
    )
    answer, source = ask_ai(prompt)
    return jsonify({"questions": answer, "source": source})

@app.route("/api/resume", methods=["POST"])
def resume():
    file = request.files.get("resume")
    target_role = str(request.form.get("role", "Entry-level role"))[:100]
    if not file or not file.filename:
        return jsonify({"error": "Choose a PDF or TXT resume."}), 400
    filename = secure_filename(file.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Only PDF and TXT files are supported."}), 400
    try:
        if extension == "pdf":
            import io
            reader = PdfReader(io.BytesIO(file.read()))
            text = "\n".join(page.extract_text() or "" for page in reader.pages[:8])
        else:
            text = file.read().decode("utf-8", errors="ignore")
        text = text[:12000].strip()
        if not text:
            return jsonify({"error": "No readable text found. If this is a scanned PDF, convert it to a text-based PDF first."}), 400
        prompt = (
            f"Review this resume for the target role: {target_role}. Give strengths, missing or unclear details, "
            "ATS readability suggestions, and 5 specific improvements. Do not infer facts not in the resume. "
            "Remind the user to remove phone, address, and other private details before sharing.\n\nRESUME TEXT:\n" + text
        )
        answer, source = ask_ai(prompt)
        if source == "demo":
            answer = (
                "Basic resume review (AI is not connected):\n"
                f"- Target role: {target_role}\n"
                "- Use a clear summary focused on the target role.\n"
                "- Put relevant skills and projects near the top.\n"
                "- Describe your individual contribution and tools used in each project.\n"
                "- Fix spelling, formatting, and inconsistent dates.\n"
                "- Add measurable outcomes only when you can verify them.\n"
                "- Tailor keywords to each genuine job description.\n\n"
                "Configure Hugging Face to get resume-specific feedback."
            )
        return jsonify({"review": answer, "source": source})
    except Exception:
        app.logger.exception("Resume parsing failed")
        return jsonify({"error": "Could not read this file. Try a text-based PDF or TXT file."}), 400

@app.route("/api/jobs")
def jobs():
    role = request.args.get("role", "software developer").strip()[:100]
    from urllib.parse import quote_plus
    q = quote_plus(role)
    return jsonify({"role": role, "links": [
        {"name": "LinkedIn Jobs", "url": f"https://www.linkedin.com/jobs/search/?keywords={q}"},
        {"name": "Indeed India", "url": f"https://in.indeed.com/jobs?q={q}"},
        {"name": "Naukri", "url": f"https://www.naukri.com/{q.replace('+', '-')}-jobs"},
        {"name": "Internshala", "url": f"https://internshala.com/internships/keywords-{q.replace('+', '%20')}/"}
    ]})

@app.route("/api/history", methods=["DELETE"])
def clear_history():
    with db() as conn:
        conn.execute("DELETE FROM messages WHERE session_id=?", (get_session_id(),))
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
