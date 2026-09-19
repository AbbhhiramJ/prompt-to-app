from pathlib import Path

class BrowserCheckUnavailable(RuntimeError):
    pass

def check(project_dir: str | Path, url: str, tests: list[dict] | None = None, timeout: int = 30) -> list[str]:
    try:
        from playwright.sync_api import sync_playwright, Error as PlaywrightError
    except ImportError as exc:
        raise BrowserCheckUnavailable("Playwright is not installed") from exc

    tests = tests or [{"type": "page_load"}]
    allowed = {"page_load", "text_visible", "click", "text_visible_after_click"}
    errors = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page_errors = []
            page.on("pageerror", lambda exc: page_errors.append(f"page error: {exc}"))
            response = page.goto(url, wait_until="networkidle", timeout=timeout * 1000)

            if not response or response.status >= 400:
                errors.append(
                    f"TEST page_load FAILED: HTTP {response.status if response else 'no response'}"
                )

            for i, test in enumerate(
                (t for t in tests if isinstance(t, dict) and t.get("type") in allowed), 1
            ):
                kind = test["type"]
                try:
                    if kind == "text_visible":
                        text = str(test.get("text", ""))
                        if not text or not page.get_by_text(text, exact=False).first.is_visible():
                            raise AssertionError(f"text={text!r}")
                    elif kind == "click":
                        page.locator(str(test.get("selector", ""))).first.click(timeout=3000)
                    elif kind == "text_visible_after_click":
                        text = str(test.get("text", ""))
                        if not text or not page.get_by_text(text, exact=False).first.is_visible():
                            raise AssertionError(f"text={text!r}")
                except Exception as exc:
                    errors.append(f"TEST {i} {kind} FAILED: {exc}")

            errors.extend(page_errors)
            browser.close()
        except PlaywrightError as exc:
            raise BrowserCheckUnavailable(str(exc)) from exc

    return errors
