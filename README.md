# Prompt → App

Natural-language application builder: describe an app, then let the orchestrator plan, generate, run, test, and iteratively repair it.

## v0.1

The MVP now has an Ollama-backed planning and generation path with a deterministic fallback:

1. Accept a natural-language app request.
2. Ask a local Ollama model for a structured build plan.
3. Ask the model to generate the app files.
4. Write the generated files into an isolated output directory.
5. Verify the minimum project structure.
6. Fall back to a known-good browser app if Ollama is unavailable or returns invalid JSON.

Default local model: `qwen2.5-coder:7b`

Default Ollama endpoint: `http://127.0.0.1:11434`

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
prompt-to-app "Build a simple habit tracker"
```

Then serve the generated app:

```bash
cd generated-app
python -m http.server 8000
```

Open `http://127.0.0.1:8000`.

## Architecture

```
Prompt
  ↓
Planner ──────→ Ollama
  ↓
AppPlan
  ↓
Generator ────→ Ollama
  ↓
Generated files
  ↓
Verifier
```

The model provides reasoning and code generation. The runtime owns filesystem writes and validation.
