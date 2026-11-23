from prompt_to_app.host_runtime import HostCapabilities, ProgressEvent, PromptToAppHost
from prompt_to_app.workflow import PromptToAppWorkflow


def test_host_runtime_emits_stages_and_returns_factory_result():
    events = []
    workflow = PromptToAppWorkflow(
        research=lambda prompt: {},
        plan=lambda prompt, research: {"name": "demo", "description": "demo"},
        generate=lambda prompt, plan, research: {"index.html": "<h1>Demo</h1>"},
        test=lambda files: [],
    )
    host = PromptToAppHost(
        workflow,
        HostCapabilities(
            create_repository=lambda name, description: f"https://github.com/test/{name}",
            write_repository=lambda url, files, message: "commit-sha",
            deploy=lambda url, sha: "https://demo.example",
            verify_live=lambda url: True,
        ),
        emit=events.append,
    )
    result = host.run("Build a demo")
    assert result.status == "ready"
    assert result.live_url == "https://demo.example"
    assert [event.stage for event in events] == [
        "understand", "research", "blueprint", "generate", "test",
        "github", "deploy", "verify_live", "complete",
    ]
    assert all(isinstance(event, ProgressEvent) for event in events)


def test_host_runtime_does_not_announce_unreached_stages():
    events = []
    workflow = PromptToAppWorkflow(
        research=lambda prompt: {},
        plan=lambda prompt, research: {"name": "broken"},
        generate=lambda prompt, plan, research: {"index.html": "broken"},
        test=lambda files: ["broken interaction"],
    )
    host = PromptToAppHost(
        workflow,
        HostCapabilities(
            create_repository=lambda *_: (_ for _ in ()).throw(AssertionError("should not publish")),
            write_repository=lambda *_: "commit",
            deploy=lambda *_: "https://example.test",
            verify_live=lambda *_: True,
        ),
        emit=events.append,
    )
    result = host.run("Build a broken app", max_repairs=0)
    assert result.status == "failed"
    assert [event.stage for event in events] == [
        "understand", "research", "blueprint", "generate", "test", "complete",
    ]
