import json
from pathlib import Path

from prompt_to_app.generator import generate
from prompt_to_app.models import AppPlan
from prompt_to_app.orchestrator import build
from prompt_to_app.repair import repair
from prompt_to_app.runner import wait_for_http

def test_build_creates_fallback_project(tmp_path):
    app_plan, project_dir, errors, url, repairs = build("Build a tiny notes app", tmp_path / "app", base_url="http://127.0.0.1:1")
    assert app_plan.name == "generated-app"
    assert project_dir.exists()
    assert errors == []
    assert url is None
    assert repairs == 0
    assert (project_dir / "index.html").exists()

def test_generator_accepts_ollama_json(monkeypatch, tmp_path):
    from prompt_to_app import generator
    monkeypatch.setattr(generator,"chat",lambda *args,**kwargs: json.dumps({"files":[
        {"path":"index.html","content":"<h1>Hello</h1>"},
        {"path":"style.css","content":"body{}"},
        {"path":"app.js","content":"console.log('ok')"}]}))
    plan_obj=AppPlan("demo","demo app",["html"],["index.html"],"python -m http.server 8000")
    root=generate(plan_obj,tmp_path/"generated")
    assert (root/"index.html").read_text()=="<h1>Hello</h1>"

def test_generated_web_app_gets_deployment_metadata(tmp_path):
    from prompt_to_app.deployment import ensure_deployment_metadata
    root=tmp_path/"generated"; root.mkdir()
    (root/"index.html").write_text("<!doctype html><html><body><h1>Demo</h1></body></html>")
    ensure_deployment_metadata(root)
    package=json.loads((root/"package.json").read_text())
    assert package["scripts"]["build"]=="vite build"
    assert (root/"vite.config.js").exists()

def test_wait_for_http_times_out():
    ok,status=wait_for_http("http://127.0.0.1:1",timeout=.4,interval=.05)
    assert ok is False
    assert status is None

def test_repair_rejects_unsafe_paths(monkeypatch):
    monkeypatch.setattr("prompt_to_app.repair.chat",lambda *args,**kwargs: json.dumps({"files":[{"path":"../escape.txt","content":"bad"}]}))
    try: repair("demo",{},["missing"],base_url="http://127.0.0.1:1")
    except ValueError: return
    assert False
