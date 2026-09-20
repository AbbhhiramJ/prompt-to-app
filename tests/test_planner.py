import json
from prompt_to_app.planner import plan

class FakeLLM:
    def generate(self, system, prompt):
        assert "Research blueprint" in prompt
        return json.dumps({"name":"researched-app","description":"A researched app","stack":["html","css","javascript"],"files":[{"path":"index.html","purpose":"main page"}],"run_command":"python -m http.server 8000","tests":[{"type":"page_load"}]})

def test_plan_accepts_research():
    result=plan("Build an app",llm=FakeLLM(),research={"product_findings":["one"],"ux_findings":["mobile first"]})
    assert result.name=="researched-app"
    assert result.tests==[{"type":"page_load"}]
