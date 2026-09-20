from pathlib import Path
from prompt_to_app.visual import audit

def test_visual_audit_is_importable():
    assert callable(audit)

def test_visual_audit_reports_unreachable_url(tmp_path: Path):
    errors = audit("http://127.0.0.1:1", tmp_path, viewports=((320, 480),), timeout=1)
    assert errors
    assert any("visual 320x480" in e for e in errors)
