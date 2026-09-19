import json
from dataclasses import dataclass
from .ollama import OllamaError, chat

@dataclass
class RepairResult:
    files: dict[str, str]
    explanation: str

REPAIR_SYSTEM = """You are the repair engine for Prompt → App.
A generated web application failed verification or runtime checks.
Return ONLY valid JSON:
{
  "files": [
    {"path": "relative/path", "content": "complete replacement content"}
  ],
  "explanation": "short description of the repair"
}
Only return files that need replacement. Preserve working files when possible.
Never use absolute paths or paths containing '..'.
"""

def repair(
    project_description: str,
    files: dict[str, str],
    errors: list[str],
    model: str = "qwen2.5-coder:7b",
    base_url: str = "http://127.0.0.1:11434",
) -> RepairResult:
    payload = {
        "description": project_description,
        "errors": errors,
        "files": files,
    }
    raw = chat(
        f"{REPAIR_SYSTEM}\n\nFailure report:\n{json.dumps(payload)}",
        model=model,
        base_url=base_url,
    )
    data = json.loads(raw)
    updates: dict[str, str] = {}
    for item in data["files"]:
        path = str(item["path"])
        if path.startswith("/") or ".." in path.split("/"):
            raise ValueError(f"unsafe repair path: {path}")
        updates[path] = str(item["content"])
    return RepairResult(updates, str(data.get("explanation", "Applied generated repair.")))
