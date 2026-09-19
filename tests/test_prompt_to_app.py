from prompt_to_app.planner import plan
from prompt_to_app.orchestrator import build

def test_plan_rejects_empty_prompt():
    try:
        plan("")
    except ValueError:
        return
    assert False

def test_build_creates_project(tmp_path):
    app_plan, project_dir, errors = build("Build a tiny notes app", tmp_path / "app")
    assert app_plan.name == "generated-app"
    assert project_dir.exists()
    assert errors == []
    assert (project_dir / "README.md").exists()
