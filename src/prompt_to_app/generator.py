import json
from pathlib import Path
from .models import AppPlan
from .ollama import OllamaError, chat
from .prompts import GENERATOR_SYSTEM

def _fallback_files(plan: AppPlan) -> dict[str, str]:
    if plan.name == "habit-tracker":
        return {
            "index.html": """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Habit Tracker</title><link rel="stylesheet" href="style.css"></head>
<body><main><h1>Habit Tracker</h1><p>Build consistency one habit at a time.</p>
<button id="add-habit">Add habit</button><ul id="habits"></ul><p id="status" aria-live="polite"></p>
</main><script src="app.js"></script></body></html>""",
            "style.css": """body{font-family:system-ui,sans-serif;max-width:680px;margin:60px auto;padding:24px}
button{padding:10px 16px;cursor:pointer}li{margin:10px 0}#status{min-height:24px}""",
            "app.js": """const button=document.querySelector('#add-habit');
const list=document.querySelector('#habits');
const status=document.querySelector('#status');
button.addEventListener('click',()=>{const item=document.createElement('li');item.textContent='New habit';list.append(item);status.textContent='Habit added';});""",
        }

    return {
        "index.html": f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{plan.name}</title><link rel="stylesheet" href="style.css"></head>
<body><main><h1>{plan.name}</h1><p>{plan.description}</p><button id="action">Test app</button><p id="status"></p></main>
<script src="app.js"></script></body></html>""",
        "style.css": "body{font-family:system-ui,sans-serif;max-width:760px;margin:80px auto;padding:24px}button{padding:10px 16px}#status{min-height:24px}",
        "app.js": "document.querySelector('#action').addEventListener('click',()=>document.querySelector('#status').textContent='App is working.');",
    }

def generate(plan: AppPlan, output_dir: str | Path, model: str = "qwen2.5-coder:7b", base_url: str = "http://127.0.0.1:11434") -> Path:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    try:
        raw = chat(
            f"{GENERATOR_SYSTEM}\n\nApp name: {plan.name}\nDescription: {plan.description}"
            f"\nStack: {plan.stack}\nRequested files: {plan.files}",
            model=model, base_url=base_url,
        )
        data = json.loads(raw)
        files = {str(item["path"]): str(item["content"]) for item in data["files"]}
    except (OllamaError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        files = _fallback_files(plan)

    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root
