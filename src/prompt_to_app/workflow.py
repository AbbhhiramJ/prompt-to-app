"""Agent-side Prompt -> App workflow contract.

The host agent supplies reasoning and connected-tool capabilities. Generated
applications never receive provider credentials.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Mapping, Protocol, Sequence

from .deployment import ensure_deployment_metadata

class Researcher(Protocol):
    def research(self, prompt: str) -> Mapping[str, object]: ...

class RepositoryManager(Protocol):
    def create_repository(self, name: str, description: str) -> str: ...
    def write_files(self, owner: str, repo: str, files: Mapping[str, str], message: str) -> str: ...
    def get_tree(self, owner: str, repo: str) -> Sequence[str]: ...

class Deployer(Protocol):
    def deploy_from_github(self, owner: str, repo_id: str, branch: str, name: str) -> str: ...
    def verify(self, url: str) -> bool: ...

@dataclass
class BuildState:
    prompt: str
    research: dict[str, object] = field(default_factory=dict)
    plan: dict[str, object] = field(default_factory=dict)
    repository_url: str | None = None
    commit_sha: str | None = None
    deployment_url: str | None = None
    repairs: int = 0
    errors: list[str] = field(default_factory=list)
    visual_errors: list[str] = field(default_factory=list)

def workflow_stages() -> tuple[str, ...]:
    return ("understand","research","blueprint","generate","test","visual_audit","repair","create_repository","write_files","deploy","verify_live","return_url")

def validate_generated_files(files: Mapping[str, str]) -> list[str]:
    errors=[]
    for path,content in files.items():
        normalized=path.replace("\\","/")
        if not normalized or normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized or normalized=="..":
            errors.append(f"unsafe path: {path}")
        if not isinstance(content,str):
            errors.append(f"non-text content: {path}")
    return errors

@dataclass
class PromptToAppWorkflow:
    research: Callable[[str], Mapping[str, object]]
    plan: Callable[[str, Mapping[str, object]], Mapping[str, object]]
    generate: Callable[[str, Mapping[str, object], Mapping[str, object]], Mapping[str, str]]
    test: Callable[[Mapping[str, str]], Sequence[str]]
    visual_audit: Callable[[Mapping[str, str]], Sequence[str]] | None = None
    repair: Callable[[str, Mapping[str, object], Mapping[str, str], Sequence[str]], Mapping[str, str]] | None = None

    def prepare(self, prompt: str) -> tuple[BuildState, Mapping[str, str]]:
        if not prompt.strip():
            raise ValueError("prompt cannot be empty")
        state=BuildState(prompt=prompt)
        state.research=dict(self.research(prompt))
        state.plan=dict(self.plan(prompt,state.research))
        files=dict(self.generate(prompt,state.plan,state.research))
        if "index.html" in files:
            files.setdefault("package.json",'{"name":"generated-app","private":true,"version":"1.0.0","scripts":{"build":"vite build","dev":"vite"}}')
            files.setdefault("vite.config.js","export default {}\\n")
        state.errors=validate_generated_files(files)
        state.errors.extend(self.test(files))
        if self.visual_audit is not None and not state.errors:
            state.visual_errors=list(self.visual_audit(files))
            state.errors.extend(state.visual_errors)
        return state,files

    def repair_until_green(self,state: BuildState,files: Mapping[str,str],max_repairs: int=2) -> tuple[BuildState,Mapping[str,str]]:
        if max_repairs<0: raise ValueError("max_repairs must be >= 0")
        current=dict(files)
        while state.errors and state.repairs<max_repairs:
            if self.repair is None: break
            current=dict(self.repair(state.prompt,state.plan,current,state.errors))
            if "index.html" in current:
                current.setdefault("package.json",'{"name":"generated-app","private":true,"version":"1.0.0","scripts":{"build":"vite build","dev":"vite"}}')
                current.setdefault("vite.config.js","export default {}\\n")
            state.repairs+=1
            state.visual_errors=[]
            state.errors=validate_generated_files(current)
            state.errors.extend(self.test(current))
            if self.visual_audit is not None and not state.errors:
                state.visual_errors=list(self.visual_audit(current))
                state.errors.extend(state.visual_errors)
        return state,current
