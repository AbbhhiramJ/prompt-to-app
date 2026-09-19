from pathlib import Path

def verify(project_dir: str | Path) -> list[str]:
    root = Path(project_dir)
    errors: list[str] = []
    if not root.exists():
        errors.append("project directory does not exist")
        return errors
    if not (root / "index.html").exists():
        errors.append("index.html is missing")
    if not (root / "style.css").exists():
        errors.append("style.css is missing")
    if not (root / "app.js").exists():
        errors.append("app.js is missing")
    return errors
