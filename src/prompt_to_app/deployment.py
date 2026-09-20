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

    vite_config = root / "vite.config.js"
    if not vite_config.exists():
        vite_config.write_text("export default {}\n", encoding="utf-8")

    # Vercel does not infer the Vite output directory reliably for generated
    # framework-neutral projects. Explicitly route the built dist/ directory
    # so generated CSS/JS/assets are deployed with index.html.
    vercel = root / "vercel.json"
    if not vercel.exists():
        vercel.write_text(json.dumps({
            "buildCommand": "npm run build",
            "outputDirectory": "dist",
            "framework": "vite"
        }, indent=2) + "\n", encoding="utf-8")

    return root
