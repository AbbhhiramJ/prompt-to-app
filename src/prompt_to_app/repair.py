import json
from dataclasses import dataclass
from pathlib import Path
from .ollama import chat

REPAIR_SYSTEM = """You are a repair engine for a generated web app.
Return ONLY valid JSON:
{"files": {"relative/path": "replacement file content"}, "explanation": "short explanation"}
Fix the reported failures with the smallest necessary changes.
Only return files that need replacement. Never use absolute paths or '..'.
Do not rewrite unrelated files.
"""

@dataclass
class RepairResult:
    files: dict[str, str]
    explanation: str = ""

def repair(
    description: str,
    current_files: dict[str, str],
    errors: list[str],
    model: str = "qwen2.5-coder:7b",
    base_url: str = "http://127.0.0.1:11434",
) -> RepairResult:
    files = "\n\n".join(f"FILE: {n}\n{c}" for n, c in current_files.items())
    prompt = (
        f"{REPAIR_SYSTEM}\n\nAPP:\n{description}"
        f"\n\nFAILURES:\n- {'\n- '.join(errors)}"
        f"\n\nCURRENT FILES:\n{files}"
    )
    try:
        data = json.loads(chat(prompt, model, base_url))
    except Exception as exc:
        raise RuntimeError(f"repair generation failed: {exc}") from exc

    updates = data.get("files", {})
    if not isinstance(updates, dict):
        raise RuntimeError("repair response files must be an object")

    safe = {}
    for name, content in updates.items():
        path = Path(str(name))
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeError(f"unsafe repair path: {name}")
        safe[str(path)] = str(content)

    return RepairResult(safe, str(data.get("explanation", "")))
