from pathlib import Path
from .planner import plan
from .generator import generate
from .verifier import verify
from .runner import serve_and_check
from .browser import run_browser_tests
from .repair import repair
from .llm import LLM

def build(prompt: str, output_dir: str | Path="./generated-app", model: str="qwen2.5-coder:7b",
          base_url: str="http://127.0.0.1:11434", serve: bool=False, port: int=8000,
          max_repairs: int=2, browser: bool=False, llm: LLM|None=None):
    if not prompt.strip(): raise ValueError("Prompt cannot be empty")
    if max_repairs < 0: raise ValueError("max_repairs must be >= 0")
    app = plan(prompt, model=model, base_url=base_url, llm=llm)
    project_dir = generate(app, output_dir, model=model, base_url=base_url, llm=llm)
    errors = verify(project_dir, app.files)
    url = None
    if serve and not errors:
        url = serve_and_check(project_dir, port)
    if browser and not errors and url:
        errors.extend(run_browser_tests(url, app.tests))
    repairs = 0
    while errors and repairs < max_repairs:
        current={str(p.relative_to(project_dir)):p.read_text(encoding="utf-8") for p in project_dir.rglob("*") if p.is_file()}
        result=repair(app.description,current,errors,model=model,base_url=base_url,llm=llm)
        for name,content in result.files.items():
            path=project_dir/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding="utf-8")
        errors=verify(project_dir,app.files)
        repairs += 1
    return app, project_dir, errors, url, repairs
