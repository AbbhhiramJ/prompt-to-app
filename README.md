# Prompt → App

Describe a web app in natural language and receive a deployed URL.

## Product flow

Prompt → cloud LLM → plan → generate → verify/repair → Vercel URL

The browser interface is served from the repository root. The /api/build endpoint performs the build.

## Production environment

Set these secrets in the deployment environment:

- LLM_API_KEY
- LLM_MODEL (default: gpt-4.1-mini)
- LLM_BASE_URL (default: https://api.openai.com/v1)
- VERCEL_TOKEN

The LLM adapter is OpenAI-compatible, so the service can use any compatible provider by changing LLM_BASE_URL and LLM_MODEL.

## Local development

python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,browser]'
playwright install chromium
prompt-to-app "Build a simple habit tracker" --serve --browser

Local Ollama remains supported for development.

## API

GET /api/health

POST /api/build

Request: {"prompt":"Build a simple habit tracker"}

Response: {"name":"habit-tracker","status":"ready","url":"https://...","repairs":0}

## Scope

The first production target is browser-based web apps. Arbitrary long-running Python, Java, or C++ backends require a separate sandbox/runtime layer.
