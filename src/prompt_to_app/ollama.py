import json
import urllib.error
import urllib.request
from typing import Any

class OllamaError(RuntimeError):
    pass

def chat(
    prompt: str,
    model: str = "qwen2.5-coder:7b",
    base_url: str = "http://127.0.0.1:11434",
    timeout: int = 120,
) -> str:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }).encode()

    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data: dict[str, Any] = json.load(response)
        return str(data["message"]["content"])
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise OllamaError(f"Ollama request failed: {exc}") from exc
