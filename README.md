# Prompt → App

Natural-language application builder: describe an app, then let the orchestrator plan, generate, run, test, and iteratively repair it.

## v0.1 goal

Prompt → App v0.1 focuses on a small, reliable loop:

1. Accept a natural-language app request.
2. Produce a structured build plan.
3. Generate a project from that plan.
4. Run the generated project locally.
5. Run basic checks.
6. Report the project path and run status.

## Architecture

```
Prompt
  ↓
Orchestrator
  ├─ Planner
  ├─ Generator
  ├─ Runner
  └─ Verifier
  ↓
Generated App
```

The orchestrator is deliberately provider-agnostic. Local Ollama models can be used for planning/code generation, while execution remains under the local runtime.

## Planned structure

- `src/prompt_to_app/` — core Python package
- `src/prompt_to_app/planner.py` — prompt → structured plan
- `src/prompt_to_app/generator.py` — plan → files
- `src/prompt_to_app/runner.py` — process execution
- `src/prompt_to_app/verifier.py` — basic validation
- `src/prompt_to_app/orchestrator.py` — end-to-end loop
- `tests/` — unit/integration tests
- `examples/` — sample prompts

## Design rule

The model reasons about what should be built. The runtime owns filesystem changes, process execution, validation, and safety boundaries.
