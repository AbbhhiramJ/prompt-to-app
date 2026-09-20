from prompt_to_app.blueprint import synthesize

def test_blueprint_has_product_decisions():
    report={"sources":[{"title":"114 habit tracking apps","url":"https://example.com","category":"product"}]}
    bp=synthesize("make a habit tracker",report)
    assert bp.core_loop
    assert bp.mvp_scope
    assert bp.evidence
    assert bp.decisions

def test_host_synthesizer_is_supported():
    bp=synthesize("x",{},lambda prompt,research: {"core_loop":["custom"],"mvp_scope":["custom"]})
    assert bp.core_loop == ["custom"]
    assert bp.mvp_scope == ["custom"]
