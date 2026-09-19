from pathlib import Path
import re

REQUIRED = ("index.html", "style.css", "app.js")

def verify(project_dir: str | Path) -> list[str]:
    root = Path(project_dir)
    if not root.exists():
        return ["project directory does not exist"]

    missing = [f"{name} is missing" for name in REQUIRED if not (root / name).exists()]
    if missing:
        return missing

    html = (root / "index.html").read_text(encoding="utf-8")
    js = (root / "app.js").read_text(encoding="utf-8")
    errors = []

    if "<html" not in html.lower():
        errors.append("index.html does not contain an HTML document")
    if not re.search(r'<script[^>]+src=["\']app\.js["\']', html, re.I):
        errors.append("index.html does not load app.js")
    if not js.strip():
        errors.append("app.js is empty")
    return errors
