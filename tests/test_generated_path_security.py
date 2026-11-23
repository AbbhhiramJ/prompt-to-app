"""Host-side safety checks for untrusted generated repository files."""
import pytest

from prompt_to_app.factory import FactoryCapabilities, SoftwareFactory
from prompt_to_app.workflow import (
    MAX_GENERATED_FILES,
    MAX_GENERATED_TEXT_BYTES,
    PromptToAppWorkflow,
    validate_generated_files,
)


@pytest.mark.parametrize("unsafe", [
    "../escape.txt", "src/../escape.txt", "src/./main.js", "/tmp/file",
    "C:/Users/demo/file", r"C:\\Users\\demo\\file", "src//app.js",
    ".github/workflows/exfiltrate.yml", "nested/.git/config",
    ".env", ".env.production", "nested/.ENV.local",
    "strange\x00file.js", "src/\nfile.js",
])
def test_generated_paths_reject_unsafe_targets(unsafe):
    assert validate_generated_files({unsafe: "content"})


def test_safe_nested_paths_are_allowed():
    assert validate_generated_files({
        "src/components/Button.tsx": "export default 1;",
        "index.html": "<h1>ok</h1>",
        "package.json": '{"private": true}',
    }) == []


def test_nontext_and_resource_limits():
    assert validate_generated_files({"asset.bin": b"payload"})
    assert validate_generated_files({f"f{i}.txt": "x" for i in range(MAX_GENERATED_FILES + 1)})
    assert validate_generated_files({"huge.txt": "x" * (MAX_GENERATED_TEXT_BYTES + 1)})


def test_unsafe_generation_never_reaches_runner_or_github():
    calls = []
    workflow = PromptToAppWorkflow(
        research=lambda _prompt: {},
        plan=lambda _prompt, _research: {"name": "demo"},
        generate=lambda *_: {"../outside.txt": "bad"},
        test=lambda _files: calls.append("test") or [],
    )
    factory = SoftwareFactory(
        workflow,
        FactoryCapabilities(
            lambda *_: calls.append("create") or "repo",
            lambda *_: calls.append("write") or "sha",
            lambda *_: calls.append("deploy") or "url",
            lambda *_: True,
        ),
    )
    result = factory.build("create app", max_repairs=0)
    assert result.status == "failed"
    assert any("unsafe path" in message for message in result.state.errors)
    assert calls == []
