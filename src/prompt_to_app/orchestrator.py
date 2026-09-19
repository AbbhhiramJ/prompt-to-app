from pathlib import Path
from .browser import BrowserCheckUnavailable, check as browser_check
from .generator import generate
from .models import AppPlan
from .planner import plan
from .repair import repair
from .runner import start, wait_for_http
from .verifier import verify

def _read_files(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }

def _apply_updates(root: Path, updates: dict[str, str]) -> None:
    for relative_path, content in updates.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

def build(
    prompt: str,
    output_dir: str | Path = "./generated-app",
    model: str = "qwen2.5-coder:7b",
    base_url: str = "http://127.0.0.1:11434",
    serve: bool = False,
    port: int = 8000,
    max_repairs: int = 2,
    browser: bool = False,
) -> tuple[AppPlan, Path, list[str], str | None, int]:
    if max_repairs < 0:
        raise ValueError("max_repairs must be >= 0")

    app_plan = plan(prompt, model=model, base_url=base_url)
    project_dir = generate(app_plan, output_dir, model=model, base_url=base_url)
    url = None
    repairs = 0
    errors = verify(project_dir)

    while True:
        if not errors and serve:
            process = start(f"python -m http.server {port}", project_dir)
            url = f"http://127.0.0.1:{port}"
            ok, status = wait_for_http(url)
            if not ok:
                errors = [f"generated app did not become reachable at {url}"]
            elif status != 200:
                errors = [f"generated app returned HTTP {status}"]
            elif browser:
                try:
                    errors = browser_check(project_dir, url, app_plan.tests)
                except BrowserCheckUnavailable:
                    errors = ["browser verification requested but Playwright is unavailable"]
            else:
                errors = []
            process.terminate()

        if not errors:
            break
        if repairs >= max_repairs:
            break

        try:
            result = repair(
                app_plan.description,
                _read_files(project_dir),
                errors,
                model=model,
                base_url=base_url,
            )
        except Exception:
            break

        _apply_updates(project_dir, result.files)
        repairs += 1
        errors = verify(project_dir)

    return app_plan, project_dir, errors, url, repairs
