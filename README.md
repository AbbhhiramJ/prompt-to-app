# Prompt → App

Natural-language application builder: describe an app, then let the orchestrator plan, generate, run, test, and repair it.

## v0.4 — bounded automatic repair

The pipeline now supports up to a configurable number of repair attempts:

```
Prompt
  ↓
Planner → Ollama
  ↓
AppPlan
  ↓
Generator → Ollama
  ↓
Files
  ↓
Verifier
  ↓
Errors? ── no ──→ Runner → HTTP check → Working app
  │
 yes
  ↓
Repair Engine → Ollama
  │
  └──────────────→ Verifier
```

Default repair limit: **2 attempts**.

Run:

```bash
prompt-to-app "Build a simple habit tracker" --serve --max-repairs 2
```

Safety boundaries:
- repair paths must be relative
- `..` path traversal is rejected
- repair attempts are bounded
- filesystem writes stay inside the requested output directory

The model provides reasoning, planning, code generation, and repair suggestions. The runtime owns filesystem writes, process execution, and validation.

## CI

GitHub Actions runs the Python test suite on pushes and pull requests to `main`.
