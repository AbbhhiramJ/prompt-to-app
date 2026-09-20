from __future__ import annotations
from pathlib import Path
import json

def ensure_deployment_metadata(project_dir: str | Path) -> Path:
    root = Path(project_dir)
    if not (root / "index.html").exists():
        return root
    package = root / "package.json"
    if not package.exists():
        package.write_text(json.dumps({
            "name": "generated-app",
            "private": True,
            "version": "1.0.0",
            "scripts": {"build": "vite build", "dev": "vite"}
        }, indent=2) + "\n", encoding="utf-8")
    if not (root / "package-lock.json").exists():
        (root / "vite.config.js").write_text("export default {}\n", encoding="utf-8")
    return root
