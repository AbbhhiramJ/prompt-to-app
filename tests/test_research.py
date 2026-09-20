from prompt_to_app.research import ResearchEngine, initial_research_questions

def test_initial_research_is_multidimensional():
    questions=initial_research_questions("a habit tracker")
    assert len(questions)==5
    assert any("UX" in q for q in questions)
    assert any("technical" in q.lower() for q in questions)

def test_research_engine_is_bounded_and_structured():
    calls=[]
    def search(query):
        calls.append(query)
        return [{"title":"Example","url":f"https://example.com/{len(calls)}","summary":"mobile responsive accessibility"}]
    report=ResearchEngine(search=search,max_rounds=2,max_sources=3).run("habit tracker")
    assert report.rounds<=2
    assert len(report.sources)<=3
    assert report.product_findings
    assert report.ux_findings
    assert report.assumptions
