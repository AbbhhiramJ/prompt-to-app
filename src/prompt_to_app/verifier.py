from pathlib import Path
import re

def verify(project_dir: str | Path) -> list[str]:
    root = Path(project_dir)
    errors: list[str] = []
    if not root.exists():
        return ["project directory does not exist"]

    required = ("index.html", "style.css", "app.js")
    for filename in required:
        if not (root / filename).exists():
            errors.append(f"{filename} is missing")

    if errors:
        return errors

    html = (root / "index.html").read_text(encoding="utf-8")
    js = (root / "app.js").read_text(encoding="utf-8")

    if "<html" not in html.lower():
        errors.append("index.html does not contain an HTML document")
    if not re.search(r"<script[^>]+src=["']app\.js["']", html, re.I):
        errors.append("index.html does not load app.js")
    if not js.strip():
        errors.append("app.js is empty")

    return errors
