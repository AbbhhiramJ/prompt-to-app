"""Host-agent software factory contract.

The generated application never receives provider credentials. The host agent
owns research, repository, deployment, and verification capabilities.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping, Optional, Sequence

from .workflow import BuildState, PromptToAppWorkflow


@dataclass
class FactoryCapabilities:
    """Capabilities supplied by the host agent."""

    research: Optional[Callable[[str], Mapping[str, object]]] = None
    create_repository: Optional[Callable[[str, str], str]] = None
    write_repository: Optional[
        Callable[[str, Mapping[str, str], str], str]
    ] = None
    deploy: Optional[Callable[[str, str], str]] = None
    verify_live: Optional[Callable[[str], bool]] = None


@dataclass
class FactoryResult:
    """User-facing result of a complete prompt-to-live-app run."""

    state: BuildState
    status: str
    live_url: Optional[str] = None
    repository_url: Optional[str] = None
    summary: str = ""
    next_action: str = ""


class SoftwareFactory:
    """End-goal orchestration layer.

    Intelligence and credentials remain on the host side. The generated app
    is only the output artifact and does not need an LLM, GitHub, Vercel,
    Composio, or Ollama credential.
    """

    def __init__(
        self,
        capabilities: FactoryCapabilities,
        workflow: PromptToAppWorkflow,
    ) -> None:
        self.capabilities = capabilities
        self.workflow = workflow

    def build(self, prompt: str) -> FactoryResult:
        if not prompt.strip():
            raise ValueError("prompt cannot be empty")

        if self.capabilities.research is None:
            raise ValueError("host research capability is required")
        if self.capabilities.create_repository is None:
            raise ValueError("host repository capability is required")
        if self.capabilities.write_repository is None:
            raise ValueError("host repository write capability is required")
        if self.capabilities.deploy is None:
            raise ValueError("host deployment capability is required")
        if self.capabilities.verify_live is None:
            raise ValueError("host live verification capability is required")

        state, files = self.workflow.prepare(prompt)

        repo_url = self.capabilities.create_repository(
            state.plan.get("name", "generated-app"),
            state.plan.get("description", "Generated application"),
        )
        state.repository_url = repo_url

        commit_sha = self.capabilities.write_repository(
            repo_url,
            files,
            "Generate application from natural-language prompt",
        )
        state.commit_sha = commit_sha

        live_url = self.capabilities.deploy(repo_url, commit_sha)
        state.deployment_url = live_url

        if not self.capabilities.verify_live(live_url):
            state.errors.append("live deployment verification failed")
            return FactoryResult(
                state=state,
                status="failed",
                live_url=live_url,
                repository_url=repo_url,
                summary="The application was deployed but did not pass live verification.",
                next_action="Inspect deployment logs and repair the generated application.",
            )

        return FactoryResult(
            state=state,
            status="ready",
            live_url=live_url,
            repository_url=repo_url,
            summary="Application researched, built, tested, deployed, and verified.",
            next_action="Open the live URL.",
        )
