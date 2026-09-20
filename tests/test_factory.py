from prompt_to_app.factory import FactoryCapabilities, SoftwareFactory
from prompt_to_app.host_agent import result_message
from prompt_to_app.workflow import PromptToAppWorkflow

def make_workflow():
    return PromptToAppWorkflow(
        research=lambda prompt: {"prompt": prompt, "sources": []},
        plan=lambda prompt, research: {"name": "demo-app", "description": "demo"},
        generate=lambda prompt, plan, research: {"index.html": "<!doctype html><h1>Demo</h1>"},
        test=lambda files: [],
    )

def test_factory_returns_verified_live_url():
    calls = []
    result = SoftwareFactory(
        make_workflow(),
        FactoryCapabilities(
            lambda name, desc: (calls.append("repo") or "https://github.com/example/demo-app"),
            lambda url, files, msg: (calls.append("write") or "abc123"),
            lambda url, sha: (calls.append("deploy") or "https://demo.example.com"),
            lambda url: (calls.append("verify") or True),
        ),
    ).build("make a demo")
    assert result.status == "ready"
    assert result.live_url == "https://demo.example.com"
    assert result.state.commit_sha == "abc123"
    assert calls == ["repo", "write", "deploy", "verify"]
    assert "https://demo.example.com" in result_message(result)

def test_factory_does_not_publish_failed_artifacts():
    workflow = PromptToAppWorkflow(
        research=lambda prompt: {"sources": []},
        plan=lambda prompt, research: {"name": "broken"},
        generate=lambda prompt, plan, research: {"index.html": "broken"},
        test=lambda files: ["broken interaction"],
    )
    result = SoftwareFactory(
        workflow,
        FactoryCapabilities(lambda *_: "repo", lambda *_: "sha", lambda *_: "url", lambda *_: True),
    ).build("make it", max_repairs=0)
    assert result.status == "failed"
    assert result.repository_url is None
