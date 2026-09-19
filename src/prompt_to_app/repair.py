import json
from dataclasses import dataclass
from pathlib import Path

from .ollama import OllamaError, chat

REPAIR_SYSTEM = """You are a repair engine for a generated web app.
Return ONLY valid JSON:
{"files": {"relative/path": "replacement file content"}, "explanation": "short explanation"}

Fix the reported verification failures with the smallest necessary changes.
Only return files that need replacement.
Never use absolute paths or paths containing '..'.
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
    context = "\n\n".join(
        f"FILE: {name}\n{content}" for name, content in current_files.items()
    )
    prompt = (
        f"{REPAIR_SYSTEM}\n\n"
        f"APP:\n{description}\n\n"
        f"VERIFICATION FAILURES:\n- " + "\n- ".join(errors) +
        f"\n\nCURRENT FILES:\n{context}"
    )
    try:
        raw = chat(prompt, model=model, base_url=base_url)
        data = json.loads(raw)
    except (OllamaError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise RuntimeError(f"repair generation failed: {exc}") from exc

    updates = data.get("files", {})
    if not isinstance(updates, dict):
        raise RuntimeError("repair response files must be an object")

    safe: dict[str, str] = {}
    for relative_path, content in updates.items():
        path = Path(str(relative_path))
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeError(f"unsafe repair path: {relative_path}")
        safe[str(path)] = str(content)

    return RepairResult(safe, str(data.get("explanation", "")))
