"""Lightweight visual/product audit for generated apps."""
from __future__ import annotations
from pathlib import Path
from typing import Iterable

DEFAULT_VIEWPORTS=((1440,900),(390,844))

def audit(url:str, artifact_dir:str|Path="./artifacts/visual", viewports:Iterable[tuple[int,int]]=DEFAULT_VIEWPORTS, timeout:int=30)->list[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is required for visual audits") from exc
    out=Path(artifact_dir); out.mkdir(parents=True,exist_ok=True); errors=[]
    with sync_playwright() as p:
        try: browser=p.chromium.launch(headless=True)
        except Exception as exc: return [f"visual browser launch failed: {exc}"]
        try:
            for width,height in viewports:
                label=f"visual {width}x{height}"
                page=browser.new_page(viewport={"width":width,"height":height})
                try:
                    response=page.goto(url,wait_until="networkidle",timeout=timeout*1000)
                    if response is None or response.status>=400:
                        errors.append(f"{label}: HTTP {response.status if response else 'no response'}"); continue
                    page.screenshot(path=str(out/f"{width}x{height}.png"),full_page=True)
                    if not page.locator("body").inner_text(timeout=5000).strip(): errors.append(f"{label}: blank body")
                    if page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2"): errors.append(f"{label}: horizontal overflow")
                    if page.locator("img").evaluate_all("(imgs)=>imgs.filter(i=>!i.complete||i.naturalWidth===0).length"): errors.append(f"{label}: broken image(s)")
                    hidden=page.locator("button,a,input,select,textarea").evaluate_all("""els=>els.filter(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return (r.width===0||r.height===0)&&(s.display!=='none'&&s.visibility!=='hidden')}).length""")
                    if hidden: errors.append(f"{label}: {hidden} invisible control(s)")
                except Exception as exc: errors.append(f"{label}: {exc}")
                finally: page.close()
        finally: browser.close()
    return errors
