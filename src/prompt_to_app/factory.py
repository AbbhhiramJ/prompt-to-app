"""End-to-end host-agent software factory."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping, Optional
from .workflow import BuildState, PromptToAppWorkflow

@dataclass
class FactoryCapabilities:
    create_repository: Callable[[str, str], str]
    write_repository: Callable[[str, Mapping[str, str], str], str]
    deploy: Callable[[str, str], str]
    verify_live: Callable[[str], bool]

@dataclass
class FactoryResult:
    state: BuildState
    status: str
    live_url: Optional[str] = None
    repository_url: Optional[str] = None
    summary: str = ""
    next_action: str = ""

class SoftwareFactory:
    """Turn one natural-language prompt into a verified deployed app."""
    def __init__(self, workflow: PromptToAppWorkflow, capabilities: FactoryCapabilities) -> None:
        self.workflow = workflow
        self.capabilities = capabilities

    def build(self, prompt: str, max_repairs: int = 2, on_stage: Callable[[str], None] | None = None) -> FactoryResult:
        if not prompt.strip():
            raise ValueError("prompt cannot be empty")
        notify = on_stage or (lambda _stage: None)
        if max_repairs < 0:
            raise ValueError("max_repairs must be non-negative")
        notify("understand")
        state = BuildState(prompt=prompt)
        try:
            state, files = self.workflow.prepare(prompt, on_stage=notify)
            if state.errors:
                state, files = self.workflow.repair_until_green(
                    state, files, max_repairs=max_repairs, on_stage=notify
                )
        except Exception as exc:
            # Generated projects and host providers are untrusted. Never expose
            # exception messages containing local paths or provider secrets.
            state.errors.append(f"generation error: {type(exc).__name__}")
            return FactoryResult(
                state, "failed",
                summary="Application generation stopped before verification.",
                next_action="Inspect the generation and test logs, then retry.",
            )
        if state.errors:
            return FactoryResult(state, "failed", summary="Generated app did not pass local verification.", next_action="Repair the reported errors and rerun the factory.")
        name = str(state.plan.get("name", "generated-app"))
        description = str(state.plan.get("description", "Generated application"))
        phase = "github"
        try:
            notify(phase)
            repo_url = self.capabilities.create_repository(name, description)
            state.repository_url = repo_url
            commit_sha = self.capabilities.write_repository(repo_url, files, "Generate application from natural-language prompt")
            state.commit_sha = commit_sha
            phase = "deploy"
            notify(phase)
            live_url = self.capabilities.deploy(repo_url, commit_sha)
            state.deployment_url = live_url
            phase = "verify_live"
            notify(phase)
            verified = self.capabilities.verify_live(live_url)
        except Exception as exc:
            # Host adapter exceptions may contain tokens, URLs or provider internals.
            # Do not expose exception messages in user-visible results.
            state.errors.append(f"{phase} adapter error: {type(exc).__name__}")
            return FactoryResult(
                state, "failed", live_url=state.deployment_url,
                repository_url=state.repository_url,
                summary="Publishing stopped before a verified live deployment.",
                next_action=f"Inspect the host {phase} adapter logs and retry.",
            )
        if not verified:
            state.errors.append("live deployment verification failed")
            return FactoryResult(state, "failed", live_url=live_url, repository_url=repo_url, summary="Deployment exists but did not pass live verification.", next_action="Inspect the deployment, repair the app, and redeploy.")
        return FactoryResult(state, "ready", live_url=live_url, repository_url=repo_url, summary="Application researched, planned, generated, tested, deployed, and verified.", next_action="Open the live URL.")
