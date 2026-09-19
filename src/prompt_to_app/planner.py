import json
from .models import AppPlan
from .ollama import OllamaError, chat
from .prompts import PLANNER_SYSTEM
from .llm import LLM

ALLOWED_TESTS={"page_load","text_visible","click","text_visible_after_click"}

def _fallback(prompt:str)->AppPlan:
    habit="habit" in prompt.lower()
    return AppPlan(name="habit-tracker" if habit else "generated-app",description=prompt.strip(),
        stack=["html","css","javascript"],files=["index.html","style.css","app.js"],
        run_command="python -m http.server 8000",
        tests=([{"type":"page_load"},{"type":"text_visible","text":"Habit Tracker"},{"type":"click","selector":"#add-habit"},{"type":"text_visible_after_click","text":"Habit added"}] if habit else [{"type":"page_load"}]))

def plan(prompt:str,model:str="qwen2.5-coder:7b",base_url:str="http://127.0.0.1:11434",llm:LLM|None=None)->AppPlan:
    text=prompt.strip()
    if not text: raise ValueError("Prompt cannot be empty")
    try:
        raw=llm.generate(PLANNER_SYSTEM,f"User request:\n{text}") if llm else chat(f"{PLANNER_SYSTEM}\n\nUser request:\n{text}",model,base_url)
        data=json.loads(raw)
        tests=[t for t in data.get("tests",[]) if isinstance(t,dict) and t.get("type") in ALLOWED_TESTS]
        return AppPlan(name=str(data.get("name","generated-app")),description=str(data.get("description",text)),
            stack=[str(x) for x in data.get("stack",["html","css","javascript"])],
            files=[str(x.get("path",x)) if isinstance(x,dict) else str(x) for x in data.get("files",[])],
            run_command=str(data.get("run_command","python -m http.server 8000")),tests=tests)
    except (OllamaError,json.JSONDecodeError,TypeError,ValueError):
        return _fallback(text)
