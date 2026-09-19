from prompt_to_app.orchestrator import build

def test_habit_tracker_fallback(tmp_path):
    plan, root, errors, url, repairs = build(
        "Build a simple habit tracker with habits, checkboxes, and completion status",
        output_dir=tmp_path / "habit-tracker",
        base_url="http://127.0.0.1:1",
        serve=True,
        browser=False,
        max_repairs=0,
    )
    assert plan.name == "habit-tracker"
    assert not errors
    assert repairs == 0
    assert "Habit Tracker" in (root / "index.html").read_text()

