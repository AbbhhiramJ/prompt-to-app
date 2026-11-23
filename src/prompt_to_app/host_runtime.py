"""Production host runtime for the Prompt -> App factory.

The runtime contains no provider SDKs or credentials. A connected host injects
capability callables and receives structured progress events plus a final result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Optional

from .factory import FactoryCapabilities, FactoryResult, SoftwareFactory
from .workflow import PromptToAppWorkflow


@dataclass(frozen=True)
class HostCapabilities:
    create_repository: Callable[[str, str], str]
    write_repository: Callable[[str, Mapping[str, str], str], str]
    deploy: Callable[[str, str], str]
    verify_live: Callable[[str], bool]

    def as_factory_capabilities(self) -> FactoryCapabilities:
        return FactoryCapabilities(
            create_repository=self.create_repository,
            write_repository=self.write_repository,
            deploy=self.deploy,
            verify_live=self.verify_live,
        )


@dataclass(frozen=True)
class ProgressEvent:
    stage: str
    message: str


class PromptToAppHost:
    """Single host-facing entry point for a natural-language app request."""

    STAGES = (
        "understand", "research", "blueprint", "generate", "test",
        "visual_audit", "repair", "github", "deploy", "verify_live", "complete",
    )

    def __init__(
        self,
        workflow: PromptToAppWorkflow,
        capabilities: HostCapabilities,
        emit: Optional[Callable[[ProgressEvent], None]] = None,
    ) -> None:
        self.factory = SoftwareFactory(workflow, capabilities.as_factory_capabilities())
        self.emit = emit or (lambda _event: None)

    def run(self, prompt: str, max_repairs: int = 2) -> FactoryResult:
        messages = {
            "understand": "Understanding the app request.",
            "research": "Researching relevant current product patterns.",
            "blueprint": "Building an evidence-aware product blueprint.",
            "generate": "Generating the application files.",
            "test": "Running functional verification.",
            "visual_audit": "Checking desktop and mobile presentation.",
            "repair": "Repairing verification failures.",
            "github": "Creating the repository and committing generated files.",
            "deploy": "Deploying the generated repository.",
            "verify_live": "Verifying the live deployment.",
        }
        result = self.factory.build(
            prompt,
            max_repairs=max_repairs,
            on_stage=lambda stage: self.emit(ProgressEvent(stage, messages[stage])),
        )
        message = "Application is live." if result.status == "ready" else "Build stopped before verified readiness."
        self.emit(ProgressEvent("complete", message))
        return result
