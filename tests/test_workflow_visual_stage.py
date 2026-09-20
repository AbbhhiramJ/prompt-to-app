from prompt_to_app.workflow import PromptToAppWorkflow

def test_workflow_runs_visual_gate():
    calls=[]
    wf=PromptToAppWorkflow(
        research=lambda p: {"topic":p},
        plan=lambda p,r: {"name":"x"},
        generate=lambda p,plan,research: {"index.html":"ok"},
        test=lambda files: [],
        visual_audit=lambda files: calls.append("visual") or [],
    )
    state, files=wf.prepare("make x")
    assert state.errors == []
    assert calls == ["visual"]
