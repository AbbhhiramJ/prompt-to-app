import json
from .models import AppPlan
from .prompts import PLANNER_SYSTEM
from .llm import LLM, OllamaLLM
from .ollama import OllamaError

ALLOWED_TESTS={"page_load","text_visible","click","text_visible_after_click"}

def _fallback(prompt):
    habit="habit" in prompt.lower()
    return AppPlan(name="habit-tracker" if habit else "generated-app",description=prompt.strip(),stack=["html","css","javascript"],files=["index.html","style.css","app.js"],run_command="python -m http.server 8000",tests=([{"type":"page_load"},{"type":"text_visible","text":"Habit Tracker"},{"type":"click","selector":"#add-habit"},{"type":"text_visible_after_click","text":"Habit added"}] if habit else [{"type":"page_load"}]))

def _research_text(research):
    return json.dumps(research,ensure_ascii=False,indent=2) if research else "No external research was supplied."

def plan(prompt, llm=None, model="qwen2.5-coder:7b", base_url="http://127.0.0.1:11434", research=None):
    text=prompt.strip()
    if not text: raise ValueError("Prompt cannot be empty")
    try:
        engine=llm or OllamaLLM(model,base_url)
        data=json.loads(engine.generate(PLANNER_SYSTEM,f"User request:\n{text}\n\nResearch blueprint:\n{_research_text(research)}"))
        tests=[t for t in data.get("tests",[]) if isinstance(t,dict) and t.get("type") in ALLOWED_TESTS]
        files=[x.get("path","") if isinstance(x,dict) else str(x) for x in data.get("files",[])]
        return AppPlan(name=str(data.get("name","generated-app")),description=str(data.get("description",text)),stack=[str(x) for x in data.get("stack",["html","css","javascript"])],files=[x for x in files if x],run_command=str(data.get("run_command","python -m http.server 8000")),tests=tests)
    except (OSError,OllamaError,ValueError,KeyError,TypeError,json.JSONDecodeError):
        return _fallback(text)
