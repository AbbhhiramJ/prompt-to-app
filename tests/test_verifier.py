from prompt_to_app.verifier import verify

def test_static_verifier_passes(tmp_path):
    (tmp_path / "index.html").write_text('<html><body><script src="app.js"></script></body></html>', encoding="utf-8")
    (tmp_path / "style.css").write_text("body {}", encoding="utf-8")
    (tmp_path / "app.js").write_text("console.log('ok')", encoding="utf-8")
    assert verify(tmp_path) == []

def test_static_verifier_reports_missing_file(tmp_path):
    (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / "style.css").write_text("", encoding="utf-8")
    assert "app.js is missing" in verify(tmp_path)
