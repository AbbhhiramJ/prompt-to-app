from pathlib import Path
from .browser import BrowserCheckUnavailable, check as browser_check
from .generator import generate
from .models import AppPlan
from .planner import plan
from .repair import repair
from .runner import start, wait_for_http
from .verifier import verify

def _files(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): p.read_text(encoding="utf-8")
        for p in root.rglob("*") if p.is_file() and ".git" not in p.parts
    }

def _write(root: Path, updates: dict[str, str]) -> None:
    for name, content in updates.items():
        path = root / name
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

    app = plan(prompt, model, base_url)
    root = generate(app, output_dir, model, base_url)
    url = None
    errors = verify(root)
    repairs = 0

    while True:
        if not errors and serve:
            process = start(f"python -m http.server {port}", root)
            url = f"http://127.0.0.1:{port}"
            ok, status = wait_for_http(url)
            errors = [] if ok and status == 200 else [
                f"generated app did not become reachable at {url}" if not ok
                else f"generated app returned HTTP {status}"
            ]
            if not errors and browser:
                try:
                    errors = browser_check(root, url, app.tests)
                except BrowserCheckUnavailable as exc:
                    errors = [f"browser verification unavailable: {exc}"]
            process.terminate()

        if not errors or repairs >= max_repairs:
            break

        try:
            result = repair(app.description, _files(root), errors, model, base_url)
        except Exception:
            break
        _write(root, result.files)
        repairs += 1
        errors = verify(root)

    return app, root, errors, url, repairs
