"""Thin host-agent entry point for Prompt -> App."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping
from .factory import FactoryCapabilities, FactoryResult, SoftwareFactory
from .workflow import PromptToAppWorkflow

@dataclass
class HostAgent:
    workflow: PromptToAppWorkflow
    create_repository: Callable[[str, str], str]
    write_repository: Callable[[str, Mapping[str, str], str], str]
    deploy: Callable[[str, str], str]
    verify_live: Callable[[str], bool]

    def run(self, prompt: str, max_repairs: int = 2) -> FactoryResult:
        return SoftwareFactory(
            self.workflow,
            FactoryCapabilities(self.create_repository, self.write_repository, self.deploy, self.verify_live),
        ).build(prompt, max_repairs=max_repairs)

def result_message(result: FactoryResult) -> str:
    if result.status == "ready" and result.live_url:
        return f"Your app is live: {result.live_url}\nRepository: {result.repository_url}"
    first_error = result.state.errors[0] if result.state.errors else "unknown failure"
    return f"Build failed: {first_error}\nRepository: {result.repository_url or 'not created'}"
