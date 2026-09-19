from pathlib import Path

def verify(project_dir: str | Path) -> list[str]:
    root = Path(project_dir)
    errors: list[str] = []
    if not root.exists():
        errors.append("project directory does not exist")
    if not (root / "README.md").exists():
        errors.append("README.md is missing")
    return errors
