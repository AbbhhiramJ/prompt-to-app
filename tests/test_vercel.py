import json

from prompt_to_app.vercel import VercelError, deploy


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"url": "example.vercel.app"}).encode()


def test_deploy_requires_token():
    try:
        deploy({"index.html": "<h1>hi</h1>"}, token="")
    except VercelError as exc:
        assert "VERCEL_TOKEN" in str(exc)
    else:
        raise AssertionError("expected VercelError")


def test_deploy_returns_https_url(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["body"] = json.loads(request.data.decode())
        captured["auth"] = request.headers["Authorization"]
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("prompt_to_app.vercel.urlopen", fake_urlopen)

    url = deploy({"index.html": "<h1>hi</h1>"}, name="demo", token="test-token")

    assert url == "https://example.vercel.app"
    assert captured["auth"] == "Bearer test-token"
    assert captured["body"]["name"] == "demo"
    assert captured["body"]["files"][0]["file"] == "index.html"
    assert captured["body"]["target"] == "production"
