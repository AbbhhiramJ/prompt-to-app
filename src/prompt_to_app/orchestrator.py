from pathlib import Path
from .generator import generate
from .models import AppPlan
from .planner import plan
from .runner import start, wait_for_http
from .verifier import verify

def build(
    prompt: str,
    output_dir: str | Path = "./generated-app",
    model: str = "qwen2.5-coder:7b",
    base_url: str = "http://127.0.0.1:11434",
    serve: bool = False,
    port: int = 8000,
) -> tuple[AppPlan, Path, list[str], str | None]:
    app_plan = plan(prompt, model=model, base_url=base_url)
    project_dir = generate(app_plan, output_dir, model=model, base_url=base_url)
    errors = verify(project_dir)
    url = None
    if not errors and serve:
        process = start(f"python -m http.server {port}", project_dir)
        url = f"http://127.0.0.1:{port}"
        ok, status = wait_for_http(url)
        if not ok:
            errors.append(f"generated app did not become reachable at {url}")
            process.terminate()
        elif status != 200:
            errors.append(f"generated app returned HTTP {status}")
            process.terminate()
    return app_plan, project_dir, errors, url
