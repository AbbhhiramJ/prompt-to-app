import json
import os
import urllib.error
import urllib.request
from typing import Protocol

class LLM(Protocol):
    def generate(self, system: str, prompt: str) -> str: ...

class CloudLLMError(RuntimeError):
    pass

class GeminiLLM:
    """Minimal production cloud LLM adapter using the Gemini REST API."""
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash",
                 base_url: str = "https://generativelanguage.googleapis.com/v1beta",
                 timeout: int = 120) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        if not self.api_key:
            raise CloudLLMError("GEMINI_API_KEY is required for cloud generation")

    def generate(self, system: str, prompt: str) -> str:
        body = json.dumps({
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}",
            data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.load(response)
            return str(data["candidates"][0]["content"]["parts"][0]["text"])
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise CloudLLMError(f"Gemini request failed ({exc.code}): {detail}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise CloudLLMError(f"Gemini request failed: {exc}") from exc
