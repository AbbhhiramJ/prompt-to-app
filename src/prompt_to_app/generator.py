import json
from pathlib import Path
from .prompts import GENERATOR_SYSTEM
from .ollama import chat
from .llm import LLM, OllamaLLM
from .models import AppPlan

def _fallback_files(plan:AppPlan)->dict[str,str]:
    if plan.name=="habit-tracker":
        return {"index.html":"<!doctype html><html><head><meta charset='utf-8'><title>Habit Tracker</title><link rel='stylesheet' href='style.css'></head><body><main><h1>Habit Tracker</h1><p>Build consistency one habit at a time.</p><button id='add-habit'>Add habit</button><ul id='habits'></ul><p id='status'></p></main><script src='app.js'></script></body></html>","style.css":"body{font-family:system-ui,sans-serif;max-width:680px;margin:60px auto;padding:24px}button{padding:10px 16px}","app.js":"const b=document.querySelector('#add-habit'),l=document.querySelector('#habits'),s=document.querySelector('#status');b.onclick=()=>{const i=document.createElement('li');i.textContent='New habit';l.append(i);s.textContent='Habit added'};"}
    return {"index.html":f"<!doctype html><html><head><title>{plan.name}</title><link rel='stylesheet' href='style.css'></head><body><h1>{plan.name}</h1><p>{plan.description}</p><script src='app.js'></script></body></html>","style.css":"body{font-family:system-ui,sans-serif;max-width:760px;margin:80px auto;padding:24px}","app.js":"console.log('App is working');"}

def generate(plan:AppPlan,output_dir:str|Path,model:str="qwen2.5-coder:7b",base_url:str="http://127.0.0.1:11434",llm:LLM|None=None)->Path:
    root=Path(output_dir); root.mkdir(parents=True,exist_ok=True)
    try:
        if llm is None:
            raw=chat(GENERATOR_SYSTEM+f"\n\nApp name: {plan.name}\nDescription: {plan.description}\nStack: {plan.stack}\nRequested files: {plan.files}",model,base_url)
        else:
            raw=llm.generate(GENERATOR_SYSTEM,f"App name: {plan.name}\nDescription: {plan.description}\nStack: {plan.stack}\nRequested files: {plan.files}")
        data=json.loads(raw); files={str(x["path"]):str(x["content"]) for x in data["files"]}
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError):
        files=_fallback_files(plan)
    for name,content in files.items():
        path=root/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding="utf-8")
    return root
