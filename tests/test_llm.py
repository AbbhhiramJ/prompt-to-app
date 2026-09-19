import json
from prompt_to_app.llm import OpenAICompatibleLLM

def test_openai_compatible_llm(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self): return json.dumps({"choices":[{"message":{"content":"ok"}}]}).encode()
    def fake_urlopen(req, timeout):
        assert req.get_header("Authorization") == "Bearer test-key"
        assert req.full_url.endswith("/chat/completions")
        body=json.loads(req.data.decode())
        assert body["model"]=="test-model"
        assert body["messages"][0]["role"]=="system"
        return Response()
    monkeypatch.setattr("prompt_to_app.llm.request.urlopen",fake_urlopen)
    llm=OpenAICompatibleLLM("test-key","test-model","https://example.com/v1")
    assert llm.generate("system","hello")=="ok"
