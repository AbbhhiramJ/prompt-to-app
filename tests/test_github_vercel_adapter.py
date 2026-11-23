"""Deterministic, credential-free contract tests for remote provider adapters."""
import pytest

from prompt_to_app.github_vercel import (
    GitHubVercelAdapter, ProviderError, slugify,
)

A = "a" * 40
B = "b" * 40
C = "c" * 40
D = "d" * 40


class FakeTransport:
    def __init__(self):
        self.calls = []
        self.verified_urls = []

    def request(self, method, url, token, payload=None):
        self.calls.append((method, url, token, payload))
        if url.endswith("/user/repos"):
            return {"html_url": "https://github.com/example/demo", "private": True}
        if url.endswith("/repos/example/demo"):
            return {"id": 123, "private": True, "default_branch": "main"}
        if "/git/ref/heads/main" in url:
            return {"object": {"sha": A}}
        if "/git/commits/" + A in url:
            return {"tree": {"sha": B}}
        if url.endswith("/git/blobs"):
            return {"sha": C}
        if url.endswith("/git/trees"):
            return {"sha": D}
        if url.endswith("/git/commits"):
            return {"sha": A}
        if url.endswith("/git/refs/heads/main"):
            return {"ref": "refs/heads/main"}
        if url.endswith("/v11/projects"):
            return {"id": "prj_test"}
        if url.endswith("/v13/deployments"):
            return {"id": "dep_test", "url": "demo-123.vercel.app"}
        if url.endswith("/v13/deployments/dep_test"):
            return {"readyState": "READY"}
        raise AssertionError(f"Unknown request {method} {url}")

    def probe(self, url):
        self.verified_urls.append(url)
        return True


def test_slug_and_explicit_publish_gate(monkeypatch):
    assert slugify("Study Planner 2026!") == "study-planner-2026"
    with pytest.raises(ValueError):
        slugify("...")
    monkeypatch.delenv("PROMPT_TO_APP_ENABLE_PUBLISH", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "secret")
    monkeypatch.setenv("VERCEL_TOKEN", "secret")
    with pytest.raises(ProviderError, match="disabled"):
        GitHubVercelAdapter.from_environment()


def test_end_to_end_api_contract_uses_private_repo_and_preview_only():
    transport = FakeTransport()
    adapter = GitHubVercelAdapter("github-secret", "vercel-secret", transport=transport, verify_attempts=1)
    url = adapter.create_repository("Demo", "Private app")
    sha = adapter.write_repository(url, {"index.html": "<h1>Hi</h1>"}, "Generated app")
    deployment = adapter.deploy(url, sha)
    assert deployment == "https://demo-123.vercel.app"
    assert adapter.verify_live(deployment) is True

    repo_payload = next(p for m, u, _, p in transport.calls if u.endswith("/user/repos"))
    assert repo_payload["private"] is True
    ref_payload = next(p for m, u, _, p in transport.calls if "/git/refs/heads/main" in u)
    assert ref_payload["force"] is False
    vercel_payload = next(p for m, u, _, p in transport.calls if u.endswith("/v13/deployments"))
    assert vercel_payload["gitSource"]["sha"] == A
    assert vercel_payload.get("target") != "production"
    assert transport.verified_urls == [deployment]
    assert all("secret" not in str(p) for _, _, _, p in transport.calls)


def test_rejects_unsafe_generated_content_before_remote_writes():
    transport = FakeTransport()
    adapter = GitHubVercelAdapter("gh", "ve", transport=transport)
    with pytest.raises(ProviderError):
        adapter.write_repository("https://github.com/example/demo", {"../secret": "bad"}, "message")
    assert transport.calls == []


def test_refuses_to_publish_existing_public_repo():
    class PublicTransport(FakeTransport):
        def request(self, method, url, token, payload=None):
            if url.endswith("/repos/example/demo"):
                return {"id": 123, "private": False, "default_branch": "main"}
            return super().request(method, url, token, payload)

    adapter = GitHubVercelAdapter("gh", "ve", transport=PublicTransport())
    with pytest.raises(ProviderError, match="public"):
        adapter.write_repository("https://github.com/example/demo", {"a.txt": "a"}, "message")


def test_unknown_deployment_and_remote_failure_are_not_ready():
    adapter = GitHubVercelAdapter("gh", "ve", transport=FakeTransport(), verify_attempts=1)
    assert adapter.verify_live("https://unknown.vercel.app") is False
    adapter._deployments["https://demo-123.vercel.app"] = "dep_test"
    assert adapter.verify_live("https://demo-123.vercel.app") is True
