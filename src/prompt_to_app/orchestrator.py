from pathlib import Path
from .generator import generate
from .planner import plan
from .verifier import verify

def build(prompt: str, output_dir: str | Path = "./generated-app"):
    app_plan = plan(prompt)
    project_dir = generate(app_plan, output_dir)
    errors = verify(project_dir)
    return app_plan, project_dir, errors
