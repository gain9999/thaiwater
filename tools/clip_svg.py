#!/usr/bin/env python3
"""Screenshot a region of the Chao Phraya chart SVG with Chromium (playwright).

Usage: python3 clip_svg.py OUT.png X Y W H [SCALE]
Coordinates are SVG user units; SCALE defaults to 2 (retina).
"""
import asyncio
import os
import sys

try:
    from playwright.async_api import async_playwright
except ImportError:  # optional dependency
    raise SystemExit("playwright is required: pip install playwright && playwright install chromium")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.environ.get('CHART_SVG') or os.path.join(BASE, 'data', 'raw', 'cp.svg')


async def main(out, x, y, w, h, scale):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = await b.new_page(viewport={'width': 1028, 'height': 1578}, device_scale_factor=scale)
        await page.route('**://*', lambda r: asyncio.ensure_future(r.abort()))
        await page.goto('file://' + SVG, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(2500)
        await page.screenshot(path=out, clip={'x': x, 'y': y, 'width': w, 'height': h})
        await b.close()


if __name__ == '__main__':
    if len(sys.argv) < 6:
        raise SystemExit("usage: clip_svg.py OUT.png X Y W H [SCALE]")
    out = sys.argv[1]
    x, y, w, h = (float(v) for v in sys.argv[2:6])
    scale = float(sys.argv[6]) if len(sys.argv) > 6 else 2.0
    asyncio.run(main(out, x, y, w, h, scale))
    print('wrote', out)
