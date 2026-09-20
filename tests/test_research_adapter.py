from prompt_to_app.research_adapter import composio_search_adapter, normalize_search_result

def test_normalize_search_result():
    result=normalize_search_result({"title":"A","url":"https://example.com","snippet":"hello"})
    assert result == {"title":"A","url":"https://example.com","summary":"hello","relevance":""}

def test_composio_adapter_builds_engine():
    engine=composio_search_adapter(lambda q: [], max_rounds=1, max_sources=2)
    report=engine.run("test app")
    assert report.rounds == 1
    assert report.sources == []
