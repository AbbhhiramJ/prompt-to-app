from __future__ import annotations
import json
import os
from dataclasses import dataclass
from urllib import request
from typing import Protocol

class LLM(Protocol):
    def generate(self, system: str, prompt: str) -> str: ...

@dataclass
class OllamaLLM:
    model: str = "qwen2.5-coder:7b"
    base_url: str = "http://127.0.0.1:11434"
    def generate(self, system: str, prompt: str) -> str:
        body=json.dumps({"model":self.model,"system":system,"prompt":prompt,"stream":False}).encode()
        req=request.Request(self.base_url.rstrip("/")+"/api/generate",data=body,headers={"Content-Type":"application/json"},method="POST")
        with request.urlopen(req,timeout=120) as resp:
            data=json.loads(resp.read().decode())
        return str(data["response"])

@dataclass
class OpenAICompatibleLLM:
    api_key: str
    model: str = "gpt-4.1-mini"
    base_url: str = "https://api.openai.com/v1"
    def generate(self, system: str, prompt: str) -> str:
        body=json.dumps({"model":self.model,"messages":[{"role":"system","content":system},{"role":"user","content":prompt}]}).encode()
        req=request.Request(self.base_url.rstrip("/")+"/chat/completions",data=body,headers={"Content-Type":"application/json","Authorization":f"Bearer {self.api_key}"},method="POST")
        with request.urlopen(req,timeout=120) as resp:
            data=json.loads(resp.read().decode())
        return str(data["choices"][0]["message"]["content"])

def cloud_llm_from_env() -> OpenAICompatibleLLM:
    key=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("LLM_API_KEY or OPENAI_API_KEY is required for cloud generation")
    return OpenAICompatibleLLM(
        api_key=key,
        model=os.getenv("LLM_MODEL","gpt-4.1-mini"),
        base_url=os.getenv("LLM_BASE_URL","https://api.openai.com/v1"),
    )
