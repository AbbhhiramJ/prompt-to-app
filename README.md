# Prompt → App

Natural-language application builder: describe an app, then let the orchestrator plan, generate, verify, repair, and deploy it.

## v0.8.1 — cloud LLM

The production path can use Gemini 2.5 Flash through GEMINI_API_KEY. Local Ollama remains available for development.

Set GEMINI_API_KEY and VERCEL_TOKEN in the deployment environment, then run:

    prompt-to-app "Build a simple habit tracker" --cloud

The cloud path is:

    Prompt → Gemini → Plan → Generate → Verify/Repair → Vercel → URL

No API keys are stored in the repository.

## Local development

    python -m venv .venv
    source .venv/bin/activate
    pip install -e '.[dev,browser]'
    playwright install chromium
    prompt-to-app "Build a simple habit tracker" --serve --browser

The current cloud milestone targets web applications first. Arbitrary Python, Java, C++, or long-running server workloads require a separate sandbox/runtime layer.
