import json
from pathlib import Path
from .models import AppPlan
from .ollama import OllamaError, chat
from .prompts import GENERATOR_SYSTEM

def _fallback_files(plan: AppPlan) -> dict[str, str]:
    return {
        "index.html": f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{plan.name}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <h1>{plan.name}</h1>
    <p>{plan.description}</p>
    <button id="action">Test app</button>
    <p id="status"></p>
  </main>
  <script src="app.js"></script>
</body>
</html>
""",
        "style.css": """body{font-family:system-ui,sans-serif;max-width:760px;margin:80px auto;padding:24px}button{padding:10px 16px}#status{min-height:24px}""",
        "app.js": """document.querySelector('#action').addEventListener('click',()=>{document.querySelector('#status').textContent='App is working.'})""",
    }

def generate(plan: AppPlan, output_dir: str | Path, model: str = "qwen2.5-coder:7b", base_url: str = "http://127.0.0.1:11434") -> Path:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    files: dict[str, str]
    try:
        raw = chat(
            f"{GENERATOR_SYSTEM}\n\nApp name: {plan.name}\nDescription: {plan.description}\nStack: {plan.stack}\nRequested files: {plan.files}",
            model=model,
            base_url=base_url,
        )
        data = json.loads(raw)
        files = {str(item["path"]): str(item["content"]) for item in data["files"]}
    except (OllamaError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        files = _fallback_files(plan)

    for relative_path, content in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root
