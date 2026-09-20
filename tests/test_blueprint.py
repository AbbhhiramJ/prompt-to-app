from prompt_to_app.blueprint import synthesize

class FakeLLM:
    def generate(self,system,prompt):
        assert "research" in prompt
        return '{"core_loop":["evidence-driven loop"],"onboarding":["fast"],"logging":["one tap"],"schedules":["custom"],"progress":["overview"],"streaks":["forgiving"],"reminders":["user controlled"],"integrations":[],"gamification":[],"privacy":["minimal"],"mobile_ux":["mobile first"],"mvp_scope":["core"],"decisions":["use evidence"],"caveats":["source limits"]}'

def test_blueprint_llm_synthesis():
    bp=synthesize("make x",{"sources":[{"title":"A","url":"https://a.example"}]},llm=FakeLLM())
    assert bp.core_loop == ["evidence-driven loop"]
    assert bp.decisions == ["use evidence"]
    assert bp.evidence[0]["url"]=="https://a.example"

def test_blueprint_fallback():
    bp=synthesize("make a habit tracker",{"sources":[{"title":"114 apps","url":"https://example.com"}]})
    assert bp.mvp_scope and bp.evidence

def test_synthesizer_type_is_available():
    from prompt_to_app.blueprint import Synthesizer
    assert Synthesizer is not None
