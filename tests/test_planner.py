from prompt_to_app.models import AppPlan

def test_app_plan_supports_generated_tests():
    plan = AppPlan(
        name="demo",
        description="demo",
        tests=[
            {"type": "page_load"},
            {"type": "click", "selector": "#go"},
        ],
    )
    assert plan.tests[1]["selector"] == "#go"
