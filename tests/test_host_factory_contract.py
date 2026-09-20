from prompt_to_app.workflow import PromptToAppWorkflow

def test_prepare_injects_web_deployment_contract():
    workflow=PromptToAppWorkflow(
        research=lambda prompt: {},
        plan=lambda prompt,research: {"name":"demo","description":"demo"},
        generate=lambda prompt,plan,research: {"index.html":"<h1>Demo</h1>"},
        test=lambda files: [],
    )
    state,files=workflow.prepare("Build a demo")
    assert state.errors==[]
    assert "package.json" in files
    assert "vite.config.js" in files
    assert '"build": "vite build"' in files["package.json"]
