from pathlib import Path
from .models import AppPlan

def generate(plan: AppPlan, output_dir: str | Path) -> Path:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text(
        f"# {plan.name}\n\n{plan.description}\n",
        encoding="utf-8",
    )
    return root
