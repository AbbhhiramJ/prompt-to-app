import json
from pathlib import Path

from prompt_to_app.generator import generate
from prompt_to_app.models import AppPlan
from prompt_to_app.ollama import chat
from prompt_to_app.orchestrator import build
from prompt_to_app.planner import plan

def test_plan_rejects_empty_prompt():
    try:
        plan("")
    except ValueError:
        return
    assert False

def test_build_creates_fallback_project(tmp_path):
    app_plan, project_dir, errors = build(
        "Build a tiny notes app",
        tmp_path / "app",
        base_url="http://127.0.0.1:1",
    )
    assert app_plan.name == "generated-app"
    assert project_dir.exists()
    assert errors == []
    assert (project_dir / "index.html").exists()
    assert (project_dir / "style.css").exists()
    assert (project_dir / "app.js").exists()

def test_generator_accepts_ollama_json(monkeypatch, tmp_path):
    from prompt_to_app import generator
    monkeypatch.setattr(
        generator,
        "chat",
        lambda *args, **kwargs: json.dumps({
            "files": [
                {"path": "index.html", "content": "<h1>Hello</h1>"},
                {"path": "style.css", "content": "body{}"},
                {"path": "app.js", "content": "console.log('ok')"},
            ]
        }),
    )
    plan_obj = AppPlan("demo", "demo app", ["html"], ["index.html"], "python -m http.server 8000")
    root = generate(plan_obj, tmp_path / "generated")
    assert (root / "index.html").read_text() == "<h1>Hello</h1>"

def test_ollama_payload_shape(monkeypatch):
    class FakeResponse:
        def read(self):
            return json.dumps({"message": {"content": "ok"}}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    from prompt_to_app import ollama
    monkeypatch.setattr(ollama.urllib.request, "urlopen", lambda *args, **kwargs: FakeResponse())
    assert chat("hello") == "ok"
