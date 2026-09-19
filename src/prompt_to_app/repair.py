import json
from dataclasses import dataclass
from pathlib import Path
from .ollama import chat
from .llm import LLM
REPAIR_SYSTEM="""You are a repair engine for a generated web app.
Return ONLY valid JSON:
{"files":{"relative/path":"replacement file content"},"explanation":"short explanation"}
Fix reported failures with the smallest necessary changes. Only return files that need replacement. Never use absolute paths or '..'. Do not rewrite unrelated files.
"""
@dataclass
class RepairResult:
    files:dict[str,str]
    explanation:str=""

def repair(description:str,current_files:dict[str,str],errors:list[str],model:str="qwen2.5-coder:7b",base_url:str="http://127.0.0.1:11434",llm:LLM|None=None)->RepairResult:
    files="\n\n".join(f"FILE: {n}\n{c}" for n,c in current_files.items())
    prompt=f"{REPAIR_SYSTEM}\n\nAPP:\n{description}\n\nFAILURES:\n- {'\n- '.join(errors)}\n\nCURRENT FILES:\n{files}"
    try:
        raw=llm.generate(REPAIR_SYSTEM,prompt) if llm else chat(prompt,model,base_url)
        data=json.loads(raw)
    except Exception as exc: raise RuntimeError(f"repair generation failed: {exc}") from exc
    updates=data.get("files",{})
    if isinstance(updates,list):
        updates={str(item["path"]):str(item["content"]) for item in updates if isinstance(item,dict) and "path" in item and "content" in item}
    if not isinstance(updates,dict): raise RuntimeError("repair response files must be an object or list")
    safe={}
    for name,content in updates.items():
        path=Path(str(name))
        if path.is_absolute() or ".." in path.parts: raise ValueError(f"unsafe repair path: {name}")
        safe[str(path)]=str(content)
    return RepairResult(safe,str(data.get("explanation","")))
