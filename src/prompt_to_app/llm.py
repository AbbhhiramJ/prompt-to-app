from __future__ import annotations
import json
import os
from dataclasses import dataclass
from urllib import request
from typing import Protocol

class LLM(Protocol):
    def generate(self, system: str, prompt: str) -> str: ...

class CloudLLMError(RuntimeError):
    pass

@dataclass
class OllamaLLM:
    model: str = "qwen2.5-coder:7b"
    base_url: str = "http://127.0.0.1:11434"
    def generate(self, system: str, prompt: str) -> str:
        body = json.dumps({"model": self.model, "system": system, "prompt": prompt, "stream": False}).encode()
        req = request.Request(self.base_url.rstrip("/") + "/api/generate", data=body, headers={"Content-Type": "application/json"}, method="POST")
        with request.urlopen(req, timeout=120) as resp:
            return str(json.loads(resp.read().decode())["response"])

@dataclass
class VercelGatewayLLM:
    model: str = "openai/gpt-5.6-mini"
    base_url: str = "https://ai-gateway.vercel.sh/v1"
    oidc_token: str | None = None
    def generate(self, system: str, prompt: str) -> str:
        token = self.oidc_token or os.getenv("VERCEL_OIDC_TOKEN")
        if not token:
            raise CloudLLMError("VERCEL_OIDC_TOKEN is unavailable")
        body = json.dumps({"model": self.model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]}).encode()
        req = request.Request(self.base_url.rstrip("/") + "/chat/completions", data=body, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}, method="POST")
        try:
            with request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            return str(data["choices"][0]["message"]["content"])
        except Exception as exc:
            raise CloudLLMError(str(exc)) from exc

@dataclass
class OpenAICompatibleLLM:
    api_key: str
    model: str = "gpt-4.1-mini"
    base_url: str = "https://api.openai.com/v1"
    def generate(self, system: str, prompt: str) -> str:
        body = json.dumps({"model": self.model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]}).encode()
        req = request.Request(self.base_url.rstrip("/") + "/chat/completions", data=body, headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}, method="POST")
        try:
            with request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            return str(data["choices"][0]["message"]["content"])
        except Exception as exc:
            raise CloudLLMError(str(exc)) from exc

def cloud_llm_from_env() -> LLM:
    if os.getenv("VERCEL_OIDC_TOKEN"):
        return VercelGatewayLLM(model=os.getenv("LLM_MODEL", "openai/gpt-5.6-mini"), base_url=os.getenv("AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh/v1"))
    key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise CloudLLMError("Production requires Vercel OIDC. Local legacy mode requires LLM_API_KEY.")
    return OpenAICompatibleLLM(key, os.getenv("LLM_MODEL", "gpt-4.1-mini"), os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))
