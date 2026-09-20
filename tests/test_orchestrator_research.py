from pathlib import Path
from prompt_to_app.orchestrator import build

class FakeLLM:
    def generate(self, system, prompt):
        if "Research blueprint" in prompt:
            if "Return ONLY valid JSON" in system:
                return '{"name":"researched-app","description":"researched app","stack":["html","css","javascript"],"files":[{"path":"index.html","purpose":"main"}],"run_command":"python -m http.server 8000","tests":[{"type":"page_load"}]}'
            return '{"files":[{"path":"index.html","content":"<!doctype html><h1>Researched app</h1>"},{"path":"style.css","content":"body{}"},{"path":"app.js","content":"console.log(1)"}]}'
        raise AssertionError("research context missing")

def test_build_passes_research_to_plan_and_generation(tmp_path: Path):
    class Search:
        def __call__(self, query):
            return [{"title":"Example source","url":"https://example.com","summary":"responsive mobile UI"}]
    from prompt_to_app.research import ResearchEngine
    app, project, errors, url, repairs = build(
        "Build a habit tracker",
        output_dir=tmp_path / "app",
        llm=FakeLLM(),
        research=ResearchEngine(Search(), max_rounds=1, max_sources=1),
    )
    assert app.name == "researched-app"
    assert (project / "index.html").exists()
    assert errors == []
    assert url is None
    assert repairs == 0
