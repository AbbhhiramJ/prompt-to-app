# Prompt → App

Natural-language application builder: describe an app, then let the orchestrator plan, generate, verify, repair, and optionally deploy it.

## v0.8 — cloud deployment

The project now includes a small Vercel deployment adapter for generated web apps. Cloud deployment sends the generated files directly to Vercel and returns the resulting URL.

    Prompt
      ↓
    Planner
      ↓
    Generator
      ↓
    Static verification
      ↓
    Vercel deployment
      ↓
    Live URL

### Cloud deployment

Set a Vercel API token in the environment:

    export VERCEL_TOKEN=...
    prompt-to-app "Build a simple habit tracker" --cloud

The cloud deployment path targets web apps such as HTML/CSS/JavaScript, React, and other Vercel-compatible projects.

### Local development

    python -m venv .venv
    source .venv/bin/activate
    pip install -e '.[dev,browser]'
    playwright install chromium

    prompt-to-app "Build a simple habit tracker" --serve --browser

## Pipeline

    Prompt
      ↓
    Planner → AppPlan + tests
      ↓
    Generator → files
      ↓
    Static verification
      ↓
    Local HTTP/browser verification OR Vercel deployment

The local Ollama path remains useful for development and testing. It is not the intended end-user runtime.

## Scope

The cloud milestone intentionally targets web applications first. Arbitrary Python, Java, C++, and other server workloads require a separate sandbox/runtime layer.
