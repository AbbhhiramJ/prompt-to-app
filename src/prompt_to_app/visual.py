"""Lightweight visual/product audit for generated apps."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

DEFAULT_VIEWPORTS = ((1440, 900), (390, 844))


def audit(
    url: str,
    artifact_dir: str | Path = "./artifacts/visual",
    viewports: Iterable[tuple[int, int]] = DEFAULT_VIEWPORTS,
    timeout: int = 30,
) -> list[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is required for visual audits") from exc

    out = Path(artifact_dir)
    out.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as exc:
            return [f"visual browser launch failed: {exc}"]

        try:
            for width, height in viewports:
                page = browser.new_page(viewport={"width": width, "height": height})
                console_errors: list[str] = []
                page_errors: list[str] = []
                page.on(
                    "console",
                    lambda msg: console_errors.append(msg.text)
                    if msg.type == "error"
                    else None,
                )
                page.on("pageerror", lambda exc: page_errors.append(str(exc)))
                try:
                    response = page.goto(
                        url,
                        wait_until="networkidle",
                        timeout=timeout * 1000,
                    )
                    if response is None or response.status >= 400:
                        errors.append(
                            f"visual {width}x{height}: HTTP "
                            f"{response.status if response else 'no response'}"
                        )
                        continue

                    page.screenshot(
                        path=str(out / f"{width}x{height}.png"),
                        full_page=True,
                    )

                    if not page.locator("body").inner_text(timeout=5000).strip():
                        errors.append(f"visual {width}x{height}: blank body")

                    overflow = page.evaluate(
                        "document.documentElement.scrollWidth > window.innerWidth + 2"
                    )
                    if overflow:
                        errors.append(
                            f"visual {width}x{height}: horizontal overflow"
                        )

                    broken_images = page.locator("img").evaluate_all(
                        "(imgs) => imgs.filter(i => !i.complete || i.naturalWidth === 0).length"
                    )
                    if broken_images:
                        errors.append(
                            f"visual {width}x{height}: {broken_images} broken image(s)"
                        )

                    invisible_controls = page.locator(
                        "button, a, input, select, textarea"
                    ).evaluate_all(
                        """els => els.filter(e => {
                            const r=e.getBoundingClientRect();
                            const s=getComputedStyle(e);
                            return (r.width===0 || r.height===0) &&
                                   s.display!=='none' &&
                                   s.visibility!=='hidden';
                        }).length"""
                    )
                    if invisible_controls:
                        errors.append(
                            f"visual {width}x{height}: "
                            f"{invisible_controls} invisible control(s)"
                        )

                    if console_errors:
                        errors.append(
                            f"visual {width}x{height}: console errors: "
                            f"{' | '.join(console_errors[:3])}"
                        )
                    if page_errors:
                        errors.append(
                            f"visual {width}x{height}: page errors: "
                            f"{' | '.join(page_errors[:3])}"
                        )
                except Exception as exc:
                    errors.append(f"visual {width}x{height}: {exc}")
                finally:
                    page.close()
        finally:
            browser.close()

    return errors
