"""Production host runtime for the Prompt -> App factory.

The runtime contains no provider SDKs or credentials. A connected host injects
capability callables and receives structured progress events plus a final result.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping, Optional

from .factory import FactoryResult, SoftwareFactory
from .workflow import PromptToAppWorkflow

@dataclass(frozen=True)
class HostCapabilities:
    create_repository: Callable[[str, str], str]
    write_repository: Callable[[str, Mapping[str, str], str], str]
    deploy: Callable[[str, str], str]
    verify_live: Callable[[str], bool]

@dataclass(frozen=True)
class ProgressEvent:
    stage: str
    message: str

class PromptToAppHost:
    """Single host-facing entry point for a natural-language app request."""
    STAGES = ("understand", "research", "blueprint", "generate", "test", "visual_audit",
              "repair", "github", "deploy", "verify_live", "complete")

    def __init__(self, workflow: PromptToAppWorkflow, capabilities: HostCapabilities,
                 emit: Optional[Callable[[ProgressEvent], None]] = None) -> None:
        self.factory = SoftwareFactory(workflow, capabilities.create_repository,
                                       capabilities.write_repository, capabilities.deploy,
                                       capabilities.verify_live)
        self.emit = emit or (lambda _event: None)

    def run(self, prompt: str, max_repairs: int = 2) -> FactoryResult:
        if not prompt.strip():
            raise ValueError("prompt cannot be empty")
        self.emit(ProgressEvent("understand", "Understanding the app request."))
        self.emit(ProgressEvent("research", "Researching relevant current product patterns."))
        self.emit(ProgressEvent("blueprint", "Building an evidence-aware product blueprint."))
        self.emit(ProgressEvent("generate", "Generating the application files."))
        self.emit(ProgressEvent("test", "Running functional verification."))
        self.emit(ProgressEvent("visual_audit", "Checking desktop and mobile presentation."))
        self.emit(ProgressEvent("repair", "Repairing only if verification reports a failure."))
        result = self.factory.build(prompt, max_repairs=max_repairs)
        if result.status == "ready":
            self.emit(ProgressEvent("github", "Repository created and application committed."))
            self.emit(ProgressEvent("deploy", "Deploying the generated repository."))
            self.emit(ProgressEvent("verify_live", "Verifying the production deployment."))
            self.emit(ProgressEvent("complete", "Application is live."))
        else:
            self.emit(ProgressEvent("complete", "Build stopped before verified readiness."))
        return result