import shlex
import subprocess
from pathlib import Path

def run(command: str, cwd: str | Path, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run a generated-app command with a bounded timeout."""
    return subprocess.run(
        shlex.split(command),
        cwd=Path(cwd),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
