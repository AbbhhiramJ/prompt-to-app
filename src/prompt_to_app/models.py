from dataclasses import dataclass, field
from typing import Any, List

@dataclass
class AppPlan:
    name: str
    description: str
    stack: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    run_command: str = ""
    tests: List[dict[str, Any]] = field(default_factory=list)
