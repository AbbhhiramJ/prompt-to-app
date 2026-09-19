from dataclasses import dataclass, field
from typing import List

@dataclass
class AppPlan:
    name: str
    description: str
    stack: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    run_command: str = ""
