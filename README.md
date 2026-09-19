# Prompt → App

Natural-language application builder: describe an app, then let the orchestrator plan, generate, run, test, and repair it.

## v0.6 — generated interaction tests

The planner now creates a small, constrained browser test plan alongside the app plan. The test runner supports:

- page load
- text visibility
- clicking a safe selector
- text visibility after an interaction

Browser failures are returned to the same bounded verification/repair pipeline.

### Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,browser]'
playwright install chromium

prompt-to-app "Build a simple habit tracker" --serve --browser
```

Browser verification remains optional for the core package.

## Architecture

```
Prompt
  ↓
Planner → AppPlan + constrained tests
  ↓
Generator → App
  ↓
Static Verifier
  ↓
Bounded Repair
  ↓
Runner
  ↓
HTTP verification
  ↓
Playwright interaction tests
  ↓
Failure feedback → Repair
```

The runtime controls filesystem writes and browser actions. Generated tests are deliberately limited to a small safe action vocabulary.
