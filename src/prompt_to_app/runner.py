import shlex
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

def start(command: str, cwd: str | Path) -> subprocess.Popen[str]:
    return subprocess.Popen(
        shlex.split(command),
        cwd=Path(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def wait_for_http(url: str, timeout: float = 10.0, interval: float = 0.25) -> tuple[bool, int | None]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as response:
                return True, response.status
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(interval)
    return False, None

def run(command: str, cwd: str | Path, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        shlex.split(command),
        cwd=Path(cwd),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
