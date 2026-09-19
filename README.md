# Prompt → App

Natural-language application builder: describe an app, then let the orchestrator plan, generate, run, test, and repair it.

## v0.5 — functional verification

The pipeline now verifies more than file existence:

- HTML document structure
- JavaScript entrypoint wiring
- non-empty JavaScript
- HTTP reachability
- optional headless browser smoke testing with Playwright
- automatic repair when static verification fails

### Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,browser]'
playwright install chromium

prompt-to-app "Build a simple habit tracker" --serve --browser
```

The generated app is served locally and opened by a headless Chromium smoke test.

Browser verification is optional so the core runtime does not require Chromium.

## Architecture

```
Prompt
  ↓
Planner → Ollama
  ↓
Generator → Ollama
  ↓
Static Verifier
  ↓
Repair Engine (bounded)
  ↓
Runner
  ↓
HTTP verification
  ↓
Optional Playwright browser verification
```

The model provides reasoning, planning, generation, and repair suggestions. The runtime owns filesystem writes, process execution, and verification.
