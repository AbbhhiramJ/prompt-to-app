from pathlib import Path
from .generator import generate
from .models import AppPlan
from .planner import plan
from .verifier import verify

def build(
    prompt: str,
    output_dir: str | Path = "./generated-app",
    model: str = "qwen2.5-coder:7b",
    base_url: str = "http://127.0.0.1:11434",
) -> tuple[AppPlan, Path, list[str]]:
    app_plan = plan(prompt, model=model, base_url=base_url)
    project_dir = generate(app_plan, output_dir, model=model, base_url=base_url)
    errors = verify(project_dir)
    return app_plan, project_dir, errors
