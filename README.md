# Prompt → App

Natural-language application builder: describe an app, then let the orchestrator plan, generate, run, test, and iteratively repair it.

## v0.3

The MVP now includes:

1. Natural-language prompt
2. Ollama-backed planning
3. Ollama-backed code generation
4. Deterministic fallback generation
5. Filesystem verification
6. Optional local app execution
7. HTTP reachability verification

### Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

prompt-to-app "Build a simple habit tracker" --serve
```

If verification passes, the generated app is served at:

```
http://127.0.0.1:8000
```

Use `--port` to select another port.

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
  ↓
Runner ────────→ local process
  ↓
HTTP probe
  ↓
Working app
```

The model provides reasoning and code generation. The runtime owns filesystem writes, process execution, and validation.
