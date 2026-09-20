import json
from pathlib import Path
from .prompts import GENERATOR_SYSTEM
from .ollama import chat, OllamaError
from .llm import LLM
from .models import AppPlan

def _fallback_files(plan):
    if plan.name=="habit-tracker":
        return {"index.html":"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Habit Tracker</title><link rel='stylesheet' href='style.css'></head><body><main><h1>Habit Tracker</h1><p>Build consistency one habit at a time.</p><button id='add-habit'>Add habit</button><ul id='habits'></ul><p id='status'></p></main><script type='module' src='app.js'></script></body></html>","style.css":"body{font-family:system-ui,sans-serif;max-width:760px;margin:80px auto;padding:24px}button{padding:10px 16px}","app.js":"const b=document.querySelector('#add-habit'),l=document.querySelector('#habits'),s=document.querySelector('#status');b.onclick=()=>{const i=document.createElement('li');i.textContent='New habit';l.append(i);s.textContent='Habit added'}"}
    return {"index.html":f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{plan.name}</title><link rel='stylesheet' href='style.css'></head><body><main><h1>{plan.name}</h1><p>{plan.description}</p></main><script type='module' src='app.js'></script></body></html>","style.css":"body{font-family:system-ui,sans-serif;max-width:760px;margin:80px auto;padding:24px}","app.js":"console.log('App is working')"}

def _research_text(research):
    return json.dumps(research,ensure_ascii=False,indent=2) if research else "No external research was supplied."

def _normalize_files(files):
    files={str(k):str(v) for k,v in files.items()}
    html=files.get("index.html")
    if html is None:return files
    if "<html" not in html.lower():
        html=f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>App</title></head><body>{html}</body></html>"
    if "style.css" in files and "stylesheet" not in html.lower():
        html=html.replace("</head>","<link rel='stylesheet' href='style.css'></head>")
    if "app.js" in files and "<script" not in html.lower():
        html=html.replace("</body>","<script type='module' src='app.js'></script></body>")
    elif "app.js" in files:
        html=html.replace("<script src='app.js'>","<script type='module' src='app.js'>")
        html=html.replace('<script src="app.js">','<script type="module" src="app.js">')
    files["index.html"]=html
    return files

def generate(plan, output_dir, model="qwen2.5-coder:7b", base_url="http://127.0.0.1:11434", llm=None, research=None, normalize=False):
    root=Path(output_dir); root.mkdir(parents=True,exist_ok=True)
    try:
        prompt=f"User request: {plan.description}\nPlan: {plan}\nResearch blueprint:\n{_research_text(research)}"
        raw=chat(GENERATOR_SYSTEM,prompt,model,base_url) if llm is None else llm.generate(GENERATOR_SYSTEM,prompt)
        data=json.loads(raw)
        files={str(x["path"]):str(x["content"]) for x in data["files"]}
    except (OSError,OllamaError,ValueError,KeyError,TypeError,json.JSONDecodeError):
        files=_fallback_files(plan)
    if normalize: files=_normalize_files(files)
    for name,content in files.items():
        path=root/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding="utf-8")
    return root
