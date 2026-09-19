import json
import subprocess
import sys
from pathlib import Path

class BrowserCheckUnavailable(RuntimeError):
    pass

def check(project_dir: str | Path, url: str, tests: list[dict] | None = None, timeout: int = 30) -> list[str]:
    tests = tests or [{"type": "page_load"}]
    safe_tests = []
    for test in tests:
        if not isinstance(test, dict):
            continue
        kind = test.get("type")
        if kind in {"page_load", "text_visible", "click", "text_visible_after_click"}:
            safe_tests.append(test)

    script = """
import asyncio
import json
import sys
from playwright.async_api import async_playwright

async def main(url, tests):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        errors = []
        page.on("pageerror", lambda exc: errors.append(f"page error: {exc}"))
        response = await page.goto(url, wait_until="networkidle")
        if response is None or response.status >= 400:
            errors.append(f"page returned HTTP {response.status if response else 'no response'}")
        for test in tests:
            kind = test.get("type")
            try:
                if kind == "page_load":
                    continue
                if kind == "text_visible":
                    text = str(test.get("text", ""))
                    if not text or not await page.get_by_text(text, exact=False).first.is_visible():
                        errors.append(f"text not visible: {text}")
                elif kind == "click":
                    selector = str(test.get("selector", ""))
                    await page.locator(selector).first.click(timeout=3000)
                elif kind == "text_visible_after_click":
                    text = str(test.get("text", ""))
                    if not text or not await page.get_by_text(text, exact=False).first.is_visible():
                        errors.append(f"text not visible after click: {text}")
            except Exception as exc:
                errors.append(f"{kind} failed: {exc}")
        await browser.close()
        return errors

errors = asyncio.run(main(sys.argv[1], json.loads(sys.argv[2])))
print(json.dumps(errors))
if errors:
    raise SystemExit(1)
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", script, url, json.dumps(safe_tests)],
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
