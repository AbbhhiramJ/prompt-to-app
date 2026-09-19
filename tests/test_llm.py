import json
import pytest
from prompt_to_app.llm import CloudLLMError,GeminiLLM

def test_gemini_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY",raising=False)
    with pytest.raises(CloudLLMError,match="GEMINI_API_KEY"): GeminiLLM()

def test_gemini_generates_text(monkeypatch):
    captured={}
    def fake_urlopen(request,timeout):
        captured["url"]=request.full_url;captured["body"]=json.loads(request.data.decode())
        return type("Fake",(),{"__enter__":lambda self:self,"__exit__":lambda self,*args:False,"read":lambda self:json.dumps({"candidates":[{"content":{"parts":[{"text":"hello"}]}}]}).encode()})()
    monkeypatch.setattr("prompt_to_app.llm.urllib.request.urlopen",fake_urlopen)
    assert GeminiLLM(api_key="test-key").generate("system","prompt")=="hello"
    assert captured["url"].endswith("models/gemini-2.5-flash:generateContent?key=test-key")
    assert captured["body"]["system_instruction"]["parts"][0]["text"]=="system"
