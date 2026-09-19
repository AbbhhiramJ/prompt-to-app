import json
import urllib.error
import urllib.request
from typing import Any

class OllamaError(RuntimeError):
    pass

def chat(prompt: str, model: str = "qwen2.5-coder:7b", base_url: str = "http://127.0.0.1:11434", timeout: int = 120) -> str:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise OllamaError(f"Ollama request failed: {exc}") from exc

    try:
        return str(data["message"]["content"])
    except (KeyError, TypeError) as exc:
        raise OllamaError("Ollama returned an unexpected response") from exc
