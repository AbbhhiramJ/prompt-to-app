from .models import AppPlan

def plan(prompt: str) -> AppPlan:
    """Return a deterministic placeholder plan for v0.1.

    The LLM-backed planner will replace this implementation after the runtime
    contract is established.
    """
    text = prompt.strip()
    if not text:
        raise ValueError("Prompt cannot be empty")
    return AppPlan(
        name="generated-app",
        description=text,
        stack=["python"],
        files=["README.md"],
        run_command="python -m http.server 8000",
    )
