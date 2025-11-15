Agentic Research Assistant

This project implements a complete agentic research pipeline with a FastAPI backend and a Vite React frontend. The system uses LLMs (via OpenRouter or OpenAI) to generate research domains, produce research questions, generate toy datasets, run simple experiments, critique results, and build a small “paper” that can be exported in Markdown or PDF formats.

------------------------------------------------------------

Overview

The application performs the following steps:

1. Domain Scout Agent – Generates emerging research topics.
2. Question Generator Agent – Produces testable research questions.
3. Data Alchemist Agent – Creates toy datasets for experimentation.
4. Experiment Designer Agent – Runs a simple model and summarizes results.
5. Critic Agent – Critiques experiment findings.
6. Paper Output – The system generates a structured “mini paper.”

The frontend provides an interface to run the pipeline, view logs, and download results.
The backend exposes API endpoints to manage and execute the pipeline.

------------------------------------------------------------

Backend Setup (FastAPI)

Open PowerShell and run:

cd C:\Users\acer\Desktop\agentic-research-assistant
.\backend\.venv\Scripts\Activate.ps1

Set your API key:

$env:OPENROUTER_API_KEY="your_key_here"

Start the backend:

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

The server will run on:
http://localhost:8000

------------------------------------------------------------

Frontend Setup (Vite + React)

In a new terminal:

cd C:\Users\acer\Desktop\agentic-research-assistant\frontend
npm install
npm run dev

Frontend will run on:
http://localhost:5173

------------------------------------------------------------

API Keys

The application supports:

- OPENROUTER_API_KEY (recommended)
- OPENAI_API_KEY (optional, if using OpenAI)

Do not commit API keys to version control.

------------------------------------------------------------

API Endpoints

Start a new research run:

POST /run

Check status:

GET /status/{{run_id}}

Get result:

GET /result/{{run_id}}

Download paper:

GET /result/{{run_id}}/download?format=md
GET /result/{{run_id}}/download?format=pdf

------------------------------------------------------------

Important Files

Backend logic:

- backend/tools/llm_client.py
- backend/agents/domain_scout.py
- backend/agents/question_generator.py
- backend/agents/critic_agent.py
- backend/agents/orchestrator.py
- backend/main.py

Frontend logic:

- frontend/src/App.jsx
- frontend/src/components
- frontend/src/services/api.js

------------------------------------------------------------

Deployment Notes

Frontend is deployable on Vercel or Netlify using the build:

npm run build

Backend can be deployed on Render, Railway, or a Docker environment.
Environment variables must be configured in the hosting dashboard.

------------------------------------------------------------
