from prompt_to_app.evidence import rank_sources, score_source

def test_authoritative_source_scores_higher():
    official=score_source("Official documentation","https://developer.apple.com/docs","documentation")
    blog=score_source("Random blog","https://example.com/x","")
    assert official.score > blog.score
    assert official.tier=="high"

def test_research_sources_are_ranked():
    rows=rank_sources([
      {"title":"Random blog","url":"https://example.com/a"},
      {"title":"Official documentation","url":"https://developer.android.com/docs","summary":"documentation and guidelines"},
    ])
    assert rows[0]["url"].startswith("https://developer.android.com")
    assert "evidence_score" in rows[0]
