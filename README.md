# Prompt → App

Natural-language application builder: describe an app, then let the orchestrator plan, generate, run, test, and repair it.

## v0.7 — test-aware repair

The repair engine now receives structured browser failures such as:

```
TEST 2 click FAILED: selector=#add
TEST 3 text_visible_after_click FAILED: text='Habit added'
```

This keeps repairs targeted instead of giving the model vague browser errors.

The system still uses a small bounded repair loop; it does not attempt unrestricted autonomous debugging.

### Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,browser]'
playwright install chromium

prompt-to-app "Build a simple habit tracker" --serve --browser
```

## Pipeline

```
Prompt
 ↓
Planner → AppPlan + tests
 ↓
Generator → App
 ↓
Static verification
 ↓
Run + HTTP check
 ↓
Playwright interaction tests
 ↓
Structured failure
 ↓
Targeted repair
 ↓
Retest (bounded)
```
