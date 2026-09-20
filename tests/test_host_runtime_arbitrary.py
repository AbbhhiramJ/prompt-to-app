from prompt_to_app.host_runtime import HostCapabilities, PromptToAppHost
from prompt_to_app.workflow import PromptToAppWorkflow


def test_host_runtime_handles_an_arbitrary_product_prompt():
    events = []

    workflow = PromptToAppWorkflow(
        research=lambda prompt: {
            "product_findings": ["weekly planning", "task priorities"],
            "prompt": prompt,
        },
        plan=lambda prompt, research: {
            "name": "study-planner",
            "description": "A simple weekly study planner",
        },
        generate=lambda prompt, plan, research: {
            "index.html": "<h1>Study Planner</h1>",
        },
        test=lambda files: [],
    )

    host = PromptToAppHost(
        workflow,
        HostCapabilities(
            create_repository=lambda name, description: f"https://github.com/test/{name}",
            write_repository=lambda url, files, message: "study-sha-001",
            deploy=lambda url, sha: "https://study-planner.example",
            verify_live=lambda url: True,
        ),
        emit=events.append,
    )

    result = host.run(
        "Build a study planner for a university student with weekly goals and priorities."
    )

    assert result.status == "ready"
    assert result.live_url == "https://study-planner.example"
    assert result.repository_url == "https://github.com/test/study-planner"
    assert [event.stage for event in events] == [
        "understand",
        "research",
        "blueprint",
        "generate",
        "test",
        "visual_audit",
        "repair",
        "github",
        "deploy",
        "verify_live",
        "complete",
    ]
    assert result.state.prompt.startswith("Build a study planner")
