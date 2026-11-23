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


def test_factory_reports_failed_deploy_without_leaking_provider_exception():
    secret = "secret-provider-credential"
    def broken_deploy(_url, _sha):
        raise RuntimeError(secret)

    result = SoftwareFactory(
        make_workflow(),
        FactoryCapabilities(
            lambda *_: "https://github.com/example/demo-app",
            lambda *_: "abc123",
            broken_deploy,
            lambda *_: True,
        ),
    ).build("make a demo")
    assert result.status == "failed"
    assert result.repository_url == "https://github.com/example/demo-app"
    assert result.live_url is None
    assert "deploy adapter error" in result.state.errors[-1]
    assert secret not in repr(result)
    assert "deploy" in result.next_action


def test_factory_does_not_claim_live_when_verifier_raises():
    result = SoftwareFactory(
        make_workflow(),
        FactoryCapabilities(
            lambda *_: "https://github.com/example/demo-app",
            lambda *_: "abc123",
            lambda *_: "https://demo.example.com",
            lambda *_: (_ for _ in ()).throw(TimeoutError("network timeout")),
        ),
    ).build("make a demo")
    assert result.status == "failed"
    assert result.live_url == "https://demo.example.com"
    assert "verify_live adapter error" in result.state.errors[-1]


def test_factory_handles_generator_failure_without_publishing():
    workflow = PromptToAppWorkflow(
        research=lambda _prompt: (_ for _ in ()).throw(RuntimeError("secret-provider-token")),
        plan=lambda *_: {},
        generate=lambda *_: {},
        test=lambda _files: [],
    )
    calls = []
    result = SoftwareFactory(
        workflow,
        FactoryCapabilities(
            lambda *_: calls.append("repo") or "repo",
            lambda *_: calls.append("write") or "sha",
            lambda *_: calls.append("deploy") or "url",
            lambda *_: True,
        ),
    ).build("make a demo")
    assert result.status == "failed"
    assert result.repository_url is None
    assert calls == []
    assert "generation error: RuntimeError" in result.state.errors
    assert "secret-provider-token" not in repr(result)


def test_host_runtime_marks_complete_after_failed_generation():
    from prompt_to_app.host_runtime import PromptToAppHost, HostCapabilities
    events = []
    workflow = PromptToAppWorkflow(
        research=lambda _prompt: {},
        plan=lambda *_: (_ for _ in ()).throw(RuntimeError("plan failed")),
        generate=lambda *_: {},
        test=lambda _files: [],
    )
    host = PromptToAppHost(
        workflow,
        HostCapabilities(
            lambda *_: "repo", lambda *_: "sha",
            lambda *_: "url", lambda *_: True,
        ),
        emit=events.append,
    )
    result = host.run("Build a demo")
    assert result.status == "failed"
    assert [event.stage for event in events] == [
        "understand", "research", "blueprint", "complete",
    ]
