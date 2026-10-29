"""Local-only UI screenshot and accessibility heuristic audit.

SECURITY: This tool is a local CLI, not a public API. It accepts only localhost
URLs and does not authenticate, click, or submit forms. For untrusted HTML,
run it in an isolated environment with network disabled.
"""
from __future__ import annotations
import argparse
import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse

VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}

def allowed_url(url: str) -> bool:
    p = urlparse(url)
    return p.scheme in ("http", "https") and p.hostname in ("localhost", "127.0.0.1", "::1") and not p.username and not p.password

CHECK_JS = r"""() => {
 const problems=[];
 const add=(code,severity,message,element)=>problems.push({
   code,severity,message,
   evidence:(element?.outerHTML||"").slice(0,240)
 });
 const visible = e => !!(e.getClientRects().length) && getComputedStyle(e).visibility !== 'hidden';
 document.querySelectorAll('img:not([alt])').forEach(e=>add('ui.image.alt','major','Image has no alt attribute',e));
 document.querySelectorAll('button').forEach(e=>{
   if(visible(e) && !(e.innerText.trim()||e.getAttribute('aria-label')||e.getAttribute('aria-labelledby')))
     add('ui.button.name','major','Visible button may lack an accessible name',e);
 });
 document.querySelectorAll('input:not([type=hidden]),select,textarea').forEach(e=>{
   if (!visible(e)) return;
   const hasLabel=!!(e.labels&&e.labels.length);
   if(!hasLabel&&!e.getAttribute('aria-label')&&!e.getAttribute('aria-labelledby'))
     add('ui.input.name','major','Visible form control may lack an accessible name',e);
 });
 if(!document.documentElement.lang) add('ui.document.lang','minor','Document missing language attribute',document.documentElement);
 if(!document.querySelector('main,[role=main]')) add('ui.landmark.main','minor','No main content landmark',document.body);
 const width=document.documentElement.scrollWidth, viewport=window.innerWidth;
 if(width>viewport+2) add('ui.layout.overflow','minor', 'Horizontal page overflow: '+width+'px vs '+viewport+'px',document.documentElement);
 return {title:document.title,issues:problems,viewport:{width:viewport,height:innerHeight},documentWidth:width};
}"""

async def audit(url: str, output: Path) -> dict:
    if not allowed_url(url):
        raise ValueError("Only explicitly local localhost/loopback URLs are supported")
    from playwright.async_api import async_playwright
    output.mkdir(parents=True, exist_ok=True)
    results = {"url": url, "screens": {}, "limits": ["Heuristic checks only; not WCAG conformance certification", "No authenticated flows or automatic repairs"]}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        try:
            for name, (width, height) in VIEWPORTS.items():
                context = await browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
                # Prevent the page from fetching remote resources and redirecting to remote hosts.
                async def guard(route):
                    if allowed_url(route.request.url):
                        await route.continue_()
                    else:
                        await route.abort()
                await context.route("**/*", guard)
                page = await context.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                await page.screenshot(path=str(output / (name + ".png")), full_page=True, animations="disabled")
                results["screens"][name] = await page.evaluate(CHECK_JS)
                results["screens"][name]["screenshot"] = name + ".png"
                await context.close()
        finally:
            await browser.close()
    (output / "report.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return results

def main():
    parser = argparse.ArgumentParser(description="Audit a localhost page with Playwright")
    parser.add_argument("url", help="localhost URL only, e.g. http://127.0.0.1:8000")
    parser.add_argument("--output", default="artifacts/ui-audit")
    args = parser.parse_args()
    if not allowed_url(args.url):
        parser.error("Only localhost or 127.0.0.1 URLs are permitted")
    report = asyncio.run(audit(args.url, Path(args.output)))
    print(json.dumps({"screens": {k: len(v["issues"]) for k,v in report["screens"].items()}, "report": str(Path(args.output) / "report.json")}, indent=2))

if __name__ == "__main__":
    main()
