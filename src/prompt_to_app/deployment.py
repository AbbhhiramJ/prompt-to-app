from __future__ import annotations
from pathlib import Path
import json

def _is_vanilla_web(root: Path) -> bool:
    return (root / "index.html").exists() and (
        (root / "app.js").exists() or (root / "script.js").exists()
    ) and (root / "style.css").exists()

def ensure_deployment_metadata(project_dir: str | Path) -> Path:
    root = Path(project_dir)
    if not (root / "index.html").exists():
        return root

    package = root / "package.json"
    if not package.exists() and not _is_vanilla_web(root):
        package.write_text(
            json.dumps({
                "name": "generated-app",
                "private": True,
                "version": "1.0.0",
                "scripts": {"build": "vite build", "dev": "vite"},
            }, indent=2) + "\n",
            encoding="utf-8",
        )

    vercel = root / "vercel.json"
    if not vercel.exists():
        if _is_vanilla_web(root):
            # Plain HTML/CSS/JS apps do not need a Node build. Serving the
            # repository root avoids requiring npm/vite just to deploy static files.
            config = {
                "buildCommand": "echo static-site",
                "outputDirectory": ".",
            }
        else:
            config = {
                "buildCommand": "npm run build",
                "outputDirectory": "dist",
                "framework": "vite",
            }
        vercel.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    if not _is_vanilla_web(root):
        vite_config = root / "vite.config.js"
        if not vite_config.exists():
            vite_config.write_text("export default {}\n", encoding="utf-8")

    return root
