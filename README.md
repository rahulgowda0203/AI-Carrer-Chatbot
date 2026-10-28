# CareerMate AI — Career Assistant Chatbot

A beginner-friendly Flask web app with a dashboard UI, Hugging Face chat integration, career recommendations, skill-gap suggestions, learning roadmaps, resume review, interview practice, and external job-search links.

## Requirements
- Python 3.10 or newer (Python 3.12 recommended)
- VS Code
- Internet connection for Hugging Face inference and Google Fonts

## Windows PowerShell setup

```powershell
mkdir CareerMateAI
cd CareerMateAI
# Extract this project ZIP into this folder if you downloaded it elsewhere.
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` in VS Code and set:
```env
HF_TOKEN=your_hugging_face_token_here
HF_MODEL=openai/gpt-oss-120b:fastest
FLASK_SECRET_KEY=replace-with-a-long-random-secret
```

Get a Hugging Face token from https://huggingface.co/settings/tokens. Create a fine-grained token with permission to make calls to Inference Providers. Keep it private and do not commit `.env` to GitHub. Model/provider availability and usage limits depend on your Hugging Face account.

## Run the app

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser. Stop the server with Ctrl+C.

## Features
- AI chat with a demo fallback if no token is configured or the API fails.
- Heuristic career matching and missing-skill suggestions.
- AI-generated learning roadmap and interview practice questions.
- Text-based PDF/TXT resume review. Scanned PDFs may not contain extractable text.
- External job portal searches. The app does not scrape, verify, or guarantee job vacancies.
- SQLite chat history scoped to the current browser session.

## Notes
- The career matcher is a simple keyword heuristic, not a scientifically validated assessment.
- Do not upload resumes containing sensitive details unless you are comfortable sharing their text with the configured AI provider.
- For production, set a strong secret key, disable Flask debug mode, add authentication and rate limits, and review privacy/security requirements.
