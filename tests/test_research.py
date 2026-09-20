from prompt_to_app.research import ResearchEngine, initial_research_questions, research_depth

def test_research_depth():
    assert research_depth("make a simple timer")[0] == "quick"
    assert research_depth("make a modern analytics dashboard with current trends")[0] == "deep"

def test_questions_change_with_depth():
    assert len(initial_research_questions("timer","quick")) == 3
    assert len(initial_research_questions("analytics dashboard current trends","deep")) > 5

def test_research_engine_is_adaptive_and_bounded():
    calls=[]
    def search(query):
        calls.append(query)
        return [{"title":"Example","url":f"https://example.com/{len(calls)}","summary":"mobile responsive accessibility product"}]
    report=ResearchEngine(search=search,max_rounds=2,max_sources=3).run("analytics dashboard current trends")
    assert report.depth == "deep"
    assert report.rounds <= 2
    assert len(report.sources) <= 3
    assert report.product_findings and report.ux_findings and report.assumptions
