import pytest
from prompt_to_app.repair import repair

def test_repair_rejects_unsafe_path(monkeypatch):
    monkeypatch.setattr(
        "prompt_to_app.repair.chat",
        lambda *args, **kwargs: '{"files":{"../escape.html":"bad"}}',
    )
    with pytest.raises(RuntimeError, match="unsafe repair path"):
        repair("demo", {"index.html": "<html/>"}, ["TEST 1 failed"])

def test_repair_accepts_targeted_browser_failure(monkeypatch):
    monkeypatch.setattr(
        "prompt_to_app.repair.chat",
        lambda *args, **kwargs: '{"files":{"app.js":"document.querySelector(\\\"#add\\\");"},"explanation":"fix button wiring"}',
    )
    result = repair(
        "habit tracker",
        {"app.js": "old"},
        ["TEST 2 click FAILED: selector=#add"],
    )
    assert result.files["app.js"].startswith("document.querySelector")
    assert "fix button wiring" in result.explanation
