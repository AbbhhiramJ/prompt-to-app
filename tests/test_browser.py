import pytest
from prompt_to_app.browser import BrowserCheckUnavailable, check

def test_browser_check_returns_list_or_unavailable(tmp_path):
    (tmp_path / "index.html").write_text("<html><body>ok</body></html>", encoding="utf-8")
    try:
        result = check(tmp_path, "http://127.0.0.1:9", timeout=1)
    except BrowserCheckUnavailable:
        pytest.skip("Playwright is not installed")
    assert isinstance(result, list)
