import json
import subprocess
import sys
from pathlib import Path

class BrowserCheckUnavailable(RuntimeError):
    pass

def check(project_dir: str | Path, url: str, timeout: int = 30) -> list[str]:
    """Run an optional Playwright smoke test.

    Playwright is intentionally optional for the core package. If installed,
    this checks that the page loads and basic browser JavaScript executes.
    """
    script = """
import asyncio
import sys
from playwright.async_api import async_playwright

async def main(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        errors = []
        page.on("pageerror", lambda exc: errors.append(f"page error: {exc}"))
        response = await page.goto(url, wait_until="networkidle")
        if response is None or response.status >= 400:
            errors.append(f"page returned HTTP {response.status if response else 'no response'}")
        await browser.close()
        return errors

errors = asyncio.run(main(sys.argv[1]))
print(json.dumps(errors))
if errors:
    raise SystemExit(1)
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", script, url],
            cwd=Path(project_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise BrowserCheckUnavailable(str(exc)) from exc

    if result.returncode != 0:
        try:
            return json.loads(result.stdout or "[]")
        except json.JSONDecodeError:
            return [result.stderr.strip() or "browser verification failed"]
    return []
